# -*- coding: utf-8 -*-
"""
Chunking Base Module

文档切分抽象基类，定义统一的切分接口。
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TextChunk:
    """文本分块"""
    content: str
    chunk_id: str
    start_index: int = 0
    end_index: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    def __repr__(self) -> str:
        return f"TextChunk(id={self.chunk_id}, length={len(self.content)})"


class BaseChunkingProvider(ABC):
    """
    文档切分提供者基类

    所有切分提供者都需要继承此类并实现切分方法。
    """

    name: str = ""
    description: str = ""

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: list[str] | None = None,
        **kwargs,
    ):
        """
        初始化切分提供者

        Args:
            chunk_size: 分块大小（字符数）
            chunk_overlap: 分块重叠大小
            separators: 分隔符列表
            **kwargs: 额外参数
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", "！", "？", " ", ""]

    @abstractmethod
    def chunk_text(self, text: str, **kwargs) -> list[str]:
        """
        切分文本为字符串列表

        Args:
            text: 待切分的文本
            **kwargs: 额外参数

        Returns:
            切分后的文本块列表
        """
        pass

    def chunk_text_with_metadata(
        self,
        text: str,
        document_id: str = "unknown",
        metadata: dict[str, Any] | None = None,
        **kwargs,
    ) -> list[TextChunk]:
        """
        切分文本并返回带元数据的 TextChunk 列表

        Args:
            text: 待切分的文本
            document_id: 文档ID
            metadata: 额外元数据
            **kwargs: 额外参数

        Returns:
            带有元数据的文本块列表
        """
        chunks = self.chunk_text(text, **kwargs)
        metadata = metadata or {}

        result = []
        for idx, chunk_content in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": idx,
                "chunk_count": len(chunks),
            }
            result.append(
                TextChunk(
                    content=chunk_content,
                    chunk_id=f"{document_id}_chunk_{idx}",
                    start_index=text.find(chunk_content) if chunk_content in text else 0,
                    end_index=text.find(chunk_content) + len(chunk_content) if chunk_content in text else len(chunk_content),
                    metadata=chunk_metadata,
                )
            )

        return result

    def get_config(self) -> dict[str, Any]:
        """获取当前配置"""
        return {
            "name": self.name,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "separators": self.separators,
        }
