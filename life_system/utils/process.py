import sys
import subprocess
import os
from life_system.utils.console import console

def detach_and_run():
    """
    分离当前进程并在后台运行。
    常用于启动常驻服务或定时任务，使其独立于当前终端会话。
    """
    # 检查是否已经是分离进程
    if len(sys.argv) > 1 and '--detached' in sys.argv:
        # 已分离，返回 True，允许主逻辑继续
        return True
    
    console.print("[yellow]🔄 正在启动后台分离进程...[/yellow]")
    
    # 构建命令
    # 这里的逻辑假设通过 python -m life_system ... 或类似方式启动
    # 为了通用性，我们重新构建当前的 sys.argv，并追加 --detached
    cmd = [sys.executable] + sys.argv + ['--detached']
    
    # 平台特定的分离标志
    kwargs = {}
    if sys.platform == 'win32':
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        kwargs.update(creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
        kwargs.update(close_fds=True)
    else:
        # Linux/Mac
        kwargs.update(start_new_session=True)

    # 断开所有标准流
    subprocess.Popen(
        cmd,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        **kwargs
    )
    
    console.print("[green]✅ 后台进程已启动。[/green]")
    # 主进程退出
    sys.exit(0)

