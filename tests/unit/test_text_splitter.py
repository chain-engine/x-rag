#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文本切分器单元测试
"""

import pytest
from utils.text_splitter import (
    TextSplitter,
    CharacterSplitter,
    WordSplitter,
    SentenceSplitter,
    ParagraphSplitter,
    SplitStrategy
)


class TestCharacterSplitter:
    """字符级切分器测试"""

    def test_basic_split(self):
        """测试基本切分"""
        splitter = CharacterSplitter(chunk_size=20, chunk_overlap=5)
        text = "这是一个测试文本，用于测试字符级切分功能。"

        chunks = splitter.split_text(text)

        assert len(chunks) > 1
        assert all(len(chunk.content) <= 20 for chunk in chunks)

    def test_empty_text(self):
        """测试空文本"""
        splitter = CharacterSplitter(chunk_size=20, chunk_overlap=5)
        chunks = splitter.split_text("")

        assert len(chunks) == 0

    def test_single_chunk(self):
        """测试单个分块"""
        splitter = CharacterSplitter(chunk_size=100, chunk_overlap=0)
        text = "短文本"

        chunks = splitter.split_text(text)

        assert len(chunks) == 1
        assert chunks[0].content == text


class TestWordSplitter:
    """单词级切分器测试"""

    def test_basic_split(self):
        """测试基本切分"""
        splitter = WordSplitter(chunk_size=10, chunk_overlap=2)
        text = "This is a test text for word splitter testing."

        chunks = splitter.split_text(text)

        assert len(chunks) > 0
        assert all(" " in chunk.content or len(chunk.content) < 10 for chunk in chunks)

    def test_chinese_text(self):
        """测试中文文本"""
        splitter = WordSplitter(chunk_size=10, chunk_overlap=2)
        text = "这是一个测试文本用于测试中文切分"

        chunks = splitter.split_text(text)

        assert len(chunks) > 0


class TestSentenceSplitter:
    """句子级切分器测试"""

    def test_basic_split(self):
        """测试基本切分"""
        splitter = SentenceSplitter(chunk_size=30, chunk_overlap=5)
        text = "这是第一句话。这是第二句话。这是第三句话。"

        chunks = splitter.split_text(text)

        assert len(chunks) > 0

    def test_with_newline(self):
        """测试包含换行符的文本"""
        splitter = SentenceSplitter(chunk_size=30, chunk_overlap=5)
        text = "这是第一句话。\n这是第二句话。\n这是第三句话。"

        chunks = splitter.split_text(text)

        assert len(chunks) > 0


class TestParagraphSplitter:
    """段落级切分器测试"""

    def test_basic_split(self):
        """测试基本切分"""
        splitter = ParagraphSplitter(chunk_size=50, chunk_overlap=10)
        text = "这是第一段。\n\n这是第二段。\n\n这是第三段。"

        chunks = splitter.split_text(text)

        assert len(chunks) >= 1

    def test_single_paragraph(self):
        """测试单段文本"""
        splitter = ParagraphSplitter(chunk_size=100, chunk_overlap=0)
        text = "这是唯一的段落。"

        chunks = splitter.split_text(text)

        assert len(chunks) == 1


class TestTextChunk:
    """文本分块测试"""

    def test_chunk_metadata(self):
        """测试分块元数据"""
        splitter = CharacterSplitter(chunk_size=20, chunk_overlap=0)
        text = "测试文本"
        metadata = {"document_id": "doc1", "source": "test"}

        chunks = splitter.split_text(text, metadata)

        assert len(chunks) == 1
        assert chunks[0].metadata["document_id"] == "doc1"
        assert chunks[0].metadata["source"] == "test"
        assert "chunk_index" in chunks[0].metadata
        assert "chunk_count" in chunks[0].metadata

    def test_chunk_id_generation(self):
        """测试分块ID生成"""
        splitter = CharacterSplitter(chunk_size=10, chunk_overlap=0)
        text = "很长的测试文本用于测试分块ID生成"
        metadata = {"document_id": "doc123"}

        chunks = splitter.split_text(text, metadata)

        assert len(chunks) > 1
        for idx, chunk in enumerate(chunks):
            assert f"doc123_chunk_{idx}" == chunk.chunk_id


class TestCreateSplitter:
    """创建切分器测试"""

    def test_create_character_splitter(self):
        """测试创建字符切分器"""
        splitter = create_splitter(SplitStrategy.CHARACTER, chunk_size=20)
        assert isinstance(splitter, CharacterSplitter)

    def test_create_word_splitter(self):
        """测试创建单词切分器"""
        splitter = create_splitter(SplitStrategy.WORD, chunk_size=20)
        assert isinstance(splitter, WordSplitter)

    def test_create_sentence_splitter(self):
        """测试创建句子切分器"""
        splitter = create_splitter(SplitStrategy.SENTENCE, chunk_size=20)
        assert isinstance(splitter, SentenceSplitter)

    def test_create_paragraph_splitter(self):
        """测试创建段落切分器"""
        splitter = create_splitter(SplitStrategy.PARAGRAPH, chunk_size=20)
        assert isinstance(splitter, ParagraphSplitter)