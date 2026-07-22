# -*- coding: utf-8 -*-
"""
LlamaIndex Chunking Provider

基于 LlamaIndex 的文档切分实现。
"""

from typing import Any, Optional

from chunking.base import BaseChunkingProvider, TextChunk
from core.logger import logger


class LlamaIndexProvider(BaseChunkingProvider):
    """
    LlamaIndex 文档切分提供者

    支持以下切分器：
    - sentence: SentenceSplitter（默认）
    - token: TokenTextSplitter
    - semantic: SemanticSplitterNodeParser（需要 embedding 模型）
    - markdown: MarkdownNodeParser
    """

    name = "llamaindex"
    description = "LlamaIndex 文档切分提供者（支持 sentence/token/semantic/markdown）"

    def __init__(
        self,
        chunk_size: int = 512,
        chunk_overlap: int = 50,
        separators: list[str] | None = None,
        strategy: str = "sentence",
        **kwargs,
    ):
        """
        初始化 LlamaIndex 切分提供者

        Args:
            chunk_size: 分块大小
            chunk_overlap: 分块重叠
            separators: 分隔符列表
            strategy: 切分策略（sentence, token, semantic, markdown）
            **kwargs: 额外参数
        """
        super().__init__(chunk_size, chunk_overlap, separators, **kwargs)
        self.strategy = strategy
        self._splitter: Optional[Any] = None

    def _get_splitter(self) -> Any:
        """获取或创建切分器实例（懒加载）"""
        if self._splitter is not None:
            return self._splitter

        if self.strategy == "sentence":
            from llama_index.core.node_parser import SentenceSplitter
            self._splitter = SentenceSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separator=self.separators[0] if self.separators else "\n\n",
            )
        elif self.strategy == "token":
            from llama_index.core.node_parser import TokenTextSplitter
            self._splitter = TokenTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        elif self.strategy == "semantic":
            from llama_index.core.node_parser import SemanticSplitterNodeParser
            from llama_index.core.embeddings import MockEmbedding

            # 使用 MockEmbedding 作为默认值，如需真实语义切分请传入自定义 embeddings
            embeddings = kwargs.get("embeddings") or MockEmbedding(embed_dim=384)
            self._splitter = SemanticSplitterNodeParser(
                embed_model=embeddings,
                buffer_size=1,
                breakpoint_threshold_type="percentile",
            )
        elif self.strategy == "markdown":
            from llama_index.core.node_parser import MarkdownNodeParser
            self._splitter = MarkdownNodeParser()
        else:
            raise ValueError(f"不支持的切分策略: {self.strategy}")

        logger.info(f"创建 LlamaIndex 切分器: strategy={self.strategy}, chunk_size={self.chunk_size}")
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

        from llama_index.core import Document as LIDocument

        splitter = self._get_splitter()
        doc = LIDocument(text=text)
        nodes = splitter.get_nodes_from_documents([doc])
        chunks = [node.get_content() for node in nodes]
        logger.debug(f"LlamaIndex 切分完成: {len(chunks)} 个文本块")
        return chunks

    def chunk_documents(self, documents: list, **kwargs) -> list:
        """
        切分 Document 对象列表

        Args:
            documents: LlamaIndex Document 对象列表
            **kwargs: 额外参数

        Returns:
            切分后的 Node 对象列表
        """
        if not documents:
            return []

        from llama_index.core import Document as LIDocument

        splitter = self._get_splitter()

        # 确保输入是 LlamaIndex Document 格式
        li_documents = []
        for doc in documents:
            if hasattr(doc, "text"):
                li_documents.append(doc)
            elif isinstance(doc, dict):
                li_documents.append(LIDocument(text=doc.get("content", ""), metadata=doc.get("metadata", {})))
            elif isinstance(doc, str):
                li_documents.append(LIDocument(text=doc))
            else:
                li_documents.append(LIDocument(text=str(doc)))

        nodes = splitter.get_nodes_from_documents(li_documents)
        logger.debug(f"LlamaIndex Document 切分完成: {len(nodes)} 个节点")
        return nodes

    def get_config(self) -> dict[str, Any]:
        """获取当前配置"""
        return {
            **super().get_config(),
            "strategy": self.strategy,
        }
