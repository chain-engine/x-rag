#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest配置
定义测试夹具和配置
"""

import pytest
import asyncio
from pathlib import Path

from repository.document_repository import DocumentRepository, JSONDocumentStorage
from repository.vector_repository import VectorRepository
from service.indexing_service import IndexingService
from service.retrieval_service import RetrievalService
from service.generation_service import GenerationService, LLMProvider
from utils.text_splitter import TextSplitter, create_splitter, SplitStrategy
from utils.embedding import get_embedding_model


@pytest.fixture
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def document_repository():
    """文档仓库测试夹具"""
    storage = JSONDocumentStorage(storage_path="./tests/data/documents")
    repo = DocumentRepository(storage)
    yield repo
    # 清理测试数据
    documents = await repo.list_all()
    for doc in documents:
        await repo.delete(doc.document_id)


@pytest.fixture
async def vector_repository():
    """向量仓库测试夹具"""
    repo = VectorRepository(
        collection_name="test_collection",
        persist_directory="./tests/data/chroma"
    )
    yield repo
    # 清理测试数据
    await repo.clear()


@pytest.fixture
async def indexing_service(document_repository, vector_repository):
    """索引服务测试夹具"""
    service = IndexingService(document_repository, vector_repository)
    await service.initialize()
    yield service
    await service.shutdown()


@pytest.fixture
async def retrieval_service(vector_repository):
    """检索服务测试夹具"""
    service = RetrievalService(vector_repository)
    await service.initialize()
    yield service
    await service.shutdown()


@pytest.fixture
def generation_service():
    """生成服务测试夹具"""
    service = GenerationService(
        default_provider=LLMProvider.DEEPSEEK,
        default_model="deepseek-chat"
    )
    yield service


@pytest.fixture
def text_splitter():
    """文本切分器测试夹具"""
    return create_splitter(
        strategy=SplitStrategy.PARAGRAPH,
        chunk_size=100,
        chunk_overlap=10
    )


@pytest.fixture
def sample_text():
    """示例文本"""
    return """
    Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。
    Python的设计哲学强调代码的可读性和简洁的语法。
    相比于C++或Java，Python让开发者能够用更少的代码表达概念。

    Python支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。
    它拥有一个庞大而全面的标准库。
    """


@pytest.fixture
def sample_documents():
    """示例文档列表"""
    return [
        {
            "text": "Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。",
            "metadata": {"topic": "python", "year": 1991}
        },
        {
            "text": "JavaScript是一种脚本语言，主要用于Web开发。",
            "metadata": {"topic": "javascript", "year": 1995}
        },
        {
            "text": "Rust是一种系统编程语言，注重安全性和性能。",
            "metadata": {"topic": "rust", "year": 2010}
        }
    ]