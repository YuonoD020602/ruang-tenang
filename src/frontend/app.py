"""Frontend Streamlit — Skrining Mandiri Depresi & Kecemasan (PHQ-9 · GAD-7).

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

st.set_page_config(page_title="Ruang Tenang · Skrining PHQ-9 & GAD-7", page_icon="🌿", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 1.6rem; max-width: 1180px;}
  .help-banner {background:#EEF3F2;border-left:4px solid #2F6F73;border-radius:10px;padding:10px 14px;
                font-size:0.92rem;margin-bottom:6px}
  .note {background:#FFF8EC;border-left:4px solid #C08A3E;border-radius:10px;padding:10px 14px;font-size:0.92rem}
  div[role="radiogroup"] {gap: 0.3rem 0.9rem; flex-wrap: wrap;}
  div[role="radiogroup"] label p {font-size: 0.9rem;}
</style>
""", unsafe_allow_html=True)

HELP = ("<b>Butuh teman bicara?</b> Healing119.id — telepon <b>119 ekstensi 8</b> (gratis, 24 jam). "
        "Dalam bahaya sekarang: <b>119</b> atau IGD rumah sakit terdekat.")

try:
    health = api_client.health()
    if "kuesioner_data" not in st.session_state:
        st.session_state.kuesioner_data = api_client.questionnaire()
except api_client.BackendError as e:
    st.error(f"Backend belum bisa dihubungi. Pastikan backend berjalan.\n\n{e}")
    st.stop()

with st.sidebar:
    st.markdown("### 🌿 Ruang Tenang")
    st.markdown("Skrining mandiri gejala **depresi (PHQ-9)** dan **kecemasan (GAD-7)**, dilengkapi chatbot "
                "berbasis dokumen WHO.")
    st.markdown(f"<div class='help-banner'>{HELP}</div>", unsafe_allow_html=True)
    st.markdown("**Status**")
    st.caption(f"Model: {'siap' if health['model_siap'] else 'belum siap'} · "
               f"Chatbot: {'LLM aktif' if health['llm_aktif'] else 'mode tanpa LLM'} · "
               f"{health['jumlah_chunk_rag']} potongan dokumen")
    st.markdown("**Sumber chatbot**")
    st.caption("WHO: *Hal yang Perlu Dilakukan Saat Stres* (2020, CC BY-NC-SA 3.0 IGO) · WHO Fact Sheet "
               "Depresi & Kecemasan (2026) · Kartu pengetahuan PHQ-9 & GAD-7.")
    st.caption("Aplikasi ini tidak berafiliasi dengan dan tidak didukung oleh WHO atau Kementerian Kesehatan.")

st.markdown("## Skrining Mandiri Depresi & Kecemasan")
st.markdown(
    "<div class='note'>Jawab 16 pertanyaan tentang <b>2 minggu terakhir</b>. Hasilnya adalah <b>skrining, bukan "
    "diagnosis</b>. Jawabanmu <b>tidak disimpan</b>; hanya dipakai untuk menghitung hasil saat ini.</div>",
    unsafe_allow_html=True)
st.write("")

tab_main, tab_about = st.tabs(["Kuesioner, hasil & chatbot", "Tentang data & model"])

with tab_main:
    left, right = st.columns([1.7, 1], gap="large")
    with left:
        if st.session_state.get("hasil") is None:
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
            if st.button("↺ Isi ulang kuesioner", width="stretch"):
                for k in ("hasil", "answers", "messages"):
                    st.session_state.pop(k, None)
                for k in list(st.session_state.keys()):
                    if str(k).startswith("q_"):
                        del st.session_state[k]
                st.rerun()
    with right:
        st.markdown("#### Tanya chatbot")
        st.caption("Jawaban diambil dari dokumen sumber dan selalu menyebut sumbernya. Chatbot tidak "
                   "mendiagnosis dan tidak membahas obat.")
        render_chat(st.session_state.get("answers"))

with tab_about:
    try:
        info = st.session_state.get("info") or api_client.info()
        st.session_state["info"] = info
        render_about(info)
    except api_client.BackendError:
        st.info("Info model belum tersedia.")

st.divider()
st.caption("Proyek belajar Bootcamp AI Engineer · PHQ-9 & GAD-7: Spitzer, Williams, Kroenke dkk. (bebas dipakai) · "
           "Data latih: Su (2023), Zenodo, CC BY 4.0 · Bukan alat diagnosis dan bukan pengganti tenaga profesional.")
