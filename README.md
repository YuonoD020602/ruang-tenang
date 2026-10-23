# Demo Skrining DASS-42 + Chatbot RAG

Aplikasi belajar (Bootcamp AI Engineer) yang memperlihatkan alur lengkap aplikasi AI:
pipeline data → model ML (dicatat di MLflow) → API FastAPI → chatbot RAG dengan pengaman → UI Streamlit → Docker/deploy.

> **Mode demo.** Pengguna **tidak mengisi kuesioner**. Aturan penggunaan DASS tidak mengizinkan DASS diberikan
> lewat website/aplikasi yang terbuka untuk umum (DASS FAQ no. 21). Aplikasi menampilkan **responden anonim** dari
> dataset publik. Hasil skrining **bukan diagnosis**.

## Fitur

| Bagian | Isi |
|---|---|
| Skoring resmi | Skor & tingkat (Normal–Sangat berat) depresi, kecemasan, stres dengan aturan baku DASS-42 |
| Model klasifikasi | Memprediksi tingkat dari 42 jawaban; 3 algoritma dibandingkan + eksperimen pengurangan item |
| Model clustering | Profil **bentuk** pola respons (skala mana yang relatif menonjol), k dipilih dengan silhouette |
| Chatbot RAG | BM25 + perluasan kueri Indonesia→Inggris atas 3 dokumen WHO + kartu DASS-42; LLM opsional (Groq) |
| Pengaman | Deteksi krisis (pesan baku Healing119.id), tolak topik obat, tolak upaya mengubah aturan, tolak di luar topik, catatan non-diagnosis |
| MLflow | Semua run tercatat; model terbaik terdaftar di Model Registry dengan alias `champion` |

## Struktur folder

```
data/raw/                  DASS_data_21.02.19.zip (Open Psychometrics)
data/processed/            demo_respondents.csv, laporan_pembersihan.json (train/test dibuat ulang pipeline)
data/dass42_items_en.json  teks asli 42 item (domain publik)
knowledge/                 dokumen sumber chatbot (.md). File berawalan "_" tidak diindeks
models/                    classifier.joblib, cluster.joblib + metadata/evaluasi (.json)
src/data/                  scoring.py (aturan resmi), pipeline.py (pembersihan & split)
src/ml/                    train_classifier.py, train_cluster.py, predict.py, features.py, mlflow_utils.py
src/rag/                   chunker.py, retriever.py, guardrails.py, llm.py, chat.py
src/backend/main.py        FastAPI: /health /info /respondents /respondents/{id} /predict /chat
src/frontend/              app.py (Streamlit) + components/
deploy/streamlit_cloud/    streamlit_app.py (backend + frontend dalam satu app)
tests/                     58 tes pytest
```

## Menjalankan di komputer sendiri

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements-train.txt

# (opsional) latih ulang semua model; model siap pakai sudah ada di folder models/
python -m src.run_pipeline

# terminal 1: backend
python -m uvicorn src.backend.main:app --port 8000
# terminal 2: frontend
python -m streamlit run src/frontend/app.py
```

Buka http://localhost:8501 (UI) dan http://localhost:8000/docs (dokumentasi API).

**Melihat MLflow:** setelah `python -m src.run_pipeline`, jalankan
`mlflow ui --backend-store-uri sqlite:///mlflow.db` lalu buka http://localhost:5000.
Ada 2 eksperimen (`dass42-klasifikasi`: 21 run, `dass42-clustering`: 14 run) dan 2 model terdaftar
(`dass42_severity_classifier`, `dass42_profile_cluster`).

**Mengaktifkan LLM (opsional):** salin `.env.example` menjadi `.env`, isi `GROQ_API_KEY`. Tanpa kunci, chatbot
tetap berjalan dalam mode kutipan dokumen.

**Tes:** `python -m pytest`

## Docker

```bash
docker compose up --build                              # backend :8000 + frontend :8501
docker compose --profile train run --rm pipeline       # latih ulang model (opsional)
docker compose --profile mlflow up mlflow              # MLflow UI :5000 (setelah pipeline)
```

## Deploy ke Streamlit Community Cloud

1. Push repo ke GitHub.
2. Di share.streamlit.io: **New app** → pilih repo & branch → **Main file path**:
   `deploy/streamlit_cloud/streamlit_app.py`.
3. (Opsional) **Advanced settings → Secrets**: `GROQ_API_KEY = "…"`.
4. Deploy. Launcher menyalakan backend di latar lalu menampilkan frontend.

## Hasil utama

- Data: 39.775 → **31.382** responden setelah 4 aturan pembersihan (usia 18–80, bukan jawaban seragam,
  < 2 kata palsu pada cek kosakata, durasi ≥ 84 detik). Split 80/20 terstratifikasi.
- Klasifikasi: regresi logistik **100%** (karena tingkat resmi adalah fungsi linear dari jawaban);
  HistGradientBoosting 93,7%; Random Forest 86,8%. Dengan 7 item terpenting per skala, akurasi turun ke ±75%.
- Clustering: skor 3 skala berkorelasi tinggi (r = 0,66–0,80), sehingga klaster dari skor mentah hanya
  memisahkan rendah/sedang/berat. Dipakai fitur **bentuk profil** (z-score dikurangi rata-rata baris), k = 5:
  Seimbang (36,5%), Stres menonjol (19,4%), Kecemasan menonjol (17,6%), Depresi & stres > kecemasan (15,7%),
  Depresi menonjol (10,8%). Silhouette 0,32 — pola bersifat kontinu, profil adalah deskripsi, bukan kategori klinis.

## Etika & batasan

- Bukan alat diagnosis; DASS-42 tidak memuat item tentang menyakiti diri, jadi pesan krisis selalu tersedia.
- Sampel online sukarela, lebih dari separuh dari Malaysia — **tidak mewakili masyarakat Indonesia**.
- Kolom demografis sensitif (agama, orientasi seksual, ras, dll.) tidak dipakai sama sekali.
- Kalimat yang menyebut nama obat dihapus dari dokumen sumber (lihat `knowledge/_kalimat_obat_dibuang.md`), dan
  jawaban LLM yang menyebut obat diganti jawaban baku.
- Nomor layanan bantuan diverifikasi 23 Oktober 2026 — cek ulang sebelum demo.

## Sumber & lisensi

- DASS-42: Lovibond, S.H. & Lovibond, P.F. (1995). *Manual for the DASS* (2nd ed.). Domain publik.
  FAQ & aturan penggunaan: https://dass.psy.unsw.edu.au/DASSFAQ.htm
- Data: Open Psychometrics (2019). https://openpsychometrics.org/_rawdata/DASS_data_21.02.19.zip
- WHO (2020). *Hal yang Perlu Dilakukan Saat Stres: Panduan Bergambar*. CC BY-NC-SA 3.0 IGO.
- WHO Fact Sheets: *Depressive disorder (depression)* (11 Sep 2026), *Anxiety disorders* (15 Sep 2026).
- Healing119.id, Kementerian Kesehatan RI.

Aplikasi ini tidak berafiliasi dengan dan tidak didukung oleh WHO, UNSW, atau Kementerian Kesehatan.
