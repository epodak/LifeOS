"""
相似度计算引擎 (Similarity Engine)
纯函数式，无副作用。只负责计算任务之间的相似度。
"""
from typing import List, Tuple
from difflib import SequenceMatcher

class SimilarityEngine:
    """相似度计算引擎：检测相似或重复的任务"""
    
    @staticmethod
    def similarity_score(text1: str, text2: str) -> float:
        """
        计算两个文本的相似度（0-1之间）
        使用简单的序列匹配算法（未来可以用词向量、BERT等）
        """
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    @staticmethod
    def find_similar_tasks(
        target_title: str, 
        candidate_titles: List[Tuple[int, str]], 
        threshold: float = 0.6
    ) -> List[Tuple[int, float]]:
        """
        查找相似的任务
        
        Args:
            target_title: 目标任务标题
            candidate_titles: 候选任务列表，格式为 [(task_id, title), ...]
            threshold: 相似度阈值，默认0.6
        
        Returns:
            相似任务列表，格式为 [(task_id, similarity_score), ...]，按相似度降序排列
        """
        similar = []
        for task_id, title in candidate_titles:
            score = SimilarityEngine.similarity_score(target_title, title)
            if score >= threshold:
                similar.append((task_id, score))
        
        # 按相似度降序排列
        similar.sort(key=lambda x: x[1], reverse=True)
        return similar
    
    @staticmethod
    def is_duplicate(text1: str, text2: str, threshold: float = 0.9) -> bool:
        """
        判断两个任务是否是重复的（相似度极高）
        """
        return SimilarityEngine.similarity_score(text1, text2) >= threshold

