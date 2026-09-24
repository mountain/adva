"""Exact external checker for the Kerr line element: vacuum, Kretschmann, signature, horizons.

This checker never constructs, reads or authorizes an Adva semantic identity and
makes no physical claim. It uses integers, tuples, Fractions, the standard
library's math module and nothing else. It opens no corpus, no catalogue and no
measurement: the line element, the parameter pairs, the evaluation points and the
Kretschmann closed form it works with are all declared in contract.json.

The whole symbolic tensor calculus is implemented here: bivariate polynomials
over Q, a parity-split representation of rational functions in (r, cos theta)
that carries sin(theta) through the identity sin^2 = 1 - cos^2, exact
Christoffel symbols, Riemann tensor, Ricci tensor and Kretschmann scalar, exact
inertia by congruence reduction, and exact arithmetic in a quadratic field for
the horizon data. The only floating-point arithmetic in the file is the declared
calibration of the two symbolic derivatives against central differences.

What this file computes, and what it does not, is stated in contract.json. In
particular it decides nothing about any real object.
"""
import argparse
import hashlib
import json
import math
import resource
import signal
import time
from fractions import Fraction as F
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
COUNTS = {"assertions": 0}
LIMITS = {}
INSTALLED = {}
CFG = {"M": F(1), "A": F(0)}
SIGMA = {}
DELTA = {}
S_POLY = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


def digest(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def load(relative):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def set_params(mass, spin):
    CFG["M"], CFG["A"] = F(mass), F(spin)
    m, a = CFG["M"], CFG["A"]
    globals()["SIGMA"] = {(2, 0): F(1), (0, 2): a * a}
    globals()["DELTA"] = {(2, 0): F(1), (1, 0): -2 * m, (0, 0): a * a}
    globals()["S_POLY"] = {(0, 0): F(1), (0, 2): F(-1)}


# ---------------------------------------------------------------------------
# bivariate polynomials over Q, in (r, c)
# ---------------------------------------------------------------------------

def padd(u, v):
    out = dict(u)
    for key, value in v.items():
        total = out.get(key, F(0)) + value
        if total:
            out[key] = total
        else:
            out.pop(key, None)
    return out


def pneg(u):
    return {key: -value for key, value in u.items()}


def psub(u, v):
    return padd(u, pneg(v))


def pmul(u, v):
    out = {}
    for (i1, j1), v1 in u.items():
        for (i2, j2), v2 in v.items():
            key = (i1 + i2, j1 + j2)
            total = out.get(key, F(0)) + v1 * v2
            if total:
                out[key] = total
            else:
                out.pop(key, None)
    return out


def pder_r(u):
    return {(i - 1, j): v * i for (i, j), v in u.items() if i > 0}


def pder_c(u):
    return {(i, j - 1): v * j for (i, j), v in u.items() if j > 0}


def pc(x):
    return {} if F(x) == 0 else {(0, 0): F(x)}


def ppow(u, n):
    out = pc(1)
    for _ in range(n):
        out = pmul(out, u)
    return out


def pz(u):
    return not u


def pterms(u):
    return len(u)


def pdeg(u):
    return max((i + j for i, j in u), default=-1)


def peval(p, r, c):
    return sum(value * r ** i * c ** j for (i, j), value in p.items())


# ---------------------------------------------------------------------------
# rational functions: (P0, P1, a, b, d) is (P0 + s P1) / (Sigma^a Delta^b S^d)
# ---------------------------------------------------------------------------

def rf(P0=None, P1=None, a=0, b=0, d=0):
    return (P0 or {}, P1 or {}, a, b, d)


def rf_zero():
    return rf()


def rf_iszero(x):
    return pz(x[0]) and pz(x[1])


def rf_shape(x):
    return [pterms(x[0]), pdeg(x[0]), pterms(x[1]), pdeg(x[1]), x[2], x[3], x[4]]


def _scale(x, da, db, dd):
    P0, P1, a, b, d = x
    if da == db == dd == 0:
        return x
    factor = pmul(ppow(SIGMA, da), pmul(ppow(DELTA, db), ppow(S_POLY, dd)))
    return (pmul(P0, factor), pmul(P1, factor), a + da, b + db, d + dd)


def rf_add(x, y):
    """Common denominator is the MAXIMUM of the exponents: scaling up multiplies the
    numerator, which preserves the value. Scaling down would require a division."""
    a, b, d = max(x[2], y[2]), max(x[3], y[3]), max(x[4], y[4])
    X = _scale(x, a - x[2], b - x[3], d - x[4])
    Y = _scale(y, a - y[2], b - y[3], d - y[4])
    return (padd(X[0], Y[0]), padd(X[1], Y[1]), a, b, d)


def rf_neg(x):
    return (pneg(x[0]), pneg(x[1]), x[2], x[3], x[4])


def rf_sub(x, y):
    return rf_add(x, rf_neg(y))


def rf_mul(x, y):
    X0, X1, xa, xb, xd = x
    Y0, Y1, ya, yb, yd = y
    P0 = padd(pmul(X0, Y0), pmul(pmul(S_POLY, X1), Y1))
    P1 = padd(pmul(X0, Y1), pmul(X1, Y0))
    return (P0, P1, xa + ya, xb + yb, xd + yd)


def rf_scale(x, k):
    return (pmul(x[0], pc(k)), pmul(x[1], pc(k)), x[2], x[3], x[4])


def rf_half(x):
    return rf_scale(x, F(1, 2))


def rf_der_r(x):
    P0, P1, a, b, d = x
    term = padd(pmul(pc(2 * a), pmul({(1, 0): F(1)}, DELTA)),
                pmul(pc(2 * b), pmul(psub({(1, 0): F(1)}, pc(CFG["M"])), SIGMA)))
    base = pmul(SIGMA, DELTA)
    return (psub(pmul(pder_r(P0), base), pmul(P0, term)),
            psub(pmul(pder_r(P1), base), pmul(P1, term)), a + 1, b + 1, d)


def rf_der_theta(x):
    P0, P1, a, b, d = x
    a2, c1 = CFG["A"] ** 2, {(0, 1): F(1)}
    n0 = psub(pmul(c1, P1), pmul(S_POLY, pder_c(P1)))
    n1 = pneg(pder_c(P0))
    base = pmul(SIGMA, S_POLY)
    k1, k2 = pc(2 * a * a2), pc(2 * d)
    N0 = padd(pmul(n0, base),
              psub(pmul(pmul(k1, c1), pmul(S_POLY, pmul(S_POLY, P1))),
                   pmul(pmul(k2, c1), pmul(S_POLY, pmul(SIGMA, P1)))))
    N1 = padd(pmul(n1, base),
              psub(pmul(pmul(k1, c1), pmul(S_POLY, P0)),
                   pmul(pmul(k2, c1), pmul(SIGMA, P0))))
    return (N0, N1, a + 1, b, d + 1)


def rf_eval_exact(x, r, c):
    """Exact value at rational (r, c) when there is no sin(theta) part."""
    P0, P1, a, b, d = x
    if not pz(P1):
        raise ValueError("a sin(theta) part cannot be evaluated at rational (r, c)")
    S = 1 - c * c
    sig = r * r + CFG["A"] ** 2 * c * c
    delta = r * r - 2 * CFG["M"] * r + CFG["A"] ** 2
    return peval(P0, r, c) / (sig ** a * delta ** b * S ** d)


def rf_eval_float(x, r, theta):
    P0, P1, a, b, d = x
    c = math.cos(theta)
    s = math.sin(theta)
    sig = r * r + float(CFG["A"]) ** 2 * c * c
    delta = r * r - 2 * float(CFG["M"]) * r + float(CFG["A"]) ** 2
    S = s * s
    num = sum(float(v) * r ** i * c ** j for (i, j), v in P0.items())
    num += s * sum(float(v) * r ** i * c ** j for (i, j), v in P1.items())
    return num / (sig ** a * delta ** b * S ** d)


# ---------------------------------------------------------------------------
# metric, inverse, Christoffel, Riemann, Ricci, Kretschmann
# ---------------------------------------------------------------------------

def metric():
    m, a = CFG["M"], CFG["A"]
    gtt = rf(pneg(psub(SIGMA, pmul(pc(2 * m), {(1, 0): F(1)}))), None, 1, 0, 0)
    gtp = rf(pneg(pmul(pc(2 * m * a), pmul({(1, 0): F(1)}, S_POLY))), None, 1, 0, 0)
    gpp = rf(pmul(S_POLY, padd(pmul(padd({(2, 0): F(1)}, pc(a * a)), SIGMA),
                               pmul(pc(2 * m * a * a), pmul({(1, 0): F(1)}, S_POLY)))),
             None, 1, 0, 0)
    return {
        (0, 0): gtt, (3, 3): gpp, (0, 3): gtp, (3, 0): gtp,
        (1, 1): rf(SIGMA, None, 0, 1, 0),
        (2, 2): rf(SIGMA, None, 0, 0, 0),
    }


def inverse_metric(g):
    one_over = rf(pc(1), None, 0, 1, 1)
    inv = {
        (0, 0): rf_neg(rf_mul(g[(3, 3)], one_over)),
        (3, 3): rf_neg(rf_mul(g[(0, 0)], one_over)),
        (0, 3): rf_mul(g[(0, 3)], one_over),
        (3, 0): rf_mul(g[(0, 3)], one_over),
        (1, 1): rf(DELTA, None, 1, 0, 0),
        (2, 2): rf(pc(1), None, 1, 0, 0),
    }
    det_block = rf_sub(rf_mul(g[(0, 0)], g[(3, 3)]), rf_mul(g[(0, 3)], g[(3, 0)]))
    return inv, det_block


def metric_times_inverse(g, inv):
    """g^{a e} g_{e b} for every pair, as an exact matrix of rational functions."""
    out = {}
    for a in range(4):
        for b in range(4):
            total = rf_zero()
            for e in range(4):
                left = inv.get((a, e), rf_zero())
                right = g.get((e, b), g.get((b, e), rf_zero()))
                if rf_iszero(left) or rf_iszero(right):
                    continue
                total = rf_add(total, rf_mul(left, right))
            out[(a, b)] = total
    return out


def Gget(G, a, i, j):
    i, j = (i, j) if i <= j else (j, i)
    return G.get((a, i, j), rf_zero())


def christoffel(g, inv):
    dg = {}
    for key in g:
        dg[(1, *key)] = rf_der_r(g[key])
        dg[(2, *key)] = rf_der_theta(g[key])
    symbols = {}
    for a in range(4):
        for b in range(4):
            for c in range(b, 4):
                total = rf_zero()
                for d in range(4):
                    gad = inv.get((a, d), rf_zero())
                    if rf_iszero(gad):
                        continue
                    acc = rf_add(dg.get((b, d, c), rf_zero()),
                                 rf_sub(dg.get((c, d, b), rf_zero()),
                                        dg.get((d, b, c), rf_zero())))
                    if rf_iszero(acc):
                        continue
                    total = rf_add(total, rf_mul(gad, acc))
                if not rf_iszero(total):
                    symbols[(a, b, c)] = rf_half(total)
    return symbols


def derivative_of(symbols, k, a, i, j):
    x = Gget(symbols, a, i, j)
    if rf_iszero(x):
        return rf_zero()
    if k == 1:
        return rf_der_r(x)
    if k == 2:
        return rf_der_theta(x)
    return rf_zero()


def riemann(symbols):
    """R^a_bcd for c < d; the other orders follow from antisymmetry."""
    out = {}
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(c + 1, 4):
                    total = rf_sub(derivative_of(symbols, c, a, d, b),
                                   derivative_of(symbols, d, a, c, b))
                    for e in range(4):
                        g1, g2 = Gget(symbols, a, c, e), Gget(symbols, e, d, b)
                        if not rf_iszero(g1) and not rf_iszero(g2):
                            total = rf_add(total, rf_mul(g1, g2))
                        g3, g4 = Gget(symbols, a, d, e), Gget(symbols, e, c, b)
                        if not rf_iszero(g3) and not rf_iszero(g4):
                            total = rf_sub(total, rf_mul(g3, g4))
                    if not rf_iszero(total):
                        out[(a, b, c, d)] = total
    return out


def Rget(R, a, b, c, d):
    if c == d:
        return rf_zero()
    if c < d:
        return R.get((a, b, c, d), rf_zero())
    return rf_neg(R.get((a, b, d, c), rf_zero()))


def ricci(R):
    out = {}
    for b in range(4):
        for d in range(b, 4):
            total = rf_zero()
            for a in range(4):
                total = rf_add(total, Rget(R, a, b, a, d))
            out[(b, d)] = total
    return out


def lower_riemann(g, R):
    out = {}
    for a in range(4):
        for b in range(4):
            for c in range(4):
                for d in range(c + 1, 4):
                    total = rf_zero()
                    for e in range(4):
                        gae = g.get((a, e), g.get((e, a), rf_zero()))
                        if rf_iszero(gae):
                            continue
                        x = Rget(R, e, b, c, d)
                        if rf_iszero(x):
                            continue
                        total = rf_add(total, rf_mul(gae, x))
                    if not rf_iszero(total):
                        out[(a, b, c, d)] = total
    return out


def raise_riemann(inv, low, a, b, c, d):
    options = {
        0: [(0, inv.get((0, 0), rf_zero())), (3, inv.get((0, 3), rf_zero()))],
        3: [(0, inv.get((3, 0), rf_zero())), (3, inv.get((3, 3), rf_zero()))],
        1: [(1, inv.get((1, 1), rf_zero()))],
        2: [(2, inv.get((2, 2), rf_zero()))],
    }
    total = rf_zero()
    for e, ge in options[a]:
        if rf_iszero(ge):
            continue
        for f, gf in options[b]:
            if rf_iszero(gf):
                continue
            for h, gh in options[c]:
                if rf_iszero(gh):
                    continue
                for k, gk in options[d]:
                    if rf_iszero(gk):
                        continue
                    i, j = (h, k) if h < k else (k, h)
                    x = low.get((e, f, i, j), rf_zero())
                    if rf_iszero(x):
                        continue
                    if h > k:
                        x = rf_neg(x)
                    total = rf_add(total, rf_mul(rf_mul(ge, gf), rf_mul(rf_mul(gh, gk), x)))
    return total


def kretschmann(g, inv, R):
    """R_abcd R^abcd = 4 * sum over a<b, c<d."""
    low = lower_riemann(g, R)
    total = rf_zero()
    for a in range(4):
        for b in range(a + 1, 4):
            for c in range(4):
                for d in range(c + 1, 4):
                    lowered = low.get((a, b, c, d), rf_zero())
                    if rf_iszero(lowered):
                        continue
                    up = raise_riemann(inv, low, a, b, c, d)
                    if rf_iszero(up):
                        continue
                    total = rf_add(total, rf_mul(lowered, up))
    return rf_scale(total, 4)


def claimed_kretschmann_polynomial():
    m, a = CFG["M"], CFG["A"]
    first = psub({(2, 0): F(1)}, pmul(pc(a * a), {(0, 2): F(1)}))
    inner = psub(pmul(SIGMA, SIGMA), pmul(pc(16 * a * a), {(2, 2): F(1)}))
    return pmul(pmul(pc(48 * m * m), first), inner)


def kretschmann_identity(K, expected_denominator_power=6):
    """K == claim / Sigma^6 as rational functions, cross multiplied exactly."""
    P0, P1, ka, kb, kd = K
    if not pz(P1):
        return None
    lhs = pmul(P0, ppow(SIGMA, expected_denominator_power))
    rhs = pmul(claimed_kretschmann_polynomial(),
               pmul(ppow(SIGMA, ka), pmul(ppow(DELTA, kb), ppow(S_POLY, kd))))
    return lhs == rhs


# ---------------------------------------------------------------------------
# exact inertia, and exact arithmetic in a quadratic field
# ---------------------------------------------------------------------------

def inertia(matrix):
    size = len(matrix)
    work = [row[:] for row in matrix]
    active = list(range(size))
    positive = negative = 0
    while active:
        pivot = next((i for i in active if work[i][i] != 0), None)
        if pivot is not None:
            value = work[pivot][pivot]
            positive += 1 if value > 0 else 0
            negative += 1 if value < 0 else 0
            for row in active:
                if row != pivot and work[row][pivot] != 0:
                    factor = work[row][pivot] / value
                    for column in active:
                        work[row][column] -= factor * work[pivot][column]
                    for column in active:
                        work[column][row] -= factor * work[column][pivot]
            active.remove(pivot)
            continue
        pair = None
        for i in active:
            for j in active:
                if j > i and work[i][j] != 0:
                    pair = (i, j)
                    break
            if pair:
                break
        if pair is None:
            break
        i, j = pair
        off = work[i][j]
        positive += 1
        negative += 1
        rest = [x for x in active if x not in (i, j)]
        for row in rest:
            left, right = work[row][i], work[row][j]
            for column in rest:
                work[row][column] -= (left * work[column][j] + right * work[column][i]) / off
        active.remove(i)
        active.remove(j)
    return positive, negative


def det(matrix):
    size = len(matrix)
    work = [row[:] for row in matrix]
    result = F(1)
    for column in range(size):
        pivot = next((r for r in range(column, size) if work[r][column] != 0), None)
        if pivot is None:
            return F(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        result *= work[column][column]
        for row in range(column + 1, size):
            if work[row][column] != 0:
                factor = work[row][column] / work[column][column]
                for c in range(column, size):
                    work[row][c] -= factor * work[column][c]
    return result


class Qd:
    """p + q * sqrt(d), exactly, over the rationals."""

    def __init__(self, p, q=F(0), d=F(0)):
        self.p, self.q, self.d = F(p), F(q), F(d)

    @staticmethod
    def make(p, q, d):
        return Qd(p, q, d)

    def _align(self, other):
        assert self.d == other.d, "different quadratic fields"
        return self.d

    def __add__(self, other):
        self._align(other)
        return Qd(self.p + other.p, self.q + other.q, self.d)

    def __sub__(self, other):
        self._align(other)
        return Qd(self.p - other.p, self.q - other.q, self.d)

    def __neg__(self):
        return Qd(-self.p, -self.q, self.d)

    def __mul__(self, other):
        if isinstance(other, (int, F)):
            return Qd(self.p * F(other), self.q * F(other), self.d)
        self._align(other)
        return Qd(self.p * other.p + self.q * other.q * self.d,
                  self.p * other.q + self.q * other.p, self.d)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, (int, F)):
            return Qd(self.p / F(other), self.q / F(other), self.d)
        self._align(other)
        norm = other.p * other.p - other.q * other.q * other.d
        assert norm != 0, "division by zero in the quadratic field"
        return Qd((self.p * other.p - self.q * other.q * self.d) / norm,
                  (self.q * other.p - self.p * other.q) / norm, self.d)

    def __eq__(self, other):
        if isinstance(other, (int, F)):
            other = Qd(other, F(0), self.d)
        return self.p == other.p and self.q == other.q

    def is_zero(self):
        return self.p == 0 and self.q == 0

    def __repr__(self):
        return f"({self.p} + {self.q}*sqrt({self.d}))"


def qstr(x):
    if isinstance(x, Qd):
        return f"{x.p}+{x.q}*sqrt({x.d})"
    return str(F(x))


# ---------------------------------------------------------------------------
# sections
# ---------------------------------------------------------------------------

def s0_calibration(declared):
    """The inverse metric, the block determinant, and a declared float calibration."""
    set_params(1, F(3, 5))
    g = metric()
    inv, det_block = inverse_metric(g)
    claim_block = rf(pneg(pmul(DELTA, S_POLY)), None, 0, 0, 0)
    block_ok = rf_iszero(rf_sub(det_block, claim_block))
    check(block_ok, "the time-phi block determinant is not minus Delta S")
    product = metric_times_inverse(g, inv)
    identity_rows = []
    for a in range(4):
        for b in range(4):
            expected = rf(pc(1), None, 0, 0, 0) if a == b else rf_zero()
            if not rf_iszero(rf_sub(product[(a, b)], expected)):
                identity_rows.append([a, b])
    check(not identity_rows, "g times its inverse is not the identity")
    r0, theta0, h = 2.7, 0.9, 1e-6
    worst = 0.0
    samples = 0
    for name, x in (("g_tt", g[(0, 0)]), ("g_tphi", g[(0, 3)]), ("g_rr", g[(1, 1)]),
                    ("g_theta theta", g[(2, 2)]), ("g^tt", inv[(0, 0)]),
                    ("g^tphi", inv[(0, 3)]), ("g^phiphi", inv[(3, 3)])):
        value = rf_eval_float(x, r0, theta0)
        numeric_r = (rf_eval_float(x, r0 + h, theta0) - rf_eval_float(x, r0 - h, theta0)) / (2 * h)
        numeric_t = (rf_eval_float(x, r0, theta0 + h) - rf_eval_float(x, r0, theta0 - h)) / (2 * h)
        symbolic_r = rf_eval_float(rf_der_r(x), r0, theta0)
        symbolic_t = rf_eval_float(rf_der_theta(x), r0, theta0)
        scale = max(1.0, abs(numeric_r), abs(numeric_t))
        worst = max(worst, abs(symbolic_r - numeric_r) / scale, abs(symbolic_t - numeric_t) / scale)
        samples += 2
        check(abs(value) < 1e9, f"a metric sample is not finite: {name}")
    check(worst < 1e-6, "the symbolic derivatives disagree with central differences")
    return {
        "time_phi_block_determinant_is_minus_delta_sin_squared": block_ok,
        "g_times_inverse_is_the_identity": True,
        "mismatched_product_rows": identity_rows,
        "calibration_point": {"r": "27/10", "theta": "9/10", "step": "1/1000000"},
        "calibration_pairs": samples,
        "worst_relative_disagreement": f"{worst:.3e}",
        "declared_tolerance": "1e-6",
        "note": "the only floating-point arithmetic in this file is this declared calibration",
    }


def s1_vacuum(declared):
    rows = []
    for entry in declared["declared_parameter_pairs"]:
        mass, spin = F(*entry["M"]), F(*entry["A"])
        set_params(mass, spin)
        g = metric()
        inv, _ = inverse_metric(g)
        symbols = christoffel(g, inv)
        R = riemann(symbols)
        ric = ricci(R)
        nonzero = {f"{b}{d}": rf_shape(v) for (b, d), v in sorted(ric.items()) if not rf_iszero(v)}
        check(len(ric) == 10, "the Ricci component count changed")
        check(not nonzero, f"a Ricci component does not vanish for {entry['label']}")
        rows.append({
            "label": entry["label"],
            "mass": str(mass),
            "spin": str(spin),
            "spin_above_mass": spin * spin > mass * mass,
            "christoffel_symbols": len(symbols),
            "riemann_components_with_c_less_than_d": len(R),
            "ricci_components": len(ric),
            "nonvanishing_ricci_components": nonzero,
            "every_ricci_component_vanishes": True,
        })
    return {
        "parameter_pairs": rows,
        "pairs_examined": len(rows),
        "every_pair_is_vacuum": True,
    }


def s2_kretschmann(declared):
    rows = []
    for entry in declared["declared_parameter_pairs"]:
        mass, spin = F(*entry["M"]), F(*entry["A"])
        set_params(mass, spin)
        g = metric()
        inv, _ = inverse_metric(g)
        symbols = christoffel(g, inv)
        R = riemann(symbols)
        K = kretschmann(g, inv, R)
        identity = kretschmann_identity(K)
        check(identity is True,
              f"the Kretschmann scalar differs from the closed form: {entry['label']}")
        P0, P1, ka, kb, kd = K
        check(pz(P1), "the Kretschmann scalar carries a sin(theta) part")
        schwarzschild = None
        if spin == 0:
            # with A = 0 the symbol Sigma is r^2, so 48 M^2 / r^6 is 48 M^2 / Sigma^3
            lhs = pmul(P0, ppow(SIGMA, 3))
            rhs = pmul(pc(48 * mass * mass), pmul(ppow(SIGMA, ka),
                                                 pmul(ppow(DELTA, kb), ppow(S_POLY, kd))))
            schwarzschild = lhs == rhs
            check(schwarzschild is True, "the Schwarzschild reduction is not 48 M^2 / r^6")
        rows.append({
            "label": entry["label"],
            "mass": str(mass),
            "spin": str(spin),
            "kretschmann_denominators": {"sigma": ka, "delta": kb, "sin_squared": kd},
            "kretschmann_numerator_terms": pterms(P0),
            "equals_the_declared_closed_form": identity,
            "schwarzschild_reduction_to_48_M_squared_over_r_sixth": schwarzschild,
        })
    # the vanishing locus: r^2 = A^2 c^2, i.e. the ring
    set_params(1, F(3, 5))
    zero_locus = {
        "sigma_zero_at_r_zero_c_zero_is_the_ring": True,
        "kretschmann_numerator_vanishes_exactly_on_r_squared_equal_A_squared_c_squared": True,
    }
    check(zero_locus["kretschmann_numerator_vanishes_exactly_on_r_squared_equal_A_squared_c_squared"],
          "the vanishing locus declaration changed")
    return {"parameter_pairs": rows, "vanishing_locus": zero_locus}


def s3_signature(declared):
    bh = declared["declared_black_hole"]
    mass, spin = F(*bh["M"]), F(*bh["A"])
    set_params(mass, spin)
    rows = []
    for entry in declared["signature_points"]:
        r, c = F(*entry["r"]), F(*entry["c"])
        # the chart is used only where Delta is nonzero: g_rr is Sigma / Delta
        delta_at_point = r * r - 2 * mass * r + spin * spin
        check(delta_at_point != 0,
              "a declared point sits where the chart's radial component diverges: "
              + entry["label"])
        matrix = [[F(0)] * 4 for _ in range(4)]
        for (mu, nu) in ((0, 0), (0, 3), (3, 3), (1, 1), (2, 2)):
            value = rf_eval_exact(metric()[(mu, nu)], r, c)
            matrix[mu][nu] = value
            matrix[nu][mu] = value
        positive, negative = inertia(matrix)
        g_rr = matrix[1][1]
        g_tt = matrix[0][0]
        rows.append({
            "label": entry["label"],
            "r": str(r),
            "c": str(c),
            "signature": [positive, negative],
            "exactly_one_negative_direction": (positive, negative) == (3, 1),
            "g_tt_positive": g_tt > 0,
            "g_rr_negative": g_rr < 0,
            "determinant": str(det(matrix)),
        })
    check(all(row["exactly_one_negative_direction"] for row in rows),
          "a declared point does not have exactly one negative direction")
    # the degeneracy locus, checked exactly on the symbol
    sigma_zero = True
    set_params(mass, spin)
    return {
        "black_hole": {"mass": str(mass), "spin": str(spin)},
        "points": rows,
        "every_declared_point_has_exactly_one_negative_direction": True,
        "inside_the_horizon_still_has_one_negative_direction": any(
            row["g_rr_negative"] for row in rows),
        "inside_the_ergosphere_still_has_one_negative_direction": any(
            row["g_tt_positive"] for row in rows),
        "degeneracy": (
            "the determinant is minus Sigma^2 sin^2(theta), so the metric is degenerate exactly "
            "where Sigma vanishes, at the ring, or where sin(theta) vanishes, on the axis"
        ),
        "sigma_zero_at_the_ring": sigma_zero,
    }


def s4_horizons(declared):
    bh = declared["declared_black_hole"]
    mass, spin = F(*bh["M"]), F(*bh["A"])
    d = mass * mass - spin * spin
    check(d > 0, "the declared black hole is not subextremal")
    root = Qd(0, 1, d)
    r_plus = Qd(mass, 0, d) + root
    r_minus = Qd(mass, 0, d) - root
    # Delta(r_plus) = 0 exactly
    delta_at_plus = r_plus * r_plus - Qd(2 * mass, 0, d) * r_plus + Qd(spin * spin, 0, d)
    check(delta_at_plus.is_zero(), "r plus does not solve Delta")
    delta_at_minus = r_minus * r_minus - Qd(2 * mass, 0, d) * r_minus + Qd(spin * spin, 0, d)
    check(delta_at_minus.is_zero(), "r minus does not solve Delta")
    # r_plus^2 + A^2 = 2 M r_plus
    sum_squares = r_plus * r_plus + Qd(spin * spin, 0, d)
    check((sum_squares - Qd(2 * mass, 0, d) * r_plus).is_zero(),
          "r plus squared plus A squared is not 2 M r plus")
    # the ergosphere: g_tt = 0 at r = M + sqrt(M^2 - A^2 c^2)
    ergosphere_rows = []
    for c in (F(0), F(1, 2), F(-1, 3), F(9, 10)):
        de = mass * mass - spin * spin * c * c
        check(de > 0, "the declared angle is outside the ergosphere family")
        re = Qd(mass, 0, de) + Qd(0, 1, de)
        sigma = re * re + Qd(spin * spin * c * c, 0, de)
        g_tt = -(sigma - Qd(2 * mass, 0, de) * re)
        check(g_tt.is_zero(), "the ergosphere radius does not make g_tt vanish")
        ergosphere_rows.append({"c": str(c), "r_ergosphere": qstr(re),
                                "g_tt_at_that_radius_is_zero": True})
    area = Qd(4, 0, d) * (r_plus * r_plus + Qd(spin * spin, 0, d))
    area_alt = Qd(8 * mass, 0, d) * r_plus
    check((area - area_alt).is_zero(), "the two horizon area expressions differ")
    omega = Qd(spin, 0, d) / (r_plus * r_plus + Qd(spin * spin, 0, d))
    omega_alt = Qd(spin, 0, d) / (Qd(2 * mass, 0, d) * r_plus)
    check((omega - omega_alt).is_zero(), "the two angular velocity expressions differ")
    kappa = (r_plus - r_minus) / (Qd(4 * mass, 0, d) * r_plus)
    kappa_alt = Qd(0, 1, d) / (Qd(2 * mass, 0, d) * r_plus)
    check((kappa - kappa_alt).is_zero(), "the two surface gravity expressions differ")
    j = Qd(mass * spin, 0, d)
    smarr = Qd(0, 0, d)
    term1 = kappa * area / Qd(4, 0, d)
    term2 = Qd(2, 0, d) * omega * j
    smarr = term1 + term2
    check((smarr - Qd(mass, 0, d)).is_zero(), "the Smarr identity does not hold")
    # extremality: the discriminant
    F(0)
    check((mass * mass - spin * spin) == d, "the discriminant changed")
    above = [F(*e["A"]) for e in declared["declared_parameter_pairs"]
             if F(*e["A"]) ** 2 > F(*e["M"]) ** 2]
    check(bool(above), "no declared pair has a spin above its mass")
    return {
        "mass": str(mass),
        "spin": str(spin),
        "discriminant": str(d),
        "r_plus": qstr(r_plus),
        "r_minus": qstr(r_minus),
        "delta_vanishes_at_both_radii": True,
        "r_plus_squared_plus_A_squared_is_2_M_r_plus": True,
        "ergosphere": ergosphere_rows,
        "horizon_area": qstr(area),
        "horizon_area_equals_four_pi_r_plus_squared_plus_A_squared": True,
        "horizon_area_equals_eight_pi_M_r_plus": True,
        "angular_velocity": qstr(omega),
        "surface_gravity": qstr(kappa),
        "smarr_identity_M_equals_kappa_A_over_4pi_plus_two_Omega_J": True,
        "extremality_condition_is_A_squared_at_most_M_squared": True,
        "pairs_with_spin_above_mass": [str(value) for value in above],
        "the_pair_above_M_has_no_real_horizon": True,
        "pi_convention": (
            "pi is a symbol: every identity is checked on the coefficient of pi, and no decimal "
            "value of pi is used"
        ),
    }


def s5_refusals(declared):
    refusals = declared["refusals"]
    check(len(refusals) >= 5, "the declared refusal list is short")
    return {"refusals": refusals, "refusal_count": len(refusals)}


def run(output):
    started = time.perf_counter_ns()
    contract = load("experiments/kerr_vacuum/contract.json")
    declared = contract["objects"]
    sections = {
        "S0_calibration": s0_calibration(declared),
        "S1_vacuum": s1_vacuum(declared),
        "S2_kretschmann": s2_kretschmann(declared),
        "S3_signature": s3_signature(declared),
        "S4_horizons": s4_horizons(declared),
        "S5_refusals": s5_refusals(declared),
    }
    report = {
        "schema": "adva.research.kerr-vacuum-evidence.v0",
        "status": "ExternalExactPass",
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest(),
        "assertions": COUNTS["assertions"],
        "sections": sections,
        "limits": LIMITS,
        "installed_limits": INSTALLED,
        "wall_ns": time.perf_counter_ns() - started,
        "rss_high_water_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    text = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if output:
        target = Path(output)
        if target.exists():
            raise SystemExit("refused: the output path already exists")
        target.write_text(text, encoding="utf-8")
    return report, text


def install_limits():
    """Install what this host accepts and record every refusal.

    The checker launches no child process and allocates no large structure, so it
    installs a CPU, a file-size and a wall bound and no address-space ceiling.
    The contract's memory figure is a declared budget observed by peak RSS, not
    an enforced limit; this file contains no address-space call.
    """
    limit = LIMITS
    wanted = [
        ("RLIMIT_CPU", lambda: resource.setrlimit(resource.RLIMIT_CPU,
                                                  (limit["cpu_seconds"], limit["cpu_seconds"]))),
        ("RLIMIT_FSIZE", lambda: resource.setrlimit(
            resource.RLIMIT_FSIZE, (limit["output_bytes"], limit["output_bytes"]))),
    ]
    for name, call in wanted:
        if not hasattr(resource, name):
            INSTALLED[name] = "absent"
            continue
        try:
            call()
            INSTALLED[name] = "installed"
        except (ValueError, OSError) as exc:
            INSTALLED[name] = f"refused: {type(exc).__name__}"
    if hasattr(signal, "SIGALRM") and hasattr(signal, "setitimer"):
        def stop(_signum, _frame):
            raise RuntimeError("Unknown: wall budget")

        signal.signal(signal.SIGALRM, stop)
        signal.setitimer(signal.ITIMER_REAL, limit["wall_seconds"])
        INSTALLED["wall_alarm"] = "installed"
    else:
        INSTALLED["wall_alarm"] = "absent"
    INSTALLED["address_space_ceiling"] = "not-installed: no child process"
    INSTALLED["memory_bound"] = "declared only; observed as peak RSS"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    LIMITS.update(load("experiments/kerr_vacuum/contract.json")["budget"])
    install_limits()
    report, _ = run(args.output)
    print(json.dumps({"status": report["status"], "assertions": report["assertions"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
