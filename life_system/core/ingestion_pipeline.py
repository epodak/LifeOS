import json
from collections import defaultdict
from threading import Lock
from typing import Dict, Any, Optional, Set
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import os
from life_system.utils.logger import logger

class IngestionPipeline:
    """
    事件摄入管道：系统的"不动点"
    
    所有 Collector 都应该通过这个管道发布事件，而不是直接调用 EventBus。
    
    持久化去重机制：
    为了防止重启后重新生成事件，Pipeline 现在在内存中维护了一个
    (path -> (mtime, size)) 的状态映射。
    注意：目前的持久化仅限于进程生命周期。如果需要重启后依然去重，
    需要将 _file_state_cache 序列化到磁盘（MVP暂不实现，靠 Service 层的 Pending 检查兜底）。
    """
    
    # 需要过滤的文件/目录模式
    FILTER_PATTERNS = {
        # 版本控制
        '.git', '.svn', '.hg',
        # Python
        '__pycache__', '*.pyc', '*.pyo', '.pytest_cache',
        # 编辑器
        '.vscode', '.idea', '*.swp', '*.swo', '*~',
        # 系统文件
        '.DS_Store', 'Thumbs.db', 'desktop.ini',
        # 临时文件
        '*.tmp', '*.temp', '*.log',
        # Node
        'node_modules', '.npm',
        # 其他
        '.env.local', '.env.*.local',
        # 显式忽略数据库文件，防止死循环
        'life.db', 'life.db-journal', '*.lock'
    }
    
    def __init__(self, debounce_window: float = 1.0):
        """
        初始化摄入管道
        
        Args:
            debounce_window: 防抖时间窗口（秒），默认1秒
        """
        self.debounce_window = debounce_window
        self._event_cache: Dict[str, tuple] = {}  # key: event_key, value: (timestamp, event_data)
        self._seen_hashes: Set[str] = set()  # 已处理的事件哈希（用于去重）
        self._file_state_cache: Dict[str, tuple] = {} # key: path, value: (mtime, size)
        self._lock = Lock()  # 线程安全
        
    def _get_file_state(self, path_str: str) -> Optional[tuple]:
        """获取文件的物理状态 (mtime, size)"""
        try:
            p = Path(path_str)
            if p.exists() and p.is_file():
                stat = p.stat()
                return (stat.st_mtime, stat.st_size)
        except Exception:
            pass
        return None

    def _generate_event_key(self, event_type: str, source: str, payload: Dict[str, Any]) -> str:
        """
        生成事件的唯一键，用于防抖
        
        对于文件事件，使用路径作为键
        对于其他事件，使用 type + source + payload 的关键字段
        """
        if event_type.startswith('file.'):
            # 文件事件：使用路径作为键
            path = payload.get('path', '')
            return f"{event_type}:{path}"
        else:
            # 其他事件：使用关键字段
            key_fields = payload.get('title') or payload.get('task_id') or payload.get('id', '')
            return f"{event_type}:{source}:{key_fields}"
    
    def _generate_event_hash(self, event_type: str, source: str, payload: Dict[str, Any]) -> str:
        """
        生成事件的哈希值，用于去重
        
        完全相同的 payload 应该被去重。
        注意：排除 timestamp 字段，确保同一事件在不同时间被视为重复（如果内容没变）。
        """
        # 复制 payload 并移除时间戳，只根据内容去重
        clean_payload = payload.copy()
        if 'timestamp' in clean_payload:
            del clean_payload['timestamp']
            
        content = json.dumps({
            'type': event_type,
            'source': source,
            'payload': clean_payload
        }, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()
    
    def _should_filter(self, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        判断事件是否应该被过滤
        
        Returns:
            True 表示应该过滤（丢弃），False 表示应该保留
        """
        # 文件事件需要检查路径
        if event_type.startswith('file.'):
            path_str = payload.get('path', '')
            if not path_str:
                return True  # 没有路径，过滤掉
            
            path = Path(path_str)
            
            # 检查文件名和目录名
            for pattern in self.FILTER_PATTERNS:
                if pattern.startswith('*'):
                    # 通配符匹配
                    if path.name.endswith(pattern[1:]):
                        logger.debug(f"Filter matched wildcard: {pattern} for {path.name}")
                        return True
                elif pattern in path.parts:
                    # 目录名匹配
                    logger.debug(f"Filter matched dir: {pattern} in {path}")
                    return True
                elif path.name == pattern:
                    # 文件名完全匹配
                    logger.debug(f"Filter matched exact: {pattern} for {path.name}")
                    return True
            
            # 检查隐藏文件（Unix 风格）
            if path.name.startswith('.'):
                # 但允许 .env（配置）和 .gitignore 等
                if path.name not in ['.env', '.gitignore', '.dockerignore']:
                    logger.debug(f"Filter hidden file: {path.name}")
                    return True
        
        return False
    
    def _normalize_payload(self, event_type: str, source: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        标准化事件 payload
        
        确保所有事件都有统一的格式
        """
        normalized = payload.copy()
        
        # 文件事件：标准化路径
        if event_type.startswith('file.'):
            path = normalized.get('path', '')
            if path:
                try:
                    # 转换为绝对路径并标准化
                    path_obj = Path(path)
                    if not path_obj.is_absolute():
                        # 如果是相对路径，尝试解析
                        normalized['path'] = str(path_obj.resolve())
                    else:
                        normalized['path'] = str(path_obj)
                    
                    # 添加路径元数据
                    normalized['path_parts'] = list(path_obj.parts)
                    normalized['is_file'] = path_obj.is_file()
                    normalized['is_dir'] = path_obj.is_dir()
                except Exception:
                    # 路径无效，保留原值
                    pass
        
        # 添加时间戳（如果不存在）
        if 'timestamp' not in normalized:
            normalized['timestamp'] = datetime.now().isoformat()
        
        # 移除可能导致哈希变动的易变字段（如 timestamp），如果它不是 payload 的核心部分
        # 但对于文件事件，timestamp 是有意义的... 
        # 关键是：我们希望 payload 相同（内容相同）时去重，但 timestamp 每次都变。
        # 所以计算哈希时，应该排除 timestamp？
        
        return normalized
    
    def ingest(
        self, 
        event_type: str, 
        source: str, 
        payload: Dict[str, Any],
        publish_func
    ) -> Optional[int]:
        """
        摄入事件：这是所有事件的唯一入口
        
        Args:
            event_type: 事件类型，如 "task.created", "file.created"
            source: 事件来源，如 "cli", "file_watcher", "scheduler"
            payload: 事件数据
            publish_func: 发布函数，应该调用 EventBus._publish_direct 避免循环
        
        Returns:
            事件ID（如果成功发布），None（如果被过滤或去重）
        """
        with self._lock:
            # 1. 过滤：检查是否应该丢弃
            if self._should_filter(event_type, payload):
                # logger.debug(f"Event filtered: {event_type} - {payload}")
                return None
            
            # 2. 标准化：统一格式
            normalized_payload = self._normalize_payload(event_type, source, payload)
            
            # === 3. 物理状态检查 (Physical State Check) ===
            # 这是为了防止 Watchdog 重复报告从未变过的文件
            if event_type.startswith('file.'):
                path = normalized_payload.get('path')
                if path:
                    current_state = self._get_file_state(path)
                    if current_state:
                        last_state = self._file_state_cache.get(path)
                        if last_state == current_state:
                            # 物理状态没变，视为重复/噪音
                            logger.debug(f"File state unchanged (duplicate event): {path}")
                            return None
                        # 更新状态缓存
                        self._file_state_cache[path] = current_state
                    else:
                        # 文件可能已被删除
                        if 'deleted' not in event_type:
                            return None
            
            # 3. 去重：检查是否已经处理过完全相同的事件
            event_hash = self._generate_event_hash(event_type, source, normalized_payload)
            if event_hash in self._seen_hashes:
                logger.debug(f"Event duplicated (hash match): {event_type}")
                return None  # 重复事件，丢弃
            
            # 4. 防抖：检查时间窗口内的重复事件
            event_key = self._generate_event_key(event_type, source, normalized_payload)
            now = datetime.now()
            
            if event_key in self._event_cache:
                last_time, last_payload = self._event_cache[event_key]
                time_diff = (now - last_time).total_seconds()
                
                if time_diff < self.debounce_window:
                    # 在防抖窗口内，更新缓存但不发布
                    self._event_cache[event_key] = (now, normalized_payload)
                    logger.debug(f"Event debounced ({time_diff:.2f}s < {self.debounce_window}s): {event_type}")
                    return None  # 等待防抖窗口结束
            
            # 5. 通过所有检查，发布事件
            try:
                # 调用发布函数（应该是 _publish_direct，避免循环）
                event_id = publish_func(event_type, source, normalized_payload)
                
                # 记录到缓存和已处理集合
                self._event_cache[event_key] = (now, normalized_payload)
                self._seen_hashes.add(event_hash)
                
                # 清理过期的缓存（超过防抖窗口2倍的时间）
                self._cleanup_cache(now)
                
                logger.info(f"Event ingested: {event_type} from {source} (ID: {event_id})")
                return event_id
            except Exception as e:
                # 发布失败，记录但不阻塞
                logger.error(f"Failed to publish event: {e}")
                return None
    
    def _cleanup_cache(self, now: datetime):
        """清理过期的缓存项"""
        expire_time = now - timedelta(seconds=self.debounce_window * 2)
        expired_keys = [
            key for key, (timestamp, _) in self._event_cache.items()
            if timestamp < expire_time
        ]
        for key in expired_keys:
            del self._event_cache[key]
    
    def reset(self):
        """重置管道状态（用于测试或重启）"""
        with self._lock:
            self._event_cache.clear()
            self._seen_hashes.clear()
            self._file_state_cache.clear()
            logger.info("Pipeline reset")
