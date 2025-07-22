#!/bin/bash

# 设置环境变量
export NTP_DOMAIN_URL="ntp.aliyun.com"

echo "启动MCP-NTP服务 (stdio模式)..."
python -m app --transport stdio --verbose
