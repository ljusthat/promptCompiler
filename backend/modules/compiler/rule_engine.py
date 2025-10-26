"""
规则引擎
执行结构检查、禁词过滤、长度限制等规则校验
"""
import re
import logging
from typing import List, Dict, Tuple

logger = logging.getLogger(__name__)


class ValidationResult:
    """校验结果"""
    
    def __init__(self):
        self.passed = True
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.suggestions: List[str] = []
    
    def add_error(self, message: str):
        """添加错误"""
        self.passed = False
        self.errors.append(message)
    
    def add_warning(self, message: str):
        """添加警告"""
        self.warnings.append(message)
    
    def add_suggestion(self, message: str):
        """添加建议"""
        self.suggestions.append(message)


class RuleEngine:
    """规则引擎类"""
    
    # 禁用词列表（可配置）
    FORBIDDEN_WORDS = [
        "违法", "暴力", "色情", "赌博",
        # 可以根据需要添加更多
    ]
    
    # 结构必需的关键词
    REQUIRED_SECTIONS = ["角色", "目标", "输出"]
    
    def __init__(self):
        """初始化规则引擎"""
        pass
    
    def validate(self, prompt_text: str) -> ValidationResult:
        """
        执行完整的规则校验
        
        Args:
            prompt_text: 待校验的 Prompt 文本
            
        Returns:
            ValidationResult: 校验结果
        """
        result = ValidationResult()
        
        # 1. 长度检查
        self._check_length(prompt_text, result)
        
        # 2. 结构检查
        self._check_structure(prompt_text, result)
        
        # 3. 禁词过滤
        self._check_forbidden_words(prompt_text, result)
        
        # 4. 清晰度检查
        self._check_clarity(prompt_text, result)
        
        # 5. 格式检查
        self._check_format(prompt_text, result)
        
        logger.info(
            f"规则校验完成 - "
            f"通过: {result.passed}, "
            f"错误: {len(result.errors)}, "
            f"警告: {len(result.warnings)}"
        )
        
        return result
    
    def _check_length(self, text: str, result: ValidationResult):
        """长度检查"""
        length = len(text)
        
        if length < 10:
            result.add_error("Prompt 过短（少于 10 字符），无法有效指导 AI")
        elif length < 50:
            result.add_warning("Prompt 较短，建议增加更多细节说明")
        
        if length > 4000:
            result.add_warning("Prompt 过长，可能影响 AI 理解，建议精简")
        
        if 50 <= length <= 2000:
            result.add_suggestion("Prompt 长度适中")
    
    def _check_structure(self, text: str, result: ValidationResult):
        """结构检查"""
        # 检查是否包含基本结构
        missing_sections = []
        
        for section in self.REQUIRED_SECTIONS:
            if section not in text and section.lower() not in text.lower():
                missing_sections.append(section)
        
        if missing_sections:
            result.add_warning(f"缺少推荐的结构部分: {', '.join(missing_sections)}")
            result.add_suggestion("建议添加明确的角色定义、任务目标和输出格式说明")
        else:
            result.add_suggestion("Prompt 结构完整")
    
    def _check_forbidden_words(self, text: str, result: ValidationResult):
        """禁词过滤"""
        found_forbidden = []
        
        for word in self.FORBIDDEN_WORDS:
            if word in text:
                found_forbidden.append(word)
        
        if found_forbidden:
            result.add_error(f"包含禁用词汇: {', '.join(found_forbidden)}")
    
    def _check_clarity(self, text: str, result: ValidationResult):
        """清晰度检查"""
        # 检查是否有过多的模糊词汇
        vague_words = ["可能", "大概", "也许", "应该", "尽量", "试试"]
        vague_count = sum(text.count(word) for word in vague_words)
        
        if vague_count > 3:
            result.add_warning(f"包含过多模糊词汇（{vague_count} 个），建议使用更明确的表达")
            result.add_suggestion("使用 '必须'、'一定'、'明确' 等词替代模糊表达")
        
        # 检查是否有明确的动词
        action_verbs = ["分析", "生成", "提取", "转换", "总结", "评估", "创建"]
        has_action = any(verb in text for verb in action_verbs)
        
        if not has_action:
            result.add_suggestion("建议使用明确的动作动词来描述任务")
    
    def _check_format(self, text: str, result: ValidationResult):
        """格式检查"""
        # 检查是否有合理的段落结构
        lines = text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) == 1:
            result.add_suggestion("建议使用分段或标题来组织内容，提高可读性")
        
        # 检查是否有编号或列表
        has_list = any(re.match(r'^\s*[\d\-\*•]+', line) for line in lines)
        if not has_list and len(non_empty_lines) > 5:
            result.add_suggestion("对于复杂内容，建议使用编号列表组织信息")
    
    def fix_common_issues(self, text: str) -> str:
        """
        自动修复常见问题
        
        Args:
            text: 原始文本
            
        Returns:
            str: 修复后的文本
        """
        # 移除多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 统一标题格式
        text = re.sub(r'^#+\s*', '# ', text, flags=re.MULTILINE)
        
        # 移除行尾空白
        text = '\n'.join(line.rstrip() for line in text.split('\n'))
        
        logger.info("常见问题已自动修复")
        return text.strip()
    
    def calculate_complexity_score(self, text: str) -> float:
        """
        计算 Prompt 复杂度评分（0-1）
        
        Args:
            text: Prompt 文本
            
        Returns:
            float: 复杂度评分，越高越复杂
        """
        score = 0.0
        
        # 长度因素
        length = len(text)
        if length > 500:
            score += 0.3
        elif length > 200:
            score += 0.2
        else:
            score += 0.1
        
        # 结构因素
        has_sections = len(re.findall(r'^#+', text, re.MULTILINE))
        score += min(has_sections * 0.1, 0.3)
        
        # 列表和条件因素
        has_lists = len(re.findall(r'^\s*[\d\-\*]', text, re.MULTILINE))
        score += min(has_lists * 0.05, 0.2)
        
        # 约束条件数量
        constraints = len(re.findall(r'(必须|不能|应该|需要|禁止)', text))
        score += min(constraints * 0.05, 0.2)
        
        return min(score, 1.0)

