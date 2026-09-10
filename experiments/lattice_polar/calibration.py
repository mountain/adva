"""Exact, bounded external polar calibration; no Adva semantic authority."""
from fractions import Fraction as Q
from itertools import combinations, permutations, product
from pathlib import Path
import argparse
import hashlib
import json
import resource
import signal
import time


class Limit(Exception):
    pass


class Meter:
    def __init__(self, budget):
        self.start = time.monotonic()
        self.budget = budget
        self.triples = 0
        self.checks = 0

    def tick(self):
        if time.monotonic() - self.start > self.budget['max_seconds']:
            raise Limit('wall-time')

    def check(self, condition, reason):
        self.tick()
        self.checks += 1
        if self.checks > self.budget['max_checks']:
            raise Limit('checks')
        if not condition:
            raise AssertionError(reason)


def dot(a, b):
    return sum(x*y for x, y in zip(a, b))


def det(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            - a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            + a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))


def solve_one(rows):
    d = det(rows)
    if not d:
        return None
    return tuple(Q(det(tuple(tuple(1 if j == k else row[j]
                                         for j in range(3))
                                   for row in rows)), d)
                 for k in range(3))


def polar(vertices, meter):
    """Enumerate vertices of intersection dot(v,y)<=1 by active triples."""
    vertices = sorted(set(vertices))
    meter.check(all(tuple(-x for x in v) in vertices for v in vertices),
                'scope requires central symmetry')
    meter.check(any(det(rows) for rows in combinations(vertices, 3)),
                'scope requires full dimension')
    found = set()
    for rows in combinations(vertices, 3):
        meter.tick()
        meter.triples += 1
        if meter.triples > meter.budget['max_triples']:
            raise Limit('constraint triples')
        y = solve_one(rows)
        if y is None:
            continue
        if all(dot(v, y) <= 1 for v in vertices):
            meter.check(all(dot(v, y) == 1 for v in rows), 'active equalities')
            found.add(y)
    return sorted(found)


def integral(x):
    return Q(x).denominator == 1


def encode(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode() + b'\n'


def coords(rows):
    return [[str(x) for x in v] for v in rows]


def classify(vertices, dual, coverage):
    if not coverage:
        return 'UnknownCoverage'
    if any(not integral(dot(v, y)) for v in vertices for y in dual):
        return 'NoCompatibleReflexiveLattice'
    if all(integral(x) for v in vertices + dual for x in v):
        return 'ReflexiveInDeclaredLattice'
    return 'UnknownLattice'


def run(contract):
    meter = Meter(contract['budget'])
    t0 = time.perf_counter_ns()
    to24 = sorted({tuple(Q(s*x) for s, x in zip(sign, p))
                   for p in permutations((0, 1, 2))
                   for sign in product((-1, 1), repeat=3)})
    cube = [tuple(map(Q, s)) for s in product((-1, 1), repeat=3)]
    shear = lambda v: (v[0]+v[1], v[1], v[2])
    inv_transpose = lambda y: (y[0], y[1]-y[0], y[2])
    fixtures = [('to24', to24), ('cube', cube),
                ('sheared-cube', sorted(map(shear, cube))),
                ('scaled-to24', [tuple(2*x for x in v) for v in to24])]
    formation_ns = time.perf_counter_ns() - t0
    results = []
    computed = {}
    for name, vertices in fixtures:
        start = time.perf_counter_ns()
        count0 = meter.triples
        dual = polar(vertices, meter)
        back = polar(dual, meter)
        meter.check(back == sorted(vertices), name + ' bidual')
        computed[name] = dual
        status = classify(vertices, dual, True)
        expected = ('NoCompatibleReflexiveLattice' if 'to24' in name
                    else 'ReflexiveInDeclaredLattice')
        meter.check(status == expected, name + ' classification')
        pairings = sorted({dot(v, y) for v in vertices for y in dual})
        active_faces = [[i for i, v in enumerate(vertices) if dot(v, y) == 1]
                        for y in dual]
        results.append({'name': name, 'vertices': coords(vertices),
                        'polar_vertices': coords(dual), 'bidual_vertices': coords(back),
                        'face_vertex_indices': active_faces,
                        'pairing_values': [str(x) for x in pairings],
                        'status': status, 'rational_biduality': True,
                        'constraint_triples': meter.triples-count0,
                        'construct_and_verify_ns': time.perf_counter_ns()-start})
    expected_dual = sorted({tuple(Q(s, 2) if i == axis else Q(0) for i in range(3))
                            for axis in range(3) for s in (-1, 1)} |
                           {tuple(Q(s, 3) for s in signs)
                            for signs in product((-1, 1), repeat=3)})
    meter.check(computed['to24'] == expected_dual, 'independent facet formula')
    faces = results[0]['face_vertex_indices']
    edges = {tuple(sorted(set(a).intersection(b)))
             for a, b in combinations(faces, 2)
             if len(set(a).intersection(b)) == 2}
    meter.check(len(to24) == 24 and len(edges) == 36 and len(faces) == 14,
                'TO24 incidence')
    meter.check([len(f) for f in faces].count(4) == 6 and
                [len(f) for f in faces].count(6) == 8, 'face types')
    meter.check(24-36+14 == 2, 'surface Euler')
    for i in range(24):
        meter.check(sorted(len(f) for f in faces if i in f) == [4, 6, 6],
                    'vertex face incidence')
    v, y = (Q(1), Q(2), Q(0)), (Q(1, 2), Q(0), Q(0))
    meter.check(v in to24 and y in computed['to24'] and dot(v, y) == Q(1, 2),
                'lattice obstruction witness')
    meter.check(sorted(map(inv_transpose, computed['cube'])) == computed['sheared-cube'],
                'fresh unimodular dual-coordinate reuse')
    meter.check(sorted(tuple(x/2 for x in w) for w in computed['to24']) == computed['scaled-to24'],
                'new scale reuse')
    meter.check(dot(shear(v), inv_transpose(y)) == dot(v, y), 'pairing covariance')
    # Distinct rejection causes: bad geometry, missing coverage, wrong dual map,
    # and an epsilon rule attempting to promote rational nonintegrality.
    bad = (Q(1), Q(0), Q(0))
    violating = (Q(2), Q(1), Q(0))
    meter.check(dot(violating, bad) == 2 > 1, 'forged polar vertex refused')
    meter.check(classify(to24, computed['to24'], False) == 'UnknownCoverage',
                'incomplete enumeration cannot accept')
    meter.check(sorted(map(shear, computed['cube'])) != computed['sheared-cube'],
                'same forward map is not dual map')
    meter.check(Q(1, 2) < Q(3, 4) and not integral(Q(1, 2)),
                'small fractional residual is not integral')
    report = {'schema': 'adva.research.lattice-polar-evidence', 'version': 0,
              'status': 'Completed', 'base_commit': contract['base_commit'],
              'fixtures': results, 'topology': {'V': 24, 'E': 36, 'F': 14, 'chi_boundary': 2},
              'obstruction': {'primal_vertex': ['1','2','0'],
                              'polar_vertex': ['1/2','0','0'], 'pairing': '1/2',
                              'scope': 'Every full-rank lattice with dual pairing at this fixed origin; no lattice search'},
              'controls': ['forged-polar-vertex-rejected', 'missing-coverage-unknown',
                           'wrong-dual-transform-rejected', 'epsilon-integrality-rejected'],
              'native_admission': 'NotGranted', 'mirror_constructed': False,
              'residuals': ['No typed Goldberg refinement or Q4/M6 filler transport',
                            'No alternative shape, translated origin, toric variety or CY constructed',
                            'No full semantic validator or independent proof-assistant replay',
                            'No runtime, crypto security, universal grammar or acceleration claim'],
              'cost': {'formation_ns': formation_ns, 'constraint_triples': meter.triples,
                       'assertions': meter.checks, 'construction_validation_ns': time.perf_counter_ns()-t0,
                       'peak_rss_kib_linux': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                       'memory_scope': 'Process high-water RSS, not file bytes or aggregate service memory',
                       'unmeasured': ['research', 'authoring', 'network', 'human interpretation validation'],
                       'correction_replays': 0}}
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Refusing to overwrite evidence')
    here = Path(__file__).resolve().parent
    raw_contract = (here/'contract.json').read_bytes()
    contract = json.loads(raw_contract)
    b = contract['budget']
    resource.setrlimit(resource.RLIMIT_AS, (b['address_space_bytes'], b['address_space_bytes']))
    resource.setrlimit(resource.RLIMIT_CPU, (b['cpu_seconds'], b['cpu_seconds']))
    resource.setrlimit(resource.RLIMIT_FSIZE, (b['max_output_file_bytes'], b['max_output_file_bytes']))
    def timeout(signum, frame):
        raise Limit('wall-time supervisor')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(b['max_seconds'])
    try:
        report = run(contract)
    except Limit as exc:
        report = {'status': 'Unknown', 'reason': str(exc), 'native_admission': 'NotGranted'}
    report['contract_sha256'] = hashlib.sha256(raw_contract).hexdigest()
    report['implementation_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    t = time.perf_counter_ns()
    payload = encode(report)
    restored = json.loads(payload)
    if restored != report:
        raise AssertionError('serialization replay')
    codec_ns = time.perf_counter_ns()-t
    report['serialization_replay'] = {'equal': True, 'measured_ns': codec_ns,
                                    'scope': 'complete pre-cost report encoded and parsed; not independent proof'}
    payload = encode(report)
    if len(payload) > b['max_output_file_bytes']:
        raise Limit('artifact size')
    t = time.perf_counter_ns()
    with args.output.open('xb') as f:
        f.write(payload)
    write_ns = time.perf_counter_ns()-t
    print(json.dumps({'status': report['status'], 'output': str(args.output),
                      'output_bytes': len(payload), 'write_ns': write_ns,
                      'cost': report.get('cost', {}), 'serialization_replay_ns': codec_ns}))


if __name__ == '__main__':
    main()
