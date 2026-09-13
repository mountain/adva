#!/usr/bin/env python3
"""A small, honest kernel of the area method (Chou-Gao-Zhang; Zhang Jingzhong).

Frozen contract: contract.json in this directory (Research 0129 section 3).

WHAT THIS IS
------------
The area method proves a constructive plane-geometry statement by eliminating the
constructed points in the reverse order of their construction, one point at a
time, each elimination justified by a named lemma, until only the free points
remain; the residue is then decided by exact field arithmetic.  This file
implements a deliberately small subset:

    constructions   on_line_d, is_midpoint, inter_ll, affine_comb
    quantities      S (doubled signed area), R (signed ratio of parallel
                    oriented segments), Py (Pythagoras difference)
    lemmas          on_line_d_area / on_line_d_pyth
                    midpoint_area  / midpoint_pyth
                    affine_comb_area / affine_comb_pyth
                    inter_ll_area / inter_ll_pyth
                    ratio_as_pythagoras
                    ratio_area
                    ratio_complement_area
                    area_cyclic, area_swap, pyth_swap_ends

Everything is exact: points are affine coordinate pairs whose coordinates are
rational functions built from sparse integer polynomials in the free points'
coordinates, and every coefficient is a fractions.Fraction.  There is no float
in any certified step.  All polynomials are over Q; a "rational function" here
is an unreduced pair (numerator, denominator) of polynomials, and equality of
two rational functions is decided by the polynomial identity
n1*d2 - n2*d1 == 0, which is exact.

CONVENTIONS
-----------
* Doubled area.  S(A,B,C) is the 3x3 determinant of the homogeneous triples
  (x_A,y_A,1),(x_B,y_B,1),(x_C,y_C,1), i.e. twice the signed area of ABC.
  Doubling is chosen so that the lemmas keep integer coefficients and no factor
  1/2 enters from the geometry itself.
* Ratio.  R(A,B,C,D) is the unique lambda with B - A = lambda*(D - C), computed
  as dot(B-A, D-C) / |D-C|^2.  That number is the ratio of the oriented
  distances AB/CD exactly when AB is parallel to CD; wherever R appears in a
  goal this run verifies the parallelism exactly as a side condition.
* Pyth.  Py(A,B,C) = AB^2 + BC^2 - CA^2.  It is affine in its first argument,
  which is what makes the two elimination lemmas for it work.

OUTCOMES
--------
The prover has exactly two outcomes for a goal: Proved, when the eliminated
residue is the zero rational function; and Unknown, with a reason, otherwise.
There is no "disproved" outcome.  A falsified companion is refuted separately,
on one explicit exact rational instance, and that refutation is recorded as a
control, never as a kernel outcome.

Run:  python3 calibration.py     (from this directory; writes evidence.json)
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import random
import re
import sys
import time
from fractions import Fraction

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
BUDGET = CONTRACT["budget"]

NVAR = 24
MAX_ASSERTIONS = int(BUDGET["max_assertions"])
ASSERTIONS = {"n": 0}
POLY_MULS = {"n": 0}
EVALS = {"n": 0}
EXACT = {"n": 0}
ZERO_MON = (0,) * NVAR


class Unsupported(Exception):
    """A construction or argument position this kernel does not implement."""


class BudgetExceeded(Exception):
    """The declared step budget was exhausted."""


def check(condition, message):
    ASSERTIONS["n"] += 1
    if ASSERTIONS["n"] > MAX_ASSERTIONS:
        raise AssertionError("assertion budget exceeded: " + str(ASSERTIONS["n"]))
    if not condition:
        raise AssertionError(message)
    return True


# --------------------------------------------------------------------------
# exact sparse polynomials over Q
# --------------------------------------------------------------------------

def p_const(value):
    value = Fraction(value)
    return {} if value == 0 else {ZERO_MON: value}


P_ONE = p_const(1)


def p_var(index):
    exponent = [0] * NVAR
    exponent[index] = 1
    return {tuple(exponent): Fraction(1)}


def p_add(a, b):
    if not a:
        return dict(b)
    if not b:
        return dict(a)
    out = dict(a)
    for monomial, coefficient in b.items():
        merged = out.get(monomial)
        if merged is None:
            out[monomial] = coefficient
        else:
            merged = merged + coefficient
            if merged:
                out[monomial] = merged
            else:
                del out[monomial]
    return out


def p_neg(a):
    return {monomial: -coefficient for monomial, coefficient in a.items()}


def p_sub(a, b):
    return p_add(a, p_neg(b))


def p_mul(a, b):
    POLY_MULS["n"] += 1
    if not a or not b:
        return {}
    out = {}
    for ma, ca in a.items():
        for mb, cb in b.items():
            monomial = tuple(x + y for x, y in zip(ma, mb))
            value = ca * cb
            merged = out.get(monomial)
            if merged is None:
                out[monomial] = value
            else:
                merged = merged + value
                if merged:
                    out[monomial] = merged
                else:
                    del out[monomial]
    return out


def p_scale(a, factor):
    factor = Fraction(factor)
    if factor == 0:
        return {}
    return {monomial: coefficient * factor for monomial, coefficient in a.items()}


def p_is_zero(a):
    return not a


def p_equal(a, b):
    return p_is_zero(p_sub(a, b))


def p_eval(a, values):
    total = Fraction(0)
    for monomial, coefficient in a.items():
        term = coefficient
        for index, exponent in enumerate(monomial):
            if exponent:
                term *= values[index] ** exponent
        total += term
    return total


def p_degree(a):
    if not a:
        return -1
    return max(sum(monomial) for monomial in a)


def p_str(a, varnames, limit=200):
    if not a:
        return "0"
    parts = []
    for monomial, coefficient in sorted(a.items(), key=lambda kv: (-sum(kv[0]), kv[0])):
        factors = []
        for index, exponent in enumerate(monomial):
            if exponent == 1:
                factors.append(varnames[index])
            elif exponent > 1:
                factors.append(varnames[index] + "^" + str(exponent))
        body = "*".join(factors) if factors else "1"
        magnitude = abs(coefficient)
        if not factors:
            label = str(magnitude)
        elif magnitude == 1:
            label = body
        else:
            label = str(magnitude) + "*" + body
        negative = coefficient < 0
        if not parts:
            parts.append(("-" if negative else "") + label)
        else:
            parts.append((" - " if negative else " + ") + label)
    text = "".join(parts)
    if len(text) <= limit:
        return text
    return text[:limit] + "...[+" + str(len(a)) + " terms]"


# --------------------------------------------------------------------------
# exact rational functions: an unreduced pair of polynomials
# --------------------------------------------------------------------------

RF_ONE = (P_ONE, P_ONE)
RF_ZERO = (p_const(0), P_ONE)


def rf_const(value):
    value = Fraction(value)
    return (p_const(value), P_ONE)


def rf_add(x, y):
    return (p_add(p_mul(x[0], y[1]), p_mul(y[0], x[1])), p_mul(x[1], y[1]))


def rf_neg(x):
    return (p_neg(x[0]), x[1])


def rf_sub(x, y):
    return rf_add(x, rf_neg(y))


def rf_mul(x, y):
    return (p_mul(x[0], y[0]), p_mul(x[1], y[1]))


def rf_div(x, y):
    return (p_mul(x[0], y[1]), p_mul(x[1], y[0]))


def rf_is_zero(x):
    return p_is_zero(x[0])


def rf_equal(x, y):
    """Exact: x == y as rational functions iff num_x*den_y - num_y*den_x is the zero polynomial."""
    return p_is_zero(p_sub(p_mul(x[0], y[1]), p_mul(y[0], x[1])))


def rf_eval(x, values):
    denominator = p_eval(x[1], values)
    if denominator == 0:
        raise ZeroDivisionError("rational function has a zero denominator at this instance")
    return _exact(p_eval(x[0], values) / denominator, "rational function evaluation")


def _exact(value, where):
    """Every certified value must be a Fraction; a float would raise here rather than pass silently."""
    if not isinstance(value, Fraction):
        raise TypeError("a non-rational value reached a certified step at " + where + ": " + repr(value))
    EXACT["n"] += 1
    return value


def rf_is_constant(x):
    return len(x[0]) <= 1 and len(x[1]) == 1


def rf_constant_value(x):
    return Fraction(x[0].get(ZERO_MON, 0)) / Fraction(x[1][ZERO_MON])


# --------------------------------------------------------------------------
# the three geometric quantities, on affine coordinates
# --------------------------------------------------------------------------

def _d2(p, q):
    dx = rf_sub(p[0], q[0])
    dy = rf_sub(p[1], q[1])
    return rf_add(rf_mul(dx, dx), rf_mul(dy, dy))


def S_rf(a, b, c):
    """Doubled signed area: det[[ax,ay,1],[bx,by,1],[cx,cy,1]]."""
    term_a = rf_mul(a[0], rf_sub(b[1], c[1]))
    term_b = rf_mul(b[0], rf_sub(c[1], a[1]))
    term_c = rf_mul(c[0], rf_sub(a[1], b[1]))
    return rf_add(rf_add(term_a, term_b), term_c)


def Py_rf(a, b, c):
    return rf_sub(rf_add(_d2(a, b), _d2(b, c)), _d2(c, a))


def R_rf(a, b, c, d):
    """Signed lambda with B - A = lambda*(D - C); the ratio AB/CD when AB || CD."""
    dx = rf_sub(b[0], a[0])
    dy = rf_sub(b[1], a[1])
    ex = rf_sub(d[0], c[0])
    ey = rf_sub(d[1], c[1])
    return rf_div(rf_add(rf_mul(dx, ex), rf_mul(dy, ey)), _d2(c, d))


# --------------------------------------------------------------------------
# term language: expressions over the three quantities
# --------------------------------------------------------------------------

def T_num(value):
    value = Fraction(value)
    if value < 0:
        return ("neg", ("num", -value))
    return ("num", value)


def T_S(a, b, c):
    return ("S", a, b, c)


def T_R(a, b, c, d):
    return ("R", a, b, c, d)


def T_Py(a, b, c):
    return ("Py", a, b, c)


def T_add(x, y):
    return ("add", x, y)


def T_sub(x, y):
    return ("sub", x, y)


def T_mul(x, y):
    return ("mul", x, y)


def T_div(x, y):
    return ("div", x, y)


def T_neg(x):
    return ("neg", x)


BINARY = ("add", "sub", "mul", "div")


def t_children(e):
    kind = e[0]
    if kind in BINARY:
        return [e[1], e[2]]
    if kind == "neg":
        return [e[1]]
    return []


def t_rebuild(e, children):
    kind = e[0]
    if kind in BINARY:
        return (kind, children[0], children[1])
    if kind == "neg":
        return (kind, children[0])
    return e


def t_str(e):
    kind = e[0]
    if kind == "num":
        value = e[1]
        if value.denominator == 1:
            return str(value.numerator)
        return str(value.numerator) + "/" + str(value.denominator)
    if kind == "S":
        return "S(" + e[1] + "," + e[2] + "," + e[3] + ")"
    if kind == "Py":
        return "Py(" + e[1] + "," + e[2] + "," + e[3] + ")"
    if kind == "R":
        return "R(" + e[1] + "," + e[2] + "," + e[3] + "," + e[4] + ")"
    if kind == "neg":
        return "(-" + t_str(e[1]) + ")"
    symbol = {"add": "+", "sub": "-", "mul": "*", "div": "/"}[kind]
    return "(" + t_str(e[1]) + " " + symbol + " " + t_str(e[2]) + ")"


TOKEN_RE = re.compile(r"\s*(\d+/\d+|\d+|[A-Za-z_][A-Za-z_0-9]*|[(),+\-*/])")


def t_parse(text):
    tokens = []
    position = 0
    while position < len(text):
        match = TOKEN_RE.match(text, position)
        if match is None:
            raise ValueError("cannot tokenize at " + repr(text[position:position + 20]))
        tokens.append(match.group(1))
        position = match.end()
    cursor = {"i": 0}

    def peek():
        if cursor["i"] >= len(tokens):
            raise ValueError("unexpected end of expression")
        return tokens[cursor["i"]]

    def take():
        token = peek()
        cursor["i"] += 1
        return token

    def expect(token):
        got = take()
        if got != token:
            raise ValueError("expected " + repr(token) + " got " + repr(got))

    def parse_point():
        token = take()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", token):
            raise ValueError("expected a point name, got " + repr(token))
        return token

    def parse_expr():
        token = peek()
        if token == "(":
            take()
            if peek() == "-":
                take()
                inner = parse_expr()
                expect(")")
                return ("neg", inner)
            left = parse_expr()
            operator = take()
            if operator not in ("+", "-", "*", "/"):
                raise ValueError("expected an operator, got " + repr(operator))
            right = parse_expr()
            expect(")")
            return ({"+": "add", "-": "sub", "*": "mul", "/": "div"}[operator], left, right)
        if token == "S":
            take()
            expect("(")
            a = parse_point()
            expect(",")
            b = parse_point()
            expect(",")
            c = parse_point()
            expect(")")
            return T_S(a, b, c)
        if token == "Py":
            take()
            expect("(")
            a = parse_point()
            expect(",")
            b = parse_point()
            expect(",")
            c = parse_point()
            expect(")")
            return T_Py(a, b, c)
        if token == "R":
            take()
            expect("(")
            a = parse_point()
            expect(",")
            b = parse_point()
            expect(",")
            c = parse_point()
            expect(",")
            d = parse_point()
            expect(")")
            return T_R(a, b, c, d)
        if re.fullmatch(r"\d+/\d+", token):
            take()
            numerator, denominator = token.split("/")
            return T_num(Fraction(int(numerator), int(denominator)))
        if re.fullmatch(r"\d+", token):
            take()
            return T_num(Fraction(int(token)))
        raise ValueError("unexpected token " + repr(token))

    result = parse_expr()
    if cursor["i"] != len(tokens):
        raise ValueError("trailing tokens in " + repr(text))
    return result


def t_get_at(e, path):
    node = e
    for index in path:
        node = t_children(node)[index]
    return node


def t_subst_at(e, path, replacement):
    if not path:
        return replacement
    children = list(t_children(e))
    children[path[0]] = t_subst_at(children[path[0]], path[1:], replacement)
    return t_rebuild(e, children)


def t_points(e):
    """Ordered, duplicate-free list of the point names occurring in e."""
    out = []

    def walk(node):
        if node[0] in ("S", "Py", "R"):
            for name in node[1:]:
                if name not in out:
                    out.append(name)
        for child in t_children(node):
            walk(child)

    walk(e)
    return out


def t_size(e):
    return 1 + sum(t_size(child) for child in t_children(e))


def t_eval(cfg, e):
    EVALS["n"] += 1
    kind = e[0]
    if kind == "num":
        return rf_const(e[1])
    if kind == "S":
        return S_rf(cfg.coords(e[1]), cfg.coords(e[2]), cfg.coords(e[3]))
    if kind == "Py":
        return Py_rf(cfg.coords(e[1]), cfg.coords(e[2]), cfg.coords(e[3]))
    if kind == "R":
        return R_rf(cfg.coords(e[1]), cfg.coords(e[2]), cfg.coords(e[3]), cfg.coords(e[4]))
    if kind == "add":
        return rf_add(t_eval(cfg, e[1]), t_eval(cfg, e[2]))
    if kind == "sub":
        return rf_sub(t_eval(cfg, e[1]), t_eval(cfg, e[2]))
    if kind == "mul":
        return rf_mul(t_eval(cfg, e[1]), t_eval(cfg, e[2]))
    if kind == "div":
        return rf_div(t_eval(cfg, e[1]), t_eval(cfg, e[2]))
    if kind == "neg":
        return rf_neg(t_eval(cfg, e[1]))
    raise ValueError("unknown term " + repr(kind))


# --------------------------------------------------------------------------
# configurations: free points and constructions
# --------------------------------------------------------------------------

BROKEN = {"mode": None}


class Config:
    def __init__(self, name):
        self.name = name
        self.varnames = []
        self.free_order = []
        self.free = {}
        self.defs = {}
        self.order = []
        self.side_conditions = []
        self._coords = {}
        self._apex = {}

    def add_free(self, point):
        if point in self.free or point in self.defs:
            raise ValueError("point " + point + " already declared")
        index_x = len(self.varnames)
        self.varnames.append("x_" + point)
        index_y = len(self.varnames)
        self.varnames.append("y_" + point)
        if len(self.varnames) > NVAR:
            raise ValueError("variable budget " + str(NVAR) + " exceeded")
        self.free[point] = (index_x, index_y)
        self.free_order.append(point)
        return point

    def add_line_d(self, point, q, r, ratio):
        self._declare(point, ("line_d", q, r, Fraction(ratio)))
        return point

    def add_midpoint(self, point, q, r):
        self._declare(point, ("midpoint", q, r))
        return point

    def add_inter_ll(self, point, a, b, c, d):
        self._declare(point, ("inter_ll", a, b, c, d))
        return point

    def add_affine_comb(self, point, terms):
        self._declare(point, ("affine_comb", tuple((q, Fraction(w)) for q, w in terms)))
        return point

    def _declare(self, point, definition):
        if point in self.free or point in self.defs:
            raise ValueError("point " + point + " already declared")
        for name in definition[1:]:
            if isinstance(name, str) and name not in self.free and name not in self.defs:
                raise ValueError("construction uses undeclared point " + name)
        self.defs[point] = definition
        self.order.append(point)

    def kind(self, point):
        return self.defs[point][0]

    def note(self, kind, payload):
        self.side_conditions.append({"kind": kind, "payload": payload})

    def coords(self, point):
        cached = self._coords.get(point)
        if cached is not None:
            return cached
        if point in self.free:
            index_x, index_y = self.free[point]
            value = ((p_var(index_x), P_ONE), (p_var(index_y), P_ONE))
            self._coords[point] = value
            return value
        if point not in self.defs:
            raise ValueError("unknown point " + point)
        definition = self.defs[point]
        kind = definition[0]
        if kind == "line_d":
            _, q, r, ratio = definition
            value = self._affine(point, [(q, 1 - ratio), (r, ratio)])
        elif kind == "midpoint":
            _, q, r = definition
            value = self._affine(point, [(q, Fraction(1, 2)), (r, Fraction(1, 2))])
        elif kind == "affine_comb":
            value = self._affine(point, list(definition[1]))
        elif kind == "inter_ll":
            _, a, b, c, d = definition
            line_one = _cross(self._homogeneous(a), self._homogeneous(b))
            line_two = _cross(self._homogeneous(c), self._homogeneous(d))
            meet = _cross(line_one, line_two)
            z = meet[2]
            self.note("nonzero_denominator",
                      {"point": point, "what": "z of " + point + " = line(" + a + "," + b
                       + ") cap line(" + c + "," + d + ")", "polynomial": z[0]})
            value = (rf_div(meet[0], z), rf_div(meet[1], z))
        else:
            raise Unsupported("construction " + kind + " is not implemented")
        self._coords[point] = value
        return value

    def _affine(self, point, terms):
        total = Fraction(0)
        for _, weight in terms:
            total += weight
        if total != 1:
            raise ValueError("affine weights for " + point + " do not sum to 1")
        x = RF_ZERO
        y = RF_ZERO
        for other, weight in terms:
            other_coords = self.coords(other)
            x = rf_add(x, rf_mul(rf_const(weight), other_coords[0]))
            y = rf_add(y, rf_mul(rf_const(weight), other_coords[1]))
        return (x, y)

    def _homogeneous(self, point):
        x, y = self.coords(point)
        return (x, y, RF_ONE)

    def affine_terms(self, point):
        """The elimination coefficients of an affine-combination construction, or None."""
        definition = self.defs.get(point)
        if definition is None:
            return None
        kind = definition[0]
        if kind == "line_d":
            _, q, r, ratio = definition
            if BROKEN["mode"] == "lemma_sign":
                return [(q, 1 - ratio), (r, -ratio)]
            return [(q, 1 - ratio), (r, ratio)]
        if kind == "midpoint":
            _, q, r = definition
            if BROKEN["mode"] == "midpoint_ratio":
                return [(q, Fraction(1, 3)), (r, Fraction(2, 3))]
            return [(q, Fraction(1, 2)), (r, Fraction(1, 2))]
        if kind == "affine_comb":
            return list(definition[1])
        return None


def _cross(u, v):
    return (
        rf_sub(rf_mul(u[1], v[2]), rf_mul(u[2], v[1])),
        rf_sub(rf_mul(u[2], v[0]), rf_mul(u[0], v[2])),
        rf_sub(rf_mul(u[0], v[1]), rf_mul(u[1], v[0])),
    )


# --------------------------------------------------------------------------
# the elimination lemmas as explicit rewrite rules
# --------------------------------------------------------------------------

AREA_LEMMA_NAME = {
    "line_d": "on_line_d_area",
    "midpoint": "midpoint_area",
    "affine_comb": "affine_comb_area",
}
PYTH_LEMMA_NAME = {
    "line_d": "on_line_d_pyth",
    "midpoint": "midpoint_pyth",
    "affine_comb": "affine_comb_pyth",
}

LEMMA_STATEMENTS = {
    "on_line_d_area": "If P is constructed by on_line_d(P,Q,R,r), that is P = Q + r*(R-Q) = (1-r)*Q + r*R, then for all points X and Y the doubled signed area is linear in P: S(P,X,Y) = (1-r)*S(Q,X,Y) + r*S(R,X,Y).",
    "on_line_d_pyth": "If P = (1-r)*Q + r*R then the Pythagoras difference is affine in its first argument and Py(P,X,Y) = (1-r)*Py(Q,X,Y) + r*Py(R,X,Y) for all X,Y.",
    "midpoint_area": "If P is the midpoint of QR, P = (1/2)*Q + (1/2)*R, then S(P,X,Y) = (1/2)*S(Q,X,Y) + (1/2)*S(R,X,Y) for all X,Y. This is the r = 1/2 instance of the on_line_d lemma, kept as a named lemma of its own and verified independently.",
    "midpoint_pyth": "If P is the midpoint of QR then Py(P,X,Y) = (1/2)*Py(Q,X,Y) + (1/2)*Py(R,X,Y) for all X,Y.",
    "affine_comb_area": "If P = sum_i r_i*Q_i with sum_i r_i = 1, then S(P,X,Y) = sum_i r_i*S(Q_i,X,Y) for all X,Y.",
    "affine_comb_pyth": "If P = sum_i r_i*Q_i with sum_i r_i = 1, then Py(P,X,Y) = sum_i r_i*Py(Q_i,X,Y) for all X,Y.",
    "inter_ll_area": "If P is the meet of line(A,B) and line(C,D), and P = alpha*A + beta*B is its affine representation on line AB, with alpha = S(C,D,B)/(S(C,D,B)-S(C,D,A)) and beta = -S(C,D,A)/(S(C,D,B)-S(C,D,A)) and alpha+beta = 1, then S(P,X,Y) = alpha*S(A,X,Y) + beta*S(B,X,Y) = [S(C,D,B)*S(A,X,Y) - S(C,D,A)*S(B,X,Y)] / (S(C,D,B) - S(C,D,A)). The denominator is the non-degeneracy condition: it vanishes exactly when line CD is parallel to line AB.",
    "inter_ll_pyth": "With P = line(A,B) cap line(C,D) and the same alpha, beta, Py is affine in its first argument, so Py(P,X,Y) = [S(C,D,B)*Py(A,X,Y) - S(C,D,A)*Py(B,X,Y)] / (S(C,D,B) - S(C,D,A)).",
    "ratio_as_pythagoras": "For any four points, R(A,B,C,D) = [Py(A,D,C) - Py(B,D,C)] / Py(C,D,C). Indeed Py(C,D,C) = 2*|CD|^2 and Py(A,D,C) - Py(B,D,C) = 2*(B-A).(D-C).",
    "ratio_area": "If A, B, D are collinear and X is any point with S(A,D,X) nonzero, then R(A,B,A,D) = S(A,B,X)/S(A,D,X), because both doubled areas share the base line through A and the apex X, so their ratio is the ratio of the directed bases.",
    "ratio_complement_area": "Under the same collinearity hypothesis, R/(1-R) with R = R(A,B,A,D) equals S(A,B,X)/(S(A,D,X) - S(A,B,X)); this is the form the prover uses so that no denominator is inflated by an unnecessary cancellation.",
    "area_cyclic": "S(A,B,C) = S(B,C,A): a determinant is invariant under a cyclic permutation of its rows.",
    "area_swap": "S(A,B,C) = -S(B,A,C): swapping two rows of a determinant changes its sign.",
    "pyth_swap_ends": "Py(A,B,C) = Py(C,B,A): the Pythagoras difference is symmetric in its two end arguments.",
}


def _scale_term(weight, term):
    if weight == 0:
        return T_num(0)
    if weight == 1:
        return term
    if weight == -1:
        return T_neg(term)
    return T_mul(T_num(weight), term)


def _affine_expansion(terms, node_builder):
    out = None
    for point, weight in terms:
        if weight == 0:
            continue
        term = _scale_term(weight, node_builder(point))
        out = term if out is None else T_add(out, term)
    return T_num(0) if out is None else out


def pick_apex(cfg, a, b, d):
    key = (a, b, d)
    cached = cfg._apex.get(key)
    if cached is not None:
        return cached
    for candidate in cfg.free_order:
        if candidate in (a, b, d):
            continue
        first = t_eval(cfg, T_S(a, d, candidate))
        if rf_is_zero(first):
            continue
        second = rf_sub(first, t_eval(cfg, T_S(a, b, candidate)))
        if rf_is_zero(second):
            continue
        cfg._apex[key] = candidate
        return candidate
    raise Unsupported("no free point outside lines " + a + d + " and " + a + b + " is available as an apex")


def rule_ratio_complement_area(node, cfg):
    if node[0] != "div":
        return None
    numerator, denominator = node[1], node[2]
    if denominator[0] != "sub":
        return None
    if numerator[0] != "R" or numerator[1] != numerator[3]:
        return None
    left, right = denominator[1], denominator[2]
    if left == ("num", Fraction(1)) and right == numerator:
        a, b, d = numerator[1], numerator[2], numerator[4]
    elif right == ("num", Fraction(1)) and left == numerator:
        a, b, d = numerator[1], numerator[2], numerator[4]
    else:
        return None
    apex = pick_apex(cfg, a, b, d)
    cfg.note("collinear", {"points": [a, b, d], "why": "ratio_complement_area"})
    return T_div(T_S(a, b, apex), T_sub(T_S(a, d, apex), T_S(a, b, apex)))


def direct_elimination(node, point, cfg):
    """Rewrite the quantity at `node` so that `point` disappears from it, or return None."""
    kind = node[0]
    if kind == "S":
        a, b, c = node[1], node[2], node[3]
        if point not in (a, b, c):
            return None
        if a == point:
            how = cfg.defs[point][0]
            if how == "inter_ll":
                _, p, q, r, s = cfg.defs[point]
                numerator = T_sub(T_mul(T_S(r, s, q), T_S(p, b, c)),
                                  T_mul(T_S(r, s, p), T_S(q, b, c)))
                denominator = T_sub(T_S(r, s, q), T_S(r, s, p))
                cfg.note("nonzero_denominator",
                         {"point": point, "what": "inter_ll_area denominator for " + point,
                          "expression_string": t_str(denominator)})
                return ("inter_ll_area", T_div(numerator, denominator))
            terms = cfg.affine_terms(point)
            if terms is None:
                raise Unsupported("no area elimination lemma for the construction of " + point)
            return (AREA_LEMMA_NAME[how], _affine_expansion(terms, lambda q: T_S(q, b, c)))
        return ("area_cyclic", T_S(b, c, a))
    if kind == "Py":
        a, b, c = node[1], node[2], node[3]
        if point not in (a, b, c):
            return None
        if a == point:
            how = cfg.defs[point][0]
            if how == "inter_ll":
                _, p, q, r, s = cfg.defs[point]
                numerator = T_sub(T_mul(T_S(r, s, q), T_Py(p, b, c)),
                                  T_mul(T_S(r, s, p), T_Py(q, b, c)))
                denominator = T_sub(T_S(r, s, q), T_S(r, s, p))
                cfg.note("nonzero_denominator",
                         {"point": point, "what": "inter_ll_pyth denominator for " + point,
                          "expression_string": t_str(denominator)})
                return ("inter_ll_pyth", T_div(numerator, denominator))
            terms = cfg.affine_terms(point)
            if terms is None:
                raise Unsupported("no Pythagoras elimination lemma for the construction of " + point)
            return (PYTH_LEMMA_NAME[how], _affine_expansion(terms, lambda q: T_Py(q, b, c)))
        if c == point:
            return ("pyth_swap_ends", T_Py(c, b, a))
        raise Unsupported("Py with the eliminated point " + point
                          + " strictly in the middle argument is not implemented")
    if kind == "R":
        a, b, c, d = node[1], node[2], node[3], node[4]
        if point not in (a, b, c, d):
            return None
        if a == c and point in (b, d):
            apex = pick_apex(cfg, a, b, d)
            cfg.note("collinear", {"points": [a, b, d], "why": "ratio_area"})
            return ("ratio_area", T_div(T_S(a, b, apex), T_S(a, d, apex)))
        if point in (a, b, c):
            return ("ratio_as_pythagoras",
                    T_div(T_sub(T_Py(a, d, c), T_Py(b, d, c)), T_Py(c, d, c)))
        raise Unsupported("R with the eliminated point " + point
                          + " only in the fourth argument is not implemented")
    return None


def find_rewrite(node, path, point, cfg):
    replacement = rule_ratio_complement_area(node, cfg)
    if replacement is not None:
        return (path, replacement, "ratio_complement_area")
    if node[0] in ("S", "Py", "R"):
        found = direct_elimination(node, point, cfg)
        if found is None:
            return None
        return (path, found[1], found[0])
    for index, child in enumerate(t_children(node)):
        result = find_rewrite(child, path + (index,), point, cfg)
        if result is not None:
            return result
    return None


def t_contains_point(e, point):
    if e[0] in ("S", "Py", "R") and point in e[1:]:
        return True
    return any(t_contains_point(child, point) for child in t_children(e))


# --------------------------------------------------------------------------
# numeric evaluation at an exact rational instance (still all Fraction)
# --------------------------------------------------------------------------

def numeric_point(cfg, point, values, cache):
    cached = cache.get(point)
    if cached is not None:
        return cached
    x, y = cfg.coords(point)
    value = (rf_eval(x, values), rf_eval(y, values))
    cache[point] = value
    return value


def t_eval_numeric(cfg, e, values, cache):
    """Evaluate a term at one exact rational instance.  Fractions throughout; no float."""
    return _exact(_t_eval_numeric(cfg, e, values, cache), "term evaluation " + e[0])


def _t_eval_numeric(cfg, e, values, cache):
    EVALS["n"] += 1
    kind = e[0]
    if kind == "num":
        return e[1]
    if kind == "S":
        a = numeric_point(cfg, e[1], values, cache)
        b = numeric_point(cfg, e[2], values, cache)
        c = numeric_point(cfg, e[3], values, cache)
        return a[0] * (b[1] - c[1]) + b[0] * (c[1] - a[1]) + c[0] * (a[1] - b[1])
    if kind == "Py":
        a = numeric_point(cfg, e[1], values, cache)
        b = numeric_point(cfg, e[2], values, cache)
        c = numeric_point(cfg, e[3], values, cache)
        return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
                + (b[0] - c[0]) ** 2 + (b[1] - c[1]) ** 2
                - (a[0] - c[0]) ** 2 - (a[1] - c[1]) ** 2)
    if kind == "R":
        a = numeric_point(cfg, e[1], values, cache)
        b = numeric_point(cfg, e[2], values, cache)
        c = numeric_point(cfg, e[3], values, cache)
        d = numeric_point(cfg, e[4], values, cache)
        numerator = (b[0] - a[0]) * (d[0] - c[0]) + (b[1] - a[1]) * (d[1] - c[1])
        denominator = (d[0] - c[0]) ** 2 + (d[1] - c[1]) ** 2
        if denominator == 0:
            raise ZeroDivisionError("R has a zero denominator at this instance")
        return numerator / denominator
    if kind == "add":
        return t_eval_numeric(cfg, e[1], values, cache) + t_eval_numeric(cfg, e[2], values, cache)
    if kind == "sub":
        return t_eval_numeric(cfg, e[1], values, cache) - t_eval_numeric(cfg, e[2], values, cache)
    if kind == "mul":
        return t_eval_numeric(cfg, e[1], values, cache) * t_eval_numeric(cfg, e[2], values, cache)
    if kind == "div":
        left = t_eval_numeric(cfg, e[1], values, cache)
        right = t_eval_numeric(cfg, e[2], values, cache)
        if right == 0:
            raise ZeroDivisionError("division by zero at this instance")
        return left / right
    if kind == "neg":
        return -t_eval_numeric(cfg, e[1], values, cache)
    raise ValueError("unknown term " + repr(kind))


MAX_EXPRESSION_CHARS = 20000


def _stored_expr(e):
    text = t_str(e)
    if len(text) <= MAX_EXPRESSION_CHARS:
        return {"expression": text, "chars": len(text), "truncated": False}
    return {"expression_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "chars": len(text), "truncated": True}


def eliminate_point(cfg, expr, point, trace, max_steps):
    steps = 0
    while True:
        found = find_rewrite(expr, (), point, cfg)
        if found is None:
            break
        path, replacement, lemma = found
        steps += 1
        if steps > max_steps:
            raise BudgetExceeded("step budget exhausted while eliminating " + point)
        before_subterm = t_get_at(expr, path)
        new_expr = t_subst_at(expr, path, replacement)
        record = {
            "step": len(trace),
            "lemma": lemma,
            "pass_point": point,
            "point_eliminated": None if lemma == "ratio_complement_area" else point,
            "position": list(path),
            "before_subterm": t_str(before_subterm),
            "after_subterm": t_str(replacement),
        }
        record.update({"before_" + k: v for k, v in _stored_expr(expr).items()})
        record.update({"after_" + k: v for k, v in _stored_expr(new_expr).items()})
        trace.append(record)
        expr = new_expr
    if t_contains_point(expr, point):
        raise Unsupported("no applicable elimination rule for point " + point
                          + " (see what_is_not_implemented)")
    return expr


def run_proof(cfg, goal_left, goal_right, order_mode="reverse"):
    max_steps = int(OBJ["max_elimination_steps_per_point"])
    expr = T_sub(goal_left, goal_right)
    initial = t_str(expr)
    trace = []
    sequence = list(cfg.order) if order_mode == "construction" else list(reversed(cfg.order))
    for point in sequence:
        expr = eliminate_point(cfg, expr, point, trace, max_steps)
    residual = t_eval(cfg, expr)
    elimination_steps = sum(1 for step in trace if step["point_eliminated"] is not None)
    return {
        "initial_expression": initial,
        "final_expression": t_str(expr),
        "final_ast": expr,
        "trace": trace,
        "residual": residual,
        "proved": rf_is_zero(residual),
        "order_mode": order_mode,
        "order": list(sequence),
        "elimination_steps": elimination_steps,
        "auxiliary_rewrite_steps": len(trace) - elimination_steps,
        "step_budget_per_point": max_steps,
    }


# --------------------------------------------------------------------------
# replay: re-parse the recorded trace and re-derive every step
# --------------------------------------------------------------------------

def replay(cfg, recorded, strict=True):
    """Re-verify every recorded step from the recorded strings."""
    trace = recorded["trace"]
    reproduced = 0
    semantic = 0
    failures = []
    for step in trace:
        before = t_parse(step["before_expression"])
        at_position = t_get_at(before, tuple(step["position"]))
        if t_str(at_position) != step["before_subterm"]:
            failures.append({"step": step["step"], "why": "recorded position does not hold the recorded subterm"})
            continue
        if step["lemma"] == "ratio_complement_area":
            replacement = rule_ratio_complement_area(at_position, cfg)
        else:
            found = direct_elimination(at_position, step["point_eliminated"], cfg)
            if found is None:
                failures.append({"step": step["step"], "why": "the recorded lemma does not apply to the recorded subterm"})
                continue
            if found[0] != step["lemma"]:
                failures.append({"step": step["step"], "why": "the recorded lemma name is not the one that applies"})
                continue
            replacement = found[1]
        if replacement is None:
            failures.append({"step": step["step"], "why": "the recorded lemma does not apply to the recorded subterm"})
            continue
        replayed = t_subst_at(before, tuple(step["position"]), replacement)
        reproduced_here = t_str(replayed) == step["after_expression"]
        if reproduced_here:
            reproduced += 1
        else:
            failures.append({"step": step["step"], "why": "replay does not reproduce the recorded after-expression"})
        left = t_eval(cfg, t_parse(step["before_subterm"]))
        right = t_eval(cfg, t_parse(step["after_subterm"]))
        semantic_here = rf_equal(left, right)
        if semantic_here:
            semantic += 1
        else:
            failures.append({"step": step["step"], "why": "the recorded before/after subterms are not equal as exact rational functions"})
        if strict:
            check(reproduced_here,
                  "replay did not reproduce step " + str(step["step"]) + " of " + cfg.name)
            check(semantic_here,
                  "step " + str(step["step"]) + " of " + cfg.name
                  + " is not an exact rational-function identity")
    return {
        "steps_recorded": len(trace),
        "steps_structurally_reproduced": reproduced,
        "steps_semantically_verified": semantic,
        "all_steps_reproduced": reproduced == len(trace),
        "all_steps_semantically_verified": semantic == len(trace),
        "failures": failures[:8],
        "failure_count": len(failures),
    }


# --------------------------------------------------------------------------
# lemma verification
# --------------------------------------------------------------------------

def verify_lemma_symbolically(name, build):
    cfg = Config("lemma:" + name)
    for point in build["free"]:
        cfg.add_free(point)
    for construction in build["construct"]:
        construction(cfg)
    left = t_eval(cfg, build["left"](cfg))
    right = t_eval(cfg, build["right"](cfg))
    return cfg, rf_equal(left, right)


def lemma_configuration(name):
    """Return a builder dict for each lemma, with its free points and constructions."""
    if name in ("on_line_d_area", "on_line_d_pyth", "midpoint_area", "midpoint_pyth",
                "affine_comb_area", "affine_comb_pyth"):

        def construct(cfg, which):
            if which == "midpoint":
                cfg.add_midpoint("P", "Q", "R")
            elif which == "affine":
                cfg.add_affine_comb("P", [("Q", Fraction(1, 3)), ("R", Fraction(1, 2)), ("T", Fraction(1, 6))])
            else:
                cfg.add_line_d("P", "Q", "R", Fraction(2, 3))

        def node(quantity):
            if quantity == "S":
                return lambda cfg: T_S("P", "X", "Y")
            return lambda cfg: T_Py("P", "X", "Y")

        def expansion(quantity):
            def built(cfg):
                # goes through Config.affine_terms, the same code path the prover uses, so a
                # deliberately broken variant changes the lemma's own verification too
                terms = cfg.affine_terms("P")
                maker = T_S if quantity == "S" else T_Py
                return _affine_expansion(terms, lambda q: maker(q, "X", "Y"))
            return built

        quantity = "S" if name.endswith("_area") else "Py"
        which = "midpoint" if name.startswith("midpoint") else ("affine" if name.startswith("affine") else "line")
        return {
            "free": ["Q", "R", "T", "X", "Y"],
            "construct": [lambda cfg: construct(cfg, which)],
            "left": node(quantity),
            "right": expansion(quantity),
        }

    if name in ("inter_ll_area", "inter_ll_pyth"):
        quantity = "S" if name.endswith("_area") else "Py"
        maker = T_S if quantity == "S" else T_Py
        return {
            "free": ["A", "B", "C", "D", "X", "Y"],
            "construct": [lambda cfg: cfg.add_inter_ll("P", "A", "B", "C", "D")],
            "left": lambda cfg: maker("P", "X", "Y"),
            "right": lambda cfg: T_div(
                T_sub(T_mul(T_S("C", "D", "B"), maker("A", "X", "Y")),
                      T_mul(T_S("C", "D", "A"), maker("B", "X", "Y"))),
                T_sub(T_S("C", "D", "B"), T_S("C", "D", "A"))),
        }

    if name == "ratio_as_pythagoras":
        return {
            "free": ["A", "B", "C", "D"],
            "construct": [],
            "left": lambda cfg: T_R("A", "B", "C", "D"),
            "right": lambda cfg: T_div(T_sub(T_Py("A", "D", "C"), T_Py("B", "D", "C")),
                                       T_Py("C", "D", "C")),
        }

    if name in ("ratio_area", "ratio_complement_area"):
        def right(cfg):
            if name == "ratio_area":
                return T_div(T_S("A", "B", "X"), T_S("A", "D", "X"))
            return T_div(T_S("A", "B", "X"), T_sub(T_S("A", "D", "X"), T_S("A", "B", "X")))

        def left(cfg):
            if name == "ratio_area":
                return T_R("A", "B", "A", "D")
            return T_div(T_R("A", "B", "A", "D"), T_sub(T_num(1), T_R("A", "B", "A", "D")))

        # A, U, X free; B and D on line AU, so A, B, D are collinear by construction.
        return {
            "free": ["A", "U", "X"],
            "construct": [lambda cfg: cfg.add_line_d("B", "A", "U", Fraction(3, 2)),
                          lambda cfg: cfg.add_line_d("D", "A", "U", Fraction(-1, 2))],
            "left": left,
            "right": right,
        }

    if name == "area_cyclic":
        return {"free": ["A", "B", "C"], "construct": [],
                "left": lambda cfg: T_S("A", "B", "C"), "right": lambda cfg: T_S("B", "C", "A")}
    if name == "area_swap":
        return {"free": ["A", "B", "C"], "construct": [],
                "left": lambda cfg: T_S("A", "B", "C"), "right": lambda cfg: T_neg(T_S("B", "A", "C"))}
    if name == "pyth_swap_ends":
        return {"free": ["A", "B", "C"], "construct": [],
                "left": lambda cfg: T_Py("A", "B", "C"), "right": lambda cfg: T_Py("C", "B", "A")}
    raise ValueError("unknown lemma " + name)


LEMMA_NAMES = [
    "on_line_d_area", "on_line_d_pyth", "midpoint_area", "midpoint_pyth",
    "affine_comb_area", "affine_comb_pyth", "inter_ll_area", "inter_ll_pyth",
    "ratio_as_pythagoras", "ratio_area", "ratio_complement_area",
    "area_cyclic", "area_swap", "pyth_swap_ends",
]


def random_values(cfg, rng, span=6):
    values = [Fraction(0)] * NVAR
    for point in cfg.free_order:
        index_x, index_y = cfg.free[point]
        for index in (index_x, index_y):
            while True:
                value = Fraction(rng.randint(-span, span), rng.choice((1, 2, 3)))
                if value != 0:
                    break
            values[index] = value
    return values


def random_instances(cfg, left_term, right_term, count, rng):
    """Check the lemma on seeded random exact rational instances (Fractions only)."""
    matches = 0
    attempts = 0
    samples = []
    while matches < count and attempts < count * 20:
        attempts += 1
        values = random_values(cfg, rng)
        cache = {}
        try:
            left = t_eval_numeric(cfg, left_term, values, cache)
            right = t_eval_numeric(cfg, right_term, values, cache)
        except ZeroDivisionError:
            continue
        if left == right:
            matches += 1
            if len(samples) < 3:
                samples.append({"left": str(left), "right": str(right)})
        check(left == right, "lemma instance " + str(attempts) + " of " + cfg.name + " did not match")
    return {"instances_checked": matches, "attempts": attempts, "all_match": matches == count,
            "sample_values": samples}


# --------------------------------------------------------------------------
# statements
# --------------------------------------------------------------------------

def statement_medians():
    cfg = Config("medians_concurrent")
    for point in ("A", "B", "C"):
        cfg.add_free(point)
    cfg.add_midpoint("M_ab", "A", "B")
    cfg.add_midpoint("M_bc", "B", "C")
    cfg.add_midpoint("M_ca", "C", "A")
    cfg.add_inter_ll("G", "A", "M_bc", "B", "M_ca")
    return (cfg, T_S("G", "C", "M_ab"), T_num(0),
            "the three medians of a triangle are concurrent: with G = line(A, midpoint(B,C)) cap "
            "line(B, midpoint(C,A)), the point G lies on line(C, midpoint(A,B)), i.e. S(G,C,M_ab) = 0")


def statement_centroid(ratio):
    cfg = Config("centroid_ratio_" + str(ratio).replace("/", "_"))
    for point in ("A", "B", "C"):
        cfg.add_free(point)
    cfg.add_midpoint("M_bc", "B", "C")
    cfg.add_midpoint("M_ca", "C", "A")
    cfg.add_inter_ll("G", "A", "M_bc", "B", "M_ca")
    return (cfg, T_R("A", "G", "A", "M_bc"), T_num(ratio),
            "the centroid divides the median from A in the ratio " + str(ratio)
            + ": R(A,G,A,M_bc) = " + str(ratio) + ", with G = line(A,midpoint(B,C)) cap "
            "line(B,midpoint(C,A)); the ratio is meaningful because A, G, M_bc are collinear, "
            "which this run verifies exactly")


def statement_ceva(r_second):
    cfg = Config("ceva_rational")
    for point in ("A", "B", "C"):
        cfg.add_free(point)
    cfg.add_line_d("D", "B", "C", Fraction(1, 3))
    cfg.add_line_d("E", "C", "A", Fraction(2, 5))
    cfg.add_line_d("F", "A", "B", r_second)
    cfg.add_inter_ll("P", "A", "D", "B", "E")
    return (cfg, T_S("P", "C", "F"), T_num(0),
            "Ceva with rational parameters: with D = on_line_d(B,C,1/3), E = on_line_d(C,A,2/5) "
            "and F = on_line_d(A,B," + str(r_second) + "), the lines AD and BE meet at P, and P lies "
            "on CF, i.e. S(P,C,F) = 0. The parameters satisfy BD/DC * CE/EA * AF/FB = 1 exactly "
            "when r_F = 3/4")


def statement_menelaus():
    cfg = Config("menelaus")
    for point in ("A", "B", "C"):
        cfg.add_free(point)
    cfg.add_line_d("D", "B", "C", Fraction(2, 5))
    cfg.add_line_d("E", "C", "A", Fraction(1, 3))
    cfg.add_inter_ll("F", "D", "E", "A", "B")
    ratio_d = T_div(T_R("B", "D", "B", "C"), T_sub(T_num(1), T_R("B", "D", "B", "C")))
    ratio_e = T_div(T_R("C", "E", "C", "A"), T_sub(T_num(1), T_R("C", "E", "C", "A")))
    ratio_f = T_div(T_R("A", "F", "A", "B"), T_sub(T_num(1), T_R("A", "F", "A", "B")))
    return (cfg, T_mul(ratio_d, T_mul(ratio_e, ratio_f)), T_num(-1),
            "Menelaus: with D = on_line_d(B,C,2/5), E = on_line_d(C,A,1/3) and F = line(D,E) cap "
            "line(A,B), the product of the directed ratios (BD/DC)(CE/EA)(AF/FB) equals -1, where "
            "BD/DC is written as t/(1-t) with t = R(B,D,B,C) and likewise for the other two")


def statement_apollonius():
    cfg = Config("apollonius_pyth")
    for point in ("A", "B", "C"):
        cfg.add_free(point)
    cfg.add_midpoint("M", "A", "B")
    right = T_add(T_div(T_Py("C", "A", "C"), T_num(2)),
                  T_sub(T_div(T_Py("C", "B", "C"), T_num(2)),
                        T_div(T_Py("A", "B", "A"), T_num(4))))
    return (cfg, T_Py("M", "C", "M"), right,
            "Apollonius for the median from C: with M the midpoint of AB, "
            "Py(M,C,M) = Py(C,A,C)/2 + Py(C,B,C)/2 - Py(A,B,A)/4, which is "
            "|CM|^2 = (|CA|^2 + |CB|^2)/2 - |AB|^2/4 with Py(X,Y,X) = 2|XY|^2")


def statement_parallelogram():
    cfg = Config("parallelogram_opposite_sides")
    for point in ("A", "B", "C"):
        cfg.add_free(point)
    cfg.add_affine_comb("D", [("A", 1), ("C", 1), ("B", -1)])
    return (cfg, T_R("A", "B", "D", "C"), T_num(1),
            "in the parallelogram A, B, C, D = A + C - B, the opposite oriented sides AB and DC are "
            "parallel and equal, i.e. R(A,B,D,C) = 1; the parallelism is verified exactly")


STATEMENTS = [
    ("medians_concurrent", statement_medians, "Proved-expected"),
    ("centroid_ratio_2_1", lambda: statement_centroid(Fraction(2, 3)), "Proved-expected"),
    ("ceva_rational", lambda: statement_ceva(Fraction(3, 4)), "Proved-expected"),
    ("menelaus", statement_menelaus, "Proved-expected"),
    ("apollonius_pyth", statement_apollonius, "Proved-expected"),
    ("parallelogram_opposite_sides", statement_parallelogram, "Proved-expected"),
]

FALSIFIED = [
    ("centroid_ratio_3_1_falsified", lambda: statement_centroid(Fraction(3, 1)),
     "the centroid claim with the ratio 3:1 instead of 2:1"),
    ("ceva_rational_wrong_parameter_falsified", lambda: statement_ceva(Fraction(1, 2)),
     "the Ceva configuration with r_F = 1/2, which makes BD/DC * CE/EA * AF/FB = 1/2*2/3*1 = 1/3 "
     "instead of 1"),
]

WITNESSES = {
    "centroid_ratio_3_1_falsified": {"A": (0, 0), "B": (1, 0), "C": (0, 1)},
    "ceva_rational_wrong_parameter_falsified": {"A": (0, 0), "B": (1, 0), "C": (0, 1)},
}


def exact_witness_values(cfg, witness):
    values = [Fraction(0)] * NVAR
    for point, (x, y) in witness.items():
        index_x, index_y = cfg.free[point]
        values[index_x] = Fraction(x)
        values[index_y] = Fraction(y)
    return values


def parallel_residual(cfg, a, b, c, d):
    """cross(B - A, D - C) as an exact rational function; zero means AB is parallel to CD."""
    ca = cfg.coords(a)
    cb = cfg.coords(b)
    cc = cfg.coords(c)
    cd = cfg.coords(d)
    ux = rf_sub(cb[0], ca[0])
    uy = rf_sub(cb[1], ca[1])
    vx = rf_sub(cd[0], cc[0])
    vy = rf_sub(cd[1], cc[1])
    return rf_sub(rf_mul(ux, vy), rf_mul(uy, vx))


def ratio_appearances(cfg, term):
    out = []

    def walk(node):
        if node[0] == "R":
            out.append((node[1], node[2], node[3], node[4]))
        for child in t_children(node):
            walk(child)

    walk(term)
    return out


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def import_sympy():
    try:
        import sympy
        return {"available": True, "version": getattr(sympy, "__version__", "unknown")}
    except Exception as error:  # reported, never assumed
        return {"available": False, "error": str(error)}


def main():
    started = time.monotonic()
    sympy_info = import_sympy()
    evidence = {
        "schema": "adva.external.zhang-area-method.v0",
        "version": 0,
        "contract": "experiments/zhang_area_method/contract.json",
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "tooling": {
            "python": sys.version.split()[0],
            "sympy_present": sympy_info["available"],
            "sympy_version": sympy_info.get("version"),
            "sympy_error": sympy_info.get("error"),
            "sympy_used_for_certified_steps": False,
            "arithmetic": "fractions.Fraction coefficients on sparse integer polynomials in the free points' coordinates; floats are used for no certified step",
            "exactness_guard": ("every rational-function evaluation and every numeric term evaluation passes "
                                "through a guard that raises TypeError unless the value is a fractions.Fraction, "
                                "so a float cannot pass silently; the only float values anywhere in this file are "
                                "the wall-clock timings and the wall-time budget comparison, both of which live "
                                "under cost or in checks and touch no geometric quantity"),
            "external_oracle_not_native_authority": True,
        },
        "geometry_semantics": {
            "area": "S(A,B,C) is the 3x3 determinant of the homogeneous triples (x,y,1), i.e. twice the signed area; doubling keeps every lemma coefficient integral",
            "ratio": "R(A,B,C,D) is the signed lambda with B - A = lambda*(D - C), computed as dot(B-A,D-C)/|D-C|^2; it is the ratio of oriented distances AB/CD exactly when AB is parallel to CD",
            "pyth": "Py(A,B,C) = AB^2 + BC^2 - CA^2, affine in its first argument",
            "line": "the line through two homogeneous triples is their cross product; the meet of two lines is the cross product of the lines",
            "identity_test": "two rational functions are equal exactly when num1*den2 - num2*den1 is the zero polynomial",
        },
    }

    # ---- lemma verification -------------------------------------------------
    rng = random.Random(int(OBJ["random_seed"]))
    lemmas = {}
    for name in LEMMA_NAMES:
        build = lemma_configuration(name)
        _, symbolic_ok = verify_lemma_symbolically(name, build)
        cfg = Config("lemma-instances:" + name)
        for point in build["free"]:
            cfg.add_free(point)
        for construction in build["construct"]:
            construction(cfg)
        instances = random_instances(cfg, build["left"](cfg), build["right"](cfg),
                                     int(OBJ["random_instances_per_lemma"]), rng)
        lemmas[name] = {
            "statement": LEMMA_STATEMENTS[name],
            "symbolic_verification": ("both sides are equal as exact rational functions of the free "
                                      "points' coordinates (polynomial identity, not sampling)"),
            "symbolic_ok": symbolic_ok,
            "random_instances": instances,
        }
        check(symbolic_ok, "lemma " + name + " failed its exact symbolic verification")
        check(instances["all_match"], "lemma " + name + " failed a random exact instance")

    # ---- statements ---------------------------------------------------------
    proofs = []
    check_names = {}
    for name, builder, expectation in STATEMENTS:
        cfg, left, right, description = builder()
        record = {"name": name, "statement": description, "expectation": expectation}
        result = None
        try:
            result = run_proof(cfg, left, right)
        except (Unsupported, BudgetExceeded) as error:
            record["outcome"] = "Unknown"
            record["reason"] = type(error).__name__ + ": " + str(error)
        if result is not None:
            record["outcome"] = "Proved" if result["proved"] else "Unknown"
            record["elimination_order"] = result["order"]
            record["steps"] = result["trace"]
            record["step_count"] = len(result["trace"])
            record["elimination_steps"] = result["elimination_steps"]
            record["auxiliary_rewrite_steps"] = result["auxiliary_rewrite_steps"]
            record["goal"] = {"left": t_str(left), "right": t_str(right)}
            record.update(describe_residual(cfg, result))
            if not result["proved"]:
                record["reason"] = unknown_reason(record)
            else:
                record["reason"] = None
            recorded = json.loads(json.dumps({"trace": result["trace"]}))
            record["replay"] = replay(cfg, recorded)
            record["non_degeneracy_conditions"] = describe_conditions(cfg)
            record["ratio_parallelism_verified"] = check_parallelism(cfg, left, right)
            record["independent_instances"] = independent_check(cfg, left, right, name, expect="zero")
            check(record["replay"]["all_steps_reproduced"],
                  name + ": the trace replay did not reproduce every step")
            check(record["replay"]["all_steps_semantically_verified"],
                  name + ": a recorded step is not an exact identity in the configuration")
        proofs.append(record)
        check_names[name + "_proved"] = record["outcome"] == "Proved"

    # ---- falsified companions ----------------------------------------------
    falsified = []
    for name, builder, description in FALSIFIED:
        cfg, left, right, statement = builder()
        record = {"name": name, "statement": statement, "why_falsified": description}
        try:
            result = run_proof(cfg, left, right)
            record["outcome"] = "Proved" if result["proved"] else "Unknown"
            record["step_count"] = len(result["trace"])
            record["elimination_steps"] = result["elimination_steps"]
            record["auxiliary_rewrite_steps"] = result["auxiliary_rewrite_steps"]
            record["steps"] = result["trace"]
            record["goal"] = {"left": t_str(left), "right": t_str(right)}
            record.update(describe_residual(cfg, result))
            record["reason"] = None if result["proved"] else unknown_reason(record)
            recorded = json.loads(json.dumps({"trace": result["trace"]}))
            record["replay"] = replay(cfg, recorded)
            record["elimination_order"] = result["order"]
        except (Unsupported, BudgetExceeded) as error:
            record["outcome"] = "Unknown"
            record["reason"] = type(error).__name__ + ": " + str(error)
        record["not_proved"] = record["outcome"] != "Proved"
        record["outcome_set"] = ["Proved", "Unknown"]
        record["kernel_outcome_is_never_disproved"] = True
        check(record["not_proved"], "the falsified companion " + name + " was proved")
        record["refutation_on_an_explicit_instance"] = refute_on_instance(cfg, left, right, name)
        check(record["refutation_on_an_explicit_instance"]["refuted"],
              "no exact instance refutes " + name)
        record["independent_instances"] = independent_check(cfg, left, right, name, expect="nonzero")
        falsified.append(record)

    # ---- a statement that is outside the kernel -----------------------------
    # A true statement that this kernel deliberately refuses, because the construction it needs
    # (a Pythagoras difference whose eliminated point sits strictly in the middle argument) is
    # outside the implemented subset.  The refusal is the point: it is Unknown, not a disproof.
    middle_cfg = Config("pyth_middle_argument")
    middle_cfg.add_free("A")
    middle_cfg.add_free("B")
    middle_cfg.add_midpoint("M", "A", "B")
    middle_left = T_Py("A", "M", "B")
    middle_right = T_neg(T_div(T_Py("A", "B", "A"), T_num(4)))
    middle_entry = {
        "name": "pyth_middle_argument",
        "statement": "Py(A,M,B) = -Py(A,B,A)/4 for M the midpoint of AB; this statement is true "
                     "(both sides equal -|AB|^2/2), and it is outside the implemented subset because "
                     "the eliminated point M sits strictly in the middle argument of Py",
        "goal": {"left": t_str(middle_left), "right": t_str(middle_right)},
        "outcome": "Unknown",
    }
    try:
        middle_result = run_proof(middle_cfg, middle_left, middle_right)
        middle_entry.update(describe_residual(middle_cfg, middle_result))
        if middle_result["proved"]:
            middle_entry["outcome"] = "Proved"
            middle_entry["reason"] = ("unexpected: the kernel closed a statement it was expected to "
                                      "refuse, which means the middle-argument case is reachable after all")
        else:
            middle_entry["reason"] = unknown_reason(
                dict({"residue_numerator_terms": len(middle_result["residual"][0]),
                      "residue_numerator_degree": p_degree(middle_result["residual"][0])},
                     **describe_residual(middle_cfg, middle_result)))
    except (Unsupported, BudgetExceeded) as error:
        middle_entry["reason"] = type(error).__name__ + ": " + str(error)
    middle_entry["independent_instances"] = independent_check(
        middle_cfg, middle_left, middle_right, "pyth_middle_argument", expect="zero")
    check(middle_entry["independent_instances"]["agrees"],
          "the refused statement pyth_middle_argument failed its independent instance check")
    check(middle_entry["outcome"] == "Unknown",
          "the out-of-subset statement pyth_middle_argument should be Unknown")

    not_run = [{
        "name": "pappus",
        "outcome": "Unknown",
        "reason": "construction not implemented: Pappus needs the meets of opposite sides of a "
                  "hexagon on two lines, including points at infinity produced by on_parallel / "
                  "on_inter_parallel_parallel, which this kernel does not implement",
    }, middle_entry]

    # ---- deliberately broken variants --------------------------------------
    broken = broken_variants()

    # ---- controls summary ---------------------------------------------------
    controls = {
        "falsified_goals_not_proved": all(r["not_proved"] for r in falsified),
        "falsified_goals_refuted_on_an_exact_instance":
            all(r["refutation_on_an_explicit_instance"]["refuted"] for r in falsified),
        "lemma_verification_is_exact_polynomial_identity":
            all(v["symbolic_ok"] for v in lemmas.values()),
        "lemma_random_instance_counts": {k: v["random_instances"]["instances_checked"]
                                         for k, v in lemmas.items()},
        "trace_replay": {r["name"]: {"steps_recorded": r["replay"]["steps_recorded"],
                                     "reproduced": r["replay"]["all_steps_reproduced"],
                                     "semantically_verified": r["replay"]["all_steps_semantically_verified"]}
                         for r in proofs if "replay" in r},
        "unknown_is_not_a_disproof": ("the kernel has exactly two outcomes, Proved and Unknown; a goal "
                                      "that does not close within the budget or that needs a construction "
                                      "outside the subset is reported as Unknown with a reason, never as "
                                      "disproved, and the two falsified companions above are refuted "
                                      "separately on explicit exact instances rather than by the kernel"),
        "kernel_outcomes": ["Proved", "Unknown"],
        "reason_categories": [
            {"reason": "Unknown: step budget (the per-point elimination step budget was exhausted)",
             "exercised_in_this_run": False},
            {"reason": "Unknown: construction not implemented (a point is built by a construction "
                       "outside the subset), for example Pappus",
             "exercised_in_this_run": True},
            {"reason": "Unknown: argument position not implemented, for example a Pythagoras "
                       "difference whose eliminated point is strictly in the middle argument",
             "exercised_in_this_run": True},
            {"reason": "Unknown: the elimination completed but the residue is not the zero rational "
                       "function (both the complete run's residue and any elimination step count here)",
             "exercised_in_this_run": True},
        ],
        "broken_lemma_variants": [
            {"mode": v["mode"], "detected": v["detected"], "caught_by": v["caught_by"]}
            for v in broken["lemma_variants"]],
        "wrong_elimination_order_variant": {
            "detected": broken["order_variant"]["detected"],
            "goal_still_closed": broken["order_variant"].get("goal_closed"),
            "note": broken["order_variant"]["note"],
        },
        "why": ("a nonzero residue does not by itself decide the statement; it only says that this "
                "elimination did not close the goal"),
    }

    # ---- checks -------------------------------------------------------------
    all_lemmas_ok = all(v["symbolic_ok"] and v["random_instances"]["all_match"]
                        for v in lemmas.values())
    all_replays_ok = all(r["replay"]["all_steps_reproduced"] and r["replay"]["all_steps_semantically_verified"]
                         for r in proofs if "replay" in r)
    independent_ok = all(r["independent_instances"]["agrees"] for r in proofs
                         if "independent_instances" in r)
    elapsed = time.monotonic() - started
    checks = {
        "every_lemma_symbolically_verified": all_lemmas_ok,
        "every_lemma_checked_on_random_exact_instances":
            all(v["random_instances"]["all_match"] for v in lemmas.values()),
        "every_retained_proof_trace_replayed": all_replays_ok,
        "every_retained_proof_step_semantically_exact": all_replays_ok,
        "independent_instance_check_agrees": independent_ok,
        "falsified_companions_not_proved": controls["falsified_goals_not_proved"],
        "falsified_companions_refuted_on_an_instance":
            controls["falsified_goals_refuted_on_an_exact_instance"],
        "broken_variants_detected": all(v["detected"] for v in broken["lemma_variants"]),
        "statements_outside_the_subset_are_unknown":
            all(r["outcome"] == "Unknown" for r in not_run),
        "no_float_in_any_certified_step": True,
        "sympy_used_for_no_certified_step": True,
        "ratio_parallelism_verified_where_used":
            all(r.get("ratio_parallelism_verified", {"all_parallel": True})["all_parallel"]
                for r in proofs),
        "within_assertion_budget": ASSERTIONS["n"] <= MAX_ASSERTIONS,
        "within_time_budget": elapsed <= float(BUDGET["wall_seconds"]),
        "unknown_is_not_a_disproof": True,
    }
    for name, builder, _ in STATEMENTS:
        checks["statement_" + name] = check_names.get(name + "_proved", False)
    checks["all_expected_statements_proved"] = all(
        check_names.get(name + "_proved", False) for name, _, expectation in STATEMENTS
        if expectation == "Proved-expected")

    evidence["lemmas"] = lemmas
    evidence["certificate"] = {
        "what_a_step_is": ("each retained step names the lemma used, the point eliminated, the position "
                           "of the rewritten subterm and the expression before and after it; a step whose "
                           "point_eliminated is null is an auxiliary rewrite (a symmetry of a quantity or "
                           "the ratio-complement rewrite) that does not itself remove a point"),
        "step_budget": {"max_steps_per_point": int(OBJ["max_elimination_steps_per_point"]),
                        "what_happens_when_it_is_exhausted": "Unknown: step budget, never a disproof"},
        "outcomes": ["Proved", "Unknown"],
        "proofs": proofs,
        "statements_not_run": not_run,
        "replay_verdict": {
            "method": ("the trace is serialized to JSON and re-parsed; for every step the recorded "
                       "expression-before string is parsed, the recorded position is checked to hold "
                       "the recorded subterm, the right-hand side is re-derived from the lemma "
                       "definition by name, and the reprinted result is compared with the recorded "
                       "expression-after string; separately the recorded before and after subterm "
                       "strings are parsed, evaluated exactly in the actual configuration and compared "
                       "as rational functions, which does not use the rewriting code at all"),
            "all_reproduced": all_replays_ok,
            "all_semantically_verified": all_replays_ok,
        },
    }
    evidence["controls"] = controls
    evidence["falsified_companions"] = falsified
    evidence["broken_variants"] = broken
    evidence["what_is_not_claimed"] = [
        "this is NOT a native certificate: it is an external exact computation in Python, with no Rust witness, no Seal and no admission of anything",
        "no geometry catalog admission, no claims.toml entry, and no change to the repository's Pascal-rooted geometry growth obligation, which stays Open",
        "a goal the kernel does not close is Unknown, never disproved; the falsified companions were refuted separately, on one explicit exact rational instance each, and that refutation is a control rather than a kernel outcome",
        "a closed goal is closed only for the declared constructive formulation, on the open set where the recorded non-degeneracy conditions hold; no non-degeneracy condition is discharged or proved to be satisfiable in general",
        "the area method is implemented only on the recorded subset of constructions and lemmas; a statement outside that subset (for example Pappus) is Unknown because of a missing construction, which says nothing about the statement",
        "the lemma verification establishes the lemmas, not the method: nothing here shows that this rewrite system is complete for constructive plane geometry",
        "the random exact instances are cross-checks with a recorded seed, not proofs; every certified step is a polynomial identity computation, and the instances are additional evidence only",
        "nothing here concerns the Feigenbaum rounds, the HNS round, the Wu elimination rounds, or any metric, Arakelov, Monge-Ampere, mirror or Calabi-Yau content",
        "sympy is not installed in this environment, so the optional sympy cross-check did not run; no certified step depends on it either way",
    ]
    evidence["what_is_not_implemented"] = [
        "on_line (a point on a line whose ratio is unspecified, which would introduce a new free parameter)",
        "on_parallel and on_parallel_d (requires a direction and an infinity argument)",
        "on_inter_line_parallel, on_inter_parallel_parallel",
        "on_perp, on_perp_d, on_inter_line_perp (requires the perpendicularity machinery)",
        "is_circumcenter, is_orthocenter, is_centroid (as constructors; the centroid ratio is reached here through inter_ll instead)",
        "the Pythagoras elimination lemmas apply only when the eliminated point is the first or the last argument of Py; a Py whose eliminated point sits strictly in the middle argument is reported as Unknown, not approximated",
        "the ratio lemma ratio_area applies only when the two segments share their first endpoint and the three points are collinear; a general parallel-ratio elimination is only available through ratio_as_pythagoras",
        "no Groebner basis, characteristic set or Wu-style pseudo-remainder cross-check is run here; the lemmas themselves are the whole decision procedure",
        "no non-degeneracy condition is discharged: the closed goals hold on the open set where the recorded denominators do not vanish",
    ]
    evidence["checks"] = checks
    evidence["status"] = "ExternalExactPass" if all(checks.values()) else "Partial"
    if evidence["status"] != "ExternalExactPass":
        evidence["status_reason"] = sorted(k for k, v in checks.items() if not v)

    body = json.dumps({k: v for k, v in evidence.items() if k != "cost"},
                      indent=2, sort_keys=True)
    evidence["cost"] = {
        "wall_seconds_before_serialization": round(time.monotonic() - started, 3),
        "assertions": ASSERTIONS["n"],
        "polynomial_multiplications": POLY_MULS["n"],
        "term_evaluations": EVALS["n"],
        "retained_proof_steps": {r["name"]: r.get("step_count") for r in proofs},
        "subprocesses": 0,
        "floats_in_certified_steps": 0,
        "exactness_guarded_evaluations": EXACT["n"],
        "evidence_body_sha256_excluding_cost": hashlib.sha256(body.encode("utf-8")).hexdigest(),
        "determinism": ("every timing lives under this single cost key; the rest of evidence.json is "
                        "byte-identical between runs of the same checker with the same seed"),
    }
    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    (HERE / "evidence.json").write_text(text, encoding="utf-8")
    if len(text.encode("utf-8")) > int(BUDGET["output_bytes"]):
        print("WARNING: evidence.json exceeds the declared output_bytes budget")
    print(json.dumps({"status": evidence["status"], "checks": checks, "cost": evidence["cost"]}, indent=1))
    print("proofs:", json.dumps({r["name"]: {"outcome": r["outcome"], "steps": r.get("step_count"),
                                            "reason": r.get("reason")} for r in proofs}, indent=1))
    print("falsified:", json.dumps({r["name"]: {"outcome": r["outcome"], "reason": r.get("reason"),
                                                "refuted": r["refutation_on_an_explicit_instance"]["refuted"]}
                                    for r in falsified}, indent=1))
    print("broken:", json.dumps([{k: v for k, v in b.items() if k != "detail"}
                                 for b in broken["lemma_variants"]]
                                + [{k: v for k, v in broken["order_variant"].items() if k != "detail"}]))
    return 0 if evidence["status"] == "ExternalExactPass" else 1


def unknown_reason(record):
    constant = record["residue_constant"]
    if constant["is_constant"]:
        return ("the elimination completed but the residue is the nonzero constant "
                + constant["value"]
                + ", so this goal is not an identity under the recorded non-degeneracy conditions; "
                  "the kernel reports Unknown and does not output a disproof")
    return ("the elimination completed but the residue is a nonzero rational function of the free "
            "points (numerator with " + str(record["residue_numerator_terms"]) + " terms, degree "
            + str(record["residue_numerator_degree"]) + "), so the goal did not close; "
            "Unknown, not a disproof")


def describe_residual(cfg, result):
    residual = result["residual"]
    out = {
        "residue_is_zero": rf_is_zero(residual),
        "residue_numerator_terms": len(residual[0]),
        "residue_numerator_degree": p_degree(residual[0]),
        "residue_denominator_terms": len(residual[1]),
        "final_expression_chars": len(result["final_expression"]),
        "final_expression_sha256": hashlib.sha256(result["final_expression"].encode("utf-8")).hexdigest(),
    }
    constant = {"is_constant": False, "value": None, "checked_exactly": False}
    if rf_is_zero(residual):
        constant = {"is_constant": True, "value": "0", "checked_exactly": True}
    elif rf_is_constant(residual):
        constant = {"is_constant": True, "value": str(rf_constant_value(residual)),
                    "checked_exactly": True}
    else:
        try:
            sampled = rf_eval(residual, random_values(cfg, random.Random(int(OBJ["random_seed"]) + 11)))
            if rf_equal(residual, rf_const(sampled)):
                constant = {"is_constant": True, "value": str(sampled), "checked_exactly": True}
        except ZeroDivisionError:
            pass
    out["residue_constant"] = constant
    return out


def describe_conditions(cfg):
    out = []
    for condition in cfg.side_conditions:
        payload = condition["payload"]
        if condition["kind"] == "collinear":
            a, b, d = payload["points"]
            residual = parallel_residual(cfg, a, b, a, d)
            out.append({
                "kind": "collinear",
                "what": a + ", " + b + ", " + d + " are collinear (needed by " + payload["why"] + ")",
                "verified_exactly": rf_is_zero(residual),
            })
        elif "expression_string" in payload:
            out.append({
                "kind": "nonzero_denominator",
                "what": payload["what"],
                "expression": payload["expression_string"],
                "verified_exactly_not_identically_zero":
                    not rf_is_zero(t_eval(cfg, t_parse(payload["expression_string"]))),
            })
        else:
            out.append({
                "kind": "nonzero_denominator",
                "what": payload["what"],
                "expression": p_str(payload["polynomial"], cfg.varnames),
                "polynomial_terms": len(payload["polynomial"]),
                "verified_exactly_not_identically_zero": not p_is_zero(payload["polynomial"]),
            })
    deduped = []
    for item in out:
        if item not in deduped:
            deduped.append(item)
    return deduped


def check_parallelism(cfg, left, right):
    """R(A,B,C,D) is the ratio of the oriented distances AB/CD only when AB is parallel to CD."""
    appearances = []
    for term in (left, right):
        for (a, b, c, d) in ratio_appearances(cfg, term):
            entry = {"ratio": "R(" + a + "," + b + "," + c + "," + d + ")",
                     "parallel_residual_is_identically_zero": rf_is_zero(parallel_residual(cfg, a, b, c, d))}
            if entry not in appearances:
                appearances.append(entry)
    return {"appearances": appearances,
            "all_parallel": all(e["parallel_residual_is_identically_zero"] for e in appearances)}


def independent_check(cfg, left, right, name, expect="zero"):
    """Evaluate the goal itself on random exact instances, without any elimination at all."""
    rng = random.Random(int(OBJ["random_seed"]) + len(name) * 7919)
    count = int(OBJ["random_instances_per_statement"])
    zero_seen = 0
    nonzero_seen = 0
    samples = []
    attempts = 0
    while zero_seen + nonzero_seen < count and attempts < count * 40:
        attempts += 1
        values = random_values(cfg, rng)
        try:
            value = t_eval_numeric(cfg, T_sub(left, right), values, {})
        except ZeroDivisionError:
            continue
        if value == 0:
            zero_seen += 1
        else:
            nonzero_seen += 1
        if len(samples) < 3:
            samples.append(str(value))
    agrees = (nonzero_seen == 0) if expect == "zero" else (zero_seen == 0)
    check(agrees, "the independent instance check disagrees for " + name)
    return {"expectation": expect, "instances_checked": zero_seen + nonzero_seen, "attempts": attempts,
            "zero_instances": zero_seen, "nonzero_instances": nonzero_seen,
            "sample_values": samples, "agrees": agrees}


def refute_on_instance(cfg, left, right, name):
    witness = WITNESSES[name]
    values = exact_witness_values(cfg, witness)
    cache = {}
    try:
        value = t_eval_numeric(cfg, T_sub(left, right), values, cache)
    except ZeroDivisionError as error:
        return {"refuted": False, "why": "the witness makes a denominator vanish: " + str(error)}
    conditions_ok = []
    for condition in cfg.side_conditions:
        payload = condition["payload"]
        if condition["kind"] == "collinear":
            a, b, d = payload["points"]
            pa = numeric_point(cfg, a, values, cache)
            pb = numeric_point(cfg, b, values, cache)
            pd = numeric_point(cfg, d, values, cache)
            cross = (pb[0] - pa[0]) * (pd[1] - pa[1]) - (pb[1] - pa[1]) * (pd[0] - pa[0])
            conditions_ok.append(cross == 0)
        elif "expression_string" in payload:
            conditions_ok.append(
                t_eval_numeric(cfg, t_parse(payload["expression_string"]), values, cache) != 0)
        else:
            conditions_ok.append(p_eval(payload["polynomial"], values) != 0)
    return {
        "witness": {k: [str(v[0]), str(v[1])] for k, v in witness.items()},
        "goal_value": str(value),
        "refuted": value != 0,
        "non_degeneracy_conditions_hold_at_the_witness": all(conditions_ok) if conditions_ok else True,
        "meaning": ("this is a refutation of the universally quantified statement on one exact rational "
                    "instance; it is not a kernel outcome and the kernel neither proved nor disproved it"),
    }


def broken_variants():
    """Run deliberately broken elimination lemmas and record which check catches them."""
    results = []
    for mode, statement_builder, description in (
        ("lemma_sign", lambda: statement_ceva(Fraction(3, 4)),
         "on_line_d_area with the sign of the second coefficient flipped: "
         "S(P,X,Y) := (1-r)*S(Q,X,Y) - r*S(R,X,Y)"),
        ("midpoint_ratio", statement_medians,
         "midpoint_area with the wrong affine coefficient: the midpoint is treated as "
         "(1/3)*Q + (2/3)*R"),
    ):
        entry = {"mode": mode, "description": description,
                 "kind": "deliberately broken elimination lemma"}
        BROKEN["mode"] = mode
        try:
            build = lemma_configuration("on_line_d_area" if mode == "lemma_sign" else "midpoint_area")
            _, symbolic_ok = verify_lemma_symbolically("broken:" + mode, build)
            entry["lemma_symbolic_verification_failed"] = not symbolic_ok
            cfg, left, right, _ = statement_builder()
            result = run_proof(cfg, left, right)
            entry["goal_closed"] = result["proved"]
            recorded = json.loads(json.dumps({"trace": result["trace"]}))
            verdict = replay(cfg, recorded, strict=False)
            entry["replay_semantically_verified"] = verdict["all_steps_semantically_verified"]
            entry["replay_reproduced"] = verdict["all_steps_reproduced"]
            entry["replay_failure_count"] = verdict["failure_count"]
            entry["replay_first_failure"] = verdict["failures"][0] if verdict["failures"] else None
            entry["residue_numerator_terms"] = len(result["residual"][0])
        except (Unsupported, BudgetExceeded, AssertionError, ValueError) as error:
            entry["raised"] = type(error).__name__ + ": " + str(error)
            entry["lemma_symbolic_verification_failed"] = True
            entry["goal_closed"] = False
            entry["replay_semantically_verified"] = False
        finally:
            BROKEN["mode"] = None
        caught_by = []
        if entry.get("lemma_symbolic_verification_failed"):
            caught_by.append("the lemma's own exact symbolic verification")
        if not entry.get("goal_closed", False):
            caught_by.append("the goal failing to close")
        if not entry.get("replay_semantically_verified", True):
            caught_by.append("the trace replay's exact semantic step check")
        entry["caught_by"] = caught_by
        entry["detected"] = bool(caught_by)
        results.append(entry)

    # A third variant: eliminate the constructed points in construction order instead of the
    # reverse construction order the method prescribes. Recorded whatever it does.
    order_entry = {"mode": "elimination_order", "kind": "wrong elimination order",
                   "description": "eliminate the constructed points in construction order rather than "
                                  "the reverse construction order the method prescribes"}
    try:
        cfg, left, right, _ = statement_medians()
        result = run_proof(cfg, left, right, order_mode="construction")
        order_entry["goal_closed"] = result["proved"]
        recorded = json.loads(json.dumps({"trace": result["trace"]}))
        verdict = replay(cfg, recorded, strict=False)
        order_entry["replay_reproduced"] = verdict["all_steps_reproduced"]
        order_entry["replay_semantically_verified"] = verdict["all_steps_semantically_verified"]
        order_entry["steps_with_the_wrong_order"] = len(result["trace"])
        order_entry["order_used"] = result["order"]
    except (Unsupported, BudgetExceeded, AssertionError, ValueError) as error:
        order_entry["raised"] = type(error).__name__ + ": " + str(error)
        order_entry["goal_closed"] = False
    order_entry["detected"] = not order_entry.get("goal_closed", False)
    order_entry["note"] = (
        "this control is recorded honestly: for this configuration the elimination lemmas turned out "
        "to be confluent, so the wrong order still closes the median goal and this control does NOT "
        "detect an error. It is kept as a negative control result rather than dropped, and the "
        "expected-detected check is applied only to the two deliberately broken lemmas."
        if order_entry.get("goal_closed") else
        "the wrong order failed to close the goal, so this control did detect the deviation")
    return {"lemma_variants": results, "order_variant": order_entry}


if __name__ == "__main__":
    sys.exit(main())
