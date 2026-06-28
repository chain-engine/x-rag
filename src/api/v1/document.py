#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档管理接口
实现文档上传、删除、查询等功能
"""

import uuid
from typing import Optional, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends

from common.schemas import DocumentInfo, DocumentQueryResponse
from common.constants import (
    HTTP_OK,
    HTTP_CREATED,
    HTTP_NOT_FOUND,
    MSG_SUCCESS,
    DEFAULT_PAGE_SIZE
)
from core.exceptions import DocumentError
from core.logger import logger
from service.indexing_service import IndexingService


router = APIRouter()


# 服务依赖
_services: dict = {}


def set_services(indexing_service: IndexingService) -> None:
    """设置服务实例"""
    _services["indexing"] = indexing_service


def get_indexing_service() -> IndexingService:
    """获取索引服务"""
    if "indexing" not in _services:
        raise RuntimeError("IndexingService not initialized")
    return _services["indexing"]


@router.post(
    "/documents/upload",
    response_model=dict[str, Any],
    summary="上传文档",
    description="上传并索引文档",
    tags=["文档"]
)
async def upload_document(
    file: UploadFile = File(...),
    metadata: Optional[str] = Query(None, description="元数据（JSON格式）"),
    indexing_service: IndexingService = Depends(get_indexing_service)
) -> dict[str, Any]:
    """上传文档接口"""
    try:
        # 读取文件内容
        content = await file.read()

        # 尝试解码文本
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("gbk")
            except Exception as e:
                raise DocumentError(f"Failed to decode file: {e}")

        # 解析元数据
        doc_metadata = {}
        if metadata:
            import json
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError as e:
                raise DocumentError(f"Invalid metadata JSON: {e}")

        # 添加文件信息到元数据
        doc_metadata["original_filename"] = file.filename

        # 索引文档
        result = indexing_service.index_document(
            text=text,
            file_name=file.filename,
            file_type=file.filename.split(".")[-1] if "." in file.filename else "txt",
            file_size=len(content),
            metadata=doc_metadata
        )

        logger.info(f"Document uploaded: {result['document_id']}")

        return {
            "code": HTTP_CREATED,
            "message": MSG_SUCCESS,
            "data": {
                "document_id": result["document_id"],
                "file_name": file.filename,
                "status": result["status"],
                "message": f"Document indexed successfully with {result['chunk_count']} chunks"
            }
        }

    except DocumentError as e:
        logger.error(f"Document error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/documents/{document_id}",
    response_model=dict[str, Any],
    summary="删除文档",
    description="删除文档及其向量索引",
    tags=["文档"]
)
async def delete_document(
    document_id: str,
    indexing_service: IndexingService = Depends(get_indexing_service)
) -> dict[str, Any]:
    """删除文档接口"""
    try:
        result = indexing_service.delete_document(document_id)

        logger.info(f"Document deleted: {document_id}")

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "document_id": document_id,
                "status": result["status"],
                "message": f"Document deleted with {result['vector_count']} vectors"
            }
        }

    except DocumentError as e:
        logger.error(f"Document error: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/documents/{document_id}",
    response_model=dict[str, Any],
    summary="获取文档信息",
    description="获取文档的详细信息",
    tags=["文档"]
)
async def get_document(
    document_id: str,
    indexing_service: IndexingService = Depends(get_indexing_service)
) -> dict[str, Any]:
    """获取文档完整信息接口

    返回文档详细信息，包括文件元数据、状态、以及关联的 chunks 预览
    """
    try:
        document = indexing_service.get_document(document_id)

        if document.get("status") == "not_found":
            return {
                "code": HTTP_NOT_FOUND,
                "message": "not found",
                "data": None
            }

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": document
        }

    except Exception as e:
        logger.error(f"Get document error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/documents",
    response_model=dict[str, Any],
    summary="查询文档列表",
    description="分页查询文档列表",
    tags=["文档"]
)
async def list_documents(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100, description="每页记录数"),
    status: Optional[str] = Query(None, description="文档状态"),
    file_type: Optional[str] = Query(None, description="文件类型"),
    indexing_service: IndexingService = Depends(get_indexing_service)
) -> dict[str, Any]:
    """查询文档列表接口"""
    try:
        # 获取所有文档
        all_documents = indexing_service.list_documents(status=status, file_type=file_type)

        # 分页
        total = len(all_documents)
        total_pages = (total + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_documents = all_documents[start_idx:end_idx]

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "items": page_documents
            }
        }

    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/documents/{document_id}/status",
    response_model=dict[str, Any],
    summary="获取文档状态",
    description="获取文档的处理状态",
    tags=["文档"]
)
async def get_document_status(
    document_id: str,
    indexing_service: IndexingService = Depends(get_indexing_service)
) -> dict[str, Any]:
    """获取文档状态接口（轻量）

    返回文档的简要状态信息，适合频繁轮询检查处理进度
    """
    try:
        status = indexing_service.get_document_status(document_id)

        if status.get("status") == "not_found":
            return {
                "code": HTTP_NOT_FOUND,
                "message": "not found",
                "data": None
            }

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": status
        }

    except Exception as e:
        logger.error(f"Get document status error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")