#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相似度计算工具
实现多种相似度计算算法，支持元数据过滤和索引优化
"""

from typing import List, Optional, Dict, Any
from enum import Enum
import numpy as np

from core.logger import logger
from core.exceptions import RetrievalError
from common.constants import (
    DISTANCE_COSINE,
    DISTANCE_EUCLIDEAN,
    DISTANCE_DOT,
)


class DistanceType(str, Enum):
    """距离度量类型"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"


class SimilarityCalculator:
    """相似度计算器"""

    @staticmethod
    def cosine_similarity(query_vector: List[float], doc_vector: List[float]) -> float:
        """计算余弦相似度

        Args:
            query_vector: 查询向量
            doc_vector: 文档向量

        Returns:
            float: 余弦相似度（范围：[-1, 1]）
        """
        query = np.array(query_vector)
        doc = np.array(doc_vector)

        norm_query = np.linalg.norm(query)
        norm_doc = np.linalg.norm(doc)

        if norm_query == 0 or norm_doc == 0:
            return 0.0

        return float(np.dot(query, doc) / (norm_query * norm_doc))

    @staticmethod
    def euclidean_distance(query_vector: List[float], doc_vector: List[float]) -> float:
        """计算欧氏距离

        Args:
            query_vector: 查询向量
            doc_vector: 文档向量

        Returns:
            float: 欧氏距离（范围：[0, +∞)）
        """
        query = np.array(query_vector)
        doc = np.array(doc_vector)
        return float(np.linalg.norm(query - doc))

    @staticmethod
    def dot_product(query_vector: List[float], doc_vector: List[float]) -> float:
        """计算点积

        Args:
            query_vector: 查询向量
            doc_vector: 文档向量

        Returns:
            float: 点积
        """
        query = np.array(query_vector)
        doc = np.array(doc_vector)
        return float(np.dot(query, doc))

    @staticmethod
    def compute_similarity(
        query_vector: List[float],
        doc_vector: List[float],
        distance_type: DistanceType = DistanceType.COSINE
    ) -> float:
        """计算相似度

        Args:
            query_vector: 查询向量
            doc_vector: 文档向量
            distance_type: 距离度量类型

        Returns:
            float: 相似度分数

        Raises:
            RetrievalError: 不支持的距离类型
        """
        if distance_type == DistanceType.COSINE:
            return SimilarityCalculator.cosine_similarity(query_vector, doc_vector)
        elif distance_type == DistanceType.EUCLIDEAN:
            # 转换欧氏距离为相似度（距离越小，相似度越高）
            distance = SimilarityCalculator.euclidean_distance(query_vector, doc_vector)
            return 1.0 / (1.0 + distance)
        elif distance_type == DistanceType.DOT:
            return SimilarityCalculator.dot_product(query_vector, doc_vector)
        else:
            raise RetrievalError(f"Unsupported distance type: {distance_type}")

    @staticmethod
    def compute_similarities(
        query_vector: List[float],
        doc_vectors: List[List[float]],
        distance_type: DistanceType = DistanceType.COSINE
    ) -> List[float]:
        """批量计算相似度

        Args:
            query_vector: 查询向量
            doc_vectors: 文档向量列表
            distance_type: 距离度量类型

        Returns:
            List[float]: 相似度分数列表
        """
        query = np.array(query_vector)
        docs = np.array(doc_vectors)

        if distance_type == DistanceType.COSINE:
            norms = np.linalg.norm(docs, axis=1)
            query_norm = np.linalg.norm(query)
            if query_norm == 0:
                return [0.0] * len(docs)
            similarities = np.dot(docs, query) / (norms * query_norm)
            similarities[np.isnan(similarities)] = 0.0
            return similarities.tolist()
        elif distance_type == DistanceType.EUCLIDEAN:
            distances = np.linalg.norm(docs - query, axis=1)
            similarities = 1.0 / (1.0 + distances)
            return similarities.tolist()
        elif distance_type == DistanceType.DOT:
            return np.dot(docs, query).tolist()
        else:
            raise RetrievalError(f"Unsupported distance type: {distance_type}")


class MetadataFilter:
    """元数据过滤器"""

    @staticmethod
    def filter_by_metadata(
        documents: List[Dict[str, Any]],
        metadata_filter: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """根据元数据过滤文档

        Args:
            documents: 文档列表，每个文档包含metadata字段
            metadata_filter: 过滤条件

        Returns:
            List[Dict[str, Any]]: 过滤后的文档列表
        """
        if not metadata_filter:
            return documents

        filtered_documents = []

        for doc in documents:
            doc_metadata = doc.get("metadata", {})

            if MetadataFilter._matches_filter(doc_metadata, metadata_filter):
                filtered_documents.append(doc)

        logger.debug(f"Filtered {len(documents)} documents to {len(filtered_documents)}")
        return filtered_documents

    @staticmethod
    def _matches_filter(metadata: Dict[str, Any], filter_condition: Dict[str, Any]) -> bool:
        """检查元数据是否匹配过滤条件

        Args:
            metadata: 文档元数据
            filter_condition: 过滤条件

        Returns:
            bool: 是否匹配
        """
        for key, value in filter_condition.items():
            if key not in metadata:
                return False

            if isinstance(value, dict):
                # 支持操作符：$eq, $ne, $gt, $lt, $in, $nin
                if "$eq" in value:
                    if metadata[key] != value["$eq"]:
                        return False
                elif "$ne" in value:
                    if metadata[key] == value["$ne"]:
                        return False
                elif "$gt" in value:
                    if not (isinstance(metadata[key], (int, float)) and metadata[key] > value["$gt"]):
                        return False
                elif "$lt" in value:
                    if not (isinstance(metadata[key], (int, float)) and metadata[key] < value["$lt"]):
                        return False
                elif "$in" in value:
                    if metadata[key] not in value["$in"]:
                        return False
                elif "$nin" in value:
                    if metadata[key] in value["$nin"]:
                        return False
                else:
                    return False
            else:
                # 精确匹配
                if metadata[key] != value:
                    return False

        return True


class MMRReranker:
    """MMR（Maximal Marginal Relevance）重排序器"""

    @staticmethod
    def rerank(
        query_vector: List[float],
        documents: List[Dict[str, Any]],
        lambda_param: float = 0.5,
        distance_type: DistanceType = DistanceType.COSINE
    ) -> List[Dict[str, Any]]:
        """使用MMR算法重排序文档

        Args:
            query_vector: 查询向量
            documents: 文档列表，每个文档包含vector字段
            lambda_param: 相关性-多样性权衡参数（0-1）
            distance_type: 距离度量类型

        Returns:
            List[Dict[str, Any]]: 重排序后的文档列表
        """
        if not documents:
            return []

        if len(documents) == 1:
            return documents

        # 提取文档向量
        doc_vectors = [doc.get("vector", []) for doc in documents]

        # 计算与查询的相关性
        similarities = SimilarityCalculator.compute_similarities(
            query_vector,
            doc_vectors,
            distance_type
        )

        # MMR算法
        selected_indices = []
        remaining_indices = list(range(len(documents)))

        while remaining_indices:
            mmr_scores = []

            for idx in remaining_indices:
                # 相关性分数
                relevance = similarities[idx]

                # 与已选文档的最大相似度（用于度量多样性）
                if selected_indices:
                    selected_vector = doc_vectors[selected_indices[0]]
                    max_sim = 0.0
                    for selected_idx in selected_indices:
                        sim = SimilarityCalculator.compute_similarity(
                            doc_vectors[idx],
                            doc_vectors[selected_idx],
                            distance_type
                        )
                        if sim > max_sim:
                            max_sim = sim
                else:
                    max_sim = 0.0

                # MMR分数
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_sim
                mmr_scores.append((idx, mmr_score))

            # 选择MMR分数最高的文档
            mmr_scores.sort(key=lambda x: x[1], reverse=True)
            best_idx, _ = mmr_scores[0]

            selected_indices.append(best_idx)
            remaining_indices.remove(best_idx)

        # 按照选择顺序返回文档
        reranked_documents = [documents[i] for i in selected_indices]

        logger.debug(f"Reranked {len(documents)} documents using MMR (lambda={lambda_param})")
        return reranked_documents


def compute_top_k_similar(
    query_vector: List[float],
    documents: List[Dict[str, Any]],
    top_k: int = 5,
    distance_type: DistanceType = DistanceType.COSINE,
    threshold: float = 0.0,
    metadata_filter: Optional[Dict[str, Any]] = None,
    use_mmr: bool = False,
    mmr_lambda: float = 0.5
) -> List[Dict[str, Any]]:
    """计算top-k最相似的文档

    Args:
        query_vector: 查询向量
        documents: 文档列表
        top_k: 返回文档数量
        distance_type: 距离度量类型
        threshold: 相似度阈值
        metadata_filter: 元数据过滤条件
        use_mmr: 是否使用MMR重排序
        mmr_lambda: MMR lambda参数

    Returns:
        List[Dict[str, Any]]: 最相似的文档列表
    """
    # 元数据过滤
    if metadata_filter:
        documents = MetadataFilter.filter_by_metadata(documents, metadata_filter)

    if not documents:
        return []

    # 提取文档向量
    doc_vectors = [doc.get("vector", []) for doc in documents]

    # 计算相似度
    similarities = SimilarityCalculator.compute_similarities(
        query_vector,
        doc_vectors,
        distance_type
    )

    # 添加相似度分数
    for doc, similarity in zip(documents, similarities):
        doc["score"] = similarity

    # 过滤低于阈值的文档
    if threshold > 0:
        documents = [doc for doc in documents if doc["score"] >= threshold]

    if not documents:
        return []

    # MMR重排序
    if use_mmr and len(documents) > 1:
        documents = MMRReranker.rerank(
            query_vector,
            documents,
            lambda_param=mmr_lambda,
            distance_type=distance_type
        )
    else:
        # 按相似度排序
        documents.sort(key=lambda x: x["score"], reverse=True)

    # 返回top-k
    return documents[:top_k]