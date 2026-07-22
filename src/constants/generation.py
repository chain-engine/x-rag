#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generation Constants Module

LLM生成相关的常量
"""

from enum import Enum
from typing import Final


# ====================================
# LLM Provider Type Enum
# ====================================
class LLMProviderType(str, Enum):
    """LLM 提供者类型枚举"""
    DEEPSEEK = "deepseek"
    DOUBAO = "doubao"
    ALIYUN = "aliyun"
    MIMO = "mimo"
    MOCK = "mock"


# ====================================
# 生成常量
# ====================================
DEFAULT_TEMPERATURE: Final[float] = 0.7
DEFAULT_MAX_TOKENS: Final[int] = 2000
DEFAULT_TIMEOUT: Final[int] = 30

# ====================================
# LLM提供商常量（字符串形式，用于配置）
# ====================================
LLM_PROVIDER_DEEPSEEK: Final[str] = LLMProviderType.DEEPSEEK.value
LLM_PROVIDER_DOUBAO: Final[str] = LLMProviderType.DOUBAO.value
LLM_PROVIDER_ALIYUN: Final[str] = LLMProviderType.ALIYUN.value
LLM_PROVIDER_MIMO: Final[str] = LLMProviderType.MIMO.value
LLM_PROVIDER_MOCK: Final[str] = LLMProviderType.MOCK.value

SUPPORTED_LLM_PROVIDERS: Final[set[str]] = {
    LLM_PROVIDER_DEEPSEEK,
    LLM_PROVIDER_DOUBAO,
    LLM_PROVIDER_ALIYUN,
    LLM_PROVIDER_MIMO,
    LLM_PROVIDER_MOCK,
}

__all__ = [
    "LLMProviderType",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_TIMEOUT",
    "LLM_PROVIDER_DEEPSEEK",
    "LLM_PROVIDER_DOUBAO",
    "LLM_PROVIDER_ALIYUN",
    "LLM_PROVIDER_MIMO",
    "LLM_PROVIDER_MOCK",
    "SUPPORTED_LLM_PROVIDERS",
]
