#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG核心功能模块（已废弃）

注意：此模块已废弃，请使用标准三层架构：
- API层：api.v1.rag, api.v1.document
- Service层：service.indexing_service, service.retrieval_service, service.generation_service
- Repository层：repository.vector_repository, repository.document_repository

示例：
    from service import IndexingService, RetrievalService, GenerationService
    from repository import VectorRepository, DocumentRepository

    # 创建和初始化
    vector_repo = VectorRepository()
    doc_repo = DocumentRepository()
    indexing_service = IndexingService(vector_repo, doc_repo)
    retrieval_service = RetrievalService(vector_repo)
    generation_service = GenerationService()

    indexing_service.initialize()
    retrieval_service.initialize()
    generation_service.initialize()
"""

import warnings

warnings.warn(
    "The 'rag' module is deprecated. Please use the three-tier architecture: "
    "service and repository modules instead.",
    DeprecationWarning,
    stacklevel=2
)

# 保留导入以向后兼容，但不推荐使用
from rag import indexing, retrieval, generation, storage

__all__ = [
    "indexing",
    "retrieval",
    "generation",
    "storage",
]