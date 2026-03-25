"""Tests for the direct strategy-cycle runner."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

os.environ.setdefault("KIWOOM_APPKEY", "dummy-appkey")
os.environ.setdefault("KIWOOM_SECRETKEY", "dummy-secretkey")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

strategy_cycle_module = importlib.import_module("src.strategy_cycle")


def test_parse_watchlist_arg_deduplicates_codes() -> None:
    """Watchlist parsing should trim whitespace and drop duplicates."""

    result = strategy_cycle_module.parse_watchlist_arg("005930, 000660,005930")

    assert result == ["005930", "000660"]


def test_build_strategy_report_contains_key_sections() -> None:
    """The text report should include regime, actions, and candidates."""

    report = strategy_cycle_module.build_strategy_report(
        {
            "environment": {"mode": "mock", "execution_allowed": False},
            "regime": {"regime": "risk_on", "average_change_pct": 1.23, "breadth_score": 2.1},
            "portfolio": {
                "estimated_assets": 1_000_000,
                "cash_available": 500_000,
                "holding_count": 1,
                "open_order_count": 0,
                "position_budget": 100_000,
            },
            "planned_actions": [
                {
                    "action": "buy",
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "quantity": 1,
                    "order_type_code": "0",
                    "order_price": "70000",
                    "reason": "test",
                }
            ],
            "candidate_rows": [
                {
                    "stock_code": "005930",
                    "stock_name": "삼성전자",
                    "score": 10,
                    "eligible": True,
                    "day_change_pct": 2.3,
                    "reasons": [],
                }
            ],
        }
    )

    assert "Strategy cycle" in report
    assert "Planned actions: 1" in report
    assert "005930 삼성전자" in report
    assert "Top candidates: 1" in report


def test_main_refuses_mock_execution_in_live_mode(monkeypatch, capsys) -> None:
    """The CLI should refuse mock execution when KIWOOM_USE_MOCK=false."""

    monkeypatch.setenv("KIWOOM_USE_MOCK", "false")
    monkeypatch.setenv("KIWOOM_APPKEY", "dummy-appkey")
    monkeypatch.setenv("KIWOOM_SECRETKEY", "dummy-secretkey")

    exit_code = strategy_cycle_module.main(["--execute-mock-orders"])
    captured = capsys.readouterr()

    assert exit_code == 2
    assert "KIWOOM_USE_MOCK=true" in captured.err
