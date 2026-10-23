"""Skoring resmi DASS-42 (aturan baku, tanpa ML)."""
from __future__ import annotations

from typing import Iterable, Mapping

import pandas as pd

from src.config import CUTOFFS, ITEM_COLS, LEVELS, SCALES


def level_index(scale: str, score: int) -> int:
    """Indeks tingkat 0..4 (Normal..Sangat berat) untuk skor suatu skala."""
    for i, upper in enumerate(CUTOFFS[scale]):
        if score <= upper:
            return i
    return len(LEVELS) - 1


def score_answers(answers: Mapping[str, int] | Iterable[int]) -> dict:
    """Hitung skor & tingkat dari 42 jawaban (nilai 0-3).

    `answers` boleh dict {"Q1": 0, ...} atau list 42 angka berurutan Q1..Q42.
    """
    if isinstance(answers, Mapping):
        vals = {c: int(answers[c]) for c in ITEM_COLS}
    else:
        lst = [int(v) for v in answers]
        if len(lst) != 42:
            raise ValueError("Harus ada tepat 42 jawaban")
        vals = dict(zip(ITEM_COLS, lst))
    bad = [c for c, v in vals.items() if v not in (0, 1, 2, 3)]
    if bad:
        raise ValueError(f"Jawaban harus 0-3; tidak valid di {bad[:5]}")

    result = {}
    for scale, items in SCALES.items():
        s = sum(vals[f"Q{i}"] for i in items)
        li = level_index(scale, s)
        result[scale] = {"skor": s, "tingkat_idx": li, "tingkat": LEVELS[li]}
    return result


def score_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Tambahkan kolom skor_<skala> dan tingkat_<skala> (indeks 0-4) ke DataFrame item 0-3."""
    out = df.copy()
    new = {}
    for scale, items in SCALES.items():
        s = out[[f"Q{i}" for i in items]].sum(axis=1)
        new[f"skor_{scale}"] = s
        new[f"tingkat_{scale}"] = s.apply(lambda x, sc=scale: level_index(sc, int(x)))
    return pd.concat([out, pd.DataFrame(new, index=out.index)], axis=1)
