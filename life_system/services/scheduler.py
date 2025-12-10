import time
from apscheduler.schedulers.background import BackgroundScheduler
from life_system.services.task_service import TaskService
from life_system.collectors.fs_watcher import FileWatcher
from life_system.utils.console import console
from life_system.utils.logger import logger
import os

service = TaskService()

def run_scheduler():
    """
    启动 LifeOS 的后台主进程 (The Brain)
    职责：
    1. 启动定时任务调度器 (APScheduler)
    2. 启动文件系统监控 (Watchdog)
    3. 运行主循环 (Event Processing)
    """
    logger.info("Starting LifeOS Background Scheduler...")
    
    # 1. 启动调度器
    scheduler = BackgroundScheduler()
    # 每 5 秒处理一次 CLI/Watchdog 产生的积压事件
    scheduler.add_job(service.process_events, 'interval', seconds=5)
    scheduler.start()
    console.print("[green]调度器 (Scheduler) 已启动[/green]")
    logger.info("APScheduler started")
    
    # 2. 启动文件监控
    # 目前默认监控当前工作目录，未来应该从配置读取
    watch_dir = os.getcwd() 
    watcher = FileWatcher(watch_dir)
    watcher.start()
    
    console.print(f"[blue]LifeOS 后台服务运行中... (PID: {os.getpid()})[/blue]")
    console.print("[dim]按 Ctrl+C 停止服务[/dim]")
    logger.info(f"LifeOS Service running at PID {os.getpid()}")
    
    try:
        # 主线程保持运行
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down service...")
        scheduler.shutdown()
        watcher.stop()
        console.print("[yellow]服务已关闭。[/yellow]")

if __name__ == "__main__":
    run_scheduler()
