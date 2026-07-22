#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG Service Module

RAG业务服务 - 编排检索、增强、生成全流程
"""

from typing import Any

from rag.pipeline import RAGPipeline
from core.logger import logger


class RAGService:
    """RAG业务服务 - 封装RAG完整流程"""

    def __init__(self, pipeline: RAGPipeline):
        self.pipeline = pipeline

    def initialize(self) -> None:
        """初始化"""
        self.pipeline.initialize()
        logger.info("RAGService initialized")

    def shutdown(self) -> None:
        """关闭"""
        self.pipeline.shutdown()
        logger.info("RAGService shut down")

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        return self.pipeline.get_stats()

    async def query(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        use_mmr: bool = False,
        mmr_lambda: float = 0.5,
        metadata_filter: dict[str, Any] | None = None,
        provider: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> dict[str, Any]:
        """RAG查询 - 完整流程

        Args:
            query: 用户查询
            top_k: 检索数量
            similarity_threshold: 相似度阈值
            use_mmr: 是否使用MMR重排序
            mmr_lambda: MMR参数
            metadata_filter: 元数据过滤条件
            provider: LLM提供商
            temperature: 温度参数
            max_tokens: 最大token数

        Returns:
            RAG查询结果
        """
        return await self.pipeline.query(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            use_mmr=use_mmr,
            mmr_lambda=mmr_lambda,
            metadata_filter=metadata_filter,
            provider=provider,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float = 0.7,
        use_mmr: bool = False,
        mmr_lambda: float = 0.5,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """仅检索 - 不进行生成

        Args:
            query: 用户查询的文本
            top_k: 检索数量
            similarity_threshold: 相似度阈值
            use_mmr: 是否使用MMR重排序
            mmr_lambda: MMR参数
            metadata_filter: 元数据过滤条件

        Returns:
            检索到的文档列表
        """
        return self.pipeline.retrieval.retrieve(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            use_mmr=use_mmr,
            mmr_lambda=mmr_lambda,
            metadata_filter=metadata_filter,
        )

    def get_vector_count(self) -> int:
        """获取向量总数"""
        return self.pipeline.retrieval.get_vector_count()

    def encode(self, texts: list[str], normalize: bool = True) -> list[list[float]]:
        """将文本转换为向量

        Args:
            texts: 文本列表
            normalize: 是否归一化

        Returns:
            向量列表
        """
        return self.pipeline.retrieval.encode(texts, normalize=normalize)

    def get_embedding_stats(self) -> dict[str, Any]:
        """获取嵌入模型统计信息"""
        return self.pipeline.retrieval.get_embedding_stats()
