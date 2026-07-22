# -*- coding: utf-8 -*-
"""
Retrieval Module

检索模块 — 向量检索和重排序（委托至 RetrievalPipeline）
"""

from typing import Any

from core.logger import logger
from core.exceptions import RetrievalError
from repositories.vector_repository import VectorRepository
from infras.embedding.bge_model import CachedBGEEmbeddingModel
from retrieval.pipeline import RetrievalPipeline
from retrieval.candidate.vector_retrieval import ChromaVectorRetrieval
from retrieval.ranking.mmr import MMRReranker
from retrieval.ranking.score_filter import ScoreFilter
from utils.similarity import SimilaritySearchEngine, DistanceType


class Retrieval:
    """
    检索器 — 向量检索和重排序

    本类作为上层 API 入口，委托至 RetrievalPipeline 执行三阶段检索流水线。
    """

    def __init__(
        self,
        vector_repo: VectorRepository | None = None,
        embedding_model: CachedBGEEmbeddingModel | None = None,
        default_top_k: int = 5,
        default_threshold: float = 0.7,
    ):
        """
        初始化检索器

        Args:
            vector_repo: 向量仓库实例（可选）
            embedding_model: Embedding 模型实例（可选）
            default_top_k: 默认召回数量
            default_threshold: 默认相似度阈值
        """
        self._vector_repo = vector_repo
        self._embedding_model = embedding_model
        self._default_top_k = default_top_k
        self._default_threshold = default_threshold
        self._initialized = False

        # ── 构建默认的检索流水线 ──────────────────────────
        vector_retrieval = ChromaVectorRetrieval(
            vector_repo=vector_repo,
            embedding_model=embedding_model,
            top_k=default_top_k,
        )

        self._pipeline = RetrievalPipeline(
            candidate_providers=[vector_retrieval],
            reranking_providers=[
                MMRReranker(distance_type=DistanceType.COSINE),
                ScoreFilter(threshold=default_threshold),
            ],
            similarity_engine=SimilaritySearchEngine(distance_type=DistanceType.COSINE),
            default_top_k=default_top_k,
            default_threshold=default_threshold,
        )

    def initialize(self) -> None:
        """初始化"""
        self._pipeline.initialize()
        self._initialized = True
        logger.info("Retrieval initialized")

    def shutdown(self) -> None:
        """关闭"""
        if self._initialized:
            self._pipeline.shutdown()
            self._initialized = False
            logger.info("Retrieval shut down")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return self._pipeline.get_stats()

    def encode(self, texts: list[str], normalize: bool = True) -> list[list[float]]:
        """将文本转换为向量"""
        self._check_initialized()
        if self._embedding_model:
            return self._embedding_model.encode(texts, normalize=normalize)
        return []

    def get_embedding_stats(self) -> dict[str, Any]:
        """获取嵌入模型统计信息"""
        if self._embedding_model:
            return {
                "model": self._embedding_model.model_name,
                "dimension": self._embedding_model.dimension,
            }
        return {"model": "unknown", "dimension": 0}

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        use_mmr: bool = False,
        mmr_lambda: float = 0.5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        检索相关文档

        Args:
            query: 查询文本
            top_k: 召回数量
            similarity_threshold: 相似度阈值
            use_mmr: 是否使用 MMR 多样性排序
            mmr_lambda: MMR 参数
            metadata_filter: 元数据过滤条件

        Returns:
            list[dict[str, Any]]: 检索结果
        """
        self._check_initialized()

        results = self._pipeline.retrieve(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            metadata_filter=metadata_filter,
            use_mmr=use_mmr,
            mmr_lambda=mmr_lambda,
        )

        formatted = []
        for result in results[:top_k]:
            formatted.append({
                "id": result.get("id"),
                "text": result.get("text"),
                "score": result.get("score", 0),
                "metadata": result.get("metadata", {}),
            })

        return formatted

    def get_vector_count(self) -> int:
        """获取向量总数"""
        self._check_initialized()
        stats = self._pipeline.get_stats()
        stats_info = stats.get("candidate_stats", {})
        for stat in stats_info.values():
            return stat.get("count", 0)
        return 0

    def _check_initialized(self) -> None:
        """检查是否已初始化"""
        if not self._initialized:
            raise RuntimeError("Retrieval not initialized. Call initialize() first.")
