#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generation Constants Module

LLM生成相关的常量
"""

from typing import Final

# ====================================
# 生成常量
# ====================================
DEFAULT_TEMPERATURE: Final[float] = 0.7
DEFAULT_MAX_TOKENS: Final[int] = 2000
DEFAULT_TIMEOUT: Final[int] = 30

# ====================================
# LLM提供商常量
# ====================================
LLM_PROVIDER_DEEPSEEK: Final[str] = "deepseek"
LLM_PROVIDER_DOUBAO: Final[str] = "doubao"
LLM_PROVIDER_ALIYUN: Final[str] = "aliyun"
LLM_PROVIDER_MIMO: Final[str] = "mimo"
LLM_PROVIDER_MOCK: Final[str] = "mock"

SUPPORTED_LLM_PROVIDERS: Final[set[str]] = {
    LLM_PROVIDER_DEEPSEEK,
    LLM_PROVIDER_DOUBAO,
    LLM_PROVIDER_ALIYUN,
    LLM_PROVIDER_MIMO,
    LLM_PROVIDER_MOCK,
}
