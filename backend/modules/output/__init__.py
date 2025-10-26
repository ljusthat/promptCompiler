"""
输出层模块
负责格式化输出和版本管理
"""
from .formatter import Formatter
from .version_manager import VersionManager

__all__ = ["Formatter", "VersionManager"]

