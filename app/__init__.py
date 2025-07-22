import asyncio
import logging
import os
import sys
from importlib.metadata import PackageNotFoundError, version

import click
from dotenv import load_dotenv

try:
    __version__ = version("mcp-ntp")
except PackageNotFoundError:
    __version__ = "0.1.0"


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """设置日志配置"""
    logger = logging.getLogger("mcp-ntp")
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


@click.version_option(__version__, prog_name="mcp-ntp")
@click.command()
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="增加详细程度 (可多次使用)",
)
@click.option(
    "--env-file",
    type=click.Path(exists=True, dir_okay=False),
    help=".env 文件路径"
)
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="传输方式 (stdio 或 sse)",
)
@click.option(
    "--port",
    default=18002,
    help="SSE 传输方式的监听端口",
)
@click.option(
    "--host",
    default="0.0.0.0",
    help="SSE 传输方式的监听地址",
)
def main(
    verbose: int,
    env_file: str | None,
    transport: str,
    port: int,
    host: str,
) -> None:
    """MCP-NTP 服务器

    支持 stdio 和 sse 两种传输方式。
    """
    # 设置日志级别
    if verbose == 1:
        current_logging_level = logging.INFO
    elif verbose >= 2:
        current_logging_level = logging.DEBUG
    else:
        current_logging_level = logging.WARNING

    logger = setup_logging(current_logging_level)
    logger.debug(f"Log level set to: {logging.getLevelName(current_logging_level)}")

    # 加载环境变量
    if env_file:
        logger.debug(f"Loading environment variables from file: {env_file}")
        load_dotenv(env_file, override=True)
    else:
        logger.debug("Attempting to load environment variables from default .env file")
        load_dotenv(override=True)

    def was_option_provided(ctx: click.Context, param_name: str) -> bool:
        return (
            ctx.get_parameter_source(param_name)
            != click.core.ParameterSource.DEFAULT_MAP
            and ctx.get_parameter_source(param_name)
            != click.core.ParameterSource.DEFAULT
        )

    # 确定最终的传输方式
    final_transport = os.getenv("TRANSPORT", transport).lower()
    if final_transport not in ["stdio", "sse"]:
        logger.warning(f"Invalid transport method '{final_transport}', using 'stdio'")
        final_transport = "stdio"

    logger.debug(f"Final transport method: {final_transport}")

    # 确定端口和主机
    final_port = int(os.getenv("PORT", port))
    final_host = os.getenv("HOST", host)

    if final_transport == "stdio":
        logger.info("Using STDIO transport method to start server")
        asyncio.run(run_stdio_server())
    else:
        logger.info(f"Using SSE transport method to start server, address: http://{final_host}:{final_port}/sse")
        asyncio.run(run_sse_server(final_host, final_port))


async def run_stdio_server():
    """运行 STDIO 传输模式的 MCP 服务器"""
    from mcp.server.stdio import stdio_server
    from .server import create_mcp_server

    import os
    ntp_url = os.getenv("NTP_DOMAIN_URL")
    app = create_mcp_server(ntp_url=ntp_url)

    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream, write_stream, app.create_initialization_options()
        )


async def run_sse_server(host: str, port: int):
    """运行 SSE 传输模式的 MCP 服务器"""
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.routing import Mount, Route
    from .server import create_mcp_server
    import uvicorn

    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        ntp_url = request.headers.get("ntp_url")
        app = create_mcp_server(ntp_url=ntp_url)
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await app.run(
                streams[0], streams[1], app.create_initialization_options()
            )

    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    config = uvicorn.Config(starlette_app, host=host, port=port)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
    main()
