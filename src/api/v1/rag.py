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
from core.dependencies import get_retrieval_service, get_augmentation_service, get_generation_service
from services.retrieval_service import RetrievalService
from services.augmentation_service import AugmentationService
from services.generation_service import GenerationService
from infras.embedding.bge_model import CachedBGEEmbeddingModel
from constants.common import HTTP_OK, MSG_SUCCESS

router = APIRouter()


@router.post(
    "/rag/query",
    summary="RAG查询",
    description="使用RAG进行问答，检索相关文档并生成答案",
    tags=["RAG"],
)
async def rag_query(
    request: RAGQueryRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    augmentation_service: AugmentationService = Depends(get_augmentation_service),
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

        # 增强：构建带有上下文的prompt
        augmented = augmentation_service.augment(
            query=request.query,
            retrieved_docs=retrieved_docs,
        )

        # 生成答案
        provider = request.provider or generation_service._default_provider
        generation_result = await generation_service.generate(
            prompt=augmented["full_prompt"],
            provider=provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        # 构建响应
        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "query": request.query,
                "answer": generation_result["text"],
                "retrieved_docs": [
                    RetrievedDocument(
                        chunk_id=doc["id"],
                        document_id=doc["metadata"].get("document_id", ""),
                        text=doc["text"],
                        score=doc["score"],
                        metadata=doc["metadata"],
                    ).model_dump()
                    for doc in retrieved_docs
                ],
                "provider": generation_result["provider"],
                "model": generation_result["model"],
                "tokens_used": generation_result["tokens_used"],
            },
        }

    except RetrievalError as e:
        logger.exception("Retrieval error")
        raise HTTPException(status_code=500, detail=str(e)) from e
    except GenerationError as e:
        logger.exception("Generation error")
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        logger.exception("RAG query error")
        raise HTTPException(status_code=500, detail="Internal server error") from e


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
