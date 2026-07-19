#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common Schemas Module

保留用于向后兼容，新代码应使用 schemas
"""

# 为了向后兼容，重新导出
from schemas.base import BaseSchema, BaseRequest, BaseResponse
from schemas.responses import (
    ResponseModel,
    PageModel,
    ErrorResponse,
    success_response,
    error_response,
)
from schemas.rag import (
    RAGQueryRequest,
    RetrievalRequest,
    EmbeddingRequest,
    GenerationRequest,
    RetrievedDocument,
    RAGQueryResponse,
    EmbeddingResponse,
    RetrievalResponse,
    GenerationResponse,
)
from schemas.document import (
    DocumentUploadRequest,
    DocumentDeleteRequest,
    DocumentQueryRequest,
    DocumentInfo,
    DocumentUploadResponse,
    DocumentDeleteResponse,
    DocumentQueryResponse,
    DocumentStatusResponse,
)
from schemas.health import (
    HealthCheckRequest,
    HealthCheckResponse,
    VersionResponse,
    StatusResponse,
)

__all__ = [
    "BaseSchema",
    "BaseRequest",
    "BaseResponse",
    "ResponseModel",
    "PageModel",
    "ErrorResponse",
    "success_response",
    "error_response",
    "RAGQueryRequest",
    "RetrievalRequest",
    "EmbeddingRequest",
    "GenerationRequest",
    "RetrievedDocument",
    "RAGQueryResponse",
    "EmbeddingResponse",
    "RetrievalResponse",
    "GenerationResponse",
    "DocumentUploadRequest",
    "DocumentDeleteRequest",
    "DocumentQueryRequest",
    "DocumentInfo",
    "DocumentUploadResponse",
    "DocumentDeleteResponse",
    "DocumentQueryResponse",
    "DocumentStatusResponse",
    "HealthCheckRequest",
    "HealthCheckResponse",
    "VersionResponse",
    "StatusResponse",
]
