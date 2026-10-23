import pytest

from src.config import ITEM_COLS, SCALES
from src.data.scoring import level_index, score_answers


def answers_with(scale: str, per_item: int, others: int = 0) -> dict:
    ans = {c: others for c in ITEM_COLS}
    for i in SCALES[scale]:
        ans[f"Q{i}"] = per_item
    return ans


def test_item_mapping_complete_and_disjoint():
    allitems = [i for v in SCALES.values() for i in v]
    assert sorted(allitems) == list(range(1, 43))
    assert all(len(v) == 14 for v in SCALES.values())


@pytest.mark.parametrize("scale,score,expected", [
    ("depresi", 9, 0), ("depresi", 10, 1), ("depresi", 13, 1), ("depresi", 14, 2), ("depresi", 27, 3), ("depresi", 28, 4),
    ("kecemasan", 7, 0), ("kecemasan", 8, 1), ("kecemasan", 10, 2), ("kecemasan", 19, 3), ("kecemasan", 20, 4),
    ("stres", 14, 0), ("stres", 15, 1), ("stres", 19, 2), ("stres", 33, 3), ("stres", 34, 4),
])
def test_cutoffs(scale, score, expected):
    assert level_index(scale, score) == expected


def test_all_zero_is_normal():
    r = score_answers({c: 0 for c in ITEM_COLS})
    assert all(r[s]["skor"] == 0 and r[s]["tingkat"] == "Normal" for s in SCALES)


def test_max_is_extremely_severe():
    r = score_answers({c: 3 for c in ITEM_COLS})
    assert all(r[s]["skor"] == 42 and r[s]["tingkat"] == "Sangat berat" for s in SCALES)


def test_only_one_scale_counts():
    r = score_answers(answers_with("stres", 2))
    assert r["stres"]["skor"] == 28 and r["depresi"]["skor"] == 0 and r["kecemasan"]["skor"] == 0


def test_list_input_and_validation():
    assert score_answers([1] * 42)["depresi"]["skor"] == 14
    with pytest.raises(ValueError):
        score_answers([1] * 41)
    with pytest.raises(ValueError):
        score_answers([4] * 42)
