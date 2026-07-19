#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Store Constants Module

向量存储相关的常量
"""

from typing import Final

# ====================================
# 向量存储常量
# ====================================
DISTANCE_COSINE: Final[str] = "cosine"
VECTOR_STORE_CHROMA: Final[str] = "chroma"
DEFAULT_COLLECTION_NAME: Final[str] = "documents"
DEFAULT_DISTANCE: Final[str] = DISTANCE_COSINE
