"""
模板管理器
负责模板的 CRUD 操作和存储
"""
import logging
from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.prompt_models import PromptTemplate, TaskType, IntentResult

logger = logging.getLogger(__name__)


class TemplateManager:
    """模板管理器类"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        """
        初始化模板管理器
        
        Args:
            db: MongoDB 数据库实例
        """
        self.db = db
        self.collection = db.templates
    
    async def create_template(self, template: PromptTemplate) -> PromptTemplate:
        """
        创建新模板
        
        Args:
            template: 模板对象
            
        Returns:
            PromptTemplate: 创建的模板
        """
        template_dict = template.model_dump()
        template_dict["created_at"] = datetime.now()
        template_dict["updated_at"] = datetime.now()
        
        await self.collection.insert_one(template_dict)
        logger.info(f"模板创建成功: {template.template_id}")
        
        return template
    
    async def get_template(self, template_id: str) -> Optional[PromptTemplate]:
        """
        获取指定模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            Optional[PromptTemplate]: 模板对象，不存在则返回 None
        """
        template_dict = await self.collection.find_one({"template_id": template_id})
        
        if template_dict:
            # 移除 MongoDB 的 _id 字段
            template_dict.pop("_id", None)
            return PromptTemplate(**template_dict)
        
        return None
    
    async def list_templates(
        self,
        task_type: Optional[TaskType] = None,
        domain: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[PromptTemplate]:
        """
        列出模板
        
        Args:
            task_type: 按任务类型筛选（可选）
            domain: 按领域筛选（可选）
            limit: 返回数量限制
            skip: 跳过数量（分页）
            
        Returns:
            List[PromptTemplate]: 模板列表
        """
        query = {}
        
        if task_type:
            query["task_types"] = task_type.value
        
        if domain:
            query["domains"] = domain
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
        templates = []
        
        async for template_dict in cursor:
            template_dict.pop("_id", None)
            templates.append(PromptTemplate(**template_dict))
        
        logger.info(f"查询到 {len(templates)} 个模板")
        return templates
    
    async def update_template(
        self,
        template_id: str,
        updates: dict
    ) -> Optional[PromptTemplate]:
        """
        更新模板
        
        Args:
            template_id: 模板ID
            updates: 更新的字段
            
        Returns:
            Optional[PromptTemplate]: 更新后的模板
        """
        updates["updated_at"] = datetime.now()
        
        result = await self.collection.find_one_and_update(
            {"template_id": template_id},
            {"$set": updates},
            return_document=True
        )
        
        if result:
            result.pop("_id", None)
            logger.info(f"模板更新成功: {template_id}")
            return PromptTemplate(**result)
        
        return None
    
    async def delete_template(self, template_id: str) -> bool:
        """
        删除模板
        
        Args:
            template_id: 模板ID
            
        Returns:
            bool: 是否删除成功
        """
        result = await self.collection.delete_one({"template_id": template_id})
        
        if result.deleted_count > 0:
            logger.info(f"模板删除成功: {template_id}")
            return True
        
        return False
    
    async def find_best_template(self, intent: IntentResult) -> Optional[PromptTemplate]:
        """
        根据意图找到最合适的模板
        
        Args:
            intent: 意图结果
            
        Returns:
            Optional[PromptTemplate]: 最匹配的模板
        """
        # 首先按任务类型和领域查找
        templates = await self.list_templates(
            task_type=intent.task_type,
            domain=intent.domain,
            limit=10
        )
        
        if templates:
            # 返回使用次数最多且评分最高的模板
            best_template = max(
                templates,
                key=lambda t: (t.avg_quality_score, t.usage_count)
            )
            logger.info(f"找到最佳模板: {best_template.name}")
            return best_template
        
        # 如果没有精确匹配，尝试只按任务类型查找
        templates = await self.list_templates(task_type=intent.task_type, limit=10)
        if templates:
            best_template = max(
                templates,
                key=lambda t: (t.avg_quality_score, t.usage_count)
            )
            logger.info(f"找到备选模板: {best_template.name}")
            return best_template
        
        logger.warning("未找到合适的模板")
        return None
    
    async def increment_usage(self, template_id: str):
        """
        增加模板使用次数
        
        Args:
            template_id: 模板ID
        """
        await self.collection.update_one(
            {"template_id": template_id},
            {"$inc": {"usage_count": 1}}
        )
    
    async def update_quality_score(self, template_id: str, new_score: float):
        """
        更新模板的平均质量评分
        
        Args:
            template_id: 模板ID
            new_score: 新的评分
        """
        template = await self.get_template(template_id)
        if template:
            # 计算新的平均分（简单平均，可以改为加权平均）
            current_avg = template.avg_quality_score
            usage_count = template.usage_count
            
            new_avg = (current_avg * (usage_count - 1) + new_score) / usage_count
            
            await self.collection.update_one(
                {"template_id": template_id},
                {"$set": {"avg_quality_score": new_avg}}
            )

