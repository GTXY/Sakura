#!/bin/bash
# Sakura 后端启动脚本
# 用法：bash start.sh
# 建议通过 systemd 管理（见 sakura-backend.service）

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 激活虚拟环境
source .venv/bin/activate

# 启动 uvicorn（绑定本地端口 8001，供 nginx 代理）
exec uvicorn app.main:app \
    --host 127.0.0.1 \
    --port 8001 \
    --workers 2 \
    --log-level info
