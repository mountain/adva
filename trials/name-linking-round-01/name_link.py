"""Name linking: link/unlink semantics with an explicit link ledger.
Applied to the math catalog keys and titles."""
import json, pathlib, re

ROOT = pathlib.Path('/Users/mingli/Adva/adva/adva-library')

def words_of(title):
    """Declared rule: split on spaces, lowercase, drop nothing else."""
    return [w.lower() for w in re.split(r'\s+', title.strip()) if w]

def link(words):
    """Explicit linking: joins with '-', retaining order and a link ledger."""
    if not words:
        raise ValueError("empty word list")
    ledger = [(words[i], words[i + 1]) for i in range(len(words) - 1)]
    return '-'.join(words), ledger

def unlink(name):
    """Unlink: split and verify recoverability of the ledger."""
    words = name.split('-')
    _, ledger = link(words)
    return words, ledger

def check(key, title):
    words = words_of(title)
    linked, ledger = link(words)
    if linked == key:
        return {"status": "linked", "words": len(words), "ledger": len(ledger)}
    # gap: key is not the link-image of the title
    return {"status": "disconnected", "title_words": words,
            "linked_form": linked, "key": key}

m = json.loads((ROOT/'math/manifest.json').read_text(encoding='utf-8'))
rows = []
for e in m['entries']:
    r = check(e['key'], e['title'])
    r['key'] = e['key']
    rows.append(r)

linked = [r for r in rows if r['status'] == 'linked']
disc = [r for r in rows if r['status'] == 'disconnected']
report = {
  "schema": "aeg.name-linking.check.research", "version": 0,
  "declared_rules": ["title words split on spaces, lowercased, joined by '-'",
                     "no silent normalization beyond the declared case rule",
                     "unlink recovers the full word sequence and order"],
  "status": "LinkedCount %d/14" % len(linked),
  "linked": [r['key'] for r in linked],
  "disconnected": [{"key": r['key'], "title_words": r['title_words'],
                    "linked_form": r['linked_form']} for r in disc],
  "example": check('three-verifier-arithmetic-calibration', 'Three-verifier arithmetic calibration')
}
pathlib.Path('report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print('linked keys:', len(linked), '/14')
for r in linked:
    print('  [linked]  ', r['key'])
print('disconnected:', len(disc), '/14')
for r in disc:
    print('  [断开]', r['key'], '<- title words:', r['title_words'], '-> link form:', r['linked_form'])
print()
print('example three-verifier:', json.dumps(report['example'], ensure_ascii=False))
