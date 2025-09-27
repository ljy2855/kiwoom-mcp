"""HTTP client wrapper around the Kiwoom OpenAPI."""

from __future__ import annotations

import uuid
from typing import Any

import httpx

from config import Settings
from models import TokenIssueResponse
from constants import OAUTH_APIS
from .token_manager import get_token_manager


class KiwoomClient:
    """Thin client responsible for talking to the Kiwoom OpenAPI endpoints."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._token_manager = get_token_manager()
        # Use mock URL if specified, otherwise use production URL
        base_url = str(settings.mock_base_url) if settings.use_mock else str(settings.base_url)
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=settings.timeout_seconds,
            headers={"User-Agent": f"kiwoom-mcp/{uuid.uuid4()}"},
        )

    async def close(self) -> None:
        """Close the underlying HTTP session."""

        await self._client.aclose()

    async def request_access_token(
        self,
        *,
        grant_type: str = "client_credentials",
    ) -> TokenIssueResponse:
        """Issue an OAuth token using the configured appkey and secretkey."""

        payload = {
            "grant_type": grant_type,
            "appkey": self._settings.appkey,
            "secretkey": self._settings.secretkey,
        }

        # Get token issuance API info
        token_api = OAUTH_APIS["TOKEN_ISSUE"]
        
        # Kiwoom API requires specific headers
        headers = {
            "api-id": token_api.api_id,
            "Content-Type": "application/json; charset=UTF-8",
        }

        response = await self._client.post(
            token_api.url,
            json=payload,
            headers=headers,
        )
        response.raise_for_status()
        return TokenIssueResponse.model_validate(response.json())

    async def revoke_token(self, *, token: str, token_type_hint: str | None = None) -> None:
        """Revoke a previously issued token (placeholder - Kiwoom API may not support this)."""

        # Note: Kiwoom API documentation doesn't show a revoke endpoint
        # This is a placeholder for potential future implementation
        payload: dict[str, Any] = {"token": token}
        if token_type_hint:
            payload["token_type_hint"] = token_type_hint

        # For now, just raise an error indicating this feature is not available
        raise NotImplementedError("Token revocation is not yet implemented for Kiwoom OpenAPI")

    async def _get_auth_headers(self, additional_headers: dict[str, str] | None = None) -> dict[str, str]:
        """Get headers with authentication token."""
        token = await self._token_manager.get_valid_token()
        
        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "authorization": f"Bearer {token}",
        }
        
        if additional_headers:
            headers.update(additional_headers)
            
        return headers

    async def get(self, path: str, *, headers: dict[str, str] | None = None, params: dict[str, Any] | None = None) -> httpx.Response:
        """Perform a GET request against the Kiwoom OpenAPI with automatic authentication."""

        auth_headers = await self._get_auth_headers(headers)
        response = await self._client.get(path, headers=auth_headers, params=params)
        response.raise_for_status()
        return response

    async def post(
        self,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Perform a POST request against the Kiwoom OpenAPI with automatic authentication."""

        auth_headers = await self._get_auth_headers(headers)
        response = await self._client.post(path, headers=auth_headers, params=params, json=json, data=data)
        response.raise_for_status()
        return response


__all__ = ["KiwoomClient"]
