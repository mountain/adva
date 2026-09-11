#!/usr/bin/env python3
"""Exact external surface-system audit. See contract.json before execution.

Authored by ChatGPT (OpenAI), through Mingli Yuan's account as an authorized
proxy. This imports Mellor--Melvin's theorem, not native Adva authority.
"""
import argparse
import ast
import hashlib
import itertools
import json
import os
from pathlib import Path
import platform
import resource
import signal
import time
from fractions import Fraction as F
from functools import total_ordering


class Exhausted(Exception):
    pass


class Domain(Exception):
    pass


class Budget:
    def __init__(self, rules):
        self.rules = rules
        self.start = time.monotonic()
        self.work = self.assertions = self.judgments = 0
        self.checks = []

    def step(self, n=1):
        self.work += n
        if self.work > self.rules['max_work_units'] or time.monotonic() - self.start >= 5:
            raise Exhausted('work or mathematical-phase deadline')

    def check(self, name, condition):
        self.step()
        self.assertions += 1
        if self.assertions > self.rules['max_assertions']:
            raise Exhausted('assertions')
        self.checks.append({'name': name, 'passed': bool(condition)})
        if not condition:
            raise AssertionError(name)


B = None


def tick():
    if B is not None:
        B.step()


@total_ordering
class Q:
    """a+b sqrt(5), independent of the predecessor's (p+q sqrt(5))/2 class."""
    __slots__ = ('a', 'b')

    def __init__(self, a=0, b=0):
        self.a, self.b = F(a), F(b)

    @staticmethod
    def of(x):
        return x if isinstance(x, Q) else Q(x)

    def __add__(self, other):
        tick(); other = Q.of(other)
        return Q(self.a + other.a, self.b + other.b)

    __radd__ = __add__

    def __neg__(self):
        tick()
        return Q(-self.a, -self.b)

    def __sub__(self, other):
        return self + -Q.of(other)

    def __mul__(self, other):
        tick(); other = Q.of(other)
        return Q(self.a * other.a + 5 * self.b * other.b,
                 self.a * other.b + self.b * other.a)

    __rmul__ = __mul__

    def __truediv__(self, other):
        tick(); other = Q.of(other)
        norm = other.a * other.a - 5 * other.b * other.b
        if not norm:
            raise ZeroDivisionError('quadratic field zero')
        return self * Q(other.a / norm, -other.b / norm)

    def sign(self):
        tick()
        a, b = self.a, self.b
        if not b:
            return (a > 0) - (a < 0)
        if not a:
            return (b > 0) - (b < 0)
        if a > 0 and b > 0:
            return 1
        if a < 0 and b < 0:
            return -1
        difference = a*a - 5*b*b
        return ((difference > 0) - (difference < 0)) * (1 if a > 0 else -1)

    def __eq__(self, other):
        other = Q.of(other)
        return self.a == other.a and self.b == other.b

    def __lt__(self, other):
        return (self - other).sign() < 0

    def __abs__(self):
        return -self if self.sign() < 0 else self

    def dump(self):
        return [str(self.a), str(self.b)]


Z, O, PHI = Q(), Q(1), Q(F(1, 2), F(1, 2))
NAMES = ('z0', 'x0', 'y0')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def cross(a, b):
    return tuple(a[(i+1) % 3]*b[(i+2) % 3] - a[(i+2) % 3]*b[(i+1) % 3]
                 for i in range(3))


def sub(a, b):
    return tuple(x-y for x, y in zip(a, b))


def dot(a, b):
    return sum((x*y for x, y in zip(a, b)), Z)


def normal(rect):
    return tuple(Q(rect['normal'] if i == rect['fixed'] else 0) for i in range(3))


def boundary(rect):
    k = rect['fixed']; u, v = (k+1) % 3, (k+2) % 3
    signs = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    if rect['normal'] == -1:
        signs = [signs[0], *reversed(signs[1:])]
    points = []
    for su, sv in signs:
        p = list(rect['center'])
        p[u] = p[u] + su*rect['extents'][u]
        p[v] = p[v] + sv*rect['extents'][v]
        points.append(tuple(p))
    B.check('boundary-normal-orientation',
            dot(cross(sub(points[1], points[0]), sub(points[2], points[1])), normal(rect)) > Z)
    return [(points[i], points[(i+1) % 4]) for i in range(4)]


def location(point, rect):
    if point[rect['fixed']] != rect['center'][rect['fixed']]:
        return 'outside'
    offsets = [abs(point[i]-rect['center'][i]) for i in range(3) if i != rect['fixed']]
    sizes = [rect['extents'][i] for i in range(3) if i != rect['fixed']]
    if any(x > h for x, h in zip(offsets, sizes)):
        return 'outside'
    return 'boundary' if any(x == h for x, h in zip(offsets, sizes)) else 'interior'


def coplanar_overlap(start, end, disk):
    low, high = Z, O
    for axis, extent in disk['extents'].items():
        change = end[axis]-start[axis]
        lower, upper = disk['center'][axis]-extent, disk['center'][axis]+extent
        if change == Z:
            if start[axis] < lower or start[axis] > upper:
                return False
        else:
            first, second = (lower-start[axis])/change, (upper-start[axis])/change
            low, high = max(low, min(first, second)), min(high, max(first, second))
    return low <= high


def boundary_events(curve, disks, name):
    events = []
    for edge, (start, end) in enumerate(boundary(curve)):
        local = []
        for other, disk in disks.items():
            if other == name:
                continue
            B.step()
            axis = disk['fixed']; delta = end[axis]-start[axis]
            if delta == Z:
                if start[axis] == disk['center'][axis] and coplanar_overlap(start, end, disk):
                    raise Domain('RefusedNongenericOrBoundaryContact')
                continue
            parameter = (disk['center'][axis]-start[axis])/delta
            if parameter < Z or parameter > O:
                continue
            point = tuple(a+parameter*(b-a) for a, b in zip(start, end))
            where = location(point, disk)
            if where == 'outside':
                continue
            if where == 'boundary' or parameter == Z or parameter == O:
                raise Domain('RefusedNongenericOrBoundaryContact')
            local.append((parameter, other, disk['normal']*delta.sign(), point))
        local.sort(key=lambda row: row[0])
        if any(a[0] == b[0] for a, b in zip(local, local[1:])):
            raise Domain('RefusedNongenericOrBoundaryContact')
        for parameter, other, sign, point in local:
            events.append({'edge': edge, 'parameter': parameter.dump(), 'surface': other,
                           'sign': sign, 'point': [x.dump() for x in point]})
    return events


def pair_coefficient(word, first, second):
    return sum(sa*sb for i, (a, sa) in enumerate(word) for b, sb in word[i+1:]
               if a == first and b == second)


def magnus(word):
    series = {(): 1}
    for name, sign in word:
        factor = {(): 1, (name,): sign}
        if sign == -1:
            factor[(name, name)] = 1
        out = {}
        for left, a in series.items():
            for right, b in factor.items():
                B.step()
                if len(left)+len(right) <= 2:
                    out[left+right] = out.get(left+right, 0)+a*b
        series = {key: val for key, val in out.items() if val}
    return series


def audit(rectangles, order=NAMES):
    B.judgments += 1
    if B.judgments > B.rules['max_judgments']:
        raise Exhausted('judgments')
    if set(rectangles) != set(NAMES) or len(order) != 3 or set(order) != set(NAMES):
        raise Domain('UnknownCoverage')
    if {r['fixed'] for r in rectangles.values()} != {0, 1, 2}:
        raise Domain('InvalidDomain')
    for rect in rectangles.values():
        k = rect['fixed']
        if rect['normal'] not in (-1, 1) or set(rect['extents']) != {0, 1, 2}-{k}:
            raise Domain('InvalidDomain')
        if any(h <= Z for h in rect['extents'].values()):
            raise Domain('InvalidDomain')
    events = {name: boundary_events(rectangles[name], rectangles, name) for name in NAMES}
    words = {name: [(row['surface'], row['sign']) for row in rows] for name, rows in events.items()}
    linking = {a: {b: sum(s for x, s in words[a] if x == b) for b in NAMES if b != a}
               for a in NAMES}
    for a, b in itertools.combinations(NAMES, 2):
        B.check('pairwise-direction-agreement', linking[a][b] == linking[b][a])
    if any(val for row in linking.values() for val in row.values()):
        return {'status': 'RefusedPairwiseNonzero', 'linking': linking, 'events': events}
    expansions = {name: magnus(word) for name, word in words.items()}
    terms = []
    for shift in range(3):
        i, j, k = order[shift:]+order[:shift]
        coefficient = pair_coefficient(words[k], i, j)
        B.check('ordered-pair-vs-magnus', coefficient == expansions[k].get((i, j), 0))
        for offset in range(len(words[k])):
            shifted = words[k][offset:]+words[k][:offset]
            B.check('basepoint-invariance', pair_coefficient(shifted, i, j) == coefficient)
        terms.append({'indices': [i, j, k], 'value': coefficient})
    point = [Z, Z, Z]
    for rect in rectangles.values():
        point[rect['fixed']] = rect['center'][rect['fixed']]
    locations = [location(point, rectangles[name]) for name in order]
    if 'outside' in locations:
        t = 0
    elif 'boundary' in locations:
        raise Domain('RefusedNongenericOrBoundaryContact')
    else:
        normals = [normal(rectangles[name]) for name in order]
        t = dot(cross(normals[0], normals[1]), normals[2]).sign()
    m = sum(term['value'] for term in terms)
    return {'status': 'VerifiedForScope', 'linking': linking, 'events': events,
            'words': {name: [[a, s] for a, s in word] for name, word in words.items()},
            'm_terms': terms, 'm': m, 't': t, 'mu': m-t,
            'triple_point': [x.dump() for x in point] if t else None,
            'order': list(order), 'native_authority': 'NotGranted'}


def serialize(rectangles):
    return {name: {'fixed': r['fixed'], 'normal': r['normal'],
                   'center': [x.dump() for x in r['center']],
                   'extents': {str(k): x.dump() for k, x in r['extents'].items()}}
            for name, r in rectangles.items()}


def deserialize(data):
    def number(pair):
        if not isinstance(pair, list) or len(pair) != 2:
            raise Domain('InvalidCoordinate')
        parts = [F(x) for x in pair]
        if any(max(x.numerator.bit_length(), x.denominator.bit_length()) >
               B.rules['input_coefficient_bits'] for x in parts):
            raise Domain('InvalidCoordinate')
        return Q(*parts)
    return {name: {'fixed': r['fixed'], 'normal': r['normal'],
                   'center': tuple(number(x) for x in r['center']),
                   'extents': {int(k): number(x) for k, x in r['extents'].items()}}
            for name, r in data.items()}


def read_rectangles(raw):
    tree = ast.parse(raw)
    fn = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
              and node.name == 'golden_rectangle_checks')
    assignment = next(node for node in fn.body if isinstance(node, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'rectangles' for t in node.targets))
    def decode(node):
        if isinstance(node, ast.Name) and node.id in ('ZERO', 'ONE', 'PHI'):
            return {'ZERO': Z, 'ONE': O, 'PHI': PHI}[node.id]
        if isinstance(node, ast.Constant) and type(node.value) in (int, str):
            return node.value
        if isinstance(node, ast.Tuple):
            return tuple(decode(x) for x in node.elts)
        if isinstance(node, ast.Dict):
            return {decode(k): decode(v) for k, v in zip(node.keys, node.values)}
        raise Domain('RefusedSourceLiteral')
    rectangles = decode(assignment.value)
    for rect in rectangles.values():
        B.check('source-plane-center', rect.pop('value') == rect['center'][rect['fixed']])
        rect['normal'] = 1
    return rectangles


def copy_rectangles(rectangles):
    return deserialize(serialize(rectangles))


def run_suite(contract, root, report):
    raw = (root/contract['source']['path']).read_bytes()
    B.check('source-byte-cap', len(raw) <= B.rules['max_input_bytes'])
    B.check('source-sha256', sha(raw) == contract['source']['sha256'])
    golden = read_rectangles(raw)
    B.check('quadratic-field-identities', Q(0, 1)*Q(0, 1) == Q(5) and PHI*PHI == PHI+O)
    B.check('golden-positive-embedding', O < PHI < Q(2) and PHI/PHI == O)

    def judge(rectangles, order):
        try:
            return audit(rectangles, order)
        except Domain as exc:
            return {'status': str(exc)}

    def case(name, rectangles, expected, order=NAMES):
        result = judge(rectangles, order)
        entry = {'name': name, 'inputs': serialize(rectangles), 'order': list(order), 'result': result}
        report['cases'].append(entry)
        if isinstance(expected, tuple):
            B.check(name+'-expected', result.get('status') == 'VerifiedForScope' and
                    tuple(result.get(k) for k in ('m', 't', 'mu')) == expected)
        else:
            B.check(name+'-expected', result.get('status') == expected)
        encoded = json.dumps(entry, sort_keys=True)
        restored = json.loads(encoded)
        replay = judge(deserialize(restored['inputs']), tuple(restored['order']))
        B.check(name+'-serialized-input-replay', replay == restored['result'])

    case('golden', golden, (0, 1, -1))
    scaled = copy_rectangles(golden)
    for r in scaled.values():
        r['extents'] = {i: 2*x for i, x in r['extents'].items()}
    case('scaled-by-two', scaled, (0, 1, -1))
    translated = copy_rectangles(golden)
    for r in translated.values():
        r['center'] = tuple(x+Q(i+1) for i, x in enumerate(r['center']))
    case('common-translation', translated, (0, 1, -1))
    rational = copy_rectangles(golden)
    for r in rational.values():
        r['extents'] = {i: Q(2) if x == PHI else x for i, x in r['extents'].items()}
    case('rational-aspect-two', rational, (0, 1, -1))
    nested = copy_rectangles(golden)
    for name, size in zip(NAMES, (3, 2, 1)):
        nested[name]['extents'] = {i: Q(size) for i in nested[name]['extents']}
    case('concentric-squares-counterexample', nested, (1, 1, 0))
    unlink = copy_rectangles(golden)
    unlink['y0']['center'] = (Z, Q(10), Z)
    case('separated-third-component', unlink, (0, 0, 0))
    for signs in itertools.product((-1, 1), repeat=3):
        if signs == (1, 1, 1):
            continue
        oriented = copy_rectangles(golden)
        for name, sign in zip(NAMES, signs):
            oriented[name]['normal'] = sign
        product = signs[0]*signs[1]*signs[2]
        case('normals-'+','.join(map(str, signs)), oriented, (0, product, -product))
    for order in itertools.permutations(NAMES):
        if order == NAMES:
            continue
        inversions = sum(NAMES.index(order[i]) > NAMES.index(order[j])
                         for i in range(3) for j in range(i+1, 3))
        parity = (-1)**inversions
        case('order-'+','.join(order), golden, (0, parity, -parity), order)
    case('missing-component', {name: golden[name] for name in NAMES[:2]}, 'UnknownCoverage')
    contact = copy_rectangles(golden)
    for r in contact.values():
        r['extents'] = {i: O for i in r['extents']}
    case('boundary-contact', contact, 'RefusedNongenericOrBoundaryContact')
    linked = copy_rectangles(golden)
    linked['x0']['center'] = (Z, Q(F(5, 2)), Z)
    linked['x0']['extents'] = {1: O, 2: Q(2)}
    linked['y0']['center'] = (Z, Q(10), Z)
    case('nonzero-pairwise', linked, 'RefusedPairwiseNonzero')
    invalid = copy_rectangles(golden)
    invalid['z0']['normal'] = 0
    case('invalid-normal', invalid, 'InvalidDomain')


def main():
    global B
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    parser.add_argument('--compare')
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    contract_bytes = (here/'contract.json').read_bytes()
    contract = json.loads(contract_bytes)
    rules = contract['budget']
    target = Path(args.output)
    if target.exists():
        raise SystemExit('refusing existing output')
    if platform.system() != 'Linux':
        raise SystemExit('RequiredProcessLimitsUnavailable: this audit requires Linux')
    resource.setrlimit(resource.RLIMIT_AS, (rules['address_space_bytes'], rules['address_space_bytes']))
    resource.setrlimit(resource.RLIMIT_CPU,
                       (rules['per_attempt_cpu_soft_seconds'], rules['per_attempt_cpu_hard_seconds']))
    signal.alarm(rules['per_attempt_alarm_seconds'])
    B = Budget(rules)
    report = {'schema': 'adva.external.borromean-surface-audit.v0', 'status': 'Running',
              'contract_sha256': sha(contract_bytes), 'source_sha256': sha(Path(__file__).read_bytes()),
              'historical_source_sha256': contract['source']['sha256'],
              'cases': [], 'native_authority': 'NotGranted',
              'theorem': contract['imported_theorem'], 'limits_installed': {
                  'address_space_bytes': rules['address_space_bytes'],
                  'cpu_soft_seconds': rules['per_attempt_cpu_soft_seconds'],
                  'cpu_hard_seconds': rules['per_attempt_cpu_hard_seconds'],
                  'alarm_seconds': rules['per_attempt_alarm_seconds']}}
    try:
        run_suite(contract, here.parents[1], report)
        if args.compare:
            path = Path(args.compare)
            if path.stat().st_size > rules['max_report_bytes']:
                raise Exhausted('comparison report size')
            previous = json.loads(path.read_bytes())
            B.check('fresh-process-replay', previous['cases'] == report['cases'] and
                    previous['contract_sha256'] == report['contract_sha256'] and
                    previous['source_sha256'] == report['source_sha256'])
        report['status'] = 'Passed'
    except Exhausted as exc:
        report['status'], report['error'] = 'UnknownResource', str(exc)
    except Exception as exc:
        report['status'], report['error'] = 'Failed', type(exc).__name__+': '+str(exc)
    report['checks'] = B.checks
    report['cost'] = {'work_units': B.work, 'assertions': B.assertions, 'judgments': B.judgments,
                      'before_serialization_seconds': time.monotonic()-B.start,
                      'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      'platform': platform.platform(), 'exclusions': contract['accounting']}
    payload = (json.dumps(report, indent=2, sort_keys=True)+'\n').encode()
    if len(payload) > rules['max_report_bytes']:
        raise SystemExit('UnknownResource: report byte cap')
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(payload)
    print(json.dumps({'status': report['status'], 'cases': len(report['cases']),
                      'cost': report['cost'], 'error': report.get('error'),
                      'bytes': len(payload), 'total_seconds': time.monotonic()-B.start}))
    signal.alarm(0)
    raise SystemExit(0 if report['status'] == 'Passed' else 1)


if __name__ == '__main__':
    main()
