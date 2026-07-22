#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generation Constants Module

LLM生成相关的常量
"""

from .base import BaseEnum
from typing import Final


class LLMProviderType(BaseEnum):
    """LLM 提供者类型枚举"""
    DEEPSEEK = "deepseek", "DeepSeek"
    DOUBAO = "doubao", "豆包"
    ALIYUN = "aliyun", "阿里云"
    MIMO = "mimo", "MIMO"
    MOCK = "mock", "模拟"


# ====================================
# 生成常量
# ====================================
DEFAULT_TEMPERATURE: Final[float] = 0.7
DEFAULT_MAX_TOKENS: Final[int] = 2000
DEFAULT_TIMEOUT: Final[int] = 30

SUPPORTED_LLM_PROVIDERS: Final[set[str]] = set(LLMProviderType.get_all_marks())

__all__ = [
    "LLMProviderType",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_TIMEOUT",
    "SUPPORTED_LLM_PROVIDERS",
]
