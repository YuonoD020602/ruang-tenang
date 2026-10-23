"""Pipeline data: CSV mentah Zenodo -> data bersih berskor -> split train/test.

Jalankan:  python -m src.data.pipeline
"""
from __future__ import annotations

import json

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import DATA_PROCESSED, DATA_RAW, ITEM_COLS, RANDOM_STATE
from src.data.scoring import score_frame

RAW_DIR = DATA_RAW / "phq_gad"
CLEANING = {
    "age_min": 18,          # aplikasi untuk dewasa; juga membuang usia tidak masuk akal (mis. 1 atau 99)
    "age_max": 60,
    "min_total_seconds": 16,  # < 1 detik per item untuk 16 item dianggap asal-asalan
}


def load_raw() -> pd.DataFrame:
    p = pd.read_csv(RAW_DIR / "phq9.csv")
    g = pd.read_csv(RAW_DIR / "gad7.csv")
    m = pd.read_csv(RAW_DIR / "demographic.csv")
    p = p.rename(columns={f"question{i}": f"P{i}" for i in range(1, 10)} | {f"time{i}": f"tP{i}" for i in range(1, 10)})
    g = g.rename(columns={f"question{i}": f"G{i}" for i in range(1, 8)} | {f"time{i}": f"tG{i}" for i in range(1, 8)})
    df = p.drop(columns="score").merge(g.drop(columns="score"), on="export_id").merge(m[["export_id", "age"]],
                                                                                     on="export_id")
    return df


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    c = CLEANING
    time_cols = [col for col in raw.columns if col.startswith("t") and col[1:] in ITEM_COLS]
    items = raw[ITEM_COLS]
    m_age = raw["age"].between(c["age_min"], c["age_max"])
    # jawaban sama untuk semua 16 item TETAPI bukan nol semua (semua 0 = tidak ada keluhan, itu sah)
    m_straight = ~((items.std(axis=1) == 0) & (items.sum(axis=1) > 0))
    m_fast = raw[time_cols].sum(axis=1) >= c["min_total_seconds"]
    keep = m_age & m_straight & m_fast
    report = {
        "baris_awal": int(len(raw)),
        "dibuang_usia_di_luar_18_60": int((~m_age).sum()),
        "dibuang_jawaban_seragam_bukan_nol": int((~m_straight).sum()),
        "dibuang_total_waktu_kurang_16_detik": int((~m_fast).sum()),
        "baris_bersih": int(keep.sum()),
    }
    # Hanya jawaban item yang dibawa; demografi tidak dipakai sebagai fitur.
    out = raw.loc[keep, ["export_id"] + ITEM_COLS].rename(columns={"export_id": "respondent_id"})
    return out.reset_index(drop=True), report


def run() -> dict:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    data, report = clean(load_raw())
    data = score_frame(data)

    strat = data["tingkat_depresi"].astype(str) + data["tingkat_kecemasan"].astype(str)
    rare = strat.map(strat.value_counts()) < 10
    strat = strat.where(~rare, "lain")
    if (strat == "lain").sum() < 2:
        strat = strat.where(strat != "lain", strat.mode()[0])
    train, test = train_test_split(data, test_size=0.2, random_state=RANDOM_STATE, stratify=strat)
    train.to_csv(DATA_PROCESSED / "train.csv", index=False)
    test.to_csv(DATA_PROCESSED / "test.csv", index=False)

    report.update({
        "baris_train": int(len(train)), "baris_test": int(len(test)),
        "tanpa_keluhan_semua_nol_persen": round(100 * float((data[ITEM_COLS].sum(axis=1) == 0).mean()), 1),
        "item9_positif_persen": round(100 * float((data["P9"] > 0).mean()), 2),
        "korelasi_phq9_gad7": round(float(data["skor_depresi"].corr(data["skor_kecemasan"])), 2),
    })
    for sc in ("depresi", "kecemasan"):
        report[f"sebaran_tingkat_{sc}_persen"] = (
            data[f"tingkat_{sc}"].value_counts(normalize=True).sort_index().mul(100).round(1).tolist())
    (DATA_PROCESSED / "laporan_pembersihan.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
