"""
优化 API 路由
提供 Prompt 优化功能
"""
from fastapi import APIRouter, HTTPException
import logging

from models.api_models import OptimizeRequest, OptimizeResponse
from modules.compiler import AIOptimizer
from modules.evaluation import MetricsCalculator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["optimize"])


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize_prompt(request: OptimizeRequest):
    """
    优化 Prompt
    
    对现有 Prompt 进行重写和优化
    """
    try:
        logger.info(f"收到优化请求 - Prompt 长度: {len(request.prompt_text)}")
        
        # 1. 计算优化前的指标
        calculator = MetricsCalculator()
        metrics_before = calculator.calculate_metrics(request.prompt_text)
        
        # 2. AI 优化
        optimizer = AIOptimizer()
        optimization_result = await optimizer.optimize(
            request.prompt_text,
            optimization_level=request.optimization_level,
            focus_areas=request.focus_areas
        )
        
        optimized_prompt = optimization_result.get("optimized_prompt", request.prompt_text)
        improvements = optimization_result.get("improvements", [])
        
        # 3. 计算优化后的指标
        metrics_after = calculator.calculate_metrics(optimized_prompt)
        
        # 4. 构建响应
        response = OptimizeResponse(
            success=True,
            original_prompt=request.prompt_text,
            optimized_prompt=optimized_prompt,
            improvements=improvements,
            metrics_before=metrics_before,
            metrics_after=metrics_after
        )
        
        logger.info(
            f"优化成功 - 评分提升: "
            f"{metrics_before.overall_score:.2f} → {metrics_after.overall_score:.2f}"
        )
        return response
        
    except Exception as e:
        logger.error(f"优化失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"优化失败: {str(e)}")

