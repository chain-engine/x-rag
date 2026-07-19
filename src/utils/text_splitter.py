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
    """语义级切分器（基于句子）"""

    def _split(self, text: str) -> List[str]:
        """按语义切分文本

        Args:
            text: 待切分的文本

        Returns:
            List[str]: 切分后的文本列表
        """
        # 先按句子切分
        sentence_splitter = SentenceSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=0
        )
        sentences = sentence_splitter._split(text)

        # 合并句子形成语义块
        chunks = []
        current_chunk = ""
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length <= self.chunk_size:
                current_chunk += sentence
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                    current_length = 0
                current_chunk += sentence
                current_length += sentence_length

        if current_chunk:
            chunks.append(current_chunk)

        return chunks


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