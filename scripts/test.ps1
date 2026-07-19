# Run tests

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Set-Location $ProjectDir

# Create data directories if they don't exist
$DataDir = Join-Path $ProjectDir "data"
if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir | Out-Null
}

@("chroma", "documents") | ForEach-Object {
    $Dir = Join-Path $DataDir $_
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Path $Dir | Out-Null
    }
}

# Run tests
uv run pytest tests/ -v --cov=src --cov-report=term-missing
