import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from life_system.core.models import Event
from life_system.core.db import SessionLocal

class EventBus:
    """
    事件总线：系统的血管
    
    注意：为了建立"不动点"，建议所有外部输入都通过 IngestionPipeline，
    但为了向后兼容，这里仍然保留直接 publish 的能力。
    """
    def __init__(self, use_pipeline: bool = True):
        self.db_factory = SessionLocal
        self.use_pipeline = use_pipeline
        self._pipeline = None
        
        if use_pipeline:
            # 延迟导入，避免循环依赖
            from life_system.core.ingestion_pipeline import IngestionPipeline
            self._pipeline = IngestionPipeline(debounce_window=1.0)

    def publish(
        self, 
        type: str, 
        source: str, 
        payload: Dict[str, Any],
        bypass_pipeline: bool = False
    ) -> int:
        """
        发布一个新事件到数据库
        
        Args:
            type: 事件类型
            source: 事件来源
            payload: 事件数据
            bypass_pipeline: 是否绕过 Ingestion Pipeline（内部事件使用）
        
        Returns:
            事件ID
        """
        # 如果启用了 pipeline 且不绕过，先通过 pipeline
        if self.use_pipeline and self._pipeline and not bypass_pipeline:
            # 对于内部事件（如 task.analyze），可能需要绕过 pipeline
            # 但对于外部事件（如 file.created），应该通过 pipeline
            if not type.startswith('task.') or source in ['cli', 'file_watcher', 'scheduler']:
                # 传递 _publish_direct 函数，避免循环调用
                event_id = self._pipeline.ingest(type, source, payload, self._publish_direct)
                if event_id is not None:
                    return event_id
                # 如果 pipeline 返回 None（被过滤/去重），直接返回 None
                # 这表示事件被过滤或去重，不应该发布
        
        # 直接发布到数据库（绕过 pipeline 或 pipeline 未启用）
        return self._publish_direct(type, source, payload)
    
    def _publish_direct(self, type: str, source: str, payload: Dict[str, Any]) -> int:
        """直接发布事件到数据库（内部方法）"""
        db = self.db_factory()
        try:
            event = Event(
                type=type,
                source=source,
                payload=payload,
                created_at=datetime.now(),
                processed=False
            )
            db.add(event)
            db.commit()
            db.refresh(event)
            return event.id
        finally:
            db.close()

    def get_unprocessed(self, limit: int = 100) -> List[Event]:
        """获取未处理的事件"""
        db = self.db_factory()
        try:
            return db.query(Event).filter(Event.processed == False).limit(limit).all()
        finally:
            db.close()

    def mark_processed(self, event_id: int):
        """标记事件为已处理"""
        db = self.db_factory()
        try:
            event = db.query(Event).filter(Event.id == event_id).first()
            if event:
                event.processed = True
                db.commit()
        finally:
            db.close()

