"""Konfigurasi terpusat: path, definisi kuesioner PHQ-9 & GAD-7, dan batas tingkat keluhan."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
QUESTIONNAIRE_FILE = ROOT / "data" / "kuesioner_id.json"
MODELS_DIR = ROOT / "models"
KNOWLEDGE_DIR = ROOT / "knowledge"

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", f"sqlite:///{(ROOT / 'mlflow.db').as_posix()}")
MLFLOW_EXPERIMENT_CLF = "phq9-gad7-klasifikasi"
MLFLOW_EXPERIMENT_CLUSTER = "phq9-gad7-clustering"
REGISTERED_CLF = "phq9_gad7_severity_classifier"
REGISTERED_CLUSTER = "phq9_gad7_symptom_profile"

RANDOM_STATE = 42

# Kode item per skala (urutan resmi)
SCALES = {
    "depresi": [f"P{i}" for i in range(1, 10)],    # PHQ-9
    "kecemasan": [f"G{i}" for i in range(1, 8)],   # GAD-7
}
INSTRUMENT = {"depresi": "PHQ-9", "kecemasan": "GAD-7"}
ITEM_COLS = SCALES["depresi"] + SCALES["kecemasan"]
MAX_SCORE = {"depresi": 27, "kecemasan": 21}

# Batas atas tiap tingkat (inklusif); di atas batas terakhir = tingkat terakhir
CUTOFFS = {
    "depresi": [4, 9, 14, 19],      # Minimal, Ringan, Sedang, Sedang–berat, Berat
    "kecemasan": [4, 9, 14],        # Minimal, Ringan, Sedang, Berat
}
LEVELS = {
    "depresi": ["Minimal", "Ringan", "Sedang", "Sedang–berat", "Berat"],
    "kecemasan": ["Minimal", "Ringan", "Sedang", "Berat"],
}
REFERRAL_SCORE = 10        # skor >= 10 pada salah satu skala -> sarankan pemeriksaan lanjutan
SELF_HARM_ITEM = "P9"      # jawaban > 0 -> tampilkan info bantuan krisis, apa pun skornya
