"""Account-related service functions for Kiwoom OpenAPI."""

from typing import Dict, Any
from .kiwoom_client import KiwoomClient
from constants import ACCOUNT_APIS


async def get_accounts(client: KiwoomClient) -> Dict[str, Any]:
    """
    Get account information from Kiwoom OpenAPI.
    
    Args:
        client: KiwoomClient instance
        
    Returns:
        Account information including account numbers and balances
    """
    try:
        # Use the actual Kiwoom API for account evaluation
        api_info = ACCOUNT_APIS["ACCOUNT_EVALUATION"]
        response = await client.get(api_info.url)
        
        return {
            "status_code": response.status_code,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "accounts": response.json() if response.status_code == 200 else None,
            "message": "Account information retrieved successfully" if response.status_code == 200 else "Failed to retrieve account information"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Account information endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_account_balance(client: KiwoomClient, account_number: str) -> Dict[str, Any]:
    """
    Get balance information for a specific account.
    
    Args:
        client: KiwoomClient instance
        account_number: Account number to get balance for
        
    Returns:
        Account balance information
    """
    try:
        # Use the actual Kiwoom API for executed balance
        api_info = ACCOUNT_APIS["EXECUTED_BALANCE"]
        response = await client.get(api_info.url)
        
        return {
            "status_code": response.status_code,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "account_number": account_number,
            "balance": response.json() if response.status_code == 200 else None,
            "message": "Account balance retrieved successfully" if response.status_code == 200 else "Failed to retrieve account balance"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Account balance endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


async def get_account_positions(client: KiwoomClient, account_number: str) -> Dict[str, Any]:
    """
    Get position information for a specific account.
    
    Args:
        client: KiwoomClient instance
        account_number: Account number to get positions for
        
    Returns:
        Account positions information
    """
    try:
        # Use the actual Kiwoom API for executed balance (positions)
        api_info = ACCOUNT_APIS["EXECUTED_BALANCE"]
        response = await client.get(api_info.url)
        
        return {
            "status_code": response.status_code,
            "api_id": api_info.api_id,
            "api_name": api_info.name,
            "account_number": account_number,
            "positions": response.json() if response.status_code == 200 else None,
            "message": "Account positions retrieved successfully" if response.status_code == 200 else "Failed to retrieve account positions"
        }
    except Exception as e:
        return {
            "error": str(e),
            "message": "Account positions endpoint not yet implemented or failed to connect",
            "note": "This requires proper Kiwoom API endpoint configuration"
        }


__all__ = ["get_accounts", "get_account_balance", "get_account_positions"]