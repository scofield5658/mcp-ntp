"""Contract tests for the installable mcp-ntp Agent Skill.

These lock the cross-agent promise: the folder is a valid Agent Skills
package, and the instructions tell an agent when to call the server and how
to register it for Claude Code, Cursor, and Copilot without a placeholder path.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / "skills" / "mcp-ntp"
SKILL_MD = SKILL_DIR / "SKILL.md"
STDIO_SNIPPET = SKILL_DIR / "assets" / "mcp-settings.snippet.json"
VSCODE_SNIPPET = SKILL_DIR / "assets" / "vscode.mcp.json"


def _frontmatter(text: str) -> str:
    assert text.startswith("---\n"), "SKILL.md must start with YAML frontmatter"
    end = text.find("\n---\n", 4)
    assert end != -1, "SKILL.md frontmatter must close"
    return text[4:end]


def test_skill_folder_matches_agentskills_name_rules():
    frontmatter = _frontmatter(SKILL_MD.read_text(encoding="utf-8"))
    assert "name: mcp-ntp\n" in frontmatter
    assert SKILL_DIR.name == "mcp-ntp"
    assert "license: MIT\n" in frontmatter
    assert "compatibility:" in frontmatter
    assert "uv" in frontmatter
    assert "author: scofield5658" in frontmatter


def test_description_triggers_on_time_questions_and_named_clients():
    frontmatter = _frontmatter(SKILL_MD.read_text(encoding="utf-8"))
    description_lines = []
    in_description = False
    for line in frontmatter.splitlines():
        if line.startswith("description:"):
            in_description = True
            continue
        if in_description and line and not line.startswith(" "):
            break
        if in_description:
            description_lines.append(line.strip())
    description = " ".join(description_lines)
    assert 1 <= len(description) <= 1024
    for phrase in (
        "get_current_time",
        "current time",
        "clock skew",
        "Claude Code",
        "Cursor",
        "Copilot",
    ):
        assert phrase in description


def test_stdio_snippet_is_published_uvx_package():
    payload = json.loads(STDIO_SNIPPET.read_text(encoding="utf-8"))
    server = payload["mcpServers"]["mcp-ntp"]
    assert server["command"] == "uvx"
    assert server["args"] == ["mcp-ntp"]
    assert server["env"]["NTP_DOMAIN_URL"] == "pool.ntp.org"
    assert "type" not in server
    raw = STDIO_SNIPPET.read_text(encoding="utf-8")
    assert "path_to_your_local" not in raw


def test_vscode_snippet_uses_servers_and_stdio_type():
    payload = json.loads(VSCODE_SNIPPET.read_text(encoding="utf-8"))
    assert "mcpServers" not in payload
    server = payload["servers"]["mcp-ntp"]
    assert server["type"] == "stdio"
    assert server["command"] == "uvx"
    assert server["args"] == ["mcp-ntp"]
    assert server["env"]["NTP_DOMAIN_URL"] == "pool.ntp.org"


def test_skill_body_covers_named_clients_and_refuses_a_hanging_stdio_launch():
    body = SKILL_MD.read_text(encoding="utf-8").split("\n---\n", 1)[1]
    assert "assets/mcp-settings.snippet.json" in body
    assert "assets/vscode.mcp.json" in body
    assert "claude mcp add --scope user --env NTP_DOMAIN_URL=pool.ntp.org --transport stdio mcp-ntp -- uvx mcp-ntp" in body
    assert "~/.cursor/mcp.json" in body
    assert ".vscode/mcp.json" in body
    assert "~/.copilot/mcp-config.json" in body
    assert "Do not start the server in a terminal" in body
    assert "path_to_your_local" not in body
    assert "mcp_settings.template.json" not in body
