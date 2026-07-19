#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Embedding Base Module

嵌入模型抽象基类
"""

from abc import ABC, abstractmethod
from typing import Any


class EmbeddingModelBase(ABC):
    """嵌入模型基类

    定义嵌入模型的标准接口
    """

    @property
    @abstractmethod
    def dimension(self) -> int:
        """获取向量维度"""
        pass

    @property
    @abstractmethod
    def model_name(self) -> str:
        """获取模型名称"""
        pass

    @abstractmethod
    def encode(self, texts: list[str], normalize: bool = True) -> list[list[float]]:
        """编码文本列表为向量

        Args:
            texts: 文本列表
            normalize: 是否归一化

        Returns:
            list[list[float]]: 向量列表
        """
        pass

    @abstractmethod
    def encode_single(self, text: str, normalize: bool = True) -> list[float]:
        """编码单个文本为向量

        Args:
            text: 文本
            normalize: 是否归一化

        Returns:
            list[float]: 向量
        """
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """关闭模型"""
        pass
