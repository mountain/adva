#!/usr/bin/env python3
"""Minimal pure-Python text -> PDF converter (container only).

Wraps a plain-text document into a single-font (Helvetica/WinAnsi) PDF.
Used for the unrelated-pair gate test so both objects have the same
container discipline; the TEXT is the public-domain original.
"""
import sys

def esc(s):
    return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")

def winansi(s):
    out = []
    for ch in s:
        o = ord(ch)
        if o < 128 or (160 <= o < 256):
            out.append(chr(o))
        else:
            out.append("?")
    return "".join(out)

def main(src, dst, lines_per_page=46):
    lines = open(src, encoding="utf-8", errors="replace").read().splitlines()
    # skip the PG boilerplate envelope
    body = []
    for ln in lines:
        if "*** START OF" in ln:
            body = []
            continue
        if "*** END OF" in ln:
            break
        body.append(winansi(ln.rstrip()))
    pages = [body[i:i + lines_per_page]
             for i in range(0, len(body), lines_per_page)]
    objs = []
    # object 1: catalog
    objs.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    # object 2: pages
    kids = " ".join(f"{3 + 2*i} 0 R" for i in range(len(pages)))
    objs.append(f"<< /Type /Pages /Count {len(pages)} /Kids [ {kids} ] >>".encode())
    # page objects + content streams
    for i, page in enumerate(pages):
        y = 720.0
        ops = ["BT /F1 11 Tf 12 TL 72 720 Td"]
        for ln in page:
            ops.append(f"({esc(ln)}) Tj T*")
        ops.append("ET")
        stream = "\n".join(ops).encode()
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    f"/Resources << /Font << /F1 {3 + 2*len(pages)} 0 R >> >> "
                    f"/Contents {4 + 2*i} 0 R >>".encode())
        objs.append(f"<< /Length {len(stream)} >>\nstream\n".encode()
                    + stream + b"\nendstream")
    # font object
    objs.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica "
                b"/Encoding /WinAnsiEncoding >>")
    out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + o + b"\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs)+1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets[1:]:
        out += f"{off:010d} 00000 n \n".encode()
    out += (f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n").encode()
    open(dst, "wb").write(out)
    print(f"wrote {dst}: {len(pages)} pages from {len(body)} lines")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
