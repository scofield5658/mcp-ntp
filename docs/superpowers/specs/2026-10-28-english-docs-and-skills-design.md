# Design: English Localization (A1) + setup-mcp-ntp Skill

**Date:** 2026-10-28  
**Status:** Proposed  
**Choice:** Approach A / scope A1 (user approved)

## Problem

`mcp-ntp` is a Python MCP server that already exposes English tool/resource descriptions, but user-facing docs, CLI help, startup scripts, and code comments remain Chinese. That lowers discoverability for the international open-source community. Developers who rely on Agent Skills also lack a project skill that guides an agent to run this MCP locally and obtain server time via `get_current_time`.

## Goals

1. Convert **user-visible** Chinese copy and **code comments/docstrings** to English (A1).
2. Add one project-level Agent Skill so an agent can set up a local mcp-ntp instance and verify server-time retrieval.
3. Keep runtime behavior, tool names, config keys, and response schema unchanged.

## Non-Goals

- No bilingual README (no `README.zh-CN.md` in this change).
- No Cursor Plugin / marketplace packaging.
- No new MCP tools or API changes.
- No generic “scaffold any MCP from scratch” tutorial beyond configuring/running this project.
- No logic refactors unrelated to wording.

## Architecture

```text
mcp-ntp/
├── README.md                          # English: install, config, usage, Skills section
├── app/*.py                           # English comments, docstrings, Click help
├── start-ntp-*.{sh,ps1}               # English echo/messages
├── mcp_settings.template.json         # Prefer portable NTP example (+ note Aliyun optional)
├── test_ntp.py / tests/               # English comments only if present
└── .agents/skills/mcp-ntp/
    ├── SKILL.md                       # Agent workflow for local setup + time tool
    └── assets/
        └── mcp-settings.snippet.json  # Client config snippet for agents to copy
```

**Compatibility note:** Cursor also discovers `.cursor/skills/`. Primary location is `.agents/skills/` (agentskills-compatible). Optionally add a short pointer in README that Cursor users can symlink or copy into `.cursor/skills/` if needed; do **not** duplicate the full skill in two trees unless discovery testing requires it.

**Skill naming:** Folder and frontmatter `name` are both `mcp-ntp` (same as the project / package name), per product owner request.

## Component Design

### 1. English localization (A1)

| Surface | Action |
|---------|--------|
| `README.md` | Full English rewrite; keep structure; add Skills + portable NTP examples (`pool.ntp.org` default example; `ntp.aliyun.com` as regional option) |
| `app/__init__.py` | English Click `help` / command docstring / comments |
| `app/server.py`, `client.py`, `config.py` | English module/docstrings/comments only |
| `start-ntp-*.sh`, `start-ntp-*.ps1` | English messages |
| `test_ntp.py` | English comments |
| Runtime strings already English | Leave as-is unless awkward |

**Invariants (must not change):**

- Tool name: `get_current_time`
- Optional arg: `ntp_server`
- Env: `NTP_DOMAIN_URL`
- SSE header: `ntp_url`
- Resource URI: `ntp://time`
- JSON result fields: `ntp_server`, `ntp_timestamp`, `ntp_time`, `local_system_time`, `time_offset`, `response_delay`
- Transports: `stdio`, `sse`
- Python / MCP SDK version constraints in README remain accurate (`Python 3.10–3.14`, `mcp==2.2.0`)

### 2. Skill: `mcp-ntp`

**Path:** `.agents/skills/mcp-ntp/SKILL.md`  
**Folder name must match** frontmatter `name` (`mcp-ntp`).

**Frontmatter (intent):**

```yaml
---
name: mcp-ntp
description: Use when setting up a local MCP server for accurate NTP/network time, configuring mcp-ntp in an MCP client, or needing an agent to call get_current_time for server time.
license: MIT
---
```

Description rules: third-person, “Use when…”, triggering conditions only (no workflow summary).

**Skill body must instruct the agent to:**

1. Confirm prerequisites: Python 3.10–3.14, `uv` preferred (or `uvx` for production-style install).
2. Choose mode: **local checkout** (`uv sync` + `uv run mcp-ntp`) vs **published package** (`uvx mcp-ntp`).
3. Set `NTP_DOMAIN_URL` (default example `pool.ntp.org`; document Aliyun as optional).
4. Write MCP client config from `assets/mcp-settings.snippet.json` / repo template (stdio first; SSE optional).
5. Smoke-test: list tools → call `get_current_time` → confirm JSON fields above.
6. Troubleshoot: missing NTP URL, network/firewall to UDP 123, wrong `--directory` path, SSE header vs env confusion.

**Assets:** minimal JSON snippet for stdio (local `uv` and/or `uvx`), not a full multi-server dump unless helpful.

### 3. README Skills section

Short section explaining:

- Where the skill lives (`.agents/skills/mcp-ntp/`)
- That Cursor/compatible agents discover project skills automatically
- Example user prompt: “Set up mcp-ntp locally and get the current server time”

## Data / Config Flow (unchanged)

```text
stdio:  NTP_DOMAIN_URL env  → create_mcp_server(ntp_url) → get_current_time
sse:    ntp_url header      → create_mcp_server(ntp_url) → get_current_time
tool:   optional ntp_server arg overrides context URL
```

Skill documents this flow; does not alter it.

## Error Handling

- Localization: no behavior change.
- Skill: tell agents to surface configuration errors verbatim (existing English messages) and not invent alternate env var names.

## Testing / Verification

1. Grep for CJK in user-facing paths (`README.md`, `app/`, scripts); A1 expects none in those surfaces after change (except possibly LICENSE author names — leave LICENSE untouched).
2. `uv sync` + existing tests (`pytest` / `test_ntp.py` as applicable). Network-dependent NTP calls may fail offline — note in PR if environment blocks UDP 123.
3. Skill frontmatter validates against agentskills constraints (`name`/`description` length and charset).
4. Manual review: README install/config snippets remain copy-pasteable.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Chinese-speaking users lose `--help` language | Accepted under A1; no zh-CN README in this PR |
| Agents misconfigure paths | Skill stresses absolute/`--directory` path and template placeholders |
| Aliyun-centric examples alienate global users | Prefer `pool.ntp.org` in English docs; keep Aliyun as optional |
| Skill duplication across `.agents` and `.cursor` | Ship once under `.agents/skills/`; document discovery |

## Rollout

Single PR on branch `cursor/english-docs-and-skills-30a6` against `main`: docs + comments + skill only. Version bump not required unless packaging metadata must change (it does not).
