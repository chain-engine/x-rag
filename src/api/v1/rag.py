#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG API Module

RAG查询接口 - 仅负责参数接收、调用业务服务、标准化返回
"""

from typing import Any
from fastapi import APIRouter, HTTPException, Depends, Request

from schemas.rag import (
    RAGQueryRequest,
    RetrievalRequest,
    EmbeddingRequest,
    RetrievedDocument,
)
from schemas.responses import ResponseModel
from core.logger import logger
from core.exceptions import RetrievalError, GenerationError
from services.rag_service import RAGService

router = APIRouter()


def get_rag_service(request: Request) -> RAGService:
    """依赖注入：获取RAG服务"""
    return request.app.state.rag_service


@router.post(
    "/rag/query",
    summary="RAG查询",
    description="使用RAG进行问答，检索相关文档并生成答案",
    tags=["RAG"],
    response_model=ResponseModel,
)
async def rag_query(
    request: RAGQueryRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> dict[str, Any]:
    """RAG查询接口"""
    try:
        result = await rag_service.query(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            use_mmr=request.use_mmr,
            mmr_lambda=request.mmr_lambda,
            metadata_filter=request.metadata_filter,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return ResponseModel(data=result).model_dump()

    except (RetrievalError, GenerationError) as e:
        logger.exception("RAG service error")
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        logger.exception("RAG query error")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post(
    "/rag/retrieve",
    summary="文本检索",
    description="通过文本检索相关文档，不进行生成",
    tags=["RAG"],
    response_model=ResponseModel,
)
async def retrieve_docs(
    request: RetrievalRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> dict[str, Any]:
    """文本检索接口"""
    try:
        documents = rag_service.retrieve(
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

        data = {
            "query": request.query,
            "documents": [doc.model_dump() for doc in retrieved_docs],
            "total": len(retrieved_docs),
        }
        return ResponseModel(data=data).model_dump()

    except RetrievalError as e:
        logger.exception("Retrieval error")
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        logger.exception("Retrieve error")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.post(
    "/rag/embed",
    summary="文本向量化",
    description="将文本转换为向量表示",
    tags=["RAG"],
    response_model=ResponseModel,
)
async def embed_text(
    request: EmbeddingRequest,
    rag_service: RAGService = Depends(get_rag_service),
) -> dict[str, Any]:
    """文本向量化接口"""
    try:
        embeddings = rag_service.encode(
            texts=request.texts,
            normalize=request.normalize,
        )
        stats = rag_service.get_embedding_stats()

        data = {
            "embeddings": embeddings,
            "dimension": stats.get("dimension"),
            "model": stats.get("model"),
        }
        return ResponseModel(data=data).model_dump()

    except Exception as e:
        logger.error(f"Embed error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/rag/stats",
    summary="RAG统计",
    description="获取RAG系统统计信息",
    tags=["RAG"],
    response_model=ResponseModel,
)
async def get_rag_stats(
    rag_service: RAGService = Depends(get_rag_service),
) -> dict[str, Any]:
    """获取RAG统计信息"""
    try:
        stats = rag_service.get_stats()
        vector_count = stats.get("vector_count", 0)

        data = {
            "vector_count": vector_count,
            "status": "running",
        }
        return ResponseModel(data=data).model_dump()

    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
