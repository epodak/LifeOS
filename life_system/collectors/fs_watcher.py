import time
import os
from pathlib import Path
from typing import Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from life_system.core.event_bus import EventBus
from life_system.utils.console import console
from life_system.utils.logger import logger

class LifeOSFileHandler(FileSystemEventHandler):
    """
    LifeOS 文件系统事件处理器
    
    职责：
    1. 监听文件系统的创建、修改、移动事件
    2. 将这些原生事件转换为 LifeOS 的标准 Event
    3. 通过 EventBus (集成 IngestionPipeline) 发布，实现防抖和去重
    """
    
    def __init__(self, bus: EventBus, watch_dir: str):
        self.bus = bus
        self.watch_dir = watch_dir
        
    def _process_event(self, event_type: str, src_path: str, dest_path: str = None):
        """处理文件事件并发布"""
        # 忽略目录事件（通常我们只关心文件的具体变化，或者让 pipeline 去过滤）
        # 这里先保留，由 Pipeline 统一决定是否过滤目录
        
        payload = {
            "path": src_path,
            "watch_dir": self.watch_dir
        }
        
        if dest_path:
            payload["dest_path"] = dest_path
            
        # 发布事件
        logger.debug(f"Detected file system event: {event_type} - {src_path}")
        self.bus.publish(
            type=f"file.{event_type}",
            source="file_watcher",
            payload=payload
        )

    def on_created(self, event):
        self._process_event("created", event.src_path)

    def on_modified(self, event):
        if not event.is_directory:
            self._process_event("modified", event.src_path)

    def on_moved(self, event):
        self._process_event("moved", event.src_path, event.dest_path)

    # 删除事件目前可能不需要触发任务，暂且忽略，或者也可以发出来
    # def on_deleted(self, event):
    #     self._process_event("deleted", event.src_path)

class FileWatcher:
    """
    文件监控服务管理器
    """
    def __init__(self, path: str):
        self.path = os.path.abspath(path)
        self.observer: Optional[Observer] = None
        self.bus = EventBus() # 自动使用 IngestionPipeline

    def start(self):
        """启动监控"""
        if not os.path.exists(self.path):
            console.print(f"[red]错误: 监控目录不存在: {self.path}[/red]")
            logger.error(f"Monitor directory does not exist: {self.path}")
            return

        event_handler = LifeOSFileHandler(self.bus, self.path)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.path, recursive=True)
        self.observer.start()
        
        console.print(f"[green]文件监控已启动，正在监听: {self.path}[/green]")
        logger.info(f"File Watcher started on: {self.path}")

    def stop(self):
        """停止监控"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            console.print("[yellow]文件监控已停止[/yellow]")
            logger.info("File Watcher stopped")

# 单例测试
if __name__ == "__main__":
    # 测试代码
    try:
        watcher = FileWatcher(".")
        watcher.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        watcher.stop()

