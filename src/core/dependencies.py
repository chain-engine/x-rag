#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dependency Injection Functions

集中管理 FastAPI 依赖注入函数
"""

from fastapi import Request

from services.indexing_service import IndexingService
from services.retrieval_service import RetrievalService
from services.generation_service import GenerationService


def get_indexing_service(request: Request) -> IndexingService:
    """依赖注入：获取索引服务"""
    return request.app.state.services.indexing_service


def get_retrieval_service(request: Request) -> RetrievalService:
    """依赖注入：获取检索服务"""
    return request.app.state.services.retrieval_service


def get_generation_service(request: Request) -> GenerationService:
    """依赖注入：获取生成服务"""
    return request.app.state.services.generation_service
