# 开发指南 (Development Guide)

## 1. 核心架构：六层同心圆
（参见 [001_SYSTEM_MECHANISM.md](001_SYSTEM_MECHANISM.md)）

## 2. 编码规范

### 2.1 日志规范 (Logging Standards) **[NEW]**

LifeOS 使用 `loguru` 作为统一的日志后端。**严禁**在核心逻辑中使用 `print`，必须使用 `logger`。

*   **导入**: `from life_system.utils.logger import logger`
*   **级别使用**:
    *   `logger.debug()`: 开发调试信息（如：Pipeline 过滤了某个文件，防抖触发）。
    *   `logger.info()`: 关键业务节点（如：服务启动，任务创建成功，Event 成功入库）。
    *   `logger.warning()`: 非预期但可恢复的问题（如：配置文件缺失使用默认值）。
    *   `logger.error()`: 导致当前操作失败的错误（如：数据库连接失败，Event 发布异常）。
    *   `logger.exception()`: 在 `except` 块中使用，自动记录堆栈信息。

*   **UI 输出**:
    *   CLI 交互仍然使用 `life_system.utils.console.console.print`，但这仅限于**直接反馈给用户**的信息。
    *   后台服务 (`life serve`) 的输出应主要依赖日志文件，屏幕输出仅作为辅助状态显示。

### 2.2 文件操作
... (原有内容)
