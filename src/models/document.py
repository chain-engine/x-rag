#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Model Module

文档实体定义
"""

from typing import Any
from datetime import datetime
from pydantic import Field

from models.base import BaseEntity, BaseTimestampMixin


class Document(BaseEntity, BaseTimestampMixin):
    """文档实体

    表示一个待检索的文档
    """
    document_id: str = Field(..., description="文档唯一标识")
    file_name: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(default=0, description="文件大小（字节）")
    status: str = Field(default="pending", description="文档状态")
    chunk_count: int = Field(default=0, description="分块数量")
    metadata: dict[str, Any] = Field(default_factory=dict, description="扩展元数据")

    class Config:
        from_attributes = True

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "document_id": self.document_id,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "status": self.status,
            "chunk_count": self.chunk_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Document":
        """从字典创建"""
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])
        return cls(**data)


class DocumentChunk(BaseEntity):
    """文档分块实体

    表示文档的一个文本分块
    """
    chunk_id: str = Field(..., description="分块唯一标识")
    document_id: str = Field(..., description="所属文档ID")
    content: str = Field(..., description="文本内容")
    chunk_index: int = Field(..., description="分块索引")
    metadata: dict[str, Any] = Field(default_factory=dict, description="分块元数据")

    class Config:
        from_attributes = True

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        return {
            "chunk_id": self.chunk_id,
            "document_id": self.document_id,
            "content": self.content,
            "chunk_index": self.chunk_index,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DocumentChunk":
        """从字典创建"""
        return cls(**data)
