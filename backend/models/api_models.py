"""
API 请求和响应模型
定义所有 API 接口的输入输出数据结构
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from .prompt_models import OptimizationLevel, CompiledPrompt, PromptTemplate, IntentResult
from .evaluation_models import QualityMetrics, EvaluationResult


# ============ 编译相关 API ============

class CompileRequest(BaseModel):
    """编译请求"""
    user_input: str = Field(description="用户原始输入")
    template_id: Optional[str] = Field(None, description="指定使用的模板ID（可选）")
    optimization_level: OptimizationLevel = Field(
        default=OptimizationLevel.MEDIUM,
        description="优化级别"
    )
    auto_evaluate: bool = Field(default=True, description="是否自动评估质量")
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_input": "帮我写一个分析财报的AI助手",
                "template_id": None,
                "optimization_level": "high",
                "auto_evaluate": True
            }
        }


class CompileResponse(BaseModel):
    """编译响应"""
    success: bool = Field(description="是否成功")
    compiled_prompt: CompiledPrompt = Field(description="编译后的 Prompt")
    metrics: Optional[QualityMetrics] = Field(None, description="质量评估指标")
    suggestions: List[str] = Field(default_factory=list, description="优化建议")
    
    # 格式化输出
    formatted_output: Dict[str, Any] = Field(description="格式化后的输出（JSON/YAML）")


# ============ 优化相关 API ============

class OptimizeRequest(BaseModel):
    """优化请求"""
    prompt_text: str = Field(description="待优化的 Prompt 文本")
    optimization_level: OptimizationLevel = Field(
        default=OptimizationLevel.MEDIUM,
        description="优化级别"
    )
    focus_areas: List[str] = Field(
        default_factory=list,
        description="重点优化的方面（如：clarity, structure, specificity）"
    )


class OptimizeResponse(BaseModel):
    """优化响应"""
    success: bool = Field(description="是否成功")
    original_prompt: str = Field(description="原始 Prompt")
    optimized_prompt: str = Field(description="优化后的 Prompt")
    improvements: List[str] = Field(description="改进点列表")
    metrics_before: QualityMetrics = Field(description="优化前的质量指标")
    metrics_after: QualityMetrics = Field(description="优化后的质量指标")


# ============ 评估相关 API ============

class EvaluateRequest(BaseModel):
    """评估请求"""
    prompt_text: str = Field(description="待评估的 Prompt 文本")
    intent: Optional[IntentResult] = Field(None, description="意图信息（可选，用于更准确的评估）")


class EvaluateResponse(BaseModel):
    """评估响应"""
    success: bool = Field(description="是否成功")
    evaluation: EvaluationResult = Field(description="评估结果")


# ============ 模板相关 API ============

class TemplateCreateRequest(BaseModel):
    """创建模板请求"""
    name: str
    description: Optional[str] = None
    role: str
    objective: str
    constraints: List[str] = Field(default_factory=list)
    output_format: str
    context_vars: Dict[str, str] = Field(default_factory=dict)
    task_types: List[str] = Field(default_factory=list)
    domains: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)


class TemplateUpdateRequest(BaseModel):
    """更新模板请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None
    objective: Optional[str] = None
    constraints: Optional[List[str]] = None
    output_format: Optional[str] = None
    context_vars: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None


class TemplateListResponse(BaseModel):
    """模板列表响应"""
    success: bool
    templates: List[PromptTemplate]
    total: int


# ============ 历史记录相关 API ============

class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    success: bool
    records: List[CompiledPrompt]
    total: int
    page: int
    page_size: int


# ============ 通用响应 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error_code: str
    error_message: str
    details: Optional[Dict[str, Any]] = None

