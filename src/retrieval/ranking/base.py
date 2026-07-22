# -*- coding: utf-8 -*-
"""
Ranking Base Module

Stage 3 — 排序筛选抽象基类，定义统一的排序接口。
"""

from abc import ABC, abstractmethod
from typing import Any, Optional


class BaseRerankingProvider(ABC):
    """
    重排序/过滤提供者基类

    所有排序筛选算法提供者都需要继承此类。
    包括：MMR 多样性排序、RRF 融合排序、语义重排、分值过滤。
    """

    name: str = ""
    description: str = ""

    @abstractmethod
    def rerank(
        self,
        query: str | list[float],
        candidates: list[dict[str, Any]],
        **kwargs,
    ) -> list[dict[str, Any]]:
        """
        对候选文档进行重排序或过滤

        Args:
            query: 查询文本或查询向量
            candidates: 候选文档列表，每项包含 id、text、score、metadata 等
            **kwargs: 额外参数

        Returns:
            list[dict[str, Any]]: 排序/过滤后的文档列表
        """
        pass

    @property
    def provider_name(self) -> str:
        """提供者名称"""
        return self.name

    def get_config(self) -> dict[str, Any]:
        """获取当前配置"""
        return {
            "name": self.name,
            "description": self.description,
        }
