"""
关键词提取器
从用户输入中提取关键词和短语
"""
import re
import logging
from typing import List, Set
from collections import Counter

logger = logging.getLogger(__name__)


class KeywordExtractor:
    """关键词提取器类"""
    
    # 常见停用词（可扩展）
    STOP_WORDS: Set[str] = {
        "的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一",
        "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有",
        "看", "好", "自己", "这", "能", "可以", "帮", "帮我", "请", "一下"
    }
    
    def __init__(self):
        """初始化关键词提取器"""
        pass
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """
        提取文本中的关键词
        
        Args:
            text: 输入文本
            top_k: 返回前 k 个关键词
            
        Returns:
            List[str]: 关键词列表
        """
        # 基础分词（这里使用简单的方法，实际项目可以使用 jieba 等分词工具）
        words = self._simple_tokenize(text)
        
        # 过滤停用词
        filtered_words = [w for w in words if w not in self.STOP_WORDS and len(w) > 1]
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        # 返回高频词
        keywords = [word for word, count in word_counts.most_common(top_k)]
        
        logger.info(f"提取到 {len(keywords)} 个关键词: {keywords[:5]}...")
        return keywords
    
    def extract_key_phrases(self, text: str) -> List[str]:
        """
        提取关键短语
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 关键短语列表
        """
        phrases = []
        
        # 提取引号内的内容
        quoted = re.findall(r'[「『"]([^」』"]+)[」』"]', text)
        phrases.extend(quoted)
        
        # 提取特殊格式（如：XX助手、XX系统）
        patterns = [
            r'(\w+(?:助手|系统|工具|平台|应用))',
            r'(\w{2,4}分析)',
            r'(生成\w{2,4})',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            phrases.extend(matches)
        
        # 去重
        phrases = list(set(phrases))
        
        logger.info(f"提取到 {len(phrases)} 个关键短语")
        return phrases
    
    def _simple_tokenize(self, text: str) -> List[str]:
        """
        简单分词（中文按字符，英文按单词）
        实际项目中应使用专业分词工具如 jieba
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 词语列表
        """
        # 移除标点符号
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 拆分为词
        words = []
        for part in text.split():
            # 英文单词
            if re.match(r'^[a-zA-Z]+$', part):
                words.append(part.lower())
            # 中文按2-4个字符提取
            elif len(part) > 1:
                for i in range(len(part)):
                    for length in [2, 3, 4]:
                        if i + length <= len(part):
                            words.append(part[i:i+length])
        
        return words
    
    def extract_domain_keywords(self, text: str) -> List[str]:
        """
        提取领域相关关键词
        
        Args:
            text: 输入文本
            
        Returns:
            List[str]: 领域关键词列表
        """
        domain_keywords = {
            "金融": ["财报", "股票", "投资", "交易", "金融", "银行", "资产"],
            "医疗": ["医疗", "健康", "病人", "诊断", "治疗", "药物", "医生"],
            "教育": ["教育", "学习", "课程", "学生", "教师", "培训", "考试"],
            "技术": ["代码", "编程", "开发", "系统", "算法", "数据", "AI"],
            "电商": ["购物", "商品", "订单", "支付", "物流", "店铺", "客户"],
        }
        
        found_domains = []
        text_lower = text.lower()
        
        for domain, keywords in domain_keywords.items():
            if any(kw in text for kw in keywords):
                found_domains.append(domain)
        
        return found_domains

