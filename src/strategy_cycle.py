"""Automation-friendly one-shot runner for the intraday strategy."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from typing import Any, Sequence

from .config import Settings
from .services.kiwoom_client import KiwoomClient
from .services.strategy import plan_intraday_momentum_strategy


def parse_watchlist_arg(raw: str | None) -> list[str] | None:
    """Parse a comma-separated watchlist argument into unique stock codes."""

    if raw is None:
        return None

    codes: list[str] = []
    for part in raw.split(","):
        code = part.strip()
        if not code:
            continue
        if len(code) != 6 or not code.isdigit():
            raise ValueError(f"Invalid stock code in watchlist: {code}")
        if code not in codes:
            codes.append(code)
    return codes or None


def _format_int(value: Any) -> str:
    """Format a Kiwoom numeric value for CLI output."""

    if value in (None, ""):
        return "-"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        return f"{value:,.2f}"
    return str(value)


def _format_percent(value: Any) -> str:
    """Format a percentage-like value for CLI output."""

    if value in (None, ""):
        return "-"
    if isinstance(value, (int, float)):
        return f"{value:.2f}%"
    return f"{value}%"


def build_strategy_report(result: dict[str, Any]) -> str:
    """Render a concise plain-text strategy report for automation output."""

    lines: list[str] = []
    environment = result.get("environment", {})
    regime = result.get("regime", {})
    portfolio = result.get("portfolio", {})

    lines.append(
        "Strategy cycle"
        f" | env={environment.get('mode', '-')}"
        f" | execution_allowed={environment.get('execution_allowed', False)}"
    )
    lines.append(
        "Regime"
        f" | {regime.get('regime', '-')}"
        f" | avg_change={_format_percent(regime.get('average_change_pct'))}"
        f" | breadth={_format_int(regime.get('breadth_score'))}"
    )
    lines.append(
        "Portfolio"
        f" | assets={_format_int(portfolio.get('estimated_assets'))}"
        f" | cash={_format_int(portfolio.get('cash_available'))}"
        f" | holdings={_format_int(portfolio.get('holding_count'))}"
        f" | open_orders={_format_int(portfolio.get('open_order_count'))}"
        f" | budget={_format_int(portfolio.get('position_budget'))}"
    )

    planned_actions = result.get("planned_actions", [])
    lines.append(f"Planned actions: {len(planned_actions)}")
    if planned_actions:
        for action in planned_actions[:5]:
            lines.append(
                "  "
                f"{action.get('action')} {action.get('stock_code')} {action.get('stock_name')} "
                f"qty={action.get('quantity')} type={action.get('order_type_code')} "
                f"price={action.get('order_price') or 'market'} reason={action.get('reason')}"
            )
    else:
        lines.append("  none")

    candidates = result.get("candidate_rows", [])
    lines.append(f"Top candidates: {min(len(candidates), 5)}")
    if candidates:
        for row in candidates[:5]:
            reason_text = ", ".join(row.get("reasons", [])[:2]) or "pass"
            lines.append(
                "  "
                f"{row.get('stock_code')} {row.get('stock_name')} "
                f"score={row.get('score')} eligible={row.get('eligible')} "
                f"change={_format_percent(row.get('day_change_pct'))} "
                f"reason={reason_text}"
            )
    else:
        lines.append("  none")

    executed_orders = result.get("executed_orders", [])
    if executed_orders:
        lines.append(f"Executed orders: {len(executed_orders)}")
        for item in executed_orders[:5]:
            action = item.get("action") or {}
            order_result = item.get("order_result") or {}
            lines.append(
                "  "
                f"{action.get('action')} {action.get('stock_code')} "
                f"success={order_result.get('success')} "
                f"message={order_result.get('message')}"
            )

    return "\n".join(lines)


async def run_strategy_cycle(
    *,
    watchlist: list[str] | None = None,
    leaders_limit: int = 10,
    candidate_limit: int = 5,
    max_positions: int = 3,
    max_new_positions: int = 1,
    position_budget_pct: int = 10,
    execute_mock_orders: bool = False,
) -> dict[str, Any]:
    """Run one full strategy cycle and return the structured result."""

    settings = Settings()
    client = KiwoomClient(settings)
    try:
        return await plan_intraday_momentum_strategy(
            client,
            settings,
            watchlist=watchlist,
            leaders_limit=leaders_limit,
            candidate_limit=candidate_limit,
            max_positions=max_positions,
            max_new_positions=max_new_positions,
            position_budget_pct=position_budget_pct,
            execute_orders=execute_mock_orders,
            confirm_mock_orders=execute_mock_orders,
        )
    finally:
        await client.close()


def _build_arg_parser() -> argparse.ArgumentParser:
    """Create the CLI parser for the strategy-cycle runner."""

    parser = argparse.ArgumentParser(
        description="Run one Kiwoom intraday strategy cycle without starting the MCP server."
    )
    parser.add_argument("--watchlist", help="Comma-separated 6-digit stock codes")
    parser.add_argument("--leaders-limit", type=int, default=10)
    parser.add_argument("--candidate-limit", type=int, default=5)
    parser.add_argument("--max-positions", type=int, default=3)
    parser.add_argument("--max-new-positions", type=int, default=1)
    parser.add_argument("--position-budget-pct", type=int, default=10)
    parser.add_argument(
        "--execute-mock-orders",
        action="store_true",
        help="Actually submit orders, but only when KIWOOM_USE_MOCK=true",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the raw JSON result instead of the text report",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the one-shot strategy cycle CLI."""

    parser = _build_arg_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        watchlist = parse_watchlist_arg(args.watchlist)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        return 2

    settings = Settings()
    if args.execute_mock_orders and not settings.use_mock:
        print(
            "--execute-mock-orders requires KIWOOM_USE_MOCK=true. Refusing to run in live mode.",
            file=sys.stderr,
        )
        return 2

    result = asyncio.run(
        run_strategy_cycle(
            watchlist=watchlist,
            leaders_limit=args.leaders_limit,
            candidate_limit=args.candidate_limit,
            max_positions=args.max_positions,
            max_new_positions=args.max_new_positions,
            position_budget_pct=args.position_budget_pct,
            execute_mock_orders=args.execute_mock_orders,
        )
    )

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(build_strategy_report(result))

    return 0 if result.get("success", False) else 1


def cli() -> None:
    """Console-script wrapper."""

    raise SystemExit(main())


__all__ = [
    "build_strategy_report",
    "cli",
    "main",
    "parse_watchlist_arg",
    "run_strategy_cycle",
]
