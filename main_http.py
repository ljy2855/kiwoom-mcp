"""HTTP server entrypoint for running the Kiwoom MCP server."""

import asyncio
from src.mcp_server import mcp_server


def main() -> None:
    """Start the MCP server as HTTP server."""
    # Run as HTTP server on localhost:8000
    asyncio.run(mcp_server.mcp.run_http_async(host="localhost", port=8000,transport="streamable-http"))


if __name__ == "__main__":
    main()
