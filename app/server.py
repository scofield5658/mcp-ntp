"""
MCP-NTP server implementation.

Uses the native MCP Server with stdio and sse transports.
"""

import json
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server import Server, ServerRequestContext
from mcp.types import (
    CallToolRequestParams,
    CallToolResult,
    ListResourcesResult,
    ListToolsResult,
    PaginatedRequestParams,
    ReadResourceRequestParams,
    ReadResourceResult,
    Resource,
    TextContent,
    TextResourceContents,
    Tool,
)

from . import client
from . import __version__

logger = logging.getLogger("mcp-ntp")

class AppContext:
    """Application lifespan context."""

    def __init__(self):
        self.initialized = False

    async def initialize(self):
        """Initialize the NTP dependency check."""
        if not self.initialized:
            logger.info("Initializing NTP time service...")
            try:
                # Probe NTP connectivity
                time_info = client.get_current_time()
                logger.info(f"NTP service initialization successful, server: {time_info.get('ntp_server', 'Unknown')}")
                self.initialized = True
            except Exception as e:
                logger.error(f"NTP service initialization failed: {e}")
                raise


@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[AppContext]:
    """Manage server lifespan."""
    context = AppContext()

    try:
        logger.info("Starting MCP-NTP server")
        await context.initialize()
        yield context
    finally:
        logger.info("Stopping MCP-NTP server")


def create_mcp_server(ntp_url: str = None) -> Server:
    """Create an MCP server instance with an optional default ntp_url."""

    async def list_resources(
        context: ServerRequestContext,
        params: PaginatedRequestParams | None,
    ) -> ListResourcesResult:
        """List available resources."""
        return ListResourcesResult(
            resources=[
                Resource(
                uri="ntp://time",
                name="NTP Server Time Informations",
                mime_type="application/json",
                description="Get current NTP server time information, including timestamp, local time comparison, etc."
                )
            ]
        )

    async def read_resource(
        context: ServerRequestContext,
        params: ReadResourceRequestParams,
    ) -> ReadResourceResult:
        """Read resource contents."""
        if params.uri == "ntp://time":
            try:
                time_info = client.get_current_time(ntp_server=ntp_url)
                return ReadResourceResult(
                    contents=[
                        TextResourceContents(
                            uri=params.uri,
                            mime_type="application/json",
                            text=json.dumps(time_info, ensure_ascii=False, indent=2),
                        )
                    ]
                )
            except Exception as e:
                logger.error(f"Failed to get NTP time information: {e}")
                return ReadResourceResult(
                    contents=[
                        TextResourceContents(
                            uri=params.uri,
                            mime_type="text/plain",
                            text=f"Error: {str(e)}",
                        )
                    ]
                )
        return ReadResourceResult(
            contents=[
                TextResourceContents(
                    uri=params.uri,
                    mime_type="text/plain",
                    text=f"Unknown resource URI: {params.uri}",
                )
            ]
        )

    async def list_tools(
        context: ServerRequestContext,
        params: PaginatedRequestParams | None,
    ) -> ListToolsResult:
        """List available tools."""
        return ListToolsResult(
            tools=[
                Tool(
                name="get_current_time",
                description="Get current time from NTP server",
                input_schema={
                    "type": "object",
                    "properties": {
                        "ntp_server": {
                            "type": "string",
                            "description": "NTP server address (optional, if not provided, the environment variable or request header configuration will be used)",
                        }
                    },
                    "required": []
                }
                )
            ]
        )

    async def call_tool(
        context: ServerRequestContext,
        params: CallToolRequestParams,
    ) -> CallToolResult:
        """Handle tool calls."""
        try:
            if params.name == "get_current_time":
                arguments = params.arguments or {}
                ntp_server = arguments.get("ntp_server", ntp_url)
                result = client.get_current_time(ntp_server=ntp_server)
                return CallToolResult(
                    content=[
                        TextContent(
                            type="text",
                            text=json.dumps(result, ensure_ascii=False, indent=2),
                        )
                    ]
                )
            raise ValueError(f"Unknown tool: {params.name}")

        except Exception as e:
            logger.error(f"Tool execution error {params.name}: {e}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"Error: {str(e)}")],
                is_error=True,
            )

    return Server(
        "mcp-ntp",
        version=__version__,
        lifespan=server_lifespan,
        on_list_resources=list_resources,
        on_read_resource=read_resource,
        on_list_tools=list_tools,
        on_call_tool=call_tool,
    )
