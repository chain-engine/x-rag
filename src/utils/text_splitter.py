#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本切分工具
实现多种文本切分策略，支持自定义切分参数和元数据提取
"""

import re
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

from core.logger import logger
from constants.rag import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
)


class SplitStrategy(str, Enum):
    """切分策略枚举"""
    CHARACTER = "character"  # 按字符数量切分，适用于固定长度切分场景
    WORD = "word"  # 按空格/标点分词后切分，保留单词完整性
    SENTENCE = "sentence"  # 按句子边界（如句号、问号）切分，保持句子完整
    PARAGRAPH = "paragraph"  # 按段落切分，适用于有明显段落结构的文档
    SEMANTIC = "semantic"  # 基于语义 embedding 相似度切分，保持语义连贯性


@dataclass
class TextChunk:
    """文本分块"""
    content: str
    chunk_id: str
    start_index: int
    end_index: int
    metadata: Dict[str, Any]

    def __repr__(self) -> str:
        return f"TextChunk(id={self.chunk_id}, length={len(self.content)})"


class TextSplitter:
    """文本切分器基类"""

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        separators: List[str] | None = None
    ) -> None:
        self.chunk_size: int = chunk_size
        self.chunk_overlap: int = chunk_overlap
        self.separators: List[str] = separators or ["\n\n", "\n", "。", "！", "？", " ", ""]
        logger.debug(f"Initialized TextSplitter with chunk_size={chunk_size}, overlap={chunk_overlap}")

    def split_text(self, text: str, metadata: Dict[str, Any] | None = None) -> List[TextChunk]:
        """切分文本

        Args:
            text: 待切分的文本
            metadata: 元数据

        Returns:
            List[TextChunk]: 切分后的文本块列表
        """
        if not text:
            return []

        metadata = metadata or {}

        # 预处理文本
        text = self._preprocess_text(text)

        # 执行切分
        chunks = self._split(text)

        # 添加元数据和ID
        chunks_with_metadata = []
        for idx, chunk in enumerate(chunks):
            chunk_metadata = {
                **metadata,
                "chunk_index": idx,
                "chunk_count": len(chunks)
            }
            chunks_with_metadata.append(
                TextChunk(
                    content=chunk,
                    chunk_id=self._generate_chunk_id(idx, metadata),
                    start_index=text.find(chunk),
                    end_index=text.find(chunk) + len(chunk),
                    metadata=chunk_metadata
                )
            )

        logger.debug(f"Split text into {len(chunks_with_metadata)} chunks")
        return chunks_with_metadata

    def _preprocess_text(self, text: str) -> str:
        """预处理文本

        Args:
            text: 原始文本

        Returns:
            str: 预处理后的文本
        """
        # 去除首尾空白
        text = text.strip()

        # 统一换行符
        text = re.sub(r'\r\n|\r', '\n', text)

        # 去除多余的空行
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text

    def _split(self, text: str) -> List[str]:
        """切分文本（子类实现）

        Args:
            text: 待切分的文本

        Returns:
            List[str]: 切分后的文本列表
        """
        raise NotImplementedError("Subclasses must implement _split method")

    def _generate_chunk_id(self, index: int, metadata: Dict[str, Any]) -> str:
        """生成分块ID

        Args:
            index: 分块索引
            metadata: 元数据

        Returns:
            str: 分块ID
        """
        doc_id = metadata.get("document_id", "unknown")
        return f"{doc_id}_chunk_{index}"


class CharacterSplitter(TextSplitter):
    """字符级切分器"""

    def _split(self, text: str) -> List[str]:
        """按字符切分文本

        Args:
            text: 待切分的文本

        Returns:
            List[str]: 切分后的文本列表
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk = text[start:end]
            chunks.append(chunk)
            start = end - self.chunk_overlap

        return chunks


class WordSplitter(TextSplitter):
    """单词级切分器"""

    def _split(self, text: str) -> List[str]:
        """按单词切分文本

        Args:
            text: 待切分的文本

        Returns:
            List[str]: 切分后的文本列表
        """
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0

        for word in words:
            word_length = len(word)
            if current_length + word_length + 1 <= self.chunk_size:
                current_chunk.append(word)
                current_length += word_length + 1
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    overlap_words = self._get_overlap_words(current_chunk)
                    current_chunk = overlap_words
                    current_length = sum(len(w) + 1 for w in current_chunk)
                current_chunk.append(word)
                current_length += word_length + 1

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks

    def _get_overlap_words(self, words: List[str]) -> List[str]:
        """获取重叠的单词

        Args:
            words: 单词列表

        Returns:
            List[str]: 重叠的单词列表
        """
        overlap_length = self.chunk_overlap
        overlap_words = []
        current_length = 0

        for word in reversed(words):
            word_length = len(word)
            if current_length + word_length + 1 <= overlap_length:
                overlap_words.insert(0, word)
                current_length += word_length + 1
            else:
                break

        return overlap_words


class SentenceSplitter(TextSplitter):
    """句子级切分器"""

    def _split(self, text: str) -> List[str]:
        """按句子切分文本

        Args:
            text: 待切分的文本

        Returns:
            List[str]: 切分后的文本列表
        """
        sentences = re.split(r'([。！？\n])', text)

        # 重新组合句子和标点
        chunks_text = []
        for i in range(0, len(sentences) - 1, 2):
            chunk = sentences[i] + sentences[i + 1]
            if chunk.strip():
                chunks_text.append(chunk)

        # 按字符大小切分
        chunks = []
        current_chunk = ""
        current_length = 0

        for sentence in chunks_text:
            sentence_length = len(sentence)
            if current_length + sentence_length <= self.chunk_size:
                current_chunk += sentence
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = self._get_overlap_text(current_chunk)
                    current_length = len(current_chunk)
                current_chunk += sentence
                current_length += sentence_length

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def _get_overlap_text(self, text: str) -> str:
        """获取重叠的文本

        Args:
            text: 文本

        Returns:
            str: 重叠的文本
        """
        overlap_length = self.chunk_overlap
        return text[-overlap_length:] if len(text) > overlap_length else text


class ParagraphSplitter(TextSplitter):
    """段落级切分器"""

    def _split(self, text: str) -> List[str]:
        """按段落切分文本

        Args:
            text: 待切分的文本

        Returns:
            List[str]: 切分后的文本列表
        """
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""
        current_length = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            paragraph_length = len(paragraph)
            if current_length + paragraph_length + 2 <= self.chunk_size:
                current_chunk += paragraph + "\n\n"
                current_length += paragraph_length + 2
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = self._get_overlap_text(current_chunk) + "\n\n"
                    current_length = len(current_chunk)
                current_chunk += paragraph + "\n\n"
                current_length += paragraph_length + 2

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def _get_overlap_text(self, text: str) -> str:
        """获取重叠的文本

        Args:
            text: 文本

        Returns:
            str: 重叠的文本
        """
        overlap_length = self.chunk_overlap
        return text[-overlap_length:] if len(text) > overlap_length else text


class SemanticSplitter(TextSplitter):
    """基于embedding相似度的语义级切分器

    使用句子embedding来确定语义边界。
    相似度高的句子会被分到同一组，而相似度低的句子会触发新的分块边界。
    """

    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
        separators: list[str] | None = None,
        similarity_threshold: float = 0.5,
        embedding_model: Any | None = None,
    ):
        super().__init__(chunk_size, chunk_overlap, separators)
        self.similarity_threshold = similarity_threshold
        self._embedding_model = embedding_model

    def _get_embedding_model(self) -> Any | None:
        """延迟加载或初始化embedding模型"""
        if self._embedding_model is None:
            try:
                from infras.embedding.bge_model import CachedBGEEmbeddingModel
                self._embedding_model = CachedBGEEmbeddingModel()
                logger.debug("SemanticSplitter已加载embedding模型")
            except Exception as e:
                logger.warning(f"加载embedding模型失败: {e}")
                return None
        return self._embedding_model

    def _split(self, text: str) -> list[str]:
        """基于语义相似度切分文本

        使用句子embedding来识别语义边界。
        当连续句子之间的相似度低于阈值时，开始新的分块。

        Args:
            text: 待切分的文本

        Returns:
            List[str]: 语义连贯的文本块列表
        """
        sentences = self._split_into_sentences(text)

        if not sentences:
            return []

        if len(sentences) == 1:
            return sentences

        model = self._get_embedding_model()

        if model is None:
            logger.warning("无法使用embedding模型，回退到基于长度的切分")
            return self._merge_by_length(sentences)

        chunks = self._merge_by_similarity(sentences, model)

        return chunks

    def _split_into_sentences(self, text: str) -> list[str]:
        """使用正则表达式将文本切分为句子"""
        sentences = re.split(r'([。！？\n]|\n\n)', text)
        merged_sentences = []
        current = ""

        for i, part in enumerate(sentences):
            if i % 2 == 0:
                current += part
            else:
                current += part
                if current.strip():
                    merged_sentences.append(current)
                current = ""

        if current.strip():
            merged_sentences.append(current)

        return [s.strip() for s in merged_sentences if s.strip()]

    def _merge_by_similarity(self, sentences: list[str], model: Any) -> list[str]:
        """基于embedding相似度合并句子为块"""
        embeddings = model.encode(sentences, normalize=True)
        chunks = []
        current_chunk = [sentences[0]]
        current_embedding = embeddings[0]

        for i in range(1, len(sentences)):
            sentence = sentences[i]
            embedding = embeddings[i]

            similarity = self._cosine_similarity(current_embedding, embedding)

            combined_text = "".join(current_chunk)
            if (similarity >= self.similarity_threshold and
                    len(combined_text) + len(sentence) <= self.chunk_size):
                current_chunk.append(sentence)
                current_embedding = self._average_embeddings(
                    [current_embedding, embedding],
                    [len(current_chunk) - 1, 1]
                )
            else:
                chunks.append("".join(current_chunk))
                current_chunk = [sentence]
                current_embedding = embedding

        if current_chunk:
            chunks.append("".join(current_chunk))

        return chunks

    def _merge_by_length(self, sentences: list[str]) -> list[str]:
        """回退方案：基于长度合并句子，不做语义分析"""
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length <= self.chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append("".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length

        if current_chunk:
            chunks.append("".join(current_chunk))

        return chunks

    def _cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """计算两个向量的余弦相似度"""
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(a * a for a in vec2) ** 0.5
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot / (norm1 * norm2)

    def _average_embeddings(
        self,
        embeddings: list[list[float]],
        weights: list[int]
    ) -> list[float]:
        """计算embedding的加权平均"""
        total_weight = sum(weights)
        if total_weight == 0:
            return embeddings[0]

        result = [0.0] * len(embeddings[0])
        for emb, weight in zip(embeddings, weights):
            for i, val in enumerate(emb):
                result[i] += val * weight / total_weight
        return result


def create_splitter(
    strategy: SplitStrategy = SplitStrategy.PARAGRAPH,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    separators: List[str] | None = None
) -> TextSplitter:
    """创建文本切分器

    Args:
        strategy: 切分策略
        chunk_size: 分块大小
        chunk_overlap: 分块重叠
        separators: 分隔符列表

    Returns:
        TextSplitter: 文本切分器实例
    """
    splitters = {
        SplitStrategy.CHARACTER: CharacterSplitter,
        SplitStrategy.WORD: WordSplitter,
        SplitStrategy.SENTENCE: SentenceSplitter,
        SplitStrategy.PARAGRAPH: ParagraphSplitter,
        SplitStrategy.SEMANTIC: SemanticSplitter,
    }

    splitter_class = splitters.get(strategy, ParagraphSplitter)
    return splitter_class(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=separators)