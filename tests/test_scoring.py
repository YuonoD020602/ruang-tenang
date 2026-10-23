import pytest

from src.config import ITEM_COLS, SCALES
from src.data.scoring import level_index, score_answers

ZERO = {c: 0 for c in ITEM_COLS}


def test_item_codes():
    assert len(SCALES["depresi"]) == 9 and len(SCALES["kecemasan"]) == 7
    assert len(set(ITEM_COLS)) == 16


@pytest.mark.parametrize("scale,score,expected", [
    ("depresi", 4, 0), ("depresi", 5, 1), ("depresi", 9, 1), ("depresi", 10, 2), ("depresi", 14, 2),
    ("depresi", 15, 3), ("depresi", 19, 3), ("depresi", 20, 4), ("depresi", 27, 4),
    ("kecemasan", 4, 0), ("kecemasan", 5, 1), ("kecemasan", 10, 2), ("kecemasan", 14, 2), ("kecemasan", 15, 3),
    ("kecemasan", 21, 3),
])
def test_cutoffs(scale, score, expected):
    assert level_index(scale, score) == expected


def test_zero_and_max():
    r0 = score_answers(ZERO)
    assert r0["depresi"]["tingkat"] == "Minimal" and r0["kecemasan"]["tingkat"] == "Minimal"
    r3 = score_answers({c: 3 for c in ITEM_COLS})
    assert r3["depresi"]["skor"] == 27 and r3["depresi"]["tingkat"] == "Berat"
    assert r3["kecemasan"]["skor"] == 21 and r3["kecemasan"]["tingkat"] == "Berat"


def test_item9_flag_independent_of_total():
    r = score_answers({**ZERO, "P9": 1})
    assert r["item9_positif"] is True and r["depresi"]["tingkat"] == "Minimal"
    assert score_answers(ZERO)["item9_positif"] is False


def test_referral_flag():
    r = score_answers({**ZERO, "G1": 3, "G2": 3, "G3": 3, "G4": 1})
    assert r["kecemasan"]["skor"] == 10 and r["kecemasan"]["perlu_pemeriksaan_lanjut"]
    assert not r["depresi"]["perlu_pemeriksaan_lanjut"]


def test_validation():
    with pytest.raises(ValueError):
        score_answers({"P1": 1})
    with pytest.raises(ValueError):
        score_answers({**ZERO, "P1": 4})
    assert score_answers([1] * 16)["depresi"]["skor"] == 9
