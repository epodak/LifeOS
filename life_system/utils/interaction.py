import sys
from typing import List, Optional
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter, FuzzyCompleter, PathCompleter
from prompt_toolkit.styles import Style
from rich.prompt import Confirm
from life_system.utils.console import console

def smart_prompt(
    prompt_text: str,
    completions: Optional[List[str]] = None,
    completer_type: str = 'fuzzy',  # 'word', 'fuzzy', 'path'
    default: str = "",
) -> Optional[str]:
    """
    一个支持自动补全的、用户友好的输入提示函数。
    基于 prompt_toolkit 实现，支持模糊匹配。
    """
    completer = None
    if completer_type == 'path':
        completer = PathCompleter()
    elif completions:
        if completer_type == 'fuzzy':
            completer = FuzzyCompleter(WordCompleter(completions, ignore_case=True))
        elif completer_type == 'word':
            completer = WordCompleter(completions, ignore_case=True)

    # 简单的 prompt_toolkit 样式
    style = Style.from_dict({
        '': '#ansicyan',
        'prompt': '#ansigreen bold',
    })
    
    # 组合提示文本
    # 注意：prompt_toolkit 的 prompt 函数接受一个 (style, text) 元组列表作为 message
    message = [
        ('class:prompt', f"{prompt_text} > ")
    ]

    try:
        answer = prompt(
            message,
            completer=completer,
            default=default,
            style=style,
            bottom_toolbar=f"[Tab]自动补全 [Up/Down]历史记录 [Default: {default}]" if default else "[Tab]自动补全 [Up/Down]历史记录"
        )
        return answer.strip()
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]操作已取消。[/yellow]")
        return None

def safe_confirm(prompt_text: str, default: bool = True) -> bool:
    """
    安全的确认提示，处理 Ctrl+C
    """
    try:
        return Confirm.ask(prompt_text, default=default, console=console)
    except KeyboardInterrupt:
        console.print("\n[yellow]操作已取消。[/yellow]")
        return False

