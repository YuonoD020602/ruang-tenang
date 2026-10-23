"""Clustering pola keluhan dari 16 jawaban item PHQ-9 + GAD-7.

Dua set fitur dibandingkan dan semuanya dicatat di MLflow:

1. `item_mentah`  : 16 jawaban item yang distandarkan. Klaster cenderung hanya memisahkan keluhan
                    sedikit / sedang / banyak (mengulang skoring resmi) -> dipakai sebagai pembanding.
2. `bentuk_item`  : 16 jawaban dikurangi rata-rata jawaban orang itu sendiri (lihat src/ml/features.py).
                    Klaster menggambarkan keluhan mana yang RELATIF paling menonjol, misalnya tidur dan
                    kelelahan, atau rasa khawatir -> dipakai aplikasi.

Model dilatih hanya pada pengisian dengan total skor >= 3 (ada keluhan yang cukup untuk membentuk pola).
Aturan pemilihan model aplikasi: set `bentuk_item`, silhouette terbaik di antara k = 3..6.

Hasil: models/cluster.joblib dan models/cluster_profiles.json

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

from src.config import (DATA_PROCESSED, ITEM_COLS, MLFLOW_EXPERIMENT_CLUSTER, MLFLOW_TRACKING_URI, MODELS_DIR,
                        RANDOM_STATE, REGISTERED_CLUSTER, SCALES)
from src.ml.features import row_center
from src.ml.mlflow_utils import log_sklearn_model, use_experiment

warnings.filterwarnings("ignore")
MIN_TOTAL = 3
SHORT_NAME = {
    "P1": "minat menurun", "P2": "murung", "P3": "masalah tidur", "P4": "lelah", "P5": "nafsu makan berubah",
    "P6": "merasa gagal", "P7": "sulit konsentrasi", "P8": "gerak lambat/gelisah", "P9": "pikiran melukai diri",
    "G1": "gugup/tegang", "G2": "sulit berhenti khawatir", "G3": "terlalu khawatir", "G4": "sulit bersantai",
    "G5": "gelisah", "G6": "mudah kesal", "G7": "takut hal buruk",
}
NAMEABLE = [c for c in ITEM_COLS if c != "P9"]   # item 9 tidak dipakai sebagai nama profil


def make_pipeline(feature_set: str, k: int) -> Pipeline:
    first = ("bentuk", FunctionTransformer(row_center)) if feature_set == "bentuk_item" else ("scaler", StandardScaler())
    return Pipeline([first, ("kmeans", KMeans(n_clusters=k, n_init=20, random_state=RANDOM_STATE))])


def describe(center: pd.Series, members: pd.DataFrame, share: float) -> dict:
    top = center[NAMEABLE].sort_values(ascending=False)
    dep = center[SCALES["depresi"]].mean()
    anx = center[SCALES["kecemasan"]].mean()
    if top.iloc[0] < 0.2:
        nama = "Keluhan merata"
        ringkas = "Tidak ada keluhan yang jauh lebih menonjol dibanding keluhan lain."
    else:
        a, b = top.index[0], top.index[1]
        nama = f"Menonjol: {SHORT_NAME[a]} & {SHORT_NAME[b]}"
        arah = ("lebih banyak keluhan suasana hati dan energi (PHQ-9)" if dep - anx > 0.15
                else "lebih banyak keluhan rasa cemas dan khawatir (GAD-7)" if anx - dep > 0.15
                else "keluhan depresi dan kecemasan relatif seimbang")
        ringkas = f"Keluhan yang paling sering dilaporkan adalah {SHORT_NAME[a]} dan {SHORT_NAME[b]}; {arah}."
    rata = {s: round(float(members[f"skor_{s}"].mean()), 1) for s in SCALES}
    return {
        "nama": nama,
        "ringkas": ringkas,
        "item_menonjol": [SHORT_NAME[i] for i in top.index[:3]],
        "rata2_skor_anggota": rata,
        "ukuran_persen": round(100 * share, 1),
        "deskripsi": (f"{ringkas} Sekitar {100 * share:.0f}% pengisian dengan keluhan dalam data latih memiliki pola "
                      f"ini. Profil hanya menggambarkan kemiripan pola keluhan, bukan seberapa berat keluhannya "
                      f"(itu dilihat dari skoring resmi), dan bukan kategori klinis atau diagnosis."),
    }


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    use_experiment(MLFLOW_EXPERIMENT_CLUSTER)
    tr = pd.read_csv(DATA_PROCESSED / "train.csv")
    te = pd.read_csv(DATA_PROCESSED / "test.csv")
    tr = tr[tr[ITEM_COLS].sum(axis=1) >= MIN_TOTAL].reset_index(drop=True)
    te = te[te[ITEM_COLS].sum(axis=1) >= MIN_TOTAL].reset_index(drop=True)
    sample = tr.sample(min(8000, len(tr)), random_state=RANDOM_STATE)
    print(f"Data latih clustering: {len(tr)} pengisian (total skor >= {MIN_TOTAL})")

    runs = []
    for feature_set in ("item_mentah", "bentuk_item"):
        print(f"Set fitur: {feature_set}")
        for k in range(2, 9):
            with mlflow.start_run(run_name=f"{feature_set}_k{k}") as run:
                pipe = make_pipeline(feature_set, k).fit(tr[ITEM_COLS])
                Zs = pipe[:-1].transform(sample[ITEM_COLS])
                lab = pipe.named_steps["kmeans"].predict(Zs)
                sil, dbi = silhouette_score(Zs, lab), davies_bouldin_score(Zs, lab)
                sizes = np.bincount(pipe.predict(tr[ITEM_COLS]), minlength=k) / len(tr)
                # seberapa jauh klaster hanya mencerminkan berat-ringan keluhan: korelasi rasio-eta skor total
                total = tr[ITEM_COLS].sum(axis=1)
                labels_all = pipe.predict(tr[ITEM_COLS])
                eta2 = float(pd.Series(total).groupby(labels_all).transform("mean").var() / total.var())
                mlflow.set_tags({"algoritma": "kmeans", "set_fitur": feature_set})
                mlflow.log_params({"k": k, "set_fitur": feature_set, "min_total_skor": MIN_TOTAL})
                mlflow.log_metrics({"silhouette": sil, "davies_bouldin": dbi,
                                    "inersia": pipe.named_steps["kmeans"].inertia_,
                                    "ukuran_klaster_terkecil_persen": 100 * sizes.min(),
                                    "eta2_skor_total": eta2})
                log_sklearn_model(pipe, name="model",
                                  signature=infer_signature(te[ITEM_COLS].head(5), pipe.predict(te[ITEM_COLS].head(5))),
                                  input_example=te[ITEM_COLS].head(2))
                runs.append({"set_fitur": feature_set, "k": k, "run_id": run.info.run_id, "pipe": pipe,
                             "silhouette": round(float(sil), 4), "davies_bouldin": round(float(dbi), 4),
                             "ukuran_terkecil_persen": round(100 * float(sizes.min()), 1),
                             "eta2_skor_total": round(eta2, 3)})
                print(f"  k={k}: silhouette={sil:.3f}  DBI={dbi:.3f}  terkecil={100 * sizes.min():.1f}%  "
                      f"eta²(skor total)={eta2:.2f}")

    eligible = [r for r in runs if r["set_fitur"] == "bentuk_item" and 3 <= r["k"] <= 6]
    best = max(eligible, key=lambda r: r["silhouette"])
    print(f"Dipilih: bentuk_item, k={best['k']}")
    mv = mlflow.register_model(f"runs:/{best['run_id']}/model", REGISTERED_CLUSTER)
    mlflow.MlflowClient().set_registered_model_alias(REGISTERED_CLUSTER, "champion", mv.version)

    pipe = best["pipe"]
    labels = pipe.predict(tr[ITEM_COLS])
    centers = pd.DataFrame(pipe.named_steps["kmeans"].cluster_centers_, columns=ITEM_COLS)
    profiles = []
    for c in range(best["k"]):
        mask = labels == c
        p = describe(centers.loc[c], tr[mask], float(mask.mean()))
        profiles.append({"cluster_id": c, **p, "pusat_bentuk": {i: round(float(v), 2) for i, v in centers.loc[c].items()}})

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(pipe, MODELS_DIR / "cluster.joblib")
    meta = {
        "set_fitur_terpilih": "bentuk_item",
        "k_terpilih": best["k"],
        "aturan_pemilihan": "set fitur bentuk_item, silhouette terbaik di antara k=3..6",
        "min_total_skor": MIN_TOTAL,
        "korelasi_antar_skala": {"phq9_gad7": round(float(tr["skor_depresi"].corr(tr["skor_kecemasan"])), 2)},
        "mlflow_run_id": best["run_id"],
        "registered_model": REGISTERED_CLUSTER,
        "registered_version": int(mv.version),
        "perbandingan": [{k: v for k, v in r.items() if k != "pipe"} for r in runs],
        "profil": profiles,
    }
    (MODELS_DIR / "cluster_profiles.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    for p in profiles:
        print(f"  [{p['cluster_id']}] {p['nama']} ({p['ukuran_persen']}%) skor={p['rata2_skor_anggota']}")
    return meta


if __name__ == "__main__":
    main()
