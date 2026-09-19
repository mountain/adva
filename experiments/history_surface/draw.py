"""Original SVG illustration from retained evidence, under Unknown v0.3.

Authored by Codex (OpenAI), through Mingli Yuan's authorized account proxy.
"""

import json
import math
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent
record = json.loads((ROOT / "evidence/run-01.json").read_text())
example = record["examples"]["surface_rewrite"]
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 650" role="img">',
    '<title>Changing boundary, recoverable history</title>',
    '<desc>Three sampling-site diagrams show an old history, its extension and '
    'one corrupted sample. The old history remains reconstructible.</desc>',
    '<rect width="1200" height="650" rx="18" fill="#f4f7fb"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#20344b}'
    '.title{font-size:29px;font-weight:bold}.sub{font-size:15px;fill:#526478}'
    '.panel{font-size:20px;font-weight:bold}.value{font-size:21px;font-weight:bold}'
    '.site{font-size:12px;fill:#526478}.word{font-size:23px;font-weight:bold}'
    '</style>',
]


def text(x, y, value, css="sub", anchor="middle", fill=None):
    color = f' style="fill:{fill}"' if fill else ""
    parts.append(f'<text x="{x}" y="{y}" class="{css}" text-anchor="{anchor}"'
                 f'{color}>{escape(value)}</text>')


text(35, 46, "Changing boundary, recoverable history", "title", "start")
text(35, 75, "Exact arithmetic over F7. Sampling sites illustrate a code, not a geometric duality.",
     anchor="start")

panels = [
    ("Before", example["before"], "[1, 0, 1]", "#3468ac"),
    ("After appending 1", example["after"], "[1, 0, 1, 1]", "#278164"),
    ("After one sample fault", example["one_fault"], "[1, 0, 1, 1]", "#278164"),
]
for column, (title, surface, history, color) in enumerate(panels):
    left = 25 + column * 390
    cx, cy = left + 185, 290
    parts.append(f'<rect x="{left}" y="105" width="370" height="380" rx="14" '
                 'fill="white" stroke="#d8e1ec"/>')
    text(cx, 145, title, "panel")
    parts.append(f'<circle cx="{cx}" cy="{cy}" r="88" fill="none" '
                 'stroke="#ccd8e7" stroke-width="2"/>')
    count = len(surface["values"])
    for i, (point, value) in enumerate(zip(surface["points"], surface["values"])):
        angle = -math.pi/2 + 2*math.pi*i/count
        x, y = cx + 88*math.cos(angle), cy + 88*math.sin(angle)
        bad = column == 2 and i == 2
        edge = "#c4494b" if bad else color
        bg = "#ffe5e5" if bad else "#ecf3fa"
        parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="23" '
                     f'fill="{bg}" stroke="{edge}" stroke-width="2"/>')
        text(f"{x:.2f}", f"{y+7:.2f}", str(value), "value")
        lx, ly = cx + 125*math.cos(angle), cy + 125*math.sin(angle)
        text(f"{lx:.2f}", f"{ly+4:.2f}", f"s={point}", "site")
    text(cx, cy - 3, f"{count} samples", "sub")
    text(cx, cy + 20, f"{surface['k']} history symbols", "sub")
    text(cx, 443, "Decoded history", "sub")
    text(cx, 473, history, "word", fill=color)

parts.append('<rect x="25" y="510" width="1150" height="88" rx="12" fill="#e3eee9"/>')
text(600, 545, "Old-history readback at every stage: [1, 0, 1]", "word")
text(600, 574, "Every old sample changes on extension. One substituted value is corrected.")
text(25, 627, "Assumptions: intact header and the stated fault bound. Decoding alone does not establish authenticity.",
     anchor="start")
parts.append("</svg>")
target = ROOT / "surface-history.svg"
target.write_text("\n".join(parts) + "\n")
print(target)
