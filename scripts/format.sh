#!/usr/bin/env bash
# Format code

set -e

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"

echo "Running ruff check and auto-fix..."
uv run ruff check src/ --fix

echo "Running ruff format..."
uv run ruff format src/

echo "Running black..."
uv run black src/

echo "Done!"
