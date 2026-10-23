"""Klien HTTP sederhana ke backend FastAPI."""
from __future__ import annotations

import os

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
TIMEOUT = 60


class BackendError(RuntimeError):
    pass


def _get(path: str, **params):
    try:
        r = requests.get(f"{BACKEND_URL}{path}", params={k: v for k, v in params.items() if v is not None},
                         timeout=TIMEOUT)
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


def list_respondents(profil_id: int | None = None):
    return _get("/respondents", profil_id=profil_id)


def random_respondent(profil_id: int | None = None):
    return _get("/respondents/random", profil_id=profil_id)


def get_respondent(respondent_id: int):
    return _get(f"/respondents/{respondent_id}")


def chat(message: str, history: list[dict], respondent_id: int | None):
    return _post("/chat", {"message": message, "history": history, "respondent_id": respondent_id})
