# -*- coding: utf-8 -*-
"""
Retrieval/Understanding Package

Stage 1 — 查询理解子包
"""

from retrieval.understanding.base import (
    BaseQueryUnderstandingProvider,
    QueryUnderstandingResult,
)
from retrieval.understanding.rewrite import (
    QueryRewriteProvider,
    LLMQueryRewriter,
    SimpleQueryRewriter,
)
from retrieval.understanding.expansion import (
    QueryExpansionProvider,
    SynonymExpander,
    EmbeddingExpander,
)
from retrieval.understanding.preprocess import (
    QueryPreprocessor,
)
from retrieval.understanding.intent import (
    IntentClassifier,
)
from retrieval.understanding.entity import (
    EntityExtractor,
)

# IntentType / EntityType 已迁移至 constants.understanding
from constants import IntentType, EntityType

__all__ = [
    # Base
    "BaseQueryUnderstandingProvider",
    "QueryUnderstandingResult",
    # Rewrite
    "QueryRewriteProvider",
    "LLMQueryRewriter",
    "SimpleQueryRewriter",
    # Expansion
    "QueryExpansionProvider",
    "SynonymExpander",
    "EmbeddingExpander",
    # Preprocess
    "QueryPreprocessor",
    # Intent
    "IntentClassifier",
    "IntentType",  # re-exported from constants
    # Entity
    "EntityExtractor",
    "EntityType",  # re-exported from constants
]
