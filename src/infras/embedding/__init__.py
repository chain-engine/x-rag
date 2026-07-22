# -*- coding: utf-8 -*-
"""
Embedding Package

嵌入模型基础设施
"""

from infras.embedding.base import EmbeddingModelBase
from infras.embedding.bge_model import BGEEmbeddingModel

__all__ = [
    "EmbeddingModelBase",
    "BGEEmbeddingModel",
]
