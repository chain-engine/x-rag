#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Entry Point

FastAPI应用入口
"""

import sys
from pathlib import Path

# 添加src目录到路径
src_dir = Path(__file__).parent.resolve()
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from core.logger import logger
from core.config import settings
from core.middleware import setup_middleware
from core.exceptions import AppException
from core.services import AppServices
from repositories.vector_repository import VectorRepository
from repositories.document_repository import DocumentRepository
from services.indexing_service import IndexingService
from services.retrieval_service import RetrievalService
from services.generation_service import GenerationService
from api.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    logger.info("Starting x-rag application...")

    try:
        # 初始化Repository层
        vector_repo = VectorRepository(
            persist_directory=settings.VECTOR_STORE_PERSIST_DIR,
            collection_name=settings.VECTOR_STORE_COLLECTION_NAME,
            distance_type=settings.VECTOR_STORE_DISTANCE,
        )
        doc_repo = DocumentRepository(storage_path="./data/documents")

        # 初始化Service层
        indexing_service = IndexingService(
            vector_repo=vector_repo,
            doc_repo=doc_repo,
            chunk_size=settings.TEXT_SPLITTER_CHUNK_SIZE,
            chunk_overlap=settings.TEXT_SPLITTER_CHUNK_OVERLAP,
        )
        retrieval_service = RetrievalService(vector_repo=vector_repo)
        generation_service = GenerationService(
            default_provider=settings.GENERATION_PROVIDER,
            default_model=settings.GENERATION_MODEL,
            default_temperature=settings.GENERATION_TEMPERATURE,
            default_max_tokens=settings.GENERATION_MAX_TOKENS,
            default_timeout=settings.GENERATION_TIMEOUT,
        )

        # 创建服务容器并初始化
        services = AppServices(
            indexing_service=indexing_service,
            retrieval_service=retrieval_service,
            generation_service=generation_service,
        )
        services.initialize()

        # 存储到 app.state
        app.state.services = services

        logger.info("All services initialized successfully")

        yield

    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    finally:
        logger.info("Shutting down x-rag application...")

        # 从 app.state 获取服务并关闭
        services: AppServices | None = getattr(app.state, "services", None)
        if services:
            services.shutdown()

        logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.API_TITLE,
        description=settings.API_DESCRIPTION,
        version=settings.API_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # 配置中间件
    setup_middleware(app)

    # 注册路由
    app.include_router(api_router, prefix=settings.API_PREFIX)

    # 全局异常处理
    @app.exception_handler(AppException)
    async def app_exception_handler(request, exc: AppException):
        """应用异常处理器"""
        logger.error(f"Application exception: {exc.message}")
        return JSONResponse(
            status_code=exc.code,
            content={
                "code": exc.code,
                "message": exc.message,
                "detail": exc.detail,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc: RequestValidationError):
        """请求验证异常处理器"""
        logger.error(f"Validation error: {exc.errors()}")
        return JSONResponse(
            status_code=400,
            content={
                "code": 400,
                "message": "Validation failed",
                "errors": exc.errors(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc: Exception):
        """通用异常处理器"""
        logger.opt(exception=True).error("Unhandled exception occurred")
        return JSONResponse(
            status_code=500,
            content={
                "code": 500,
                "message": "Internal server error",
                "detail": str(exc) if settings.DEBUG else None,
            },
        )

    # 根路径
    @app.get("/", tags=["根路径"])
    async def root():
        """根路径"""
        return {
            "name": "x-rag",
            "version": "1.0.0",
            "description": "A production-ready RAG learning and training project",
            "docs": "/docs",
            "redoc": "/redoc",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )
