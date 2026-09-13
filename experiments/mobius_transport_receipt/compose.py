"""External two-leg receiver; retains the parent checker unchanged."""
import argparse
import copy
import json
from pathlib import Path
import resource
import time
import check as C


def normalize(m, p):
    C.matrix(m, p)
    q = pow(next(v for v in m if v), -1, p)
    return [v*q % p for v in m]


def frame(context, receipt=None):
    p = context['p']
    xs = list(range(p)) + [C.INF]
    target = receipt is not None
    return {
        'scope': context['target_scope' if target else 'source_scope'],
        'p': p,
        'alphabet': list(C.LETTERS),
        'generators': [normalize(m, p) for m in
                       (receipt['target_matrices'][:2] if target else context['generators'])],
        'ordered_probes': receipt['target_probes'] if target else context['probes'],
        'predicate_set': sorted(receipt['target_predicate'] if target else context['predicate'], key=xs.index),
    }


def compose(receipts, expected, route_ids, fuel=None):
    old_cap = C.CAP
    if fuel is not None:
        C.CAP = min(C.CAP, C.UNITS + fuel)
    try:
        C.require(len(receipts) == len(expected) == len(route_ids) == 2)
        C.require(all(type(i) is str and 0 < len(i) < 100 for i in route_ids))
        C.require(len(set(route_ids)) == 2, 'InvalidRouteLabels')
        results = [C.verify(C.canon(r), C.canon(e)) for r, e in zip(receipts, expected)]
        for i, result in enumerate(results):
            if result['status'] != 'AcceptedTransportForDeclaredAction':
                return {'status': 'BlockedLeg', 'leg': i, 'reason': result, 'native_admission': False}
        left = frame(expected[0], receipts[0])
        right = frame(expected[1])
        mismatch = [key for key in left if left[key] != right[key]]
        if mismatch:
            return {'status': 'InvalidIntermediateInterface', 'mismatch': mismatch,
                    'left': left, 'right': right, 'leg_results': results, 'native_admission': False}
        a, b = expected
        p = a['p']
        direct_context = copy.deepcopy(a)
        direct_context['H'] = normalize(C.mul(b['H'], a['H'], p), p)
        direct_context['target_scope'] = b['target_scope']
        direct = C.produce(direct_context)
        final = C.verify(C.canon(direct), C.canon(direct_context))
        C.require(final['status'] == 'AcceptedTransportForDeclaredAction', 'InternalDirectFailure')
        # Matching the final frame is stronger than comparing only H2*H1.
        C.require(frame(direct_context, direct) == frame(b, receipts[1]), 'InternalEndpointMismatch')
        squares = []
        for label, target in zip(C.LETTERS, receipts[1]['target_matrices']):
            for x in list(range(p)) + [C.INF]:
                hx = C.act(a['H'], x, p)
                khx = C.act(b['H'], hx, p)
                staged_value = C.act(b['H'], C.act(receipts[0]['target_matrices'][C.LETTERS.index(label)], hx, p), p)
                final_value = C.act(target, khx, p)
                direct_value = C.act(direct['target_matrices'][C.LETTERS.index(label)], khx, p)
                C.require(staged_value == final_value == direct_value, 'InternalCovarianceMismatch')
                squares.append([label, x, staged_value])
        return {'status': 'AcceptedComposition', 'intermediate_frame': left,
                'history': {'route_ids': route_ids, 'scopes': [a['source_scope'], a['target_scope'], b['target_scope']],
                            'coordinate_changes': [a['H'], b['H']]},
                'direct_context': direct_context, 'direct_receipt': direct,
                'point_squares': squares, 'native_admission': False}
    except C.Refusal as err:
        return {'status': str(err), 'native_admission': False}
    finally:
        C.CAP = old_cap


def inputs(p, inverse=False):
    a = C.context(p)
    a['source_scope'], a['target_scope'] = 'A', 'B'
    ra = C.produce(a)
    b = C.context(p)
    b.update(source_scope='B', target_scope='C',
             H=C.inv(a['H'], p) if inverse else [1, 1, 0, 1],
             generators=copy.deepcopy(ra['target_matrices'][:2]),
             probes=copy.deepcopy(ra['target_probes']), predicate=copy.deepcopy(ra['target_predicate']))
    return [ra, C.produce(b)], [a, b]


def suite():
    started = time.perf_counter()
    rows = []
    phase_ms = {'construction': 0.0, 'verification': 0.0, 'reuse': 0.0, 'serialization': 0.0}
    for p in (5, 7):
        t = time.perf_counter()
        receipts, expected = inputs(p)
        phase_ms['construction'] += 1000*(time.perf_counter()-t)
        def trial(name, rs, es, wanted, route=('A-B', 'B-C'), fuel=None):
            t = time.perf_counter()
            result = compose(rs, es, list(route), fuel)
            phase_ms['verification'] += 1000*(time.perf_counter()-t)
            assert result['status'] == wanted, (p, name, result, wanted)
            rows.append({'field': p, 'name': name, 'receipts': rs, 'expected_contexts': es,
                         'route_ids': list(route), 'result': result})
            return result
        good = trial('matched', receipts, expected, 'AcceptedComposition')
        # Each mutated second leg is re-produced and remains independently valid.
        for name in ('scope', 'probes', 'predicate', 'generator'):
            es = copy.deepcopy(expected)
            if name == 'scope': es[1]['source_scope'] = 'B-other'
            elif name == 'probes': es[1]['probes'] = list(reversed(es[1]['probes']))
            elif name == 'predicate': es[1]['predicate'] = [0]
            else: es[1]['generators'] = list(reversed(es[1]['generators']))
            rs = [copy.deepcopy(receipts[0]), C.produce(es[1])]
            result = trial('changed-middle-'+name, rs, es, 'InvalidIntermediateInterface')
            assert all(x['status'] == 'AcceptedTransportForDeclaredAction' for x in result['leg_results'])
            assert normalize(C.mul(es[1]['H'], es[0]['H'], p), p) == good['direct_context']['H']
        es = copy.deepcopy(expected)
        es[1]['generators'] = [[2*v % p for v in m] for m in es[1]['generators']]
        es[1]['predicate'].reverse()
        trial('scalar-representative-and-set-order', [copy.deepcopy(receipts[0]), C.produce(es[1])], es, 'AcceptedComposition')
        rs = copy.deepcopy(receipts)
        rs[1]['observations'] = [r for r in rs[1]['observations'] if r[1] != C.INF]
        missing = trial('missing-middle-infinity-observations', rs, expected, 'BlockedLeg')
        assert missing['reason']['status'] == 'UnknownCoverage'
        rs = copy.deepcopy(receipts)
        rs[1]['observations'][0][2] = next(x for x in list(range(p))+[C.INF] if x != rs[1]['observations'][0][2])
        bad = trial('forged-second-leg-value', rs, expected, 'BlockedLeg')
        assert bad['reason']['status'] == 'InvalidEvidence'
        trial('duplicate-route-label', receipts, expected, 'InvalidRouteLabels', route=('same', 'same'))
        trial('zero-fuel', receipts, expected, 'UnknownResource', fuel=0)
        t = time.perf_counter()
        inv_rs, inv_es = inputs(p, inverse=True)
        inv_result = trial('inverse-round-trip', inv_rs, inv_es, 'AcceptedComposition')
        assert inv_result['direct_context']['H'] == [1, 0, 0, 1]
        assert inv_result['history']['scopes'] == ['A', 'B', 'C']
        assert len(inv_result['history']['route_ids']) == 2
        # Noncommuting positive pair exposes an incorrect multiplication order.
        h, k = expected[0]['H'], expected[1]['H']
        wrong = normalize(C.mul(h, k, p), p)
        right = good['direct_context']['H']
        separating = [x for x in list(range(p))+[C.INF] if C.act(wrong, x, p) != C.act(right, x, p)]
        assert separating
        rows.append({'field': p, 'name': 'wrong-composition-order', 'wrong_H': wrong,
                     'right_H': right, 'separating_points': separating})
        phase_ms['reuse'] += 1000*(time.perf_counter()-t)
    t = time.perf_counter()
    stable = {'status': 'Passed', 'cases': rows, 'native_admission': False,
              'new_terms': 0, 'residual': ['No native receipt composition', 'No intent authentication', 'No global transport or learning claim']}
    assert json.loads(C.canon(stable)) == stable
    phase_ms['serialization'] = 1000*(time.perf_counter()-t)
    stable['cost'] = {'work_units': C.UNITS, 'phase_ms': phase_ms,
                      'phase_note': 'reuse includes inverse-check verification; phases overlap and must not be summed',
                      'elapsed_before_write_ms': 1000*(time.perf_counter()-started),
                      'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      'search_candidates': 0}
    return stable


if __name__ == '__main__':
    resource.setrlimit(resource.RLIMIT_CPU, (15, 15))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024**2, 256*1024**2))
    ap = argparse.ArgumentParser()
    ap.add_argument('--output', required=True)
    args = ap.parse_args()
    try:
        result = suite()
    except C.Refusal as e:
        result = {'status': str(e), 'work_units': C.UNITS, 'native_admission': False}
    encoded = C.canon(result)+'\n'
    if len(encoded.encode()) > 1048576:
        raise SystemExit('UnknownResource: checkpoint size')
    Path(args.output).write_text(encoded)
    print(C.canon({k: result[k] for k in ('status', 'cost') if k in result}))
