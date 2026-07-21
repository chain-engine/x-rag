#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Repository Module

Vector store repository
"""

from typing import Any

from .base_repository import BaseRepository
from infras.vector_store.chroma import ChromaVectorStore
from core.logger import logger


class VectorRepository(BaseRepository):
    """向量仓库"""

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        collection_name: str = "documents",
        distance_type: str = "cosine",
    ):
        self._store = ChromaVectorStore(
            persist_directory=persist_directory,
            collection_name=collection_name,
            distance_type=distance_type,
        )
        self._initialized = False

    def initialize(self) -> None:
        """初始化向量存储"""
        if self._initialized:
            return
        self._store.initialize()
        self._initialized = True
        logger.info("VectorRepository initialized")

    def shutdown(self) -> None:
        """关闭向量存储"""
        if self._initialized:
            self._store.shutdown()
            self._initialized = False
            logger.info("VectorRepository shut down")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return self._store.get_stats()

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """添加向量"""
        self._ensure_initialized()
        self._store.add(ids, embeddings, documents, metadatas)

    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """搜索向量"""
        self._ensure_initialized()
        results = self._store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        # 转换结果格式
        for result in results:
            distance = result.pop("distance", 0.0)
            # 将距离转换为相似度分数
            if distance is not None:
                result["score"] = 1.0 / (1.0 + distance)
            else:
                result["score"] = 0.0

        return results

    def delete(self, ids: list[str]) -> None:
        """删除向量"""
        self._ensure_initialized()
        self._store.delete(ids)

    def delete_by_document_id(self, document_id: str) -> int:
        """根据文档ID删除向量"""
        self._ensure_initialized()

        results = self._store.search(
            query_embedding=[0.0] * 1024,  # 使用零向量搜索
            top_k=10000,
            where={"document_id": document_id},
        )

        ids_to_delete = [r["id"] for r in results if r.get("metadata", {}).get("document_id") == document_id]

        if ids_to_delete:
            self._store.delete(ids_to_delete)

        return len(ids_to_delete)

    def get_by_document_id(self, document_id: str) -> list[dict[str, Any]]:
        """根据文档ID获取向量"""
        self._ensure_initialized()

        results = self._store.search(
            query_embedding=[0.0] * 1024,
            top_k=10000,
            where={"document_id": document_id},
        )

        return [r for r in results if r.get("metadata", {}).get("document_id") == document_id]

    def get_count(self) -> int:
        """获取向量总数"""
        self._ensure_initialized()
        return self._store.get_count()

    def _ensure_initialized(self) -> None:
        """确保已初始化"""
        if not self._initialized:
            raise RuntimeError("VectorRepository not initialized. Call initialize() first.")
