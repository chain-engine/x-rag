#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Infras Package

基础设施层，封装第三方中间件、客户端、连接生命周期
"""

from infras.vector_store.base import VectorStoreBase, VectorRecord
from infras.vector_store.chroma import ChromaVectorStore
from infras.document_store.base import DocumentStoreBase
from infras.document_store.json_store import JSONDocumentStore
from infras.embedding.base import EmbeddingModelBase
from infras.embedding.bge_model import BGEEmbeddingModel

__all__ = [
    "VectorStoreBase",
    "VectorRecord",
    "ChromaVectorStore",
    "DocumentStoreBase",
    "JSONDocumentStore",
    "EmbeddingModelBase",
    "BGEEmbeddingModel",
]
