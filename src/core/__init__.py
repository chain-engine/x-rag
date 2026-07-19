#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Core Package

核心支撑层：配置、日志、异常、容器、响应封装
"""

# 注意：logger和config不从此导入，避免循环依赖
# 请直接从具体模块导入：from core.logger import logger
#                                     from core.config import settings

from core.exceptions import (
    AppException,
    BusinessError,
    SystemError,
    NotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    RateLimitError,
    DocumentError,
    EmbeddingError,
    VectorStoreError,
    RetrievalError,
    GenerationError,
    DatabaseError,
    ConfigurationError,
)
from core.container import (
    Container,
    container,
    inject,
    singleton,
    transient,
    provides,
    scoped_container,
    get_container,
)
from core.response import success_response, error_response, BaseResp

__all__ = [
    # Config
    "Settings",
    "settings",
    # Logger
    "logger",
    # Exceptions
    "AppException",
    "BusinessError",
    "SystemError",
    "NotFoundError",
    "ValidationError",
    "UnauthorizedError",
    "ForbiddenError",
    "ConflictError",
    "RateLimitError",
    "DocumentError",
    "EmbeddingError",
    "VectorStoreError",
    "RetrievalError",
    "GenerationError",
    "DatabaseError",
    "ConfigurationError",
    # Container
    "Container",
    "container",
    "inject",
    "singleton",
    "transient",
    "provides",
    "scoped_container",
    "get_container",
    # Response
    "success_response",
    "error_response",
    "BaseResp",
]
