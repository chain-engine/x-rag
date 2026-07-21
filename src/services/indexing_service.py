#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Indexing Service Module

索引构建服务
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from services.base_service import BaseService
from repositories.vector_repository import VectorRepository
from repositories.document_repository import DocumentRepository
from core.logger import logger
from core.exceptions import DocumentError
from utils.text_splitter import ParagraphSplitter
from infras.embedding.bge_model import CachedBGEEmbeddingModel
from constants.rag import (
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
        chunk_overlap: int = 50,
    ):
        self._vector_repo = vector_repo
        self._doc_repo = doc_repo
        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._initialized = False
        self._embedding_model: CachedBGEEmbeddingModel | None = None
        self._text_splitter = ParagraphSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def initialize(self) -> None:
        """初始化服务（仅初始化存储，不加载模型）"""
        self._vector_repo.initialize()
        self._doc_repo.initialize()
        # 不在这里创建 embedding model，延迟到首次使用时
        self._initialized = True
        logger.info("IndexingService initialized (embedding model will be loaded on first use)")

    def _get_embedding_model(self) -> CachedBGEEmbeddingModel:
        """延迟获取 embedding model"""
        if self._embedding_model is None:
            logger.info("Loading embedding model on first use...")
            self._embedding_model = CachedBGEEmbeddingModel()
        return self._embedding_model

    def shutdown(self) -> None:
        """关闭服务"""
        if self._initialized:
            self._vector_repo.shutdown()
            self._doc_repo.shutdown()
            if self._embedding_model:
                self._embedding_model.shutdown()
            self._initialized = False
            logger.info("IndexingService shut down")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "type": "indexing",
            "chunk_size": self._chunk_size,
            "chunk_overlap": self._chunk_overlap,
            "vector_stats": self._vector_repo.get_stats(),
            "document_stats": self._doc_repo.get_stats(),
        }

    def index_document(
        self,
        text: str,
        document_id: str | None = None,
        file_name: str = "",
        file_type: str = "txt",
        file_size: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """索引文档"""
        self._check_initialized()

        if document_id is None:
            document_id = str(uuid.uuid4())

        if metadata is None:
            metadata = {}

        try:
            # 保存文档元数据
            logger.info(f"Indexing document {document_id}: saving metadata...")
            self._doc_repo.save({
                "document_id": document_id,
                "file_name": file_name,
                "file_type": file_type,
                "file_size": file_size,
                "status": DOC_STATUS_PROCESSING,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "metadata": metadata,
            })
            logger.info(f"Document {document_id} metadata saved")

            # 切分文本
            logger.info(f"Document {document_id}: splitting text...")
            chunks = self._text_splitter.split_text(text, metadata)
            logger.info(f"Document {document_id}: split into {len(chunks)} chunks")

            if not chunks:
                raise DocumentError(f"No chunks generated for document {document_id}")

            # 提取文本
            chunk_texts = [chunk.content for chunk in chunks]

            # 向量化
            logger.info(f"Document {document_id}: encoding {len(chunk_texts)} chunks...")
            embeddings = self._get_embedding_model().encode(chunk_texts, normalize=True)
            logger.info(f"Document {document_id}: encoded successfully")

            # 准备向量存储数据
            ids = [chunk.chunk_id for chunk in chunks]
            metadatas = [
                {
                    "document_id": document_id,
                    "chunk_index": str(idx),
                    **chunk.metadata,
                }
                for idx, chunk in enumerate(chunks)
            ]

            # 存储向量
            self._vector_repo.add(ids, embeddings, chunk_texts, metadatas)

            # 更新文档状态
            self._doc_repo.update(document_id, {
                "status": DOC_STATUS_COMPLETED,
                "chunk_count": len(chunks),
                "updated_at": datetime.utcnow().isoformat(),
            })

            logger.info(f"Successfully indexed document {document_id}")

            return {
                "document_id": document_id,
                "status": "completed",
                "chunk_count": len(chunks),
            }

        except Exception as e:
            import traceback
            logger.error(f"Failed to index document {document_id}: {e}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            self._doc_repo.update(document_id, {"status": DOC_STATUS_FAILED})
            raise DocumentError(f"Failed to index document {document_id}: {e}") from e

    def index_document_from_file(
        self,
        file_path: str,
        document_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """从文件索引文档"""
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
                raise DocumentError(f"Failed to read file: {e}") from e

        # 提取文件信息
        file_name = path.name
        file_type = path.suffix.lstrip(".").lower()
        file_size = path.stat().st_size

        # 添加文件元数据
        file_metadata = {
            "file_path": str(path),
            "file_name": file_name,
            "file_size": file_size,
            "file_type": file_type,
        }

        if metadata:
            file_metadata.update(metadata)

        return self.index_document(
            text=text,
            document_id=document_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            metadata=file_metadata,
        )

    def delete_document(self, document_id: str) -> dict[str, Any]:
        """删除文档"""
        self._check_initialized()

        try:
            vector_count = self._vector_repo.delete_by_document_id(document_id)
            self._doc_repo.delete(document_id)

            logger.info(f"Successfully deleted document {document_id} ({vector_count} vectors)")

            return {
                "document_id": document_id,
                "status": "deleted",
                "vector_count": vector_count,
            }

        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise DocumentError(f"Failed to delete document {document_id}: {e}") from e

    def get_document(self, document_id: str) -> dict[str, Any]:
        """获取文档完整信息"""
        self._check_initialized()

        document = self._doc_repo.load(document_id)

        if document is None:
            return {
                "document_id": document_id,
                "status": "not_found",
                "message": "Document not found",
            }

        vectors = self._vector_repo.get_by_document_id(document_id)

        chunks = []
        for vec in vectors:
            text = vec.get("text", "")
            chunks.append({
                "chunk_id": vec.get("id"),
                "text": text[:200] + "..." if len(text) > 200 else text,
                "metadata": vec.get("metadata", {}),
            })

        return {
            "document_id": document.get("document_id"),
            "file_name": document.get("file_name"),
            "file_type": document.get("file_type"),
            "file_size": document.get("file_size", 0),
            "status": document.get("status"),
            "chunk_count": document.get("chunk_count", 0),
            "vector_count": len(vectors),
            "created_at": document.get("created_at"),
            "updated_at": document.get("updated_at"),
            "metadata": document.get("metadata", {}),
            "chunks": chunks,
        }

    def get_document_status(self, document_id: str) -> dict[str, Any]:
        """获取文档状态"""
        self._check_initialized()

        document = self._doc_repo.load(document_id)

        if document is None:
            return {
                "document_id": document_id,
                "status": "not_found",
            }

        vectors = self._vector_repo.get_by_document_id(document_id)

        return {
            "document_id": document.get("document_id"),
            "file_name": document.get("file_name"),
            "status": document.get("status"),
            "chunk_count": document.get("chunk_count", 0),
            "vector_count": len(vectors),
        }

    def list_documents(
        self,
        status: str | None = None,
        file_type: str | None = None,
        skip: int = 0,
        limit: int | None = None,
    ) -> dict[str, Any]:
        """列出文档（支持分页）

        参数:
            status: 按文档状态筛选
            file_type: 按文件类型筛选
            skip: 跳过的文档数量
            limit: 返回的最大文档数量

        返回:
            包含文档列表和分页信息的字典
        """
        self._check_initialized()

        if skip < 0:
            skip = 0
        if limit is not None and limit < 1:
            limit = None

        documents = self._doc_repo.list_all()

        if status:
            documents = [doc for doc in documents if doc.get("status") == status]
        if file_type:
            documents = [doc for doc in documents if doc.get("file_type") == file_type]

        total = len(documents)

        if skip > 0 and skip < len(documents):
            documents = documents[skip:]
        elif skip >= len(documents):
            documents = []

        if limit is not None and limit > 0:
            documents = documents[:limit]

        return {
            "documents": documents,
            "total": total,
            "skip": skip,
            "limit": limit,
        }

    def _check_initialized(self) -> None:
        """检查服务是否已初始化"""
        if not self._initialized:
            raise RuntimeError("IndexingService not initialized. Call initialize() first.")
