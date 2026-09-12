import asyncio
import json
from mcp.types import (
    CallToolRequestParams,
    ListResourcesResult,
    ListToolsResult,
    ReadResourceRequestParams,
)

from app.server import create_mcp_server


async def invoke_handler(server, method, params):
    entry = server.get_request_handler(method)
    assert entry is not None, f"{method} handler must be registered"
    return await entry.handler(None, params)


def test_server_registers_v2_tool_and_resource_handlers():
    """Catches a migration that leaves MCP v2 handlers unregistered."""
    server = create_mcp_server("ntp.example.test")

    tools = asyncio.run(invoke_handler(server, "tools/list", None))
    resources = asyncio.run(invoke_handler(server, "resources/list", None))

    assert isinstance(tools, ListToolsResult)
    assert tools.tools[0].name == "get_current_time"
    assert isinstance(resources, ListResourcesResult)
    assert resources.resources[0].uri == "ntp://time"


def test_server_returns_v2_results_for_tool_and_resource_reads(monkeypatch):
    """Catches bare v1 return values that MCP v2 rejects during validation."""
    monkeypatch.setattr(
        "app.server.client.get_current_time",
        lambda ntp_server: {
            "ntp_server": ntp_server,
            "ntp_timestamp": 1.0,
            "ntp_time": "2026-09-12T00:00:01",
            "local_system_time": "2026-09-12T00:00:01",
            "time_offset": 0.0,
            "response_delay": 0.01,
        },
    )
    server = create_mcp_server("ntp.example.test")

    tool_result = asyncio.run(
        invoke_handler(
            server,
            "tools/call",
            CallToolRequestParams(name="get_current_time", arguments={}),
        )
    )
    resource_result = asyncio.run(
        invoke_handler(
            server,
            "resources/read",
            ReadResourceRequestParams(uri="ntp://time"),
        )
    )

    assert tool_result.is_error is False
    assert json.loads(tool_result.content[0].text)["ntp_server"] == "ntp.example.test"
    assert resource_result.contents[0].mime_type == "application/json"
    assert json.loads(resource_result.contents[0].text)["ntp_server"] == "ntp.example.test"
