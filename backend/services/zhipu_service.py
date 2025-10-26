"""
智谱 AI 服务封装
提供意图提取、Prompt 优化和质量评估三大核心功能
"""
import json
import logging
from typing import Dict, Any, Optional
from zhipuai import ZhipuAI

from config import settings
from models.prompt_models import IntentResult, TaskType
from models.evaluation_models import QualityMetrics

logger = logging.getLogger(__name__)


class ZhipuAIService:
    """智谱 AI 服务类"""
    
    def __init__(self):
        """初始化智谱 AI 客户端"""
        self.client = ZhipuAI(api_key=settings.ZHIPU_API_KEY)
        self.model = "glm-4-flash"  # 使用 glm-4-flash 模型
    
    async def intent_extraction(self, user_input: str) -> IntentResult:
        """
        意图提取：分析用户输入，识别任务类型、领域和目标
        
        Args:
            user_input: 用户原始输入
            
        Returns:
            IntentResult: 意图提取结果
        """
        try:
            # 构建意图提取的 Prompt
            system_prompt = """你是一个专业的意图分析专家。
分析用户输入，提取以下信息并以 JSON 格式返回：
{
    "task_type": "任务类型（generation/analysis/conversation/extraction/transformation/reasoning/other）",
    "domain": "领域分类（如：金融、医疗、教育、技术等）",
    "objective": "核心目标的简洁描述",
    "constraints": ["约束条件1", "约束条件2"],
    "keywords": ["关键词1", "关键词2"],
    "context": {"key": "value"},
    "confidence": 0.95
}

请确保返回的是纯 JSON 格式，不要包含其他文字。"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请分析以下用户输入：\n{user_input}"}
                ],
                temperature=0.3,  # 较低温度以保证稳定性
            )
            
            # 解析响应
            content = response.choices[0].message.content
            logger.info(f"意图提取原始响应: {content}")
            
            # 提取 JSON 部分（移除可能的 markdown 代码块）
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            intent_data = json.loads(content)
            
            # 验证并转换任务类型
            task_type_str = intent_data.get("task_type", "other").lower()
            try:
                task_type = TaskType(task_type_str)
            except ValueError:
                task_type = TaskType.OTHER
            
            # 构建 IntentResult 对象
            intent_result = IntentResult(
                task_type=task_type,
                domain=intent_data.get("domain", "general"),
                objective=intent_data.get("objective", user_input),
                constraints=intent_data.get("constraints", []),
                keywords=intent_data.get("keywords", []),
                context=intent_data.get("context", {}),
                confidence=intent_data.get("confidence", 0.8)
            )
            
            logger.info(f"意图提取成功: {intent_result.task_type} - {intent_result.domain}")
            return intent_result
            
        except Exception as e:
            logger.error(f"意图提取失败: {e}")
            # 返回默认结果
            return IntentResult(
                task_type=TaskType.OTHER,
                domain="general",
                objective=user_input,
                constraints=[],
                keywords=[],
                context={},
                confidence=0.5
            )
    
    async def prompt_optimization(
        self,
        prompt_text: str,
        intent: Optional[IntentResult] = None,
        focus_areas: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        Prompt 优化：重写并增强 Prompt 的质量
        
        Args:
            prompt_text: 原始 Prompt 文本
            intent: 意图信息（可选）
            focus_areas: 重点优化的方面（可选）
            
        Returns:
            Dict: 包含优化后的 Prompt 和改进说明
        """
        try:
            # 构建优化 Prompt
            system_prompt = """你是一个专业的 Prompt 工程专家。
你的任务是优化用户提供的 Prompt，使其更清晰、更具体、更有效。

优化要点：
1. 明确角色定义
2. 清晰的任务目标
3. 具体的约束条件
4. 明确的输出格式要求
5. 必要的上下文信息

重要：optimized_prompt 必须是纯文本字符串，不能是 JSON 对象，而是一个完整的、可直接使用的 Prompt 文本。

请返回 JSON 格式：
{
    "optimized_prompt": "角色：xxx\\n\\n目标：xxx\\n\\n约束条件：\\n- xxx\\n- xxx\\n\\n输出格式：xxx",
    "improvements": ["改进点1", "改进点2", "改进点3"],
    "explanation": "优化思路的简要说明"
}"""
            
            user_message = f"请优化以下 Prompt：\n\n{prompt_text}"
            
            if intent:
                user_message += f"\n\n任务类型：{intent.task_type}\n领域：{intent.domain}\n目标：{intent.objective}"
            
            if focus_areas:
                user_message += f"\n\n重点优化方面：{', '.join(focus_areas)}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.5,
            )
            
            content = response.choices[0].message.content
            logger.info(f"Prompt 优化原始响应: {content[:200]}...")
            
            # 提取 JSON 部分
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            logger.info("Prompt 优化成功")
            return result
            
        except Exception as e:
            logger.error(f"Prompt 优化失败: {e}")
            return {
                "optimized_prompt": prompt_text,
                "improvements": [],
                "explanation": "优化过程出现错误，返回原始 Prompt"
            }
    
    async def quality_evaluation(
        self,
        prompt_text: str,
        intent: Optional[IntentResult] = None
    ) -> Dict[str, Any]:
        """
        质量评估：多维度评估 Prompt 的质量
        
        Args:
            prompt_text: 待评估的 Prompt 文本
            intent: 意图信息（可选，用于更准确的评估）
            
        Returns:
            Dict: 包含质量指标和详细分析
        """
        try:
            # 构建评估 Prompt
            system_prompt = """你是一个专业的 Prompt 质量评估专家。
请从以下维度评估 Prompt 的质量（每项 0-1 分）：

1. structure_score（结构合规率）：是否包含角色、目标、约束、输出格式等完整结构
2. consistency_score（目标一致性）：各部分是否围绕核心目标，无矛盾
3. completeness_score（语义完整度）：信息是否完整，无歧义
4. clarity_score（表达清晰度）：语言是否清晰、简洁、易懂

请返回 JSON 格式：
{
    "structure_score": 0.85,
    "consistency_score": 0.90,
    "completeness_score": 0.80,
    "clarity_score": 0.88,
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["不足1", "不足2"],
    "suggestions": ["建议1", "建议2"],
    "analysis": "详细分析说明"
}"""
            
            user_message = f"请评估以下 Prompt 的质量：\n\n{prompt_text}"
            
            if intent:
                user_message += f"\n\n预期任务类型：{intent.task_type}\n预期目标：{intent.objective}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.3,
            )
            
            content = response.choices[0].message.content
            logger.info(f"质量评估原始响应: {content[:200]}...")
            
            # 提取 JSON 部分
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # 计算综合评分
            metrics = QualityMetrics(
                structure_score=result.get("structure_score", 0.7),
                consistency_score=result.get("consistency_score", 0.7),
                completeness_score=result.get("completeness_score", 0.7),
                clarity_score=result.get("clarity_score", 0.7),
                overall_score=0.0
            )
            metrics.calculate_overall()
            
            result["metrics"] = metrics
            logger.info(f"质量评估成功，综合评分: {metrics.overall_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"质量评估失败: {e}")
            # 返回默认评估
            default_metrics = QualityMetrics(
                structure_score=0.5,
                consistency_score=0.5,
                completeness_score=0.5,
                clarity_score=0.5,
                overall_score=0.5
            )
            return {
                "metrics": default_metrics,
                "strengths": [],
                "weaknesses": ["评估过程出现错误"],
                "suggestions": ["请检查 Prompt 格式"],
                "analysis": "无法完成详细分析"
            }

