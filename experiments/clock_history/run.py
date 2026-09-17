#!/usr/bin/env python3
"""Clock/history finite producer and process supervisor, Unknown v0.3.
Authored by ChatGPT (OpenAI), via Mingli Yuan's authorized account proxy.
This attribution is not Mingli Yuan's authorship, review, or endorsement.
"""
import argparse
import copy
from fractions import Fraction as F
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import resource
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
PROFILE = 'adva.research.clock-history.v0'
PRODUCER_SHA = 'd55dbcf2a394b4c34c1cc76a869d7003dea8113afe74c197c7bb512a2ec5353f'
WORK = 0


def tick(n=1):
    global WORK
    WORK += n
    if WORK > 100000:
        raise TimeoutError('producer-work')


def rat(x):
    x = F(x)
    return [x.numerator, x.denominator]


def edge(a, b):
    return {'rate': rat(a), 'offset': rat(b)}


def compose(edges):
    a, b = F(1), F(0)
    for e in edges:
        tick()
        rate, offset = F(*e['rate']), F(*e['offset'])
        a, b = rate * a, rate * b + offset
    return a, b


def kind(a, b):
    return 'ClockConsistent' if (a, b) == (1, 0) else 'RateConsistent' if a == 1 else 'ClockInconsistent'


def conjugate(edges, gauges):
    result = []
    for i, e in enumerate(edges):
        s, o = gauges[i]
        t, p = gauges[(i + 1) % 3]
        a, b = F(*e['rate']), F(*e['offset'])
        result.append(edge(t * a / s, t * b + p - t * a * o / s))
        tick()
    return result


def produce(expected, micro):
    a, b = compose(expected['edges'])
    rows = []
    for event in expected['events']:
        value = F(*event['time'])
        readings = [rat(value)]
        for j, e in enumerate(expected['edges']):
            value = F(*e['rate']) * value + F(*e['offset'])
            if j < 2:
                readings.append(rat(value))
            tick()
        rows.append({'id': event['id'], 'readings': readings, 'roundtrip': rat(value)})
    return {'profile': PROFILE, 'request': copy.deepcopy(expected),
            'calibration': {'rate': rat(a), 'offset': rat(b), 'kind': kind(a, b)},
            'events': rows, 'micro': copy.deepcopy(micro)}


def limit_child():
    resource.setrlimit(resource.RLIMIT_CPU, (3, 3))
    resource.setrlimit(resource.RLIMIT_AS, (134217728, 134217728))
    resource.setrlimit(resource.RLIMIT_FSIZE, (262144, 262144))


class Campaign:
    def __init__(self, out):
        self.out, self.start = out, time.perf_counter()
        self.runs, self.assertions, self.receiver_work = [], 0, 0
        self.times = {k: 0.0 for k in ('construction_seconds', 'receiving_seconds',
                                     'serialization_seconds', 'control_seconds',
                                     'reuse_construction_seconds', 'reuse_receiving_seconds')}
        old_path = ROOT.parent / 'reversible_memory' / 'run.py'
        raw = old_path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != PRODUCER_SHA:
            raise ValueError('old-producer-source-pin')
        spec = importlib.util.spec_from_loader('pinned_reversible_memory_producer', loader=None)
        self.old = importlib.util.module_from_spec(spec)
        self.old.__file__ = str(old_path)
        exec(compile(raw, str(old_path), 'exec'), self.old.__dict__)

    def check(self, condition, message):
        self.assertions += 1
        if not condition:
            raise AssertionError(message)

    def budget(self):
        self.check(self.receiver_work + self.old.WORK + WORK <= 100000, 'total-work')
        if time.perf_counter() - self.start > 30:
            raise TimeoutError('campaign-wall')
        self.check(sum(p.stat().st_size for p in self.out.rglob('*') if p.is_file()) <= 2097152, 'evidence-size')

    def save(self, path, value):
        t = time.perf_counter()
        path.write_text(json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2, allow_nan=False) + '\n')
        self.times['serialization_seconds'] += time.perf_counter() - t

    def build(self, name, m=3, q=F(1, 4), initial=0, H=3, mode='iid', schedule=None,
              edges=None, clocks=None, times=None):
        t = time.perf_counter()
        micro_request = self.old.request(name + ':micro', m, q, initial, mode=mode, schedule=schedule, H=H)
        expected = {'question': name, 'history': [name + ':declared'],
                    'scope': 'finite-clock-calibration-and-observed-history',
                    'clocks': clocks or ['A', 'B', 'C'],
                    'edges': edges or [edge(2, 1), edge(3, -2), edge(F(1, 6), F(-1, 6))],
                    'events': [{'id': 'e' + str(i), 'time': rat(t)} for i, t in enumerate(range(H + 1) if times is None else times)],
                    'micro_request': micro_request}
        micro = self.old.produce(micro_request)
        candidate = produce(expected, micro)
        dt = time.perf_counter() - t
        self.times['construction_seconds'] += dt
        if name == 'positive-gauge-reuse':
            self.times['reuse_construction_seconds'] += dt
        return expected, candidate

    def call(self, name, e, c, outcome, prefix, calibration=True, micro_kind=None, micro_prefix=0):
        self.budget()
        self.check(len(self.runs) < 32, 'receiver-call-cap')
        d = self.out / name
        d.mkdir(parents=True)
        self.save(d / 'expected.json', e)
        self.save(d / 'candidate.json', c)
        self.check(all((d / n).stat().st_size <= 65536 for n in ('expected.json', 'candidate.json')), 'input-size')
        args = [sys.executable, '-B', '-S', str(ROOT / 'receive.py'), '--expected', str(d / 'expected.json'), '--candidate', str(d / 'candidate.json')]
        self.save(d / 'command.json', {'argv': args, 'timeout_seconds': 3, 'address_space_bytes': 134217728})
        row = {'case': name, 'expected_outcome': outcome}
        self.runs.append(row)
        remaining = 30 - (time.perf_counter() - self.start)
        if remaining <= 0:
            raise TimeoutError('campaign-wall')
        t = time.perf_counter()
        with (d / 'stdout.json').open('wb') as stdout, (d / 'stderr.txt').open('wb') as stderr:
            child = subprocess.Popen(args, stdout=stdout, stderr=stderr, preexec_fn=limit_child)
            try:
                child.wait(timeout=min(3, remaining))
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=0.2)
        elapsed = time.perf_counter() - t
        self.times['receiving_seconds'] += elapsed
        if e.get('question') == 'positive-gauge-reuse':
            self.times['reuse_receiving_seconds'] += elapsed
        row.update(returncode=child.returncode, wall_seconds=elapsed)
        self.check(child.returncode == 0, (name, child.returncode, (d / 'stderr.txt').read_text()))
        ans = json.loads((d / 'stdout.json').read_text())
        self.receiver_work += ans['work_units']
        row.update(outcome=ans['outcome'], reason=ans['reason'], work_units=ans['work_units'],
                   dynamics_outcome=ans['dynamics_outcome'], verified_events=len(ans['verified_events']))
        self.check(ans['outcome'] == outcome, (name, ans['outcome'], ans['reason']))
        self.check(ans['expected_request'] == (None if outcome == 'InvalidContext' else e), (name, 'expected-binding'))
        self.check(ans['verified_events'] == c['events'][:prefix], (name, 'event-prefix'))
        self.check(ans['verified_calibration'] == (c['calibration'] if calibration else None), (name, 'calibration'))
        self.check(ans['dynamics_outcome'] == micro_kind, (name, 'dynamics-outcome'))
        self.check(all(ans[k] is False for k in ('native_authority', 'close_authorized', 'free_authorized')), (name, 'authority'))
        first = next(({'step': r['step'], **r['witness']} for r in c['micro']['trace'][:micro_prefix] if r['witness'] is not None), None)
        self.check(ans['verified_counterexample'] == first, (name, 'retained-counterexample'))
        if micro_kind is None:
            self.check(ans['micro_result'] is None, (name, 'unchecked-micro'))
        else:
            self.check(ans['micro_result']['verified_prefix'] == c['micro']['trace'][:micro_prefix], (name, 'micro-prefix'))
            self.check(ans['micro_result']['expected_request'] == e['micro_request'], (name, 'micro-binding'))
        if outcome == 'UnknownCoverage':
            self.check(ans['obstruction'] == {'missing_events': [r['id'] for r in e['events'][prefix:]],
                                             'micro': ans['micro_result']['obstruction']}, (name, 'coverage'))
        if outcome == 'CalibrationObstruction':
            self.check(ans['obstruction'] == c['calibration'], (name, 'calibration-obstruction'))
        self.budget()
        return ans


def execute(camp):
    saved = {}
    specs = [('fresh-quarter', {}),
             ('repeated-fair', {'m': 1, 'q': F(1, 2), 'initial': F(1, 2), 'H': 2, 'schedule': [0, 0]}),
             ('parity-three', {'q': F(1, 2), 'mode': 'parity'}),
             ('fresh-fair', {'q': F(1, 2)})]
    for name, kw in specs:
        e, c = camp.build(name, **kw)
        saved[name] = (e, c)
        mk = c['micro']['claim']['kind']
        camp.call('valid/' + name, e, c, 'VerifiedTransport', len(c['events']), micro_kind=mk, micro_prefix=e['micro_request']['horizon'])
    base_edges = saved['fresh-quarter'][0]['edges']
    gauges = [(F(2), F(1)), (F(3), F(-2)), (F(1, 2), F(3))]
    reuse_edges = conjugate(base_edges, gauges)
    reuse = camp.build('positive-gauge-reuse', q=F(1, 3), initial=F(1, 3), edges=reuse_edges,
                      clocks=['甲钟', '乙钟', '丙钟'], times=[F(-1, 3), F(1), F(7, 3), F(11, 3)])
    camp.call('valid/positive-gauge-reuse', *reuse, 'VerifiedTransport', 4, micro_kind='VerifiedMarkovHorizon', micro_prefix=3)
    t = time.perf_counter()
    controls = []
    for edges in (base_edges, base_edges[:2] + [edge(F(1, 6), F(5, 6))], base_edges[:2] + [edge(F(1, 3), F(-1, 3))]):
        # Direct closed formulas are independent of the producer's iterative composition.
        a, b = [F(*x['rate']) for x in edges], [F(*x['offset']) for x in edges]
        direct_R, direct_D = a[2] * a[1] * a[0], a[2] * a[1] * b[0] + a[2] * b[1] + b[2]
        changed = conjugate(edges, gauges)
        R, D = compose(changed)
        s, o = gauges[0]
        camp.check(R == direct_R and D == s * direct_D + (1 - direct_R) * o, 'gauge-conjugacy')
        camp.check(kind(R, D) == kind(direct_R, direct_D), 'calibration-class-invariant')
        # Every declared adjacent event interval stays strictly positive under all three gauges.
        for g, _ in gauges:
            for left, right in zip((F(-2, 3), F(0), F(2, 3)), (F(0), F(2, 3), F(4, 3))):
                camp.check(g * (right - left) > 0, 'positive-chart-preserves-order')
                tick()
        controls.append({'source_edges': edges, 'gauges': [[rat(s), rat(o)] for s, o in gauges],
                         'direct_loop': [rat(direct_R), rat(direct_D)], 'conjugated_edges': changed,
                         'conjugated_loop': [rat(R), rat(D)]})
    parity = saved['parity-three'][1]['micro']
    fresh = saved['fresh-fair'][1]['micro']
    camp.check(parity['trace'][:2] == fresh['trace'][:2], 'parity-two-step-prefix-invisible')
    camp.check(parity['claim']['first_failure'] == 3 and parity['trace'][2]['law'] == [[1, 1], [0, 1]], 'parity-third-step-counterexample')
    repeated = saved['repeated-fair'][1]['micro']
    camp.check(all(r['marginal_match'] and r['adjacent_match'] for r in repeated['trace']) and repeated['claim']['first_failure'] == 2, 'adjacent-laws-hide-reused-bit')
    weights = [F(*x) for x in saved['parity-three'][0]['micro_request']['initial_joint'][:8]]
    marginals = []
    for omitted in range(3):
        masses = {bits: F(0) for bits in itertools.product((0, 1), repeat=2)}
        for bits, p in zip(itertools.product((0, 1), repeat=3), weights):
            masses[bits[:omitted] + bits[omitted + 1:]] += p
            tick()
        camp.check(all(x == F(1, 4) for x in masses.values()), 'every-two-bit-parity-marginal-fair')
        marginals.append({'omitted': omitted, 'masses': [rat(masses[k]) for k in sorted(masses)]})
    camp.times['control_seconds'] += time.perf_counter() - t
    camp.save(camp.out / 'independent-controls.json', {'gauge_controls': controls, 'parity_two_bit_marginals': marginals,
              'parity_prefix_steps': 2, 'parity_counterexample_step': 3,
              'meaning': 'Finite exact algebra and supplied source distributions; not physical synchronization or a learned source law.'})
    for name, last in [('rate-only', edge(F(1, 6), F(5, 6))), ('drift-fixed-zero', edge(F(1, 3), F(-1, 3)))]:
        e, c = camp.build(name, q=F(1, 2), mode='parity', edges=base_edges[:2] + [last])
        camp.call('obstruction/' + name, e, c, 'CalibrationObstruction', 4, micro_kind='Counterexample', micro_prefix=3)
    e, original = saved['parity-three']
    c = copy.deepcopy(original); c['events'] = c['events'][:-1]
    camp.call('partial/terminal-event', e, c, 'UnknownCoverage', 3, micro_kind='Counterexample', micro_prefix=3)
    c = copy.deepcopy(original); c['micro'] = camp.old.produce(e['micro_request'], keep=2)
    camp.call('partial/micro-prefix', e, c, 'UnknownCoverage', 4, micro_kind='UnknownCoverage', micro_prefix=2)
    bad = []
    def alter(name, path, value, prefix=0, calibration=True, micro_kind=None, micro_prefix=0):
        c = copy.deepcopy(original); at = c
        for key in path[:-1]: at = at[key]
        at[path[-1]] = value
        bad.append((name, e, c, 'InvalidEvidence', prefix, calibration, micro_kind, micro_prefix))
    alter('wrong-loop', ['calibration', 'offset'], [1, 1], calibration=False)
    alter('wrong-reading', ['events', 1, 'readings', 1], [99, 1], prefix=1)
    alter('wrong-roundtrip', ['events', 1, 'roundtrip'], [99, 1], prefix=1)
    alter('changed-id', ['events', 1, 'id'], 'other-event', prefix=1)
    alter('missing-initial', ['events'], original['events'][1:])
    alter('reordered-events', ['events'], [original['events'][0], original['events'][2], original['events'][1], original['events'][3]], prefix=1)
    alter('duplicated-event', ['events'], [original['events'][0], original['events'][1], original['events'][1], original['events'][3]], prefix=2)
    alter('micro-binding', ['micro', 'request', 'schedule'], [0, 0, 2], prefix=4, micro_kind='InvalidEvidence')
    alter('false-history-row', ['micro', 'trace', 2, 'history_match'], True, prefix=4, micro_kind='InvalidEvidence', micro_prefix=2)
    alter('false-micro-claim', ['micro', 'claim', 'kind'], 'VerifiedMarkovHorizon', prefix=4, micro_kind='InvalidEvidence', micro_prefix=3)
    alter('question-binding', ['request', 'question'], 'changed-question', calibration=False)
    alter('clock-label-binding', ['request', 'clocks'], ['甲', '乙', '丙'], calibration=False)
    alter('history-binding', ['request', 'history'], ['other-history'], calibration=False)
    alter('wrong-profile', ['profile'], PROFILE + '.changed', calibration=False)
    alter('boolean-rate-evidence', ['calibration', 'rate'], [True, 1], calibration=False)
    c = copy.deepcopy(original); c['free_authorized'] = True
    bad.append(('extra-authority', e, c, 'InvalidEvidence', 0, False, None, 0))
    for name, expected, candidate, *rest in bad:
        camp.call('evidence/' + name, expected, candidate, *rest)
    contexts = []
    def context(name, path, value):
        changed = copy.deepcopy(e); at = changed
        for key in path[:-1]: at = at[key]
        at[path[-1]] = value
        contexts.append((name, changed))
    context('boolean-rate', ['edges', 0, 'rate'], [True, 1])
    context('nonpositive-clock', ['edges', 0, 'rate'], [0, 1])
    changed = copy.deepcopy(e); del changed['question']; contexts.append(('missing-question', changed))
    context('duplicate-event-id', ['events', 1, 'id'], 'e0')
    context('unordered-event-time', ['events', 1, 'time'], [0, 1])
    context('scope', ['scope'], 'universal')
    context('boolean-micro-horizon', ['micro_request', 'horizon'], True)
    for name, expected in contexts:
        camp.call('context/' + name, expected, original, 'InvalidContext', 0, False)
    camp.check(len(camp.runs) == 32, 'declared-thirty-two-cases')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (134217728, 134217728))
    args.output.mkdir(parents=True, exist_ok=False)
    camp = Campaign(args.output)
    failure = None
    camp.save(args.output / 'contract.json', json.loads((ROOT / 'contract.json').read_text()))
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('campaign-wall')))
    signal.alarm(30)
    try:
        execute(camp)
    except Exception as exc:
        failure = {'type': type(exc).__name__, 'message': str(exc)}
    finally:
        signal.alarm(0)
    size = sum(p.stat().st_size for p in args.output.rglob('*') if p.is_file())
    elapsed = time.perf_counter() - camp.start
    if size > 2097152 or elapsed > 30:
        failure = failure or {'type': 'BudgetExceeded', 'message': 'campaign-boundary'}
    result = {'profile': PROFILE, 'success': failure is None, 'failure': failure, 'receiver_calls': len(camp.runs),
              'assertions': camp.assertions, 'receiver_work': camp.receiver_work, 'clock_producer_control_work': WORK,
              'imported_micro_producer_work': camp.old.WORK, 'total_work_units': WORK + camp.old.WORK + camp.receiver_work,
              'search_candidates': 0, 'wall_seconds': elapsed, 'phases': camp.times, 'cases': camp.runs,
              'child_maxrss_kib': resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              'supervisor_maxrss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'evidence_bytes_before_summary': size, 'python': sys.version,
              'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in ('receive.py', 'run.py', 'contract.json')},
              'old_producer_sha256': PRODUCER_SHA,
              'limits': 'Linux per-process RSS high water, not aggregate memory. Phase timing excludes final summary. Reuse timings are subsets. Input preparation, local exact controls and process checks counted; Fraction internals are not individually metered. Research, review and network cost unmeasured.'}
    camp.save(args.output / 'execution.json', result)
    print(json.dumps({k: v for k, v in result.items() if k not in ('cases', 'source_sha256')}))
    return 0 if failure is None else 1


if __name__ == '__main__':
    raise SystemExit(main())
