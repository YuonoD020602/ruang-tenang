"""Tab 'Tentang data & model': ringkasan pembersihan data dan evaluasi model dari backend."""
from __future__ import annotations

import pandas as pd
import streamlit as st

SCALES = ["depresi", "kecemasan"]


def _n(x) -> str:
    return f"{x:,}".replace(",", ".")


def render_about(info: dict):
    d = info["data"]
    st.markdown("#### Data")
    c = st.columns(4)
    c[0].metric("Pengisian awal", _n(d["baris_awal"]))
    c[1].metric("Setelah dibersihkan", _n(d["baris_bersih"]))
    c[2].metric("Data latih", _n(d["baris_train"]))
    c[3].metric("Data uji", _n(d["baris_test"]))
    st.markdown(
        f"- Usia di luar 18–60 tahun: **{_n(d['dibuang_usia_di_luar_18_60'])}** dibuang\n"
        f"- Jawaban sama untuk 16 item (selain semua \"tidak pernah\"): **{_n(d['dibuang_jawaban_seragam_bukan_nol'])}**\n"
        f"- Total waktu menjawab < 16 detik: **{_n(d['dibuang_total_waktu_kurang_16_detik'])}**")
    st.caption(f"Sumber: dataset terbuka Zenodo (Su, 2023; CC BY 4.0), mahasiswa di Tiongkok, Februari–Maret 2021. "
               f"{d['tanpa_keluhan_semua_nol_persen']}% menjawab \"tidak pernah\" untuk semua item. Korelasi skor "
               f"PHQ-9 dan GAD-7: r = {d['korelasi_phq9_gad7']}. Data tidak mewakili masyarakat Indonesia.")

    st.markdown("#### Model klasifikasi tingkat keluhan")
    ev = pd.DataFrame(info["evaluasi_klasifikasi"])[["algoritma", "akurasi_rata2", "f1_makro_rata2"]]
    ev.columns = ["Algoritma", "Akurasi rata-rata", "F1 makro rata-rata"]
    st.dataframe(ev.style.format({"Akurasi rata-rata": "{:.3f}", "F1 makro rata-rata": "{:.3f}"}),
                 hide_index=True, width="stretch")
    st.caption("Regresi logistik hampir sempurna karena tingkat resmi memang dihitung dari jumlah jawaban "
               "(hubungan linear). Model tidak menggantikan skoring resmi; ia hanya pembanding.")

    st.markdown("**Eksperimen: cukupkah 2–4 pertanyaan untuk menandai skor ≥ 10?**")
    rows = []
    for s in SCALES:
        for r in info["pengurangan_item"][s]["hasil"]:
            rows.append({"Skala": "PHQ-9" if s == "depresi" else "GAD-7", "Metode": r["metode"],
                         "Sensitivitas": r["sensitivitas"], "Spesifisitas": r["spesifisitas"], "AUC": r["auc"]})
    st.dataframe(pd.DataFrame(rows).style.format({"Sensitivitas": "{:.2f}", "Spesifisitas": "{:.2f}", "AUC": "{:.3f}"}),
                 hide_index=True, width="stretch")
    phq2 = info["pengurangan_item"]["depresi"]["hasil"][0]
    st.caption(f"Sensitivitas = proporsi pengisian dengan skor ≥ 10 yang berhasil ditandai. Di data ini PHQ-2 "
               f"hanya menandai {phq2['sensitivitas'] * 100:.0f}% kasus, jadi aplikasi tetap memakai kuesioner "
               f"lengkap. Item terpilih data tampak lebih baik, tetapi dipilih dari populasi yang sama sehingga "
               f"belum tentu berlaku di tempat lain.")

    st.markdown("#### Model clustering pola keluhan")
    cl = pd.DataFrame(info["evaluasi_clustering"])
    piv = cl.pivot(index="k", columns="set_fitur", values=["silhouette", "eta2_skor_total"])
    piv.columns = [f"{'Silhouette' if a == 'silhouette' else 'η² skor total'} · "
                   f"{'item mentah' if b == 'item_mentah' else 'bentuk item'}" for a, b in piv.columns]
    st.dataframe(piv.style.format("{:.3f}"), width="stretch")
    st.caption("η² menunjukkan seberapa besar klaster hanya mencerminkan berat-ringan keluhan. Klaster dari item "
               "mentah (η² ≈ 0,8) sebagian besar mengulang skoring resmi, sedangkan klaster dari bentuk item "
               "(η² < 0,1) menggambarkan keluhan apa yang menonjol. Silhouette yang rendah menandakan pola keluhan "
               "bersifat kontinu, jadi profil adalah deskripsi, bukan kategori yang tegas.")
    prof = pd.DataFrame([{"Profil": p["nama"], "Porsi": f"{p['ukuran_persen']}%",
                          "Rata-rata skor PHQ-9 / GAD-7": f"{p['rata2_skor_anggota']['depresi']} / "
                                                         f"{p['rata2_skor_anggota']['kecemasan']}"}
                         for p in info["profil"]])
    st.dataframe(prof, hide_index=True, width="stretch")
