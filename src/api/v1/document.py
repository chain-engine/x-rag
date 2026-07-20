#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Document API Module

文档管理接口
"""

from typing import Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends

from schemas.document import (
    DocumentUploadResponse,
    DocumentDeleteResponse,
    DocumentQueryResponse,
    DocumentStatusResponse,
    DocumentInfo,
)
from core.logger import logger
from core.exceptions import DocumentError, ValidationError
from core.dependencies import get_indexing_service
from services.indexing_service import IndexingService
from constants.common import HTTP_OK, MSG_SUCCESS

router = APIRouter()


@router.post(
    "/documents/upload",
    summary="文档上传",
    description="上传文档并自动进行索引",
    tags=["文档"],
)
async def upload_document(
    file: UploadFile = File(..., description="上传的文件"),
    metadata: str = Form("{}", description="文档元数据（JSON字符串）"),
    indexing_service: IndexingService = Depends(get_indexing_service),
) -> dict[str, Any]:
    """文档上传接口"""
    try:
        import json

        # 解析元数据
        try:
            meta = json.loads(metadata) if metadata else {}
        except json.JSONDecodeError:
            raise ValidationError("Invalid metadata JSON format")

        # 读取文件内容
        content = await file.read()

        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError:
            try:
                text = content.decode("gbk")
            except Exception:
                raise DocumentError("Unsupported file encoding")

        # 获取文件信息
        file_name = file.filename or "unknown"
        file_type = file_name.split(".")[-1].lower() if "." in file_name else "txt"

        # 索引文档
        result = indexing_service.index_document(
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
    description="获取文档列表",
    tags=["文档"],
)
async def list_documents(
    page: int = 1,
    page_size: int = 20,
    status: str | None = None,
    file_type: str | None = None,
    indexing_service: IndexingService = Depends(get_indexing_service),
) -> dict[str, Any]:
    """文档列表接口"""
    try:
        documents = indexing_service.list_documents(status=status, file_type=file_type)

        # 分页
        total = len(documents)
        total_pages = (total + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size

        paginated_docs = documents[start_idx:end_idx]

        # 转换格式
        doc_infos = []
        for doc in paginated_docs:
            doc_infos.append({
                "document_id": doc.get("document_id"),
                "file_name": doc.get("file_name"),
                "file_type": doc.get("file_type"),
                "file_size": doc.get("file_size", 0),
                "status": doc.get("status"),
                "chunk_count": doc.get("chunk_count", 0),
                "created_at": doc.get("created_at"),
                "updated_at": doc.get("updated_at"),
                "metadata": doc.get("metadata", {}),
            })

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
        logger.error(f"List documents error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/documents/{document_id}",
    summary="获取文档详情",
    description="获取指定文档的详细信息",
    tags=["文档"],
)
async def get_document(
    document_id: str,
    indexing_service: IndexingService = Depends(get_indexing_service),
) -> dict[str, Any]:
    """获取文档详情接口"""
    try:
        document = indexing_service.get_document(document_id)

        if document.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Document not found")

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
    indexing_service: IndexingService = Depends(get_indexing_service),
) -> dict[str, Any]:
    """删除文档接口"""
    try:
        result = indexing_service.delete_document(document_id)

        return {
            "code": HTTP_OK,
            "message": MSG_SUCCESS,
            "data": {
                "document_id": result["document_id"],
                "status": result["status"],
                "vector_count": result["vector_count"],
                "message": "Document deleted successfully",
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
    indexing_service: IndexingService = Depends(get_indexing_service),
) -> dict[str, Any]:
    """获取文档状态接口"""
    try:
        status = indexing_service.get_document_status(document_id)

        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Document not found")

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
