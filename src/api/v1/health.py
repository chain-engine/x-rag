#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Health Check API Module

健康检查和系统状态接口
"""

from datetime import datetime
from typing import Any
from fastapi import APIRouter, Request

from schemas.health import HealthCheckResponse, VersionResponse, StatusResponse
from core.logger import logger
from constants.common import HTTP_OK

router = APIRouter()

# 全局服务实例（通过lifespan注入）
_indexing_service = None
_retrieval_service = None
_start_time = datetime.utcnow()


def set_services(indexing_service=None, retrieval_service=None) -> None:
    """设置服务实例"""
    global _indexing_service, _retrieval_service
    if indexing_service:
        _indexing_service = indexing_service
    if retrieval_service:
        _retrieval_service = retrieval_service


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="健康检查",
    description="检查系统健康状态",
    tags=["系统"],
)
async def health_check() -> dict[str, Any]:
    """健康检查接口"""
    checks = {}

    # 检查向量存储
    if _retrieval_service:
        try:
            vector_count = _retrieval_service.get_vector_count()
            checks["vector_store"] = "healthy"
            checks["vector_count"] = vector_count
        except Exception as e:
            checks["vector_store"] = f"unhealthy: {str(e)}"
    else:
        checks["vector_store"] = "not_initialized"

    # 检查文档存储
    if _indexing_service:
        try:
            doc_stats = _indexing_service.get_stats()
            checks["document_store"] = "healthy"
            checks["document_count"] = len(doc_stats.get("document_stats", {}).get("document_count", 0))
        except Exception as e:
            checks["document_store"] = f"unhealthy: {str(e)}"
    else:
        checks["document_store"] = "not_initialized"

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
async def get_status() -> dict[str, Any]:
    """系统状态接口"""
    global _start_time

    uptime = (datetime.utcnow() - _start_time).total_seconds()
    vector_count = 0
    document_count = 0

    if _retrieval_service:
        try:
            vector_count = _retrieval_service.get_vector_count()
        except Exception as e:
            logger.warning(f"Failed to get vector count: {e}")

    if _indexing_service:
        try:
            doc_stats = _indexing_service.get_stats()
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
