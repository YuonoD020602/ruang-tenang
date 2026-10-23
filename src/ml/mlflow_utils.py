"""Bantuan MLflow: simpan model sklearn buatan sendiri dengan format skops.

MLflow versi baru menolak menyimpan model pohon (RandomForest, dll.) kecuali tipe internalnya
dinyatakan tepercaya. Model di proyek ini kita latih sendiri, jadi tipe sklearn yang
dilaporkan skops aman dipercaya. Fungsi milik proyek ini (modul src.*) juga dipercaya. Tipe lain tetap ditolak.
"""
import mlflow.sklearn
from skops.io import dumps, get_untrusted_types


def log_sklearn_model(model, **kwargs):
    untrusted = get_untrusted_types(data=dumps(model))
    foreign = [t for t in untrusted if not t.startswith(("sklearn.", "src."))]
    if foreign:
        raise ValueError(f"Tipe di luar sklearn tidak dipercaya otomatis: {foreign}")
    return mlflow.sklearn.log_model(model, skops_trusted_types=untrusted or None, **kwargs)


def use_experiment(name: str):
    """Pilih eksperimen MLflow; jika baru dan MLFLOW_ARTIFACT_ROOT di-set, simpan artefak di sana.

    Berguna di Docker supaya artefak model ikut tersimpan di volume yang sama dengan database MLflow.
    """
    import os

    import mlflow

    root = os.getenv("MLFLOW_ARTIFACT_ROOT")
    if root and mlflow.get_experiment_by_name(name) is None:
        mlflow.create_experiment(name, artifact_location=root.rstrip("/") + "/" + name)
    return mlflow.set_experiment(name)
