#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common Constants Module

通用常量定义，不依赖于特定业务领域
"""

from .base import BaseEnum
from typing import Final


class HttpStatus(BaseEnum):
    """HTTP 状态码枚举"""
    OK = 200, "成功"
    CREATED = 201, "已创建"
    BAD_REQUEST = 400, "请求错误"
    UNAUTHORIZED = 401, "未授权"
    FORBIDDEN = 403, "禁止访问"
    NOT_FOUND = 404, "资源不存在"
    CONFLICT = 409, "资源冲突"
    TOO_MANY_REQUESTS = 429, "请求过于频繁"
    INTERNAL_ERROR = 500, "服务器内部错误"


class ResponseMsg(BaseEnum):
    """响应消息枚举"""
    SUCCESS = "success", "操作成功"
    CREATED = "created", "创建成功"
    DELETED = "deleted", "删除成功"
    UPDATED = "updated", "更新成功"
    NOT_FOUND = "not found", "资源不存在"
    BAD_REQUEST = "bad request", "请求错误"
    UNAUTHORIZED = "unauthorized", "未授权"
    FORBIDDEN = "forbidden", "禁止访问"
    CONFLICT = "conflict", "资源冲突"
    INTERNAL_ERROR = "internal server error", "服务器内部错误"


# ====================================
# 时间格式常量
# ====================================
DATE_FORMAT: Final[str] = "%Y-%m-%d"
DATETIME_FORMAT: Final[str] = "%Y-%m-%d %H:%M:%S"
ISO_DATETIME_FORMAT: Final[str] = "%Y-%m-%dT%H:%M:%S.%fZ"

# ====================================
# 分页常量
# ====================================
DEFAULT_PAGE_SIZE: Final[int] = 20
MAX_PAGE_SIZE: Final[int] = 100

# ====================================
# 超时常量
# ====================================
SHORT_TIMEOUT: Final[int] = 5
MEDIUM_TIMEOUT: Final[int] = 30
LONG_TIMEOUT: Final[int] = 300

# ====================================
# 正则表达式常量
# ====================================
EMAIL_REGEX: Final[str] = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
PHONE_REGEX: Final[str] = r"^1[3-9]\d{9}$"


class HeaderType(BaseEnum):
    """HTTP 请求头类型枚举"""
    REQUEST_ID = "X-Request-ID", "请求ID"
    AUTHORIZATION = "Authorization", "授权令牌"
    CONTENT_TYPE = "Content-Type", "内容类型"
