#!/usr/bin/env pwsh
# x-rag Test Script for Windows (PowerShell)

$ErrorActionPreference = 'Stop'

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "x-rag Tests" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found" -ForegroundColor Red
    exit 1
}

# Activate virtual environment if exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & "venv\Scripts\Activate.ps1"
}

# Run unit tests
Write-Host "Running unit tests..." -ForegroundColor Green
uv run pytest tests/unit/ -v --cov=src --cov-report=term-missing

# Run integration tests if available
if (Test-Path "tests/integration") {
    Write-Host "Running integration tests..." -ForegroundColor Green
    uv run pytest tests/integration/ -v
}

# Generate coverage report
Write-Host "Generating coverage report..." -ForegroundColor Green
uv run pytest --cov=src --cov-report=html --cov-report=term

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Tests completed" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Coverage report: htmlcov\index.html" -ForegroundColor White
