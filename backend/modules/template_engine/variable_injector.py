"""
变量注入器
将动态变量注入到模板中
"""
import re
import logging
from typing import Dict, Any
from jinja2 import Template, Environment, meta

logger = logging.getLogger(__name__)


class VariableInjector:
    """变量注入器类"""
    
    def __init__(self):
        """初始化变量注入器"""
        self.env = Environment()
    
    def inject(self, template_text: str, variables: Dict[str, Any]) -> str:
        """
        将变量注入到模板中
        
        Args:
            template_text: 模板文本（支持 Jinja2 语法）
            variables: 变量字典
            
        Returns:
            str: 注入变量后的文本
        """
        try:
            template = Template(template_text)
            result = template.render(**variables)
            logger.info(f"变量注入成功，注入了 {len(variables)} 个变量")
            return result
        except Exception as e:
            logger.error(f"变量注入失败: {e}")
            # 如果 Jinja2 失败，尝试简单替换
            return self._simple_replace(template_text, variables)
    
    def _simple_replace(self, text: str, variables: Dict[str, Any]) -> str:
        """
        简单的变量替换（使用 {var_name} 格式）
        
        Args:
            text: 文本
            variables: 变量字典
            
        Returns:
            str: 替换后的文本
        """
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            text = text.replace(placeholder, str(value))
        
        return text
    
    def extract_variables(self, template_text: str) -> list:
        """
        从模板中提取所有变量名
        
        Args:
            template_text: 模板文本
            
        Returns:
            list: 变量名列表
        """
        try:
            # 使用 Jinja2 提取变量
            ast = self.env.parse(template_text)
            variables = meta.find_undeclared_variables(ast)
            return list(variables)
        except Exception:
            # 如果 Jinja2 失败，使用正则提取
            return re.findall(r'\{(\w+)\}', template_text)
    
    def validate_variables(self, template_text: str, variables: Dict[str, Any]) -> bool:
        """
        验证是否提供了所有必需的变量
        
        Args:
            template_text: 模板文本
            variables: 提供的变量
            
        Returns:
            bool: 是否所有必需变量都已提供
        """
        required_vars = self.extract_variables(template_text)
        provided_vars = set(variables.keys())
        
        missing_vars = set(required_vars) - provided_vars
        
        if missing_vars:
            logger.warning(f"缺少变量: {missing_vars}")
            return False
        
        return True
    
    def inject_with_defaults(
        self,
        template_text: str,
        variables: Dict[str, Any],
        defaults: Dict[str, Any]
    ) -> str:
        """
        带默认值的变量注入
        
        Args:
            template_text: 模板文本
            variables: 提供的变量
            defaults: 默认值
            
        Returns:
            str: 注入后的文本
        """
        # 合并变量（提供的变量优先）
        merged_variables = {**defaults, **variables}
        return self.inject(template_text, merged_variables)

