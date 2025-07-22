Write-Host "启动MCP-NTP服务 (sse模式)..." -ForegroundColor Green
python -m app --transport sse --port 18002 --verbose
