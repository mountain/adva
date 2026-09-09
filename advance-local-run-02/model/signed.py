"""Signed (sign-pair) church arithmetic for the full 0..255 byte set.
Extends reducer.py primitives; unit checks first, then the full run."""
import hashlib, json, pathlib, sys, time
sys.setrecursionlimit(200000)
import importlib.util
spec = importlib.util.spec_from_file_location('r', 'reducer.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
A, S, K, I = r.A, r.S, r.K, r.I
atom = r.atom

def APP(*terms):
    t = terms[0]
    for n in terms[1:]:
        t = A(t, n)
    return t

_fv = {}
def free_vars(t):
    if t in _fv:
        return _fv[t]
    if t[0] == 'atom':
        out = {t[1]}
    elif t[0] == 'app':
        out = free_vars(t[1]) | free_vars(t[2])
    else:
        out = set()
    _fv[t] = out
    return out

def bracket(term, var):
    if var not in free_vars(term):
        return A(K, term)
    if term[0] == 'atom' and term[1] == var:
        return I
    if term[0] != 'app':
        return A(K, term)
    return APP(S, bracket(term[1], var), bracket(term[2], var))

def lam(var, body):
    return bracket(body, var)

def church(n):
    body = atom('x')
    for _ in range(n):
        body = A(atom('f'), body)
    return lam('f', lam('x', body))

TRUE = lam('a', lam('b', atom('a')))
FALSE = lam('a', lam('b', atom('b')))
PAIR = lam('a', lam('b', lam('f', APP(atom('f'), atom('a'), atom('b')))))
FST = lam('p', A(atom('p'), TRUE))
SND = lam('p', A(atom('p'), FALSE))
SUCC = lam('n', lam('f', lam('x', A(atom('f'), APP(atom('n'), atom('f'), atom('x'))))))
ZERO = church(0)
ISZERO = lam('n', APP(atom('n'), lam('x', FALSE), TRUE))
PRED = lam('n', APP(FST, APP(atom('n'),
    lam('p', APP(PAIR, APP(SND, atom('p')), APP(SUCC, APP(SND, atom('p'))))),
    APP(PAIR, ZERO, ZERO))))
SUB = lam('m', lam('n', APP(atom('n'), PRED, atom('m'))))
LE = lam('m', lam('n', A(ISZERO, APP(SUB, atom('m'), atom('n')))))
ADD = lam('m', lam('n', lam('f', lam('x', APP(atom('m'), atom('f'), APP(atom('n'), atom('f'), atom('x')))))))
IF = lam('c', lam('t', lam('e', APP(atom('c'), atom('t'), atom('e')))))

SIGN_ADD = lam('a', lam('b',
    APP(IF, APP(FST, atom('b')),
        APP(PAIR, TRUE, APP(ADD, APP(SND, atom('a')), APP(SND, atom('b')))),
        APP(IF, APP(LE, APP(SND, atom('b')), APP(SND, atom('a'))),
            APP(PAIR, TRUE, APP(SUB, APP(SND, atom('a')), APP(SND, atom('b')))),
            APP(PAIR, FALSE, APP(SUB, APP(SND, atom('b')), APP(SND, atom('a'))))))))

def model_eval(t, fuel):
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
        raise RuntimeError('bad term')
    return ev(APP(t, atom('f'), atom('x'))), calls[0]

def bool_marker(term, fuel):
    """behavioral test: TRUE picks church 1, FALSE picks church 0."""
    return model_eval(APP(term, church(1), church(0)), fuel)[0]

def signed_value(pair_term, fuel):
    mag = model_eval(APP(SND, pair_term), fuel)[0]
    marker = bool_marker(APP(FST, pair_term), fuel)
    return mag if marker == 1 else -mag

def encode_byte(b):
    u = (b % 8) + 1
    v = b - 2 * u
    a = APP(PAIR, TRUE, APP(ADD, church(u), church(u)))
    sign = TRUE if v >= 0 else FALSE
    bterm = APP(PAIR, sign, church(abs(v)))
    return APP(SIGN_ADD, a, bterm), u, v

print('=== primitive unit checks ===')
assert model_eval(APP(SUCC, church(3)), 20000)[0] == 4
assert bool_marker(APP(ISZERO, church(0)), 20000) == 1
assert bool_marker(APP(ISZERO, church(5)), 20000) == 0
assert model_eval(APP(PRED, church(5)), 20000)[0] == 4
assert model_eval(APP(SUB, church(7), church(2)), 300000)[0] == 5
assert bool_marker(APP(LE, church(3), church(5)), 300000) == 1
assert bool_marker(APP(LE, church(5), church(3)), 300000) == 0
assert model_eval(APP(ADD, church(4), church(4)), 20000)[0] == 8
print('primitives ok')

for b in (0, 7, 35, 100, 255):
    t, u, v = encode_byte(b)
    print('b=%d u=%d v=%d value=%d' % (b, u, v, signed_value(t, 2000000)))
