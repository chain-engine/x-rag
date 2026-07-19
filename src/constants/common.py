#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Common Constants Module

通用常量定义，不依赖于特定业务领域
"""

from typing import Final

# ====================================
# HTTP 状态码常量
# ====================================
HTTP_OK: Final[int] = 200
HTTP_CREATED: Final[int] = 201
HTTP_BAD_REQUEST: Final[int] = 400
HTTP_UNAUTHORIZED: Final[int] = 401
HTTP_FORBIDDEN: Final[int] = 403
HTTP_NOT_FOUND: Final[int] = 404
HTTP_CONFLICT: Final[int] = 409
HTTP_TOO_MANY_REQUESTS: Final[int] = 429
HTTP_INTERNAL_ERROR: Final[int] = 500

# ====================================
# 响应消息常量
# ====================================
MSG_SUCCESS: Final[str] = "success"
MSG_CREATED: Final[str] = "created"
MSG_DELETED: Final[str] = "deleted"
MSG_UPDATED: Final[str] = "updated"
MSG_NOT_FOUND: Final[str] = "not found"
MSG_BAD_REQUEST: Final[str] = "bad request"
MSG_UNAUTHORIZED: Final[str] = "unauthorized"
MSG_FORBIDDEN: Final[str] = "forbidden"
MSG_CONFLICT: Final[str] = "conflict"
MSG_INTERNAL_ERROR: Final[str] = "internal server error"

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

# ====================================
# 请求头常量
# ====================================
HEADER_REQUEST_ID: Final[str] = "X-Request-ID"
HEADER_AUTHORIZATION: Final[str] = "Authorization"
HEADER_CONTENT_TYPE: Final[str] = "Content-Type"
