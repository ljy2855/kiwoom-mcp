"""Application configuration and settings management."""

from functools import lru_cache

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables or .env files."""

    appkey: str = Field(..., alias="KIWOOM_APPKEY", description="Kiwoom OpenAPI app key")
    secretkey: str = Field(..., alias="KIWOOM_SECRETKEY", description="Kiwoom OpenAPI secret key")
    base_url: HttpUrl = Field(
        "https://api.kiwoom.com",
        alias="KIWOOM_BASE_URL",
        description="Base URL for Kiwoom OpenAPI REST endpoints (production)",
    )
    mock_base_url: HttpUrl = Field(
        "https://mockapi.kiwoom.com",
        alias="KIWOOM_MOCK_BASE_URL",
        description="Base URL for Kiwoom OpenAPI mock endpoints (KRX only)",
    )
    token_endpoint: str = Field(
        "/oauth2/token",
        alias="KIWOOM_TOKEN_ENDPOINT",
        description="Relative path for token issuance",
    )
    use_mock: bool = Field(
        False,
        alias="KIWOOM_USE_MOCK",
        description="Whether to use mock API endpoint (for KRX testing)",
    )
    timeout_seconds: float = Field(10.0, description="HTTP client timeout in seconds")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""

    return Settings()


__all__ = ["Settings", "get_settings"]
