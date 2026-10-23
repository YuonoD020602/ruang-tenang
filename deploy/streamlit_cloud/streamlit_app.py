"""Titik masuk untuk Streamlit Community Cloud.

Streamlit Cloud hanya menjalankan satu aplikasi, jadi file ini:
  1. menyalin kunci LLM dari st.secrets ke environment (jika ada),
  2. menyalakan backend FastAPI di proses latar (port 8000), sekali saja,
  3. menunggu backend sehat, lalu menjalankan frontend Streamlit seperti biasa.

Di Streamlit Cloud, isi "Main file path" dengan:  deploy/streamlit_cloud/streamlit_app.py
"""
from __future__ import annotations

import os
import runpy
import subprocess
import sys
import time
from pathlib import Path

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
os.chdir(ROOT)
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

PORT = int(os.getenv("BACKEND_PORT", "8000"))
os.environ.setdefault("BACKEND_URL", f"http://127.0.0.1:{PORT}")

# kunci LLM opsional dari Secrets Streamlit Cloud
try:
    for key in ("GROQ_API_KEY", "LLM_API_KEY", "LLM_MODEL", "LLM_BASE_URL"):
        if key in st.secrets and not os.getenv(key):
            os.environ[key] = str(st.secrets[key])
except Exception:
    pass  # tidak ada secrets.toml -> mode tanpa LLM


def _healthy() -> bool:
    try:
        return requests.get(f"http://127.0.0.1:{PORT}/health", timeout=2).ok
    except requests.RequestException:
        return False


@st.cache_resource(show_spinner="Menyalakan backend…")
def start_backend():
    if _healthy():
        return None
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.backend.main:app", "--host", "127.0.0.1", "--port", str(PORT)],
        cwd=ROOT, env=os.environ.copy(),
    )
    for _ in range(90):
        if _healthy():
            return proc
        time.sleep(1)
    raise RuntimeError("Backend gagal menyala dalam 90 detik")


start_backend()

# Streamlit hanya memuat ulang file utama saat kode di repo berubah. Modul tampilan di src/frontend
# dibuang dari cache supaya perubahan tampilan setelah push langsung terpakai tanpa reboot.
for _name in [m for m in sys.modules if m.startswith("src.frontend")]:
    del sys.modules[_name]

runpy.run_path(str(ROOT / "src" / "frontend" / "app.py"), run_name="__main__")
