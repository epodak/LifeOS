import json
from datetime import datetime
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from life_system.core.models import Event
from life_system.core.db import SessionLocal

class EventBus:
    def __init__(self):
        self.db_factory = SessionLocal

    def publish(self, type: str, source: str, payload: Dict[str, Any]) -> int:
        """发布一个新事件到数据库"""
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

