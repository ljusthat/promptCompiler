"""
意图提取器
使用智谱 AI 提取用户输入的意图信息
"""
import logging
from typing import Optional

from services.zhipu_service import ZhipuAIService
from models.prompt_models import IntentResult

logger = logging.getLogger(__name__)


class IntentExtractor:
    """意图提取器类"""
    
    def __init__(self):
        """初始化意图提取器"""
        self.zhipu_service = ZhipuAIService()
    
    async def extract(self, user_input: str) -> IntentResult:
        """
        从用户输入中提取意图信息
        
        Args:
            user_input: 用户原始输入
            
        Returns:
            IntentResult: 提取的意图结果
        """
        logger.info(f"开始提取意图，输入长度: {len(user_input)}")
        
        try:
            # 调用智谱 AI 服务提取意图
            intent_result = await self.zhipu_service.intent_extraction(user_input)
            
            logger.info(
                f"意图提取完成 - 类型: {intent_result.task_type}, "
                f"领域: {intent_result.domain}, "
                f"置信度: {intent_result.confidence:.2f}"
            )
            
            return intent_result
            
        except Exception as e:
            logger.error(f"意图提取失败: {e}")
            raise
    
    async def extract_with_context(
        self,
        user_input: str,
        previous_context: Optional[dict] = None
    ) -> IntentResult:
        """
        带上下文的意图提取（考虑历史对话）
        
        Args:
            user_input: 用户当前输入
            previous_context: 之前的上下文信息
            
        Returns:
            IntentResult: 提取的意图结果
        """
        # 如果有历史上下文，可以结合分析
        if previous_context:
            enhanced_input = f"上下文: {previous_context}\n\n当前输入: {user_input}"
            return await self.extract(enhanced_input)
        else:
            return await self.extract(user_input)

