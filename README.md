# LifeOS MVP (任务闭环版)

这是一个基于"六层架构"设计的个人生活管理系统最小可行性产品 (MVP)。
目前的版本专注于解决 **"任务有始无终"** 的痛点，通过强制的状态流转和后台自动处理，确保每个任务都有明确的结局。

## 架构说明

项目遵循以下分层结构：

- **collectors/**: 采集层 (目前只有 CLI 输入)
- **core/**: 核心层 (DB模型, EventBus)
- **services/**: 服务层 (业务逻辑, 如将事件转为任务)
- **interfaces/**: 交互层 (CLI 命令)
- **engines/**: 分析层 (暂留空，未来放 AI 分析)
- **storage/**: 存储层 (SQLite, 由 core/db.py 管理)

## 快速开始

### 1. 环境准备

确保你已激活常用的 Conda 环境 (如 AI 环境)。

```bash
# 直接安装依赖到当前 Conda 环境
pip install -r life_system/requirements.txt
```

### 2. 初始化

```bash
python main.py init
```

### 3. 启动后台服务 (推荐)

在一个单独的终端窗口中运行，它会自动处理新任务事件：

```bash
python main.py serve
```

### 4. 日常使用

在主终端中：

```bash
# 1. 添加任务 (这会发布一个事件，后台服务会自动将其转为任务)
python main.py add "完成系统设计文档"

# 2. 查看待办任务
python main.py list

# 3. 完成任务
python main.py done <ID>

# 4. 放弃任务 (显式放弃，而不是把任务晾在一边)
python main.py drop <ID>
```

## 核心逻辑

1. **解耦**: `add` 命令并不直接写任务表，而是发布一个 `task.created` 事件。
2. **自动化**: `serve` 进程监听这些事件，并将其转换为具体的 Task 记录。
3. **闭环**: 任务状态只能流转为 `done` (完成) 或 `dropped` (放弃)，没有无限期的 "pending"。

## 后续计划

- [ ] 接入 Watchdog 实现文件新建自动监控
- [ ] 接入 LLM 分析新建文件的内容
- [ ] 每日回顾 (Review) 功能

