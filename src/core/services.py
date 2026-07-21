#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Application Services Container

集中管理所有应用服务实例
"""

from dataclasses import dataclass

from services.indexing_service import IndexingService
from services.retrieval_service import RetrievalService
from services.augmentation_service import AugmentationService
from services.generation_service import GenerationService


@dataclass
class AppServices:
    """应用服务容器"""
    indexing_service: IndexingService
    retrieval_service: RetrievalService
    augmentation_service: AugmentationService
    generation_service: GenerationService

    def initialize(self) -> None:
        """初始化所有服务"""
        self.indexing_service.initialize()
        self.retrieval_service.initialize()
        self.augmentation_service.initialize()
        self.generation_service.initialize()

    def shutdown(self) -> None:
        """关闭所有服务"""
        self.indexing_service.shutdown()
        self.retrieval_service.shutdown()
        self.augmentation_service.shutdown()
        self.generation_service.shutdown()
