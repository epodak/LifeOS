# Ingestion Pipeline 使用指南

## 核心原则

**所有外部输入（CLI、文件监控、定时触发）都必须通过 Ingestion Pipeline 才能进入系统。**

## 使用方式

### 方式 1：通过 EventBus（推荐，自动使用 Pipeline）

EventBus 已经集成了 Ingestion Pipeline，默认启用：

```python
from life_system.core.event_bus import EventBus

bus = EventBus()  # 默认启用 pipeline

# 外部事件（会自动通过 pipeline）
bus.publish("file.created", "file_watcher", {"path": "file.py"})
bus.publish("task.created", "cli", {"title": "优化lifeOS"})

# 内部事件（可以绕过 pipeline）
bus.publish("task.analyze", "task_service", {"task_id": 1}, bypass_pipeline=True)
```

### 方式 2：直接使用 IngestionPipeline（高级用法）

如果你需要更细粒度的控制：

```python
from life_system.core.ingestion_pipeline import IngestionPipeline
from life_system.core.event_bus import EventBus

pipeline = IngestionPipeline(debounce_window=1.0)
bus = EventBus(use_pipeline=False)  # 禁用 EventBus 的自动 pipeline

# 通过 pipeline 摄入
event_id = pipeline.ingest(
    "file.created",
    "file_watcher",
    {"path": "/path/to/file.py"},
    bus._publish_direct  # 传递发布函数
)
```

## 在 Collector 中使用

### 文件监控 Collector（未来实现）

```python
# life_system/collectors/file_watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from life_system.core.event_bus import EventBus

class LifeOSFileHandler(FileSystemEventHandler):
    def __init__(self):
        self.bus = EventBus()  # 自动使用 pipeline
    
    def on_created(self, event):
        if not event.is_directory:
            # 通过 EventBus 发布，会自动经过 pipeline
            self.bus.publish(
                "file.created",
                "file_watcher",
                {"path": event.src_path}
            )
    
    def on_modified(self, event):
        if not event.is_directory:
            # 多次修改会被 pipeline 防抖
            self.bus.publish(
                "file.modified",
                "file_watcher",
                {"path": event.src_path}
            )
```

### CLI Collector（已实现）

```python
# life_system/services/task_service.py
class TaskService:
    def __init__(self):
        self.bus = EventBus()  # 自动使用 pipeline
    
    def create_task_event(self, title: str) -> int:
        # 通过 EventBus 发布，会自动经过 pipeline
        return self.bus.publish(
            type="task.created",
            source="cli",
            payload={"title": title}
        )
```

## 防抖示例

假设 VSCode 保存文件时触发了多次事件：

```python
# 14:30:00.100 - 第一次修改
bus.publish("file.modified", "file_watcher", {"path": "file.py"})
# → 进入 pipeline，缓存，不发布

# 14:30:00.200 - 第二次修改（0.1秒后）
bus.publish("file.modified", "file_watcher", {"path": "file.py"})
# → 进入 pipeline，更新缓存，不发布

# 14:30:00.300 - 第三次修改（0.1秒后）
bus.publish("file.modified", "file_watcher", {"path": "file.py"})
# → 进入 pipeline，更新缓存，不发布

# 14:30:01.100 - 时间窗口结束（1秒后）
# → pipeline 自动发布最后一个事件
```

结果：只发布一次 `file.modified` 事件，而不是三次。

## 过滤示例

```python
# 这些事件会被自动过滤，不会进入系统
bus.publish("file.created", "file_watcher", {"path": ".git/config"})  # ❌ 过滤
bus.publish("file.created", "file_watcher", {"path": "__pycache__/file.pyc"})  # ❌ 过滤
bus.publish("file.created", "file_watcher", {"path": "node_modules/package.json"})  # ❌ 过滤

# 这些事件会通过
bus.publish("file.created", "file_watcher", {"path": "src/main.py"})  # ✅ 通过
bus.publish("file.created", "file_watcher", {"path": "README.md"})  # ✅ 通过
```

## 去重示例

```python
# 第一次发布
bus.publish("task.created", "cli", {"title": "优化lifeOS"})  # ✅ 发布，ID=1

# 完全相同的事件（可能是重复提交）
bus.publish("task.created", "cli", {"title": "优化lifeOS"})  # ❌ 去重，返回 None
```

## 标准化示例

```python
# 输入：相对路径
bus.publish("file.created", "file_watcher", {"path": "src/file.py"})

# Pipeline 标准化后：
{
    "path": "/absolute/path/to/src/file.py",  # 绝对路径
    "path_parts": ["/", "absolute", "path", "to", "src", "file.py"],
    "is_file": True,
    "is_dir": False,
    "timestamp": "2025-12-10T14:30:00.123456"
}
```

## 配置 Pipeline

### 调整防抖窗口

```python
from life_system.core.event_bus import EventBus
from life_system.core.ingestion_pipeline import IngestionPipeline

# 创建自定义 pipeline（防抖窗口 2 秒）
pipeline = IngestionPipeline(debounce_window=2.0)

# 在 EventBus 中使用（需要修改 EventBus 的初始化）
# 或者直接使用 pipeline.ingest()
```

### 添加自定义过滤规则

修改 `life_system/core/ingestion_pipeline.py` 中的 `FILTER_PATTERNS`：

```python
FILTER_PATTERNS = {
    # ... 现有规则
    '*.custom',  # 添加自定义模式
    'custom_dir',
}
```

## 注意事项

1. **内部事件**：系统内部生成的事件（如 `task.analyze`）可以使用 `bypass_pipeline=True` 绕过 pipeline
2. **线程安全**：Pipeline 是线程安全的，可以在多线程环境中使用
3. **性能**：Pipeline 使用内存缓存，重启后会丢失防抖状态（这是预期的）
4. **去重持久化**：如果需要跨重启去重，需要将 `_seen_hashes` 持久化到数据库（未来扩展）

