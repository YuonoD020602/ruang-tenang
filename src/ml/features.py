"""Fitur turunan yang dipakai di pipeline model (harus berada di modul agar bisa diserialisasi)."""
import numpy as np


def row_center(X):
    """Kurangi tiap baris dengan rata-rata barisnya.

    Setelah skor tiga skala distandarkan, langkah ini menghapus "tinggi-rendah keseluruhan"
    dan menyisakan BENTUK profil: skala mana yang relatif lebih tinggi atau lebih rendah
    dibanding dua skala lainnya pada orang yang sama.
    """
    X = np.asarray(X, dtype=float)
    return X - X.mean(axis=1, keepdims=True)
