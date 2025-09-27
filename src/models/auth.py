"""Authentication-related request and response models for Kiwoom OpenAPI."""

from pydantic import BaseModel, Field


class TokenIssueRequest(BaseModel):
    """Request payload for Kiwoom OAuth token issuance."""

    grant_type: str = Field(
        "client_credentials",
        description="OAuth grant type - must be 'client_credentials'",
    )
    appkey: str = Field(description="Kiwoom OpenAPI app key")
    secretkey: str = Field(description="Kiwoom OpenAPI secret key")


class TokenIssueResponse(BaseModel):
    """Response from Kiwoom OAuth token issuance API."""

    expires_dt: str = Field(description="Token expiration datetime (YYYYMMDDHHMMSS format)")
    token_type: str = Field(description="Token type, typically 'bearer'")
    token: str = Field(description="Access token for API calls")
    return_code: int = Field(description="Return code from Kiwoom API (0 for success)")
    return_msg: str = Field(description="Return message from Kiwoom API")


class TokenRevokeRequest(BaseModel):
    """Request payload for token revocation (placeholder for future implementation)."""

    token: str = Field(description="Previously issued token to revoke")
    token_type_hint: str | None = Field(
        default=None,
        description="Optional hint (e.g. 'access_token' or 'refresh_token')",
    )
