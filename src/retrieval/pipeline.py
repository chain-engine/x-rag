# -*- coding: utf-8 -*-
"""
Retrieval Pipeline Module

检索流水线 — 编排「查询理解 → 候选召回 → 排序筛选」三阶段
"""

from __future__ import annotations

from typing import Any, ClassVar

from core.logger import logger
from core.exceptions import RetrievalError
from retrieval.understanding.base import (
    BaseQueryUnderstandingProvider,
    QueryUnderstandingResult,
)
from retrieval.candidate.base import BaseRetrievalProvider
from retrieval.ranking.base import BaseRerankingProvider
from constants.rag import (
    RerankingProviderName,
    DEFAULT_TOP_K,
    DEFAULT_SIMILARITY_THRESHOLD,
    DEFAULT_MMR_LAMBDA,
    DISTANCE_COSINE,
    DISTANCE_EUCLIDEAN,
)
from infras.embedding.base import EmbeddingModelBase
from llms.providers import BaseLLMProvider


class RetrievalPipeline:
    """
    检索流水线

    编排检索的三个阶段：
    1. 查询理解（Query Understanding）
    2. 候选召回（Candidate Retrieval）
    3. 排序筛选（Ranking & Filtering）

    支持灵活配置各阶段的 Provider，按顺序执行并传递结果。
    """

    def __init__(
        self,
        understanding_providers: list[BaseQueryUnderstandingProvider] | None = None,
        candidate_providers: list[BaseRetrievalProvider] | None = None,
        reranking_providers: list[BaseRerankingProvider] | None = None,
        filter_engine: MetadataFilterEngine | None = None,
        similarity_engine: SimilaritySearchEngine | None = None,
        default_top_k: int = 5,
        default_threshold: float = 0.7,
    ) -> None:
        """
        初始化检索流水线

        Args:
            understanding_providers: 查询理解阶段提供者列表
            candidate_providers: 候选召回阶段提供者列表
            reranking_providers: 排序筛选阶段提供者列表
            filter_engine: 元数据过滤引擎
            similarity_engine: 相似度计算引擎
            default_top_k: 默认召回数量
            default_threshold: 默认相似度阈值
        """
        self._understanding_providers: list[BaseQueryUnderstandingProvider] = understanding_providers or []
        self._candidate_providers: list[BaseRetrievalProvider] = candidate_providers or []
        self._reranking_providers: list[BaseRerankingProvider] = reranking_providers or []
        self._filter_engine: MetadataFilterEngine = filter_engine or MetadataFilterEngine()
        self._similarity_engine: SimilaritySearchEngine = similarity_engine or SimilaritySearchEngine(
            distance_type=DistanceType.COSINE
        )
        self._default_top_k: int = default_top_k
        self._default_threshold: float = default_threshold
        self._initialized: bool = False

        self._llm_providers: dict[str, BaseLLMProvider] = {}
        self._embedding_model: EmbeddingModelBase | None = None

    # ── Properties ──────────────────────────────────────────

    @property
    def understanding_providers(self) -> list[BaseQueryUnderstandingProvider]:
        return list(self._understanding_providers)

    @property
    def candidate_providers(self) -> list[BaseRetrievalProvider]:
        return list(self._candidate_providers)

    @property
    def reranking_providers(self) -> list[BaseRerankingProvider]:
        return list(self._reranking_providers)

    # ── Lifecycle ───────────────────────────────────────────

    def initialize(self) -> None:
        """初始化所有 Provider"""
        if self._initialized:
            return

        for provider in self._candidate_providers:
            if hasattr(provider, "initialize"):
                provider.initialize()

        for provider in self._understanding_providers:
            if hasattr(provider, "initialize"):
                provider.initialize()

        self._initialized = True
        logger.info(
            f"RetrievalPipeline initialized: "
            f"{len(self._understanding_providers)} understanding, "
            f"{len(self._candidate_providers)} candidate, "
            f"{len(self._reranking_providers)} reranking providers"
        )

    def shutdown(self) -> None:
        """关闭所有资源"""
        if not self._initialized:
            return

        for provider in self._candidate_providers:
            if hasattr(provider, "shutdown"):
                provider.shutdown()

        for provider in self._understanding_providers:
            if hasattr(provider, "shutdown"):
                provider.shutdown()

        self._initialized = False
        logger.info("RetrievalPipeline shut down")

    # ── Public API ──────────────────────────────────────────

    def add_understanding_provider(
        self, provider: BaseQueryUnderstandingProvider
    ) -> None:
        """动态添加查询理解 Provider"""
        self._understanding_providers.append(provider)
        logger.debug(f"Added understanding provider: {provider.name}")

    def add_candidate_provider(self, provider: BaseRetrievalProvider) -> None:
        """动态添加候选召回 Provider"""
        self._candidate_providers.append(provider)
        if hasattr(provider, "initialize") and self._initialized:
            provider.initialize()
        logger.debug(f"Added candidate provider: {provider.name}")

    def add_reranking_provider(self, provider: BaseRerankingProvider) -> None:
        """动态添加排序筛选 Provider"""
        self._reranking_providers.append(provider)
        logger.debug(f"Added reranking provider: {provider.name}")

    def retrieve(
        self,
        query: str,
        top_k: int | None = None,
        similarity_threshold: float | None = None,
        metadata_filter: dict[str, Any] | None = None,
        use_mmr: bool = False,
        mmr_lambda: float = 0.5,
        context: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        执行检索流水线

        Args:
            query: 用户查询文本
            top_k: 召回数量（默认使用配置的 default_top_k）
            similarity_threshold: 相似度阈值
            metadata_filter: 元数据过滤条件
            use_mmr: 是否使用 MMR 多样性排序
            mmr_lambda: MMR 参数
            context: 额外上下文（如对话历史）

        Returns:
            list[dict[str, Any]]: 检索结果列表
        """
        self._check_initialized()

        effective_top_k = top_k or self._default_top_k
        effective_threshold = similarity_threshold or self._default_threshold
        context = context or {}

        try:
            # ── Stage 1: 查询理解 ──────────────────────────
            understanding_result = self._stage1_understand(query, context)
            processed_query = understanding_result.processed_query

            # ── Stage 2: 候选召回 ──────────────────────────
            candidates = self._stage2_candidate_retrieval(
                query=processed_query,
                sub_queries=understanding_result.sub_queries,
                top_k=effective_top_k,
                metadata_filter=metadata_filter,
            )

            if not candidates:
                logger.debug("RetrievalPipeline: no candidates found")
                return []

            # ── Stage 3: 排序筛选 ──────────────────────────
            results = self._stage3_rank_and_filter(
                query=processed_query,
                candidates=candidates,
                effective_threshold=effective_threshold,
                effective_top_k=effective_top_k,
                use_mmr=use_mmr,
                mmr_lambda=mmr_lambda,
            )

            logger.debug(
                f"RetrievalPipeline: retrieved {len(results)} results "
                f"from {len(candidates)} candidates"
            )
            return results

        except Exception as e:
            logger.error(f"RetrievalPipeline failed: {e}")
            raise RetrievalError(f"Retrieval failed: {e}") from e

    def get_stats(self) -> dict[str, Any]:
        """获取流水线统计信息"""
        candidate_stats: dict[str, Any] = {}
        for provider in self._candidate_providers:
            name = provider.name
            if hasattr(provider, "get_stats"):
                candidate_stats[name] = provider.get_stats()

        return {
            "type": "retrieval_pipeline",
            "stages": {
                "understanding": [p.name for p in self._understanding_providers],
                "candidate": [p.name for p in self._candidate_providers],
                "reranking": [p.name for p in self._reranking_providers],
            },
            "defaults": {
                "top_k": self._default_top_k,
                "threshold": self._default_threshold,
            },
            "candidate_stats": candidate_stats,
        }

    # ── Internal Stages ────────────────────────────────────

    def _stage1_understand(
        self, query: str, context: dict[str, Any]
    ) -> QueryUnderstandingResult:
        """Stage 1: 查询理解（并行执行所有 Provider 后合并结果）"""
        if not self._understanding_providers:
            return QueryUnderstandingResult(
                original_query=query,
                processed_query=query,
            )

        results: list[QueryUnderstandingResult] = []

        for provider in self._understanding_providers:
            try:
                result = provider.process(query=query, context=context)
                results.append(result)
                logger.debug(
                    f"Stage1 [{provider.name}]: '{query}' -> "
                    f"processed='{result.processed_query}', "
                    f"sub_queries={len(result.sub_queries)}, "
                    f"hyde={'yes' if result.hypothetical_doc else 'no'}"
                )
            except Exception as e:
                logger.warning(f"Stage1 [{provider.name}] failed: {e}")

        if not results:
            return QueryUnderstandingResult(
                original_query=query,
                processed_query=query,
            )

        merged = results[0]
        for result_item in results[1:]:
            merged = merged.merge(result_item)

        logger.debug(
            f"Stage1 merged: processed='{merged.processed_query}', "
            f"sub_queries={merged.sub_queries}, "
            f"expanded_terms={merged.expanded_terms}"
        )
        return merged

    def _stage2_candidate_retrieval(
        self,
        query: str,
        sub_queries: list[str],
        top_k: int,
        metadata_filter: dict[str, Any] | None,
    ) -> list[dict[str, Any]]:
        """Stage 2: 候选召回"""
        if not self._candidate_providers:
            logger.warning("No candidate providers configured")
            return []

        all_results: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        queries_to_search = sub_queries if sub_queries else [query]

        for q in queries_to_search:
            for provider in self._candidate_providers:
                try:
                    results = provider.search(
                        query=q,
                        top_k=top_k,
                        metadata_filter=metadata_filter,
                    )
                    for r in results:
                        if r.get("id") not in seen_ids:
                            seen_ids.add(r.get("id"))
                            all_results.append(r)
                except Exception as e:
                    logger.warning(f"Stage2 [{provider.name}] failed for '{q}': {e}")

        all_results.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return all_results

    def _stage3_rank_and_filter(
        self,
        query: str,
        candidates: list[dict[str, Any]],
        effective_threshold: float,
        effective_top_k: int,
        use_mmr: bool,
        mmr_lambda: float,
    ) -> list[dict[str, Any]]:
        """Stage 3: 排序筛选"""
        current_candidates = candidates

        for provider in self._reranking_providers:
            try:
                if provider.name == RerankingProviderName.MMR_RERANKER:
                    if use_mmr:
                        current_candidates = provider.rerank(
                            query=query,
                            candidates=current_candidates,
                            lambda_param=mmr_lambda,
                            top_k=effective_top_k * 2,
                        )
                else:
                    current_candidates = provider.rerank(
                        query=query,
                        candidates=current_candidates,
                        top_k=effective_top_k * 2,
                    )
            except Exception as e:
                logger.warning(f"Stage3 [{provider.name}] failed: {e}")

        filtered = [
            doc for doc in current_candidates
            if doc.get("score", 0.0) >= effective_threshold
        ]

        filtered.sort(key=lambda x: x.get("score", 0.0), reverse=True)
        return filtered[:effective_top_k]

    def _check_initialized(self) -> None:
        """检查是否已初始化"""
        if not self._initialized:
            self.initialize()
