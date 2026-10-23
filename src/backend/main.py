"""Backend FastAPI untuk aplikasi demo skrining DASS-42.

Jalankan:  uvicorn src.backend.main:app --reload --port 8000
Dokumentasi interaktif: http://localhost:8000/docs
"""
from __future__ import annotations

import json
import random
from functools import lru_cache

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field, field_validator

from src.config import DATA_PROCESSED, ITEM_COLS, MODELS_DIR, ROOT, SCALES
from src.ml.predict import analyze, model_info, models_ready
from src.rag import llm
from src.rag.chat import answer, get_retriever

app = FastAPI(
    title="DASS-42 Demo Advisor API",
    description=("API demo: skoring resmi DASS-42, model klasifikasi, profil klaster, dan chatbot RAG. "
                 "Data responden berasal dari dataset publik anonim; aplikasi tidak memberikan kuesioner "
                 "kepada pengguna dan tidak memberikan diagnosis."),
    version="1.0.0",
)


# ---------- data responden demo ----------
@lru_cache(maxsize=1)
def demo_df() -> pd.DataFrame:
    return pd.read_csv(DATA_PROCESSED / "demo_respondents.csv").set_index("respondent_id")


@lru_cache(maxsize=1)
def item_texts() -> dict:
    return json.loads((ROOT / "data" / "dass42_items_en.json").read_text(encoding="utf-8"))["item"]


def answers_of(rid: int) -> dict[str, int]:
    df = demo_df()
    if rid not in df.index:
        raise HTTPException(status_code=404, detail=f"Responden {rid} tidak ada di data demo")
    row = df.loc[rid]
    return {c: int(row[c]) for c in ITEM_COLS}


@lru_cache(maxsize=1)
def demo_index() -> list[dict]:
    out = []
    for rid in demo_df().index:
        r = analyze(answers_of(int(rid)))
        out.append({"respondent_id": int(rid), "profil_id": r["profil"]["cluster_id"], "profil": r["profil"]["nama"],
                    **{f"tingkat_{s}": r["skoring_resmi"][s]["tingkat"] for s in SCALES}})
    return out


# ---------- skema ----------
class PredictRequest(BaseModel):
    answers: dict[str, int] = Field(..., description="42 jawaban Q1..Q42, nilai 0-3")

    @field_validator("answers")
    @classmethod
    def check(cls, v):
        missing = [c for c in ITEM_COLS if c not in v]
        if missing:
            raise ValueError(f"Jawaban kurang: {missing[:5]}…")
        bad = [k for k, x in v.items() if k in ITEM_COLS and x not in (0, 1, 2, 3)]
        if bad:
            raise ValueError(f"Nilai harus 0-3 pada {bad[:5]}")
        return v


class ChatTurn(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    history: list[ChatTurn] = Field(default_factory=list)
    respondent_id: int | None = Field(None, description="Responden demo yang sedang dilihat (opsional)")


# ---------- endpoint ----------
@app.get("/health")
def health():
    return {"status": "ok", "model_siap": models_ready(), "llm_aktif": llm.available(),
            "jumlah_chunk_rag": len(get_retriever().chunks), "jumlah_responden_demo": len(demo_df())}


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
        "korelasi_antar_skala": clu_meta["korelasi_antar_skala"],
        "profil": clu_meta["profil"],
        "llm_model": llm.model_name() if llm.available() else None,
    }


@app.get("/respondents")
def list_respondents(profil_id: int | None = Query(None, description="Filter per profil klaster")):
    rows = demo_index()
    if profil_id is not None:
        rows = [r for r in rows if r["profil_id"] == profil_id]
    return {"jumlah": len(rows), "responden": rows}


@app.get("/respondents/random")
def random_respondent(profil_id: int | None = None):
    rows = demo_index()
    if profil_id is not None:
        rows = [r for r in rows if r["profil_id"] == profil_id]
    if not rows:
        raise HTTPException(404, "Tidak ada responden untuk filter ini")
    return get_respondent(random.choice(rows)["respondent_id"])


@app.get("/respondents/{respondent_id}")
def get_respondent(respondent_id: int):
    ans = answers_of(respondent_id)
    texts = item_texts()
    items = {s: [{"item": f"Q{i}", "teks_en": texts[f"Q{i}"], "jawaban": ans[f"Q{i}"]} for i in idx]
             for s, idx in SCALES.items()}
    return {"respondent_id": respondent_id, "hasil": analyze(ans), "item_per_skala": items}


@app.post("/predict")
def predict(req: PredictRequest):
    """Analisis 42 jawaban. Dipakai frontend HANYA untuk responden dari dataset demo."""
    return analyze(req.answers)


@app.post("/chat")
def chat(req: ChatRequest):
    result = analyze(answers_of(req.respondent_id)) if req.respondent_id is not None else None
    return answer(req.message, history=[t.model_dump() for t in req.history], result=result)
