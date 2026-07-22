#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pytest Configuration

定义测试夹具和配置
"""

import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path

from repositories.document_repository import DocumentRepository
from repositories.vector_repository import VectorRepository
from services.document_service import DocumentService
from rag.retrieval import Retrieval
from rag.generation import LLMGeneration
from rag.augmentation import Augmentation
from rag.pipeline import RAGPipeline
from utils.text_splitter import TextSplitter, create_splitter, SplitStrategy


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_dir():
    """临时目录夹具"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def document_repository(temp_dir):
    """文档仓库测试夹具"""
    repo = DocumentRepository(storage_path=str(Path(temp_dir) / "documents"))
    repo.initialize()
    yield repo
    repo.shutdown()


@pytest.fixture
def vector_repository(temp_dir):
    """向量仓库测试夹具"""
    repo = VectorRepository(
        collection_name="test_collection",
        persist_directory=str(Path(temp_dir) / "chroma"),
    )
    repo.initialize()
    yield repo
    repo.shutdown()


@pytest.fixture
def document_service(document_repository, vector_repository):
    """文档服务测试夹具"""
    service = DocumentService(
        vector_repo=vector_repository,
        doc_repo=document_repository,
        chunk_size=100,
        chunk_overlap=10,
        chunking_provider="langchain",
        chunking_strategy="recursive",
    )
    service.initialize()
    yield service
    service.shutdown()


@pytest.fixture
def retrieval(vector_repository):
    """检索组件测试夹具"""
    ret = Retrieval(
        vector_repo=vector_repository,
        default_top_k=5,
        default_threshold=0.7,
    )
    ret.initialize()
    yield ret
    ret.shutdown()


@pytest.fixture
def augmentation():
    """增强组件测试夹具"""
    aug = Augmentation()
    aug.initialize()
    yield aug
    aug.shutdown()


@pytest.fixture
def generation():
    """生成组件测试夹具"""
    gen = LLMGeneration(
        default_provider="mock",
        default_model="mock-model",
    )
    gen.initialize()
    yield gen
    gen.shutdown()


@pytest.fixture
def rag_pipeline(retrieval, augmentation, generation):
    """RAG 流水线测试夹具"""
    pipeline = RAGPipeline(
        retrieval=retrieval,
        augmentation=augmentation,
        generation=generation,
    )
    pipeline.initialize()
    yield pipeline
    pipeline.shutdown()


@pytest.fixture
def text_splitter():
    """文本切分器测试夹具"""
    return create_splitter(
        strategy=SplitStrategy.PARAGRAPH,
        chunk_size=100,
        chunk_overlap=10,
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
            "metadata": {"topic": "python", "year": 1991},
        },
        {
            "text": "JavaScript是一种脚本语言，主要用于Web开发。",
            "metadata": {"topic": "javascript", "year": 1995},
        },
        {
            "text": "Rust是一种系统编程语言，注重安全性和性能。",
            "metadata": {"topic": "rust", "year": 2010},
        },
    ]
