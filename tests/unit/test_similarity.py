#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相似度计算单元测试
"""

import pytest
import numpy as np
from src.utils.similarity import (
    SimilarityCalculator,
    DistanceType,
    MetadataFilter,
    MMRReranker,
)


class TestSimilarityCalculator:
    """相似度计算器测试"""

    def test_cosine_similarity(self):
        """测试余弦相似度"""
        vec1 = [1, 2, 3]
        vec2 = [2, 4, 6]  # vec1的2倍

        similarity = SimilarityCalculator.cosine_similarity(vec1, vec2)

        assert similarity == pytest.approx(1.0, abs=0.01)

    def test_cosine_similarity_orthogonal(self):
        """测试正交向量的余弦相似度"""
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]

        similarity = SimilarityCalculator.cosine_similarity(vec1, vec2)

        assert similarity == pytest.approx(0.0, abs=0.01)

    def test_euclidean_distance(self):
        """测试欧氏距离"""
        vec1 = [0, 0, 0]
        vec2 = [3, 4, 0]

        distance = SimilarityCalculator.euclidean_distance(vec1, vec2)

        assert distance == pytest.approx(5.0, abs=0.01)

    def test_dot_product(self):
        """测试点积"""
        vec1 = [1, 2, 3]
        vec2 = [4, 5, 6]

        dot = SimilarityCalculator.dot_product(vec1, vec2)

        assert dot == 32  # 1*4 + 2*5 + 3*6

    def test_compute_similarity_cosine(self):
        """测试计算相似度（余弦）"""
        vec1 = [1, 2, 3]
        vec2 = [2, 4, 6]

        similarity = SimilarityCalculator.compute_similarity(
            vec1,
            vec2,
            DistanceType.COSINE,
        )

        assert similarity == pytest.approx(1.0, abs=0.01)

    def test_compute_similarities(self):
        """测试批量计算相似度"""
        query_vec = [1, 2, 3]
        doc_vecs = [
            [1, 2, 3],
            [2, 4, 6],
            [3, 2, 1],
        ]

        similarities = SimilarityCalculator.compute_similarities(
            query_vec,
            doc_vecs,
            DistanceType.COSINE,
        )

        assert len(similarities) == 3
        assert similarities[0] == pytest.approx(1.0, abs=0.01)
        assert similarities[1] == pytest.approx(1.0, abs=0.01)


class TestMetadataFilter:
    """元数据过滤器测试"""

    def test_filter_by_metadata_exact_match(self):
        """测试精确匹配过滤"""
        documents = [
            {"text": "doc1", "metadata": {"category": "tech", "year": 2020}},
            {"text": "doc2", "metadata": {"category": "news", "year": 2021}},
            {"text": "doc3", "metadata": {"category": "tech", "year": 2022}},
        ]

        filtered = MetadataFilter.filter_by_metadata(
            documents,
            {"category": "tech"},
        )

        assert len(filtered) == 2
        assert all(doc["metadata"]["category"] == "tech" for doc in filtered)

    def test_filter_by_metadata_operator(self):
        """测试操作符过滤"""
        documents = [
            {"text": "doc1", "metadata": {"year": 2020}},
            {"text": "doc2", "metadata": {"year": 2021}},
            {"text": "doc3", "metadata": {"year": 2022}},
        ]

        filtered = MetadataFilter.filter_by_metadata(
            documents,
            {"year": {"$gt": 2020}},
        )

        assert len(filtered) == 2
        assert all(doc["metadata"]["year"] > 2020 for doc in filtered)

    def test_filter_by_metadata_in(self):
        """测试in操作符"""
        documents = [
            {"text": "doc1", "metadata": {"status": "active"}},
            {"text": "doc2", "metadata": {"status": "pending"}},
            {"text": "doc3", "metadata": {"status": "completed"}},
        ]

        filtered = MetadataFilter.filter_by_metadata(
            documents,
            {"status": {"$in": ["active", "pending"]}},
        )

        assert len(filtered) == 2

    def test_filter_empty_result(self):
        """测试空结果"""
        documents = [
            {"text": "doc1", "metadata": {"category": "tech"}},
        ]

        filtered = MetadataFilter.filter_by_metadata(
            documents,
            {"category": "news"},
        )

        assert len(filtered) == 0


class TestMMRReranker:
    """MMR重排序器测试"""

    def test_rerank_basic(self):
        """测试基本重排序"""
        query_vec = [1, 0, 0]

        documents = [
            {
                "id": "1",
                "vector": [1, 0, 0],
                "text": "doc1",
                "metadata": {},
            },
            {
                "id": "2",
                "vector": [0.9, 0.1, 0],
                "text": "doc2",
                "metadata": {},
            },
            {
                "id": "3",
                "vector": [0.95, 0.05, 0],
                "text": "doc3",
                "metadata": {},
            },
        ]

        reranked = MMRReranker.rerank(
            query_vec,
            documents,
            lambda_param=0.7,
            distance_type=DistanceType.COSINE,
        )

        assert len(reranked) == len(documents)

    def test_rerank_single_document(self):
        """测试单个文档重排序"""
        query_vec = [1, 0, 0]

        documents = [
            {
                "id": "1",
                "vector": [1, 0, 0],
                "text": "doc1",
                "metadata": {},
            },
        ]

        reranked = MMRReranker.rerank(
            query_vec,
            documents,
            lambda_param=0.5,
            distance_type=DistanceType.COSINE,
        )

        assert len(reranked) == 1
        assert reranked[0]["id"] == "1"

    def test_rerank_empty_documents(self):
        """测试空文档列表"""
        query_vec = [1, 0, 0]

        reranked = MMRReranker.rerank(
            query_vec,
            [],
            lambda_param=0.5,
            distance_type=DistanceType.COSINE,
        )

        assert len(reranked) == 0
