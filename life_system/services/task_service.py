from typing import List, Optional
from sqlalchemy.orm import Session
from life_system.core.event_bus import EventBus
from life_system.core.models import Task, Event
from life_system.core.db import SessionLocal

class TaskService:
    def __init__(self):
        self.bus = EventBus()
        self.db_factory = SessionLocal

    def create_task_event(self, title: str) -> int:
        """从 CLI 接收命令，只负责发布事件"""
        return self.bus.publish(
            type="task.created",
            source="cli",
            payload={"title": title}
        )

    def process_events(self):
        """处理未处理的 task.created 事件，将其转换为 Task 记录"""
        events = self.bus.get_unprocessed()
        db = self.db_factory()
        count = 0
        try:
            for event in events:
                if event.type == "task.created":
                    # 1. 创建 Task
                    title = event.payload.get("title")
                    if title:
                        new_task = Task(title=title, status="pending")
                        db.add(new_task)
                        # 可以在这里添加 TaskTransition 记录
                    
                    # 2. 标记事件为已处理
                    event.processed = True
                    count += 1
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            print(f"Error processing events: {e}")
            return 0
        finally:
            db.close()

    def list_tasks(self, status: Optional[str] = None) -> List[Task]:
        db = self.db_factory()
        try:
            query = db.query(Task)
            if status:
                query = query.filter(Task.status == status)
            return query.all()
        finally:
            db.close()

    def update_status(self, task_id: int, new_status: str) -> bool:
        db = self.db_factory()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                task.status = new_status
                db.commit()
                return True
            return False
        finally:
            db.close()

