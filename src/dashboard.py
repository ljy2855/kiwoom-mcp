"""Dashboard web application for Kiwoom account and trade activity."""

from __future__ import annotations

import asyncio
import json
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Awaitable, Callable
from zoneinfo import ZoneInfo

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Route

from .config import Settings, get_settings
from .dashboard_template import DASHBOARD_HTML
from .services import account
from .services.kiwoom_client import KiwoomClient

KST = ZoneInfo("Asia/Seoul")

TableColumn = dict[str, str]
DashboardLoader = Callable[[KiwoomClient, Settings, str, str], Awaitable[dict[str, Any]]]


def _today_ymd() -> str:
    """Return the current date in Korea as YYYYMMDD."""

    return datetime.now(KST).strftime("%Y%m%d")


def _default_start_date(days: int = 30) -> str:
    """Return a default start date in Korea as YYYYMMDD."""

    return (datetime.now(KST) - timedelta(days=days)).strftime("%Y%m%d")


def _validate_ymd(value: str, field_name: str) -> str:
    """Validate that a string is a YYYYMMDD date."""

    if len(value) != 8 or not value.isdigit():
        raise ValueError(f"{field_name} must be YYYYMMDD")
    return value


def _pick_first(record: dict[str, Any], *keys: str) -> Any:
    """Return the first non-empty value for the given keys."""

    for key in keys:
        value = record.get(key)
        if value not in (None, ""):
            return value
    return ""


def _to_int(value: Any) -> int | None:
    """Convert a Kiwoom numeric field to an int when possible."""

    if isinstance(value, int):
        return value
    if value in (None, ""):
        return None
    text = str(value).replace(",", "").strip()
    if not text:
        return None
    if text.startswith(("+", "-")):
        sign = -1 if text[0] == "-" else 1
        text = text[1:]
    else:
        sign = 1
    if not text.isdigit():
        return None
    return sign * int(text)


def _tone_for_value(value: Any) -> str:
    """Classify a numeric value for UI styling."""

    number = _to_int(value)
    if number is None:
        return "neutral"
    if number > 0:
        return "positive"
    if number < 0:
        return "negative"
    return "neutral"


def _records(result: dict[str, Any], key: str) -> list[dict[str, Any]]:
    """Return list-like rows from a normalized service result."""

    value = result.get(key, [])
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _first_record(result: dict[str, Any], key: str) -> dict[str, Any]:
    """Return the first record from a result payload."""

    rows = _records(result, key)
    return rows[0] if rows else {}


def _nested_rows(rows: list[dict[str, Any]], nested_key: str) -> list[dict[str, Any]]:
    """Flatten nested list rows when Kiwoom returns summary + detail arrays."""

    flattened: list[dict[str, Any]] = []
    for row in rows:
        nested = row.get(nested_key)
        if isinstance(nested, list):
            flattened.extend(item for item in nested if isinstance(item, dict))
    return flattened


def _normalize_rows(rows: list[dict[str, Any]], column_aliases: dict[str, list[str]]) -> list[dict[str, Any]]:
    """Normalize raw Kiwoom records into a stable table shape."""

    normalized: list[dict[str, Any]] = []
    for row in rows:
        normalized.append(
            {
                key: _pick_first(row, *aliases)
                for key, aliases in column_aliases.items()
            }
        )
    return normalized


def _source_status(result: dict[str, Any]) -> tuple[str, str]:
    """Convert a Kiwoom response into a dashboard status."""

    message = str(result.get("return_msg") or result.get("message") or "")
    if "관련자료가없습니다" in message or "조회 내역이 없습니다" in message or "해당조회내역이 없습니다" in message:
        return "empty", "빈 결과"
    if not result.get("success", False):
        if "제공되지 않습니다" in message:
            return "unsupported", "모의 미지원"
        return "error", "오류"
    if result.get("total_records", 0) == 0:
        return "empty", "빈 결과"
    return "ok", "정상"


def _table_payload(
    *,
    title: str,
    columns: list[TableColumn],
    rows: list[dict[str, Any]],
    raw_rows: list[dict[str, Any]],
    empty_message: str,
) -> dict[str, Any]:
    """Build a table descriptor for the dashboard UI."""

    return {
        "title": title,
        "columns": columns,
        "rows": rows,
        "raw_rows": raw_rows,
        "row_count": len(raw_rows),
        "empty_message": empty_message,
    }


def _prefer_nonzero(primary: Any, fallback: Any) -> Any:
    """Use fallback when the primary value is empty or zero-like."""

    primary_number = _to_int(primary)
    if primary in ("", None) or primary_number == 0:
        return fallback
    return primary


async def build_dashboard_snapshot(
    client: KiwoomClient,
    settings: Settings,
    start_date: str,
    end_date: str,
) -> dict[str, Any]:
    """Collect and normalize dashboard data from Kiwoom APIs."""

    (
        evaluation_result,
        current_status_result,
        profit_detail_result,
        realized_profit_result,
        execution_result,
        order_status_result,
        unexecuted_result,
    ) = await asyncio.gather(
        account.get_account_evaluation(client),
        account.get_account_current_status(client),
        account.get_daily_account_profit_detail(client, start_date, end_date),
        account.get_daily_realized_profit_by_stock(client, "", start_date),
        account.get_execution_info(client, "0", "0", "1"),
        account.get_order_execution_status(client, "1", "0", "0", "0", "KRX"),
        account.get_unexecuted_orders(client, "0", "0", "1"),
    )

    evaluation_record = _first_record(evaluation_result, "evaluation_data")
    current_status_record = _first_record(current_status_result, "daily_status_data")
    profit_detail_record = _first_record(profit_detail_result, "profit_detail_data")
    profit_detail_rows = _records(profit_detail_result, "profit_detail_data")
    execution_rows = _records(execution_result, "execution_data")
    realized_profit_rows = _records(realized_profit_result, "realized_profit_data")
    unexecuted_rows = _records(unexecuted_result, "unexecuted_orders_data")

    holdings_rows: list[dict[str, Any]] = []
    if isinstance(evaluation_record.get("stk_acnt_evlt_prst"), list):
        holdings_rows = [
            row for row in evaluation_record["stk_acnt_evlt_prst"]
            if isinstance(row, dict)
        ]

    order_status_summary_rows = _records(order_status_result, "order_execution_status_data")
    order_status_rows = _nested_rows(order_status_summary_rows, "acnt_ord_cntr_prst_array")

    if not order_status_rows:
        order_status_rows = order_status_summary_rows

    summary = [
        {
            "label": "총 추정자산",
            "value": _pick_first(evaluation_record, "tot_est_amt", "prsm_dpst_aset_amt"),
            "kind": "currency",
            "tone": "neutral",
        },
        {
            "label": "평가자산",
            "value": _pick_first(evaluation_record, "aset_evlt_amt"),
            "kind": "currency",
            "tone": "neutral",
        },
        {
            "label": "예수금",
            "value": _pick_first(current_status_record, "entr", "d2_est_dpst", "dpsit", "entr_amt", "entr"),
            "fallback": _pick_first(evaluation_record, "entr"),
            "kind": "currency",
            "tone": "neutral",
        },
        {
            "label": "D+2 예수금",
            "value": _pick_first(current_status_record, "d2_entra", "d2_est_dpst"),
            "fallback": _pick_first(evaluation_record, "d2_entra"),
            "kind": "currency",
            "tone": "neutral",
        },
        {
            "label": "당일 손익",
            "value": _pick_first(evaluation_record, "tdy_lspft_amt"),
            "kind": "currency",
            "tone": _tone_for_value(_pick_first(evaluation_record, "tdy_lspft_amt")),
        },
        {
            "label": "총 손익률",
            "value": _pick_first(evaluation_record, "lspft_ratio", "lspft_rt", "tdy_lspft_rt"),
            "kind": "ratio",
            "tone": _tone_for_value(_pick_first(evaluation_record, "lspft_amt", "tdy_lspft_amt")),
        },
    ]

    for item in summary:
        if item.get("value") in ("", None) and item.get("fallback") not in ("", None):
            item["value"] = item["fallback"]
        item.pop("fallback", None)

    sources = []
    for title, result in [
        ("계좌 평가", evaluation_result),
        ("당일 계좌 현황", current_status_result),
        ("기간별 수익률", profit_detail_result),
        ("실현손익", realized_profit_result),
        ("체결 내역", execution_result),
        ("주문 체결 현황", order_status_result),
        ("미체결 주문", unexecuted_result),
    ]:
        status, status_label = _source_status(result)
        sources.append(
            {
                "title": title,
                "api_id": result.get("api_id"),
                "status": status,
                "status_label": status_label,
                "message": result.get("return_msg") or result.get("message"),
                "record_count": result.get("total_records", 0),
            }
        )

    holdings_columns = [
        {"key": "stock_name", "label": "종목"},
        {"key": "stock_code", "label": "코드"},
        {"key": "quantity", "label": "수량"},
        {"key": "avg_price", "label": "평균단가"},
        {"key": "current_price", "label": "현재가"},
        {"key": "evaluation_amount", "label": "평가금액"},
        {"key": "profit_loss", "label": "손익"},
        {"key": "profit_rate", "label": "수익률"},
    ]
    holdings_aliases = {
        "stock_name": ["stk_nm", "item_nm", "name"],
        "stock_code": ["stk_cd", "code"],
        "quantity": ["rmnd_qty", "qty", "hold_qty", "bal_qty"],
        "avg_price": ["avg_prc", "pur_uv", "buy_uv", "avg_uv"],
        "current_price": ["cur_prc", "now_prc", "close_pric"],
        "evaluation_amount": ["evlt_amt", "aset_evlt_amt"],
        "profit_loss": ["lspft_amt", "pl_amt", "evlt_pl"],
        "profit_rate": ["lspft_rt", "lspft_ratio", "pl_rt"],
    }

    order_columns = [
        {"key": "trade_date", "label": "일자"},
        {"key": "trade_time", "label": "시간"},
        {"key": "stock_name", "label": "종목"},
        {"key": "stock_code", "label": "코드"},
        {"key": "side", "label": "구분"},
        {"key": "status", "label": "상태"},
        {"key": "order_qty", "label": "주문수량"},
        {"key": "filled_qty", "label": "체결수량"},
        {"key": "order_price", "label": "주문가"},
        {"key": "filled_price", "label": "체결가"},
        {"key": "order_no", "label": "주문번호"},
    ]
    order_aliases = {
        "trade_date": ["ord_dt", "cntr_dt", "trde_dt", "dt"],
        "trade_time": ["ord_tmd", "ord_tm", "cntr_tm", "tm"],
        "stock_name": ["stk_nm", "item_nm", "name"],
        "stock_code": ["stk_cd", "code"],
        "side": ["trde_tp_nm", "sell_tp_nm", "trde_tp", "sell_tp"],
        "status": ["ord_prst", "cntr_prst", "prst", "stts"],
        "order_qty": ["ord_qty", "qty"],
        "filled_qty": ["cntr_qty", "exec_qty", "engg_qty"],
        "order_price": ["ord_uv", "uv"],
        "filled_price": ["cntr_uv", "exec_uv"],
        "order_no": ["ord_no", "orig_ord_no", "orgn_ord_no"],
    }

    execution_columns = [
        {"key": "trade_date", "label": "일자"},
        {"key": "trade_time", "label": "시간"},
        {"key": "stock_name", "label": "종목"},
        {"key": "stock_code", "label": "코드"},
        {"key": "side", "label": "구분"},
        {"key": "filled_qty", "label": "체결수량"},
        {"key": "filled_price", "label": "체결가"},
        {"key": "amount", "label": "체결금액"},
        {"key": "order_no", "label": "주문번호"},
    ]
    execution_aliases = {
        "trade_date": ["cntr_dt", "ord_dt", "dt"],
        "trade_time": ["cntr_tm", "ord_tmd", "tm"],
        "stock_name": ["stk_nm", "item_nm", "name"],
        "stock_code": ["stk_cd", "code"],
        "side": ["trde_tp_nm", "sell_tp_nm", "sell_tp"],
        "filled_qty": ["cntr_qty", "exec_qty"],
        "filled_price": ["cntr_uv", "exec_uv"],
        "amount": ["cntr_amt", "amt", "engg_amt"],
        "order_no": ["ord_no", "orig_ord_no"],
    }

    realized_columns = [
        {"key": "trade_date", "label": "일자"},
        {"key": "stock_name", "label": "종목"},
        {"key": "stock_code", "label": "코드"},
        {"key": "quantity", "label": "수량"},
        {"key": "buy_amount", "label": "매입금액"},
        {"key": "sell_amount", "label": "매도금액"},
        {"key": "profit_loss", "label": "실현손익"},
        {"key": "profit_rate", "label": "수익률"},
    ]
    realized_aliases = {
        "trade_date": ["dt", "trde_dt", "ord_dt"],
        "stock_name": ["stk_nm", "item_nm", "name"],
        "stock_code": ["stk_cd", "code"],
        "quantity": ["qty", "sel_qty", "trde_qty"],
        "buy_amount": ["pur_amt", "buy_amt", "maeip_amt"],
        "sell_amount": ["sel_amt", "sell_amt", "maedo_amt"],
        "profit_loss": ["rlzt_pl", "lspft_amt", "pl_amt"],
        "profit_rate": ["rlzt_rt", "lspft_rt", "pl_rt"],
    }

    daily_profit_columns = [
        {"key": "trade_date", "label": "일자"},
        {"key": "deposit", "label": "예수금"},
        {"key": "estimated_assets", "label": "추정자산"},
        {"key": "evaluation_amount", "label": "평가금액"},
        {"key": "profit_loss", "label": "손익"},
        {"key": "profit_rate", "label": "수익률"},
    ]
    daily_profit_aliases = {
        "trade_date": ["dt", "base_dt", "trde_dt"],
        "deposit": ["entr_to", "entr_fr", "entr", "dpsit", "d2_entra"],
        "estimated_assets": ["tot_amt_to", "tot_amt_fr", "tot_est_amt", "prsm_dpst_aset_amt"],
        "evaluation_amount": ["scrt_evlt_amt_to", "scrt_evlt_amt_fr", "aset_evlt_amt", "evlt_amt"],
        "profit_loss": ["evltv_prft", "lspft_amt", "tdy_lspft_amt"],
        "profit_rate": ["prft_rt", "tern_rt", "lspft_ratio", "lspft_rt"],
    }

    sources_with_issues = [
        source for source in sources if source["status"] in {"unsupported", "error"}
    ]
    empty_sources = [
        source for source in sources if source["status"] == "empty"
    ]
    overview = {
        "holdings_count": len(holdings_rows),
        "active_orders_count": len(unexecuted_rows),
        "order_status_count": len(order_status_rows),
        "executions_count": len(execution_rows),
        "realized_trades_count": len(realized_profit_rows),
        "issues_count": len(sources_with_issues),
        "empty_sources_count": len(empty_sources),
    }
    performance = [
        {
            "label": "기간 시작 자산",
            "value": _pick_first(profit_detail_record, "tot_amt_fr", "invt_bsamt"),
            "kind": "currency",
            "tone": "neutral",
        },
        {
            "label": "현재 기준 자산",
            "value": _prefer_nonzero(
                _pick_first(profit_detail_record, "tot_amt_to"),
                _pick_first(evaluation_record, "tot_est_amt", "prsm_dpst_aset_amt"),
            ),
            "kind": "currency",
            "tone": "neutral",
        },
        {
            "label": "기간 손익",
            "value": _pick_first(profit_detail_record, "evltv_prft", "lspft_amt"),
            "kind": "currency",
            "tone": _tone_for_value(_pick_first(profit_detail_record, "evltv_prft", "lspft_amt")),
        },
        {
            "label": "기간 수익률",
            "value": _pick_first(profit_detail_record, "prft_rt", "tern_rt"),
            "kind": "ratio",
            "tone": _tone_for_value(_pick_first(profit_detail_record, "evltv_prft", "lspft_amt")),
        },
    ]

    return {
        "generated_at": datetime.now(KST).isoformat(),
        "environment": {
            "mode": "mock" if settings.use_mock else "live",
            "label": "Mock Investment" if settings.use_mock else "Live Trading",
            "base_url": settings.active_base_url,
        },
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
        },
        "identity": {
            "account_name": _pick_first(evaluation_record, "acnt_nm") or "계좌명 없음",
            "branch_name": _pick_first(evaluation_record, "brch_nm") or "지점 정보 없음",
        },
        "overview": overview,
        "performance": performance,
        "summary": summary,
        "sources": sources,
        "tables": {
            "holdings": _table_payload(
                title="보유 종목",
                columns=holdings_columns,
                rows=_normalize_rows(holdings_rows, holdings_aliases),
                raw_rows=holdings_rows,
                empty_message="현재 보유 종목이 없습니다.",
            ),
            "unexecuted_orders": _table_payload(
                title="미체결 주문",
                columns=order_columns,
                rows=_normalize_rows(unexecuted_rows, order_aliases),
                raw_rows=unexecuted_rows,
                empty_message="현재 미체결 주문이 없습니다.",
            ),
            "order_status": _table_payload(
                title="주문 체결 현황",
                columns=order_columns,
                rows=_normalize_rows(order_status_rows, order_aliases),
                raw_rows=order_status_rows,
                empty_message="조회 가능한 주문 현황이 없습니다.",
            ),
            "executions": _table_payload(
                title="체결 이력",
                columns=execution_columns,
                rows=_normalize_rows(execution_rows, execution_aliases),
                raw_rows=execution_rows,
                empty_message="체결 이력이 없습니다.",
            ),
            "realized_profit": _table_payload(
                title="실현손익",
                columns=realized_columns,
                rows=_normalize_rows(realized_profit_rows, realized_aliases),
                raw_rows=realized_profit_rows,
                empty_message="선택 기간의 실현손익이 없습니다.",
            ),
            "daily_profit_detail": _table_payload(
                title="기간별 수익률",
                columns=daily_profit_columns,
                rows=_normalize_rows(profit_detail_rows, daily_profit_aliases),
                raw_rows=profit_detail_rows,
                empty_message="선택 기간의 수익률 상세 데이터가 없습니다.",
            ),
        },
    }


def _render_dashboard_page(initial_config: dict[str, Any]) -> str:
    """Return the dashboard shell HTML."""

    initial_json = json.dumps(initial_config, ensure_ascii=False)
    return DASHBOARD_HTML.replace("__INITIAL_CONFIG__", initial_json)


async def _homepage(request: Request) -> HTMLResponse:
    """Serve the dashboard shell."""

    default_start = _default_start_date()
    default_end = _today_ymd()
    return HTMLResponse(
        _render_dashboard_page(
            {
                "start_date": default_start,
                "end_date": default_end,
            }
        )
    )


async def _favicon(_: Request) -> Response:
    """Return an empty favicon response to avoid noisy 404s."""

    return Response(status_code=204)


def create_dashboard_app(
    *,
    data_loader: DashboardLoader | None = None,
) -> Starlette:
    """Create the dashboard ASGI application."""

    settings = get_settings()
    loader = data_loader or build_dashboard_snapshot

    @asynccontextmanager
    async def lifespan(app: Starlette):
        app.state.settings = settings
        app.state.kiwoom_client = KiwoomClient(settings)
        try:
            yield
        finally:
            await app.state.kiwoom_client.close()

    async def dashboard_api(request: Request) -> JSONResponse:
        start_date = request.query_params.get("start_date", _default_start_date())
        end_date = request.query_params.get("end_date", _today_ymd())

        try:
            start_date = _validate_ymd(start_date, "start_date")
            end_date = _validate_ymd(end_date, "end_date")
        except ValueError as exc:
            return JSONResponse({"success": False, "error": str(exc)}, status_code=400)

        payload = await loader(
            request.app.state.kiwoom_client,
            request.app.state.settings,
            start_date,
            end_date,
        )
        return JSONResponse(payload)

    routes = [
        Route("/", endpoint=_homepage),
        Route("/favicon.ico", endpoint=_favicon),
        Route("/api/dashboard", endpoint=dashboard_api),
    ]
    return Starlette(routes=routes, lifespan=lifespan)


app = create_dashboard_app()


__all__ = ["app", "build_dashboard_snapshot", "create_dashboard_app"]
