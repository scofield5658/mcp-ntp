"""
MCP-NTP 服务器实现
使用原生 MCP Server 支持 stdio 和 sse 传输方式
"""

import json
import logging
from collections.abc import Sequence
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator

from mcp.server import Server
from mcp.types import Resource, TextContent, Tool

from . import client

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

    # 创建服务器实例
    app = Server("mcp-ntp", lifespan=server_lifespan)

    @app.list_resources()
    async def list_resources() -> list[Resource]:
        """列出可用资源"""
        return [
            Resource(
                uri="ntp://time",
                name="NTP Server Time Informations",
                mimeType="application/json",
                description="Get current NTP server time information, including timestamp, local time comparison, etc."
            )
        ]

    @app.read_resource()
    async def read_resource(uri: str) -> tuple[str, str]:
        """读取资源内容"""
        if uri == "ntp://time":
            try:
                time_info = client.get_current_time(ntp_server=ntp_url)
                return (
                    json.dumps(time_info, ensure_ascii=False, indent=2),
                    "application/json"
                )
            except Exception as e:
                logger.error(f"Failed to get NTP time information: {e}")
                return f"Error: {str(e)}", "text/plain"
        else:
            return f"Unknown resource URI: {uri}", "text/plain"

    @app.list_tools()
    async def list_tools() -> list[Tool]:
        """列出可用工具"""
        return [
            Tool(
                name="get_current_time",
                description="Get current time from NTP server",
                inputSchema={
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

    @app.call_tool()
    async def call_tool(name: str, arguments: Any) -> Sequence[TextContent]:
        """调用工具"""
        try:
            if name == "get_current_time":
                ntp_server = arguments.get("ntp_server", ntp_url)
                result = client.get_current_time(ntp_server=ntp_server)
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(result, ensure_ascii=False, indent=2)
                    )
                ]
            else:
                raise ValueError(f"Unknown tool: {name}")

        except Exception as e:
            logger.error(f"Tool execution error {name}: {e}")
            return [
                TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )
            ]

    return app
