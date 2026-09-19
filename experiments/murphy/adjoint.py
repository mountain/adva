"""Pure Iota transpose/adjoint on explicit 2x2 coordinate tables.

Authored by ChatGPT (OpenAI). Standard library, no native Adva calls.
Run after research.py: python3 adjoint.py --base EVIDENCE --output FRESH_DIRECTORY
"""
import argparse
import hashlib
import json
from pathlib import Path
import lambda_ref as l

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument('--base', type=Path, required=True)
ap.add_argument('--output', type=Path, required=True)
args = ap.parse_args()
args.output.mkdir(parents=True, exist_ok=False)
checks = []


def need(condition, name):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def tuple4(*items):
    return l.L('receiver', l.apps(l.V('receiver'), *items))


def perm(indices):
    return l.L('z', l.A(l.V('z'), l.lams('a b c d',
        tuple4(*(l.V('abcd'[i]) for i in indices)))))


def nf(term):
    return l.normal(l.db(term))


def compile_term(name, term):
    code = l.encode(l.to_iota(l.ski(term)))
    decoded = l.decode(code)
    need(nf(decoded) == nf(term), name+' Iota compilation beta equivalence')
    (args.output/(name+'.iota')).write_text(code+'\n')
    sizes[name] = {'characters': len(code), 'sha256': hashlib.sha256((code+'\n').encode()).hexdigest()}
    return decoded


result = {'schema': 'iota.adjoint.reference.v1', 'native_runs': 0,
          'scope': 'explicit 2x2 tables of four-slot signed complex coordinates',
          'limits': {'lambda_work': 4000000, 'lambda_wall_seconds': 30}}
sizes = {}
try:
    base = json.loads((args.base/'result.json').read_text())
    need(base['status'] == 'CheckedWithinDeclaredScope', 'base experiment checked')
    c = l.decode((args.base/'C.iota').read_text().strip())
    # Reconstruct and pin C to the exact compact source used in research.py.
    c_source = perm([0, 1, 3, 2])
    need(nf(c) == nf(c_source), 'input C agrees with conjugation source')
    transpose_source = perm([0, 2, 1, 3])
    t = compile_term('transpose2', transpose_source)
    conjugate_source = l.L('m', l.A(l.V('m'), l.lams('a b c d',
        tuple4(*(l.A(c_source, l.V(k)) for k in 'abcd')))))
    conjugate_table = compile_term('conjugate2', conjugate_source)
    # T(C(M)) written directly avoids an unnecessary composition wrapper.
    adjoint_source = l.L('m', l.A(l.V('m'), l.lams('a b c d',
        tuple4(*(l.A(c_source, l.V(k)) for k in 'acbd')))))
    adjoint = compile_term('adjoint2', adjoint_source)
    names = ['x'+str(i) for i in range(16)]
    entries = [tuple4(*(l.V(x) for x in names[i:i+4])) for i in range(0,16,4)]
    matrix = tuple4(*entries)
    def equal(x, y, label):
        need(nf(l.lams(' '.join(names), x)) == nf(l.lams(' '.join(names), y)), label)
    equal(l.A(t, matrix), tuple4(*(entries[i] for i in [0,2,1,3])), 'transpose exchanges off-diagonal entries')
    equal(l.A(t, l.A(t, matrix)), matrix, 'transpose squared is identity')
    equal(l.A(conjugate_table, l.A(conjugate_table, matrix)), matrix, 'entrywise conjugation squared is identity')
    equal(l.A(adjoint, matrix), l.A(t, l.A(conjugate_table, matrix)), 'adjoint equals transpose after conjugation')
    equal(l.A(t, l.A(conjugate_table, matrix)), l.A(conjugate_table, l.A(t, matrix)), 'transpose commutes with entrywise conjugation')
    equal(l.A(adjoint, l.A(adjoint, matrix)), matrix, 'adjoint squared is identity')
    expected_entries = [tuple4(*(l.V(names[4*i+j]) for j in [0,1,3,2])) for i in [0,2,1,3]]
    equal(l.A(adjoint, matrix), tuple4(*expected_entries), 'adjoint output matches all sixteen formal slots')
    # P need not be a coordinate-table endomorphism. Retain the actual witness.
    here = Path(__file__).resolve().parent
    p = l.closure(json.loads((here/'inputs/P-tree.json').read_text()))
    slots = list(map(l.V, 'pqrs'))
    pz = nf(l.lams('p q r s', l.A(p, tuple4(*slots))))
    body = pz
    for _ in slots:
        body = body[1]
    head = body
    while head[0] == 'a':
        head = head[1]
    need(head == ('v', 2), 'P on coordinate tuple has opaque q as result head')
    result['P_on_coordinate_tuple'] = l.pretty(pz)
    result['P_coordinate_endomorphism_established'] = False
    # Raw tree reflection is an involution, but it does not preserve beta equality.
    def mirror(x):
        return l.A(mirror(x[2]), mirror(x[1])) if x[0] == 'a' else x
    k1 = l.iota_k
    k2 = l.apps(k1, k1, l.iota_s)  # K K S = K, another presentation of the same value.
    need(nf(k1) == nf(k2), 'two Iota presentations of K are beta equal')
    need(nf(mirror(k1)) == nf(l.C('I')), 'tree mirror of canonical Iota K is I')
    need(nf(mirror(k1)) != nf(mirror(k2)), 'tree mirror does not descend to beta-equivalence classes')
    result.update(status='CheckedWithinDeclaredScope', programs=sizes,
                  base_result_sha256=hashlib.sha256((args.base/'result.json').read_bytes()).hexdigest())
except (RuntimeError, TimeoutError, RecursionError) as error:
    result.update(status='Unknown', reason=str(error))
except Exception as error:
    result.update(status='Failed', reason=repr(error))
result.update(assertions=len(checks), checks=checks, counted_lambda_work=l.work)
(args.output/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','P_on_coordinate_tuple']}, ensure_ascii=False, indent=2))
if result['status'] != 'CheckedWithinDeclaredScope':
    raise SystemExit(1)
