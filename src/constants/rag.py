#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Constants Module

RAG核心模块相关的常量
"""

from enum import Enum
from typing import Final

# ====================================
# 文档状态常量
# ====================================
DOC_STATUS_PENDING: Final[str] = "pending"
DOC_STATUS_PROCESSING: Final[str] = "processing"
DOC_STATUS_COMPLETED: Final[str] = "completed"
DOC_STATUS_FAILED: Final[str] = "failed"
DOC_STATUS_DELETED: Final[str] = "deleted"

# ====================================
# 文档类型常量
# ====================================
DOC_TYPE_TXT: Final[str] = "txt"
DOC_TYPE_MD: Final[str] = "md"
DOC_TYPE_PDF: Final[str] = "pdf"
DOC_TYPE_DOCX: Final[str] = "docx"
DOC_TYPE_HTML: Final[str] = "html"

SUPPORTED_DOC_TYPES: Final[set[str]] = {
    DOC_TYPE_TXT,
    DOC_TYPE_MD,
    DOC_TYPE_PDF,
    DOC_TYPE_DOCX,
    DOC_TYPE_HTML,
}

# ====================================
# 距离度量方式
# ====================================
DISTANCE_COSINE: Final[str] = "cosine"
DISTANCE_EUCLIDEAN: Final[str] = "euclidean"
DISTANCE_DOT: Final[str] = "dot"

# ====================================
# 检索常量
# ====================================
DEFAULT_TOP_K: Final[int] = 5
DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.7
DEFAULT_MMR_LAMBDA: Final[float] = 0.5

# ====================================
# 文本切分常量
# ====================================
DEFAULT_CHUNK_SIZE: Final[int] = 512
DEFAULT_CHUNK_OVERLAP: Final[int] = 50


# ====================================
# 距离度量类型枚举
# ====================================
class DistanceType(str, Enum):
    """距离度量类型"""
    COSINE = DISTANCE_COSINE
    EUCLIDEAN = DISTANCE_EUCLIDEAN
    DOT = DISTANCE_DOT


# ====================================
# 排序 Provider 名称常量
# ====================================
class RerankingProviderName:
    """排序 Provider 名称常量"""
    MMR_RERANKER: Final[str] = "mmr_reranker"
    RRF_RERANKER: Final[str] = "rrf_reranker"
    SEMANTIC_RERANKER: Final[str] = "semantic_reranker"
    SCORE_FILTER: Final[str] = "score_filter"


__all__ = [
    "DOC_STATUS_PENDING",
    "DOC_STATUS_PROCESSING",
    "DOC_STATUS_COMPLETED",
    "DOC_STATUS_FAILED",
    "DOC_STATUS_DELETED",
    "DOC_TYPE_TXT",
    "DOC_TYPE_MD",
    "DOC_TYPE_PDF",
    "DOC_TYPE_DOCX",
    "DOC_TYPE_HTML",
    "SUPPORTED_DOC_TYPES",
    "DISTANCE_COSINE",
    "DISTANCE_EUCLIDEAN",
    "DISTANCE_DOT",
    "DEFAULT_TOP_K",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_MMR_LAMBDA",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_CHUNK_OVERLAP",
    "DistanceType",
    "RerankingProviderName",
]
