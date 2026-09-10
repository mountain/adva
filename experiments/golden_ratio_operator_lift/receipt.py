"""Bounded external receipt checker. No native Adva authority is granted."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re
import resource
import time

WORD = 'abbbaBAAB'
MAX_BYTES = 16384


class Invalid(Exception):
    def __init__(self, status, reason):
        self.status, self.reason = status, reason


class Fuel:
    def __init__(self, limit=10000):
        self.used, self.limit = 0, limit

    def tick(self, n=1):
        self.used += n
        if self.used > self.limit:
            raise Invalid('UnknownResource', 'arithmetic work limit')

    def q(self, x):
        self.tick()
        if max(x.numerator.bit_length(), x.denominator.bit_length()) > 512:
            raise Invalid('UnknownResource', 'intermediate rational size')
        return x


def require(ok, status, reason):
    if not ok:
        raise Invalid(status, reason)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)


def fingerprint(context):
    return hashlib.sha256(canonical(context).encode()).hexdigest()


def fields(obj, keys):
    require(type(obj) is dict and set(obj) == set(keys), 'InvalidSchema', 'unexpected object fields')


def parse(raw):
    require(type(raw) is bytes and len(raw) <= MAX_BYTES, 'InvalidSchema', 'input bytes limit/type')
    def pairs(items):
        obj = {}
        for k, v in items:
            require(k not in obj, 'InvalidSchema', 'duplicate JSON key')
            obj[k] = v
        return obj
    return json.loads(raw, object_pairs_hook=pairs)


def rational(x):
    require(type(x) is str and len(x) <= 24, 'InvalidSchema', 'rational string required')
    require(re.fullmatch(r'-?(0|[1-9][0-9]*)(/[1-9][0-9]*)?', x) is not None,
            'InvalidSchema', 'invalid rational syntax')
    q = F(x)
    require(str(q) == x and max(q.numerator.bit_length(), q.denominator.bit_length()) <= 32,
            'InvalidSchema', 'noncanonical or oversized rational')
    return q


def vector(xs, n):
    require(type(xs) is list and len(xs) == n, 'InvalidSchema', 'vector dimension')
    return tuple(map(rational, xs))


def matrix(xs, n):
    require(type(xs) is list and len(xs) == n, 'InvalidSchema', 'matrix dimension')
    return tuple(vector(row, n) for row in xs)


def eye(n):
    return tuple(tuple(F(i == j) for j in range(n)) for i in range(n))


def mv(a, v, fuel):
    return tuple(fuel.q(sum(fuel.q(x*y) for x, y in zip(row, v))) for row in a)


def mm(a, b, fuel):
    cols = [mv(a, col, fuel) for col in zip(*b)]
    return tuple(zip(*cols))


def inverse(a, fuel, status):
    n = len(a)
    rows = [list(a[i])+list(eye(n)[i]) for i in range(n)]
    for j in range(n):
        pivot = next((i for i in range(j, n) if rows[i][j]), None)
        require(pivot is not None, status, 'singular matrix')
        rows[j], rows[pivot] = rows[pivot], rows[j]
        scale = rows[j][j]
        rows[j] = [fuel.q(x/scale) for x in rows[j]]
        for i in range(n):
            if i != j:
                scale = rows[i][j]
                rows[i] = [fuel.q(x-scale*y) for x, y in zip(rows[i], rows[j])]
    return tuple(tuple(row[n:]) for row in rows)


def direct(a, ai, v, fuel):
    """Compose actual maps from right to left, retaining linear and shift parts."""
    linear, shift = eye(len(a)), (F(0),)*len(a)
    for letter in reversed(WORD):
        if letter in 'aA':
            m = a if letter == 'a' else ai
            linear, shift = mm(m, linear, fuel), mv(m, shift, fuel)
        else:
            sign = 1 if letter == 'b' else -1
            shift = tuple(fuel.q(x+sign*y) for x, y in zip(shift, v))
    return linear, shift


def verify(raw, expected_context_sha256, fuel_limit=10000):
    """Caller must choose expected_context_sha256 independently of raw."""
    started = time.perf_counter()
    fuel = Fuel(fuel_limit)
    try:
        result = _verify(raw, expected_context_sha256, fuel)
    except Invalid as e:
        result = {'status': e.status, 'reason': e.reason}
    except (ValueError, TypeError, UnicodeError, RecursionError) as e:
        result = {'status': 'InvalidSchema', 'reason': type(e).__name__}
    result.update(native_admission='NotGranted', work_units=fuel.used,
                  validation_seconds=time.perf_counter()-started)
    return result


def _verify(raw, expected, fuel):
    require(type(expected) is str and re.fullmatch('[0-9a-f]{64}', expected) is not None,
            'InvalidContextBinding', 'receiver context fingerprint required')
    obj = parse(raw)
    fields(obj, ['schema', 'context', 'context_sha256', 'observations'])
    require(obj['schema'] == 'adva.external.operator-lift-receipt.v0', 'InvalidSchema', 'schema version')
    c = obj['context']
    fields(c, ['domain', 'dimension', 'operator', 'basis', 'word', 'composition'])
    n = c['dimension']
    require(type(n) is int and n in (2, 3), 'InvalidSchema', 'dimension must be 2 or 3')
    require(c['domain'] == 'Q-vector-affine' and c['word'] == WORD
            and c['composition'] == 'rightmost-first', 'InvalidSchema', 'unsupported interpretation')
    a = matrix(c['operator'], n)
    # Each listed basis vector is a column, not a matrix row.
    basis = matrix(c['basis'], n)
    digest = fingerprint(c)
    require(obj['context_sha256'] == digest == expected, 'InvalidContextBinding', 'context differs from receiver selection')
    ai = inverse(a, fuel, 'InvalidInverse')
    inverse(tuple(zip(*basis)), fuel, 'InvalidBasis')
    obs = obj['observations']
    require(type(obs) is list and len(obs) <= n, 'InvalidSchema', 'observation count')
    seen, computed = set(), []
    for entry in obs:
        fields(entry, ['basis_index', 'translation_residual', 'closed'])
        j = entry['basis_index']
        require(type(j) is int and 0 <= j < n and j not in seen,
                'InvalidSchema', 'duplicate or invalid basis index')
        seen.add(j)
        require(type(entry['closed']) is bool, 'InvalidSchema', 'closed must be Boolean')
        claimed = vector(entry['translation_residual'], n)
        v = basis[j]
        linear, residual = direct(a, ai, v, fuel)
        av = mv(a, v, fuel)
        aav = mv(a, av, fuel)
        oracle = tuple(fuel.q(-x+3*y-z) for x, y, z in zip(aav, av, v))
        require(linear == eye(n) and residual == oracle, 'InternalMismatch', 'direct and polynomial calculations differ')
        closed = all(x == 0 for x in residual)
        require(claimed == residual and entry['closed'] == closed,
                'InvalidEvidence', 'reported residual or Boolean does not replay')
        computed.append({'basis_index': j, 'translation_residual': list(map(str, residual)), 'closed': closed})
    missing = sorted(set(range(n))-seen)
    status = ('Refuted' if any(not r['closed'] for r in computed) else
              'UnknownCoverage' if missing else 'ClosedForAllTranslationsByLinearity')
    return {'status': status, 'context_sha256': digest, 'context': c,
            'replayed': computed, 'missing_basis_indices': missing,
            'scope': 'all rational translations in the declared space, via checked basis and affine-word lemma'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('receipt')
    parser.add_argument('--expected-context-sha256', required=True)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (256*1024*1024, 256*1024*1024))
    try:
        with Path(args.receipt).open('rb') as f:
            raw = f.read(MAX_BYTES+1)
        result = verify(raw, args.expected_context_sha256)
    except OSError as e:
        result = {'status': 'InvalidInput', 'reason': type(e).__name__}
    except MemoryError:
        result = {'status': 'UnknownResource', 'reason': 'address-space limit'}
    print(json.dumps(result, sort_keys=True))
    return 0 if result['status'] == 'ClosedForAllTranslationsByLinearity' else 2


if __name__ == '__main__':
    raise SystemExit(main())
