"""
输入层模块测试
"""
import pytest
from modules.input_layer import IntentExtractor, KeywordExtractor, InputNormalizer


class TestInputNormalizer:
    """输入标准化器测试"""
    
    def test_normalize_basic(self):
        normalizer = InputNormalizer()
        text = "  这是  一个   测试   "
        result = normalizer.normalize(text)
        assert result == "这是 一个 测试"
    
    def test_remove_sensitive_info(self):
        normalizer = InputNormalizer()
        text = "我的手机号是13812345678"
        result = normalizer.remove_sensitive_info(text)
        assert "[手机号]" in result
        assert "13812345678" not in result


class TestKeywordExtractor:
    """关键词提取器测试"""
    
    def test_extract_keywords(self):
        extractor = KeywordExtractor()
        text = "帮我写一个分析财报的AI助手"
        keywords = extractor.extract_keywords(text, top_k=5)
        assert len(keywords) > 0
        assert isinstance(keywords, list)
    
    def test_extract_key_phrases(self):
        extractor = KeywordExtractor()
        text = "需要一个财报分析助手来处理数据"
        phrases = extractor.extract_key_phrases(text)
        assert isinstance(phrases, list)


# IntentExtractor 需要 API 密钥，在实际测试时可以使用 mock
@pytest.mark.asyncio
class TestIntentExtractor:
    """意图提取器测试（需要 mock）"""
    
    @pytest.mark.skip(reason="需要 API 密钥")
    async def test_extract(self):
        extractor = IntentExtractor()
        result = await extractor.extract("帮我写一个分析财报的AI助手")
        assert result is not None
        assert result.task_type is not None

