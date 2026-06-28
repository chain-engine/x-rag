#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
响应格式标准化
定义统一的响应数据结构
"""

from typing import Any, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """通用响应模型"""

    code: int = Field(..., description="响应状态码", example=200)
    message: str = Field(..., description="响应消息", example="success")
    data: T | None = Field(None, description="响应数据")
    request_id: str | None = Field(None, description="请求ID")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "success",
                "data": None,
                "request_id": "uuid-here"
            }
        }


class PageModel(BaseModel, Generic[T]):
    """分页模型"""

    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description "每页记录数")
    total_pages: int = Field(..., description="总页数")
    items: list[T] = Field(..., description="数据列表")

    class Config:
        json_schema_extra = {
            "example": {
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5,
                "items": []
            }
        }


class ErrorDetail(BaseModel):
    """错误详情模型"""

    field: str | None = Field(None, description="错误字段")
    message: str = Field(..., description="错误消息")
    type: str = Field(..., description="错误类型")


class ErrorResponse(BaseModel):
    """错误响应模型"""

    code: int = Field(..., description="错误状态码", example=400)
    message: str = Field(..., description="错误消息", example="Bad Request")
    errors: list[ErrorDetail] | None = Field(None, description="错误详情列表")
    request_id: str | None = Field(None, description="请求ID")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 400,
                "message": "Bad Request",
                "errors": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "type": "ValueError"
                    }
                ],
                "request_id": "uuid-here"
            }
        }


def success_response(
    data: Any = None,
    message: str = "success",
    code: int = 200,
    request_id: str | None = None
) -> dict[str, Any]:
    """构造成功响应

    Args:
        data: 响应数据
        message: 响应消息
        code: 状态码
        request_id: 请求ID

    Returns:
        dict[str, Any]: 响应字典
    """
    return {
        "code": code,
        "message": message,
        "data": data,
        "request_id": request_id
    }


def error_response(
    message: str,
    code: int = 500,
    errors: list[ErrorDetail] | None = None,
    request_id: str | None = None
) -> dict[str, Any]:
    """构造错误响应

    Args:
        message: 错误消息
        code: 错误状态码
        errors: 错误详情列表
        request_id: 请求ID

    Returns:
        dict[str, Any]: 错误响应字典
    """
    return {
        "code": code,
        "message": message,
        "errors": errors,
        "request_id": request_id
    }