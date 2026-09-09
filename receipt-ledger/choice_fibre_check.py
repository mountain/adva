"""ChoiceWitness + FibreAccount validator (retention-declaration discipline)."""
import hashlib, json, pathlib

ROOT = pathlib.Path('/Users/mingli/Adva/AEG')
ADVA = pathlib.Path('/Users/mingli/Adva/adva')
DOC = ROOT/'trials/receipt-ledger/choices-and-fibres.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def resolve(retention):
    p = ROOT/retention if (ROOT/retention).exists() else ADVA/retention
    return p if p.exists() else None

def main():
    doc = json.loads(DOC.read_text(encoding='utf-8'))
    findings = []
    for c in doc['choices']:
        if not isinstance(c.get('name'), str) or not c['name']:
            findings.append("selection needs a named witness")
        retained = c.get('retained') or []
        if not retained:
            findings.append(f"choice {c['name']}: empty retained set (silent drop)")
        selected = c.get('selected', {})
        if selected.get('payload_sha256'):
            hit = any(r.get('payload_sha256') == selected['payload_sha256'] for r in retained)
            if not hit:
                findings.append(f"choice {c['name']}: selected payload not in retained set")
        for r in retained:
            if r.get('payload_sha256') and r.get('retention'):
                p = resolve(r['retention'])
                if p is None:
                    findings.append(f"choice {c['name']}: retained payload location missing: {r['retention']}")
                elif sha(p) != r['payload_sha256']:
                    findings.append(f"choice {c['name']}: retained payload pin mismatch: {r['retention']}")
    fs = doc.get('fibres') or []
    nums = [f['receipt'] for f in fs]
    if sorted(nums) != list(range(1, 18)):
        findings.append(f"fibre coverage violation: {sorted(nums)}")
    for f in fs:
        if f.get('fibre_status') not in ('discharged', 'empty', 'unknown'):
            findings.append(f"receipt-{f['receipt']:02d}: bad fibre status")
    status = 'ChoiceFibreConsistent' if not findings else 'Rejected'
    report = {"schema": "aeg.choice-fibre-ledger.check.research", "version": 0,
              "status": status, "findings": findings,
              "choices": len(doc['choices']), "fibres": len(fs)}
    (ROOT/'trials/receipt-ledger/choice-fibre-report.json').write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
