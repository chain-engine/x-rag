#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BGE Embedding Model Module

BGE嵌入模型实现
"""

import os

# 使用 HuggingFace 镜像加速下载
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")

import hashlib
import threading
from typing import Optional
from sentence_transformers import SentenceTransformer

from infras.embedding.base import EmbeddingModelBase
from core.logger import logger
from core.exceptions import EmbeddingError
from constants.embedding import (
    DEFAULT_EMBEDDING_MODEL,
    DEFAULT_EMBEDDING_DEVICE,
    DEFAULT_EMBEDDING_BATCH_SIZE,
)


class BGEEmbeddingModel(EmbeddingModelBase):
    """BGE嵌入模型实现"""

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        device: str = DEFAULT_EMBEDDING_DEVICE,
        batch_size: int = DEFAULT_EMBEDDING_BATCH_SIZE,
    ):
        self._model_name = model_name
        self._device = device
        self._batch_size = batch_size
        self._model: Optional[SentenceTransformer] = None
        self._dimension: int = 0

    @property
    def dimension(self) -> int:
        """获取向量维度"""
        if self._dimension == 0:
            self._ensure_loaded()
        return self._dimension

    @property
    def model_name(self) -> str:
        """获取模型名称"""
        return self._model_name

    def encode(self, texts: list[str], normalize: bool = True) -> list[list[float]]:
        """编码文本列表为向量

        将人类可读的文本转换为数值向量表示。

        Args:
            texts: 待编码的文本列表
                示例: ["今天天气很好", "今天下雨了"]
            normalize: 是否归一化向量（默认True）
                - True: 向量长度归一化为1，便于计算余弦相似度（推荐）
                - False: 保留原始向量长度

        Returns:
            二维浮点数列表，每个子列表是一个文本的向量

        Example:
            >>> model = BGEEmbeddingModel()
            >>> vectors = model.encode(["苹果", "香蕉"])
            >>> # 返回: [[0.1, -0.2, ...], [0.5, 0.1, ...]]
        """
        self._ensure_loaded()

        if not texts:
            return []

        try:
            embeddings = self._model.encode(
                texts,
                batch_size=self._batch_size,
                normalize_embeddings=normalize,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Failed to encode texts: {e}")
            raise EmbeddingError(f"Failed to encode texts: {e}") from e

    def encode_single(self, text: str, normalize: bool = True) -> list[float]:
        """编码单个文本为向量"""
        return self.encode([text], normalize=normalize)[0]

    def shutdown(self) -> None:
        """关闭模型"""
        if self._model is not None:
            del self._model
            self._model = None
            self._dimension = 0
            logger.info("BGEEmbeddingModel shut down")

    def _ensure_loaded(self) -> None:
        """确保模型已加载"""
        if self._model is None:
            try:
                logger.info(f"Loading embedding model: {self._model_name} on {self._device}")
                self._model = SentenceTransformer(self._model_name, device=self._device)
                self._dimension = self._model.get_embedding_dimension()
                logger.info(f"Loaded embedding model with dimension {self._dimension}")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise EmbeddingError(f"Failed to load model: {e}") from e


class CachedBGEEmbeddingModel(BGEEmbeddingModel):
    """带缓存的BGE嵌入模型（线程安全）"""

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        device: str = DEFAULT_EMBEDDING_DEVICE,
        batch_size: int = DEFAULT_EMBEDDING_BATCH_SIZE,
        cache_size: int = 1000,
    ):
        super().__init__(model_name, device, batch_size)
        self._cache_size = cache_size
        self._cache: dict[str, list[float]] = {}
        self._cache_lock = threading.RLock()

    def encode(self, texts: list[str], normalize: bool = True) -> list[list[float]]:
        """编码文本列表为向量（带缓存，线程安全）

        将人类可读的文本转换为计算机可处理的数值向量。
        相似的文本会得到相似的向量，可用于语义搜索、相似度计算等场景。

        Args:
            texts: 待编码的文本列表
                示例: ["今天天气很好", "今天下雨了", "我喜欢吃苹果"]
            normalize: 是否归一化向量
                - True: 向量长度归一化为1，便于计算余弦相似度（推荐）
                - False: 保留原始向量长度

        Returns:
            二维浮点数列表，每个子列表对应一个文本的向量

        Example:
            >>> vectors = model.encode(["苹果", "香蕉"])
            >>> # 返回:
            >>> # [
            >>> #   [0.123, -0.456, 0.789, ...],  # "苹果"的向量
            >>> #   [0.234, -0.567, 0.890, ...]   # "香蕉"的向量
            >>> # ]
            >>> len(vectors)      # 2 (2个文本)
            >>> len(vectors[0])  # 1024 (每向量1024维)

        Note:
            - "苹果" 和 "香蕉" 语义相似，向量距离近
            - "苹果" 和 "我喜欢吃水果" 语义不同，向量距离远
        """
        if not texts:
            return []

        embeddings = []
        uncached_texts = []
        uncached_indices = []

        with self._cache_lock:
            for idx, text in enumerate(texts):
                cache_key = self._get_cache_key(text, normalize)
                if cache_key in self._cache:
                    embeddings.append(self._cache[cache_key])  # 命中缓存，直接使用
                else:
                    embeddings.append(None)
                    uncached_texts.append(text)
                    uncached_indices.append(idx)

        if uncached_texts:
            logger.info(f"Encoding {len(uncached_texts)} uncached texts")
            new_embeddings = super().encode(uncached_texts, normalize)  # 调用父类方法批量编码

            with self._cache_lock:
                for text, embedding in zip(uncached_texts, new_embeddings):
                    cache_key = self._get_cache_key(text, normalize)
                    self._add_to_cache(cache_key, embedding)

                for idx, embedding in zip(uncached_indices, new_embeddings):
                    embeddings[idx] = embedding

        return embeddings

    def clear_cache(self) -> None:
        """清空缓存"""
        with self._cache_lock:
            self._cache.clear()
            logger.debug("Cleared embedding cache")

    def _get_cache_key(self, text: str, normalize: bool) -> str:
        """获取缓存键（使用SHA256）"""
        text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        return f"{self._model_name}:{normalize}:{text_hash}"

    def _add_to_cache(self, key: str, value: list[float]) -> None:
        """添加到缓存（LRU淘汰）"""
        if len(self._cache) >= self._cache_size:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
        self._cache[key] = value
