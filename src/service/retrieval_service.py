#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检索服务
处理文档检索和相似度计算的业务逻辑
"""

from typing import List, Optional, Dict, Any

from service.base_service import BaseService
from repository.vector_repository import VectorRepository
from core.logger import logger
from core.exceptions import RetrievalError
from utils.embedding import encode_text
from utils.similarity import compute_top_k_similar, DistanceType
from common.constants import DEFAULT_TOP_K, DEFAULT_SIMILARITY_THRESHOLD


class RetrievalService(BaseService):
    """检索服务"""

    def __init__(self, vector_repo: VectorRepository):
        self.vector_repo = vector_repo
        self._initialized = False

    def initialize(self) -> None:
        """初始化服务"""
        self.vector_repo.initialize()
        self._initialized = True
        logger.info("RetrievalService initialized")

    def shutdown(self) -> None:
        """关闭服务"""
        if self._initialized:
            self.vector_repo.shutdown()
            self._initialized = False
            logger.info("RetrievalService shut down")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "type": "retrieval",
            "initialized": self._initialized,
            "vector_stats": self.vector_repo.get_stats() if self._initialized else None
        }

    def retrieve(
        self,
        query: str,
        top_k: int = DEFAULT_TOP_K,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
        use_mmr: bool = False,
        mmr_lambda: float = 0.5,
        metadata_filter: Optional[Dict[str, Any]] = None,
        distance_type: str = "cosine"
    ) -> List[Dict[str, Any]]:
        """检索相关文档

        Args:
            query: 查询文本
            top_k: 返回文档数量
            similarity_threshold: 相似度阈值
            use_mmr: 是否使用MMR算法
            mmr_lambda: MMR lambda参数
            metadata_filter: 元数据过滤条件
            distance_type: 距离度量类型

        Returns:
            List[Dict[str, Any]]: 检索结果列表

        Raises:
            RetrievalError: 检索失败
        """
        self._check_initialized()

        try:
            # 预处理查询
            query = query.strip()

            # 向量化查询
            query_vector = encode_text(query, normalize=True, cached=True)
            logger.debug(f"Query vector dimension: {len(query_vector)}")

            # 从向量存储检索
            if metadata_filter or use_mmr:
                # 需要后处理的情况
                all_results = self.vector_repo.query(
                    query_embeddings=[query_vector],
                    n_results=top_k * 3 if use_mmr else top_k * 2,
                    where=metadata_filter
                )

                # 转换为标准格式
                documents = []
                for result in all_results:
                    documents.append({
                        "id": result["id"],
                        "vector": result["vector"],
                        "text": result["text"],
                        "metadata": result["metadata"],
                        "score": result["score"]
                    })

                # 应用阈值过滤
                if similarity_threshold > 0:
                    documents = [doc for doc in documents if doc["score"] >= similarity_threshold]

                # 应用MMR重排序
                if use_mmr and len(documents) > 1:
                    from utils.similarity import MMRReranker
                    documents = MMRReranker.rerank(
                        query_vector,
                        documents,
                        lambda_param=mmr_lambda,
                        distance_type=DistanceType(distance_type)
                    )
                else:
                    documents.sort(key=lambda x: x["score"], reverse=True)

                # 返回top-k
                results = documents[:top_k]
            else:
                # 直接使用向量数据库的查询功能
                results = self.vector_repo.query(
                    query_embeddings=[query_vector],
                    n_results=top_k,
                    where=metadata_filter
                )

                # 过滤低于阈值的文档
                filtered = [r for r in results if r["score"] >= similarity_threshold]
                results = filtered[:top_k] if len(filtered) > top_k else filtered

            logger.info(f"Retrieved {len(results)} documents for query: {query[:50]}...")

            return results

        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            raise RetrievalError(f"Failed to retrieve documents: {e}") from e

    def retrieve_by_document_id(self, document_id: str) -> List[Dict[str, Any]]:
        """根据文档ID检索文档

        Args:
            document_id: 文档ID

        Returns:
            List[Dict[str, Any]]: 检索结果列表
        """
        self._check_initialized()

        try:
            results = self.vector_repo.get_by_document_id(document_id)
            logger.info(f"Retrieved {len(results)} vectors for document {document_id}")
            return results
        except Exception as e:
            logger.error(f"Failed to retrieve document {document_id}: {e}")
            raise RetrievalError(f"Failed to retrieve document {document_id}: {e}") from e

    def get_vector_count(self) -> int:
        """获取向量数量

        Returns:
            int: 向量数量
        """
        self._check_initialized()
        return self.vector_repo.count()

    def _check_initialized(self) -> None:
        """检查服务是否已初始化"""
        if not self._initialized:
            raise RuntimeError("RetrievalService not initialized. Call initialize() first.")