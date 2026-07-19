#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Router Module

路由注册
"""

from fastapi import APIRouter

from api.v1 import health, rag, document

api_router = APIRouter()

# 注册健康检查路由
api_router.include_router(health.router, tags=["系统"])

# 注册RAG路由
api_router.include_router(rag.router, tags=["RAG"])

# 注册文档管理路由
api_router.include_router(document.router, tags=["文档"])
