from __future__ import annotations

from config import Settings


def llm_health_hint(settings: Settings) -> str:
    if settings.llm_provider == "ollama":
        return f"Ollama expected at {settings.ollama_base_url} with model {settings.ollama_chat_model}"
    return f"OpenAI-compatible endpoint expected at {settings.openai_base_url}"

