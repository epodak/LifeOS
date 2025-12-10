import typer
from rich.console import Console
from rich.table import Table
from life_system.core.db import init_db
from life_system.services.task_service import TaskService

app = typer.Typer()
console = Console()
service = TaskService()

@app.command()
def init():
    """初始化数据库"""
    init_db()
    console.print("[green]Database initialized![/green]")

@app.command()
def add(title: str):
    """添加新任务（发布事件）"""
    event_id = service.create_task_event(title)
    console.print(f"[green]Task event published (ID: {event_id}). Run 'process' to apply.[/green]")
    # 为了 MVP 方便体验，这里可以自动触发一次 process，或者由用户手动触发
    # service.process_events() 

@app.command()
def process():
    """手动触发事件处理（将事件转换为任务）"""
    count = service.process_events()
    console.print(f"[green]Processed {count} events.[/green]")

@app.command()
def list(status: str = "pending"):
    """列出任务"""
    # 在列出前先尝试处理一次积压事件（"懒加载"策略，防止后台没开时看不到新任务）
    service.process_events()
    
    tasks = service.list_tasks(status)
    table = Table(title=f"Tasks ({status})")
    table.add_column("ID", justify="right", style="cyan", no_wrap=True)
    table.add_column("Title", style="magenta")
    table.add_column("Status", style="green")
    table.add_column("Created At", justify="right")

    for task in tasks:
        table.add_row(
            str(task.id), 
            task.title, 
            task.status, 
            task.created_at.strftime("%Y-%m-%d %H:%M")
        )

    console.print(table)

@app.command()
def done(task_id: int):
    """标记任务完成"""
    if service.update_status(task_id, "done"):
        console.print(f"[green]Task {task_id} marked as done![/green]")
    else:
        console.print(f"[red]Task {task_id} not found.[/red]")

@app.command()
def drop(task_id: int):
    """放弃任务"""
    if service.update_status(task_id, "dropped"):
        console.print(f"[yellow]Task {task_id} dropped.[/yellow]")
    else:
        console.print(f"[red]Task {task_id} not found.[/red]")

@app.command()
def serve():
    """启动后台调度服务"""
    from life_system.services.scheduler import run_scheduler
    run_scheduler()

if __name__ == "__main__":
    app()

