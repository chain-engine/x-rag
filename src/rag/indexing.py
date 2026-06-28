#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索引构建模块
处理文档索引构建流程
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from core.logger import logger
from core.exceptions import DocumentError, EmbeddingError, VectorStoreError
from utils.text_splitter import create_splitter, SplitStrategy
from utils.embedding import encode_texts
from common.constants import (
    DOC_STATUS_PENDING,
    DOC_STATUS_PROCESSING,
    DOC_STATUS_COMPLETED,
    DOC_STATUS_FAILED,
)


# 全局存储实例
_vector_db = None
_doc_store = None


def initialize_stores(vector_db, doc_store):
    """初始化存储实例

    Args:
        vector_db: 向量数据库实例
        doc_store: 文档存储实例
    """
    global _vector_db, _doc_store
    _vector_db = vector_db
    _doc_store = doc_store
    logger.info("RAG stores initialized")


def index_document(
    text: str,
    document_id: str | None = None,
    file_name: str = "",
    file_type: str = "txt",
    file_size: int = 0,
    metadata: Dict[str, Any] | None = None,
    chunk_size: int = 512,
    chunk_overlap: int = 50
) -> Dict[str, Any]:
    """索引文档

    Args:
        text: 文档内容
        document_id: 文档ID，自动生成如果为None
        file_name: 文件名
        file_type: 文件类型
        file_size: 文件大小
        metadata: 元数据
        chunk_size: 分块大小
        chunk_overlap: 分块重叠

    Returns:
        Dict[str, Any]: 索引结果

    Raises:
        DocumentError: 索引失败
    """
    if _vector_db is None or _doc_store is None:
        raise RuntimeError("Stores not initialized. Call initialize_stores() first.")

    if document_id is None:
        document_id = str(uuid.uuid4())

    if metadata is None:
        metadata = {}

    try:
        # 保存文档元数据
        _doc_store.save({
            "document_id": document_id,
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size,
            "status": DOC_STATUS_PROCESSING,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "metadata": metadata
        })

        # 切分文本
        splitter = create_splitter(
            strategy=SplitStrategy.PARAGRAPH,
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        chunks = splitter.split_text(text, metadata)

        if not chunks:
            raise DocumentError(f"No chunks generated for document {document_id}")

        logger.info(f"Split document {document_id} into {len(chunks)} chunks")

        # 提取文本
        chunk_texts = [chunk.content for chunk in chunks]

        # 向量化
        embeddings = encode_texts(chunk_texts, normalize=True, cached=True)

        if len(embeddings) != len(chunks):
            raise EmbeddingError("Embedding count mismatch")

        logger.info(f"Generated {len(embeddings)} embeddings for document {document_id}")

        # 准备向量存储数据
        ids = [chunk.chunk_id for chunk in chunks]
        documents = chunk_texts
        metadatas = [
            {
                "document_id": document_id,
                "chunk_index": str(idx),
                **chunk.metadata
            }
            for idx, chunk in enumerate(chunks)
        ]

        # 存储向量
        _vector_db.add(ids, embeddings, documents, metadatas)

        # 更新文档状态
        _doc_store.update(document_id, {
            "status": DOC_STATUS_COMPLETED,
            "chunk_count": len(chunks),
            "updated_at": datetime.utcnow().isoformat()
        })

        logger.info(f"Successfully indexed document {document_id}")

        return {
            "document_id": document_id,
            "status": "completed",
            "chunk_count": len(chunks)
        }

    except Exception as e:
        logger.error(f"Failed to index document {document_id}: {e}")
        if _doc_store:
            _doc_store.update(document_id, {"status": DOC_STATUS_FAILED})
        raise DocumentError(f"Failed to index document {document_id}: {e}") from e


def index_document_from_file(
    file_path: str,
    document_id: str | None = None,
    metadata: Dict[str, Any] | None = None
) -> Dict[str, Any]:
    """从文件索引文档

    Args:
        file_path: 文件路径
        document_id: 文档ID
        metadata: 元数据

    Returns:
        Dict[str, Any]: 索引结果

    Raises:
        DocumentError: 索引失败
    """
    path = Path(file_path)

    if not path.exists():
        raise DocumentError(f"File not found: {file_path}")

    # 读取文件内容
    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except UnicodeDecodeError:
        try:
            with open(path, "r", encoding="gbk") as f:
                text = f.read()
        except Exception as e:
            raise DocumentError(f"Failed to read file: {e}")

    # 提取文件信息
    file_name = path.name
    file_type = path.suffix.lstrip(".").lower()
    file_size = path.stat().st_size

    # 添加文件元数据
    file_metadata = {
        "file_path": str(path),
        "file_name": file_name,
        "file_size": file_size,
        "file_type": file_type
    }

    if metadata:
        file_metadata.update(metadata)

    return index_document(
        text=text,
        document_id=document_id,
        file_name=file_name,
        file_type=file_type,
        file_size=file_size,
        metadata=file_metadata
    )


def delete_document(document_id: str) -> Dict[str, Any]:
    """删除文档

    Args:
        document_id: 文档ID

    Returns:
        Dict[str, Any]: 删除结果

    Raises:
        DocumentError: 删除失败
    """
    if _vector_db is None or _doc_store is None:
        raise RuntimeError("Stores not initialized")

    try:
        # 删除向量
        vector_count = _vector_db.delete_by_document_id(document_id)

        # 删除文档元数据
        _doc_store.delete(document_id)

        logger.info(f"Successfully deleted document {document_id} ({vector_count} vectors)")

        return {
            "document_id": document_id,
            "status": "deleted",
            "vector_count": vector_count
        }

    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise DocumentError(f"Failed to delete document {document_id}: {e}") from e


def get_document_status(document_id: str) -> Dict[str, Any]:
    """获取文档状态

    Args:
        document_id: 文档ID

    Returns:
        Dict[str, Any]: 文档状态
    """
    if _doc_store is None:
        raise RuntimeError("Document store not initialized")

    document = _doc_store.load(document_id)

    if document is None:
        return {
            "document_id": document_id,
            "status": "not_found"
        }

    if _vector_db:
        vectors = _vector_db.get_by_document_id(document_id)
        vector_count = len(vectors)
    else:
        vector_count = 0

    return {
        "document_id": document.get("document_id"),
        "file_name": document.get("file_name"),
        "file_type": document.get("file_type"),
        "status": document.get("status"),
        "chunk_count": document.get("chunk_count", 0),
        "vector_count": vector_count,
        "created_at": document.get("created_at"),
        "updated_at": document.get("updated_at"),
        "metadata": document.get("metadata", {})
    }


def list_documents(
    status: str | None = None,
    file_type: str | None = None
) -> List[Dict[str, Any]]:
    """列出文档

    Args:
        status: 文档状态过滤
        file_type: 文件类型过滤

    Returns:
        List[Dict[str, Any]]: 文档列表
    """
    if _doc_store is None:
        raise RuntimeError("Document store not initialized")

    documents = _doc_store.list_all()

    if status:
        documents = [doc for doc in documents if doc.get("status") == status]
    if file_type:
        documents = [doc for doc in documents if doc.get("file_type") == file_type]

    return documents