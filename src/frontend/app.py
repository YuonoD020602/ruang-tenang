"""Frontend Streamlit — Ruang Tenang: skrining mandiri depresi (PHQ-9) & kecemasan (GAD-7) + chatbot.

Jalankan:  streamlit run src/frontend/app.py
(Backend harus sudah berjalan; alamatnya diatur lewat env BACKEND_URL.)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st  # noqa: E402

from src.frontend import api_client  # noqa: E402
from src.frontend.components.about_view import render_about  # noqa: E402
from src.frontend.components.chat_view import render_chat  # noqa: E402
from src.frontend.components.form_view import render_form  # noqa: E402
from src.frontend.components.result_view import render_result  # noqa: E402
from src.frontend.styles import BRAND_SVG, CSS  # noqa: E402

st.set_page_config(page_title="Ruang Tenang — skrining depresi & kecemasan", page_icon="🌿", layout="wide",
                   initial_sidebar_state="collapsed")
st.markdown(CSS, unsafe_allow_html=True)

try:
    health = api_client.health()
    if "kuesioner_data" not in st.session_state:
        st.session_state.kuesioner_data = api_client.questionnaire()
except api_client.BackendError as e:
    st.error(f"Backend belum bisa dihubungi. Muat ulang halaman sebentar lagi.\n\n{e}")
    st.stop()

with st.sidebar:
    st.markdown("### Tentang aplikasi")
    st.caption(f"Model {'siap' if health['model_siap'] else 'belum siap'}. "
               f"Chatbot {'memakai LLM' if health['llm_aktif'] else 'dalam mode kutipan dokumen'}, "
               f"dengan {health['jumlah_chunk_rag']} potongan dokumen.")
    st.markdown("**Sumber chatbot**")
    st.caption("WHO, *Hal yang Perlu Dilakukan Saat Stres* (2020, CC BY-NC-SA 3.0 IGO); WHO Fact Sheet Depresi "
               "dan Kecemasan (2026); kartu pengetahuan PHQ-9 dan GAD-7.")
    st.caption("Aplikasi ini tidak berafiliasi dengan dan tidak didukung oleh WHO atau Kementerian Kesehatan.")

has_result = st.session_state.get("hasil") is not None
headline = "Ini gambaran perasaanmu dua minggu terakhir." if has_result else \
           "Bagaimana kabarmu dua minggu terakhir?"
st.markdown(
    f"<div class='rt-hero'><div class='rt-brand'>{BRAND_SVG}Ruang Tenang</div>"
    f"<h1>{headline}</h1>"
    "<p class='lead'>Jawab 16 pertanyaan singkat tentang suasana hati dan rasa cemas. Hasilnya skrining, bukan "
    "diagnosis, dan jawabanmu tidak disimpan. Ada yang ingin ditanyakan? Teman Tanya siap membantu kapan saja.</p>"
    "<div class='rt-help'><span>Butuh teman bicara sekarang?</span>"
    "<span><b>Healing119.id</b>: telepon <b>119</b>, ekstensi <b>8</b> (gratis, 24 jam)</span>"
    "<span>Dalam bahaya: <b>119</b> atau IGD terdekat</span></div></div>",
    unsafe_allow_html=True)
st.markdown("<a class='rt-fab' href='#teman-tanya'><span class='dot'></span>Tanya chatbot</a>",
            unsafe_allow_html=True)

tab_main, tab_about = st.tabs(["Kuesioner dan chatbot", "Tentang data dan model"])

with tab_main:
    left, right = st.columns([1.55, 1], gap="large")
    with left:
        if not has_result:
            answers = render_form(st.session_state.kuesioner_data)
            if answers is not None:
                try:
                    st.session_state.hasil = api_client.predict(answers)
                    st.session_state.answers = answers
                    st.session_state.messages = []
                    st.rerun()
                except api_client.BackendError as e:
                    st.error(str(e))
        else:
            render_result(st.session_state.hasil)
            st.write("")
            if st.button("Isi ulang kuesioner", width="stretch"):
                for k in ("hasil", "answers", "messages"):
                    st.session_state.pop(k, None)
                for k in list(st.session_state.keys()):
                    if str(k).startswith("q_"):
                        del st.session_state[k]
                st.rerun()
    with right:
        render_chat(st.session_state.get("answers"))

with tab_about:
    try:
        info = st.session_state.get("info") or api_client.info()
        st.session_state["info"] = info
        render_about(info)
    except api_client.BackendError:
        st.info("Info model belum tersedia. Muat ulang halaman.")

st.write("")
st.markdown(
    "<p class='rt-foot'>Proyek belajar Bootcamp AI Engineer. PHQ-9 dan GAD-7 dikembangkan oleh Spitzer, Williams, "
    "Kroenke, dan rekan, dan bebas dipakai. Model dilatih dari data terbuka Su (2023, Zenodo, CC BY 4.0). Aplikasi "
    "ini bukan alat diagnosis dan bukan pengganti tenaga profesional.</p>", unsafe_allow_html=True)
