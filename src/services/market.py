"""Market data service functions for Kiwoom OpenAPI."""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import httpx

from ..constants import APIInfo, MARKET_DATA_APIS, RANKING_APIS, SECTOR_APIS
from .kiwoom_client import KiwoomClient

KST = ZoneInfo("Asia/Seoul")


def _normalize_return_code(value: Any) -> int | None:
    """Normalize Kiwoom business return codes into integers when possible."""

    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _extract_business_status(response_data: Any) -> tuple[int | None, str | None]:
    """Extract Kiwoom business status from a response payload."""

    if not isinstance(response_data, dict):
        return None, None
    return (
        _normalize_return_code(response_data.get("return_code")),
        response_data.get("return_msg"),
    )


def _build_result(
    *,
    api_info: APIInfo,
    context: dict[str, Any],
    payload_key: str,
    payload: Any,
    return_code: int | None = None,
    return_msg: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    """Create a normalized result payload for market-data wrappers."""

    success = error is None
    result = {
        "success": success,
        "status_code": 200,
        "api_id": api_info.api_id,
        "api_name": api_info.name,
        **context,
        payload_key: payload,
    }

    if isinstance(payload, list):
        result["total_records"] = len(payload)
    else:
        result["total_records"] = 1 if payload else 0

    if return_code is not None:
        result["return_code"] = return_code
    if return_msg is not None:
        result["return_msg"] = return_msg

    if success:
        result["message"] = return_msg or "Successfully retrieved market data"
    else:
        result["error"] = error
        result["message"] = return_msg or error or "Kiwoom API returned a business error"

    return result


def _build_exception_result(
    *,
    api_info: APIInfo,
    context: dict[str, Any],
    payload_key: str,
    empty_payload: Any,
    message: str,
    error: Exception,
) -> dict[str, Any]:
    """Create a consistent result for transport or runtime errors."""

    return {
        "success": False,
        "status_code": None,
        "api_id": api_info.api_id,
        "api_name": api_info.name,
        **context,
        payload_key: empty_payload,
        "total_records": 0,
        "error": str(error),
        "message": message,
        "note": "This requires proper Kiwoom API endpoint configuration",
    }


async def _post_market_query(
    client: KiwoomClient,
    *,
    api_info: APIInfo,
    request_data: dict[str, Any],
    context: dict[str, Any],
    payload_key: str,
    payload_extractor: Any,
    empty_payload: Any,
    exception_message: str,
) -> dict[str, Any]:
    """Execute a single Kiwoom market-data request and normalize the response."""

    try:
        response = None
        for attempt in range(3):
            try:
                response = await client.post(
                    api_info.url,
                    headers={"api-id": api_info.api_id, "cont-yn": "N"},
                    json=request_data,
                )
                break
            except httpx.HTTPStatusError as error:
                if error.response.status_code != 429 or attempt == 2:
                    raise
                await asyncio.sleep(0.2 * (attempt + 1))
        if response is None:
            raise RuntimeError("No response returned from Kiwoom market query")
        response_data = response.json()
        return_code, return_msg = _extract_business_status(response_data)

        if return_code not in (None, 0):
            return _build_result(
                api_info=api_info,
                context=context,
                payload_key=payload_key,
                payload=empty_payload,
                return_code=return_code,
                return_msg=return_msg,
                error=return_msg or f"Kiwoom API returned return_code={return_code}",
            )

        return _build_result(
            api_info=api_info,
            context=context,
            payload_key=payload_key,
            payload=payload_extractor(response_data),
            return_code=return_code,
            return_msg=return_msg,
        )
    except Exception as error:
        return _build_exception_result(
            api_info=api_info,
            context=context,
            payload_key=payload_key,
            empty_payload=empty_payload,
            message=exception_message,
            error=error,
        )


def _extract_list(*keys: str):
    """Return an extractor that yields the first list found in the given keys."""

    def extractor(response_data: Any) -> list[dict[str, Any]]:
        if not isinstance(response_data, dict):
            return []
        for key in keys:
            value = response_data.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
        return []

    return extractor


def _extract_dict(response_data: Any) -> dict[str, Any]:
    """Return the response payload as a dict without business-status keys."""

    if not isinstance(response_data, dict):
        return {}
    return {
        key: value
        for key, value in response_data.items()
        if key not in {"return_code", "return_msg"}
    }


def _limit_rows(rows: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    """Return a bounded number of rows from a result set."""

    if limit <= 0:
        return []
    return rows[:limit]


async def get_index_snapshot(
    client: KiwoomClient,
    *,
    inds_cd: str,
    mrkt_tp: str,
) -> dict[str, Any]:
    """Get a sector or market index snapshot with intraday points."""

    return await _post_market_query(
        client,
        api_info=SECTOR_APIS["ka20001"],
        request_data={"inds_cd": inds_cd, "mrkt_tp": mrkt_tp},
        context={"inds_cd": inds_cd, "mrkt_tp": mrkt_tp},
        payload_key="index_snapshot",
        payload_extractor=_extract_dict,
        empty_payload={},
        exception_message="Index snapshot query failed",
    )


async def get_sector_overview(
    client: KiwoomClient,
    *,
    inds_cd: str = "001",
    limit: int = 10,
) -> dict[str, Any]:
    """Get the overall sector leaderboard for a given market anchor code."""

    result = await _post_market_query(
        client,
        api_info=SECTOR_APIS["ka20003"],
        request_data={"inds_cd": inds_cd},
        context={"inds_cd": inds_cd, "limit": limit},
        payload_key="sector_rows",
        payload_extractor=_extract_list("all_inds_idex"),
        empty_payload=[],
        exception_message="Sector overview query failed",
    )
    result["sector_rows"] = _limit_rows(result.get("sector_rows", []), limit)
    result["total_records"] = len(result["sector_rows"])
    return result


async def get_top_gainers(
    client: KiwoomClient,
    *,
    mrkt_tp: str = "000",
    limit: int = 20,
) -> dict[str, Any]:
    """Get top gainers with ETF/ETN excluded by default."""

    result = await _post_market_query(
        client,
        api_info=RANKING_APIS["ka10027"],
        request_data={
            "sort_tp": "1",
            "trde_qty_cnd": "0010",
            "stk_cnd": "16",
            "crd_cnd": "0",
            "updown_incls": "0",
            "pric_cnd": "8",
            "trde_prica_cnd": "10",
            "mrkt_tp": mrkt_tp,
            "stex_tp": "1",
        },
        context={"mrkt_tp": mrkt_tp, "limit": limit},
        payload_key="gainer_rows",
        payload_extractor=_extract_list("pred_pre_flu_rt_upper"),
        empty_payload=[],
        exception_message="Top gainers query failed",
    )
    result["gainer_rows"] = _limit_rows(result.get("gainer_rows", []), limit)
    result["total_records"] = len(result["gainer_rows"])
    return result


async def get_top_volume_leaders(
    client: KiwoomClient,
    *,
    mrkt_tp: str = "000",
    limit: int = 20,
) -> dict[str, Any]:
    """Get top-volume names with ETF/ETN excluded by default."""

    result = await _post_market_query(
        client,
        api_info=RANKING_APIS["ka10030"],
        request_data={
            "sort_tp": "1",
            "mang_stk_incls": "16",
            "crd_tp": "0",
            "trde_qty_tp": "10",
            "pric_tp": "2",
            "trde_prica_tp": "10",
            "mrkt_open_tp": "0",
            "mrkt_tp": mrkt_tp,
            "stex_tp": "1",
        },
        context={"mrkt_tp": mrkt_tp, "limit": limit},
        payload_key="volume_rows",
        payload_extractor=_extract_list("tdy_trde_qty_upper"),
        empty_payload=[],
        exception_message="Top volume query failed",
    )
    result["volume_rows"] = _limit_rows(result.get("volume_rows", []), limit)
    result["total_records"] = len(result["volume_rows"])
    return result


async def get_top_value_leaders(
    client: KiwoomClient,
    *,
    mrkt_tp: str = "000",
    limit: int = 20,
) -> dict[str, Any]:
    """Get top traded-value names."""

    result = await _post_market_query(
        client,
        api_info=RANKING_APIS["ka10032"],
        request_data={
            "mang_stk_incls": "1",
            "mrkt_tp": mrkt_tp,
            "stex_tp": "1",
        },
        context={"mrkt_tp": mrkt_tp, "limit": limit},
        payload_key="value_rows",
        payload_extractor=_extract_list("trde_prica_upper"),
        empty_payload=[],
        exception_message="Top traded value query failed",
    )
    result["value_rows"] = _limit_rows(result.get("value_rows", []), limit)
    result["total_records"] = len(result["value_rows"])
    return result


async def get_stock_quote(client: KiwoomClient, *, stock_code: str) -> dict[str, Any]:
    """Get a quote snapshot for one stock."""

    return await _post_market_query(
        client,
        api_info=MARKET_DATA_APIS["ka10007"],
        request_data={"stk_cd": stock_code},
        context={"stock_code": stock_code},
        payload_key="quote",
        payload_extractor=_extract_dict,
        empty_payload={},
        exception_message="Stock quote query failed",
    )


async def get_stock_orderbook(client: KiwoomClient, *, stock_code: str) -> dict[str, Any]:
    """Get the orderbook for one stock."""

    return await _post_market_query(
        client,
        api_info=MARKET_DATA_APIS["ka10004"],
        request_data={"stk_cd": stock_code},
        context={"stock_code": stock_code},
        payload_key="orderbook",
        payload_extractor=_extract_dict,
        empty_payload={},
        exception_message="Stock orderbook query failed",
    )


async def get_stock_daily_bars(
    client: KiwoomClient,
    *,
    stock_code: str,
    limit: int = 20,
) -> dict[str, Any]:
    """Get recent daily bars for one stock."""

    result = await _post_market_query(
        client,
        api_info=MARKET_DATA_APIS["ka10005"],
        request_data={"stk_cd": stock_code},
        context={"stock_code": stock_code, "limit": limit},
        payload_key="daily_bars",
        payload_extractor=_extract_list("stk_ddwkmm"),
        empty_payload=[],
        exception_message="Stock daily-bar query failed",
    )
    result["daily_bars"] = _limit_rows(result.get("daily_bars", []), limit)
    result["total_records"] = len(result["daily_bars"])
    return result


async def get_stock_detail_bundle(
    client: KiwoomClient,
    *,
    stock_code: str,
    bar_limit: int = 5,
) -> dict[str, Any]:
    """Get quote, orderbook, and recent daily bars for one stock."""

    quote_result = await get_stock_quote(client, stock_code=stock_code)
    orderbook_result = await get_stock_orderbook(client, stock_code=stock_code)
    daily_bars_result = await get_stock_daily_bars(
        client,
        stock_code=stock_code,
        limit=bar_limit,
    )

    success = all(
        [
            quote_result.get("success", False),
            orderbook_result.get("success", False),
            daily_bars_result.get("success", False),
        ]
    )

    return {
        "success": success,
        "stock_code": stock_code,
        "quote_result": quote_result,
        "orderbook_result": orderbook_result,
        "daily_bars_result": daily_bars_result,
        "quote": quote_result.get("quote", {}),
        "orderbook": orderbook_result.get("orderbook", {}),
        "daily_bars": daily_bars_result.get("daily_bars", []),
    }


async def get_market_snapshot(
    client: KiwoomClient,
    *,
    watchlist: list[str] | None = None,
    leaders_limit: int = 10,
    sector_limit: int = 10,
) -> dict[str, Any]:
    """Build an aggregated market snapshot suitable for hourly automation."""

    watchlist_codes = []
    for code in watchlist or []:
        if code and code not in watchlist_codes:
            watchlist_codes.append(code)

    kospi_result = await get_index_snapshot(client, inds_cd="001", mrkt_tp="000")
    kosdaq_result = await get_index_snapshot(client, inds_cd="101", mrkt_tp="101")
    sector_result = await get_sector_overview(client, inds_cd="001", limit=sector_limit)
    gainers_result = await get_top_gainers(client, mrkt_tp="000", limit=leaders_limit)
    volume_result = await get_top_volume_leaders(client, mrkt_tp="000", limit=leaders_limit)
    value_result = await get_top_value_leaders(client, mrkt_tp="000", limit=leaders_limit)

    watchlist_details = []
    for stock_code in watchlist_codes:
        watchlist_details.append(
            await get_stock_detail_bundle(client, stock_code=stock_code)
        )

    success = all(
        [
            kospi_result.get("success", False),
            kosdaq_result.get("success", False),
            sector_result.get("success", False),
            gainers_result.get("success", False),
            volume_result.get("success", False),
            value_result.get("success", False),
        ]
    )

    return {
        "success": success,
        "generated_at": datetime.now(KST).isoformat(),
        "leaders_limit": leaders_limit,
        "sector_limit": sector_limit,
        "watchlist": watchlist_codes,
        "indices": {
            "kospi": kospi_result.get("index_snapshot", {}),
            "kosdaq": kosdaq_result.get("index_snapshot", {}),
        },
        "leaders": {
            "gainers": gainers_result.get("gainer_rows", []),
            "volume": volume_result.get("volume_rows", []),
            "value": value_result.get("value_rows", []),
        },
        "sector_rows": sector_result.get("sector_rows", []),
        "watchlist_details": watchlist_details,
        "sources": {
            "kospi": kospi_result,
            "kosdaq": kosdaq_result,
            "sector": sector_result,
            "gainers": gainers_result,
            "volume": volume_result,
            "value": value_result,
        },
    }


__all__ = [
    "get_index_snapshot",
    "get_market_snapshot",
    "get_sector_overview",
    "get_stock_daily_bars",
    "get_stock_detail_bundle",
    "get_stock_orderbook",
    "get_stock_quote",
    "get_top_gainers",
    "get_top_value_leaders",
    "get_top_volume_leaders",
]
