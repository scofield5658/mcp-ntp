"""
MCP-NTP 服务器实现
使用原生 MCP Server 支持 stdio 和 sse 传输方式
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
    """应用上下文"""

    def __init__(self):
        self.initialized = False

    async def initialize(self):
        """初始化连接"""
        if not self.initialized:
            logger.info("Initializing NTP time service...")
            try:
                # 测试NTP连接
                time_info = client.get_current_time()
                logger.info(f"NTP service initialization successful, server: {time_info.get('ntp_server', 'Unknown')}")
                self.initialized = True
            except Exception as e:
                logger.error(f"NTP service initialization failed: {e}")
                raise


@asynccontextmanager
async def server_lifespan(server: Server) -> AsyncIterator[AppContext]:
    """服务器生命周期管理"""
    context = AppContext()

    try:
        logger.info("Starting MCP-NTP server")
        await context.initialize()
        yield context
    finally:
        logger.info("Stopping MCP-NTP server")


def create_mcp_server(ntp_url: str = None) -> Server:
    """创建 MCP 服务器实例，支持动态 ntp_url"""

    async def list_resources(
        context: ServerRequestContext,
        params: PaginatedRequestParams | None,
    ) -> ListResourcesResult:
        """列出可用资源"""
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
        """读取资源内容"""
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
        """列出可用工具"""
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
        """调用工具"""
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
