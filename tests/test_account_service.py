"""Tests for Kiwoom account service wrappers."""

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

account_module = importlib.import_module("src.services.account")


class DummyResponse:
    """Simple response stub for service-layer tests."""

    def __init__(self, payload: Any, headers: dict[str, str] | None = None, status_code: int = 200):
        self._payload = payload
        self.headers = headers or {}
        self.status_code = status_code

    def json(self) -> Any:
        return self._payload


class DummyClient:
    """Simple client stub that records outbound POST calls."""

    def __init__(self, payload: Any, headers: dict[str, str] | None = None):
        self._payload = payload
        self._headers = headers or {}
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
        return DummyResponse(self._payload, headers=self._headers)


def test_business_error_is_not_reported_as_success() -> None:
    """Non-zero Kiwoom return codes should not be reported as successful."""

    client = DummyClient(
        {
            "return_code": 20,
            "return_msg": "[2000](571489:장이 열리지 않는 날입니다.)",
        }
    )

    result = asyncio.run(
        account_module.get_orderable_amount(
            client,
            stk_cd="005490",
            trde_tp="2",
            uv="343500",
        )
    )

    assert result["success"] is False
    assert result["return_code"] == 20
    assert "장이 열리지 않는 날입니다" in result["error"]
    assert result["orderable_amount_data"] == []


def test_execution_info_uses_filled_order_api() -> None:
    """Execution history wrapper should call the ka10076 endpoint contract."""

    client = DummyClient(
        {
            "cntr": [],
            "return_code": 0,
            "return_msg": "조회가 완료되었습니다.",
        }
    )

    result = asyncio.run(
        account_module.get_execution_info(
            client,
            qry_tp="0",
            sell_tp="0",
            stex_tp="0",
        )
    )

    assert result["success"] is True
    assert client.calls[0]["headers"]["api-id"] == "ka10076"
    assert client.calls[0]["json"] == {
        "qry_tp": "0",
        "sell_tp": "0",
        "stex_tp": "0",
    }


def test_order_execution_status_uses_kt00009_contract() -> None:
    """Order/execution status wrapper should use the kt00009 request schema."""

    client = DummyClient(
        {
            "acnt_ord_cntr_prst_array": [],
            "return_code": 0,
            "return_msg": "조회가 완료되었습니다.",
        }
    )

    result = asyncio.run(
        account_module.get_order_execution_status(
            client,
            stk_bond_tp="1",
            mrkt_tp="0",
            sell_tp="0",
            qry_tp="0",
            dmst_stex_tp="KRX",
        )
    )

    assert result["success"] is True
    assert client.calls[0]["headers"]["api-id"] == "kt00009"
    assert client.calls[0]["json"] == {
        "stk_bond_tp": "1",
        "mrkt_tp": "0",
        "sell_tp": "0",
        "qry_tp": "0",
        "dmst_stex_tp": "KRX",
    }
