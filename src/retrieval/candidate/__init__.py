# -*- coding: utf-8 -*-
"""
Retrieval/Candidate Package

Stage 2 — 候选召回子包
"""

from retrieval.candidate.base import BaseRetrievalProvider
from retrieval.candidate.vector_retrieval import (
    VectorRetrievalProvider,
    ChromaVectorRetrieval,
)
from retrieval.candidate.keyword_retrieval import (
    KeywordRetrievalProvider,
    BM25Retriever,
)

__all__ = [
    "BaseRetrievalProvider",
    "VectorRetrievalProvider",
    "ChromaVectorRetrieval",
    "KeywordRetrievalProvider",
    "BM25Retriever",
]
