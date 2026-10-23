"""Uji endpoint FastAPI dengan TestClient."""
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.config import ITEM_COLS
from src.ml.predict import models_ready

pytestmark = pytest.mark.skipif(not models_ready(), reason="Model belum dilatih (jalankan pipeline)")
client = TestClient(app)
ZERO = {c: 0 for c in ITEM_COLS}


def test_health_and_questionnaire():
    assert client.get("/health").json()["model_siap"]
    q = client.get("/kuesioner").json()
    assert len(q["skala"]["depresi"]["item"]) == 9 and len(q["skala"]["kecemasan"]["item"]) == 7
    assert [p["nilai"] for p in q["pilihan"]] == [0, 1, 2, 3]


def test_predict_validation():
    assert client.post("/predict", json={"answers": {"P1": 1}}).status_code == 422
    assert client.post("/predict", json={"answers": {**ZERO, "P1": 5}}).status_code == 422
    ok = client.post("/predict", json={"answers": {c: 1 for c in ITEM_COLS}})
    assert ok.status_code == 200 and ok.json()["skoring_resmi"]["depresi"]["skor"] == 9


def test_predict_item9_flag():
    r = client.post("/predict", json={"answers": {**ZERO, "P9": 2}}).json()
    assert r["skoring_resmi"]["item9_positif"] is True


def test_info():
    r = client.get("/info").json()
    assert r["data"]["baris_bersih"] > 20000 and r["profil"]


def test_chat_with_answers():
    r = client.post("/chat", json={"message": "Apa arti hasil skriningku?",
                                   "answers": {**ZERO, "P3": 3, "P4": 3}}).json()
    assert "Hasil skriningmu" in r["jawaban"]


def test_chat_crisis():
    assert client.post("/chat", json={"message": "aku pengen mati aja"}).json()["mode"] == "krisis"
