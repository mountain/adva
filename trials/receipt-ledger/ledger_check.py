"""Ledger validator (production-ledger discipline applied to receipt ancestry)."""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path('/Users/mingli/Adva/AEG')
LEDGER = ROOT/'trials/receipt-ledger/ledger.json'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    ledger = json.loads(LEDGER.read_text(encoding='utf-8'))
    entries = ledger['entries']
    findings = []

    # coverage: exactly once, no unknown/missing/duplicate
    nums = [e['receipt'] for e in entries]
    if sorted(nums) != list(range(1, len(entries) + 1)):
        findings.append(f"coverage violation: {sorted(nums)}")
    if len(set(nums)) != len(nums):
        findings.append("duplicate receipt entries")

    # pins
    for e in entries:
        p = ROOT/e['path']
        if not p.exists():
            findings.append(f"receipt-{e['receipt']:02d} file missing")
        elif sha(p) != e['sha256']:
            findings.append(f"receipt-{e['receipt']:02d} pin mismatch")

    # predecessor uniqueness: each receipt is canonical predecessor of at most one entry
    targets = [e['canonical_predecessor'] for e in entries if e['canonical_predecessor']]
    if len(targets) != len(set(targets)):
        findings.append(f"predecessor multiplicity violation: {sorted(targets)}")

    # on-disk field vs canonical + repairs
    by_num = {e['receipt']: e for e in entries}
    for e in entries:
        n = e['receipt']
        if n == 1:
            if e['canonical_predecessor'] is not None:
                findings.append("root must have null predecessor")
            continue
        on_disk = json.loads((ROOT/e['path']).read_text(encoding='utf-8')).get('predecessor_sha256')
        canon_sha = by_num[e['canonical_predecessor']]['sha256']
        if on_disk == canon_sha:
            if e.get('repair'):
                findings.append(f"receipt-{n:02d} declares an unnecessary repair")
        else:
            if not e.get('repair'):
                findings.append(f"receipt-{n:02d} predecessor disagrees without a repair")
            else:
                pass  # explicit repair present: acceptable

    status = 'LedgerConsistent' if not findings else 'Rejected'
    report = {
      "schema": "aeg.receipt-ledger.check.research", "version": 0,
      "status": status, "findings": findings,
      "repairs_applied": [{"receipt": e['receipt'], "repair": e['repair']}
                          for e in entries if e.get('repair')],
      "entries": len(entries)
    }
    out = ROOT/'trials/receipt-ledger/check-report.json'
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
