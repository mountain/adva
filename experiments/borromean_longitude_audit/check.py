#!/usr/bin/env python3
"""Bounded exact diagram -> preferred longitude -> degree-two Magnus audit.

ChatGPT (OpenAI), through Mingli Yuan's account as an authorized proxy.
External mathematics only. Read contract.json before running.
"""
import argparse
import hashlib
import itertools
import json
from pathlib import Path
import platform
import resource
import signal
import time


class Exhausted(Exception):
    pass


class Refused(Exception):
    pass


class Budget:
    def __init__(self, rules):
        self.rules = rules
        self.start = time.monotonic()
        self.work = self.diagrams = self.longitudes = 0
        self.checks = []

    def step(self, n=1):
        self.work += n
        if (self.work > self.rules['max_work_units'] or
                time.monotonic()-self.start > self.rules['mathematical_phase_seconds']):
            raise Exhausted('work or mathematical-phase time')

    def check(self, name, condition):
        self.step()
        if len(self.checks) >= self.rules['max_assertions']:
            raise Exhausted('assertions')
        self.checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)

    def count(self, kind, cap):
        self.step()
        setattr(self, kind, getattr(self, kind)+1)
        if getattr(self, kind) > self.rules[cap]:
            raise Exhausted(kind)


B = Q = None


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bounded_read(path, cap):
    if path.stat().st_size > cap:
        raise Exhausted('input bytes')
    data = path.read_bytes()
    if len(data) > cap:
        raise Exhausted('input bytes changed')
    return data


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Q())


def cross(a, b):
    return tuple(a[(k+1)%3]*b[(k+2)%3]-a[(k+2)%3]*b[(k+1)%3]
                 for k in range(3))


def det(a, b):
    return a[0]*b[1]-a[1]*b[0]


def dump(value):
    if isinstance(value, Q):
        return value.dump()
    if isinstance(value, dict):
        return {str(k): dump(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [dump(v) for v in value]
    return value


def number(pair):
    if not isinstance(pair, list) or len(pair) != 2:
        raise Refused('InvalidDomain')
    x = Q(*pair)
    for f in (x.a, x.b):
        if max(abs(f.numerator).bit_length(), f.denominator.bit_length()) > B.rules['input_coefficient_bits']:
            raise Exhausted('input coefficient bits')
    return x


def polygons(inputs, order):
    """Input adapter only. No filled surface enters the diagram calculation."""
    if len(inputs) != 3 or len(set(order)) != 3 or set(inputs) != set(order):
        raise Refused('UnknownCoverage')
    answer = []
    for name in order:
        r = inputs[name]
        k, sign = r['fixed'], r['normal']
        if k not in (0, 1, 2) or sign not in (-1, 1):
            raise Refused('InvalidDomain')
        u, v = (k+1)%3, (k+2)%3
        if set(r['extents']) != {str(u), str(v)} or len(r['center']) != 3:
            raise Refused('InvalidDomain')
        c = tuple(number(x) for x in r['center'])
        h = {int(a): number(b) for a, b in r['extents'].items()}
        if any(x <= Q() for x in h.values()):
            raise Refused('InvalidDomain')
        points = []
        # Reversing the second in-plane axis reverses the polygon orientation.
        for su, sv in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
            p = list(c)
            p[u] += su*h[u]
            p[v] += sign*sv*h[v]
            points.append(tuple(p))
        n = cross(sub(points[1], points[0]), sub(points[2], points[1]))
        B.check('adapter-oriented-boundary', n[k].sign() == sign)
        answer.append(points)
    return answer


def diagram(polys, direction):
    """Exact regular diagram from ordered polygons alone, no surface oracle."""
    B.count('diagrams', 'max_diagrams')
    d = tuple(Q(x) for x in direction)
    e1 = cross(d, (Q(1), Q(), Q()))
    e2 = cross(d, e1)
    if dot(e1, e1) == Q() or dot(e2, e2) == Q():
        raise Refused('RefusedProjectionCollapse')
    B.check('projection-positive-basis', dot(cross(e1, e2), d) > Q())
    edges = []
    for i, points in enumerate(polys):
        if len(points) != 4:
            raise Refused('InvalidPolygon')
        steps = [sub(points[(j+1)%4], points[j]) for j in range(4)]
        n = cross(steps[0], steps[1])
        # Enforce an embedded rectangle, rather than assuming arbitrary input
        # polygons have no self-crossings. Its non-edge-on projection is convex.
        if (dot(n, n) == Q() or dot(steps[0], steps[1]) != Q() or
                steps[2] != tuple(-x for x in steps[0]) or
                steps[3] != tuple(-x for x in steps[1])):
            raise Refused('InvalidPolygon')
        if dot(n, d) == Q():
            raise Refused('RefusedProjectionCollapse')
        for j, p in enumerate(points):
            a = (dot(p, e1), dot(p, e2))
            tangent = (dot(steps[j], e1), dot(steps[j], e2))
            if tangent == (Q(), Q()):
                raise Refused('RefusedProjectionCollapse')
            edges.append((i, j, p, steps[j], a, tangent))
    events = []
    for first, second in itertools.combinations(edges, 2):
        B.step()
        i, ei, p, v, a, av = first
        j, ej, q, w, b, bw = second
        if i == j:
            continue  # Injective affine projection of the checked rectangle.
        delta = sub(b, a)
        denominator = det(av, bw)
        if denominator == Q():
            if det(delta, av) == Q():
                axis = 0 if av[0] != Q() else 1
                aa = sorted((a[axis], a[axis]+av[axis]))
                bb = sorted((b[axis], b[axis]+bw[axis]))
                if max(aa[0], bb[0]) <= min(aa[1], bb[1]):
                    raise Refused('RefusedProjectedOverlap')
            continue
        s, t = det(delta, bw)/denominator, det(delta, av)/denominator
        if not (Q() <= s <= Q(1) and Q() <= t <= Q(1)):
            continue
        if s in (Q(), Q(1)) or t in (Q(), Q(1)):
            raise Refused('RefusedVertexContact')
        point_p = tuple(x+s*y for x, y in zip(p, v))
        point_q = tuple(x+t*y for x, y in zip(q, w))
        height = dot(sub(point_p, point_q), d).sign()
        if not height:
            raise Refused('RefusedLinkContact')
        projected = tuple(x+s*y for x, y in zip(a, av))
        if any(projected == c['projected'] for c in events):
            raise Refused('RefusedTripleProjection')
        over, under = ((i, ei, s), (j, ej, t)) if height > 0 else ((j, ej, t), (i, ei, s))
        sign = dot(cross(v, w) if height > 0 else cross(w, v), d).sign()
        B.check('crossing-sign-2D-vs-3D', sign == height*denominator.sign())
        events.append({'id': len(events), 'over': over, 'under': under,
                       'sign': sign, 'projected': projected,
                       'over_point': point_p if height > 0 else point_q,
                       'under_point': point_q if height > 0 else point_p})
        if len(events) > B.rules['max_crossings_per_diagram']:
            raise Exhausted('crossings')
    return events


# Series with constant term one, followed by three linear and nine quadratic
# coefficients. All higher degrees are discarded; variables do not commute.
IDENTITY = ((0, 0, 0), ((0, 0, 0), (0, 0, 0), (0, 0, 0)))


def generator(i):
    return (tuple(int(k == i) for k in range(3)), IDENTITY[1])


def multiply(a, b):
    B.step()
    return (tuple(a[0][i]+b[0][i] for i in range(3)),
            tuple(tuple(a[1][i][j]+b[1][i][j]+a[0][i]*b[0][j]
                        for j in range(3)) for i in range(3)))


def inverse(a):
    B.step()
    return (tuple(-v for v in a[0]),
            tuple(tuple(-a[1][i][j]+a[0][i]*a[0][j] for j in range(3))
                  for i in range(3)))


def evaluate(word, images):
    if len(word) > B.rules['max_word_letters']:
        raise Exhausted('word letters')
    result = IDENTITY
    for a, sign in word:
        image = images[a]
        result = multiply(result, image if sign == 1 else inverse(image))
    return result


def ordered_pairs(word):
    linear, quadratic = [0]*3, [[0]*3 for _ in range(3)]
    for p, (i, sign) in enumerate(word):
        B.step()
        linear[i] += sign
        if sign == -1:
            quadratic[i][i] += 1  # X_i^2 in (1+X_i)^-1.
        for j, other in word[p+1:]:
            B.step()
            quadratic[i][j] += sign*other
    return tuple(linear), tuple(tuple(row) for row in quadratic)


def reversed_word(word):
    return [(a, -sign) for a, sign in reversed(word)]


def longitudes(events):
    B.count('longitudes', 'max_longitude_computations')
    under = [sorted((c for c in events if c['under'][0] == i),
                    key=lambda c: c['under'][1:]) for i in range(3)]
    sizes = [max(1, len(v)) for v in under]
    offsets = [0, sizes[0], sizes[0]+sizes[1]]
    components = [i for i in range(3) for _ in range(sizes[i])]
    n = len(components)

    def at(i, location):
        ordinal = sum(c['under'][1:] < location for c in under[i]) % sizes[i]
        return offsets[i]+ordinal

    words = [[] for _ in range(3)]
    relations = []
    for i in range(3):
        for ordinal, c in enumerate(under[i]):
            over = at(c['over'][0], c['over'][1:])
            words[i].append((over, c['sign']))
            relations.append({'crossing': c['id'], 'in': offsets[i]+ordinal,
                              'out': offsets[i]+(ordinal+1)%sizes[i],
                              'over': over, 'sign': c['sign']})

    linking = [[0]*3 for _ in range(3)]
    for i in range(3):
        for a, sign in words[i]:
            linking[i][components[a]] += sign
    for i, j in itertools.combinations(range(3), 2):
        total = sum(c['sign'] for c in events if {c['under'][0], c['over'][0]} == {i, j})
        B.check('pairwise-two-undercrossing-readings',
                2*linking[i][j] == total == 2*linking[j][i])
    if any(v for row in linking for v in row):
        raise Refused('RefusedPairwiseNonzero')

    prefixes, representatives = [], []
    for i in range(3):
        for ordinal in range(sizes[i]):
            prefix = words[i][:ordinal]
            prefixes.append(prefix)
            v = [(components[a], sign) for a, sign in prefix]
            representatives.append(reversed_word(v)+[(i, 1)]+v)
    meridians = [generator(i) for i in range(3)]
    eta2 = [evaluate(w, meridians) for w in representatives]
    for a in range(n):
        prefix = evaluate(prefixes[a], eta2)
        eta3 = multiply(multiply(inverse(prefix), meridians[components[a]]), prefix)
        B.check('Chen-next-iteration-degree-two', eta2[a] == eta3)
    for r in relations:
        b = eta2[r['over']]
        if r['sign'] == -1:
            b = inverse(b)
        rhs = multiply(multiply(inverse(b), eta2[r['in']]), b)
        B.check('Wirtinger-relation-including-closing', eta2[r['out']] == rhs)

    expanded, series = [], []
    for i in range(3):
        w = []
        for a, sign in words[i]:
            w.extend(representatives[a] if sign == 1 else reversed_word(representatives[a]))
            if len(w) > B.rules['max_word_letters']:
                raise Exhausted('expanded longitude letters')
        value = evaluate(w, meridians)
        B.check('explicit-word-vs-arc-series', value == evaluate(words[i], eta2))
        B.check('Magnus-vs-signed-ordered-pairs', value == ordered_pairs(w))
        B.check('longitude-zero-linear', value[0] == (0, 0, 0))
        B.check('longitude-zero-diagonal', all(value[1][j][j] == 0 for j in range(3)))
        B.check('longitude-antisymmetry', all(value[1][j][k] == -value[1][k][j]
                                               for j in range(3) for k in range(3)))
        expanded.append(w)
        series.append(value)
    cyclic = [series[2][1][0][1], series[0][1][1][2], series[1][1][2][0]]
    B.check('three-cyclic-longitudes', len(set(cyclic)) == 1)
    return {'status': 'VerifiedForScope', 'mu': cyclic[0], 'pairwise': linking,
            'arc_components': components, 'under_event_order': [[c['id'] for c in v] for v in under],
            'relations': relations, 'arc_prefixes': prefixes,
            'arc_representatives': representatives, 'arc_Magnus': eta2,
            'preferred_longitudes_in_arcs': words, 'preferred_longitudes_in_meridians': expanded,
            'longitude_Magnus': series, 'cyclic_mu': cyclic, 'self_writhe': [0, 0, 0]}


def run(contract, root, result):
    raw = bounded_read(root/contract['inputs']['path'], B.rules['max_input_bytes'])
    B.check('fixture-bytes-pinned', sha(raw) == contract['inputs']['sha256'])
    fixtures = json.loads(raw)['cases']
    B.check('fixed-fixture-count', len(fixtures) == 22)
    cases = result['cases']
    for fixture in fixtures:
        row = {'name': fixture['name'], 'order': fixture['order'], 'views': []}
        cases.append(row)  # Keep partial evidence if a later assertion fails.
        accepted = fixture['name'] not in ('missing-component', 'boundary-contact', 'nonzero-pairwise', 'invalid-normal')
        if not accepted:
            try:
                p = polygons(fixture['inputs'], fixture['order'])
                c = diagram(p, contract['conventions']['projection_directions'][0])
                longitudes(c)
            except Refused as error:
                row['refusal'] = str(error)
            else:
                raise AssertionError('inherited-control-accepted')
            desired = {'missing-component': {'UnknownCoverage'},
                       'boundary-contact': {'RefusedLinkContact', 'RefusedVertexContact', 'RefusedProjectedOverlap', 'RefusedTripleProjection'},
                       'nonzero-pairwise': {'RefusedPairwiseNonzero'},
                       'invalid-normal': {'InvalidDomain'}}[fixture['name']]
            B.check('inherited-control-'+fixture['name'], row['refusal'] in desired)
            continue
        p = polygons(fixture['inputs'], fixture['order'])
        row['polygons'] = dump(p)
        for direction in contract['conventions']['projection_directions']:
            c = diagram(p, direction)
            view = {'direction': direction, 'crossings': dump(c)}
            row['views'].append(view)
            answer = longitudes(c)
            view['longitude'] = dump(answer)
            # This is the first access to the predicted invariant for this view.
            view['surface_mu'] = fixture['result']['mu']
            B.check('longitude-matches-pinned-surface-'+fixture['name'],
                    answer['mu'] == view['surface_mu'])
            rotated = [v[1:]+v[:1] for v in p]
            moved_events = diagram(rotated, direction)
            moved = longitudes(moved_events)
            view['rotated_basepoints'] = {'crossings': dump(moved_events), 'longitude': dump(moved)}
            B.check('changed-basepoints-same-mu', moved['mu'] == answer['mu'])
        B.check('two-projections-same-mu', row['views'][0]['longitude']['mu'] == row['views'][1]['longitude']['mu'])
    p = polygons(fixtures[0]['inputs'], fixtures[0]['order'])
    try:
        diagram(p, (1, 0, 0))
    except Refused as error:
        result['edge_on_control'] = str(error)
    else:
        raise AssertionError('edge-on-projection-accepted')
    B.check('edge-on-control', result['edge_on_control'] == 'RefusedProjectionCollapse')


def main():
    global B, Q
    cli = argparse.ArgumentParser()
    cli.add_argument('--output', required=True)
    cli.add_argument('--compare')
    args = cli.parse_args()
    here = Path(__file__).resolve().parent
    root = here.parent.parent
    started = time.monotonic()
    raw_contract = bounded_read(here/'contract.json', 32768)
    contract = json.loads(raw_contract)
    limits = contract['budget']
    result = {'schema': 'adva.external.borromean-longitude-report.v0',
              'status': 'UnknownResource', 'native_authority': 'NotGranted',
              'contract_sha256': sha(raw_contract), 'source_sha256': sha(Path(__file__).read_bytes()),
              'input_sha256': contract['inputs']['sha256'],
              'shared_arithmetic_sha256': contract['shared_arithmetic']['sha256'],
              'cases': [], 'limits_installed': False}
    B = Budget(limits)
    try:
        if platform.system() != 'Linux':
            raise Exhausted('Linux limits required')
        resource.setrlimit(resource.RLIMIT_AS, (limits['address_space_bytes'], limits['address_space_bytes']))
        resource.setrlimit(resource.RLIMIT_CPU, (limits['per_attempt_cpu_soft_seconds'], limits['per_attempt_cpu_hard_seconds']))
        def alarm_handler(signum, frame):
            raise Exhausted('process alarm or CPU limit')
        signal.signal(signal.SIGALRM, alarm_handler)
        signal.signal(signal.SIGXCPU, alarm_handler)
        signal.alarm(limits['per_attempt_alarm_seconds'])
        result['limits_installed'] = True
        module_path = root/contract['shared_arithmetic']['path']
        module_bytes = bounded_read(module_path, limits['max_input_bytes'])
        B.check('arithmetic-module-pinned', sha(module_bytes) == contract['shared_arithmetic']['sha256'])
        # Execute exactly the checked bytes, avoiding a read/import TOCTOU.
        import types
        arithmetic = types.ModuleType('pinned_external_quadratic_arithmetic')
        exec(compile(module_bytes, str(module_path), 'exec'), arithmetic.__dict__)
        Q = arithmetic.Q
        arithmetic.B = B
        run(contract, root, result)
        if args.compare:
            prior = json.loads(bounded_read(Path(args.compare), limits['max_report_bytes']))
            B.check('fresh-process-mathematical-replay', prior['status'] == 'Passed' and
                    prior['cases'] == result['cases'] and
                    prior['edge_on_control'] == result['edge_on_control'] and
                    prior['contract_sha256'] == result['contract_sha256'] and
                    prior['source_sha256'] == result['source_sha256'])
        result['status'] = 'Passed'
    except Exhausted as error:
        result['status'], result['reason'] = 'UnknownResource', str(error)
    except Refused as error:
        result['status'], result['reason'] = 'Refused', str(error)
    except Exception as error:
        result['status'], result['reason'] = 'Failed', type(error).__name__+': '+str(error)
    result['checks'] = B.checks
    result['cost'] = {'work_units': B.work, 'assertions': len(B.checks),
                      'diagrams': B.diagrams, 'longitude_computations': B.longitudes,
                      'pre_publication_seconds': time.monotonic()-started,
                      'peak_rss_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    encoded = (json.dumps(result, indent=2, sort_keys=True)+'\n').encode()
    if len(encoded) > limits['max_report_bytes']:
        raise Exhausted('report cap; partial result not published')
    with Path(args.output).open('xb') as destination:
        destination.write(encoded)
    print(json.dumps({'status': result['status'], 'reason': result.get('reason'),
                      'report_bytes': len(encoded), 'elapsed_including_publication': time.monotonic()-started,
                      'cost': result['cost']}))
    return 0 if result['status'] == 'Passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
