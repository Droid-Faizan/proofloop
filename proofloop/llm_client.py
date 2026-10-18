"""Backboard/OpenRouter client wrapper. API credentials stay server-side."""

from __future__ import annotations

import os
from typing import Any

DEFAULT_MODEL = "openai/gpt-4o-mini"


def _setting(name: str, default: str = "") -> str:
    value = os.getenv(name, "").strip()
    if value:
        return value
    # Streamlit-hosted secrets are supported as well as environment variables.
    try:
        import streamlit as st

        value = str(st.secrets.get(name, default)).strip()
        if value:
            return value
    except Exception:
        pass
    return default


def api_configuration() -> dict[str, str]:
    return {
        "api_key": _setting("BACKBOARD_API_KEY"),
        "model": _setting("MODEL_NAME", DEFAULT_MODEL) or DEFAULT_MODEL,
        "provider": _setting("LLM_PROVIDER", "openrouter") or "openrouter",
    }


async def generate_review(prompt: str) -> str:
    """Call Backboard once and return the actual model response or raise a clear error."""
    config = api_configuration()
    if not config["api_key"]:
        raise RuntimeError(
            "BACKBOARD_API_KEY is not configured. Add it to your environment or Streamlit secrets, then restart the app."
        )

    try:
        from backboard import BackboardClient
    except ImportError as exc:
        raise RuntimeError(
            "The Backboard SDK is not installed. Run `pip install -r requirements.txt` and restart the app."
        ) from exc

    client = BackboardClient(api_key=config["api_key"])
    response: Any = await client.send_message(
        prompt,
        llm_provider=config["provider"],
        model_name=config["model"],
        stream=False,
        json_output=True,
    )
    content = getattr(response, "content", None)
    if not content or not str(content).strip():
        raise RuntimeError("The AI service returned an empty response. Check the configured model and try again.")
    return str(content).strip()
