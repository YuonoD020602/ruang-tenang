"""Tampilan hasil skrining: info bantuan (bila perlu), skor 2 skala, profil, dan perbandingan model."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

SCALES = ["depresi", "kecemasan"]
LABEL = {"depresi": "Depresi (PHQ-9)", "kecemasan": "Kecemasan (GAD-7)"}
CUTOFFS = {"depresi": [4, 9, 14, 19], "kecemasan": [4, 9, 14]}
MAX = {"depresi": 27, "kecemasan": 21}
# dari tenang ke hangat; tidak memakai merah menyala supaya tidak menakutkan
PALETTE = {
    "depresi": ["#DCEBE4", "#EEF0D5", "#F6E5C8", "#F2D3BF", "#E9C0B8"],
    "kecemasan": ["#DCEBE4", "#EEF0D5", "#F6E5C8", "#E9C0B8"],
}
TEXT = {
    "depresi": ["#2E6B55", "#5E6A1F", "#8A5A12", "#8F4A26", "#8A3A31"],
    "kecemasan": ["#2E6B55", "#5E6A1F", "#8A5A12", "#8A3A31"],
}

CRISIS_HTML = (
    "<div style='background:#FBEDEA;border-left:5px solid #8A3A31;border-radius:12px;padding:14px 18px;"
    "margin-bottom:14px'>"
    "<div style='font-weight:700;color:#8A3A31;font-size:1.05rem'>Terima kasih sudah jujur menjawab.</div>"
    "<div style='margin-top:6px'>Kamu menjawab pertanyaan nomor 9 (pikiran bahwa lebih baik mati atau ingin melukai "
    "diri) selain \"tidak pernah\". Ini penting untuk ditanggapi, berapa pun skor totalmu. Kamu tidak harus "
    "menghadapinya sendirian.</div>"
    "<ul style='margin:8px 0 0 0'>"
    "<li><b>Healing119.id</b> (Kementerian Kesehatan RI): telepon <b>119</b>, pilih <b>ekstensi 8</b>, atau chat "
    "lewat www.healing119.id. Gratis, 24 jam.</li>"
    "<li><b>Dalam bahaya sekarang?</b> Telepon <b>119</b> atau datang ke <b>IGD rumah sakit terdekat</b>.</li>"
    "<li>Hubungi orang yang kamu percaya dan katakan bahwa kamu sedang tidak baik-baik saja.</li>"
    "</ul></div>"
)


def severity_chart(off: dict) -> go.Figure:
    fig = go.Figure()
    for idx, s in enumerate(SCALES):
        bounds = [0] + [c + 0.5 for c in CUTOFFS[s]] + [MAX[s]]
        for i in range(len(bounds) - 1):
            fig.add_shape(type="rect", x0=bounds[i] / MAX[s], x1=bounds[i + 1] / MAX[s], y0=idx - 0.38,
                          y1=idx + 0.38, fillcolor=PALETTE[s][i], line_width=0, layer="below")
    fig.add_trace(go.Bar(
        y=[LABEL[s] for s in SCALES], x=[off[s]["skor"] / MAX[s] for s in SCALES], orientation="h", width=0.28,
        marker_color="#1E5B5A", cliponaxis=False,
        text=[f"{off[s]['skor']}/{MAX[s]}, {off[s]['tingkat']}" for s in SCALES], textposition="outside",
        hovertemplate="%{y}<extra></extra>",
    ))
    fig.update_layout(
        height=170, margin=dict(l=10, r=120, t=6, b=24), showlegend=False,
        xaxis=dict(range=[0, 1], showticklabels=False, showgrid=False, title="Proporsi dari skor maksimum"),
        yaxis=dict(autorange="reversed"), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13))
    return fig


def render_result(res: dict):
    off = res["skoring_resmi"]
    if off.get("item9_positif"):
        st.markdown(CRISIS_HTML, unsafe_allow_html=True)

    cols = st.columns(2)
    for col, s in zip(cols, SCALES):
        li = off[s]["tingkat_idx"]
        col.markdown(
            f"<div style='background:{PALETTE[s][li]};border-radius:18px;padding:16px 18px'>"
            f"<div style='font-size:0.88rem;color:#4A5A5E'>{LABEL[s]}</div>"
            f"<div style='font-size:1.9rem;font-weight:700;color:#1F2A2E;line-height:1.2'>{off[s]['skor']}"
            f"<span style='font-size:0.9rem;font-weight:400;color:#4A5A5E'> / {MAX[s]}</span></div>"
            f"<div style='font-weight:600;color:{TEXT[s][li]}'>{off[s]['tingkat']}</div></div>",
            unsafe_allow_html=True)
    st.plotly_chart(severity_chart(off), width="stretch", config={"displayModeBar": False})

    if any(off[s]["perlu_pemeriksaan_lanjut"] for s in SCALES):
        st.info("Skor 10 ke atas umumnya menjadi tanda untuk pemeriksaan lanjutan. Pertimbangkan berbicara dengan "
                "psikolog, dokter di puskesmas, atau layanan Healing119.id (119 ekstensi 8).")

    prof = res["profil"]
    st.markdown("**Pola keluhan** (model clustering)")
    st.markdown(
        f"<div style='border:1px solid #D5E2DF;border-radius:14px;padding:14px 16px;background:#FFFFFF'>"
        f"<div style='font-size:1.1rem;font-weight:700;color:#1E5B5A'>{prof['nama']}</div>"
        f"<div style='margin-top:6px'>{prof['deskripsi']}</div>"
        + (f"<div style='margin-top:8px;color:#8A5A12'>ⓘ {prof['catatan']}</div>" if prof.get("catatan") else "")
        + "</div>", unsafe_allow_html=True)
    st.write("")

    st.markdown("**Skoring resmi vs model klasifikasi**")
    clf = res["klasifikasi"]["per_skala"]
    rows = "".join(
        f"<tr><td>{LABEL[s]}</td><td>{off[s]['tingkat']}</td><td>{clf[s]['tingkat']}</td>"
        f"<td style='text-align:center'>{'✓' if clf[s]['sama_dengan_resmi'] else '≠'}</td></tr>" for s in SCALES)
    st.markdown("<table style='width:100%;border-collapse:collapse;font-size:0.92rem'>"
                "<tr style='text-align:left;color:#4A5A5E'><th>Skala</th><th>Resmi</th><th>Model</th><th>Sama</th></tr>"
                f"{rows}</table>", unsafe_allow_html=True)
    st.caption("Hasil yang berlaku selalu skoring resmi. Ini hasil skrining, bukan diagnosis.")
