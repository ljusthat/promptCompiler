"""
模板管理 API 路由
提供模板的 CRUD 操作
"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from database import get_database
from models.api_models import (
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplateListResponse
)
from models.prompt_models import PromptTemplate
from modules.template_engine import TemplateManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/templates", tags=["templates"])


@router.post("/", response_model=PromptTemplate)
async def create_template(
    request: TemplateCreateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """创建新模板"""
    try:
        template = PromptTemplate(
            name=request.name,
            description=request.description,
            role=request.role,
            objective=request.objective,
            constraints=request.constraints,
            output_format=request.output_format,
            context_vars=request.context_vars,
            task_types=[t for t in request.task_types],
            domains=request.domains,
            tags=request.tags
        )
        
        manager = TemplateManager(db)
        created = await manager.create_template(template)
        
        logger.info(f"模板创建成功: {created.template_id}")
        return created
        
    except Exception as e:
        logger.error(f"创建模板失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"创建模板失败: {str(e)}")


@router.get("/", response_model=TemplateListResponse)
async def list_templates(
    task_type: str = None,
    domain: str = None,
    limit: int = 50,
    skip: int = 0,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """列出模板"""
    try:
        manager = TemplateManager(db)
        
        # 转换任务类型
        from models.prompt_models import TaskType
        task_type_enum = TaskType(task_type) if task_type else None
        
        templates = await manager.list_templates(
            task_type=task_type_enum,
            domain=domain,
            limit=limit,
            skip=skip
        )
        
        total = len(templates)  # 简化版本，实际应该查询总数
        
        return TemplateListResponse(
            success=True,
            templates=templates,
            total=total
        )
        
    except Exception as e:
        logger.error(f"列出模板失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"列出模板失败: {str(e)}")


@router.get("/{template_id}", response_model=PromptTemplate)
async def get_template(
    template_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """获取指定模板"""
    try:
        manager = TemplateManager(db)
        template = await manager.get_template(template_id)
        
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        return template
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取模板失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取模板失败: {str(e)}")


@router.put("/{template_id}", response_model=PromptTemplate)
async def update_template(
    template_id: str,
    request: TemplateUpdateRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """更新模板"""
    try:
        manager = TemplateManager(db)
        
        # 构建更新字典（仅包含非 None 的字段）
        updates = {}
        for field, value in request.model_dump().items():
            if value is not None:
                updates[field] = value
        
        if not updates:
            raise HTTPException(status_code=400, detail="没有提供更新字段")
        
        updated = await manager.update_template(template_id, updates)
        
        if not updated:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        logger.info(f"模板更新成功: {template_id}")
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模板失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"更新模板失败: {str(e)}")


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """删除模板"""
    try:
        manager = TemplateManager(db)
        success = await manager.delete_template(template_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="模板不存在")
        
        logger.info(f"模板删除成功: {template_id}")
        return {"success": True, "message": "模板已删除"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除模板失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"删除模板失败: {str(e)}")

