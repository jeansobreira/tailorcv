"""LLM provider routing: OpenAI, Anthropic, or Gemini (OpenAI-compatible)."""

import os

from anthropic import Anthropic
from openai import OpenAI

_GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"


def call_llm(system_prompt: str, user_message: str) -> str:
    """Call the configured LLM provider and return the text response.

    Provider priority: OpenAI → Anthropic → Gemini (OpenAI-compatible endpoint).

    Args:
        system_prompt: The system/instruction prompt.
        user_message: The user message to send.

    Returns:
        The LLM text response.

    Raises:
        RuntimeError: If no API key is configured.
    """
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        client = OpenAI(api_key=openai_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content

    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        model = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001")
        client = Anthropic(api_key=anthropic_key)
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        model = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        client = OpenAI(api_key=google_key, base_url=_GEMINI_BASE_URL)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
        )
        return response.choices[0].message.content

    raise RuntimeError(
        "Nenhuma chave de API configurada. "
        "Defina OPENAI_API_KEY, ANTHROPIC_API_KEY ou GOOGLE_API_KEY no .env."
    )
