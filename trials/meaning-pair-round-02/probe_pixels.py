#!/usr/bin/env python3
"""Pixel-layer probe: ink fraction per page, pure Python (zlib + PNG filters).

Measures, per rendered page: dimensions, color type, byte size, and the
fraction of non-white pixels (ink). White = all channels >= 240.
Supports color types 0 (gray), 2 (RGB), 3 (palette, first PLTE entry only
approximated), 4 (gray+alpha), 6 (RGBA).
"""
import json
import pathlib
import struct
import sys
import zlib

ROUND = pathlib.Path("/Users/mingli/Adva/AEG/trials/meaning-pair-round-02")


def parse_png(path):
    raw = pathlib.Path(path).read_bytes()
    assert raw[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos, chunks, idat = 8, {}, b""
    while pos < len(raw):
        ln, name = struct.unpack(">I4s", raw[pos:pos + 8])
        data = raw[pos + 8:pos + 8 + ln]
        pos += 12 + ln
        if name == b"IHDR":
            w, h, bd, ct = struct.unpack(">IIBB", data[:10])
            chunks["IHDR"] = (w, h, bd, ct)
        elif name == b"PLTE":
            chunks["PLTE"] = data
        elif name == b"IDAT":
            idat += data
        elif name == b"IEND":
            break
    w, h, bd, ct = chunks["IHDR"]
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[ct]
    stride = w * ch
    decomp = zlib.decompress(idat)
    rows, prev, i = [], None, 0
    for y in range(h):
        f = decomp[i]
        line = bytearray(decomp[i + 1:i + 1 + stride])
        i += 1 + stride
        if f == 1:
            for x in range(ch, stride):
                line[x] = (line[x] + line[x - ch]) & 0xFF
        elif f == 2 and prev is not None:
            for x in range(stride):
                line[x] = (line[x] + prev[x]) & 0xFF
        elif f == 3 and prev is not None:
            for x in range(stride):
                a = line[x - ch] if x >= ch else 0
                line[x] = (line[x] + ((a + prev[x]) >> 1)) & 0xFF
        elif f == 4 and prev is not None:
            for x in range(stride):
                a = line[x - ch] if x >= ch else 0
                b = prev[x]
                c = prev[x - ch] if x >= ch else 0
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pr) & 0xFF
        rows.append(bytes(line))
        prev = line
    return w, h, bd, ct, rows


def ink_fraction(w, h, ct, rows):
    if ct == 3:
        return None  # palette approximation not attempted
    ch = {0: 1, 2: 3, 4: 2, 6: 4}[ct]
    ink = total = 0
    for row in rows:
        for x in range(0, len(row), ch):
            px = row[x:x + ch]
            white = all(v >= 240 for v in px[:3])
            if not white:
                ink += 1
            total += 1
    return round(ink / total, 6)


def words_per_page(txt):
    pages = [p for p in txt.split("\x0c") if p.strip()]
    out = []
    for p in pages:
        out.append(len(__import__("re").findall(r"[A-Za-z0-9]+", p)))
    return out


def main():
    report = {"schema": "aeg.pixel-probe", "version": 0, "docs": {}}
    for name, prefix, txt in (("gpt4", "gpt4-", "a-full.txt"),
                              ("alpha", "alpha-", "b-full.txt")):
        pngs = sorted(ROUND.glob(f"pixels/{prefix}*.png"),
                      key=lambda p: int(p.stem.rsplit("-", 1)[1]))
        pages = []
        for p in pngs:
            w, h, bd, ct, rows = parse_png(p)
            pages.append({
                "page": int(p.stem.rsplit("-", 1)[1]),
                "bytes": p.stat().st_size,
                "width": w, "height": h, "bit_depth": bd, "color_type": ct,
                "ink": ink_fraction(w, h, ct, rows),
            })
        texts = words_per_page((ROUND / txt).read_text())
        sizes = [p["bytes"] for p in pages]
        inks = [p["ink"] for p in pages if p["ink"] is not None]
        n = min(len(texts), len(sizes))
        import statistics
        mx, my = sum(texts[:n]) / n, sum(sizes[:n]) / n
        cov = sum((x - mx) * (y - my) for x, y in zip(texts[:n], sizes[:n]))
        vx = sum((x - mx) ** 2 for x in texts[:n])
        vy = sum((y - my) ** 2 for y in sizes[:n])
        r = cov / ((vx * vy) ** 0.5) if vx and vy else None
        report["docs"][name] = {
            "page_count": len(pages),
            "total_bytes": sum(sizes),
            "mean_bytes_per_page": round(sum(sizes) / len(sizes)),
            "mean_ink": round(statistics.mean(inks), 6) if inks else None,
            "max_ink_page": max(pages, key=lambda p: p["ink"] or 0)["page"],
            "words_total": sum(texts),
            "words_per_page": round(sum(texts) / len(texts), 2),
            "bytes_per_word": round(sum(sizes) / sum(texts), 3),
            "pearson_words_bytes": round(r, 4) if r is not None else None,
            "top5_heaviest_pages": sorted(pages, key=lambda p: -p["bytes"])[:5],
            "pages": pages,
        }
    out = ROUND / "pixel-probe.json"
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    for name in ("gpt4", "alpha"):
        d = report["docs"][name]
        print(f"{name}: pages={d['page_count']} bytes/page={d['mean_bytes_per_page']} "
              f"ink={d['mean_ink']} words/page={d['words_per_page']} "
              f"bytes/word={d['bytes_per_word']} r(words,bytes)={d['pearson_words_bytes']}")
        print("   heaviest pages:", [(p["page"], p["bytes"]) for p in d["top5_heaviest_pages"]])


if __name__ == "__main__":
    sys.exit(main())
