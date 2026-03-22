"""Smoke tests for the Kiwoom MCP server."""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path

from fastmcp import Client

os.environ.setdefault("KIWOOM_APPKEY", "dummy-appkey")
os.environ.setdefault("KIWOOM_SECRETKEY", "dummy-secretkey")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

mcp_server_module = importlib.import_module("src.mcp_server")
account_module = importlib.import_module("src.services.account")


def test_server_registers_expected_tools() -> None:
    """The server should expose the expected MCP tools."""

    async def run_test() -> None:
        server = mcp_server_module.create_mcp_server()
        try:
            tools = await server.mcp.get_tools()
            tool_names = set(tools)
            assert "get_account_current_status" in tool_names
            assert "get_account_evaluation" in tool_names
            assert "get_order_execution_status" in tool_names
            assert "place_stock_buy_order" in tool_names
            assert "cancel_stock_order" in tool_names
            assert "get_unexecuted_orders" in tool_names

            execution_tool = tools["get_execution_info"]
            assert execution_tool.parameters["properties"]["sell_tp"]["enum"] == ["0", "1", "2"]
            assert execution_tool.description.startswith("API `ka10076`")

            buy_order_tool = tools["place_stock_buy_order"]
            assert buy_order_tool.parameters["properties"]["confirm_live_order"]["const"] is True
            assert buy_order_tool.parameters["properties"]["order_type_code"]["enum"][0] == "0"
            assert buy_order_tool.description.startswith("LIVE ORDER: API `kt10000`")
        finally:
            await server.close()

    asyncio.run(run_test())


def test_mcp_tool_call_returns_structured_data(monkeypatch) -> None:
    """A tool should be callable through the FastMCP client."""

    async def fake_get_account_current_status(client):
        return {"status": "ok", "source": "smoke-test"}

    monkeypatch.setattr(
        account_module,
        "get_account_current_status",
        fake_get_account_current_status,
    )

    async def run_test() -> None:
        server = mcp_server_module.create_mcp_server()
        try:
            async with Client(server.mcp) as client:
                result = await client.call_tool("get_account_current_status", {})
                assert result.is_error is False
                assert result.data == {"status": "ok", "source": "smoke-test"}
        finally:
            await server.close()

    asyncio.run(run_test())
