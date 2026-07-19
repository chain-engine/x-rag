#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repository Package

数据访问层，封装业务CRUD操作
"""

from repository.base_repository import BaseRepository
from repository.vector_repository import VectorRepository
from repository.document_repository import DocumentRepository

__all__ = [
    "BaseRepository",
    "VectorRepository",
    "DocumentRepository",
]
