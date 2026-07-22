#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Constants Module

RAG核心模块相关的常量
"""

from .base import BaseEnum
from typing import Final


class DocStatus(BaseEnum):
    """文档状态枚举"""
    PENDING = "pending", "待处理"
    PROCESSING = "processing", "处理中"
    COMPLETED = "completed", "已完成"
    FAILED = "failed", "处理失败"
    DELETED = "deleted", "已删除"


class DocType(BaseEnum):
    """文档类型枚举"""
    TXT = "txt", "纯文本"
    MD = "md", "Markdown"
    PDF = "pdf", "PDF文档"
    DOCX = "docx", "Word文档"
    HTML = "html", "HTML网页"


SUPPORTED_DOC_TYPES: Final[set[str]] = set(DocType.get_all_marks())

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
# Prompt 常量
# ====================================
DEFAULT_SYSTEM_PROMPT: Final[str] = "你是一个专业的AI助手，请根据提供的参考资料回答用户问题。"
DEFAULT_USER_PROMPT_TEMPLATE: Final[str] = """基于以下参考资料回答问题。

参考资料：
{context}

问题：{query}

请根据参考资料回答，如果资料中没有相关信息，请如实说明。"""

# ====================================
# 文本切分常量
# ====================================
DEFAULT_CHUNK_SIZE: Final[int] = 512
DEFAULT_CHUNK_OVERLAP: Final[int] = 50


class DistanceType(BaseEnum):
    """距离度量类型枚举"""
    COSINE = "cosine", "余弦距离"
    EUCLIDEAN = "euclidean", "欧氏距离"
    DOT = "dot", "点积"


class RerankingProviderName(BaseEnum):
    """排序 Provider 名称枚举"""
    MMR_RERANKER = "mmr_reranker", "MMR重排序"
    RRF_RERANKER = "rrf_reranker", "RRF重排序"
    SEMANTIC_RERANKER = "semantic_reranker", "语义重排序"
    SCORE_FILTER = "score_filter", "分数过滤"


__all__ = [
    "DocStatus",
    "DocType",
    "SUPPORTED_DOC_TYPES",
    "DISTANCE_COSINE",
    "DISTANCE_EUCLIDEAN",
    "DISTANCE_DOT",
    "DEFAULT_TOP_K",
    "DEFAULT_SIMILARITY_THRESHOLD",
    "DEFAULT_MMR_LAMBDA",
    "DEFAULT_CHUNK_SIZE",
    "DEFAULT_CHUNK_OVERLAP",
    "DEFAULT_SYSTEM_PROMPT",
    "DEFAULT_USER_PROMPT_TEMPLATE",
    "DistanceType",
    "RerankingProviderName",
]
