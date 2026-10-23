"""Formulir PHQ-9 & GAD-7. Mengembalikan dict jawaban saat dikirim lengkap, selain itu None."""
from __future__ import annotations

import streamlit as st

SCALE_TITLE = {"depresi": "Bagian 1 · PHQ-9", "kecemasan": "Bagian 2 · GAD-7"}


def render_form(q: dict) -> dict | None:
    labels = [p["label"] for p in q["pilihan"]]
    values = [p["nilai"] for p in q["pilihan"]]

    st.markdown(f"**{q['petunjuk']}**")
    with st.form("kuesioner", border=False):
        answers: dict[str, int | None] = {}
        no = 0
        for scale, block in q["skala"].items():
            st.markdown(f"<div style='margin:14px 0 4px 0;color:#2F6F73;font-weight:700'>{SCALE_TITLE[scale]}</div>",
                        unsafe_allow_html=True)
            for item in block["item"]:
                no += 1
                choice = st.radio(f"{no}. {item['teks']}", labels, index=None, horizontal=True,
                                  key=f"q_{item['kode']}")
                answers[item["kode"]] = None if choice is None else values[labels.index(choice)]
        submitted = st.form_submit_button("Lihat hasil", type="primary", width="stretch")

    st.caption(q["hak_cipta"])
    if not submitted:
        return None
    missing = [k for k, v in answers.items() if v is None]
    if missing:
        st.warning(f"Masih ada {len(missing)} pertanyaan yang belum dijawab. Semua pertanyaan perlu dijawab.")
        return None
    return {k: int(v) for k, v in answers.items()}
