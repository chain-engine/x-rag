# -*- coding: utf-8 -*-
"""
HyDE Module

Hypothetical Document Embeddings — 生成假设性文档以提升检索效果
"""

from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from retrieval.understanding.base import (
    BaseQueryUnderstandingProvider,
    QueryUnderstandingResult,
)
from llms.providers import get_llm_provider, BaseLLMProvider
from core.logger import logger


class HyDEProvider(BaseQueryUnderstandingProvider):
    """
    HyDE 提供者基类

    HyDE (Hypothetical Document Embeddings) 通过 LLM 生成"假设性答案文档"，
    然后用假设文档的向量去检索，从而提升召回率。
    """

    name = "hyde"
    description = "HyDE — 生成假设性文档进行检索"

    def supports(self) -> list[str]:
        return ["hyde"]

    def process(
        self,
        query: str,
        context: Optional[dict[str, Any]] = None,
    ) -> QueryUnderstandingResult:
        """生成假设性文档"""
        raise NotImplementedError("HyDE 子类必须实现 generate_hypothetical_doc 方法")

    def generate_hypothetical_doc(self, query: str) -> str:
        """生成假设性文档"""
        raise NotImplementedError("HyDE 子类必须实现 generate_hypothetical_doc 方法")


class LLMHyDE(HyDEProvider):
    """
    基于 LLM 的 HyDE

    使用大语言模型生成一个假设性的答案文档。
    """

    name = "llm_hyde"
    description = "LLM HyDE — 使用 LLM 生成假设性答案文档"

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        provider_name: str = "deepseek",
        system_prompt: Optional[str] = None,
    ):
        """
        初始化 LLM HyDE

        Args:
            llm_provider: LLM 提供者实例
            provider_name: LLM 提供者名称
            system_prompt: 系统提示词
        """
        self._llm_provider = llm_provider
        self._provider_name = provider_name
        self._system_prompt = system_prompt or (
            "你是一个文档生成专家。请根据用户的问题，生成一段假设性的答案文档。\n\n"
            "要求：\n"
            "1. 假设你知道问题的正确答案\n"
            "2. 生成一段连贯的、详细的答案文档\n"
            "3. 内容应该准确、专业\n"
            "4. 长度适中（100-300字）\n\n"
            "只返回假设性答案，不要任何解释或前缀。"
        )

    def generate_hypothetical_doc(self, query: str) -> str:
        """使用 LLM 生成假设性文档"""
        if self._llm_provider is None:
            self._llm_provider = get_llm_provider(self._provider_name)

        messages = [
            SystemMessage(content=self._system_prompt),
            HumanMessage(content=query),
        ]

        try:
            response = self._llm_provider.invoke(messages)
            doc = response.content if hasattr(response, "content") else str(response)
            logger.debug(f"LLMHyDE generated hypothetical doc ({len(doc)} chars)")
            return doc.strip()
        except Exception as e:
            logger.warning(f"LLMHyDE failed: {e}")
            return query

    def process(
        self,
        query: str,
        context: Optional[dict[str, Any]] = None,
    ) -> QueryUnderstandingResult:
        """生成假设性文档并返回结果"""
        hypothetical_doc = self.generate_hypothetical_doc(query)
        return QueryUnderstandingResult(
            original_query=query,
            processed_query=hypothetical_doc,
            hypothetical_doc=hypothetical_doc,
            metadata={"provider": self.name},
        )
