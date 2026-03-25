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
os.environ.setdefault("KIWOOM_USE_MOCK", "false")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

mcp_server_module = importlib.import_module("src.mcp_server")
account_module = importlib.import_module("src.services.account")
strategy_module = importlib.import_module("src.services.strategy")


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
            assert "get_market_snapshot" in tool_names
            assert "plan_intraday_momentum_strategy" in tool_names
            assert "run_mock_intraday_momentum_strategy" in tool_names
            assert "place_stock_buy_order" in tool_names
            assert "cancel_stock_order" in tool_names
            assert "get_unexecuted_orders" in tool_names

            execution_tool = tools["get_execution_info"]
            assert execution_tool.parameters["properties"]["sell_tp"]["enum"] == ["0", "1", "2"]
            assert execution_tool.description.startswith("API `ka10076`")

            buy_order_tool = tools["place_stock_buy_order"]
            assert buy_order_tool.parameters["properties"]["confirm_live_order"]["const"] is True
            assert buy_order_tool.parameters["properties"]["order_type_code"]["enum"][0] == "0"
            assert buy_order_tool.parameters["properties"]["dmst_stex_tp"]["default"] == "KRX"
            assert buy_order_tool.description.startswith("ORDER SUBMISSION: API `kt10000`")

            strategy_tool = tools["run_mock_intraday_momentum_strategy"]
            assert strategy_tool.parameters["properties"]["confirm_mock_strategy_execution"]["const"] is True
            assert strategy_tool.parameters["properties"]["position_budget_pct"]["maximum"] == 50
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


def test_strategy_tool_is_callable(monkeypatch) -> None:
    """The strategy planning tool should be callable through the FastMCP client."""

    async def fake_plan_strategy(client, settings, **kwargs):
        return {"status": "ok", "strategy": "dry-run", "kwargs": kwargs}

    monkeypatch.setattr(
        strategy_module,
        "plan_intraday_momentum_strategy",
        fake_plan_strategy,
    )

    async def run_test() -> None:
        server = mcp_server_module.create_mcp_server()
        try:
            async with Client(server.mcp) as client:
                result = await client.call_tool(
                    "plan_intraday_momentum_strategy",
                    {
                        "leaders_limit": 8,
                        "candidate_limit": 4,
                        "max_positions": 3,
                        "max_new_positions": 1,
                        "position_budget_pct": 10,
                    },
                )
                assert result.is_error is False
                assert result.data["status"] == "ok"
                assert result.data["kwargs"]["leaders_limit"] == 8
        finally:
            await server.close()

    asyncio.run(run_test())
