from __future__ import annotations

from neuroforge.config import config


class LLMProviderError(Exception):
    pass


def call_llm(messages: list[dict], system: str, max_tokens: int = 1024) -> str:
    provider = config.NEUROFORGE_PROVIDER

    if provider == "anthropic":
        from anthropic import Anthropic

        client = Anthropic(api_key=config.NEUROFORGE_API_KEY)
        response = client.messages.create(
            model=config.NEUROFORGE_MODEL,
            max_tokens=max_tokens,
            system=system,
            messages=messages,
        )
        return response.content[0].text

    elif provider == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=config.NEUROFORGE_API_KEY)
        all_messages = [{"role": "system", "content": system}] + messages
        response = client.chat.completions.create(
            model=config.NEUROFORGE_MODEL,
            max_tokens=max_tokens,
            messages=all_messages,
        )
        return response.choices[0].message.content

    elif provider == "openai-compatible":
        from openai import OpenAI

        client = OpenAI(
            api_key=config.NEUROFORGE_API_KEY,
            base_url=config.NEUROFORGE_BASE_URL,
        )
        all_messages = [{"role": "system", "content": system}] + messages
        response = client.chat.completions.create(
            model=config.NEUROFORGE_MODEL,
            max_tokens=max_tokens,
            messages=all_messages,
        )
        return response.choices[0].message.content

    else:
        raise LLMProviderError(
            f"Unsupported provider '{config.NEUROFORGE_PROVIDER}'. "
            "Valid options: anthropic, openai, openai-compatible"
        )
