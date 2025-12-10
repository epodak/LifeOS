import sys
from pathlib import Path
from loguru import logger
from life_system.config.settings import DB_PATH

# 确定日志目录 (放在项目根目录的 logs 下)
# DB_PATH 位于 LifeOS/life.db，我们根据它推断 logs 目录
PROJECT_ROOT = Path(DB_PATH).parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 配置 Loguru
# 1. 移除默认的 handler (避免重复)
logger.remove()

# 2. 添加控制台输出 (带颜色，只要 INFO 级别及以上)
# 注意：CLI 工具通常直接用 print/rich 输出给用户，日志更多用于调试
# 所以控制台日志级别可以设高一点，或者在 serve 模式下才显示详细日志
logger.add(
    sys.stderr,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 3. 添加文件输出 (每天轮转，保留 7 天，记录所有 DEBUG 级别及以上的信息)
logger.add(
    LOG_DIR / "life_os.log",
    rotation="00:00",      # 每天午夜轮转
    retention="7 days",    # 保留7天
    compression="zip",     # 压缩旧日志
    level="DEBUG",
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
)

# 导出配置好的 logger
__all__ = ["logger"]

