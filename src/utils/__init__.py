#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils Package

工具模块，提供相似度计算、过滤、重排序和索引优化功能
"""

# 相似度计算
from .similarity import (
    SimilaritySearchEngine,
    SimilarityCalculator,
    DistanceType,
)

# 过滤器
from .filters import (
    MetadataFilterEngine,
    MetadataFilter,
)

# 重排序
from .reranker import (
    MMRReranker,
    RRFReranker,
)

# 索引优化
from .index_optimizer import (
    VectorIndexOptimizer,
    IndexConfig,
    MemoryEstimate,
)

__all__ = [
    # Similarity - 相似度计算
    "SimilaritySearchEngine",
    "SimilarityCalculator",
    "DistanceType",
    # Filters - 元数据过滤
    "MetadataFilterEngine",
    "MetadataFilter",
    # Reranker - 重排序
    "MMRReranker",
    "RRFReranker",
    # Index Optimizer - 索引优化
    "VectorIndexOptimizer",
    "IndexConfig",
    "MemoryEstimate",
]
