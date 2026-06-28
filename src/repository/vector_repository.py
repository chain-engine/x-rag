#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量仓库
基于Chroma的向量数据访问层
"""

from typing import List, Optional, Dict, Any
import chromadb
from chromadb.config import Settings as ChromaSettings

from repository.base_repository import BaseRepository
from core.logger import logger
from core.exceptions import DatabaseError


class VectorRepository(BaseRepository):
    """向量仓库"""

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "documents",
        distance_type: str = "cosine"
    ):
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.distance_type = distance_type
        self._client: Optional[chromadb.PersistentClient] = None
        self._collection = None

    def initialize(self) -> None:
        """初始化向量数据库"""
        try:
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True)
            )
            self._collection = self._get_or_create_collection()
            logger.info(f"VectorRepository initialized: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to initialize VectorRepository: {e}")
            raise DatabaseError(f"Failed to initialize vector store: {e}") from e

    def shutdown(self) -> None:
        """关闭向量数据库"""
        if self._client:
            del self._client
            self._client = None
            logger.info("VectorRepository shut down")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "type": "vector",
            "collection": self.collection_name,
            "count": self.count()
        }

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

    def add(
        self,
        ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """向向量库添加向量数据

        Args:
            ids: 向量唯一标识符列表，每个ID必须唯一，用于后续检索和管理
            embeddings: 向量嵌入数据列表，每个元素是一个浮点数列表，表示文档的向量化结果
            documents: 向量对应的原始文档文本列表，用于后续检索时返回上下文信息
            metadatas: 元数据列表，每个元素是一个字典，包含文档的额外属性（如来源、时间等），可选参数

        Returns:
            None

        Raises:
            ValueError: 当 ids、embeddings、documents 的长度不一致时抛出
            ValueError: 当 metadatas 的长度与 ids 不一致时抛出
            DatabaseError: 向量库操作失败时抛出

        Examples:
            >>> repo.add(
            ...     ids=["doc_001", "doc_002"],
            ...     embeddings=[[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]],
            ...     documents=["文档1内容", "文档2内容"],
            ...     metadatas=[{"source": "file_a"}, {"source": "file_b"}]
            ... )
        """
        if len(ids) != len(embeddings) or len(ids) != len(documents):
            raise ValueError("Length of ids, embeddings, and documents must match")

        if metadatas is None:
            metadatas = [{} for _ in ids]

        if len(metadatas) != len(ids):
            raise ValueError("Length of metadatas must match ids")

        try:
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas
            )
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
                    "vector": results["embeddings"][idx] if results["embeddings"] is not None and len(results["embeddings"]) > idx else None,
                    "text": results["documents"][idx] if results["documents"] is not None and len(results["documents"]) > idx else None,
                    "metadata": results["metadatas"][idx] if results["metadatas"] is not None and len(results["metadatas"]) > idx else {}
                })
            return vectors
        except Exception as e:
            logger.error(f"Failed to get vectors: {e}")
            raise DatabaseError(f"Failed to get vectors: {e}") from e

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
        where_document: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """查询相似向量

        在向量库中根据查询向量检索最相似的文档片段。

        Args:
            query_embeddings: 查询向量列表，每个元素是一个浮点数列表，表示查询文本的向量化结果
            n_results: 返回的最大结果数量，默认为5
            where: 元数据过滤条件，用于过滤具有特定属性的文档，如 {"source": "news"}
            where_document: 文档内容过滤条件，用于按文档内容进行过滤

        Returns:
            List[Dict[str, Any]]: 匹配的文档列表，每个元素包含以下字段：
                - id: 向量唯一标识符
                - vector: 向量嵌入数据
                - text: 原始文档文本
                - metadata: 元数据字典
                - distance: 与查询向量的距离（越小越相似）
                - score: 相似度分数（1 - distance，越大越相似）

        Raises:
            DatabaseError: 向量库查询操作失败时抛出

        Examples:
            >>> results = repo.query(
            ...     query_embeddings=[[0.1, 0.2, 0.3]],
            ...     n_results=3,
            ...     where={"source": "news"}
            ... )
            >>> print(results[0]["text"], results[0]["score"])
        """
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
                    "vector": results["embeddings"][idx] if results["embeddings"] is not None and len(results["embeddings"]) > idx else None,
                    "text": results["documents"][idx] if results["documents"] is not None and len(results["documents"]) > idx else None,
                    "metadata": results["metadatas"][idx] if results["metadatas"] is not None and len(results["metadatas"]) > idx else {}
                })
            return vectors
        except Exception as e:
            logger.error(f"Failed to get vectors by document ID: {e}")
            raise DatabaseError(f"Failed to get vectors by document ID: {e}") from e