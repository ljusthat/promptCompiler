"""
Prompt 相关数据模型
定义意图提取、模板、编译结果等核心数据结构
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum
import uuid


class OptimizationLevel(str, Enum):
    """优化级别枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskType(str, Enum):
    """任务类型枚举"""
    GENERATION = "generation"  # 内容生成
    ANALYSIS = "analysis"      # 数据分析
    CONVERSATION = "conversation"  # 对话交互
    EXTRACTION = "extraction"   # 信息提取
    TRANSFORMATION = "transformation"  # 格式转换
    REASONING = "reasoning"     # 推理决策
    OTHER = "other"


class IntentResult(BaseModel):
    """意图提取结果"""
    task_type: TaskType = Field(description="任务类型")
    domain: str = Field(description="领域分类（如：金融、医疗、教育等）")
    objective: str = Field(description="核心目标描述")
    constraints: List[str] = Field(default_factory=list, description="约束条件列表")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")
    confidence: float = Field(ge=0.0, le=1.0, description="意图识别置信度")


class PromptTemplate(BaseModel):
    """Prompt 模板"""
    template_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="模板唯一标识")
    name: str = Field(description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    
    # 模板核心结构
    role: str = Field(description="角色定义")
    objective: str = Field(description="任务目标")
    constraints: List[str] = Field(default_factory=list, description="约束条件")
    output_format: str = Field(description="输出格式要求")
    
    # 模板变量
    context_vars: Dict[str, str] = Field(default_factory=dict, description="上下文变量")
    
    # 元数据
    task_types: List[TaskType] = Field(default_factory=list, description="适用的任务类型")
    domains: List[str] = Field(default_factory=list, description="适用领域")
    tags: List[str] = Field(default_factory=list, description="标签")
    
    # 时间戳
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # 使用统计
    usage_count: int = Field(default=0, description="使用次数")
    avg_quality_score: float = Field(default=0.0, description="平均质量评分")


class CompiledPrompt(BaseModel):
    """编译后的 Prompt"""
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="版本唯一标识")
    
    # 原始输入
    original_input: str = Field(description="用户原始输入")
    
    # 意图分析结果
    intent: IntentResult = Field(description="意图提取结果")
    
    # 使用的模板
    template_id: Optional[str] = Field(None, description="使用的模板ID")
    
    # 编译结果
    role: str = Field(description="角色定义")
    objective: str = Field(description="任务目标")
    constraints: List[str] = Field(default_factory=list, description="约束条件")
    output_format: str = Field(description="输出格式")
    context: Dict[str, Any] = Field(default_factory=dict, description="上下文信息")
    
    # 完整的 Prompt 文本
    full_prompt: str = Field(description="完整的结构化 Prompt")
    
    # 优化信息
    optimization_level: OptimizationLevel = Field(description="优化级别")
    optimized: bool = Field(default=False, description="是否经过AI优化")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "original_input": "帮我写一个分析财报的AI助手",
                "intent": {
                    "task_type": "analysis",
                    "domain": "finance",
                    "objective": "分析公司财务报表",
                    "constraints": ["专业性", "准确性"],
                    "keywords": ["财报", "分析", "AI助手"],
                    "context": {},
                    "confidence": 0.95
                },
                "role": "你是一位专业的财务分析专家",
                "objective": "分析公司财务报表，提供专业洞察",
                "full_prompt": "# 角色\\n你是一位专业的财务分析专家...",
                "optimization_level": "high"
            }
        }

