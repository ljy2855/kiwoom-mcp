"""MCP server implementation using FastMCP for Kiwoom OpenAPI integration."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict

from fastmcp import FastMCP

from config import Settings, get_settings
from services.kiwoom_client import KiwoomClient
from services.token_manager import get_token_manager
from services import account, order


class KiwoomMCPServer:
    """MCP server that provides Kiwoom OpenAPI functionality."""

    def __init__(self):
        self.mcp = FastMCP("kiwoom-mcp")
        self._client = KiwoomClient(get_settings())
        self._setup_resources()
        self._setup_tools()

    def _setup_resources(self) -> None:
        """Setup MCP resources for configuration and status."""
        
        @self.mcp.resource("config://kiwoom")
        def get_kiwoom_config() -> str:
            """Get Kiwoom OpenAPI configuration."""
            settings = get_settings()
            token_manager = get_token_manager()
            token_info = token_manager.get_token_info()
            
            config = {
                "base_url": str(settings.base_url),
                "mock_base_url": str(settings.mock_base_url),
                "use_mock": settings.use_mock,
                "has_appkey": bool(settings.appkey),
                "has_secretkey": bool(settings.secretkey),
                "api_id": settings.api_id,
                "token_endpoint": settings.token_endpoint,
                "timeout_seconds": settings.timeout_seconds,
                "token_status": token_info,
            }
            return json.dumps(config, indent=2)

    def _setup_tools(self) -> None:
        """Setup MCP tools for Kiwoom OpenAPI operations."""
        
        @self.mcp.tool()
        async def get_accounts() -> Dict[str, Any]:
            """
            Get account information from Kiwoom OpenAPI.
            
            Returns:
                Account information including account numbers and balances
            """
            return await account.get_accounts(self._client)

        @self.mcp.tool()
        async def place_order(
            account_number: str,
            symbol: str,
            order_type: str,
            quantity: int,
            price: float | None = None,
            order_option: str = "00"
        ) -> Dict[str, Any]:
            """
            Place an order for stocks through Kiwoom OpenAPI.
            
            Args:
                account_number: Account number for the order
                symbol: Stock symbol/code to trade
                order_type: Order type (buy/sell)
                quantity: Number of shares to order
                price: Price per share (None for market order)
                order_option: Order option (00=지정가, 05=시장가, etc.)
                
            Returns:
                Order placement result
            """
            return await order.place_order(
                self._client, account_number, symbol, order_type, quantity, price, order_option
            )

        @self.mcp.tool()
        async def get_order_status(order_id: str) -> Dict[str, Any]:
            """
            Get the status of a specific order.
            
            Args:
                order_id: Order ID to check status for
                
            Returns:
                Order status information
            """
            return await order.get_order_status(self._client, order_id)

        @self.mcp.tool()
        async def get_account_balance(account_number: str) -> Dict[str, Any]:
            """
            Get balance information for a specific account.
            
            Args:
                account_number: Account number to get balance for
                
            Returns:
                Account balance information
            """
            return await account.get_account_balance(self._client, account_number)

        @self.mcp.tool()
        async def get_account_positions(account_number: str) -> Dict[str, Any]:
            """
            Get position information for a specific account.
            
            Args:
                account_number: Account number to get positions for
                
            Returns:
                Account positions information
            """
            return await account.get_account_positions(self._client, account_number)

        @self.mcp.tool()
        async def get_order_history(account_number: str, limit: int = 100) -> Dict[str, Any]:
            """
            Get order history for a specific account.
            
            Args:
                account_number: Account number to get order history for
                limit: Maximum number of orders to retrieve (default: 100)
                
            Returns:
                Order history information
            """
            return await order.get_order_history(self._client, account_number, limit)

        @self.mcp.tool()
        async def cancel_order(order_id: str) -> Dict[str, Any]:
            """
            Cancel a specific order.
            
            Args:
                order_id: Order ID to cancel
                
            Returns:
                Order cancellation result
            """
            return await order.cancel_order(self._client, order_id)

        @self.mcp.tool()
        async def refresh_token() -> Dict[str, Any]:
            """
            Manually refresh the authentication token.
            
            Returns:
                Token refresh result and status
            """
            try:
                token_manager = get_token_manager()
                new_token = await token_manager.force_refresh()
                token_info = token_manager.get_token_info()
                
                return {
                    "status": "success",
                    "message": "Token refreshed successfully",
                    "token_info": token_info
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Token refresh failed: {str(e)}"
                }

    async def close(self) -> None:
        """Close the HTTP client connection."""
        await self._client.close()

    def run(self) -> None:
        """Run the MCP server."""
        self.mcp.run()


# Create global server instance
mcp_server = KiwoomMCPServer()


def create_mcp_server() -> KiwoomMCPServer:
    """Create and return a new MCP server instance."""
    return KiwoomMCPServer()


__all__ = ["KiwoomMCPServer", "mcp_server", "create_mcp_server"]
