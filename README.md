# Kiwoom MCP Server

MCP (Model Context Protocol) server that provides Kiwoom OpenAPI

## Prerequisites

- Python 3.12+
- Kiwoom OpenAPI appkey and secretkey
- FastMCP package


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

### Live Order Tools

These tools submit real live orders. They are not simulation tools.

- `place_stock_buy_order`
  - API `kt10000`
  - Required args: `confirm_live_order=true`, `stk_cd`, `ord_qty`, `order_type_code`
  - Optional args: `ord_uv`, `cond_uv`

- `place_stock_sell_order`
  - API `kt10001`
  - Required args: `confirm_live_order=true`, `stk_cd`, `ord_qty`, `order_type_code`
  - Optional args: `ord_uv`, `cond_uv`

- `modify_stock_order`
  - API `kt10002`
  - Required args: `confirm_live_order=true`, `orig_ord_no`, `stk_cd`, `mdfy_qty`, `mdfy_uv`
  - Optional args: `mdfy_cond_uv`

- `cancel_stock_order`
  - API `kt10003`
  - Required args: `confirm_live_order=true`, `orig_ord_no`, `stk_cd`, `cncl_qty`
  - Note: `cncl_qty="0"` cancels the remaining quantity entirely

## Development Checks

- Run tests with:
  ```bash
  uv run pytest -q
  ```
