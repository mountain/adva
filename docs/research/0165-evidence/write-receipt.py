"""Receipt 08: interpretation relation between two opaque binaries."""
import hashlib, json, pathlib, sys
D = pathlib.Path(sys.argv[1])
AEG = pathlib.Path('/Users/mingli/Adva/AEG')
pred = (AEG/'trials/advance-receipt-round-01/receipt-07.json').read_bytes()
pins = (D/'pins.txt').read_text(encoding='utf-8', errors='replace')
hyps = json.loads((D/'hypotheses.json').read_text(encoding='utf-8'))
receipt = {
  "schema": "aeg.advance-receipt.research", "version": 0, "round": 8,
  "predecessor_sha256": hashlib.sha256(pred).hexdigest(),
  "delta": {"kind": "resource", "admitted": True,
            "description": "two opaque binaries supplied at OS root; interpretation-relation probing"},
  "status": "VariationObserved" if any(h["status"] == "VariationObserved" for h in hyps) else "Unknown",
  "evidence": {"pins": pins.splitlines()[:6],
               "hypotheses": hyps,
               "holes_policy": "all errors, stripped symbols, unrun checks retained as holes; they are the next round's energy"},
  "bounds": {"read_only": True, "chunk_size": 64}
}
(D/'receipt-08.json').write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print(json.dumps(receipt, indent=2, ensure_ascii=False))
