FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# ========================================
# Builder stage
# ========================================
FROM base AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Compile dependencies
RUN uv sync --no-install-project --group dev

# ========================================
# Production stage
# ========================================
FROM base AS production

WORKDIR /app

# Copy dependency groups only (no dev)
COPY pyproject.toml uv.lock ./

# Install production dependencies only
RUN uv sync --no-install-project --frozen

# Copy source code
COPY src/ ./src/
COPY config.yaml ./

# Create non-root user
RUN useradd --create-home appuser
USER appuser

# Create data directories
RUN mkdir -p /app/data/chroma /app/data/documents /app/logs
ENV DATA_DIR=/app/data
ENV LOGS_DIR=/app/logs

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# ========================================
# Development stage
# ========================================
FROM base AS development

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install all dependencies
RUN uv sync

# Copy source code
COPY src/ ./src/
COPY config.yaml ./

# Create data directories
RUN mkdir -p data/chroma data/documents logs

# Run development server with hot reload
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
