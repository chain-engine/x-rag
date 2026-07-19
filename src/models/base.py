#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base Model Module

实体基类和混入定义
"""

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field


class BaseEntity(BaseModel):
    """实体基类

    所有数据实体的基类，提供通用字段
    """
    id: Optional[str] = Field(default=None, description="唯一标识符")

    class Config:
        from_attributes = True


class BaseTimestampMixin(BaseModel):
    """时间戳混入

    提供创建时间和更新时间字段
    """
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")

    class Config:
        from_attributes = True
