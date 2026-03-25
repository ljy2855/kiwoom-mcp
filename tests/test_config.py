"""Configuration tests for live vs mock credential selection."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from src.config import Settings


def test_settings_select_live_credentials_when_mock_is_disabled(monkeypatch) -> None:
    """Live credentials should be active when mock mode is off."""

    monkeypatch.setenv("KIWOOM_USE_MOCK", "false")
    monkeypatch.setenv("KIWOOM_APPKEY", "live-appkey")
    monkeypatch.setenv("KIWOOM_SECRETKEY", "live-secret")
    monkeypatch.delenv("KIWOOM_MOCK_APPKEY", raising=False)
    monkeypatch.delenv("KIWOOM_MOCK_SECRETKEY", raising=False)

    settings = Settings(_env_file=None)

    assert settings.active_appkey == "live-appkey"
    assert settings.active_secretkey == "live-secret"
    assert settings.active_base_url == "https://api.kiwoom.com/"


def test_settings_select_mock_credentials_when_enabled(monkeypatch) -> None:
    """Mock credentials should be active when mock mode is on."""

    monkeypatch.setenv("KIWOOM_USE_MOCK", "true")
    monkeypatch.setenv("KIWOOM_MOCK_APPKEY", "mock-appkey")
    monkeypatch.setenv("KIWOOM_MOCK_SECRETKEY", "mock-secret")
    monkeypatch.delenv("KIWOOM_APPKEY", raising=False)
    monkeypatch.delenv("KIWOOM_SECRETKEY", raising=False)

    settings = Settings(_env_file=None)

    assert settings.active_appkey == "mock-appkey"
    assert settings.active_secretkey == "mock-secret"
    assert settings.active_base_url == "https://mockapi.kiwoom.com/"


def test_settings_require_mock_credentials_when_enabled(monkeypatch) -> None:
    """Mock mode should fail fast if mock credentials are missing."""

    monkeypatch.setenv("KIWOOM_USE_MOCK", "true")
    monkeypatch.delenv("KIWOOM_APPKEY", raising=False)
    monkeypatch.delenv("KIWOOM_SECRETKEY", raising=False)
    monkeypatch.delenv("KIWOOM_MOCK_APPKEY", raising=False)
    monkeypatch.delenv("KIWOOM_MOCK_SECRETKEY", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
