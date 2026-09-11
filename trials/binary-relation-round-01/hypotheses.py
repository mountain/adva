"""Hypothesis table with observed evidence; errors/holes are recorded, not hidden."""
import json, pathlib, sys
D = pathlib.Path(sys.argv[1])
pins = (D/'pins.txt').read_text(encoding='utf-8', errors='replace')
ft = (D/'file-types.txt').read_text(encoding='utf-8', errors='replace')
chunks = json.loads((D/'chunks.json').read_text(encoding='utf-8'))
voc = (D/'vocabulary-summary.txt').read_text(encoding='utf-8', errors='replace')
sym = (D/'symbols.txt').read_text(encoding='utf-8', errors='replace')
rows = [
 {"h": "H1 same source family", "check": "shared symbol/string density",
  "observed": f"common strings {voc.splitlines()[-1] if voc else '?'}; symbols {'present' if sym and 'nm failed' not in sym else 'stripped -> hole'}",
  "status": "Unknown"},
 {"h": "H2 one embeds the other", "check": "chunk containment",
  "observed": f"{chunks['common_chunks']} shared 64B chunks of {chunks['size_Q']//64}; hint: {chunks['relation_hint']}",
  "status": "VariationObserved" if chunks["common_chunks"] else "EvidenceStutter"},
 {"h": "H3 one interprets the other", "check": "file types + load commands",
  "observed": ft.splitlines()[:2],
  "status": "Unknown"},
 {"h": "H4 shared function frontier", "check": "both executable + same-input output comparison (manual next round)",
  "observed": "not run this round -> hole (energy for next round)",
  "status": "Unknown"},
]
(D/'hypotheses.json').write_text(json.dumps(rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps({"hypotheses": rows}, indent=2, ensure_ascii=False))
