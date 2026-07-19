#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JSON Document Store Module

JSON文件文档存储实现
"""

import json
import os
from pathlib import Path
from typing import Any, Optional

from infras.document_store.base import DocumentStoreBase
from core.logger import logger
from core.exceptions import DocumentError


class JSONDocumentStore(DocumentStoreBase):
    """JSON文件文档存储实现"""

    def __init__(self, storage_path: str = "./data/documents"):
        self.storage_path = Path(storage_path)
        self._initialized = False

    def initialize(self) -> None:
        """初始化存储目录"""
        if self._initialized:
            return

        try:
            self.storage_path.mkdir(parents=True, exist_ok=True)
            self._initialized = True
            logger.info(f"JSONDocumentStore initialized: path={self.storage_path}")
        except Exception as e:
            logger.error(f"Failed to initialize JSONDocumentStore: {e}")
            raise DocumentError(f"Failed to initialize: {e}") from e

    def shutdown(self) -> None:
        """关闭存储"""
        self._initialized = False
        logger.info("JSONDocumentStore shut down")

    def _get_file_path(self, document_id: str) -> Path:
        """获取文档文件路径"""
        return self.storage_path / f"{document_id}.json"

    def save(self, document_id: str, data: dict[str, Any]) -> None:
        """保存文档到JSON文件"""
        self._ensure_initialized()

        try:
            file_path = self._get_file_path(document_id)
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved document: {document_id}")
        except Exception as e:
            logger.error(f"Failed to save document {document_id}: {e}")
            raise DocumentError(f"Failed to save document: {e}") from e

    def load(self, document_id: str) -> dict[str, Any] | None:
        """从JSON文件加载文档"""
        self._ensure_initialized()

        try:
            file_path = self._get_file_path(document_id)
            if not file_path.exists():
                return None

            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load document {document_id}: {e}")
            return None

    def delete(self, document_id: str) -> None:
        """删除文档文件"""
        self._ensure_initialized()

        try:
            file_path = self._get_file_path(document_id)
            if file_path.exists():
                file_path.unlink()
                logger.debug(f"Deleted document: {document_id}")
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {e}")
            raise DocumentError(f"Failed to delete document: {e}") from e

    def list_all(self) -> list[dict[str, Any]]:
        """列出所有文档"""
        self._ensure_initialized()

        documents = []
        try:
            for file_path in self.storage_path.glob("*.json"):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        documents.append(json.load(f))
                except Exception as e:
                    logger.warning(f"Failed to load document {file_path}: {e}")
                    continue
            return documents
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []

    def get_stats(self) -> dict[str, Any]:
        """获取统计信息"""
        self._ensure_initialized()

        try:
            files = list(self.storage_path.glob("*.json"))
            return {
                "type": "json",
                "storage_path": str(self.storage_path),
                "document_count": len(files),
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"type": "json", "error": str(e)}

    def _ensure_initialized(self) -> None:
        """确保已初始化"""
        if not self._initialized:
            raise DocumentError("DocumentStore not initialized. Call initialize() first.")
