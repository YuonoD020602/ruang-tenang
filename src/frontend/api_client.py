"""Klien HTTP sederhana ke backend FastAPI."""
from __future__ import annotations

import os

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 60


class BackendError(RuntimeError):
    pass


def _get(path: str):
    try:
        r = requests.get(f"{BACKEND_URL}{path}", timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise BackendError(f"Gagal menghubungi backend ({BACKEND_URL}{path}): {e}") from e


def _post(path: str, payload: dict):
    try:
        r = requests.post(f"{BACKEND_URL}{path}", json=payload, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise BackendError(f"Gagal menghubungi backend ({BACKEND_URL}{path}): {e}") from e


def health():
    return _get("/health")


def info():
    return _get("/info")


def questionnaire():
    return _get("/kuesioner")


def predict(answers: dict):
    return _post("/predict", {"answers": answers})


def chat(message: str, history: list[dict], answers: dict | None):
    return _post("/chat", {"message": message, "history": history, "answers": answers})
