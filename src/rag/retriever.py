"""Retrieval BM25 dengan perluasan kueri Indonesia -> Inggris.

Dua fact sheet WHO berbahasa Inggris, sedangkan pertanyaan pengguna berbahasa Indonesia.
BM25 hanya mencocokkan kata, jadi kueri diperluas dengan padanan Inggris dari glosarium kecil
di bawah. Cara ini ringan, tanpa unduhan model, dan mudah diaudit.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from rank_bm25 import BM25Okapi

from src.rag.chunker import Chunk

STOPWORDS = set("""
yang dan di ke dari ini itu untuk dengan pada adalah atau juga tidak bisa akan ada saya aku kamu anda kita kami
mereka apa bagaimana kenapa mengapa apakah kapan siapa dalam sebagai oleh karena jika kalau agar supaya sudah
belum masih sangat lebih paling tentang seperti banyak sedang bila maka tapi tetapi namun hal cara bagi para
gimana gmn sih dong ya nya kah lah pun jadi buat sama aja saja the a an and or of to in for on with is are be
was were it this that as by at from can may have has had not do does what how why when which who your you i
""".split())

# Glosarium perluasan kueri (kata dasar Indonesia -> kata Inggris di fact sheet WHO)
GLOSSARY = {
    "depresi": "depression depressive", "depresif": "depression depressive",
    "cemas": "anxiety anxious", "kecemasan": "anxiety anxious", "ansietas": "anxiety",
    "gangguan": "disorder disorders", "gejala": "symptoms symptom", "tanda": "symptoms signs",
    "penyebab": "contributing factors causes", "faktor": "factors", "risiko": "risk factors",
    "pencegahan": "prevention prevent", "mencegah": "prevention prevent",
    "pengobatan": "treatment treatments", "penanganan": "treatment treatments", "terapi": "therapy treatment",
    "perawatan": "treatment care", "diagnosis": "diagnosis", "konseling": "counselling talk therapy",
    "psikolog": "psychological professionals", "psikologis": "psychological",
    "tidur": "sleep sleeping", "makan": "eating appetite", "nafsu": "appetite", "olahraga": "exercise",
    "alkohol": "alcohol", "sedih": "sad depressed mood", "lelah": "tired energy", "capek": "tired energy",
    "panik": "panic", "serangan": "attacks", "fobia": "phobias phobia", "sosial": "social",
    "khawatir": "worry fear", "takut": "fear", "konsentrasi": "concentration concentrating",
    "fokus": "concentration", "perempuan": "women", "wanita": "women", "laki": "men", "pria": "men",
    "anak": "children adolescents", "remaja": "adolescents", "lansia": "older adults",
    "global": "globally world", "dunia": "world globally", "prevalensi": "estimated percent population",
    "berapa": "estimated", "bunuh": "suicide", "rawat": "self-care care", "mandiri": "self-care",
    "dukungan": "support", "keluarga": "family friends", "teman": "friends", "bipolar": "bipolar",
    "episode": "episode episodes", "berulang": "recurrent", "relaksasi": "relaxation", "napas": "breathing",
    "who": "who response", "sendiri": "self-care", "mengatasi": "manage self-care",
    "mengelola": "manage managing self-care", "menenangkan": "relaxation calm", "tenang": "relaxation calm",
}

# kata glosarium yang terlalu umum untuk menandai topik (tetap dipakai untuk perluasan kueri)
GENERIC_WORDS = {"berapa", "global", "dunia", "who", "anak", "remaja", "lansia", "perempuan", "wanita", "laki",
                 "pria", "keluarga", "teman", "makan", "tidur", "alkohol", "olahraga", "sendiri", "dukungan",
                 "sosial", "faktor", "serangan", "episode", "nafsu", "tanda", "risiko", "berulang", "mandiri",
                 "rawat", "prevalensi", "mengatasi", "mengelola", "tenang", "fokus", "konsentrasi", "napas"}

DOMAIN_WORDS = (set(GLOSSARY) - GENERIC_WORDS) | {
    "stres", "stress", "dass", "phq", "gad", "skrining", "skor", "skala", "tingkat", "hasil", "profil", "klaster", "kuesioner",
    "grounding", "melepaskan", "nilai", "emosi", "perasaan", "pikiran", "mental", "jiwa", "kesehatan",
    "tenang", "menenangkan", "rileks", "gelisah", "tegang", "marah", "kesal", "menangis", "kesepian",
    "skrining", "normal", "ringan", "berat", "item", "pernyataan", "badai", "terpancing", "baik",
    "psikiater", "bantuan", "menghadapi", "mengelola", "mengatasi", "latihan", "ruang",
}


def _strip_particles(tok: str) -> str:
    for suf in ("nya", "lah", "kah"):
        if tok.endswith(suf) and len(tok) > len(suf) + 3:
            return tok[: -len(suf)]
    return tok


PREFIXES = ("meng", "meny", "mem", "men", "me", "peng", "peny", "pem", "pen", "per", "pe",
            "ber", "ter", "di", "ke", "se")
SUFFIXES = ("kan", "an", "i")


def light_stem(tok: str) -> str:
    """Stemmer Indonesia sederhana (buang satu awalan & satu akhiran umum).

    Tidak sempurna, tapi cukup supaya "menenangkan" bertemu "tenang" atau "kecemasan" bertemu
    "cemas". Hasilnya dipakai sebagai token TAMBAHAN, kata aslinya tetap disimpan.
    """
    t = tok
    for suf in SUFFIXES:
        if t.endswith(suf) and len(t) - len(suf) >= 4:
            t = t[: -len(suf)]
            break
    for pre in PREFIXES:
        if t.startswith(pre) and len(t) - len(pre) >= 4:
            t = t[len(pre):]
            break
    return t


def tokenize(text: str) -> list[str]:
    toks = re.findall(r"[a-zA-ZÀ-ÿ]+", text.lower())
    out = []
    for t in toks:
        if t in STOPWORDS or len(t) <= 1:
            continue
        t = _strip_particles(t)
        out.append(t)
        st = light_stem(t)
        if st != t:
            out.append(st)
    return out


def expand(tokens: list[str]) -> list[str]:
    out = list(tokens)
    for t in tokens:
        if t in GLOSSARY:
            out.extend(re.findall(r"[a-z]+", GLOSSARY[t]))
    return out


@dataclass
class Hit:
    chunk: Chunk
    score: float


class Retriever:
    def __init__(self, chunks: list[Chunk]):
        self.chunks = chunks
        self.bm25 = BM25Okapi([tokenize(c.title + " " + c.section + " " + c.text) for c in chunks])

    def search(self, query: str, k: int = 4, prefer_doc: str | None = None) -> list[Hit]:
        q = expand(tokenize(query))
        if not q:
            return []
        scores = self.bm25.get_scores(q)
        if prefer_doc:
            scores = [s * 1.25 if c.doc_id == prefer_doc else s for s, c in zip(scores, self.chunks)]
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [Hit(self.chunks[i], float(scores[i])) for i in order if scores[i] > 0]

    @staticmethod
    def domain_overlap(query: str) -> int:
        toks = re.findall(r"[a-zA-ZÀ-ÿ]+", query.lower())
        return sum(1 for t in toks if _strip_particles(t) in DOMAIN_WORDS or light_stem(_strip_particles(t)) in DOMAIN_WORDS)
