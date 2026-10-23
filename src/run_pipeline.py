"""Jalankan seluruh pipeline: data -> klasifikasi -> clustering (semua run tercatat di MLflow).

Pemakaian:  python -m src.run_pipeline
"""
import os
import time

os.environ.setdefault("MLFLOW_DISABLE_AGENT_HINT", "1")

from src.data import pipeline  # noqa: E402
from src.ml import train_classifier, train_cluster  # noqa: E402


def main():
    t0 = time.time()
    print("== 1/3 Pipeline data ==")
    rep = pipeline.run()
    print(f"   {rep['baris_bersih']} baris bersih ({rep['baris_train']} latih / {rep['baris_test']} uji)")
    print("== 2/3 Model klasifikasi ==")
    train_classifier.main()
    print("== 3/3 Model clustering ==")
    train_cluster.main()
    print(f"Selesai dalam {time.time() - t0:.0f} detik. Lihat hasil: mlflow ui --backend-store-uri sqlite:///mlflow.db")


if __name__ == "__main__":
    main()
