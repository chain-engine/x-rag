#!/bin/bash

# x-rag 代码格式化脚本

set -e

echo "======================================"
echo "x-rag 代码格式化"
echo "======================================"

# 检查是否安装了black和ruff
if ! command -v black &> /dev/null; then
    echo "安装black..."
    pip install black
fi

if ! command -v ruff &> /dev/null; then
    echo "安装ruff..."
    pip install ruff
fi

echo "格式化代码..."
black src/ tests/ examples/

echo "检查代码..."
ruff check src/ tests/ examples/ --fix

echo "类型检查..."
if command -v mypy &> /dev/null; then
    mypy src/
else
    echo "跳过类型检查 (mypy未安装)"
fi

echo "======================================"
echo "格式化完成"
echo "======================================"