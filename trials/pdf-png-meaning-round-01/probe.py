#!/usr/bin/env python3
"""pdf-png meaning probe, round 01.

Objects: the 14 PNG files rendered by pdftoppm between the two PDFs in the
mingli home path:
  /Users/mingli/BP001(8).pdf            (strategy, 10 pages, 1920x1080 pts)
  /Users/mingli/NeoLab - TrustBase(1).pdf (pitch, 14 pages, 959.76x540 pts)
  /Users/mingli/slide-01.png .. slide-14.png (raster renderings, 150 dpi)

Probe: parse each PNG IHDR (width, height, bit depth, color type) without any
image library, pin each file with SHA-256, and compare the pixel layer against
the text layer (trustbase-full.txt page word counts).
"""
import hashlib
import json
import os
import re
import struct
import statistics
import sys

HOME = os.path.expanduser("~")
AEG = os.path.join(HOME, "Adva", "AEG")
EVIDENCE = os.path.join(AEG, "trials", "binary-relation-round-01", "evidence-pdf-01")
OUT = os.path.join(AEG, "trials", "pdf-png-meaning-round-01")

TRUSTBASE_PDF = os.path.join(HOME, "NeoLab - TrustBase(1).pdf")
BP001_PDF = os.path.join(HOME, "BP001(8).pdf")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def png_header(path):
    """Return (width, height, bitdepth, colortype) from the IHDR chunk."""
    with open(path, "rb") as f:
        sig = f.read(8)
        assert sig == b"\x89PNG\r\n\x1a\n", "not a PNG"
        ln, name = struct.unpack(">I4s", f.read(8))
        assert name == b"IHDR", "IHDR not first"
        assert ln == 13, "bad IHDR length"
        w, h, bd, ct, _cm, _fl, _il = struct.unpack(">IIBBBBB", f.read(13))
    return w, h, bd, ct


def page_word_counts():
    raw = open(os.path.join(EVIDENCE, "trustbase-full.txt")).read()
    pages = [p for p in raw.split("\x0c") if p.strip()]
    return [len(re.findall(r"[A-Za-z0-9]+", p)) for p in pages]


def pearson(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx == 0 or vy == 0:
        return None
    return cov / ((vx * vy) ** 0.5)


def main():
    pngs = sorted(
        p for p in os.listdir(HOME) if re.match(r"slide-\d{2}\.png$", p)
    )
    slides = []
    for name in pngs:
        path = os.path.join(HOME, name)
        w, h, bd, ct = png_header(path)
        st = os.stat(path)
        slides.append({
            "file": name,
            "path": path,
            "width": w,
            "height": h,
            "bit_depth": bd,
            "color_type": ct,
            "bytes": st.st_size,
            "mtime_iso": None,
            "sha256": sha256_file(path),
        })
    words = page_word_counts()
    report = {
        "schema": "aeg.pdf-png.probe",
        "inputs": {
            "strategy_pdf": BP001_PDF,
            "pitch_pdf": TRUSTBASE_PDF,
            "pitch_pdf_sha256": sha256_file(TRUSTBASE_PDF),
            "strategy_pdf_sha256": sha256_file(BP001_PDF),
            "pitch_pdf_pages": 14,
            "strategy_pdf_pages": 10,
            "pitch_page_pts": "959.76 x 540",
        },
        "slides": slides,
        "text_layer": {
            "pages": len(words),
            "words_per_page": words,
        },
        "checks": {},
        "correlation": None,
    }
    widths = {s["width"] for s in slides}
    heights = {s["height"] for s in slides}
    depths = {s["bit_depth"] for s in slides}
    colors = {s["color_type"] for s in slides}
    report["checks"]["count_equals_pitch_pages"] = len(slides) == 14
    report["checks"]["uniform_geometry"] = (len(widths) == 1 and len(heights) == 1)
    report["checks"]["aspect_16_by_9"] = all(
        abs(s["width"] / s["height"] - 16 / 9) < 0.01 for s in slides
    )
    report["checks"]["widths"] = sorted(widths)
    report["checks"]["heights"] = sorted(heights)
    report["checks"]["bit_depths"] = sorted(depths)
    report["checks"]["color_types"] = sorted(colors)
    report["checks"]["all_pinned"] = all(s["sha256"] for s in slides)
    sizes = [s["bytes"] for s in slides]
    if len(words) == len(slides):
        r = pearson(words, sizes)
        report["correlation"] = {
            "pair": "text_words_per_page vs png_bytes_per_slide",
            "pearson": round(r, 4) if r is not None else None,
            "words_total": sum(words),
            "bytes_total": sum(sizes),
            "words_per_kb": round(sum(words) / (sum(sizes) / 1024), 3),
        }
    report["slides_by_bytes"] = sorted(
        [{"file": s["file"], "bytes": s["bytes"], "words": words[i]}
         for i, s in enumerate(slides)],
        key=lambda d: d["bytes"],
    )
    out = os.path.join(OUT, "probe.json")
    with open(out, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("wrote", out)
    print("checks:", json.dumps(report["checks"], ensure_ascii=False))
    print("correlation:", json.dumps(report["correlation"], ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())
