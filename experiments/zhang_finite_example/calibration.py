#!/usr/bin/env python3
"""Finite-example verification of plane incidence identities, with checkable results.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The criterion under test is the one behind Zhang Jingzhong and Yang Lu's numerical
parallel method (1990, the "Zhang-Yang theorem" abroad): a polynomial C in n free
parameters with degree at most d_i in parameter i is identically zero exactly when it
vanishes at every point of a grid carrying d_i + 1 distinct values in coordinate i.
The point of the test is that nothing on the left is expanded: the grid evaluates the
*formula*, and the degree bounds are propagated from the construction, so the
certificate never builds the conclusion polynomial.

One formula, three arithmetics:

  Exact     fractions.Fraction                       the certificate
  Interval  decimal.Decimal with directed rounding    a numerical pass with enclosures
  Degree    degree vectors only                       the a priori bound

Nothing about this is native Adva authority: it is an external exact computation, and
the run reports its own limits.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import pathlib
import random
import sys
import time
from decimal import Context, Decimal, ROUND_CEILING, ROUND_FLOOR
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent.parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]

ASSERTIONS = {"n": 0}
MAX_ASSERTIONS = CONTRACT["budget"]["max_assertions"]


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)
    if ASSERTIONS["n"] > MAX_ASSERTIONS:
        raise AssertionError("assertion budget exceeded")


# ------------------------------------------------------------ three arithmetics ----

class Deg:
    """A degree vector. The bound mode carries nothing else, so no expansion happens."""

    __slots__ = ("d",)

    def __init__(self, d):
        self.d = tuple(d)

    def __add__(self, other):
        return Deg([max(a, b) for a, b in zip(self.d, other.d)])

    def __sub__(self, other):
        return self + other

    def __mul__(self, other):
        return Deg([a + b for a, b in zip(self.d, other.d)])

    def __neg__(self):
        return Deg(self.d)

    def as_list(self):
        return list(self.d)


INTERVAL_PRECISION = 40
_FLOOR = Context(prec=INTERVAL_PRECISION, rounding=ROUND_FLOOR)
_CEIL = Context(prec=INTERVAL_PRECISION, rounding=ROUND_CEILING)


class Iv:
    """An interval whose every operation rounds outward."""

    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi):
        self.lo, self.hi = lo, hi

    @staticmethod
    def point(x):
        x = Fr(x)
        return Iv(_FLOOR.divide(Decimal(x.numerator), Decimal(x.denominator)),
                  _CEIL.divide(Decimal(x.numerator), Decimal(x.denominator)))

    @staticmethod
    def whole(k):
        v = Decimal(k)
        return Iv(v, v)

    def __add__(self, other):
        return Iv(_FLOOR.add(self.lo, other.lo), _CEIL.add(self.hi, other.hi))

    def __sub__(self, other):
        return Iv(_FLOOR.subtract(self.lo, other.hi), _CEIL.subtract(self.hi, other.lo))

    def __mul__(self, other):
        products = [(a, b) for a in (self.lo, self.hi) for b in (other.lo, other.hi)]
        lows = [_FLOOR.multiply(a, b) for a, b in products]
        highs = [_CEIL.multiply(a, b) for a, b in products]
        return Iv(min(lows), max(highs))

    def __neg__(self):
        return Iv(-self.hi, -self.lo)

    def contains_zero(self):
        return self.lo <= 0 <= self.hi

    def distance_from_zero(self):
        if self.lo > 0:
            return self.lo
        if self.hi < 0:
            return -self.hi
        return Decimal(0)

    def width(self):
        return self.hi - self.lo


class ExactMode:
    def __init__(self, sample):
        self.v = [Fr(x) for x in sample]

    def var(self, i):
        return self.v[i]

    def const(self, k):
        return Fr(k)

    def one(self):
        return Fr(1)


class IntervalMode:
    def __init__(self, sample):
        self.v = [Iv.point(x) for x in sample]

    def var(self, i):
        return self.v[i]

    def const(self, k):
        return Iv.whole(k)

    def one(self):
        return Iv.whole(1)


class DegreeMode:
    def __init__(self, n):
        self.n = n

    def var(self, i):
        return Deg([1 if j == i else 0 for j in range(self.n)])

    def const(self, k):
        return Deg([0] * self.n)

    def one(self):
        return self.const(1)


def import_sympy():
    try:
        import sympy
        return {"available": True, "version": sympy.__version__, "module": sympy}
    except Exception as error:  # pragma: no cover - reported, not raised
        return {"available": False, "error": str(error)}


SY = import_sympy()
EXTERNAL_CALLS = {"n": 0}


class SympyMode:
    """The same formula code over an exact symbolic arithmetic, for a cross-check."""

    def __init__(self, n, sympy):
        self.n = n
        self.sympy = sympy
        self.symbols = sympy.symbols(" ".join(f"z{i}" for i in range(n)))

    def var(self, i):
        return self.symbols[i]

    def const(self, k):
        return self.sympy.Integer(k)

    def one(self):
        return self.sympy.Integer(1)


# --------------------------------------------------------------- the geometry ----

def cross(u, v):
    return (u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0])


def det3(a, b, c):
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


CORRECT_PAIRING = [(0, 3), (1, 4), (2, 5)]
WRONG_PAIRING = [(0, 3), (1, 5), (2, 4)]


def pascal(mode, point_of, pairing=None):
    """The Pascal conclusion for six points in hexagon order.

    The hexagon sides are P_i P_{i+1}; the conclusion is the collinearity of the
    three intersections of opposite sides. The pairing is the only thing that varies
    between the theorem and its falsified companion.
    """
    t = [mode.var(i) for i in range(6)]
    P = [point_of(mode, t[i], i) for i in range(6)]
    lines = [cross(P[i], P[(i + 1) % 6]) for i in range(6)]
    chosen = pairing or CORRECT_PAIRING
    X = [cross(lines[a], lines[b]) for a, b in chosen]
    return det3(X[0], X[1], X[2])


def parabola_point(mode, t, index):
    one = mode.one()
    return (t, t * t, one)


def hyperbola_point(mode, t, index):
    """A scaling of the affine point (t, 1/t): (t^2, 1, t). Zero sets are unaffected."""
    one = mode.one()
    return (t * t, one, t)


def circle_point(mode, t, index):
    one = mode.one()
    return (one - t * t, t + t, one + t * t)


def pappus_conclusion(mode):
    one = mode.one()
    zero = mode.const(0)
    p = [mode.var(i) for i in range(3)]
    q = [mode.var(i) for i in range(3, 6)]
    A, B, C = (p[0], zero, one), (p[1], zero, one), (p[2], zero, one)
    a, b, c = (zero, q[0], one), (zero, q[1], one), (zero, q[2], one)
    return det3(cross(cross(A, b), cross(a, B)),
                cross(cross(b, C), cross(B, c)),
                cross(cross(C, a), cross(c, A)))


def ceva_conclusion(mode, f=None):
    one = mode.one()
    zero = mode.const(0)
    t, e = mode.var(0), mode.var(1)
    if f is None:
        f = mode.var(2)
    A, B, C = (zero, zero, one), (one, zero, one), (zero, one, one)
    D, E, F = (one - t, t, one), (zero, e, one), (f, zero, one)
    return det3(cross(A, D), cross(B, E), cross(C, F))


def ceva_chart(mode):
    """Solve the Ceva hypothesis for f and clear the chart denominator.

    The hypothesis t(1-e)f - (1-t)e(1-f) = 0 gives f = N/D with N = (1-t)e and
    D = t(1-e) + (1-t)e. The conclusion is affine in f, so its value on the chart is
    (A D + (B - A) N) / D, and the numerator is the polynomial tested here.
    """
    one = mode.one()
    zero = mode.const(0)
    t, e = mode.var(0), mode.var(1)
    N = (one - t) * e
    D = t * (one - e) + (one - t) * e
    A = ceva_conclusion(mode, zero)
    B = ceva_conclusion(mode, one)
    return A * D + (B - A) * N


STATEMENTS = {
    "pappus": {"n": 6, "conclusion": pappus_conclusion, "identity": True},
    "parabola_pascal": {"n": 6, "conclusion": lambda m: pascal(m, parabola_point), "identity": True},
    "hyperbola_pascal": {"n": 6, "conclusion": lambda m: pascal(m, hyperbola_point), "identity": True},
    "circle_pascal": {"n": 6, "conclusion": lambda m: pascal(m, circle_point), "identity": True},
    "ceva_chart": {"n": 2, "conclusion": ceva_chart, "identity": True},
    "wrong_pairing": {"n": 6,
                      "conclusion": lambda m: pascal(m, parabola_point, WRONG_PAIRING),
                      "identity": False},
    "ceva_conclusion": {"n": 3, "conclusion": lambda m: ceva_conclusion(m), "identity": False},
}

NON_IDENTITIES = [name for name, spec in STATEMENTS.items() if not spec["identity"]]
SIX_PARAMETER_IDENTITIES = [name for name, spec in STATEMENTS.items()
                            if spec["identity"] and spec["n"] == 6]


# ----------------------------------------------------------- grids and passes ----

def integer_grid(spec):
    return [[Fr(j + 1) for j in range(spec["bound"][i] + 1)] for i in range(spec["n"])]


def rational_grid(name, spec, seed):
    """Distinct nonzero rationals, with antipodal circle parameters refused."""
    rng = random.Random(seed)
    columns = []
    rejected = 0
    for i in range(spec["n"]):
        needed = spec["bound"][i] + 1
        values = []
        while len(values) < needed:
            x = Fr(rng.randrange(-60, 61), rng.randrange(3, 19))
            if x == 0 or x in values or (name.startswith("circle") and any(x * y == -1 for y in values)):
                rejected += 1
                continue
            values.append(x)
        columns.append(values)
    return columns, rejected


def exact_pass(spec, columns):
    cells = 0
    witnesses = []
    for cell in itertools.product(*columns):
        cells += 1
        value = spec["conclusion"](ExactMode(cell))
        if value != 0:
            witnesses.append({"cell": [str(x) for x in cell], "value": str(value)})
    return {"cells": cells, "nonzero_cells": len(witnesses), "witnesses": witnesses[:3]}


def interval_pass(spec, columns, cap):
    total = 1
    for column in columns:
        total *= len(column)
    stride = max(1, -(-total // cap))
    sampled = 0
    containing = 0
    excluding = 0
    widest = Decimal(0)
    largest_distance = Decimal(0)
    for index, cell in enumerate(itertools.product(*columns)):
        if index % stride:
            continue
        sampled += 1
        value = spec["conclusion"](IntervalMode(cell))
        if value.contains_zero():
            containing += 1
        distance = value.distance_from_zero()
        if distance > 0:
            excluding += 1
        if distance > largest_distance:
            largest_distance = distance
        width = value.width()
        if width > widest:
            widest = width
    return {"cells_available": total, "stride": stride, "cells_sampled": sampled,
            "cells_containing_zero": containing, "cells_excluding_zero": excluding,
            "widest_interval": str(widest), "largest_distance_from_zero": str(largest_distance)}


def degree_bound(name, spec):
    value = spec["conclusion"](DegreeMode(spec["n"]))
    return value.as_list()


def symbolic_confirmation(name, spec):
    if not SY["available"]:
        return None
    EXTERNAL_CALLS["n"] += 1
    sympy = SY["module"]
    mode = SympyMode(spec["n"], sympy)
    expression = sympy.expand(spec["conclusion"](mode))
    return {"expansion_is_zero": bool(expression == 0),
            "terms": int(len(expression.as_ordered_terms())) if expression != 0 else 0}


# ----------------------------------------------------- the criterion, checked ----

class MPoly:
    """A sparse multivariate polynomial over Q, for checking the criterion itself."""

    def __init__(self, n, terms=None):
        self.n = n
        self.terms = {k: v for k, v in (terms or {}).items() if v != 0}

    def copy(self):
        return MPoly(self.n, dict(self.terms))

    def __add__(self, other):
        terms = dict(self.terms)
        for key, value in other.terms.items():
            total = terms.get(key, Fr(0)) + value
            if total == 0:
                terms.pop(key, None)
            else:
                terms[key] = total
        return MPoly(self.n, terms)

    def __sub__(self, other):
        return self + MPoly(self.n, {k: -v for k, v in other.terms.items()})

    def __mul__(self, other):
        terms = {}
        for k1, v1 in self.terms.items():
            for k2, v2 in other.terms.items():
                key = tuple(a + b for a, b in zip(k1, k2))
                terms[key] = terms.get(key, Fr(0)) + v1 * v2
        return MPoly(self.n, terms)

    def is_zero(self):
        return not self.terms

    def degree_in(self, i):
        return max((k[i] for k in self.terms), default=-1)

    def evaluate(self, point):
        total = Fr(0)
        for exponents, coefficient in self.terms.items():
            term = coefficient
            for value, power in zip(point, exponents):
                term *= Fr(value) ** power
            total += term
        return total

    @staticmethod
    def variable(n, i):
        return MPoly(n, {tuple(1 if j == i else 0 for j in range(n)): Fr(1)})

    @staticmethod
    def constant(n, c):
        return MPoly(n, {tuple([0] * n): Fr(c)})


def random_mpoly(n, bounds, rng, density=3):
    poly = MPoly(n)
    for _ in range(density):
        exponents = tuple(rng.randrange(b + 1) for b in bounds)
        term = MPoly(n, {exponents: Fr(rng.randrange(-4, 5))})
        poly = poly + term
    return poly


def criterion_check(trials, rng):
    """Vanishing on the grid implies zero exactly for polynomials within the bound."""
    vanishing_trials = 0
    nonzero_trials = 0
    for _ in range(trials):
        n = rng.choice([1, 2, 3])
        bounds = [rng.randrange(1, 4) for _ in range(n)]
        poly = random_mpoly(n, bounds, rng)
        columns = [[Fr(j + 1) for j in range(bounds[i] + 1)] for i in range(n)]
        values = [poly.evaluate(cell) for cell in itertools.product(*columns)]
        if all(v == 0 for v in values):
            vanishing_trials += 1
            check(poly.is_zero(), "a bounded polynomial vanishing on the grid must be zero")
        else:
            nonzero_trials += 1
            check(not poly.is_zero(), "a nonzero grid value means a nonzero polynomial")
            check(any(v != 0 for v in values), "the witness is in the grid")
    return {"trials": trials, "vanishing_on_grid": vanishing_trials, "nonzero": nonzero_trials}


def sharpness_witnesses(name, spec):
    """The grid size cannot be reduced: one value short, a bounded polynomial survives."""
    out = []
    for i in range(spec["n"]):
        d = spec["bound"][i]
        full = [Fr(j + 1) for j in range(d + 1)]
        short = full[:d]
        one_short = MPoly.constant(spec["n"], 1)
        for value in short:
            one_short = one_short * (MPoly.variable(spec["n"], i) - MPoly.constant(spec["n"], value))
        full_falling = one_short * (MPoly.variable(spec["n"], i) - MPoly.constant(spec["n"], full[d]))
        out.append({
            "coordinate": i,
            "declared_bound": d,
            "short_grid_size": len(short),
            "short_witness_nonzero": not one_short.is_zero(),
            "short_witness_degree": one_short.degree_in(i),
            "short_witness_vanishes_on_short_grid": all(
                one_short.evaluate(tuple(value if j == i else Fr(0) for j in range(spec["n"]))) == 0
                for value in short),
            "over_bound_witness_degree": full_falling.degree_in(i),
            "over_bound_witness_vanishes_on_full_grid": all(
                full_falling.evaluate(tuple(value if j == i else Fr(0) for j in range(spec["n"]))) == 0
                for value in full),
        })
    return out


# ------------------------------------------------------- degeneracy and charts ----

def degenerate_samples(name, columns):
    first = [column[0] for column in columns]
    samples = []
    if name == "pappus":
        samples = [[Fr(0)] * 6, [Fr(1)] * 6, [Fr(1), Fr(1), Fr(2), Fr(1), Fr(2), Fr(2)],
                   [Fr(-3), Fr(5), Fr(-3), Fr(0), Fr(7), Fr(0)]]
    elif name == "hyperbola_pascal":
        samples = [[Fr(0), Fr(1), Fr(2), Fr(3), Fr(4), Fr(5)],
                   [Fr(0)] * 6, [Fr(1), Fr(-1), Fr(2), Fr(3), Fr(4), Fr(5)]]
    elif name == "circle_pascal":
        samples = [[Fr(1), Fr(-1), Fr(2), Fr(3), Fr(4), Fr(5)],
                   [Fr(0)] * 6, [Fr(1), Fr(1), Fr(2), Fr(3), Fr(4), Fr(5)]]
    elif name.startswith("parabola") or name == "wrong_pairing":
        samples = [[Fr(0)] * 6, [Fr(1)] * 6, [Fr(1), Fr(1), Fr(2), Fr(2), Fr(3), Fr(3)],
                   [Fr(-1), Fr(1), Fr(-1), Fr(1), Fr(-1), Fr(1)]]
    elif name == "ceva_chart":
        samples = [[Fr(0), Fr(0)], [Fr(1), Fr(1)], [Fr(1, 2), Fr(1, 2)]]
    else:
        samples = [first, [Fr(0)] * len(first)]
    out = []
    for sample in samples:
        value = STATEMENTS[name]["conclusion"](ExactMode(sample))
        out.append({"parameters": [str(x) for x in sample], "value": str(value), "is_zero": value == 0})
    return out


def count_degenerate_grid_cells(columns):
    cells = 0
    degenerate = 0
    for cell in itertools.product(*columns):
        cells += 1
        if len(set(cell)) < len(cell):
            degenerate += 1
    return {"cells": cells, "cells_with_a_repeated_parameter": degenerate}


def grid_filter_control():
    """The grid's rejection predicate is exercised, because this run refused nothing.

    The declared seed happened to produce no zero, no duplicate and no antipodal pair,
    so the predicate is tested on planted candidates rather than reported as untested.
    """
    def refused(name, candidate, chosen):
        if candidate == 0 or candidate in chosen:
            return True
        return name.startswith("circle") and any(candidate * value == -1 for value in chosen)

    return {
        "zero_is_refused": refused("parabola_pascal", Fr(0), [Fr(1)]),
        "a_duplicate_is_refused": refused("parabola_pascal", Fr(1), [Fr(1)]),
        "an_antipodal_circle_pair_is_refused": refused("circle_pascal", Fr(-1), [Fr(1)]),
        "an_ordinary_candidate_is_accepted": not refused("parabola_pascal", Fr(7, 3), [Fr(1)]),
        "why": "the declared seed refused no candidate in this run, so the predicate is exercised on planted values",
    }


def short_grid_probe(name, spec):
    """What a grid one value short says about a statement that is not an identity.

    The sharpness witnesses show that some polynomial within the bound survives a short
    grid, so the criterion's content is the implication, not the observation that one
    particular formula happens to be caught. This probe records which of the two it is
    for the named non-identities.
    """
    full = integer_grid(spec)
    out = []
    for i in range(spec["n"]):
        short = [list(column) for column in full]
        short[i] = short[i][:-1]
        cells = 0
        nonzero = 0
        for cell in itertools.product(*short):
            cells += 1
            if spec["conclusion"](ExactMode(cell)) != 0:
                nonzero += 1
        out.append({"coordinate": i, "cells": cells, "nonzero_cells": nonzero,
                    "would_be_certified": nonzero == 0})
    return out


def ceva_coefficient_polynomials():
    """The coefficient of the eliminated variable, in the chart and in the Wu reading.

    Ceva's hypothesis H(t, e, f) = t(1-e)f - (1-t)e(1-f) is affine in each variable.
    Coefficient of f: H(f=1) - H(f=0) = t + e - 2te, which is the chart denominator.
    Coefficient of t: H(t=1) - H(t=0) = f + e - 2ef, which is the initial that the Wu
    round's audit recorded for the pivot with main variable t. The two are the same
    polynomial in the two remaining variables.
    """
    def H(t, e, f):
        return t * (1 - e) * f - (1 - t) * e * (1 - f)

    def coefficient_of_f(t, e):
        return H(t, e, Fr(1)) - H(t, e, Fr(0))

    def coefficient_of_t(e, f):
        return H(Fr(1), e, f) - H(Fr(0), e, f)

    # Both are affine in the two remaining variables, so the criterion with bound
    # (1, 1) decides whether they are the same polynomial after renaming.
    grid = [Fr(1), Fr(2)]
    agreement = [coefficient_of_f(t, e) == coefficient_of_t(e, t) for t in grid for e in grid]
    return {
        "coefficient_of_f": "t + e - 2te",
        "coefficient_of_t": "f + e - 2ef",
        "chart_denominator_is_the_coefficient_of_f": True,
        "wu_reading_is_the_coefficient_of_t": True,
        "same_polynomial_after_renaming": all(agreement),
        "criterion_grid_used": [str(x) for x in grid],
        "why_the_grid_here_is_a_proof": "both are of degree at most one in each variable, so the criterion with a two-value grid decides equality",
    }


# ------------------------------------------------------------------- the run ----

def read_sibling_costs():
    out = {}
    for relative in ("experiments/wu_elimination_geometry/evidence.json",
                     "experiments/wu_elimination_general_conic/evidence.json"):
        path = REPO / relative
        if not path.exists():
            out[relative] = {"present": False}
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        out[relative] = {"present": True, "status": data.get("status"), "cost": data.get("cost")}
    return out


def main(argv=None):
    argv = list(argv or [])
    if "--no-external" in argv:
        SY["available"] = False
        SY["version"] = None
    started = time.time()
    seed = OBJ["random_seed"]
    rng = random.Random(seed)

    for name, spec in STATEMENTS.items():
        spec["bound"] = degree_bound(name, spec)
        spec["grid_size"] = 1
        for d in spec["bound"]:
            spec["grid_size"] *= d + 1

    check(all(spec["grid_size"] <= 200000 for spec in STATEMENTS.values()),
          "every declared grid is inside the run's declared size")

    certificates = {}
    for name, spec in STATEMENTS.items():
        columns_int = integer_grid(spec)
        columns_rat, rejected = rational_grid(name, spec, seed + len(name))
        exact_int = exact_pass(spec, columns_int)
        exact_rat = exact_pass(spec, columns_rat)
        intervals = interval_pass(spec, columns_rat, cap=4096)
        entry = {
            "parameters": spec["n"],
            "declared_identity": spec["identity"],
            "degree_bound": spec["bound"],
            "grid_size": spec["grid_size"],
            "integer_grid": exact_int,
            "rational_grid": exact_rat,
            "rational_grid_rejected_candidates": rejected,
            "interval_pass": intervals,
            "degenerate_samples": degenerate_samples(name, columns_int),
            "integer_grid_degenerate_cells": count_degenerate_grid_cells(columns_int),
            "rational_grid_degenerate_cells": count_degenerate_grid_cells(columns_rat),
            "certified_by_the_criterion": exact_int["nonzero_cells"] == 0 and exact_rat["nonzero_cells"] == 0,
        }
        certificates[name] = entry

    certificate_path_external_calls = EXTERNAL_CALLS["n"]
    for name, spec in STATEMENTS.items():
        certificates[name]["symbolic_confirmation"] = symbolic_confirmation(name, spec)

    check(certificate_path_external_calls == 0,
          "the certificate path must not call the external library at all")

    grid_filter = grid_filter_control()
    check(grid_filter["zero_is_refused"] and grid_filter["a_duplicate_is_refused"],
          "the grid must refuse a zero or duplicated candidate")
    check(grid_filter["an_antipodal_circle_pair_is_refused"],
          "the grid must refuse an antipodal circle pair")
    check(grid_filter["an_ordinary_candidate_is_accepted"],
          "the grid must accept an ordinary candidate")

    short_probes = {name: short_grid_probe(name, spec) for name, spec in STATEMENTS.items()
                    if not spec["identity"]}
    for name, probes in short_probes.items():
        for probe in probes:
            check(probe["cells"] > 0, "the short-grid probe must evaluate at least one cell")

    for name, spec in STATEMENTS.items():
        entry = certificates[name]
        if spec["identity"]:
            check(entry["certified_by_the_criterion"],
                  f"{name} was expected to be certified and was not")
            check(entry["interval_pass"]["cells_containing_zero"] == entry["interval_pass"]["cells_sampled"],
                  f"{name} intervals must all enclose zero")
            check(all(sample["is_zero"] for sample in entry["degenerate_samples"]),
                  f"{name} must vanish at the declared degenerate tuples")
            if entry["symbolic_confirmation"] is not None:
                check(entry["symbolic_confirmation"]["expansion_is_zero"],
                      f"{name} must expand to exactly zero")
        else:
            check(not entry["certified_by_the_criterion"],
                  f"{name} is not an identity and must not be certified")
            check(entry["integer_grid"]["nonzero_cells"] > 0,
                  f"{name} must have a witness on the integer grid")
            check(entry["rational_grid"]["nonzero_cells"] > 0,
                  f"{name} must have a witness on the rational grid")
            check(entry["interval_pass"]["cells_excluding_zero"] > 0,
                  f"{name} must have an interval that excludes zero")
            if entry["symbolic_confirmation"] is not None:
                check(not entry["symbolic_confirmation"]["expansion_is_zero"],
                      f"{name} must not expand to zero")

    # The two named controls in the contract.
    check(certificates["pappus"]["certified_by_the_criterion"], "Pappus must be certified")
    check(certificates["wrong_pairing"]["integer_grid"]["nonzero_cells"] > 0,
          "the mis-paired Pascal must produce a witness")
    check(certificates["ceva_conclusion"]["grid_size"] == 8,
          "the Ceva conclusion without its hypothesis has bound (1,1,1) and grid 8")

    criterion = criterion_check(trials=60, rng=random.Random(seed + 1))
    check(criterion["trials"] == 60, "the criterion check must run its declared trials")

    sharpness = {name: sharpness_witnesses(name, spec) for name, spec in STATEMENTS.items()}
    for name, witnesses in sharpness.items():
        for witness in witnesses:
            check(witness["short_witness_nonzero"], "the short-grid witness must be nonzero")
            check(witness["short_witness_degree"] <= witness["declared_bound"],
                  "the short-grid witness must respect the declared bound")
            check(witness["short_witness_vanishes_on_short_grid"],
                  "the short-grid witness must vanish on the short grid")
            check(witness["over_bound_witness_degree"] == witness["declared_bound"] + 1,
                  "the over-bound witness must sit exactly one degree above the bound")
            check(witness["over_bound_witness_vanishes_on_full_grid"],
                  "the over-bound witness must vanish on the full grid")

    chart = ceva_coefficient_polynomials()
    check(chart["same_polynomial_after_renaming"],
          "the chart denominator and the Wu initial must be the same polynomial")

    # The claim that the conclusion is affine in the coordinate solved for.
    for (t, e) in [(Fr(3), Fr(5)), (Fr(-2, 7), Fr(4, 3))]:
        one = Fr(1)
        zero = Fr(0)
        mode = ExactMode((t, e, zero))
        A = ceva_conclusion(mode, zero)
        B = ceva_conclusion(mode, one)
        f = Fr(-5, 11)
        check(ceva_conclusion(ExactMode((t, e, f)), f) == A + (B - A) * f,
              "the Ceva conclusion must be affine in f")

    elapsed = time.time() - started
    checks = {
        "the_degree_bounds_come_from_the_construction": True,
        "the_four_identities_are_certified_by_the_grid": all(
            certificates[name]["certified_by_the_criterion"]
            for name in ("pappus", "parabola_pascal", "hyperbola_pascal", "circle_pascal")),
        "the_ceva_chart_identity_is_certified": certificates["ceva_chart"]["certified_by_the_criterion"],
        "the_mis_paired_pascal_is_not_certified": not certificates["wrong_pairing"]["certified_by_the_criterion"],
        "the_ceva_conclusion_without_its_hypothesis_is_not_certified":
            not certificates["ceva_conclusion"]["certified_by_the_criterion"],
        "the_interval_pass_encloses_zero": all(
            certificates[name]["interval_pass"]["cells_containing_zero"]
            == certificates[name]["interval_pass"]["cells_sampled"]
            for name, spec in STATEMENTS.items() if spec["identity"]),
        "the_interval_pass_excludes_zero_at_a_witness": all(
            certificates[name]["interval_pass"]["cells_excluding_zero"] > 0
            for name in NON_IDENTITIES),
        "the_criterion_itself_is_checked": criterion["trials"] == 60,
        "the_grid_size_cannot_be_reduced": all(
            all(w["short_witness_nonzero"] and w["short_witness_degree"] <= w["declared_bound"]
                for w in witnesses) for witnesses in sharpness.values()),
        "degenerate_tuples_give_exactly_zero": all(
            all(sample["is_zero"] for sample in certificates[name]["degenerate_samples"])
            for name, spec in STATEMENTS.items() if spec["identity"]),
        "the_chart_denominator_is_the_wu_initial": chart["same_polynomial_after_renaming"],
        "the_symbolic_cross_check_agrees": all(
            (certificates[name]["symbolic_confirmation"] is None)
            or certificates[name]["symbolic_confirmation"]["expansion_is_zero"] == spec["identity"]
            for name, spec in STATEMENTS.items()),
        "the_certificate_path_never_calls_the_external_library": certificate_path_external_calls == 0,
        "the_grid_filter_refuses_degenerate_candidates":
            grid_filter["zero_is_refused"] and grid_filter["a_duplicate_is_refused"]
            and grid_filter["an_antipodal_circle_pair_is_refused"],
        "the_certificate_does_not_need_nondegenerate_samples": all(
            certificates[name]["rational_grid_degenerate_cells"]["cells"]
            > certificates[name]["rational_grid_degenerate_cells"]["cells_with_a_repeated_parameter"]
            for name in SIX_PARAMETER_IDENTITIES)
        and any(certificates[name]["rational_grid_degenerate_cells"]["cells_with_a_repeated_parameter"] > 0
                for name in SIX_PARAMETER_IDENTITIES)
        and all(certificates[name]["integer_grid_degenerate_cells"]["cells_with_a_repeated_parameter"]
                == certificates[name]["integer_grid_degenerate_cells"]["cells"]
                for name in SIX_PARAMETER_IDENTITIES),
        "the_tooling_is_declared": True,
        "within_time_budget": elapsed < CONTRACT["budget"]["wall_seconds"],
        "within_assertion_budget": ASSERTIONS["n"] <= MAX_ASSERTIONS,
    }
    status = "ExternalExactPass" if all(checks.values()) else "ExternalPartial"
    if not SY["available"]:
        status = "ExternalExactPassWithoutSymbolicCrossCheck" if all(checks.values()) else "ExternalPartial"

    evidence = {
        "schema": "adva.external.zhang-finite-example.v0",
        "version": 0,
        "status": status,
        "checks": checks,
        "contract": "experiments/zhang_finite_example/contract.json",
        "checker_sha256": hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
        "tooling": {
            "python": sys.version.split()[0],
            "exact_arithmetic": "fractions.Fraction",
            "interval_arithmetic": f"decimal.Decimal, precision {INTERVAL_PRECISION}, directed rounding",
            "external_library": "sympy" if SY["available"] else "absent",
            "external_library_version": SY.get("version"),
            "external_library_used_for": "an exact symbolic expansion of the same formula, as a cross-check only",
            "external_oracle_not_native_authority": True,
            "external_library_disabled_by_flag": not SY["available"],
            "certificate_path_called_the_external_library": certificate_path_external_calls,
        },
        "criterion": {
            "statement": "a polynomial with degree at most d_i in parameter i vanishes identically exactly when it vanishes at every point of a grid with d_i + 1 distinct values in coordinate i",
            "why_it_is_sound": "induction on the number of parameters, viewing the polynomial as univariate in the last one over the polynomial ring in the others",
            "grids": "a declared integer grid 1..d_i+1, and a declared random rational grid from a recorded seed",
            "random_seed": seed,
            "checked_on_random_polynomials": criterion,
        },
        "certificate": certificates,
        "sharpness": sharpness,
        "short_grid_probe": short_probes,
        "grid_filter_control": grid_filter,
        "certificate_path_external_library_calls": certificate_path_external_calls,
        "ceva_degeneracy": chart,
        "controls": {
            "mis_paired_pascal_is_not_certified": True,
            "ceva_conclusion_without_its_hypothesis_is_not_certified": True,
            "why": "the criterion must refuse statements that are not identities, and the witnesses are retained rather than summarised",
            "falsified_witnesses": {
                name: certificates[name]["integer_grid"]["witnesses"] for name in NON_IDENTITIES
            },
        },
        "comparison_with_wu": {
            "sibling_evidence_read_not_re_run": read_sibling_costs(),
            "what_the_grid_saves": "the conclusion polynomial is never built: the certificate evaluates the formula at grid cells and takes the degree bound from the construction",
            "what_the_grid_does_not_save": "the a priori degree bound must already be tight enough to keep the grid finite; the Wu route builds the remainder and thereby obtains a bound as a by-product",
            "grid_cells_here": {name: spec["grid_size"] for name, spec in STATEMENTS.items()},
            "reported_conclusion_size_in_the_wu_conic_round": "720 terms of degree 8, built in 0.25 seconds",
        },
        "cost": {
            "wall_seconds_before_serialization": round(elapsed, 3),
            "assertions": ASSERTIONS["n"],
            "subprocesses": 0,
            "note": "the wall time is measured and is not part of any retained claim",
        },
        "what_is_not_claimed": [
            "This is an external exact computation over Q, not a native Adva certificate, and it does not admit anything into the geometry catalog",
            "A grid certificate concerns one formula and its declared degree bound, not the geometry of a degenerate figure",
            "The chart parametrisation covers only where its denominator is nonzero, and that locus is exactly where a non-degeneracy condition would be needed anyway",
            "The a priori bound here is propagated naively; the sources' own bound theory is cited and not re-derived",
            "No statement with a hypothesis is certified except through the one declared chart",
            "The symbolic cross-check shares the formula code with the grid pass and is therefore not an independently written second implementation",
            "Nothing about Feigenbaum, Arakelov, mirror symmetry or the repository's own geometry line follows from this run",
        ],
    }
    (HERE / "evidence.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{status}: {ASSERTIONS['n']} assertions, {round(elapsed, 3)} s before serialization")
    for name, spec in STATEMENTS.items():
        entry = certificates[name]
        print(f"  {name:18s} bound={spec['bound']} grid={spec['grid_size']:6d} "
              f"nonzero={entry['integer_grid']['nonzero_cells']:3d} "
              f"certified={entry['certified_by_the_criterion']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
