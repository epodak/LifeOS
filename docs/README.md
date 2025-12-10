# LifeOS 文档索引

为了保持项目整洁并提供清晰的阅读路径，我们将文档按主题分类并编号。

## 📚 文档分类 (Documentation Map)

### 0xx - 架构与机制 (Architecture & Mechanisms)
理解系统的高层设计和核心运行原理。
- **[001_SYSTEM_MECHANISM.md](001_SYSTEM_MECHANISM.md)**: 系统核心机制（双进程模型、自动化流程）。

### 1xx - 开发规范 (Standards & Guides)
开发者必读，包含代码规范、日志规范和开发流程。
- **[100_DEV_GUIDE.md](100_DEV_GUIDE.md)**: 核心开发指南。

### 2xx - 业务规范 (Feature Specifications)
业务逻辑的定义，不涉及具体代码实现。
- **[200_SPEC_TASK_LIFECYCLE.md](200_SPEC_TASK_LIFECYCLE.md)**: 任务状态流转规范。

### 3xx - 详细设计 (Detailed Design)
特定组件的详细设计文档和使用说明。
- **[300_DESIGN_INGESTION_PIPELINE.md](300_DESIGN_INGESTION_PIPELINE.md)**: 事件摄入管道的设计原理。
- **[301_IMPL_TASK_LIFECYCLE.md](301_IMPL_TASK_LIFECYCLE.md)**: 任务生命周期的代码实现细节。
- **[302_USAGE_INGESTION_PIPELINE.md](302_USAGE_INGESTION_PIPELINE.md)**: 如何在代码中使用 Pipeline。

### 4xx - 用户界面 (UI/UX)
前端交互、CLI、TUI 和 GUI 的设计指南。
- **[400_UI_GUIDE.md](400_UI_GUIDE.md)**: UI 开发与交互指南。

### 9xx - 架构决策记录 (ADR - Architecture Decision Records)
记录关键的技术决策及其背后的原因。
- **[900_ADR_FILE_WATCHER_AND_PIPELINE.md](900_ADR_FILE_WATCHER_AND_PIPELINE.md)**: 引入 Ingestion Pipeline 的决策过程。

