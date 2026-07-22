# -*- coding: utf-8 -*-
"""
Subquery Decomposition Module

子查询分解 — 将复杂查询分解为多个简单子查询
"""

from typing import Any, Optional

from langchain_core.messages import HumanMessage, SystemMessage

from retrieval.understanding.base import (
    BaseQueryUnderstandingProvider,
    QueryUnderstandingResult,
)
from llms.providers import get_llm_provider, BaseLLMProvider
from core.logger import logger


class SubqueryDecompositionProvider(BaseQueryUnderstandingProvider):
    """
    子查询分解提供者基类

    将复杂的多意图查询分解为多个可以并行检索的简单子查询。
    """

    name = "subquery_decomposition"
    description = "子查询分解 — 分解复杂查询为多个简单子查询"

    def supports(self) -> list[str]:
        return ["subquery"]

    def process(
        self,
        query: str,
        context: Optional[dict[str, Any]] = None,
    ) -> QueryUnderstandingResult:
        """分解查询"""
        raise NotImplementedError(
            "子类必须实现 decompose 方法"
        )

    def decompose(self, query: str) -> list[str]:
        """分解查询为子查询列表"""
        raise NotImplementedError(
            "子类必须实现 decompose 方法"
        )


class LLMSubqueryDecomposer(SubqueryDecompositionProvider):
    """
    基于 LLM 的子查询分解

    使用大语言模型将复杂查询分解为多个可以独立检索的子查询。
    """

    name = "llm_subquery_decomposer"
    description = "LLM 子查询分解器 — 使用 LLM 分解复杂查询"

    def __init__(
        self,
        llm_provider: Optional[BaseLLMProvider] = None,
        provider_name: str = "deepseek",
        system_prompt: Optional[str] = None,
        max_subqueries: int = 5,
    ):
        """
        初始化 LLM 子查询分解器

        Args:
            llm_provider: LLM 提供者实例
            provider_name: LLM 提供者名称
            system_prompt: 系统提示词
            max_subqueries: 最大子查询数量
        """
        self._llm_provider = llm_provider
        self._provider_name = provider_name
        self._max_subqueries = max_subqueries
        self._system_prompt = system_prompt or (
            "你是一个查询分解专家。你的任务是将复杂查询分解为多个简单的子查询。\n\n"
            "要求：\n"
            "1. 每个子查询应该只关注一个方面\n"
            "2. 子查询之间相互独立，可以并行检索\n"
            "3. 保留原始查询的核心意图\n"
            "4. 最多分解为5个子查询\n\n"
            "格式要求：\n"
            "将每个子查询单独一行返回，不要编号，不要其他解释。"
        )

    def decompose(self, query: str) -> list[str]:
        """使用 LLM 分解查询"""
        if self._llm_provider is None:
            self._llm_provider = get_llm_provider(self._provider_name)

        prompt_with_limit = (
            self._system_prompt
            + f"\n\n用户查询：{query}\n\n（最多 {self._max_subqueries} 个子查询）"
        )

        messages = [
            SystemMessage(content=prompt_with_limit),
            HumanMessage(content=query),
        ]

        try:
            response = self._llm_provider.invoke(messages)
            content = response.content if hasattr(response, "content") else str(response)

            sub_queries = [
                line.strip()
                for line in content.split("\n")
                if line.strip() and not line.strip().startswith("#")
            ]
            sub_queries = sub_queries[: self._max_subqueries]

            logger.debug(f"LLMSubqueryDecomposer: '{query}' -> {sub_queries}")
            return sub_queries
        except Exception as e:
            logger.warning(f"LLMSubqueryDecomposer failed: {e}")
            return [query]

    def process(
        self,
        query: str,
        context: Optional[dict[str, Any]] = None,
    ) -> QueryUnderstandingResult:
        """分解查询并返回结果"""
        sub_queries = self.decompose(query)
        combined = " ".join(sub_queries) if sub_queries else query
        return QueryUnderstandingResult(
            original_query=query,
            processed_query=combined,
            sub_queries=sub_queries,
            metadata={"provider": self.name, "subquery_count": len(sub_queries)},
        )
