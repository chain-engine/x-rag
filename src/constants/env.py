#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Environment Constants Module

环境标识常量
"""

from .base import BaseEnum


class Environment(BaseEnum):
    """环境类型枚举"""
    DEVELOPMENT = "development", "开发环境"
    TEST = "test", "测试环境"
    PRODUCTION = "production", "生产环境"
