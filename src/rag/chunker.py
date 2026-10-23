"""Ubah file knowledge/*.md menjadi potongan teks (chunk) bermetadata.

Format file yang dikenali:
  # Judul dokumen
  Sumber: <url>          (opsional)
  ## Nama bagian
  *(hal. N)*             (opsional, penanda halaman)
  teks...

File yang namanya diawali "_" (mis. pesan krisis) TIDAK diindeks.
Bagian bernama "Sumber" juga tidak diindeks.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

TARGET_WORDS = 170
MIN_WORDS = 25

LANG_HINT = {"who_depresi": "en", "who_kecemasan": "en"}


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    title: str
    section: str
    pages: list[int] = field(default_factory=list)
    url: str | None = None
    lang: str = "id"
    text: str = ""

    def citation(self) -> str:
        hal = ""
        if self.pages:
            hal = f", hal. {self.pages[0]}" if len(self.pages) == 1 else f", hal. {self.pages[0]}–{self.pages[-1]}"
        return f"{self.title} — {self.section}{hal}"


def _units(path: Path):
    """Kembalikan (meta, list[(section, page, paragraph)])."""
    title, url, section, page = path.stem, None, None, None
    units = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("# "):
            title = line[2:].strip()
            continue
        m = re.match(r"Sumber:\s*(\S+)", line)
        if m and section is None:
            url = m.group(1)
            continue
        if line.startswith("Tanggal:") and section is None:
            continue
        if line.startswith("## "):
            section, page = line[3:].strip(), None
            continue
        m = re.fullmatch(r"\*\(hal\. (\d+)\)\*", line)
        if m:
            page = int(m.group(1))
            continue
        if section is None or section.lower() == "sumber":
            continue
        units.append((section, page, line))
    return {"title": title, "url": url}, units


def _split_long(text: str, limit: int) -> list[str]:
    sents = re.split(r"(?<=[.!?])\s+", text)
    out, cur = [], []
    for s in sents:
        if cur and len(" ".join(cur + [s]).split()) > limit:
            out.append(" ".join(cur))
            cur = [cur[-1]]          # tumpang-tindih satu kalimat
        cur.append(s)
    if cur:
        out.append(" ".join(cur))
    return out


def chunk_file(path: Path) -> list[Chunk]:
    meta, units = _units(path)
    doc_id = path.stem
    chunks: list[Chunk] = []
    buf, buf_pages, buf_sec = [], [], None

    def flush():
        nonlocal buf, buf_pages
        if not buf:
            return
        text = "\n".join(buf).strip()
        pieces = _split_long(text, TARGET_WORDS + 60) if len(text.split()) > TARGET_WORDS + 60 else [text]
        for piece in pieces:
            chunks.append(Chunk(chunk_id=f"{doc_id}#{len(chunks)}", doc_id=doc_id, title=meta["title"],
                                section=buf_sec, pages=sorted(set(p for p in buf_pages if p is not None)),
                                url=meta["url"], lang=LANG_HINT.get(doc_id, "id"), text=piece))
        buf, buf_pages = [], []

    for sec, page, para in units:
        if sec != buf_sec:
            flush()
            buf_sec = sec
        if buf and len(" ".join(buf).split()) + len(para.split()) > TARGET_WORDS:
            flush()
        buf.append(para)
        buf_pages.append(page)
    flush()

    # gabungkan potongan yang terlalu pendek dengan tetangganya di bagian yang sama
    merged: list[Chunk] = []
    for c in chunks:
        if merged and merged[-1].section == c.section and len(c.text.split()) < MIN_WORDS:
            merged[-1].text += "\n" + c.text
            merged[-1].pages = sorted(set(merged[-1].pages + c.pages))
        else:
            merged.append(c)
    for i, c in enumerate(merged):
        c.chunk_id = f"{doc_id}#{i}"
    return merged


def load_chunks(knowledge_dir: Path) -> list[Chunk]:
    out = []
    for p in sorted(knowledge_dir.glob("*.md")):
        if p.name.startswith("_"):
            continue
        out.extend(chunk_file(p))
    return out
