from unittest.mock import MagicMock, patch
import pytest

from neuroforge.llm.client import LLMProviderError, call_llm


def test_call_llm_unsupported_provider(monkeypatch):
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_PROVIDER", "xyz")
    with pytest.raises(LLMProviderError, match="Unsupported provider 'xyz'"):
        call_llm(messages=[], system="sys")


def test_anthropic_provider(monkeypatch):
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_PROVIDER", "anthropic")
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_API_KEY", "test-key")
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_MODEL", "claude-sonnet-4-6")

    mock_anthropic_cls = MagicMock()
    mock_client = MagicMock()
    mock_anthropic_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_content = MagicMock()
    mock_content.text = "Anthropic response"
    mock_response.content = [mock_content]
    mock_client.messages.create.return_value = mock_response

    with patch.dict("sys.modules", {"anthropic": MagicMock(Anthropic=mock_anthropic_cls)}):
        res = call_llm(messages=[{"role": "user", "content": "hi"}], system="system prompt", max_tokens=100)

    assert res == "Anthropic response"
    mock_anthropic_cls.assert_called_once_with(api_key="test-key")
    mock_client.messages.create.assert_called_once_with(
        model="claude-sonnet-4-6",
        max_tokens=100,
        system="system prompt",
        messages=[{"role": "user", "content": "hi"}],
    )


def test_openai_provider(monkeypatch):
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_PROVIDER", "openai")
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_API_KEY", "test-openai-key")
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_MODEL", "gpt-4o")

    mock_openai_cls = MagicMock()
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "OpenAI response"
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    with patch.dict("sys.modules", {"openai": MagicMock(OpenAI=mock_openai_cls)}):
        res = call_llm(messages=[{"role": "user", "content": "hi"}], system="system prompt", max_tokens=200)

    assert res == "OpenAI response"
    mock_openai_cls.assert_called_once_with(api_key="test-openai-key")
    mock_client.chat.completions.create.assert_called_once_with(
        model="gpt-4o",
        max_tokens=200,
        messages=[
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "hi"},
        ],
    )


def test_openai_compatible_provider(monkeypatch):
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_PROVIDER", "openai-compatible")
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_API_KEY", "test-compat-key")
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_BASE_URL", "http://localhost:11434/v1")
    monkeypatch.setattr("neuroforge.config.config.NEUROFORGE_MODEL", "llama3")

    mock_openai_cls = MagicMock()
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client

    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_choice.message.content = "Compat response"
    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    with patch.dict("sys.modules", {"openai": MagicMock(OpenAI=mock_openai_cls)}):
        res = call_llm(messages=[{"role": "user", "content": "hello"}], system="system prompt")

    assert res == "Compat response"
    mock_openai_cls.assert_called_once_with(
        api_key="test-compat-key",
        base_url="http://localhost:11434/v1",
    )
    mock_client.chat.completions.create.assert_called_once_with(
        model="llama3",
        max_tokens=1024,
        messages=[
            {"role": "system", "content": "system prompt"},
            {"role": "user", "content": "hello"},
        ],
    )
