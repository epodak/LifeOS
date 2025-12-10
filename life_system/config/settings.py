import os
import sys

# 获取 setup.py 所在的根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 如果在项目中运行，确保使用项目内的 config
if os.getcwd() != PROJECT_ROOT and os.path.exists(os.path.join(PROJECT_ROOT, "life.db")):
    # 强制将 DB 路径指向项目根目录，而不是当前执行目录
    from pathlib import Path
    DB_PATH = Path(PROJECT_ROOT) / "life.db"
    DB_URL = f"sqlite:///{DB_PATH}"
else:
    # 默认回退
    from pathlib import Path
    DB_PATH = Path("life.db")
    DB_URL = f"sqlite:///{DB_PATH}"
