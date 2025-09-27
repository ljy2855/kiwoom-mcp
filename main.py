"""Entrypoint for running the Kiwoom MCP server."""

from src.mcp_server import mcp_server


def main() -> None:
    """Start the MCP server."""
    mcp_server.run()


if __name__ == "__main__":
    main()
