"""Token management for Kiwoom OpenAPI authentication."""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Optional

from config import Settings, get_settings
from models import TokenIssueResponse


class TokenManager:
    """Manages Kiwoom OpenAPI tokens with automatic renewal."""

    def __init__(self, settings: Optional[Settings] = None):
        self._settings = settings or get_settings()
        self._token: Optional[str] = None
        self._token_type: Optional[str] = None
        self._expires_at: Optional[datetime] = None
        self._lock = asyncio.Lock()

    async def get_valid_token(self) -> str:
        """
        Get a valid access token, issuing a new one if needed.
        
        Returns:
            Valid access token string
            
        Raises:
            Exception: If token issuance fails
        """
        async with self._lock:
            if self._is_token_valid():
                return self._token

            # Token is expired or doesn't exist, get a new one
            await self._issue_new_token()
            return self._token

    def _is_token_valid(self) -> bool:
        """Check if current token is valid and not expired."""
        if not self._token or not self._expires_at:
            return False
        
        # Add 5 minute buffer before expiry
        buffer_time = timedelta(minutes=5)
        return datetime.now() + buffer_time < self._expires_at

    async def _issue_new_token(self) -> None:
        """Issue a new token from Kiwoom OpenAPI."""
        from .kiwoom_client import KiwoomClient
        
        client = KiwoomClient(self._settings)
        try:
            response = await client.request_access_token()
            
            # Check if request was successful
            if response.return_code != 0:
                raise Exception(f"Token issuance failed: {response.return_msg}")
            
            self._token = response.token
            self._token_type = response.token_type
            
            # Parse expiration datetime (YYYYMMDDHHMMSS format)
            expires_str = response.expires_dt
            self._expires_at = datetime.strptime(expires_str, "%Y%m%d%H%M%S")
            
        finally:
            await client.close()

    async def force_refresh(self) -> str:
        """
        Force refresh the token regardless of current validity.
        
        Returns:
            New access token string
        """
        async with self._lock:
            await self._issue_new_token()
            return self._token

    def get_token_info(self) -> dict:
        """Get current token information for debugging."""
        return {
            "has_token": bool(self._token),
            "token_type": self._token_type,
            "expires_at": self._expires_at.isoformat() if self._expires_at else None,
            "is_valid": self._is_token_valid(),
            "expires_in_minutes": (
                (self._expires_at - datetime.now()).total_seconds() / 60 
                if self._expires_at and self._is_token_valid() 
                else 0
            ),
        }


# Global token manager instance
_token_manager: Optional[TokenManager] = None


def get_token_manager() -> TokenManager:
    """Get the global token manager instance."""
    global _token_manager
    if _token_manager is None:
        _token_manager = TokenManager()
    return _token_manager


__all__ = ["TokenManager", "get_token_manager"]
