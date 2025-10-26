"""
评估 API 路由
提供 Prompt 质量评估功能
"""
from fastapi import APIRouter, HTTPException
import logging

from models.api_models import EvaluateRequest, EvaluateResponse
from modules.evaluation import QualityEvaluator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["evaluate"])


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_prompt(request: EvaluateRequest):
    """
    评估 Prompt 质量
    
    多维度分析 Prompt 的质量指标
    """
    try:
        logger.info(f"收到评估请求 - Prompt 长度: {len(request.prompt_text)}")
        
        # 执行质量评估
        evaluator = QualityEvaluator()
        evaluation = await evaluator.evaluate(
            request.prompt_text,
            request.intent
        )
        
        # 构建响应
        response = EvaluateResponse(
            success=True,
            evaluation=evaluation
        )
        
        logger.info(f"评估成功 - 综合评分: {evaluation.metrics.overall_score:.2f}")
        return response
        
    except Exception as e:
        logger.error(f"评估失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"评估失败: {str(e)}")

