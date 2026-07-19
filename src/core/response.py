#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Response Module

统一响应封装
"""

from typing import Any
from pydantic import BaseModel, Field

from constants.common import HTTP_OK


class BaseResp(BaseModel):
    """基础响应模型"""
    code: int = Field(default=HTTP_OK, description="状态码")
    message: str = Field(default="success", description="消息")
    data: Any = Field(default=None, description="数据")
    request_id: str | None = Field(default=None, description="请求ID")


def success_response(
    data: Any = None,
    message: str = "success",
    code: int = HTTP_OK,
    request_id: str | None = None,
) -> dict[str, Any]:
    """构造成功响应"""
    return {
        "code": code,
        "message": message,
        "data": data,
        "request_id": request_id,
    }


def error_response(
    message: str,
    code: int = 500,
    errors: list[dict[str, Any]] | None = None,
    request_id: str | None = None,
) -> dict[str, Any]:
    """构造错误响应"""
    return {
        "code": code,
        "message": message,
        "errors": errors,
        "request_id": request_id,
    }
