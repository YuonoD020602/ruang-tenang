"""Frontend Streamlit — Demo Skrining DASS-42.

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
from src.frontend.components.result_view import render_result  # noqa: E402

st.set_page_config(page_title="Demo Skrining DASS-42", page_icon="🌿", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 1.6rem; max-width: 1180px;}
  .help-banner {background:#EEF3F2;border-left:4px solid #2F6F73;border-radius:10px;padding:10px 14px;
                font-size:0.92rem;margin-bottom:6px}
  .demo-note {background:#FFF8EC;border-left:4px solid #C08A3E;border-radius:10px;padding:10px 14px;
              font-size:0.92rem}
</style>
""", unsafe_allow_html=True)

HELP = ("<b>Butuh teman bicara?</b> Healing119.id — telepon <b>119 ekstensi 8</b> (gratis, 24 jam). "
        "Dalam bahaya sekarang: <b>119</b> atau IGD rumah sakit terdekat.")

# ---------- status backend ----------
try:
    health = api_client.health()
except api_client.BackendError as e:
    st.error(f"Backend belum bisa dihubungi. Pastikan backend berjalan.\n\n{e}")
    st.stop()

# ---------- sidebar ----------
with st.sidebar:
    st.markdown("### 🌿 Demo Skrining DASS-42")
    st.markdown("Aplikasi belajar yang menampilkan **responden contoh** dari dataset publik, lalu "
                "menjelaskan hasilnya dengan chatbot berbasis dokumen WHO.")
    st.markdown(f"<div class='help-banner'>{HELP}</div>", unsafe_allow_html=True)
    st.markdown("**Status**")
    st.caption(f"Model: {'siap' if health['model_siap'] else 'belum siap'} · "
               f"Chatbot: {'LLM aktif' if health['llm_aktif'] else 'mode tanpa LLM'} · "
               f"{health['jumlah_chunk_rag']} potongan dokumen · {health['jumlah_responden_demo']} responden demo")
    st.markdown("**Sumber chatbot**")
    st.caption("WHO: *Hal yang Perlu Dilakukan Saat Stres* (2020, CC BY-NC-SA 3.0 IGO) · WHO Fact Sheet "
               "Depresi & Kecemasan (2026) · Kartu pengetahuan DASS-42.")
    st.caption("Aplikasi ini tidak berafiliasi dengan dan tidak didukung oleh WHO.")

# ---------- header ----------
st.markdown("## Demo Skrining DASS-42")
st.markdown(
    "<div class='demo-note'><b>Ini mode demo.</b> Kamu tidak mengisi kuesioner. Aturan penggunaan DASS tidak "
    "mengizinkan kuesioner ini diberikan lewat aplikasi yang terbuka untuk umum, jadi yang ditampilkan adalah "
    "jawaban <b>responden anonim</b> dari dataset publik. Hasil skrining bukan diagnosis.</div>",
    unsafe_allow_html=True)
st.write("")

tab_demo, tab_about = st.tabs(["Hasil & chatbot", "Tentang data & model"])

with tab_demo:
    info_cache = st.session_state.get("info")
    if info_cache is None:
        try:
            info_cache = st.session_state["info"] = api_client.info()
        except api_client.BackendError:
            info_cache = None
    profiles = {p["cluster_id"]: p["nama"] for p in info_cache["profil"]} if info_cache else {}

    c1, c2, c3 = st.columns([1.6, 1, 1])
    choice = c1.selectbox("Pilih profil pola respons", ["Semua profil"] + [profiles[k] for k in sorted(profiles)])
    pid = None if choice == "Semua profil" else next(k for k, v in profiles.items() if v == choice)
    c2.write("")
    c2.write("")
    if c2.button("🎲 Ambil responden acak", width="stretch") or "respondent" not in st.session_state:
        st.session_state.respondent = api_client.random_respondent(pid)
        st.session_state.messages = []
    ids = [r["respondent_id"] for r in api_client.list_respondents(pid)["responden"]]
    current = st.session_state.respondent["respondent_id"]
    picked = c3.selectbox("Atau pilih nomor responden", ids, index=ids.index(current) if current in ids else None,
                          placeholder="Nomor responden…")
    if picked and picked != current:
        st.session_state.respondent = api_client.get_respondent(int(picked))
        st.session_state.messages = []
        st.rerun()

    left, right = st.columns([1.35, 1], gap="large")
    with left:
        render_result(st.session_state.respondent)
    with right:
        st.markdown("#### Tanya chatbot")
        st.caption("Jawaban diambil dari dokumen sumber dan selalu menyebut sumbernya. Chatbot tidak "
                   "mendiagnosis dan tidak membahas obat.")
        render_chat(st.session_state.respondent["respondent_id"])

with tab_about:
    if info_cache:
        render_about(info_cache)
    else:
        st.info("Info model belum tersedia.")

st.divider()
st.caption("Proyek belajar Bootcamp AI Engineer · DASS-42: Lovibond & Lovibond (1995), domain publik · "
           "Data: Open Psychometrics (2019) · Bukan alat diagnosis dan bukan pengganti tenaga profesional.")
