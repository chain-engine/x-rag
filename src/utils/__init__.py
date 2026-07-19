#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils Package

工具模块，包含文本处理、相似度计算等功能
"""

from utils.text_splitter import (
    TextSplitter,
    CharacterSplitter,
    WordSplitter,
    SentenceSplitter,
    ParagraphSplitter,
    SemanticSplitter,
    TextChunk,
    SplitStrategy,
    create_splitter,
)
from utils.similarity import (
    SimilarityCalculator,
    DistanceType,
    MetadataFilter,
    MMRReranker,
    compute_top_k_similar,
)
from utils.embedding import (
    encode_texts,
    encode_text,
)

__all__ = [
    # Text Splitter
    "TextSplitter",
    "CharacterSplitter",
    "WordSplitter",
    "SentenceSplitter",
    "ParagraphSplitter",
    "SemanticSplitter",
    "TextChunk",
    "SplitStrategy",
    "create_splitter",
    # Similarity
    "SimilarityCalculator",
    "DistanceType",
    "MetadataFilter",
    "MMRReranker",
    "compute_top_k_similar",
    # Embedding
    "encode_texts",
    "encode_text",
]
