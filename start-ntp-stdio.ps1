# Set the NTP server for stdio mode
$env:NTP_DOMAIN_URL = "pool.ntp.org"

Write-Host "Starting MCP-NTP (stdio)..." -ForegroundColor Green
python -m app --transport stdio --verbose
