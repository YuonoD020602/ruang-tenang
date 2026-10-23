"""Gaya tampilan "Ruang Tenang".

Arah desain: ruang yang teduh di siang hari (latar hijau-kabut, kartu putih, aksen hijau laguna) dengan satu
elemen yang sengaja paling mencolok: panel chatbot berwarna langit senja yang menempel di samping kuesioner,
seperti lampu yang selalu menyala di sudut ruangan. Satu huruf saja, Plus Jakarta Sans.
"""

PALETTE = {
    "laguna": "#1E5B5A",     # aksen utama, tombol, pilihan terpilih
    "kabut": "#F3F7F5",      # latar halaman
    "kertas": "#FFFFFF",     # kartu
    "tinta": "#1C2B2D",      # teks utama
    "redup": "#5B6B6E",      # teks pendukung
    "garis": "#DCE8E3",      # garis kartu
    "senja_1": "#25204A",    # panel chatbot (atas)
    "senja_2": "#41387A",    # panel chatbot (bawah)
    "lampu": "#F2C46D",      # aksen hangat di panel chatbot
}

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

:root {
  --laguna:#1E5B5A; --kabut:#F3F7F5; --kertas:#FFFFFF; --tinta:#1C2B2D; --redup:#5B6B6E; --garis:#DCE8E3;
  --senja1:#25204A; --senja2:#41387A; --lampu:#F2C46D;
}
html, body, .stApp, .stMarkdown, p, li, label, input, textarea, button, h1, h2, h3, h4, h5, h6,
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
  font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
}
[data-testid="stIconMaterial"], .material-symbols-rounded { font-family: 'Material Symbols Rounded' !important; }
.stApp { background: var(--kabut); color: var(--tinta); }
.block-container { padding-top: 2.2rem; max-width: 1240px; }
header[data-testid="stHeader"] { background: transparent; }

/* ---------- hero ---------- */
.rt-brand { display:flex; align-items:center; gap:10px; color:var(--laguna); font-weight:700; font-size:1rem; }
.rt-brand svg { width:30px; height:30px; }
.rt-hero h1 { font-size: clamp(1.9rem, 3.6vw, 2.9rem); font-weight:800; letter-spacing:-0.025em; line-height:1.12;
              color:var(--tinta); margin:14px 0 10px 0; max-width: 20ch; }
.rt-hero p.lead { font-size:1.08rem; color:var(--redup); max-width: 62ch; line-height:1.6; margin:0; }
.rt-help { display:flex; flex-wrap:wrap; gap:6px 18px; align-items:center; margin:18px 0 6px 0; padding:12px 16px;
           background:#E4F0EC; border-radius:14px; font-size:0.95rem; color:var(--tinta); }
.rt-help b { color:var(--laguna); }

/* ---------- tabs ---------- */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid var(--garis); }
.stTabs [data-baseweb="tab"] { font-weight:600; padding: 10px 14px; }

/* ---------- kuesioner ---------- */
[data-testid="stElementContainer"]:has(.rt-progress) { position:sticky; top:0; z-index:5; }
.rt-progress { background:var(--kabut); padding:10px 0 12px 0; }
.rt-progress .bar { height:8px; border-radius:99px; background:#DCE8E3; overflow:hidden; }
.rt-progress .fill { height:100%; background:var(--laguna); border-radius:99px; transition: width .25s ease; }
.rt-progress .txt { font-size:0.9rem; color:var(--redup); margin-top:6px; }
.rt-section { font-weight:700; font-size:1.12rem; color:var(--tinta); margin:22px 0 2px 0; }
.rt-section span { display:block; font-weight:500; font-size:0.92rem; color:var(--redup); margin-top:2px; }

[class*="st-key-qcard_"] { background:var(--kertas); border:1px solid var(--garis); border-left:5px solid var(--garis);
                           border-radius:16px; padding:14px 18px 10px 18px; margin-bottom:10px; }
[class*="st-key-qcard_"]:has(input:checked) { border-left-color: var(--laguna); }
[class*="st-key-qcard_"] [data-testid="stWidgetLabel"] p { font-size:1rem; font-weight:600; color:var(--tinta); line-height:1.45; }
[class*="st-key-qcard_"] div[role="radiogroup"] { gap:8px; flex-wrap:wrap; }
[class*="st-key-qcard_"] div[role="radiogroup"] label {
  border:1.5px solid #CADCD5; border-radius:999px; padding:6px 14px; margin:0; background:#fff; cursor:pointer;
}
[class*="st-key-qcard_"] div[role="radiogroup"] label:hover { border-color: var(--laguna); }
[class*="st-key-qcard_"] label[data-testid="stRadioOption"] > div > div:first-child { display:none; }
[class*="st-key-qcard_"] div[role="radiogroup"] label p { font-size:0.92rem; color:var(--tinta); }
[class*="st-key-qcard_"] div[role="radiogroup"] label:has(input:checked) { background:var(--laguna); border-color:var(--laguna); }
[class*="st-key-qcard_"] div[role="radiogroup"] label:has(input:checked) p { color:#fff; font-weight:600; }
[class*="st-key-qcard_"] div[role="radiogroup"] label:has(input:focus-visible) { outline:3px solid var(--lampu); outline-offset:2px; }

.stButton > button[kind="primary"] { background:var(--laguna); border-color:var(--laguna); border-radius:14px;
                                     font-weight:700; padding:0.7rem 1rem; }
.stButton > button[kind="primary"]:disabled { background:#A9C3BD; border-color:#A9C3BD; color:#fff; }

/* ---------- panel chatbot: elemen paling mencolok ---------- */
[data-testid="stColumn"]:has(.st-key-chatpanel) {
  position: sticky; top: 1rem; align-self: flex-start; max-height: calc(100vh - 2rem); overflow-y: auto;
  border-radius: 24px;
}
.st-key-chatpanel {
  background: linear-gradient(165deg, var(--senja1) 0%, var(--senja2) 100%);
  border-radius: 24px; padding: 22px 20px 16px 20px; color:#F4F1FF;
  box-shadow: 0 18px 40px -18px rgba(37,32,74,.55);
}
.st-key-chatpanel p, .st-key-chatpanel li, .st-key-chatpanel span, .st-key-chatpanel label { color:#F4F1FF; }
.st-key-chatpanel a { color: var(--lampu); }
.rt-chat-head { display:flex; gap:12px; align-items:center; }
.rt-chat-head .lamp { width:44px; height:44px; border-radius:50%; background: radial-gradient(circle at 35% 35%, #FFE4A8, var(--lampu) 60%, #C9973C);
                      box-shadow: 0 0 22px 4px rgba(242,196,109,.45); flex:none; }
.rt-chat-head h3 { margin:0; padding:0 !important; font-size:1.25rem; font-weight:800; color:#fff; letter-spacing:-0.01em; }
.rt-chat-head p { margin:2px 0 0 0; font-size:0.9rem; color:#CFC8F2 !important; }
.rt-chat-hint { font-size:0.88rem; color:#CFC8F2 !important; margin:16px 0 4px 0; }
.rt-fab:hover, .rt-fab:visited { color:#fff !important; text-decoration:none !important; }

.st-key-chatpanel .stButton > button {
  background: rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.22); color:#fff; border-radius:12px;
  text-align:left; justify-content:flex-start; font-weight:500;
}
.st-key-chatpanel .stButton > button:hover { background: rgba(255,255,255,.16); border-color: var(--lampu); color:#fff; }
.st-key-chatpanel .stButton > button p { color:#fff; }
.st-key-chatpanel [data-testid="stChatMessage"] { background: rgba(255,255,255,.07); border-radius:16px; padding:10px 12px; }
.st-key-chatpanel [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
.st-key-chatpanel [data-testid="stChatMessage"]:has(.rt-user) { background: rgba(242,196,109,.14); }
.st-key-chatpanel [data-testid="stExpander"] details { background: rgba(0,0,0,.18); border-color: rgba(255,255,255,.15); border-radius:12px; }
.st-key-chatpanel [data-testid="stExpander"] summary p { color:#E7E2FF; }
.st-key-chatpanel [data-testid="stCaptionContainer"] p { color:#BDB5E6 !important; }
.st-key-chatpanel blockquote { border-left: 3px solid var(--lampu); color:#ECE8FF; }
.st-key-chatpanel [data-testid="stChatInput"] { background:#fff; border-radius:16px; }
.st-key-chatpanel [data-testid="stChatInput"] textarea { color: var(--tinta); }
.st-key-chatpanel [data-testid="stChatInput"] button { background: var(--lampu); color: var(--senja1); border-radius:12px; }
.st-key-chatpanel .stButton > button[kind="tertiary"] { background:transparent; border:none; color:#CFC8F2; padding:0; }

#teman-tanya { scroll-margin-top: 80px; }
/* tombol mengambang untuk layar sempit: langsung ke chatbot */
.rt-fab { display:none; }
@media (max-width: 900px) {
  [data-testid="stColumn"]:has(.st-key-chatpanel) { position: static; max-height:none; overflow:visible; }
  .rt-fab { display:flex; position:fixed; right:16px; bottom:18px; z-index:1000; align-items:center; gap:8px;
            background: linear-gradient(165deg, var(--senja1), var(--senja2)); color:#fff !important; text-decoration:none !important;
            padding:12px 18px; border-radius:999px; font-weight:700; box-shadow:0 10px 24px -8px rgba(37,32,74,.6); }
  .rt-fab .dot { width:12px; height:12px; border-radius:50%; background: var(--lampu); box-shadow:0 0 10px 2px rgba(242,196,109,.6); }
}
@media (prefers-reduced-motion: reduce) { .rt-progress .fill { transition:none; } }

/* ---------- hasil ---------- */
.rt-card { background:var(--kertas); border:1px solid var(--garis); border-radius:18px; padding:16px 18px; }
.rt-foot { color: var(--redup); font-size:0.85rem; line-height:1.6; }
</style>
"""

BRAND_SVG = (
    "<svg viewBox='0 0 32 32' aria-hidden='true'><circle cx='16' cy='16' r='15' fill='#E4F0EC'/>"
    "<path d='M16 25c0-6 1-10 6-14-6 1-9 4-10 8-1-3-3-5-6-6 3 3 4 7 4 12' fill='none' stroke='#1E5B5A' "
    "stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/></svg>"
)
