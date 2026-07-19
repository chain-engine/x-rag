#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Vector Store Base Module

向量存储抽象基类
"""

from abc import ABC, abstractmethod
from typing import Any


class VectorRecord:
    """向量记录"""

    def __init__(
        self,
        id: str,
        text: str,
        vector: list[float],
        metadata: dict[str, Any] | None = None,
    ):
        self.id = id
        self.text = text
        self.vector = vector
        self.metadata = metadata or {}


class VectorStoreBase(ABC):
    """向量存储基类

    定义向量存储的标准接口
    """

    @abstractmethod
    def initialize(self) -> None:
        """初始化向量存储"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """关闭向量存储"""
        pass

    @abstractmethod
    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """添加向量

        Args:
            ids: 向量ID列表
            embeddings: 向量列表
            documents: 原始文档文本列表
            metadatas: 元数据列表
        """
        pass

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where: dict[str, Any] | None = None,
        include: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """搜索相似向量

        Args:
            query_embedding: 查询向量
            top_k: 返回数量
            where: 过滤条件
            include: 返回字段

        Returns:
            list[dict[str, Any]]: 搜索结果列表
        """
        pass

    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        """删除向量

        Args:
            ids: 向量ID列表
        """
        pass

    @abstractmethod
    def get_count(self) -> int:
        """获取向量总数

        Returns:
            int: 向量数量
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """获取统计信息

        Returns:
            dict[str, Any]: 统计信息
        """
        pass
