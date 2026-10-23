"""Klien LLM berformat OpenAI-compatible (default: Groq). Opsional.

Variabel lingkungan:
  LLM_API_KEY  atau  GROQ_API_KEY   -> kunci API (kalau kosong, chatbot memakai mode tanpa LLM)
  LLM_BASE_URL  (default https://api.groq.com/openai/v1)
  LLM_MODEL     (default openai/gpt-oss-120b)
"""
from __future__ import annotations

import os

import requests

DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_MODEL = "openai/gpt-oss-120b"


def _key() -> str | None:
    return os.getenv("LLM_API_KEY") or os.getenv("GROQ_API_KEY") or None


def available() -> bool:
    return _key() is not None


def model_name() -> str:
    return os.getenv("LLM_MODEL", DEFAULT_MODEL)


def chat(messages: list[dict], temperature: float = 0.2, max_tokens: int = 700, timeout: int = 40) -> str:
    """Kirim percakapan, kembalikan teks jawaban. Melempar exception jika gagal."""
    url = os.getenv("LLM_BASE_URL", DEFAULT_BASE_URL).rstrip("/") + "/chat/completions"
    resp = requests.post(
        url,
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
        json={"model": model_name(), "messages": messages, "temperature": temperature, "max_tokens": max_tokens},
        timeout=timeout,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()
