"""Tests for Kiwoom live order service wrappers."""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path
from typing import Any

os.environ.setdefault("KIWOOM_APPKEY", "dummy-appkey")
os.environ.setdefault("KIWOOM_SECRETKEY", "dummy-secretkey")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

order_module = importlib.import_module("src.services.order")


class DummyResponse:
    """Simple response stub for order service tests."""

    def __init__(self, payload: Any, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code
        self.headers: dict[str, str] = {}

    def json(self) -> Any:
        return self._payload


class DummyClient:
    """Client stub that records outbound POST calls."""

    def __init__(self, payload: Any):
        self._payload = payload
        self.calls: list[dict[str, Any]] = []

    async def post(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> DummyResponse:
        self.calls.append(
            {
                "path": path,
                "headers": headers or {},
                "params": params,
                "json": json,
                "data": data,
            }
        )
        return DummyResponse(self._payload)


def test_buy_order_uses_kt10000_contract() -> None:
    """Buy orders should map to the live kt10000 request schema."""

    client = DummyClient({"dmst_stex_tp": "KRX"})

    result = asyncio.run(
        order_module.place_stock_buy_order(
            client,
            stk_cd="005930",
            ord_qty="1",
            order_type_code="0",
            ord_uv="70000",
        )
    )

    assert result["success"] is True
    assert client.calls[0]["headers"]["api-id"] == "kt10000"
    assert client.calls[0]["json"] == {
        "stk_cd": "005930",
        "ord_qty": "1",
        "trde_tp": "0",
        "dmst_stex_tp": "KRX",
        "ord_uv": "70000",
    }


def test_cancel_order_business_error_is_reported() -> None:
    """Business errors from live order endpoints should not be reported as success."""

    client = DummyClient(
        {
            "return_code": 2,
            "return_msg": "입력 값 오류입니다.",
        }
    )

    result = asyncio.run(
        order_module.cancel_stock_order(
            client,
            orig_ord_no="1234567",
            stk_cd="005930",
            cncl_qty="0",
        )
    )

    assert result["success"] is False
    assert result["return_code"] == 2
    assert result["message"] == "입력 값 오류입니다."
    assert result["cancel_order_result"]["return_msg"] == "입력 값 오류입니다."
    assert client.calls[0]["json"]["dmst_stex_tp"] == "KRX"
