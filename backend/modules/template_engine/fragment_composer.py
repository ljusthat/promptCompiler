"""
片段组合器
将多个模板片段组合成完整的 Prompt
"""
import logging
from typing import List, Dict, Any, Optional

from models.prompt_models import PromptTemplate, IntentResult

logger = logging.getLogger(__name__)


class FragmentComposer:
    """片段组合器类"""
    
    # 标准 Prompt 结构模板
    STANDARD_STRUCTURE = """# 角色 (Role)
{role}

# 任务目标 (Objective)
{objective}

# 约束条件 (Constraints)
{constraints}

# 输出格式 (Output Format)
{output_format}

# 上下文信息 (Context)
{context}
"""
    
    def __init__(self):
        """初始化片段组合器"""
        pass
    
    def compose_from_template(
        self,
        template: PromptTemplate,
        intent: IntentResult,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        从模板和意图组合 Prompt
        
        Args:
            template: Prompt 模板
            intent: 意图结果
            additional_context: 额外的上下文信息
            
        Returns:
            str: 组合后的完整 Prompt
        """
        # 准备变量
        context = {**intent.context, **(additional_context or {})}
        
        # 格式化约束条件
        constraints_text = self._format_list(template.constraints)
        
        # 格式化上下文
        context_text = self._format_context(context)
        
        # 组合 Prompt
        prompt = self.STANDARD_STRUCTURE.format(
            role=template.role,
            objective=template.objective,
            constraints=constraints_text,
            output_format=template.output_format,
            context=context_text
        )
        
        logger.info("从模板组合 Prompt 完成")
        return prompt.strip()
    
    def compose_from_intent(
        self,
        intent: IntentResult,
        user_input: str
    ) -> str:
        """
        直接从意图生成 Prompt（无模板）
        
        Args:
            intent: 意图结果
            user_input: 用户原始输入
            
        Returns:
            str: 生成的 Prompt
        """
        # 根据任务类型生成默认角色
        role = self._generate_role_from_intent(intent)
        
        # 使用意图中的目标
        objective = intent.objective
        
        # 格式化约束条件
        constraints_text = self._format_list(intent.constraints) if intent.constraints else "无特殊约束"
        
        # 默认输出格式
        output_format = self._generate_output_format(intent)
        
        # 格式化上下文
        context_text = self._format_context(intent.context)
        if not context_text:
            context_text = f"用户需求: {user_input}"
        
        # 组合 Prompt
        prompt = self.STANDARD_STRUCTURE.format(
            role=role,
            objective=objective,
            constraints=constraints_text,
            output_format=output_format,
            context=context_text
        )
        
        logger.info("从意图生成 Prompt 完成")
        return prompt.strip()
    
    def compose_custom(self, fragments: Dict[str, str]) -> str:
        """
        自定义片段组合
        
        Args:
            fragments: 片段字典 {section_name: content}
            
        Returns:
            str: 组合后的 Prompt
        """
        sections = []
        
        for section_name, content in fragments.items():
            if content:
                sections.append(f"# {section_name}\n{content}")
        
        prompt = "\n\n".join(sections)
        logger.info(f"自定义组合完成，包含 {len(sections)} 个片段")
        return prompt
    
    def _format_list(self, items: List[str]) -> str:
        """格式化列表为编号文本"""
        if not items:
            return "无"
        
        return "\n".join(f"{i+1}. {item}" for i, item in enumerate(items))
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """格式化上下文字典"""
        if not context:
            return "无额外上下文"
        
        lines = []
        for key, value in context.items():
            lines.append(f"- {key}: {value}")
        
        return "\n".join(lines)
    
    def _generate_role_from_intent(self, intent: IntentResult) -> str:
        """根据意图生成默认角色"""
        role_templates = {
            "generation": "你是一位专业的内容创作专家",
            "analysis": f"你是一位专业的{intent.domain}数据分析专家",
            "conversation": "你是一位经验丰富的对话助手",
            "extraction": "你是一位精准的信息提取专家",
            "transformation": "你是一位专业的格式转换专家",
            "reasoning": "你是一位逻辑严密的推理专家",
        }
        
        role = role_templates.get(intent.task_type.value, "你是一位专业的AI助手")
        return role
    
    def _generate_output_format(self, intent: IntentResult) -> str:
        """根据意图生成默认输出格式"""
        format_templates = {
            "generation": "请以清晰、结构化的方式呈现生成的内容",
            "analysis": "请提供详细的分析报告，包括数据洞察和建议",
            "conversation": "请以自然、友好的对话方式回复",
            "extraction": "请以结构化的格式（如 JSON 或表格）呈现提取的信息",
            "transformation": "请输出转换后的格式，确保格式正确",
            "reasoning": "请展示推理过程，并给出最终结论",
        }
        
        return format_templates.get(intent.task_type.value, "请以清晰、准确的方式呈现结果")
    
    def add_system_prompt(self, prompt: str, system_instructions: str) -> str:
        """
        添加系统级指令
        
        Args:
            prompt: 原始 Prompt
            system_instructions: 系统指令
            
        Returns:
            str: 添加系统指令后的 Prompt
        """
        return f"# 系统指令\n{system_instructions}\n\n{prompt}"
    
    def add_examples(self, prompt: str, examples: List[Dict[str, str]]) -> str:
        """
        添加示例
        
        Args:
            prompt: 原始 Prompt
            examples: 示例列表 [{"input": "...", "output": "..."}]
            
        Returns:
            str: 添加示例后的 Prompt
        """
        if not examples:
            return prompt
        
        examples_text = "# 参考示例\n\n"
        for i, example in enumerate(examples, 1):
            examples_text += f"## 示例 {i}\n"
            examples_text += f"输入: {example.get('input', '')}\n"
            examples_text += f"输出: {example.get('output', '')}\n\n"
        
        return f"{prompt}\n\n{examples_text}"

