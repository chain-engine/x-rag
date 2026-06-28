#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
健康检查接口
提供服务健康状态检查和版本信息
"""

from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from common.schemas import HealthCheckResponse
from common.constants import HTTP_OK, MSG_SUCCESS

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="健康检查",
    description="检查服务健康状态",
    tags=["系统"]
)
async def health_check() -> HealthCheckResponse:
    """健康检查接口

    Returns:
        HealthCheckResponse: 健康检查响应
    """
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )


@router.get(
    "/version",
    summary="版本信息",
    description="获取服务版本信息",
    tags=["系统"]
)
async def get_version() -> dict[str, Any]:
    """获取版本信息

    Returns:
        dict[str, str]: 版本信息
    """
    return {
        "code": HTTP_OK,
        "message": MSG_SUCCESS,
        "data": {
            "version": "1.0.0",
            "name": "x-rag",
            "description": "A production-ready RAG learning and training project"
        }
    }


@router.get(
    "/status",
    summary="服务状态",
    description="获取详细的服务状态信息",
    tags=["系统"]
)
async def get_status() -> dict[str, Any]:
    """获取服务状态

    Returns:
        dict[str, Any]: 服务状态
    """
    # TODO: 添加更多状态检查（数据库连接、向量存储等）
    status = {
        "code": HTTP_OK,
        "message": MSG_SUCCESS,
        "data": {
            "service": "x-rag",
            "status": "running",
            "version": "1.0.0",
            "components": {
                "api": "healthy",
                "vector_store": "healthy",
                "document_store": "healthy"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    return status