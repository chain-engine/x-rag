# -*- coding: utf-8 -*-
"""
LangChain Chunking Provider

基于 LangChain 的文档切分实现。
"""

from typing import Any, Optional

from chunking.base import BaseChunkingProvider, TextChunk
from core.logger import logger


class LangchainProvider(BaseChunkingProvider):
    """
    LangChain 文档切分提供者

    支持以下切分器：
    - recursive: RecursiveCharacterTextSplitter（默认）
    - character: CharacterTextSplitter
    - token: TokenTextSplitter
    - semantic: SemanticChunker（需要 embedding 模型）
    """

    name = "langchain"
    description = "LangChain 文档切分提供者（支持 recursive/character/token/semantic）"

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: list[str] | None = None,
        strategy: str = "recursive",
        **kwargs,
    ):
        """
        初始化 LangChain 切分提供者

        Args:
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
            separators: 分隔符列表
            strategy: 切分策略（recursive, character, token, semantic）
            **kwargs: 额外参数
        """
        super().__init__(chunk_size, chunk_overlap, separators, **kwargs)
        self.strategy = strategy
        self._splitter: Optional[Any] = None

    def _get_splitter(self) -> Any:
        """获取或创建切分器实例（懒加载）"""
        if self._splitter is not None:
            return self._splitter

        if self.strategy == "recursive":
            from langchain_text_splitters import RecursiveCharacterTextSplitter
            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=self.separators,
            )
        elif self.strategy == "character":
            from langchain_text_splitters import CharacterTextSplitter
            self._splitter = CharacterTextSplitter(
                separator="\n",
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        elif self.strategy == "token":
            from langchain_text_splitters import TokenTextSplitter
            self._splitter = TokenTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        elif self.strategy == "semantic":
            from langchain_text_splitters import SemanticChunker
            from langchain_community.embeddings import HuggingFaceEmbeddings

            embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={"device": "cpu"},
                encode_kwargs={"normalize_embeddings": True},
            )
            self._splitter = SemanticChunker(
                embeddings=embeddings,
                breakpoint_threshold_type="percentile",
            )
        else:
            raise ValueError(f"不支持的切分策略: {self.strategy}")

        logger.info(f"创建 LangChain 切分器: strategy={self.strategy}, chunk_size={self.chunk_size}")
        return self._splitter

    def chunk_text(self, text: str, **kwargs) -> list[str]:
        """
        切分文本为字符串列表

        Args:
            text: 待切分的文本
            **kwargs: 额外参数

        Returns:
            切分后的文本块列表
        """
        if not text or not text.strip():
            return []

        splitter = self._get_splitter()
        chunks = splitter.split_text(text)
        logger.debug(f"LangChain 切分完成: {len(chunks)} 个文本块")
        return chunks

    def chunk_documents(self, documents: list, **kwargs) -> list:
        """
        切分 Document 对象列表

        Args:
            documents: LangChain Document 对象列表
            **kwargs: 额外参数

        Returns:
            切分后的 Document 对象列表
        """
        if not documents:
            return []

        splitter = self._get_splitter()

        from langchain.docstore.document import Document as LCDocument

        # 确保输入是 LangChain Document 格式
        lc_documents = []
        for doc in documents:
            if isinstance(doc, LCDocument):
                lc_documents.append(doc)
            elif isinstance(doc, dict):
                lc_documents.append(LCDocument(page_content=doc.get("content", ""), metadata=doc.get("metadata", {})))
            elif isinstance(doc, str):
                lc_documents.append(LCDocument(page_content=doc))
            else:
                lc_documents.append(LCDocument(page_content=str(doc)))

        result = splitter.split_documents(lc_documents)
        logger.debug(f"LangChain Document 切分完成: {len(result)} 个文档块")
        return result

    def get_config(self) -> dict[str, Any]:
        """获取当前配置"""
        return {
            **super().get_config(),
            "strategy": self.strategy,
        }
