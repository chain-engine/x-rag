#!/bin/bash

# x-rag 服务启动脚本

set -e

echo "======================================"
echo "x-rag 服务启动"
echo "======================================"

# 检查Python版本
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Python版本: $PYTHON_VERSION"

# 检查是否为Python 3.11+
if ! python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "错误: 需要Python 3.11或更高版本"
    exit 1
fi

# 检查虚拟环境
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "警告: 未检测到虚拟环境，建议使用虚拟环境"
    echo "创建虚拟环境: python -m venv venv"
    echo "激活虚拟环境: source venv/bin/activate (Linux/Mac) 或 venv\Scripts\activate (Windows)"
fi

# 检查依赖
echo "检查依赖..."
pip show fastapi > /dev/null 2>&1 || {
    echo "安装依赖..."
    pip install -r requirements.txt
}

# 创建必要的目录
echo "创建目录..."
mkdir -p data/chroma data/documents logs

# 启动服务
echo "======================================"
echo "启动x-rag服务..."
echo "======================================"

# 获取配置
HOST=${SERVER_HOST:-0.0.0.0}
PORT=${SERVER_PORT:-8000}
DEBUG=${DEBUG:-true}

echo "服务地址: http://$HOST:$PORT"
echo "API文档: http://$HOST:$PORT/docs"
echo "ReDoc文档: http://$HOST:$PORT/redoc"

# 启动应用
if [ "$DEBUG" = "true" ]; then
    echo "开发模式 (热重载)"
    uv run uvicorn src.main:app --host "$HOST" --port "$PORT" --reload --log-level info
else
    echo "生产模式"
    uv run uvicorn src.main:app --host "$HOST" --port "$PORT" --workers 4 --log-level info
fi