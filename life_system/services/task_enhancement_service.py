"""
任务增强服务 (Task Enhancement Service)
基于分析引擎的结果，更新任务的元数据
"""
from typing import Dict, Any
from sqlalchemy.orm import Session
from life_system.core.models import Task
from life_system.core.db import SessionLocal
from life_system.core.event_bus import EventBus
from life_system.utils.console import console

class TaskEnhancementService:
    """任务增强服务：基于分析结果更新任务元数据"""
    
    def __init__(self):
        self.bus = EventBus()
        self.db_factory = SessionLocal
    
    def enhance_task(self, task_id: int, analysis_result: Dict[str, Any]) -> bool:
        """
        基于分析结果增强任务
        
        Args:
            task_id: 任务ID
            analysis_result: 分析引擎返回的结果
                {
                    "keywords": List[str],
                    "category": str,
                    "priority": str,
                    "suggested_tags": List[str],
                    "similar_tasks": List[Tuple[int, float]]  # 可选
                }
        """
        db = self.db_factory()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return False
            
            # 更新任务元数据
            if "suggested_tags" in analysis_result:
                task.tags = analysis_result["suggested_tags"]
            if "category" in analysis_result:
                task.category = analysis_result["category"]
            if "priority" in analysis_result:
                task.priority = analysis_result["priority"]
            if "similar_tasks" in analysis_result:
                # 只保留相似度最高的前3个任务
                similar = analysis_result["similar_tasks"][:3]
                task.related_task_ids = [task_id for task_id, _ in similar]
            
            db.commit()
            
            # 发布任务增强完成事件
            self.bus.publish(
                type="task.enhanced",
                source="task_enhancement_service",
                payload={"task_id": task_id, "enhancements": analysis_result}
            )
            
            console.print(f"[cyan]任务 #{task_id} 已增强: {analysis_result.get('category', 'N/A')}, {analysis_result.get('priority', 'N/A')}[/cyan]")
            return True
        except Exception as e:
            db.rollback()
            console.print(f"[red]增强任务失败: {e}[/red]")
            return False
        finally:
            db.close()

