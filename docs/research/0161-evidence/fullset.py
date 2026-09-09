"""Full 0..255 byte set: signed substrate projection + tamper + iota round-trip sample."""
import hashlib, json, pathlib, sys, time
sys.setrecursionlimit(200000)
import importlib.util
spec = importlib.util.spec_from_file_location('s', 'signed.py')
s = importlib.util.module_from_spec(spec); spec.loader.exec_module(s)
APP = s.APP

FUEL = 2000000
start = time.monotonic()
rows = []
ok_values, ok_distinct = 0, set()
sizes = []
for b in range(256):
    t, u, v = s.encode_byte(b)
    val = s.signed_value(t, FUEL)
    rows.append({'b': b, 'u': u, 'v': v, 'value': val, 'term_size': s.r.size(t),
                 'term_sha': hashlib.sha256(repr(t).encode()).hexdigest()[:16]})
    ok_values += (val == b)
    ok_distinct.add(rows[-1]['term_sha'])
    sizes.append(rows[-1]['term_size'])
print('values correct: %d/256' % ok_values)
print('distinct terms: %d/256' % len(ok_distinct))
print('term size min/max: %d/%d' % (min(sizes), max(sizes)))

# tamper controls on a sample: v -> v+1
tamper_ok = True
for b in (0, 35, 100, 255):
    t, u, v = s.encode_byte(b)
    sign = s.TRUE if v >= 0 else s.FALSE
    bt = APP(s.PAIR, sign, s.church(abs(v) + 1))
    a = APP(s.PAIR, s.TRUE, APP(s.ADD, s.church(u), s.church(u)))
    tampered = APP(s.SIGN_ADD, a, bt)
    tv = s.signed_value(tampered, FUEL)
    print('tamper b=%d -> %d' % (b, tv))
    tamper_ok &= (tv != b)
print('tamper controls:', 'ok' if tamper_ok else 'FAIL')

# iota round-trip sample
rt = {}
for b in (0, 35, 100, 255):
    t, u, v = s.encode_byte(b)
    iot = s.r.to_iota(t)
    exp, steps = s.r.expand_iota(iot, 2000000)
    norm = s.r.normalize(exp, 2000000)
    val = s.signed_value(norm, FUEL)
    rt[b] = {'value': val, 'expand_steps': steps, 'iota_size': s.r.size(iot)}
    print('round-trip b=%d -> %d (iota_size=%d, steps=%d)' % (b, val, rt[b]['iota_size'], steps))
print('elapsed %.1fs' % (time.monotonic() - start))

results = {
  'schema': 'aeg.iota-projection-fullset.research', 'version': 0,
  'status': 'VariationObserved' if (ok_values == 256 and len(ok_distinct) == 256 and tamper_ok
                                    and all(rt[b]['value'] == b for b in rt)) else 'Rejected',
  'values_correct': ok_values, 'distinct_terms': len(ok_distinct),
  'term_size_min': min(sizes), 'term_size_max': max(sizes),
  'tamper': tamper_ok, 'round_trip_sample': rt,
  'bounds': {'model_fuel': FUEL, 'expand_fuel': 2000000},
  'sample_rows': [r for r in rows if r['b'] in (0, 7, 35, 100, 255)]
}
pathlib.Path('fullset-results.json').write_text(json.dumps(results, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
print('status:', results['status'])
