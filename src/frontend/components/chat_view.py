"""Panel chatbot "Teman Tanya": riwayat, saran pertanyaan, sumber, dan penanda mode.

Panel dibungkus container berkunci `chatpanel` sehingga bisa diberi gaya khusus dan menempel (sticky)
di samping kuesioner. Lihat src/frontend/styles.py.
"""
from __future__ import annotations

import streamlit as st

from src.frontend import api_client

MODE_BADGE = {
    "llm": ("Dirangkum dari dokumen", "#F2C46D"),
    "tanpa_llm": ("Kutipan dokumen", "#B9E3D3"),
    "krisis": ("Info bantuan", "#FFB4A8"),
    "tolak_obat": ("Topik obat tidak dibahas", "#F2C46D"),
    "tolak_ubah_aturan": ("Aturan tetap berlaku", "#F2C46D"),
    "di_luar_topik": ("Di luar topik", "#CFC8F2"),
}

SUGGESTIONS_RESULT = ["Apa arti hasil skriningku?", "Apa yang bisa kulakukan untuk mengelola stres?",
                      "Kapan sebaiknya mencari bantuan profesional?"]
SUGGESTIONS_GENERAL = ["Apa saja gejala depresi?", "Bagaimana cara menenangkan diri saat cemas?",
                       "Apa bedanya cemas biasa dan gangguan kecemasan?"]


def _badge(mode: str):
    text, color = MODE_BADGE.get(mode, (mode, "#CFC8F2"))
    st.markdown(f"<span style='font-size:0.75rem;color:{color};border:1px solid {color};border-radius:999px;"
                f"padding:1px 9px'>{text}</span>", unsafe_allow_html=True)


def _sources(sources: list[dict]):
    if not sources:
        return
    with st.expander(f"Sumber ({len(sources)})"):
        for s in sources:
            hal = ""
            if s.get("halaman"):
                p = s["halaman"]
                hal = f", hal. {p[0]}" if len(p) == 1 else f", hal. {p[0]}–{p[-1]}"
            link = f" — [buka]({s['url']})" if s.get("url") else ""
            st.markdown(f"**[{s['no']}] {s['judul']}**, {s['bagian']}{hal}{link}")
            st.caption(s["kutipan"])


def _send(message: str, answers: dict | None):
    hist = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]]
    st.session_state.messages.append({"role": "user", "content": message})
    try:
        resp = api_client.chat(message, hist, answers)
    except api_client.BackendError as e:
        resp = {"jawaban": f"Backend tidak bisa dihubungi. Coba muat ulang halaman. ({e})", "mode": "error",
                "sumber": []}
    st.session_state.messages.append({"role": "assistant", "content": resp["jawaban"], "mode": resp.get("mode"),
                                      "sumber": resp.get("sumber", []), "catatan": resp.get("catatan")})


def render_chat(answers: dict | None):
    st.session_state.setdefault("messages", [])
    with st.container(key="chatpanel"):
        st.markdown("<div id='teman-tanya'></div>", unsafe_allow_html=True)
        sub = ("Tanyakan arti hasilmu atau cara mengelola stres." if answers
               else "Tanya kapan saja, juga sambil mengisi kuesioner.")
        st.markdown(f"<div class='rt-chat-head'><div class='lamp'></div><div><h3>Teman Tanya</h3>"
                    f"<p>{sub}</p></div></div>", unsafe_allow_html=True)

        if not st.session_state.messages:
            st.markdown("<p class='rt-chat-hint'>Coba mulai dengan:</p>", unsafe_allow_html=True)
            for q in (SUGGESTIONS_RESULT if answers else SUGGESTIONS_GENERAL):
                if st.button(q, width="stretch", key=f"sugg_{q}"):
                    _send(q, answers)
                    st.rerun()
        else:
            box = st.container(height=380, border=False)
            for m in st.session_state.messages:
                avatar = "🙂" if m["role"] == "user" else "🌙"
                with box.chat_message(m["role"], avatar=avatar):
                    if m["role"] == "assistant" and m.get("mode"):
                        _badge(m["mode"])
                    st.markdown(m["content"])
                    if m.get("catatan"):
                        st.caption(m["catatan"])
                    if m["role"] == "assistant":
                        _sources(m.get("sumber", []))

        prompt = st.chat_input("Tulis pertanyaanmu…")
        if prompt:
            _send(prompt, answers)
            st.rerun()
        foot_l, foot_r = st.columns([3, 1])
        foot_l.caption("Menjawab dari dokumen WHO dan kartu PHQ-9/GAD-7. Tidak mendiagnosis, tidak membahas obat.")
        if st.session_state.messages and foot_r.button("Hapus", type="tertiary", key="clear_chat"):
            st.session_state.messages = []
            st.rerun()
