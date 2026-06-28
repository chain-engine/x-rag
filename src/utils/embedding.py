#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向量化工具
集成BGE-M3模型，支持批量向量化和向量缓存机制
"""

import hashlib
from typing import List, Optional
from functools import lru_cache
import numpy as np
from sentence_transformers import SentenceTransformer

from core.logger import logger
from core.exceptions import EmbeddingError
from core.config import settings
from common.constants import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_DEVICE,
    DEFAULT_EMBEDDING_BATCH_SIZE,
)


class EmbeddingModel:
    """嵌入模型类"""

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        batch_size: int | None = None
    ) -> None:
        model_name = model_name or getattr(settings, "EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        device = device or getattr(settings, "EMBEDDING_DEVICE", DEFAULT_EMBEDDING_DEVICE)
        batch_size = batch_size or getattr(settings, "EMBEDDING_BATCH_SIZE", DEFAULT_EMBEDDING_BATCH_SIZE)

        self.model_name: str = model_name
        self.device: str = device
        self.batch_size: int = batch_size
        self._model: Optional[SentenceTransformer] = None
        self._dimension: int = 0

        logger.info(f"Initializing embedding model: {model_name} on {device}")

    @property
    def model(self) -> SentenceTransformer:
        """获取模型实例（懒加载）

        Returns:
            SentenceTransformer: 模型实例
        """
        if self._model is None:
            try:
                self._model = SentenceTransformer(self.model_name, device=self.device)
                self._dimension = self._model.get_sentence_embedding_dimension()
                logger.info(f"Loaded embedding model {self.model_name} with dimension {self._dimension}")
            except Exception as e:
                logger.error(f"Failed to load embedding model {self.model_name}: {e}")
                raise EmbeddingError(f"Failed to load embedding model: {e}")
        return self._model

    @property
    def dimension(self) -> int:
        """获取向量维度

        Returns:
            int: 向量维度
        """
        if self._dimension == 0:
            _ = self.model
        return self._dimension

    def encode(
        self,
        texts: List[str],
        normalize: bool = True,
        batch_size: Optional[int] = None
    ) -> List[List[float]]:
        """将文本编码为向量

        Args:
            texts: 待编码的文本列表
            normalize: 是否归一化
            batch_size: 批处理大小

        Returns:
            List[List[float]]: 向量列表

        Raises:
            EmbeddingError: 编码失败时抛出
        """
        if not texts:
            return []

        try:
            batch_size = batch_size or self.batch_size
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise EmbeddingError(f"Failed to encode texts: {e}")

    def encode_single(
        self,
        text: str,
        normalize: bool = True
    ) -> List[float]:
        """将单个文本编码为向量

        Args:
            text: 待编码的文本
            normalize: 是否归一化

        Returns:
            List[float]: 向量

        Raises:
            EmbeddingError: 编码失败时抛出
        """
        return self.encode([text], normalize=normalize)[0]

    @staticmethod
    def _get_text_hash(text: str) -> str:
        """获取文本哈希值（用于缓存）

        Args:
            text: 文本

        Returns:
            str: 哈希值
        """
        return hashlib.md5(text.encode("utf-8")).hexdigest()


class CachedEmbeddingModel(EmbeddingModel):
    """带缓存的嵌入模型"""

    def __init__(
        self,
        model_name: str | None = None,
        device: str | None = None,
        batch_size: int | None = None,
        cache_size: int = 1000
    ) -> None:
        super().__init__(model_name, device, batch_size)
        self.cache_size = cache_size
        self._cache: dict[str, List[float]] = {}

    def encode(
        self,
        texts: List[str],
        normalize: bool = True,
        batch_size: Optional[int] = None
    ) -> List[List[float]]:
        """将文本编码为向量（带缓存）

        Args:
            texts: 待编码的文本列表
            normalize: 是否归一化
            batch_size: 批处理大小

        Returns:
            List[List[float]]: 向量列表
        """
        if not texts:
            return []

        # 检查缓存
        embeddings = []
        uncached_texts = []
        uncached_indices = []

        for idx, text in enumerate(texts):
            cache_key = self._get_cache_key(text, normalize)
            if cache_key in self._cache:
                embeddings.append(self._cache[cache_key])
            else:
                embeddings.append(None)
                uncached_texts.append(text)
                uncached_indices.append(idx)

        # 编码未缓存的文本
        if uncached_texts:
            new_embeddings = super().encode(uncached_texts, normalize, batch_size)

            # 更新缓存
            for text, embedding in zip(uncached_texts, new_embeddings):
                cache_key = self._get_cache_key(text, normalize)
                self._add_to_cache(cache_key, embedding)

            # 合并结果
            for idx, embedding in zip(uncached_indices, new_embeddings):
                embeddings[idx] = embedding

        return embeddings

    def _get_cache_key(self, text: str, normalize: bool) -> str:
        """获取缓存键

        Args:
            text: 文本
            normalize: 是否归一化

        Returns:
            str: 缓存键
        """
        text_hash = self._get_text_hash(text)
        return f"{self.model_name}:{normalize}:{text_hash}"

    def _add_to_cache(self, key: str, value: List[float]) -> None:
        """添加到缓存

        Args:
            key: 缓存键
            value: 缓存值
        """
        if len(self._cache) >= self.cache_size:
            # 简单的LRU策略：移除第一个缓存项
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = value

    def clear_cache(self) -> None:
        """清空缓存"""
        self._cache.clear()
        logger.debug("Cleared embedding cache")


# 全局模型实例
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model(cached: bool = True, cache_size: int = 1000) -> EmbeddingModel:
    """获取嵌入模型实例（单例模式）

    Args:
        cached: 是否使用缓存
        cache_size: 缓存大小

    Returns:
        EmbeddingModel: 嵌入模型实例
    """
    global _embedding_model

    if _embedding_model is None:
        if cached:
            cache_size = getattr(settings, "EMBEDDING_CACHE_SIZE", 1000)
            _embedding_model = CachedEmbeddingModel(cache_size=cache_size)
        else:
            _embedding_model = EmbeddingModel()

    return _embedding_model


def encode_texts(
    texts: List[str],
    normalize: bool = True,
    cached: bool = True
) -> List[List[float]]:
    """编码文本列表

    Args:
        texts: 待编码的文本列表
        normalize: 是否归一化
        cached: 是否使用缓存

    Returns:
        List[List[float]]: 向量列表
    """
    model = get_embedding_model(cached=cached)
    return model.encode(texts, normalize=normalize)


def encode_text(text: str, normalize: bool = True, cached: bool = True) -> List[float]:
    """编码单个文本

    Args:
        text: 待编码的文本
        normalize: 是否归一化
        cached: 是否使用缓存

    Returns:
        List[float]: 向量
    """
    return encode_texts([text], normalize=normalize, cached=cached)[0]