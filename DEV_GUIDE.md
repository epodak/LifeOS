# LifeOS 架构与开发总纲 (The Master Guide)

本文档是 LifeOS 的核心开发宪章。它统摄全局，定义了系统的架构原则、编码规范以及扩展机制。任何代码提交都必须遵循本指南。

---

## 📚 文档索引 (Doc Index)

LifeOS 的文档体系如下，请按需查阅：

*   **[UI_GUIDE.md](UI_GUIDE.md)**: **UI 与交互设计规范**。包含 CLI 参数命名、Textual/Gooey 界面开发指南。
*   **[SYSTEM_MECHANISM.md](SYSTEM_MECHANISM.md)**: **系统运行机制说明**。解释 `life` 全局命令、`pip install -e` 及入口点原理。
*   **[README.md](README.md)**: **用户使用手册**。面向最终用户的安装与使用说明。

---

## 1. 核心架构：六层同心圆 (The 6-Layer Architecture)

LifeOS 不仅仅是一组脚本，而是一个基于**事件驱动**的解耦系统。我们严格坚持以下六层架构：

| 层级 | 英文 | 职责 | 依赖关系 |
| :--- | :--- | :--- | :--- |
| **1. 采集层** | `Collectors` | 感知世界（文件变化、时间触发、用户输入）。**只产出 Event，绝不写库。** | 依赖 `Core` (EventBus) |
| **2. 事件层** | `Core (Events)` | 系统的血管。定义标准事件格式，分发消息。 | 被所有层依赖 |
| **3. 存储层** | `Storage` | 系统的记忆。数据库 (SQLite) 和文件存储。 | 被 `Core` 定义，被 `Services` 调用 |
| **4. 分析层** | `Engines` | 系统的“脑”。AI 分析、相似度计算、规则判断。**纯函数式，无副作用。** | 独立，或依赖 `Core` (Models) |
| **5. 服务层** | `Services` | 系统的手。**消费 Event**，编排逻辑，调用 `Storage`。 | 依赖 `Core`, `Storage`, `Engines` |
| **6. 交互层** | `Interfaces` | 系统的脸。CLI/TUI/GUI。**只调用 Service 或发布 Event**。 | 依赖 `Services` |

**架构铁律**：
> ❌ **禁止** `Interface` 直接操作 `Storage` (必须通过 `Service`)。
> ❌ **禁止** `Collector` 直接调用 `Service` (必须通过 `EventBus`)。

---

## 2. 编码规范与最佳实践 (Code Standards)

本系统集成了 Python 开发的现代最佳实践，请严格遵守。

### 2.1 文件与路径 (File I/O)
*   **编码**: 所有文件读写必须显式指定 `encoding='utf-8'`。
*   **路径**: 严禁字符串拼接路径。必须使用 `pathlib.Path`。
    ```python
    # ✅ 正确
    from pathlib import Path
    data_path = Path(__file__).parent / "data.json"
    
    # ❌ 错误
    data_path = os.path.dirname(__file__) + "\\data.json"
    ```
*   **原子化写入**: 涉及关键数据保存时，应采用“写临时文件 -> 重命名”的原子操作，防止断电导致文件损坏。（参考 `life_system.utils.io`）

### 2.2 交互与输入 (Interaction)
*   **禁止原生 Input**: 严禁在代码中使用 `input()` 或 `print()` 进行交互。
*   **统一入口**: 必须使用 `life_system.utils.interaction` 模块。
    *   **智能提示**: 使用 `smart_prompt` (支持 Tab 补全、模糊匹配)。
    *   **安全确认**: 使用 `safe_confirm` (优雅处理 Ctrl+C)。
    *   *原理参考*: `python交互式输入.txt`, `python参数补全.txt`

### 2.3 进程管理 (Process Separation)
*   **后台任务**: 对于监控、定时任务，必须实现**进程分离**，确保父进程退出后子进程存活。
*   **工具**: 使用 `life_system.utils.process.detach_and_run`。
    *   *原理参考*: `python进程分离.txt`

### 2.4 日志与输出 (Logging & Output)
*   **用户可见**: 使用 `life_system.utils.console.console.print` (Rich 格式化)。
*   **系统调试**: 使用 `loguru` (未来集成到 `utils.logger`)。

---

## 3. 开发流程指南 (How to Develop)

### 3.1 场景：添加一个新功能 "灵感记录"

1.  **定义数据 (Core)**:
    在 `life_system/core/models.py` 中添加 `Idea` 表模型。

2.  **实现服务 (Service)**:
    在 `life_system/services/idea_service.py` 中编写 `create_idea` 逻辑。

3.  **实现交互 (Interface)**:
    在 `life_system/interfaces/tools/idea.py` (新建) 中编写 Typer 命令：
    ```python
    @app.command()
    def add():
        content = smart_prompt("灵感内容")
        Service().create_idea(content)
    ```

4.  **注册命令**:
    在 `life_system/interfaces/cli.py` 中注册 `idea` 子命令。

### 3.2 场景：开发一个独立 GUI 工具
直接在 `life_system/interfaces/` 下创建一个新的 GUI 入口脚本（如 `cal_gui.py`），使用 `Gooey` 装饰，然后在 CLI 中通过 `subprocess` 调用它。

---

## 4. 常用工具库速查 (Utils Reference)

| 模块 | 导入路径 | 核心功能 |
| :--- | :--- | :--- |
| **交互** | `life_system.utils.interaction` | `smart_prompt(text, completions=...)`, `safe_confirm(text)` |
| **输出** | `life_system.utils.console` | `console.print()`, `console.rule()` |
| **进程** | `life_system.utils.process` | `detach_and_run()` |
| **配置** | `life_system.config.settings` | `DB_PATH`, `PROJECT_ROOT` |

---

> **核心精神**：LifeOS 是一个长期生长的系统。不要写死代码，要写可进化、可插拔的模块。
