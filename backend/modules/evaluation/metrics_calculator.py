"""
指标计算器
计算各种质量指标和统计数据
"""
import re
import logging
from typing import List, Dict
from collections import Counter

from models.evaluation_models import QualityMetrics

logger = logging.getLogger(__name__)


class MetricsCalculator:
    """指标计算器类"""
    
    def __init__(self):
        """初始化指标计算器"""
        pass
    
    def calculate_structure_score(self, prompt_text: str) -> float:
        """
        计算结构合规率
        
        Args:
            prompt_text: Prompt 文本
            
        Returns:
            float: 结构得分 (0-1)
        """
        score = 0.0
        
        # 检查是否有标题/分节
        if re.search(r'^#+\s+', prompt_text, re.MULTILINE):
            score += 0.3
        
        # 检查是否有角色定义
        if re.search(r'(角色|role|你是)', prompt_text, re.IGNORECASE):
            score += 0.2
        
        # 检查是否有目标/任务说明
        if re.search(r'(目标|objective|任务|task)', prompt_text, re.IGNORECASE):
            score += 0.2
        
        # 检查是否有输出格式说明
        if re.search(r'(输出|output|格式|format)', prompt_text, re.IGNORECASE):
            score += 0.2
        
        # 检查是否有列表或编号
        if re.search(r'^\s*[\d\-\*•]+', prompt_text, re.MULTILINE):
            score += 0.1
        
        return min(score, 1.0)
    
    def calculate_consistency_score(self, prompt_text: str) -> float:
        """
        计算目标一致性（简化版本，实际应使用 AI 评估）
        
        Args:
            prompt_text: Prompt 文本
            
        Returns:
            float: 一致性得分 (0-1)
        """
        # 这里使用简单的启发式方法
        # 实际项目中应使用 AI 进行语义分析
        
        score = 0.7  # 基准分
        
        # 检查是否有矛盾的指令
        contradictions = [
            (r'详细', r'简洁'),
            (r'专业', r'通俗'),
            (r'严肃', r'幽默'),
        ]
        
        for word1, word2 in contradictions:
            if re.search(word1, prompt_text) and re.search(word2, prompt_text):
                score -= 0.15
        
        return max(score, 0.0)
    
    def calculate_completeness_score(self, prompt_text: str) -> float:
        """
        计算语义完整度
        
        Args:
            prompt_text: Prompt 文本
            
        Returns:
            float: 完整度得分 (0-1)
        """
        score = 0.0
        
        # 基础长度要求
        length = len(prompt_text)
        if length >= 100:
            score += 0.3
        elif length >= 50:
            score += 0.2
        else:
            score += 0.1
        
        # 关键要素检查
        essential_elements = [
            r'(角色|role)',
            r'(目标|objective|任务)',
            r'(输出|output)',
            r'(上下文|context|背景)',
        ]
        
        for element in essential_elements:
            if re.search(element, prompt_text, re.IGNORECASE):
                score += 0.15
        
        return min(score, 1.0)
    
    def calculate_clarity_score(self, prompt_text: str) -> float:
        """
        计算表达清晰度
        
        Args:
            prompt_text: Prompt 文本
            
        Returns:
            float: 清晰度得分 (0-1)
        """
        score = 1.0
        
        # 检查模糊词汇
        vague_words = ['可能', '大概', '也许', '应该', '尽量']
        vague_count = sum(prompt_text.count(word) for word in vague_words)
        score -= min(vague_count * 0.1, 0.3)
        
        # 检查是否有明确的动词
        action_verbs = ['分析', '生成', '提取', '转换', '总结', '创建']
        if any(verb in prompt_text for verb in action_verbs):
            score += 0.1
        else:
            score -= 0.2
        
        # 检查句子长度（过长影响清晰度）
        sentences = re.split(r'[。.!！?？]', prompt_text)
        avg_length = sum(len(s) for s in sentences) / max(len(sentences), 1)
        if avg_length > 100:
            score -= 0.2
        
        return max(min(score, 1.0), 0.0)
    
    def calculate_metrics(self, prompt_text: str) -> QualityMetrics:
        """
        计算所有质量指标
        
        Args:
            prompt_text: Prompt 文本
            
        Returns:
            QualityMetrics: 质量指标对象
        """
        metrics = QualityMetrics(
            structure_score=self.calculate_structure_score(prompt_text),
            consistency_score=self.calculate_consistency_score(prompt_text),
            completeness_score=self.calculate_completeness_score(prompt_text),
            clarity_score=self.calculate_clarity_score(prompt_text),
            overall_score=0.0
        )
        
        # 计算综合得分
        metrics.calculate_overall()
        
        logger.info(f"指标计算完成 - 综合得分: {metrics.overall_score:.2f}")
        return metrics
    
    def calculate_readability(self, text: str) -> float:
        """
        计算可读性得分
        
        Args:
            text: 文本
            
        Returns:
            float: 可读性得分 (0-1)
        """
        # 简化的可读性计算
        lines = text.split('\n')
        non_empty_lines = [l for l in lines if l.strip()]
        
        score = 0.5  # 基准分
        
        # 适当的段落数量
        if 3 <= len(non_empty_lines) <= 20:
            score += 0.2
        
        # 有适当的空行分隔
        empty_lines = len(lines) - len(non_empty_lines)
        if empty_lines > 0:
            score += 0.1
        
        # 有标题或列表
        if re.search(r'^#+\s+|\n\s*[\d\-\*]', text, re.MULTILINE):
            score += 0.2
        
        return min(score, 1.0)
    
    def get_statistics(self, prompt_text: str) -> Dict:
        """
        获取 Prompt 的统计信息
        
        Args:
            prompt_text: Prompt 文本
            
        Returns:
            Dict: 统计信息字典
        """
        lines = prompt_text.split('\n')
        words = prompt_text.split()
        
        return {
            "total_characters": len(prompt_text),
            "total_lines": len(lines),
            "total_words": len(words),
            "avg_line_length": len(prompt_text) / max(len(lines), 1),
            "has_sections": len(re.findall(r'^#+', prompt_text, re.MULTILINE)),
            "has_lists": len(re.findall(r'^\s*[\d\-\*]', prompt_text, re.MULTILINE)),
            "readability_score": self.calculate_readability(prompt_text)
        }

