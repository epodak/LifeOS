from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Button
from textual.containers import Container, Horizontal
from textual.binding import Binding
from life_system.services.task_service import TaskService

class TaskApp(App):
    """LifeOS 的终端图形界面 (TUI)"""
    
    CSS = """
    Screen {
        layout: vertical;
    }
    DataTable {
        height: 1fr;
        border: solid green;
    }
    .buttons {
        height: auto;
        dock: bottom;
        padding: 1;
        background: $boost;
    }
    Button {
        margin-right: 1;
    }
    """

    BINDINGS = [
        ("d", "done_task", "完成任务"),
        ("q", "quit", "退出"),
        ("r", "refresh", "刷新"),
    ]

    def __init__(self):
        super().__init__()
        self.service = TaskService()

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable()
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.cursor_type = "row"
        table.add_columns("ID", "标题", "状态", "创建时间")
        self.refresh_data()

    def refresh_data(self):
        table = self.query_one(DataTable)
        table.clear()
        tasks = self.service.list_tasks("pending")
        for task in tasks:
            table.add_row(
                str(task.id),
                task.title,
                task.status,
                task.created_at.strftime("%Y-%m-%d %H:%M")
            )

    def action_done_task(self):
        table = self.query_one(DataTable)
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        # Textual 的 DataTable row_key 默认可能不是我们想要的 ID，这里为了简单演示，
        # 我们假设第一列是 ID。在实际生产中，会在 add_row 时指定 key。
        # 更好的做法是在 add_row 时绑定 key:
        # table.add_row(..., key=str(task.id))
        
        # 重新获取当前选中行的第一列(ID)
        try:
            row = table.get_row_at(table.cursor_coordinate.row)
            task_id = int(row[0])
            self.service.update_status(task_id, "done")
            self.notify(f"任务 {task_id} 已完成")
            self.refresh_data()
        except Exception:
            self.notify("请先选择一个任务", severity="warning")

    def action_refresh(self):
        self.refresh_data()

