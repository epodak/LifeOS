"""
提醒服务 (Reminder Service)
处理任务提醒逻辑
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from life_system.core.models import Task
from life_system.core.db import SessionLocal
from life_system.core.event_bus import EventBus
from life_system.utils.console import console

class ReminderService:
    """提醒服务：处理任务提醒"""
    
    def __init__(self):
        self.bus = EventBus()
        self.db_factory = SessionLocal
    
    def remind_pending_tasks(self, days_threshold: int = 7) -> int:
        """
        提醒长期未更新的 pending 任务
        
        Args:
            days_threshold: 多少天未更新需要提醒，默认7天
        
        Returns:
            提醒的任务数量
        """
        db = self.db_factory()
        count = 0
        try:
            threshold_date = datetime.now() - timedelta(days=days_threshold)
            
            # 查找需要提醒的任务：
            # 1. 状态为 pending
            # 2. 创建时间超过阈值
            # 3. 上次提醒时间超过1天（避免频繁提醒）
            tasks = db.query(Task).filter(
                Task.status == "pending",
                Task.created_at < threshold_date
            ).all()
            
            for task in tasks:
                # 检查是否需要提醒（上次提醒超过1天，或从未提醒过）
                should_remind = False
                if task.last_remind_at is None:
                    should_remind = True
                elif (datetime.now() - task.last_remind_at).days >= 1:
                    should_remind = True
                
                if should_remind:
                    self._send_reminder(task)
                    task.last_remind_at = datetime.now()
                    task.remind_count = (task.remind_count or 0) + 1
                    count += 1
            
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            console.print(f"[red]提醒任务失败: {e}[/red]")
            return 0
        finally:
            db.close()
    
    def _send_reminder(self, task: Task):
        """发送提醒（控制台输出，未来可以扩展为通知）"""
        days_old = (datetime.now() - task.created_at).days
        console.print(
            f"[yellow]⏰ 提醒: 任务 #{task.id} '{task.title}' 已 pending {days_old} 天[/yellow]"
        )
        
        # 发布提醒事件（未来可以扩展为桌面通知、邮件等）
        self.bus.publish(
            type="task.remind",
            source="reminder_service",
            payload={
                "task_id": task.id,
                "task_title": task.title,
                "days_old": days_old,
                "remind_count": task.remind_count or 0
            }
        )
    
    def auto_archive_old_tasks(self, days_threshold: int = 30) -> int:
        """
        自动归档长期未更新的 pending 任务
        
        Args:
            days_threshold: 多少天未更新需要归档，默认30天
        
        Returns:
            归档的任务数量
        """
        db = self.db_factory()
        count = 0
        try:
            threshold_date = datetime.now() - timedelta(days=days_threshold)
            
            tasks = db.query(Task).filter(
                Task.status == "pending",
                Task.created_at < threshold_date
            ).all()
            
            for task in tasks:
                # 归档任务
                old_status = task.status
                task.status = "archived"
                
                # 发布自动归档事件
                self.bus.publish(
                    type="task.auto_archive",
                    source="reminder_service",
                    payload={
                        "task_id": task.id,
                        "task_title": task.title,
                        "days_old": (datetime.now() - task.created_at).days,
                        "from_status": old_status
                    }
                )
                
                # 记录状态流转（通过事件，由 TransitionService 处理）
                self.bus.publish(
                    type="task.status.changed",
                    source="reminder_service",
                    payload={
                        "task_id": task.id,
                        "from_status": old_status,
                        "to_status": "archived",
                        "reason": "auto_archive"
                    }
                )
                
                count += 1
                console.print(f"[yellow]📦 自动归档: 任务 #{task.id} '{task.title}' (已 pending {days_threshold} 天)[/yellow]")
            
            db.commit()
            return count
        except Exception as e:
            db.rollback()
            console.print(f"[red]自动归档失败: {e}[/red]")
            return 0
        finally:
            db.close()

