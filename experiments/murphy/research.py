"""Bounded external Iota/conjugation research. Authored by ChatGPT (OpenAI).

Python standard library only. Run: python3 research.py --output FRESH_DIRECTORY
No native Adva execution, repository mutation, network access, or hidden retries.
"""
import argparse
from collections import Counter
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import time
import lambda_ref as l

HERE = Path(__file__).resolve().parent
A, V, L = l.A, l.V, l.L
START = time.monotonic()
CHECKS = []


def need(condition, name):
    if not condition:
        raise AssertionError(name)
    CHECKS.append(name)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def nodes(t):
    return 1 + sum(nodes(x) for x in t[1:] if isinstance(x, tuple))


def contract_once(t, path=''):
    """Independent leftmost-outermost Iota/S/K/I tree rewriting."""
    if t[0] != 'a':
        return None
    args, head = [], t
    while head[0] == 'a':
        args.append(head[2])
        head = head[1]
    args.reverse()
    name = head[1] if head[0] == 'c' else None
    arity = {'j': 1, 'I': 1, 'K': 2, 'S': 3}.get(name)
    if arity is not None and len(args) >= arity:
        if name == 'j':
            out = l.apps(args[0], l.C('S'), l.C('K'))
        elif name in ('I', 'K'):
            out = args[0]
        else:
            x, y, z = args[:3]
            out = A(A(x, z), A(y, z))
        return l.apps(out, *args[arity:]), path, name
    left = contract_once(t[1], path + 'L')
    if left:
        return A(left[0], t[2]), left[1], left[2]
    right = contract_once(t[2], path + 'R')
    if right:
        return A(t[1], right[0]), right[1], right[2]
    return None


def reduce_comb(t, label, trace=False):
    start, count, maximum = time.monotonic(), Counter(), nodes(t)
    rows = []
    for step in range(20001):
        if time.monotonic() - start > 30:
            raise TimeoutError('Unknown: combinator wall limit ' + label)
        if nodes(t) > 200000:
            raise TimeoutError('Unknown: combinator node limit ' + label)
        changed = contract_once(t)
        if changed is None:
            return t, {'label': label, 'contractions': step,
                       'rules': dict(count), 'peak_nodes': maximum,
                       'normal_form_sha256': digest(t), 'trace': rows}
        if step == 20000:
            raise TimeoutError('Unknown: combinator contraction limit ' + label)
        t, path, rule = changed
        size = nodes(t)
        maximum = max(maximum, size)
        count[rule] += 1
        if trace:
            rows.append({'step': step+1, 'path': path, 'rule': rule,
                         'nodes': size, 'sha256': digest(t)})


def tuple4(*args):
    return L('collector', l.apps(V('collector'), *args))


def permutation(indices):
    return L('z', A(V('z'), l.lams('p q r s',
        tuple4(*(V('pqrs'[k]) for k in indices)))))


def normal_named(t):
    return l.normal(l.db(t))


def lambda_study(out):
    p_tree = json.loads((HERE/'inputs/P-tree.json').read_text())
    p = l.closure(p_tree)
    inner = l.left(l.closure(p_tree[1]))
    p_code = (HERE/'inputs/P.iota').read_text().strip()
    need(len(p_code) == 823, 'P has 823 prefix characters')
    need(l.encode(l.to_iota(l.ski(p))) == p_code, 'P compilation matches previous artifact')
    need(p == L('x', A(V('x'), inner)), 'P is lambda h.h A')
    pp_nf = normal_named(A(p, p))
    need(pp_nf == normal_named(A(inner, inner)), 'PP beta normal form equals AA')
    need(pp_nf != normal_named(p), 'PP and P have distinct beta normal forms')
    pure_p = l.decode(p_code)
    pp_reduced, pp_stats = reduce_comb(A(pure_p, pure_p), 'PP', trace=True)
    need(normal_named(pp_reduced) == pp_nf, 'independent Iota rewriting agrees on PP')
    (out/'PP.iota').write_text('*'+p_code+p_code+'\n')
    (out/'PP-trace.json').write_bytes(canonical(pp_stats)+b'\n')
    pp_stats.pop('trace')

    # An explicit four-slot coordinate tuple, not a claim about the user's
    # Adva list representation. It denotes (p-q) + i*(r-s).
    permutations = {'C': [0, 1, 3, 2], 'J': [3, 2, 0, 1], 'N': [1, 0, 3, 2]}
    source, compiled, sizes, reductions = {}, {}, {}, {}
    slots = list(map(V, 'pqrs'))
    z = tuple4(*slots)
    for name, order in permutations.items():
        source[name] = permutation(order)
        code = l.encode(l.to_iota(l.ski(source[name])))
        compiled[name] = l.decode(code)
        need(normal_named(compiled[name]) == normal_named(source[name]),
             name+' Iota translation agrees with lambda source')
        sizes[name] = {'characters': len(code), 'iota_leaves': code.count('i'),
                       'application_nodes': code.count('*')}
        (out/(name+'.iota')).write_text(code+'\n')
        test = l.ski(l.apps(compiled[name], z, V('out')))
        result, stats = reduce_comb(test, name+' on four opaque slots')
        need(result == l.apps(V('out'), *(slots[k] for k in order)),
             name+' direct combinator reduction produces the expected slot order')
        reductions[name] = stats

    c, j, n = (compiled[k] for k in ('C', 'J', 'N'))
    def check_tuple(lhs, rhs, label):
        need(normal_named(l.lams('p q r s', lhs)) ==
             normal_named(l.lams('p q r s', rhs)), label)
    check_tuple(A(c, A(c, z)), z, 'C squared is identity on encoded coordinates')
    check_tuple(A(j, A(j, z)), A(n, z), 'J squared is negation on encoded coordinates')
    check_tuple(A(j, A(j, A(j, A(j, z)))), z, 'J fourth power is identity')
    check_tuple(A(c, A(j, A(c, z))), A(n, A(j, z)), 'C J C equals minus J')
    check_tuple(A(n, A(n, z)), z, 'negation squared is identity')
    need(normal_named(l.lams('p q r s', A(j, A(j, z)))) !=
         normal_named(l.lams('p q r s', z)), 'J squared is not identity: opaque-slot witness')
    need(normal_named(l.lams('p q r s', A(c, z))) !=
         normal_named(l.lams('p q r s', A(j, z))), 'C and J are distinct')
    return {'P_characters': 823, 'PP_characters': 1647,
            'PP_beta_normal_form': l.pretty(pp_nf),
            'P_beta_normal_form_nodes': nodes(normal_named(p)),
            'PP_beta_normal_form_nodes': nodes(pp_nf),
            'PP_equals_AA': True, 'PP_equals_P_by_beta': False,
            'PP_reduction': pp_stats, 'coordinate_encoding': '(p-q)+i*(r-s)',
            'coordinate_program_sizes': sizes, 'coordinate_reductions': reductions,
            'coordinate_laws_scope': 'all constructor tuples of four opaque payloads'}


def eye(n):
    return [[Q(i == j) for j in range(n)] for i in range(n)]


def zero(n):
    return [[Q(0) for _ in range(n)] for _ in range(n)]


def mm(a, b):
    return [[sum((x*y for x, y in zip(row, col)), Q(0))
             for col in zip(*b)] for row in a]


def tr(a):
    return [list(row) for row in zip(*a)]


def scale(a, q):
    return [[x*q for x in row] for row in a]


def add(a, b):
    return [[x+y for x, y in zip(r, s)] for r, s in zip(a, b)]


def sim(t, a, inv):
    return mm(mm(t, a), inv)


def decoded(a):
    return [[Q(x) for x in r] for r in a]


def encoded(a):
    return [[str(x) for x in r] for r in a]


def diag(values):
    return [[Q(x if i == j else 0) for j in range(len(values))]
            for i, x in enumerate(values)]


def frame_study():
    frames = json.loads((HERE/'inputs/frames.json').read_text())
    identities = {f['family']: f for f in frames if f['id'].endswith('/identity')}
    rows, controls = [], []
    for frame in frames:
        name = frame['id']
        t, inv, h, j, g, o = (decoded(frame[k]) for k in ('T', 'inverse', 'H', 'J', 'G', 'O'))
        dim = len(j)
        ident, nil = eye(dim), zero(dim)
        source = identities[frame['family']]
        h0, j0 = decoded(source['H']), decoded(source['J'])
        c0 = diag([1]*(dim//2)+[-1]*(dim//2))
        c = sim(t, c0, inv)
        ginv = mm(t, tr(t))
        def adj(a):
            return mm(mm(ginv, tr(a)), g)
        need(mm(t, inv) == ident and mm(inv, t) == ident, name+' inverse')
        need(h == sim(t, h0, inv) and j == sim(t, j0, inv), name+' source binding')
        need(g == mm(tr(inv), inv) and o == inv, name+' metric and observer binding')
        need(mm(j, j) == scale(ident, -1), name+' J^2=-I')
        need(mm(c, c) == ident, name+' C^2=I')
        need(sim(c, j, c) == scale(j, -1), name+' CJC=-J')
        need(sim(c, h, c) == h, name+' CHC=H for this real H')
        need(mm(mm(tr(c), g), c) == g, name+' conjugation preserves metric')
        need(mm(mm(o, c), t) == c0, name+' observed conjugation agrees')
        need(adj(h) == h and adj(j) == scale(j, -1), name+' H self-adjoint and J skew-adjoint')
        a = scale(mm(j, h), -1)
        need(sim(c, a, c) == scale(a, -1), name+' CAC=-A')
        # A noncommuting pair gives a meaningful order-reversal witness.
        x0 = zero(dim)
        y0 = zero(dim)
        for offset in (0, dim//2):
            x0[offset][offset+1] = 1
            y0[offset+1][offset] = 1
        x, y = sim(t, x0, inv), sim(t, y0, inv)
        need(mm(x, y) != mm(y, x), name+' adjoint control pair does not commute')
        need(adj(mm(x, y)) == mm(adj(y), adj(x)), name+' adjoint reverses composition')
        need(adj(mm(x, y)) != mm(adj(x), adj(y)), name+' unchanged-order adjoint fails')
        need(adj(adj(x)) == x, name+' adjoint is involutive')
        coeff = ident
        for k in range(13):
            if k:
                coeff = scale(mm(a, coeff), Q(1, k))
            need(sim(c, coeff, c) == scale(coeff, (-1)**k), name+f' time conjugation coefficient {k}')
        if '/mixed' in name:
            need(sim(c0, j, c0) != scale(j, -1), name+' stale coordinate conjugation fails')
            controls.append(name+': untransported C fails CJC=-J')
        if '/scaled' in name:
            need(tr(j) != scale(j, -1), name+' ordinary transpose fails in scaled coordinates')
            controls.append(name+': old Euclidean metric gives wrong J adjoint')
        rows.append({'frame': name, 'dimension': dim, 'C': encoded(c),
                     'series_order': 12, 'conjugation_and_adjoint_checks': True})
    # J alone does not select a conjugation: C and -C are two distinct choices.
    j = [[Q(0), Q(-1)], [Q(1), Q(0)]]
    c = diag([1, -1])
    other = scale(c, -1)
    need(c != other and mm(other, other) == eye(2) and sim(other, j, other) == scale(j, -1),
         'one J admits two distinct conjugations')
    return {'frames': rows, 'negative_controls': controls,
            'scope': 'extension of existing frame coordinates; no replay of old process checker'}


def carrier_study():
    s = json.loads((HERE/'inputs/carrier_structure.json').read_text())
    n = len(s['directions'])
    need(n == 3, 'carrier uses the declared three directions')
    vertices = s['cube']['vertices']
    edges = [(e['mask'], e['direction']) for e in s['cube']['enabled']]
    need(set(vertices) == set(range(1 << n)), 'carrier vertices form declared cube')
    need(set(edges) == {(v, d) for v in vertices for d in range(n) if not v & (1 << d)},
         'carrier enabled edges match forward cube')
    pairing = []
    for i in range(n):
        row = []
        for j in range(n):
            delta = {(((v | (1 << j)) >> i) & 1) - ((v >> i) & 1)
                     for v, d in edges if d == j}
            need(len(delta) == 1, f'incidence dx_{i}(g_{j}) single-valued')
            row.append(delta.pop())
        pairing.append(row)
    need(pairing == eye(n), 'cut-derived pairing is identity')
    dim = 1 << n
    wedge, contraction = [], []
    for i in range(n):
        e, q = zero(dim), zero(dim)
        for mask in range(dim):
            sign = (-1)**((mask & ((1 << i)-1)).bit_count())
            if mask & (1 << i):
                q[mask ^ (1 << i)][mask] = sign
            else:
                e[mask | (1 << i)][mask] = sign
        wedge.append(e)
        contraction.append(q)
    clifford = [add(e, q) for e, q in zip(wedge, contraction)]
    for i in range(n):
        need(tr(wedge[i]) == contraction[i], f'wedge and contraction {i} are dual')
        for j in range(n):
            need(add(mm(clifford[i], clifford[j]), mm(clifford[j], clifford[i])) ==
                 scale(eye(dim), 2*(i == j)), f'Clifford relation {i},{j}')
    volume = eye(dim)
    for c in clifford:
        volume = mm(c, volume)  # Exact repository order c_2(c_1(c_0 .)).
    basis = s['extended_carrier']['signed_basis']
    masks = [b for b, sign in basis]
    need(all(volume[r][b] == 0 for b in masks for r in range(dim) if r not in masks),
         'volume preserves the declared W')
    omega = [[volume[r][b]*rs*bs for b, bs in basis] for r, rs in basis]
    # Minus exterior parity: + on grade 1 and - on grade 2.
    conjugation = diag([(-1)**(b.bit_count()+1) for b, _ in basis])
    ident = eye(len(basis))
    need(mm(omega, omega) == scale(ident, -1), 'carrier Omega^2=-I')
    need(mm(conjugation, conjugation) == ident, 'carrier C^2=I')
    need(sim(conjugation, omega, conjugation) == scale(omega, -1), 'carrier C Omega C=-Omega')
    need(tr(conjugation) == conjugation and tr(omega) == scale(omega, -1),
         'carrier C symmetric and Omega skew')
    canonical_j = zero(6)
    for i in range(3):
        canonical_j[i][i+3], canonical_j[i+3][i] = -1, 1
    need(omega in (canonical_j, scale(canonical_j, -1)), 'carrier Omega is signed canonical J')
    orientation = 1 if omega == canonical_j else -1
    need(sim(omega, omega, scale(omega, -1)) == omega,
         'multiplication by i does not complex-conjugate i')
    return {'cut_pairing': pairing, 'signed_basis': basis,
            'composition_order': 'c_2(c_1(c_0 .))', 'Omega': encoded(omega),
            'C': encoded(conjugation), 'canonical_J_sign': orientation,
            'definition_of_C': 'minus grade parity restricted to W',
            'scope': 'declared carrier fixture, not a map from arbitrary Iota syntax'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output
    out.mkdir(parents=True, exist_ok=False)
    result = {'schema': 'iota.conjugation.external-reference.v1',
              'native_runs': 0, 'source_word': '0001011011',
              'prior_Zot_CEK_transitions': 125,
              'limits': {'combinator_contractions_per_case': 20000,
                         'combinator_tree_nodes': 200000,
                         'wall_seconds_per_combinator_case': 30,
                         'lambda_work': 4000000, 'lambda_wall_seconds': 30,
                         'matrix_max_dimension': 12, 'series_order': 12}}
    try:
        sources = json.loads((HERE/'inputs/source_manifest.json').read_text())
        for source in sources:
            data = (HERE/'inputs'/source['filename']).read_bytes()
            need(hashlib.sha256(data).hexdigest() == source['sha256'], source['filename']+' exact sha256')
            need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == source['git_blob'],
                 source['filename']+' Git blob binding')
        result['lambda'] = lambda_study(out)
        result['frames'] = frame_study()
        result['carrier'] = carrier_study()
        result['status'] = 'CheckedWithinDeclaredScope'
    except (TimeoutError, RecursionError) as error:
        result.update(status='Unknown', reason=str(error))
    except Exception as error:
        result.update(status='Failed', reason=repr(error))
    result['checks'] = CHECKS
    result['assertions'] = len(CHECKS)
    result['wall_seconds'] = time.monotonic()-START
    (out/'result.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('lambda', 'frames', 'carrier', 'checks')}, ensure_ascii=False, indent=2))
    if result['status'] != 'CheckedWithinDeclaredScope':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
