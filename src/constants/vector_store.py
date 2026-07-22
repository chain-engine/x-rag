#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Store Constants Module

向量存储相关的常量
"""

from .base import BaseEnum
from typing import Final


class VectorStoreType(BaseEnum):
    """向量存储类型枚举"""
    CHROMA = "chroma", "Chroma向量数据库"
    # 可扩展其他类型
    # MILVUS = "milvus", "Milvus向量数据库"
    # QDRANT = "qdrant", "Qdrant向量数据库"


DISTANCE_COSINE: Final[str] = "cosine"
DEFAULT_COLLECTION_NAME: Final[str] = "documents"
DEFAULT_DISTANCE: Final[str] = DISTANCE_COSINE
