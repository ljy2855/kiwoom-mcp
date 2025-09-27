"""Order-related service functions for Kiwoom OpenAPI."""

from datetime import datetime
from typing import Dict, Any
from .kiwoom_client import KiwoomClient
from constants import ORDER_APIS, ACCOUNT_APIS


async def place_order(
    client: KiwoomClient,
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
        client: KiwoomClient instance
        account_number: Account number for the order
        symbol: Stock symbol/code to trade
        order_type: Order type (buy/sell)
        quantity: Number of shares to order
        price: Price per share (None for market order)
        order_option: Order option (00=지정가, 05=시장가, etc.)
        
    Returns:
        Order placement result
    """
    try:
        # Select appropriate API based on order type
        if order_type.lower() == "buy":
            api_info = ORDER_APIS["BUY_ORDER"]
        elif order_type.lower() == "sell":
            api_info = ORDER_APIS["SELL_ORDER"]
        else:
            return {
                "error": "Invalid order type",
                "message": "Order type must be 'buy' or 'sell'"
            }
        
        # Prepare order data according to Kiwoom API format
        order_data = {
            "account_number": account_number,
            "symbol": symbol,
            "order_type": order_type,
            "quantity": quantity,
            "price": price,
            "order_option": order_option,
            "timestamp": str(int(datetime.now().timestamp() * 1000))
        }
        
        response = await client.post(api_info.url, json=order_data)
        
        return {
            "status_code": response.status_code,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "order_result": response.json() if response.status_code == 200 else None,
            "message": "Order placed successfully" if response.status_code == 200 else "Failed to place order"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Order placement endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_order_status(client: KiwoomClient, order_id: str) -> Dict[str, Any]:
    """
    Get the status of a specific order.
    
    Args:
        client: KiwoomClient instance
        order_id: Order ID to check status for
        
    Returns:
        Order status information
    """
    try:
        # Use the actual Kiwoom API for order execution status
        api_info = ACCOUNT_APIS["ORDER_EXECUTION_STATUS"]
        response = await client.get(api_info.url)
        
        return {
            "status_code": response.status_code,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "order_id": order_id,
            "order_status": response.json() if response.status_code == 200 else None,
            "message": "Order status retrieved successfully" if response.status_code == 200 else "Failed to retrieve order status"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Order status endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_order_history(client: KiwoomClient, account_number: str, limit: int = 100) -> Dict[str, Any]:
    """
    Get order history for a specific account.
    
    Args:
        client: KiwoomClient instance
        account_number: Account number to get order history for
        limit: Maximum number of orders to retrieve
        
    Returns:
        Order history information
    """
    try:
        # Use the actual Kiwoom API for order execution detail
        api_info = ACCOUNT_APIS["ORDER_EXECUTION_DETAIL"]
        params = {"limit": limit} if limit else {}
        response = await client.get(api_info.url, params=params)
        
        return {
            "status_code": response.status_code,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "account_number": account_number,
            "orders": response.json() if response.status_code == 200 else None,
            "message": "Order history retrieved successfully" if response.status_code == 200 else "Failed to retrieve order history"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Order history endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def cancel_order(client: KiwoomClient, order_id: str) -> Dict[str, Any]:
    """
    Cancel a specific order.
    
    Args:
        client: KiwoomClient instance
        order_id: Order ID to cancel
        
    Returns:
        Order cancellation result
    """
    try:
        # Use the actual Kiwoom API for cancel order
        api_info = ORDER_APIS["CANCEL_ORDER"]
        
        # Prepare cancellation data
        cancel_data = {
            "order_id": order_id,
            "timestamp": str(int(datetime.now().timestamp() * 1000))
        }
        
        response = await client.post(api_info.url, json=cancel_data)
        
        return {
            "status_code": response.status_code,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "order_id": order_id,
            "cancel_result": response.json() if response.status_code == 200 else None,
            "message": "Order cancelled successfully" if response.status_code == 200 else "Failed to cancel order"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Order cancellation endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


__all__ = ["place_order", "get_order_status", "get_order_history", "cancel_order"]
