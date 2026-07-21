#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generation Service Module

生成服务
"""

import os
from typing import Any, AsyncIterator
import httpx

from services.base_service import BaseService
from core.logger import logger
from core.exceptions import GenerationError
from constants.generation import LLM_PROVIDER_DEEPSEEK, LLM_PROVIDER_OPENAI


class GenerationService(BaseService):
    """生成服务"""

    PROVIDER_ENDPOINTS = {
        LLM_PROVIDER_OPENAI: "https://api.openai.com/v1/chat/completions",
        LLM_PROVIDER_DEEPSEEK: "https://api.deepseek.com/v1/chat/completions",
    }

    def __init__(
        self,
        default_provider: str = LLM_PROVIDER_DEEPSEEK,
        default_model: str = "deepseek-chat",
        default_temperature: float = 0.7,
        default_max_tokens: int = 2000,
        default_timeout: int = 30,
    ):
        self._default_provider = default_provider
        self._default_model = default_model
        self._default_temperature = default_temperature
        self._default_max_tokens = default_max_tokens
        self._default_timeout = default_timeout
        self._initialized = False

    def initialize(self) -> None:
        """初始化服务"""
        self._initialized = True
        logger.info(f"GenerationService initialized with provider: {self._default_provider}")

    def shutdown(self) -> None:
        """关闭服务"""
        self._initialized = False
        logger.info("GenerationService shut down")

    def get_stats(self) -> dict[str, Any]:
        """获取服务统计信息"""
        return {
            "type": "generation",
            "provider": self._default_provider,
            "model": self._default_model,
        }

    async def generate(
        self,
        prompt: str,
        provider: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """生成文本

        注意: prompt应为增强后的完整prompt，增强逻辑已移至AugmentationService
        """
        self._check_initialized()

        provider = provider or self._default_provider
        temperature = temperature or self._default_temperature
        max_tokens = max_tokens or self._default_max_tokens

        try:
            if provider == LLM_PROVIDER_OPENAI:
                return await self._call_openai(prompt, temperature, max_tokens)
            elif provider == LLM_PROVIDER_DEEPSEEK:
                return await self._call_deepseek(prompt, temperature, max_tokens)
            else:
                raise GenerationError(f"Unsupported provider: {provider}")

        except GenerationError:
            raise
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            raise GenerationError(f"Generation failed: {e}") from e

    async def _call_openai(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        """调用OpenAI API"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise GenerationError("OPENAI_API_KEY not configured")

        async with httpx.AsyncClient(timeout=self._default_timeout) as client:
            response = await client.post(
                self.PROVIDER_ENDPOINTS[LLM_PROVIDER_OPENAI],
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._default_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            if response.status_code != 200:
                raise GenerationError(f"API error: {response.text}")

            data = response.json()
            return {
                "text": data["choices"][0]["message"]["content"],
                "provider": LLM_PROVIDER_OPENAI,
                "model": data.get("model", self._default_model),
                "tokens_used": data.get("usage", {}).get("total_tokens"),
            }

    async def _call_deepseek(
        self,
        prompt: str,
        temperature: float,
        max_tokens: int,
    ) -> dict[str, Any]:
        """调用DeepSeek API"""
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise GenerationError("DEEPSEEK_API_KEY not configured")

        async with httpx.AsyncClient(timeout=self._default_timeout) as client:
            response = await client.post(
                self.PROVIDER_ENDPOINTS[LLM_PROVIDER_DEEPSEEK],
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": self._default_model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                },
            )

            if response.status_code != 200:
                raise GenerationError(f"API error: {response.text}")

            data = response.json()
            return {
                "text": data["choices"][0]["message"]["content"],
                "provider": LLM_PROVIDER_DEEPSEEK,
                "model": data.get("model", self._default_model),
                "tokens_used": data.get("usage", {}).get("total_tokens"),
            }

    async def stream_generate(
        self,
        prompt: str,
        provider: str | None = None,
        temperature: float | None = None,
    ) -> AsyncIterator[str]:
        """流式生成文本

        当前版本暂不支持流式生成
        """
        raise NotImplementedError("Streaming generation not yet implemented")

    def _check_initialized(self) -> None:
        """检查服务是否已初始化"""
        if not self._initialized:
            raise RuntimeError("GenerationService not initialized. Call initialize() first.")
