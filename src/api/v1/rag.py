#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG接口
实现RAG查询接口，支持检索增强生成
"""

from typing import Optional, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends

from common.schemas import (
    RAGQueryRequest,
    RetrievedDocument,
    EmbeddingRequest,
    RetrievalRequest
)
from common.constants import HTTP_OK, MSG_SUCCESS, HTTP_NOT_FOUND
from core.exceptions import RetrievalError, GenerationError, ConfigurationError
from core.logger import logger
from service.retrieval_service import RetrievalService
from service.generation_service import GenerationService


router = APIRouter()


# 服务依赖
_services: dict = {}


def set_services(
    retrieval_service: RetrievalService,
    generation_service: GenerationService
) -> None:
    """设置服务实例"""
    _services["retrieval"] = retrieval_service
    _services["generation"] = generation_service


def get_retrieval_service() -> RetrievalService:
    """获取检索服务"""
    if "retrieval" not in _services:
        raise RuntimeError("RetrievalService not initialized")
    return _services["retrieval"]


def get_generation_service() -> GenerationService:
    """获取生成服务"""
    if "generation" not in _services:
        raise RuntimeError("GenerationService not initialized")
    return _services["generation"]


@router.post(
    "/rag/query",
    response_model=dict[str, Any],
    summary="RAG查询",
    description="使用RAG进行问答，检索相关文档并生成答案",
    tags=["RAG"]
)
async def rag_query(
    request: RAGQueryRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    generation_service: GenerationService = Depends(get_generation_service)
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
            metadata_filter=request.metadata_filter
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
                    "tokens_used": None
                }
            }

        # 提取上下文
        context = [doc["text"] for doc in retrieved_docs]

        # 生成答案
        provider = request.provider or generation_service.default_provider.value
        generation_result = await generation_service.generate(
            prompt=request.query,
            context=context,
            provider=provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # 构建响应
        retrieved_docs_response = [
            RetrievedDocument(
                chunk_id=doc["id"],
                document_id=doc["metadata"].get("document_id", ""),
                text=doc["text"],
                score=doc["score"],
                metadata=doc["metadata"]
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
                "tokens_used": generation_result["tokens_used"]
            }
        }

    except RetrievalError as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except GenerationError as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except ConfigurationError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"RAG query error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/rag/retrieve",
    response_model=dict[str, Any],
    summary="文档检索",
    description="检索相关文档，不进行生成",
    tags=["RAG"]
)
async def retrieve_docs(
    request: RetrievalRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
) -> dict[str, Any]:
    """文档检索接口"""
    try:

        # 检索相关文档
        documents = retrieval_service.retrieve(
            query=request.query,
            top_k=request.top_k,
            similarity_threshold=request.similarity_threshold,
            use_mmr=request.use_mmr,
            mmr_lambda=request.mmr_lambda,
            metadata_filter=request.metadata_filter
        )

        retrieved_docs = [
            RetrievedDocument(
                chunk_id=doc["id"],
                document_id=doc["metadata"].get("document_id", ""),
                text=doc["text"],
                score=doc["score"],
                metadata=doc["metadata"]
            )
            for doc in documents
        ]

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "query": request.query,
                "documents": [doc.model_dump() for doc in retrieved_docs],
                "total": len(retrieved_docs)
            }
        }

    except RetrievalError as e:
        logger.error(f"Retrieval error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Retrieve error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post(
    "/rag/embed",
    response_model=dict[str, Any],
    summary="文本向量化",
    description="将文本转换为向量表示",
    tags=["RAG"]
)
async def embed_text(request: EmbeddingRequest) -> dict[str, Any]:
    """文本向量化接口"""
    try:
        from utils.embedding import encode_texts, get_embedding_model

        # 获取嵌入模型实例（单例模式）
        model = get_embedding_model(cached=True)

        # 编码文本列表为向量
        embeddings = encode_texts(
            texts=request.texts,
            normalize=request.normalize,
            cached=True
        )

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "embeddings": embeddings,
                "dimension": model.dimension,
                "model": model.model_name
            }
        }

    except Exception as e:
        logger.error(f"Embed error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/rag/stats",
    summary="RAG统计",
    description="获取RAG系统统计信息",
    tags=["RAG"]
)
async def get_rag_stats(
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
) -> dict[str, Any]:
    """获取RAG统计信息"""
    try:
        vector_count = retrieval_service.get_vector_count()

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "vector_count": vector_count,
                "status": "running"
            }
        }

    except Exception as e:
        logger.error(f"Get stats error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")