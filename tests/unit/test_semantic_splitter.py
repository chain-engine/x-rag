# -*- coding: utf-8 -*-
"""
Semantic Splitter Tests
"""

import pytest
from src.utils.text_splitter import SemanticSplitter, SplitStrategy, create_splitter


class TestSemanticSplitter:
    """Test SemanticSplitter functionality"""

    def test_create_semantic_splitter(self):
        """Test creating semantic splitter via factory"""
        splitter = create_splitter(
            strategy=SplitStrategy.SEMANTIC,
            chunk_size=100,
            similarity_threshold=0.5
        )
        assert isinstance(splitter, SemanticSplitter)
        assert splitter.chunk_size == 100
        assert splitter.similarity_threshold == 0.5

    def test_empty_text(self):
        """Test splitting empty text"""
        splitter = SemanticSplitter(chunk_size=100)
        chunks = splitter._split("")
        assert chunks == []

    def test_single_sentence(self):
        """Test splitting single sentence"""
        splitter = SemanticSplitter(chunk_size=100)
        text = "This is a single sentence."
        chunks = splitter._split(text)
        assert len(chunks) >= 1

    def test_multiple_sentences(self):
        """Test splitting multiple sentences"""
        splitter = SemanticSplitter(chunk_size=50, similarity_threshold=0.3)
        text = "First sentence here. Second sentence here. Third sentence here."
        chunks = splitter._split(text)
        assert len(chunks) >= 1

    def test_sentence_splitting(self):
        """Test basic sentence splitting"""
        splitter = SemanticSplitter(chunk_size=100)
        sentences = splitter._split_into_sentences("Hello. World! How are you?")
        assert len(sentences) >= 3

    def test_cosine_similarity(self):
        """Test cosine similarity calculation"""
        splitter = SemanticSplitter(chunk_size=100)
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = splitter._cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0)

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity for orthogonal vectors"""
        splitter = SemanticSplitter(chunk_size=100)
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = splitter._cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(0.0)

    def test_average_embeddings(self):
        """Test weighted embedding average"""
        splitter = SemanticSplitter(chunk_size=100)
        embeddings = [[1.0, 0.0], [0.0, 1.0]]
        weights = [1, 1]
        avg = splitter._average_embeddings(embeddings, weights)
        assert len(avg) == 2
        assert avg[0] == pytest.approx(0.5)
        assert avg[1] == pytest.approx(0.5)

    def test_chunk_size_limit(self):
        """Test that chunks respect size limit"""
        splitter = SemanticSplitter(chunk_size=20, similarity_threshold=0.1)
        text = "Short sentence one. This is a much longer sentence that should definitely exceed the chunk size limit."
        chunks = splitter._split(text)
        for chunk in chunks:
            assert len(chunk) <= 20

    def test_chinese_text(self):
        """Test splitting Chinese text"""
        splitter = SemanticSplitter(chunk_size=50)
        text = "这是第一句。这是第二句。这是第三句。"
        chunks = splitter._split(text)
        assert len(chunks) >= 1
