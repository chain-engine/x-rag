#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Constants Module

RAG核心模块相关的常量
"""

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
