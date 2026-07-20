#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Repositories Package

数据访问层，封装业务CRUD操作
"""

from Repositories.base_repository import BaseRepository
from Repositories.vector_repository import VectorRepository
from Repositories.document_repository import DocumentRepository

__all__ = [
    "BaseRepository",
    "VectorRepository",
    "DocumentRepository",
]
