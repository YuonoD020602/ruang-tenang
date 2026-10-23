"""Analisis lengkap satu pengisian: skoring resmi + model klasifikasi + profil pola keluhan."""
from __future__ import annotations

import json
from functools import lru_cache

import joblib
import pandas as pd

from src.config import ITEM_COLS, LEVELS, MODELS_DIR, SCALES
from src.data.scoring import score_answers


@lru_cache(maxsize=1)
def _load():
    clf = joblib.load(MODELS_DIR / "classifier.joblib")
    clu = joblib.load(MODELS_DIR / "cluster.joblib")
    clf_meta = json.loads((MODELS_DIR / "classifier_meta.json").read_text(encoding="utf-8"))
    clu_meta = json.loads((MODELS_DIR / "cluster_profiles.json").read_text(encoding="utf-8"))
    profiles = {p["cluster_id"]: p for p in clu_meta["profil"]}
    return clf, clu, clf_meta, clu_meta, profiles


def models_ready() -> bool:
    try:
        _load()
        return True
    except Exception:
        return False


def model_info() -> dict:
    _, _, clf_meta, clu_meta, _ = _load()
    return {
        "klasifikasi": {"algoritma": clf_meta["algoritma_terpilih"], "registered_model": clf_meta["registered_model"],
                        "versi": clf_meta["registered_version"]},
        "clustering": {"k": clu_meta["k_terpilih"], "set_fitur": clu_meta["set_fitur_terpilih"],
                       "registered_model": clu_meta["registered_model"], "versi": clu_meta["registered_version"]},
        "profil": [{"cluster_id": p["cluster_id"], "nama": p["nama"], "ukuran_persen": p["ukuran_persen"]}
                   for p in clu_meta["profil"]],
    }


def analyze(answers: dict[str, int]) -> dict:
    clf, clu, _, _, profiles = _load()
    official = score_answers(answers)
    X = pd.DataFrame([[int(answers[c]) for c in ITEM_COLS]], columns=ITEM_COLS)

    pred = clf.predict(X)[0]
    klasifikasi, all_match = {}, True
    for j, scale in enumerate(SCALES):
        li = int(pred[j])
        match = li == official[scale]["tingkat_idx"]
        all_match &= match
        klasifikasi[scale] = {"tingkat_idx": li, "tingkat": LEVELS[scale][li], "sama_dengan_resmi": bool(match)}

    total = sum(official[s]["skor"] for s in SCALES)
    if total == 0:
        prof = {"cluster_id": None, "nama": "Tidak ada keluhan yang dilaporkan",
                "ringkas": "Semua pertanyaan dijawab \"tidak pernah\".",
                "deskripsi": "Tidak ada pola keluhan yang bisa digambarkan karena tidak ada keluhan yang dilaporkan.",
                "ukuran_persen": None}
        catatan = None
    else:
        cid = int(clu.predict(X)[0])
        prof = profiles[cid]
        low = all(official[s]["tingkat_idx"] == 0 for s in SCALES)
        catatan = ("Keluhan secara keseluruhan masih minimal, jadi pola ini hanya gambaran ringan."
                   if low else None)

    return {
        "skoring_resmi": official,
        "klasifikasi": {"per_skala": klasifikasi, "semua_sama_dengan_resmi": bool(all_match)},
        "profil": {"cluster_id": prof["cluster_id"], "nama": prof["nama"], "ringkas": prof["ringkas"],
                   "deskripsi": prof["deskripsi"], "ukuran_persen": prof["ukuran_persen"], "catatan": catatan},
        "pengingat": "Ini hasil skrining, bukan diagnosis.",
    }
