import os
import sys
import time
from pathlib import Path
from filelock import FileLock, Timeout
from life_system.config.settings import DB_PATH
from life_system.utils.logger import logger
from life_system.utils.console import console

# 锁文件位置：与 DB 同级，确保所有进程看到的是同一个锁
LOCK_FILE_PATH = Path(DB_PATH).parent / "life_serve.lock"

class SingleInstanceLock:
    """
    确保 LifeOS 后台服务全局唯一
    """
    def __init__(self):
        self.lock_file = LOCK_FILE_PATH
        self.lock = FileLock(self.lock_file, timeout=0)
        
    def acquire(self) -> bool:
        """尝试获取锁，如果已被占用则返回 False"""
        try:
            self.lock.acquire()
            # 写入当前 PID 方便调试
            with open(self.lock_file, "w") as f:
                f.write(str(os.getpid()))
            logger.info(f"Acquired single instance lock: {self.lock_file} (PID: {os.getpid()})")
            return True
        except Timeout:
            # 读取占用锁的 PID
            try:
                with open(self.lock_file, "r") as f:
                    pid = f.read().strip()
            except:
                pid = "unknown"
            
            logger.warning(f"Failed to acquire lock. Service already running (PID: {pid})")
            console.print(f"[yellow]LifeOS 后台服务已在运行 (PID: {pid})。[/yellow]")
            console.print("[yellow]请勿重复启动。如果要重启，请先杀死旧进程。[/yellow]")
            return False

    def release(self):
        """释放锁"""
        if self.lock.is_locked:
            self.lock.release()
            try:
                os.remove(self.lock_file)
            except:
                pass
            logger.info("Released single instance lock")

