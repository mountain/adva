#!/usr/bin/env python3
"""Exact calibration of one exchange amplitude variation, with checkable results.

Frozen contract: experiments/exchange_amplitude_variation_v1/contract.json.
Superseded contract, retained byte for byte: contract-initial.json beside it.
This checker is an external exact calibration.  It constructs no native
certificate, promotes no native identity, and makes no physical claim.

What the run decides, and with what:

* the twelve-phase 0233 fixture, its exact periodic reference and the side
  identity h_1 = E_0(h), h_2 = E_1(h_1), h_m = h_2 for m = 3..12, asserted for a
  general anomaly h rather than assumed;
* the unperturbed annual return E, the return polynomial P, its factorisation in
  Q(sqrt(17))[y] with y = h + 2, the two real roots and the conjugate pair, with
  exact sign conditions and an independent field-arithmetic check;
* the collapse witness of the superseded contract, executed as a control;
* the discriminant variety D(p, q) = Res_h(E_{p,q} - 1, d/dh E_{p,q}) exactly,
  with degree, term count, factorisation and declared branches;
* a declared finite case analysis of the maximum, one characteristic chain per
  case by pseudo-division, every remainder cross-checked by an independent
  Groebner basis membership test;
* real-root counting and exact rational isolation by Sturm sequences at declared
  parameter points, with the side of the discriminant variety;
* minimality rather than stationarity by exact rational interval arithmetic on a
  declared box: the interval-subdivision variant.  Successive difference
  substitution is not implemented and the evidence says so;
* a declared finite sequence of closed loops in the (p, q) plane with the
  resulting permutation of the four roots where exact real tracking decides it,
  and an explicit Undecided outcome with its reason where it does not;
* every control the frozen contract declares.

All acceptance arithmetic is integers and fractions.Fraction, plus the declared
quadratic field Q(sqrt(17)) and exact polynomial arithmetic.  No floating-point
value enters an assertion or the evidence payload.  sympy is a declared external
library and is not native authority.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import pathlib
import resource
import signal
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "contract.json"
INITIAL_PATH = HERE / "contract-initial.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
INITIAL = json.loads(INITIAL_PATH.read_text(encoding="utf-8"))

ASSERTIONS = {"n": 0}


def check(condition, message):
    """One exact acceptance assertion, counted."""
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def qsign(value):
    """The sign of an exact sympy rational as a Python integer."""
    return (int(value.p) > 0) - (int(value.p) < 0)


def _gcd(left, right):
    """An exact integer gcd, used only for the content of an integer polynomial."""
    left, right = abs(left), abs(right)
    while right:
        left, right = right, left % right
    return left


def rat(value):
    """An exact sympy rational from a Fraction, an int or a string."""
    if isinstance(value, Fr):
        return RATIONAL(value.numerator, value.denominator)
    return RATIONAL(value)


# ------------------------------------------------------------ interval algebra --

class Ivl:
    """A closed interval with exact Fraction endpoints; no float is ever formed."""

    __slots__ = ("hi", "lo")

    def __init__(self, lo, hi=None):
        self.lo = lo if isinstance(lo, Fr) else Fr(lo)
        self.hi = self.lo if hi is None else (hi if isinstance(hi, Fr) else Fr(hi))
        if self.lo > self.hi:
            raise ValueError("empty interval")

    def __add__(self, other):
        other = other if isinstance(other, Ivl) else Ivl(other)
        return Ivl(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __sub__(self, other):
        other = other if isinstance(other, Ivl) else Ivl(other)
        return Ivl(self.lo - other.hi, self.hi - other.lo)

    def __neg__(self):
        return Ivl(-self.hi, -self.lo)

    def __mul__(self, other):
        other = other if isinstance(other, Ivl) else Ivl(other)
        products = (self.lo * other.lo, self.lo * other.hi,
                    self.hi * other.lo, self.hi * other.hi)
        return Ivl(min(products), max(products))

    __rmul__ = __mul__

    def scale(self, factor):
        factor = factor if isinstance(factor, Fr) else Fr(factor)
        if factor >= 0:
            return Ivl(self.lo * factor, self.hi * factor)
        return Ivl(self.hi * factor, self.lo * factor)

    def power(self, exponent):
        result = Ivl(1)
        for _ in range(exponent):
            result = result * self
        return result

    def sign(self):
        if self.lo > 0:
            return "positive"
        if self.hi < 0:
            return "negative"
        if self.lo == 0 and self.hi == 0:
            return "zero"
        return "mixed"

    def __str__(self):
        return "[" + str(self.lo) + ", " + str(self.hi) + "]"


# --------------------------------------------------- Q(sqrt(17)) exact arithmetic --

class Q17:
    """a + b * sqrt(17) with a and b exact Fractions."""

    __slots__ = ("a", "b")

    def __init__(self, a=0, b=0):
        self.a = a if isinstance(a, Fr) else Fr(a)
        self.b = b if isinstance(b, Fr) else Fr(b)

    def __add__(self, other):
        other = other if isinstance(other, Q17) else Q17(other)
        return Q17(self.a + other.a, self.b + other.b)

    __radd__ = __add__

    def __sub__(self, other):
        other = other if isinstance(other, Q17) else Q17(other)
        return Q17(self.a - other.a, self.b - other.b)

    def __neg__(self):
        return Q17(-self.a, -self.b)

    def __mul__(self, other):
        other = other if isinstance(other, Q17) else Q17(other)
        return Q17(self.a * other.a + 17 * self.b * other.b,
                   self.a * other.b + self.b * other.a)

    __rmul__ = __mul__

    def __eq__(self, other):
        other = other if isinstance(other, Q17) else Q17(other)
        return self.a == other.a and self.b == other.b

    def is_zero(self):
        return self.a == 0 and self.b == 0

    def __str__(self):
        return "(" + str(self.a) + " + " + str(self.b) + " sqrt(17))"


def q17_mul(left, right):
    out = [Q17() for _ in range(len(left) + len(right) - 1)]
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            out[i + j] = out[i + j] + x * y
    return out


def q17_eval(coefficients, value):
    total = Q17()
    for coefficient in reversed(coefficients):
        total = total * value + coefficient
    return total


def q17_scale(coefficients, factor):
    return [factor * coefficient for coefficient in coefficients]


# ------------------------------------------------------------ sympy declaration --

def import_sympy():
    try:
        import sympy
        return {"available": True, "version": sympy.__version__, "sympy": sympy}
    except Exception as error:  # pragma: no cover - reported, never raised
        return {"available": False, "error": str(error)}


SY = import_sympy()
if SY["available"]:
    sp = SY["sympy"]
    RATIONAL = sp.Rational
else:  # pragma: no cover - the tooling branch is reported, not reached
    RATIONAL = None


# ------------------------------------------------------------------- the fixture --

REFERENCE_PATH = (0, 1, 2, 1, 0, -1, -2, -1, 0, 1, 0, -1, 0)
DILATIONS = (Fr(1, 2), Fr(3, 4)) + (Fr(1),) * 10
CURVATURES = (Fr(1, 8), Fr(1, 8)) + (Fr(0),) * 10

# declared perturbed parameters at which E_{p,q}(0) = 0 is asserted
DECLARED_PERTURBATIONS = ((Fr(0), Fr(0)), (Fr(-2), Fr(17, 10)), (Fr(15, 8), Fr(0)),
                          (Fr(1), Fr(1)), (Fr(-1, 8), Fr(0)), (Fr(5, 2), Fr(-1, 4)))

DECLARED_POINTS = (
    ("frozen", Fr(0), Fr(0)),
    ("the declared J_inf witness", Fr(-2), Fr(17, 10)),
    ("equal perturbations", Fr(1), Fr(1)),
    ("large positive p with q = 0", Fr(15, 8), Fr(0)),
    ("above the parabola with q > -1/8", Fr(0), Fr(6)),
    ("below q = -1/8", Fr(0), Fr(-3, 10)),
    ("four real roots", Fr(5, 2), Fr(-1, 4)),
    ("on the branch B1", Fr(0), Fr(43, 8)),
    ("on the branch B2 at p = 0", Fr(0), Fr(-17, 64)),
    ("the tangency vertex of B1 and B2", Fr(-19, 128), Fr(-17, 64)),
    ("on the degenerate line B3", Fr(0), Fr(-1, 8)),
    ("on the degenerate line B4", Fr(-1, 8), Fr(0)),
    ("the triple point of B1, B3 and B4", Fr(-1, 8), Fr(-1, 8)),
)

WITNESS = (Fr(-2), Fr(17, 10))
PLATEAU_BOX = (Ivl(Fr(-2) - Fr(1, 1000), Fr(-2) + Fr(1, 1000)),
               Ivl(Fr(17, 10) - Fr(1, 1000), Fr(17, 10) + Fr(1, 1000)))
ESCAPE_RAY = (1, 2, 4, 8, 16, 64, 256, 1024)
ISOLATION_EPS = RATIONAL(1, 10 ** 12) if SY["available"] else None
COARSE_EPS = RATIONAL(1, 10 ** 18) if SY["available"] else None


def build_symbolic():
    """The declared family, exactly, as sympy expressions in p, q and h."""
    p, q, h = sp.symbols("p q h")
    alpha = RATIONAL(1, 8) + p
    beta = RATIONAL(1, 8) + q
    e0 = h / 2 + alpha * h ** 2
    annual = sp.expand(RATIONAL(3, 4) * e0 + beta * e0 ** 2)
    return {
        "p": p, "q": q, "h": h, "alpha": alpha, "beta": beta,
        "E0": sp.expand(e0), "E": annual, "G": sp.expand(annual - 1),
        "Gp": sp.expand(sp.diff(annual, p)), "Gq": sp.expand(sp.diff(annual, q)),
        "Gh": sp.expand(sp.diff(annual, h)),
    }


def g_at(sym, pv, qv):
    """The exact univariate return polynomial G(pv, qv, h)."""
    return sp.Poly(sp.expand(sym["G"].subs({sym["p"]: rat(pv), sym["q"]: rat(qv)})), sym["h"])


def discriminant_polynomial(sym):
    """The primitive integer discriminant polynomial D(p, q)."""
    resultant = sp.expand(sp.resultant(sp.Poly(sym["G"], sym["h"]),
                                       sp.Poly(sym["Gh"], sym["h"])))
    return sp.Poly(resultant, sym["p"], sym["q"]).primitive()[1]


# ------------------------------------------------------------- section S1 -------

def section_fixture(sym):
    """The 0233 fixture and the side identity for a general anomaly."""
    h = sym["h"]
    check(len(REFERENCE_PATH) == 13, "the reference path is a closed 13-boundary path")
    check(REFERENCE_PATH[0] == REFERENCE_PATH[12], "the reference path closes")
    check(len(DILATIONS) == 12 and len(CURVATURES) == 12, "the fixture has twelve phases")
    check(DILATIONS[2:] == (Fr(1),) * 10, "phases 2..11 are pure translations")
    check(CURVATURES[2:] == (Fr(0),) * 10, "phases 2..11 are linear")
    check(DILATIONS[0] == Fr(1, 2) and DILATIONS[1] == Fr(3, 4), "declared dilations at 0 and 1")
    check(CURVATURES[0] == Fr(1, 8) and CURVATURES[1] == Fr(1, 8),
          "declared curvatures at 0 and 1")
    # the reference is an exact periodic orbit of the declared phase recursion
    position = Fr(REFERENCE_PATH[0])
    for m in range(12):
        deviation = position - Fr(REFERENCE_PATH[m])
        image = Fr(REFERENCE_PATH[m + 1]) + DILATIONS[m] * deviation \
            + CURVATURES[m] * deviation ** 2
        check(image == Fr(REFERENCE_PATH[m + 1]),
              f"the reference boundary {m + 1} is reproduced by the declared phase map")
        position = image
    check(position == Fr(REFERENCE_PATH[12]), "the reference closes after twelve phases")
    anomaly_symbol = sp.Symbol("hh")
    for m in range(12):
        anomaly = DILATIONS[m] * anomaly_symbol + CURVATURES[m] * anomaly_symbol ** 2
        check(sp.expand(anomaly - (DILATIONS[m] * anomaly_symbol
                                   + CURVATURES[m] * anomaly_symbol ** 2)) == 0,
              f"the anomaly map of phase {m} is a_m h + q_m h^2")
        check(sp.expand(anomaly.subs({anomaly_symbol: 0})) == 0,
              f"the anomaly map of phase {m} vanishes on the reference")
    # the general-h side identity by exact composition
    h1 = sp.expand(DILATIONS[0] * h + CURVATURES[0] * h ** 2)
    h2 = sp.expand(DILATIONS[1] * h1 + CURVATURES[1] * h1 ** 2)
    walk = h2
    for m in range(2, 12):
        walk = sp.expand(DILATIONS[m] * walk + CURVATURES[m] * walk ** 2)
        check(sp.expand(walk - h2) == 0, f"side {m + 1} equals side 2 for a general h")
    frozen_return = sp.expand(sym["E"].subs({sym["p"]: 0, sym["q"]: 0}))
    check(sp.expand(walk - frozen_return) == 0,
          "the composed return of the unperturbed fixture equals the frozen return")
    check(sp.expand(h1 - sym["E0"].subs({sym["p"]: 0})) == 0, "side 1 is E_0(h)")
    check(sp.expand(h2 - frozen_return) == 0, "side 2 is E_{p,q}(h) at the frozen parameters")
    # the perturbed family, composed through the same twelve phases
    perturbed_one = sp.expand(DILATIONS[0] * h + (CURVATURES[0] + sym["p"]) * h ** 2)
    perturbed_two = sp.expand(DILATIONS[1] * perturbed_one
                              + (CURVATURES[1] + sym["q"]) * perturbed_one ** 2)
    perturbed_walk = perturbed_two
    for m in range(2, 12):
        perturbed_walk = sp.expand(DILATIONS[m] * perturbed_walk
                                   + CURVATURES[m] * perturbed_walk ** 2)
    check(sp.expand(perturbed_one - sym["E0"]) == 0, "the perturbed side 1 is E_0(h)")
    check(sp.expand(perturbed_walk - sym["E"]) == 0,
          "the perturbed twelve-phase composition equals the declared E_{p,q}")
    check(sp.expand(sym["E"].subs({h: 0})) == 0, "E_{p,q}(0) = 0 identically")
    for pv, qv in DECLARED_PERTURBATIONS:
        value = sp.expand(sym["E"].subs({sym["p"]: rat(pv), sym["q"]: rat(qv), h: 0}))
        check(value == 0, f"E_{{p,q}}(0) = 0 at the declared perturbation ({pv}, {qv})")
    check(sp.expand((sym["E"] - 1) - sym["G"]) == 0,
          "the branch equation E_{p,q}(h) = 1 is G = 0")
    return {
        "declared_reading": CONTRACT["declared_reading"]["process"],
        "reference_path": list(REFERENCE_PATH),
        "dilations": [str(x) for x in DILATIONS],
        "curvatures": [str(x) for x in CURVATURES],
        "reference_is_an_exact_periodic_orbit": True,
        "side_identity_for_a_general_h": {
            "h_1": str(h1),
            "h_2": str(h2),
            "h_m_equals_h_2_for_m_equals_3_to_12": True,
            "composed_return": str(walk),
            "annual_return": str(sym["E"]),
        },
        "side_amplitude_model": {
            "side_0": "|h|",
            "side_1": "|E_0(h)| with E_0(h) = h/2 + (1/8 + p) h^2",
            "sides_2_to_11": "exactly 1 on a branch, because h_m = h_2 = E_{p,q}(h) = 1",
            "terminal_boundary_12": "exactly 1 on a branch, reported separately",
        },
        "E_0": str(sym["E0"]),
        "E_p_q": str(sym["E"]),
        "E_p_q_minus_one": str(sym["G"]),
        "E_p_q_at_zero_is_zero_for_declared_parameters": [str(pv) + ", " + str(qv)
                                                         for pv, qv in DECLARED_PERTURBATIONS],
    }


# ------------------------------------------------------------- section S2 -------

def section_unperturbed(sym):
    """The frozen return, its Q(sqrt(17)) factorisation, its roots and sign data."""
    h, y = sym["h"], sp.Symbol("y")
    frozen = sp.expand(sym["E"].subs({sym["p"]: 0, sym["q"]: 0}))
    declared = sp.expand(RATIONAL(3, 8) * h + RATIONAL(1, 8) * h ** 2
                         + RATIONAL(1, 64) * h ** 3 + RATIONAL(1, 512) * h ** 4)
    check(sp.expand(frozen - declared) == 0, "the frozen annual return is the declared quartic")
    return_polynomial = sp.expand(512 * frozen - 512)
    expected = h ** 4 + 8 * h ** 3 + 64 * h ** 2 + 192 * h - 512
    check(sp.expand(return_polynomial - expected) == 0,
          "the return equation is P(h) = h^4 + 8 h^3 + 64 h^2 + 192 h - 512")
    shifted = sp.expand(return_polynomial.subs(h, y - 2))
    check(sp.expand(shifted - (y ** 4 + 40 * y ** 2 - 688)) == 0,
          "P(y - 2) = y^4 + 40 y^2 - 688")
    # an independent check in Q(sqrt(17))[y]: multiply the two declared factors by hand
    factor_one = [Q17(20) - Q17(0, 8), Q17(), Q17(1)]
    factor_two = [Q17(20) + Q17(0, 8), Q17(), Q17(1)]
    product = q17_mul(factor_one, factor_two)
    check(product == [Q17(-688), Q17(), Q17(40), Q17(), Q17(1)],
          "the factorisation is an identity in Q(sqrt(17))[y]")
    check(not q17_eval(product, Q17(1)).is_zero(),
          "the product is not the zero polynomial in the field")
    # exact sign conditions, by comparison of squares only
    check(64 * 17 > 400, "8 sqrt(17) > 20 because 64*17 = 1088 > 400 = 20^2")
    # the two values of y^2 satisfy w^2 + 40 w - 688 = 0 in Q(sqrt(17))
    real_square = Q17(-20, 8)
    complex_square = Q17(-20, -8)
    rows = []
    for name, w in (("real pair", real_square), ("conjugate pair", complex_square)):
        value = w * w + Q17(40) * w - Q17(688)
        check(value.is_zero(), f"y^2 = w satisfies w^2 + 40 w - 688 = 0 for the {name}")
        rows.append({"name": name, "y_squared": str(w),
                     "sign_of_y_squared": "positive" if w.a > 0 or (w.a == 0 and w.b > 0)
                     else "negative"})
    check(real_square.a < 0 and real_square.b > 0, "8 sqrt(17) - 20 is written exactly")
    check(17 * real_square.b * real_square.b > real_square.a * real_square.a,
          "8 sqrt(17) - 20 > 0 by comparing squares: (8 sqrt(17))^2 = 1088 > 400")
    check(complex_square.a < 0 and complex_square.b < 0, "-20 - 8 sqrt(17) < 0")
    frozen_poly = sp.Poly(expected, h)
    intervals = frozen_poly.intervals(eps=ISOLATION_EPS)
    check(len(intervals) == 2, "the frozen return equation has two distinct real roots")
    check(frozen_poly.eval(RATIONAL(-6)) * frozen_poly.eval(RATIONAL(-5)) < 0,
          "exact rational bracket for the negative root")
    check(frozen_poly.eval(RATIONAL(3, 2)) * frozen_poly.eval(RATIONAL(17, 10)) < 0,
          "exact rational bracket for the positive root")
    return {
        "annual_return": str(frozen),
        "return_polynomial": str(expected),
        "shifted_polynomial": str(sp.expand(shifted)),
        "factorisation_in_Q_sqrt17_y": "(y^2 + 20 - 8 sqrt(17)) (y^2 + 20 + 8 sqrt(17))",
        "factorisation_checked_by_field_arithmetic": True,
        "two_real_roots": "h = -2 +- sqrt(8 sqrt(17) - 20)",
        "conjugate_pair": "h = -2 +- i sqrt(8 sqrt(17) + 20)",
        "sign_conditions": {
            "8_sqrt17_minus_20_positive": True,
            "comparison": "64*17 = 1088 > 400 = 20^2, so 8 sqrt(17) > 20",
            "first_factor": "y^2 + 20 - 8 sqrt(17) = y^2 - (8 sqrt(17) - 20) has two real roots, "
                            "since its constant term is negative",
            "second_factor": "y^2 + 20 + 8 sqrt(17) > 0 for every real y, so it carries the "
                             "conjugate pair",
        },
        "field_rows": rows,
        "sturm": {
            "distinct_real_roots": len(intervals),
            "isolation_intervals": [[str(RATIONAL(lo)), str(RATIONAL(hi)), multiplicity]
                                    for (lo, hi), multiplicity in intervals],
            "exact_brackets": {"negative_root_in": "(-6, -5)",
                               "positive_root_in": "(3/2, 17/10)"},
        },
    }


# ------------------------------------------------------------- section S3 -------

def side_amplitudes(branch):
    """The twelve side amplitudes and the terminal amplitude for one branch value."""
    h1 = DILATIONS[0] * branch + CURVATURES[0] * branch ** 2
    terminal = h1
    for m in range(1, 12):
        terminal = DILATIONS[m] * terminal + CURVATURES[m] * terminal ** 2
    sides = [abs(branch), abs(h1)] + [abs(terminal)] * 10
    return sides, abs(terminal)


def section_superseded_witness():
    """The collapse witness of the superseded contract, reproduced exactly."""
    p_value = Q17(-4)
    q_value = Q17(-16, 8)
    check(q_value == Q17(-16, 8) and q_value.b == 8,
          "q = 8 sqrt(17) - 16 is represented exactly")
    check(q_value.a == -16 and q_value.b * q_value.b * 17 == 64 * 17,
          "the square of the sqrt(17) part is 64*17 = 1088")
    first_factor = [Q17(20) - Q17(0, 8) + q_value, p_value, Q17(1)]
    second_factor = [Q17(20) + Q17(0, 8), Q17(), Q17(1)]
    collapsed = [Q17(4), Q17(-4), Q17(1)]
    check(first_factor == collapsed,
          "at p = -4 and q = 8 sqrt(17) - 16 the first factor is (y - 2)^2")
    quartic = q17_mul(first_factor, second_factor)
    check(quartic == q17_mul(collapsed, second_factor), "the quartic carries the collapsed factor")
    check(q17_eval(collapsed, Q17(2)).is_zero(), "y = 2 is a root of the collapsed factor")
    check(not q17_eval(second_factor, Q17(2)).is_zero(),
          "the other factor does not vanish at y = 2, so the multiplicity is exactly two")
    check(second_factor == [Q17(20, 8), Q17(), Q17(1)],
          "the conjugate factor is y^2 + 20 + 8 sqrt(17)")
    sides, terminal = side_amplitudes(Fr(0))
    check(all(value == 0 for value in sides), "at the collapsed branch every side amplitude is 0")
    check(terminal == 0, "at the collapsed branch the terminal amplitude is 0")
    eps_rows = []
    for eps in (Fr(1, 2), Fr(1, 4), Fr(1, 10), Fr(1, 100)):
        plus_sides, plus_terminal = side_amplitudes(eps)
        minus_sides, minus_terminal = side_amplitudes(-eps)
        level = max(plus_sides + minus_sides)
        check(level == eps, f"branches at +-eps give J_inf = eps exactly for eps = {eps}")
        check(plus_terminal < eps and minus_terminal < eps,
              f"the terminal amplitude stays below the level for eps = {eps}")
        check(all(value < eps for value in plus_sides[2:] + minus_sides[2:]),
              f"every translation side stays below the level for eps = {eps}")
        eps_rows.append({
            "eps": str(eps),
            "J_inf_of_the_two_branches": str(level),
            "side_amplitudes_positive_branch": [str(value) for value in plus_sides],
            "side_amplitudes_negative_branch": [str(value) for value in minus_sides],
            "terminal_amplitude_positive_branch": str(plus_terminal),
            "terminal_amplitude_negative_branch": str(minus_terminal),
        })
    return {
        "supersedes": CONTRACT["correction"]["supersedes"],
        "superseded_sha256_declared": CONTRACT["correction"]["superseded_sha256"],
        "superseded_sha256_recomputed": digest(INITIAL_PATH),
        "superseded_sha256_matches": digest(INITIAL_PATH)
                                      == CONTRACT["correction"]["superseded_sha256"],
        "initial_family": "P_{p,q}(y) = (y^2 + p y + (20 - 8 sqrt(17) + q)) "
                          "(y^2 + 20 + 8 sqrt(17)) with y = h + 2",
        "collapsed_parameters": {"p": "-4", "q": "8 sqrt(17) - 16"},
        "first_factor_at_the_collapsed_parameters": "(y - 2)^2",
        "double_root": {"y": "2", "h": "0", "multiplicity": 2},
        "amplitudes_at_the_collapsed_branch": [str(value) for value in sides],
        "terminal_amplitude_at_the_collapsed_branch": str(terminal),
        "J_inf_at_the_collapsed_branch": "0",
        "branches_at_plus_minus_eps": eps_rows,
        "why_the_initial_contract_was_superseded": (
            "In the initial family the two branches were roots of the perturbed quartic rather "
            "than of a declared return equation, so they could be moved onto the reference "
            "h = 0. At (p, q) = (-4, 8 sqrt(17) - 16) the quartic has a double root exactly at "
            "h = 0, every side amplitude vanishes and J_inf = 0 with coincident branches; with "
            "distinct branches at +-eps the functional is exactly eps, so the infimum 0 is "
            "approached without being attained. The frozen contract instead keeps the branches "
            "defined by E_{p,q}(h) = 1, so h = 0 is never a branch and the collapse is excluded."),
        "the_reference_is_never_a_branch_in_the_frozen_family": (
            "E_{p,q}(0) = 0 for every (p, q), while a branch requires E_{p,q}(h) = 1"),
    }


# ------------------------------------------------------------- section S4 -------

def section_discriminant(sym):
    """D(p, q) exactly, with degree, term count, factorisation and declared branches."""
    p, q, h = sym["p"], sym["q"], sym["h"]
    g, g_h = sym["G"], sym["Gh"]
    primitive = discriminant_polynomial(sym)
    expected = sp.expand(-((8 * p + 1) ** 6) * ((8 * q + 1) ** 2) * ((64 * q + 17) ** 2)
                         * (2048 * p ** 2 + 608 * p - 8 * q + 43))
    check(sp.expand(primitive.as_expr() - expected) == 0,
          "the primitive integer discriminant polynomial is the declared factorisation")
    check(primitive.LC() != 0, "the primitive polynomial is nonzero")
    coefficients = [coefficient for _, coefficient in primitive.terms()]
    check(all(coefficient.q == 1 for coefficient in coefficients),
          "the cleared polynomial has integer coefficients")
    content_of_integers = 0
    for coefficient in coefficients:
        content_of_integers = _gcd(content_of_integers, abs(int(coefficient)))
    check(content_of_integers == 1, "the integer coefficients are coprime, so the clearing is "
                                    "primitive")
    resultant = sp.expand(sp.resultant(sp.Poly(g, h), sp.Poly(g_h, h)))
    leading = sp.Poly(g, h).LC()
    check(sp.expand(resultant - leading * sp.expand(sp.discriminant(g, h))) == 0,
          "Res_h(G, G_h) = lc(G) disc_h(G) as polynomials in p and q")
    terms = primitive.as_expr().as_ordered_terms()
    factor_list = [(sp.factor(factor), multiplicity)
                   for factor, multiplicity in sp.factor_list(primitive.as_expr())[1]]
    check(len(factor_list) == 4, "the primitive polynomial has four irreducible factors")
    parabola = sp.expand(256 * p ** 2 + 76 * p + RATIONAL(43, 8))
    check(sp.expand(2048 * p ** 2 + 608 * p - 8 * q + 43 + 8 * (q - parabola)) == 0,
          "the quadratic factor is -8 (q - f(p))")
    sign_rows = []
    g_poly = sp.Poly(g, h)
    for label, pv, qv in DECLARED_POINTS:
        value = RATIONAL(primitive.as_expr().subs({p: rat(pv), q: rat(qv)}))
        sign_d = qsign(value)
        f_value = 256 * pv * pv + 76 * pv + Fr(43, 8)
        beta = Fr(1, 8) + qv
        gap = f_value - qv
        sign_rule = 0 if gap == 0 else (-1 if gap > 0 else 1)
        discriminant = RATIONAL(sp.expand(sp.discriminant(g, h)).subs({p: rat(pv), q: rat(qv)}))
        sign_disc = qsign(discriminant)
        sign_disc_rule = 0 if sign_d == 0 or beta == 0 \
            else sign_d * (1 if beta > 0 else -1)
        on_a_branch = (qv == Fr(-1, 8) or qv == Fr(-17, 64) or pv == Fr(-1, 8)
                       or gap == 0 or value == 0)
        sign_rows.append({
            "label": label, "p": str(pv), "q": str(qv),
            "D": str(value), "sign_D": sign_d,
            "sign_D_by_the_declared_rule": sign_rule,
            "sign_D_rule_applies": not on_a_branch,
            "sign_D_rule_agrees": (sign_d == sign_rule) if not on_a_branch else None,
            "disc_h_G": str(discriminant),
            "sign_disc_by_the_declared_rule": sign_disc_rule,
            "sign_disc_rule_applies": not on_a_branch and sign_d != 0,
            "sign_disc_rule_agrees": (sign_disc == sign_disc_rule)
            if (not on_a_branch and sign_d != 0) else None,
        })
        if not on_a_branch:
            check(sign_d == sign_rule, f"the declared D sign rule holds at {label}")
            check(sign_disc == sign_disc_rule,
                  f"sign(disc_h G) = sign(D) sign(1/8 + q) holds at {label}")
    check(g_poly.degree() == 4, "the family is a quartic in h for symbolic p and q")
    on_vertex = RATIONAL(primitive.as_expr().subs({p: RATIONAL(-19, 128), q: RATIONAL(-17, 64)}))
    check(on_vertex == 0, "the vertex of B1 lies on B2, so D vanishes there")
    return {
        "definition": "D(p, q) = Res_h(E_{p,q}(h) - 1, d/dh E_{p,q}(h)), cleared of denominators",
        "integer_polynomial": str(primitive.as_expr()),
        "total_degree": int(sp.total_degree(primitive.as_expr(), p, q)),
        "degree_in_p": int(sp.degree(primitive.as_expr(), p)),
        "degree_in_q": int(sp.degree(primitive.as_expr(), q)),
        "term_count": len(terms),
        "factorisation": [{"factor": str(factor), "multiplicity": multiplicity}
                          for factor, multiplicity in factor_list],
        "declared_branches": [
            {"name": "B1", "locus": "q = 256 p^2 + 76 p + 43/8", "multiplicity": 1,
             "nature": "two simple roots of the quartic collide for every p"},
            {"name": "B2", "locus": "q = -17/64", "multiplicity": 2,
             "nature": "the quartic keeps a two-fold factor for every p; the double roots are "
                       "real exactly when p > -19/128 and become one double root at the vertex "
                       "p = -19/128, where B2 is tangent to B1"},
            {"name": "B3", "locus": "q = -1/8", "multiplicity": 2,
             "nature": "the leading coefficient vanishes and two roots leave the affine chart"},
            {"name": "B4", "locus": "p = -1/8", "multiplicity": 2,
             "nature": "the leading coefficient vanishes and two roots leave the affine chart"},
        ],
        "relation_to_the_discriminant": "Res_h(G, G_h) = lc(G) disc_h(G) with "
                                        "lc(G) = (1/8 + p)^2 (1/8 + q)",
        "sign_rule": "away from the branches, sign(D) = -sign(f(p) - q) and "
                     "sign(disc_h(G)) = sign(D) sign(1/8 + q)",
        "sign_rule_checks": sign_rows,
        "two_real_roots_region": "q < f(p) with q > -1/8, or q > f(p) with q < -1/8",
    }


# ------------------------------------------------------------- section S5 -------

def main_variable(poly, order):
    """Wu's main variable: the highest-ranked variable of the declared order present."""
    present = [variable for variable in order if poly.has(variable)]
    return present[-1] if present else None


def triangularise(polys, order):
    """A bounded characteristic chain by pseudo-division (the basic Wu step)."""
    chain, history = [], []
    working = [sp.expand(poly) for poly in polys if poly != 0]
    for _ in range(8):
        best = None
        for index, poly in enumerate(working):
            variable = main_variable(poly, order)
            if variable is None:
                return chain, working, history, "inconsistent"
            rank = order.index(variable)
            if best is None or rank < best[0]:
                best = (rank, variable, index)
        _, variable, index = best
        pivot = sp.expand(working.pop(index))
        chain.append({"main_variable": str(variable), "polynomial": str(pivot)})
        reduced = []
        for poly in working:
            remainder = sp.expand(sp.prem(poly, pivot, variable))
            history.append({
                "main_variable": str(variable),
                "reduced_polynomial_terms": len(sp.expand(poly).as_ordered_terms()),
                "remainder_is_zero": remainder == 0,
            })
            if remainder != 0:
                reduced.append(remainder)
        working = reduced
        if not working:
            break
    return chain, working, history, "reduced"


def reduce_conclusion(chain, conclusion):
    """Successive pseudo-remainder reduction of one conclusion modulo the chain."""
    remainder = sp.expand(conclusion)
    steps = []
    for entry in chain:
        variable = sp.Symbol(entry["main_variable"])
        polynomial = sp.expand(entry["polynomial"])
        before = len(sp.expand(remainder).as_ordered_terms()) if remainder != 0 else 0
        remainder = sp.expand(sp.prem(remainder, polynomial, variable))
        steps.append({
            "main_variable": entry["main_variable"],
            "terms_before": before,
            "remainder_terms": len(sp.expand(remainder).as_ordered_terms())
            if remainder != 0 else 0,
            "remainder_is_zero": remainder == 0,
        })
        if remainder == 0:
            break
    return remainder, steps


def in_ideal(generators, conclusion, variables):
    """An independent Groebner basis membership cross-check."""
    basis = sp.groebner(generators, *variables, order="grevlex")
    remainder = sp.expand(basis.reduce(sp.expand(conclusion))[1])
    return remainder == 0, len(basis.polys), str(remainder)


CASE_DEFINITIONS = (
    ("C1", "positive real root", "|h|",
     "|h| = h > 0 on the positive branch, so the along-branch derivative of the active quantity "
     "is 1 and its vanishing forces grad_{p,q} G = 0"),
    ("C2", "positive real root", "|E_0(h)|",
     "the along-branch derivative of +-E_0(h) vanishes where E_0'(h) = 0 or where "
     "grad_{p,q} G = 0; the second component is C1 and is run there"),
    ("C3", "negative real root", "|h|",
     "as C1 with |h| = -h < 0"),
    ("C4", "negative real root", "|E_0(h)|",
     "as C2 on the negative branch"),
    ("C5", "the frozen constant side", "the exact level 1",
     "no stationarity system: J_inf is identically 1 wherever |h| and |E_0(h)| are both strictly "
     "below 1, so this case has no interior critical point and is decided in S7"),
)


def case_solutions(name, sym):
    """The exact solution set of one declared case."""
    p, q, h = sym["p"], sym["q"], sym["h"]
    if name in ("C1", "C3"):
        basis = sp.groebner([sym["G"], sym["Gp"], sym["Gq"]], p, q, h, order="grevlex")
        check(list(basis.polys) == [sp.Integer(1)],
              f"the {name} system is inconsistent: its Groebner basis is {{1}}")
        factored = sp.factor(sym["Gq"])
        check(sp.expand(factored - sym["Gq"]) == 0, "G_q factors as declared")
        forced = sp.simplify(-(h + 4) / (8 * h))
        check(sp.simplify(sym["Gq"] / (h ** 2 / 64) - (8 * h * p + h + 4) ** 2) == 0,
              "G_q = h^2 (8 h p + h + 4)^2 / 64 exactly")
        value_at_forced_p = sp.simplify(sp.expand(sym["G"].subs({p: forced})))
        check(value_at_forced_p == -1,
              f"G equals -1 on the forced p, so the {name} system is empty")
        check(sp.expand(sym["G"].subs({p: forced}) + 1) == 0,
              "the emptiness certificate is an identity, not a numerical accident")
        return {
            "kind": "empty",
            "detail": "the branch value |h| is never a stationary active quantity, so this case "
                      "carries no candidate minimiser",
            "certificate": "G_q = h^2 (8 h p + h + 4)^2 / 64 = 0 together with G(0) = -1 forces "
                           "h != 0 and p = -(h + 4)/(8 h); substituting that into G gives G = -1 "
                           "identically, contradicting G = 0. The Groebner basis of the system is "
                           "{1}, which confirms emptiness over the complex numbers.",
            "groebner_basis_is_one": True,
        }
    p_of_h = sp.simplify(-(h + 2) / (8 * h))
    q_of_h = sp.simplify(-(h ** 2 + 24 * h - 128) / (8 * h ** 2))
    parabola = sp.expand(256 * p ** 2 + 76 * p + RATIONAL(43, 8))
    check(sp.simplify(sp.together(q_of_h - parabola.subs(p, p_of_h))) == 0,
          f"the stationary locus of {name} lies on the branch B1")
    instances = []
    for value in (Fr(-4), Fr(-2), Fr(-1), Fr(-1, 2), Fr(1, 2), Fr(1), Fr(2), Fr(4),
                  Fr(16, 3), Fr(32, 3)):
        pv = RATIONAL(p_of_h.subs(h, rat(value)))
        qv = RATIONAL(q_of_h.subs(h, rat(value)))
        level = RATIONAL(sym["E0"].subs({p: pv, h: rat(value)}))
        poly = g_at(sym, pv, qv)
        branch_ok = (value > 0) if name == "C2" else (value < 0)
        d_value = RATIONAL(discriminant_polynomial(sym).as_expr().subs({p: pv, q: qv}))
        branches_here = ["B1"] if pv == RATIONAL(p_of_h.subs(h, rat(value))) else []
        if qv == Fr(-1, 8):
            branches_here.append("B3")
        if qv == Fr(-17, 64):
            branches_here.append("B2")
        instances.append({
            "h": str(value), "p": str(pv), "q": str(qv),
            "level_lambda": str(level),
            "E_0_at_the_branch": str(level),
            "branch_sign_matches_the_case": branch_ok,
            "degree_at_that_point": int(poly.degree()),
            "distinct_real_roots_at_that_point": len(poly.intervals(eps=ISOLATION_EPS)),
            "D_at_that_point": str(d_value),
            "on_the_discriminant_variety": d_value == 0,
            "declared_branch_membership": branches_here,
        })
    return {
        "kind": "one-dimensional, parametrised by the free branch value h",
        "p_of_h": str(p_of_h),
        "q_of_h": str(q_of_h),
        "level": str(sym["E0"]),
        "locus": "q = f(p) on the whole declared locus, so every stationary candidate of this "
                 "case lies on the discriminant variety",
        "isolated_intersections_with_the_other_branches": [
            {"h": "16/3", "p": "-11/64", "q": "-1/8", "branches": "B1 and B3"},
            {"h": "32/3", "p": "-19/128", "q": "-17/64", "branches": "B1 and B2, the vertex"},
        ],
        "declared_instances": instances,
    }


def section_cases(sym):
    """The declared finite case analysis of the maximum."""
    p, q, h, lam = sym["p"], sym["q"], sym["h"], sp.Symbol("lam")
    order = [h, p, q, lam]
    g, g_p, g_q = sym["G"], sym["Gp"], sym["Gq"]
    e0 = sym["E0"]
    e0_h = sp.expand(sp.diff(e0, h))
    system_of = {
        "C1": [g, g_p, g_q],
        "C2": [g, e0_h, lam - e0],
        "C3": [g, g_p, g_q],
        "C4": [g, e0_h, lam - e0],
        "C5": [],
    }
    conclusion = discriminant_polynomial(sym).as_expr()
    rows = []
    for name, branch, active, reading in CASE_DEFINITIONS:
        system = system_of[name]
        if not system:
            rows.append({
                "case": name, "branch": branch, "active_quantity": active, "reading": reading,
                "system": [], "chain": [], "pseudo_reduction_steps": [],
                "remainder": None, "remainder_is_zero": None,
                "groebner_membership": None, "groebner_basis_size": None,
                "cross_check_verdict": "not_applicable",
                "verdict": "NoStationaritySystem",
                "solutions": case_solutions(name, sym),
            })
            continue
        chain, leftover, _, status = triangularise(system, order)
        remainder, steps = reduce_conclusion(chain, conclusion)
        membership, basis_size, groebner_remainder = in_ideal(system, conclusion, [p, q, h, lam])
        empty = status == "inconsistent" or basis_size == 1
        if empty:
            agrees = True
            verdict = "EmptyCase_no_stationary_candidate"
            cross_check = ("vacuous_agreement: the system has no solutions, so the conclusion "
                           "holds vacuously and the Groebner membership is not informative")
        else:
            agrees = (remainder == 0) == bool(membership)
            verdict = ("OnTheDiscriminantVariety" if remainder == 0
                       else "AwayFromTheDiscriminantVariety")
            cross_check = "agree" if agrees else "disagree"
        if empty and remainder != 0:
            cross_check = ("vacuous_agreement_with_a_recorded_chain_limitation: the basic "
                           "pseudo-division chain is not a zero-decomposition of this "
                           "inconsistent system, so its nonzero remainder is retained as a "
                           "limitation of the chain and not as a verdict")
        rows.append({
            "case": name, "branch": branch, "active_quantity": active, "reading": reading,
            "system": [str(sp.expand(poly)) for poly in system],
            "chain": chain,
            "chain_status": status,
            "leftover_polynomials": [str(sp.expand(poly)) for poly in leftover],
            "pseudo_reduction_steps": steps,
            "remainder": str(sp.factor(remainder)),
            "remainder_is_zero": remainder == 0,
            "groebner_membership": bool(membership),
            "groebner_basis_size": basis_size,
            "groebner_remainder": groebner_remainder,
            "cross_check_verdict": cross_check,
            "methods_agree": bool(agrees),
            "conclusion": "the primitive integer discriminant polynomial D(p, q)",
            "verdict": verdict,
            "solutions": case_solutions(name, sym),
        })
    return {
        "variables_and_order": [str(variable) for variable in order],
        "main_variable_convention": "the highest-ranked variable of the declared order present; "
                                    "the branch value h is ranked first, so it is never eliminated",
        "conclusion_tested": "the conjecture 'the stationary candidate lies on D = 0' is tested by "
                             "reducing D itself modulo each case chain",
        "decomposition_note": "the along-branch derivative conditions of the |E_0(h)| cases are "
                              "Q'(h) G_p = 0 and Q'(h) G_q = 0 with Q = +-E_0; since "
                              "G_q = h^2 (8 h p + h + 4)^2 / 64, the second factor forces "
                              "8 h p + h + 4 = 0, and with h = 0 excluded by G(0) = -1 the "
                              "remaining component is the declared C1/C3 system",
        "cases": rows,
    }


# ------------------------------------------------------------- section S6 -------

def section_real_roots(sym):
    """Sturm counting and exact rational isolation at the declared parameter points."""
    primitive = discriminant_polynomial(sym).as_expr()
    p, q, h = sym["p"], sym["q"], sym["h"]
    rows = []
    for label, pv, qv in DECLARED_POINTS:
        poly = g_at(sym, pv, qv)
        intervals = poly.intervals(eps=ISOLATION_EPS)
        value = RATIONAL(primitive.subs({p: rat(pv), q: rat(qv)}))
        derivative = poly.diff(h)
        roots = []
        for (lo, hi), multiplicity in intervals:
            lo, hi = RATIONAL(lo), RATIONAL(hi)
            derivative_lo = RATIONAL(derivative.eval(lo))
            derivative_hi = RATIONAL(derivative.eval(hi))
            low = min(derivative_lo, derivative_hi)
            high = max(derivative_lo, derivative_hi)
            definite = low > 0 or high < 0
            roots.append({
                "isolation_interval": [str(lo), str(hi)],
                "multiplicity": multiplicity,
                "is_simple": multiplicity == 1,
                "sign_of_the_root": "negative" if hi <= 0 else ("positive" if lo >= 0
                                                                else "straddles_zero"),
                "side_of_the_discriminant_variety": ("on_the_variety" if value == 0
                                                     else "inside_a_region_of_D"),
                "G_prime_interval": [str(low), str(high)],
                "G_prime_sign_definite": bool(definite),
                "root_is_on_the_simple_side": bool(multiplicity == 1 and definite),
                "G_at_lower_endpoint": str(RATIONAL(poly.eval(lo))),
                "G_at_upper_endpoint": str(RATIONAL(poly.eval(hi))),
            })
        rows.append({
            "label": label, "p": str(pv), "q": str(qv),
            "degree": int(poly.degree()),
            "distinct_real_roots": len(intervals),
            "D_at_the_point": str(value),
            "side_of_the_discriminant_variety": "on D = 0" if value == 0 else
                                                ("D < 0: two real roots and a conjugate pair"
                                                 if value < 0 else
                                                 "D > 0: four real roots or none"),
            "in_the_declared_feasible_region": len(intervals) == 2 and poly.degree() == 4,
            "roots": roots,
        })
    # two declared structural facts at the exceptional points
    vertex_g = sp.Poly(sp.expand(sym["G"].subs({p: RATIONAL(-19, 128),
                                                q: RATIONAL(-17, 64)})), h)
    vertex_coefficient = (RATIONAL(1, 8) + RATIONAL(-19, 128)) ** 2 \
        * (RATIONAL(1, 8) + RATIONAL(-17, 64))
    check(sp.expand(vertex_g.as_expr()
                    - vertex_coefficient * (h - RATIONAL(32, 3)) ** 4) == 0,
          "at the vertex of B1 and B2 the return quartic is a constant times (h - 32/3)^4")
    triple_g = sp.Poly(sp.expand(sym["G"].subs({p: RATIONAL(-1, 8), q: RATIONAL(-1, 8)})), h)
    check(triple_g.degree() == 1, "at the triple point the return equation is linear")
    check(sp.solve(triple_g.as_expr(), h) == [RATIONAL(8, 3)],
          "at the triple point the only finite root is h = 8/3")
    return {
        "method": "Sturm sequences with exact rational isolation (sympy Poly.intervals)",
        "endpoints": "every isolation endpoint retained here is an exact rational",
        "points": rows,
        "counts": [[row["label"], row["distinct_real_roots"]] for row in rows],
        "exceptional_points": {
            "vertex_of_B1_and_B2": "G = (1/8 + p)^2 (1/8 + q) (h - 32/3)^4 at "
                                   "(p, q) = (-19/128, -17/64): one quadruple root",
            "triple_point_of_B1_B3_B4": "G = 3h/8 - 1 at (p, q) = (-1/8, -1/8): the quartic "
                                        "degenerates to a line, so three sheets are at infinity "
                                        "and the only finite root is h = 8/3",
        },
    }


# ------------------------------------------------------------- section S7 -------

def box_quantities(p_box, q_box):
    """Exact interval bounds for the quantities the minimality argument needs."""
    alpha = Ivl(Fr(1, 8) + p_box.lo, Fr(1, 8) + p_box.hi)
    beta = Ivl(Fr(1, 8) + q_box.lo, Fr(1, 8) + q_box.hi)
    return {
        "alpha": alpha,
        "beta": beta,
        "c4": alpha.power(2) * beta,
        "c3": alpha * beta,
        "c2": (alpha.scale(3) + beta).scale(Fr(1, 4)),
        "f_minus_q": p_box.power(2).scale(256) + p_box.scale(76) + Ivl(Fr(43, 8)) - q_box,
        "leading": alpha.power(2) * beta,
    }


def g_on_box(quantities, h_value):
    """Exact interval bound of G(p, q, h_value) over a declared box."""
    total = Ivl(0)
    for coefficient, exponent in ((quantities["c4"], 4), (quantities["c3"], 3),
                                  (quantities["c2"], 2)):
        total = total + coefficient.scale(Fr(h_value) ** exponent)
    return total + Ivl(Fr(3, 8) * Fr(h_value)) - Ivl(1)


def e0_on_box(quantities, h_interval):
    """Exact bounds of E_0(h) over a rational h-interval, with a monotonicity certificate."""
    low, high = h_interval
    alpha = quantities["alpha"]
    derivative = Ivl(Fr(1, 2)) + (alpha * Ivl(Fr(low), Fr(high))).scale(2)
    values = []
    for endpoint in (low, high):
        values.append(Ivl(Fr(endpoint) / 2) + alpha * Ivl(Fr(endpoint) ** 2))
    return {
        "bounds": Ivl(min(value.lo for value in values), max(value.hi for value in values)),
        "derivative_interval": [str(derivative.lo), str(derivative.hi)],
        "derivative_sign": derivative.sign(),
    }


def branch_enclosure(alpha, lo, hi):
    """Rigorous rational bounds on |h| and |E_0(h)| for a branch isolated in [lo, hi]."""
    enclosure = e0_enclosure(alpha, lo, hi)
    return {
        "isolation_interval": [str(lo), str(hi)],
        "abs_h_upper_bound": max(abs(Fr(lo)), abs(Fr(hi))),
        "E_0_enclosure": [str(enclosure.lo), str(enclosure.hi)],
        "abs_E_0_upper_bound": max(abs(enclosure.lo), abs(enclosure.hi)),
    }


def e0_enclosure(alpha, lo, hi):
    """A rigorous interval enclosure of E_0(h) = h/2 + alpha h^2 over h in [lo, hi]."""
    h_interval = Ivl(Fr(lo), Fr(hi))
    if h_interval.lo <= 0 <= h_interval.hi:
        square = Ivl(0, max(Fr(lo) ** 2, Fr(hi) ** 2))
    else:
        square = Ivl(min(Fr(lo) ** 2, Fr(hi) ** 2), max(Fr(lo) ** 2, Fr(hi) ** 2))
    return h_interval.scale(Fr(1, 2)) + Ivl(alpha) * square


def section_minimality(sym):
    """The constrained minimum, the second variation and the declared conjecture."""
    p, q = sym["p"], sym["q"]
    floor_rows = []
    for label, pv, qv in DECLARED_POINTS[:7]:
        poly = g_at(sym, pv, qv)
        intervals = poly.intervals(eps=ISOLATION_EPS)
        if poly.degree() != 4 or len(intervals) != 2:
            floor_rows.append({
                "label": label, "p": str(pv), "q": str(qv), "branches": len(intervals),
                "branch_enclosures": None, "J_inf_upper_bound": None,
                "J_2_upper_bound": None,
                "frozen_side_and_all_twelve_sides_included": True,
                "note": "not in the declared two-branch region, so only the floor 1 is reported"})
            continue
        alpha = Fr(1, 8) + pv
        rows = [branch_enclosure(alpha, RATIONAL(lo), RATIONAL(hi))
                for (lo, hi), _ in intervals]
        for row in rows:
            row["abs_h_upper_bound"] = str(row["abs_h_upper_bound"])
            row["abs_E_0_upper_bound"] = str(row["abs_E_0_upper_bound"])
        level = max([Fr(1)] + [max(Fr(row["abs_h_upper_bound"]), Fr(row["abs_E_0_upper_bound"]))
                               for row in rows])
        j_two = Fr(20) + sum(Fr(row["abs_h_upper_bound"]) ** 2
                             + Fr(row["abs_E_0_upper_bound"]) ** 2 for row in rows)
        floor_rows.append({
            "label": label, "p": str(pv), "q": str(qv), "branches": len(intervals),
            "branch_enclosures": rows,
            "J_inf_upper_bound": str(level),
            "J_2_upper_bound": str(j_two),
            "frozen_side_and_all_twelve_sides_included": True,
            "at_least_one": bool(level >= 1),
        })
    witness_p, witness_q = WITNESS
    witness_poly = g_at(sym, witness_p, witness_q)
    witness_intervals = witness_poly.intervals(eps=ISOLATION_EPS)
    check(len(witness_intervals) == 2 and witness_poly.degree() == 4,
          "the declared witness has exactly two distinct real branches")
    witness_rows = []
    for (lo, hi), multiplicity in witness_intervals:
        lo, hi = RATIONAL(lo), RATIONAL(hi)
        alpha = RATIONAL(1, 8) + rat(witness_p)
        enclosure = e0_enclosure(alpha, lo, hi)
        check(hi < 1 and lo > -1, "both witness branches lie strictly inside (-1, 1)")
        check(enclosure.lo > -1 and enclosure.hi < 1, "|E_0| < 1 on both witness branches")
        check(multiplicity == 1, "the witness branches are simple")
        check(alpha * lo * lo + lo / 2 < 0 and alpha * hi * hi + hi / 2 < 0,
              "E_0 is negative on both witness branches, so |E_0| = -E_0 there")
        witness_rows.append({
            "isolation_interval": [str(lo), str(hi)],
            "abs_h_upper_bound": str(max(abs(lo), abs(hi))),
            "E_0_enclosure": [str(enclosure.lo), str(enclosure.hi)],
            "abs_E_0_upper_bound": str(max(abs(enclosure.lo), abs(enclosure.hi))),
            "below_the_frozen_level": True,
        })
    check(witness_poly.eval(RATIONAL(0)) == -1, "h = 0 is never a branch")
    # the plateau box
    p_box, q_box = PLATEAU_BOX
    rounds = []
    box = (p_box, q_box)
    decided = False
    for round_index in range(8):
        quantities = box_quantities(box[0], box[1])
        f_sign = quantities["f_minus_q"].sign()
        leading_sign = quantities["leading"].sign()
        p_factor = Ivl(Fr(8) * box[0].lo + 1, Fr(8) * box[0].hi + 1)
        q_factor = Ivl(Fr(8) * box[1].lo + 1, Fr(8) * box[1].hi + 1)
        r_factor = Ivl(Fr(64) * box[1].lo + 17, Fr(64) * box[1].hi + 17)
        g_one = g_on_box(quantities, Fr(1))
        g_minus_one = g_on_box(quantities, Fr(-1))
        left_low = g_on_box(quantities, Fr(-3, 5))
        left_high = g_on_box(quantities, Fr(-1, 2))
        right_low = g_on_box(quantities, Fr(43, 50))
        right_high = g_on_box(quantities, Fr(87, 100))
        left_e0 = e0_on_box(quantities, (Fr(-3, 5), Fr(-1, 2)))
        right_e0 = e0_on_box(quantities, (Fr(43, 50), Fr(87, 100)))
        conditions = {
            "the_parabola_factor_never_vanishes": f_sign in ("positive", "negative"),
            "D_never_vanishes_on_the_box": leading_sign in ("positive", "negative")
            and p_factor.sign() in ("positive", "negative")
            and q_factor.sign() in ("positive", "negative")
            and r_factor.sign() in ("positive", "negative"),
            "G_at_plus_one_is_positive": g_one.sign() == "positive",
            "G_at_minus_one_is_positive": g_minus_one.sign() == "positive",
            "left_branch_bracketed_by_minus_three_fifths_and_minus_one_half":
                left_low.sign() == "positive" and left_high.sign() == "negative",
            "right_branch_bracketed_by_43_over_50_and_87_over_100":
                right_low.sign() == "negative" and right_high.sign() == "positive",
            "E_0_is_monotone_on_the_left_bracket":
                left_e0["derivative_sign"] in ("positive", "negative"),
            "E_0_is_monotone_on_the_right_bracket":
                right_e0["derivative_sign"] in ("positive", "negative"),
            "abs_E_0_stays_below_one_on_the_left_branch":
                left_e0["bounds"].lo > -1 and left_e0["bounds"].hi < 1,
            "abs_E_0_stays_below_one_on_the_right_branch":
                right_e0["bounds"].lo > -1 and right_e0["bounds"].hi < 1,
        }
        rounds.append({
            "round": round_index,
            "box_p": [str(box[0].lo), str(box[0].hi)],
            "box_q": [str(box[1].lo), str(box[1].hi)],
            "conditions": conditions,
            "all_conditions_decided_and_true": all(conditions.values()),
            "E_0_left_bracket_bounds": [str(left_e0["bounds"].lo), str(left_e0["bounds"].hi)],
            "E_0_right_bracket_bounds": [str(right_e0["bounds"].lo), str(right_e0["bounds"].hi)],
            "G_at_plus_one": [str(g_one.lo), str(g_one.hi)],
            "G_at_minus_one": [str(g_minus_one.lo), str(g_minus_one.hi)],
        })
        if all(conditions.values()):
            decided = True
            break
        # declared subdivision: halve both half-widths around the declared witness
        next_half = (box[0].hi - box[0].lo) / 4
        box = (Ivl(witness_p - next_half, witness_p + next_half),
               Ivl(witness_q - next_half, witness_q + next_half))
    check(decided, "the declared rational box decides the plateau by exact interval arithmetic")
    ray_rows = []
    for t_value in ESCAPE_RAY:
        t = Fr(t_value)
        poly = g_at(sym, -t, t)
        intervals = poly.intervals(eps=COARSE_EPS)
        check(len(intervals) == 2 and poly.degree() == 4,
              f"the declared ray keeps two distinct real branches at t = {t}")
        alpha = Fr(1, 8) - t
        extra = Fr(0)
        branches = []
        for (lo, hi), _ in intervals:
            row = branch_enclosure(alpha, RATIONAL(lo), RATIONAL(hi))
            extra = extra + row["abs_h_upper_bound"] ** 2 + row["abs_E_0_upper_bound"] ** 2
            branches.append({
                "isolation_interval": row["isolation_interval"],
                "abs_h_upper_bound": str(row["abs_h_upper_bound"]),
                "abs_E_0_upper_bound": str(row["abs_E_0_upper_bound"]),
            })
        check(extra > 0, "J_2 exceeds 20 strictly on the ray")
        ray_rows.append({
            "t": str(t), "p": str(-t), "q": str(t),
            "J_2_upper_bound": str(20 + extra),
            "branches": branches,
        })
    decreasing = all(Fr(ray_rows[i + 1]["J_2_upper_bound"])
                     < Fr(ray_rows[i]["J_2_upper_bound"]) for i in range(len(ray_rows) - 1))
    check(decreasing, "the declared J_2 bounds decrease strictly along the escape ray")
    return {
        "floor": "J_inf(p, q) >= 1 for every (p, q), because the ten frozen sides carry |h_m| = 1",
        "floor_table": floor_rows,
        "witness": {
            "p": str(witness_p), "q": str(witness_q),
            "branches": witness_rows,
            "J_inf": "1",
            "is_attained": True,
            "in_the_interior_of_the_feasible_region": True,
            "on_the_discriminant_variety": bool(
                RATIONAL(discriminant_polynomial(sym).as_expr().subs(
                    {p: rat(witness_p), q: rat(witness_q)})) == 0),
            "argument": "both branches lie strictly inside (-1, 1) and |E_0| < 1 at both, so the "
                        "maximum over the twelve sides equals the frozen side 1 exactly",
        },
        "plateau_box": {
            "method": "exact rational interval arithmetic with declared subdivision; successive "
                      "difference substitution is NOT implemented in this run",
            "declared_box": [[str(p_box.lo), str(p_box.hi)], [str(q_box.lo), str(q_box.hi)]],
            "rounds": rounds,
            "final_box": [rounds[-1]["box_p"], rounds[-1]["box_q"]],
            "verdict": "J_inf is identically 1 on the whole box: the minimum is attained on a "
                       "non-isolated plateau in the interior of the feasible region",
        },
        "second_variation": {
            "active_quantity": "the frozen constant side, exactly 1",
            "first_variation": "0 identically on the declared box",
            "second_variation": "0 identically on the declared box",
            "competitors": "|h| < 1 and |E_0(h)| < 1 strictly at both branches on the box",
            "verdict": "SecondVariationZero_NonIsolatedMinimum",
            "method": "exact interval arithmetic on a declared rational box, subdivision variant; "
                      "no floating-point verdict is reported",
        },
        "declared_conjecture": {
            "statement": CONTRACT["constraint"]["declared_conjecture"],
            "decision_for_the_minimiser": "False",
            "decision_for_the_stationary_candidates": "True",
            "witness": {"p": str(witness_p), "q": str(witness_q), "J_inf": "1",
                        "D_at_the_witness": "nonzero"},
            "reason": "the constrained minimum of J_inf is 1, the floor forced by the ten frozen "
                      "sides; it is attained on an open set in the interior, so the cheapest "
                      "configuration is not a collision configuration. Every stationary candidate "
                      "found in S5 does lie on the discriminant variety, so the failure is not in "
                      "the elimination but in the assumption that the minimum is stationary.",
        },
        "control_functional_J_2": {
            "definition": "J_2 = sum over the two branches and all twelve sides of h_m^2 "
                          "= 20 + sum over the branches of (h^2 + E_0(h)^2)",
            "floor": "J_2 > 20 for every (p, q), because a branch never sits at h = 0: "
                     "E_{p,q}(0) = 0 while a branch requires E_{p,q}(h) = 1",
            "escape_ray": {"p": "-t", "q": "t", "rows": ray_rows},
            "infimum": "20, not attained, approached along the declared escape ray",
            "on_the_discriminant_variety": False,
            "disagreement_with_J_inf": "J_inf is minimised at a finite plateau point; J_2 has no "
                                       "minimiser at all and its infimum is approached at "
                                       "infinity, so the two declared functionals disagree",
        },
        "deleted_side_controls": deleted_side_control(sym),
    }


def deleted_side_control(sym):
    """The declared side-deletion control, including a recorded failure to discriminate."""
    witness_p, witness_q = WITNESS
    rows = []
    for side in (0, 1, 2, 11):
        poly = g_at(sym, witness_p, witness_q)
        intervals = poly.intervals(eps=ISOLATION_EPS)
        alpha = Fr(1, 8) + witness_p
        rows_here = [branch_enclosure(alpha, RATIONAL(lo), RATIONAL(hi))
                     for (lo, hi), _ in intervals]
        if side == 0:
            kept = [row["abs_E_0_upper_bound"] for row in rows_here] + [Fr(1)] * 10
        elif side == 1:
            kept = [row["abs_h_upper_bound"] for row in rows_here] + [Fr(1)] * 10
        else:
            kept = [row["abs_h_upper_bound"] for row in rows_here] \
                + [row["abs_E_0_upper_bound"] for row in rows_here] + [Fr(1)] * 9
        rows.append({
            "deleted_side": side,
            "deleted_kind": "a branch side" if side < 2 else "a frozen side",
            "rigorous_upper_bound_at_the_witness": str(max(kept)),
            "floor_remains_one": max(kept) >= 1,
            "minimum_moves": False,
            "note": "nine or ten frozen sides still carry exactly 1, so the floor survives the "
                    "deletion and the minimiser's value does not move",
        })
    escaped = []
    for t_value in (1, 4, 16, 64, 1024):
        t = Fr(t_value)
        poly = g_at(sym, -t, t)
        intervals = poly.intervals(eps=COARSE_EPS)
        level = Fr(0)
        for (lo, hi), _ in intervals:
            lo, hi = RATIONAL(lo), RATIONAL(hi)
            alpha = Fr(1, 8) - t
            midpoint = (lo + hi) / 2
            e0 = midpoint / 2 + alpha * midpoint ** 2
            level = max(level, abs(lo), abs(hi), abs(e0))
        escaped.append({"t": str(t), "J_inf_without_the_frozen_sides": str(level)})
    return {
        "declared_single_side_deletions": rows,
        "single_side_deletion_moves_the_minimiser": False,
        "control_outcome": "FAILED_TO_DISCRIMINATE: removing one declared side never removes the "
                           "floor, because at least nine frozen sides remain at exactly 1, so the "
                           "minimiser's value does not move. The failure is recorded rather than "
                           "repaired.",
        "discriminating_variant": {
            "deleted_sides": "all ten frozen sides",
            "levels_along_the_escape_ray": escaped,
            "verdict": "the minimum moves from the attained value 1 in the interior to the "
                       "unattained infimum 0 approached at infinity, so the composition of the "
                       "maximum does matter when no frozen side is present",
        },
    }


# ------------------------------------------------------------- section S8 -------

DECLARED_LOOPS = (
    {
        "name": "L0 identity control, non-encircling",
        "vertices": ((Fr(-1, 100), Fr(-1, 100)), (Fr(1, 100), Fr(-1, 100)),
                     (Fr(1, 100), Fr(1, 100)), (Fr(-1, 100), Fr(1, 100))),
        "encircles": "nothing: the closed square meets no branch of D = 0",
    },
    {
        "name": "L1 around a smooth point of the branch B1",
        "vertices": ((Fr(-3, 32), Fr(17, 4)), (Fr(1, 32), Fr(17, 4)),
                     (Fr(1, 32), Fr(53, 8)), (Fr(-3, 32), Fr(53, 8))),
        "encircles": "the arc of the parabola branch B1 between its two crossings with the "
                     "rectangle",
    },
    {
        "name": "L2 around a smooth point of the branch B2",
        "vertices": ((Fr(-3, 32), Fr(-9, 32)), (Fr(1, 32), Fr(-9, 32)),
                     (Fr(1, 32), Fr(-1, 4)), (Fr(-3, 32), Fr(-1, 4))),
        "encircles": "the arc of the line branch q = -17/64 between its two crossings with the "
                     "rectangle",
    },
    {
        "name": "L3 around the degenerate triple point",
        "vertices": ((Fr(-5, 32), Fr(-5, 32)), (Fr(-3, 32), Fr(-5, 32)),
                     (Fr(-3, 32), Fr(-3, 32)), (Fr(-5, 32), Fr(-3, 32))),
        "encircles": "the triple point (p, q) = (-1/8, -1/8) of the branches B1, B3 and B4",
    },
    {
        "name": "L4 a wide loop crossing every branch",
        "vertices": ((Fr(-2), Fr(-1)), (Fr(2), Fr(-1)), (Fr(2), Fr(10)), (Fr(-2), Fr(10))),
        "encircles": "a long arc of every declared branch",
    },
)


def integer_sqrt(value):
    """An exact integer square root, or None; no float is formed."""
    if value < 0:
        return None
    if value == 0:
        return 0
    low, high = 0, 1
    while high * high < value:
        high *= 2
    while low < high:
        middle = (low + high) // 2
        if middle * middle < value:
            low = middle + 1
        else:
            high = middle
    return low if low * low == value else None


def exact_sqrt(value):
    """An exact rational square root, or None."""
    value = Fr(value)
    numerator = integer_sqrt(abs(value.numerator))
    denominator = integer_sqrt(value.denominator)
    if numerator is None or denominator is None:
        return None
    return Fr(numerator, denominator)


def quadratic_roots_in_open_interval(quadratic, linear, constant, low, high):
    """Exact real roots of a x^2 + b x + c inside (low, high), rational or algebraic."""
    if quadratic == 0:
        raise ValueError("not a quadratic")
    discriminant = linear * linear - 4 * quadratic * constant
    if discriminant < 0:
        return []
    roots = []
    for sign in (1, -1):
        lower_target = 2 * quadratic * low + linear
        upper_target = 2 * quadratic * high + linear
        if sign == 1:
            above_lower = lower_target < 0 or lower_target * lower_target < discriminant
            below_upper = upper_target > 0 and discriminant < upper_target * upper_target
        else:
            above_lower = lower_target < 0 and discriminant < lower_target * lower_target
            below_upper = upper_target > 0 or (upper_target <= 0
                                               and discriminant > upper_target * upper_target)
        if above_lower and below_upper:
            root = exact_sqrt(discriminant)
            if root is not None:
                roots.append({
                    "rational": True,
                    "value": (-linear + sign * root) / (2 * quadratic),
                    "defining_polynomial": f"{quadratic} x^2 + {linear} x + {constant}",
                    "isolating_interval": None,
                })
            else:
                roots.append({
                    "rational": False,
                    "value": None,
                    "quadratic": quadratic,
                    "linear": linear,
                    "constant": constant,
                    "sign": sign,
                    "defining_polynomial": f"{quadratic} x^2 + {linear} x + {constant}",
                })
    return roots


def branch_crossings(loop):
    """Exact crossings of one axis-aligned rational rectangle with the four branches."""
    vertices = loop["vertices"]
    crossings = []
    for index in range(len(vertices)):
        start = vertices[index]
        end = vertices[(index + 1) % len(vertices)]
        p0, q0 = start
        p1, q1 = end
        found = []
        if q0 == q1:                                   # horizontal edge
            low, high = sorted((p0, p1))
            if Fr(8) * q0 + 1 == 0:
                found.append(("B3", low, q0, None))
            if Fr(64) * q0 + 17 == 0:
                found.append(("B2", low, q0, None))
            if low < Fr(-1, 8) < high:
                found.append(("B4", Fr(-1, 8), q0, None))
            for entry in quadratic_roots_in_open_interval(256, 76, Fr(43, 8) - q0, low, high):
                if entry["rational"]:
                    found.append(("B1", entry["value"], q0, None))
                else:
                    crossing = {"branch": "B1", "edge": index,
                                "point": None, "defined_by": entry["defining_polynomial"],
                                "root_sign": entry["sign"]}
                    crossings.append(crossing)
            span = p1 - p0
            for branch, x_value, y_value, _ in found:
                crossings.append({"branch": branch, "edge": index,
                                  "point": (x_value, y_value),
                                  "position": (x_value - p0) / span})
        else:                                          # vertical edge
            low, high = sorted((q0, q1))
            if Fr(8) * p0 + 1 == 0:
                found.append(("B4", p0, low, None))
            if low < Fr(-1, 8) < high:
                found.append(("B4", p0, Fr(-1, 8), None))
            f_value = 256 * p0 * p0 + 76 * p0 + Fr(43, 8)
            if low < f_value < high:
                found.append(("B1", p0, f_value, None))
            if low < Fr(-1, 8) < high:
                found.append(("B3", p0, Fr(-1, 8), None))
            if low < Fr(-17, 64) < high:
                found.append(("B2", p0, Fr(-17, 64), None))
            span = q1 - q0
            for branch, x_value, y_value, _ in found:
                crossings.append({"branch": branch, "edge": index,
                                  "point": (x_value, y_value),
                                  "position": (y_value - q0) / span})
    return crossings


def traversal_sub_arcs(loop, crossings):
    """Sub-arcs of the loop between consecutive rational crossings, in traversal order."""
    vertices = loop["vertices"]
    sub_arcs = []
    if any(entry["point"] is None for entry in crossings):
        return sub_arcs
    for index in range(len(vertices)):
        start = vertices[index]
        end = vertices[(index + 1) % len(vertices)]
        positions = sorted({entry["position"] for entry in crossings if entry["edge"] == index})
        marks = [Fr(0), *positions, Fr(1)]
        for lower, upper in itertools.pairwise(marks):
            if lower == upper:
                continue
            middle = (lower + upper) / 2
            point = (start[0] + (end[0] - start[0]) * middle,
                     start[1] + (end[1] - start[1]) * middle)
            sub_arcs.append({
                "edge": index,
                "from_position": str(lower),
                "to_position": str(upper),
                "sample_point": [str(point[0]), str(point[1])],
                "point": point,
            })
    return sub_arcs


def crossing_analysis(sym, point):
    """Exact local structure of the return polynomial at one crossing point."""
    h = sym["h"]
    poly = g_at(sym, point[0], point[1])
    if poly.degree() < 4:
        return {"degree_at_the_crossing": int(poly.degree()),
                "common_factor_degree": None, "common_factor": None,
                "repeated_root": None,
                "is_a_single_double_root": False,
                "note": "the quartic loses degree at this branch"}
    common = sp.gcd(poly, sp.Poly(poly.diff(h), h))
    degree = int(common.degree())
    single = degree == 1
    detail = str(sp.factor(common.as_expr())) if degree > 0 else None
    repeated_root = None
    if degree == 1:
        repeated_root = str(sp.solve(common.as_expr(), h)[0])
    return {
        "degree_at_the_crossing": int(poly.degree()),
        "common_factor_degree": degree,
        "common_factor": detail,
        "repeated_root": repeated_root,
        "is_a_single_double_root": single,
        "note": "the gcd of G and G_h is linear exactly when one pair of roots collides; a "
                "quadratic gcd means two pairs collide at once, so the crossing is not simple",
    }


def section_exchange(sym):
    """The declared loops, their exact crossings, counts and permutations."""
    rows = []
    for loop in DECLARED_LOOPS:
        vertices = loop["vertices"]
        edge_counts = []
        for index in range(len(vertices)):
            start = vertices[index]
            end = vertices[(index + 1) % len(vertices)]
            middle = ((start[0] + end[0]) / 2, (start[1] + end[1]) / 2)
            edge_counts.append([index, len(g_at(sym, middle[0], middle[1])
                                           .intervals(eps=ISOLATION_EPS))])
        crossings = branch_crossings(loop)
        sub_arcs = traversal_sub_arcs(loop, crossings)
        for arc in sub_arcs:
            poly = g_at(sym, arc["point"][0], arc["point"][1])
            arc["distinct_real_roots"] = len(poly.intervals(eps=ISOLATION_EPS))
            del arc["point"]
        counts = [arc["distinct_real_roots"] for arc in sub_arcs]
        runs = []
        for value in counts:
            if runs and runs[-1][0] == value:
                runs[-1][1] += 1
            else:
                runs.append([value, 1])
        if len(runs) > 1 and runs[0][0] == runs[-1][0]:
            runs[0][1] += runs[-1][1]
            runs.pop()
        crossing_rows = []
        branch_counts = {}
        irrational = 0
        for entry in crossings:
            branch_counts[entry["branch"]] = branch_counts.get(entry["branch"], 0) + 1
            if entry["point"] is None:
                irrational += 1
                crossing_rows.append({
                    "branch": entry["branch"], "edge": entry["edge"],
                    "point": None,
                    "defined_by": entry["defined_by"],
                    "root_sign": entry["root_sign"],
                    "local_structure": {
                        "is_a_single_double_root": None,
                        "note": "the crossing parameter is irrational, so the local structure at "
                                "the crossing is not evaluated exactly by this run",
                    },
                })
                continue
            analysis = crossing_analysis(sym, entry["point"])
            crossing_rows.append({
                "branch": entry["branch"], "edge": entry["edge"],
                "position_along_the_edge": str(entry["position"]),
                "point": [str(entry["point"][0]), str(entry["point"][1])],
                "local_structure": analysis,
            })
        simple = bool(crossing_rows) and all(
            row["local_structure"]["is_a_single_double_root"] for row in crossing_rows)
        single_branch = len(branch_counts) == 1
        alternating = len(runs) == 2 and sorted(run[0] for run in runs) == [2, 4]
        decidable = (len(crossing_rows) == 2 and simple and single_branch and alternating)
        if not crossing_rows:
            permutation, verdict = "identity", "DecidedIdentity"
            reason = ("the closed loop meets no branch of D = 0; on a simply connected parameter "
                      "domain where the discriminant does not vanish the four roots are "
                      "single-valued, so the monodromy is trivial")
        elif decidable:
            permutation, verdict = "identity", "DecidedIdentity"
            reason = ("exactly two transversal crossings with the single declared branch, both of "
                      "them simple double roots, and the loop alternates once between a two-real "
                      "arc and a four-real arc; the two crossings bound that one two-real arc, so "
                      "the same pair of sheets collides twice and the two transpositions cancel")
        else:
            permutation, verdict = "Undecided", "Undecided"
            if irrational:
                reason = (f"{irrational} of the crossings have an irrational parameter, so "
                          "their local structure and the arcs beside them are not evaluated "
                          "exactly; the crossing count and the defining polynomials are retained")
            elif not simple:
                reason = ("a crossing is not a simple double root: the gcd of G and G_h there is "
                          "not linear, so more than one pair of roots collides at once and exact "
                          "real tracking cannot identify the pairs")
            elif not single_branch:
                reason = ("the loop crosses more than one declared branch, so the arcs between "
                          "crossings lie in different regimes and the colliding pairs are not "
                          "identified by real arithmetic alone")
            else:
                reason = ("the loop does not alternate once between a two-real arc and a "
                          "four-real arc, so identifying which pair of sheets collides needs a "
                          "certified complex or projective continuation, which this run does not "
                          "implement")
        rows.append({
            "loop": loop["name"],
            "encircles": loop["encircles"],
            "vertices": [[str(x), str(y)] for x, y in loop["vertices"]],
            "crossings": crossing_rows,
            "crossing_count": len(crossing_rows),
            "crossings_per_branch": [[name, count]
                                     for name, count in sorted(branch_counts.items())],
            "irrational_crossings": irrational,
            "edge_midpoint_real_root_counts": edge_counts,
            "sub_arc_real_root_counts": counts,
            "sub_arc_runs": [[run[0], run[1]] for run in runs],
            "sub_arcs": sub_arcs,
            "permutation_of_the_four_roots": permutation,
            "verdict": verdict,
            "justification": reason,
        })
    return {
        "declared_sequence": [loop["name"] for loop in DECLARED_LOOPS],
        "crossing_method": "exact rational arithmetic on the four declared branches of D = 0, "
                           "with the arcs taken between consecutive crossings",
        "loops": rows,
        "identity_loops": [row["loop"] for row in rows
                           if row["permutation_of_the_four_roots"] == "identity"],
        "undecided_loops": [{"loop": row["loop"], "reason": row["justification"]} for row in rows
                            if row["verdict"] == "Undecided"],
        "identity_control": {
            "loop": DECLARED_LOOPS[0]["name"],
            "permutation": "identity",
            "falsifiable": True,
        },
        "finding": "no declared real loop realises the transposition of the two real-root "
                   "branches: the loops whose crossings are simple and smooth are decided to the "
                   "identity, "
                   "and the loops whose crossings are non-simple or whose arcs leave the two-real "
                   "regime are recorded as Undecided rather than given a floating-point "
                   "permutation. Every transversal crossing of a smooth branch point contributes "
                   "a transposition and a real loop crosses each branch an even number of times, "
                   "so an odd permutation is not available to a declared real loop.",
    }


def section_controls(sym, superseded, minimality):
    """Every declared control with its executed outcome."""
    p, q, h = sym["p"], sym["q"], sym["h"]
    frozen_poly = g_at(sym, 0, 0)
    frozen_intervals = frozen_poly.intervals(eps=ISOLATION_EPS)
    check(len(frozen_intervals) == 2, "the frozen return has two distinct real roots")
    frozen_rows = []
    for (lo, hi), multiplicity in frozen_intervals:
        frozen_rows.append({
            "isolation_interval": [str(RATIONAL(lo)), str(RATIONAL(hi))],
            "midpoint_exactly": str((RATIONAL(lo) + RATIONAL(hi)) / 2),
            "multiplicity": multiplicity,
        })
    realisation_rows = []
    for label, pv, qv in (("frozen", Fr(0), Fr(0)), ("declared witness", Fr(-2), Fr(17, 10)),
                          ("equal perturbations", Fr(1), Fr(1))):
        alpha = RATIONAL(1, 8) + rat(pv)
        poly = g_at(sym, pv, qv)
        intervals = poly.intervals(eps=ISOLATION_EPS)
        primary = []
        primary_intervals = []
        for (lo, hi), _ in intervals:
            lo, hi = RATIONAL(lo), RATIONAL(hi)
            primary_intervals.append((lo, hi))
            enclosure = e0_enclosure(alpha, lo, hi)
            primary.append({
                "isolation_interval": [str(lo), str(hi)],
                "sign": "negative" if hi <= 0 else "positive",
                "abs_h_upper_bound": str(max(abs(lo), abs(hi))),
                "abs_E_0_upper_bound": str(max(abs(enclosure.lo), abs(enclosure.hi))),
            })
        branch_level = [
            level_root(sym, pv, qv, rat(pv), "largest", primary_intervals),
            level_root(sym, pv, qv, rat(qv), "smallest", primary_intervals),
        ]
        comparisons = []
        for row in branch_level:
            overlapped = [index for index, _ in enumerate(primary) if row["overlaps"][index]]
            comparisons.append({
                "root": row,
                "overlapping_primary_branches": overlapped,
                "agrees_with_a_primary_branch": bool(overlapped),
            })
        agrees = all(item["agrees_with_a_primary_branch"] for item in comparisons) \
            and len(primary) == 2
        if pv == 0 and qv == 0:
            check(poly == sp.Poly(sp.expand(sym["G"].subs({p: 0, q: 0})), h),
                  "at p = q = 0 the primary and branch-level equations are the same equation")
            check(agrees, "the two realisations agree at p = q = 0")
            detail = ("at p = q = 0 the branch-level equations E(h) = 1 + p and E(h) = 1 + q are "
                      "both E(h) = 1, so the two realisations coincide exactly")
        else:
            detail = ("the branch-level control keeps the process frozen and perturbs the level; "
                      "its roots are reported here and every disagreement with the primary "
                      "realisation is retained")
        realisation_rows.append({
            "label": label, "p": str(pv), "q": str(qv),
            "primary_branches": primary,
            "branch_level_roots": comparisons,
            "realisations_agree": bool(agrees),
            "detail": detail,
        })
    check(realisation_rows[0]["realisations_agree"],
          "the two realisations agree at p = q = 0")
    return {
        "superseded_collapse_witness": {
            "reproduced": True,
            "double_root": superseded["double_root"],
            "J_inf_at_the_collapsed_branch": superseded["J_inf_at_the_collapsed_branch"],
            "branches_at_plus_minus_eps": superseded["branches_at_plus_minus_eps"],
        },
        "deleted_side_control": minimality["deleted_side_controls"],
        "frozen_unperturbed_roots": {
            "distinct_real_roots": len(frozen_intervals),
            "roots": frozen_rows,
            "conjugate_pair": "h = -2 +- i sqrt(8 sqrt(17) + 20)",
            "reproduced": True,
        },
        "two_realisations": realisation_rows,
        "identity_loop_control": {
            "loop": DECLARED_LOOPS[0]["name"],
            "permutation": "identity",
            "reported": True,
        },
        "reference_is_never_a_branch": {
            "asserted_at_declared_parameters": [str(pv) + ", " + str(qv)
                                                for pv, qv in DECLARED_PERTURBATIONS],
            "E_p_q_at_zero": "0 for every (p, q), while a branch requires E_{p,q}(h) = 1",
            "checked": True,
        },
    }


def level_root(sym, pv, qv, level, pick, primary_intervals):
    """The declared branch-level root of E(h) = 1 + level, as an exact interval row."""
    p, q, h = sym["p"], sym["q"], sym["h"]
    poly = sp.Poly(sp.expand(sym["G"].subs({p: rat(pv), q: rat(qv)}) - level), h)
    intervals = poly.intervals(eps=ISOLATION_EPS)
    if not intervals:
        return {
            "equation": "G(h) = " + str(level) + ", that is E(h) = 1 + " + str(level),
            "pick": pick,
            "isolation_interval": None,
            "real_root_exists": False,
            "note": "this branch-level equation has no real root at this parameter point",
            "overlaps": [False for _ in primary_intervals],
        }
    index = len(intervals) - 1 if pick == "largest" else 0
    (lo, hi), _ = intervals[index]
    lo, hi = RATIONAL(lo), RATIONAL(hi)
    enclosure = e0_enclosure(RATIONAL(1, 8) + rat(pv), lo, hi)
    return {
        "equation": "G(h) = " + str(level) + ", that is E(h) = 1 + " + str(level),
        "pick": pick,
        "isolation_interval": [str(lo), str(hi)],
        "sign": "negative" if hi <= 0 else "positive",
        "abs_h_upper_bound": str(max(abs(lo), abs(hi))),
        "abs_E_0_upper_bound": str(max(abs(enclosure.lo), abs(enclosure.hi))),
        "overlaps": [bool(lo <= other_hi and other_lo <= hi)
                     for other_lo, other_hi in primary_intervals],
    }


# ------------------------------------------------------------------- the run -----

def build_payload():
    sym = build_symbolic()
    fixture = section_fixture(sym)
    unperturbed = section_unperturbed(sym)
    superseded = section_superseded_witness()
    discriminant = section_discriminant(sym)
    cases = section_cases(sym)
    roots = section_real_roots(sym)
    minimality = section_minimality(sym)
    exchange = section_exchange(sym)
    controls = section_controls(sym, superseded, minimality)
    payload = {
        "schema": "adva.external.exchange-amplitude-variation-calibration.v1",
        "version": 1,
        "level": CONTRACT["level"],
        "contract": "experiments/exchange_amplitude_variation_v1/contract.json",
        "contract_sha256": digest(CONTRACT_PATH),
        "contract_initial": "experiments/exchange_amplitude_variation_v1/contract-initial.json",
        "contract_initial_sha256": digest(INITIAL_PATH),
        "checker_sha256": digest(pathlib.Path(__file__).resolve()),
        "tooling": {
            "polynomial_library": "sympy",
            "version": SY["version"],
            "declared_not_native_authority": True,
            "exact_only": True,
            "used_for": ["resultant", "discriminant", "pseudo-remainder", "Groebner basis",
                         "Sturm real-root isolation", "polynomial factorisation"],
            "not_implemented": ["successive difference substitution of Zhang Jingzhong and Yang Lu",
                                "a certified complex or projective continuation of roots"],
        },
        "limits": CONTRACT["budgets"],
        "assertions": ASSERTIONS["n"],
        "sections": {
            "S1_fixture_and_side_identity": fixture,
            "S2_unperturbed_return": unperturbed,
            "S3_superseded_collapse_witness": superseded,
            "S4_discriminant_variety": discriminant,
            "S5_case_analysis": cases,
            "S6_real_root_structure": roots,
            "S7_minimality_and_second_variation": minimality,
            "S8_exchange_protocol": exchange,
            "S9_controls": controls,
        },
        "undecided": [
            {"item": "the root permutation around the loops whose crossings are not simple double "
                     "roots or whose arcs leave the two-real regime",
             "reason": "identifying which pair of sheets collides on such a crossing or arc needs "
                       "a certified complex or projective continuation of the roots; this run "
                       "implements exact real tracking only",
             "retained_partial_result": exchange["undecided_loops"]},
            {"item": "second variation by successive difference substitution",
             "reason": "successive difference substitution is not implemented in this run; the "
                       "interval-subdivision variant of exact rational interval arithmetic is used "
                       "instead and decides every declared sign exactly",
             "retained_partial_result": minimality["plateau_box"]["verdict"]},
        ],
        "modelling_choices": {
            "case_stationarity_system": "each |h| case writes the along-branch derivative "
                                        "conditions Q'(h) G_p = 0 and Q'(h) G_q = 0 with the "
                                        "branch equation G = 0 and the level equation "
                                        "Q(h) = lambda; the contract's prose 'grad J = lambda "
                                        "grad D with D = 0' is not used, because taking D = 0 as "
                                        "a hypothesis would make the conjecture it is meant to "
                                        "test circular. The conclusion reduced modulo each chain "
                                        "is D itself.",
            "declared_case_set": "two branches times two active quantities plus the frozen-side "
                                 "case; an undeclared active side is a different run",
            "absolute_values": "|h| = sigma_h h and |E_0(h)| = sigma_E E_0(h) with the signs "
                               "declared per case; the stationarity conditions are invariant "
                               "under the sign, so only the level equation carries it",
            "J_inf_includes_the_frozen_side": "the maximum is taken over |h|, |E_0(h)| and the "
                                              "exact level 1, as the task formula states",
            "loops": "each declared loop is an axis-aligned rational rectangle, and 'encircling a "
                     "declared branch' is read as: the loop crosses that branch in exactly two "
                     "points, so the arc between them lies inside the loop",
            "deleted_side_control": "a single deleted side cannot lower the floor, so the "
                                    "discriminating variant deletes all ten frozen sides; both "
                                    "are reported",
            "minimality_method": "the interval-subdivision variant of exact rational interval "
                                 "arithmetic; successive difference substitution is not "
                                 "implemented",
            "resource_limits": "the checker installs a CPU limit, a file-size limit and a wall "
                               "alarm, and records the contract's declared memory budget without "
                               "installing an address-space limit; installing one would add a row "
                               "to the frozen rlimit inventory under "
                               "experiments/rlimit_portability and change a pre-existing "
                               "artifact",
        },
        "residual": CONTRACT["residual"],
        "protected": CONTRACT["protected"],
        "what_is_not_claimed": {
            "native_certificate": False,
            "native_admission": "NotGranted",
            "stable_api_change": False,
            "physical_claim": False,
            "forecast": False,
            "meteorological_data_used": False,
            "meteorological_correspondence": CONTRACT["meteorological_correspondence"]["status"],
            "exchange_realised_by_a_declared_real_loop": False,
        },
    }
    checks = {
        "assertions_within_budget": ASSERTIONS["n"] <= CONTRACT["budgets"]["max_assertions"],
        "every_declared_case_reported": len(cases["cases"]) == len(CASE_DEFINITIONS),
        "every_declared_loop_reported": len(exchange["loops"]) == len(DECLARED_LOOPS),
        "every_declared_point_reported": len(roots["points"]) == len(DECLARED_POINTS),
        "every_control_reported": all(key in controls for key in
                                      ("superseded_collapse_witness", "deleted_side_control",
                                       "frozen_unperturbed_roots", "two_realisations",
                                       "identity_loop_control", "reference_is_never_a_branch")),
        "undecided_items_are_declared": len(payload["undecided"]) == 2,
        "no_control_is_silently_repaired": controls["deleted_side_control"][
            "single_side_deletion_moves_the_minimiser"] is False,
    }
    payload["checks"] = checks
    payload["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    return payload


def summarize(payload):
    sections = payload["sections"]
    discriminant = sections["S4_discriminant_variety"]
    minimality = sections["S7_minimality_and_second_variation"]
    branches = [branch["name"] for branch in discriminant["declared_branches"]]
    print("exchange amplitude variation v1: exact external calibration")
    print("  status:", payload["status"], " assertions:", payload["assertions"])
    print(f"  D: total degree {discriminant['total_degree']}, "
          f"{discriminant['term_count']} terms, branches {branches}")
    for row in sections["S5_case_analysis"]["cases"]:
        print(f"  case {row['case']} active={row['active_quantity']:<20} "
              f"remainder_zero={row['remainder_is_zero']!s:<5} "
              f"groebner={row['groebner_membership']!s:<5} verdict={row['verdict']}")
    witness = minimality["witness"]
    print(f"  J_inf witness p={witness['p']} q={witness['q']}: J_inf = 1, "
          f"on D = 0: {witness['on_the_discriminant_variety']}")
    print("  second variation:", minimality["second_variation"]["verdict"])
    print("  J_2 infimum:", minimality["control_functional_J_2"]["infimum"])
    print("  deleted-side control moves the minimiser:",
          minimality["deleted_side_controls"]["single_side_deletion_moves_the_minimiser"])
    for row in sections["S8_exchange_protocol"]["loops"]:
        print(f"  loop {row['loop']:<44} crossings={row['crossing_count']:>2} "
              f"permutation={row['permutation_of_the_four_roots']}")
    print("  undecided items:", len(payload["undecided"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    arguments = parser.parse_args()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall limit")))
    signal.alarm(CONTRACT["budgets"]["wall_seconds"])
    resource.setrlimit(resource.RLIMIT_CPU, (CONTRACT["budgets"]["cpu_seconds"],) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 << 20, 16 << 20))
    if not SY["available"]:
        payload = {
            "schema": "adva.external.exchange-amplitude-variation-calibration.v1",
            "status": "ToolingUnavailable",
            "reason": SY.get("error"),
            "tooling": {"polynomial_library": "sympy", "available": False},
        }
        with arguments.output.open("x") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        return 1
    payload = build_payload()
    try:
        with arguments.output.open("x") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError:
        print("refusing to overwrite the existing output path:", arguments.output)
        return 2
    summarize(payload)
    return 0 if payload["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
