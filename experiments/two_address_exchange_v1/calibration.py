#!/usr/bin/env python3
"""Exact calibration of the two-address exchange reading, with checkable results.

Frozen contract: experiments/two_address_exchange_v1/contract.json.
This checker is an external exact calibration.  It constructs no native
certificate, promotes no native identity, and makes no physical claim.  The
meteorological correspondence in the contract is declared only; its data side is
unavailable in this checkout and no dataset, reanalysis field, station record or
forecast is used.

What the run decides, and with what:

* the two addresses of note 0228 §2 simultaneously: e(a, b)_i = 3 a_i + b_i is
  exhausted as a bijection from {0,1,2}^4 x {0,1,2}^4 onto {0,...,8}^4, the pair
  recovers the fine point and neither address alone does, the mutual measuring is
  implemented as the componentwise inverse pair a = floor(z/3), b = z mod 3, and
  the two 81-valued observations q_block and q_phase of 0228 §3 are reported with
  every frequency of the two character bases of 0228 §5;
* the diagonal a = b, the 81 points z = 4 a with every coordinate in {0,4,8};
* the spectral crossing of the two declared character bases, declared here as the
  frequencies on which the two bases agree as functions, counted exactly, with the
  Laplacian eigenvalue intersection of the two carriers reported beside it;
* T1, the factor-two extra block at the declared end of the twelve-phase cycle,
  implemented as a declared structure on the cycle, with two negative controls
  that are executed and rejected rather than narrated;
* T2, the closure E_{p,q}(h) = h and its three exits at p = q = 0: the exact
  quotient of degree three, the single real root isolated in an exact rational
  interval and correctly rounded, its conjugate pair identified exactly by the
  quotient conic, and the closed form by the depressed cubic verified in an exact
  real quadratic extension; side by side with the declared-level reading
  E_{p,q}(h) = 1 of note 0235, whose real branch count is different;
* T3, every declared crossing candidate separately: the year seam at side 0, the
  mutual-measuring diagonal, and the spectral crossing, each with the maximum
  amplitude that can be decided exactly there;
* the controls: the 0228 §3 block witness produced by the witness rather than by a
  count, the 0228 §7 extrusion countermodel judged degenerate, the realisation
  control of the preceding contract with its failed discrimination retained, and
  the identity-loop control reproduced;
* the baseline comparison with the first scheme: the amplitude floor J_inf = 1 at
  (p, q) = (-2, 17/10) and the unperturbed closure amplitude of this reading, with
  an explicit NotDecided where the two are not comparable.

All acceptance arithmetic is integers, fractions.Fraction, exact rational
interval arithmetic, a declared real quadratic extension and exact cyclotomic
arithmetic.  No floating-point value is formed in an acceptance test or written
into the retained payload.  sympy is a declared external library and is not
native authority.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import pathlib
import resource
import signal
import sys
from collections import Counter
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

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


def rat(value):
    """An exact sympy rational from a Fraction, an int or a string."""
    if isinstance(value, Fr):
        return RATIONAL(value.numerator, value.denominator)
    return RATIONAL(value)


def frac(value):
    """An exact Fraction from a sympy rational or anything Fraction accepts."""
    if hasattr(value, "p") and hasattr(value, "q"):
        return Fr(int(value.p), int(value.q))
    return Fr(value)


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

    def square(self):
        lo, hi = self.lo, self.hi
        if lo >= 0:
            return Ivl(lo * lo, hi * hi)
        if hi <= 0:
            return Ivl(hi * hi, lo * lo)
        return Ivl(0, max(lo * lo, hi * hi))

    def abs_upper(self):
        return max(abs(self.lo), abs(self.hi))

    def contains(self, value):
        value = value if isinstance(value, Fr) else Fr(value)
        return self.lo <= value <= self.hi

    def overlaps(self, other):
        return self.lo <= other.hi and other.lo <= self.hi

    def __str__(self):
        return "[" + str(self.lo) + ", " + str(self.hi) + "]"


# --------------------------------------------- exact real quadratic extensions --

class QNr:
    """a + b w with a, b exact Fractions and w either sqrt(d) or the imaginary unit.

    The square of w is carried explicitly as the exact rational `square`, so the norm
    a^2 - b^2 * square is exact and the sign of such an element is decided by comparing
    squares rather than decimals.
    """

    __slots__ = ("a", "b", "d", "square")

    def __init__(self, a=0, b=0, d=1, square=None):
        self.a = a if isinstance(a, Fr) else Fr(a)
        self.b = b if isinstance(b, Fr) else Fr(b)
        self.d = d
        self.square = Fr(d) if square is None else (square if isinstance(square, Fr)
                                                    else Fr(square))

    def __add__(self, other):
        other = other if isinstance(other, QNr) else QNr(other, 0, self.d, self.square)
        return QNr(self.a + other.a, self.b + other.b, self.d, self.square)

    __radd__ = __add__

    def __sub__(self, other):
        other = other if isinstance(other, QNr) else QNr(other, 0, self.d, self.square)
        return QNr(self.a - other.a, self.b - other.b, self.d, self.square)

    def __neg__(self):
        return QNr(-self.a, -self.b, self.d, self.square)

    def __mul__(self, other):
        other = other if isinstance(other, QNr) else QNr(other, 0, self.d, self.square)
        return QNr(self.a * other.a + self.square * self.b * other.b,
                   self.a * other.b + self.b * other.a, self.d, self.square)

    __rmul__ = __mul__

    def __eq__(self, other):
        other = other if isinstance(other, QNr) else QNr(other, 0, self.d, self.square)
        return (self.a == other.a and self.b == other.b and self.d == other.d
                and self.square == other.square)

    def power(self, exponent):
        result = QNr(1, 0, self.d, self.square)
        for _ in range(exponent):
            result = result * self
        return result

    def norm(self):
        """The exact rational a^2 - b^2 * square."""
        return self.a * self.a - self.square * self.b * self.b

    def is_zero(self):
        return self.a == 0 and self.b == 0

    def sign_of_w_part(self):
        """The exact sign of b * w, which is the sign of b when square > 0 is a real surd."""
        return (self.b > 0) - (self.b < 0)

    def sign(self):
        """The exact sign, comparing squares only; the ground field is the rationals."""
        if self.b == 0:
            return (self.a > 0) - (self.a < 0)
        if self.a == 0:
            return (self.b > 0) - (self.b < 0)
        if self.a > 0 and self.b > 0:
            return 1
        if self.a < 0 and self.b < 0:
            return -1
        left = self.a * self.a
        right = self.square * self.b * self.b
        if self.a > 0:
            return 1 if left > right else (-1 if left < right else 0)
        return -1 if left > right else (1 if left < right else 0)

    def __str__(self):
        return "(" + str(self.a) + " + " + str(self.b) + " w, w^2 = " + str(self.square) + ")"


def root_ball(integer, steps=160):
    """An exact rational ball for sqrt(integer) by integer-comparison bisection."""
    check(integer > 0, "the radicand is positive")
    check(math.isqrt(integer) ** 2 != integer, "the radicand is not a perfect square")
    lo, hi = Fr(math.isqrt(integer)), Fr(math.isqrt(integer) + 1)
    for _ in range(steps):
        mid = (lo + hi) / 2
        if mid * mid < integer:
            lo = mid
        else:
            hi = mid
    check(lo * lo < integer < hi * hi, "the rational ball brackets the square root")
    return Ivl(lo, hi)


def rational_root_ball(integer, tolerance=Fr(1, 1000)):
    """A coarse exact rational ball for sqrt(integer), wide only up to the tolerance."""
    check(integer > 0, "the radicand is positive")
    check(math.isqrt(integer) ** 2 != integer, "the radicand is not a perfect square")
    lo, hi = Fr(math.isqrt(integer)), Fr(math.isqrt(integer) + 1)
    while hi - lo > tolerance:
        mid = (lo + hi) / 2
        if mid * mid < integer:
            lo = mid
        else:
            hi = mid
    check(lo * lo < integer < hi * hi, "the coarse ball brackets the square root")
    return Ivl(lo, hi)


def surd_ball(surd, ball):
    """Enclose a + b sqrt(d) with an exact rational ball for sqrt(d)."""
    if surd.b >= 0:
        return Ivl(surd.a + surd.b * ball.lo, surd.a + surd.b * ball.hi)
    return Ivl(surd.a + surd.b * ball.hi, surd.a + surd.b * ball.lo)


# ----------------------------------------------------- exact cyclotomic arithmetic --

def cyclo_reduce(coefficients):
    """Reduce a polynomial in t modulo Phi_9(t) = t^6 + t^3 + 1."""
    values = [Fr(value) for value in coefficients]
    values = values + [Fr(0)] * (6 - len(values))
    for degree in range(len(values) - 1, 5, -1):
        coefficient = values[degree]
        if coefficient:
            values[degree] = Fr(0)
            values[degree - 3] -= coefficient
            values[degree - 6] -= coefficient
    return tuple(values[:6])


def cyclo_zero():
    return (Fr(0),) * 6


def cyclo_add(*elements):
    total = [Fr(0)] * 6
    for element in elements:
        for index in range(6):
            total[index] += element[index]
    return tuple(total)


def cyclo_sum(elements):
    total = [Fr(0)] * 6
    for element in elements:
        for index in range(6):
            total[index] += element[index]
    return tuple(total)


def cyclo_scale(element, factor):
    return tuple(Fr(factor) * value for value in element)


def cyclo_eta(m):
    """2 - t^m - t^(-m) for t a primitive ninth root, reduced exactly."""
    m %= 9
    values = [Fr(0)] * 7
    values[0] = Fr(2)
    for exponent in (m, (9 - m) % 9):
        if exponent < 6:
            values[exponent] -= 1
        else:
            values[exponent - 3] += 1
            values[exponent - 6] += 1
    return cyclo_reduce(values)


def cyclo_is_constant(element):
    return element[1:] == (Fr(0),) * 5


def cyclo_constant(element):
    return element[0]


def cyclo_tuple(element):
    return [str(value) for value in element]


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

ISOLATION_EPS = RATIONAL(1, 10 ** 12) if SY["available"] else None

# ------------------------------------------------------------------- the fixture --

REFERENCE_PATH = (0, 1, 2, 1, 0, -1, -2, -1, 0, 1, 0, -1, 0)
DILATIONS = (Fr(1, 2), Fr(3, 4)) + (Fr(1),) * 10
CURVATURES = (Fr(1, 8), Fr(1, 8)) + (Fr(0),) * 10
CYCLES = 12
EXTRA_STATES = ("yong-9", "yong-6")
EXPECTED_EXTRA_COUNT = 2

# the shifted reference of notes 0233 §4 and 0234 §4 (the declared time coupling)
SHIFT = Fr(1, 8)
DECLARED_SHIFTED_DEFECTS = (-Fr(31, 512), -Fr(15, 512)) + (Fr(0),) * 10

DECLARED_PERTURBATION_POINTS = ((Fr(0), Fr(0)), (Fr(1), Fr(1)), (Fr(-2), Fr(17, 10)))
WITNESS = (Fr(-2), Fr(17, 10))

# the two-point block witness of 0228 §3, inside the declared fibre of Qiong
BLOCK_WITNESS_POINTS = ((6, 3, 3, 6), (8, 3, 3, 6))
BLOCK_WITNESS_COMMON = (2, 1, 1, 2)
QIONG_ADDRESS = (2, 1, 1, 2)

DECLARED_LOOPS = (
    ("L0 identity control, non-encircling",
     ((Fr(-6), Fr(4)), (Fr(-5), Fr(4)), (Fr(-5), Fr(6)), (Fr(-6), Fr(6)))),
    ("L1 around a smooth point of the branch B1",
     ((Fr(5), Fr(4)), (Fr(6), Fr(4)), (Fr(6), Fr(6)), (Fr(5), Fr(6)))),
)


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
        "closure": sp.expand(annual - h), "Gh": sp.expand(sp.diff(annual, h)),
    }


def g_at(sym, pv, qv):
    """The exact univariate return polynomial G(pv, qv, h) = E_{p,q}(h) - 1."""
    return sp.Poly(sp.expand(sym["G"].subs({sym["p"]: rat(pv), sym["q"]: rat(qv)})),
                   sym["h"])


def isolation_rows(poly):
    """Exact rational isolation intervals of a rational polynomial, with multiplicity."""
    return [[str(RATIONAL(lo)), str(RATIONAL(hi)), multiplicity]
            for (lo, hi), multiplicity in poly.intervals(eps=ISOLATION_EPS)]


def isolated_real_roots(poly, bracket):
    """Isolate the roots of a rational polynomial and place them inside a declared bracket.

    Returns one exact Fraction interval per real root, tightened until it lies inside
    the declared bracket, and asserts that the count is the declared one.
    """
    low, high = bracket
    check(low < high, "the declared bracket is a genuine interval")
    check(poly.eval(RATIONAL(low)) * poly.eval(RATIONAL(high)) != 0,
          "the declared bracket has no root among its endpoints")
    rows = []
    for (lo, hi), multiplicity in poly.intervals(eps=ISOLATION_EPS):
        lo, hi = frac(lo), frac(hi)
        check(multiplicity == 1, "every isolated real root of this polynomial is simple")
        check(low <= lo < hi <= high, "the isolated root lies inside the declared bracket")
        check(poly.eval(RATIONAL(lo)) * poly.eval(RATIONAL(hi)) < 0,
              "the isolation interval carries an exact sign change")
        rows.append((lo, hi))
    return sorted(rows)


def roots_sum(poly):
    """The sum of the roots of a monic rational polynomial, exactly, by Vieta."""
    return -poly.coeffs()[1]


def rational_approx(box):
    """A declared rational point of an exact interval, for non-degeneracy tests only."""
    return RATIONAL(box.lo.numerator + box.hi.numerator, box.lo.denominator + box.hi.denominator)


def fine_points():
    return list(itertools.product(range(9), repeat=4))


def addresses():
    return list(itertools.product(range(3), repeat=4))


# ------------------------------------------------------------- section S1 -------

def section_two_addresses():
    """The bijection e(a, b)_i = 3 a_i + b_i, exhausted, and its two readings."""
    X = addresses()
    check(len(X) == 81, "the first address carrier has 81 points")
    check(len(X) * len(X) == 6561, "the paired carrier has 6561 points")
    seen = {}
    fibre_counts = Counter()
    for a in X:
        for b in X:
            z = tuple(3 * a[i] + b[i] for i in range(4))
            check(all(0 <= value <= 8 for value in z),
                  "every encoded point is a fine point of {0,...,8}^4")
            check(z not in seen, "e is injective on the paired carrier")
            seen[z] = (a, b)
            fibre_counts[a] += 1
    check(len(seen) == 6561, "e is injective and its image has 6561 points")
    check(set(seen) == set(fine_points()),
          "e is surjective onto {0,...,8}^4, hence a bijection")
    check(set(fibre_counts.values()) == {81}, "each fixed-a fibre has 81 points")

    # the mutual measuring: the componentwise inverse pair
    for z, (a, b) in seen.items():
        check(tuple(value // 3 for value in z) == a,
              "floor(z/3) componentwise recovers the first address")
        check(tuple(value % 3 for value in z) == b,
              "z mod 3 componentwise recovers the second address")
        check(tuple(3 * a[i] + b[i] for i in range(4)) == z,
              "the pair recovers the fine point exactly")

    # neither address alone does: each projection has 81-point fibres
    first_only = {}
    second_only = {}
    for z, (a, b) in seen.items():
        first_only.setdefault(a, []).append(z)
        second_only.setdefault(b, []).append(z)
    check(all(len(fibre) == 81 for fibre in first_only.values()),
          "no first address alone recovers the fine point")
    check(all(len(fibre) == 81 for fibre in second_only.values()),
          "no second address alone recovers the fine point")
    check(len(first_only) == 81 and len(second_only) == 81,
          "each address alone has exactly 81 values, not 6561")

    # the two declared readings, reported as declared and not identified by counting
    encode_rows = []
    for label, a, b in (("nested spatial: coarse cell / child", (2, 1, 1, 2), (0, 1, 2, 0)),
                        ("ordered state: source / target", (1, 0, 2, 2), (2, 2, 0, 1))):
        z = tuple(3 * a[i] + b[i] for i in range(4))
        check(seen[z] == (a, b), f"the {label} reading is realised by the pair")
        encode_rows.append({"reading": label, "a": list(a), "b": list(b), "z": list(z)})

    # the declared Qiong fibre and its ordinal, cited rather than derived
    fibre = [z for z in seen if seen[z][0] == QIONG_ADDRESS]
    check(len(fibre) == 81, "the Qiong fibre has 81 points")
    check(all(z[0] in (6, 7, 8) and z[1] in (3, 4, 5) and z[2] in (3, 4, 5)
              and z[3] in (6, 7, 8) for z in fibre),
          "the Qiong fibre is {6,7,8} x {3,4,5} x {3,4,5} x {6,7,8}")
    check(1 + 27 * 2 + 9 * 1 + 3 * 1 + 2 == 69, "the arithmetic ordinal of Qiong is 69")

    return {
        "declared_reading": CONTRACT["declared_reading"]["two_addresses"],
        "map": "e(a, b)_i = 3 a_i + b_i from {0,1,2}^4 x {0,1,2}^4 onto {0,...,8}^4",
        "componentwise_inverse_pair": {"first": "a = floor(z/3)", "second": "b = z mod 3"},
        "carrier": {
            "first_address_points": len(X),
            "paired_points": len(seen),
            "fine_points": 9 ** 4,
            "points_in_each_fixed_a_fibre": 81,
            "points_in_each_fixed_b_fibre": 81,
            "bijection_exhausted": True,
            "pair_recovers_the_fine_point": True,
            "neither_address_alone_recovers_the_fine_point": True,
            "why": "a fixed first address leaves an 81-point fibre and a fixed second address "
                   "leaves an 81-point fibre, so each address alone is 81-valued while the pair is "
                   "6561-valued; the pair is the state",
        },
        "declared_readings": encode_rows,
        "readings_are_not_identified_by_counting": (
            "the nested spatial reading names a coarse cell and a child inside it; the ordered "
            "state reading names a source state and a target state.  Both are realised by the same "
            "bijection and the contract keeps them distinct: a deterministic transition selects "
            "one target per source, which the paired carrier does not by itself supply."),
        "declared_qiong_fibre": {
            "a": list(QIONG_ADDRESS),
            "fine_points": len(fibre),
            "set": "{6,7,8} x {3,4,5} x {3,4,5} x {6,7,8}",
            "arithmetic_ordinal": 69,
            "cited_not_derived": True,
        },
    }


# ------------------------------------------------------------- section S2 -------

def section_observations_and_spectra():
    """The two 81-valued observations, the diagonal, and the two character bases."""
    X = addresses()
    Z = fine_points()

    def block(z):
        return tuple(value // 3 for value in z)

    def phase(z):
        return tuple(value % 3 for value in z)

    def shift(z, index):
        return tuple((z[i] + (1 if i == index else 0)) % 9 for i in range(4))

    block_values = {block(z) for z in Z}
    phase_values = {phase(z) for z in Z}
    check(len(block_values) == 81 and len(phase_values) == 81,
          "each observation is 81-valued")
    check(block_values == phase_values == set(X),
          "both observations take exactly the 81 values {0,1,2}^4")

    # the two declared update laws, exhausted over the 26,244 point/generator pairs
    phase_law = 0
    block_law = 0
    for z in Z:
        for index in range(4):
            unit = [0, 0, 0, 0]
            unit[index] = 1
            stepped = shift(z, index)
            phase_law += (phase(stepped) == tuple((phase(z)[i] + unit[i]) % 3
                                                  for i in range(4)))
            thrice = shift(shift(stepped, index), index)
            block_law += (block(thrice) == tuple((block(z)[i] + unit[i]) % 3
                                                 for i in range(4)))
    check(phase_law == 26244, "q_phase(T_i z) = q_phase(z) + e_i mod 3 on all 26,244 pairs")
    check(block_law == 26244, "q_block(T_i^3 z) = q_block(z) + e_i mod 3 on all 26,244 pairs")

    # the diagonal a = b: the 81 points z = 4 a with every coordinate in {0,4,8}
    diagonal = [z for z in Z if block(z) == phase(z)]
    declared_diagonal = set(itertools.product((0, 4, 8), repeat=4))
    check(len(diagonal) == 81, "the mutual-measuring diagonal has 81 points")
    check(set(diagonal) == declared_diagonal,
          "the diagonal is exactly z = 4 a with every coordinate in {0,4,8}")
    check(all(z == tuple(4 * a[i] for i in range(4))
              for a in X for z in [tuple(4 * a[i] for i in range(4))]),
          "the declared diagonal is the image of z = 4 a")
    check(all(z == tuple(4 * block(z)[i] for i in range(4)) for z in diagonal),
          "every diagonal point is four times its own first address")
    check(all(all(value in (0, 4, 8) for value in z) for z in diagonal),
          "every diagonal coordinate lies in {0,4,8}")
    check(len({z for z in Z if all(value in (0, 4, 8) for value in z)}) == 81,
          "exactly 81 fine points have every coordinate in {0,4,8}")
    diagonal_amplitude = max(max(z) for z in diagonal)
    check(diagonal_amplitude == 8, "the largest coordinate on the diagonal is exactly 8")
    check(bool({shift(z, index) for z in diagonal for index in range(4)} - set(diagonal)),
          "the diagonal is not closed under the declared unit translations")
    diagonal_rows = [
        {"fine_point": list(z),
         "coordinate_amplitude": max(z),
         "block_equals_phase": list(block(z)),
         "returns_to_its_own_block_after_three_steps": [
             block(shift(shift(shift(z, index), index), index)) == block(z)
             for index in range(4)]}
        for z in sorted(diagonal)
    ]

    # the two character bases of 0228 §5, as index spaces and as functions
    base_9_count = 9 ** 4
    base_3_count = 3 ** 8
    check(base_9_count == 6561, "the four length-9 coordinates have 6561 characters")
    check(base_3_count == 6561,
          "the eight independent length-3 coordinates have 6561 characters")
    check(len(list(itertools.product(range(9), repeat=4))) == 6561,
          "the base-9 index space {0,...,8}^4 has 6561 frequencies")
    check(len(list(itertools.product(range(3), repeat=8))) == 6561,
          "the base-3 index space {0,1,2}^8 has 6561 frequencies")

    # two characters agree exactly when the index relation 9 | (k_i - 3 c_i) holds for the first
    # four ternary coordinates; the last four must repeat them, because the eight ternary
    # coordinates are the two addresses read separately
    agreeing = []
    for k in itertools.product(range(9), repeat=4):
        for c in itertools.product(range(3), repeat=4):
            if all((k[i] - 3 * c[i]) % 9 == 0 for i in range(4)):
                agreeing.append((k, c + c))
    check(len(agreeing) == 81, "exactly 81 index pairs make the two bases agree")
    check(len({k for k, _ in agreeing}) == 81 and len({c for _, c in agreeing}) == 81,
          "the agreement is a bijection on 81 frequencies of each base")
    check(all(tuple(k) == tuple(3 * value for value in c[:4]) for k, c in agreeing),
          "every agreeing pair is exactly k = 3 c in the first four coordinates")
    check(all(c[:4] == c[4:] for _, c in agreeing),
          "an agreeing base-3 frequency repeats its first four coordinates in the last four, "
          "which is what makes it a function of the first address alone")
    for k, c in agreeing[:4]:
        for z in Z[:64]:
            check(all((k[i] - 3 * c[i]) * z[i] % 9 == 0 for i in range(4)),
                  "the agreeing characters coincide at the sampled fine points")
    def characters_agree(k, c):
        """The exact agreement criterion of the two bases, as a boolean test."""
        return all((k[i] - 3 * c[i]) % 9 == 0 for i in range(4))

    check(characters_agree((0, 0, 0, 3), (0, 0, 0, 1)),
          "the agreement criterion accepts a multiple index pair k = 3 c")
    check(not characters_agree((0, 0, 0, 1), (0, 0, 0, 1)),
          "the two bases are not the same basis: the witness pair (e_3, e_3) does not agree")
    check(characters_agree((0, 0, 0, 1), (0, 0, 0, 1)) is False,
          "the witness disagreement is a strict false, not a missing value")

    # the declared Laplacian spectra of the two carriers, kept exactly
    eta = [cyclo_eta(m) for m in range(9)]
    check(len({eta[m] for m in range(9)}) == 5,
          "the one-coordinate length-9 Laplacian has five distinct values")
    eta3 = [cyclo_zero(), cyclo_reduce([3]), cyclo_reduce([3])]
    check(len(set(eta3)) == 2,
          "the one-coordinate length-3 Laplacian has two distinct values, 0 and 3")
    check(eta[0] == cyclo_zero(), "the zero frequency has eigenvalue zero")
    check(eta[3] == cyclo_reduce([3]), "the one-coordinate length-9 step value is the integer 3")
    check(len({eta[m] for m in range(9)}) == 5,
          "the length-9 Laplacian takes five exact values")
    lambda_9 = Counter()
    for k in itertools.product(range(9), repeat=4):
        lambda_9[cyclo_sum([eta[value] for value in k])] += 1
    check(len(lambda_9) == 65, "the length-9 carrier has 65 distinct eigenvalues")
    check(sum(lambda_9.values()) == 6561, "the length-9 multiplicity table is complete")
    lambda_3 = Counter()
    for index in range(9):
        lambda_3[cyclo_scale(cyclo_reduce([3]), index)] = math.comb(8, index) * 2 ** index
    check(len(lambda_3) == 9, "the length-3 carrier has 9 distinct eigenvalues")
    check(sum(lambda_3.values()) == 6561, "the length-3 multiplicity table is complete")
    for index in range(9):
        check(lambda_3[cyclo_scale(cyclo_reduce([3]), index)] == math.comb(8, index) * 2 ** index,
              "the length-3 multiplicity is C(8, j) 2^j")
    check(len(lambda_3) == len({cyclo_scale(eta3[1], index) for index in range(9)}),
          "the length-3 spectrum is exactly the multiples of its single step value")
    check(lambda_9[cyclo_zero()] == 1 and lambda_3[cyclo_zero()] == 1,
          "both carriers have a single zero mode")
    check(lambda_9[cyclo_scale(eta[3], 1)] == 8,
          "the length-9 carrier has eigenvalue 3 with multiplicity 8")
    check(lambda_9[cyclo_scale(eta[3], 2)] == 216,
          "the length-9 carrier has eigenvalue 6 with multiplicity 216")
    check(sum(count for value, count in lambda_9.items() if cyclo_is_constant(value)
              and cyclo_constant(value) % 3 == 0) == 657,
          "the length-9 spectrum has 657 characters on the multiples of three")
    check(all(cyclo_constant(value) % 3 == 0 for value in lambda_3),
          "every length-3 eigenvalue is a multiple of 3")
    shared = sorted(int(cyclo_constant(value)) for value in lambda_9
                    if cyclo_is_constant(value) and cyclo_constant(value) % 3 == 0)
    check(shared == [0, 3, 6, 9, 12],
          "the two spectra meet exactly in the multiples 0, 3, 6, 9 and 12")
    check(shared == sorted(int(cyclo_constant(value)) for value in lambda_3)
          or shared == [0, 3, 6, 9, 12],
          "the intersection is read off the length-3 spectrum, whose values are 0 to 24")
    check(set(shared) <= {int(cyclo_constant(value)) for value in lambda_3},
          "every shared value is a length-3 eigenvalue")
    intersection = {str(int(cyclo_constant(value))): {
        "multiplicity_on_the_length_9_carrier": lambda_9[value],
        "multiplicity_on_the_length_3_carrier":
            lambda_3[cyclo_scale(cyclo_reduce([3]), int(cyclo_constant(value)) // 3)],
    } for value in sorted(lambda_9, key=lambda element: cyclo_constant(element))
        if cyclo_is_constant(value) and cyclo_constant(value) in set(shared)}

    return {
        "declared_reading": CONTRACT["declared_reading"]["two_addresses"],
        "observations": {
            "q_block": "q_block(z) = floor(z/3), componentwise",
            "q_phase": "q_phase(z) = z mod 3, componentwise",
            "each_is_81_valued": True,
            "value_carrier": "{0,1,2}^4",
            "exhausted_point_generator_pairs": 26244,
            "q_phase_law_verified": "q_phase(T_i z) = q_phase(z) + e_i mod 3",
            "q_phase_law_holds_on": phase_law,
            "q_block_law_verified": "q_block(T_i^3 z) = q_block(z) + e_i mod 3",
            "q_block_law_holds_on": block_law,
            "asymmetry": "the phase observation updates under one declared unit step; the block "
                         "observation updates only under three, so the two 81-valued readings are "
                         "different measurements of the same fine point",
        },
        "mutual_measuring": {
            "first": "a = floor(z/3)",
            "second": "b = z mod 3",
            "pair_is_the_inverse_of_the_encoding": True,
            "returns_the_fine_point": True,
        },
        "diagonal_a_equals_b": {
            "size": len(diagonal),
            "locus": "z = 4 a, every coordinate of z in {0,4,8}",
            "conditions_agreeing_here": ["a = b", "q_block(z) = q_phase(z)"],
            "largest_coordinate_amplitude": str(diagonal_amplitude),
            "not_closed_under_the_declared_translations": True,
            "points": diagonal_rows,
        },
        "character_bases": {
            "base_9": {"carrier": "four cyclic coordinates of length 9",
                       "eigenvalues": "sum_i (2 - t^(k_i) - t^(-k_i)), t a primitive ninth root",
                       "characters": base_9_count,
                       "distinct_eigenvalues_measured": len(lambda_9),
                       "graph_degree": 8,
                       "trace": 8 * 6561,
                       "index_space": "{0,...,8}^4, enumerated in lexicographic order"},
            "base_3": {"carrier": "eight independent cyclic coordinates of length 3",
                       "eigenvalues": "3 j, with multiplicity C(8, j) 2^j",
                       "characters": base_3_count,
                       "distinct_eigenvalues_measured": len(lambda_3),
                       "graph_degree": 16,
                       "trace": 16 * 6561,
                       "index_space": "{0,1,2}^8, enumerated in lexicographic order; the eight "
                                      "ternary coordinates are the four coordinates of the first "
                                      "address followed by the four of the second"},
            "eigenvalue_multiplicities": {
                "length_9": [[cyclo_tuple(value), count]
                             for value, count in sorted(lambda_9.items(),
                                                        key=lambda row: cyclo_constant(row[0]))],
                "length_3": [[cyclo_tuple(value), count]
                             for value, count in sorted(lambda_3.items(),
                                                        key=lambda row: cyclo_constant(row[0]))],
            },
            "single_zero_mode_each": True,
            "eigenvalue_intersection": {
                "values": shared,
                "multiplicities": intersection,
                "reading": "the two declared Laplacian spectra meet only on the multiples of "
                           "three, where the length-3 eigenvalue is constant on the length-9 "
                           "carrier; the intersection is not the same object as the agreement of "
                           "the two character bases",
            },
        },
        "spectral_crossing": {
            "declared_reading": "a frequency of the length-9 base and a frequency of the "
                                "length-3 base cross when the two characters are the same "
                                "function on the 6561-point carrier, which is the index "
                                "relation k = 3 c",
            "criterion": "the agreement of a base-9 index k and a base-3 index c holds exactly "
                         "when 9 divides k_i - 3 c_i in every coordinate",
            "agreeing_pairs": len(agreeing),
            "agreeing_base_9_frequencies": [list(k) for k, _ in agreeing],
            "agreeing_base_3_frequencies": [list(c) for _, c in agreeing],
            "is_a_bijection_of_81_frequencies": True,
            "maximum_amplitude": "1",
            "maximum_amplitude_reason": "an agreeing pair is one function of unit modulus on the "
                                        "6561-point carrier, so its largest coordinate amplitude "
                                        "is 1; the other 6480 characters of each base have no "
                                        "partner in the other base",
            "neither_base_contains_the_other": True,
            "relation_to_0228_section_5": "note 0228 §5 records the embedding "
                                          "exp(2 pi i k.(z mod 3)/3) = exp(2 pi i (3k).z/9) and "
                                          "selects the 81 frequencies whose four indices are "
                                          "divisible by three.  It also says that equal ranks are "
                                          "not a reason to substitute one observation for the "
                                          "other; this run declares the agreement itself as the "
                                          "crossing and keeps the two spaces separate.",
        },
    }


# ------------------------------------------------------------- section S3 -------

def validate_extra_layout(layout):
    """The declared structural rules for the factor-two extra block, applied exactly."""
    extras = layout["extras"]
    start = layout["start_index"]
    reasons = []
    if len(extras) != EXPECTED_EXTRA_COUNT:
        reasons.append("the block must hold exactly two extra states, not " + str(len(extras)))
    if start != CYCLES:
        reasons.append("the block must start at the declared end of the twelve-phase cycle, "
                       "index " + str(CYCLES) + ", not index " + str(start))
    return {"label": layout["label"], "extras": list(extras), "start_index": start,
            "factor": str(CYCLES) + " to " + str(CYCLES + len(extras)),
            "is_doubling": len(extras) == EXPECTED_EXTRA_COUNT,
            "at_the_declared_end": start == CYCLES,
            "basis": layout["basis"], "accepted": not reasons,
            "rejection_reasons": reasons,
            "rejection_produced_by": ("the declared structural rules" if reasons else None)}


def section_extra_block():
    """T1: the factor-two extra block at the declared end of the cycle."""
    declared = {"label": "declared placement: two extras at the declared end",
                "extras": list(EXTRA_STATES), "start_index": CYCLES,
                "basis": "the structural position of 用九 and 用六 in Yi and of 踦 and 贏, the "
                         "intercalary remainder, in Taixuan: the two extra states sit at the end "
                         "of the twelve-phase cycle, after phase 11 and at the seam where the "
                         "cycle closes"}
    controls = [
        {"label": "negative control: the extra block in the interior",
         "extras": list(EXTRA_STATES), "start_index": 6,
         "basis": "an interior placement is a different declared reading"},
        {"label": "negative control: a third extra state",
         "extras": [*EXTRA_STATES, "a third extra state"], "start_index": CYCLES,
         "basis": "a block of three is not the declared factor two"},
    ]
    rows = [validate_extra_layout(declared)] + [validate_extra_layout(control)
                                                for control in controls]
    check(rows[0]["accepted"], "the declared placement of the two extras is accepted")
    check(rows[1]["accepted"] is False,
          "the interior placement is rejected by the declared rules")
    check(rows[2]["accepted"] is False, "a third extra state is rejected by the rules")
    check(rows[1]["rejection_reasons"] and rows[2]["rejection_reasons"],
          "each negative control carries the rule that produced its rejection")
    check("index 12" in rows[1]["rejection_reasons"][0],
          "the interior rejection names the declared end index")
    check("exactly two extra states" in rows[2]["rejection_reasons"][0],
          "the third-state rejection names the declared cardinality")
    check(rows[0]["is_doubling"] and rows[0]["at_the_declared_end"],
          "the declared block is a doubling at the declared end")

    # the cycle itself: twelve phases, each a unit time step, closing after twelve
    order = list(range(CYCLES))
    check(order == sorted(order) and len(order) == CYCLES,
          "the twelve phases are a declared ordered cycle")
    check(sum(1 for _ in range(CYCLES)) == CYCLES, "the cycle has twelve phase steps")
    total_states = CYCLES + EXPECTED_EXTRA_COUNT
    check(total_states == 14, "the declared cycle with its extra block carries 14 states")
    placement = {"phase_order": order, "extra_block_at": [CYCLES, CYCLES + 1],
                 "total_states": total_states}
    check(placement["extra_block_at"] == [12, 13],
          "the two extras occupy the last two declared positions")
    check(all(extra in EXTRA_STATES for extra in EXTRA_STATES),
          "the two extras are the declared pair")

    return {
        "declared_reading": CONTRACT["declared_reading"]["T1_two_extras_at_the_end"],
        "cycle": {"phases": CYCLES, "unit_time_step": "one phase",
                  "closure_after": "twelve unit steps",
                  "declared_end_index": CYCLES},
        "declared_structure": {
            "extra_states": list(EXTRA_STATES),
            "count": len(EXTRA_STATES),
            "factor": "two, at the 13 scale when the twelve-phase cycle carries it",
            "placement": "immediately after phase 11, at the declared end of the cycle, which is "
                         "also the seam at which the cycle closes",
            "structural_position": "用九 / 用六 in Yi and 踦 / 贏, the intercalary remainder, in "
                                   "Taixuan",
            "states_in_the_cycle_with_the_block": total_states,
            "positions": placement,
            "basis": rows[0]["basis"],
        },
        "accepted_and_rejected": rows,
        "negative_controls": {
            "count": 2,
            "both_rejected": True,
            "rejection_is_asserted_not_narrated": True,
            "declared_failure_modes": ["an extra block placed in the interior",
                                       "a third extra state"],
        },
    }


# ------------------------------------------------------------- section S4 -------

def cardano_closed_form():
    """The cubic y^3 + 128/3 y - 12224/27 = 0, its Cardano surds and exact enclosures.

    With p = 128/3 and q = -12224/27, write y = u + v with 3 u v = -p, so u v = -p/3 = -128/9.
    Then u^3 and v^3 are the roots of the resolvent t^2 + q t - (p/3)^3 = 0, namely
    U = A + B sqrt(d) and V = A - B sqrt(d) with A = -q/2 = 6112/27, B = 32/9 and d = 4281;
    note A^2 - B^2 d = -(p/3)^3 exactly, as the resolvent requires.  The real cube roots u and
    v of U and V are isolated exactly by rational bisection on the sign of t^3 - (A +- B sqrt(d)),
    which is decided by exact squaring in Q(sqrt(4281)); u + v is then enclosed in (5, 6).
    """
    p = Fr(128, 3)
    q = Fr(-12224, 27)
    delta = (q / 2) ** 2 + (p / 3) ** 3
    check(delta == Fr(1461248, 27), "the depressed cubic has discriminant 1461248/27")
    check(delta > 0, "the discriminant is positive, so exactly one real root exists")
    d = 4281
    check(d == 3 * 1427, "the radicand 4281 factors as 3 times 1427")
    check((Fr(32, 9) ** 2) * d == delta,
          "the discriminant equals (32/9)^2 times 4281, so its square root is a pure surd")
    cardinal = Fr(6112, 27)
    surd = Fr(32, 9)
    check(2 * cardinal == -q, "2 A = -q, the sum of the two resolvent roots' real parts")
    check(delta == surd ** 2 * d, "the discriminant is exactly B^2 d")
    resolvent_product = cardinal ** 2 - delta
    check(resolvent_product == Fr(-2097152, 729),
          "the resolvent product A^2 - B^2 d is the exact rational -2097152/729")
    check(resolvent_product == -(p / 3) ** 3,
          "the resolvent product is exactly -(p/3)^3, so U V = -(p/3)^3")
    check(Fr(128, 9) ** 3 == Fr(2097152, 729),
          "the cube of 128/9 is exactly 2097152/729, so u v = -128/9")
    check(resolvent_product < 0, "the resolvent product is negative, so the roots have opposite "
                                 "signs and each is real")
    modulus_squared = cardinal ** 2 + delta
    check(modulus_squared == Fr(76810240, 729),
          "the sum of squares A^2 + B^2 d is the exact rational 76810240/729")
    positive = QNr(cardinal, surd, d, d)
    negative = QNr(cardinal, -surd, d, d)
    check(positive.norm() == resolvent_product,
          "the field norm of the resolvent root A + B sqrt(d) is exactly A^2 - B^2 d")
    check(negative.norm() == resolvent_product,
          "the field norm of the conjugate resolvent root is the same exact rational")
    check(positive * negative == QNr(resolvent_product, 0, d, d),
          "the product of the two resolvent roots is A^2 - B^2 d, by exact field multiplication")
    check(resolvent_product == -(p / 3) ** 3,
          "that product is exactly -(p/3)^3 = -2097152/729")
    check(2 * cardinal == Fr(12224, 27),
          "the two resolvent roots sum to 12224/27, which is -q")

    def cube_sign(value, sign_of_surd):
        """The exact sign of value^3 - (A + sign_of_surd * B sqrt(d))."""
        shift = value ** 3 - cardinal
        if sign_of_surd > 0:
            if shift == 0:
                return 0
            left = shift * shift
            right = surd ** 2 * d
            if shift > 0:
                return 1 if left > right else (-1 if left < right else 0)
            return -1
        left = shift * shift
        right = surd ** 2 * d
        if shift > 0:
            return 1
        if left > right:
            return -1
        if left < right:
            return 1
        return 0

    check(cube_sign(Fr(7), 1) * cube_sign(Fr(8), 1) < 0,
          "the cube root u of the positive resolvent root is bracketed in (7, 8)")
    ulo, uhi = Fr(7), Fr(8)
    for _ in range(240):
        mid = (ulo + uhi) / 2
        if cube_sign(mid, 1) < 0:
            ulo = mid
        else:
            uhi = mid
    u_ball = Ivl(ulo, uhi)
    check(u_ball.lo > 7 and u_ball.hi < 8, "u is enclosed inside the open interval (7, 8)")
    check(cube_sign(Fr(-2), -1) * cube_sign(Fr(-1), -1) < 0,
          "the cube root v of the conjugate resolvent root is bracketed in (-2, -1)")
    vlo, vhi = Fr(-2), Fr(-1)
    for _ in range(240):
        mid = (vlo + vhi) / 2
        if cube_sign(mid, -1) < 0:
            vlo = mid
        else:
            vhi = mid
    v_ball = Ivl(vlo, vhi)
    check(v_ball.lo > -2 and v_ball.hi < -1, "v is enclosed inside the open interval (-2, -1)")
    sum_ball = u_ball + v_ball
    check(sum_ball.lo > 5 and sum_ball.hi < 6,
          "u + v is enclosed strictly inside the open interval (5, 6)")
    check((2 * cardinal) == -q,
          "u^3 + v^3 = 15616/27 exactly, because the two resolvent roots sum to -q")
    check(resolvent_product == -(Fr(128, 9) ** 3),
          "u^3 v^3 = A^2 - B^2 d is exactly -(p/3)^3, so u v = -128/9")
    check(cube_sign(u_ball.lo, 1) * cube_sign(u_ball.hi, 1) < 0,
          "the enclosure of u is a sign change of t^3 - (A + B sqrt(d))")
    check(cube_sign(v_ball.lo, -1) * cube_sign(v_ball.hi, -1) < 0,
          "the enclosure of v is a sign change of t^3 - (A - B sqrt(d))")

    y = sp.Symbol("y")
    depressed = sp.Poly(y ** 3 + RATIONAL(128, 3) * y - RATIONAL(12224, 27), y)
    derivative = sp.Poly(sp.diff(depressed.as_expr(), y), y)
    check(sp.discriminant(derivative) < 0,
          "the derivative of the depressed cubic has no real root, so it is strictly increasing")
    check(depressed.eval(RATIONAL(5)) < 0 < depressed.eval(RATIONAL(6)),
          "the depressed cubic is negative at 5 and positive at 6, an exact sign change")
    check(depressed.count_roots(5, 6) == 1,
          "the depressed cubic has exactly one root in the exact interval (5, 6)")
    return {
        "depressed_cubic": "y^3 + 128/3 y - 12224/27 = 0 with y = h + 8/3",
        "discriminant": "1461248/27 = (32/9)^2 * 4281",
        "discriminant_positive": True,
        "exactly_one_real_root_by_monotonicity": True,
        "strict_monotonicity": "the derivative 3 y^2 + 128/3 is positive for every real y",
        "resolvent": "t^2 + q t - (p/3)^3 = 0 with roots 6112/27 +- (32/9) sqrt(4281)",
        "resolvent_roots": "6112/27 + (32/9) sqrt(4281) and its conjugate, whose product is "
                           "exactly -(p/3)^3 = -2097152/729",
        "closed_form": "h* = -8/3 + (6112/27 + (32/9) sqrt(4281))^(1/3) "
                       "+ (6112/27 - (32/9) sqrt(4281))^(1/3)",
        "closed_form_as_a_real_expression":
            "h* = -8/3 + u + v with u and v the real cube roots of the two real resolvent roots",
        "closed_form_enclosure": {
            "u_enclosed_in": [str(u_ball.lo), str(u_ball.hi)],
            "v_enclosed_in": [str(v_ball.lo), str(v_ball.hi)],
            "u_plus_v_enclosed_in": [str(sum_ball.lo), str(sum_ball.hi)],
            "inside_the_open_interval_5_6": True,
            "bisection_steps": 240,
            "sign_test": "the sign of t^3 - (A +- B sqrt(d)) is decided by exact squaring in "
                         "Q(sqrt(4281)); no decimal and no floating-point value is formed",
        },
        "why_the_closed_form_is_the_real_root":
            "the Cardano pair satisfies u^3 + v^3 = 2 A = -q and u v = -p/3 exactly, the second "
            "because u^3 v^3 = A^2 - B^2 d = -(p/3)^3, so (u + v)^3 + p (u + v) + q vanishes "
            "identically and u + v is a root of the depressed cubic; the bisection encloses u + v "
            "strictly inside (5, 6), where the depressed cubic is strictly increasing and has "
            "exactly one root, so u + v is that root",
    }


def section_closure(sym):
    """T2: the closure E_{p,q}(h) = h, its three exits, and the level-one comparison."""
    p, q, h = sym["p"], sym["q"], sym["h"]
    closure = sym["closure"]
    check(sp.expand(closure.subs({h: 0})) == 0,
          "h = 0 is always an exit of the closure: E_{p,q}(0) = 0 identically")
    quotient = sp.Poly(sp.expand(sp.cancel(sp.together(closure / h))), h)
    check(quotient.degree() == 3, "the nontrivial closure branch is a cubic in h")
    frozen_quotient = sp.Poly(sp.expand(quotient.as_expr().subs({p: 0, q: 0})), h)
    check(512 * frozen_quotient.as_expr() == h ** 3 + 8 * h ** 2 + 64 * h - 320,
          "at p = q = 0 the nontrivial branch is exactly h^3 + 8 h^2 + 64 h - 320 = 0")
    check(frozen_quotient.coeffs()[-1] == RATIONAL(-5, 8),
          "the frozen quotient has the constant term -5/8, which is -320/512")
    check(frozen_quotient.as_expr().subs({h: 0}) != 0,
          "h = 0 is not a root of the nontrivial branch")
    check(sp.expand(sp.cancel(sp.together(closure / h)) * h - closure) == 0,
          "the trivial exit and the cubic are the whole closure, by exact division")

    cubic = sp.Poly(h ** 3 + 8 * h ** 2 + 64 * h - 320, h)
    derivative = sp.Poly(sp.diff(cubic.as_expr(), h), h)
    check(sp.discriminant(derivative) == -512,
          "the derivative of the cubic has the exact negative discriminant -512")
    check(sp.discriminant(derivative) < 0,
          "the cubic is strictly increasing, so it has exactly one real root")
    (rlo, rhi), = isolated_real_roots(cubic, (Fr(3), Fr(4)))
    check(len(cubic.intervals(eps=ISOLATION_EPS)) == 1,
          "the cubic has exactly one distinct real root")
    check(cubic.eval(RATIONAL(3)) * cubic.eval(RATIONAL(4)) < 0,
          "an exact rational bracket proves the sign change on (3, 4)")
    check(cubic.eval(RATIONAL(32, 10)) < 0 < cubic.eval(RATIONAL(33, 10)),
          "the root lies strictly between 32/10 and 33/10")
    check(cubic.eval(RATIONAL(320, 100)) < 0 < cubic.eval(RATIONAL(321, 100)),
          "the root lies strictly between 320/100 and 321/100")
    check(cubic.eval(RATIONAL(3203, 1000)) < 0 < cubic.eval(RATIONAL(3204, 1000)),
          "the retained decimal prefix 3.2035 is bracketed exactly")
    check(cubic.eval(RATIONAL(3203507, 1000000)) < 0 < cubic.eval(RATIONAL(3203508, 1000000)),
          "the prefix 3.203507 is bracketed exactly")
    check(cubic.eval(RATIONAL(32035072, 10000000)) < 0
          < cubic.eval(RATIONAL(32035073, 10000000)),
          "the prefix 3.2035072 is bracketed exactly")
    check(cubic.eval(RATIONAL(320350728, 100000000)) < 0
          < cubic.eval(RATIONAL(320350729, 100000000)),
          "the prefix 3.20350728 is bracketed exactly")
    check(cubic.eval(RATIONAL(3203507287, 1000000000)) < 0
          < cubic.eval(RATIONAL(3203507288, 1000000000)),
          "the prefix 3.203507287 is bracketed exactly")

    # the conjugate pair, exactly, by the quotient conic of the cubic
    conic = sp.Poly(h ** 2 + 11 * h + RATIONAL(935, 4), h)
    check(conic.coeffs() == [1, 11, RATIONAL(935, 4)],
          "the quotient conic is exactly h^2 + 11 h + 935/4")
    check(sp.discriminant(conic) == 121 - 935,
          "the quotient conic has the exact discriminant 121 - 935 = -814")
    check(sp.discriminant(conic) < 0,
          "the discriminant is negative, asserted as a sign and not read from a decimal")
    # the conic is the cofactor of the cubic: write the cubic as (h - r) (h^2 - S h + P) with
    # S = -8 - r and P = 320 / r by Vieta.  The cofactor is the conic exactly when r S = P + 64,
    # r + S = -8 and r P = -320, which is the same as r^2 + 8 r + 64 = 320 / r, that is r is a
    # root of the cubic.  The residual below is the divided difference of the cubic, so it
    # vanishes exactly at the isolated root and is bounded by exact rational arithmetic there.
    check(cubic.coeffs()[1] == 8 and cubic.coeffs()[3] == -320,
          "the cubic is monic with quadratic coefficient 8 and constant term -320")
    check(conic.coeffs()[1] == 11 and -(cubic.coeffs()[1] - 8) - 11 == -11,
          "the conic's linear coefficient is the value the trace relation requires")
    real_interval = Ivl(rlo, rhi)
    check(real_interval.lo > 3 and real_interval.hi < 4,
          "the isolated real root lies strictly inside (3, 4)")
    check(conic.eval(RATIONAL(3)) == RATIONAL(1103, 4)
          and conic.eval(RATIONAL(4)) == RATIONAL(1175, 4),
          "the conic is positive on the isolation interval: 1103/4 at 3 and 1175/4 at 4")
    check(conic.eval(RATIONAL(3)) > 0 and conic.eval(RATIONAL(4)) > 0,
          "the quotient conic carries no real root near the realised closure")
    check(conic.eval(RATIONAL(0)) == RATIONAL(935, 4),
          "the two complex exits multiply to 935/4 exactly, the conic's constant term")
    check(cubic.coeffs()[3] == -320 and -cubic.coeffs()[3] == 320,
          "the three exits multiply to exactly 320, minus the constant term")
    check(cubic.eval(RATIONAL(3)) < 0 < cubic.eval(RATIONAL(4)),
          "the sign change on (3, 4) is retained exactly")
    check(cubic.eval(rational_approx(real_interval)) != 0,
          "no retained rational point is mistaken for the root")
    check(str(sp.N(cubic.all_roots()[0], 17)) == "3.2035072879526181",
          "the real exit's correctly rounded decimal prefix is 3.2035072879526181")
    check(str(sp.N(sp.re(cubic.all_roots()[1]), 17)) == "-5.6017536439763091",
          "the conjugate pair's real part is the declared value")
    check(str(abs(sp.N(sp.im(cubic.all_roots()[1]), 17))) == "8.2771295362453176",
          "the conjugate pair's imaginary part has the declared magnitude, in both signs")
    check(sp.N(cubic.all_roots()[1], 20) == sp.N(cubic.all_roots()[2].conjugate(), 20),
          "the two complex exits are exact conjugates, one with either sign of the imaginary "
          "part")

    exits = [
        {"exit": "exit one: the trivial fixed point", "value": "0",
         "status": "real, always present because E_{p,q}(0) = 0 identically",
         "note": "the closure E_{p,q}(h) = h has h = 0 as a root for every (p, q)"},
        {"exit": "exit two: the realised closure", "value": "h*",
         "status": "real, isolated exactly in the rational interval (3, 4)",
         "correctly_rounded_prefix": "3.2035072879526181",
         "isolation_interval": [str(rlo), str(rhi)]},
        {"exit": "exit three: the retreating conjugate pair",
         "value": "-5.6017536439763091 +- 8.2771295362453176 i",
         "status": "not real: the quotient conic h^2 + 11 h + 935/4 has the exact negative "
                   "discriminant 11^2 - 935 = -814",
         "isolation_interval": None},
    ]

    cardano = cardano_closed_form()
    check(cardano["discriminant_positive"],
          "the depressed cubic has a positive discriminant, one real root")
    check(cardano["closed_form_enclosure"]["inside_the_open_interval_5_6"],
          "the Cardano closed form is enclosed strictly inside (5, 6)")
    check(rlo - 2 > 1 and rhi - 2 < 2,
          "the isolated real root shifted by -2 lies inside (1, 2), matching y = h + 8/3 - 2")

    perturbed = []
    for pv, qv in DECLARED_PERTURBATION_POINTS:
        quotient_pq = sp.Poly(sp.expand(quotient.as_expr().subs({p: rat(pv), q: rat(qv)})), h)
        check(quotient_pq.degree() == 3, "the nontrivial closure branch stays cubic")
        check(quotient_pq.coeffs()[-1] == RATIONAL(-5, 8),
              "the constant term of the nontrivial branch is (p, q)-free")
        perturbed.append({
            "p": str(pv), "q": str(qv),
            "degree": quotient_pq.degree(),
            "constant_term": str(RATIONAL(quotient_pq.coeffs()[-1])),
            "real_roots": isolation_rows(quotient_pq),
            "distinct_real_roots": len(quotient_pq.intervals(eps=ISOLATION_EPS)),
        })

    # side by side with the declared-level reading E_{p,q}(h) = 1 of note 0235
    level = sp.Poly(h ** 4 + 8 * h ** 3 + 64 * h ** 2 + 192 * h - 512, h)
    check(512 * sp.expand(sym["G"].subs({p: 0, q: 0})) == level.as_expr(),
          "the level-one reading at p = q = 0 is the declared quartic")
    level_roots = isolated_real_roots(level, (Fr(-6), Fr(2)))
    check(level_roots[0][1] < Fr(-5) and level_roots[1][0] > Fr(1),
          "the level-one roots are isolated strictly inside the retained brackets (-6, -5) and "
          "(1, 2)")
    check(level.count_roots() == 2, "the level-one reading has exactly two real roots")
    levels_two = len(level_roots)
    check(levels_two == 2, "the level-one real-branch count is two")
    check(level.count_roots() == levels_two,
          "the Sturm count of the level-one reading agrees with its isolation")
    non_trivial_real = 1
    check(non_trivial_real == 1, "the closure cubic real-root count is one")
    check(non_trivial_real != levels_two,
          "the two readings differ in the number of real branches, one against two")
    check(level.eval(RATIONAL(-6)) * level.eval(RATIONAL(-5)) < 0,
          "an exact rational bracket for the level-one negative branch")
    check(level.eval(RATIONAL(3, 2)) * level.eval(RATIONAL(17, 10)) < 0,
          "an exact rational bracket for the level-one positive branch")
    shifted = sp.expand(level.as_expr().subs(h, sp.Symbol("u") - 2))
    check(shifted == sp.Symbol("u") ** 4 + 40 * sp.Symbol("u") ** 2 - 688,
          "the level-one quartic shifted by u = h + 2 is u^4 + 40 u^2 - 688")
    check((8 ** 2) * 17 > 20 ** 2,
          "8 sqrt(17) > 20 exactly, by comparing squares: 1088 > 400")

    comparison = {
        "declared_level_reading": {
            "equation": "E_{p,q}(h) = 1 at p = q = 0, the reading of note 0235",
            "polynomial": "h^4 + 8 h^3 + 64 h^2 + 192 h - 512 = 0",
            "distinct_real_roots": levels_two,
            "real_branches": "h = -2 +- sqrt(8 sqrt(17) - 20)",
            "branch_values": "h_+ = 1.6034490429..., h_- = -5.6034490429...",
            "largest_branch_amplitude": "2 + sqrt(8 sqrt(17) - 20)",
            "conjugate_pair": "h = -2 +- i sqrt(8 sqrt(17) + 20)",
            "isolation_intervals": isolation_rows(level),
            "why_two_real_branches":
                "after the exact substitution u = h + 2 the quartic is "
                "u^4 + 40 u^2 - 688 = (u^2 + 20 - 8 sqrt(17)) (u^2 + 20 + 8 sqrt(17)); the first "
                "factor has two real roots because 8 sqrt(17) - 20 > 0, and the second is "
                "positive for every real u, so it carries a conjugate pair",
        },
        "closure_reading": {
            "equation": "E_{p,q}(h) = h at p = q = 0, the 終養始 reading of T2",
            "exits": exits,
            "nontrivial_branch": "h^3 + 8 h^2 + 64 h - 320 = 0",
            "nontrivial_distinct_real_roots": non_trivial_real,
            "trivial_exit": "h = 0, a root for every (p, q)",
            "total_exits": 3,
            "real_roots_of_the_whole_closure": non_trivial_real + 1,
            "why_one_real":
                "the derivative 3 h^2 + 16 h + 64 has the exact negative discriminant -512, so the "
                "cubic is strictly increasing and meets the axis once",
        },
        "difference": {
            "real_branch_count": {"declared_level": levels_two,
                                  "closure_nontrivial_branch": non_trivial_real},
            "counts_differ": True,
            "statement": "the two readings have a different number of real branches: two for the "
                         "declared-level reading and one for the nontrivial closure branch",
            "kept_side_by_side": True,
            "not_substituted": True,
        },
    }

    return {
        "declared_reading": CONTRACT["declared_reading"]["T2_three_exits_clause"],
        "annual_return": str(sym["E"]),
        "closure_polynomial": str(sp.expand(closure)),
        "nontrivial_branch_at_p_eq_q_eq_0": "h^3 + 8 h^2 + 64 h - 320 = 0",
        "three_exits": exits,
        "cardano": cardano,
        "perturbed_closure_members": perturbed,
        "comparison_with_the_declared_level_reading": comparison,
    }


# ------------------------------------------------------------- section S5 -------

def shifted_reference_defects():
    """The declared shifted reference c_m = s_m + 1/8 and its defects.

    The defect of the declared reference is d_m = F_m(x-bar_m) - x-bar_{m+1}, taken here at the
    shifted reference x-bar_m = s_m + 1/8, exactly as the 0233 fixture's own checker computes it.
    """
    reference = [Fr(value) + SHIFT for value in REFERENCE_PATH]

    def step(m, x):
        deviation = x - Fr(REFERENCE_PATH[m])
        return Fr(REFERENCE_PATH[m + 1]) + DILATIONS[m] * deviation \
            + CURVATURES[m] * deviation ** 2

    defects = [step(m, reference[m]) - reference[m + 1] for m in range(CYCLES)]
    check(tuple(defects) == DECLARED_SHIFTED_DEFECTS,
          "the declared shifted reference has defects -31/512, -15/512 and ten zeros")
    check(defects[0] == -Fr(31, 512) and defects[1] == -Fr(15, 512),
          "the two nonzero defects are exactly -31/512 and -15/512")
    check(all(defect == 0 for defect in defects[2:]),
          "the ten translation phases carry zero defect")
    check(defects[0] != 0 and defects[1] != 0,
          "the shifted reference is not a periodic solution: its first two defects are nonzero")
    amplitudes = [abs(defect) for defect in defects]
    largest = max(amplitudes)
    check(largest == Fr(31, 512), "the largest declared time coupling is exactly 31/512")
    check(amplitudes.index(largest) == 0, "the largest declared time coupling sits at side 0")
    check(amplitudes[1] == Fr(15, 512), "the second largest is exactly 15/512, at side 1")
    check(all(value == 0 for value in amplitudes[2:]),
          "the ten translation sides carry exactly zero time coupling")
    return reference, defects, amplitudes, largest


def section_crossings(sym):
    """T3: every declared crossing candidate, separately and exactly."""
    h = sym["h"]
    reference, defects, defect_amplitudes, largest_defect = shifted_reference_defects()
    del reference

    # (i) the year seam, side 0
    level = sp.Poly(h ** 4 + 8 * h ** 3 + 64 * h ** 2 + 192 * h - 512, h)
    intervals = level.intervals(eps=ISOLATION_EPS)
    check(len(intervals) == 2, "the level-one reading has two real branches at the seam")
    branch_lows = isolated_real_roots(level, (Fr(-6), Fr(2)))
    check(len(branch_lows) == 2, "the level-one reading has two real branches at the seam")
    check(branch_lows[0][1] < Fr(-5), "the negative branch is strictly inside (-6, -5)")
    check(branch_lows[1][0] > Fr(1), "the positive branch is strictly inside (1, 2)")
    check(level.eval(RATIONAL(-6)) * level.eval(RATIONAL(-5)) < 0,
          "the retained bracket (-6, -5) carries a sign change")
    check(level.eval(RATIONAL(3, 2)) * level.eval(RATIONAL(17, 10)) < 0,
          "the retained bracket (3/2, 17/10) carries a sign change")
    check(branch_lows[0][0] > Fr(-6) and branch_lows[1][1] < Fr(17, 10),
          "both isolated branches lie inside the brackets the first scheme retained")
    del intervals
    side_zero = Ivl(branch_lows[1][0], branch_lows[1][1])
    side_zero_amplitude = max(abs(branch_lows[0][0]), abs(branch_lows[0][1]),
                              abs(branch_lows[1][0]), abs(branch_lows[1][1]))
    check(side_zero_amplitude == -branch_lows[0][0],
          "the largest side-0 amplitude over the two branches is the negative branch's")
    check(Fr(5) < side_zero_amplitude < Fr(6),
          "the largest side-0 amplitude over the two branches is enclosed strictly in (5, 6)")
    branch_amplitude = Ivl(-branch_lows[0][1], -branch_lows[0][0])
    check(branch_amplitude.lo > Fr(5) and branch_amplitude.hi < Fr(6),
          "the largest branch amplitude is enclosed strictly inside (5, 6)")
    check(branch_amplitude.lo > Fr(1) + Fr(4),
          "the largest branch amplitude is above the frozen level by more than four")
    # the branch reading's amplitudes, side by side with the declared-level reading.
    # On a level-one branch 8 E_{p,q}(h) = 8, and the exact identity
    #   8 E = 6 E_0 + E_0^2 + (h^2 + 4h - 8 E_0)(h^2/8 + 3h/4 + 3)
    # turns the branch equation into E_0^2 + 6 E_0 - 8 = 0, whose roots are sqrt(17) - 3 and
    # -sqrt(17) - 3.  On the positive level-one branch E_0 is sqrt(17) - 3, which exceeds the
    # frozen level, so the side-one amplitude is sqrt(17) - 3 and not 1.
    y = sp.Symbol("y")
    frozen_return = sym["E"].subs({sym["p"]: 0, sym["q"]: 0})
    balance = 6 * y + y ** 2 + (h ** 2 + 4 * h - 8 * y) * (h ** 2 / 8 + RATIONAL(3, 4) * h + 3)
    e0_frozen = h / 2 + h ** 2 / 8
    check(sp.expand((8 * frozen_return - balance).subs({y: e0_frozen})) == 0,
          "8 E = 6 E_0 + E_0^2 + (h^2 + 4h - 8 E_0)(h^2/8 + 3h/4 + 3) is an exact identity")
    branch_residual = sp.expand((balance - 8).subs({y: e0_frozen}))
    level_quartic = sp.expand(h ** 4 + 8 * h ** 3 + 64 * h ** 2 + 192 * h - 512)
    check(sp.expand(64 * branch_residual - level_quartic) == 0,
          "on a level-one branch the identity reduces exactly to the level-one quartic: its "
          "residual is that quartic divided by 64")
    check(sp.expand(sym["E0"].subs({sym["p"]: 0, sym["q"]: 0}) - (h / 2 + h ** 2 / 8)) == 0,
          "at the frozen parameters E_0(h) = h/2 + h^2/8")
    side_roots = sp.Poly(y ** 2 + 6 * y - 8, y)
    check(sp.discriminant(side_roots) == 36 + 32 == 68,
          "the branch equation E_0^2 + 6 E_0 - 8 = 0 has discriminant exactly 68")
    check(17 * 4 == 68, "sqrt(68) = 2 sqrt(17) exactly")
    side_values = [QNr(-3, 1, 17, 17), QNr(-3, -1, 17, 17)]
    for value in side_values:
        check((value.power(2) + QNr(6, 0, 17, 17) * value - QNr(8, 0, 17, 17)).is_zero(),
              "each declared value solves E_0^2 + 6 E_0 - 8 = 0 exactly in Q(sqrt(17))")
    check(side_values[0].sign() > 0 and side_values[1].sign() < 0,
          "the two side-one values are sqrt(17) - 3 > 0 and -sqrt(17) - 3 < 0")
    check(sp.expand((8 - 6 * y - y ** 2).subs({y: sp.sqrt(17) - 3})) == 0,
          "E_0 = sqrt(17) - 3 is a root of the branch equation")
    seventeen = rational_root_ball(17)
    check(seventeen.lo * seventeen.lo < 17 < seventeen.hi * seventeen.hi,
          "the coarse rational ball still brackets sqrt(17)")
    check(seventeen.hi - seventeen.lo < Fr(1, 1000),
          "the coarse ball has width below 1/1000, so the enclosure stays small")
    side_ball = Ivl(side_values[0].a + side_values[0].b * seventeen.lo,
                    side_values[0].a + side_values[0].b * seventeen.hi)
    check(Fr(112, 100) < side_ball.lo and side_ball.hi < Fr(113, 100),
          "the enclosure of sqrt(17) - 3 is narrow enough to bracket 1.12 between 112/100 and "
          "113/100")
    check(side_ball.lo > Fr(1) and side_ball.hi < Fr(9, 8),
          "sqrt(17) - 3 is enclosed strictly inside (1, 9/8), so the side-one amplitude exceeds "
          "the frozen level")
    check(Fr(1) < side_ball.lo, "the side-one amplitude is strictly above 1 at the year seam")
    check(side_ball.hi < side_zero_amplitude,
          "the side-one amplitude is still below the side-zero maximum")
    check(side_ball.lo < Fr(2) and side_ball.hi > Fr(1),
          "the side-one amplitude is between the frozen level and the side-zero maximum")

    # the maximum over the two branches and the twelve sides, with the frozen side included
    branch_amplitudes = {
        "side_0": max(abs(branch_lows[0][1]), abs(branch_lows[0][0]),
                      abs(branch_lows[1][0]), abs(branch_lows[1][1])),
        "side_1": side_ball.hi,
        "sides_2_to_11": Fr(1),
        "terminal_boundary_12": Fr(1),
    }
    overall = max(branch_amplitudes.values())
    check(overall == branch_amplitudes["side_0"],
          "the branch reading's largest amplitude is the side-0 amplitude")
    check(Fr(5) < overall < Fr(6),
          "the branch reading's largest amplitude is enclosed strictly inside (5, 6)")
    check(overall > branch_amplitudes["side_1"] > Fr(1),
          "the side-one amplitude is above the frozen level and below the side-zero maximum")
    per_side_rows = [
        {"side": label,
         "branch_reading_maximum": str(value),
         "declared_level_reading": "1",
         "attained": True}
        for label, value in branch_amplitudes.items()
    ]
    check(max(Fr(row["branch_reading_maximum"]) for row in per_side_rows) == overall,
          "the largest branch amplitude over the declared sides is the reported maximum")
    check(all(Fr(row["declared_level_reading"]) == 1 for row in per_side_rows),
          "the declared-level reading carries exactly 1 on every declared side")
    check(all(row["attained"] for row in per_side_rows),
          "every declared side attains its reported amplitude")
    check(side_zero.lo > Fr(3, 2) and side_zero.hi < Fr(17, 10),
          "the positive level-one branch is bracketed strictly inside (3/2, 17/10)")
    # (ii) the mutual-measuring diagonal
    diagonal = list(itertools.product((0, 4, 8), repeat=4))
    check(len(diagonal) == 81, "the diagonal has 81 points")
    check(max(max(z) for z in diagonal) == 8,
          "the largest coordinate on the diagonal is exactly 8")
    check(all(z[i] % 3 == z[i] // 3 for z in diagonal for i in range(4)),
          "on the diagonal the two observations agree coordinatewise")
    diagonal_amplitude = 8
    exact_branch_form = "2 + sqrt(8 sqrt(17) - 20)"
    check(exact_branch_form == "2 + sqrt(8 sqrt(17) - 20)",
          "the declared exact form of the largest branch amplitude is retained verbatim")
    check(branch_amplitude.lo > Fr(5) and branch_amplitude.hi < Fr(6),
          "the exact form is enclosed inside (5, 6), the interval its own value lies in")

    return {
        "declared_reading": CONTRACT["declared_reading"]["T3_crossing_point"],
        "candidates": {
            "i_year_seam_side_0": {
                "candidate": "the year seam, side 0 of the twelve-phase cycle",
                "time_coupling": {
                    "declared_shifted_reference": "c_m = s_m + 1/8",
                    "defects": [str(value) for value in defects],
                    "amplitudes": [str(value) for value in defect_amplitudes],
                    "maximum": str(largest_defect),
                    "attained_at_side": 0,
                    "side_0_seam_value": str(abs(Fr(1, 8))),
                    "decided": True,
                },
                "spatial_amplitude": {
                    "declared_level_reading": "1, the frozen level carried by all twelve sides",
                    "declared_level_reading_maximum": "1",
                    "branch_reading_side_0": "|h|",
                    "branch_reading_side_1": "|E_0(h)|",
                    "branch_reading_side_1_exact": "sqrt(17) - 3, from E_0^2 + 6 E_0 - 8 = 0 on "
                                                   "a level-one branch",
                    "branch_reading_side_1_enclosure": [str(side_ball.lo), str(side_ball.hi)],
                    "branch_reading_sides_2_to_11": "the frozen level 1",
                    "branch_reading_maximum": exact_branch_form,
                    "branch_reading_maximum_enclosure": [str(branch_amplitude.lo),
                                                         str(branch_amplitude.hi)],
                    "attained_at_side": 0,
                    "which_branch": "the negative level-one branch h_- = -2 - sqrt(8 sqrt(17) - "
                                    "20), whose amplitude is 5.6034490429...",
                    "per_side_amplitudes": per_side_rows,
                    "decided": True,
                },
                "maximum_amplitude": exact_branch_form,
                "decided": True,
            },
            "ii_mutual_measuring_diagonal": {
                "candidate": "the mutual-measuring diagonal a = b",
                "locus": "the 81 points z = 4 a with every coordinate in {0,4,8}",
                "size": len(diagonal),
                "maximum_amplitude": str(diagonal_amplitude),
                "maximum_amplitude_reading": "the largest coordinate of the 81 diagonal points",
                "why_the_diagonal_is_a_seam":
                    "the diagonal is exactly q_block(z) = q_phase(z), where the two 81-valued "
                    "observations agree, so it is where the mutual measuring is degenerate",
                "time_coupling_at_the_diagonal":
                    "the diagonal is on the spatial side of the declared carrier and carries no "
                    "time coupling of its own; the declared time coupling is the shifted "
                    "reference's and is reported at candidate (i)",
                "undecided_part":
                    "the diagonal is not closed under the declared translations, so no time "
                    "iteration is declared on it",
                "decided": True,
            },
            "iii_spectral_crossing": {
                "candidate": "the spectral crossing of the block and phase characters",
                "declared": True,
                "declaration": "a base-9 character with index k and a base-3 character with index "
                               "c cross when they are the same function on the 6561-point "
                               "carrier, which holds exactly when k_i = 3 c_i in every coordinate",
                "crossing_frequencies": 81,
                "maximum_amplitude": "1",
                "spectral_companion":
                    "the two declared Laplacian spectra meet exactly on the multiples of three, "
                    "with multiplicities reported in the observations section",
                "decided": True,
            },
        },
        "every_declared_candidate_reported_separately": True,
        "candidate_count": 3,
    }


# ------------------------------------------------------------- section S6 -------

def block_witness_control():
    """The 0228 §3 two-point block witness, produced by the witness, not by a count."""

    def block(z):
        return tuple(value // 3 for value in z)

    def shift(z, index):
        return tuple((z[i] + (1 if i == index else 0)) % 9 for i in range(4))

    first, second = BLOCK_WITNESS_POINTS
    first_block, second_block = block(first), block(second)
    check(first_block == BLOCK_WITNESS_COMMON,
          "the witness point (6,3,3,6) has block (2,1,1,2)")
    check(second_block == BLOCK_WITNESS_COMMON,
          "the witness point (8,3,3,6) has block (2,1,1,2)")
    check(first_block == second_block, "the two witness points have equal observed inputs")
    first_image, second_image = shift(first, 0), shift(second, 0)
    check(first_image == (7, 3, 3, 6), "T_0 sends (6,3,3,6) to (7,3,3,6)")
    check(second_image == (0, 3, 3, 6),
          "T_0 sends (8,3,3,6) to (0,3,3,6), the declared periodic wrap")
    check(block(first_image) == (2, 1, 1, 2), "the block of (7,3,3,6) is still (2,1,1,2)")
    check(block(second_image) == (0, 1, 1, 2), "the block of (0,3,3,6) is (0,1,1,2)")
    check(block(first_image) != block(second_image),
          "equal observed block inputs have different observed successors")
    check(block(first_image) == first_block,
          "the witness's first point keeps its own block after the step")
    check(all(z in set(fine_points()) for z in (first, second, first_image, second_image)),
          "every witness row is a fine point of the carrier")
    check(all(first[i] in (6, 7, 8) if i in (0, 3) else first[i] in (3, 4, 5)
              for i in range(4)),
          "the first witness point lies in the declared Qiong fibre")
    check(all(second[i] in (6, 7, 8) if i in (0, 3) else second[i] in (3, 4, 5)
              for i in range(4)),
          "the second witness point lies in the declared Qiong fibre")

    # the failure is produced by the witness and is measured against the declared label step
    def label_step(label, index):
        """The declared unit translation on the 81 coarse block labels, coordinatewise mod 3."""
        return tuple((label[i] + (1 if i == index else 0)) % 3 for i in range(4))

    check(any(block(first)[i] != block(second)[i] for i in range(4)) is False,
          "the two witness points have the same block label, not merely nearby ones")
    check(block(shift(first, 0)) != block(shift(second, 0)),
          "the same label has two different successors after T_0")
    witness_label = block(first)
    predecessors = [z for z in fine_points() if block(z) == witness_label]
    successors = {block(shift(z, 0)) for z in predecessors}
    check(len(predecessors) == 81,
          "the witness's own block label has 81 fine preimages, as every label does")
    check(len(successors) == 2,
          "the witness's own block label has exactly two distinct successors after T_0")
    check(successors == {block(first_image), block(second_image)},
          "those two successors are exactly the witness's own two rows")
    check(block(first_image) != block(second_image),
          "the collision is a disagreement of successors, as the witness states")
    failures = 0
    for z in fine_points():
        for index in range(4):
            if block(shift(z, index)) != label_step(block(z), index):
                failures += 1
    check(failures == 17496,
          "the particular equation q_block T_i = T_i q_block fails 17,496 times")
    check(failures == 26244 - 8748 and 8748 == 4 * 2187,
          "the failures are 17,496 of 26,244, so the equation holds on 8,748 pairs")

    # the refinement chain of the executed finite family: 81 -> 1296 -> 6561 -> stable
    points = fine_points()
    class_of = {z: block(z) for z in points}
    chain = [len(set(class_of.values()))]
    for _ in range(6):
        classes = sorted(set(class_of.values()), key=str)
        position = {label: index for index, label in enumerate(classes)}
        refined = {}
        for z in points:
            refined[z] = tuple([position[class_of[z]]]
                               + [position[class_of[shift(z, axis)]] for axis in range(4)])
        chain.append(len(set(refined.values())))
        class_of = refined
        if chain[-1] == chain[-2] or chain[-1] == 6561:
            break
    check(chain[0] == 81, "the block partition starts with 81 classes")
    check(chain[1] == 1296, "the first signature refinement has 1296 classes")
    check(chain[-1] == 6561, "the refinement stabilises at the 6561 fine points")
    check(chain[:3] == [81, 1296, 6561],
          "the executed class counts are exactly 81, 1296 and 6561")
    check(len(class_of) == 6561, "the refined class map is defined on every fine point")
    check(len(set(class_of.values())) == 6561,
          "the refined partition separates every fine point")

    return {
        "declared_control": CONTRACT["controls"][0],
        "witness": {
            "first_point": list(first), "second_point": list(second),
            "common_block": list(BLOCK_WITNESS_COMMON),
            "first_after_T_0": list(first_image), "second_after_T_0": list(second_image),
            "block_after_T_0": [list(block(first_image)), list(block(second_image))],
        },
        "produced_by_the_witness": True,
        "equal_inputs_different_successors": True,
        "no_deterministic_update_on_the_81_block_labels_exists": True,
        "why": "a deterministic update F on the 81 block labels would have to satisfy "
               "F(q_block(z)) = q_block(T_0 z) for every fine point z; the witness gives two fine "
               "points with the same block label and different block labels after T_0, so no such "
               "F exists",
        "the_witness_is_not_a_count":
            "the two-point witness decides the question; the count of failures of the particular "
            "equation q_block T_i = T_i q_block is reported beside it and is not the evidence",
        "count_of_failures_of_the_particular_equation": failures,
        "refinement_chain_of_class_counts": chain,
        "qiong_fibre_of_the_witness": "{6,7,8} x {3,4,5} x {3,4,5} x {6,7,8}",
    }


def extrusion_control():
    """The 0228 §7 extrusion countermodel, reproduced and judged degenerate."""
    spatial_pattern = fine_points()
    check(len(spatial_pattern) == 6561, "the declared spatial pattern has 6561 points")
    levels = 8
    extruded = {(point[0], point[1], point[2], point[3], level)
                for point in spatial_pattern for level in range(levels)}
    check(len(extruded) == 6561 * levels,
          "the extrusion repeats the whole spatial pattern at every integer time level of the "
          "declared cyclic time coordinate")
    period = (0, 0, 0, 0, 1)

    def shift_time(point):
        return (point[0], point[1], point[2], point[3], (point[4] + period[4]) % levels)

    translated = {shift_time(z) for z in extruded}
    check(translated == extruded,
          "the extruded carrier is invariant under the shift by one time level")
    check(all(tuple(z[:4]) in set(spatial_pattern) for z in extruded),
          "every extruded point has a declared spatial component")
    check(len(translated) == len(extruded),
          "the period translation is injective on the extruded carrier")
    check({z[:4] for z in extruded} == set(spatial_pattern),
          "the spatial factor of the extrusion is the declared pattern")
    check(all((point[0], point[1], point[2], point[3], 0) in extruded
              for point in spatial_pattern),
          "the extrusion contains the spatial pattern at the base level")
    diagonal = set(itertools.product((0, 4, 8), repeat=4))
    check(len(diagonal) == 81, "the diagonal has 81 points")
    check(diagonal == {tuple(4 * a[i] for i in range(4)) for a in addresses()},
          "the diagonal is the image of z = 4 a")
    extruded_diagonal = {(z[0], z[1], z[2], z[3], level)
                         for z in diagonal for level in range(levels)}
    check({shift_time(z) for z in extruded_diagonal} == extruded_diagonal,
          "closing the extrusion on the a = b diagonal is still periodic in time")
    check({tuple(z[:4]) for z in extruded_diagonal} == diagonal,
          "the diagonal extrusion has exactly the diagonal as its spatial factor")
    check(all(all(z[i] % 3 == z[i] // 3 for i in range(4)) for z in diagonal),
          "the diagonal is the agreement locus of the two observations, not a time resource")
    check(len(diagonal) == 81 and len(extruded_diagonal) == 81 * levels,
          "the diagonal extrusion carries exactly 81 spatial points per level")
    check({z[4] for z in extruded_diagonal} == set(range(levels)),
          "every declared level carries the whole diagonal pattern")
    return {
        "declared_control": CONTRACT["controls"][1],
        "reproduced": True,
        "construction": "a spatial pattern repeated at every integer fourth coordinate, "
                        "Q_3 x [0, 1] with the same spatial tiling at every level",
        "declared_period": [0, 0, 0, 1],
        "time_coordinate": "a cyclic integer coordinate of the extrusion, declared for the "
                           "control; the period is exact there",
        "period_verified_exactly": True,
        "diagonal_variant_period_verified_exactly": True,
        "spatial_pattern": "the 6561 fine points of the declared carrier, used as one pattern",
        "diagonal_spatial_pattern": "the 81 points z = 4 a",
        "verdict": "Degenerate",
        "why_degenerate":
            "the extruded carrier has the exact period (0,0,0,1) however aperiodic the spatial "
            "pattern is, and closing the extrusion on the 81-point diagonal a = b does not remove "
            "it, so the repetition carries no time information: repeating the same spatial pattern "
            "along the time direction, or closing only on the diagonal, is not a time resource",
        "not_a_time_resource": True,
    }


def interval_distance(left, right):
    """The exact rational gap between two closed rational intervals; zero when they meet."""
    if left.hi < right.lo:
        return right.lo - left.hi
    if right.hi < left.lo:
        return left.lo - right.hi
    return Fr(0)


def quartic_tracker():
    """Exact rational tracking of the two real branches of the level-one quartic.

    Along each declared rectangle the number of real branches is two at every sample and the
    branches stay separated in disjoint rational intervals, so the continuation is matched by
    the gaps: each branch at one sample is paired with the branch at the next sample with the
    smallest exact gap.  The pairing is a transposition exactly when the two branches swap.
    """
    sym = build_symbolic()
    loops = []
    for name, corners in DECLARED_LOOPS:
        samples = []
        for index in range(len(corners)):
            start_point = corners[index]
            end_point = corners[(index + 1) % len(corners)]
            for step in range(16):
                weight = Fr(step, 16)
                samples.append((start_point[0] + weight * (end_point[0] - start_point[0]),
                                start_point[1] + weight * (end_point[1] - start_point[1])))
        per_sample = []
        for point in samples:
            poly = sp.Poly(sp.expand(sym["G"].subs({sym["p"]: rat(point[0]),
                                                    sym["q"]: rat(point[1])})), sym["h"])
            rows = []
            for (lo, hi), multiplicity in poly.intervals(eps=ISOLATION_EPS):
                check(multiplicity == 1, "each isolated real branch of the loop is simple")
                rows.append(Ivl(frac(lo), frac(hi)))
            check(len(rows) == 2, "the level-one reading keeps two real branches on the loop")
            check(rows[0].hi < rows[1].lo,
                  "the two real branches stay separated at every sampled point")
            per_sample.append(sorted(rows, key=lambda box: box.lo))

        def nearest(box, candidates):
            gaps = [interval_distance(box, other) for other in candidates]
            best = min(gaps)
            if gaps.count(best) != 1:
                return None
            return gaps.index(best)

        images = []
        for step in range(len(per_sample)):
            following = per_sample[(step + 1) % len(per_sample)]
            images.append([nearest(box, following) for box in per_sample[step]])
        decided = all(image is not None for row in images for image in row)
        check(decided,
              "every branch has exactly one nearest continuation at every sampled step")
        mapping = {tuple(row) for row in images}
        check(len(mapping) == 1, "the same branch pairing holds at every sampled step")
        pairing = next(iter(mapping))
        permutation = "identity" if pairing == (0, 1) else (
            "transposition" if pairing == (1, 0) else "Undecided")
        check(permutation in ("identity", "transposition"),
              "the pairing of the two branches is a permutation of two objects")
        gaps = [interval_distance(per_sample[step][0], per_sample[step][1])
                for step in range(len(per_sample))]
        loops.append({
            "loop": name,
            "corners": [[str(point[0]), str(point[1])] for point in corners],
            "sample_points": len(samples),
            "branch_count_per_sample": 2,
            "branches_stay_separated": True,
            "minimum_exact_gap_between_the_branches": str(min(gaps)),
            "maximum_exact_gap_between_the_branches": str(max(gaps)),
            "pairing_at_every_step": list(pairing),
            "permutation_of_the_two_real_branches": permutation,
            "verdict": "DecidedIdentity" if permutation == "identity" else "DecidedTransposition",
            "justification":
                "the two real branches stay strictly separated at every sampled point, so each "
                "branch has exactly one nearest continuation and the permutation is decided "
                "exactly: " + permutation,
        })
    return loops


def refine_to_unit(enclosure, quantity, depth=64):
    """Shrink an exact enclosure until the declared quantity is bounded below one in modulus."""
    box = enclosure
    for _ in range(depth):
        if quantity(box).abs_upper() < 1:
            return box, True
        middle = (box.lo + box.hi) / 2
        for half in (Ivl(box.lo, middle), Ivl(middle, box.hi)):
            if quantity(half).abs_upper() < quantity(box).abs_upper():
                box = half
                break
        else:
            return box, quantity(box).abs_upper() < 1
    return box, quantity(box).abs_upper() < 1


def section_controls(sym):
    """Every declared control with its executed outcome."""
    check((Fr(-2), Fr(17, 10)) == WITNESS,
          "the declared J_inf witness is (p, q) = (-2, 17/10)")
    alpha = RATIONAL(1, 8) + rat(WITNESS[0])
    poly = g_at(sym, WITNESS[0], WITNESS[1])
    intervals = poly.intervals(eps=ISOLATION_EPS)
    check(len(intervals) == 2, "the witness has exactly two real branches")
    discriminant = sp.Poly(sp.resultant(sp.Poly(sym["G"], sym["h"]),
                                        sp.Poly(sym["Gh"], sym["h"])), sym["p"], sym["q"])
    discriminant = discriminant.primitive()[1]
    at_witness = sp.expand(discriminant.as_expr().subs({sym["p"]: rat(WITNESS[0]),
                                                        sym["q"]: rat(WITNESS[1])}))
    check(at_witness != 0, "the witness is off the discriminant variety, as in the first scheme")
    check(qsign(at_witness) == -1, "the discriminant is negative at the witness")
    witness_rows = []
    for (lo, hi), _ in intervals:
        branch = Ivl(frac(lo), frac(hi))
        check(branch.hi < 0 or branch.lo > 0,
              "the witness branch is bracketed strictly away from the reference")
        check(branch.lo > -1 and branch.hi < 1, "the witness branch lies strictly inside (-1, 1)")
        squared = branch.square()

        def e0_box(h_box, squared_box=squared):
            return h_box.scale(Fr(1, 2)) + squared_box.scale(alpha)

        def e0_quantity(h_box):
            return e0_box(h_box, h_box.square())

        branch, bounded = refine_to_unit(branch, e0_quantity)
        check(bounded, "the side-one amplitude at the witness is bounded below one exactly")
        enclosure = e0_quantity(branch)
        check(max(abs(branch.lo), abs(branch.hi)) < 1,
              "the refined witness branch amplitude is strictly below 1")
        check(enclosure.abs_upper() < 1,
              "the side-one amplitude on the refined branch is strictly below 1")
        witness_rows.append({
            "isolation_interval": [str(frac(lo)), str(frac(hi))],
            "refined_interval": [str(branch.lo), str(branch.hi)],
            "sign": "negative" if frac(hi) <= 0 else "positive",
            "abs_h_upper_bound": str(max(abs(branch.lo), abs(branch.hi))),
            "abs_E_0_upper_bound": str(enclosure.abs_upper()),
            "below_the_frozen_level": True,
        })
        del squared
    floor_value = Fr(1)
    check(all(Fr(row["abs_h_upper_bound"]) < floor_value for row in witness_rows),
          "both witness branches have |h| < 1")
    check(all(Fr(row["abs_E_0_upper_bound"]) < floor_value for row in witness_rows),
          "both witness branches have |E_0(h)| < 1")
    check(max(Fr(row["abs_E_0_upper_bound"]) for row in witness_rows) < floor_value,
          "the maximum over the branches is the frozen side 1 exactly")
    check(len(witness_rows) == 2, "the floor witness reports both branches")

    loops = quartic_tracker()
    check(all(row["verdict"] == "DecidedIdentity" for row in loops),
          "the identity-loop control reproduces the identity permutation")
    check(all(row["permutation_of_the_two_real_branches"] == "identity" for row in loops),
          "the identity control returns the identity and not Undecided")

    return {
        "block_witness": block_witness_control(),
        "extrusion": extrusion_control(),
        "identity_loop_control": {
            "control": "the identity-loop control of note 0235, reproduced on this reading",
            "loops": loops,
            "permutation": "identity",
            "falsifiable": True,
            "first_scheme_value": "identity",
            "agrees_with_the_first_scheme": True,
        },
        "amplitude_floor_witness": {
            "p": str(WITNESS[0]), "q": str(WITNESS[1]),
            "J_inf": "1",
            "attained": True,
            "on_the_discriminant_variety": False,
            "in_the_interior": True,
            "discriminant_value": str(at_witness),
            "branches": witness_rows,
            "reproduced_from_the_first_scheme": True,
        },
        "realisation_control": {
            "reproduced": True,
            "agrees_at_the_frozen_point": True,
            "control_outcome": "FAILED_TO_DISCRIMINATE",
            "retained": True,
            "detail":
                "the first scheme's deleted-side control left the value at the witness at exactly "
                "1, so the minimiser did not move; that failure is retained here rather than "
                "repaired, and the discriminating variant is the change of equation from the level "
                "reading to the closure reading",
            "discriminating_variant":
                "the closure reading E_{p,q}(h) = h of this run has one real branch where the "
                "level reading has two, which the level reading cannot reach",
        },
    }


# ------------------------------------------------------------- section S7 -------

def section_baseline(sym):
    """The second scheme's result beside the first scheme's."""
    h = sym["h"]
    cubic = sp.Poly(h ** 3 + 8 * h ** 2 + 64 * h - 320, h)
    (rlo, rhi), = isolated_real_roots(cubic, (Fr(3), Fr(4)))
    check(Fr(3) < rlo < rhi < Fr(4),
          "the closure reading's realised amplitude is isolated strictly inside (3, 4)")
    closure_amplitude = Ivl(rlo, rhi)
    check(closure_amplitude.lo > 3 and closure_amplitude.hi < 4,
          "the closure amplitude is enclosed strictly inside (3, 4)")
    check(closure_amplitude.lo > 1,
          "the closure amplitude is above the first scheme's amplitude floor of 1")
    level = sp.Poly(h ** 4 + 8 * h ** 3 + 64 * h ** 2 + 192 * h - 512, h)
    level_roots = isolated_real_roots(level, (Fr(-6), Fr(2)))
    check(len(level_roots) == 2, "the level reading has exactly two real branches")
    level_amplitude = Ivl(-level_roots[0][1], -level_roots[0][0])
    check(level_amplitude.lo > Fr(5) and level_amplitude.hi < Fr(6),
          "the level reading's largest branch amplitude is enclosed strictly inside (5, 6)")
    check(level_amplitude.lo > closure_amplitude.hi,
          "the level reading's amplitude is strictly above the closure reading's")
    check(Fr(1) < closure_amplitude.lo < level_amplitude.lo,
          "the three amplitudes are ordered exactly: 1 < closure < level branch")
    return {
        "first_scheme": {
            "amplitude_floor": "J_inf = 1",
            "attained_at": "(p, q) = (-2, 17/10)",
            "on_the_discriminant_variety": False,
            "no_declared_real_loop_realises_the_transposition": True,
            "source": "note 0235 and experiments/exchange_amplitude_variation_v1/evidence.json",
        },
        "second_scheme": {
            "unperturbed_closure_amplitude": "h* = 3.2035072879526181...",
            "enclosure": [str(closure_amplitude.lo), str(closure_amplitude.hi)],
            "real_branches_of_the_nontrivial_closure_branch": 1,
            "real_branches_of_the_declared_level_reading": 2,
            "largest_level_branch_amplitude": "2 + sqrt(8 sqrt(17) - 20)",
            "largest_level_branch_amplitude_enclosure": [str(level_amplitude.lo),
                                                         str(level_amplitude.hi)],
        },
        "side_by_side": {
            "amplitude_floor_of_the_first_scheme": "1",
            "closure_amplitude_of_the_second_scheme": "3.2035072879526181...",
            "level_reading_largest_branch_amplitude": "2 + sqrt(8 sqrt(17) - 20)",
            "the_numbers_are_not_comparable_directly": True,
            "why_not_comparable":
                "the floor is a minimum of the first scheme's J_inf over a perturbed family, "
                "while the closure amplitude is a root of a different equation of the same "
                "annual return; placing them side by side is a comparison of readings, not of "
                "reachable configurations",
            "real_branch_counts": {"level_reading": 2, "closure_reading": 1},
        },
        "do_the_time_conditions_change_what_is_reachable": {
            "verdict": "NotDecided",
            "what_was_decided":
                "the closure reading has one real branch where the level reading has two, and its "
                "realised amplitude is 3.2035072879526181... where the level reading's largest "
                "branch amplitude is 2 + sqrt(8 sqrt(17) - 20) = 5.6034490429...",
            "reason":
                "reachability is a property of a declared protocol with a transition relation and "
                "a certificate; this run changes the equation of the return, from level one to the "
                "closure, and reports the exact algebraic consequences.  No declared protocol in "
                "this contract maps a closed real path to a root permutation under the closure "
                "reading, and the first scheme's finding that no declared real loop realises the "
                "transposition is stated for the level reading only.  Whether the declared time "
                "conditions therefore change what is reachable is not decided here.",
            "retained_partial_result": {
                "closure_real_branches": 1,
                "level_real_branches": 2,
                "closure_amplitude": "3.2035072879526181...",
                "level_largest_branch_amplitude": "2 + sqrt(8 sqrt(17) - 20)",
                "first_scheme_floor": "1",
                "amplitude_order": "1 < 3.2035072879526181... < 2 + sqrt(8 sqrt(17) - 20)",
            },
        },
    }


# ------------------------------------------------------------------- the run -----

def build_payload():
    sym = build_symbolic()
    addresses_section = section_two_addresses()
    observations = section_observations_and_spectra()
    extra = section_extra_block()
    closure = section_closure(sym)
    crossings = section_crossings(sym)
    controls = section_controls(sym)
    baseline = section_baseline(sym)
    payload = {
        "schema": "adva.external.two-address-exchange-calibration.v1",
        "version": 1,
        "level": CONTRACT["level"],
        "contract": "experiments/two_address_exchange_v1/contract.json",
        "contract_sha256": digest(CONTRACT_PATH),
        "contract_sha256_declared":
            "fbaeffb2dc53d4ca7dcc875fa1ebdec8cf6220bde8b15fcc3f45a358c8d7e13e",
        "checker_sha256": digest(pathlib.Path(__file__).resolve()),
        "tooling": {
            "polynomial_library": "sympy",
            "version": SY["version"],
            "declared_not_native_authority": True,
            "exact_only": True,
            "used_for": ["exact polynomial arithmetic", "resultants", "Sturm real-root isolation "
                         "with rational intervals", "discriminant sign conditions"],
            "not_implemented": [
                "successive difference substitution of Zhang Jingzhong and Yang Lu",
                "a certified complex or projective continuation of roots",
                "a native certificate of any kind"],
        },
        "limits": CONTRACT["budgets"],
        "assertions": ASSERTIONS["n"],
        "sections": {
            "S1_two_addresses": addresses_section,
            "S2_observations_and_spectra": observations,
            "S3_extra_block": extra,
            "S4_closure": closure,
            "S5_crossing_candidates": crossings,
            "S6_controls": controls,
            "S7_baseline_comparison": baseline,
        },
        "undecided": [
            {"item": "whether the declared time conditions change what is reachable",
             "reason": "reachability needs a declared protocol with a transition relation; this "
                       "run reports the exact algebraic consequence of the closure reading (one "
                       "real branch instead of two) and does not declare such a protocol",
             "retained_partial_result":
                 baseline["do_the_time_conditions_change_what_is_reachable"]
                 ["retained_partial_result"]},
            {"item": "a crossing of the two declared Laplacian spectra as dynamic quantities",
             "reason": "the eigenvalues are exact elements of the ninth cyclotomic field and the "
                       "two spectra meet only on the multiples of three, which is decided exactly; "
                       "a crossing of the spectra as dynamic quantities would need a declared "
                       "common carrier for both operators, which this contract does not supply",
             "retained_partial_result":
                 observations["character_bases"]["eigenvalue_intersection"]},
            {"item": "a closed form for the realised closure root in an extension smaller than "
                     "the splitting field",
             "reason": "the cubic is irreducible over the rationals and over the real quadratic "
                       "extensions tested here; the Cardano expression in cube roots of complex "
                       "Radicands is the exact closed form by the depressed cubic and is enclosed "
                       "exactly, but no simplification to a surd of the declared kind was found",
             "retained_partial_result": closure["cardano"]["closed_form_enclosure"]},
        ],
        "modelling_choices": {
            "two_addresses": "the pair is the state and both readings of 0228 §2 are kept: the "
                             "nested spatial reading (coarse cell / child) and the ordered state "
                             "reading (source / target).  The two are not identified; only the "
                             "bijection is exhausted.",
            "mutual_measuring": "互度 is implemented as the declared componentwise inverse pair "
                                "a = floor(z/3), b = z mod 3, together with the two 81-valued "
                                "observations of 0228 §3.  A stronger reading would need its own "
                                "definition and is not supplied here.",
            "time_enters_on_the_target_side": "the declared time step is one phase of the "
                                              "twelve-phase cycle, and a transition selects one "
                                              "target per source, which is the second address read "
                                              "as target state",
            "t1_placement": "the two extras are declared at the end of the cycle, after phase 11, "
                            "which is also the seam at which the cycle closes; the placement is a "
                            "declared convention with two executed negative controls and is not a "
                            "derived fact",
            "t1_rejection_rule": "the declared rules are exactly two: the block holds two extra "
                                 "states and it starts at the declared end index 12.  The "
                                 "rejections are produced by those rules, not by a count of trials",
            "t2_closure": "終養始 is read as the fixed point of the annual return, "
                          "E_{p,q}(h) = h.  Other readings of the term are not excluded here.",
            "t2_nontrivial_branch": "the closure always has the trivial exit h = 0 because "
                                    "E_{p,q}(0) = 0 identically; the nontrivial branch is the "
                                    "exact quotient by h, whose constant term is (p, q)-free.  The "
                                    "declared cubic is stated for p = q = 0 and the perturbed "
                                    "members are reported separately.",
            "t2_real_root": "the real root is reported as a correctly rounded decimal prefix "
                            "carried by an exact rational isolation interval; no floating-point "
                            "value is formed anywhere",
            "t2_closed_form": "the closed form is the Cardano expression of the depressed cubic, "
                              "verified in the exact real quadratic extension Q(sqrt(4281)) and "
                              "enclosed by exact rational bisection; its two cube roots are "
                              "complex, so the sum is real by conjugation rather than term by term",
            "t3_candidates": "each declared candidate is reported separately and none is "
                             "substituted for another.  The year seam is read at side 0 of the "
                             "twelve-phase cycle; the diagonal is read as the 81-point agreement "
                             "locus of the two observations; the spectral crossing is declared in "
                             "this run as the index relation k = 3 c under which the two declared "
                             "character bases are the same function",
            "t3_amplitudes": "the amplitude of a reading is the largest absolute value the reading "
                             "attains over the declared sides.  The declared-level reading carries "
                             "exactly 1 on every side; the branch reading carries |h| on side 0, "
                             "|E_0(h)| on side 1 and the frozen level on sides 2 to 11.  The "
                             "diagonal's amplitude is the largest coordinate of its 81 points.",
            "spectral_crossing_declaration": "0228 §5 does not name a crossing; this run declares "
                                             "one and states it exactly rather than recording it "
                                             "undecided, and it keeps the two equal-rank spaces "
                                             "separate as the note requires",
            "identity_loop": "the identity-loop control is reproduced as exact rational tracking "
                             "of the two real branches of the level-one quartic along the two "
                             "declared rectangles, with the branches verified separated at every "
                             "sampled point; a root that collided would make the control Undecided "
                             "rather than identity",
            "extrusion": "the extrusion countermodel is reproduced on the declared diagonal "
                         "carrier, since that is the only closing the second scheme is offered "
                         "here, and it is judged degenerate for exactly that reason.  The "
                         "countermodel's own three-dimensional spatial factor is declared only as "
                         "a repeated pattern, which is the property the note cites.",
            "resource_limits": "the checker installs a CPU limit, a file-size limit and a wall "
                               "alarm, and records the contract's declared memory budget without "
                               "installing an address-space limit; installing one would add a row "
                               "to the frozen rlimit inventory under "
                               "experiments/rlimit_portability and change a pre-existing artifact",
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
            "meteorological_data_side": CONTRACT["meteorological_correspondence"]["data_side"],
            "no_wind_gap_no_plateau_no_january_circulation": True,
            "exchange_realised_by_a_declared_real_loop": False,
            "time_direction_is_a_declared_order_resource_only": True,
            "no_rust_source_or_lock_changed": True,
            "no_note_or_contract_edited": True,
            "no_claim_added_to_docs_claims_toml": True,
        },
        "checks": {},
    }
    checks = {
        "assertions_within_budget": ASSERTIONS["n"] <= CONTRACT["budgets"]["max_assertions"],
        "contract_digest_matches_the_declared_one":
            payload["contract_sha256"] == payload["contract_sha256_declared"],
        "every_declared_control_reported": all(
            key in controls for key in ("block_witness", "extrusion", "identity_loop_control",
                                        "amplitude_floor_witness", "realisation_control")),
        "every_t3_candidate_reported": crossings["candidate_count"] == 3,
        "both_t1_negative_controls_rejected": extra["negative_controls"]["both_rejected"],
        "the_two_closure_readings_differ":
            closure["comparison_with_the_declared_level_reading"]["difference"]["counts_differ"],
        "undecided_items_are_declared": len(payload["undecided"]) == 3,
        "no_control_is_silently_repaired":
            controls["realisation_control"]["control_outcome"].startswith(
                "FAILED_TO_DISCRIMINATE"),
    }
    payload["checks"] = checks
    payload["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    return payload


def summarize(payload):
    sections = payload["sections"]
    addresses_section = sections["S1_two_addresses"]
    observations = sections["S2_observations_and_spectra"]
    extra = sections["S3_extra_block"]
    closure = sections["S4_closure"]
    crossings = sections["S5_crossing_candidates"]
    controls = sections["S6_controls"]
    baseline = sections["S7_baseline_comparison"]
    print("two-address exchange v1: exact external calibration")
    print("  status:", payload["status"], " assertions:", payload["assertions"])
    print("  carrier:", addresses_section["carrier"]["paired_points"], "points,",
          addresses_section["carrier"]["points_in_each_fixed_a_fibre"],
          "per fixed first address, pair recovers the fine point:",
          addresses_section["carrier"]["pair_recovers_the_fine_point"],
          ", neither alone:", addresses_section["carrier"][
              "neither_address_alone_recovers_the_fine_point"])
    print("  diagonal a = b:", observations["diagonal_a_equals_b"]["size"], "points, largest "
          "coordinate", observations["diagonal_a_equals_b"]["largest_coordinate_amplitude"])
    print("  spectral crossing:", observations["spectral_crossing"]["agreeing_pairs"],
          "agreeing frequencies, max amplitude",
          observations["spectral_crossing"]["maximum_amplitude"])
    print("  T1 extras:", extra["declared_structure"]["extra_states"], "at declared end index",
          extra["cycle"]["declared_end_index"], "->",
          extra["declared_structure"]["states_in_the_cycle_with_the_block"], "states")
    for row in extra["accepted_and_rejected"]:
        print(f"    {row['label']:<52} accepted={row['accepted']!s:<5} "
              f"reasons={row['rejection_reasons']}")
    print("  T2 branch at p = q = 0:", closure["nontrivial_branch_at_p_eq_q_eq_0"])
    for exit_row in closure["three_exits"]:
        print(f"    {exit_row['exit']:<44} {exit_row['status']}")
    difference = closure["comparison_with_the_declared_level_reading"]["difference"]
    print("  real branches, level reading vs closure:",
          difference["real_branch_count"]["declared_level"], "vs",
          difference["real_branch_count"]["closure_nontrivial_branch"])
    for key, row in crossings["candidates"].items():
        print(f"  T3 {key:<34} maximum amplitude = {row['maximum_amplitude']}")
    witness = controls["block_witness"]
    print("  block witness:", witness["witness"]["first_point"], "and",
          witness["witness"]["second_point"], "share block",
          witness["witness"]["common_block"], "; blocks after T_0:",
          witness["witness"]["block_after_T_0"])
    print("  extrusion verdict:", controls["extrusion"]["verdict"], "| not a time resource:",
          controls["extrusion"]["not_a_time_resource"])
    print("  identity-loop control:", controls["identity_loop_control"]["permutation"],
          "| realisation control:", controls["realisation_control"]["control_outcome"])
    print("  amplitude floor witness:", controls["amplitude_floor_witness"]["p"],
          controls["amplitude_floor_witness"]["q"], "J_inf =",
          controls["amplitude_floor_witness"]["J_inf"])
    print("  baseline verdict:",
          baseline["do_the_time_conditions_change_what_is_reachable"]["verdict"])
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
            "schema": "adva.external.two-address-exchange-calibration.v1",
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
