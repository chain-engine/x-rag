#!/usr/bin/env pwsh
# x-rag Code Formatting Script for Windows (PowerShell)

$ErrorActionPreference = 'Stop'

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "x-rag Code Formatting" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Activate virtual environment if exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Check and install black
Write-Host "Checking black..." -ForegroundColor White
if (-not (uv run python -c "import black" 2>$null)) {
    Write-Host "Installing black..." -ForegroundColor Yellow
    uv pip install black
}

# Check and install ruff
Write-Host "Checking ruff..." -ForegroundColor White
if (-not (uv run python -c "import ruff" 2>$null)) {
    Write-Host "Installing ruff..." -ForegroundColor Yellow
    uv pip install ruff
}

# Format code
Write-Host "Formatting code..." -ForegroundColor Green
uv run black src/ tests/ examples/

# Check code
Write-Host "Checking code..." -ForegroundColor Green
uv run ruff check src/ tests/ examples/ --fix

# Type check (if mypy available)
Write-Host "Type checking..." -ForegroundColor White
if (uv run python -c "import mypy" 2>$null) {
    uv run mypy src/
} else {
    Write-Host "Skipping type check (mypy not installed)" -ForegroundColor Gray
}

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Formatting completed" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
