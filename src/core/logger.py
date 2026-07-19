#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger Module

基于Loguru的日志封装
"""

import os
from typing import Final
from loguru import logger as _logger

# 避免在导入时创建全局配置实例，而是延迟初始化
try:
    from core.config import settings
    _config_loaded = True
except ImportError:
    _config_loaded = False
    settings = None

# 配置日志
def _configure_logger():
    """配置日志"""
    # 确保日志目录存在
    if settings:
        log_dir = os.path.dirname(settings.LOG_FILE_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 移除默认的控制台处理器
        _logger.remove()
        
        # 配置日志输出到文件
        _logger.add(
            settings.LOG_FILE_PATH,
            rotation=settings.LOG_ROTATION,
            retention=settings.LOG_RETENTION,
            compression="zip",
            level=settings.LOG_LEVEL,
            enqueue=True,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        )
        
        # 配置日志输出到控制台（开发环境）
        if settings.DEBUG:
            _logger.add(
                sink=lambda msg: print(msg, end=""),
                level="DEBUG",
                enqueue=True,
                colorize=True,
                format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}</cyan> | <level>{message}</level>",
            )

# 尝试配置日志
if _config_loaded:
    _configure_logger()

logger = _logger
__all__: Final[list[str]] = ["logger"]
