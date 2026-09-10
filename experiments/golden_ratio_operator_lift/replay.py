"""Typed operator lift of a pinned scalar affine word; external evidence only."""
import argparse
from fractions import Fraction as F
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import time

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = Path(__file__).with_name('contract.json')
started = time.perf_counter()
work = 0
checks = []


def tick(n=1):
    global work
    work += n
    if work > 20000 or time.perf_counter() - started > 9:
        raise TimeoutError('finite work or wall budget exhausted')


def check(name, condition):
    tick()
    if not condition:
        raise ValueError(name)
    checks.append(name)


def matrix(rows):
    return tuple(tuple(F(x) for x in row) for row in rows)


def eye(n):
    return matrix([[int(i == j) for j in range(n)] for i in range(n)])


def mm(a, b):
    n = len(a)
    tick(n**3)
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(n))
                       for j in range(n)) for i in range(n))


def inverse(a):
    n = len(a)
    rows = [list(a[i])+list(eye(n)[i]) for i in range(n)]
    for j in range(n):
        tick(n**2)
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        if pivot is None:
            raise ZeroDivisionError('noninvertible operator')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        d = rows[j][j]
        rows[j] = [x/d for x in rows[j]]
        for i in range(n):
            if i != j:
                d = rows[i][j]
                rows[i] = [x-d*y for x, y in zip(rows[i], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def affine(a, v):
    n = len(a)
    return tuple(tuple(a[i])+tuple([v[i]]) for i in range(n)) + \
        (tuple(F(0) for _ in range(n))+(F(1),),)


def word_action(a, v, word):
    n = len(a)
    zero = (F(0),)*n
    letters = {'a': affine(a, zero), 'A': affine(inverse(a), zero),
               'b': affine(eye(n), v), 'B': affine(eye(n), tuple(-x for x in v))}
    out = eye(n+1)
    for letter in word:
        out = mm(out, letters[letter])
    return out


def polynomial(a):
    squared = mm(a, a)
    return tuple(tuple(squared[i][j]-3*a[i][j]+int(i == j)
                       for j in range(len(a))) for i in range(len(a)))


def basis_receipt(dimension, observations):
    if len({i for i, _ in observations}) != len(observations):
        return 'InvalidDuplicateDirection'
    if any(not ok for _, ok in observations):
        return 'Refuted'
    if {i for i, _ in observations} != set(range(dimension)):
        return 'UnknownCoverage'
    return 'ClosedForAllTranslationsByLinearity'


def run():
    contract = json.loads(CONTRACT.read_text())
    source = ROOT/contract['source_path']
    check('source-pin', hashlib.sha256(source.read_bytes()).hexdigest() == contract['source_sha256'])
    spec = importlib.util.spec_from_file_location('golden_lift_source', source)
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    word = contract['word']
    check('delivered-polynomial', tool.word_residual_polynomial(word) == {2: -1, 1: 3, 0: -1})
    for exponent in (2, -2):
        check('scalar-root-'+str(exponent), tool.affine_word(tool.PHI**exponent, word) == tool.IDENTITY)
    h = matrix([[1, 1], [1, 2]])
    c = matrix([[2, 0], [0, 1]])
    inputs = [('H', h), ('changed-frame', mm(mm(c, h), inverse(c))),
              ('non-root', matrix([[2, 0], [0, F(1, 2)]])),
              ('hidden-third-direction', matrix([[1, 1, 0], [1, 2, 0], [0, 0, 1]]))]
    cases = []
    for name, a in inputs:
        case_started = time.perf_counter()
        n = len(a)
        check(name+'-actual-inverse', mm(a, inverse(a)) == eye(n))
        p = polynomial(a)
        observations = []
        vectors = []
        for j in range(n):
            v = tuple(F(int(i == j)) for i in range(n))
            out = word_action(a, v, word)
            residual = tuple(-p[i][j] for i in range(n))
            check(name+'-direct-versus-polynomial-'+str(j), out == affine(eye(n), residual))
            observations.append((j, out == eye(n+1)))
            vectors.append({'basis_index': j, 'translation_residual': residual,
                            'whole_affine_matrix': out, 'closed': out == eye(n+1)})
        result = basis_receipt(n, observations)
        check(name+'-expected', result == ('ClosedForAllTranslationsByLinearity'
              if name in ('H', 'changed-frame') else 'Refuted'))
        cases.append({'name': name, 'operator': a, 'polynomial_residual': p,
                      'basis_results': vectors, 'judgment': result})
        if name == 'hidden-third-direction':
            partial = basis_receipt(n, observations[:2])
            check('partial-two-directions-unknown', partial == 'UnknownCoverage')
            check('third-direction-counterexample', vectors[2]['translation_residual'] == (0, 0, 1))
            cases[-1]['first_two_only'] = partial
        if name == 'non-root':
            check('zero-probe-degeneracy', word_action(a, (F(0),)*n, word) == eye(n+1))
        cases[-1]['construction_validation_seconds'] = time.perf_counter()-case_started
    check('H-is-not-identity', h != eye(2))
    check('duplicate-basis-refused', basis_receipt(2, [(0, True), (0, True)]) == 'InvalidDuplicateDirection')
    try:
        inverse(matrix([[0, 0], [0, 0]]))
    except ZeroDivisionError:
        check('singular-operator-refused', True)
    else:
        check('singular-operator-refused', False)
    return {'cases': cases, 'word': word,
            'identity': 'W(L,v)(x)=x-(L^2-3L+I)v',
            'scope': 'finite checks plus a separately stated elementary algebraic derivation',
            'native_admission': 'NotGranted', 'history': word,
            'residuals': ['No native importer or certificate', 'No equality of Mobius and vector-affine actions',
                          'No general receipt calculus, physical metric, holonomy or universal grammar claim']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    target = Path(parser.parse_args().output)
    if target.exists() or not target.parent.is_dir():
        raise SystemExit('fresh output in an existing directory required')
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
    try:
        result = dict(status='Passed', **run())
    except TimeoutError as exc:
        result = {'status': 'Unknown', 'reason': str(exc)}
    except (ValueError, ZeroDivisionError, OSError) as exc:
        result = {'status': 'Invalid', 'reason': str(exc)}
    result['checks'] = checks
    result['work_units'] = work
    result['pins'] = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                      for p in (CONTRACT, Path(__file__))}
    result['cost'] = {'construction_validation_seconds': time.perf_counter()-started,
                      'peak_RSS_KiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      'search_candidates': 0, 'child_processes': 0,
                      'word_formation_seconds': None,
                      'word_formation_note': 'Human/agent algebra and coding time not separately measured',
                      'final_write_seconds': None}
    t = time.perf_counter()
    payload = json.dumps(result, default=str, indent=2)+'\n'
    assert len(payload.encode()) <= 65536
    decoded = json.loads(payload)
    assert json.dumps(decoded, indent=2)+'\n' == payload
    result['cost']['serialization_seconds'] = time.perf_counter()-t
    payload = json.dumps(result, default=str, indent=2)+'\n'
    with target.open('x') as f:
        f.write(payload)
    print(json.dumps({'status': result['status'], 'checks': len(checks), 'work_units': work,
                      'cost': result['cost']}))
    return 0 if result['status'] == 'Passed' else 2


if __name__ == '__main__':
    raise SystemExit(main())
