# LifeOS UI 设计指南 (UI_GUIDE)

本文档专注于 LifeOS 的用户界面 (UI) 与交互设计规范。鉴于系统支持多种交互模式（CLI, TUI, GUI），我们需要统一的设计语言与参数标准。

## 1. 交互模式概览 (Multi-Modal Interaction)

LifeOS 支持三种层级的交互模式，以适应从脚本自动化到桌面使用的不同场景：

| 模式 | 全称 | 技术栈 | 适用场景 | 启动参数 |
| :--- | :--- | :--- | :--- | :--- |
| **CLI** | Command Line Interface | `Typer` + `Rich` | 快速操作、脚本调用、远程 SSH | (默认) |
| **TUI** | Terminal UI | `Textual` | 复杂交互、数据浏览、键盘流操作 | `-t` / `--tui` |
| **GUI** | Graphical User Interface | `Gooey` | 桌面环境、鼠标操作、参数配置 | `-g` / `--gui` |

---

## 2. 参数命名规范

为了保证不同工具间体验的一致性，所有命令必须遵循以下参数命名标准：

### 2.1 系统保留参数
*   `-h`, `--help`: 显示帮助信息 (Typer 自动生成)。
*   `--version`: 显示版本信息。

### 2.2 模式切换参数 (Options)
所有涉及界面切换的命令，必须统一使用以下开关：
*   `--gui` / `-g`: 启动独立窗口 (Gooey)。
*   `--tui` / `-t`: 启动终端图形界面 (Textual)。
*   `--interactive` / `-i`: 启动问答式交互 (Smart Prompt)。
*   `--dry-run`: 仅预览不执行 (用于关键写操作)。

### 2.3 常用筛选器
*   `--status` / `-s`: 状态筛选 (如 `pending`, `done`)。
*   `--limit` / `-n`: 数量限制。
*   `--filter` / `-f`: 关键词过滤。

---

## 3. UI 开发指南

### 3.1 CLI 开发 (Typer + Rich)
*   **原则**: 简洁、多彩、快。
*   **输入**: 使用 `life_system.utils.interaction.smart_prompt` 替代 `input()`。
*   **输出**: 使用 `life_system.utils.console.console` 替代 `print()`。

### 3.2 TUI 开发 (Textual)
*   **位置**: `life_system/interfaces/tui.py` (或独立模块)。
*   **原则**: 键盘优先 (Vim-like 快捷键)。
*   **示例**:
    ```python
    # 在 CLI 中调用 TUI
    if tui:
        from life_system.interfaces.tui import TaskApp
        TaskApp().run()
        return
    ```

### 3.3 GUI 开发 (Gooey)
*   **位置**: `life_system/interfaces/gui.py`。
*   **原则**: 零配置启动。Gooey 适合将复杂的 CLI 参数图形化。
*   **注意**: Gooey 通常需要作为主入口运行，建议通过 `subprocess` 启动以避免环境污染。

---

## 4. 配色方案
*   **Success**: `green`
*   **Warning**: `yellow`
*   **Error**: `red`
*   **Info**: `cyan`
*   **Primary**: `blue` (用于标题、边框)

