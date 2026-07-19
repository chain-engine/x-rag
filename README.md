# x-rag: 生产级 RAG 实训项目

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **English**: [README.en.md](./README.en.md)

## 项目简介

x-rag 是一个**生产级 RAG（检索增强生成）学习和实训项目**，遵循后端行业标准化工程实践，提供分层清晰、模块化、高可扩展、易维护的通用服务架构。

### 核心价值

- **分层架构**: 标准五层业务架构 + 通用核心支撑层，完全与 Web 框架隔离
- **模块化设计**: 核心支撑层可复用在 RESTful API、定时任务、消息消费、离线脚本、单元测试等全场景
- **开箱即用**: 支持多环境切换、容器化部署，可快速搭建企业级 RESTful API 后端服务
- **工程规范**: 遵循 PEP8、完整类型注解、生产级日志与异常处理

## 核心特征

- **向量检索**: 支持 Chroma 向量存储，集成 BGE-M3 多语言嵌入模型
- **智能检索**: 支持 MMR（最大边际相关性）重排序，提升检索多样性
- **灵活切分**: 提供字符级、单词级、句子级、段落级、语义级等多种文本切分策略
- **多 LLM 支持**: 支持 DeepSeek、OpenAI 等主流 LLM 提供商
- **依赖注入**: 内置通用 IOC 容器，支持单例/多例模式
- **中间件支持**: CORS、限流、请求追踪、统一异常处理

## 项目结构

```
x-rag/
├── src/                          # 核心源码
│   ├── api/                      # API接口层
│   │   ├── router.py             # 路由注册
│   │   └── v1/                   # API v1版本
│   │       ├── health.py          # 健康检查
│   │       ├── rag.py            # RAG接口
│   │       └── document.py        # 文档管理
│   ├── service/                  # 业务逻辑层
│   │   ├── indexing_service.py    # 索引服务
│   │   ├── retrieval_service.py   # 检索服务
│   │   └── generation_service.py  # 生成服务
│   ├── repository/               # 数据访问层
│   │   ├── vector_repository.py  # 向量仓库
│   │   └── document_repository.py # 文档仓库
│   ├── models/                  # ORM实体层
│   │   ├── document.py           # 文档实体
│   │   └── vector.py            # 向量记录
│   ├── infras/                  # 基础设施层
│   │   ├── vector_store/         # 向量存储
│   │   ├── document_store/       # 文档存储
│   │   └── embedding/            # 嵌入模型
│   ├── core/                    # 核心支撑层
│   │   ├── config.py            # 配置中心
│   │   ├── logger.py            # 日志模块
│   │   ├── exceptions.py         # 异常定义
│   │   ├── container.py         # 依赖注入容器
│   │   ├── middleware.py         # 中间件
│   │   └── response.py           # 响应封装
│   ├── schemas/                  # 数据模型
│   │   ├── rag.py               # RAG相关Schema
│   │   ├── document.py           # 文档相关Schema
│   │   └── health.py            # 健康检查Schema
│   ├── constants/                # 常量定义
│   │   ├── common.py            # 通用常量
│   │   ├── rag.py               # RAG常量
│   │   ├── generation.py         # 生成常量
│   │   └── ...
│   ├── utils/                   # 工具函数
│   │   ├── text_splitter.py     # 文本切分
│   │   └── similarity.py         # 相似度计算
│   └── main.py                   # 应用入口
├── tests/                       # 测试用例
│   ├── conftest.py              # 测试配置
│   └── unit/                    # 单元测试
├── examples/                    # 示例代码
├── scripts/                     # 运维脚本
│   ├── start.sh / start.ps1    # 启动脚本
│   ├── test.sh / test.ps1      # 测试脚本
│   └── format.sh / format.ps1  # 格式化脚本
├── docs/                        # 项目文档
├── .github/workflows/            # GitHub Actions
├── .pre-commit-config.yaml     # Pre-commit配置
├── config.yaml                  # 配置文件
├── .env.example                 # 环境变量模板
├── docker-compose.yml           # Docker编排
├── Dockerfile                   # Docker镜像
├── pyproject.toml              # 项目配置
├── CHANGELOG.md               # 变更日志
├── LICENSE                     # MIT协议
└── README.md                  # 本文档
```

## 系统架构

### 分层架构

```
┌─────────────────────────────────────────────────────────┐
│                      API 接口层                          │
│  (api/v1/health.py, rag.py, document.py)               │
├─────────────────────────────────────────────────────────┤
│                      业务逻辑层                          │
│  (service/indexing_service.py, retrieval_service.py, ...) │
├─────────────────────────────────────────────────────────┤
│                      数据访问层                          │
│  (repository/vector_repository.py, document_repository.py) │
├─────────────────────────────────────────────────────────┤
│              基础设施层 (infras/)                       │
│  ┌─────────────┬──────────────┬─────────────────┐       │
│  │ VectorStore │ DocumentStore│ EmbeddingModel  │       │
│  │   (Chroma)  │    (JSON)   │   (BGE-M3)     │       │
│  └─────────────┴──────────────┴─────────────────┘       │
├─────────────────────────────────────────────────────────┤
│                      核心支撑层                          │
│  (core/config.py, logger.py, exceptions.py, container.py) │
└─────────────────────────────────────────────────────────┘
```

### 目录依赖关系

```
src/
├── api/      → services/
├── services/ → repositories/ + infras/
├── repository/→ infras/
├── infras/   → (无依赖)
├── core/     → (无依赖)
├── models/   → (无依赖)
├── schemas/   → core/
└── utils/    → core/
```

## 快速开始

### 环境要求

- Python 3.11+
- uv (推荐) 或 pip

### 克隆项目

```bash
git clone https://github.com/yeyushilai/x-rag.git
cd x-rag
```

### 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

### 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env，填入你的 API Key
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

### 启动服务

```bash
# 开发模式（热重载）
uv run uvicorn src.main:app --reload

# 或使用脚本
./scripts/start.sh   # Linux/macOS
.\scripts\start.ps1  # Windows
```

服务启动后访问:
- API 文档: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker 部署

```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f
```

## 常用命令

```bash
# 运行测试
uv run pytest tests/

# 代码格式化
uv run ruff check src/ --fix
uv run ruff format src/

# 类型检查
uv run mypy src/

# 安装预提交钩子
uv run pre-commit install
```

## 技术栈

| 类别 | 技术 |
|------|------|
| Web 框架 | FastAPI + Uvicorn |
| 数据存储 | Chroma (向量数据库) |
| 嵌入模型 | BGE-M3 (智源开源) |
| LLM | DeepSeek / OpenAI |
| 日志 | Loguru |
| 依赖注入 | 自研 IOC 容器 |
| 工具库 | Pydantic, httpx |
| 容器化 | Docker, docker-compose |
| CI/CD | GitHub Actions |

## API 文档

### 健康检查

```bash
GET /api/v1/health
```

### 文档管理

```bash
# 上传文档
POST /api/v1/documents/upload

# 列出文档
GET /api/v1/documents

# 获取文档
GET /api/v1/documents/{document_id}

# 删除文档
DELETE /api/v1/documents/{document_id}

# 获取文档状态
GET /api/v1/documents/{document_id}/status
```

### RAG 查询

```bash
# RAG问答
POST /api/v1/rag/query

# 仅检索
POST /api/v1/rag/retrieve

# 文本向量化
POST /api/v1/rag/embed

# 统计信息
GET /api/v1/rag/stats
```

## 许可证

本项目基于 [MIT License](./LICENSE) 开源。

## 联系方式

- 作者: John Young (夜雨诗来)
- 邮箱: john.young@foxmail.com
- Gitee: https://gitee.com/yeyushilai
- GitHub: https://github.com/yeyushilai

## 参考资料

- [Python](https://docs.python.org/3.11/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [uv](https://github.com/astral-sh/uv)
- [Chroma](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Pydantic](https://docs.pydantic.dev/)
