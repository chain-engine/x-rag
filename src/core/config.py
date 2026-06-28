#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用配置管理
支持从环境变量和YAML配置文件读取配置
"""

import os
from typing import Final, Any
from pathlib import Path
from dataclasses import dataclass, field
import yaml
from dotenv import load_dotenv


@dataclass
class ServerConfig:
    """服务器配置"""
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    workers: int = 4
    environment: str = "development"


@dataclass
class LoggingConfig:
    """日志配置"""
    level: str = "INFO"
    file_path: str = "logs/x-rag-{time:YYYYMMDDHHmmss}.log"
    rotation: str = "1 day"
    retention: str = "7 days"


@dataclass
class RateLimitConfig:
    """限流配置"""
    enabled: bool = False
    requests_per_minute: int = 60
    requests_per_hour: int = 1000


@dataclass
class CORSConfig:
    """CORS配置"""
    enabled: bool = True
    allow_origins: list[str] = field(default_factory=lambda: ["*"])
    allow_methods: list[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE", "OPTIONS"])
    allow_headers: list[str] = field(default_factory=lambda: ["*"])
    allow_credentials: bool = False


@dataclass
class APIConfig:
    """API配置"""
    prefix: str = "/api/v1"
    title: str = "x-rag API"
    description: str = "RAG学习和实训项目API"
    version: str = "1.0.0"


@dataclass
class EmbeddingConfig:
    """向量模型配置"""
    model: str = "BAAI/bge-m3"
    device: str = "cpu"
    batch_size: int = 32
    cache_size: int = 1000
    normalize: bool = True


@dataclass
class VectorStoreConfig:
    """向量存储配置"""
    type: str = "chroma"
    persist_directory: str = "./data/chroma"
    collection_name: str = "documents"
    distance: str = "cosine"


@dataclass
class TextSplitterConfig:
    """文本切分配置"""
    chunk_size: int = 512
    chunk_overlap: int = 50
    separators: list[str] = field(default_factory=lambda: ["\n\n", "\n", "。", "！", "？", " ", ""])


@dataclass
class RetrievalConfig:
    """检索配置"""
    top_k: int = 5
    similarity_threshold: float = 0.7
    use_mmr: bool = False
    mmr_lambda: float = 0.5


@dataclass
class GenerationConfig:
    """生成配置"""
    provider: str = "deepseek"
    model: str = "deepseek-chat"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 30


class Settings:
    """应用配置类

    支持从环境变量和YAML配置文件读取配置
    优先级：环境变量 > YAML配置文件 > 默认配置
    """

    # 配置文件路径
    CONFIG_FILE_PATH: Final[str] = 'config.yaml'

    def __init__(self) -> None:
        """初始化配置"""
        load_dotenv()
        self._config: dict[str, Any] = self._load_config()
        self._parse_config()

    def _get_default_config(self) -> dict[str, Any]:
        """获取默认配置

        Returns:
            dict[str, Any]: 默认配置字典
        """
        return {
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'debug': True,
                'workers': 4,
                'environment': 'development'
            },
            'logging': {
                'level': 'INFO',
                'file_path': 'logs/x-rag-{time:YYYYMMDDHHmmss}.log',
                'rotation': '1 day',
                'retention': '7 days'
            },
            'rate_limit': {
                'enabled': False,
                'requests_per_minute': 60,
                'requests_per_hour': 1000
            },
            'cors': {
                'enabled': True,
                'allow_origins': ['*'],
                'allow_methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
                'allow_headers': ['*'],
                'allow_credentials': False
            },
            'api': {
                'prefix': '/api/v1',
                'title': 'x-rag API',
                'description': 'RAG学习和实训项目API',
                'version': '1.0.0'
            },
            'embedding': {
                'model': 'BAAI/bge-m3',
                'device': 'cpu',
                'batch_size': 32,
                'cache_size': 1000,
                'normalize': True
            },
            'vector_store': {
                'type': 'chroma',
                'persist_directory': './data/chroma',
                'collection_name': 'documents',
                'distance': 'cosine'
            },
            'text_splitter': {
                'chunk_size': 512,
                'chunk_overlap': 50,
                'separators': ['\n\n', '\n', '。', '！', '？', ' ', '']
            },
            'retrieval': {
                'top_k': 5,
                'similarity_threshold': 0.7,
                'use_mmr': False,
                'mmr_lambda': 0.5
            },
            'generation': {
                'provider': 'deepseek',
                'model': 'deepseek-chat',
                'temperature': 0.7,
                'max_tokens': 2000,
                'timeout': 30
            }
        }

    def _load_config(self) -> dict[str, Any]:
        """加载配置

        优先级：环境变量 > YAML配置文件 > 默认配置

        Returns:
            dict[str, Any]: 合并后的配置
        """

        # 获取默认配置
        config: dict[str, Any] = self._get_default_config()

        # 从YAML文件加载配置
        self._load_from_file(config)

        # 从环境变量加载配置（优先级最高）
        self._load_from_env(config)

        return config

    def _load_from_file(self, config: dict[str, Any]) -> None:
        """从YAML文件加载配置

        Args:
            config: 配置字典
        """
        config_file: Path = Path(self.CONFIG_FILE_PATH)
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    file_config: dict[str, Any] = yaml.safe_load(f) or {}
                self._merge_config(config, file_config)
            except Exception as e:
                print(f"警告: 无法加载配置文件 {self.CONFIG_FILE_PATH}: {e}")

    def _merge_config(self, base: dict[str, Any], override: dict[str, Any]) -> None:
        """递归合并配置

        Args:
            base: 基础配置字典
            override: 要覆盖的配置字典
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _load_from_env(self, config: dict[str, Any]) -> None:
        """从环境变量加载配置

        Args:
            config: 配置字典
        """
        # 服务器配置
        if os.environ.get('DEBUG'):
            config['server']['debug'] = os.environ.get('DEBUG').lower() == 'true'
        if os.environ.get('PORT'):
            config['server']['port'] = int(os.environ.get('PORT'))
        if os.environ.get('SERVER_PORT'):
            config['server']['port'] = int(os.environ.get('SERVER_PORT'))
        if os.environ.get('SERVER_HOST'):
            config['server']['host'] = os.environ.get('SERVER_HOST')

        # 日志配置
        if os.environ.get('LOG_LEVEL'):
            config['logging']['level'] = os.environ.get('LOG_LEVEL')
        if os.environ.get('LOG_FILE_PATH'):
            config['logging']['file_path'] = os.environ.get('LOG_FILE_PATH')
        if os.environ.get('LOG_ROTATION'):
            config['logging']['rotation'] = os.environ.get('LOG_ROTATION')
        if os.environ.get('LOG_RETENTION'):
            config['logging']['retention'] = os.environ.get('LOG_RETENTION')

        # 向量模型配置
        if os.environ.get('EMBEDDING_MODEL'):
            config['embedding']['model'] = os.environ.get('EMBEDDING_MODEL')
        if os.environ.get('EMBEDDING_DEVICE'):
            config['embedding']['device'] = os.environ.get('EMBEDDING_DEVICE')
        if os.environ.get('EMBEDDING_BATCH_SIZE'):
            config['embedding']['batch_size'] = int(os.environ.get('EMBEDDING_BATCH_SIZE'))
        if os.environ.get('EMBEDDING_CACHE_SIZE'):
            config['embedding']['cache_size'] = int(os.environ.get('EMBEDDING_CACHE_SIZE'))
        if os.environ.get('EMBEDDING_NORMALIZE'):
            config['embedding']['normalize'] = os.environ.get('EMBEDDING_NORMALIZE').lower() == 'true'

        # 向量存储配置
        if os.environ.get('VECTOR_STORE_PERSIST_DIR'):
            config['vector_store']['persist_directory'] = os.environ.get('VECTOR_STORE_PERSIST_DIR')
        if os.environ.get('VECTOR_STORE_COLLECTION_NAME'):
            config['vector_store']['collection_name'] = os.environ.get('VECTOR_STORE_COLLECTION_NAME')
        if os.environ.get('VECTOR_STORE_DISTANCE'):
            config['vector_store']['distance'] = os.environ.get('VECTOR_STORE_DISTANCE')

        # 文本切分配置
        if os.environ.get('TEXT_SPLITTER_CHUNK_SIZE'):
            config['text_splitter']['chunk_size'] = int(os.environ.get('TEXT_SPLITTER_CHUNK_SIZE'))
        if os.environ.get('TEXT_SPLITTER_CHUNK_OVERLAP'):
            config['text_splitter']['chunk_overlap'] = int(os.environ.get('TEXT_SPLITTER_CHUNK_OVERLAP'))

        # 检索配置
        if os.environ.get('RETRIEVAL_TOP_K'):
            config['retrieval']['top_k'] = int(os.environ.get('RETRIEVAL_TOP_K'))
        if os.environ.get('RETRIEVAL_SIMILARITY_THRESHOLD'):
            config['retrieval']['similarity_threshold'] = float(os.environ.get('RETRIEVAL_SIMILARITY_THRESHOLD'))
        if os.environ.get('RETRIEVAL_USE_MMR'):
            config['retrieval']['use_mmr'] = os.environ.get('RETRIEVAL_USE_MMR').lower() == 'true'
        if os.environ.get('RETRIEVAL_MMR_LAMBDA'):
            config['retrieval']['mmr_lambda'] = float(os.environ.get('RETRIEVAL_MMR_LAMBDA'))

        # 生成配置
        if os.environ.get('GENERATION_PROVIDER'):
            config['generation']['provider'] = os.environ.get('GENERATION_PROVIDER')
        if os.environ.get('GENERATION_MODEL'):
            config['generation']['model'] = os.environ.get('GENERATION_MODEL')
        if os.environ.get('GENERATION_TEMPERATURE'):
            config['generation']['temperature'] = float(os.environ.get('GENERATION_TEMPERATURE'))
        if os.environ.get('GENERATION_MAX_TOKENS'):
            config['generation']['max_tokens'] = int(os.environ.get('GENERATION_MAX_TOKENS'))
        if os.environ.get('GENERATION_TIMEOUT'):
            config['generation']['timeout'] = int(os.environ.get('GENERATION_TIMEOUT'))

        # API配置
        if os.environ.get('API_PREFIX'):
            config['api']['prefix'] = os.environ.get('API_PREFIX')

        # 限流配置
        if os.environ.get('RATE_LIMIT_ENABLED'):
            config['rate_limit']['enabled'] = os.environ.get('RATE_LIMIT_ENABLED').lower() == 'true'
        if os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE'):
            config['rate_limit']['requests_per_minute'] = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_MINUTE'))
        if os.environ.get('RATE_LIMIT_REQUESTS_PER_HOUR'):
            config['rate_limit']['requests_per_hour'] = int(os.environ.get('RATE_LIMIT_REQUESTS_PER_HOUR'))

        # CORS配置
        if os.environ.get('CORS_ENABLED'):
            config['cors']['enabled'] = os.environ.get('CORS_ENABLED').lower() == 'true'
        if os.environ.get('CORS_ALLOW_ORIGINS'):
            config['cors']['allow_origins'] = os.environ.get('CORS_ALLOW_ORIGINS')

    def _parse_config(self) -> None:
        """解析配置到具体配置对象"""
        self.server = ServerConfig(**self._config['server'])
        self.logging = LoggingConfig(**self._config['logging'])
        self.rate_limit = RateLimitConfig(**self._config['rate_limit'])
        self.cors = CORSConfig(**self._config['cors'])
        self.api = APIConfig(**self._config['api'])
        self.embedding = EmbeddingConfig(**self._config['embedding'])
        self.vector_store = VectorStoreConfig(**self._config['vector_store'])
        self.text_splitter = TextSplitterConfig(**self._config['text_splitter'])
        self.retrieval = RetrievalConfig(**self._config['retrieval'])
        self.generation = GenerationConfig(**self._config['generation'])

    def reload(self) -> None:
        """重新加载配置"""
        self._config = self._load_config()
        self._parse_config()

    # ===== 服务器配置属性 =====
    @property
    def SERVER_HOST(self) -> str:
        return self.server.host

    @property
    def SERVER_PORT(self) -> int:
        return self.server.port

    @property
    def DEBUG(self) -> bool:
        return self.server.debug

    @property
    def PORT(self) -> int:
        return self.server.port

    @property
    def SERVER_WORKERS(self) -> int:
        return self.server.workers

    @property
    def SERVER_ENVIRONMENT(self) -> str:
        return self.server.environment

    # ===== 日志配置属性 =====
    @property
    def LOG_LEVEL(self) -> str:
        return self.logging.level

    @property
    def LOG_FILE_PATH(self) -> str:
        return self.logging.file_path

    @property
    def LOG_ROTATION(self) -> str:
        return self.logging.rotation

    @property
    def LOG_RETENTION(self) -> str:
        return self.logging.retention

    # ===== 向量模型配置属性 =====
    @property
    def EMBEDDING_MODEL(self) -> str:
        return self.embedding.model

    @property
    def EMBEDDING_DEVICE(self) -> str:
        return self.embedding.device

    @property
    def EMBEDDING_BATCH_SIZE(self) -> int:
        return self.embedding.batch_size

    @property
    def EMBEDDING_CACHE_SIZE(self) -> int:
        return self.embedding.cache_size

    @property
    def EMBEDDING_NORMALIZE(self) -> bool:
        return self.embedding.normalize

    # ===== 向量存储配置属性 =====
    @property
    def VECTOR_STORE_PERSIST_DIR(self) -> str:
        return self.vector_store.persist_directory

    @property
    def VECTOR_STORE_COLLECTION_NAME(self) -> str:
        return self.vector_store.collection_name

    @property
    def VECTOR_STORE_DISTANCE(self) -> str:
        return self.vector_store.distance

    @property
    def VECTOR_STORE_TYPE(self) -> str:
        return self.vector_store.type

    # ===== 文本切分配置属性 =====
    @property
    def TEXT_SPLITTER_CHUNK_SIZE(self) -> int:
        return self.text_splitter.chunk_size

    @property
    def TEXT_SPLITTER_CHUNK_OVERLAP(self) -> int:
        return self.text_splitter.chunk_overlap

    @property
    def TEXT_SPLITTER_SEPARATORS(self) -> list[str]:
        return self.text_splitter.separators

    # ===== 检索配置属性 =====
    @property
    def RETRIEVAL_TOP_K(self) -> int:
        return self.retrieval.top_k

    @property
    def RETRIEVAL_SIMILARITY_THRESHOLD(self) -> float:
        return self.retrieval.similarity_threshold

    @property
    def RETRIEVAL_USE_MMR(self) -> bool:
        return self.retrieval.use_mmr

    @property
    def RETRIEVAL_MMR_LAMBDA(self) -> float:
        return self.retrieval.mmr_lambda

    # ===== 生成配置属性 =====
    @property
    def GENERATION_PROVIDER(self) -> str:
        return self.generation.provider

    @property
    def GENERATION_MODEL(self) -> str:
        return self.generation.model

    @property
    def GENERATION_TEMPERATURE(self) -> float:
        return self.generation.temperature

    @property
    def GENERATION_MAX_TOKENS(self) -> int:
        return self.generation.max_tokens

    @property
    def GENERATION_TIMEOUT(self) -> int:
        return self.generation.timeout

    # ===== API配置属性 =====
    @property
    def API_PREFIX(self) -> str:
        return self.api.prefix

    @property
    def API_TITLE(self) -> str:
        return self.api.title

    @property
    def API_DESCRIPTION(self) -> str:
        return self.api.description

    @property
    def API_VERSION(self) -> str:
        return self.api.version

    # ===== 限流配置属性 =====
    @property
    def RATE_LIMIT_ENABLED(self) -> bool:
        return self.rate_limit.enabled

    @property
    def RATE_LIMIT_REQUESTS_PER_MINUTE(self) -> int:
        return self.rate_limit.requests_per_minute

    @property
    def RATE_LIMIT_REQUESTS_PER_HOUR(self) -> int:
        return self.rate_limit.requests_per_hour

    # ===== CORS配置属性 =====
    @property
    def CORS_ENABLED(self) -> bool:
        return self.cors.enabled

    @property
    def CORS_ALLOW_ORIGINS(self) -> str:
        if isinstance(self.cors.allow_origins, list):
            return ",".join(self.cors.allow_origins)
        return self.cors.allow_origins

    @property
    def CORS_ALLOW_METHODS(self) -> list[str]:
        return self.cors.allow_methods

    @property
    def CORS_ALLOW_HEADERS(self) -> list[str]:
        return self.cors.allow_headers

    @property
    def CORS_ALLOW_CREDENTIALS(self) -> bool:
        return self.cors.allow_credentials


# 创建全局配置实例
settings: Final[Settings] = Settings()
