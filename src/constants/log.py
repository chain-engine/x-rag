#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Log Level Constants Module

日志级别常量
"""

from .base import BaseEnum


class LogLevel(BaseEnum):
    """日志级别枚举"""
    DEBUG = "DEBUG", "调试级别"
    INFO = "INFO", "信息级别"
    WARNING = "WARNING", "警告级别"
    ERROR = "ERROR", "错误级别"
    CRITICAL = "CRITICAL", "严重错误级别"
