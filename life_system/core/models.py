from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON
from life_system.core.db import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)  # e.g., "task.created"
    source = Column(String)            # e.g., "cli", "watcher"
    payload = Column(JSON)             # 具体的事件数据
    created_at = Column(DateTime, default=datetime.now)
    processed = Column(Boolean, default=False)

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    status = Column(String, default="pending")  # pending, done, dropped, archived
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    # 可以在此添加更多字段：deadline, project_id, tags 等

