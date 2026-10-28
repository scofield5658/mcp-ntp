# MCP-NTP Time Service

An MCP (Model Context Protocol) NTP time service that gives language models accurate network time.

## Features

- Fetch accurate network time from an NTP server
- Support both `stdio` and `sse` transports
- Expose a `get_current_time` tool for models to query the current time
- Configure the NTP server via environment variable or request header
- Return detailed time information and NTP protocol metrics

## Install

Requires Python 3.10 through 3.14. The service pins MCP Python SDK 2.2.0.

```bash
# Install dependencies with uv
uv sync
```

## Configuration

### Environment variable (stdio)

Set `NTP_DOMAIN_URL`:

```bash
export NTP_DOMAIN_URL="pool.ntp.org"
```

Regional option (China): `ntp.aliyun.com`.

### Request header (sse)

Include the `ntp_url` header:

```
ntp_url: pool.ntp.org
```

## Usage

### stdio

```bash
export NTP_DOMAIN_URL="pool.ntp.org"
python -m app
```

Or use the helper scripts: `start-ntp-stdio.sh` / `start-ntp-stdio.ps1`.

### sse

```bash
python -m app --transport sse --port 8080

# Smoke-test the SSE endpoint
curl -H "ntp_url: pool.ntp.org" http://localhost:8080/sse
```

Or use: `start-ntp-sse.sh` / `start-ntp-sse.ps1`.

### MCP client settings

See `mcp_settings.template.json` for Cursor/compatible MCP client examples (`uv` local debug, SSE debug, and `uvx` production).

## Tool: `get_current_time`

Get the current time from an NTP server.

**Parameters:**

- `ntp_server` (optional): NTP server address. If omitted, uses the environment variable or request header.

**Example response:**

```json
{
  "ntp_server": "pool.ntp.org",
  "ntp_timestamp": 1703123456.789,
  "ntp_time": "2023-12-21T10:30:56.789",
  "local_system_time": "2023-12-21T10:30:56.789",
  "time_offset": 0.123,
  "response_delay": 0.045
}
```

## Debugging

```bash
export NTP_DOMAIN_URL="pool.ntp.org"
python -m app -v
```

## Agent Skill

This repo ships an installable Agent Skill at `skills/mcp-ntp/` so agents can set up a local mcp-ntp instance and call `get_current_time`.

Install into your project or user skills directory:

```bash
# Via skills CLI (recommended)
npx skills add scofield5658/mcp-ntp --skill mcp-ntp

# Or copy / symlink the standalone folder
cp -r skills/mcp-ntp ~/.agents/skills/
# Cursor users may also use ~/.cursor/skills/
```

Example prompt after install:

> Set up mcp-ntp locally and get the current server time.

## Development

### Project layout

```
mcp-ntp/
├── app/
│   ├── __init__.py      # CLI entry
│   ├── server.py        # MCP server
│   ├── client.py        # NTP client
│   └── config.py        # Configuration
├── skills/mcp-ntp/      # Installable Agent Skill
├── pyproject.toml
└── README.md
```

### Extending NTP configuration

`get_current_time` in `client.py` can be extended for additional NTP server selection logic.

## License

MIT License
