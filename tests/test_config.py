import pytest
from neuroforge.config import Settings


def test_settings_loads_with_valid_api_key(monkeypatch):
    monkeypatch.setenv("NEUROFORGE_API_KEY", "test-key-123")
    settings = Settings()
    assert settings.NEUROFORGE_API_KEY == "test-key-123"


def test_provider_defaults_to_anthropic(monkeypatch):
    monkeypatch.setenv("NEUROFORGE_API_KEY", "test-key-123")
    monkeypatch.delenv("NEUROFORGE_PROVIDER", raising=False)
    settings = Settings()
    assert settings.NEUROFORGE_PROVIDER == "anthropic"


def test_log_level_defaults_to_info(monkeypatch):
    monkeypatch.setenv("NEUROFORGE_API_KEY", "test-key-123")
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    settings = Settings()
    assert settings.LOG_LEVEL == "INFO"


def test_max_task_retries_defaults_to_3(monkeypatch):
    monkeypatch.setenv("NEUROFORGE_API_KEY", "test-key-123")
    monkeypatch.delenv("MAX_TASK_RETRIES", raising=False)
    settings = Settings()
    assert settings.MAX_TASK_RETRIES == 3


def test_neuroforge_max_tokens_defaults_to_4096(monkeypatch):
    monkeypatch.setenv("NEUROFORGE_API_KEY", "test-key-123")
    monkeypatch.delenv("NEUROFORGE_MAX_TOKENS", raising=False)
    settings = Settings()
    assert settings.NEUROFORGE_MAX_TOKENS == 4096
