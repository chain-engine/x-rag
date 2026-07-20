# x-rag: Production-Ready RAG Learning Project

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

> **中文**: [README.md](./README.md)

## Project Overview

x-rag is a **production-grade RAG (Retrieval-Augmented Generation) learning and training project**, following backend industry-standard engineering practices with a clear layered, modular, highly extensible, and maintainable architecture.

### Core Values

- **Layered Architecture**: Standard five-layer business architecture + universal core support layer, completely isolated from web framework
- **Modular Design**: Core support layer can be reused across RESTful API, scheduled tasks, message consumers, offline scripts, and unit tests
- **Ready to Use**: Supports multi-environment switching and containerized deployment, enabling rapid enterprise RESTful API backend setup
- **Engineering Standards**: PEP8 compliance, complete type annotations, production-grade logging and exception handling

## Core Features

- **Vector Retrieval**: Chroma vector store integration with BGE-M3 multilingual embedding model
- **Smart Retrieval**: MMR (Maximal Marginal Relevance) reranking for improved retrieval diversity
- **Flexible Splitting**: Multiple text splitting strategies - character, word, sentence, paragraph, and semantic
- **Multi-LLM Support**: DeepSeek, OpenAI, and other major LLM providers
- **Dependency Injection**: Built-in universal IOC container with singleton/transient support
- **Middleware Support**: CORS, rate limiting, request tracing, unified exception handling

## Project Structure

```
x-rag/
├── src/                          # Core source code
│   ├── api/                      # API interface layer
│   │   ├── router.py             # Route registration
│   │   └── v1/                   # API v1
│   │       ├── health.py          # Health check
│   │       ├── rag.py            # RAG endpoints
│   │       └── document.py        # Document management
│   ├── service/                  # Business logic layer
│   │   ├── indexing_service.py    # Indexing service
│   │   ├── retrieval_service.py   # Retrieval service
│   │   └── generation_service.py # Generation service
│   ├── repository/               # Data access layer
│   │   ├── vector_repository.py  # Vector repository
│   │   └── document_repository.py # Document repository
│   ├── models/                  # ORM entity layer
│   │   ├── document.py           # Document entity
│   │   └── vector.py            # Vector record
│   ├── infras/                  # Infrastructure layer
│   │   ├── vector_store/         # Vector store
│   │   ├── document_store/       # Document store
│   │   └── embedding/            # Embedding model
│   ├── core/                    # Core support layer
│   │   ├── config.py            # Configuration center
│   │   ├── logger.py            # Logging module
│   │   ├── exceptions.py         # Exception definitions
│   │   ├── container.py         # DI container
│   │   ├── middleware.py         # Middleware
│   │   └── response.py          # Response wrapper
│   ├── schemas/                  # Data models
│   │   ├── rag.py               # RAG schemas
│   │   ├── document.py           # Document schemas
│   │   └── health.py            # Health schemas
│   ├── constants/                # Constants
│   │   ├── common.py            # Common constants
│   │   ├── rag.py               # RAG constants
│   │   ├── generation.py         # Generation constants
│   │   └── ...
│   ├── utils/                   # Utilities
│   │   ├── text_splitter.py     # Text splitting
│   │   └── similarity.py         # Similarity calculation
│   └── main.py                   # Application entry
├── tests/                       # Test cases
│   ├── conftest.py              # Test configuration
│   └── unit/                    # Unit tests
├── examples/                    # Example code
├── scripts/                     # Operations scripts
│   ├── start.sh / start.ps1    # Start script
│   ├── test.sh / test.ps1      # Test script
│   └── format.sh / format.ps1  # Format script
├── docs/                        # Documentation
├── .github/workflows/            # GitHub Actions
├── .pre-commit-config.yaml     # Pre-commit config
├── config.yaml                  # Configuration file
├── .env.example                 # Environment template
├── docker-compose.yml           # Docker compose
├── Dockerfile                   # Docker image
├── pyproject.toml              # Project config
├── CHANGELOG.md               # Changelog
├── LICENSE                     # MIT License
└── README.md                  # This file
```

## System Architecture

### Layered Architecture Diagram

```mermaid
graph TB
    subgraph "API Layer (api)"
        A1["health.py<br/>Health Check"]
        A2["rag.py<br/>RAG Query"]
        A3["document.py<br/>Document Management"]
        A1 --- A2 --- A3
    end

    subgraph "Business Logic Layer (service)"
        S1["IndexingService"]
        S2["RetrievalService"]
        S3["GenerationService"]
    end

    subgraph "Data Access Layer (repository)"
        R1["VectorRepository"]
        R2["DocumentRepository"]
    end

    subgraph "Infrastructure Layer (infras)"
        I1["ChromaVectorStore"]
        I2["JSONDocumentStore"]
        I3["BGEEmbeddingModel"]
    end

    subgraph "Core Support Layer (core)"
        C1["config.py"]
        C2["logger.py"]
        C3["exceptions.py"]
        C4["container.py"]
        C5["middleware.py"]
        C6["response.py"]
    end

    subgraph "Data Models"
        M1["models/<br/>ORM Entities"]
        SCH1["schemas/<br/>Request/Response"]
        CST1["constants/<br/>Constants"]
    end

    subgraph "Utilities"
        U1["text_splitter.py"]
        U2["similarity.py"]
        U3["embedding.py"]
    end

    A1 --> S1
    A2 --> S2
    A2 --> S3
    A3 --> S1

    S1 --> R1
    S1 --> R2
    S2 --> R1
    S3 --> R2

    R1 --> I1
    R2 --> I2
    S1 --> I3
    S2 --> I3

    A1 -.-> C2
    A2 -.-> C2
    A3 -.-> C2
    S1 -.-> C2
    S2 -.-> C2
    S3 -.-> C2

    S1 -.-> C1
    S2 -.-> C1
    S3 -.-> C1

    A1 -.-> C5
    A2 -.-> C5
    A3 -.-> C5

    SCH1 -.-> C1
    SCH1 -.-> C2

    style A1 fill:#e1f5fe
    style A2 fill:#e1f5fe
    style A3 fill:#e1f5fe
    style S1 fill:#fff3e0
    style S2 fill:#fff3e0
    style S3 fill:#fff3e0
    style R1 fill:#e8f5e9
    style R2 fill:#e8f5e9
    style I1 fill:#fce4ec
    style I2 fill:#fce4ec
    style I3 fill:#fce4ec
    style C1 fill:#f3e5f5
    style C2 fill:#f3e5f5
    style C3 fill:#f3e5f5
    style C4 fill:#f3e5f5
    style C5 fill:#f3e5f5
    style C6 fill:#f3e5f5
```

### Core Business Flow Diagram

```mermaid
flowchart TD
    Start([User Request]) --> Health{Health Check?}
    
    Health -->|Yes| HealthCheck[Check Service Status<br/>Return System Health Info]
    HealthCheck --> End([Response])
    
    Health -->|Document Upload| Upload[Upload Document]
    Upload --> Validate[Validate Parameters]
    Validate -->|Fail| Error1[Return Error]
    Validate -->|Success| ReadFile[Read File Content]
    
    ReadFile --> SplitText[Split Text<br/>chunk_size/overlap]
    SplitText --> Embed[Vectorize<br/>BGE-M3 Model]
    
    Embed --> StoreVector[Store Vector<br/>Chroma]
    Embed --> StoreDoc[Store Document<br/>JSON]
    
    StoreVector --> Success1[Return Upload Success]
    StoreDoc --> Success1
    Success1 --> End
    
    Health -->|RAG Query| Query[Receive Query]
    Query --> EncodeQuery[Vectorize Query]
    EncodeQuery --> Search[Vector Search<br/>top_k/threshold]
    
    Search --> MMR{Enable MMR?}
    MMR -->|Yes| MMRSort[MMR Reranking<br/>Balance Relevance & Diversity]
    MMR -->|No| Filter[Similarity Filter]
    MMRSort --> BuildContext
    Filter --> BuildContext[Build Context]
    
    BuildContext --> LLM{Use LLM?}
    LLM -->|Yes| Generate[Call LLM<br/>DeepSeek/OpenAI]
    Generate --> Answer[Return RAG Answer]
    LLM -->|No| JustDocs[Return Retrieved Docs Only]
    
    Answer --> End
    JustDocs --> End
    
    Error1 --> End
```

### Module Dependency Diagram

```mermaid
graph LR
    subgraph "src/"
        subgraph "api/"
            API["api/v1/<br/>API Layer"]
        end
        
        subgraph "service/"
            SVC["service/<br/>Business Logic"]
        end
        
        subgraph "repository/"
            REPO["repository/<br/>Data Access"]
        end
        
        subgraph "infras/"
            INFRAS["infras/<br/>Infrastructure"]
        end
        
        subgraph "core/"
            CORE["core/<br/>Core Support"]
        end
        
        subgraph "models/"
            MODELS["models/<br/>Entities"]
        end
        
        subgraph "schemas/"
            SCHEMAS["schemas/<br/>Data Models"]
        end
        
        subgraph "constants/"
            CONST["constants/<br/>Constants"]
        end
        
        subgraph "utils/"
            UTILS["utils/<br/>Utilities"]
        end
    end

    API --> SVC
    SVC --> REPO
    SVC --> INFRAS
    SVC --> CORE
    
    REPO --> INFRAS
    REPO --> MODELS
    
    SCHEMAS -.-> CORE
    SCHEMAS -.-> CONST
    
    UTILS -.-> CORE
    UTILS -.-> CONST

    style API fill:#e1f5fe,stroke:#01579b
    style SVC fill:#fff3e0,stroke:#e65100
    style REPO fill:#e8f5e9,stroke:#2e7d32
    style INFRAS fill:#fce4ec,stroke:#c2185b
    style CORE fill:#f3e5f5,stroke:#7b1fa2
    style MODELS fill:#e0f7fa,stroke:#00838f
    style SCHEMAS fill:#fff8e1,stroke:#ff8f00
    style CONST fill:#efebe9,stroke:#5d4037
    style UTILS fill:#f1f8e9,stroke:#558b2f
```

### Dependency Rules

```mermaid
graph TD
    subgraph "Allowed Dependencies"
        R1["✓ API → Service → Repository"]
        R2["✓ Repository → Infras (get resources)"]
        R3["✓ Service → Core (config/logging)"]
        R4["✓ Schemas ↔ Core (weak dependency)"]
        R5["✓ Utils ↔ Core (weak dependency)"]
    end

    subgraph "Forbidden Rules ⚠️"
        D1["✗ No cross-layer calls (API → Repository)"]
        D2["✗ Lower layers cannot depend on upper layers"]
        D3["✗ No circular dependencies"]
        D4["✗ Infras cannot depend on Repository/Service"]
    end

    R1 --> D1
    R2 --> D2
    R3 --> D3
    R4 --> D4
```

## Quick Start

### Requirements

- Python 3.11+
- uv (recommended) or pip

### Clone Project

```bash
git clone https://github.com/yeyushilai/x-rag.git
cd x-rag
```

### Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -e .
```

### Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API Key
DEEPSEEK_API_KEY=your-deepseek-api-key-here
```

### Start Service

```bash
# Development mode (hot reload)
uv run uvicorn src.main:app --reload

# Or using scripts
./scripts/start.sh   # Linux/macOS
.\scripts\start.ps1  # Windows
```

After starting, access:
- API Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Docker Deployment

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f
```

## Common Commands

```bash
# Run tests
uv run pytest tests/

# Format code
uv run ruff check src/ --fix
uv run ruff format src/

# Type checking
uv run mypy src/

# Install pre-commit hooks
uv run pre-commit install
```

## Tech Stack

| Category | Technology |
|----------|------------|
| Web Framework | FastAPI + Uvicorn |
| Data Storage | Chroma (Vector Database) |
| Embedding Model | BGE-M3 (BAAI Open Source) |
| LLM | DeepSeek / OpenAI |
| Logging | Loguru |
| DI Container | Custom IOC Container |
| Utilities | Pydantic, httpx |
| Containerization | Docker, docker-compose |
| CI/CD | GitHub Actions |

## API Documentation

### Health Check

```bash
GET /api/v1/health
```

### Document Management

```bash
# Upload document
POST /api/v1/documents/upload

# List documents
GET /api/v1/documents

# Get document
GET /api/v1/documents/{document_id}

# Delete document
DELETE /api/v1/documents/{document_id}

# Get document status
GET /api/v1/documents/{document_id}/status
```

### RAG Query

```bash
# RAG Q&A
POST /api/v1/rag/query

# Retrieval only
POST /api/v1/rag/retrieve

# Text embedding
POST /api/v1/rag/embed

# Statistics
GET /api/v1/rag/stats
```

## License

This project is open source under [MIT License](./LICENSE).

## Contact

- Author: John Young
- Email: john.young@foxmail.com
- Gitee: https://gitee.com/yeyushilai
- GitHub: https://github.com/yeyushilai

## References

- [Python](https://docs.python.org/3.11/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [uv](https://github.com/astral-sh/uv)
- [Chroma](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Pydantic](https://docs.pydantic.dev/)
