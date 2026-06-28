#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志模块

基于 loguru 的日志封装，集成 config.Settings 配置。
"""

import os
from typing import Final
from loguru import logger
from core.config import settings

# 确保日志目录存在
log_dir: str = os.path.dirname(settings.LOG_FILE_PATH)
if log_dir:
    os.makedirs(log_dir, exist_ok=True)

# 移除默认的控制台处理器，避免重复输出
logger.remove()

# 配置日志输出到文件
logger.add(
    settings.LOG_FILE_PATH,
    rotation=settings.LOG_ROTATION,
    retention=settings.LOG_RETENTION,
    compression='zip',
    level=settings.LOG_LEVEL,
    enqueue=True
)

# 配置日志输出到控制台
logger.add(
    sink=lambda msg: print(msg, end=""),
    level='DEBUG',
    enqueue=True
)

# 导出logger实例
__all__: Final[list[str]] = ['logger']
