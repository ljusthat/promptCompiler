"""
输入标准化器
清洗和标准化用户输入
"""
import re
import logging
# from typing import str

logger = logging.getLogger(__name__)


class InputNormalizer:
    """输入标准化器类"""
    
    def __init__(self):
        """初始化标准化器"""
        pass
    
    def normalize(self, text: str) -> str:
        """
        标准化输入文本
        
        Args:
            text: 原始输入文本
            
        Returns:
            str: 标准化后的文本
        """
        if not text:
            return ""
        
        # 1. 移除多余空白
        text = self._remove_extra_whitespace(text)
        
        # 2. 统一标点符号
        text = self._normalize_punctuation(text)
        
        # 3. 移除特殊字符（保留必要的）
        text = self._clean_special_chars(text)
        
        # 4. 标准化数字
        text = self._normalize_numbers(text)
        
        logger.info(f"文本标准化完成，长度: {len(text)}")
        return text.strip()
    
    def _remove_extra_whitespace(self, text: str) -> str:
        """移除多余的空白字符"""
        # 替换多个空格为单个空格
        text = re.sub(r'\s+', ' ', text)
        # 移除行首行尾空白
        text = '\n'.join(line.strip() for line in text.split('\n'))
        return text
    
    def _normalize_punctuation(self, text: str) -> str:
        """统一标点符号（全角转半角）"""
        punctuation_map = {
            '，': ',',
            '。': '.',
            '！': '!',
            '？': '?',
            '：': ':',
            '；': ';',
            '（': '(',
            '）': ')',
            '【': '[',
            '】': ']',
            '「': '"',
            '」': '"',
            '『': '"',
            '』': '"',
        }
        
        for cn, en in punctuation_map.items():
            text = text.replace(cn, en)
        
        return text
    
    def _clean_special_chars(self, text: str) -> str:
        """清理特殊字符（保留中文、英文、数字、基本标点）"""
        # 保留中文、英文、数字、空格和常用标点
        # 注意：这里不做过于激进的清理，避免丢失重要信息
        # text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?:;()\[\]"\'-]', '', text)
        
        # 移除 emoji（可选）
        # text = re.sub(r'[\U00010000-\U0010ffff]', '', text)
        
        return text
    
    def _normalize_numbers(self, text: str) -> str:
        """标准化数字格式（全角转半角）"""
        number_map = {
            '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
            '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
        }
        
        for cn, en in number_map.items():
            text = text.replace(cn, en)
        
        return text
    
    def remove_sensitive_info(self, text: str) -> str:
        """
        移除敏感信息（如：手机号、邮箱等）
        
        Args:
            text: 输入文本
            
        Returns:
            str: 移除敏感信息后的文本
        """
        # 脱敏手机号
        text = re.sub(r'1[3-9]\d{9}', '[手机号]', text)
        
        # 脱敏邮箱
        text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[邮箱]', text)
        
        # 脱敏身份证号
        text = re.sub(r'\d{17}[\dXx]', '[身份证]', text)
        
        return text
    
    def truncate(self, text: str, max_length: int = 2000) -> str:
        """
        截断过长的文本
        
        Args:
            text: 输入文本
            max_length: 最大长度
            
        Returns:
            str: 截断后的文本
        """
        if len(text) <= max_length:
            return text
        
        logger.warning(f"文本过长 ({len(text)} 字符)，截断至 {max_length} 字符")
        return text[:max_length] + "..."

