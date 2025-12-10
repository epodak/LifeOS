# LifeOS 开发规范与扩展指南

本文档旨在为 LifeOS 的持续迭代和小工具开发提供统一的标准。基于 "LifeOS MVP" 架构，结合最佳实践（Python 脚本规范、交互式输入、进程分离等），确保系统的高内聚、低耦合与易用性。

详细的 UI 与交互设计规范，请参考 [UI_GUIDE.md](UI_GUIDE.md)。

## 1. 系统迭代原则

### 1.1 六层架构的坚持
在扩展功能时，必须严格遵守六层架构的分层职责，严禁跨层调用：

*   **Collectors (采集层)**: 只负责感知外部变化（CLI, 文件监控, 定时器），**只产出 Event**，绝不直接写数据库或调用 Service。
*   **Core (核心层)**: 定义数据模型 (Models) 和 基础组件 (EventBus, DB)。所有层都依赖它，但它不依赖任何层。
*   **Services (服务层)**: 核心业务逻辑所在。**消费 Event**，操作 DB。是连接 EventBus 和 Storage 的桥梁。
*   **Engines (引擎层)**: 纯计算/分析单元（如 AI 分析、相似度计算）。输入数据 -> 输出结果，不直接副作用于 DB。
*   **Interfaces (交互层)**: CLI 或 Web UI。**只调用 Service** 或 **发布 Event**，绝不直接操作 DB。
*   **Storage (存储层)**: 数据库实际读写。由 Core 定义模型，Service 进行调用。

### 1.2 迭代流程 (The "LifeOS Way")
1.  **定义事件**: 在 `core/events.py` (或逻辑上) 定义新的事件类型，如 `file.created`, `note.added`。
2.  **实现采集**: 编写 Collector (如 `collectors/fs_watcher.py`)，检测变化并 `bus.publish()` 事件。
3.  **编写服务**: 在 `services/` 下编写逻辑，订阅并处理该事件 (如 `TaskIntakeService`)。
4.  **暴露接口**: 在 `interfaces/cli.py` 中添加命令，方便手动触发或调试。

---

## 2. 小工具开发规范

LifeOS 的“小工具”应该是 **可独立使用的 CLI 命令**，同时 **复用 LifeOS 的核心能力**。

### 2.1 脚本头部与编码
所有新建 Python 文件必须包含：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Description: 模块/工具描述
"""
```

### 2.2 路径与环境处理
使用 `pathlib` 处理路径，严禁硬编码分隔符。

```python
from pathlib import Path

# 获取项目根目录 (基于本文件位置)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 路径拼接
data_file = PROJECT_ROOT / "data" / "config.json"
```

### 2.3 交互式输入 (Smart Prompt)
为了统一体验，LifeOS 的所有用户输入必须使用 `life_system.utils.interaction` 模块。

**严禁使用 Python 原生 `input()`。**

```python
from life_system.utils.interaction import smart_prompt, safe_confirm

def create_project_tool():
    name = smart_prompt("请输入项目名称", completions=["LifeOS", "Work", "Personal"])
    if not name: return

    if safe_confirm(f"确认创建项目 '{name}'?"):
        # ... call service ...
        pass
```

### 2.4 命令行参数 (Typer + Rich)
LifeOS 全面使用 `Typer` 构建 CLI，配合 `Rich` 进行美化输出。

*   **命令定义**: 使用 `typer` 装饰器。
*   **帮助信息**: Docstring 会自动转为帮助文档。
*   **输出**: 使用全局 `console` 对象。

```python
import typer
from life_system.utils.console import console # 全局 console 单例

app = typer.Typer()

@app.command()
def sync(
    dry_run: bool = typer.Option(False, "--dry-run", help="仅预览，不执行写操作")
):
    """
    同步数据到云端。
    """
    if dry_run:
        console.print("[yellow]DRY RUN: 正在模拟同步...[/yellow]")
        return
    
    # ...
```

### 2.5 进程分离 (后台任务)
对于需要长时间运行或在后台执行的任务（如启动监控器），必须使用标准的进程分离技术。

参考 `life_system/utils/process.py` 中的 `detach_and_run` 装饰器或函数。

---

## 3. 核心工具库 (Utils) 设计

为了支撑上述规范，我们需要在 `life_system/utils/` 下完善以下基础设施：

### 3.1 `life_system/utils/console.py`
统一的 Rich Console 实例。

```python
from rich.console import Console
console = Console()
```

### 3.2 `life_system/utils/interaction.py`
封装 `prompt_toolkit`，提供 `smart_prompt` 和 `safe_confirm`。

### 3.3 `life_system/utils/process.py`
封装跨平台进程分离逻辑。

### 3.4 `life_system/utils/logger.py`
基于 `loguru` 的统一日志配置。

---

## 4. 如何开发并注册一个小工具

假设你要开发一个“快速记录灵感”的小工具 `idea`。

**Step 1: 编写逻辑**
在 `life_system/interfaces/tools/idea.py` (新建目录) 中编写 Typer 应用。

```python
import typer
from life_system.core.event_bus import EventBus
from life_system.utils.interaction import smart_prompt

app = typer.Typer()

@app.command()
def add():
    """快速记录一个灵感"""
    content = smart_prompt("你的灵感是什么?")
    if content:
        EventBus().publish("idea.created", "cli", {"content": content})
        print("灵感已捕获!")
```

**Step 2: 注册命令**
在 `life_system/interfaces/cli.py` 中挂载这个子命令。

```python
from life_system.interfaces.tools import idea
app.add_typer(idea.app, name="idea", help="灵感管理工具")
```

**Step 3: 使用**
直接在终端运行：
```bash
life idea add
```

---

## 5. 总结

*   **架构**: 坚守六层，Event 驱动。
*   **交互**: 必须用 `smart_prompt` 和 `Rich`。
*   **后台**: 必须用 `detach_and_run`。
*   **入口**: 统一通过 `life` 命令扩展子命令。

这份规范旨在让你的 LifeOS 既像一个严谨的工程，又像一系列顺手的小脚本集合。
