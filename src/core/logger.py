#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger Module

基于Loguru的日志封装
"""

import os
from pathlib import Path
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
    if settings:
        # 确保日志目录存在
        log_file_path = settings.LOG_FILE_PATH
        if not os.path.isabs(log_file_path):
            # 如果是相对路径，基于项目根目录（core 的上级目录）
            project_root = Path(__file__).parent.parent.resolve()
            log_file_path = str(project_root / log_file_path)
        
        log_dir = os.path.dirname(log_file_path)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # 移除默认的控制台处理器
        _logger.remove()
        
        # 配置日志输出到文件
        _logger.add(
            log_file_path,
            rotation=settings.LOG_ROTATION,
            retention=settings.LOG_RETENTION,
            compression="zip",
            level=settings.LOG_LEVEL,
            enqueue=settings.DEBUG is False,
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
            backtrace=True,
            diagnose=True,
        )
        
        # 始终配置日志输出到控制台（仅输出 WARNING 及以上级别以避免过多干扰）
        _logger.add(
            sink=__import__("sys").stderr,
            level="WARNING",
            enqueue=False,
            colorize=True,
            format="<red>{time:HH:mm:ss}</red> | <level>{level: <8}</level> | <cyan>{name}:{function}</cyan> | <level>{message}</level>",
        )
        
        # 如果是调试模式，额外输出 DEBUG 级别日志
        if settings.DEBUG:
            _logger.add(
                sink=__import__("sys").stderr,
                level="DEBUG",
                enqueue=False,
                colorize=True,
                format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}:{function}</cyan> | <level>{message}</level>",
            )

# 尝试配置日志
if _config_loaded:
    _configure_logger()

logger = _logger
__all__: Final[list[str]] = ["logger"]
