"""Bounded iota/SKI substrate projection (pure stdlib)."""
import hashlib, json, itertools, pathlib, sys
sys.setrecursionlimit(100000)

A = lambda t1, t2: ('app', t1, t2)
S = ('S',); K = ('K',); I = ('I',); IOTA = ('iota',)
def atom(name): return ('atom', name)

def size(t):
    return 1 if t[0] in ('S', 'K', 'I', 'iota', 'atom') else 1 + size(t[1]) + size(t[2])

# ---- iota-lang encodings: I=iota iota; K=iota(iota(iota iota)); S=iota(iota(iota(iota iota)))
I_ENC = A(IOTA, IOTA)
K_ENC = A(IOTA, A(IOTA, A(IOTA, IOTA)))
S_ENC = A(IOTA, A(IOTA, A(IOTA, A(IOTA, IOTA))))

def whnf(t, fuel):
    """weak head normal form with iota rule: iota x -> x S K (first application).
    Returns (term, fuel_used)."""
    used = 0
    while True:
        if t[0] != 'app':
            return t, used
        h, args = t, []
        while h[0] == 'app':
            args.append(h[2]); h = h[1]
        args.reverse()
        if h == IOTA and args:
            t = A(A(args[0], S), K)
            for a in args[1:]:
                t = A(t, a)
            used += 1
        elif h == S and len(args) >= 3:
            t = A(A(args[0], args[2]), A(args[1], args[2]))
            for a in args[3:]:
                t = A(t, a)
            used += 1
        elif h == K and len(args) >= 2:
            t = args[0]
            for a in args[2:]:
                t = A(t, a)
            used += 1
        elif h == I and args:
            t = args[0]
            for a in args[1:]:
                t = A(t, a)
            used += 1
        else:
            return t, used
        if used > fuel:
            raise RuntimeError('fuel exceeded in whnf')

def expand_iota(t, fuel):
    """expand every iota application: iota x -> x S K. Returns (term, steps)."""
    steps = [0]
    def go(x):
        if x[0] != 'app':
            return x
        l = go(x[1]); r = go(x[2])
        if l == IOTA:
            steps[0] += 1
            if steps[0] > fuel:
                raise RuntimeError('expand fuel exceeded')
            return go(A(A(r, S), K))
        return A(l, r)
    return go(t), steps[0]

def free_vars(term, acc=None):
    if acc is None:
        acc = set()
    if term[0] == 'atom':
        acc.add(term[1])
    elif term[0] == 'app':
        free_vars(term[1], acc); free_vars(term[2], acc)
    return acc

def bracket_abstract(term, var):
    """standard SKI bracket abstraction of lambda var. term,
    with the free-variable shortcut: closed subterms become K term."""
    if var not in free_vars(term):
        return A(K, term)
    if term[0] == 'atom' and term[1] == var:
        return I
    if term[0] in ('S', 'K', 'I', 'iota', 'atom'):
        return A(K, term)
    return A(A(S, bracket_abstract(term[1], var)), bracket_abstract(term[2], var))

def church(n):
    """lambda f. lambda x. f^n x  (bracketed to SKI)."""
    body = atom('x')
    for _ in range(n):
        body = A(atom('f'), body)
    inner = bracket_abstract(body, 'x')
    return bracket_abstract(inner, 'f')

def add_lam(a_sk, b_sk):
    """lambda f. lambda x. a f (b f x), bracketed to SKI."""
    body = A(A(atom('a'), atom('f')), A(A(atom('b'), atom('f')), atom('x')))
    # substitute combinator terms for atoms a,b
    def subst(t):
        if t[0] == 'atom':
            if t[1] == 'a': return a_sk
            if t[1] == 'b': return b_sk
        if t[0] != 'app':
            return t
        return A(subst(t[1]), subst(t[2]))
    body = subst(body)
    inner = bracket_abstract(body, 'x')
    return bracket_abstract(inner, 'f')

def encode_byte(b):
    """0164 formula: (add (add (copy u)) v) with copy = duplicate u."""
    u = (b % 8) + 1
    v = b - 2 * u
    cu = church(u); cv = church(v)
    inner = add_lam(cu, cu)          # u+u
    t = add_lam(inner, cv)           # (u+u)+v
    return t, u, v

def to_iota(t):
    if t[0] == 'S': return S_ENC
    if t[0] == 'K': return K_ENC
    if t[0] == 'I': return I_ENC
    if t[0] == 'app': return A(to_iota(t[1]), to_iota(t[2]))
    return t

def normalize(t, fuel):
    """full normalization: whnf at every position. Fuel = whnf steps."""
    steps = [0]
    def go(x):
        w, used = whnf(x, fuel - steps[0])
        steps[0] += used
        if w[0] == 'app':
            return A(go(w[1]), go(w[2]))
        return w
    return go(t)

def model_eval(t, fuel):
    """evaluate SKI term in the finite integer model: S/K/I as functions,
    f as +1, x as 0. Pure lambda-model evaluation, not rewrite proof."""
    calls = [0]
    def ev(x):
        calls[0] += 1
        if calls[0] > fuel:
            raise RuntimeError('model fuel exceeded')
        if x[0] == 'app':
            return ev(x[1])(ev(x[2]))
        if x[0] == 'S':
            return lambda f: lambda g: lambda z: f(z)(g(z))
        if x[0] == 'K':
            return lambda y: lambda _: y
        if x[0] == 'I':
            return lambda y: y
        if x[0] == 'atom':
            if x[1] == 'f':
                return lambda y: y + 1
            if x[1] == 'x':
                return 0
            raise RuntimeError('free atom ' + x[1])
        raise RuntimeError('bad term: ' + str(x[0]))
    return ev(A(A(t, atom('f')), atom('x')))

def run(bounds=(200000, 100000)):
    results = {'schema': 'aeg.iota-projection.research', 'version': 0}
    # C1: combinator laws on atoms
    a1, a2, a3 = atom('p'), atom('q'), atom('r')
    c1 = {}
    for name, enc, law in (('I', I_ENC, None), ('K', K_ENC, None), ('S', S_ENC, None)):
        if name == 'I':
            w, used = whnf(A(enc, a1), bounds[0]); ok = (w == a1)
        elif name == 'K':
            w, used = whnf(A(A(enc, a1), a2), bounds[0]); ok = (w == a1)
        else:
            w, used = whnf(A(A(A(enc, a1), a2), a3), bounds[0]); ok = (w == A(A(a1, a3), A(a2, a3)))
        c1[name] = {'ok': ok, 'fuel_used': used}
    results['C1_combinator_laws'] = c1
    # C2, C3, C4, C5
    rows = []
    for b in (35, 100, 255):
        t, u, v = encode_byte(b)
        iot = to_iota(t)
        exp, steps = expand_iota(iot, bounds[0])
        rows.append({'b': b, 'u': u, 'v': v, 'term_size': size(t),
                     'iota_size': size(iot), 'expand_steps': steps,
                     'C2_substrate_roundtrip': model_eval(exp, bounds[1]),
                     'eta_note': 'iota encodings expand to eta-expanded SKI (e.g. K -> S S K K); equality is by value, not syntax',
                     'C3_value': model_eval(t, bounds[1]),
                     'C4_tampered_value': model_eval(tamper(b), bounds[1]),
                     'term_sha': hashlib.sha256(str(t).encode()).hexdigest()[:16]})
    results['bytes'] = rows
    results['C5_distinct_terms'] = len({r['term_sha'] for r in rows}) == len(rows)
    results['status'] = 'VariationObserved' if (all(r['C2_substrate_roundtrip'] == r['b'] and r['C3_value'] == r['b'] for r in rows)
                                                and results['C5_distinct_terms']
                                                and all(r['C4_tampered_value'] != r['b'] for r in rows)
                                                and all(v['ok'] for v in c1.values())) else 'Rejected'
    return results

def tamper(b):
    t, u, v = encode_byte(b)
    cv = church(v + 1)
    inner = add_lam(church(u), church(u))
    return add_lam(inner, cv)

if __name__ == '__main__':
    res = run()
    print(json.dumps(res, indent=2, ensure_ascii=False))
    pathlib.Path('results.json').write_text(json.dumps(res, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print('status:', res['status'])
