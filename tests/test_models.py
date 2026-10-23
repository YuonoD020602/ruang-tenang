"""Uji model terlatih (butuh models/*.joblib hasil pipeline)."""
import pandas as pd
import pytest

from src.config import DATA_PROCESSED, ITEM_COLS, SCALES
from src.ml.predict import analyze, model_info, models_ready

pytestmark = pytest.mark.skipif(not models_ready(), reason="Model belum dilatih (jalankan pipeline)")


def demo_rows(n=30):
    df = pd.read_csv(DATA_PROCESSED / "demo_respondents.csv").head(n)
    return [{c: int(r[c]) for c in ITEM_COLS} for _, r in df.iterrows()]


def test_analyze_structure():
    r = analyze(demo_rows(1)[0])
    assert set(r) >= {"skoring_resmi", "klasifikasi", "profil", "pengingat"}
    assert set(r["skoring_resmi"]) == set(SCALES)
    assert isinstance(r["profil"]["nama"], str) and r["profil"]["nama"]


def test_classifier_agrees_with_official_on_demo():
    agree = [analyze(a)["klasifikasi"]["semua_sama_dengan_resmi"] for a in demo_rows(50)]
    assert sum(agree) / len(agree) >= 0.95


def test_all_normal_gets_note():
    r = analyze({c: 0 for c in ITEM_COLS})
    assert r["profil"]["catatan"]


def test_model_info_registered():
    info = model_info()
    assert info["klasifikasi"]["registered_model"]
    assert info["clustering"]["k"] >= 3
