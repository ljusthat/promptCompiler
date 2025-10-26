"""
MongoDB 数据库连接与操作封装
提供数据库连接管理和基础 CRUD 操作
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

try:
    from config import settings
except ImportError:
    # 如果config导入失败，提供默认配置
    class Settings:
        MONGODB_URL = "mongodb://localhost:27017"
        MONGODB_DB_NAME = "prompt_compiler"
    settings = Settings()

logger = logging.getLogger(__name__)


class Database:
    """数据库管理类"""
    
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    
    @classmethod
    async def connect(cls):
        """建立数据库连接"""
        try:
            cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
            cls.db = cls.client[settings.MONGODB_DB_NAME]
            
            # 测试连接
            await cls.client.admin.command('ping')
            logger.info(f"成功连接到 MongoDB: {settings.MONGODB_DB_NAME}")
            
            # 创建索引
            await cls._create_indexes()
            
        except Exception as e:
            logger.error(f"MongoDB 连接失败: {e}")
            raise
    
    @classmethod
    async def disconnect(cls):
        """关闭数据库连接"""
        if cls.client is not None:
            cls.client.close()
            logger.info("MongoDB 连接已关闭")
    
    @classmethod
    async def _create_indexes(cls):
        """创建数据库索引"""
        if cls.db is None:
            return
        
        # 为模板集合创建索引
        await cls.db.templates.create_index("template_id", unique=True)
        await cls.db.templates.create_index("created_at")
        
        # 为历史记录创建索引
        await cls.db.history.create_index("version_id", unique=True)
        await cls.db.history.create_index("created_at")
        
        # 为反馈记录创建索引
        await cls.db.feedback.create_index("prompt_id")
        await cls.db.feedback.create_index("created_at")
        
        logger.info("数据库索引创建完成")
    
    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """获取数据库实例"""
        if cls.db is None:
            raise RuntimeError("数据库未连接，请先调用 connect()")
        return cls.db


# 依赖注入函数，用于 FastAPI 路由
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI 依赖注入：获取数据库实例"""
    return Database.get_db()

