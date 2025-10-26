"""
编译 API 路由
提供 Prompt 编译功能
"""
from fastapi import APIRouter, Depends, HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from database import get_database
from models.api_models import CompileRequest, CompileResponse
from models.prompt_models import CompiledPrompt
from modules.input_layer import IntentExtractor, InputNormalizer
from modules.template_engine import TemplateManager, FragmentComposer
from modules.compiler import RuleEngine, AIOptimizer, SelfChecker
from modules.evaluation import QualityEvaluator
from modules.output import Formatter, VersionManager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["compile"])


@router.post("/compile", response_model=CompileResponse)
async def compile_prompt(
    request: CompileRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    编译 Prompt
    
    将用户输入转化为结构化、优化的 Prompt
    """
    try:
        logger.info(f"收到编译请求 - 输入长度: {len(request.user_input)}")
        
        # 1. 输入标准化
        normalizer = InputNormalizer()
        normalized_input = normalizer.normalize(request.user_input)
        
        # 2. 意图提取
        intent_extractor = IntentExtractor()
        intent = await intent_extractor.extract(normalized_input)
        
        # 3. 模板选择（如果未指定模板ID）
        template_manager = TemplateManager(db)
        template = None
        
        if request.template_id:
            template = await template_manager.get_template(request.template_id)
            if not template:
                logger.warning(f"指定的模板不存在: {request.template_id}")
        else:
            # 根据意图自动选择模板
            template = await template_manager.find_best_template(intent)
        
        # 4. 片段组合
        composer = FragmentComposer()
        
        if template:
            prompt_text = composer.compose_from_template(template, intent)
            template_id = template.template_id
            # 更新模板使用次数
            await template_manager.increment_usage(template_id)
        else:
            prompt_text = composer.compose_from_intent(intent, normalized_input)
            template_id = None
        
        # 5. 规则校验
        rule_engine = RuleEngine()
        validation_result = rule_engine.validate(prompt_text)
        
        # 自动修复常见问题
        if not validation_result.passed:
            prompt_text = rule_engine.fix_common_issues(prompt_text)
        
        # 6. AI 优化（根据优化级别）
        optimized = False
        improvements = []
        
        if request.optimization_level.value != "low":
            optimizer = AIOptimizer()
            optimization_result = await optimizer.optimize(
                prompt_text,
                intent,
                request.optimization_level
            )
            
            if optimization_result:
                optimized_prompt = optimization_result.get("optimized_prompt", prompt_text)
                
                # 处理优化返回的可能是字典的情况
                if isinstance(optimized_prompt, dict):
                    # 将结构化字典转换为文本
                    role = optimized_prompt.get("role", "")
                    objective = optimized_prompt.get("objective", "")
                    constraints = optimized_prompt.get("constraints", [])
                    
                    prompt_text = f"角色：{role}\n\n目标：{objective}"
                    if constraints:
                        prompt_text += f"\n\n约束条件：\n" + "\n".join(f"- {c}" for c in constraints)
                    if "output_format" in optimized_prompt:
                        prompt_text += f"\n\n输出格式：{optimized_prompt['output_format']}"
                else:
                    prompt_text = optimized_prompt
                
                improvements = optimization_result.get("improvements", [])
                optimized = True
                
                # 7. 自检
                checker = SelfChecker()
                check_result = await checker.check(prompt_text, prompt_text, intent)
                
                if not check_result["passed"]:
                    logger.warning("自检未通过，使用原始版本")
                    # 可以选择回退或继续使用
        
        # 8. 构建编译结果
        compiled_prompt = CompiledPrompt(
            original_input=request.user_input,
            intent=intent,
            template_id=template_id,
            role=intent.objective,  # 这里简化处理
            objective=intent.objective,
            constraints=intent.constraints,
            output_format="清晰、结构化的输出",
            context=intent.context,
            full_prompt=prompt_text,
            optimization_level=request.optimization_level,
            optimized=optimized
        )
        
        # 9. 质量评估（如果需要）
        metrics = None
        if request.auto_evaluate:
            evaluator = QualityEvaluator()
            evaluation = await evaluator.evaluate(
                prompt_text,
                intent,
                compiled_prompt.version_id
            )
            metrics = evaluation.metrics
            
            # 更新模板评分
            if template_id and metrics:
                await template_manager.update_quality_score(
                    template_id,
                    metrics.overall_score
                )
        
        # 10. 保存版本
        version_manager = VersionManager(db)
        await version_manager.save_version(compiled_prompt)
        
        # 11. 格式化输出
        formatter = Formatter()
        formatted_output = formatter._build_output_dict(compiled_prompt, metrics)
        
        # 12. 构建响应
        suggestions = []
        suggestions.extend(validation_result.suggestions)
        suggestions.extend(improvements)
        
        response = CompileResponse(
            success=True,
            compiled_prompt=compiled_prompt,
            metrics=metrics,
            suggestions=suggestions,
            formatted_output=formatted_output
        )
        
        logger.info(f"编译成功 - 版本ID: {compiled_prompt.version_id}")
        return response
        
    except Exception as e:
        logger.error(f"编译失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"编译失败: {str(e)}")

