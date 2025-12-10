import typer
from rich.table import Table
from life_system.core.db import init_db
from life_system.services.task_service import TaskService
from life_system.utils.console import console
from life_system.utils.interaction import smart_prompt, safe_confirm

app = typer.Typer(
    help="LifeOS: 你的个人生活操作系统",
    add_completion=False, # 禁用 Typer 默认的 shell 补全安装提示，保持清爽
    context_settings={"help_option_names": ["-h", "--help"]} # 统一使用 -h 和 --help
)
service = TaskService()

@app.command()
def init():
    """初始化数据库"""
    if safe_confirm("确定要初始化数据库吗？这不会删除现有数据，但会创建缺失的表。"):
        init_db()
        console.print("[green]Database initialized![/green]")

@app.command()
def add(title: str = typer.Argument(None, help="任务标题")):
    """
    添加新任务。
    如果不提供标题，将进入交互式模式。
    """
    if not title:
        title = smart_prompt("请输入任务标题")
    
    if not title:
        return

    event_id = service.create_task_event(title)
    console.print(f"[green]Task event published (ID: {event_id}). Run 'process' to apply.[/green]")

@app.command()
def process():
    """手动触发事件处理（将事件转换为任务）"""
    count = service.process_events()
    console.print(f"[green]Processed {count} events.[/green]")

@app.command()
def list(
    status: str = typer.Option("pending", "--status", "-s", help="筛选状态: pending, done, dropped"),
    ui: bool = typer.Option(False, "--tui", "-t", help="启动 TUI 终端图形界面"),
    gui: bool = typer.Option(False, "--gui", "-g", help="启动 GUI 独立窗口界面")
):
    """
    列出任务。
    支持 -s 筛选状态。
    支持 -t 启动终端界面。
    支持 -g 启动独立窗口界面。
    """
    # 懒加载策略
    service.process_events()
    
    if gui:
        import sys
        import subprocess
        # 启动独立的 GUI 进程
        # 注意：Gooey 需要作为主程序运行，这里简单的做法是调用另一个脚本
        from pathlib import Path
        gui_script = Path(__file__).parent / "gui.py"
        subprocess.Popen([sys.executable, str(gui_script)])
        return

    if ui:
        from life_system.interfaces.tui import TaskApp
        app = TaskApp()
        app.run()
        return

    # 普通列表模式
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
