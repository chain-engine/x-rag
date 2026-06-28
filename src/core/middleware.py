#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中间件模块
实现CORS、限流、请求ID追踪等中间件
"""

import uuid
from typing import Callable
from functools import wraps
from fastapi import Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from core.logger import logger
from core.config import settings
from core.exceptions import RateLimitError
from common.constants import HEADER_REQUEST_ID


# 限流器实例
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_REQUESTS_PER_MINUTE}/minute",
                   f"{settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour"]
)


async def request_id_middleware(request: Request, call_next: Callable) -> Response:
    """请求ID中间件

    为每个请求生成唯一的请求ID，并添加到响应头中

    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理器

    Returns:
        Response: 响应对象
    """
    request_id: str = request.headers.get(HEADER_REQUEST_ID) or str(uuid.uuid4())
    request.state.request_id = request_id

    response: Response = await call_next(request)
    response.headers[HEADER_REQUEST_ID] = request_id

    logger.info(f"Request {request_id}: {request.method} {request.url.path}")

    return response


async def error_handler_middleware(request: Request, call_next: Callable) -> Response:
    """错误处理中间件

    统一捕获所有异常，返回标准化的错误响应

    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理器

    Returns:
        Response: 响应对象
    """
    try:
        return await call_next(request)
    except RateLimitExceeded as e:
        logger.warning(f"Rate limit exceeded: {e}")
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=429,
            content={
                "code": 429,
                "message": "Rate limit exceeded",
                "request_id": getattr(request.state, "request_id", None)
            }
        )
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "Internal server error",
                "request_id": getattr(request.state, "request_id", None)
            }
        )


async def logging_middleware(request: Request, call_next: Callable) -> Response:
    """日志中间件

    记录请求和响应的详细信息

    Args:
        request: 请求对象
        call_next: 下一个中间件或路由处理器

    Returns:
        Response: 响应对象
    """
    import time

    # 记录请求开始时间
    start_time: float = time.time()
    request.state.start_time = start_time

    # 调用下一个中间件或路由处理器
    response: Response = await call_next(request)

    # 计算处理时间（毫秒）
    process_time: float = (time.time() - start_time) * 1000

    logger.info(
        f"Request {getattr(request.state, 'request_id', 'unknown')} "
        f"completed in {process_time:.2f}ms "
        f"with status {response.status_code}"
    )

    return response


def get_cors_middleware_origins() -> list[str]:
    """获取CORS允许的来源

    Returns:
        list[str]: 允许的来源列表
    """
    from core.config import settings
    cors_origins: str = getattr(settings, "CORS_ALLOW_ORIGINS", "*")
    if cors_origins == "*":
        return ["*"]
    return [origin.strip() for origin in cors_origins.split(",")]


def setup_cors_middleware(app) -> None:
    """配置CORS中间件

    Args:
        app: FastAPI应用实例
    """
    from core.config import settings
    if not getattr(settings, "CORS_ENABLED", True):
        return

    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_cors_middleware_origins(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_middleware(app) -> None:
    """配置所有中间件

    Args:
        app: FastAPI应用实例

    注意：HTTP中间件按照添加顺序的相反顺序执行
    最后添加的中间件最先执行
    """
    # CORS中间件（特殊中间件，不受上述规则限制）
    setup_cors_middleware(app)

    # 日志中间件（最后添加，最先执行）
    app.middleware("http")(logging_middleware)

    # 错误处理中间件
    app.middleware("http")(error_handler_middleware)

    # 请求ID中间件（最先添加，最后执行）
    app.middleware("http")(request_id_middleware)