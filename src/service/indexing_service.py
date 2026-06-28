#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索引构建服务
处理文档索引构建流程的业务逻辑
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from service.base_service import BaseService
from repository.vector_repository import VectorRepository
from repository.document_repository import DocumentRepository
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


class IndexingService(BaseService):
    """索引构建服务"""

    def __init__(
        self,
        vector_repo: VectorRepository,
        doc_repo: DocumentRepository,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ):
        self.vector_repo = vector_repo
        self.doc_repo = doc_repo
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._initialized = False

    def initialize(self) -> None:
        """初始化服务"""
        self.vector_repo.initialize()
        self.doc_repo.initialize()
        self._initialized = True
        logger.info("IndexingService initialized")

    def shutdown(self) -> None:
        """关闭服务"""
        if self._initialized:
            self.vector_repo.shutdown()
            self.doc_repo.shutdown()
            self._initialized = False
            logger.info("IndexingService shut down")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "type": "indexing",
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "vector_stats": self.vector_repo.get_stats(),
            "document_stats": self.doc_repo.get_stats()
        }

    def index_document(
        self,
        text: str,
        document_id: str | None = None,
        file_name: str = "",
        file_type: str = "txt",
        file_size: int = 0,
        metadata: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """索引文档

        Args:
            text: 文档内容
            document_id: 文档ID，自动生成如果为None
            file_name: 文件名
            file_type: 文件类型
            file_size: 文件大小
            metadata: 元数据

        Returns:
            Dict[str, Any]: 索引结果

        Raises:
            DocumentError: 索引失败
        """
        self._check_initialized()

        if document_id is None:
            document_id = str(uuid.uuid4())

        if metadata is None:
            metadata = {}

        try:
            # 保存文档元数据
            self.doc_repo.save({
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
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
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
            self.vector_repo.add(ids, embeddings, documents, metadatas)

            # 更新文档状态
            self.doc_repo.update(document_id, {
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
            self.doc_repo.update(document_id, {"status": DOC_STATUS_FAILED})
            raise DocumentError(f"Failed to index document {document_id}: {e}") from e

    def index_document_from_file(
        self,
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

        return self.index_document(
            text=text,
            document_id=document_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            metadata=file_metadata
        )

    def delete_document(self, document_id: str) -> Dict[str, Any]:
        """删除文档

        Args:
            document_id: 文档ID

        Returns:
            Dict[str, Any]: 删除结果

        Raises:
            DocumentError: 删除失败
        """
        self._check_initialized()

        try:
            # 删除向量
            vector_count = self.vector_repo.delete_by_document_id(document_id)

            # 删除文档元数据
            self.doc_repo.delete(document_id)

            logger.info(f"Successfully deleted document {document_id} ({vector_count} vectors)")

            return {
                "document_id": document_id,
                "status": "deleted",
                "vector_count": vector_count
            }

        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise DocumentError(f"Failed to delete document {document_id}: {e}") from e

    def get_document(self, document_id: str) -> Dict[str, Any]:
        """获取文档完整信息

        Args:
            document_id: 文档ID

        Returns:
            Dict[str, Any]: 文档完整信息（包括状态和向量详情）
        """
        self._check_initialized()

        document = self.doc_repo.load(document_id)

        if document is None:
            return {
                "document_id": document_id,
                "status": "not_found",
                "message": "Document not found"
            }

        vectors = self.vector_repo.get_by_document_id(document_id)
        vector_count = len(vectors)

        chunks = []
        for vec in vectors:
            chunks.append({
                "chunk_id": vec.get("id"),
                "text": vec.get("text", "")[:200] + "..." if len(vec.get("text", "")) > 200 else vec.get("text", ""),
                "vector_dimension": len(vec.get("vector", [])),
                "metadata": vec.get("metadata", {})
            })

        return {
            "document_id": document.get("document_id"),
            "file_name": document.get("file_name"),
            "file_type": document.get("file_type"),
            "file_size": document.get("file_size", 0),
            "status": document.get("status"),
            "chunk_count": document.get("chunk_count", 0),
            "vector_count": vector_count,
            "created_at": document.get("created_at"),
            "updated_at": document.get("updated_at"),
            "metadata": document.get("metadata", {}),
            "chunks": chunks
        }

    def get_document_status(self, document_id: str) -> Dict[str, Any]:
        """获取文档状态

        Args:
            document_id: 文档ID

        Returns:
            Dict[str, Any]: 文档状态
        """
        self._check_initialized()

        document = self.doc_repo.load(document_id)

        if document is None:
            return {
                "document_id": document_id,
                "status": "not_found"
            }

        vectors = self.vector_repo.get_by_document_id(document_id)
        vector_count = len(vectors)

        return {
            "document_id": document.get("document_id"),
            "file_name": document.get("file_name"),
            "status": document.get("status"),
            "chunk_count": document.get("chunk_count", 0),
            "vector_count": vector_count
        }

    def list_documents(
        self,
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
        self._check_initialized()

        documents = self.doc_repo.list_all()

        if status:
            documents = [doc for doc in documents if doc.get("status") == status]
        if file_type:
            documents = [doc for doc in documents if doc.get("file_type") == file_type]

        return documents

    def _check_initialized(self) -> None:
        """检查服务是否已初始化"""
        if not self._initialized:
            raise RuntimeError("IndexingService not initialized. Call initialize() first.")