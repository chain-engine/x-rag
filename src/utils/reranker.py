# -*- coding: utf-8 -*-
"""
Reranker Module

重排序算法工具集。

NOTE: MMRReranker 和 RRFReranker 已重构为 retrieval.ranking 子包中的类。
      此文件保留原有的静态方法实现，用于向后兼容。
      新代码请使用 retrieval.ranking 模块中的类。
"""

from typing import List, Dict, Any

from utils.similarity import SimilaritySearchEngine, DistanceType
from core.logger import logger


class MMRReranker:
    """
    MMR（Maximal Marginal Relevance）重排序器

    MMR 通过平衡相关性与多样性来选择文档，避免返回内容高度重复的结果。

    公式：score = λ × relevance - (1 - λ) × max_similarity_to_selected
    - λ 越大：越偏向相关性
    - λ 越小：越偏向多样性
    """

    @staticmethod
    def rerank(
        query_vector: List[float],
        documents: List[Dict[str, Any]],
        lambda_param: float = 0.5,
        distance_type: DistanceType = DistanceType.COSINE,
    ) -> List[Dict[str, Any]]:
        """
        使用MMR算法重排序文档

        Args:
            query_vector: 查询向量
            documents: 文档列表，每个文档包含 vector 字段
            lambda_param: 相关性-多样性权衡参数（0-1）
            distance_type: 距离度量类型

        Returns:
            List[Dict[str, Any]]: 重排序后的文档列表
        """
        if not documents:
            return []

        if len(documents) == 1:
            return documents

        engine = SimilaritySearchEngine(distance_type=distance_type)
        doc_vectors = [doc.get("vector", []) for doc in documents]
        similarities = engine.compute_batch(query_vector, doc_vectors)

        selected_indices = []
        remaining_indices = list(range(len(documents)))

        while remaining_indices:
            mmr_scores = []

            for idx in remaining_indices:
                relevance = similarities[idx]

                max_sim = -1.0
                for selected_idx in selected_indices:
                    sim = engine.compute(
                        doc_vectors[idx],
                        doc_vectors[selected_idx],
                    )
                    if sim > max_sim:
                        max_sim = sim

                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
                mmr_scores.append((idx, mmr_score))

            mmr_scores.sort(key=lambda x: x[1], reverse=True)
            best_idx, _ = mmr_scores[0]

            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)

        reranked_documents = [documents[i] for i in selected_indices]

        logger.debug(f"MMRReranker: reranked {len(documents)} docs (lambda={lambda_param})")
        return reranked_documents


class RRFReranker:
    """
    RRF（Reciprocal Rank Fusion）重排序器

    通过多路检索结果的倒数排名进行融合，适用于集成多种检索方法的结果。
    """

    @staticmethod
    def fuse(
        ranked_lists: List[List[Dict[str, Any]]],
        k: int = 60,
    ) -> List[Dict[str, Any]]:
        """
        使用 RRF 算法融合多个排名列表

        Args:
            ranked_lists: 多个已排序的文档列表
            k: RRF 公式中的常数（通常为 60）

        Returns:
            List[Dict[str, Any]]: 融合后的文档列表（按 RRF 分数降序）
        """
        rrf_scores: Dict[str, float] = {}
        doc_ids: Dict[str, Dict[str, Any]] = {}

        for ranked_list in ranked_lists:
            for rank, doc in enumerate(ranked_list):
                doc_id = doc.get("id")
                if doc_id is None:
                    continue

                if doc_id not in rrf_scores:
                    rrf_scores[doc_id] = 0.0
                    doc_ids[doc_id] = doc

                rrf_scores[doc_id] += 1.0 / (k + rank + 1)

        sorted_docs = sorted(
            doc_ids.items(),
            key=lambda x: rrf_scores[x[0]],
            reverse=True,
        )

        logger.debug(f"RRFReranker: fused {len(ranked_lists)} lists into {len(sorted_docs)} docs")
        return [doc for _, doc in sorted_docs]
