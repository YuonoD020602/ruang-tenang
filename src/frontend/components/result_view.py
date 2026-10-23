"""Tampilan hasil satu responden: skor 3 skala, perbandingan model, profil, dan jawaban item."""
from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

SCALES = ["depresi", "kecemasan", "stres"]
LABEL = {"depresi": "Depresi", "kecemasan": "Kecemasan", "stres": "Stres"}
CUTOFFS = {"depresi": [9, 13, 20, 27], "kecemasan": [7, 9, 14, 19], "stres": [14, 18, 25, 33]}
LEVELS = ["Normal", "Ringan", "Sedang", "Berat", "Sangat berat"]
# dari tenang ke hangat; tidak memakai merah menyala supaya tidak menakutkan
BAND_COLORS = ["#DCEBE4", "#EEF0D5", "#F6E5C8", "#F2D3BF", "#E9C0B8"]
LEVEL_TEXT = ["#2E6B55", "#5E6A1F", "#8A5A12", "#8F4A26", "#8A3A31"]
ANSWER_LABEL = ["0 · Tidak sesuai sama sekali", "1 · Kadang-kadang", "2 · Cukup sering", "3 · Hampir selalu"]


def severity_chart(official: dict) -> go.Figure:
    fig = go.Figure()
    ys = [LABEL[s] for s in SCALES]
    # pita tingkat keparahan per skala
    for s in SCALES:
        bounds = [0] + [c + 0.5 for c in CUTOFFS[s]] + [42]
        for i in range(5):
            fig.add_shape(type="rect", x0=bounds[i], x1=bounds[i + 1], y0=SCALES.index(s) - 0.38,
                          y1=SCALES.index(s) + 0.38, fillcolor=BAND_COLORS[i], line_width=0, layer="below")
    fig.add_trace(go.Bar(
        y=ys, x=[official[s]["skor"] for s in SCALES], orientation="h", width=0.28,
        marker_color="#2F6F73",
        text=[f"{official[s]['skor']} · {official[s]['tingkat']}" for s in SCALES], textposition="outside",
        cliponaxis=False,
        hovertemplate="%{y}: skor %{x} dari 42<extra></extra>",
    ))
    fig.update_layout(
        height=230, margin=dict(l=10, r=110, t=10, b=30), showlegend=False,
        xaxis=dict(range=[0, 42], title="Skor (0–42)", gridcolor="rgba(0,0,0,0.06)"),
        yaxis=dict(autorange="reversed"), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(size=13),
    )
    return fig


def render_legend():
    chips = " ".join(
        f"<span style='background:{BAND_COLORS[i]};color:{LEVEL_TEXT[i]};padding:2px 10px;border-radius:999px;"
        f"font-size:0.8rem;margin-right:4px'>{LEVELS[i]}</span>" for i in range(5))
    st.markdown(f"<div style='margin:-6px 0 10px 0'>Pita latar: {chips}</div>", unsafe_allow_html=True)


def render_result(data: dict):
    hasil = data["hasil"]
    off = hasil["skoring_resmi"]

    st.markdown(f"#### Responden contoh #{data['respondent_id']}")
    cols = st.columns(3)
    for col, s in zip(cols, SCALES):
        li = off[s]["tingkat_idx"]
        col.markdown(
            f"<div style='background:{BAND_COLORS[li]};border-radius:14px;padding:14px 16px'>"
            f"<div style='font-size:0.85rem;color:#4A5A5E'>{LABEL[s]}</div>"
            f"<div style='font-size:1.9rem;font-weight:700;color:#1F2A2E;line-height:1.2'>{off[s]['skor']}"
            f"<span style='font-size:0.9rem;font-weight:400;color:#4A5A5E'> / 42</span></div>"
            f"<div style='font-weight:600;color:{LEVEL_TEXT[li]}'>{off[s]['tingkat']}</div></div>",
            unsafe_allow_html=True)

    st.plotly_chart(severity_chart(off), width="stretch", config={"displayModeBar": False})
    render_legend()

    prof = hasil["profil"]
    st.markdown("**Profil pola respons** (model clustering)")
    st.markdown(
        f"<div style='border:1px solid #D5E2DF;border-radius:14px;padding:14px 16px;background:#FFFFFF'>"
        f"<div style='font-size:1.1rem;font-weight:700;color:#2F6F73'>{prof['nama']}</div>"
        f"<div style='margin-top:6px'>{prof['deskripsi']}</div>"
        + (f"<div style='margin-top:8px;color:#8A5A12'>ⓘ {prof['catatan']}</div>" if prof.get("catatan") else "")
        + "</div>", unsafe_allow_html=True)
    st.write("")

    st.markdown("**Skoring resmi vs model klasifikasi**")
    clf = hasil["klasifikasi"]["per_skala"]
    rows = "".join(
        f"<tr><td>{LABEL[s]}</td><td>{off[s]['tingkat']}</td><td>{clf[s]['tingkat']}</td>"
        f"<td style='text-align:center'>{'✓' if clf[s]['sama_dengan_resmi'] else '≠'}</td></tr>" for s in SCALES)
    st.markdown(
        "<table style='width:100%;border-collapse:collapse;font-size:0.92rem'>"
        "<tr style='text-align:left;color:#4A5A5E'><th>Skala</th><th>Resmi</th><th>Model</th><th>Sama</th></tr>"
        f"{rows}</table>", unsafe_allow_html=True)
    if hasil["klasifikasi"]["semua_sama_dengan_resmi"]:
        st.caption("Model klasifikasi memberi tingkat yang sama dengan aturan resmi.")
    else:
        st.caption("Ada perbedaan. Hasil yang berlaku tetap skoring resmi.")

    with st.expander("Lihat 42 jawaban responden ini"):
        st.caption("Teks item dalam bahasa aslinya (Inggris). Jawaban menggambarkan satu minggu terakhir.")
        tabs = st.tabs([LABEL[s] for s in SCALES])
        for tab, s in zip(tabs, SCALES):
            with tab:
                for it in data["item_per_skala"][s]:
                    st.markdown(f"<div style='display:flex;justify-content:space-between;gap:12px;padding:4px 0;"
                                f"border-bottom:1px solid #EEF3F2'><span><b>{it['item']}</b> {it['teks_en']}</span>"
                                f"<span style='white-space:nowrap;color:#2F6F73'>{ANSWER_LABEL[it['jawaban']]}</span>"
                                f"</div>", unsafe_allow_html=True)
