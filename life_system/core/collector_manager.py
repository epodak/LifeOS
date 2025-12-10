import importlib
import pkgutil
import threading
from typing import Dict, Type
from life_system.utils.logger import logger
from life_system.utils.console import console

class CollectorManager:
    """
    Collector 插件管理器
    
    职责：
    1. 动态发现并加载 collectors 目录下的所有收集器
    2. 统一管理收集器的生命周期 (start/stop)
    3. 确保所有收集器都接入 Ingestion Pipeline
    """
    
    def __init__(self, watch_dir: str):
        self.watch_dir = watch_dir
        self.collectors = {}
        self.threads = []
        
    def discover_and_start(self):
        """发现并启动所有收集器"""
        # 1. 显式启动核心收集器 (如 FileWatcher)
        # 未来这里可以改为完全动态加载，但 MVP 阶段先硬编码核心组件以确保稳定性
        try:
            from life_system.collectors.fs_watcher import FileWatcher
            watcher = FileWatcher(self.watch_dir)
            watcher.start()
            self.collectors['fs_watcher'] = watcher
            logger.info("Collector 'fs_watcher' started")
        except Exception as e:
            logger.error(f"Failed to start fs_watcher: {e}")

        # 2. (未来扩展) 扫描 life_system.collectors 包下的其他模块
        # for module_info in pkgutil.iter_modules(['life_system/collectors']):
        #     ...

    def stop_all(self):
        """停止所有收集器"""
        for name, collector in self.collectors.items():
            try:
                if hasattr(collector, 'stop'):
                    collector.stop()
                    logger.info(f"Collector '{name}' stopped")
            except Exception as e:
                logger.error(f"Error stopping collector '{name}': {e}")
        self.collectors.clear()

