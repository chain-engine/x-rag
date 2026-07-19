#!/usr/bin/env bash
# Run tests

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

# Create data directories if they don't exist
mkdir -p data/chroma data/documents logs

# Run tests
uv run pytest tests/ -v --cov=src --cov-report=term-missing
