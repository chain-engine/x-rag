#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document Store Base Module

文档存储抽象基类
"""

from abc import ABC, abstractmethod
from typing import Any


class DocumentStoreBase(ABC):
    """文档存储基类

    定义文档存储的标准接口
    """

    @abstractmethod
    def initialize(self) -> None:
        """初始化文档存储"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """关闭文档存储"""
        pass

    @abstractmethod
    def save(self, document_id: str, data: dict[str, Any]) -> None:
        """保存文档

        Args:
            document_id: 文档ID
            data: 文档数据
        """
        pass

    @abstractmethod
    def load(self, document_id: str) -> dict[str, Any] | None:
        """加载文档

        Args:
            document_id: 文档ID

        Returns:
            dict[str, Any] | None: 文档数据
        """
        pass

    @abstractmethod
    def delete(self, document_id: str) -> None:
        """删除文档

        Args:
            document_id: 文档ID
        """
        pass

    @abstractmethod
    def list_all(self) -> list[dict[str, Any]]:
        """列出所有文档

        Returns:
            list[dict[str, Any]]: 文档列表
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, Any]:
        """获取统计信息

        Returns:
            dict[str, Any]: 统计信息
        """
        pass
