#!/bin/bash

echo "Starting MCP-NTP (sse)..."
python -m app --transport sse --port 8080 --verbose
