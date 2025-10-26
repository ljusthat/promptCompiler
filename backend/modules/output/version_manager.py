"""
版本管理器
管理 Prompt 的历史版本
"""
import logging
from typing import List, Optional
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.prompt_models import CompiledPrompt

logger = logging.getLogger(__name__)


class VersionManager:
    """版本管理器类"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        初始化版本管理器
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.collection = db.history
    
    async def save_version(self, compiled_prompt: CompiledPrompt) -> CompiledPrompt:
        """
        保存 Prompt 版本
        
        Args:
            compiled_prompt: 编译后的 Prompt
            
        Returns:
            CompiledPrompt: 保存的版本
        """
        prompt_dict = compiled_prompt.model_dump()
        prompt_dict["created_at"] = datetime.now()
        
        await self.collection.insert_one(prompt_dict)
        logger.info(f"版本保存成功: {compiled_prompt.version_id}")
        
        return compiled_prompt
    
    async def get_version(self, version_id: str) -> Optional[CompiledPrompt]:
        """
        获取指定版本
        
        Args:
            version_id: 版本ID
            
        Returns:
            Optional[CompiledPrompt]: Prompt 对象，不存在则返回 None
        """
        prompt_dict = await self.collection.find_one({"version_id": version_id})
        
        if prompt_dict:
            prompt_dict.pop("_id", None)
            return CompiledPrompt(**prompt_dict)
        
        return None
    
    async def list_versions(
        self,
        limit: int = 50,
        skip: int = 0,
        filter_dict: Optional[dict] = None
    ) -> List[CompiledPrompt]:
        """
        列出历史版本
        
        Args:
            limit: 返回数量限制
            skip: 跳过数量（分页）
            filter_dict: 过滤条件（可选）
            
        Returns:
            List[CompiledPrompt]: Prompt 列表
        """
        query = filter_dict or {}
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        
        versions = []
        async for prompt_dict in cursor:
            prompt_dict.pop("_id", None)
            versions.append(CompiledPrompt(**prompt_dict))
        
        logger.info(f"查询到 {len(versions)} 个历史版本")
        return versions
    
    async def get_versions_by_input(self, original_input: str) -> List[CompiledPrompt]:
        """
        获取相同输入的所有版本
        
        Args:
            original_input: 原始输入
            
        Returns:
            List[CompiledPrompt]: Prompt 列表
        """
        return await self.list_versions(
            limit=100,
            filter_dict={"original_input": original_input}
        )
    
    async def get_recent_versions(self, limit: int = 20) -> List[CompiledPrompt]:
        """
        获取最近的版本
        
        Args:
            limit: 返回数量
            
        Returns:
            List[CompiledPrompt]: Prompt 列表
        """
        return await self.list_versions(limit=limit)
    
    async def delete_version(self, version_id: str) -> bool:
        """
        删除指定版本
        
        Args:
            version_id: 版本ID
            
        Returns:
            bool: 是否删除成功
        """
        result = await self.collection.delete_one({"version_id": version_id})
        
        if result.deleted_count > 0:
            logger.info(f"版本删除成功: {version_id}")
            return True
        
        return False
    
    async def count_versions(self, filter_dict: Optional[dict] = None) -> int:
        """
        统计版本数量
        
        Args:
            filter_dict: 过滤条件（可选）
            
        Returns:
            int: 版本数量
        """
        query = filter_dict or {}
        count = await self.collection.count_documents(query)
        return count
    
    async def get_version_statistics(self) -> dict:
        """
        获取版本统计信息
        
        Returns:
            dict: 统计信息
        """
        total_count = await self.count_versions()
        
        # 统计各优化级别的版本数
        low_count = await self.count_versions({"optimization_level": "low"})
        medium_count = await self.count_versions({"optimization_level": "medium"})
        high_count = await self.count_versions({"optimization_level": "high"})
        
        # 统计优化过的版本数
        optimized_count = await self.count_versions({"optimized": True})
        
        return {
            "total_versions": total_count,
            "by_optimization_level": {
                "low": low_count,
                "medium": medium_count,
                "high": high_count
            },
            "optimized_count": optimized_count,
            "optimized_ratio": optimized_count / total_count if total_count > 0 else 0
        }
    
    async def search_versions(
        self,
        search_text: str,
        limit: int = 20
    ) -> List[CompiledPrompt]:
        """
        搜索版本（根据原始输入或 Prompt 内容）
        
        Args:
            search_text: 搜索文本
            limit: 返回数量限制
            
        Returns:
            List[CompiledPrompt]: 匹配的 Prompt 列表
        """
        query = {
            "$or": [
                {"original_input": {"$regex": search_text, "$options": "i"}},
                {"full_prompt": {"$regex": search_text, "$options": "i"}}
            ]
        }
        
        return await self.list_versions(limit=limit, filter_dict=query)
    
    async def cleanup_old_versions(self, days: int = 30) -> int:
        """
        清理旧版本（保留最近 N 天的版本）
        
        Args:
            days: 保留天数
            
        Returns:
            int: 删除的版本数
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        result = await self.collection.delete_many({
            "created_at": {"$lt": cutoff_date}
        })
        
        deleted_count = result.deleted_count
        logger.info(f"清理了 {deleted_count} 个旧版本（{days} 天前）")
        
        return deleted_count

