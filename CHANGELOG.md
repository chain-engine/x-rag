# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-07-19

### Added

- **Architecture**: Production-grade layered architecture with clear separation:
  - `src/api/` - API interface layer
  - `src/service/` - Business logic layer
  - `src/repository/` - Data access layer
  - `src/models/` - ORM entity layer
  - `src/infras/` - Infrastructure layer
  - `src/core/` - Core support layer (config, logger, exceptions, DI container)
  - `src/schemas/` - Pydantic request/response models
  - `src/constants/` - Organized constants by domain

- **Infrastructure Layer**: Abstract base classes for:
  - Vector stores (Chroma implementation)
  - Document stores (JSON implementation)
  - Embedding models (BGE implementation with caching)

- **Dependency Injection Container**: Singleton/transient support, decorator-based registration

- **CI/CD Pipeline**: GitHub Actions workflow with:
  - Code quality checks (ruff, black, mypy)
  - Unit tests with coverage
  - Docker image build and push

- **Pre-commit Configuration**: Automated code formatting and linting

- **Docker Support**:
  - Multi-stage Dockerfile (builder + production + development)
  - Health checks and non-root user
  - docker-compose.yml for production deployment

- **Scripts**: Platform-agnostic start/test/format scripts (bash + PowerShell)

### Changed

- **Configuration**: Migrated to `pydantic-settings` compatible structure
- **Exception Handling**: Enhanced exception hierarchy with detailed logging
- **Middleware**: Improved logging and request tracking
- **Tests**: Rewritten to work with new architecture

### Fixed

- Removed deprecated `src/rag/` legacy module
- Fixed test fixtures to match new service/repository signatures
- Corrected import paths throughout the codebase

### Documentation

- Bilingual documentation (README.md, README.en.md)
- API documentation with OpenAPI/Swagger
- Complete environment configuration guide

## [0.1.0] - 2024-01-01

### Added

- Initial RAG implementation
- Basic document indexing and retrieval
- Chroma vector store integration
- BGE-M3 embedding model support
- DeepSeek and OpenAI LLM provider support
- RESTful API with FastAPI

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 0.2.0 | 2026-07-19 | Production-grade architecture refactoring |
| 0.1.0 | 2024-01-01 | Initial release |
