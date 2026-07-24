# -*- coding: utf-8 -*-
"""
Chunking Package

文档切分（Document Chunking）模块，提供统一的文本切分接口。

支持多种切分方案：
- LangChain: RecursiveCharacterTextSplitter, CharacterTextSplitter, TokenTextSplitter, SemanticChunker
- LlamaIndex: SentenceSplitter, TokenTextSplitter, SemanticSplitterNodeParser, MarkdownNodeParser
"""

from chunking.base import BaseChunkingProvider
from chunking.langchain_provider import LangchainProvider
from chunking.llama_index_provider import LlamaIndexProvider

__all__ = [
    "BaseChunkingProvider",
    "LangchainProvider",
    "LlamaIndexProvider",
    "get_chunking_provider",
    "list_chunking_providers",
]


_PROVIDERS: dict[str, type[BaseChunkingProvider]] = {
    "langchain": LangchainProvider,
    "llamaindex": LlamaIndexProvider,
}


def get_chunking_provider(provider_name: str = "langchain", **kwargs) -> BaseChunkingProvider:
    """
    获取文档切分提供者实例

    Args:
        provider_name: 提供者名称（langchain, llamaindex）
        **kwargs: 额外的切分参数

    Returns:
        BaseChunkingProvider 实例

    Raises:
        ValueError: 不支持的提供者
    """
    provider_name = provider_name.lower()

    if provider_name not in _PROVIDERS:
        available = ", ".join(_PROVIDERS.keys())
        raise ValueError(f"不支持的切分提供者: {provider_name}。支持的提供者: {available}")

    from core.logger import logger
    logger.info(f"Getting document chunking provider: {provider_name}")
    return _PROVIDERS[provider_name](**kwargs)


def list_chunking_providers() -> list[dict[str, str]]:
    """列出所有可用的切分提供者"""
    return [
        {"name": name, "description": cls.description}
        for name, cls in _PROVIDERS.items()
    ]
