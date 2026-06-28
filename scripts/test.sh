#!/bin/bash

# x-rag 测试脚本

set -e

echo "======================================"
echo "x-rag 测试"
echo "======================================"

# 检查Python版本
if ! python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "错误: 需要Python 3.11或更高版本"
    exit 1
fi

# 运行单元测试
echo "运行单元测试..."
pytest tests/unit/ -v --cov=src --cov-report=term-missing

# 运行集成测试（如果有）
if [ -d "tests/integration" ]; then
    echo "运行集成测试..."
    pytest tests/integration/ -v
fi

# 生成覆盖率报告
echo "生成覆盖率报告..."
pytest --cov=src --cov-report=html --cov-report=term

echo "======================================"
echo "测试完成"
echo "======================================"
echo "覆盖率报告: htmlcov/index.html"