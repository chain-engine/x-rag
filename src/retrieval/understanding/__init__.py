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
from retrieval.understanding.hyde import (
    HyDEProvider,
    LLMHyDE,
)
from retrieval.understanding.subquery import (
    SubqueryDecompositionProvider,
    LLMSubqueryDecomposer,
)

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
    # HyDE
    "HyDEProvider",
    "LLMHyDE",
    # Subquery
    "SubqueryDecompositionProvider",
    "LLMSubqueryDecomposer",
]
