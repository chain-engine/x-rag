#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Retrieval Service Module

检索服务
"""

from typing import Any

from service.base_service import BaseService
from repository.vector_repository import VectorRepository
from core.logger import logger
from core.exceptions import RetrievalError
from infras.embedding.bge_model import CachedBGEEmbeddingModel


class RetrievalService(BaseService):
    """检索服务"""

    def __init__(self, vector_repo: VectorRepository):
        self._vector_repo = vector_repo
        self._initialized = False
        self._embedding_model: CachedBGEEmbeddingModel | None = None

    def initialize(self) -> None:
        """初始化服务"""
        self._vector_repo.initialize()
        self._embedding_model = CachedBGEEmbeddingModel()
        self._initialized = True
        logger.info("RetrievalService initialized")

    def shutdown(self) -> None:
        """关闭服务"""
        if self._initialized:
            self._vector_repo.shutdown()
            if self._embedding_model:
                self._embedding_model.shutdown()
            self._initialized = False
            logger.info("RetrievalService shut down")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return {
            "type": "retrieval",
            "vector_count": self._vector_repo.get_count(),
            "vector_stats": self._vector_repo.get_stats(),
        }

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        use_mmr: bool = False,
        mmr_lambda: float = 0.5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """检索相关文档"""
        self._check_initialized()

        try:
            # 将查询文本转换为向量
            query_embedding = self._embedding_model.encode_single(query, normalize=True)

            # 执行向量检索
            results = self._vector_repo.search(
                query_embedding=query_embedding,
                top_k=top_k,
                where=metadata_filter,
            )

            # 过滤低相似度结果
            filtered_results = [
                r for r in results
                if r.get("score", 0) >= similarity_threshold
            ]

            # 如果启用MMR，重新排序结果以增加多样性
            if use_mmr and len(filtered_results) > 1:
                filtered_results = self._mmr_rerank(
                    query_embedding=query_embedding,
                    results=filtered_results,
                    lambda_val=mmr_lambda,
                    top_k=top_k,
                )

            # 格式化结果
            formatted_results = []
            for result in filtered_results[:top_k]:
                formatted_results.append({
                    "id": result.get("id"),
                    "text": result.get("text"),
                    "score": result.get("score", 0),
                    "metadata": result.get("metadata", {}),
                })

            return formatted_results

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            raise RetrievalError(f"Retrieval failed: {e}") from e

    def get_vector_count(self) -> int:
        """获取向量总数"""
        self._check_initialized()
        return self._vector_repo.get_count()

    def _mmr_rerank(
        self,
        query_embedding: list[float],
        results: list[dict[str, Any]],
        lambda_val: float,
        top_k: int,
    ) -> list[dict[str, Any]]:
        """MMR重排序以增加结果多样性"""
        if not results or top_k >= len(results):
            return results

        selected = []
        remaining = results.copy()

        while len(selected) < top_k and remaining:
            if len(selected) == 0:
                selected.append(remaining.pop(0))
                continue

            best_score = -1
            best_idx = 0
            best_result = None

            for idx, result in enumerate(remaining):
                relevance = result.get("score", 0)
                max_similarity = 0

                # 计算与已选结果的最大相似度
                for selected_result in selected:
                    selected_embedding = selected_result.get("embedding")
                    if selected_embedding:
                        similarity = self._cosine_similarity(query_embedding, selected_embedding)
                        max_similarity = max(max_similarity, similarity)

                mmr_score = lambda_val * relevance - (1 - lambda_val) * max_similarity

                if mmr_score > best_score:
                    best_score = mmr_score
                    best_idx = idx
                    best_result = result

            if best_result:
                selected.append(remaining.pop(best_idx))

        return selected

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """计算余弦相似度"""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(a * a for a in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)

    def _check_initialized(self) -> None:
        """检查服务是否已初始化"""
        if not self._initialized:
            raise RuntimeError("RetrievalService not initialized. Call initialize() first.")
