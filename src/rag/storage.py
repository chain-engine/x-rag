#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存储模块
统一管理向量数据库和文档存储
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings

from core.logger import logger
from core.exceptions import DatabaseError


class VectorDB:
    """向量数据库封装"""

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "documents",
        distance_type: str = "cosine"
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.distance_type = distance_type

        try:
            self._client = chromadb.PersistentClient(
                path=persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
            )
            self._collection = self._get_or_create_collection()
            logger.info(f"VectorDB initialized: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize VectorDB: {e}")
            raise DatabaseError(f"Failed to initialize vector store: {e}") from e

    def _get_or_create_collection(self):
        """获取或创建集合"""
        distance_mapping = {"cosine": "cosine", "euclidean": "l2", "dot": "ip"}
        distance = distance_mapping.get(self.distance_type, "cosine")

        try:
            return self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": distance}
            )
        except Exception as e:
            logger.error(f"Failed to get or create collection: {e}")
            raise DatabaseError(f"Failed to get or create collection: {e}") from e

    def add(self, ids: List[str], embeddings: List[List[float]],
            documents: List[str], metadatas: List[Dict[str, Any]] | None = None) -> None:
        """添加向量"""
        if len(ids) != len(embeddings) or len(ids) != len(documents):
            raise ValueError("Length of ids, embeddings, and documents must match")

        if metadatas is None:
            metadatas = [{} for _ in ids]

        if len(metadatas) != len(ids):
            raise ValueError("Length of metadatas must match ids")

        try:
            self._collection.add(ids=ids, embeddings=embeddings,
                              documents=documents, metadatas=metadatas)
            logger.debug(f"Added {len(ids)} vectors to collection")
        except Exception as e:
            logger.error(f"Failed to add vectors: {e}")
            raise DatabaseError(f"Failed to add vectors: {e}") from e

    def get(self, ids: List[str]) -> List[Dict[str, Any]]:
        """获取向量"""
        try:
            results = self._collection.get(
                ids=ids,
                include=["embeddings", "documents", "metadatas"]
            )
            vectors = []
            for idx in range(len(results["ids"])):
                vectors.append({
                    "id": results["ids"][idx],
                    "vector": results["embeddings"][idx] if results["embeddings"] else None,
                    "text": results["documents"][idx] if results["documents"] else None,
                    "metadata": results["metadatas"][idx] if results["metadatas"] else {}
                })
            return vectors
        except Exception as e:
            logger.error(f"Failed to get vectors: {e}")
            raise DatabaseError(f"Failed to get vectors: {e}") from e

    def query(self, query_embeddings: List[List[float]], n_results: int = 5,
              where: Dict[str, Any] | None = None,
              where_document: Dict[str, Any] | None = None) -> List[Dict[str, Any]]:
        """查询向量"""
        try:
            results = self._collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                where_document=where_document,
                include=["embeddings", "documents", "metadatas", "distances"]
            )
            documents = []
            for query_idx in range(len(query_embeddings)):
                for result_idx in range(len(results["ids"][query_idx])):
                    documents.append({
                        "id": results["ids"][query_idx][result_idx],
                        "vector": results["embeddings"][query_idx][result_idx],
                        "text": results["documents"][query_idx][result_idx],
                        "metadata": results["metadatas"][query_idx][result_idx],
                        "distance": results["distances"][query_idx][result_idx],
                        "score": 1.0 - results["distances"][query_idx][result_idx]
                    })
            return documents
        except Exception as e:
            logger.error(f"Failed to query vectors: {e}")
            raise DatabaseError(f"Failed to query vectors: {e}") from e

    def count(self) -> int:
        """统计向量数量"""
        try:
            return self._collection.count()
        except Exception as e:
            logger.error(f"Failed to count vectors: {e}")
            raise DatabaseError(f"Failed to count vectors: {e}") from e

    def clear(self) -> None:
        """清空集合"""
        try:
            self._client.delete_collection(name=self.collection_name)
            self._collection = self._get_or_create_collection()
            logger.info(f"Cleared collection {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise DatabaseError(f"Failed to clear collection: {e}") from e

    def delete_by_document_id(self, document_id: str) -> int:
        """根据文档ID删除向量"""
        try:
            results = self._collection.get(where={"document_id": document_id})
            ids = results["ids"]

            if ids:
                self._collection.delete(ids=ids)
                logger.debug(f"Deleted {len(ids)} vectors for document {document_id}")
                return len(ids)

            return 0
        except Exception as e:
            logger.error(f"Failed to delete vectors by document ID: {e}")
            raise DatabaseError(f"Failed to delete vectors by document ID: {e}") from e

    def get_by_document_id(self, document_id: str) -> List[Dict[str, Any]]:
        """根据文档ID获取向量"""
        try:
            results = self._collection.get(
                where={"document_id": document_id},
                include=["embeddings", "documents", "metadatas"]
            )
            vectors = []
            for idx in range(len(results["ids"])):
                vectors.append({
                    "id": results["ids"][idx],
                    "vector": results["embeddings"][idx] if results["embeddings"] else None,
                    "text": results["documents"][idx] if results["documents"] else None,
                    "metadata": results["metadatas"][idx] if results["metadatas"] else {}
                })
            return vectors
        except Exception as e:
            logger.error(f"Failed to get vectors by document ID: {e}")
            raise DatabaseError(f"Failed to get vectors by document ID: {e}") from e


class DocumentStore:
    """文档存储（基于JSON）"""

    def __init__(self, storage_path: str = "./data/documents"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"DocumentStore initialized at {storage_path}")

    def _get_document_path(self, document_id: str) -> Path:
        """获取文档文件路径"""
        return self.storage_path / f"{document_id}.json"

    def save(self, document: Dict[str, Any]) -> None:
        """保存文档"""
        try:
            file_path = self._get_document_path(document["document_id"])
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(document, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved document {document['document_id']}")
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            raise DatabaseError(f"Failed to save document: {e}") from e

    def load(self, document_id: str) -> Optional[Dict[str, Any]]:
        """加载文档"""
        try:
            file_path = self._get_document_path(document_id)
            if not file_path.exists():
                return None
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            raise DatabaseError(f"Failed to load document: {e}") from e

    def delete(self, document_id: str) -> bool:
        """删除文档"""
        try:
            file_path = self._get_document_path(document_id)
            if not file_path.exists():
                return False
            file_path.unlink()
            logger.debug(f"Deleted document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise DatabaseError(f"Failed to delete document: {e}") from e

    def update(self, document_id: str, updates: Dict[str, Any]) -> None:
        """更新文档"""
        document = self.load(document_id)
        if document is None:
            raise DatabaseError(f"Document {document_id} not found")
        document.update(updates)
        self.save(document)

    def list_all(self) -> List[Dict[str, Any]]:
        """列出所有文档"""
        try:
            documents = []
            for file_path in self.storage_path.glob("*.json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    documents.append(json.load(f))
            return documents
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            raise DatabaseError(f"Failed to list documents: {e}") from e


# 全局实例（用于兼容旧的模块初始化）
_vector_db_instance: VectorDB | None = None
_doc_store_instance: DocumentStore | None = None


def get_vector_db() -> VectorDB:
    """获取全局向量数据库实例"""
    if _vector_db_instance is None:
        raise RuntimeError("Vector DB not initialized")
    return _vector_db_instance


def get_document_store() -> DocumentStore:
    """获取全局文档存储实例"""
    if _doc_store_instance is None:
        raise RuntimeError("Document store not initialized")
    return _doc_store_instance


def initialize_storage(vector_db: VectorDB, doc_store: DocumentStore) -> None:
    """初始化全局存储实例"""
    global _vector_db_instance, _doc_store_instance
    _vector_db_instance = vector_db
    _doc_store_instance = doc_store
    logger.info("Storage instances initialized globally")