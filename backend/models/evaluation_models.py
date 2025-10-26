"""
评估相关数据模型
定义质量评估、反馈记录等数据结构
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
import uuid


class QualityMetrics(BaseModel):
    """质量评估指标"""
    structure_score: float = Field(ge=0.0, le=1.0, description="结构合规率 (0-1)")
    consistency_score: float = Field(ge=0.0, le=1.0, description="目标一致性 (0-1)")
    completeness_score: float = Field(ge=0.0, le=1.0, description="语义完整度 (0-1)")
    clarity_score: float = Field(ge=0.0, le=1.0, description="表达清晰度 (0-1)")
    overall_score: float = Field(ge=0.0, le=1.0, description="综合评分 (0-1)")
    
    def calculate_overall(self):
        """计算综合评分（加权平均）"""
        weights = {
            'structure': 0.25,
            'consistency': 0.30,
            'completeness': 0.25,
            'clarity': 0.20
        }
        self.overall_score = (
            self.structure_score * weights['structure'] +
            self.consistency_score * weights['consistency'] +
            self.completeness_score * weights['completeness'] +
            self.clarity_score * weights['clarity']
        )
        return self.overall_score


class EvaluationResult(BaseModel):
    """评估结果"""
    evaluation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt_version_id: str = Field(description="被评估的 Prompt 版本ID")
    
    # 质量指标
    metrics: QualityMetrics = Field(description="质量评估指标")
    
    # 详细分析
    strengths: List[str] = Field(default_factory=list, description="优点列表")
    weaknesses: List[str] = Field(default_factory=list, description="不足之处")
    suggestions: List[str] = Field(default_factory=list, description="改进建议")
    
    # AI 评估的原始输出
    ai_analysis: Optional[str] = Field(None, description="AI 的详细分析文本")
    
    # 元数据
    evaluated_at: datetime = Field(default_factory=datetime.now)
    evaluator: str = Field(default="zhipu_ai", description="评估者（AI 或人工）")


class FeedbackRecord(BaseModel):
    """反馈记录"""
    feedback_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    prompt_version_id: str = Field(description="关联的 Prompt 版本ID")
    
    # 反馈内容
    rating: int = Field(ge=1, le=5, description="用户评分 (1-5)")
    comment: Optional[str] = Field(None, description="用户评论")
    
    # 使用效果反馈
    effectiveness: Optional[int] = Field(None, ge=1, le=5, description="实际使用效果评分")
    actual_output_quality: Optional[int] = Field(None, ge=1, le=5, description="实际输出质量评分")
    
    # 改进建议
    improvement_suggestions: List[str] = Field(default_factory=list, description="用户建议")
    
    # 元数据
    user_id: Optional[str] = Field(None, description="用户ID")
    created_at: datetime = Field(default_factory=datetime.now)
    
    # 标签
    tags: List[str] = Field(default_factory=list, description="反馈标签")


class ComparisonResult(BaseModel):
    """Prompt 对比结果"""
    comparison_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # 对比的两个版本
    version_a_id: str
    version_b_id: str
    
    # 对比维度
    metrics_comparison: Dict[str, Dict[str, float]] = Field(
        description="各项指标对比 {metric_name: {version_a: score, version_b: score}}"
    )
    
    # 胜出者
    winner: Optional[str] = Field(None, description="综合评分更高的版本ID")
    
    # 详细分析
    analysis: str = Field(description="对比分析说明")
    
    created_at: datetime = Field(default_factory=datetime.now)

