#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常量重导出模块

此文件保留用于向后兼容，新代码应使用 constants 模块
"""

from typing import Final

from constants.common import *  # noqa: F401, F403
from constants.env import *  # noqa: F401, F403
from constants.rag import *  # noqa: F401, F403
from constants.embedding import *  # noqa: F401, F403
from constants.vector_store import *  # noqa: F401, F403
from constants.generation import *  # noqa: F401, F403
from constants.rate_limit import *  # noqa: F401, F403
from constants.log import *  # noqa: F401, F403
from constants.server import *  # noqa: F401, F403

# ====================================
# 环境常量
# ====================================
ENV_DEVELOPMENT: Final[str] = "development"  # 开发环境标识
ENV_TEST: Final[str] = "test"  # 测试环境标识
ENV_PRODUCTION: Final[str] = "production"  # 生产环境标识

# ====================================
# 距离度量方式
# ====================================
DISTANCE_COSINE: Final[str] = "cosine"  # 余弦相似度，通过计算向量夹角余弦值衡量相似度
DISTANCE_EUCLIDEAN: Final[str] = "euclidean"  # 欧几里得距离，计算向量间的直线距离
DISTANCE_DOT: Final[str] = "dot"  # 点积相似度，计算向量内积表示相似程度

# ====================================
# 文档状态常量
# ====================================
DOC_STATUS_PENDING: Final[str] = "pending"  # 文档待处理状态
DOC_STATUS_PROCESSING: Final[str] = "processing"  # 文档处理中状态
DOC_STATUS_COMPLETED: Final[str] = "completed"  # 文档处理完成状态
DOC_STATUS_FAILED: Final[str] = "failed"  # 文档处理失败状态
DOC_STATUS_DELETED: Final[str] = "deleted"  # 文档已删除状态

# ====================================
# 文档类型常量
# ====================================
DOC_TYPE_TXT: Final[str] = "txt"  # 纯文本文件类型
DOC_TYPE_MD: Final[str] = "md"  # Markdown 文档类型
DOC_TYPE_PDF: Final[str] = "pdf"  # PDF 文档类型
DOC_TYPE_DOCX: Final[str] = "docx"  # Word 文档类型
DOC_TYPE_HTML: Final[str] = "html"  # HTML 网页类型

SUPPORTED_DOC_TYPES: Final[set[str]] = {  # 系统支持的所有文档类型集合
    DOC_TYPE_TXT,
    DOC_TYPE_MD,
    DOC_TYPE_PDF,
    DOC_TYPE_DOCX,
    DOC_TYPE_HTML,
}

# ====================================
# 向量模型常量
# ====================================
DEFAULT_EMBEDDING_MODEL: Final[str] = "BAAI/bge-m3"  # 默认 embedding 模型，BGE-M3 是智源开源的多语言向量模型
DEFAULT_EMBEDDING_DEVICE: Final[str] = "cpu"  # 默认计算设备，cpu 或 cuda（gpu）
DEFAULT_EMBEDDING_BATCH_SIZE: Final[int] = 32  # 默认批处理大小，控制每次处理的数据量
DEFAULT_EMBEDDING_CACHE_SIZE: Final[int] = 1000  # embedding 结果缓存大小

# ====================================
# 向量存储常量
# ====================================
VECTOR_STORE_CHROMA: Final[str] = "chroma"  # Chroma 向量数据库标识
DEFAULT_COLLECTION_NAME: Final[str] = "documents"  # 默认 collection 名称，用于存储文档向量
DEFAULT_DISTANCE: Final[str] = DISTANCE_COSINE  # 默认距离度量方式

# ====================================
# 文本切分常量
# ====================================
DEFAULT_CHUNK_SIZE: Final[int] = 512  # 默认文本块大小（按 token 计）
DEFAULT_CHUNK_OVERLAP: Final[int] = 50  # 默认文本块重叠大小，保持上下文连贯性

# ====================================
# 检索常量
# ====================================
DEFAULT_TOP_K: Final[int] = 5  # 默认返回最相似的 K 条结果
DEFAULT_SIMILARITY_THRESHOLD: Final[float] = 0.7  # 默认相似度阈值，低于此值的结果将被过滤
DEFAULT_MMR_LAMBDA: Final[float] = 0.5  # MMR（最大边际相关性）参数，平衡相关性和多样性

# ====================================
# 生成常量
# ====================================
DEFAULT_TEMPERATURE: Final[float] = 0.7  # LLM 生成温度参数，控制随机性（0-1 之间）
DEFAULT_MAX_TOKENS: Final[int] = 2000  # LLM 生成的最大 token 数量限制
DEFAULT_TIMEOUT: Final[int] = 30  # LLM API 请求超时时间（秒）

# ====================================
# LLM提供商常量
# ====================================
LLM_PROVIDER_OPENAI: Final[str] = "openai"  # OpenAI API 提供商
LLM_PROVIDER_ANTHROPIC: Final[str] = "anthropic"  # Anthropic Claude API 提供商
LLM_PROVIDER_DEEPSEEK: Final[str] = "deepseek"  # DeepSeek API 提供商
LLM_PROVIDER_ALIYUN: Final[str] = "aliyun"  # 阿里云通义千问 API 提供商

SUPPORTED_LLM_PROVIDERS: Final[set[str]] = {  # 系统支持的所有 LLM 提供商集合
    LLM_PROVIDER_OPENAI,
    LLM_PROVIDER_ANTHROPIC,
    LLM_PROVIDER_DEEPSEEK,
    LLM_PROVIDER_ALIYUN,
}

# ====================================
# HTTP状态码常量
# ====================================
HTTP_OK: Final[int] = 200  # 请求成功
HTTP_CREATED: Final[int] = 201  # 资源创建成功
HTTP_BAD_REQUEST: Final[int] = 400  # 客户端请求错误
HTTP_UNAUTHORIZED: Final[int] = 401  # 未认证/认证失败
HTTP_FORBIDDEN: Final[int] = 403  # 无权限访问
HTTP_NOT_FOUND: Final[int] = 404  # 资源不存在
HTTP_CONFLICT: Final[int] = 409  # 资源冲突
HTTP_TOO_MANY_REQUESTS: Final[int] = 429  # 请求过于频繁，触发限流
HTTP_INTERNAL_ERROR: Final[int] = 500  # 服务器内部错误

# ====================================
# 响应消息常量
# ====================================
MSG_SUCCESS: Final[str] = "success"  # 操作成功消息
MSG_CREATED: Final[str] = "created"  # 资源创建成功消息
MSG_DELETED: Final[str] = "deleted"  # 资源删除成功消息
MSG_UPDATED: Final[str] = "updated"  # 资源更新成功消息
MSG_NOT_FOUND: Final[str] = "not found"  # 资源未找到消息
MSG_BAD_REQUEST: Final[str] = "bad request"  # 错误请求消息
MSG_UNAUTHORIZED: Final[str] = "unauthorized"  # 未认证消息
MSG_FORBIDDEN: Final[str] = "forbidden"  # 无权限消息
MSG_CONFLICT: Final[str] = "conflict"  # 资源冲突消息
MSG_INTERNAL_ERROR: Final[str] = "internal server error"  # 服务器内部错误消息

# ====================================
# 限流常量
# ====================================
DEFAULT_REQUESTS_PER_MINUTE: Final[int] = 60  # 默认每分钟请求次数限制
DEFAULT_REQUESTS_PER_HOUR: Final[int] = 1000  # 默认每小时请求次数限制

# ====================================
# 日志级别常量
# ====================================
LOG_DEBUG: Final[str] = "DEBUG"  # 调试级别日志，用于开发调试
LOG_INFO: Final[str] = "INFO"  # 信息级别日志，记录一般信息
LOG_WARNING: Final[str] = "WARNING"  # 警告级别日志，记录潜在问题
LOG_ERROR: Final[str] = "ERROR"  # 错误级别日志，记录错误信息
LOG_CRITICAL: Final[str] = "CRITICAL"  # 严重级别日志，记录严重错误

# ====================================
# 请求头常量
# ====================================
HEADER_REQUEST_ID: Final[str] = "X-Request-ID"  # 请求追踪 ID，用于日志关联
HEADER_AUTHORIZATION: Final[str] = "Authorization"  # 授权认证头
HEADER_CONTENT_TYPE: Final[str] = "Content-Type"  # 内容类型头

# ====================================
# 正则表达式常量
# ====================================
EMAIL_REGEX: Final[str] = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"  # 邮箱地址验证正则
PHONE_REGEX: Final[str] = r"^1[3-9]\d{9}$"  # 中国大陆手机号验证正则

# ====================================
# 时间格式常量
# ====================================
DATE_FORMAT: Final[str] = "%Y-%m-%d"  # 日期格式，如 2024-01-01
DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"  # 日期时间格式，如 2024-01-01 12:00:00
ISO_DATETIME_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S.%fZ"  # ISO 8601 格式，如 2024-01-01T12:00:00.000000Z

# ====================================
# 分页常量
# ====================================
DEFAULT_PAGE_SIZE: Final[int] = 20  # 默认每页显示数量
MAX_PAGE_SIZE: Final[int] = 100  # 最大每页显示数量，防止一次请求过多数据

# ====================================
# 超时常量
# ====================================
SHORT_TIMEOUT: Final[int] = 5  # 短超时时间，用于快速操作（秒）
MEDIUM_TIMEOUT: Final[int] = 30  # 中等超时时间，用于一般操作（秒）
LONG_TIMEOUT: Final[int] = 300  # 长超时时间，用于耗时操作（秒）
