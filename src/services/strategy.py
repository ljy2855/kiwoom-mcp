"""Strategy planning and mock execution helpers for Kiwoom OpenAPI."""

from __future__ import annotations

from datetime import datetime
from math import floor
from typing import Any
from zoneinfo import ZoneInfo

from ..config import Settings
from . import account, market, order
from .kiwoom_client import KiwoomClient

KST = ZoneInfo("Asia/Seoul")
ETF_KEYWORDS = (
    "KODEX",
    "TIGER",
    "KOSEF",
    "KBSTAR",
    "HANARO",
    "ARIRANG",
    "ACE",
    "PLUS",
    "RISE",
    "SOL",
    "TIMEFOLIO",
    "FOCUS",
    "ETN",
    "인버스",
    "레버리지",
    "2X",
)


def _pick_first(record: dict[str, Any], *keys: str) -> Any:
    """Return the first non-empty value for the given keys."""

    for key in keys:
        value = record.get(key)
        if value not in ("", None):
            return value
    return None


def _to_float(value: Any) -> float | None:
    """Convert a Kiwoom numeric field to a float when possible."""

    if value in ("", None):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).replace(",", "").strip()
    if not text:
        return None
    sign = 1.0
    if text[0] == "+":
        text = text[1:]
    elif text[0] == "-":
        sign = -1.0
        text = text[1:]
    try:
        return sign * float(text)
    except ValueError:
        return None


def _to_int(value: Any) -> int | None:
    """Convert a Kiwoom numeric field to an int when possible."""

    number = _to_float(value)
    if number is None:
        return None
    return int(number)


def _to_price(value: Any) -> int | None:
    """Convert a price-like Kiwoom field to a positive integer."""

    number = _to_int(value)
    if number is None:
        return None
    return abs(number)


def _to_ratio(value: Any) -> float | None:
    """Convert a percentage-like Kiwoom field to a float."""

    return _to_float(value)


def _position_rate(profit_rate: Any, avg_price: int | None, current_price: int | None) -> float | None:
    """Return a holding profit rate from either the row or derived prices."""

    rate = _to_ratio(profit_rate)
    if rate is not None:
        return rate
    if avg_price and current_price:
        return ((current_price - avg_price) / avg_price) * 100
    return None


def _sanitize_watchlist(
    watchlist: list[str] | None,
    holdings: list[dict[str, Any]],
) -> list[str]:
    """Merge the user watchlist and current holdings."""

    merged: list[str] = []
    for code in watchlist or []:
        if code and code not in merged:
            merged.append(code)
    for holding in holdings:
        stock_code = holding.get("stock_code")
        if stock_code and stock_code not in merged:
            merged.append(stock_code)
    return merged


def _is_excluded_security(name: str) -> bool:
    """Return True for instruments the strategy intentionally ignores."""

    if not name:
        return True
    if name.endswith("우") or "스팩" in name or "SPAC" in name.upper():
        return True
    return any(keyword in name for keyword in ETF_KEYWORDS)


def _normalize_holding_rows(evaluation_result: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Extract account summary and holdings from the evaluation response."""

    rows = evaluation_result.get("evaluation_data", [])
    if not isinstance(rows, list) or not rows:
        return {}, []

    evaluation_record = rows[0] if isinstance(rows[0], dict) else {}
    raw_holdings = evaluation_record.get("stk_acnt_evlt_prst", [])
    if not isinstance(raw_holdings, list):
        raw_holdings = []

    holdings = []
    for row in raw_holdings:
        if not isinstance(row, dict):
            continue
        stock_code = str(_pick_first(row, "stk_cd", "code") or "").strip()
        quantity = abs(_to_int(_pick_first(row, "rmnd_qty", "qty", "hold_qty", "bal_qty")) or 0)
        if not stock_code or quantity <= 0:
            continue
        avg_price = _to_price(_pick_first(row, "avg_prc", "pur_uv", "buy_uv", "avg_uv"))
        current_price = _to_price(_pick_first(row, "cur_prc", "now_prc", "close_pric"))
        holdings.append(
            {
                "stock_code": stock_code,
                "stock_name": str(_pick_first(row, "stk_nm", "item_nm", "name") or stock_code),
                "quantity": quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "profit_loss": _to_int(_pick_first(row, "lspft_amt", "pl_amt", "evlt_pl")),
                "profit_rate": _position_rate(
                    _pick_first(row, "lspft_rt", "lspft_ratio", "pl_rt"),
                    avg_price,
                    current_price,
                ),
            }
        )

    return evaluation_record, holdings


def _extract_open_order_codes(unexecuted_result: dict[str, Any]) -> set[str]:
    """Return the set of stock codes that already have open orders."""

    rows = unexecuted_result.get("unexecuted_orders_data", [])
    if not isinstance(rows, list):
        return set()
    return {
        str(_pick_first(row, "stk_cd", "code"))
        for row in rows
        if isinstance(row, dict) and _pick_first(row, "stk_cd", "code")
    }


def _build_market_regime(snapshot: dict[str, Any]) -> dict[str, Any]:
    """Classify the current market into risk-on, neutral, or risk-off."""

    kospi = snapshot.get("indices", {}).get("kospi", {})
    kosdaq = snapshot.get("indices", {}).get("kosdaq", {})

    kospi_change = _to_ratio(kospi.get("flu_rt")) or 0.0
    kosdaq_change = _to_ratio(kosdaq.get("flu_rt")) or 0.0
    kospi_rising = _to_int(kospi.get("rising")) or 0
    kospi_falling = _to_int(kospi.get("fall")) or 0
    kosdaq_rising = _to_int(kosdaq.get("rising")) or 0
    kosdaq_falling = _to_int(kosdaq.get("fall")) or 0

    kospi_breadth = kospi_rising / max(kospi_falling, 1)
    kosdaq_breadth = kosdaq_rising / max(kosdaq_falling, 1)
    breadth_score = (kospi_breadth + kosdaq_breadth) / 2
    average_change = (kospi_change + kosdaq_change) / 2

    if average_change >= 0.5 and breadth_score >= 1.15:
        regime = "risk_on"
    elif average_change <= -0.5 or breadth_score < 0.85:
        regime = "risk_off"
    else:
        regime = "neutral"

    return {
        "regime": regime,
        "risk_on": regime == "risk_on",
        "average_change_pct": round(average_change, 2),
        "breadth_score": round(breadth_score, 2),
        "kospi_change_pct": round(kospi_change, 2),
        "kosdaq_change_pct": round(kosdaq_change, 2),
        "kospi_breadth": round(kospi_breadth, 2),
        "kosdaq_breadth": round(kosdaq_breadth, 2),
    }


def _merge_leaderboards(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    """Merge leaderboard rows into a candidate universe with source tags."""

    universe: dict[str, dict[str, Any]] = {}
    leaders = snapshot.get("leaders", {})

    for source_name, rows in leaders.items():
        if not isinstance(rows, list):
            continue
        for rank, row in enumerate(rows, start=1):
            if not isinstance(row, dict):
                continue
            stock_code = str(_pick_first(row, "stk_cd", "code") or "").strip()
            stock_name = str(_pick_first(row, "stk_nm", "item_nm", "name") or stock_code)
            if not stock_code or _is_excluded_security(stock_name):
                continue
            entry = universe.setdefault(
                stock_code,
                {
                    "stock_code": stock_code,
                    "stock_name": stock_name,
                    "sources": [],
                    "ranks": {},
                    "seed_row": row,
                },
            )
            entry["stock_name"] = stock_name
            entry["seed_row"] = row
            entry["sources"].append(source_name)
            entry["ranks"][source_name] = rank

    return sorted(
        universe.values(),
        key=lambda item: (
            -int("gainers" in item["sources"]),
            -len(item["sources"]),
            item["ranks"].get("value", 999),
            item["ranks"].get("gainers", 999),
            item["ranks"].get("volume", 999),
        ),
    )


def _select_entry_price(detail: dict[str, Any]) -> tuple[str, str]:
    """Choose a conservative entry order type and price."""

    orderbook = detail.get("orderbook", {})
    best_ask = _to_price(orderbook.get("sel_fpr_bid"))
    if best_ask:
        return "0", str(best_ask)
    return "3", ""


def _select_exit_price(detail: dict[str, Any]) -> tuple[str, str]:
    """Choose a conservative exit order type and price."""

    orderbook = detail.get("orderbook", {})
    best_bid = _to_price(orderbook.get("buy_fpr_bid"))
    if best_bid:
        return "0", str(best_bid)
    return "3", ""


def _score_candidate(
    candidate: dict[str, Any],
    detail: dict[str, Any],
    regime: dict[str, Any],
) -> tuple[bool, dict[str, Any]]:
    """Score one candidate and decide whether it is eligible for entry."""

    quote = detail.get("quote", {})
    orderbook = detail.get("orderbook", {})
    bars = detail.get("daily_bars", [])
    stock_name = str(quote.get("stk_nm") or candidate.get("stock_name") or candidate["stock_code"])

    current_price = _to_price(quote.get("cur_prc"))
    open_price = _to_price(quote.get("open_pric"))
    high_price = _to_price(quote.get("high_pric"))
    prev_close = _to_price(quote.get("pred_close_pric"))
    prev_high = None
    if len(bars) > 1 and isinstance(bars[1], dict):
        prev_high = _to_price(bars[1].get("high_pric"))

    day_change_pct = _to_ratio(quote.get("flu_rt"))
    total_buy = _to_price(orderbook.get("tot_buy_req")) or 0
    total_sell = _to_price(orderbook.get("tot_sel_req")) or 0
    orderbook_ratio = total_buy / max(total_sell, 1)
    best_bid = _to_price(orderbook.get("buy_fpr_bid"))
    best_ask = _to_price(orderbook.get("sel_fpr_bid"))
    spread_pct = None
    if best_bid and best_ask and best_bid > 0:
        spread_pct = ((best_ask - best_bid) / best_bid) * 100

    reasons: list[str] = []
    if not regime.get("risk_on", False):
        reasons.append("시장 레짐이 risk-on이 아님")
    if current_price is None or open_price is None or high_price is None or prev_close is None:
        reasons.append("시세 데이터가 불완전함")
    if current_price and current_price < 3000:
        reasons.append("저가주 필터")
    if day_change_pct is None or day_change_pct < 1 or day_change_pct > 18:
        reasons.append("당일 상승률 조건 미충족")
    if current_price and open_price and current_price < open_price:
        reasons.append("시가 아래에서 거래 중")
    if current_price and high_price and (high_price - current_price) / max(current_price, 1) > 0.025:
        reasons.append("고가 대비 너무 멀어짐")
    if orderbook_ratio < 1.0:
        reasons.append("매수 잔량 우위 부족")

    score = 0
    source_set = set(candidate.get("sources", []))
    if "value" in source_set:
        score += 3
    if "gainers" in source_set:
        score += 2
    if "volume" in source_set:
        score += 1
    if day_change_pct is not None:
        if 1 <= day_change_pct <= 10:
            score += 2
        elif 10 < day_change_pct <= 18:
            score += 1
    if current_price and open_price and current_price >= open_price:
        score += 1
    if current_price and high_price and (high_price - current_price) / max(current_price, 1) <= 0.01:
        score += 2
    if prev_high and current_price and current_price >= prev_high:
        score += 2
    if orderbook_ratio >= 1.2:
        score += 2
    elif orderbook_ratio >= 1.0:
        score += 1
    if spread_pct is not None and spread_pct <= 0.35:
        score += 1

    breakout = bool(prev_high and current_price and current_price >= prev_high)
    eligible = not reasons and score >= 8

    return eligible, {
        "stock_code": candidate["stock_code"],
        "stock_name": stock_name,
        "sources": list(source_set),
        "score": score,
        "eligible": eligible,
        "reasons": reasons,
        "current_price": current_price,
        "open_price": open_price,
        "high_price": high_price,
        "prev_close": prev_close,
        "prev_high": prev_high,
        "day_change_pct": day_change_pct,
        "orderbook_ratio": round(orderbook_ratio, 2),
        "spread_pct": round(spread_pct, 3) if spread_pct is not None else None,
        "breakout": breakout,
        "entry_order_type_code": _select_entry_price(detail)[0],
        "entry_price": _select_entry_price(detail)[1],
    }


def _review_holding(
    holding: dict[str, Any],
    detail: dict[str, Any],
    regime: dict[str, Any],
) -> dict[str, Any]:
    """Review an existing holding and decide whether to hold or exit."""

    quote = detail.get("quote", {})
    current_price = _to_price(quote.get("cur_prc")) or holding.get("current_price")
    open_price = _to_price(quote.get("open_pric"))
    profit_rate = holding.get("profit_rate")
    quantity = holding.get("quantity", 0)

    action = "hold"
    priority = 0
    reason = "추세 유지"

    if profit_rate is not None and profit_rate <= -3.0:
        action = "sell"
        priority = 100
        reason = "손절 규칙"
    elif profit_rate is not None and profit_rate >= 6.0:
        action = "sell"
        priority = 90
        reason = "익절 규칙"
    elif (
        regime.get("regime") == "risk_off"
        and profit_rate is not None
        and profit_rate <= 1.0
    ):
        action = "sell"
        priority = 80
        reason = "시장 약세로 디리스킹"
    elif (
        current_price
        and open_price
        and current_price < open_price
        and profit_rate is not None
        and profit_rate < 0
    ):
        action = "sell"
        priority = 70
        reason = "시가 이탈 + 손실 포지션"

    order_type_code, exit_price = _select_exit_price(detail)
    return {
        "action": action,
        "priority": priority,
        "stock_code": holding["stock_code"],
        "stock_name": holding["stock_name"],
        "quantity": quantity,
        "profit_rate": profit_rate,
        "reason": reason,
        "order_type_code": order_type_code,
        "order_price": exit_price,
    }


def _safe_budget_amount(
    evaluation_record: dict[str, Any],
    *,
    position_budget_pct: int,
) -> int:
    """Estimate a safe per-position budget from account evaluation data."""

    total_estimated = _to_price(_pick_first(evaluation_record, "tot_est_amt", "prsm_dpst_aset_amt")) or 0
    cash_available = _to_price(_pick_first(evaluation_record, "entr", "d2_entra", "ord_psbl_amt")) or 0
    base_amount = total_estimated or cash_available
    target_budget = floor(base_amount * (position_budget_pct / 100))
    if cash_available > 0:
        target_budget = min(target_budget, cash_available)
    return max(target_budget, 0)


async def _execute_strategy_actions(
    client: KiwoomClient,
    *,
    planned_actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Execute the planned actions as mock orders."""

    executions = []
    for action in planned_actions:
        if action["action"] == "buy":
            result = await order.place_stock_buy_order(
                client,
                stk_cd=action["stock_code"],
                ord_qty=str(action["quantity"]),
                order_type_code=action["order_type_code"],
                ord_uv=action["order_price"],
            )
        elif action["action"] == "sell":
            result = await order.place_stock_sell_order(
                client,
                stk_cd=action["stock_code"],
                ord_qty=str(action["quantity"]),
                order_type_code=action["order_type_code"],
                ord_uv=action["order_price"],
            )
        else:
            continue
        executions.append(
            {
                "action": action,
                "order_result": result,
            }
        )
    return executions


async def plan_intraday_momentum_strategy(
    client: KiwoomClient,
    settings: Settings,
    *,
    watchlist: list[str] | None = None,
    leaders_limit: int = 10,
    candidate_limit: int = 5,
    max_positions: int = 3,
    max_new_positions: int = 1,
    position_budget_pct: int = 10,
    execute_orders: bool = False,
    confirm_mock_orders: bool = False,
) -> dict[str, Any]:
    """Build and optionally execute a conservative intraday momentum strategy."""

    evaluation_result = await account.get_account_evaluation(client)
    unexecuted_result = await account.get_unexecuted_orders(client, "0", "0", "1")
    evaluation_record, holdings = _normalize_holding_rows(evaluation_result)
    open_order_codes = _extract_open_order_codes(unexecuted_result)

    merged_watchlist = _sanitize_watchlist(watchlist, holdings)
    snapshot = await market.get_market_snapshot(
        client,
        watchlist=merged_watchlist,
        leaders_limit=leaders_limit,
    )
    regime = _build_market_regime(snapshot)

    detail_cache: dict[str, dict[str, Any]] = {}
    for detail in snapshot.get("watchlist_details", []):
        stock_code = detail.get("stock_code")
        if stock_code:
            detail_cache[stock_code] = detail

    holding_actions = []
    for holding in holdings:
        stock_code = holding["stock_code"]
        detail = detail_cache.get(stock_code)
        if detail is None:
            detail = await market.get_stock_detail_bundle(client, stock_code=stock_code)
            detail_cache[stock_code] = detail
        holding_actions.append(_review_holding(holding, detail, regime))

    universe = _merge_leaderboards(snapshot)
    candidate_rows = []
    skipped_candidates = []

    held_codes = {holding["stock_code"] for holding in holdings}
    safe_budget = _safe_budget_amount(
        evaluation_record,
        position_budget_pct=position_budget_pct,
    )
    available_slots = max(max_positions - len(holdings), 0)
    buy_slots = min(available_slots, max_new_positions)

    scan_limit = max(candidate_limit * 4, candidate_limit)
    for candidate in universe[:scan_limit]:
        stock_code = candidate["stock_code"]
        if stock_code in held_codes:
            skipped_candidates.append(
                {
                    "stock_code": stock_code,
                    "stock_name": candidate["stock_name"],
                    "reason": "이미 보유 중",
                }
            )
            continue
        if stock_code in open_order_codes:
            skipped_candidates.append(
                {
                    "stock_code": stock_code,
                    "stock_name": candidate["stock_name"],
                    "reason": "기존 미체결 주문 존재",
                }
            )
            continue

        detail = detail_cache.get(stock_code)
        if detail is None:
            detail = await market.get_stock_detail_bundle(client, stock_code=stock_code)
            detail_cache[stock_code] = detail

        eligible, scored = _score_candidate(candidate, detail, regime)
        candidate_rows.append(scored)

        if not eligible or buy_slots <= 0:
            continue

        entry_price = _to_price(scored.get("entry_price"))
        if not entry_price or safe_budget <= 0:
            skipped_candidates.append(
                {
                    "stock_code": stock_code,
                    "stock_name": candidate["stock_name"],
                    "reason": "주문 가능 예산 부족",
                }
            )
            continue

        quantity = floor(safe_budget / entry_price)
        if quantity < 1:
            skipped_candidates.append(
                {
                    "stock_code": stock_code,
                    "stock_name": candidate["stock_name"],
                    "reason": "주문 수량이 1주 미만",
                }
            )
            continue

        scored["planned_action"] = {
            "action": "buy",
            "priority": 50 + scored["score"],
            "stock_code": stock_code,
            "stock_name": candidate["stock_name"],
            "quantity": quantity,
            "order_type_code": scored["entry_order_type_code"],
            "order_price": scored["entry_price"],
            "reason": "유동성/추세/호가 우위 조건 충족",
            "score": scored["score"],
        }
        buy_slots -= 1

    planned_actions = [
        {
            "action": action["action"],
            "priority": action["priority"],
            "stock_code": action["stock_code"],
            "stock_name": action["stock_name"],
            "quantity": action["quantity"],
            "order_type_code": action["order_type_code"],
            "order_price": action["order_price"],
            "reason": action["reason"],
        }
        for action in holding_actions
        if action["action"] == "sell"
    ]
    planned_actions.extend(
        row["planned_action"]
        for row in candidate_rows
        if isinstance(row.get("planned_action"), dict)
    )
    planned_actions.sort(key=lambda item: (-item["priority"], item["stock_code"]))

    executed_orders: list[dict[str, Any]] = []
    execution_allowed = execute_orders and confirm_mock_orders and settings.use_mock
    if execute_orders and not settings.use_mock:
        executed_orders.append(
            {
                "action": None,
                "order_result": {
                    "success": False,
                    "message": "실행 모드는 mock 환경에서만 허용됩니다",
                },
            }
        )
    elif execution_allowed:
        executed_orders = await _execute_strategy_actions(
            client,
            planned_actions=planned_actions,
        )

    return {
        "success": evaluation_result.get("success", False) and snapshot.get("success", False),
        "strategy_name": "krx_intraday_momentum_v1",
        "generated_at": datetime.now(KST).isoformat(),
        "environment": {
            "mode": "mock" if settings.use_mock else "live",
            "execution_allowed": execution_allowed,
        },
        "regime": regime,
        "portfolio": {
            "estimated_assets": _to_price(_pick_first(evaluation_record, "tot_est_amt", "prsm_dpst_aset_amt")),
            "cash_available": _to_price(_pick_first(evaluation_record, "entr", "d2_entra")),
            "holding_count": len(holdings),
            "open_order_count": len(open_order_codes),
            "position_budget": safe_budget,
            "max_positions": max_positions,
            "max_new_positions": max_new_positions,
        },
        "holdings": holdings,
        "holding_actions": holding_actions,
        "candidate_rows": candidate_rows,
        "skipped_candidates": skipped_candidates,
        "planned_actions": planned_actions,
        "executed_orders": executed_orders,
        "market_snapshot": {
            "indices": snapshot.get("indices", {}),
            "leaders": snapshot.get("leaders", {}),
            "sector_rows": snapshot.get("sector_rows", []),
        },
        "message": "Built intraday strategy plan"
        if not execution_allowed
        else "Built and executed intraday strategy plan",
    }


__all__ = ["plan_intraday_momentum_strategy"]
