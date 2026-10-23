"""Backend FastAPI untuk aplikasi skrining mandiri PHQ-9 & GAD-7.

Jalankan:  uvicorn src.backend.main:app --reload --port 8000
Dokumentasi interaktif: http://localhost:8000/docs

Privasi: jawaban pengguna hanya dipakai untuk menghitung hasil saat itu dan TIDAK disimpan.
"""
from __future__ import annotations

import json
from functools import lru_cache

from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

from src.config import DATA_PROCESSED, ITEM_COLS, MODELS_DIR, QUESTIONNAIRE_FILE
from src.ml.predict import analyze, model_info, models_ready
from src.rag import llm
from src.rag.chat import answer, get_retriever

app = FastAPI(
    title="Skrining Mandiri PHQ-9 & GAD-7 API",
    description=("Skoring resmi PHQ-9 (depresi) & GAD-7 (kecemasan), model klasifikasi, profil pola keluhan, "
                 "dan chatbot RAG berbasis dokumen WHO. Jawaban tidak disimpan. Hasil adalah skrining, bukan diagnosis."),
    version="2.0.0",
)


@lru_cache(maxsize=1)
def questionnaire() -> dict:
    return json.loads(QUESTIONNAIRE_FILE.read_text(encoding="utf-8"))


def _validate_answers(v: dict[str, int]) -> dict[str, int]:
    missing = [c for c in ITEM_COLS if c not in v]
    if missing:
        raise ValueError(f"Jawaban kurang: {missing}")
    bad = [k for k in ITEM_COLS if v[k] not in (0, 1, 2, 3)]
    if bad:
        raise ValueError(f"Nilai harus 0-3 pada {bad}")
    return {k: int(v[k]) for k in ITEM_COLS}


class PredictRequest(BaseModel):
    answers: dict[str, int] = Field(..., description="16 jawaban: P1..P9 (PHQ-9) dan G1..G7 (GAD-7), nilai 0-3")

    @field_validator("answers")
    @classmethod
    def check(cls, v):
        return _validate_answers(v)


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list)
    answers: dict[str, int] | None = Field(None, description="Jawaban kuesioner (opsional) agar chatbot bisa "
                                                            "menjelaskan hasil; tidak disimpan")

    @field_validator("answers")
    @classmethod
    def check(cls, v):
        return None if v is None else _validate_answers(v)


@app.get("/health")
def health():
    return {"status": "ok", "model_siap": models_ready(), "llm_aktif": llm.available(),
            "jumlah_chunk_rag": len(get_retriever().chunks)}


@app.get("/kuesioner")
def get_questionnaire():
    """Teks petunjuk, pilihan jawaban, dan 16 item dalam Bahasa Indonesia."""
    return questionnaire()


@app.get("/info")
def info():
    report = json.loads((DATA_PROCESSED / "laporan_pembersihan.json").read_text(encoding="utf-8"))
    clf_meta = json.loads((MODELS_DIR / "classifier_meta.json").read_text(encoding="utf-8"))
    clu_meta = json.loads((MODELS_DIR / "cluster_profiles.json").read_text(encoding="utf-8"))
    return {
        "model": model_info(),
        "data": report,
        "evaluasi_klasifikasi": clf_meta["perbandingan_model"],
        "pengurangan_item": clf_meta["pengurangan_item"],
        "evaluasi_clustering": clu_meta["perbandingan"],
        "korelasi_antar_skala": clu_meta.get("korelasi_antar_skala"),
        "profil": clu_meta["profil"],
        "llm_model": llm.model_name() if llm.available() else None,
    }


@app.post("/predict")
def predict(req: PredictRequest):
    return analyze(req.answers)


@app.post("/chat")
def chat(req: ChatRequest):
    result = analyze(req.answers) if req.answers else None
    return answer(req.message, history=[t.model_dump() for t in req.history], result=result)
