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
LLM_PROVIDER_OPENAI: Final[str] = "openai"
LLM_PROVIDER_ANTHROPIC: Final[str] = "anthropic"
LLM_PROVIDER_DEEPSEEK: Final[str] = "deepseek"
LLM_PROVIDER_ALIYUN: Final[str] = "aliyun"

SUPPORTED_LLM_PROVIDERS: Final[set[str]] = {
    LLM_PROVIDER_OPENAI,
    LLM_PROVIDER_ANTHROPIC,
    LLM_PROVIDER_DEEPSEEK,
    LLM_PROVIDER_ALIYUN,
}
