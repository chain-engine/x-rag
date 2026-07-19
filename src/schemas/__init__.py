#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Schemas Package

统一存放接口请求入参、响应返回Pydantic模型
"""

from schemas.base import (
    BaseSchema,
    BaseRequest,
    BaseResponse,
)
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
    # Base
    "BaseSchema",
    "BaseRequest",
    "BaseResponse",
    # Responses
    "ResponseModel",
    "PageModel",
    "ErrorResponse",
    "success_response",
    "error_response",
    # RAG
    "RAGQueryRequest",
    "RetrievalRequest",
    "EmbeddingRequest",
    "GenerationRequest",
    "RetrievedDocument",
    "RAGQueryResponse",
    "EmbeddingResponse",
    "RetrievalResponse",
    "GenerationResponse",
    # Document
    "DocumentUploadRequest",
    "DocumentDeleteRequest",
    "DocumentQueryRequest",
    "DocumentInfo",
    "DocumentUploadResponse",
    "DocumentDeleteResponse",
    "DocumentQueryResponse",
    "DocumentStatusResponse",
    # Health
    "HealthCheckRequest",
    "HealthCheckResponse",
    "VersionResponse",
    "StatusResponse",
]
