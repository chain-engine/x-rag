#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据模型定义
使用Pydantic定义数据模型，支持请求参数校验和响应格式标准化
"""

from typing import Any, Generic, TypeVar, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

from core.exceptions import ValidationError
from common.constants import (
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TIMEOUT,
    DEFAULT_TOP_K,
    DEFAULT_SIMILARITY_THRESHOLD,
    DOC_TYPE_TXT,
    DOC_TYPE_MD,
    DOC_TYPE_PDF,
    DOC_TYPE_DOCX,
    DOC_TYPE_HTML,
    SUPPORTED_DOC_TYPES,
    LLM_PROVIDER_OPENAI,
    LLM_PROVIDER_ANTHROPIC,
    LLM_PROVIDER_DEEPSEEK,
    LLM_PROVIDER_ALIYUN,
    SUPPORTED_LLM_PROVIDERS,
)


T = TypeVar("T")


# ====================================
# 枚举类型定义
# ====================================

class DocStatus(str, Enum):
    """文档状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DELETED = "deleted"


class DocType(str, Enum):
    """文档类型枚举"""
    TXT = "txt"
    MD = "md"
    PDF = "pdf"
    DOCX = "docx"
    HTML = "html"


class DistanceType(str, Enum):
    """距离度量类型枚举"""
    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT = "dot"


class LLMProvider(str, Enum):
    """LLM提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    ALIYUN = "aliyun"


# ====================================
# 请求模型定义
# ====================================

class HealthCheckRequest(BaseModel):
    """健康检查请求"""
    pass


class DocumentUploadRequest(BaseModel):
    """文档上传请求"""
    file_type: str = Field(..., description="文档类型", example="txt")
    metadata: dict[str, Any] = Field(default_factory=dict, description="文档元数据")

    @validator("file_type")
    def validate_file_type(cls, v: str) -> str:
        if v not in SUPPORTED_DOC_TYPES:
            raise ValidationError(f"Unsupported file type: {v}")
        return v


class DocumentDeleteRequest(BaseModel):
    """文档删除请求"""
    document_id: str = Field(..., description="文档ID")


class DocumentQueryRequest(BaseModel):
    """文档查询请求"""
    page: int = Field(default=1, ge=1, description="页码")
    page_size: int = Field(default=20, ge=1, le=100, description="每页记录数")
    status: Optional[DocStatus] = Field(None, description="文档状态")
    file_type: Optional[DocType] = Field(None, description="文档类型")


class RAGQueryRequest(BaseModel):
    """RAG查询请求"""
    query: str = Field(..., min_length=1, max_length=2000, description="查询内容")
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=20, description="返回文档数量")
    similarity_threshold: float = Field(
        default=DEFAULT_SIMILARITY_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="相似度阈值"
    )
    use_mmr: bool = Field(default=False, description="是否使用MMR算法")
    mmr_lambda: float = Field(default=0.5, ge=0.0, le=1.0, description="MMR lambda参数")
    metadata_filter: Optional[dict[str, Any]] = Field(None, description="元数据过滤条件")
    provider: Optional[LLMProvider] = Field(None, description="LLM提供商")
    temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        ge=0.0,
        le=2.0,
        description="温度参数"
    )
    max_tokens: int = Field(
        default=DEFAULT_MAX_TOKENS,
        ge=1,
        le=8000,
        description="最大token数"
    )


class EmbeddingRequest(BaseModel):
    """向量化请求"""
    texts: list[str] = Field(..., min_length=1, description="待向量化的文本列表")
    normalize: bool = Field(default=True, description="是否归一化")


class RetrievalRequest(BaseModel):
    """检索请求"""
    query: str = Field(..., min_length=1, description="查询内容")
    top_k: int = Field(default=DEFAULT_TOP_K, ge=1, le=20, description="返回文档数量")
    similarity_threshold: float = Field(
        default=DEFAULT_SIMILARITY_THRESHOLD,
        ge=0.0,
        le=1.0,
        description="相似度阈值"
    )
    use_mmr: bool = Field(default=False, description="是否使用MMR算法")
    mmr_lambda: float = Field(default=0.5, ge=0.0, le=1.0, description="MMR lambda参数")
    metadata_filter: Optional[dict[str, Any]] = Field(None, description="元数据过滤条件")


class GenerationRequest(BaseModel):
    """生成请求"""
    prompt: str = Field(..., min_length=1, max_length=8000, description="生成提示")
    context: list[str] = Field(default_factory=list, description="上下文文本")
    provider: Optional[LLMProvider] = Field(None, description="LLM提供商")
    temperature: float = Field(
        default=DEFAULT_TEMPERATURE,
        ge=0.0,
        le=2.0,
        description="温度参数"
    )
    max_tokens: int = Field(
        default=DEFAULT_MAX_TOKENS,
        ge=1,
        le=8000,
        description="最大token数"
    )
    timeout: int = Field(default=DEFAULT_TIMEOUT, ge=1, le=300, description="超时时间（秒）")


# ====================================
# 响应模型定义
# ====================================

class HealthCheckResponse(BaseModel):
    """健康检查响应"""
    status: str = Field(..., description="服务状态")
    version: str = Field(..., description="版本号")
    timestamp: datetime = Field(..., description="时间戳")


class DocumentInfo(BaseModel):
    """文档信息"""
    document_id: str = Field(..., description="文档ID")
    file_name: str = Field(..., description="文件名")
    file_type: str = Field(..., description="文件类型")
    file_size: int = Field(..., description="文件大小（字节）")
    status: str = Field(..., description="文档状态")
    chunk_count: int = Field(..., description="分块数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class DocumentUploadResponse(BaseModel):
    """文档上传响应"""
    document_id: str = Field(..., description="文档ID")
    file_name: str = Field(..., description="文件名")
    status: str = Field(..., description="处理状态")
    message: str = Field(..., description="消息")


class DocumentDeleteResponse(BaseModel):
    """文档删除响应"""
    document_id: str = Field(..., description="文档ID")
    status: str = Field(..., description="删除状态")
    message: str = Field(..., description="消息")


class DocumentQueryResponse(BaseModel):
    """文档查询响应"""
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页记录数")
    total_pages: int = Field(..., description="总页数")
    items: list[DocumentInfo] = Field(..., description="文档列表")


class RetrievedDocument(BaseModel):
    """检索到的文档"""
    chunk_id: str = Field(..., description="分块ID")
    document_id: str = Field(..., description="文档ID")
    text: str = Field(..., description="文本内容")
    score: float = Field(..., description="相似度分数")
    metadata: dict[str, Any] = Field(default_factory=dict, description="元数据")


class RAGQueryResponse(BaseModel):
    """RAG查询响应"""
    query: str = Field(..., description="查询内容")
    answer: str = Field(..., description="生成的答案")
    retrieved_docs: list[RetrievedDocument] = Field(..., description="检索到的文档")
    provider: str = Field(..., description="使用的LLM提供商")
    model: str = Field(..., description="使用的模型")
    tokens_used: Optional[int] = Field(None, description="使用的token数")


class EmbeddingResponse(BaseModel):
    """向量化响应"""
    embeddings: list[list[float]] = Field(..., description="向量列表")
    dimension: int = Field(..., description="向量维度")
    model: str = Field(..., description="使用的模型")


class RetrievalResponse(BaseModel):
    """检索响应"""
    query: str = Field(..., description="查询内容")
    documents: list[RetrievedDocument] = Field(..., description="检索到的文档")
    total: int = Field(..., description="检索到的文档总数")


class GenerationResponse(BaseModel):
    """生成响应"""
    text: str = Field(..., description="生成的文本")
    provider: str = Field(..., description="使用的LLM提供商")
    model: str = Field(..., description="使用的模型")
    tokens_used: Optional[int] = Field(None, description="使用的token数")
    finish_reason: Optional[str] = Field(None, description="结束原因")


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int = Field(..., description="错误状态码")
    message: str = Field(..., description="错误消息")
    errors: Optional[list[dict[str, Any]]] = Field(None, description="错误详情")
    request_id: Optional[str] = Field(None, description="请求ID")