#!/usr/bin/env pwsh
# x-rag Service Start Script for Windows (PowerShell)

$ErrorActionPreference = 'Stop'

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "x-rag Service Start" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

# Check Python version
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Python version: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python not found" -ForegroundColor Red
    exit 1
}

# Get configuration from environment or use defaults
$Host = if ($env:SERVER_HOST) { $env:SERVER_HOST } else { "0.0.0.0" }
$Port = if ($env:SERVER_PORT) { $env:SERVER_PORT } else { "8000" }
$Debug = if ($env:DEBUG) { $env:DEBUG } else { "true" }

# Create necessary directories
$requiredDirs = @("data\chroma", "data\documents", "logs")
foreach ($dir in $requiredDirs) {
    if (-not (Test-Path $dir)) {
        Write-Host "Creating directory: $dir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Start service
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Starting x-rag service..." -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan

Write-Host "Service URL: http://$Host`:$Port" -ForegroundColor White
Write-Host "API Docs: http://$Host`:$Port/docs" -ForegroundColor White
Write-Host "ReDoc: http://$Host`:$Port/redoc" -ForegroundColor White

# Start application
if ($Debug -eq "true") {
    Write-Host "Development mode (hot reload)" -ForegroundColor Green
    uv run uvicorn src.main:app --host $Host --port $Port --reload --log-level info
} else {
    Write-Host "Production mode" -ForegroundColor Green
    uv run uvicorn src.main:app --host $Host --port $Port --workers 4 --log-level info
}
