# English Docs (A1) + mcp-ntp Skill Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship English user-facing docs/comments (A1) and a project Agent Skill named `mcp-ntp` that helps agents run this MCP locally and call `get_current_time`.

**Architecture:** Docs and comments-only localization; one skill under `.agents/skills/mcp-ntp/` with a config asset. No runtime API changes.

**Tech Stack:** Python MCP server (`mcp==2.2.0`), uv, Agent Skills (`.agents/skills/*/SKILL.md`).

## Global Constraints

- Skill folder + frontmatter `name` must be `mcp-ntp` (not `setup-mcp-ntp`).
- Do not change tool name `get_current_time`, env `NTP_DOMAIN_URL`, header `ntp_url`, resource `ntp://time`, or JSON result fields.
- Prefer `pool.ntp.org` in English examples; keep `ntp.aliyun.com` as optional regional example.
- Do not bump package version unless required (not required).
- LICENSE file author text stays as-is.

---

### Task 1: English README + config template + startup scripts

**Files:**
- Modify: `README.md`
- Modify: `mcp_settings.template.json`
- Modify: `start-ntp-stdio.sh`, `start-ntp-sse.sh`, `start-ntp-stdio.ps1`, `start-ntp-sse.ps1`

- [ ] **Step 1: Rewrite README.md in English**

Include: features, install (`uv sync`), env/header config, stdio/sse usage, `get_current_time` docs, debugging, project structure, Skills section pointing at `.agents/skills/mcp-ntp/`, MIT license. Default NTP example: `pool.ntp.org`.

- [ ] **Step 2: Update mcp_settings.template.json**

Use `pool.ntp.org` as the primary example value for `NTP_DOMAIN_URL` / `ntp_url`. Keep the three server entries (stdio debug, sse debug, stdio production).

- [ ] **Step 3: English startup script messages**

Replace Chinese echo/`Write-Host` strings with English equivalents; keep commands the same. Prefer `pool.ntp.org` if scripts export `NTP_DOMAIN_URL`.

- [ ] **Step 4: Commit**

```bash
git add README.md mcp_settings.template.json start-ntp-*.sh start-ntp-*.ps1
git commit -m "docs: translate user-facing docs and scripts to English"
```

---

### Task 2: English Python comments, docstrings, and CLI help

**Files:**
- Modify: `app/__init__.py`, `app/server.py`, `app/client.py`, `app/config.py`
- Modify: `test_ntp.py` (and `tests/` if any Chinese remains)

- [ ] **Step 1: Translate all CJK comments/docstrings/Click help in app/**

Keep runtime English error messages and tool schemas unchanged.

- [ ] **Step 2: Translate comments in test_ntp.py**

- [ ] **Step 3: Verify no CJK remains in app/, README, scripts**

```bash
rg '[\p{Han}]' README.md app start-ntp-*.sh start-ntp-*.ps1 test_ntp.py mcp_settings.template.json || true
```

Expected: no matches (except possibly none).

- [ ] **Step 4: Commit**

```bash
git add app/ test_ntp.py
git commit -m "chore: translate Python comments and CLI help to English"
```

---

### Task 3: Add `.agents/skills/mcp-ntp` skill

**Files:**
- Create: `.agents/skills/mcp-ntp/SKILL.md`
- Create: `.agents/skills/mcp-ntp/assets/mcp-settings.snippet.json`
- Modify: `README.md` Skills section if not already accurate after Task 1

- [ ] **Step 1: Write SKILL.md**

Frontmatter:

```yaml
---
name: mcp-ntp
description: Use when setting up a local MCP server for accurate NTP/network time, configuring mcp-ntp in an MCP client, or needing an agent to call get_current_time for server time.
license: MIT
---
```

Body: prerequisites, local vs uvx install, env/header config, client snippet reference, smoke-test via `get_current_time`, troubleshooting (missing URL, UDP 123, path placeholders, sse vs stdio).

- [ ] **Step 2: Write assets/mcp-settings.snippet.json**

Minimal stdio local + uvx examples with `pool.ntp.org`.

- [ ] **Step 3: Commit**

```bash
git add .agents/skills/mcp-ntp README.md
git commit -m "feat: add mcp-ntp Agent Skill for local setup and time queries"
```

---

### Task 4: Verify and finalize

**Files:** none new (verification only)

- [ ] **Step 1: Run tests**

```bash
uv sync
uv run pytest -q
```

- [ ] **Step 2: Optional NTP smoke (may fail offline)**

```bash
NTP_DOMAIN_URL=pool.ntp.org uv run python -c "from app.client import get_current_time; print(get_current_time())"
```

- [ ] **Step 3: Push and mark PR ready**

Update PR body to reflect skill name `mcp-ntp` and completed implementation.
