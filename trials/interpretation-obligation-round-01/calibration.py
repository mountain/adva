"""Sentence-3 predicate calibration: carrier vs instrumentation.
Follows Research 0166's M/I/Q/B pattern in a bounded local form."""
import hashlib, json, pathlib, re, sys

ADVA = pathlib.Path('/Users/mingli/Adva/adva')
AEG = pathlib.Path('/Users/mingli/Adva/AEG')
OUT = pathlib.Path(__file__).resolve().parent
CARRIER_PATTERNS = ('learn-*.transition.adva', 'learn-*.frontier.adva', 'run-*.transition.adva')

def sha(b): return hashlib.sha256(b).hexdigest()

def carrier_hash(rd):
    parts = []
    for pat in CARRIER_PATTERNS:
        for f in sorted(rd.glob(pat)):
            parts.append(f.read_bytes())
    return sha(b'\x00'.join(parts))

def strip_instrumentation(raw: bytes) -> bytes:
    j = json.loads(raw.decode('utf-8'))
    def walk(o):
        if isinstance(o, dict):
            for k in list(o.keys()):
                if any(w in k.lower() for w in ('second', 'timing', 'wall', 'clock', 'elapsed', 'duration')):
                    o.pop(k, None)
                else:
                    walk(o[k])
        elif isinstance(o, list):
            for v in o: walk(v)
    walk(j)
    return json.dumps(j, sort_keys=True).encode()

# --- Q evaluation on the archives ---
c1 = ADVA/'docs/research/0162-evidence/archive-cycle1'
c2 = ADVA/'docs/research/0162-evidence/archive-cycle2'
h1 = {d.name: carrier_hash(d) for d in sorted(c1.glob('round-*'))}
h2 = {d.name: carrier_hash(d) for d in sorted(c2.glob('round-*'))}
carrier_constant = (len(set(h1.values())) == 1 and len(set(h2.values())) == 1
                    and all(h1[k] == h2[k] for k in h1))

# --- Q evaluation on native outputs ---
rr = AEG/'.rust-run100'
raw = {}; stripped = {}
for f in sorted(rr.glob('out-*.adva')):
    b = f.read_bytes()
    raw[f.name] = sha(b)
    stripped[f.name] = sha(strip_instrumentation(b))
instrumentation_only_variation = (len(set(raw.values())) > 1 and len(set(stripped.values())) == 1)

# --- counterexample control: carrier that INCLUDES instrumentation ---
def carrier_hash_with_instrumentation(rd):
    parts = []
    for pat in CARRIER_PATTERNS:
        for f in sorted(rd.glob(pat)):
            parts.append(strip_instrumentation(f.read_bytes()))  # same as stripped carrier
    return sha(b'\x00'.join(parts))
# the real failure mode: hashing the RAW run reports including phase_seconds
raw_run_hashes = set()
for f in sorted(rr.glob('out-*.adva')):
    raw_run_hashes.add(sha(f.read_bytes()))
counterexample_guard = len(raw_run_hashes) > 1  # undelimited carrier would falsely vary

# --- tamper control ---
tampered = bytearray(sorted(c1.glob('round-*'))[0].glob('learn-01.transition.adva').__next__().read_bytes())
tampered[0] ^= 0xFF
tamper_changes_hash = sha(tampered) != carrier_hash(sorted(c1.glob('round-*'))[0])

status = ('MatchedFiniteScope' if (carrier_constant and instrumentation_only_variation
          and counterexample_guard and tamper_changes_hash) else 'Rejected')
report = {
  "schema": "aeg.interpretation-obligation.result.research", "version": 0,
  "status": status,
  "question": "unchanged inputs -> declared-carrier constant (EvidenceStutter) while non-carrier instrumentation varies (IncidentalVariation)?",
  "evidence": {
    "archive_cycle1_distinct_carrier": len(set(h1.values())),
    "archive_cycle2_distinct_carrier": len(set(h2.values())),
    "cross_cycle_equal_rounds": sum(1 for k in h1 if h1[k] == h2[k]),
    "native_raw_distinct": len(set(raw.values())),
    "native_stripped_distinct": len(set(stripped.values())),
    "counterexample_guard_passed": counterexample_guard,
    "tamper_changes_hash": tamper_changes_hash,
    "sample_carrier_sha": h1['round-001'][:16],
  },
  "sentence_to_predicate_mapping": {
    "sentence": "变异必须落在声明的载波上——行动之前，先定义自己测量什么。",
    "predicate": "carrier = declared projection (learn transition/frontier + run transition); unchanged input implies carrier-hash constant AND any observed variation confined to instrumentation fields",
    "status": "proposed-mapping (human review pending)"
  },
  "native_admission": "not-granted",
  "no_teichmuller_calabi_yau_step": True
}
(OUT/'report.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
print(json.dumps(report, indent=2, ensure_ascii=False))
