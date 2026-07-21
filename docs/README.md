# x-rag Documentation

This directory contains documentation for the x-rag project.

## Available Documents

- [API Reference](api-reference.md) - Detailed API endpoint documentation
- [Configuration Guide](configuration.md) - Configuration options and environment variables
- [Development Guide](development.md) - Development setup and guidelines

## Project Structure

```
x-rag/
├── src/
│   ├── api/            # FastAPI routes and endpoints
│   ├── core/           # Core functionality (config, dependencies, exceptions)
│   ├── infras/         # Infrastructure (embedding, vector store, document store)
│   ├── models/         # Data models
│   ├── Repositories/   # Data access layer
│   ├── schemas/        # Pydantic schemas for API
│   ├── services/       # Business logic services
│   └── utils/          # Utility functions
├── tests/              # Test suite
├── docs/               # Documentation
└── examples/           # Usage examples
```

## Key Concepts

### RAG (Retrieval-Augmented Generation)

RAG combines retrieval and generation:
1. Retrieve relevant documents from a knowledge base
2. Augment the prompt with retrieved context
3. Generate answer using an LLM

### Text Chunking Strategies

| Strategy | Description | Use Case |
|---------|-------------|----------|
| Character | Fixed-size chunks by character count | Simple use cases |
| Word | Chunks by word count | English documents |
| Sentence | Chunks at sentence boundaries | Preserves sentence integrity |
| Paragraph | Chunks at paragraph boundaries | Well-structured documents |
| Semantic | Embedding-based semantic boundaries | Maximum coherence |

### Vector Store

Chroma is used for vector storage with support for:
- Cosine similarity
- Euclidean distance
- Metadata filtering
- Collection management
