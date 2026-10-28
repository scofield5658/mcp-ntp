---
name: mcp-ntp
description: >-
  Gives an agent accurate NTP network time by registering the mcp-ntp MCP
  server and calling get_current_time. Use when the user asks for the current
  time, server time, UTC time, clock skew, or to set up mcp-ntp in Claude
  Code, Cursor, Copilot, or another MCP client.
license: MIT
compatibility: Requires uv (uvx), Python 3.10-3.14, and outbound UDP/123 to the NTP host. The skill folder installs into any Agent Skills client.
metadata:
  author: scofield5658
  version: "0.3.1"
---

# mcp-ntp

## Overview

Register the published package, then call `get_current_time`. Do not start the server in a terminal: stdio waits on stdin and hangs. Default host is `pool.ntp.org`. In mainland China use `ntp.aliyun.com` when the user wants a regional server. The only stdio setting is env `NTP_DOMAIN_URL`, set in the MCP config. A shell variable is not passed to the server.

## When to Use

- The user asks the current time, server time, UTC time, or whether the clock is skewed
- The user asks to add or configure mcp-ntp
- `get_current_time` is not available yet

Skip this for non-time MCP work. Do not rename the tool or its response fields.

## Register

Use `uvx mcp-ntp` unless the user is editing this repository. Write only the matching row.

| Client | Where | What to write |
|--------|--------|----------------|
| Claude Code | user scope, or `--scope project` for one repo | the command below |
| Cursor | `~/.cursor/mcp.json`, or `.cursor/mcp.json` for one project | [`assets/mcp-settings.snippet.json`](assets/mcp-settings.snippet.json) |
| VS Code + GitHub Copilot | `.vscode/mcp.json` | [`assets/vscode.mcp.json`](assets/vscode.mcp.json) |
| Copilot CLI | `~/.copilot/mcp-config.json`, or project `.mcp.json` | [`assets/mcp-settings.snippet.json`](assets/mcp-settings.snippet.json) |
| Any other agent | that client's MCP config file | the `mcpServers` snippet when that schema fits |

### Claude Code

```bash
claude mcp add --scope user --env NTP_DOMAIN_URL=pool.ntp.org --transport stdio mcp-ntp -- uvx mcp-ntp
```

`--transport stdio` sits between `--env` and the server name. `--scope project` writes `.mcp.json` and is only for a repo the user wants to share.

### Cursor

Merge the snippet. Top-level key is `mcpServers`. Do not add `type`.

### VS Code with GitHub Copilot

Copy `assets/vscode.mcp.json` to `.vscode/mcp.json`. Top-level key is `servers` and the entry has `"type": "stdio"`. The `mcpServers` snippet is the wrong schema here.

### Copilot CLI

Merge the `mcpServers` snippet into `~/.copilot/mcp-config.json` or the project `.mcp.json`.

### Other agents

Keep command `uvx`, args `["mcp-ntp"]`, and env `NTP_DOMAIN_URL`. Remap the file shape if the client requires it. Do not rename those fields.

Reconnect if the client does not reload MCP servers, then confirm it lists `get_current_time`.

## Call

Call `get_current_time` with no arguments. Pass `ntp_server` only when the user names another host. The payload is `ntp_server`, `ntp_timestamp`, `ntp_time`, `local_system_time`, `time_offset` (seconds, NTP minus the host clock), and `response_delay`. Report `ntp_time`. Mention `time_offset` when the user asks if the local clock is wrong. Resource `ntp://time` returns the same payload.

## Local checkout

Only when this workspace is the mcp-ntp source tree and the user wants that tree. Run `uv sync`. MCP args are `uv`, `--directory`, the absolute checkout path, `run`, `mcp-ntp`, with the same `NTP_DOMAIN_URL`. That path must contain `pyproject.toml`. Do not write a placeholder.

## SSE

Only when the user asks for a long-running server. Start it in the background:

```bash
uvx mcp-ntp --transport sse --host 127.0.0.1 --port 8080
```

Send header `ntp_url`, not `NTP_DOMAIN_URL`. Cursor uses `url` `http://127.0.0.1:8080/sse` and `headers.ntp_url`, with no `type`. Claude Code and Copilot CLI add `"type": "sse"`. VS Code puts those fields under `servers` and sets `"type": "sse"`.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| Unconfigured NTP server | Set `NTP_DOMAIN_URL`, header `ntp_url`, or argument `ntp_server` |
| NTP timeout | Open UDP 123, or use `pool.ntp.org` |
| `uvx mcp-ntp` never returns | Stop it and register the server in the MCP config |
| VS Code misses the server | Use `.vscode/mcp.json`, key `servers`, `"type": "stdio"` |
| Claude Code skips a URL entry | Add `"type": "sse"`. A `url` without `type` is treated as stdio and skipped |

## Invariants

Do not rename `get_current_time`, the response fields, `NTP_DOMAIN_URL`, or `ntp_url`.
