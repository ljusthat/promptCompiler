"""
质量评估器
使用智谱 AI 进行多维度质量评估
"""
import logging
from typing import Optional
from datetime import datetime

from services.zhipu_service import ZhipuAIService
from models.prompt_models import IntentResult
from models.evaluation_models import QualityMetrics, EvaluationResult

logger = logging.getLogger(__name__)


class QualityEvaluator:
    """质量评估器类"""
    
    def __init__(self):
        """初始化质量评估器"""
        self.zhipu_service = ZhipuAIService()
    
    async def evaluate(
        self,
        prompt_text: str,
        intent: Optional[IntentResult] = None,
        prompt_version_id: Optional[str] = None
    ) -> EvaluationResult:
        """
        评估 Prompt 质量
        
        Args:
            prompt_text: 待评估的 Prompt 文本
            intent: 意图信息（可选）
            prompt_version_id: Prompt 版本ID（可选）
            
        Returns:
            EvaluationResult: 评估结果
        """
        logger.info("开始质量评估")
        
        # 调用智谱 AI 服务进行评估
        evaluation_data = await self.zhipu_service.quality_evaluation(
            prompt_text,
            intent
        )
        
        # 构建评估结果
        evaluation_result = EvaluationResult(
            prompt_version_id=prompt_version_id or "unknown",
            metrics=evaluation_data["metrics"],
            strengths=evaluation_data.get("strengths", []),
            weaknesses=evaluation_data.get("weaknesses", []),
            suggestions=evaluation_data.get("suggestions", []),
            ai_analysis=evaluation_data.get("analysis", ""),
            evaluated_at=datetime.now(),
            evaluator="zhipu_ai"
        )
        
        logger.info(
            f"质量评估完成 - 综合评分: {evaluation_result.metrics.overall_score:.2f}"
        )
        
        return evaluation_result
    
    async def batch_evaluate(
        self,
        prompts: list[tuple[str, Optional[IntentResult]]]
    ) -> list[EvaluationResult]:
        """
        批量评估多个 Prompt
        
        Args:
            prompts: Prompt 列表 [(prompt_text, intent), ...]
            
        Returns:
            list[EvaluationResult]: 评估结果列表
        """
        results = []
        
        for prompt_text, intent in prompts:
            try:
                result = await self.evaluate(prompt_text, intent)
                results.append(result)
            except Exception as e:
                logger.error(f"评估失败: {e}")
                # 创建默认评估结果
                default_result = EvaluationResult(
                    prompt_version_id="error",
                    metrics=QualityMetrics(
                        structure_score=0.0,
                        consistency_score=0.0,
                        completeness_score=0.0,
                        clarity_score=0.0,
                        overall_score=0.0
                    ),
                    weaknesses=[f"评估失败: {str(e)}"],
                    evaluator="error"
                )
                results.append(default_result)
        
        logger.info(f"批量评估完成，共评估 {len(results)} 个 Prompt")
        return results
    
    async def compare(
        self,
        prompt_a: str,
        prompt_b: str,
        intent: Optional[IntentResult] = None
    ) -> dict:
        """
        对比两个 Prompt 的质量
        
        Args:
            prompt_a: 第一个 Prompt
            prompt_b: 第二个 Prompt
            intent: 意图信息（可选）
            
        Returns:
            dict: 对比结果
        """
        # 评估两个 Prompt
        eval_a = await self.evaluate(prompt_a, intent, "version_a")
        eval_b = await self.evaluate(prompt_b, intent, "version_b")
        
        # 比较各项指标
        metrics_comparison = {
            "structure": {
                "version_a": eval_a.metrics.structure_score,
                "version_b": eval_b.metrics.structure_score,
                "diff": eval_b.metrics.structure_score - eval_a.metrics.structure_score
            },
            "consistency": {
                "version_a": eval_a.metrics.consistency_score,
                "version_b": eval_b.metrics.consistency_score,
                "diff": eval_b.metrics.consistency_score - eval_a.metrics.consistency_score
            },
            "completeness": {
                "version_a": eval_a.metrics.completeness_score,
                "version_b": eval_b.metrics.completeness_score,
                "diff": eval_b.metrics.completeness_score - eval_a.metrics.completeness_score
            },
            "clarity": {
                "version_a": eval_a.metrics.clarity_score,
                "version_b": eval_b.metrics.clarity_score,
                "diff": eval_b.metrics.clarity_score - eval_a.metrics.clarity_score
            },
            "overall": {
                "version_a": eval_a.metrics.overall_score,
                "version_b": eval_b.metrics.overall_score,
                "diff": eval_b.metrics.overall_score - eval_a.metrics.overall_score
            }
        }
        
        # 确定胜出者
        winner = "version_b" if eval_b.metrics.overall_score > eval_a.metrics.overall_score else "version_a"
        
        return {
            "eval_a": eval_a,
            "eval_b": eval_b,
            "metrics_comparison": metrics_comparison,
            "winner": winner,
            "analysis": self._generate_comparison_analysis(eval_a, eval_b, winner)
        }
    
    def _generate_comparison_analysis(
        self,
        eval_a: EvaluationResult,
        eval_b: EvaluationResult,
        winner: str
    ) -> str:
        """生成对比分析说明"""
        diff = abs(eval_b.metrics.overall_score - eval_a.metrics.overall_score)
        
        if diff < 0.05:
            return "两个版本质量相近，差异不明显"
        elif diff < 0.15:
            return f"{winner} 略优于另一版本，改进幅度较小"
        else:
            return f"{winner} 明显优于另一版本，改进效果显著"

