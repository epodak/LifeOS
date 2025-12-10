# LifeOS MVP (任务闭环版)

这是一个基于"六层架构"设计的个人生活管理系统最小可行性产品 (MVP)。
目前的版本专注于解决 **"任务有始无终"** 的痛点，通过强制的状态流转和后台自动处理，确保每个任务都有明确的结局。

## 📖 核心文档

文档已迁移至 `docs/` 目录，分类如下：

- **0xx 架构机制**: [系统运行机制](docs/001_SYSTEM_MECHANISM.md)
- **1xx 开发规范**: [开发指南](docs/100_DEV_GUIDE.md)
- **2xx 业务逻辑**: [任务生命周期规范](docs/200_SPEC_TASK_LIFECYCLE.md)
- **3xx 详细设计**: [Ingestion Pipeline 设计](docs/300_DESIGN_INGESTION_PIPELINE.md)
- **4xx 用户界面**: [UI 设计指南](docs/400_UI_GUIDE.md)
- **9xx 决策记录**: [ADR: Pipeline 架构决策](docs/900_ADR_FILE_WATCHER_AND_PIPELINE.md)

## 快速开始

### 1. 环境准备

确保你已激活常用的 Conda 环境 (如 AI 环境)。

```bash
# 直接安装依赖到当前 Conda 环境
pip install -r life_system/requirements.txt

# 以可编辑模式安装 life 命令
pip install -e .
```

### 2. 初始化

```bash
# 初始化数据库
life init

# 如果需要删除旧数据重新开始
life init -f
```

### 3. 使用

```bash
# 添加任务 (交互式)
life add

# 添加任务 (独立弹窗)
life add -g

# 查看任务列表 (文本)
life list

# 查看任务列表 (全屏 TUI)
life list -u

# 完成任务
life done <ID>
```
