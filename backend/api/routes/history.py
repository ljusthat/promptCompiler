"""
历史记录 API 路由
提供 Prompt 历史版本查询
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from database import get_database
from models.api_models import HistoryListResponse
from modules.output import VersionManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/history", tags=["history"])


@router.get("/", response_model=HistoryListResponse)
async def list_history(
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    列出历史记录
    
    返回最近的 Prompt 编译历史
    """
    try:
        manager = VersionManager(db)
        
        records = await manager.list_versions(limit=limit, skip=skip)
        total = await manager.count_versions()
        
        page = (skip // limit) + 1 if limit > 0 else 1
        
        return HistoryListResponse(
            success=True,
            records=records,
            total=total,
            page=page,
            page_size=limit
        )
        
    except Exception as e:
        logger.error(f"列出历史记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出历史记录失败: {str(e)}")


@router.get("/{version_id}")
async def get_history(
    version_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """获取指定历史版本"""
    try:
        manager = VersionManager(db)
        version = await manager.get_version(version_id)
        
        if not version:
            raise HTTPException(status_code=404, detail="版本不存在")
        
        return version
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取历史版本失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取历史版本失败: {str(e)}")


@router.get("/search/")
async def search_history(
    q: str = Query(..., description="搜索关键词"),
    limit: int = Query(default=20, ge=1, le=100),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """搜索历史记录"""
    try:
        manager = VersionManager(db)
        results = await manager.search_versions(q, limit=limit)
        
        return {
            "success": True,
            "results": results,
            "count": len(results)
        }
        
    except Exception as e:
        logger.error(f"搜索历史记录失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"搜索历史记录失败: {str(e)}")


@router.get("/stats/summary")
async def get_statistics(
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """获取历史统计信息"""
    try:
        manager = VersionManager(db)
        stats = await manager.get_version_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

