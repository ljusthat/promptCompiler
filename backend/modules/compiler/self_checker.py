"""
自检机制
验证优化后的 Prompt 质量
"""
import logging
from typing import Dict, Any

from services.zhipu_service import ZhipuAIService
from models.prompt_models import IntentResult
from models.evaluation_models import QualityMetrics
from .rule_engine import RuleEngine

logger = logging.getLogger(__name__)


class SelfChecker:
    """自检器类"""
    
    def __init__(self):
        """初始化自检器"""
        self.zhipu_service = ZhipuAIService()
        self.rule_engine = RuleEngine()
    
    async def check(
        self,
        optimized_prompt: str,
        original_prompt: str,
        intent: IntentResult
    ) -> Dict[str, Any]:
        """
        自检优化后的 Prompt
        
        Args:
            optimized_prompt: 优化后的 Prompt
            original_prompt: 原始 Prompt
            intent: 意图信息
            
        Returns:
            Dict: 自检结果
        """
        logger.info("开始自检优化后的 Prompt")
        
        # 1. 规则检查
        validation_result = self.rule_engine.validate(optimized_prompt)
        
        # 2. AI 质量评估
        evaluation_result = await self.zhipu_service.quality_evaluation(
            optimized_prompt,
            intent
        )
        
        # 3. 对比分析
        comparison = await self._compare_versions(original_prompt, optimized_prompt, intent)
        
        # 4. 综合判断
        passed = validation_result.passed and evaluation_result["metrics"].overall_score > 0.7
        
        result = {
            "passed": passed,
            "validation": {
                "passed": validation_result.passed,
                "errors": validation_result.errors,
                "warnings": validation_result.warnings,
                "suggestions": validation_result.suggestions
            },
            "quality_metrics": evaluation_result["metrics"],
            "comparison": comparison,
            "recommendation": self._generate_recommendation(
                validation_result,
                evaluation_result["metrics"],
                comparison
            )
        }
        
        logger.info(f"自检完成 - 通过: {passed}")
        return result
    
    async def _compare_versions(
        self,
        original: str,
        optimized: str,
        intent: IntentResult
    ) -> Dict[str, Any]:
        """
        对比原始版本和优化版本
        
        Args:
            original: 原始 Prompt
            optimized: 优化后的 Prompt
            intent: 意图信息
            
        Returns:
            Dict: 对比结果
        """
        # 评估原始版本
        original_eval = await self.zhipu_service.quality_evaluation(original, intent)
        original_metrics = original_eval["metrics"]
        
        # 评估优化版本
        optimized_eval = await self.zhipu_service.quality_evaluation(optimized, intent)
        optimized_metrics = optimized_eval["metrics"]
        
        # 计算改进幅度
        improvements = {
            "structure": optimized_metrics.structure_score - original_metrics.structure_score,
            "consistency": optimized_metrics.consistency_score - original_metrics.consistency_score,
            "completeness": optimized_metrics.completeness_score - original_metrics.completeness_score,
            "clarity": optimized_metrics.clarity_score - original_metrics.clarity_score,
            "overall": optimized_metrics.overall_score - original_metrics.overall_score
        }
        
        return {
            "original_metrics": original_metrics,
            "optimized_metrics": optimized_metrics,
            "improvements": improvements,
            "is_better": optimized_metrics.overall_score > original_metrics.overall_score
        }
    
    def _generate_recommendation(
        self,
        validation_result,
        metrics: QualityMetrics,
        comparison: Dict[str, Any]
    ) -> str:
        """
        生成推荐建议
        
        Args:
            validation_result: 规则校验结果
            metrics: 质量指标
            comparison: 对比结果
            
        Returns:
            str: 推荐建议
        """
        if not validation_result.passed:
            return "优化后的 Prompt 存在严重问题，建议使用原始版本或重新优化"
        
        if metrics.overall_score < 0.6:
            return "优化后的 Prompt 质量偏低，建议进一步优化"
        
        if not comparison["is_better"]:
            return "优化效果不明显，建议使用原始版本或尝试不同的优化策略"
        
        if metrics.overall_score >= 0.8:
            return "优化后的 Prompt 质量优秀，推荐使用"
        
        return "优化后的 Prompt 质量良好，可以使用"
    
    async def verify_intent_alignment(
        self,
        prompt_text: str,
        expected_intent: IntentResult
    ) -> bool:
        """
        验证 Prompt 是否符合预期意图
        
        Args:
            prompt_text: Prompt 文本
            expected_intent: 预期意图
            
        Returns:
            bool: 是否符合预期
        """
        # 重新提取 Prompt 的意图
        actual_intent = await self.zhipu_service.intent_extraction(prompt_text)
        
        # 比较任务类型
        type_match = actual_intent.task_type == expected_intent.task_type
        
        # 比较领域（允许一定容错）
        domain_match = (
            actual_intent.domain == expected_intent.domain or
            actual_intent.domain in expected_intent.domain or
            expected_intent.domain in actual_intent.domain
        )
        
        # 综合判断
        aligned = type_match and domain_match
        
        logger.info(f"意图对齐验证 - 任务类型匹配: {type_match}, 领域匹配: {domain_match}")
        return aligned

