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