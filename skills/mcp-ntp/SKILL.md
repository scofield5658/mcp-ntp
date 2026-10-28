---
name: mcp-ntp
description: Use when setting up a local MCP server for accurate NTP/network time, configuring mcp-ntp in an MCP client, or needing an agent to call get_current_time for server time.
license: MIT
---

# mcp-ntp

## Overview

mcp-ntp is a Python MCP server that exposes accurate network time via NTP. Use this skill to run it locally and call `get_current_time`.

## When to Use

- The user wants a local MCP that returns server/network time
- The user asks to configure mcp-ntp in Cursor or another MCP client
- The agent needs `get_current_time` rather than the host clock alone

**Do not use** for general MCP scaffolding unrelated to this project, or for non-time tools.

## Prerequisites

- Python 3.10–3.14
- [`uv`](https://github.com/astral-sh/uv) recommended (`uvx` works for the published package)
- Outbound UDP port 123 to the chosen NTP host

## Setup

### Option A — local checkout (development)

```bash
cd /path/to/mcp-ntp
uv sync
export NTP_DOMAIN_URL="pool.ntp.org"
uv run mcp-ntp
# equivalent: python -m app
```

### Option B — published package (stdio)

```bash
export NTP_DOMAIN_URL="pool.ntp.org"
uvx mcp-ntp
```

### Option C — SSE

```bash
uv run mcp-ntp --transport sse --host 127.0.0.1 --port 8080
# Client must send header: ntp_url: pool.ntp.org
```

Regional NTP example (China): `ntp.aliyun.com`.

## MCP client config

Copy from `assets/mcp-settings.snippet.json` or the repo root `mcp_settings.template.json`.

Replace `path_to_your_local_mcp-project` with the absolute path to this repository when using the local `uv` entry.

**stdio config keys:**

- Env: `NTP_DOMAIN_URL`
- Command: `uv` + `--directory` + `run` + `mcp-ntp`, or `uvx` + `mcp-ntp`

**sse config keys:**

- URL: `http://localhost:8080/sse` (or your host/port)
- Header: `ntp_url`

Do not invent alternate env var or header names.

## Smoke test

1. Confirm the MCP server appears in the client and lists tool `get_current_time`.
2. Call `get_current_time` (optionally pass `ntp_server`).
3. Expect JSON with: `ntp_server`, `ntp_timestamp`, `ntp_time`, `local_system_time`, `time_offset`, `response_delay`.

Resource `ntp://time` returns the same time payload if the client supports resources.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Error about unconfigured NTP server | Set `NTP_DOMAIN_URL` (stdio) or `ntp_url` header (sse), or pass `ntp_server` |
| NTP request failed / timeout | Check UDP 123 egress; try `pool.ntp.org` |
| Client cannot start server | Fix `--directory` path; run `uv sync` in the checkout |
| SSE connects but no time | Ensure `ntp_url` header is present |

## Invariants

Do not rename the tool, change response field names, or substitute different config keys when helping users integrate this server.
