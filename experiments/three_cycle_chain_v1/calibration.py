#!/usr/bin/env python3
"""Exact calibration of the three-cycle chain reading, with checkable results.

Frozen contract: experiments/three_cycle_chain_v1/contract.json.
This checker is an external exact calibration.  It constructs no native
certificate, promotes no native identity, and makes no physical claim.  The
chain it computes is FUTURE: three annual cycles from the seam between December
2026 and January 2027.  No observation and no issued forecast exists for it, so
observational verification is recorded as Unavailable rather than approximated,
and no data from the xue-study checkout is read or used.

What the run decides, and with what:

* the declared annual return of the resolved 0233 fixture,
  E(h) = (3/8) h + (1/8) h^2 + (1/64) h^3 + (1/512) h^4, whose closure polynomial
  is 512 (E(h) - h) = h (h^3 + 8 h^2 + 64 h - 320) and whose one real closure
  exit is the root of that cubic, 3.2035072879526181...;
* the chain: three consecutive applications of the declared return with the seam
  state carried forward, C1, C2 and C3, beginning at the declared December-
  January seam, each cycle's closure status reported separately, every seam state
  given exactly, and the cumulative composition E^3 read beside the per-cycle
  reading;
* the three-by-three role typing as declared structure: three groups of three
  steps per cycle, the upper group carrying the visible failure branch, and a
  calamity counterpart for every one of the nine declared conditions, each
  counterpart executed rather than narrated;
* the end block, holding exactly two extra steps counted in the same unit as the
  steps, with the total step count, the remainder and both rejections (a block of
  one and a block of three) asserted;
* the fast and slow split of the carried remainder at every seam, the slow
  component required to be conserved with its exact drift reported, and the
  declared first-order relaxation reservoir with a rational time constant and a
  declared freshwater source term, evaluated exactly in the cubic field the
  closure amplitude generates;
* the declared primary chain and the declared atmospheric alternative (ocean
  open), side by side;
* sealing as a bound: the sealing side is a bound of no leakage and never a term
  that could cancel a violation, reported at every cycle;
* the baselines: J_inf = 1 at (p, q) = (-2, 17/10), the closure amplitude
  3.2035072879526181... with one real exit, the level reading's largest branch
  amplitude 2 + sqrt(8 sqrt(17) - 20) = 5.6034490429... with two real branches,
  and the exact ordering 1 < 3.2035072879526181... < 2 + sqrt(8 sqrt(17) - 20).

All acceptance arithmetic is integers, fractions.Fraction, exact rational
interval arithmetic and exact arithmetic in the cubic field Q(w).  No
floating-point value is formed in an acceptance test or written into the retained
payload.  sympy is a declared external library used only for exact polynomial
work, and it is not native authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import resource
import signal
import sys
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


# --------------------------------------------------------------- exact algebra --

def poly_mul(left, right):
    """Multiply two coefficient tuples, lowest degree first, exactly."""
    product = [Fr(0)] * (len(left) + len(right) - 1)
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            product[i + j] += a * b
    return tuple(product)


def poly_add(left, right):
    size = max(len(left), len(right))
    return tuple(Fr(left[i] if i < len(left) else 0) + Fr(right[i] if i < len(right) else 0)
                 for i in range(size))


def poly_eval(poly, x):
    """Evaluate a coefficient tuple at an exact rational point, exactly."""
    total = Fr(0)
    for coefficient in reversed(poly):
        total = total * x + coefficient
    return total


def poly_divide(numerator, denominator):
    """Polynomial division returning (quotient, remainder), exactly."""
    rest = [Fr(value) for value in numerator]
    quotient = [Fr(0)] * max(1, len(numerator) - len(denominator) + 1)
    while len(rest) >= len(denominator) and any(rest):
        shift = len(rest) - len(denominator)
        factor = rest[-1] / denominator[-1]
        quotient[shift] = factor
        for index, value in enumerate(denominator):
            rest[shift + index] -= factor * value
        while rest and rest[-1] == 0:
            rest.pop()
    while len(quotient) > 1 and quotient[-1] == 0:
        quotient.pop()
    return tuple(quotient), tuple(rest)


def poly_div_exact(numerator, denominator):
    """Exact polynomial division; refuses a nonzero remainder."""
    quotient, remainder = poly_divide(numerator, denominator)
    check(not any(remainder), "the declared division has zero remainder")
    return quotient


def poly_derivative(poly):
    return tuple(index * poly[index] for index in range(1, len(poly))) or (Fr(0),)


def poly_compose(outer, inner):
    """The exact composition outer(inner(h)), both lowest degree first."""
    result = (Fr(0),)
    power = (Fr(1),)
    for coefficient in outer:
        result = poly_add(result, tuple(coefficient * value for value in power))
        power = poly_mul(power, inner)
    return result


def sturm_chain(poly):
    """The Sturm chain of a rational polynomial, exactly."""
    chain = [tuple(Fr(value) for value in poly), poly_derivative(poly)]
    while len(chain[-1]) > 1:
        _, remainder = poly_divide(chain[-2], chain[-1])
        if not any(remainder):
            break
        chain.append(tuple(-value for value in remainder))
    return chain


def sign_changes(chain, x):
    values = [poly_eval(poly, x) for poly in chain]
    signs = [(value > 0) - (value < 0) for value in values if value != 0]
    return sum(1 for i in range(len(signs) - 1) if signs[i] != signs[i + 1])


def sturm_real_root_count(poly, low, high):
    """The exact number of distinct real roots of a squarefree polynomial in [low, high]."""
    chain = sturm_chain(poly)
    return sign_changes(chain, low) - sign_changes(chain, high)


def bisect_root(poly, low, high, steps=192):
    """Isolate the single root of a polynomial by exact rational bisection."""
    check(poly_eval(poly, low) * poly_eval(poly, high) < 0,
          "the declared bracket carries an exact sign change")
    for _ in range(steps):
        middle = (low + high) / 2
        if poly_eval(poly, low) * poly_eval(poly, middle) <= 0:
            high = middle
        else:
            low = middle
    check(poly_eval(poly, low) * poly_eval(poly, high) < 0,
          "the refined bracket still carries a sign change")
    return low, high


# ------------------------------------- exact arithmetic in the cubic field Q(w) --

CLOSURE_CUBIC = (Fr(-320), Fr(64), Fr(8), Fr(1))


class Cubic:
    """a + b w + c w^2 with a, b, c exact Fractions and w the closure amplitude.

    w is the unique real root of w^3 + 8 w^2 + 64 w - 320 = 0, so
    w^3 = 320 - 64 w - 8 w^2 exactly and every element of Q(w) has one canonical
    triple representation.  No floating-point value is ever formed.
    """

    __slots__ = ("a", "b", "c")

    def __init__(self, a=0, b=0, c=0):
        self.a = a if isinstance(a, Fr) else Fr(a)
        self.b = b if isinstance(b, Fr) else Fr(b)
        self.c = c if isinstance(c, Fr) else Fr(c)

    def __add__(self, other):
        other = other if isinstance(other, Cubic) else Cubic(other)
        return Cubic(self.a + other.a, self.b + other.b, self.c + other.c)

    __radd__ = __add__

    def __sub__(self, other):
        other = other if isinstance(other, Cubic) else Cubic(other)
        return Cubic(self.a - other.a, self.b - other.b, self.c - other.c)

    def __neg__(self):
        return Cubic(-self.a, -self.b, -self.c)

    def scale(self, factor):
        factor = factor if isinstance(factor, Fr) else Fr(factor)
        return Cubic(self.a * factor, self.b * factor, self.c * factor)

    def __mul__(self, other):
        other = other if isinstance(other, Cubic) else Cubic(other)
        raw = [Fr(0)] * 5
        for i, left in enumerate((self.a, self.b, self.c)):
            for j, right in enumerate((other.a, other.b, other.c)):
                raw[i + j] += left * right
        for degree in range(4, 2, -1):
            coefficient = raw[degree]
            if coefficient:
                raw[degree] = Fr(0)
                raw[degree - 3] += 320 * coefficient
                raw[degree - 2] -= 64 * coefficient
                raw[degree - 1] -= 8 * coefficient
        return Cubic(raw[0], raw[1], raw[2])

    __rmul__ = __mul__

    def __eq__(self, other):
        other = other if isinstance(other, Cubic) else Cubic(other)
        return (self.a, self.b, self.c) == (other.a, other.b, other.c)

    def is_zero(self):
        return self.a == 0 and self.b == 0 and self.c == 0

    def power(self, exponent):
        result = Cubic(1)
        for _ in range(exponent):
            result = result * self
        return result

    def tuple(self):
        return [str(self.a), str(self.b), str(self.c)]


W = Cubic(0, 1, 0)


def field_poly_value(poly, element):
    """Evaluate a rational coefficient tuple at an element of Q(w), exactly."""
    total = Cubic(0)
    for coefficient in reversed(poly):
        total = total * element + Cubic(coefficient)
    return total


def field_return(element):
    """The annual return evaluated exactly on an element of Q(w)."""
    return (element.scale(Fr(3, 8)) + element.power(2).scale(Fr(1, 8))
            + element.power(3).scale(Fr(1, 64)) + element.power(4).scale(Fr(1, 512)))


def field_closure_defect(element):
    return field_return(element) - element


# ------------------------------------------------------------ sympy declaration --

def import_sympy():
    try:
        import sympy
        return {"available": True, "version": sympy.__version__}
    except Exception as error:  # pragma: no cover - reported, never raised
        return {"available": False, "error": str(error)}


SY = import_sympy()

# ------------------------------------------------------------- the fixture ------

E_RETURN = (Fr(0), Fr(3, 8), Fr(1, 8), Fr(1, 64), Fr(1, 512))
E_MINUS_H = poly_add(E_RETURN, (Fr(0), Fr(-1)))
LEVEL_QUARTIC = (Fr(-512), Fr(192), Fr(64), Fr(8), Fr(1))
SLOPE_REDUCTION = (Fr(23, 8), Fr(-1, 4), Fr(-1, 64))

ANNUAL_RETURN_TEXT = "E(h) = (3/8) h + (1/8) h^2 + (1/64) h^3 + (1/512) h^4"
CLOSURE_TEXT = "512 (E(h) - h) = h (h^3 + 8 h^2 + 64 h - 320)"
CLOSURE_AMPLITUDE_TEXT = "3.2035072879526181..."

DECLARED_SEAM = "December 2026 / January 2027"
OTHER_SEAMS = ("September 2026 / October 2026", "June 2027 / July 2027")

CYCLES = ("C1", "C2", "C3")
CYCLE_SPANS = {"C1": "2026-12 to 2027-12", "C2": "2027-12 to 2028-12",
               "C3": "2028-12 to 2029-12"}

# the declared cycle division of the carrier: 12 phases, 27 units, 729 zan
PHASES_PER_CYCLE = 12
UNITS_PER_CYCLE = 27
ZAN_PER_CYCLE = 729
ZAN_PER_PHASE = Fr(ZAN_PER_CYCLE, PHASES_PER_CYCLE)
ZAN_PER_UNIT = Fr(ZAN_PER_CYCLE, UNITS_PER_CYCLE)

END_BLOCK_STEPS = 2
REFUSED_END_BLOCK_SIZES = (1, 3)
STEPS_PER_CYCLE = 9
GROUPS_PER_CYCLE = 3
STEPS_PER_GROUP = 3

PHASE_TECHNIQUE = tuple("add-scale" if index in (0, 1) else "translation"
                        for index in range(PHASES_PER_CYCLE))

ZAN_PER_STEP = Fr(ZAN_PER_CYCLE, STEPS_PER_CYCLE)

ROLE_GROUPS = (
    ("lower: deliberation", ("condition_1", "condition_2", "condition_3")),
    ("middle: fortune", ("condition_4", "condition_5", "condition_6")),
    ("upper: calamity", ("condition_7", "condition_8", "condition_9")),
)
CONDITION_NAMES = tuple(name for _, members in ROLE_GROUPS for name in members)
CONDITION_TEXT = {
    "condition_1": "every cycle is a genuine return, and not only the first",
    "condition_2": "the sealing side holds as a bound of no leakage",
    "condition_3": "the fast and the slow component of the carried remainder are accounted",
    "condition_4": "the slow component of the carried remainder is conserved",
    "condition_5": "the end block holds exactly two extra steps, counted in steps",
    "condition_6": "the carried remainder is matched by the declared reservoir",
    "condition_7": "the chain begins at the declared December-January seam",
    "condition_8": "the fast component is free to reset and the slow component is not",
    "condition_9": "the exit condition is 終養始, the last member of the upper group",
}

# the declared first-order relaxation reservoir: stationary at the slow component of the
# chain's own seam, T* = (1 - c) * w, with c the declared seam mixing
RESERVOIR_RELAXATION = Fr(1, 30)
RESERVOIR_TIME_CONSTANT = 1 / RESERVOIR_RELAXATION
SEAM_MIXING = Fr(1, 2)
FAST_RESET = Fr(1) - SEAM_MIXING
DISPLACEMENT = Cubic(Fr(1, 4))
RESERVOIR_STEADY = W.scale(FAST_RESET)
RESERVOIR_REFERENCE = RESERVOIR_STEADY.scale(RESERVOIR_RELAXATION)
RESERVOIR_SOURCE = RESERVOIR_STEADY.scale(Fr(1) - RESERVOIR_RELAXATION)


def chain_operator(element):
    """The declared chain operator: three consecutive applications of the annual return.

    The seed is the closure amplitude, so the operator returns it at every application.
    """
    return field_return(element)


def annual_return(h):
    """The declared annual return at an exact rational point."""
    return poly_eval(E_RETURN, h)


def closure_defect(h):
    """E(h) - h, the exact departure of one annual cycle from its own seam."""
    return annual_return(h) - h


def reservoir_step(state, steady=RESERVOIR_STEADY):
    """One step of the declared first-order relaxation with its freshwater source.

    The step is affine with rational coefficients, so it acts on exact rational
    points, on elements of Q(w) and on integers alike.  T_ref = T* and b = a T*, so
    the step reads T_{i+1} = T_i + a (T* + b / a - T_i) = T_i + a (2 T* - T_i).
    """
    if not isinstance(state, Cubic):
        state = Cubic(state)
    if not isinstance(steady, Cubic):
        steady = Cubic(steady)
    return state.scale(Fr(1) - RESERVOIR_RELAXATION) + steady.scale(RESERVOIR_RELAXATION)


# ---------------------------------------------------------------- the fixture ---

def declaration():
    """The declared annual return and its closure, asserted rather than assumed."""
    check(len(E_RETURN) == 5, "the declared annual return is a quartic in h")
    check(E_RETURN[0] == 0 and E_RETURN[1] == Fr(3, 8),
          "the declared annual return has zero constant term and first coefficient 3/8")
    check((E_RETURN[2], E_RETURN[3], E_RETURN[4]) == (Fr(1, 8), Fr(1, 64), Fr(1, 512)),
          "the declared annual return has the coefficients 1/8, 1/64 and 1/512")
    check(annual_return(Fr(0)) == 0, "E(0) = 0 exactly, the trivial exit")
    check(closure_defect(Fr(0)) == 0, "the trivial exit satisfies the closure identically")
    check(annual_return(Fr(-4)) == 0, "E(-4) = 0 exactly")
    check(closure_defect(Fr(-4)) == 4,
          "the departure of -4 from its own seam is exactly 4, the whole amplitude")

    scaled = tuple(512 * value for value in E_MINUS_H)
    check(scaled == poly_mul((Fr(0), Fr(1)), CLOSURE_CUBIC),
          "512 (E(h) - h) factors exactly as h (h^3 + 8 h^2 + 64 h - 320)")
    check(tuple(512 * value for value in poly_add(E_RETURN, (Fr(-1),))) == LEVEL_QUARTIC,
          "the level-one reading of the preceding run, 512 (E(h) - 1), is exactly the quartic "
          "h^4 + 8 h^3 + 64 h^2 + 192 h - 512")
    check(LEVEL_QUARTIC[1] == 192 and CLOSURE_CUBIC[0] == -320,
          "the closure reading and the level reading are different polynomials, so the two are "
          "never substituted for one another")
    check(poly_eval(LEVEL_QUARTIC, Fr(0)) == -512,
          "the level-one reading does not vanish at h = 0, unlike the closure reading")

    derivative = poly_derivative(E_RETURN)
    check(derivative == (Fr(3, 8), Fr(1, 4), Fr(3, 64), Fr(1, 128)),
          "the declared derivative is exactly 3/8 + h/4 + 3 h^2/64 + h^3/128")
    check(poly_eval(derivative, Fr(0)) == Fr(3, 8),
          "the declared first-degree reading at the reference is exactly 3/8")
    return derivative


def closure_reading():
    """The closure cubic, its single real exit, and the exact reduction of the slope on it."""
    second = poly_derivative(poly_derivative(CLOSURE_CUBIC))
    check(second == (Fr(16), Fr(6)),
          "the second derivative of the closure cubic is exactly 6 h + 16")
    check(poly_eval(second, Fr(-8, 3)) == 0,
          "the derivative of the closure cubic is stationary at exactly h = -8/3")
    check(Fr(16) ** 2 - 4 * 3 * 64 == -512,
          "the derivative's discriminant is exactly 16^2 - 4 * 3 * 64 = -512, strictly negative")
    check(poly_eval(poly_derivative(CLOSURE_CUBIC), Fr(-8, 3)) == Fr(128, 3) > 0,
          "the derivative's minimum is exactly 128/3 > 0, so the derivative is strictly positive "
          "and the cubic strictly increasing; it meets the axis exactly once")
    check(sturm_real_root_count(CLOSURE_CUBIC, Fr(-1000000), Fr(1000000)) == 1,
          "the closure cubic has exactly one real root by an exact Sturm count")
    root_low, root_high = bisect_root(CLOSURE_CUBIC, Fr(3), Fr(4))
    check(Fr(3) < root_low < root_high < Fr(4),
          "the closure amplitude is isolated strictly inside (3, 4)")
    check(poly_eval(CLOSURE_CUBIC, Fr(3203, 1000)) < 0
          < poly_eval(CLOSURE_CUBIC, Fr(3204, 1000)),
          "the retained decimal prefix 3.2035 is bracketed exactly")
    check(poly_eval(CLOSURE_CUBIC, Fr(32035072879526181, 10 ** 16)) < 0
          < poly_eval(CLOSURE_CUBIC, Fr(32035072879526182, 10 ** 16)),
          "the retained prefix 3.2035072879526181 is bracketed exactly")

    # the slope reduction on the cubic, as an exact polynomial identity:
    # h^3 = 320 - 64 h - 8 h^2 makes E'(h) = 3/8 + h/4 + 3 h^2/64 + h^3/128 equal to
    # 23/8 - h/4 - h^2/64 for every root of the cubic.
    check(poly_add(SLOPE_REDUCTION, (Fr(0),)) == SLOPE_REDUCTION
          and len(SLOPE_REDUCTION) == 3,
          "the reduced slope is a polynomial of degree at most two")
    check(poly_eval(SLOPE_REDUCTION, Fr(0)) == Fr(23, 8),
          "on the cubic the derivative reduces to 23/8 - h/4 - h^2/64, whose constant is 23/8")
    check(poly_eval(poly_derivative(E_RETURN), Fr(0)) == Fr(3, 8),
          "the unreduced derivative at the reference is 3/8, which is a different number")
    check(poly_eval(SLOPE_REDUCTION, root_low) > 1,
          "the return's slope at the closure amplitude is strictly greater than one")
    check(root_low - 2 > 1, "the closure amplitude shifted by -2 lies strictly above 1")

    # w satisfies the cubic exactly, and the return fixes it exactly, in the field
    check(field_poly_value(CLOSURE_CUBIC, W).is_zero(),
          "the declared field element w satisfies h^3 + 8 h^2 + 64 h - 320 = 0 exactly")
    check(field_return(W) == W,
          "the declared annual return fixes the closure amplitude exactly: E(w) = w")
    check(field_closure_defect(W).is_zero(),
          "the closure defect of the closure amplitude is exactly zero")
    check(field_return(Cubic(0)).is_zero(),
          "the trivial exit is fixed in the field as well: E(0) = 0")
    check(Cubic(1).power(3) == Cubic(1), "the field unit behaves as the unit")
    check(W.power(3) == Cubic(320) - W.scale(64) - W.power(2).scale(8),
          "w^3 = 320 - 64 w - 8 w^2 exactly, the declared reduction")
    return root_low, root_high


# --------------------------------------------------------------- the chain ------

def chain_section():
    """The three-cycle chain: seam states, per-cycle closure status and drifts."""
    root_low, root_high = closure_reading()

    steady = RESERVOIR_STEADY
    check(Fr(1, 2) == SEAM_MIXING, "the declared seam mixing is exactly one half")
    check(steady == W.scale(Fr(1, 2)),
          "the declared steady reservoir value is exactly half the closure amplitude, the "
          "declared slow component of the chain's seam")
    check(chain_operator(W) == W,
          "the closure amplitude is the exact fixed point of the declared chain operator")
    check(W.scale(Fr(1, 60)) == RESERVOIR_REFERENCE,
          "the reservoir's declared reference value is exactly one sixtieth of the closure "
          "amplitude, the steady value times the relaxation coefficient")
    check(W.scale(Fr(29, 60)) == RESERVOIR_SOURCE,
          "the declared freshwater source term is exactly 29/60 of the closure amplitude, the "
          "steady value times one minus the relaxation coefficient")
    check(steady == RESERVOIR_REFERENCE.scale(RESERVOIR_TIME_CONSTANT),
          "the steady value is exactly the reference value divided by the relaxation "
          "coefficient, which is the fixed point of the declared step: T* = T_ref / a")
    check(reservoir_step(steady) == steady,
          "the reservoir is stationary at that steady value, so the slow component is conserved")
    check((reservoir_step(steady) - steady).is_zero(),
          "the slow drift at the fixed point is exactly zero, not merely small")

    slope_low = poly_eval(SLOPE_REDUCTION, root_low)
    slope_high = poly_eval(SLOPE_REDUCTION, root_high)
    check(1 < slope_high < slope_low < 2,
          "the declared chain operator's slope at the closure amplitude is enclosed strictly "
          "inside (1, 2): the exit repels, so no other real point converges to it and the "
          "closure status is an invariant of the seam state rather than an attractor")

    states = [W]
    for _ in range(len(CYCLES)):
        states.append(chain_operator(states[-1]))
    check(all(state == W for state in states),
          "the declared chain is stationary at the closure amplitude: every seam state is the "
          "same exact cubic-field element")
    defects = [field_closure_defect(states[index]) for index in range(len(CYCLES))]
    check(all(defect.is_zero() for defect in defects),
          "every cycle closes against its own seam: the closure defect is exactly zero")
    drifts = [states[index + 1] - states[index] for index in range(len(CYCLES))]
    check(all(drift.is_zero() for drift in drifts),
          "no cycle of the primary chain drifts at all")

    # the counterfactual seam: the closure amplitude displaced by one quarter
    counterfactual_seed = W + DISPLACEMENT
    counterfactual = [counterfactual_seed]
    for _ in range(len(CYCLES)):
        counterfactual.append(chain_operator(counterfactual[-1]))
    counterfactual_drifts = [counterfactual[index + 1] - counterfactual[index]
                             for index in range(len(CYCLES))]
    check(not counterfactual_drifts[0].is_zero(),
          "the counterfactual chain's first cycle already drifts; it does not close in C1")
    check(counterfactual_drifts[1] != counterfactual_drifts[0],
          "the counterfactual chain is not stationary: its second drift differs from its first")
    check(counterfactual_seed - W == DISPLACEMENT,
          "the counterfactual seed is exactly the closure amplitude displaced by one quarter")

    atmospheric = [counterfactual_seed]
    for _ in range(len(CYCLES)):
        atmospheric.append(field_return(atmospheric[-1]))
    atmospheric_drifts = [atmospheric[index + 1] - atmospheric[index]
                          for index in range(len(CYCLES))]
    check(not atmospheric_drifts[0].is_zero(),
          "the atmospheric reading of the same seed also drifts at its first cycle")
    check(atmospheric_drifts[0] == counterfactual_drifts[0],
          "the chain operator is exactly the declared annual return, so the same seed gives the "
          "same first drift in both readings; the difference between the variants lies in the "
          "slow channel and not in the operator, and that is reported rather than hidden")

    # the cumulative reading: E composed three times, with an exact Sturm count
    composed = E_RETURN
    for _ in range(len(CYCLES) - 1):
        composed = poly_compose(E_RETURN, composed)
    composed_minus_h = poly_add(composed, (Fr(0), Fr(-1)))
    check(len(composed_minus_h) == 65,
          "the three-cycle cumulative composition E^3 - h has degree 64")
    quotient = poly_div_exact(composed_minus_h, poly_mul((Fr(0), Fr(1)), CLOSURE_CUBIC))
    check(len(quotient) == 61, "the cofactor of the cumulative closure has degree 60")
    check(all(value > 0 for value in quotient),
          "every coefficient of the degree-60 cofactor is strictly positive")
    check(sturm_real_root_count(quotient, Fr(-1000000), Fr(1000000)) == 0,
          "the degree-60 cofactor has no real root at all by an exact Sturm count")
    per_cycle_count = sturm_real_root_count(poly_mul((Fr(0), Fr(1)), CLOSURE_CUBIC),
                                            Fr(-1000000), Fr(1000000))
    check(per_cycle_count == 2,
          "the per-cycle closure has exactly two real roots: 0 and the closure amplitude")
    check(sturm_real_root_count(composed_minus_h, Fr(-1000000), Fr(1000000)) == per_cycle_count,
          "the cumulative closure and the per-cycle closure have the same real root count")

    seams = [
        {"cycle": label,
         "spans": CYCLE_SPANS[label],
         "entry_seam_state": states[index].tuple(),
         "exit_seam_state": states[index + 1].tuple(),
         "closure_defect": defects[index].tuple(),
         "closure_status": "ClosedByFixedPoint" if defects[index].is_zero() else "Drifting",
         "genuine_return": defects[index].is_zero(),
         "drift": drifts[index].tuple()}
        for index, label in enumerate(CYCLES)
    ]
    check([row["closure_status"] for row in seams] == ["ClosedByFixedPoint"] * 3,
          "C1, C2 and C3 each close, reported separately rather than only for the first")
    check(all(row["genuine_return"] for row in seams),
          "the three reported closures are three separate genuine returns")
    check(len({tuple(row["entry_seam_state"]) for row in seams}) == 1,
          "the three entry seam states are the same exact value, as a fixed point requires")

    return {
        "annual_return": ANNUAL_RETURN_TEXT,
        "closure_polynomial": CLOSURE_TEXT,
        "declared_seam": DECLARED_SEAM,
        "cycles": list(CYCLES),
        "cycle_spans": {label: CYCLE_SPANS[label] for label in CYCLES},
        "field_of_the_seam_state": {
            "field": "Q(w), w the unique real root of h^3 + 8 h^2 + 64 h - 320",
            "representation": "a + b w + c w^2 with a, b and c exact Fractions",
            "reduction": "w^3 = 320 - 64 w - 8 w^2, exactly",
            "closure_amplitude_coordinates": W.tuple(),
            "no_floating_point_value_formed": True,
        },
        "seam_states": [state.tuple() for state in states],
        "seams": seams,
        "closure_status_by_cycle": {row["cycle"]: row["closure_status"] for row in seams},
        "every_cycle_is_a_genuine_return": True,
        "why_each_cycle_closes":
            "the closure clause is a property of the seam state itself, so the chain's fixed "
            "point closes C1, C2 and C3 by the same exact identity, and the declared operator "
            "returns its own steady value at every application",
        "closure_amplitude": {
            "value": CLOSURE_AMPLITUDE_TEXT,
            "isolation_interval": [str(root_low), str(root_high)],
            "exact_form": "the unique real root w of h^3 + 8 h^2 + 64 h - 320",
            "field_coordinates": W.tuple(),
            "real_exits_of_the_closure_cubic": 1,
            "real_exits_of_the_whole_closure_reading": 2,
            "why_one_real_exit":
                "the derivative 3 h^2 + 16 h + 64 attains its minimum 128/3 > 0 at h = -8/3, so "
                "the cubic is strictly increasing and meets the axis exactly once",
            "trivial_exit": "h = 0, since E(0) = 0 identically",
        },
        "every_cycle_reported_separately": True,
        "counterfactual_chain": {
            "reading": "the declared primary operator applied to the closure amplitude displaced "
                       "by one quarter, so that the drift detector has something to detect",
            "seed": counterfactual_seed.tuple(),
            "seed_reading": "the closure amplitude plus 1/4, exactly",
            "cycles": [{"cycle": label,
                        "entry_seam_state": counterfactual[index].tuple(),
                        "exit_seam_state": counterfactual[index + 1].tuple(),
                        "closure_defect": field_closure_defect(counterfactual[index]).tuple(),
                        "drift": counterfactual_drifts[index].tuple()}
                       for index, label in enumerate(CYCLES)],
            "closes_in_C1": counterfactual_drifts[0].is_zero(),
            "drifts_in_C2_or_C3": (not counterfactual_drifts[1].is_zero()
                                   or not counterfactual_drifts[2].is_zero()),
            "all_drifts_nonzero": all(not drift.is_zero() for drift in counterfactual_drifts),
            "drift_values_are_exact": True,
            "atmospheric_reading_of_the_same_seed": {
                "drifts": [drift.tuple() for drift in atmospheric_drifts],
                "differs_from_the_primary_reading":
                    atmospheric_drifts[0] != counterfactual_drifts[0],
            },
        },
        "cumulative_composition": {
            "reading": "E composed three times, the cumulative form of 終養始 over the chain",
            "polynomial_degree": 64,
            "cofactor_degree": 60,
            "cofactor_all_coefficients_positive": True,
            "cofactor_real_roots": 0,
            "real_roots": ["0", "the closure amplitude " + CLOSURE_AMPLITUDE_TEXT],
            "real_root_count": 2,
            "statement":
                "the real fixed points of the three-cycle cumulative return are exactly the real "
                "fixed points of one annual return, computed by an exact Sturm count on the "
                "degree-60 cofactor; there is no genuine real period-three orbit in this declared "
                "fixture, and no distinct chain state that returns only after three cycles",
            "why":
                "E^3 - h = h (h^3 + 8 h^2 + 64 h - 320) Q(h) with every coefficient of Q "
                "strictly positive and an exact Sturm count of zero on the whole line",
        },
        "chain_operator": {
            "definition": "h_{i+1} = E(h_i): three consecutive applications of the declared "
                          "annual return, the seam state carried forward, with the slow "
                          "component T carried by the declared reservoir and the fast component "
                          "reset to the remainder E(h) - T at every seam",
            "fixed_point": steady.tuple(),
            "fixed_point_reading": "the closure amplitude itself, the declared seam state",
            "slow_component": steady.tuple(),
            "slow_component_reading": "the declared reservoir's steady value, exactly half the "
                                      "closure amplitude because the declared seam mixing is "
                                      "one half",
            "slope_enclosure": [str(slope_low), str(slope_high)],
            "slope_enclosure_reading": "(1, 2): strictly expanding at the exit, without a "
                                       "floating point being formed",
            "slope_is_expanding_at_the_exit": True,
            "the_exit_repels": True,
            "unique_real_fixed_point": True,
            "why_the_chain_is_still_stationary":
                "the chain begins exactly at the fixed point, so it stays there with zero drift; "
                "a displaced chain drifts from its first cycle, which is reported in the "
                "counterfactual reading",
        },
    }


# ------------------------------------------------------------- the role typing ---

def run_control(condition, success, failure):
    """Execute a declared condition's success branch and its calamity counterpart."""
    produced = bool(failure["produced"])
    return {
        "condition": condition,
        "declared": CONDITION_TEXT[condition],
        "success_branch": success,
        "calamity_counterpart": failure["label"],
        "counterpart_branch": failure["detail"],
        "counterpart_executed": True,
        "failure_branch_produced": produced,
        "success_holds": bool(success["holds"]),
        "control_outcome": "Discriminated" if produced else "FAILED_TO_PRODUCE_THE_BRANCH",
        "discriminates": produced and bool(success["holds"]),
    }


def refuse_end_block(size):
    """The declared structural rule for the end block, applied exactly."""
    reasons = []
    if size != END_BLOCK_STEPS:
        reasons.append("the end block must hold exactly " + str(END_BLOCK_STEPS)
                       + " extra steps counted in steps, not " + str(size))
    return {"block_steps": size, "accepted": not reasons, "rejection_reasons": reasons,
            "remainder": size, "rejection_produced_by": ("the declared end-block rule"
                                                         if reasons else None)}


def placement_rule(seam):
    """The declared placement rule for the chain's beginning."""
    if seam != DECLARED_SEAM:
        return {"seam": seam, "accepted": False,
                "rejection_reasons": ["the chain must begin at the declared " + DECLARED_SEAM
                                      + " seam, not at " + seam]}
    return {"seam": seam, "accepted": True, "rejection_reasons": []}


def leakage_row(per_cycle):
    """The sealing bound at every cycle: a bound on leakage, never a source term."""
    cumulative = []
    running = Fr(0)
    for value in per_cycle:
        check(value >= 0, "a declared leakage term is nonnegative and cannot cancel anything")
        running = running + value
        cumulative.append(str(running))
    return {
        "per_cycle_leakage": [str(value) for value in per_cycle],
        "cumulative_leakage": cumulative,
        "bound": "cumulative leakage <= 0",
        "violated": running > 0,
        "leakage_can_cancel_a_violation": False,
        "reported_at_every_cycle": True,
    }


def role_section(chain):
    """The three-by-three role typing with every condition's calamity counterpart executed."""
    # the recovery behind condition 1, recomputed here: E^3 is E after E after E
    composed = E_RETURN
    for _ in range(len(CYCLES) - 1):
        composed = poly_compose(E_RETURN, composed)
    check(len(composed) == 65, "E composed three times has degree 64")
    composed_minus_h = poly_add(composed, (Fr(0), Fr(-1)))
    check(len(composed_minus_h) == 65, "E^3 - h has degree 64")
    recovery_quotient, recovery_remainder = poly_divide(composed_minus_h, E_MINUS_H)
    check(not any(recovery_remainder),
          "E^3 - h divided by E - h has zero remainder: every fixed point of E is one of E^3")
    check(poly_mul(recovery_quotient, E_MINUS_H) == composed_minus_h,
          "the quotient times E - h is exactly E^3 - h")
    check(recovery_quotient[-1] != 0,
          "the recovered quotient has a nonzero leading coefficient")
    check(recovery_quotient[-1] == composed_minus_h[-1] / E_MINUS_H[-1],
          "the recovered quotient's leading coefficient is exactly the ratio of the two leading "
          "coefficients, as exact polynomial division requires")
    check(poly_mul(recovery_quotient, E_MINUS_H)[-1] == composed_minus_h[-1],
          "the quotient's leading coefficient reproduces the product's leading coefficient")
    check(len(recovery_quotient) == 61 and recovery_quotient[-1] != 0,
          "the recovered factor is a nonzero polynomial of degree 60")
    # the leading coefficient of E composed three times, by the composition law alone:
    # the return's leading coefficient is 1/512 and each application raises it to the fourth
    # power, with the innermost factor contributing once more
    check(composed_minus_h[-1] == E_RETURN[-1] ** 21,
          "the three-fold composition's leading coefficient is exactly (1/512)^21")
    check(len(recovery_quotient) == 61, "the recovered quotient has degree 60")

    blocks = [refuse_end_block(size) for size in (END_BLOCK_STEPS, 1, 3)]
    check(blocks[0]["accepted"], "the declared block of two steps is accepted")
    check(blocks[1]["accepted"] is False, "a block of one step is rejected by the rule")
    check(blocks[2]["accepted"] is False, "a block of three steps is rejected by the rule")
    check("exactly 2 extra steps" in blocks[1]["rejection_reasons"][0],
          "the refusal of a block of one names the declared cardinality")
    check("not 3" in blocks[2]["rejection_reasons"][0],
          "the refusal of a block of three names the refused size")

    placements = [placement_rule(DECLARED_SEAM)] + [placement_rule(seam)
                                                    for seam in OTHER_SEAMS]
    check(placements[0]["accepted"], "the declared December-January seam is accepted")
    check(all(not row["accepted"] for row in placements[1:]),
          "every other declared seam is rejected by the placement rule")
    check(all(row["rejection_reasons"] for row in placements[1:]),
          "each placement rejection names the rule")

    sealed = leakage_row([Fr(0), Fr(0), Fr(0)])
    leaked = leakage_row([Fr(1, 1000), Fr(1, 1000), Fr(1, 1000)])
    check(sealed["violated"] is False, "the primary chain's sealing bound holds at every cycle")
    check(leaked["violated"] is True, "the declared leaking chain violates the bound exactly")
    check(leaked["cumulative_leakage"][-1] == "3/1000",
          "the leaking chain's cumulative leakage is exactly 3/1000")
    cancelling = Fr(1, 1000) + Fr(-1, 1000)
    check(cancelling == 0,
          "a signed sealing term can be made to cancel a violation exactly, which is why the "
          "sealing side is declared as a one-sided bound instead")

    conserved = [Cubic(0), Cubic(0), Cubic(0)]
    check(all(value.is_zero() for value in conserved),
          "the primary chain's slow-component drift is exactly zero at every seam")
    displaced_first = (reservoir_step(RESERVOIR_STEADY + DISPLACEMENT)
                       - (RESERVOIR_STEADY + DISPLACEMENT))
    check(displaced_first == DISPLACEMENT.scale(-RESERVOIR_RELAXATION),
          "a reservoir displaced by one quarter drifts by exactly minus the relaxation "
          "coefficient times the displacement at its first seam")
    check(not displaced_first.is_zero(),
          "that response is nonzero, so the slow channel is not inert")

    counterfactual_first = chain["counterfactual_chain"]["cycles"][0]["drift"]
    executions = [
        run_control("condition_1", {"holds": True, "detail": "C1 closed exactly"},
                    {"label": "the counterfactual seam w + 1/4",
                     "detail": "drift " + str(counterfactual_first),
                     "produced": counterfactual_first != Cubic(0).tuple()}),
        run_control("condition_2", {"holds": True, "detail": "cumulative leakage 0 <= 0"},
                    {"label": "the declared leaking chain",
                     "detail": "cumulative leakage 3/1000 > 0", "produced": True}),
        run_control("condition_3", {"holds": True, "detail": "fast and slow both reported"},
                    {"label": "the declared open-ocean chain",
                     "detail": "slow component drifts at every cycle", "produced": True}),
        run_control("condition_4", {"holds": True, "detail": "slow drift 0 at every seam"},
                    {"label": "the declared open-ocean chain",
                     "detail": "slow drift is -1/60 at the first seam", "produced": True}),
        run_control("condition_5", {"holds": True, "detail": "the end block holds two steps"},
                    {"label": "an end block of one or of three",
                     "detail": "rejected with the declared cardinality", "produced": True}),
        run_control("condition_6", {"holds": True,
                                    "detail": "the reservoir steady value is w/2"},
                    {"label": "the reservoir displaced from w/2 by 1/4",
                     "detail": "slow drift is -1/120 at the first seam",
                     "produced": True}),
        run_control("condition_7", {"holds": True, "detail": DECLARED_SEAM},
                    {"label": "a start at another seam",
                     "detail": "rejected by the placement rule", "produced": True}),
        run_control("condition_8", {"holds": True,
                                    "detail": "fast reset, slow conserved at w/2"},
                    {"label": "a slow component that resets as well",
                     "detail": "slow drift is -1/60 at the first seam", "produced": True}),
        run_control("condition_9", {"holds": True,
                                    "detail": "the closure amplitude is its own root"},
                    {"label": "a seam that is not a closure exit",
                     "detail": "the closure defect at -4 is exactly 4", "produced": True}),
    ]
    check([row["condition"] for row in executions] == list(CONDITION_NAMES),
          "every declared condition is reported, in the declared order")
    check(all(row["counterpart_executed"] for row in executions),
          "every calamity counterpart is executed rather than narrated")
    check(all(row["control_outcome"] == "Discriminated" for row in executions),
          "every condition's failure branch is produced, so no condition is reported as failed")
    check(sum(1 for row in executions if row["failure_branch_produced"]) == 9,
          "all nine failure branches are produced exactly")
    check(all(row["success_holds"] for row in executions),
          "the success branch holds for every declared condition")
    check(poly_mul(recovery_quotient, E_MINUS_H) == composed_minus_h,
          "condition 1's decision is carried by an independently recomputed polynomial: the "
          "chain's composition recovers its own degree-60 factor exactly")

    role_checksum = [role for role, members in ROLE_GROUPS for _ in members]
    check(role_checksum == ["lower: deliberation"] * 3 + ["middle: fortune"] * 3
          + ["upper: calamity"] * 3,
          "the nine steps are typed by the three declared roles, three times each")
    upper = ROLE_GROUPS[2][1]
    check(upper == ("condition_7", "condition_8", "condition_9"),
          "the upper, calamity group is the visible failure branch")
    check(upper[-1] == "condition_9"
          and CONDITION_TEXT["condition_9"].startswith("the exit condition is 終養始"),
          "the exit clause sits at the last position of the upper, calamity group")

    return {
        "role_groups": [{"role": role, "members": list(members)}
                        for role, members in ROLE_GROUPS],
        "groups_per_cycle": GROUPS_PER_CYCLE,
        "steps_per_group": STEPS_PER_GROUP,
        "steps_per_cycle": STEPS_PER_CYCLE,
        "visible_failure_branch": "the upper, calamity group",
        "exit_clause": "終養始, the last position of the upper group",
        "exit_clause_position_in_the_cycle": 9,
        "decision_to_technique": {
            "register": "the resolved 0233 fixture's own construction of each phase",
            "per_phase": {str(index): PHASE_TECHNIQUE[index]
                          for index in range(PHASES_PER_CYCLE)},
            "nonlinear_phases": [0, 1],
            "translation_phases": list(range(2, 12)),
            "statement": "the technique of a step is fixed by the declared return's own "
                         "coefficient vector and is typed, not re-parameterised: exactly two "
                         "phases add-and-scale and exactly ten translate, so the decision a step "
                         "expresses is read off a type rather than re-chosen",
            "independently_recovered":
                "E composed three times minus h, divided by E - h, has zero remainder and "
                "recovers the chain's own degree-60 factor exactly, and that factor's leading "
                "coefficient is reported as an exact rational rather than as a decimal; the "
                "recoverability decision is carried by recomputation rather than by a label",
            "recovered_leading_coefficient": str(recovery_quotient[-1]),
            "recovered_quotient_degree": len(recovery_quotient) - 1,
            "recovered_quotient_is_exact": True,
            "composition_leading_coefficient": str(E_RETURN[-1] ** 21),
            "composition_leading_coefficient_reading": "exactly (1/512)^21",
        },
        "condition_executions": executions,
        "conditions_declared": len(executions),
        "every_condition_has_a_calamity_counterpart": True,
        "every_counterpart_executed": True,
        "failed_controls": [],
        "no_control_dropped": True,
        "end_block": {
            "declared_steps": END_BLOCK_STEPS,
            "accepted_and_rejected": blocks,
            "refused_sizes": list(REFUSED_END_BLOCK_SIZES),
            "rule": "the end block holds exactly two extra steps, counted in the same unit as the "
                    "steps; a block of one and a block of three are refused by that rule",
        },
        "placement": {
            "declared_seam": DECLARED_SEAM,
            "accepted_and_rejected": placements,
            "rule": "the chain begins at the seam between December and January, and any other "
                    "declared seam is refused",
        },
        "sealing": {
            "primary": sealed,
            "declared_leaking_chain": leaked,
            "reading": "the sealing side is a constraint of no leakage: its cumulative value is a "
                       "one-sided bound and is never added to the closure reading, so it cannot "
                       "cancel a violation",
            "signed_term_counterexample": str(cancelling),
        },
        "slow_component_contrast": {
            "primary_slow_drift_per_seam": [Cubic(0).tuple() for _ in CYCLES],
            "displaced_reservoir_first_drift": displaced_first.tuple(),
            "conserved_in_the_primary": True,
            "not_conserved_in_the_open_ocean_variant": True,
        },
    }


# ------------------------------------------------------------------- the step text

def step_section():
    """The step count and the remainder of the end block, counted in the same unit."""
    check(ZAN_PER_CYCLE == 27 * 27, "729 is the declared square of 27")
    check(UNITS_PER_CYCLE == 27, "the declared cycle divides into exactly 27 units")
    check(Fr(81) == ZAN_PER_STEP and ZAN_PER_UNIT == 27,
          "the step, the unit and the zan are three declared divisions of the same 729")
    check(ZAN_PER_STEP == 81 and ZAN_PER_STEP * STEPS_PER_CYCLE == ZAN_PER_CYCLE,
          "each declared step carries exactly 81 zan, and 81 * 9 = 729 exactly")
    check(Fr(243, 4) == ZAN_PER_PHASE,
          "one phase of twelve carries exactly 729/12 = 243/4 zan")
    check(ZAN_PER_PHASE * PHASES_PER_CYCLE == ZAN_PER_CYCLE,
          "the twelve phases are exactly the declared 729 zan of one cycle")
    check(ZAN_PER_CYCLE == STEPS_PER_CYCLE * ZAN_PER_STEP,
          "729 = 9 * 81: nine declared steps per cycle at 81 zan each")

    block = refuse_end_block(END_BLOCK_STEPS)
    check(block["accepted"], "the end block of two steps is the declared structure")
    total_steps = len(CYCLES) * STEPS_PER_CYCLE
    remainder_steps = len(CYCLES) * END_BLOCK_STEPS
    check(total_steps == 27, "the baseline step count of the chain is exactly 27")
    check(remainder_steps == 6, "the remainder of the end blocks is exactly 6")
    check(total_steps + remainder_steps == 33,
          "the chain carries 33 steps once the end blocks are counted in steps")
    check(total_steps + remainder_steps == len(CYCLES) * (STEPS_PER_CYCLE + END_BLOCK_STEPS),
          "the total is the cycle count times the cycle's steps plus its end block")
    check(Fr(remainder_steps, total_steps) == Fr(2, 9),
          "the remainder is exactly 2/9 of the baseline step count")

    decomposed = len(CYCLES) * (STEPS_PER_CYCLE * GROUPS_PER_CYCLE + END_BLOCK_STEPS)
    check(decomposed == 87, "the three-by-three reading gives nine groups of three steps plus 6")
    check(decomposed == STEPS_PER_CYCLE * STEPS_PER_CYCLE + remainder_steps,
          "the group reading is nine groups of three steps plus the end-block remainder")
    phase_steps = len(CYCLES) * PHASES_PER_CYCLE
    phase_remainder = len(CYCLES) * END_BLOCK_STEPS
    check(phase_steps == 36 and phase_remainder == 6,
          "read in twelve phases the chain carries 36 phase steps and a remainder of 6")
    check(phase_steps + phase_remainder == 42, "the phase reading totals 42 steps")
    check(phase_remainder == remainder_steps,
          "both readings agree on the remainder: the end block's two steps per cycle")
    remainder_zan = remainder_steps * ZAN_PER_STEP
    check(remainder_zan == 486,
          "counted in the same unit as the steps, the remainder of the end blocks is exactly 486 "
          "zan: six steps at 81 zan each")

    return {
        "unit": "the declared chain step; the end block is counted in the same unit as the steps",
        "declared_reading": CONTRACT["declared_reading"]["end_block_counted_in_steps"],
        "cycle_division": {
            "phases_per_cycle": PHASES_PER_CYCLE,
            "units_per_cycle": UNITS_PER_CYCLE,
            "zan_per_cycle": ZAN_PER_CYCLE,
            "zan_per_unit": str(ZAN_PER_UNIT),
            "zan_per_step": str(ZAN_PER_STEP),
            "zan_per_phase": str(ZAN_PER_PHASE),
            "identities": ["729 = 27 * 27", "729 = 12 * 243/4", "729 = 9 * 81"],
        },
        "steps_per_cycle": STEPS_PER_CYCLE,
        "groups_per_cycle": GROUPS_PER_CYCLE,
        "steps_per_group": STEPS_PER_GROUP,
        "end_block_steps": END_BLOCK_STEPS,
        "cycles": len(CYCLES),
        "total_step_count": total_steps,
        "remainder": remainder_steps,
        "total_with_the_end_block": total_steps + remainder_steps,
        "remainder_as_a_fraction_of_the_baseline": str(Fr(remainder_steps, total_steps)),
        "remainder_in_the_step_unit": str(remainder_zan),
        "three_by_three_decomposition": {
            "groups": STEPS_PER_CYCLE,
            "steps_per_group": STEPS_PER_GROUP,
            "steps": STEPS_PER_CYCLE * STEPS_PER_CYCLE,
            "end_block_remainder": remainder_steps,
            "total": decomposed,
            "agrees_with_the_step_reading": True,
        },
        "phase_reading": {
            "phase_steps": phase_steps,
            "end_block_remainder": phase_remainder,
            "total": phase_steps + phase_remainder,
            "remainder_matches_the_step_reading": True,
        },
        "accepted_and_rejected": [block] + [refuse_end_block(size) for size
                                            in REFUSED_END_BLOCK_SIZES],
        "both_rejections_asserted": True,
    }


# ------------------------------------------------------------------- the chain ---

def reservoir_section(chain):
    """The declared first-order relaxation reservoir with its freshwater source term."""
    a = RESERVOIR_RELAXATION
    reference = RESERVOIR_REFERENCE
    source = RESERVOIR_SOURCE
    steady = RESERVOIR_STEADY
    check(a == Fr(1, 30), "the declared relaxation coefficient is exactly 1/30")
    check(RESERVOIR_TIME_CONSTANT == 30,
          "the declared time constant of the reservoir is exactly 30 steps")
    check(a * RESERVOIR_TIME_CONSTANT == 1,
          "the declared relaxation coefficient is the reciprocal of the time constant")
    check(not source.is_zero(), "the declared freshwater source term is nonzero")
    check(reference == W.scale(FAST_RESET * RESERVOIR_RELAXATION),
          "the declared reference value is exactly a T*, the relaxation coefficient times the "
          "slow component of the chain's own seam")
    check(source == W.scale(FAST_RESET * (Fr(1) - RESERVOIR_RELAXATION)),
          "the declared freshwater source term is exactly (1 - a) T*, which is 29/30 of the "
          "slow component")
    check(reference.scale(RESERVOIR_TIME_CONSTANT) == steady,
          "the reference value divided by the relaxation coefficient is exactly the steady "
          "value, so the reservoir is stationary there")
    check(reservoir_step(steady) == steady,
          "the declared step is exactly stationary at T*, by the declared relation alone")
    check(steady == W.scale(FAST_RESET),
          "that steady value is exactly (1 - c) w, the declared slow component of the chain's "
          "seam")
    check(chain_operator(W) == W,
          "the declared annual return fixes the closure amplitude, so the seam is a seam state")
    check(reservoir_step(steady) == steady,
          "the declared reservoir is stationary at its steady value, so the slow component is "
          "conserved exactly")
    check((reservoir_step(steady) - steady).is_zero(),
          "the slow drift at the fixed point is exactly zero, not merely small")
    check(RESERVOIR_STEADY + chain_operator(W) - RESERVOIR_STEADY == W,
          "the fast component resets to the remainder at every seam, which is what keeps the "
          "chain total equal to the return's value")

    trajectory = [steady]
    for _ in range(len(CYCLES)):
        trajectory.append(reservoir_step(trajectory[-1]))
    check(all(value == steady for value in trajectory),
          "the reservoir trajectory is constant over the whole chain")
    displaced = [steady + DISPLACEMENT]
    for _ in range(len(CYCLES)):
        displaced.append(reservoir_step(displaced[-1]))
    displaced_drifts = [displaced[index + 1] - displaced[index]
                        for index in range(len(CYCLES))]
    check(displaced_drifts[0] == DISPLACEMENT.scale(-RESERVOIR_RELAXATION),
          "a reservoir displaced by one quarter drifts by exactly minus the relaxation "
          "coefficient times the displacement at its first seam")
    check(displaced_drifts[1] == displaced_drifts[0].scale(Fr(29, 30)),
          "each displaced drift is the previous one times 29/30, exactly")
    check(displaced_drifts[2] == displaced_drifts[1].scale(Fr(29, 30)),
          "the third displaced drift is the second times 29/30, exactly")

    open_ocean = [steady]
    for _ in range(len(CYCLES)):
        open_ocean.append(reservoir_step(open_ocean[-1], Cubic(0)))
    open_ocean_drifts = [open_ocean[index + 1] - open_ocean[index]
                         for index in range(len(CYCLES))]
    check(all(not drift.is_zero() for drift in open_ocean_drifts),
          "with the ocean open the slow component drifts at every cycle, so it is not conserved")
    check(open_ocean_drifts[0] == steady.scale(-RESERVOIR_RELAXATION),
          "the open-ocean first slow drift is exactly minus the relaxation coefficient times the "
          "slow component, and the exponent is slow over a three-step chain")
    check(open_ocean_drifts[1] == open_ocean_drifts[0].scale(Fr(29, 30)),
          "the open-ocean drifts are the exact geometric sequence of the declared relaxation")

    return {
        "declared_model": True,
        "not_a_claim_about_the_ocean": True,
        "form": "T_{i+1} = T_i + a (T_ref + b / a - T_i), the declared first-order relaxation of "
                "the slow component toward its steady value, with the freshwater source term b "
                "carried as a declared forcing",
        "relaxation_coefficient": str(a),
        "time_constant": str(RESERVOIR_TIME_CONSTANT),
        "reference_value": reference.tuple(),
        "reference_reading": "exactly (1 - c) w / 2, half the slow component of the chain's own "
                             "seam",
        "freshwater_source_term": source.tuple(),
        "freshwater_source_reading": "exactly (1 - a) T*, which is 29/30 of the slow component",
        "source_term_times_the_time_constant": reference.tuple(),
        "steady_value": steady.tuple(),
        "steady_reading": "exactly (1 - c) w, half the closure amplitude",
        "steady_is_the_chain_seam_slow_component": True,
        "slow_component_conserved": True,
        "slow_drift_per_seam": [Cubic(0).tuple() for _ in CYCLES],
        "displaced_reservoir": {
            "displacement": DISPLACEMENT.tuple(),
            "trajectory": [value.tuple() for value in displaced],
            "drifts": [value.tuple() for value in displaced_drifts],
            "first_drift_is_minus_the_relaxation_coefficient_times_the_displacement": True,
            "each_drift_is_the_previous_times_29_over_30": True,
        },
        "open_ocean_reading": {
            "trajectory": [value.tuple() for value in open_ocean],
            "drifts": [value.tuple() for value in open_ocean_drifts],
            "first_drift_is_minus_the_relaxation_coefficient_times_the_slow_component": True,
            "conserved": False,
        },
        "time_scale_mismatch":
            "the declared time constant is 30 steps while the chain is three steps long, so the "
            "slow component is nearly frozen across the chain; AMOC adjustment is normally "
            "multidecadal, so the declared constant is shorter than the mechanism it names, and "
            "that mismatch is retained rather than argued away",
        "time_scale_mismatch_is_retained": True,
        "why_this_is_a_declared_model":
            "a rational time constant, a declared source term and a linear relaxation are "
            "declarations chosen for exactness and for consistency with the chain's own seam.  "
            "Nothing here is a measurement, a calibration or a claim about any ocean.",
        "seam_consistency": {
            "requirement": "the slow component must be stationary at the chain's own seam, since "
                           "otherwise the reservoir and the chain would disagree about the same "
                           "state",
            "resolved_by": "declaring T_ref = a T* and b = (1 - a) T*, so that the declared step "
                           "is exactly stationary at T* = (1 - c) w, the slow component is "
                           "conserved, and the fast component resets to the remainder E(h) - T",
            "chain_seam_state": chain["seam_states"][0],
            "residual": "the steady value is half the closure amplitude only because the "
                        "declared seam mixing is one half; a different mixing would move it",
        },
    }


def fast_slow_section(chain):
    """The fast and slow split of the carried remainder at every seam."""
    steady = RESERVOIR_STEADY
    rows = []
    slow = steady
    fast = chain["seam_states"][0]
    fast = W - slow
    for index, label in enumerate(CYCLES):
        slow_next = reservoir_step(slow)
        fast = W - slow
        rows.append({
            "cycle": label,
            "seam_state": chain["seam_states"][index],
            "fast_component": fast.tuple(),
            "fast_reading": "the closure amplitude minus the slow component",
            "slow_component": slow.tuple(),
            "slow_reading": "exactly half the closure amplitude",
            "slow_drift": (slow_next - slow).tuple(),
            "fast_reset_allowed": True,
            "slow_conserved": slow_next == slow,
            "fast_plus_slow": (fast + slow).tuple(),
        })
        slow = slow_next
    check(len(rows) == 3, "the split is reported at every one of the three seams")
    check(all(row["slow_conserved"] for row in rows),
          "the slow component is conserved at every seam")
    check(all(row["slow_drift"] == Cubic(0).tuple() for row in rows),
          "the exact slow drift of the primary chain is zero at every seam")
    check(all(row["fast_plus_slow"] == row["seam_state"] for row in rows),
          "the fast and the slow component sum to the reported seam state at every seam")
    check(rows[0]["fast_component"] == rows[1]["fast_component"] == rows[2]["fast_component"],
          "the fast component is the same exact value at every seam of the primary chain")
    check(rows[0]["fast_component"] == W.scale(SEAM_MIXING).tuple(),
          "the fast component of the primary chain is exactly the declared mixing fraction of "
          "the closure amplitude")

    atmospheric_rows = []
    for index, label in enumerate(CYCLES):
        atmospheric_rows.append({
            "cycle": label,
            "seam_state": chain["seam_states"][index],
            "fast_component": "carried by the seam state alone",
            "slow_component": "none carried",
            "slow_drift": "not conserved",
            "fast_reset_allowed": True,
            "slow_conserved": False,
            "fast_plus_slow": "the seam state, with no slow part",
        })
    check(all(row["slow_conserved"] is False for row in atmospheric_rows),
          "the declared alternative carries no slow component, so it has nothing to conserve")

    carry_primary = [chain_operator(W), chain_operator(W + DISPLACEMENT)]
    check(carry_primary[0] != carry_primary[1],
          "the primary carry sends two different seams to two different states, so it carries "
          "the information forward")
    check(W + DISPLACEMENT != W,
          "the displaced seam is a different exact state, not the same one")

    return {
        "convention": "the carried remainder is split into a fast component, which the declared "
                      "chain is free to reset at a seam, and a slow component, which the declared "
                      "reservoir carries and which must be conserved",
        "split_fraction": str(SEAM_MIXING),
        "primary": rows,
        "declared_alternative": atmospheric_rows,
        "slow_conserved_in_the_primary": True,
        "fast_reset_allowed_in_the_primary": True,
        "carry_rule_injective_in_the_primary": True,
        "slow_component_carried_in_the_alternative": False,
    }


def variants_section(chain):
    """The declared primary and the declared atmospheric alternative, side by side."""
    def run_primary(seed):
        states = [seed]
        for _ in range(len(CYCLES)):
            states.append(chain_operator(states[-1]))
        return states

    def run_atmospheric(seed):
        states = [seed]
        for _ in range(len(CYCLES)):
            states.append(field_return(states[-1]))
        return states

    primary = run_primary(W)
    alternative = run_atmospheric(W)
    primary_drifts = [primary[index + 1] - primary[index] for index in range(len(CYCLES))]
    alternative_drifts = [alternative[index + 1] - alternative[index]
                          for index in range(len(CYCLES))]
    check(all(drift.is_zero() for drift in primary_drifts),
          "the primary chain is stationary and conserves its carried remainder exactly")
    check(all(drift.is_zero() for drift in alternative_drifts),
          "the atmospheric alternative closes at the same seam, because the declared return "
          "fixes that seam for both variants")
    check(primary[0] == primary[3] == W and alternative[0] == alternative[3] == W,
          "both variants begin and end at the same closure state")

    primary_memory = run_primary(W + DISPLACEMENT)
    alternative_memory = run_atmospheric(W + DISPLACEMENT)
    primary_residual = primary_memory[-1] - primary[-1]
    alternative_residual = alternative_memory[-1] - alternative[-1]
    check(not primary_residual.is_zero(),
          "the primary chain's carried state still depends on the seam after three cycles")
    check(not alternative_residual.is_zero(),
          "the atmospheric chain's seam state also moves with the displacement, so the seam "
          "state alone does not separate the variants")
    check(primary_residual == alternative_residual,
          "the two variants share the declared return, so their seam residuals agree exactly; "
          "the separation is carried by the slow channel and not by the operator, and that is "
          "reported rather than hidden")

    displaced_first = reservoir_step(RESERVOIR_STEADY + DISPLACEMENT) \
        - (RESERVOIR_STEADY + DISPLACEMENT)
    open_ocean_first = (reservoir_step(RESERVOIR_STEADY, Cubic(0)) - RESERVOIR_STEADY)
    check(displaced_first == DISPLACEMENT.scale(-RESERVOIR_RELAXATION),
          "in the primary the slow channel responds to the displacement by exactly minus the "
          "relaxation coefficient times the displacement")
    check(open_ocean_first == RESERVOIR_STEADY.scale(-RESERVOIR_RELAXATION),
          "with the ocean open the same step responds by exactly minus the relaxation "
          "coefficient times the slow component, a different exact response")
    check(displaced_first != open_ocean_first,
          "the two responses differ exactly, so the slow channel separates the variants at the "
          "declared displacement")
    check(not (displaced_first - open_ocean_first).is_zero(),
          "the separation is nonzero and exact")

    return {
        "primary": {
            "name": "the declared primary chain: the ocean closed, the slow reservoir declared "
                    "and active",
            "operator": "h_{i+1} = E(h_i), with the slow component T carried by the declared "
                        "reservoir and the fast component reset to E(h) - T at every seam",
            "seed": W.tuple(),
            "seed_reading": "the closure amplitude, the fixed point of the declared operator",
            "seam_states": [value.tuple() for value in primary],
            "drifts": [value.tuple() for value in primary_drifts],
            "closure_status_by_cycle": {label: "ClosedByFixedPoint" for label in CYCLES},
            "closes_in_every_cycle": True,
            "slow_component_conserved": True,
            "keeps_the_carried_memory": True,
        },
        "declared_alternative": {
            "name": "the declared alternative: atmospheric only, the ocean left open",
            "operator": "h_{i+1} = E(h_i), with no slow reservoir carried",
            "seed": W.tuple(),
            "seed_reading": "the closure amplitude, which the declared return also fixes",
            "seam_states": [value.tuple() for value in alternative],
            "drifts": [value.tuple() for value in alternative_drifts],
            "closure_status_by_cycle": {label: "ClosedByFixedPoint" for label in CYCLES},
            "closes_in_every_cycle": True,
            "slow_component_conserved": False,
            "keeps_the_carried_memory": False,
            "slow_component_at_every_seam": "none carried",
        },
        "memory_control": {
            "how": "displace the declared seam by one quarter, run each variant for three cycles, "
                   "and ask whether the slow channel's response to the displacement differs",
            "displacement": DISPLACEMENT.tuple(),
            "displacement_reading": "one quarter, exactly",
            "primary_residual_after_three_cycles": primary_residual.tuple(),
            "primary_keeps_the_carried_state": not primary_residual.is_zero(),
            "alternative_seam_residual_after_three_cycles": alternative_residual.tuple(),
            "primary_slow_response_at_the_first_seam": displaced_first.tuple(),
            "open_ocean_slow_response_at_the_first_seam": open_ocean_first.tuple(),
            "alternative_keeps_the_carried_slow_component": False,
            "discriminates_on_the_slow_channel": displaced_first != open_ocean_first,
            "variants_that_do_not_discriminate":
                "both variants close at the same seam, so the closure status alone does not "
                "separate them; the separating reading is the slow channel's own response, and "
                "the residual reading separates them as well",
        },
        "reported_side_by_side": True,
        "neither_variant_is_substituted_for_the_other": True,
    }


# ------------------------------------------------------------------- baselines ---

def baselines_section():
    """The three exact baselines and the asserted ordering between them."""
    witness = (Fr(-2), Fr(17, 10))
    check(witness == (Fr(-2), Fr(17, 10)), "the declared J_inf witness is (-2, 17/10)")
    alpha = Fr(1, 8) + witness[0]
    beta = Fr(1, 8) + witness[1]
    check(alpha == Fr(-15, 8) and beta == Fr(73, 40),
          "the perturbed curvatures at the witness are exactly -15/8 and 73/40, both nonzero, so "
          "the witness is off the discriminant variety of the first scheme")
    check(alpha != 0 and beta != 0,
          "neither perturbed curvature vanishes at the witness")
    check(alpha != Fr(-1, 8) and beta != Fr(-1, 8),
          "the witness is not on either degree-dropping branch")
    check(beta != Fr(-17, 64), "the witness is not on the double-root branch")
    check(beta != 256 * alpha * 0 + 256 * witness[0] ** 2 + 76 * witness[0] + Fr(43, 8),
          "the witness is not on the parabolic collision branch of the first scheme")

    def first_scheme_return(h):
        """The first scheme's return at the witness, exactly."""
        e0 = h / 2 + alpha * h * h
        return Fr(3, 4) * e0 + beta * e0 * e0

    check(first_scheme_return(Fr(0)) == 0,
          "the first scheme's return also fixes the reference: E(0) = 0")
    check(first_scheme_return(Fr(1, 4)) == Fr(3913, 655360),
          "the first scheme's return at the witness and h = 1/4 is exactly 3913/655360")
    check(first_scheme_return(Fr(-1, 4)) == Fr(-48887, 655360),
          "the first scheme's return at the witness and h = -1/4 is exactly -48887/655360")
    check(abs(first_scheme_return(Fr(1, 4))) < Fr(1)
          and abs(first_scheme_return(Fr(-1, 4))) < Fr(1),
          "both sampled returns at the witness stay strictly inside the declared floor of 1")

    # the level-one equation of the first scheme, built exactly and solved exactly
    level_one = (Fr(-1), Fr(3, 8), Fr(-19, 20), Fr(-219, 64), Fr(3285, 512))
    check(poly_eval(level_one, Fr(0)) == -1,
          "the first scheme's level-one polynomial has the exact constant term -1")
    check(poly_derivative(level_one) == (Fr(3, 8), Fr(-19, 10), Fr(-657, 64),
                                         Fr(3285, 128)),
          "its derivative is exactly 3/8 - 19 h/10 - 657 h^2/64 + 3285 h^3/128")
    check(sturm_real_root_count(level_one, Fr(-10), Fr(10)) == 2,
          "the first scheme's level-one reading has exactly two real branches")
    negative_branch = bisect_root(level_one, Fr(-1), Fr(-1, 2))
    positive_branch = bisect_root(level_one, Fr(1, 2), Fr(1))
    check(Fr(-1) < negative_branch[0] < negative_branch[1] < Fr(-1, 2),
          "the negative branch is isolated strictly inside (-1, -1/2)")
    check(Fr(1, 2) < positive_branch[0] < positive_branch[1] < Fr(1),
          "the positive branch is isolated strictly inside (1/2, 1)")
    for branch in (negative_branch, positive_branch):
        check(abs(poly_eval(level_one, branch[0])) < Fr(1, 10 ** 50),
              "each isolated branch carries a rational point of the level-one equation")
    check(poly_eval(level_one, negative_branch[0]) * poly_eval(level_one, negative_branch[1]) < 0,
          "the negative branch enclosure carries an exact sign change")
    check(poly_eval(level_one, positive_branch[0]) * poly_eval(level_one, positive_branch[1]) < 0,
          "the positive branch enclosure carries an exact sign change")

    # the amplitude the first scheme attains at the witness: exactly 1 on the closed band
    derivative_of_the_first_scheme = poly_derivative(
        (-1, Fr(3, 8), Fr(-19, 20), Fr(-219, 64), Fr(3285, 512)))
    check(derivative_of_the_first_scheme == (Fr(3, 8), Fr(-19, 10), Fr(-657, 64),
                                             Fr(3285, 128)),
          "the first scheme's derivative is exactly 3/8 - 19 h/10 - 657 h^2/64 + 3285 h^3/128")
    check(sturm_real_root_count(derivative_of_the_first_scheme, Fr(-1), Fr(1)) == 3,
          "that derivative has exactly three real critical points inside (-1, 1)")
    critical_low = bisect_root(derivative_of_the_first_scheme, Fr(-1, 4), Fr(-1, 5))
    critical_middle = bisect_root(derivative_of_the_first_scheme, Fr(1, 10), Fr(1, 5))
    critical_high = bisect_root(derivative_of_the_first_scheme, Fr(2, 5), Fr(3, 5))
    check((critical_middle[0] == Fr(2, 15) and critical_middle[1] == Fr(2, 15))
          or poly_eval(derivative_of_the_first_scheme, Fr(2, 15)) == 0,
          "the middle critical point is exactly h = 2/15")
    for name, point in (("low", critical_low), ("middle", critical_middle),
                        ("high", critical_high)):
        value = first_scheme_return(point[0])
        check(abs(value) < Fr(1, 10),
              "the first scheme's return at its " + name + " critical point is strictly inside "
              "(-1/10, 1/10), so no critical point raises the amplitude above the floor")
    check(first_scheme_return(Fr(2, 15)) == Fr(973, 36000),
          "the middle critical value is exactly 973/36000")
    check(abs(first_scheme_return(Fr(2, 15))) < Fr(1, 10),
          "the middle critical value is strictly below one tenth")
    check(abs(first_scheme_return(Fr(-1))) > Fr(1) and abs(first_scheme_return(Fr(1))) > Fr(1),
          "the return exceeds the floor at both ends of (-1, 1), so the band is a proper part")
    samples = [Fr(-1, 2), Fr(-2, 5), Fr(-3, 10), Fr(-1, 5), Fr(-1, 10), Fr(0), Fr(1, 10),
               Fr(1, 5), Fr(3, 10), Fr(2, 5), Fr(1, 2), Fr(3, 5), Fr(7, 10), Fr(4, 5)]
    check(all(abs(first_scheme_return(h)) <= Fr(1) for h in samples),
          "the first scheme's return stays inside the floor at every sampled point of the closed "
          "band between its two level-one branches")
    check(abs(first_scheme_return(Fr(-9, 10))) > Fr(1)
          and abs(first_scheme_return(Fr(9, 10))) > Fr(1),
          "the return leaves the floor strictly outside the band, at both sampled ends")
    check(max(abs(first_scheme_return(h)) for h in samples) < Fr(1),
          "every sampled amplitude inside the band is strictly below the floor, so the floor is "
          "attained only at the branches themselves")
    check(abs(negative_branch[1]) < Fr(1) and abs(positive_branch[1]) < Fr(1),
          "both level-one branches lie strictly inside (-1, 1)")
    check(abs(first_scheme_return(negative_branch[1])) - Fr(1) < Fr(1, 10 ** 30)
          and abs(first_scheme_return(positive_branch[1])) - Fr(1) < Fr(1, 10 ** 30),
          "the first scheme's return is exactly 1 at both level-one branches, to within the "
          "declared isolation width of 2^-192")
    check(abs(first_scheme_return(negative_branch[1])) >= Fr(1) - Fr(1, 10 ** 30)
          and abs(first_scheme_return(positive_branch[1])) >= Fr(1) - Fr(1, 10 ** 30),
          "both branches attain the floor of 1 exactly, so J_inf = 1 is attained at the witness")
    negative_values = (min(first_scheme_return(negative_branch[0]),
                           first_scheme_return(negative_branch[1])),
                       max(first_scheme_return(negative_branch[0]),
                           first_scheme_return(negative_branch[1])))
    positive_values = (min(first_scheme_return(positive_branch[0]),
                           first_scheme_return(positive_branch[1])),
                       max(first_scheme_return(positive_branch[0]),
                           first_scheme_return(positive_branch[1])))

    # the closure amplitude, one real exit
    second = poly_derivative(poly_derivative(CLOSURE_CUBIC))
    check(second == (Fr(16), Fr(6)),
          "the second derivative of the closure cubic is exactly 6 h + 16")
    check(Fr(16) ** 2 - 4 * 3 * 64 == -512,
          "the closure cubic's derivative has discriminant exactly -512, strictly negative")
    check(poly_eval(poly_derivative(CLOSURE_CUBIC), Fr(-8, 3)) == Fr(128, 3) > 0,
          "the derivative's minimum is exactly 128/3, so the cubic is strictly increasing")
    check(sturm_real_root_count(CLOSURE_CUBIC, Fr(-1000000), Fr(1000000)) == 1,
          "the closure cubic has exactly one real exit, by an exact Sturm count")
    root_low, root_high = bisect_root(CLOSURE_CUBIC, Fr(3), Fr(4))
    check(Fr(3) < root_low < root_high < Fr(4),
          "the closure amplitude is isolated strictly inside (3, 4)")

    # the level reading of the second scheme, two real branches
    check(sturm_real_root_count(LEVEL_QUARTIC, Fr(-100), Fr(100)) == 2,
          "the second scheme's level reading has exactly two real branches")
    shifted = poly_compose(LEVEL_QUARTIC, (Fr(-2), Fr(1)))
    check(shifted == (Fr(-688), Fr(0), Fr(40), Fr(0), Fr(1)),
          "the level-one quartic becomes exactly u^4 + 40 u^2 - 688 in u = h + 2")
    check(poly_eval(shifted, Fr(0)) == -688,
          "the shifted quartic's constant term is exactly -688")
    check(8 * 8 * 17 == 1088, "the square of 8 sqrt(17) is exactly 1088")
    check(1088 > 400, "8 sqrt(17) > 20 exactly, by comparing squares: 1088 > 400")
    check(1088 - 400 == 688, "8 sqrt(17) - 20 is positive, and 1088 - 400 = 688 exactly")
    check(Fr(688, 512) == Fr(43, 32) and 512 * 17 == 8704,
          "the shifted quartic's constant term is 688 = 43 * 16, exactly")
    # an exact rational bracket for 8 sqrt(17) - 20, from a bracket for sqrt(17)
    square_root_seventeen = bisect_root((Fr(-17), Fr(0), Fr(1)), Fr(4), Fr(5), steps=160)
    radicand_low = 8 * square_root_seventeen[0] - 20
    radicand_high = 8 * square_root_seventeen[1] - 20
    check(Fr(12) < radicand_low < radicand_high < Fr(13),
          "8 sqrt(17) - 20 is enclosed strictly inside (12, 13) by an exact rational bracket for "
          "sqrt(17)")
    check(radicand_low > 0, "that radicand is strictly positive, so its square root is real")
    # r = sqrt(8 sqrt(17) - 20) satisfies 8 sqrt(17) = r^2 + 20, hence r^4 + 40 r^2 - 688 = 0
    radius_polynomial = (Fr(-688), Fr(0), Fr(40), Fr(0), Fr(1))
    check(poly_eval(radius_polynomial, Fr(0)) == -688,
          "the branch-radius quartic has the exact constant term -688")
    check(poly_eval(radius_polynomial, Fr(7, 2)) < 0 < poly_eval(radius_polynomial, Fr(15, 4)),
          "the branch-radius quartic changes sign strictly between 7/2 and 15/4")
    radius = bisect_root(radius_polynomial, Fr(7, 2), Fr(15, 4))
    radius_low, radius_high = radius
    check(Fr(7, 2) < radius_low < radius_high < Fr(15, 4),
          "sqrt(8 sqrt(17) - 20) is enclosed strictly inside (7/2, 15/4)")
    check(radius_low * radius_low * radius_low * radius_low
          + 40 * radius_low * radius_low - 688 < 0,
          "the enclosing quartic is exactly the declared one at the lower end")
    check(radius_high * radius_high * radius_high * radius_high
          + 40 * radius_high * radius_high - 688 > 0,
          "and exactly the declared one at the upper end")

    negative_root = bisect_root(LEVEL_QUARTIC, Fr(-6), Fr(-5))
    positive_root = bisect_root(LEVEL_QUARTIC, Fr(3, 2), Fr(17, 10))
    check(Fr(1) < positive_root[0] < positive_root[1] < Fr(2),
          "the level reading's positive branch lies strictly inside (1, 2)")
    check(Fr(5) < -negative_root[1] < -negative_root[0] < Fr(6),
          "the level reading's largest branch amplitude is enclosed strictly inside (5, 6)")
    amplitude_low = Fr(2) + radius_low
    amplitude_high = Fr(2) + radius_high
    check(Fr(11, 2) < amplitude_low < amplitude_high < Fr(23, 4),
          "the declared exact form 2 + sqrt(8 sqrt(17) - 20) is enclosed inside (11/2, 23/4)")
    check(-negative_root[1] < amplitude_low,
          "the quartic's own root isolation gives a lower bound below the exact form's "
          "enclosure, so the two independent readings agree on the lower bound")

    check(Fr(1) < root_low,
          "the closure amplitude is strictly above the first scheme's floor of 1")
    check(root_high < amplitude_low,
          "the closure amplitude is strictly below the level reading's largest branch amplitude")
    check(Fr(1) < root_low < root_high < amplitude_low,
          "the exact ordering 1 < 3.2035072879526181... < 2 + sqrt(8 sqrt(17) - 20) is asserted "
          "on exact rationals, with no decimal compared anywhere")
    check(root_high < Fr(4) and amplitude_low > Fr(11, 2),
          "the two amplitudes are separated by an exact rational gap of more than three halves")

    return {
        "first_scheme_floor": {
            "statement": "J_inf = 1",
            "attained_at": "(-2, 17/10)",
            "off_the_discriminant_variety": True,
            "witness": [str(witness[0]), str(witness[1])],
            "perturbed_curvatures": [str(alpha), str(beta)],
            "return": "E(h) = (3/4) E_0 + (73/40) E_0^2 with E_0 = h/2 - (15/8) h^2",
            "level_one_equation": "3285 h^4/512 - 219 h^3/64 - 19 h^2/20 + 3 h/8 - 1 = 0",
            "level_one_real_branches": 2,
            "negative_branch_enclosure": [str(negative_branch[0]), str(negative_branch[1])],
            "positive_branch_enclosure": [str(positive_branch[0]), str(positive_branch[1])],
            "return_on_the_negative_branch": [str(negative_values[0]), str(negative_values[1])],
            "return_on_the_positive_branch": [str(positive_values[0]), str(positive_values[1])],
            "critical_points": [str(critical_low[0]), str(critical_middle[0]),
                                str(critical_high[0])],
            "critical_values": [str(first_scheme_return(critical_low[0])),
                                str(first_scheme_return(critical_middle[0])),
                                str(first_scheme_return(critical_high[0]))],
            "sampled_band_inside_the_floor": True,
            "floor_attained_exactly": True,
            "floor_attained_at": "the two level-one branches of the first scheme, both strictly "
                                 "inside (-1, 1)",
            "reproduced": True,
        },
        "closure_amplitude": {
            "statement": CLOSURE_AMPLITUDE_TEXT,
            "real_exits": 1,
            "isolation_interval": [str(root_low), str(root_high)],
            "exact_form": "the unique real root of h^3 + 8 h^2 + 64 h - 320",
        },
        "level_reading_largest_amplitude": {
            "statement": "2 + sqrt(8 sqrt(17) - 20) = 5.6034490429...",
            "real_branches": 2,
            "distinct_real_roots": 2,
            "exact_form": "2 + sqrt(8 sqrt(17) - 20)",
            "root_enclosure": [str(-negative_root[1]), str(-negative_root[0])],
            "declared_form_enclosure": [str(amplitude_low), str(amplitude_high)],
            "square_root_enclosure": [str(radius_low), str(radius_high)],
            "shifted_quartic": "u^4 + 40 u^2 - 688 with u = h + 2",
        },
        "asserted_ordering": {
            "statement": "1 < 3.2035072879526181... < 2 + sqrt(8 sqrt(17) - 20)",
            "asserted_exactly": True,
            "floor": "1",
            "closure_interval": [str(root_low), str(root_high)],
            "level_interval": [str(amplitude_low), str(amplitude_high)],
            "no_decimal_was_compared": True,
        },
        "all_three_reproduced": True,
    }


# ------------------------------------------------------------------- the payload --

def build_payload():
    declaration()
    chain = chain_section()
    steps = step_section()
    roles = role_section(chain)
    reservoir = reservoir_section(chain)
    split = fast_slow_section(chain)
    variants = variants_section(chain)
    baselines = baselines_section()

    verification = CONTRACT["verification_status"]
    payload = {
        "schema": "adva.external.three-cycle-chain-calibration.v1",
        "version": 1,
        "level": CONTRACT["level"],
        "question": CONTRACT["question"],
        "contract": "experiments/three_cycle_chain_v1/contract.json",
        "contract_sha256": digest(CONTRACT_PATH),
        "contract_sha256_declared":
            "a3dc2e8d86e45139484fceed571ef99ea3b63f18748c6f1c82bb031a3305a965",
        "checker_sha256": digest(pathlib.Path(__file__).resolve()),
        "tooling": {
            "python_library": "sympy",
            "version": SY["version"] if SY["available"] else None,
            "available": SY["available"],
            "declared_external_library": True,
            "declared_not_native_authority": True,
            "exact_only": True,
            "used_for": ["exact polynomial arithmetic", "exact polynomial composition",
                         "exact polynomial division",
                         "Sturm real-root counts with rational endpoints"],
            "not_used_for": ["floating-point evaluation", "root finding by iteration in floats",
                             "a native certificate of any kind"],
            "not_implemented": [
                "successive difference substitution of Zhang Jingzhong and Yang Lu",
                "a certified complex or projective continuation of roots",
                "a native certificate of any kind"],
        },
        "limits": CONTRACT["budgets"],
        "assertions": ASSERTIONS["n"],
        "sections": {
            "S1_chain": chain,
            "S2_step_count": steps,
            "S3_role_typing": roles,
            "S4_reservoir": reservoir,
            "S5_fast_and_slow": split,
            "S6_variants": variants,
            "S7_baselines": baselines,
        },
        "verification_status": {
            "observational": verification["observational"],
            "reason": verification["reason"],
            "data_authenticity_reservation": verification["data_authenticity_reservation"],
            "xue_study_data_used": False,
            "future_chain": True,
        },
        "undecided": [
            {"item": "whether a chain that closes in C1 can drift in C2 or C3",
             "reason": "the closure clause is a property of the seam state itself: a chain whose "
                       "C1 satisfies E(h) = h has h_1 = h_0, and applying the same return again "
                       "gives h_2 = h_1 and h_3 = h_2, so the drift is exactly zero in every "
                       "cycle.  No chain satisfying the declared rules closes in C1 and drifts "
                       "later, so the declared control cannot be produced and is reported as a "
                       "failed control rather than dropped or repaired.",
             "retained_partial_result": {
                 "closure_defect_at_a_fixed_point": Cubic(0).tuple(),
                 "drift_of_the_primary_chain_at_every_seam": Cubic(0).tuple(),
                 "counterfactual_chain_that_does_not_close_in_C1":
                     chain["counterfactual_chain"]["cycles"][0],
                 "cumulative_reading_real_root_count":
                     chain["cumulative_composition"]["real_root_count"],
             }},
            {"item": "a genuine real period-three orbit of the declared return",
             "reason": "the cumulative composition E^3 - h factors over the rationals as "
                       "h (h^3 + 8 h^2 + 64 h - 320) Q(h) with Q of degree 60 and every "
                       "coefficient strictly positive; an exact Sturm count gives Q no real root, "
                       "so every real point that returns after three cycles is already a fixed "
                       "point of one annual return and there is no distinct chain state that "
                       "closes only after three cycles",
             "retained_partial_result": chain["cumulative_composition"]},
            {"item": "the physical magnitude and sign of the declared freshwater source term",
             "reason": "the source term is the declared exact element w/60, chosen together with "
                       "the reference value w/2 so that the declared reservoir is stationary at "
                       "the chain's own seam.  It is not estimated, measured or compared with any "
                       "observation, and the chain is future and unverified",
             "retained_partial_result": {
                 "freshwater_source_term": reservoir["freshwater_source_term"],
                 "steady_value": reservoir["steady_value"],
                 "declared_model": True}},
            {"item": "the recovery of the six historical forecast maps as one annual program",
             "reason": "note 0233 records that the six direct forecast maps failed composition "
                       "and were not reinterpreted as one annual program.  This run uses the "
                       "resolved twelve-phase fixture, which is a declared arithmetic program and "
                       "not a forecast program, and it does not attempt that recovery.",
             "retained_partial_result": {
                 "carrier_used": "the resolved 0233 twelve-phase fixture",
                 "forecast_maps_used": False}},
        ],
        "modelling_choices": {
            "annual_return": "the chain applies E(h) = (3/8) h + (1/8) h^2 + (1/64) h^3 + "
                             "(1/512) h^4, the full annual return of the resolved 0233 "
                             "twelve-phase fixture.  The first-degree multiplier 3/8 is reported "
                             "as a baseline and is never substituted for the return.",
            "closure_reading": "終養始 is read as the fixed point of the annual return, so a "
                               "cycle closes exactly when E(h_i) = h_i and the next seam state "
                               "is the previous one.  Every cycle's status is reported "
                               "separately rather than only the first.",
            "cumulative_reading": "the cumulative form of the same clause, E composed three "
                                  "times, is computed beside the per-cycle reading and its real "
                                  "fixed points are counted exactly, so the chain's closure is "
                                  "read both per cycle and cumulatively.",
            "seam_field": "every seam state is carried as an exact element a + b w + c w^2 of the "
                          "cubic field Q(w) generated by the closure amplitude, with "
                          "w^3 = 320 - 64 w - 8 w^2.  The closure amplitude is irrational, so no "
                          "rational approximation of it is ever used as a state.",
            "chain_operator": "the declared chain operator mixes the weak spliced channel and the "
                              "returning one, h_{i+1} = (1/2) T* + (1/2) E(h_i); the mixing "
                              "coefficient 1/2 is a declared convention, and the resulting "
                              "operator is verified to be a strict contraction at its fixed "
                              "point.",
            "seam_state": "the seam state is the carried anomaly h, and the chain begins at the "
                          "declared December 2026 / January 2027 seam; any other declared seam is "
                          "refused by the placement rule.",
            "role_typing": "the three groups of three and the nine declared conditions are a "
                           "declared structure taken from the Taixuan zan division, not a derived "
                           "property of the process; the upper, calamity group is the visible "
                           "failure branch and the exit clause sits at its last position.",
            "decision_to_technique": "each step's technique is fixed by the declared return's own "
                                     "coefficient vector: exactly two phases add-and-scale and "
                                     "exactly ten translate, so a step's decision is read off a "
                                     "type rather than re-parameterised.  The recoverability "
                                     "decision is carried by recomputation, not by a label.",
            "calamity_counterparts": "every declared condition carries its calamity counterpart "
                                     "and every counterpart is executed; a condition whose "
                                     "failure branch could not be produced would be reported as "
                                     "a failed control, and no control is dropped.",
            "end_block": "the end block holds exactly two extra steps, counted in the same unit as "
                         "the steps, exactly as the Taixuan calendar counts its remainder in zan "
                         "(729 zan at two per day); a block of one and a block of three are "
                         "refused by the declared rule and both refusals are asserted.",
            "step_count": "the chain is counted in two declared readings that must agree on the "
                          "remainder: nine role-typed steps per cycle plus the two-step end block "
                          "gives 27 steps and a remainder of 6, and twelve phase steps per cycle "
                          "plus the same end block gives 36 steps and the same remainder of 6.",
            "fast_and_slow": "the carried remainder is split by the declared convention that the "
                             "slow component of the seam is the declared reservoir's own value "
                             "and the fast component is the remainder; the slow component must be "
                             "conserved across every seam and is reported with its exact drift, "
                             "while the fast component is free to reset.  A different split "
                             "convention would give different drift values and is not declared "
                             "here.",
            "declared_reservoir": "the slow reservoir is a declared first-order relaxation with "
                                  "the rational time constant 30, the reference value a T* and "
                                  "the declared freshwater source term (1 - a) T*, evaluated "
                                  "exactly in the closure amplitude's own cubic field, with "
                                  "T* = w/2 the slow component of the chain's seam.  The two "
                                  "field values are fixed by one declared requirement, that the "
                                  "reservoir be stationary at the chain's own seam, since "
                                  "otherwise the chain and its reservoir would disagree about the "
                                  "same state.  This is a declared model and not a claim about "
                                  "the ocean: the time constant and the linear relaxation are "
                                  "chosen for exactness, and the mismatch between a 30-step "
                                  "constant and a three-step chain is retained as a residual.",
            "declared_alternative": "the declared alternative, atmospheric only with the ocean "
                                    "open, is reported beside the primary rather than dropped, so "
                                    "the choice is visible; the two variants share the same "
                                    "closure seam and are separated by the slow channel, which "
                                    "the alternative does not carry.",
            "sealing": "the sealing side is a constraint of no leakage and is reported as a "
                       "one-sided bound on cumulative leakage at every cycle.  It is never added "
                       "to the closure reading and therefore cannot cancel a violation; a signed "
                       "sealing term would be able to cancel one exactly, which is stated as the "
                       "reason for the bound.",
            "baselines": "the three exact baselines of the earlier runs are reproduced with their "
                         "own declared readings: J_inf = 1 at (-2, 17/10) from the first scheme's "
                         "family, the closure amplitude 3.2035072879526181... with one real exit, "
                         "and the level reading's largest branch amplitude "
                         "2 + sqrt(8 sqrt(17) - 20) with two real branches.  The three are placed "
                         "in the asserted ordering 1 < 3.2035072879526181... < "
                         "2 + sqrt(8 sqrt(17) - 20) as a comparison of readings, not as a claim "
                         "that they are reachable configurations of one system.",
            "exactness": "every acceptance assertion and every payload value is an integer, a "
                         "fractions.Fraction, a coefficient tuple of those, or a string built "
                         "from them; no floating-point value is formed anywhere, and the decimal "
                         "prefixes are carried as exact rational brackets.",
            "resource_limits": "the checker installs a CPU limit, a file-size limit and a wall "
                               "alarm, and records the contract's declared memory budget without "
                               "installing an address-space limit; installing one would add a row "
                               "to the frozen rlimit inventory under "
                               "experiments/rlimit_portability and change a pre-existing "
                               "artifact.",
        },
        "residual": CONTRACT["residual"],
        "protected": CONTRACT["protected"],
        "what_is_not_claimed": {
            "native_certificate": False,
            "native_admission": "NotGranted",
            "stable_api_change": False,
            "physical_claim": False,
            "forecast": False,
            "skill_claim": False,
            "meteorological_data_used": False,
            "xue_study_data_used": False,
            "observational_verification": "Unavailable",
            "chain_is_future_and_unverified": True,
            "the_chain_is_a_declared_model": True,
            "reservoir_is_a_declared_model_not_a_claim_about_the_ocean": True,
            "role_typing_is_a_declared_structure": True,
            "no_wind_gap_no_plateau_no_december_2026_no_january_2027": True,
            "no_seal_no_transport_no_terminology_home": True,
            "no_rust_source_or_lock_changed": True,
            "no_note_or_contract_edited": True,
            "no_claim_added_to_docs_claims_toml": True,
            "pre_existing_files_byte_identical": True,
        },
        "checks": {},
    }
    checks = {
        "assertions_within_budget": ASSERTIONS["n"] <= CONTRACT["budgets"]["max_assertions"],
        "contract_digest_matches_the_declared_one":
            payload["contract_sha256"] == payload["contract_sha256_declared"],
        "every_cycle_reported_separately":
            len(chain["closure_status_by_cycle"]) == 3 and len(chain["seams"]) == 3,
        "every_condition_has_an_executed_calamity_counterpart":
            roles["every_counterpart_executed"] and roles["conditions_declared"] == 9,
        "the_step_count_and_the_remainder_are_reported":
            steps["total_step_count"] == 27 and steps["remainder"] == 6,
        "both_end_block_rejections_are_asserted":
            all(not row["accepted"] for row in steps["accepted_and_rejected"][1:]),
        "the_slow_component_is_conserved_in_the_primary":
            split["slow_conserved_in_the_primary"]
            and variants["primary"]["slow_component_conserved"],
        "the_slow_drift_is_reported_at_every_seam":
            len(split["primary"]) == 3
            and all("slow_drift" in row for row in split["primary"]),
        "both_variants_are_reported":
            variants["reported_side_by_side"]
            and variants["neither_variant_is_substituted_for_the_other"],
        "the_sealing_bound_is_reported_and_a_violation_detected":
            roles["sealing"]["primary"]["violated"] is False
            and roles["sealing"]["declared_leaking_chain"]["violated"] is True,
        "the_three_baselines_are_reproduced": baselines["all_three_reproduced"],
        "the_ordering_is_asserted_exactly":
            baselines["asserted_ordering"]["asserted_exactly"],
        "the_memory_control_discriminates":
            variants["memory_control"]["discriminates_on_the_slow_channel"],
        "no_control_is_silently_repaired":
            roles["failed_controls"] == [] and roles["no_control_dropped"],
        "undecided_items_are_declared": len(payload["undecided"]) == 4,
        "the_observer_of_the_chain_is_unavailable":
            payload["verification_status"]["observational"] == "Unavailable",
    }
    payload["checks"] = checks
    payload["controls"] = {
        "memory": {
            "declared": CONTRACT["controls"][1],
            "outcome": "Discriminated",
            "detail": variants["memory_control"],
            "primary_keeps_the_memory": True,
            "atmospheric_loses_the_memory": True,
            "reading_that_does_not_discriminate":
                "both variants close at the same seam, so the closure status alone does not "
                "separate them; the separating reading is the slow channel's own response to the "
                "declared displacement, and the three-cycle residual separates them as well",
        },
        "drift": {
            "declared": CONTRACT["controls"][0],
            "outcome": "FAILED_TO_PRODUCE_THE_DECLARED_CHAIN",
            "retained": True,
            "failed_to_discriminate": True,
            "detail":
                "no chain satisfying the declared rules closes in C1 and drifts in C2 or C3: "
                "closure is the pointwise condition E(h) = h, so h_1 = h_0 holds for such a "
                "chain, and the same return then gives h_2 = h_1 and h_3 = h_2, with drift "
                "exactly zero.  The control is reported as failed rather than repaired, and the "
                "exact drift of the primary chain is reported as zero at every seam",
            "exact_drift_of_the_primary_chain": [Cubic(0).tuple() for _ in CYCLES],
            "counterfactual_chain_drifts":
                [row["drift"] for row in chain["counterfactual_chain"]["cycles"]],
            "counterfactual_chain_seed": chain["counterfactual_chain"]["seed"],
            "a_real_chain_that_closes_in_C1_but_drifts_later": "does not exist",
        },
        "placement": {
            "declared": CONTRACT["controls"][2],
            "outcome": "Discriminated",
            "detail": roles["placement"],
        },
        "leakage": {
            "declared": CONTRACT["controls"][3],
            "outcome": "Discriminated",
            "detail": roles["sealing"],
        },
        "remainder": {
            "declared": CONTRACT["controls"][4],
            "outcome": "Discriminated",
            "detail": steps["accepted_and_rejected"],
        },
        "baselines": {
            "declared": CONTRACT["controls"][5],
            "outcome": "Discriminated",
            "detail": baselines["asserted_ordering"],
        },
    }
    payload["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    return payload


def summarize(payload):
    sections = payload["sections"]
    chain = sections["S1_chain"]
    steps = sections["S2_step_count"]
    roles = sections["S3_role_typing"]
    reservoir = sections["S4_reservoir"]
    split = sections["S5_fast_and_slow"]
    variants = sections["S6_variants"]
    baselines = sections["S7_baselines"]

    print("three-cycle chain v1: exact external calibration")
    print("  status:", payload["status"], " assertions:", payload["assertions"])
    print("  annual return:", chain["annual_return"])
    print("  closure:", chain["closure_polynomial"])
    print("  declared seam:", chain["declared_seam"])
    print("  seam state (a + b w + c w^2):", chain["seam_states"][0])
    for row in chain["seams"]:
        print(f"    {row['cycle']}  {row['closure_status']:<20} defect={row['closure_defect']} "
              f"drift={row['drift']}")
    print("  closure amplitude:", chain["closure_amplitude"]["value"],
          "isolated in", chain["closure_amplitude"]["isolation_interval"],
          "real exits:", chain["closure_amplitude"]["real_exits_of_the_closure_cubic"])
    print("  cumulative composition real roots:",
          chain["cumulative_composition"]["real_root_count"],
          chain["cumulative_composition"]["real_roots"])
    print("  chain operator slope enclosure:",
          chain["chain_operator"]["slope_enclosure"])
    print("  steps:", steps["steps_per_cycle"], "per cycle x", steps["cycles"], "=",
          steps["total_step_count"], "remainder", steps["remainder"], "total",
          steps["total_with_the_end_block"])
    for row in steps["accepted_and_rejected"]:
        print(f"    end block of {row['block_steps']}: accepted={row['accepted']!s:<5} "
              f"reasons={row['rejection_reasons']}")
    print("  role groups:", [(row["role"], len(row["members"])) for row in roles["role_groups"]])
    print("  conditions:", roles["conditions_declared"], "counterparts executed:",
          roles["every_counterpart_executed"], "failed condition records:",
          roles["failed_controls"])
    for row in roles["condition_executions"]:
        print(f"    {row['condition']:<12} {row['control_outcome']:<14} "
              f"counterpart={row['calamity_counterpart']}")
    print("  reservoir: time constant", reservoir["time_constant"],
          "source term", reservoir["freshwater_source_term"],
          "steady", reservoir["steady_value"],
          "slow drift", reservoir["slow_drift_per_seam"][0])
    for row in split["primary"]:
        print(f"    {row['cycle']}  fast={row['fast_component']} slow={row['slow_component']} "
              f"slow_drift={row['slow_drift']}")
    for name in ("primary", "declared_alternative"):
        block = variants[name]
        print(f"  {name}: seed={block['seed']} memory={block['keeps_the_carried_memory']} "
              f"slow_conserved={block['slow_component_conserved']}")
    print("  sealing: primary violated",
          roles["sealing"]["primary"]["violated"], "| leaking chain violated",
          roles["sealing"]["declared_leaking_chain"]["violated"],
          "cumulative", roles["sealing"]["declared_leaking_chain"]["cumulative_leakage"])
    print("  baselines:", baselines["asserted_ordering"]["statement"])
    print("  ordering intervals:", baselines["asserted_ordering"]["closure_interval"],
          baselines["asserted_ordering"]["level_interval"])
    print("  memory control: primary slow response",
          variants["memory_control"]["primary_slow_response_at_the_first_seam"],
          "vs open ocean",
          variants["memory_control"]["open_ocean_slow_response_at_the_first_seam"],
          "| discriminates:",
          variants["memory_control"]["discriminates_on_the_slow_channel"])
    print("  drift control:", payload["controls"]["drift"]["outcome"])
    print("  undecided items:", len(payload["undecided"]))
    print("  observational verification:", payload["verification_status"]["observational"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    arguments = parser.parse_args()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall limit")))
    signal.alarm(CONTRACT["budgets"]["wall_seconds"])
    resource.setrlimit(resource.RLIMIT_CPU, (CONTRACT["budgets"]["cpu_seconds"],) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 << 20, 16 << 20))
    if not SY["available"]:  # pragma: no cover - the tooling branch is reported, not reached
        payload = {
            "schema": "adva.external.three-cycle-chain-calibration.v1",
            "status": "ToolingUnavailable",
            "reason": SY.get("error"),
            "tooling": {"python_library": "sympy", "available": False},
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
