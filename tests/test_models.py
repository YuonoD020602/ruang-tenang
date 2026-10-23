"""Uji model terlatih (butuh models/*.joblib hasil pipeline)."""
import pandas as pd
import pytest

from src.config import DATA_PROCESSED, ITEM_COLS, SCALES
from src.ml.predict import analyze, model_info, models_ready

pytestmark = pytest.mark.skipif(not models_ready(), reason="Model belum dilatih (jalankan pipeline)")
ZERO = {c: 0 for c in ITEM_COLS}


def test_analyze_structure():
    r = analyze({**ZERO, "P3": 2, "P4": 3, "G1": 1})
    assert set(r) >= {"skoring_resmi", "klasifikasi", "profil", "pengingat"}
    assert set(SCALES) <= set(r["skoring_resmi"])
    assert r["profil"]["cluster_id"] is not None and r["profil"]["nama"]


def test_all_zero_has_no_profile():
    r = analyze(ZERO)
    assert r["profil"]["cluster_id"] is None


def test_classifier_agrees_with_official():
    p = DATA_PROCESSED / "test.csv"
    if not p.exists():
        pytest.skip("data uji belum dibuat")
    df = pd.read_csv(p).sample(300, random_state=0)
    agree = [analyze({c: int(r[c]) for c in ITEM_COLS})["klasifikasi"]["semua_sama_dengan_resmi"]
             for _, r in df.iterrows()]
    assert sum(agree) / len(agree) >= 0.98


def test_profiles_never_named_after_item9():
    for p in model_info()["profil"]:
        assert "melukai" not in p["nama"]


def test_model_info_registered():
    info = model_info()
    assert info["klasifikasi"]["registered_model"] and info["clustering"]["k"] >= 3
