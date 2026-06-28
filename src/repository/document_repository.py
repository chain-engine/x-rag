#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档仓库
基于JSON的文档元数据存储
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List

from repository.base_repository import BaseRepository
from core.logger import logger
from core.exceptions import DatabaseError


class DocumentRepository(BaseRepository):
    """文档仓库"""

    def __init__(self, storage_path: str = "./data/documents"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        """初始化文档仓库"""
        logger.info(f"DocumentRepository initialized at {self.storage_path}")

    def shutdown(self) -> None:
        """关闭文档仓库"""
        logger.info("DocumentRepository shut down")

    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "type": "document",
            "storage_path": str(self.storage_path),
            "count": len(list(self.storage_path.glob("*.json")))
        }

    def _get_document_path(self, document_id: str) -> Path:
        """获取文档文件路径"""
        return self.storage_path / f"{document_id}.json"

    def save(self, document: Dict[str, Any]) -> None:
        """保存文档"""
        try:
            file_path = self._get_document_path(document["document_id"])
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(document, f, ensure_ascii=False, indent=2)
            logger.debug(f"Saved document {document['document_id']}")
        except Exception as e:
            logger.error(f"Failed to save document: {e}")
            raise DatabaseError(f"Failed to save document: {e}") from e

    def load(self, document_id: str) -> Optional[Dict[str, Any]]:
        """加载文档"""
        try:
            file_path = self._get_document_path(document_id)
            if not file_path.exists():
                return None
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load document: {e}")
            raise DatabaseError(f"Failed to load document: {e}") from e

    def delete(self, document_id: str) -> bool:
        """删除文档"""
        try:
            file_path = self._get_document_path(document_id)
            if not file_path.exists():
                return False
            file_path.unlink()
            logger.debug(f"Deleted document {document_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise DatabaseError(f"Failed to delete document: {e}") from e

    def update(self, document_id: str, updates: Dict[str, Any]) -> None:
        """更新文档"""
        document = self.load(document_id)
        if document is None:
            raise DatabaseError(f"Document {document_id} not found")
        document.update(updates)
        self.save(document)

    def list_all(self) -> List[Dict[str, Any]]:
        """列出所有文档"""
        try:
            documents = []
            for file_path in self.storage_path.glob("*.json"):
                with open(file_path, "r", encoding="utf-8") as f:
                    documents.append(json.load(f))
            return documents
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            raise DatabaseError(f"Failed to list documents: {e}") from e

    def exists(self, document_id: str) -> bool:
        """检查文档是否存在"""
        return self._get_document_path(document_id).exists()