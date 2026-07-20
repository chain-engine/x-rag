#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Check API Module

健康检查和系统状态接口
"""

from datetime import datetime
from typing import Annotated, Any
from fastapi import APIRouter, Depends

from schemas.health import HealthCheckResponse, VersionResponse, StatusResponse
from core.logger import logger
from core.dependencies import get_indexing_service, get_retrieval_service
from services.indexing_service import IndexingService
from services.retrieval_service import RetrievalService

router = APIRouter()

_start_time = datetime.utcnow()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="健康检查",
    description="检查系统健康状态",
    tags=["系统"],
)
async def health_check(
    indexing_service: Annotated[IndexingService, Depends(get_indexing_service)],
    retrieval_service: Annotated[RetrievalService, Depends(get_retrieval_service)],
) -> dict[str, Any]:
    """健康检查接口"""
    checks = {}

    # 检查向量存储
    try:
        vector_count = retrieval_service.get_vector_count()
        checks["vector_store"] = "healthy"
        checks["vector_count"] = vector_count
    except Exception as e:
        checks["vector_store"] = f"unhealthy: {str(e)}"

    # 检查文档存储
    try:
        doc_stats = indexing_service.get_stats()
        checks["document_store"] = "healthy"
        checks["document_count"] = doc_stats.get("document_stats", {}).get("document_count", 0)
    except Exception as e:
        checks["document_store"] = f"unhealthy: {str(e)}"

    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow(),
        "checks": checks,
    }


@router.get(
    "/version",
    response_model=VersionResponse,
    summary="版本信息",
    description="获取系统版本信息",
    tags=["系统"],
)
async def get_version() -> dict[str, Any]:
    """版本信息接口"""
    return {
        "version": "1.0.0",
        "name": "x-rag",
        "description": "A production-ready RAG learning and training project",
        "python_version": "3.11",
    }


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="系统状态",
    description="获取系统运行状态",
    tags=["系统"],
)
async def get_status(
    indexing_service: Annotated[IndexingService, Depends(get_indexing_service)],
    retrieval_service: Annotated[RetrievalService, Depends(get_retrieval_service)],
) -> dict[str, Any]:
    """系统状态接口"""
    uptime = (datetime.utcnow() - _start_time).total_seconds()
    vector_count = 0
    document_count = 0

    try:
        vector_count = retrieval_service.get_vector_count()
    except Exception as e:
        logger.warning(f"Failed to get vector count: {e}")

    try:
        doc_stats = indexing_service.get_stats()
        document_count = doc_stats.get("document_stats", {}).get("document_count", 0)
    except Exception as e:
        logger.warning(f"Failed to get document count: {e}")

    return {
        "status": "running",
        "uptime": uptime,
        "memory_usage": {},
        "vector_count": vector_count,
        "document_count": document_count,
    }
