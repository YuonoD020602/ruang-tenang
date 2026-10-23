"""Latih model klasifikasi tingkat keluhan (PHQ-9: 5 tingkat, GAD-7: 4 tingkat) + eksperimen skrining singkat.

Eksperimen 1 — model lengkap: 3 algoritma memprediksi tingkat dari 16 jawaban item.
Eksperimen 2 — skrining singkat: seberapa baik 2 item (PHQ-2 / GAD-2, versi pendek resmi) dan k item
               terpilih data menandai "skor >= 10" (batas umum untuk pemeriksaan lanjutan)?

Semua run dicatat di MLflow; model lengkap terbaik didaftarkan ke Model Registry (alias champion)
dan disimpan ke models/classifier.joblib untuk dipakai backend.

Jalankan:  python -m src.ml.train_classifier
"""
from __future__ import annotations

import json
import warnings

import joblib
import mlflow
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.multioutput import MultiOutputClassifier

from src.config import (DATA_PROCESSED, ITEM_COLS, MLFLOW_EXPERIMENT_CLF, MLFLOW_TRACKING_URI, MODELS_DIR,
                        RANDOM_STATE, REFERRAL_SCORE, REGISTERED_CLF, SCALES)
from src.ml.mlflow_utils import log_sklearn_model, use_experiment

warnings.filterwarnings("ignore")
TARGETS = [f"tingkat_{s}" for s in SCALES]
SHORT_FORM = {"depresi": ["P1", "P2"], "kecemasan": ["G1", "G2"]}   # PHQ-2 dan GAD-2
SHORT_CUTOFF = 3                                                    # batas umum PHQ-2/GAD-2


def load():
    return pd.read_csv(DATA_PROCESSED / "train.csv"), pd.read_csv(DATA_PROCESSED / "test.csv")


def evaluate(y_true: pd.DataFrame, y_pred: np.ndarray) -> dict:
    m = {}
    for j, t in enumerate(TARGETS):
        sc = t.replace("tingkat_", "")
        yt, yp = y_true[t].to_numpy(), y_pred[:, j]
        m[f"akurasi_{sc}"] = accuracy_score(yt, yp)
        m[f"f1_makro_{sc}"] = f1_score(yt, yp, average="macro")
    m["akurasi_rata2"] = float(np.mean([m[f"akurasi_{s}"] for s in SCALES]))
    m["f1_makro_rata2"] = float(np.mean([m[f"f1_makro_{s}"] for s in SCALES]))
    return m


CANDIDATES = {
    "logistic_regression": lambda: LogisticRegression(max_iter=5000, C=10.0),
    "random_forest": lambda: RandomForestClassifier(n_estimators=150, min_samples_leaf=3, n_jobs=-1,
                                                    random_state=RANDOM_STATE),
    "hist_gradient_boosting": lambda: HistGradientBoostingClassifier(max_iter=300, random_state=RANDOM_STATE),
}


def train_full_models(tr, te):
    X_tr, X_te, y_tr, y_te = tr[ITEM_COLS], te[ITEM_COLS], tr[TARGETS], te[TARGETS]
    results = []
    for name, make in CANDIDATES.items():
        with mlflow.start_run(run_name=f"lengkap16_{name}") as run:
            model = MultiOutputClassifier(make()).fit(X_tr, y_tr)
            pred = model.predict(X_te)
            metrics = evaluate(y_te, pred)
            mlflow.set_tags({"eksperimen": "model_lengkap_16_item", "algoritma": name})
            mlflow.log_params({"algoritma": name, "jumlah_item": 16, "n_train": len(X_tr), "n_test": len(X_te)})
            mlflow.log_metrics(metrics)
            log_sklearn_model(model, name="model", signature=infer_signature(X_te.head(5), pred[:5]),
                              input_example=X_te.head(2))
            results.append({"algoritma": name, "run_id": run.info.run_id, "model": model, **metrics})
            print(f"  {name:24s} akurasi rata2={metrics['akurasi_rata2']:.4f}  f1 makro={metrics['f1_makro_rata2']:.4f}")
    return results


def _screen_metrics(y_true, flag) -> dict:
    y_true, flag = np.asarray(y_true).astype(bool), np.asarray(flag).astype(bool)
    tp, fn = (flag & y_true).sum(), (~flag & y_true).sum()
    tn, fp = (~flag & ~y_true).sum(), (flag & ~y_true).sum()
    return {"sensitivitas": float(tp / max(tp + fn, 1)), "spesifisitas": float(tn / max(tn + fp, 1)),
            "persen_ditandai": float(100 * flag.mean())}


def short_screening(tr, te, ks=(2, 3, 4)):
    summary = {}
    for scale, items in SCALES.items():
        y_tr = tr[f"skor_{scale}"] >= REFERRAL_SCORE
        y_te = te[f"skor_{scale}"] >= REFERRAL_SCORE
        res = {"prevalensi_positif_persen_test": round(100 * float(y_te.mean()), 2), "hasil": []}

        # versi pendek resmi (PHQ-2 / GAD-2) dengan batas >= 3
        short = SHORT_FORM[scale]
        s2 = te[short].sum(axis=1)
        m = _screen_metrics(y_te, s2 >= SHORT_CUTOFF)
        m["auc"] = float(roc_auc_score(y_te, s2))
        with mlflow.start_run(run_name=f"singkat_{scale}_{'PHQ' if scale == 'depresi' else 'GAD'}-2"):
            mlflow.set_tags({"eksperimen": "skrining_singkat", "skala": scale, "metode": "versi_pendek_resmi"})
            mlflow.log_params({"skala": scale, "item": ",".join(short), "batas": SHORT_CUTOFF})
            mlflow.log_metrics(m)
        res["hasil"].append({"metode": f"{'PHQ' if scale == 'depresi' else 'GAD'}-2 (item {', '.join(short)}) ≥ 3",
                             **{k: round(v, 3) for k, v in m.items()}})

        # k item terpilih data (urutan kepentingan dari random forest), regresi logistik
        rf = RandomForestClassifier(n_estimators=200, n_jobs=-1, random_state=RANDOM_STATE).fit(tr[items], y_tr)
        ranking = [items[i] for i in np.argsort(rf.feature_importances_)[::-1]]
        for k in ks:
            feats = ranking[:k]
            clf = LogisticRegression(max_iter=3000, class_weight="balanced").fit(tr[feats], y_tr)
            prob = clf.predict_proba(te[feats])[:, 1]
            m = _screen_metrics(y_te, prob >= 0.5)
            m["auc"] = float(roc_auc_score(y_te, prob))
            with mlflow.start_run(run_name=f"singkat_{scale}_top{k}"):
                mlflow.set_tags({"eksperimen": "skrining_singkat", "skala": scale, "metode": "item_terpilih_data"})
                mlflow.log_params({"skala": scale, "jumlah_item": k, "item": ",".join(feats)})
                mlflow.log_metrics(m)
            res["hasil"].append({"metode": f"{k} item terpilih data ({', '.join(feats)})",
                                 **{kk: round(v, 3) for kk, v in m.items()}})
        res["urutan_item_terpenting"] = ranking
        summary[scale] = res
        for r in res["hasil"]:
            print(f"  {scale:9s} {r['metode']:38s} sens={r['sensitivitas']:.3f} spes={r['spesifisitas']:.3f} AUC={r['auc']:.3f}")
    return summary


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    use_experiment(MLFLOW_EXPERIMENT_CLF)
    tr, te = load()
    print("Model lengkap (16 item):")
    results = train_full_models(tr, te)
    best = max(results, key=lambda r: (r["f1_makro_rata2"], r["akurasi_rata2"]))
    print(f"Terbaik: {best['algoritma']}")
    mv = mlflow.register_model(f"runs:/{best['run_id']}/model", REGISTERED_CLF)
    mlflow.MlflowClient().set_registered_model_alias(REGISTERED_CLF, "champion", mv.version)

    print("Eksperimen skrining singkat (target: skor >= 10):")
    short = short_screening(tr, te)

    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump(best["model"], MODELS_DIR / "classifier.joblib")
    meta = {
        "algoritma_terpilih": best["algoritma"],
        "mlflow_run_id": best["run_id"],
        "registered_model": REGISTERED_CLF,
        "registered_version": int(mv.version),
        "target": TARGETS,
        "perbandingan_model": [{k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k != "model"}
                               for r in results],
        "pengurangan_item": short,
    }
    (MODELS_DIR / "classifier_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return meta


if __name__ == "__main__":
    main()
