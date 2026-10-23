"""Latih model klasifikasi tingkat keparahan (3 skala x 5 tingkat) + eksperimen pengurangan item.

Semua run dicatat di MLflow; model terbaik didaftarkan ke Model Registry dan disimpan
ke models/classifier.joblib untuk dipakai backend.

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
from sklearn.metrics import accuracy_score, f1_score
from sklearn.multioutput import MultiOutputClassifier

from src.ml.mlflow_utils import log_sklearn_model, use_experiment
from src.config import (DATA_PROCESSED, ITEM_COLS, MLFLOW_EXPERIMENT_CLF, MLFLOW_TRACKING_URI,
                        MODELS_DIR, RANDOM_STATE, REGISTERED_CLF, SCALES)

warnings.filterwarnings("ignore")
TARGETS = [f"tingkat_{s}" for s in SCALES]


def load():
    tr = pd.read_csv(DATA_PROCESSED / "train.csv")
    te = pd.read_csv(DATA_PROCESSED / "test.csv")
    return tr, te


def evaluate(y_true: pd.DataFrame, y_pred: np.ndarray) -> dict:
    m = {}
    for j, t in enumerate(TARGETS):
        sc = t.replace("tingkat_", "")
        yt, yp = y_true[t].to_numpy(), y_pred[:, j]
        m[f"akurasi_{sc}"] = accuracy_score(yt, yp)
        m[f"f1_makro_{sc}"] = f1_score(yt, yp, average="macro")
        m[f"selisih_maks_1_tingkat_{sc}"] = float(np.mean(np.abs(yt - yp) <= 1))
    m["akurasi_rata2"] = float(np.mean([m[f"akurasi_{s}"] for s in SCALES]))
    m["f1_makro_rata2"] = float(np.mean([m[f"f1_makro_{s}"] for s in SCALES]))
    return m


CANDIDATES = {
    "logistic_regression": lambda: LogisticRegression(max_iter=3000, C=1.0),
    "random_forest": lambda: RandomForestClassifier(n_estimators=150, min_samples_leaf=5,
                                                    n_jobs=-1, random_state=RANDOM_STATE),
    "hist_gradient_boosting": lambda: HistGradientBoostingClassifier(max_iter=300, learning_rate=0.1,
                                                                     random_state=RANDOM_STATE),
}


def train_full_models(tr, te):
    X_tr, X_te = tr[ITEM_COLS], te[ITEM_COLS]
    y_tr, y_te = tr[TARGETS], te[TARGETS]
    results = []
    for name, make in CANDIDATES.items():
        with mlflow.start_run(run_name=f"full42_{name}") as run:
            model = MultiOutputClassifier(make()).fit(X_tr, y_tr)
            pred = model.predict(X_te)
            metrics = evaluate(y_te, pred)
            mlflow.set_tags({"eksperimen": "model_lengkap_42_item", "algoritma": name})
            mlflow.log_params({"algoritma": name, "jumlah_item": 42, "n_train": len(X_tr), "n_test": len(X_te)})
            mlflow.log_metrics(metrics)
            sig = infer_signature(X_te.head(5), pred[:5])
            log_sklearn_model(model, name="model", signature=sig, input_example=X_te.head(2))
            results.append({"algoritma": name, "run_id": run.info.run_id, "model": model, **metrics})
            print(f"  {name:24s} akurasi rata2={metrics['akurasi_rata2']:.4f}  f1 makro={metrics['f1_makro_rata2']:.4f}")
    return results


def item_reduction(tr, te, ks=(2, 3, 5, 7, 10, 14)):
    """Seberapa akurat tingkat tiap skala bisa ditebak dari sedikit item? (temuan pendukung)"""
    summary = {}
    for scale, items in SCALES.items():
        target = f"tingkat_{scale}"
        rf = RandomForestClassifier(n_estimators=300, n_jobs=-1, random_state=RANDOM_STATE)
        rf.fit(tr[ITEM_COLS], tr[target])
        ranking = [ITEM_COLS[i] for i in np.argsort(rf.feature_importances_)[::-1]]
        summary[scale] = {"urutan_item_terpenting": ranking[:14], "hasil": []}
        for k in ks:
            feats = ranking[:k]
            with mlflow.start_run(run_name=f"reduksi_{scale}_top{k}"):
                clf = LogisticRegression(max_iter=3000).fit(tr[feats], tr[target])
                pred = clf.predict(te[feats])
                acc = accuracy_score(te[target], pred)
                f1 = f1_score(te[target], pred, average="macro")
                within1 = float(np.mean(np.abs(te[target].to_numpy() - pred) <= 1))
                own = sum(1 for f in feats if int(f[1:]) in items)
                mlflow.set_tags({"eksperimen": "pengurangan_item", "skala": scale})
                mlflow.log_params({"skala": scale, "jumlah_item": k, "item": ",".join(feats),
                                   "item_milik_skala_sendiri": own})
                mlflow.log_metrics({"akurasi": acc, "f1_makro": f1, "selisih_maks_1_tingkat": within1})
                summary[scale]["hasil"].append({"k": k, "akurasi": round(acc, 4), "f1_makro": round(f1, 4),
                                               "selisih_maks_1_tingkat": round(within1, 4),
                                               "item_milik_skala_sendiri": own})
        print(f"  reduksi {scale:10s}: " + ", ".join(f"k={r['k']}→{r['akurasi']:.3f}" for r in summary[scale]["hasil"]))
    return summary


def main():
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    use_experiment(MLFLOW_EXPERIMENT_CLF)
    tr, te = load()
    print("Model lengkap (42 item):")
    results = train_full_models(tr, te)
    best = max(results, key=lambda r: (r["f1_makro_rata2"], r["akurasi_rata2"]))
    print(f"Terbaik: {best['algoritma']}")

    mv = mlflow.register_model(f"runs:/{best['run_id']}/model", REGISTERED_CLF)
    client = mlflow.MlflowClient()
    client.set_registered_model_alias(REGISTERED_CLF, "champion", mv.version)

    print("Eksperimen pengurangan item:")
    reduction = item_reduction(tr, te)

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
        "pengurangan_item": reduction,
    }
    (MODELS_DIR / "classifier_meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return meta


if __name__ == "__main__":
    main()
