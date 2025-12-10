# Event Ingestion Pipeline 设计文档

## 核心概念：重整化不动点

**不动点定义**：无论外部世界的输入（文件变动、CLI输入、时间触发）多么嘈杂和频繁，系统内部都存在一个稳定的结构，能够将这些输入"坍缩"为标准化的、有限的"元任务"。

## 架构调整

### 旧架构（发散）
```
Collector -> EventBus -> Service
```

### 新架构（收敛到不动点）
```
Collector -> Ingestion Pipeline (不动点) -> EventBus -> Service
```

## Ingestion Pipeline 的职责

### 1. 防抖 (Debounce)
**问题**：VSCode 保存一次文件可能触发 5-10 次 `modified` 事件

**解决方案**：
- 同一路径的事件在时间窗口内（默认1秒）只保留最后一个
- 使用 `event_key` 识别同一资源的不同事件
- 时间窗口内的重复事件被缓存，窗口结束后发布最后一个

**示例**：
```
14:30:00.100 - file.modified: /path/to/file.py  (缓存)
14:30:00.200 - file.modified: /path/to/file.py  (缓存，替换上一个)
14:30:00.300 - file.modified: /path/to/file.py  (缓存，替换上一个)
14:30:01.100 - 时间窗口结束，发布最后一个事件
```

### 2. 过滤 (Filter)
**问题**：`.git`, `__pycache__`, 临时文件等不应该触发任务

**解决方案**：
- 维护过滤模式列表
- 文件事件检查路径是否匹配过滤模式
- 匹配的事件直接丢弃，不进入系统

**过滤规则**：
- 版本控制：`.git`, `.svn`, `.hg`
- Python：`__pycache__`, `*.pyc`, `.pytest_cache`
- 编辑器：`.vscode`, `.idea`, `*.swp`
- 系统文件：`.DS_Store`, `Thumbs.db`
- 临时文件：`*.tmp`, `*.temp`, `*.log`
- Node：`node_modules`

### 3. 标准化 (Normalize)
**问题**：不同来源的事件格式不一致

**解决方案**：
- 统一事件 payload 格式
- 文件事件：路径标准化为绝对路径，添加元数据
- 所有事件：添加时间戳（如果不存在）

**标准化后的格式**：
```python
{
    "path": "/absolute/path/to/file.py",  # 绝对路径
    "path_parts": ["/", "absolute", "path", "to", "file.py"],
    "is_file": True,
    "is_dir": False,
    "timestamp": "2025-12-10T14:30:00.123456"
}
```

### 4. 去重 (Deduplication)
**问题**：完全相同的事件可能被多次发布

**解决方案**：
- 计算事件的 MD5 哈希
- 维护已处理事件的哈希集合
- 相同哈希的事件直接丢弃

## 使用方式

### 在 Collector 中使用

**旧方式（错误）**：
```python
# ❌ 直接调用 EventBus
from life_system.core.event_bus import EventBus
bus = EventBus()
bus.publish("file.created", "file_watcher", {"path": "file.py"})
```

**新方式（正确）**：
```python
# ✅ 通过 Ingestion Pipeline
from life_system.core.ingestion_pipeline import IngestionPipeline
from life_system.core.event_bus import EventBus

pipeline = IngestionPipeline(debounce_window=1.0)
bus = EventBus()

pipeline.ingest("file.created", "file_watcher", {"path": "file.py"}, bus)
```

### 在 CLI 中使用

**旧方式**：
```python
# TaskService.create_task_event 直接调用 bus.publish
```

**新方式**：
```python
# TaskService 应该通过 pipeline.ingest
# 但为了向后兼容，可以在 EventBus.publish 内部调用 pipeline
# 或者让 TaskService 显式使用 pipeline
```

## 架构位置

根据六层架构，Ingestion Pipeline 属于 **Core 层**：

```
1. 采集层 (Collectors) - 调用 pipeline.ingest()
2. 事件层 (Core)
   ├─ Ingestion Pipeline (不动点) ← 新增
   └─ EventBus
3. 存储层 (Storage)
4. 分析层 (Engines)
5. 服务层 (Services)
6. 交互层 (Interfaces)
```

## 线程安全

Ingestion Pipeline 使用 `threading.Lock` 确保线程安全，可以安全地在多线程环境中使用（如文件监控线程 + 主事件循环）。

## 性能考虑

1. **内存管理**：定期清理过期的缓存项（超过防抖窗口2倍的时间）
2. **哈希集合**：使用 `set` 实现 O(1) 的去重检查
3. **缓存大小**：理论上限是时间窗口内的唯一事件数，实际使用中应该很小

## 未来扩展

1. **配置化**：过滤规则可以从配置文件加载
2. **统计**：记录过滤、去重、防抖的事件数量
3. **优先级**：某些事件类型可以绕过防抖（如 `task.created`）
4. **持久化**：去重哈希可以持久化到数据库，避免重启后重复处理

