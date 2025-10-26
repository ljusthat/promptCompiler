"""
FastAPI 主程序
Prompt Compiler 系统的入口文件
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from database import Database
from api.routes import compile, optimize, evaluate, templates, history

# 配置日志
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    logger.info("正在启动 Prompt Compiler 系统...")
    
    try:
        # 连接数据库
        await Database.connect()
        logger.info("数据库连接成功")
        
        yield
        
    finally:
        # 关闭时
        logger.info("正在关闭 Prompt Compiler 系统...")
        await Database.disconnect()
        logger.info("数据库连接已关闭")


# 创建 FastAPI 应用
app = FastAPI(
    title="Prompt Compiler API",
    description="基于语义编译与自适应优化的 Prompt 输出系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(compile.router)
app.include_router(optimize.router)
app.include_router(evaluate.router)
app.include_router(templates.router)
app.include_router(history.router)


# 根路由
@app.get("/")
async def root():
    """根路径，返回 API 信息"""
    return {
        "name": "Prompt Compiler API",
        "version": "1.0.0",
        "description": "基于语义编译与自适应优化的 Prompt 输出系统",
        "endpoints": {
            "compile": "/api/compile",
            "optimize": "/api/optimize",
            "evaluate": "/api/evaluate",
            "templates": "/api/templates",
            "history": "/api/history"
        },
        "docs": "/docs",
        "status": "running"
    }


# 健康检查
@app.get("/health")
async def health_check():
    """健康检查端点"""
    try:
        # 检查数据库连接
        db = Database.get_db()
        await db.command('ping')
        
        return {
            "status": "healthy",
            "database": "connected",
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    logger.error(f"未处理的异常: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error_code": "INTERNAL_SERVER_ERROR",
            "error_message": "服务器内部错误",
            "details": str(exc) if settings.DEBUG else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level="info" if settings.DEBUG else "warning"
    )

