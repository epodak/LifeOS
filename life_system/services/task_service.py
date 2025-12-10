from typing import List, Optional
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import desc
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
                # 检查该事件是否在其他地方已经被处理（防止并发问题）
                # 注意：这里我们使用 update 语句的行级锁特性或者条件更新来确保安全
                # 但为了简单起见，我们假设 get_unprocessed 已经尽力了。
                
                # 为了防止"DetachedInstanceError"，我们直接使用 event 对象的数据（它们应该在内存中了）
                # 状态更新则通过显式的 SQL UPDATE 语句执行，确保万无一失。
                
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
                    path = event.payload.get("path")
                    event_type = event.type.split(".")[1] # created, modified
                    if path:
                        if any(path.endswith(ext) for ext in ['.md', '.txt', '.py']):
                            title = f"[{event_type.upper()}] 审查文件: {os.path.basename(path)}"
                            
                            # === 智能去重策略 ===
                            # 1. 检查是否有 PENDING 的同名任务 -> 直接跳过
                            pending_task = db.query(Task).filter(
                                Task.title == title, 
                                Task.status == "pending"
                            ).first()
                            
                            if pending_task:
                                logger.debug(f"Skipped duplicate task (already pending): {title}")
                                db.query(Event).filter(Event.id == event.id).update({"processed": True})
                                continue
                                
                            # 2. 检查是否有最近完成 (DONE) 的同名任务 -> 防止"诈尸"
                            cutoff_time = datetime.now() - timedelta(minutes=5)
                            recent_done_task = db.query(Task).filter(
                                Task.title == title,
                                Task.status == "done",
                                Task.updated_at > cutoff_time
                            ).order_by(desc(Task.updated_at)).first()
                            
                            if recent_done_task:
                                logger.info(f"Skipped recent done task (cool-down active): {title} (Done at {recent_done_task.updated_at})")
                                db.query(Event).filter(Event.id == event.id).update({"processed": True})
                                continue

                            # 只有既没有 pending，又没有最近 done 的任务，才创建新的
                            new_task = Task(title=title, status="pending")
                            db.add(new_task)
                            task_created = True
                            console.print(f"[cyan]自动发现: {title}[/cyan]")
                            logger.info(f"Auto-generated task from file event: {title}")

                # 标记事件为已处理 (使用显式 UPDATE)
                db.query(Event).filter(Event.id == event.id).update({"processed": True})
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
                # 记录状态变更日志
                logger.info(f"Task {task_id} status updated to {new_status}")
                return True
            logger.warning(f"Task {task_id} not found when updating status to {new_status}")
            return False
        finally:
            db.close()
