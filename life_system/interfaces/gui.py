import sys
from gooey import Gooey, GooeyParser
from life_system.services.task_service import TaskService
from life_system.core.db import init_db

def run_gui():
    # 检查命令行参数，如果有特定子命令（如 'add'），则直接进入该子命令的界面
    # 注意：Gooey 默认会解析 sys.argv。如果我们通过 subprocess 传递了 "add"，
    # Gooey 会尝试解析它。但 Gooey 通常是生成整个 CLI 的 GUI wrapper。
    # 为了实现“只显示 add 界面”，我们需要在这里做一些 hack 或者配置。
    
    # 简单的做法：Gooey 启动后默认就是选择子命令的界面。
    # 如果要直接跳到 add 页面，Gooey 目前对 programmatic navigation 支持有限。
    # 但我们可以通过修改 sys.argv 让 argparse 默认选中 add，但这只影响 CLI 执行，不影响 GUI 初始页。
    
    # 更好的解耦方案是：gui.py 只是一个入口，根据参数决定显示哪个 Gooey App。
    # 下面是一个简化的实现，根据第一个参数决定是否只构建 add 的 GUI。
    
    target_command = None
    if len(sys.argv) > 1 and sys.argv[1] in ['add', 'list', 'done']:
         target_command = sys.argv[1]
         # 清理参数，否则 GooeyParser 会困惑
         # sys.argv = [sys.argv[0]] 
         # 不，Gooey 需要参数来决定是否忽略某些配置。
         
    # ... (Gooey 装饰器逻辑)
    # 实际上，Gooey 主要是把 argparse 转成 GUI。
    # 如果我们想让 life add -g 只弹出一个“添加任务”的框，
    # 我们应该定义一个只包含 add 功能的 Gooey App。
    
    pass 

# 为了真正解耦，我们将逻辑拆分为不同的入口函数
# 但为了不创建太多文件，我们可以在这一个文件里用不同的函数和装饰器

@Gooey(
    program_name="添加任务",
    default_size=(400, 300),
    navigation='TABBED',
    show_sidebar=False, # 隐藏侧边栏，使其看起来像一个专注的弹窗
    encoding='utf-8'
)
def run_add_gui():
    service = TaskService()
    parser = GooeyParser(description="快速添加新任务")
    parser.add_argument('title', help='任务标题', widget='TextField')
    
    args = parser.parse_args()
    event_id = service.create_task_event(args.title)
    print(f"成功: 任务已添加 (ID: {event_id})")

@Gooey(
    program_name="LifeOS GUI",
    default_size=(600, 500),
    navigation='TABBED',
    encoding='utf-8'
)
def run_full_gui():
    service = TaskService()
    parser = GooeyParser(description="LifeOS 任务管理系统")
    subs = parser.add_subparsers(help="commands", dest="command")

    # Add Command
    add_parser = subs.add_parser('add', help='添加新任务')
    add_parser.add_argument('title', help='任务标题', widget='TextField')

    # List Command
    list_parser = subs.add_parser('list', help='查看任务列表')
    list_parser.add_argument('--status', choices=['pending', 'done', 'dropped'], default='pending', help='筛选状态')

    # Done Command
    done_parser = subs.add_parser('done', help='完成任务')
    done_parser.add_argument('task_id', help='任务ID', widget='IntegerField')

    args = parser.parse_args()

    # 逻辑桥接
    if args.command == 'add':
        event_id = service.create_task_event(args.title)
        print(f"成功: 任务事件已发布 (ID: {event_id})")
    elif args.command == 'list':
        service.process_events()
        tasks = service.list_tasks(args.status)
        for t in tasks:
            print(f"[{t.id}] {t.title} <{t.status}>")
    elif args.command == 'done':
        if service.update_status(int(args.task_id), "done"):
            print(f"成功: 任务 {args.task_id} 已完成。")

if __name__ == '__main__':
    # 简单的路由分发
    if len(sys.argv) > 1 and sys.argv[1] == 'add':
        # 移除 'add' 参数，否则 argparse 会报错，或者 Gooey 会误解
        # GooeyParser.parse_args() 会解析 sys.argv[1:]
        # 对于 run_add_gui，我们希望它解析的是用户在 GUI 里填的内容，而不是启动时的 'add'
        # 这里的 trick 是：Gooey 在启动时，如果没有参数，会显示配置界面。点击 Start 后会带参数再次运行。
        # 当我们通过 subprocess 运行 python gui.py add 时，
        # 我们希望它直接显示 run_add_gui 的界面。
        sys.argv = [sys.argv[0]] # 重置参数，让 Gooey 以为是第一次启动
        run_add_gui()
    else:
        run_full_gui()

