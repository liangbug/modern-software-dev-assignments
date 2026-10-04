import os
from types import SimpleNamespace
from typing import Optional

from google import genai
from google.genai import types

_client: Optional[genai.Client] = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file or environment."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def chat(model: str, messages: list, options: Optional[dict] = None) -> SimpleNamespace:
    """Drop-in replacement for ollama.chat(), backed by the Gemini API.

    Accepts the same [{"role": ..., "content": ...}, ...] message list and
    options={"temperature": ...} shape as ollama.chat(), and returns an
    object exposing response.message.content like the ollama client does.
    """
    options = options or {}
    system_instruction = None
    contents = []
    for message in messages:
        role = message["role"]
        content = message["content"]
        if role == "system":
            system_instruction = content
        else:
            contents.append(
                types.Content(
                    role="model" if role == "assistant" else "user",
                    parts=[types.Part.from_text(text=content)],
                )
            )

    config = types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=options.get("temperature"),
    )
    response = _get_client().models.generate_content(
        model=model,
        contents=contents,
        config=config,
    )
    return SimpleNamespace(message=SimpleNamespace(content=response.text))
