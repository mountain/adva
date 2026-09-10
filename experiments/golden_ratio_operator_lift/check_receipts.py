"""Finite adversarial suite; the producer uses the earlier homogeneous replay."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import resource
import time

import receipt as r
import replay as producer

HERE = Path(__file__).parent


def context(a, basis):
    return {'domain': 'Q-vector-affine', 'dimension': len(a),
            'operator': [[str(x) for x in row] for row in a],
            'basis': [[str(x) for x in row] for row in basis],
            'word': r.WORD, 'composition': 'rightmost-first'}


def produce(c):
    a = producer.matrix(c['operator'])
    n = len(a)
    observations = []
    for j, row in enumerate(c['basis']):
        out = producer.word_action(a, tuple(map(producer.F, row)), r.WORD)
        observations.append({'basis_index': j,
                             'translation_residual': [str(out[i][n]) for i in range(n)],
                             'closed': out == producer.eye(n+1)})
    return {'schema': 'adva.external.operator-lift-receipt.v0', 'context': c,
            'context_sha256': r.fingerprint(c), 'observations': observations}


def suite():
    beginning = time.perf_counter()
    h = [['1', '1'], ['1', '2']]
    standard = [['1', '0'], ['0', '1']]
    base = produce(context(h, standard))
    fresh = produce(context(h, [['1', '1'], ['0', '1']]))
    changed = produce(context([['1', '2'], ['1/2', '2']], standard))
    third = produce(context([['1','1','0'], ['1','2','0'], ['0','0','1']],
                            [['1','0','0'], ['0','1','0'], ['0','0','1']]))
    construction = time.perf_counter()-beginning
    cases = []
    def add(name, obj, expected, anchor=None, fuel=10000):
        raw = obj if isinstance(obj, str) else r.canonical(obj)
        anchor = (obj['context_sha256'] if anchor is None and isinstance(obj, dict)
                  else anchor)
        cases.append({'name': name, 'raw_json': raw, 'expected_context_sha256': anchor,
                      'fuel_limit': fuel, 'expected_status': expected})
    closed = 'ClosedForAllTranslationsByLinearity'
    add('standard-basis', base, closed)
    add('fresh-nonstandard-basis', fresh, closed)
    add('changed-frame-explicit-new-context', changed, closed)
    for name, obj in [('basis', fresh), ('operator', changed), ('dimension', third)]:
        add('self-rehashed-'+name+'-old-anchor', obj, 'InvalidContextBinding', base['context_sha256'])
    partial = copy.deepcopy(third); partial['observations'] = partial['observations'][:2]
    add('missing-third-direction', partial, 'UnknownCoverage')
    add('third-direction-refutes', third, 'Refuted')
    negative = copy.deepcopy(third); negative['observations'] = negative['observations'][2:]
    add('one-negative-direction-suffices', negative, 'Refuted')
    for name, mutate, status in [
        ('forged-zero', lambda o: o['observations'][2].update(translation_residual=['0','0','0'], closed=True), 'InvalidEvidence'),
        ('forged-Boolean', lambda o: o['observations'][2].update(closed=True), 'InvalidEvidence')]:
        obj = copy.deepcopy(third); mutate(obj); add(name, obj, status)
    obj = copy.deepcopy(base); obj['observations'].reverse(); add('reordered-evidence-indices', obj, closed)
    obj = copy.deepcopy(base); obj['observations'] = []; add('empty-observation-list', obj, 'UnknownCoverage')
    mutations = [
        ('duplicate-index', lambda o: o['observations'][1].update(basis_index=0)),
        ('out-of-range-index', lambda o: o['observations'][0].update(basis_index=2)),
        ('Boolean-index', lambda o: o['observations'][0].update(basis_index=False)),
        ('Boolean-dimension', lambda o: o['context'].update(dimension=True)),
        ('wrong-word', lambda o: o['context'].update(word='bbbaaBAAB')),
        ('wrong-order', lambda o: o['context'].update(composition='leftmost-first')),
        ('float-rational', lambda o: o['context']['operator'][0].__setitem__(0, 1.0)),
        ('noncanonical-rational', lambda o: o['context']['operator'][0].__setitem__(0, '2/2')),
        ('zero-denominator', lambda o: o['context']['operator'][0].__setitem__(0, '1/0')),
        ('oversized-rational', lambda o: o['context']['operator'][0].__setitem__(0, str(2**33))),
        ('unknown-field', lambda o: o.update(override=True)),
        ('wrong-residual-dimension', lambda o: o['observations'][0].update(translation_residual=['0'])),
    ]
    for name, mutate in mutations:
        obj = copy.deepcopy(base); mutate(obj); add(name, obj, 'InvalidSchema')
    for name, field, value, status in [
        ('dependent-basis', 'basis', [['1','0'], ['2','0']], 'InvalidBasis'),
        ('singular-operator', 'operator', [['0','0'], ['0','0']], 'InvalidInverse')]:
        obj = copy.deepcopy(base); obj['context'][field] = value
        obj['context_sha256'] = r.fingerprint(obj['context'])
        add(name, obj, status)
    add('missing-external-anchor', base, 'InvalidContextBinding', '')
    add('duplicate-JSON-key', '{"schema":0,"schema":1}', 'InvalidSchema', base['context_sha256'])
    add('oversized-input', ' '*16385, 'InvalidSchema', base['context_sha256'])
    add('fuel-exhaustion', base, 'UnknownResource', fuel=0)
    if len(cases) > 40:
        raise RuntimeError('suite count budget')
    validation = time.perf_counter()
    total_work = producer.work
    for c in cases:
        if time.perf_counter()-beginning > 12:
            raise TimeoutError('suite budget')
        result = r.verify(c['raw_json'].encode(), c['expected_context_sha256'], c['fuel_limit'])
        c['result'] = result
        total_work += result['work_units']
        if total_work > 100000:
            raise TimeoutError('suite arithmetic budget')
        if result['status'] != c['expected_status']:
            return {'status': 'Failed', 'cases': cases, 'failure': c['name']}
    return {'status': 'Passed', 'cases': cases, 'checks': len(cases),
            'cost': {'construction_seconds': construction,
                     'suite_validation_seconds': time.perf_counter()-validation,
                     'fresh_basis_validation_seconds': cases[1]['result']['validation_seconds'],
                     'total_arithmetic_work_units': total_work, 'search_candidates': 0,
                     'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                     'research_and_coding_seconds': None},
            'residual': 'Finite external validator, not native admission or authentication'}


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output', required=True)
    target = Path(parser.parse_args().output)
    if target.exists():
        raise SystemExit('fresh output required')
    resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
    result = suite()
    result['pins'] = {p: hashlib.sha256((HERE/p).read_bytes()).hexdigest()
                      for p in ['receipt-contract.json', 'receipt.py', 'check_receipts.py', 'replay.py']}
    t = time.perf_counter()
    payload = json.dumps(result, indent=2)+'\n'
    assert json.loads(payload) == result
    result.setdefault('cost', {})['serialization_roundtrip_seconds'] = time.perf_counter()-t
    payload = json.dumps(result, indent=2)+'\n'
    assert len(payload.encode()) <= 262144
    t = time.perf_counter()
    with target.open('x') as f:
        f.write(payload)
    print(json.dumps({'status': result['status'], 'checks': result.get('checks'),
                      'cost': result['cost'], 'write_seconds': time.perf_counter()-t}))
    return 0 if result['status'] == 'Passed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
