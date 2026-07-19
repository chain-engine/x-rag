#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Model Module

向量记录实体定义
"""

from typing import Any
from pydantic import Field

from models.base import BaseEntity


class VectorRecord(BaseEntity):
    """向量记录实体

    表示一个嵌入向量及其关联的文档片段
    """
    vector_id: str = Field(..., description="向量唯一标识")
    chunk_id: str = Field(..., description="关联的分块ID")
    document_id: str = Field(..., description="关联的文档ID")
    text: str = Field(..., description="原始文本")
    vector: list[float] = Field(default_factory=list, description="向量数据")
    score: float | None = Field(default=None, description="相似度分数")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元数据")

    class Config:
        from_attributes = True

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "id": self.vector_id,
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "text": self.text,
            "vector": self.vector,
            "score": self.score,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "VectorRecord":
        """从字典创建"""
        return cls(**data)
