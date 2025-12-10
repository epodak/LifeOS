import time
from apscheduler.schedulers.background import BackgroundScheduler
from life_system.services.task_service import TaskService
from life_system.collectors.fs_watcher import FileWatcher
from life_system.utils.console import console
from life_system.utils.logger import logger
from life_system.utils.lock import SingleInstanceLock
from life_system.core.collector_manager import CollectorManager
import os
import sys

service = TaskService()

def run_scheduler():
    """
    启动 LifeOS 的后台主进程 (The Brain)
    职责：
    1. 确保全局单例运行
    2. 启动定时任务调度器 (APScheduler)
    3. 启动所有收集器 (CollectorManager)
    4. 运行主循环 (Event Processing)
    """
    # 0. 单例检查
    instance_lock = SingleInstanceLock()
    if not instance_lock.acquire():
        sys.exit(1)
        
    logger.info("Starting LifeOS Background Scheduler...")
    
    # 初始化收集器管理器
    # 暂时默认监控当前目录，但应该在文档中强调 "cd 到正确的目录再运行 serve"
    collector_manager = CollectorManager(os.getcwd())
    
    try:
        # 1. 启动调度器
        scheduler = BackgroundScheduler()
        # 每 5 秒处理一次 CLI/Watchdog 产生的积压事件
        scheduler.add_job(service.process_events, 'interval', seconds=5)
        scheduler.start()
        console.print("[green]调度器 (Scheduler) 已启动[/green]")
        logger.info("APScheduler started")
        
        # 2. 启动所有收集器 (替换原有的硬编码 FileWatcher)
        collector_manager.discover_and_start()
        
        console.print(f"[blue]LifeOS 后台服务运行中... (PID: {os.getpid()})[/blue]")
        console.print("[dim]按 Ctrl+C 停止服务[/dim]")
        logger.info(f"LifeOS Service running at PID {os.getpid()}")
        
        # 主线程保持运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down service...")
        scheduler.shutdown()
        collector_manager.stop_all()
        console.print("[yellow]服务已关闭。[/yellow]")
    finally:
        # 确保退出时释放锁
        instance_lock.release()

if __name__ == "__main__":
    run_scheduler()
