#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Store Package

文档存储基础设施
"""

from infras.document_store.base import DocumentStoreBase
from infras.document_store.json_store import JSONDocumentStore

__all__ = [
    "DocumentStoreBase",
    "JSONDocumentStore",
]
