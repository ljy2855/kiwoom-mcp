# Kiwoom MCP Server

MCP (Model Context Protocol) server that provides Kiwoom OpenAPI

## Prerequisites

- Python 3.12+
- Kiwoom OpenAPI appkey and secretkey
- FastMCP package

## Environment Setup

The server supports both live trading and mock trading credentials.

For development, enable the mock trading environment in `.env`:

```dotenv
KIWOOM_USE_MOCK=true
KIWOOM_MOCK_APPKEY=your-mock-app-key
KIWOOM_MOCK_SECRETKEY=your-mock-secret-key
```

For live trading, switch mock mode off and provide the live credentials:

```dotenv
KIWOOM_USE_MOCK=false
KIWOOM_APPKEY=your-live-app-key
KIWOOM_SECRETKEY=your-live-secret-key
```

If `KIWOOM_USE_MOCK=true`, all authenticated REST calls and order tools are routed to `https://mockapi.kiwoom.com`.

## Project layout

```
kiwoom_mcp/
│
├── main.py                    # CLI entrypoint that runs the MCP server
├── pyproject.toml             # Project metadata and dependency declarations
├── README.md
└── src/
    ├── __init__.py
    ├── config.py              # Settings loaded from environment/.env
    ├── mcp_server.py          # FastMCP server implementation
    ├── constants/
    │   ├── __init__.py
    │   └── api.py             # API ID, names, and URL constants
    ├── models/
    │   ├── __init__.py
    │   └── auth.py            # OAuth-related request/response models
    └── services/
        ├── account.py         # Account-related service functions
        ├── order.py           # Order-related service functions
        ├── kiwoom_client.py   # Async HTTP client wrapper for Kiwoom APIs
        └── token_manager.py   # Token management and automatic renewal
```

## Token Management

The server automatically handles token management:

- **Automatic Token Issuance**: Tokens are issued automatically when first needed
- **Automatic Token Refresh**: Tokens are refreshed automatically before expiration (5-minute buffer)
- **Thread-Safe**: Token operations are protected with locks to prevent race conditions
- **Transparent**: All API calls automatically include valid authentication headers

## API Constants

The server uses centralized API constants for all Kiwoom OpenAPI endpoints:

[API list](./kiwoom_api_spec.md)

## Available MCP Tools

The server currently exposes the following MCP tools.

### Account / Query Tools

- `get_account_current_status`
  - API `kt00017`
  - No arguments
  - Returns the current-day account snapshot such as D+2 estimated deposit and evaluated stock amount

- `get_account_evaluation`
  - API `kt00004`
  - Args: `qry_tp`, `dmst_stex_tp`
  - Returns evaluated assets, holdings, and profit/loss summary

- `get_daily_account_profit_detail`
  - API `kt00016`
  - Args: `fr_dt`, `to_dt`
  - Returns detailed account profit-rate data for a date range

- `get_daily_realized_profit_by_stock`
  - API `ka10072`
  - Args: `start_date`, optional `stock_code`
  - Returns realized profit/loss records from the given start date

- `get_orderable_amount`
  - API `kt00010`
  - Args: `stk_cd`, `trde_tp`, `uv`, optional `trde_qty`, `exp_buy_unp`
  - Returns orderable/withdrawable amount information for a stock

- `get_execution_info`
  - API `ka10076`
  - Args: `qry_tp`, `sell_tp`, `stex_tp`, optional `stk_cd`, `ord_no`
  - Returns filled-order execution history only

- `get_order_execution_status`
  - API `kt00009`
  - Args: `stk_bond_tp`, `mrkt_tp`, `sell_tp`, `qry_tp`, `dmst_stex_tp`, optional `stk_cd`, `fr_ord_no`
  - Returns account order/execution status snapshot including non-filled states

- `get_unexecuted_orders`
  - API `ka10075`
  - Args: `all_stk_tp`, `trde_tp`, `stex_tp`, optional `stk_cd`
  - Returns currently unexecuted orders

### Market / Strategy Tools

- `get_market_snapshot`
  - Aggregates KOSPI/KOSDAQ index snapshots, sector overview, top gainers, top volume, top traded value, and optional watchlist details
  - Args: optional `watchlist`, `leaders_limit`
  - Use this as the main market-context input for hourly automations

- `plan_intraday_momentum_strategy`
  - Dry-run planner for a conservative intraday momentum strategy
  - Args: optional `watchlist`, `leaders_limit`, `candidate_limit`, `max_positions`, `max_new_positions`, `position_budget_pct`
  - Applies market-regime filtering, leaderboard-based candidate selection, and stop-loss / take-profit rules without sending orders

- `run_mock_intraday_momentum_strategy`
  - Mock-only execution wrapper around the same strategy
  - Required args: `confirm_mock_strategy_execution=true`
  - Optional args: same as `plan_intraday_momentum_strategy`
  - Refuses to place orders unless `KIWOOM_USE_MOCK=true`

### Order Submission Tools

These tools submit orders to the currently configured Kiwoom environment.
When `KIWOOM_USE_MOCK=true`, they go to the mock investment environment.
When `KIWOOM_USE_MOCK=false`, they go to the live trading environment.

- `place_stock_buy_order`
  - API `kt10000`
  - Required args: `confirm_live_order=true`, `stk_cd`, `ord_qty`, `order_type_code`
  - Optional args: `dmst_stex_tp` (default `KRX`), `ord_uv`, `cond_uv`

- `place_stock_sell_order`
  - API `kt10001`
  - Required args: `confirm_live_order=true`, `stk_cd`, `ord_qty`, `order_type_code`
  - Optional args: `dmst_stex_tp` (default `KRX`), `ord_uv`, `cond_uv`

- `modify_stock_order`
  - API `kt10002`
  - Required args: `confirm_live_order=true`, `orig_ord_no`, `stk_cd`, `mdfy_qty`, `mdfy_uv`
  - Optional args: `dmst_stex_tp` (default `KRX`), `mdfy_cond_uv`

- `cancel_stock_order`
  - API `kt10003`
  - Required args: `confirm_live_order=true`, `orig_ord_no`, `stk_cd`, `cncl_qty`
  - Optional args: `dmst_stex_tp` (default `KRX`)
  - Note: `cncl_qty="0"` cancels the remaining quantity entirely

## Development Checks

- Run tests with:
  ```bash
  uv run pytest -q
  ```

## Dashboard

The project also includes a web dashboard for account overview and trade history.

- Start the dashboard:
  ```bash
  uv run python main_dashboard.py
  ```
- Open:
  - [http://127.0.0.1:8001](http://127.0.0.1:8001)
- JSON data endpoint:
  - [http://127.0.0.1:8001/api/dashboard](http://127.0.0.1:8001/api/dashboard)

The dashboard reads the same `.env` settings as the MCP server, so with `KIWOOM_USE_MOCK=true` it will query the mock investment environment.

## Strategy Notes

The built-in strategy is intentionally conservative.

- It buys only when the market regime is risk-on based on KOSPI/KOSDAQ breadth and index performance
- It prefers liquid momentum names from gainers / volume / traded-value leaderboards
- It exits on a fixed stop-loss (`-3%`), take-profit (`+6%`), or weak-market de-risking rule
- It is designed for mock-trading validation first, not for unattended live trading

## Direct Strategy Runner

For automation, the recommended path is to run the strategy directly without starting the MCP server.

- Dry-run one cycle:
  ```bash
  uv run python main_strategy_cycle.py
  ```
- Dry-run with a custom watchlist:
  ```bash
  uv run python main_strategy_cycle.py --watchlist 005930,000660,035420
  ```
- Print raw JSON:
  ```bash
  uv run python main_strategy_cycle.py --json
  ```
- Execute mock orders:
  ```bash
  KIWOOM_USE_MOCK=true uv run python main_strategy_cycle.py --execute-mock-orders
  ```

There is also a console script entrypoint:

```bash
uv run kiwoom-strategy-cycle --json
```

Safety rule:

- `--execute-mock-orders` is refused unless `KIWOOM_USE_MOCK=true`
