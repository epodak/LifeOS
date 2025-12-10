"""
任务分析引擎 (Analysis Engine)
纯函数式，无副作用。只负责分析任务内容，返回分析结果。
"""
from typing import Dict, Any, List
import re
from collections import Counter

class TaskAnalyzer:
    """任务分析引擎：提取关键词、分类、优先级"""
    
    # 关键词词典（未来可以扩展为机器学习模型）
    KEYWORDS = {
        "优化": {"category": "开发/维护", "priority": "medium"},
        "修复": {"category": "开发/维护", "priority": "high"},
        "重构": {"category": "开发/维护", "priority": "medium"},
        "实现": {"category": "开发/功能", "priority": "high"},
        "添加": {"category": "开发/功能", "priority": "medium"},
        "学习": {"category": "学习/成长", "priority": "low"},
        "阅读": {"category": "学习/成长", "priority": "low"},
        "整理": {"category": "生活/整理", "priority": "low"},
    }
    
    @staticmethod
    def analyze(title: str) -> Dict[str, Any]:
        """
        分析任务标题，返回分析结果
        
        Returns:
            {
                "keywords": List[str],      # 提取的关键词
                "category": str,            # 分类
                "priority": str,            # 优先级
                "suggested_tags": List[str] # 建议的标签
            }
        """
        # 提取关键词
        keywords = []
        category = None
        priority = "medium"  # 默认优先级
        
        # 简单的关键词匹配（未来可以用 NLP 模型）
        for keyword, info in TaskAnalyzer.KEYWORDS.items():
            if keyword in title:
                keywords.append(keyword)
                if not category:
                    category = info["category"]
                # 优先级取最高（high > medium > low）
                if info["priority"] == "high" or (info["priority"] == "medium" and priority == "low"):
                    priority = info["priority"]
        
        # 提取其他可能的标签（名词、动词）
        words = re.findall(r'\w+', title)
        suggested_tags = list(set(words[:3]))  # 取前3个不重复的词作为标签
        
        # 如果没有匹配到分类，使用默认分类
        if not category:
            category = "未分类"
        
        return {
            "keywords": keywords,
            "category": category,
            "priority": priority,
            "suggested_tags": suggested_tags
        }
    
    @staticmethod
    def extract_entities(title: str) -> Dict[str, Any]:
        """
        提取实体（项目名、工具名等）
        例如："优化lifeOS" → {"project": "lifeOS"}
        """
        # 简单的实体提取（未来可以用 NER 模型）
        entities = {}
        
        # 检测项目名（大写字母开头的词）
        project_match = re.search(r'[A-Z][a-zA-Z]+', title)
        if project_match:
            entities["project"] = project_match.group()
        
        return entities

