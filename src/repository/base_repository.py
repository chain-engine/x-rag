#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
仓库基类
定义数据访问层的基础接口
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List


class BaseRepository(ABC):
    """仓库基类"""

    @abstractmethod
    def initialize(self) -> None:
        """初始化仓库"""
        pass

    @abstractmethod
    def shutdown(self) -> None:
        """关闭仓库"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        pass