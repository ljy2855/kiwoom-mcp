"""Tests for the intraday strategy planner."""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path

from src.config import Settings

os.environ.setdefault("KIWOOM_APPKEY", "dummy-appkey")
os.environ.setdefault("KIWOOM_SECRETKEY", "dummy-secretkey")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

strategy_module = importlib.import_module("src.services.strategy")


async def fake_account_evaluation(client):
    return {
        "success": True,
        "evaluation_data": [
            {
                "tot_est_amt": "1000000",
                "entr": "500000",
                "stk_acnt_evlt_prst": [],
            }
        ],
    }


async def fake_unexecuted_orders(client, all_stk_tp, trde_tp, stex_tp, stk_cd=""):
    return {
        "success": True,
        "unexecuted_orders_data": [],
    }


async def fake_market_snapshot(client, *, watchlist=None, leaders_limit=10):
    return {
        "success": True,
        "indices": {
            "kospi": {"flu_rt": "+1.20", "rising": "600", "fall": "300"},
            "kosdaq": {"flu_rt": "+1.00", "rising": "700", "fall": "350"},
        },
        "leaders": {
            "gainers": [{"stk_cd": "005930", "stk_nm": "삼성전자"}],
            "volume": [{"stk_cd": "005930", "stk_nm": "삼성전자"}],
            "value": [{"stk_cd": "005930", "stk_nm": "삼성전자"}],
        },
        "sector_rows": [{"stk_cd": "001", "stk_nm": "종합(KOSPI)"}],
        "watchlist_details": [],
    }


async def fake_stock_detail_bundle(client, *, stock_code, bar_limit=5):
    return {
        "success": True,
        "stock_code": stock_code,
        "quote": {
            "stk_cd": stock_code,
            "stk_nm": "삼성전자",
            "cur_prc": "+70000",
            "flu_rt": "+2.94",
            "open_pric": "+69000",
            "high_pric": "+70500",
            "pred_close_pric": "68000",
        },
        "orderbook": {
            "sel_fpr_bid": "+70000",
            "buy_fpr_bid": "+69900",
            "tot_sel_req": "10000",
            "tot_buy_req": "18000",
        },
        "daily_bars": [
            {"date": "20260325", "close_pric": "+70000"},
            {"date": "20260324", "high_pric": "+69000", "close_pric": "+68000"},
        ],
    }


async def fake_place_stock_buy_order(client, **kwargs):
    return {
        "success": True,
        "message": "mock buy submitted",
        "kwargs": kwargs,
    }


def test_strategy_planner_generates_buy_action(monkeypatch) -> None:
    """Risk-on conditions with a strong candidate should yield a buy plan."""

    monkeypatch.setattr(strategy_module.account, "get_account_evaluation", fake_account_evaluation)
    monkeypatch.setattr(strategy_module.account, "get_unexecuted_orders", fake_unexecuted_orders)
    monkeypatch.setattr(strategy_module.market, "get_market_snapshot", fake_market_snapshot)
    monkeypatch.setattr(strategy_module.market, "get_stock_detail_bundle", fake_stock_detail_bundle)

    result = asyncio.run(
        strategy_module.plan_intraday_momentum_strategy(
            client=object(),
            settings=Settings(KIWOOM_APPKEY="dummy-appkey", KIWOOM_SECRETKEY="dummy-secretkey"),
            watchlist=["005930"],
            leaders_limit=5,
            candidate_limit=3,
            max_positions=3,
            max_new_positions=1,
            position_budget_pct=10,
        )
    )

    assert result["success"] is True
    assert result["regime"]["risk_on"] is True
    assert result["planned_actions"][0]["action"] == "buy"
    assert result["planned_actions"][0]["stock_code"] == "005930"
    assert result["planned_actions"][0]["quantity"] >= 1


def test_strategy_executor_submits_mock_buy_orders(monkeypatch) -> None:
    """Execution mode should submit mock buy orders when allowed."""

    monkeypatch.setattr(strategy_module.account, "get_account_evaluation", fake_account_evaluation)
    monkeypatch.setattr(strategy_module.account, "get_unexecuted_orders", fake_unexecuted_orders)
    monkeypatch.setattr(strategy_module.market, "get_market_snapshot", fake_market_snapshot)
    monkeypatch.setattr(strategy_module.market, "get_stock_detail_bundle", fake_stock_detail_bundle)
    monkeypatch.setattr(strategy_module.order, "place_stock_buy_order", fake_place_stock_buy_order)

    result = asyncio.run(
        strategy_module.plan_intraday_momentum_strategy(
            client=object(),
            settings=Settings(
                KIWOOM_USE_MOCK="true",
                KIWOOM_MOCK_APPKEY="dummy-mock-appkey",
                KIWOOM_MOCK_SECRETKEY="dummy-mock-secretkey",
            ),
            watchlist=["005930"],
            execute_orders=True,
            confirm_mock_orders=True,
        )
    )

    assert result["environment"]["execution_allowed"] is True
    assert len(result["executed_orders"]) == 1
    assert result["executed_orders"][0]["order_result"]["success"] is True
    assert result["executed_orders"][0]["action"]["stock_code"] == "005930"
