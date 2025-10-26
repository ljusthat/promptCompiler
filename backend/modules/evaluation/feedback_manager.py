"""
反馈管理器
收集和管理用户反馈，用于持续优化
"""
import logging
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.evaluation_models import FeedbackRecord

logger = logging.getLogger(__name__)


class FeedbackManager:
    """反馈管理器类"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        初始化反馈管理器
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.collection = db.feedback
    
    async def add_feedback(self, feedback: FeedbackRecord) -> FeedbackRecord:
        """
        添加反馈记录
        
        Args:
            feedback: 反馈记录对象
            
        Returns:
            FeedbackRecord: 添加的反馈记录
        """
        feedback_dict = feedback.model_dump()
        feedback_dict["created_at"] = datetime.now()
        
        await self.collection.insert_one(feedback_dict)
        logger.info(f"反馈记录已添加: {feedback.feedback_id}")
        
        return feedback
    
    async def get_feedback(self, feedback_id: str) -> Optional[FeedbackRecord]:
        """
        获取指定反馈记录
        
        Args:
            feedback_id: 反馈ID
            
        Returns:
            Optional[FeedbackRecord]: 反馈记录，不存在则返回 None
        """
        feedback_dict = await self.collection.find_one({"feedback_id": feedback_id})
        
        if feedback_dict:
            feedback_dict.pop("_id", None)
            return FeedbackRecord(**feedback_dict)
        
        return None
    
    async def get_feedback_by_prompt(self, prompt_version_id: str) -> List[FeedbackRecord]:
        """
        获取指定 Prompt 的所有反馈
        
        Args:
            prompt_version_id: Prompt 版本ID
            
        Returns:
            List[FeedbackRecord]: 反馈记录列表
        """
        cursor = self.collection.find(
            {"prompt_version_id": prompt_version_id}
        ).sort("created_at", -1)
        
        feedbacks = []
        async for feedback_dict in cursor:
            feedback_dict.pop("_id", None)
            feedbacks.append(FeedbackRecord(**feedback_dict))
        
        return feedbacks
    
    async def get_average_rating(self, prompt_version_id: str) -> Optional[float]:
        """
        获取指定 Prompt 的平均评分
        
        Args:
            prompt_version_id: Prompt 版本ID
            
        Returns:
            Optional[float]: 平均评分，无反馈则返回 None
        """
        feedbacks = await self.get_feedback_by_prompt(prompt_version_id)
        
        if not feedbacks:
            return None
        
        total_rating = sum(f.rating for f in feedbacks)
        avg_rating = total_rating / len(feedbacks)
        
        return avg_rating
    
    async def get_recent_feedbacks(self, limit: int = 50) -> List[FeedbackRecord]:
        """
        获取最近的反馈记录
        
        Args:
            limit: 返回数量限制
            
        Returns:
            List[FeedbackRecord]: 反馈记录列表
        """
        cursor = self.collection.find().sort("created_at", -1).limit(limit)
        
        feedbacks = []
        async for feedback_dict in cursor:
            feedback_dict.pop("_id", None)
            feedbacks.append(FeedbackRecord(**feedback_dict))
        
        logger.info(f"获取到 {len(feedbacks)} 条最近反馈")
        return feedbacks
    
    async def analyze_feedback_trends(self) -> dict:
        """
        分析反馈趋势
        
        Returns:
            dict: 趋势分析结果
        """
        feedbacks = await self.get_recent_feedbacks(limit=100)
        
        if not feedbacks:
            return {
                "total_count": 0,
                "average_rating": 0.0,
                "rating_distribution": {},
                "common_issues": [],
                "improvement_suggestions": []
            }
        
        # 统计评分分布
        rating_counts = {}
        for f in feedbacks:
            rating_counts[f.rating] = rating_counts.get(f.rating, 0) + 1
        
        # 收集常见问题和建议
        all_suggestions = []
        for f in feedbacks:
            all_suggestions.extend(f.improvement_suggestions)
        
        # 计算平均评分
        avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks)
        
        return {
            "total_count": len(feedbacks),
            "average_rating": avg_rating,
            "rating_distribution": rating_counts,
            "common_suggestions": list(set(all_suggestions))[:10],  # 去重并取前10
        }
    
    async def get_high_rated_prompts(self, min_rating: float = 4.0) -> List[str]:
        """
        获取高评分的 Prompt ID 列表
        
        Args:
            min_rating: 最低评分要求
            
        Returns:
            List[str]: Prompt 版本ID列表
        """
        cursor = self.collection.find({"rating": {"$gte": min_rating}})
        
        prompt_ids = set()
        async for feedback_dict in cursor:
            prompt_ids.add(feedback_dict["prompt_version_id"])
        
        logger.info(f"找到 {len(prompt_ids)} 个高评分 Prompt")
        return list(prompt_ids)
    
    async def get_low_rated_prompts(self, max_rating: float = 2.0) -> List[str]:
        """
        获取低评分的 Prompt ID 列表
        
        Args:
            max_rating: 最高评分要求
            
        Returns:
            List[str]: Prompt 版本ID列表
        """
        cursor = self.collection.find({"rating": {"$lte": max_rating}})
        
        prompt_ids = set()
        async for feedback_dict in cursor:
            prompt_ids.add(feedback_dict["prompt_version_id"])
        
        logger.info(f"找到 {len(prompt_ids)} 个低评分 Prompt")
        return list(prompt_ids)

