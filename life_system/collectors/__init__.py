"""
采集层 (Collectors)
感知世界（文件变化、时间触发、用户输入）。只产出 Event，绝不写库。

所有 Collector 都应该通过 IngestionPipeline 发布事件，而不是直接调用 EventBus。
"""

__all__ = []

