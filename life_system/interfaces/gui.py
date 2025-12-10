import sys
from gooey import Gooey, GooeyParser
from life_system.services.task_service import TaskService
from life_system.core.db import init_db

@Gooey(
    program_name="LifeOS GUI",
    default_size=(600, 500),
    navigation='TABBED',
    header_bg_color='#73b5e7',
    body_bg_color='#ffffff',
    encoding='utf-8'
)
def run_gui():
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

    # 简单的逻辑桥接
    if args.command == 'add':
        event_id = service.create_task_event(args.title)
        print(f"成功: 任务事件已发布 (ID: {event_id})")
        print("请运行 'Process' 或等待后台处理。")
    
    elif args.command == 'list':
        # 懒加载
        service.process_events()
        tasks = service.list_tasks(args.status)
        print(f"--- 任务列表 ({args.status}) ---")
        for t in tasks:
            print(f"[{t.id}] {t.title} <{t.created_at.strftime('%Y-%m-%d %H:%M')}>")
            
    elif args.command == 'done':
        if service.update_status(int(args.task_id), "done"):
            print(f"成功: 任务 {args.task_id} 已标记为完成。")
        else:
            print(f"错误: 未找到任务 {args.task_id}")

if __name__ == '__main__':
    run_gui()

