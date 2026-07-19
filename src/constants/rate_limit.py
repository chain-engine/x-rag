#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rate Limit Constants Module

限流相关的常量
"""

from typing import Final

# ====================================
# 限流常量
# ====================================
DEFAULT_REQUESTS_PER_MINUTE: Final[int] = 60
DEFAULT_REQUESTS_PER_HOUR: Final[int] = 1000
