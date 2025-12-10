import time
from apscheduler.schedulers.background import BackgroundScheduler
from life_system.services.task_service import TaskService
from rich.console import Console

console = Console()
service = TaskService()

def run_scheduler():
    scheduler = BackgroundScheduler()
    
    # 每 10 秒处理一次新事件（为了测试效果设短一点）
    scheduler.add_job(service.process_events, 'interval', seconds=10)
    
    # 每天 08:00 生成今日任务（占位，暂未实现具体逻辑）
    # scheduler.add_job(planner.plan_today, "cron", hour=8, minute=0)

    scheduler.start()
    console.print("[green]Scheduler started. Press Ctrl+C to exit.[/green]")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.shutdown()
        console.print("[yellow]Scheduler shutdown.[/yellow]")

if __name__ == "__main__":
    run_scheduler()

