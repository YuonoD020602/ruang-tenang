"""Pipeline data: ZIP mentah -> data bersih berskor -> split train/test -> responden demo.

Jalankan:  python -m src.data.pipeline
"""
from __future__ import annotations

import io
import json
import zipfile

import pandas as pd
from sklearn.model_selection import train_test_split

from src.config import CLEANING, DATA_PROCESSED, DATA_RAW_ZIP, ITEM_COLS, RANDOM_STATE
from src.data.scoring import score_frame

ANSWER_COLS = [f"Q{i}A" for i in range(1, 43)]


def load_raw() -> pd.DataFrame:
    with zipfile.ZipFile(DATA_RAW_ZIP) as z:
        name = next(n for n in z.namelist() if n.endswith("data.csv"))
        with z.open(name) as f:
            return pd.read_csv(io.TextIOWrapper(f, encoding="utf-8"), sep="\t")


def clean(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Terapkan 4 aturan pembersihan; kembalikan data bersih + laporan jumlah yang dibuang."""
    c = CLEANING
    m_age = raw["age"].between(c["age_min"], c["age_max"])
    m_straight = raw[ANSWER_COLS].std(axis=1) > 0
    m_fake = raw[["VCL6", "VCL9", "VCL12"]].sum(axis=1) <= c["max_fake_words"]
    m_fast = raw["testelapse"] >= c["min_test_seconds"]
    keep = m_age & m_straight & m_fake & m_fast

    report = {
        "baris_awal": int(len(raw)),
        "dibuang_usia_di_luar_18_80": int((~m_age).sum()),
        "dibuang_jawaban_sama_semua": int((~m_straight).sum()),
        "dibuang_kata_palsu_2_atau_lebih": int((~m_fake).sum()),
        "dibuang_durasi_kurang_84_detik": int((~m_fast).sum()),
        "baris_bersih": int(keep.sum()),
    }

    # Hanya item jawaban yang dipakai. Kolom demografis sensitif (agama, orientasi, ras, dll.) TIDAK dibawa.
    items = raw.loc[keep, ANSWER_COLS].copy() - 1          # 1-4 -> 0-3
    items.columns = ITEM_COLS
    items.insert(0, "respondent_id", raw.index[keep].astype(int))
    return items.reset_index(drop=True), report


def run() -> dict:
    DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
    raw = load_raw()
    data, report = clean(raw)
    data = score_frame(data)

    # stratifikasi pada kombinasi tingkat 3 skala supaya proporsi terjaga
    strat = (data["tingkat_depresi"].astype(str) + data["tingkat_kecemasan"].astype(str)
             + data["tingkat_stres"].astype(str))
    rare = strat.map(strat.value_counts()) < 10
    strat = strat.where(~rare, "lain")
    if (strat == "lain").sum() < 2:          # kelompok gabungan harus berisi >= 2 baris
        strat = strat.where(strat != "lain", strat.mode()[0])
    train, test = train_test_split(data, test_size=0.2, random_state=RANDOM_STATE, stratify=strat)

    train.to_csv(DATA_PROCESSED / "train.csv", index=False)
    test.to_csv(DATA_PROCESSED / "test.csv", index=False)
    report.update({"baris_train": int(len(train)), "baris_test": int(len(test))})
    for sc in ("depresi", "kecemasan", "stres"):
        report[f"sebaran_tingkat_{sc}_persen"] = (
            data[f"tingkat_{sc}"].value_counts(normalize=True).sort_index().mul(100).round(1).tolist())
    (DATA_PROCESSED / "laporan_pembersihan.json").write_text(json.dumps(report, indent=2, ensure_ascii=False))
    return report


if __name__ == "__main__":
    print(json.dumps(run(), indent=2, ensure_ascii=False))
