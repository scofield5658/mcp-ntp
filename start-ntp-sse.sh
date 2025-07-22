#!/bin/bash

echo "启动MCP-NTP服务 (sse模式)..."
python -m app --transport sse --port 8080 --verbose
