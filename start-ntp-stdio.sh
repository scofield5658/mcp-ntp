#!/bin/bash

# Set the NTP server for stdio mode
export NTP_DOMAIN_URL="pool.ntp.org"

echo "Starting MCP-NTP (stdio)..."
python -m app --transport stdio --verbose
