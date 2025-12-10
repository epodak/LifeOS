# LifeOS MVP (任务闭环版)

这是一个基于"六层架构"设计的个人生活管理系统最小可行性产品 (MVP)。
目前的版本专注于解决 **"任务有始无终"** 的痛点，通过强制的状态流转和后台自动处理，确保每个任务都有明确的结局。

详细文档：
- [DEV_GUIDE.md](DEV_GUIDE.md): 开发规范与扩展指南
- [UI_GUIDE.md](UI_GUIDE.md): UI 设计与交互指南
- [SYSTEM_MECHANISM.md](SYSTEM_MECHANISM.md): `life` 命令运行原理说明

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
