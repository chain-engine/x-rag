#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embedding Constants Module

向量模型相关的常量
"""

from typing import Final

# ====================================
# 向量模型常量
# ====================================
DEFAULT_EMBEDDING_MODEL: Final[str] = "BAAI/bge-m3"
DEFAULT_EMBEDDING_DEVICE: Final[str] = "cpu"
DEFAULT_EMBEDDING_BATCH_SIZE: Final[int] = 32
DEFAULT_EMBEDDING_CACHE_SIZE: Final[int] = 100
