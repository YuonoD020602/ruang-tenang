"""Kuesioner PHQ-9 & GAD-7 dengan kartu per pertanyaan dan indikator kemajuan.

Mengembalikan dict jawaban saat tombol "Lihat hasil" ditekan dan semua terjawab, selain itu None.
"""
from __future__ import annotations

import streamlit as st

SECTION = {
    "depresi": ("Suasana hati dan energi", "9 pertanyaan dari PHQ-9"),
    "kecemasan": ("Rasa cemas dan khawatir", "7 pertanyaan dari GAD-7"),
}


def render_form(q: dict) -> dict | None:
    labels = [p["label"] for p in q["pilihan"]]
    values = [p["nilai"] for p in q["pilihan"]]
    codes = [it["kode"] for block in q["skala"].values() for it in block["item"]]

    answered = sum(1 for c in codes if st.session_state.get(f"q_{c}") is not None)
    total = len(codes)
    st.markdown(
        f"<div class='rt-progress'><div class='bar'><div class='fill' style='width:{100 * answered / total:.0f}%'></div>"
        f"</div><div class='txt'>{answered} dari {total} pertanyaan terjawab</div></div>", unsafe_allow_html=True)
    st.markdown(f"**{q['petunjuk']}**")

    answers: dict[str, int | None] = {}
    no = 0
    for scale, block in q["skala"].items():
        title, sub = SECTION[scale]
        st.markdown(f"<div class='rt-section'>{title}<span>{sub}</span></div>", unsafe_allow_html=True)
        for item in block["item"]:
            no += 1
            with st.container(key=f"qcard_{item['kode']}"):
                choice = st.radio(f"{no}. {item['teks']}", labels, index=None, horizontal=True,
                                  key=f"q_{item['kode']}")
            answers[item["kode"]] = None if choice is None else values[labels.index(choice)]

    remaining = sum(1 for v in answers.values() if v is None)
    label = "Lihat hasil" if remaining == 0 else f"Lihat hasil (tinggal {remaining} pertanyaan)"
    clicked = st.button(label, type="primary", width="stretch", disabled=remaining > 0)
    st.caption(q["hak_cipta"])
    if clicked and remaining == 0:
        return {k: int(v) for k, v in answers.items()}
    return None
