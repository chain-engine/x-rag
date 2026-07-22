#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document API Module

文档管理接口 - 仅负责参数接收、调用业务服务、标准化返回
"""

from typing import Any
import json
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends, Request

from schemas.document import (
    DocumentUploadResponse,
    DocumentDeleteResponse,
    DocumentQueryResponse,
    DocumentStatusResponse,
    DocumentInfo,
)
from core.logger import logger
from core.exceptions import DocumentError, ValidationError
from services.document_service import DocumentService
from constants.common import HTTP_OK, MSG_SUCCESS

router = APIRouter()


def get_document_service(request: Request) -> DocumentService:
    """依赖注入：获取文档服务"""
    return request.app.state.document_service


@router.post(
    "/documents/upload",
    summary="文档上传",
    description="上传文档并自动进行索引",
    tags=["文档"],
)
async def upload_document(
    file: UploadFile = File(..., description="上传的文件"),
    metadata: str = Form("{}", description="文档元数据（JSON字符串）"),
    document_service: DocumentService = Depends(get_document_service),
) -> dict[str, Any]:
    """文档上传接口"""
    try:
        meta = _parse_metadata(metadata)

        content = await file.read()

        text = _decode_content(content)

        file_name = file.filename or "unknown"
        file_type = file_name.split(".")[-1].lower() if "." in file_name else "txt"

        result = document_service.upload_document(
            text=text,
            file_name=file_name,
            file_type=file_type,
            file_size=len(content),
            metadata=meta,
        )

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "document_id": result["document_id"],
                "file_name": file_name,
                "status": result["status"],
                "chunk_count": result["chunk_count"],
                "message": "Document uploaded and indexed successfully",
            },
        }

    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Upload error")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/documents",
    summary="文档列表",
    description="获取文档列表（支持分页）",
    tags=["文档"],
)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    file_type: str | None = None,
    document_service: DocumentService = Depends(get_document_service),
) -> dict[str, Any]:
    """文档列表接口（支持分页）"""
    try:
        page = max(1, page)
        page_size = min(max(1, page_size), 100)

        skip = (page - 1) * page_size

        result = document_service.list_documents(
            status=status,
            file_type=file_type,
            skip=skip,
            limit=page_size,
        )

        documents = result["documents"]
        total = result["total"]
        total_pages = (total + page_size - 1) // page_size

        doc_infos = [
            {
                "document_id": doc.get("document_id"),
                "file_name": doc.get("file_name"),
                "file_type": doc.get("file_type"),
                "file_size": doc.get("file_size", 0),
                "status": doc.get("status"),
                "chunk_count": doc.get("chunk_count", 0),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
                "metadata": doc.get("metadata", {}),
            }
            for doc in documents
        ]

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": total_pages,
                "items": doc_infos,
            },
        }

    except Exception as e:
        logger.error(f"列出文档失败: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/documents/{document_id}",
    summary="获取文档详情",
    description="获取指定文档的详细信息",
    tags=["文档"],
)
async def get_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> dict[str, Any]:
    """获取文档详情接口"""
    try:
        document = document_service.get_document(document_id)

        if document.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="文档不存在")

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": document,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete(
    "/documents/{document_id}",
    summary="删除文档",
    description="删除指定文档及其关联的向量",
    tags=["文档"],
)
async def delete_document(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> dict[str, Any]:
    """删除文档接口"""
    try:
        result = document_service.delete_document(document_id)

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "document_id": result["document_id"],
                "status": result["status"],
                "vector_count": result["vector_count"],
                "message": "文档删除成功",
            },
        }

    except DocumentError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.exception("Delete document error")
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.get(
    "/documents/{document_id}/status",
    summary="获取文档状态",
    description="获取指定文档的处理状态",
    tags=["文档"],
)
async def get_document_status(
    document_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> dict[str, Any]:
    """获取文档状态接口"""
    try:
        status = document_service.get_document_status(document_id)

        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="文档不存在")

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": status,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document status error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


def _parse_metadata(metadata: str) -> dict[str, Any]:
    """解析元数据JSON"""
    try:
        return json.loads(metadata) if metadata else {}
    except json.JSONDecodeError:
        raise ValidationError("Invalid metadata JSON format")


def _decode_content(content: bytes) -> str:
    """解码文件内容"""
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        try:
            return content.decode("gbk")
        except Exception as e:
            raise DocumentError(f"Unsupported file encoding: {e}")
