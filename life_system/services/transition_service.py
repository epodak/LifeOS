"""
状态流转服务 (Transition Service)
记录任务状态变更历史，确保任务有明确的"结局"
"""
from datetime import datetime
from sqlalchemy.orm import Session
from life_system.core.models import Task, TaskTransition
from life_system.core.db import SessionLocal
from life_system.utils.console import console

class TransitionService:
    """状态流转服务：记录任务状态变更历史"""
    
    def __init__(self):
        self.db_factory = SessionLocal
    
    def record_transition(
        self, 
        task_id: int, 
        from_status: str, 
        to_status: str, 
        reason: str = "user_action",
        metadata: dict = None
    ) -> bool:
        """
        记录任务状态流转
        
        Args:
            task_id: 任务ID
            from_status: 原状态
            to_status: 新状态
            reason: 变更原因，如 "user_action", "auto_archive", "remind"
            metadata: 额外的元数据
        """
        db = self.db_factory()
        try:
            transition = TaskTransition(
                task_id=task_id,
                from_status=from_status,
                to_status=to_status,
                reason=reason,
                extra_data=metadata or {},
                created_at=datetime.now()
            )
            db.add(transition)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            console.print(f"[red]记录状态流转失败: {e}[/red]")
            return False
        finally:
            db.close()
    
    def get_task_history(self, task_id: int) -> list:
        """获取任务的状态流转历史"""
        db = self.db_factory()
        try:
            transitions = db.query(TaskTransition).filter(
                TaskTransition.task_id == task_id
            ).order_by(TaskTransition.created_at).all()
            return transitions
        finally:
            db.close()

