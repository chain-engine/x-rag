#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
依赖注入容器
实现依赖注入能力，支持单例/多例模式管理
"""

from typing import Any, Callable, TypeVar, Generic, Type, get_type_hints
from functools import wraps
from contextlib import contextmanager
from dataclasses import dataclass, field
import threading

from core.logger import logger

T = TypeVar("T")


@dataclass
class ServiceDescriptor:
    """服务描述符"""
    service_type: Type
    factory: Callable[[], Any]
    instance: Any = None
    is_singleton: bool = True
    dependencies: list[Type] = field(default_factory=list)


class Container:
    """依赖注入容器"""

    _instance: "Container" = None
    _lock: threading.Lock = threading.Lock()

    def __new__(cls) -> "Container":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._services: dict[Type, ServiceDescriptor] = {}
                    cls._instance._building: set[Type] = set()
        return cls._instance

    def register(
        self,
        service_type: Type[T],
        factory: Callable[[], T] | None = None,
        is_singleton: bool = True
    ) -> None:
        """注册服务

        Args:
            service_type: 服务类型
            factory: 工厂函数，如果为None则使用默认构造函数
            is_singleton: 是否为单例模式
        """
        if factory is None:
            factory = service_type

        if service_type in self._services:
            logger.warning(f"Service {service_type.__name__} already registered, overwriting")

        descriptor = ServiceDescriptor(
            service_type=service_type,
            factory=factory,
            is_singleton=is_singleton
        )

        self._services[service_type] = descriptor
        logger.debug(f"Registered service: {service_type.__name__}")

    def resolve(self, service_type: Type[T]) -> T:
        """解析服务

        Args:
            service_type: 服务类型

        Returns:
            T: 服务实例

        Raises:
            ValueError: 如果服务未注册或存在循环依赖
        """
        if service_type not in self._services:
            raise ValueError(f"Service {service_type.__name__} not registered")

        descriptor: ServiceDescriptor = self._services[service_type]

        # 检查循环依赖
        if service_type in self._building:
            raise ValueError(f"Circular dependency detected for {service_type.__name__}")

        # 单例模式且已创建实例
        if descriptor.is_singleton and descriptor.instance is not None:
            return descriptor.instance

        # 创建实例
        try:
            self._building.add(service_type)
            instance = self._create_instance(descriptor.factory)
            self._building.remove(service_type)

            if descriptor.is_singleton:
                descriptor.instance = instance

            return instance
        except Exception as e:
            self._building.discard(service_type)
            logger.error(f"Failed to resolve service {service_type.__name__}: {e}")
            raise

    def _create_instance(self, factory: Callable) -> Any:
        """创建服务实例

        Args:
            factory: 工厂函数

        Returns:
            Any: 服务实例
        """
        try:
            # 尝试通过类型提示自动注入依赖
            type_hints = get_type_hints(factory)
            if type_hints:
                kwargs = {}
                for param_name, param_type in type_hints.items():
                    if param_type in self._services:
                        kwargs[param_name] = self.resolve(param_type)
                return factory(**kwargs)
            return factory()
        except TypeError:
            return factory()

    def is_registered(self, service_type: Type) -> bool:
        """检查服务是否已注册

        Args:
            service_type: 服务类型

        Returns:
            bool: 是否已注册
        """
        return service_type in self._services

    def clear(self) -> None:
        """清空容器"""
        self._services.clear()
        self._building.clear()


# 全局容器实例
container: Container = Container()


def inject(*dependencies: Type):
    """依赖注入装饰器

    自动将依赖注入到函数参数中

    Args:
        dependencies: 依赖类型列表

    Returns:
        Callable: 装饰器函数

    Example:
        @inject(Repository)
        def my_function(repo: Repository):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            for dep in dependencies:
                dep_name = dep.__name__.lower()
                if dep_name not in kwargs:
                    kwargs[dep_name] = container.resolve(dep)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def singleton(service_type: Type[T] | None = None):
    """单例服务装饰器

    Args:
        service_type: 服务类型，如果为None则使用被装饰的类

    Returns:
        Callable: 装饰器函数

    Example:
        @singleton
        class MyService:
            pass
    """
    def decorator(cls: Type[T]) -> Type[T]:
        container.register(cls, cls, is_singleton=True)
        return cls
    if service_type is not None:
        return decorator(service_type)
    return decorator


def transient(service_type: Type[T] | None = None):
    """多例服务装饰器

    Args:
        service_type: 服务类型，如果为None则使用被装饰的类

    Returns:
        Callable: 装饰器函数

    Example:
        @transient
        class MyService:
            pass
    """
    def decorator(cls: Type[T]) -> Type[T]:
        container.register(cls, cls, is_singleton=False)
        return cls
    if service_type is not None:
        return decorator(service_type)
    return decorator


def provides(service_type: Type[T]):
    """服务提供者装饰器

    用于将一个工厂函数注册为特定类型的服务提供者

    Args:
        service_type: 服务类型

    Returns:
        Callable: 装饰器函数

    Example:
        @provides(MyService)
        def create_my_service() -> MyService:
            return MyService()
    """
    def decorator(factory: Callable) -> Callable:
        container.register(service_type, factory, is_singleton=True)
        return factory
    return decorator


@contextmanager
def scoped_container():
    """作用域容器上下文管理器

    用于在特定作用域内使用独立的容器实例

    Yields:
        Container: 容器实例
    """
    local_container = Container()
    yield local_container
    local_container.clear()


def get_container() -> Container:
    """获取全局容器实例

    Returns:
        Container: 容器实例
    """
    return container