"""Tab 'Tentang data & model': ringkasan pembersihan data dan evaluasi model dari backend."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

SCALES = ["depresi", "kecemasan", "stres"]
COLORS = {"depresi": "#2F6F73", "kecemasan": "#C08A3E", "stres": "#7A6FA8"}


def render_about(info: dict):
    d = info["data"]
    st.markdown("#### Data")
    c = st.columns(4)
    c[0].metric("Responden awal", f"{d['baris_awal']:,}".replace(",", "."))
    c[1].metric("Setelah dibersihkan", f"{d['baris_bersih']:,}".replace(",", "."))
    c[2].metric("Data latih", f"{d['baris_train']:,}".replace(",", "."))
    c[3].metric("Data uji", f"{d['baris_test']:,}".replace(",", "."))
    st.markdown(
        f"- Usia di luar 18–80 tahun: **{d['dibuang_usia_di_luar_18_80']:,}** dibuang\n"
        f"- Menjawab angka yang sama untuk 42 item: **{d['dibuang_jawaban_sama_semua']:,}**\n"
        f"- Mencentang ≥ 2 kata palsu pada tes kosakata: **{d['dibuang_kata_palsu_2_atau_lebih']:,}**\n"
        f"- Selesai < 84 detik: **{d['dibuang_durasi_kurang_84_detik']:,}**".replace(",", "."))
    st.caption("Sumber: survei DASS-42 online Open Psychometrics (2017–2019). Pengisi sukarela, lebih dari "
               "separuh dari Malaysia; data tidak mewakili masyarakat Indonesia.")

    st.markdown("#### Model klasifikasi tingkat keparahan")
    ev = pd.DataFrame(info["evaluasi_klasifikasi"])[["algoritma", "akurasi_rata2", "f1_makro_rata2"]]
    ev.columns = ["Algoritma", "Akurasi rata-rata", "F1 makro rata-rata"]
    st.dataframe(ev.style.format({"Akurasi rata-rata": "{:.3f}", "F1 makro rata-rata": "{:.3f}"}),
                 hide_index=True, width="stretch")
    st.caption("Regresi logistik mencapai 100% karena tingkat resmi memang dihitung dari jumlah jawaban item "
               "(hubungan linear). Model tidak menggantikan skoring resmi; ia hanya pembanding.")

    st.markdown("**Eksperimen: seberapa akurat jika item dikurangi?**")
    fig = go.Figure()
    for s in SCALES:
        res = info["pengurangan_item"][s]["hasil"]
        fig.add_trace(go.Scatter(x=[r["k"] for r in res], y=[r["akurasi"] for r in res], mode="lines+markers",
                                 name=s.capitalize(), line=dict(color=COLORS[s], width=2)))
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=10, b=40), xaxis_title="Jumlah item terpenting dipakai",
                      yaxis_title="Akurasi tingkat", yaxis=dict(range=[0.5, 1.02], tickformat=".0%"),
                      plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                      legend=dict(orientation="h", y=1.12))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    st.caption("Dengan 7 item per skala, tingkat tepat ditebak sekitar 3 dari 4 kali. Ini menunjukkan kenapa "
               "versi lengkap tetap dipakai untuk hasil utama.")

    st.markdown("#### Model clustering profil")
    cl = pd.DataFrame(info["evaluasi_clustering"])
    piv = cl.pivot(index="k", columns="set_fitur", values="silhouette")
    st.dataframe(piv.rename(columns={"tingkat": "Silhouette · fitur tingkat",
                                     "bentuk_profil": "Silhouette · fitur bentuk profil"}).style.format("{:.3f}"),
                 width="stretch")
    corr = info["korelasi_antar_skala"]
    st.caption(f"Ketiga skala berkorelasi tinggi (depresi–stres r = {corr['skor_depresi']['skor_stres']:.2f}, "
               f"kecemasan–stres r = {corr['skor_kecemasan']['skor_stres']:.2f}). Klaster dari skor mentah hanya "
               "memisahkan keluhan rendah/sedang/berat, jadi aplikasi memakai klaster dari BENTUK profil: skala "
               "mana yang relatif menonjol pada orang yang sama.")
    prof = pd.DataFrame([{"Profil": p["nama"], "Porsi data latih": f"{p['ukuran_persen']}%",
                          "Rata-rata skor (D/K/S)": " / ".join(str(p["rata2_skor_anggota"][s]) for s in SCALES)}
                         for p in info["profil"]])
    st.dataframe(prof, hide_index=True, width="stretch")
