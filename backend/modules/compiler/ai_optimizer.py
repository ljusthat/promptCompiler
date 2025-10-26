"""
AI 优化器
使用智谱 AI 进行 Prompt 重写和优化
"""
import logging
from typing import Optional, List

from services.zhipu_service import ZhipuAIService
from models.prompt_models import IntentResult, OptimizationLevel

logger = logging.getLogger(__name__)


class AIOptimizer:
    """AI 优化器类"""
    
    def __init__(self):
        """初始化 AI 优化器"""
        self.zhipu_service = ZhipuAIService()
    
    async def optimize(
        self,
        prompt_text: str,
        intent: Optional[IntentResult] = None,
        optimization_level: OptimizationLevel = OptimizationLevel.MEDIUM,
        focus_areas: Optional[List[str]] = None
    ) -> dict:
        """
        优化 Prompt
        
        Args:
            prompt_text: 原始 Prompt 文本
            intent: 意图信息
            optimization_level: 优化级别
            focus_areas: 重点优化的方面
            
        Returns:
            dict: 优化结果，包含优化后的 Prompt 和改进说明
        """
        logger.info(f"开始优化 Prompt，优化级别: {optimization_level}")
        
        # 根据优化级别设置不同的 focus_areas
        if not focus_areas:
            focus_areas = self._get_default_focus_areas(optimization_level)
        
        # 调用智谱 AI 服务
        result = await self.zhipu_service.prompt_optimization(
            prompt_text=prompt_text,
            intent=intent,
            focus_areas=focus_areas
        )
        
        logger.info(f"Prompt 优化完成，改进点数量: {len(result.get('improvements', []))}")
        return result
    
    def _get_default_focus_areas(self, level: OptimizationLevel) -> List[str]:
        """
        根据优化级别获取默认的优化重点
        
        Args:
            level: 优化级别
            
        Returns:
            List[str]: 优化重点列表
        """
        if level == OptimizationLevel.LOW:
            return ["clarity"]  # 低级别：仅关注清晰度
        elif level == OptimizationLevel.MEDIUM:
            return ["clarity", "structure"]  # 中级别：清晰度 + 结构
        else:  # HIGH
            return ["clarity", "structure", "specificity", "effectiveness"]  # 高级别：全面优化
    
    async def enhance_clarity(self, prompt_text: str) -> str:
        """
        增强 Prompt 的清晰度
        
        Args:
            prompt_text: 原始 Prompt
            
        Returns:
            str: 优化后的 Prompt
        """
        result = await self.optimize(
            prompt_text,
            focus_areas=["clarity"]
        )
        return result.get("optimized_prompt", prompt_text)
    
    async def enhance_structure(self, prompt_text: str) -> str:
        """
        增强 Prompt 的结构
        
        Args:
            prompt_text: 原始 Prompt
            
        Returns:
            str: 优化后的 Prompt
        """
        result = await self.optimize(
            prompt_text,
            focus_areas=["structure"]
        )
        return result.get("optimized_prompt", prompt_text)
    
    async def add_specificity(self, prompt_text: str) -> str:
        """
        增加 Prompt 的具体性
        
        Args:
            prompt_text: 原始 Prompt
            
        Returns:
            str: 优化后的 Prompt
        """
        result = await self.optimize(
            prompt_text,
            focus_areas=["specificity", "details"]
        )
        return result.get("optimized_prompt", prompt_text)
    
    async def compress(self, prompt_text: str, target_length: Optional[int] = None) -> str:
        """
        压缩 Prompt（保留核心信息）
        
        Args:
            prompt_text: 原始 Prompt
            target_length: 目标长度（可选）
            
        Returns:
            str: 压缩后的 Prompt
        """
        focus = ["conciseness", "core_information"]
        if target_length:
            focus.append(f"target_length_{target_length}")
        
        result = await self.optimize(
            prompt_text,
            focus_areas=focus
        )
        return result.get("optimized_prompt", prompt_text)
    
    async def expand(self, prompt_text: str) -> str:
        """
        扩展 Prompt（添加更多细节）
        
        Args:
            prompt_text: 原始 Prompt
            
        Returns:
            str: 扩展后的 Prompt
        """
        result = await self.optimize(
            prompt_text,
            focus_areas=["details", "examples", "context"]
        )
        return result.get("optimized_prompt", prompt_text)

