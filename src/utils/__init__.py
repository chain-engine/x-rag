#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Utils Package

Utility modules for text processing, similarity calculation
"""

from .text_splitter import (
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
from .similarity import (
    SimilarityCalculator,
    DistanceType,
    MetadataFilter,
    MMRReranker,
    compute_top_k_similar,
)
from .embedding import (
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
