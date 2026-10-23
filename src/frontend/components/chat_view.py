"""Panel chatbot: riwayat, saran pertanyaan, sumber, dan penanda mode."""
from __future__ import annotations

import streamlit as st

from src.frontend import api_client

MODE_BADGE = {
    "llm": ("Jawaban LLM dari dokumen", "#2F6F73"),
    "tanpa_llm": ("Kutipan dokumen (tanpa LLM)", "#5E6A1F"),
    "krisis": ("Info bantuan darurat", "#8A3A31"),
    "tolak_obat": ("Topik obat tidak dibahas", "#8A5A12"),
    "tolak_ubah_aturan": ("Aturan tetap berlaku", "#8A5A12"),
    "di_luar_topik": ("Di luar topik", "#4A5A5E"),
}

SUGGESTIONS_RESULT = ["Apa arti hasil skriningku?", "Apa yang bisa kulakukan untuk mengelola stres?",
                      "Kapan sebaiknya mencari bantuan profesional?"]
SUGGESTIONS_GENERAL = ["Apa saja gejala depresi?", "Apa itu grounding?",
                       "Apa yang bisa dilakukan sendiri untuk mengatasi kecemasan?"]


def _badge(mode: str):
    text, color = MODE_BADGE.get(mode, (mode, "#4A5A5E"))
    st.markdown(f"<span style='font-size:0.75rem;color:{color};border:1px solid {color};border-radius:999px;"
                f"padding:1px 8px'>{text}</span>", unsafe_allow_html=True)


def _sources(sources: list[dict]):
    if not sources:
        return
    with st.expander(f"Sumber ({len(sources)})"):
        for s in sources:
            hal = ""
            if s.get("halaman"):
                p = s["halaman"]
                hal = f", hal. {p[0]}" if len(p) == 1 else f", hal. {p[0]}–{p[-1]}"
            link = f" · [buka]({s['url']})" if s.get("url") else ""
            st.markdown(f"**[{s['no']}] {s['judul']}** — {s['bagian']}{hal}{link}")
            st.caption(s["kutipan"])


def _send(message: str, answers: dict | None):
    hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]]
    st.session_state.messages.append({"role": "user", "content": message})
    try:
        resp = api_client.chat(message, hist, answers)
    except api_client.BackendError as e:
        resp = {"jawaban": f"Maaf, backend tidak bisa dihubungi. ({e})", "mode": "error", "sumber": []}
    st.session_state.messages.append({"role": "assistant", "content": resp["jawaban"],
                                      "mode": resp.get("mode"), "sumber": resp.get("sumber", []),
                                      "catatan": resp.get("catatan")})


def render_chat(answers: dict | None):
    st.session_state.setdefault("messages", [])

    if not st.session_state.messages:
        st.caption("Coba salah satu pertanyaan ini:")
        sugg = SUGGESTIONS_RESULT if answers else SUGGESTIONS_GENERAL
        for q in sugg:
            if st.button(q, width="stretch", key=f"sugg_{q}"):
                _send(q, answers)
                st.rerun()

    box = st.container(height=560, border=False) if st.session_state.messages else st.container()
    for m in st.session_state.messages:
        with box.chat_message(m["role"], avatar="🙂" if m["role"] == "user" else "🌿"):
            if m["role"] == "assistant" and m.get("mode"):
                _badge(m["mode"])
            st.markdown(m["content"])
            if m.get("catatan"):
                st.caption(m["catatan"])
            if m["role"] == "assistant":
                _sources(m.get("sumber", []))

    prompt = st.chat_input("Tanya tentang depresi, kecemasan, stres, atau hasil skriningmu…")
    if prompt:
        _send(prompt, answers)
        st.rerun()

    if st.session_state.messages and st.button("Hapus percakapan", type="tertiary"):
        st.session_state.messages = []
        st.rerun()
