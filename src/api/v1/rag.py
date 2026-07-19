#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG API Module

RAG查询接口
"""

from typing import Any
from fastapi import APIRouter, HTTPException, Depends

from schemas.rag import (
    RAGQueryRequest,
    RetrievalRequest,
    EmbeddingRequest,
    RetrievedDocument,
)
from core.logger import logger
from core.exceptions import RetrievalError, GenerationError, ConfigurationError
from service.retrieval_service import RetrievalService
from service.generation_service import GenerationService
from infras.embedding.bge_model import CachedBGEEmbeddingModel
from constants.common import HTTP_OK, MSG_SUCCESS

router = APIRouter()

# 全局服务实例（通过lifespan注入）
_retrieval_service: RetrievalService | None = None
_generation_service: GenerationService | None = None


def set_services(retrieval_service: RetrievalService, generation_service: GenerationService) -> None:
    """设置服务实例"""
    global _retrieval_service, _generation_service
    _retrieval_service = retrieval_service
    _generation_service = generation_service


def get_retrieval_service() -> RetrievalService:
    """获取检索服务"""
    if _retrieval_service is None:
        raise RuntimeError("RetrievalService not initialized")
    return _retrieval_service


def get_generation_service() -> GenerationService:
    """获取生成服务"""
    if _generation_service is None:
        raise RuntimeError("GenerationService not initialized")
    return _generation_service


@router.post(
    "/rag/query",
    summary="RAG查询",
    description="使用RAG进行问答，检索相关文档并生成答案",
    tags=["RAG"],
)
async def rag_query(
    request: RAGQueryRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    generation_service: GenerationService = Depends(get_generation_service),
) -> dict[str, Any]:
    """RAG查询接口"""
    try:
        # 检索相关文档
        retrieved_docs = retrieval_service.retrieve(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            use_mmr=request.use_mmr,
            mmr_lambda=request.mmr_lambda,
            metadata_filter=request.metadata_filter,
        )

        if not retrieved_docs:
            logger.warning(f"No documents retrieved for query: {request.query[:50]}...")
            return {
                "code": HTTP_OK,
                "message": MSG_SUCCESS,
                "data": {
                    "query": request.query,
                    "answer": "抱歉，没有找到相关文档内容。",
                    "retrieved_docs": [],
                    "provider": "none",
                    "model": "none",
                    "tokens_used": None,
                },
            }

        # 提取上下文
        context = [doc["text"] for doc in retrieved_docs]

        # 生成答案
        provider = request.provider or generation_service._default_provider
        generation_result = await generation_service.generate(
            prompt=request.query,
            context=context,
            provider=provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # 构建响应
        retrieved_docs_response = [
            RetrievedDocument(
                chunk_id=doc["id"],
                document_id=doc["metadata"].get("document_id", ""),
                text=doc["text"],
                score=doc["score"],
                metadata=doc["metadata"],
            )
            for doc in retrieved_docs
        ]

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "query": request.query,
                "answer": generation_result["text"],
                "retrieved_docs": [doc.model_dump() for doc in retrieved_docs_response],
                "provider": generation_result["provider"],
                "model": generation_result["model"],
                "tokens_used": generation_result["tokens_used"],
            },
        }

    except RetrievalError as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except GenerationError as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/rag/retrieve",
    summary="文档检索",
    description="检索相关文档，不进行生成",
    tags=["RAG"],
)
async def retrieve_docs(
    request: RetrievalRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> dict[str, Any]:
    """文档检索接口"""
    try:
        documents = retrieval_service.retrieve(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            use_mmr=request.use_mmr,
            mmr_lambda=request.mmr_lambda,
            metadata_filter=request.metadata_filter,
        )

        retrieved_docs = [
            RetrievedDocument(
                chunk_id=doc["id"],
                document_id=doc["metadata"].get("document_id", ""),
                text=doc["text"],
                score=doc["score"],
                metadata=doc["metadata"],
            )
            for doc in documents
        ]

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "query": request.query,
                "documents": [doc.model_dump() for doc in retrieved_docs],
                "total": len(retrieved_docs),
            },
        }

    except RetrievalError as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Retrieve error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/rag/embed",
    summary="文本向量化",
    description="将文本转换为向量表示",
    tags=["RAG"],
)
async def embed_text(request: EmbeddingRequest) -> dict[str, Any]:
    """文本向量化接口"""
    try:
        embedding_model = CachedBGEEmbeddingModel()
        embeddings = embedding_model.encode(request.texts, normalize=request.normalize)

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "embeddings": embeddings,
                "dimension": embedding_model.dimension,
                "model": embedding_model.model_name,
            },
        }

    except Exception as e:
        logger.error(f"Embed error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/rag/stats",
    summary="RAG统计",
    description="获取RAG系统统计信息",
    tags=["RAG"],
)
async def get_rag_stats(
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
) -> dict[str, Any]:
    """获取RAG统计信息"""
    try:
        vector_count = retrieval_service.get_vector_count()

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "vector_count": vector_count,
                "status": "running",
            },
        }

    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
