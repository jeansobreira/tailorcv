"""Tests for llm.py — LLM provider routing."""

from unittest.mock import MagicMock

import pytest

import llm


def test_call_llm_openai(monkeypatch, mocker) -> None:
    """_call_llm uses OpenAI SDK when OPENAI_API_KEY is set."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    mock_choice = MagicMock()
    mock_choice.message.content = "result"
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    mocker.patch("llm.OpenAI", return_value=mock_client)

    result = llm.call_llm("sys", "usr")

    assert result == "result"
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"


def test_call_llm_anthropic(monkeypatch, mocker) -> None:
    """_call_llm uses Anthropic SDK when ANTHROPIC_API_KEY is set."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "ant-test")
    monkeypatch.setenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    mock_content = MagicMock()
    mock_content.text = "result-anthropic"
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(content=[mock_content])
    mocker.patch("llm.Anthropic", return_value=mock_client)

    result = llm.call_llm("sys", "usr")

    assert result == "result-anthropic"
    mock_client.messages.create.assert_called_once()
    call_kwargs = mock_client.messages.create.call_args.kwargs
    assert call_kwargs["model"] == "claude-haiku-4-5-20251001"
    assert call_kwargs["system"] == "sys"


def test_call_llm_gemini(monkeypatch, mocker) -> None:
    """_call_llm uses OpenAI-compat client for Gemini when GOOGLE_API_KEY is set."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.setenv("GOOGLE_API_KEY", "AIza-test")
    monkeypatch.setenv("GEMINI_MODEL", "gemini-1.5-flash")

    mock_choice = MagicMock()
    mock_choice.message.content = "result-gemini"
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    mocker.patch("llm.OpenAI", return_value=mock_client)

    result = llm.call_llm("sys", "usr")

    assert result == "result-gemini"
    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gemini-1.5-flash"


def test_call_llm_priority_openai_over_anthropic(monkeypatch, mocker) -> None:
    """OpenAI takes priority over Anthropic when both keys are set."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "ant-test")

    mock_choice = MagicMock()
    mock_choice.message.content = "ok"
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    mock_openai = mocker.patch("llm.OpenAI", return_value=mock_client)
    mock_anthropic = mocker.patch("llm.Anthropic")

    llm.call_llm("sys", "usr")

    mock_openai.assert_called_once()
    mock_anthropic.assert_not_called()


def test_call_llm_priority_anthropic_over_gemini(monkeypatch, mocker) -> None:
    """Anthropic takes priority over Gemini when both keys are set."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "ant-test")
    monkeypatch.setenv("GOOGLE_API_KEY", "AIza-test")

    mock_content = MagicMock()
    mock_content.text = "ok"
    mock_client = MagicMock()
    mock_client.messages.create.return_value = MagicMock(content=[mock_content])
    mock_anthropic = mocker.patch("llm.Anthropic", return_value=mock_client)
    mock_openai = mocker.patch("llm.OpenAI")

    llm.call_llm("sys", "usr")

    mock_anthropic.assert_called_once()
    mock_openai.assert_not_called()


def test_call_llm_default_models(monkeypatch, mocker) -> None:
    """call_llm falls back to default model names when model vars are absent."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.delenv("OPENAI_MODEL", raising=False)

    mock_choice = MagicMock()
    mock_choice.message.content = "ok"
    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = MagicMock(choices=[mock_choice])
    mocker.patch("llm.OpenAI", return_value=mock_client)

    llm.call_llm("sys", "usr")

    call_kwargs = mock_client.chat.completions.create.call_args.kwargs
    assert call_kwargs["model"] == "gpt-4o-mini"


def test_call_llm_raises_without_keys(monkeypatch) -> None:
    """call_llm raises RuntimeError when no API key is configured."""
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="Nenhuma chave de API"):
        llm.call_llm("sys", "usr")
