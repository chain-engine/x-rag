# Format code

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

Set-Location $ProjectDir

Write-Host "Running ruff check and auto-fix..."
uv run ruff check src/ --fix

Write-Host "Running ruff format..."
uv run ruff format src/

Write-Host "Running black..."
uv run black src/

Write-Host "Done!"
