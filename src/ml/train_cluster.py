"""Clustering profil pola respons dari skor 3 skala (depresi, kecemasan, stres).

Dua set fitur dibandingkan dan semuanya dicatat di MLflow:

1. `tingkat`        : skor 3 skala yang distandarkan (z-score).
                      Temuan: karena ketiga skala berkorelasi tinggi (r = 0,66–0,80), klaster yang
                      terbentuk hanya memisahkan keluhan rendah / sedang / berat. Ini mengulang
                      informasi skoring resmi, jadi dipakai sebagai pembanding saja.
2. `bentuk_profil`  : z-score lalu dikurangi rata-rata barisnya (lihat src/ml/features.py).
                      Klaster menggambarkan skala mana yang RELATIF menonjol pada seseorang.
                      Ini informasi baru yang tidak diberikan skoring resmi -> dipakai aplikasi.

Aturan pemilihan model aplikasi: set `bentuk_profil`, silhouette terbaik di antara k = 3..6.

Hasil: models/cluster.joblib, models/cluster_profiles.json, data/processed/demo_respondents.csv

Jalankan:  python -m src.ml.train_cluster
"""
from __future__ import annotations

import json
import warnings

import joblib
import mlflow
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

from src.config import (DATA_PROCESSED, ITEM_COLS, MLFLOW_EXPERIMENT_CLUSTER, MLFLOW_TRACKING_URI,
                        MODELS_DIR, RANDOM_STATE, REGISTERED_CLUSTER, SCALES)
from src.ml.features import row_center
from src.ml.mlflow_utils import log_sklearn_model, use_experiment

warnings.filterwarnings("ignore")
FEATURES = [f"skor_{s}" for s in SCALES]
SCALE_LIST = list(SCALES)
GAP = 0.35  # selisih (dalam satuan z) agar suatu skala dianggap "menonjol" / "lebih rendah"


def make_pipeline(feature_set: str, k: int) -> Pipeline:
    steps = [("scaler", StandardScaler())]
    if feature_set == "bentuk_profil":
        steps.append(("bentuk", FunctionTransformer(row_center)))
    steps.append(("kmeans", KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE)))
    return Pipeline(steps)


def transform_until_kmeans(pipe: Pipeline, X):
    return pipe[:-1].transform(X)


def label_shape(center: np.ndarray) -> tuple[str, str]:
    """Nama & kalimat penjelas dari pusat klaster (vektor bentuk profil, jumlahnya ~0)."""
    order = np.argsort(center)[::-1]           # dari paling tinggi relatif
    hi, mid, lo = (SCALE_LIST[i] for i in order)
    c_hi, c_mid, c_lo = center[order]
    if c_hi - c_mid >= GAP:
        return (f"{hi.capitalize()} paling menonjol",
                f"Dibanding dua skala lain, keluhan {hi} relatif paling tinggi.")
    if c_mid - c_lo >= GAP:
        return (f"{hi.capitalize()} & {mid} lebih tinggi daripada {lo}",
                f"Keluhan {hi} dan {mid} relatif setara, sedangkan {lo} relatif paling rendah.")
    return ("Seimbang di ketiga skala",
            "Ketiga skala berada pada tingkat yang relatif seimbang; tidak ada yang jauh lebih menonjol.")


def build_profiles(pipe: Pipeline, train: pd.DataFrame) -> list[dict]:
    labels = pipe.predict(train[FEATURES])
    centers = pipe.named_steps["kmeans"].cluster_centers_
    profiles = []
    for c in range(len(centers)):
        mask = labels == c
        nama, kalimat = label_shape(centers[c])
        profiles.append({
            "cluster_id": int(c),
            "nama": nama,
            "ringkas": kalimat,
            "ukuran_persen": round(100 * float(mask.mean()), 1),
            "pusat_bentuk_z": {s: round(float(v), 2) for s, v in zip(SCALE_LIST, centers[c])},
            "rata2_skor_anggota": {s: round(float(train.loc[mask, f"skor_{s}"].mean()), 1) for s in SCALES},
            "deskripsi": (f"{kalimat} Sekitar {100 * mask.mean():.0f}% responden dalam data latih memiliki "
                          f"pola ini. Profil hanya menggambarkan perbandingan antarskala pada orang yang sama, "
                          f"bukan seberapa berat keluhannya (itu dilihat dari skoring resmi), dan bukan "
                          f"kategori klinis atau diagnosis."),
        })
    return profiles


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    use_experiment(MLFLOW_EXPERIMENT_CLUSTER)
    tr = pd.read_csv(DATA_PROCESSED / "train.csv")
    te = pd.read_csv(DATA_PROCESSED / "test.csv")
    sample = tr.sample(min(8000, len(tr)), random_state=RANDOM_STATE)
    corr = tr[FEATURES].corr().round(2)

    runs = []
    for feature_set in ("tingkat", "bentuk_profil"):
        print(f"Set fitur: {feature_set}")
        for k in range(2, 9):
            with mlflow.start_run(run_name=f"{feature_set}_k{k}") as run:
                pipe = make_pipeline(feature_set, k).fit(tr[FEATURES])
                Zs = transform_until_kmeans(pipe, sample[FEATURES])
                lab = pipe.named_steps["kmeans"].predict(Zs)
                sil, dbi = silhouette_score(Zs, lab), davies_bouldin_score(Zs, lab)
                sizes = np.bincount(pipe.predict(tr[FEATURES]), minlength=k) / len(tr)
                mlflow.set_tags({"algoritma": "kmeans", "set_fitur": feature_set})
                mlflow.log_params({"k": k, "set_fitur": feature_set, "fitur": ",".join(FEATURES)})
                mlflow.log_metrics({"silhouette": sil, "davies_bouldin": dbi,
                                    "inersia": pipe.named_steps["kmeans"].inertia_,
                                    "ukuran_klaster_terkecil_persen": 100 * sizes.min()})
                sig = infer_signature(te[FEATURES].head(5), pipe.predict(te[FEATURES].head(5)))
                log_sklearn_model(pipe, name="model", signature=sig, input_example=te[FEATURES].head(2))
                runs.append({"set_fitur": feature_set, "k": k, "run_id": run.info.run_id, "pipe": pipe,
                             "silhouette": round(float(sil), 4), "davies_bouldin": round(float(dbi), 4),
                             "ukuran_terkecil_persen": round(100 * float(sizes.min()), 1)})
                print(f"  k={k}: silhouette={sil:.3f}  DBI={dbi:.3f}  klaster terkecil={100 * sizes.min():.1f}%")

    eligible = [r for r in runs if r["set_fitur"] == "bentuk_profil" and 3 <= r["k"] <= 6]
    best = max(eligible, key=lambda r: r["silhouette"])
    print(f"Dipilih: bentuk_profil, k={best['k']}")
    mv = mlflow.register_model(f"runs:/{best['run_id']}/model", REGISTERED_CLUSTER)
    mlflow.MlflowClient().set_registered_model_alias(REGISTERED_CLUSTER, "champion", mv.version)

    profiles = build_profiles(best["pipe"], tr)
    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(best["pipe"], MODELS_DIR / "cluster.joblib")
    meta = {
        "set_fitur_terpilih": "bentuk_profil",
        "k_terpilih": best["k"],
        "aturan_pemilihan": "set fitur bentuk_profil, silhouette terbaik di antara k=3..6",
        "korelasi_antar_skala": corr.to_dict(),
        "mlflow_run_id": best["run_id"],
        "registered_model": REGISTERED_CLUSTER,
        "registered_version": int(mv.version),
        "perbandingan": [{k: v for k, v in r.items() if k != "pipe"} for r in runs],
        "profil": profiles,
    }
    (MODELS_DIR / "cluster_profiles.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    for p in profiles:
        print(f"  [{p['cluster_id']}] {p['nama']} ({p['ukuran_persen']}%) pusat={p['pusat_bentuk_z']}")

    # Responden demo dari data TEST (tidak dipakai melatih): hingga 30 per profil, hanya jawaban item.
    te = te.copy()
    te["cluster_id"] = best["pipe"].predict(te[FEATURES])
    parts = [g.sample(min(30, len(g)), random_state=RANDOM_STATE) for _, g in te.groupby("cluster_id")]
    demo = pd.concat(parts)[["respondent_id"] + ITEM_COLS].sample(frac=1, random_state=RANDOM_STATE)
    demo.to_csv(DATA_PROCESSED / "demo_respondents.csv", index=False)
    print(f"Responden demo: {len(demo)} baris")
    return meta


if __name__ == "__main__":
    main()
