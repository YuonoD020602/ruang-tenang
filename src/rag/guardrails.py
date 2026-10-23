"""Pengaman chatbot: deteksi krisis, pertanyaan obat, permintaan diagnosis, dan upaya mengubah aturan.

Semua pengecekan memakai pola teks sederhana yang mudah diaudit. Prinsipnya: lebih baik
terlalu sensitif (menampilkan info bantuan saat tidak perlu) daripada melewatkan krisis.
"""
from __future__ import annotations

import re
from functools import lru_cache

from src.config import KNOWLEDGE_DIR

_CRISIS = [
    r"bunuh\s*diri", r"\bsuicid", r"kill\s+my\s*self", r"end\s+my\s+life", r"self[\s-]*harm",
    r"(ingin|mau|pengen|pingin|kepengen|rasanya\s+mau|lebih\s+baik)\s+mati",
    r"(akhiri|mengakhiri|menyudahi)\s+(hidup|nyawa)", r"(tidak|gak|ga|nggak|enggak)\s+(mau|ingin|pengen)\s+hidup",
    r"(menyakiti|melukai|nyakitin|lukai|sakiti)\s+(diri|badan)", r"\bmenyayat\b|\bsayat\b",
    r"hidup\s+(tidak|gak|ga|nggak)\s+(ada\s+)?(gunanya|artinya|berarti)", r"tidak\s+ingin\s+bangun\s+lagi",
]
_MEDICATION = [
    r"\bobat\b", r"\bdosis\b", r"resep\s+(obat|dokter|psikiater)", r"antidepres", r"\bssri\b", r"fluoxetine|sertraline|escitalopram",
    r"benzodiazepin|alprazolam|diazepam|clonazepam|xanax", r"\bpil\b", r"\btablet\b", r"\bmg\b",
    r"\bmedication|\bmedicine|\bdrug",
]
_DIAGNOSIS = [
    r"apa(kah)?\s+(saya|aku|dia|orang\s+ini|responden(\s+ini)?)\s+(\w+\s+)?(depresi|cemas|gangguan|sakit\s+jiwa|stres)",
    r"(saya|aku)\s+(kena|punya|mengidap|menderita)\s+(depresi|gangguan|kecemasan|anxiety)",
    r"diagnos",
]
_INJECTION = [
    r"abaikan\s+(semua\s+)?(instruksi|aturan|perintah)", r"ignore\s+(all\s+)?(previous|prior|the)?\s*(instructions|rules)",
    r"system\s*prompt", r"prompt\s+sistem", r"lupakan\s+(semua\s+)?(aturan|instruksi)",
    r"(berpura|pura)-?\s*pura\s+(jadi|menjadi)", r"jailbreak", r"mode\s+developer|developer\s+mode",
    r"tanpa\s+(aturan|batasan|filter)",
]


def _any(patterns, text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in patterns)


def is_crisis(text: str) -> bool:
    return _any(_CRISIS, text)


def asks_medication(text: str) -> bool:
    return _any(_MEDICATION, text)


def asks_diagnosis(text: str) -> bool:
    return _any(_DIAGNOSIS, text)


def is_injection(text: str) -> bool:
    return _any(_INJECTION, text)


def mentions_medication(text: str) -> bool:
    """Dipakai untuk menyaring JAWABAN LLM (jaring pengaman terakhir)."""
    return bool(re.search(r"antidepres|ssri|serotonin|fluoxetine|sertraline|escitalopram|benzodiazepin|"
                          r"alprazolam|diazepam|clonazepam|xanax|\bdosis\b|\bmg\b", text.lower()))


@lru_cache(maxsize=1)
def crisis_message() -> str:
    """Ambil teks baku dari knowledge/_pesan_krisis.md (bagian 'Teks yang ditampilkan ke pengguna')."""
    raw = (KNOWLEDGE_DIR / "_pesan_krisis.md").read_text(encoding="utf-8")
    m = re.search(r"## Teks yang ditampilkan ke pengguna\s*(.*?)\n---", raw, flags=re.S)
    return m.group(1).strip() if m else raw


HELP_BANNER = ("Butuh teman bicara? Healing119.id — telepon 119 ekstensi 8 (gratis, 24 jam). "
               "Darurat: 119 atau IGD terdekat.")

MEDICATION_REPLY = (
    "Maaf, aku tidak membahas obat, termasuk nama obat, dosis, atau efek sampingnya. "
    "Keputusan tentang obat hanya boleh diambil bersama dokter atau psikiater yang memeriksamu langsung.\n\n"
    "Yang bisa aku bantu: menjelaskan gejala depresi, kecemasan, dan stres; arti hasil skrining DASS-42; "
    "dan cara-cara mengelola stres dari panduan WHO."
)

INJECTION_REPLY = (
    "Aku tetap mengikuti aturan yang sama: menjawab hanya dari dokumen sumber, tidak mendiagnosis, "
    "dan tidak membahas obat. Silakan tanyakan hal tentang depresi, kecemasan, stres, atau hasil DASS-42."
)

OUT_OF_SCOPE_REPLY = (
    "Maaf, pertanyaan itu di luar cakupanku. Aku hanya bisa menjawab tentang depresi, kecemasan, stres, "
    "hasil skrining DASS-42, dan cara mengelola stres berdasarkan panduan WHO."
)

DIAGNOSIS_NOTE = (
    "Catatan: aku tidak bisa menentukan apakah seseorang memiliki gangguan tertentu. DASS-42 adalah alat "
    "skrining; untuk kepastian, bicarakan dengan psikolog atau dokter."
)
