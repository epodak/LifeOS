# 开发指南 (Development Guide)

本文档为 LifeOS 的开发者提供架构原则、编码规范和最佳实践指南。

## 1. 核心架构：六层同心圆

LifeOS 遵循严格的分层架构（Onion Architecture），旨在实现高内聚、低耦合。

**依赖原则 (The Dependency Rule)**：源码依赖方向只能是**由外向内**。内层不得了解外层的任何细节。

### 1.1 层级定义

1.  **Core (核心层)**
    *   **位置**: `life_system/core/`
    *   **职责**: 定义全系统通用的数据结构 (Models)、通信协议 (EventBus) 和核心机制 (IngestionPipeline)。
    *   **依赖**: **零依赖**。它不依赖任何其他层。

2.  **Storage (存储层)**
    *   **位置**: `life_system/core/db.py` (目前简化在 core 中，逻辑上独立)
    *   **职责**: 数据的持久化存储 (SQLite/SQLAlchemy)。
    *   **依赖**: 依赖 Core (Models)。

3.  **Engines (引擎层)**
    *   **位置**: `life_system/engines/`
    *   **职责**: 纯粹的计算逻辑、AI 分析、相似度计算。无状态。
    *   **依赖**: 依赖 Core。

4.  **Collectors (采集层)**
    *   **位置**: `life_system/collectors/`
    *   **职责**: 监听外部世界（文件、网络、时间），将信号转化为标准的 `Event`。
    *   **依赖**: 依赖 Core (EventBus, Pipeline)。**不依赖 Service**。

5.  **Services (服务层)**
    *   **位置**: `life_system/services/`
    *   **职责**: 业务逻辑的编排者。它协调 Engines、Storage 和 Core 来完成具体的业务用例（如“创建任务”、“完成任务”）。
    *   **依赖**: 依赖 Core, Engines, Storage。

6.  **Interfaces (交互层)**
    *   **位置**: `life_system/interfaces/`
    *   **职责**: 与用户交互的界面 (CLI, TUI, GUI)。负责接收输入并显示输出。
    *   **依赖**: 依赖 Services。**不应包含业务逻辑**。

---

## 2. 编码规范 (Coding Standards)

### 2.1 日志规范 (Logging)
*   **原则**: 系统运行状态必须可追溯。
*   **工具**: `loguru`
*   **规范**:
    *   **严禁**在核心逻辑中使用 `print`。
    *   使用 `from life_system.utils.logger import logger`。
    *   `logger.debug()`: 开发细节 (Pipeline 过滤, 锁获取)。
    *   `logger.info()`: 关键业务状态 (Service 启动, 任务状态变更)。
    *   `logger.error()`: 操作失败 (DB 错误, 异常捕获)。
*   **UI 输出**: 仅在 `interfaces/` 层使用 `console.print` (Rich) 向用户展示直接结果。

### 2.2 文件与路径 (File I/O)
*   **原则**: 跨平台兼容。
*   **工具**: `pathlib`
*   **规范**:
    *   **严禁**使用 `os.path.join` 或字符串拼接路径。
    *   **必须**使用 `pathlib.Path` 对象。
    *   示例: `Path.home() / "LifeOS" / "data.json"`。
    *   文件读写必须显式指定编码: `open(..., encoding='utf-8')`。

### 2.3 交互体验 (Interaction)
*   **原则**: 统一、友好、健壮。
*   **工具**: `life_system.utils.interaction` (基于 `prompt_toolkit` 和 `rich`)
*   **规范**:
    *   使用 `smart_prompt` 获取用户输入（支持历史记录、自动补全）。
    *   使用 `safe_confirm` 进行危险操作确认。
    *   捕获 `KeyboardInterrupt` (Ctrl+C) 并优雅退出，而不是打印堆栈。

### 2.4 类型提示 (Type Hinting)
*   所有函数和方法**必须**包含 Python 类型提示 (Type Hints)。
*   使用 `typing` 模块 (`List`, `Dict`, `Optional`, `Any` 等)。

---

## 3. 开发流程指南 (Development Flow)

### 3.1 如何添加一个新的命令 (CLI)
1.  **Service**: 在 `life_system/services/` 中实现业务逻辑。
2.  **Interface**: 在 `life_system/interfaces/cli.py` 中添加 `app.command()`。
3.  **Call**: 接口层仅负责解析参数，调用 Service 方法，并打印结果。

### 3.2 如何添加一个新的收集器 (Collector)
1.  **Create**: 在 `life_system/collectors/` 下新建文件 (如 `email_listener.py`)。
2.  **Implement**: 实现收集逻辑，确保有 `start()` 和 `stop()` 方法。
3.  **Ingest**: **必须**通过 `IngestionPipeline` 提交数据，严禁直接写入数据库。
4.  **Register**: 在 `CollectorManager` 中注册该收集器。

### 3.3 如何修改核心模型 (Models)
1.  修改 `life_system/core/models.py`。
2.  **注意**: MVP 阶段使用 `init_db` 自动建表，但生产环境需要引入 Alembic 进行数据库迁移。如修改了表结构，目前建议使用 `life init -f` 重置数据库（数据会丢失，仅限开发期）。
