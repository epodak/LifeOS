import sys
from os.path import dirname, abspath
import os

# 将项目根目录添加到 python path
sys.path.insert(0, dirname(dirname(abspath(__file__))))

from life_system.interfaces.cli import app

if __name__ == "__main__":
    app()

