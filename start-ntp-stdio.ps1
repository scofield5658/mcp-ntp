# 设置环境变量
$env:NTP_DOMAIN_URL = "ntp.aliyun.com"

Write-Host "启动MCP-NTP服务 (stdio模式)..." -ForegroundColor Green
python -m app --transport stdio --verbose
