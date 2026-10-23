"""Uji endpoint FastAPI dengan TestClient."""
import pytest
from fastapi.testclient import TestClient

from src.backend.main import app
from src.config import ITEM_COLS
from src.ml.predict import models_ready

pytestmark = pytest.mark.skipif(not models_ready(), reason="Model belum dilatih (jalankan pipeline)")
client = TestClient(app)


def test_health():
    r = client.get("/health").json()
    assert r["status"] == "ok" and r["model_siap"] and r["jumlah_chunk_rag"] > 50


def test_respondents_and_detail():
    lst = client.get("/respondents").json()
    assert lst["jumlah"] > 0
    rid = lst["responden"][0]["respondent_id"]
    d = client.get(f"/respondents/{rid}").json()
    assert d["respondent_id"] == rid and len(sum(d["item_per_skala"].values(), [])) == 42


def test_unknown_respondent_404():
    assert client.get("/respondents/999999999").status_code == 404


def test_predict_validation():
    assert client.post("/predict", json={"answers": {"Q1": 1}}).status_code == 422
    assert client.post("/predict", json={"answers": {c: 5 for c in ITEM_COLS}}).status_code == 422
    ok = client.post("/predict", json={"answers": {c: 1 for c in ITEM_COLS}})
    assert ok.status_code == 200 and ok.json()["skoring_resmi"]["depresi"]["skor"] == 14


def test_chat_with_respondent_context():
    rid = client.get("/respondents").json()["responden"][0]["respondent_id"]
    r = client.post("/chat", json={"message": "Apa arti hasil ini?", "respondent_id": rid}).json()
    assert "Responden contoh ini" in r["jawaban"]


def test_chat_crisis():
    r = client.post("/chat", json={"message": "aku pengen mati aja"}).json()
    assert r["mode"] == "krisis"
