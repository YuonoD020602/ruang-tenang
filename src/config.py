"""Konfigurasi terpusat: path, definisi skala DASS-42, dan batas tingkat keparahan."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW_ZIP = ROOT / "data" / "raw" / "DASS_data_21.02.19.zip"
DATA_PROCESSED = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
KNOWLEDGE_DIR = ROOT / "knowledge"

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", f"sqlite:///{(ROOT / 'mlflow.db').as_posix()}")
MLFLOW_EXPERIMENT_CLF = "dass42-klasifikasi"
MLFLOW_EXPERIMENT_CLUSTER = "dass42-clustering"
REGISTERED_CLF = "dass42_severity_classifier"
REGISTERED_CLUSTER = "dass42_profile_cluster"

RANDOM_STATE = 42

# Nomor item (urutan asli DASS-42, Q1..Q42) per skala
SCALES = {
    "depresi":   [3, 5, 10, 13, 16, 17, 21, 24, 26, 31, 34, 37, 38, 42],
    "kecemasan": [2, 4, 7, 9, 15, 19, 20, 23, 25, 28, 30, 36, 40, 41],
    "stres":     [1, 6, 8, 11, 12, 14, 18, 22, 27, 29, 32, 33, 35, 39],
}
ITEM_COLS = [f"Q{i}" for i in range(1, 43)]

# Batas atas tiap tingkat (inklusif) untuk Normal, Ringan, Sedang, Berat; di atasnya = Sangat berat
CUTOFFS = {
    "depresi":   [9, 13, 20, 27],
    "kecemasan": [7, 9, 14, 19],
    "stres":     [14, 18, 25, 33],
}
LEVELS = ["Normal", "Ringan", "Sedang", "Berat", "Sangat berat"]

# Aturan pembersihan data (disepakati)
CLEANING = {
    "age_min": 18,
    "age_max": 80,
    "max_fake_words": 1,      # buang jika mencentang >= 2 dari 3 kata palsu
    "min_test_seconds": 84,   # < 2 detik per item dianggap asal-asalan
}
