#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Augmentation Module

增强模块 - RAG中负责将检索结果与查询进行增强融合的环节
"""

from typing import Any

from constants.rag import DEFAULT_SYSTEM_PROMPT, DEFAULT_USER_PROMPT_TEMPLATE
from core.logger import logger


class Augmentation:
    """增强器"""

    def __init__(
        self,
        system_prompt: str | None = None,
        user_prompt_template: str | None = None,
        max_context_length: int = 8000,
    ):
        self._system_prompt = system_prompt or DEFAULT_SYSTEM_PROMPT
        self._user_prompt_template = user_prompt_template or DEFAULT_USER_PROMPT_TEMPLATE
        self._max_context_length = max_context_length

    def initialize(self) -> None:
        """初始化增强器（无需加载资源，保持接口一致性）"""
        pass

    def shutdown(self) -> None:
        """关闭增强器（无需释放资源，保持接口一致性）"""
        pass

    def augment(
        self,
        query: str,
        retrieved_docs: list[dict[str, Any]],
        include_metadata: bool = False,
    ) -> dict[str, Any]:
        """增强查询与检索结果

        Args:
            query: 用户查询
            retrieved_docs: 检索到的文档列表
            include_metadata: 是否在上下文中包含元数据

        Returns:
            包含增强后prompt和相关信息的字典
        """
        if not retrieved_docs:
            return {
                "system_prompt": self._system_prompt,
                "user_prompt": query,
                "full_prompt": query,
                "context_count": 0,
                "context_length": 0,
            }

        context_items = []
        total_length = 0

        for i, doc in enumerate(retrieved_docs):
            text = doc.get("text", "")
            doc_length = len(text)

            if total_length + doc_length > self._max_context_length:
                remaining = self._max_context_length - total_length
                if remaining > 100:
                    text = text[:remaining] + "..."
                    doc_length = remaining
                else:
                    break

            total_length += doc_length

            if include_metadata:
                metadata = doc.get("metadata", {})
                source = metadata.get("source", "unknown")
                context_items.append(f"[文档{i+1}] 来源: {source}\n{text}")
            else:
                context_items.append(f"[文档{i+1}]\n{text}")

        context_text = "\n\n".join(context_items)
        user_prompt = self._user_prompt_template.format(
            context=context_text,
            query=query,
        )

        return {
            "system_prompt": self._system_prompt,
            "user_prompt": user_prompt,
            "full_prompt": user_prompt,
            "context_count": len(context_items),
            "context_length": total_length,
        }

    def build_prompt(self, query: str, contexts: list[str]) -> str:
        """构建带有上下文的prompt

        Args:
            query: 用户查询
            contexts: 上下文字符串列表

        Returns:
            增强后的完整prompt
        """
        if not contexts:
            return query

        context_text = "\n\n".join([f"[文档{i+1}]\n{ctx}" for i, ctx in enumerate(contexts)])
        return self._user_prompt_template.format(
            context=context_text,
            query=query,
        )
