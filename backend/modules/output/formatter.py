"""
格式化器
将 Prompt 输出为不同格式（JSON、YAML等）
"""
import json
import yaml
import logging
from typing import Dict, Any
from datetime import datetime

from models.prompt_models import CompiledPrompt
from models.evaluation_models import QualityMetrics

logger = logging.getLogger(__name__)


class Formatter:
    """格式化器类"""
    
    def __init__(self):
        """初始化格式化器"""
        pass
    
    def to_json(self, compiled_prompt: CompiledPrompt, metrics: QualityMetrics = None) -> str:
        """
        输出为 JSON 格式
        
        Args:
            compiled_prompt: 编译后的 Prompt
            metrics: 质量指标（可选）
            
        Returns:
            str: JSON 字符串
        """
        output_dict = self._build_output_dict(compiled_prompt, metrics)
        
        json_str = json.dumps(output_dict, ensure_ascii=False, indent=2)
        logger.info("输出为 JSON 格式完成")
        return json_str
    
    def to_yaml(self, compiled_prompt: CompiledPrompt, metrics: QualityMetrics = None) -> str:
        """
        输出为 YAML 格式
        
        Args:
            compiled_prompt: 编译后的 Prompt
            metrics: 质量指标（可选）
            
        Returns:
            str: YAML 字符串
        """
        output_dict = self._build_output_dict(compiled_prompt, metrics)
        
        yaml_str = yaml.dump(
            output_dict,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False
        )
        logger.info("输出为 YAML 格式完成")
        return yaml_str
    
    def to_markdown(self, compiled_prompt: CompiledPrompt, metrics: QualityMetrics = None) -> str:
        """
        输出为 Markdown 格式
        
        Args:
            compiled_prompt: 编译后的 Prompt
            metrics: 质量指标（可选）
            
        Returns:
            str: Markdown 字符串
        """
        md_parts = []
        
        # 标题
        md_parts.append(f"# Compiled Prompt\n")
        md_parts.append(f"**Version ID**: `{compiled_prompt.version_id}`\n")
        md_parts.append(f"**Created**: {compiled_prompt.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
        md_parts.append(f"**Optimization Level**: {compiled_prompt.optimization_level}\n")
        
        # 原始输入
        md_parts.append(f"\n## Original Input\n")
        md_parts.append(f"```\n{compiled_prompt.original_input}\n```\n")
        
        # 意图分析
        md_parts.append(f"\n## Intent Analysis\n")
        md_parts.append(f"- **Task Type**: {compiled_prompt.intent.task_type}\n")
        md_parts.append(f"- **Domain**: {compiled_prompt.intent.domain}\n")
        md_parts.append(f"- **Objective**: {compiled_prompt.intent.objective}\n")
        md_parts.append(f"- **Confidence**: {compiled_prompt.intent.confidence:.2%}\n")
        
        # 编译后的 Prompt
        md_parts.append(f"\n## Compiled Prompt\n")
        md_parts.append(f"```\n{compiled_prompt.full_prompt}\n```\n")
        
        # 质量指标
        if metrics:
            md_parts.append(f"\n## Quality Metrics\n")
            md_parts.append(f"- **Structure**: {metrics.structure_score:.2%}\n")
            md_parts.append(f"- **Consistency**: {metrics.consistency_score:.2%}\n")
            md_parts.append(f"- **Completeness**: {metrics.completeness_score:.2%}\n")
            md_parts.append(f"- **Clarity**: {metrics.clarity_score:.2%}\n")
            md_parts.append(f"- **Overall**: {metrics.overall_score:.2%}\n")
        
        markdown = "".join(md_parts)
        logger.info("输出为 Markdown 格式完成")
        return markdown
    
    def to_plain_text(self, compiled_prompt: CompiledPrompt) -> str:
        """
        输出为纯文本格式（仅 Prompt 内容）
        
        Args:
            compiled_prompt: 编译后的 Prompt
            
        Returns:
            str: 纯文本
        """
        return compiled_prompt.full_prompt
    
    def _build_output_dict(
        self,
        compiled_prompt: CompiledPrompt,
        metrics: QualityMetrics = None
    ) -> Dict[str, Any]:
        """
        构建输出字典
        
        Args:
            compiled_prompt: 编译后的 Prompt
            metrics: 质量指标（可选）
            
        Returns:
            Dict: 输出字典
        """
        output = {
            "version_id": compiled_prompt.version_id,
            "created_at": compiled_prompt.created_at.isoformat(),
            "optimization_level": compiled_prompt.optimization_level,
            "optimized": compiled_prompt.optimized,
            "original_input": compiled_prompt.original_input,
            "intent": {
                "task_type": compiled_prompt.intent.task_type,
                "domain": compiled_prompt.intent.domain,
                "objective": compiled_prompt.intent.objective,
                "constraints": compiled_prompt.intent.constraints,
                "keywords": compiled_prompt.intent.keywords,
                "confidence": compiled_prompt.intent.confidence
            },
            "prompt": {
                "role": compiled_prompt.role,
                "objective": compiled_prompt.objective,
                "constraints": compiled_prompt.constraints,
                "output_format": compiled_prompt.output_format,
                "context": compiled_prompt.context,
                "full_text": compiled_prompt.full_prompt
            }
        }
        
        if compiled_prompt.template_id:
            output["template_id"] = compiled_prompt.template_id
        
        if metrics:
            output["quality_metrics"] = {
                "structure_score": metrics.structure_score,
                "consistency_score": metrics.consistency_score,
                "completeness_score": metrics.completeness_score,
                "clarity_score": metrics.clarity_score,
                "overall_score": metrics.overall_score
            }
        
        return output
    
    def format_api_response(
        self,
        compiled_prompt: CompiledPrompt,
        metrics: QualityMetrics = None,
        suggestions: list = None
    ) -> Dict[str, Any]:
        """
        格式化为 API 响应格式
        
        Args:
            compiled_prompt: 编译后的 Prompt
            metrics: 质量指标（可选）
            suggestions: 建议列表（可选）
            
        Returns:
            Dict: API 响应字典
        """
        response = {
            "success": True,
            "compiled_prompt": compiled_prompt.model_dump(),
            "formatted_output": self._build_output_dict(compiled_prompt, metrics)
        }
        
        if metrics:
            response["metrics"] = metrics.model_dump()
        
        if suggestions:
            response["suggestions"] = suggestions
        
        return response

