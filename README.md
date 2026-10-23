# Ruang Tenang — Skrining Mandiri PHQ-9 & GAD-7 + Chatbot RAG

Aplikasi belajar (Bootcamp AI Engineer) dengan alur lengkap aplikasi AI:
pipeline data → model ML (dicatat di MLflow) → API FastAPI → chatbot RAG dengan pengaman → UI Streamlit → Docker/deploy.

Pengguna mengisi **16 pertanyaan** (PHQ-9 untuk depresi, GAD-7 untuk kecemasan) tentang 2 minggu terakhir,
lalu melihat skor, tingkat keluhan, pola keluhan, dan bisa bertanya ke chatbot. **Hasil adalah skrining, bukan
diagnosis.** Jawaban tidak disimpan.

> Versi awal proyek ini memakai DASS-42. DASS diganti karena aturan pembuatnya tidak mengizinkan DASS diberikan
> lewat aplikasi yang terbuka untuk umum (DASS FAQ no. 21). PHQ-9 dan GAD-7 boleh digandakan, diterjemahkan,
> dan ditampilkan tanpa izin.

## Fitur

| Bagian | Isi |
|---|---|
| Skoring resmi | PHQ-9 0–27 (Minimal/Ringan/Sedang/Sedang–berat/Berat), GAD-7 0–21 (Minimal/Ringan/Sedang/Berat); tanda pemeriksaan lanjutan bila skor ≥ 10 |
| Pengaman item 9 | Jawaban PHQ-9 nomor 9 selain "tidak pernah" langsung memunculkan panel bantuan (Healing119.id, 119, IGD), apa pun skornya |
| Model klasifikasi | Memprediksi tingkat dari 16 jawaban; 3 algoritma dibandingkan + eksperimen skrining singkat (PHQ-2/GAD-2 vs item terpilih data) |
| Model clustering | Pola keluhan dari **bentuk** jawaban (keluhan mana yang relatif menonjol), k dipilih dengan silhouette |
| Chatbot RAG | BM25 + perluasan kueri Indonesia→Inggris atas 3 dokumen WHO + kartu PHQ-9/GAD-7; LLM opsional (Groq) |
| Pengaman chatbot | Deteksi krisis (pesan baku), tolak topik obat, tolak upaya mengubah aturan, tolak di luar topik, catatan non-diagnosis |
| MLflow | Semua run tercatat; model terbaik terdaftar di Model Registry dengan alias `champion` |

## Struktur folder

```
data/raw/phq_gad/          phq9.csv, gad7.csv, demographic.csv (Zenodo, CC BY 4.0) + SUMBER.md
data/processed/            laporan_pembersihan.json (train/test dibuat ulang pipeline)
data/kuesioner_id.json     teks petunjuk, pilihan jawaban, dan 16 item Bahasa Indonesia
knowledge/                 dokumen sumber chatbot (.md); file berawalan "_" tidak diindeks
models/                    classifier.joblib, cluster.joblib + metadata/evaluasi (.json)
src/data/                  scoring.py (aturan resmi), pipeline.py (pembersihan & split)
src/ml/                    train_classifier.py, train_cluster.py, predict.py, features.py, mlflow_utils.py
src/rag/                   chunker.py, retriever.py, guardrails.py, llm.py, chat.py
src/backend/main.py        FastAPI: /health /kuesioner /info /predict /chat
src/frontend/              app.py (Streamlit) + components/
deploy/streamlit_cloud/    streamlit_app.py (backend + frontend dalam satu app)
tests/                     pytest
```

## Menjalankan di komputer sendiri

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements-train.txt

python -m src.run_pipeline        # (opsional) latih ulang; model siap pakai sudah ada di models/

python -m uvicorn src.backend.main:app --port 8000      # terminal 1
python -m streamlit run src/frontend/app.py             # terminal 2
```

UI: http://localhost:8501 · API: http://localhost:8000/docs ·
MLflow: `mlflow ui --backend-store-uri sqlite:///mlflow.db` → http://localhost:5000
(2 eksperimen: `phq9-gad7-klasifikasi` 11 run, `phq9-gad7-clustering` 14 run; 2 model terdaftar).

LLM opsional: salin `.env.example` menjadi `.env`, isi `GROQ_API_KEY`. Tanpa kunci, chatbot memakai mode
kutipan dokumen. Tes: `python -m pytest`.

## Docker

```bash
docker compose up --build                              # backend :8000 + frontend :8501
docker compose --profile train run --rm pipeline       # latih ulang model (opsional)
docker compose --profile mlflow up mlflow              # MLflow UI :5000 (setelah pipeline)
```

## Deploy ke Streamlit Community Cloud

Main file path: `deploy/streamlit_cloud/streamlit_app.py`, Python 3.13, Secrets: `GROQ_API_KEY = "…"`.
Setiap push ke `main` otomatis memperbarui aplikasi.

## Hasil utama

- **Data:** 24.292 → **23.589** pengisian setelah pembersihan (usia 18–60, bukan jawaban seragam selain semua 0,
  total waktu ≥ 16 detik). 29% menjawab "tidak pernah" untuk semua item; korelasi PHQ-9–GAD-7 r = 0,76.
- **Klasifikasi:** regresi logistik akurasi ~100% (tingkat resmi adalah fungsi linear dari jawaban);
  HistGradientBoosting 99,1%, Random Forest 98,2% (F1 makro lebih rendah karena kelas berat sangat jarang).
- **Skrining singkat** (target skor ≥ 10): PHQ-2 sensitivitas 0,61 / spesifisitas 0,98; GAD-2 0,85 / 0,98.
  Item terpilih data tampak lebih baik, tetapi dipilih dari populasi yang sama.
- **Clustering:** klaster dari item mentah sebagian besar mengulang berat-ringan keluhan (η² ≈ 0,8). Dari bentuk
  item (η² < 0,1), k = 3: *terlalu khawatir & gugup/tegang*, *masalah tidur & lelah*, *minat menurun & lelah*.
  Silhouette rendah (~0,07) → pola bersifat kontinu; profil adalah deskripsi, bukan kategori klinis.

## Etika & batasan

- Bukan alat diagnosis; tidak menggantikan tenaga profesional.
- Data latih: mahasiswa satu universitas di Tiongkok (2021) — **tidak mewakili masyarakat Indonesia**.
- Teks GAD-7 adalah terjemahan kerja; cocokkan dengan versi Indonesia tervalidasi sebelum dipakai di luar proyek belajar.
- Kalimat yang menyebut nama obat dihapus dari dokumen sumber (`knowledge/_kalimat_obat_dibuang.md`); jawaban LLM yang
  menyebut obat diganti jawaban baku.
- Nomor layanan bantuan diverifikasi 23 Oktober 2026 — cek ulang sebelum demo.

## Sumber & lisensi

- Kroenke, Spitzer & Williams (2001), PHQ-9; Spitzer, Kroenke, Williams & Löwe (2006), GAD-7. Bebas dipakai.
- Su, Z. (2023). *Temporal dynamics in psychological assessments* [dataset]. Zenodo. https://zenodo.org/records/10423537 (CC BY 4.0).
- WHO (2020). *Hal yang Perlu Dilakukan Saat Stres: Panduan Bergambar*. CC BY-NC-SA 3.0 IGO.
- WHO Fact Sheets: *Depressive disorder (depression)* (11 Sep 2026), *Anxiety disorders* (15 Sep 2026).
- Healing119.id, Kementerian Kesehatan RI.

Aplikasi ini tidak berafiliasi dengan dan tidak didukung oleh WHO, Pfizer, atau Kementerian Kesehatan.
