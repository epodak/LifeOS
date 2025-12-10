from typing import List, Optional
import os
from sqlalchemy.orm import Session
from life_system.core.event_bus import EventBus
from life_system.core.models import Task, Event
from life_system.core.db import SessionLocal
from life_system.utils.console import console
from life_system.utils.logger import logger

class TaskService:
    def __init__(self):
        self.bus = EventBus()
        self.db_factory = SessionLocal

    def create_task_event(self, title: str) -> int:
        """从 CLI 接收命令，只负责发布事件"""
        logger.info(f"Publishing task.created event: {title}")
        return self.bus.publish(
            type="task.created",
            source="cli",
            payload={"title": title}
        )

    def process_events(self):
        """处理未处理的事件，将其转换为 Task 记录"""
        events = self.bus.get_unprocessed()
        if not events:
            return 0
            
        db = self.db_factory()
        count = 0
        try:
            for event in events:
                task_created = False
                # 处理 CLI 手动任务
                if event.type == "task.created":
                    title = event.payload.get("title")
                    if title:
                        new_task = Task(title=title, status="pending")
                        db.add(new_task)
                        task_created = True
                        logger.info(f"Converted event {event.id} to Task: {title}")
                
                # 处理文件监控事件
                elif event.type.startswith("file."):
                    # 这里是 MVP 的简单逻辑：直接把“文件变动”变成一个任务
                    # 未来这里应该调用 AI Engine 进行分析
                    path = event.payload.get("path")
                    event_type = event.type.split(".")[1] # created, modified
                    if path:
                        # 简单的防噪：只关注 .md, .txt, .py 文件
                        if any(path.endswith(ext) for ext in ['.md', '.txt', '.py']):
                            title = f"[{event_type.upper()}] 审查文件: {os.path.basename(path)}"
                            # 避免重复创建同名任务（简单去重）
                            exists = db.query(Task).filter(Task.title == title, Task.status == "pending").first()
                            if not exists:
                                new_task = Task(title=title, status="pending")
                                db.add(new_task)
                                task_created = True
                                console.print(f"[cyan]自动发现: {title}[/cyan]")
                                logger.info(f"Auto-generated task from file event: {title}")
                            else:
                                logger.debug(f"Skipped duplicate task for file: {path}")

                # 标记事件为已处理
                event.processed = True
                count += 1
                
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            console.print(f"[red]处理事件时出错: {e}[/red]")
            logger.error(f"Error processing events: {e}")
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
