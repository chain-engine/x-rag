#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成模块
处理LLM文本生成
"""

import os
from typing import Optional
from enum import Enum
import httpx

from core.logger import logger
from core.exceptions import GenerationError, ConfigurationError


class LLMProvider(str, Enum):
    """LLM提供商"""
    OPENAI = "openai"
    DEEPSEEK = "deepseek"
    ALIYUN = "aliyun"


# API密钥和配置
_API_KEYS = {
    LLMProvider.OPENAI: os.getenv("OPENAI_API_KEY", ""),
    LLMProvider.DEEPSEEK: os.getenv("DEEPSEEK_API_KEY", ""),
    LLMProvider.ALIYUN: os.getenv("ALIYUN_API_KEY", ""),
}

_API_BASES = {
    LLMProvider.OPENAI: "https://api.openai.com/v1",
    LLMProvider.DEEPSEEK: "https://api.deepseek.com/v1",
    LLMProvider.ALIYUN: "https://dashscope.aliyuncs.com/compatible-mode/v1",
}

# 默认配置
_DEFAULT_PROVIDER = LLMProvider.DEEPSEEK
_DEFAULT_MODEL = "deepseek-chat"
_DEFAULT_TEMPERATURE = 0.7
_DEFAULT_MAX_TOKENS = 2000
_DEFAULT_TIMEOUT = 30


def generate(
    prompt: str,
    context: Optional[list[str]] = None,
    provider: Optional[LLMProvider | str] = None,
    model: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None,
    timeout: Optional[int] = None
) -> Dict[str, Any]:
    """生成文本

    Args:
        prompt: 生成提示
        context: 上下文文本列表
        provider: LLM提供商
        model: 模型名称
        temperature: 温度参数
        max_tokens: 最大token数
        timeout: 超时时间

    Returns:
        Dict[str, Any]: 生成结果

    Raises:
        GenerationError: 生成失败
    """
    # 转换provider为枚举
    if provider is None:
        provider = _DEFAULT_PROVIDER
    elif isinstance(provider, str):
        provider = LLMProvider(provider)

    model = model or _DEFAULT_MODEL
    temperature = temperature if temperature is not None else _DEFAULT_TEMPERATURE
    max_tokens = max_tokens or _DEFAULT_MAX_TOKENS
    timeout = timeout or _DEFAULT_TIMEOUT

    # 构建完整提示
    full_prompt = _build_prompt(prompt, context)

    logger.info(f"Generating with {provider.value}/{model}, prompt length: {len(full_prompt)}")

    try:
        if provider == LLMProvider.OPENAI:
            return _generate_openai(full_prompt, model, temperature, max_tokens, timeout)
        elif provider == LLMProvider.DEEPSEEK:
            return _generate_deepseek(full_prompt, model, temperature, max_tokens, timeout)
        elif provider == LLMProvider.ALIYUN:
            return _generate_aliyun(full_prompt, model, temperature, max_tokens, timeout)
        else:
            raise GenerationError(f"Unsupported provider: {provider}")
    except httpx.TimeoutException:
        logger.error(f"Generation timeout after {timeout}s")
        raise GenerationError(f"Generation timeout after {timeout}s") from None
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise GenerationError(f"Generation failed: {e}") from e


def _generate_openai(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    timeout: int
) -> Dict[str, Any]:
    """使用OpenAI生成文本"""
    api_key = _API_KEYS.get(LLMProvider.OPENAI)

    if not api_key or api_key.startswith("sk-xxxx"):
        raise ConfigurationError("OpenAI API key not configured")

    api_base = _API_BASES[LLMProvider.OPENAI]

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text": data["choices"][0]["message"]["content"],
            "provider": LLMProvider.OPENAI.value,
            "model": model,
            "tokens_used": data.get("usage", {}).get("total_tokens"),
            "finish_reason": data["choices"][0].get("finish_reason")
        }


def _generate_deepseek(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    timeout: int
) -> Dict[str, Any]:
    """使用DeepSeek生成文本"""
    api_key = _API_KEYS.get(LLMProvider.DEEPSEEK)

    if not api_key or api_key.startswith("sk-xxxx"):
        raise ConfigurationError("DeepSeek API key not configured")

    api_base = _API_BASES[LLMProvider.DEEPSEEK]

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text": data["choices"][0]["message"]["content"],
            "provider": LLMProvider.DEEPSEEK.value,
            "model": model,
            "tokens_used": data.get("usage", {}).get("total_tokens"),
            "finish_reason": data["choices"][0].get("finish_reason")
        }


def _generate_aliyun(
    prompt: str,
    model: str,
    temperature: float,
    max_tokens: int,
    timeout: int
) -> Dict[str, Any]:
    """使用阿里云通义千问生成文本"""
    api_key = _API_KEYS.get(LLMProvider.ALIYUN)

    if not api_key or api_key.startswith("sk-xxxx"):
        raise ConfigurationError("Aliyun API key not configured")

    api_base = _API_BASES[LLMProvider.ALIYUN]

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{api_base}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload
        )
        response.raise_for_status()
        data = response.json()

        return {
            "text": data["choices"][0]["message"]["content"],
            "provider": LLMProvider.ALIYUN.value,
            "model": model,
            "tokens_used": data.get("usage", {}).get("total_tokens"),
            "finish_reason": data["choices"][0].get("finish_reason")
        }


def _build_prompt(
    question: str,
    context: Optional[list[str]] = None
) -> str:
    """构建生成提示

    Args:
        question: 问题
        context: 上下文列表

    Returns:
        str: 完整的提示
    """
    if context and len(context) > 0:
        context_text = "\n\n".join([f"[文档{i+1}]\n{ctx}" for i, ctx in enumerate(context)])
        prompt = f"""基于以下文档内容回答问题。如果文档中没有相关信息，请如实告知。

文档内容：
{context_text}

问题：
{question}

请基于上述文档内容提供准确、详细的回答。"""
    else:
        prompt = f"""问题：
{question}

请提供准确、详细的回答。"""

    return prompt


async def stream_generate(*args, **kwargs):
    """流式生成文本（待实现）"""
    raise NotImplementedError("Stream generation not yet implemented")