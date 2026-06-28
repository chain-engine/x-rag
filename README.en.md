# x-rag

A complete RAG (Retrieval-Augmented Generation) learning and training project, following industry best practices.

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Description

x-rag is a production-grade RAG learning and training project that provides a standardized, modular, highly scalable, and maintainable backend service foundation. It implements the complete RAG workflow, including offline index construction, online query retrieval, and augmented generation.

### Key Features

- 🏗️ **Standard Three-Tier Architecture**: API, Service, and Repository layers with strict dependency management
- 🔧 **Dependency Injection**: container with singleton/transient support
- 📝 **Complete Documentation**: Bilingual (Chinese/English) documentation with detailed architecture and usage examples
- 🧪 **Test Coverage**: Unit and integration tests to ensure code quality
- 🚀 **Docker Support**: Ready-to-use Docker image and docker-compose configuration
- 🔌 **Hot Reload**: Development mode with hot reload for improved efficiency
- 📊 **Multiple Embedding Models**: Support for mainstream models like BGE-M3
- 🗃️ **Multiple Vector Stores**: Chroma-based vector storage with persistence
- 🤖 **Multiple LLM Providers**: Support for OpenAI, DeepSeek, Aliyun Qwen, and more

## Project Structure

```
x-rag/
├── src/                        # Core business code
│   ├── api/                    # API layer
│   │   ├── router.py           # Router registration
│   │   └── v1/                 # v1 API endpoints
│   │       ├── health.py       # Health check
│   │       ├── rag.py          # RAG endpoints
│   │       └── document.py     # Document management
│   ├── service/                # Service layer
│   │   ├── indexing_service.py # Indexing service
│   │   ├── retrieval_service.py# Retrieval service
│   │   └── generation_service.py# Generation service
│   ├── repository/             # Repository layer
│   │   ├── vector_repository.py# Vector repository
│   │   └── document_repository.py# Document repository
│   ├── core/                   # Core support layer
│   │   ├── config.py           # Configuration center
│   │   ├── logger.py           # Logging module
│   │   ├── exceptions.py       # Exception definitions
│   │   ├── middleware.py       # Middleware
│   │   └── container.py        # Dependency injection container
│   ├── common/                 # Common components
│   │   ├── constants.py        # Constants
│   │   ├── schemas.py          # Data models
│   │   └── responses.py        # Response formats
│   └── utils/                  # Utility functions
│       ├── text_splitter.py    # Text splitting
│       ├── embedding.py        # Embedding (BGE-M3)
│       └── similarity.py       # Similarity calculation
├── examples/                   # Usage examples
│   ├── basic_rag.py            # Basic RAG example
│   └── document_processing.py  # Document processing example
├── tests/                      # Test directory
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # pytest configuration
├── scripts/                    # Deployment scripts
│   ├── start.ps1               # Start script (PowerShell)
│   ├── start.sh                # Start script (Linux/Mac)
│   ├── test.ps1                # Test script (PowerShell)
│   ├── test.sh                 # Test script (Linux/Mac)
│   ├── format.ps1              # Format script (PowerShell)
│   └── format.sh               # Format script (Linux/Mac)
├── config/                     # Configuration files
├── pyproject.toml              # Project dependencies
├── Dockerfile                  # Docker image
├── docker-compose.yml          # Docker compose
├── .env                        # Environment variables
├── .env.example                # Environment variables example
├── config.yaml                 # Configuration file
└── README.md                   # Project documentation
```

## Quick Start

### ① Requirements

#### Windows System

- **Python**: 3.11 or higher
- **OS**: Windows 10/11
- **Package Manager**: uv

```powershell
# Check Python version
python --version
# Should display Python 3.11.x or higher

# Check if uv is installed
uv --version
# If not installed, it will show the installation command
```

#### Linux/Mac System

- **Python**: 3.11 or higher
- **OS**: Linux (Ubuntu 20.04+, Debian 11+, Arch Linux, etc.), macOS 12+
- **Package Manager**: uv

```bash
# Check Python version
python --version
# Should display Python 3.11.x or higher

# Check if uv is installed
uv --version
# If not installed, it will show the installation command
```

### ② Clone Project

```bash
# Clone the project repository
git clone https://github.com/yeyushilai/x-rag.git

# Enter project directory
cd x-rag
```

### ③ Install Dependencies

#### Install uv (if not already installed)

```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### Sync dependencies

```bash
# Install project dependencies
uv sync

# Or install production dependencies only
uv sync --group prod
```

### ④ Configuration File Creation

#### .env Configuration

Copy `.env.example` to `.env` and modify key configurations:

```bash
cp .env.example .env
```

Edit the `.env` file and configure the following key parameters:

```bash
# ====================================
# LLM Configuration
# ====================================
GENERATION_PROVIDER=deepseek
GENERATION_MODEL=deepseek-chat
DEEPSEEK_API_KEY=your_api_key_here

# ====================================
# Embedding Model Configuration
# ====================================
EMBEDDING_MODEL=BAAI/bge-m3
EMBEDDING_DEVICE=cpu
EMBEDDING_BATCH_SIZE=32
EMBEDDING_CACHE_SIZE=1000

# ====================================
# Service Configuration
# ====================================
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
DEBUG=true
ENVIRONMENT=development

# ====================================
# Vector Store Configuration
# ====================================
VECTOR_STORE_PERSIST_DIR=./data/chroma
VECTOR_STORE_COLLECTION_NAME=documents
VECTOR_STORE_DISTANCE=cosine

# ====================================
# Text Splitter Configuration
# ====================================
TEXT_SPLITTER_CHUNK_SIZE=512
TEXT_SPLITTER_CHUNK_OVERLAP=50

# ====================================
# Retrieval Configuration
# ====================================
RETRIEVAL_TOP_K=5
RETRIEVAL_SIMILARITY_THRESHOLD=0.7
RETRIEVAL_USE_MMR=false

# ====================================
# API Configuration
# ====================================
API_PREFIX=/api/v1
```

#### config.yaml Configuration

`config.yaml` contains more detailed configuration items, adjust as needed:

```yaml
# Service configuration
server:
  host: 0.0.0.0
  port: 8000
  debug: false
  environment: development

# Logging configuration
logging:
  level: INFO
  file_path: logs/app.log
  rotation: 1 day
  retention: 7 days

# Embedding model configuration
embedding:
  model: BAAI/bge-m3
  device: cpu
  batch_size: 32
  cache_size: 1000
  normalize: true

# Vector store configuration
vector_store:
  type: chroma
  persist_directory: ./data/chroma
  collection_name: documents
  distance: cosine

# Text splitter configuration
text_splitter:
  chunk_size: 512
  chunk_overlap: 50
  separators:
    - "\n\n"
    - "\n"
    - "."
    - "!"
    - "?"
    - " "
    - ""

# Retrieval configuration
retrieval:
  top_k: 5
  similarity_threshold: 0.7
  use_mmr: false
  mmr_lambda: 0.5

# Generation configuration
generation:
  provider: deepseek
  model: deepseek-chat
  temperature: 0.7
  max_tokens: 2000
  timeout: 30
```

### ⑤ Start Service

#### 1. Local Development Mode

Supports hot reload and debugging:

```bash
# Start using uv (recommended)
uv run python src/main.py

# Or start using uvicorn directly
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Use start script (Linux/Mac)
bash scripts/start.sh

# Use start script (Windows)
scripts/start.bat
```

After successful startup, you can access:

- API Documentation: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

#### 2. Docker Containerized Deployment

Start with Docker Compose:

```bash
# Build and start service
docker-compose up -d

# View service status
docker-compose ps

# View service logs
docker-compose logs -f

# Stop service
docker-compose down

# Restart service
docker-compose restart
```

Docker deployment advantages:

- Environment isolation
- One-click deployment
- Easy to scale

### ⑥ Common Commands

#### Test Related

```bash
# Run all tests
uv run pytest tests/

# Run unit tests
uv run pytest tests/unit/

# Run integration tests
uv run pytest tests/integration/

# Generate coverage report
uv run pytest --cov=src --cov-report=html --cov-report=term

# View coverage report
# Open htmlcov/index.html file
```

#### Code Quality

```bash
# Code formatting
uv run black src/ tests/ examples/

# Code checking
uv run ruff check src/ tests/ examples/ --fix

# Type checking
uv run mypy src/
```

#### Dependency Management

```bash
# Sync dependencies
uv sync

# Add dependency
uv add package-name

# Add development dependency
uv add --group dev package-name

# Update dependencies
uv sync --upgrade
```

## Tech Stack

### Web Framework
- **FastAPI**: Modern, high-performance web framework
- **Uvicorn**: ASGI server

### Data Storage
- **Chroma**: Vector database
- **JSON**: Document metadata storage

### Machine Learning
- **Sentence-Transformers**: Text embedding (BGE-M3)
- **NumPy**: Numerical computing

### Utilities
- **Pydantic**: Data validation and settings management
- **Loguru**: Logging
- **PyYAML**: YAML configuration parsing
- **httpx**: Async HTTP client

### Deployment
- **Docker**: Containerization
- **Docker Compose**: Service orchestration

## API Documentation

After starting the service, access API documentation at:

### Swagger UI

Interactive API documentation:
```
http://localhost:8000/docs
```

### ReDoc

Read-only API documentation:
```
http://localhost:8000/redoc
```

### OpenAPI JSON

OpenAPI specification:
```
http://localhost:8000/openapi.json
```

## Example Usage

```python
import asyncio
import httpx

async def rag_query(query: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/rag/query",
            json={
                "query": query,
                "top_k": 3,
                "similarity_threshold": 0.7
            }
        )
        result = response.json()
        return result

# Run example
answer = asyncio.run(rag_query("What is Python?"))
print(answer["data"]["answer"])
```

For more examples, see the [examples/](examples/) directory.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Chroma Documentation](https://docs.trychroma.com/)
- [Sentence-Transformers Documentation](https://www.sbert.net/)
- [BGE-M3 Model](https://github.com/FlagOpen/FlagEmbedding)
- [Python Documentation](https://docs.python.org/3.11/)

## Contact

- **Author**: John Young (aka 夜雨诗来)
- **Email**: john.young@foxmail.com
- **Gitee**: https://gitee.com/yeyushilai
- **GitHub**: https://github.com/yeyushilai

---

<div align="center">

If this project helps you, please give it a ⭐️

Made with ❤️ by 夜雨诗来

</div>