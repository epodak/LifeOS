from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey
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
    
    # 任务元数据（由分析引擎和增强服务填充）
    tags = Column(JSON, default=list)  # 标签列表，如 ["优化", "开发"]
    category = Column(String)           # 分类，如 "开发/维护"
    priority = Column(String, default="medium")  # low, medium, high
    related_task_ids = Column(JSON, default=list)  # 关联的相似任务ID列表
    
    # 提醒和归档相关
    last_remind_at = Column(DateTime)  # 上次提醒时间
    remind_count = Column(Integer, default=0)  # 提醒次数
    
    # 可扩展字段
    deadline = Column(DateTime)        # 截止日期
    project_id = Column(Integer)       # 所属项目ID（未来扩展）

class TaskTransition(Base):
    """记录任务状态流转历史，确保任务有明确的结局"""
    __tablename__ = "task_transitions"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), index=True)
    from_status = Column(String)       # 原状态
    to_status = Column(String)         # 新状态
    reason = Column(String)             # 变更原因，如 "user_action", "auto_archive", "remind"
    created_at = Column(DateTime, default=datetime.now)
    extra_data = Column(JSON)            # 额外的元数据，如提醒内容、自动归档原因等

