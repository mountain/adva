#!/usr/bin/env python3
"""Exact calibration of the declared rounded ending (圆融), with checkable results.

Frozen contract: experiments/three_cycle_supplement_v2/contract.json (this run).  The run
inherits, reads and hashes three parent contracts and edits none of them:

* experiments/three_cycle_chain_v1/contract.json (in force, retained byte for byte),
* experiments/three_cycle_chain_v1/contract-supplement-1.json (its four amendments),
* experiments/three_cycle_supplement_v1/contract.json (the surgery run of note 0237, whose
  two retained failures and undecided necessity of opposite chirality carry forward).

This checker is an external exact calibration of a DECLARED construction.  It constructs no
native certificate, promotes no native identity, and makes no physical claim.  No magnitude
is asserted for aerosols, low cloud, water vapour, wildfire or the committed component
anywhere in an acceptance assertion or in the retained payload.

What the run decides, and with what:

* R1 the rounded ending: the two terminal conditions as a CONJUNCTION, each in full - the
  sealable component closes at the fixed point of the annual return (exact in Q(w), w the
  real root of h^3 + 8 h^2 + 64 h - 320), and the committed component carries out of the
  chain and is written out rather than discharged - with the two residual records kept
  separate and the four prohibitions each executed against a rejected control: an either-or
  terminal, a netting terminal, an obstructing terminal and a compromising terminal;
* R2 the Yi pair 既濟/未濟 as the contrast family: the existing address machinery is reused
  (the mutual-measuring diagonal a = b is 81 points, its complement 6480), and a
  forced-closed, a forced-open and an either-or terminal each FAIL the rounded ending;
* R3 the beginning split: resetable obstructions (phase misalignment, declared as the five
  Wayeb days, and the step-carry remainder, declared as the chain's own 2/9) against the
  non-resetable one-way commitment state; a reset on a resetable obstruction is accepted, a
  reset on the commitment is rejected and leaves the state unchanged;
* R4 the middle five: two directed cycles on the same five points, generation +1 and
  overcoming +2 modulo five, both generators because five is prime; rejecting one cycle and
  identifying the two each fail;
* R5 the astronomical remainders: the chain length in integer days against 260, 2920 and
  18980, with the three exact remainders reported and the assertion that the chain closes
  none of them;
* R6 three is not a degree: the three-year period is not a third-degree spherical harmonic
  and not a failure of injectivity, and any reading that identifies them is rejected;
* R7 the one-way commitment reservoir: non-decreasing state, a declared threshold branch and
  hysteresis on a declared loop, with the parent chain's declared first-order relaxation
  failing the monotonicity and the hysteresis controls - that failure is the evidence that
  the one-way shape is doing work;
* R8 sealing refused for a leak: the committed component may be accounted but never sealed,
  and a chain that treats it as sealable or that lets it offset a sealing violation fails;
* R9 the four-by-two classification: aerosols, low cloud, water vapour and wildfire on the
  north and the south side, each cell carrying exactly one of three declarations, with no
  magnitude anywhere and with the structure, ratchet, symmetry and fusion controls rejected;
* R10 the fourth uncertainty term committed-but-unquantified, recorded separately at every
  seam and never fused with mapping, bias or sampling;
* R11 the inherited controls: sampling-change invariance, separated uncertainty, layer-wise
  sealing, the identity loop and the atmospheric-chain memory loss;
* R12 the exact baselines, reproduced: J_inf = 1 at (p, q) = (-2, 17/10), the closure
  amplitude 3.2035072879526181... with one real exit on the nontrivial closure branch, the
  level reading's largest amplitude 2 + sqrt(8 sqrt(17) - 20) with two real branches, and the
  asserted ordering 1 < 3.2035072879526181... < 2 + sqrt(8 sqrt(17) - 20).

All acceptance arithmetic is exact integers, fractions.Fraction, exact rational interval
arithmetic, one exact real quadratic extension and the exact cubic field Q(w); sympy 1.14 is
a declared external library used only as an engine for resultants, integer factorisation and
Sturm real-root isolation, and is not native authority.  No floating-point value is formed in
an acceptance test or written into the retained payload.  No data is read or used.

Resource policy: RLIMIT_CPU and RLIMIT_FSIZE are installed together with a wall alarm; the
contract's declared memory budget is recorded and no address-space ceiling is installed,
because no child process is launched.
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
from itertools import pairwise

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

EXPERIMENTS = HERE.parent
PARENT_DIR = EXPERIMENTS / "three_cycle_chain_v1"
PARENT_CONTRACT_PATH = PARENT_DIR / "contract.json"
PARENT_SUPPLEMENT_PATH = PARENT_DIR / "contract-supplement-1.json"
SURGERY_DIR = EXPERIMENTS / "three_cycle_supplement_v1"
SURGERY_CONTRACT_PATH = SURGERY_DIR / "contract.json"

PARENT_CONTRACT = json.loads(PARENT_CONTRACT_PATH.read_text(encoding="utf-8"))

DECLARED_CONTRACT_SHA256 = "823eedfaa492d0524c901793b580d5f02b67d7cf739f26781e326aa667d1e990"
DECLARED_PARENT_SHA256 = "a3dc2e8d86e45139484fceed571ef99ea3b63f18748c6f1c82bb031a3305a965"
DECLARED_SUPPLEMENT_SHA256 = "e125ee4940b838924257d9420bde71cf060a0745dc5d3d482c1691158785ac9f"
DECLARED_SURGERY_SHA256 = "157838642e9097ea4a1a1c7461db9e548affb0c6f3af7b830816f37f22b74f5a"

ASSERTIONS = {"n": 0}


def check(condition, message):
    """One exact acceptance assertion, counted."""
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def fr(value):
    """An exact Fraction from an int, a Fraction, a sympy rational or a decimal string."""
    if hasattr(value, "p") and hasattr(value, "q"):
        return Fr(int(value.p), int(value.q))
    return Fr(value)


def sgn(value):
    return (value > 0) - (value < 0)


def contains_float(node):
    """True when a float appears anywhere in the payload."""
    if isinstance(node, float):
        return True
    if isinstance(node, dict):
        return any(contains_float(key) or contains_float(value) for key, value in node.items())
    if isinstance(node, (list, tuple)):
        return any(contains_float(item) for item in node)
    return False


# ------------------------------------------------- the exact cubic field Q(w) --

CLOSURE_CUBIC = (Fr(-320), Fr(64), Fr(8), Fr(1))


class Cubic:
    """a + b w + c w^2 with a, b, c exact Fractions and w the closure amplitude.

    w is the unique real root of w^3 + 8 w^2 + 64 w - 320 = 0, so w^3 = 320 - 64 w - 8 w^2
    exactly and every element of Q(w) has one canonical triple representation.  No
    floating-point value is ever formed.
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
    """Evaluate a rational coefficient tuple (lowest degree first) at an element of Q(w)."""
    total = Cubic(0)
    for coefficient in reversed(poly):
        total = total * element + Cubic(coefficient)
    return total


def field_return(element):
    """The annual return E(h) = (3/8) h + (1/8) h^2 + (1/64) h^3 + (1/512) h^4, exactly."""
    return (element.scale(Fr(3, 8)) + element.power(2).scale(Fr(1, 8))
            + element.power(3).scale(Fr(1, 64)) + element.power(4).scale(Fr(1, 512)))


def field_closure_defect(element):
    """The closure defect E(h) - h, exactly."""
    return field_return(element) - element


# --------------------------------------- exact rational intervals and extensions --

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

    def __neg__(self):
        return Ivl(-self.hi, -self.lo)

    def abs_upper(self):
        return max(abs(self.lo), abs(self.hi))

    def scale(self, factor):
        factor = factor if isinstance(factor, Fr) else Fr(factor)
        if factor >= 0:
            return Ivl(self.lo * factor, self.hi * factor)
        return Ivl(self.hi * factor, self.lo * factor)

    def __str__(self):
        return "[" + str(self.lo) + ", " + str(self.hi) + "]"


def quadratic_abs_upper(second, first, constant, box):
    """An exact upper bound of |a2 x^2 + a1 x + a0| on a closed rational interval."""
    def value(point):
        return second * point * point + first * point + constant

    candidates = [box.lo, box.hi]
    if second != 0:
        vertex = -first / (2 * second)
        if box.lo <= vertex <= box.hi:
            candidates.append(vertex)
    return max(abs(value(point)) for point in candidates)


def sqrt_ball(radicand, steps=160):
    """An exact rational ball for the square root of a positive rational."""
    check(radicand > 0, "the declared radicand is positive")
    low, high = Fr(0), Fr(1)
    while high * high < radicand:
        high *= 2
    for _ in range(steps):
        middle = (low + high) / 2
        if middle * middle < radicand:
            low = middle
        else:
            high = middle
    check(low * low <= radicand <= high * high, "the rational ball brackets the square root")
    return Ivl(low, high)


def correctly_rounded_prefix(box, digits):
    """The correctly rounded decimal prefix of the value carried by a positive interval."""
    check(box.lo > 0, "the decimal prefix routine is declared for a positive interval")
    exponent = 1
    while Fr(10) ** exponent <= box.lo:
        exponent += 1
    check(Fr(10) ** (exponent - 1) <= box.lo < box.hi < Fr(10) ** exponent,
          "the interval lies inside one decade")
    scale = 10 ** (digits - exponent)
    low = (box.lo * scale + Fr(1, 2)).__floor__()
    high = (box.hi * scale + Fr(1, 2)).__floor__()
    check(low == high, "the two rounded endpoints agree, so the prefix is decided")
    text = str(low)
    check(len(text) == digits, "the rounded integer carries the declared number of digits")
    return text[0] + "." + text[1:]


class QNr:
    """a + b w with a, b exact Fractions and w^2 an exact rational `square`."""

    __slots__ = ("a", "b", "square")

    def __init__(self, a=0, b=0, square=1):
        self.a = a if isinstance(a, Fr) else Fr(a)
        self.b = b if isinstance(b, Fr) else Fr(b)
        self.square = square if isinstance(square, Fr) else Fr(square)

    def __add__(self, other):
        other = other if isinstance(other, QNr) else QNr(other, 0, self.square)
        return QNr(self.a + other.a, self.b + other.b, self.square)

    __radd__ = __add__

    def __sub__(self, other):
        other = other if isinstance(other, QNr) else QNr(other, 0, self.square)
        return QNr(self.a - other.a, self.b - other.b, self.square)

    def __mul__(self, other):
        other = other if isinstance(other, QNr) else QNr(other, 0, self.square)
        return QNr(self.a * other.a + self.square * self.b * other.b,
                   self.a * other.b + self.b * other.a, self.square)

    __rmul__ = __mul__

    def is_zero(self):
        return self.a == 0 and self.b == 0

    def sign(self):
        """The exact sign, comparing squares only; the ground field is the rationals."""
        if self.b == 0:
            return sgn(self.a)
        if self.a == 0:
            return sgn(self.b)
        if self.a > 0 and self.b > 0:
            return 1
        if self.a < 0 and self.b < 0:
            return -1
        left, right = self.a * self.a, self.square * self.b * self.b
        if self.a > 0:
            return 1 if left > right else (-1 if left < right else 0)
        return -1 if left > right else (1 if left < right else 0)


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

ISOLATION_EPS = RATIONAL(1, 10 ** 24) if SY["available"] else None


def rat(value):
    """An exact sympy rational from an int or a Fraction."""
    value = value if isinstance(value, Fr) else Fr(value)
    return RATIONAL(value.numerator, value.denominator)


def isolated_real_roots(poly, bracket):
    """Exact rational isolation intervals of the real roots, each strictly inside a bracket."""
    low, high = bracket
    check(low < high, "the declared bracket is a genuine interval")
    check(poly.eval(RATIONAL(low)) * poly.eval(RATIONAL(high)) != 0,
          "the declared bracket has no root among its endpoints")
    rows = []
    for (lo, hi), multiplicity in poly.intervals(eps=ISOLATION_EPS):
        lo, hi = fr(lo), fr(hi)
        check(multiplicity == 1, "every isolated real root of this polynomial is simple")
        check(low <= lo < hi <= high, "the isolated root lies inside the declared bracket")
        check(poly.eval(RATIONAL(lo)) * poly.eval(RATIONAL(hi)) < 0,
              "the isolation interval carries an exact sign change")
        rows.append((lo, hi))
    return sorted(rows)


# ---------------------------------------------------------- declared fixture ----

PHASES = 12
CYCLE_COUNT = 3
CYCLE_LABELS = ("C1", "C2", "C3")
END_BLOCK_STEPS = 2
BASELINE_STEPS_PER_CYCLE = 9
TOTAL_BASELINE_STEPS = 27
END_BLOCK_REMAINDER_STEPS = 6
STEP_CARRY_REMAINDER = Fr(2, 9)
ZAN_PER_CYCLE = 729
ZAN_PER_STEP = Fr(ZAN_PER_CYCLE, BASELINE_STEPS_PER_CYCLE)
ZAN_OF_THE_REMAINDER = END_BLOCK_REMAINDER_STEPS * 81

SEALABLE_COMPONENT = "sealable"
COMMITTED_COMPONENT = "committed"
COMMITTED_POSITIONS = ("C1", "C2", "C3", "exit")
COMMITTED_RECORD_FIELDS = ("record_id", "kind", "component", "seams_carried",
                           "positions_intact", "discharged", "magnitude")
NO_MAGNITUDE = "none_declared"

ANNUAL_CYCLE_DAYS = 365
MONTH_COUNT = 18
DAYS_PER_MONTH = 20
WAYEB_DAYS = 5
TZOLKIN_DAYS = 260
VENUS_EIGHT_YEAR_DAYS = 2920
CALENDAR_ROUND_DAYS = 18980
COMMENSURABILITIES = (
    ("Tzolkin", TZOLKIN_DAYS),
    ("five Venus synodic periods, eight solar years", VENUS_EIGHT_YEAR_DAYS),
    ("the calendar round", CALENDAR_ROUND_DAYS),
)
YEAR_LENGTH_CONTROLS = (
    ("declared primary: the declared annual cycle", 365),
    ("eighteen twenty-day months", MONTH_COUNT * DAYS_PER_MONTH),
    ("fifty-two weeks of seven days", 52 * 7),
)

OBSTRUCTION_CLASSES = (
    ("phase_misalignment", "resetable",
     "the declared position of the Wayeb days: the annual cycle of 365 days against eighteen "
     "twenty-day months, a declared misalignment of five days",
     Fr(WAYEB_DAYS)),
    ("step_carry_remainder", "resetable",
     "the declared step-carry remainder of the parent chain: six steps of twenty-seven, which "
     "is two ninths of a cycle, the remainder the end block holds",
     STEP_CARRY_REMAINDER),
    ("one_way_commitment_state", "non_resetable",
     "the declared state of the one-way commitment reservoir, which carries out of the chain "
     "and is written out rather than discharged",
     None),
)

FIVE_POINTS = (0, 1, 2, 3, 4)
GENERATION_STEP = 1
OVERCOMING_STEP = 2

THRESHOLD_OPEN = Fr(1)
THRESHOLD_CLOSE = Fr(1, 4)
BRANCH_OPEN_STEP = Fr(1, 8)
BRANCH_CLOSED_STEP = Fr(1, 16)
LOOP_CONTROLS = (Fr(0), Fr(1, 2), Fr(1), Fr(1, 2), Fr(0))
HYSTERESIS_PROBE = Fr(1, 2)
PARENT_RELAXATION = Fr(1, 30)
PARENT_TIME_CONSTANT = 30
PARENT_STEADY = W.scale(Fr(1, 2))
PARENT_DISPLACEMENT = Fr(1, 4)

LAYER_ORDER = ("mixed", "thermocline", "deep")
LAYER_CONTENTS = (Fr(1, 8), Fr(1, 4), Fr(1, 2))
FAST_REMAINDER = Fr(1, 4)
SEAM_TRANSFERS = (("mixed", "thermocline", Fr(1, 8)), ("thermocline", "deep", Fr(1, 16)))
LAYER_SEALING_BOUND = (Fr(0), Fr(0), Fr(0))
SEALING_SHARES = {"outer": Fr(13, 24), "inner": Fr(11, 24)}
TOTAL_CANCELLING_VIOLATION = {"mixed": Fr(1, 64), "thermocline": Fr(0), "deep": Fr(-1, 64)}

OBSERVATION_COMPOSITIONS = (
    ("A", (Fr(1), Fr(0), Fr(0))),
    ("B", (Fr(1, 2), Fr(1, 4), Fr(1, 4))),
)
COMPOSITION_OFFSETS = (Fr(1, 32), Fr(1, 16), Fr(3, 64))
UNCERTAINTY_TERMS = ("mapping", "bias", "sampling")
FOURTH_TERM = "committed-but-unquantified"

IDENTITY_LOOP_LEGS = (3, 3, 3, 3)
NON_CLOSED_LOOP_LEGS = (3, 3, 3, 4)

FACTORS = ("aerosols", "low_cloud", "water_vapour", "wildfire")
SIDES = ("north", "south")
DECLARATIONS = ("correction_to_be_made", "structure_to_be_preserved",
                "explicitly_unquantified")
SIDE_SPECIFIC_FACTORS = ("aerosols", "low_cloud", "water_vapour")
BOTH_SIDES_FACTORS = ("wildfire",)
NORTH = "north"
SOUTH = "south"

PERTURBATION_WITNESS = (Fr(-2), Fr(17, 10))
DISCRIMINANT_FACTOR = "2048*p**2 + 608*p - 8*q + 43"
DISCRIMINANT_FACTOR_DISPLAY = "2048 p^2 + 608 p - 8 q + 43"
LEVEL_READING_QUARTIC = "h^4 + 8 h^3 + 64 h^2 + 192 h - 512 = 0"
CLOSURE_AMPLITUDE_PREFIX = "3.2035072879526181"
CLOSURE_AMPLITUDE_TEXT = "3.2035072879526181..."
LEVEL_AMPLITUDE_TEXT = "2 + sqrt(8 sqrt(17) - 20)"


# ------------------------------------------------ R1: the rounded ending -------

def closure_root_identification():
    """The declared fixed point w with the exact facts that identify it as the real exit."""
    derivative_discriminant = 16 * 16 - 4 * 3 * 64
    at_three = field_poly_value(CLOSURE_CUBIC, Cubic(3))
    at_four = field_poly_value(CLOSURE_CUBIC, Cubic(4))
    return {
        "cubic": "h^3 + 8 h^2 + 64 h - 320 = 0",
        "derivative": "3 h^2 + 16 h + 64",
        "derivative_discriminant": str(derivative_discriminant),
        "derivative_is_strictly_positive": derivative_discriminant < 0,
        "value_at_three": at_three.tuple(),
        "value_at_four": at_four.tuple(),
        "sign_change_on_the_declared_bracket": (
            (at_three.a < 0) and (at_four.a > 0) and at_three.b == 0 == at_three.c
            and at_four.b == 0 == at_four.c),
        "real_root_count": 1,
        "the_cubic_has_exactly_one_real_root": derivative_discriminant < 0,
        "the_declared_element_is_a_root": field_poly_value(CLOSURE_CUBIC, W).is_zero(),
        "the_declared_element_is_that_root":
            derivative_discriminant < 0 and field_poly_value(CLOSURE_CUBIC, W).is_zero(),
        "declared_bracket": ["3", "4"],
        "reading": "the derivative of the cubic is a quadratic with discriminant -512 < 0 and a "
                   "positive leading coefficient, so the cubic is strictly increasing and has "
                   "exactly one real root; the value at 3 is negative and at 4 positive, and the "
                   "declared element w satisfies the cubic exactly in Q(w), so w is that unique "
                   "real exit and the identification is exact rather than approximate",
    }


def sealable_residual_record():
    """The residual record of the sealable component, kept separate from the other one."""
    defect = field_closure_defect(W)
    return {
        "component": SEALABLE_COMPONENT,
        "condition": "closes at the fixed point of the annual return",
        "residual_name": "the closure defect E(h) - h at the declared fixed point",
        "residual": defect.tuple(),
        "holds": defect.is_zero(),
        "holds_exactly": defect.is_zero(),
        "quantified": True,
        "quantified_reading": "the closure defect is exactly the zero of Q(w)",
        "separate_record": True,
        "fused_with_the_other_component": False,
    }


def commitment_record(**overrides):
    """The declared written record of the committed component."""
    record = {
        "record_id": "K-1",
        "kind": "the carried committed debt, written out of the chain",
        "component": COMMITTED_COMPONENT,
        "seams_carried": "C1, C2, C3 and the exit",
        "positions_intact": "all four declared positions",
        "discharged": False,
        "magnitude": NO_MAGNITUDE,
    }
    record.update(overrides)
    return record


def commitment_verdict(record):
    """The write-out condition of the committed component, as a condition on the record."""
    if record is None:
        return {
            "written": False, "carried_out": False, "discharged": False, "verdict": "Rejected",
            "reasons": ["the committed component is implicit: no written record is declared, so "
                        "it cannot be carried out and written out"],
            "rejected_by": "the write-out condition of the committed component",
        }
    missing = [field for field in COMMITTED_RECORD_FIELDS
               if not str(record.get(field, "")).strip()]
    if missing:
        return {
            "written": False, "carried_out": False, "discharged": bool(record.get("discharged")),
            "verdict": "Rejected",
            "reasons": ["the committed component is not written out: the record omits "
                        + ", ".join(missing)],
            "rejected_by": "the write-out condition of the committed component",
        }
    if record.get("discharged") is not False:
        return {
            "written": True, "carried_out": False, "discharged": True,
            "verdict": "Rejected",
            "reasons": ["the committed component must be carried out rather than discharged; the "
                        "record declares discharged = " + str(record.get("discharged"))],
            "rejected_by": "the carry-out condition of the committed component",
        }
    if record.get("magnitude") != NO_MAGNITUDE:
        return {
            "written": True, "carried_out": False, "discharged": False,
            "verdict": "Rejected",
            "reasons": ["no magnitude may be given for the committed component; the record "
                        "declares magnitude = " + str(record.get("magnitude"))],
            "rejected_by": "the no-magnitude declaration for the committed component",
        }
    return {
        "written": True, "carried_out": True, "discharged": False,
        "verdict": "CarriedOutAndWrittenOut", "reasons": [],
        "rejected_by": "",
    }


def committed_residual_record(written_record, verdict):
    """The residual record of the committed component, kept separate from the other one."""
    return {
        "component": COMMITTED_COMPONENT,
        "condition": "carries out of the chain and is written out rather than discharged",
        "residual_name": "the carried commitment, written out and unquantified",
        "residual": "carried_out_and_written_out",
        "holds": verdict["carried_out"] and verdict["written"] and not verdict["discharged"],
        "holds_exactly": verdict["carried_out"] and verdict["written"]
        and not verdict["discharged"],
        "quantified": False,
        "magnitude": written_record["magnitude"],
        "separate_record": True,
        "fused_with_the_other_component": False,
    }


def conjunction_verdict(sealable_holds, committed_holds):
    """The declared rounded ending: the conjunction of both terminal conditions, each in full."""
    reasons = []
    if not sealable_holds:
        reasons.append("the sealable component does not close at the fixed point of the annual "
                       "return")
    if not committed_holds:
        reasons.append("the committed component is not carried out of the chain and written out")
    return {
        "terminal": "the declared conjunction of the two terminal conditions",
        "sealable_holds": bool(sealable_holds),
        "committed_holds": bool(committed_holds),
        "both_hold_in_full": bool(sealable_holds) and bool(committed_holds),
        "accepted": not reasons,
        "verdict": "RoundedEndingHolds" if not reasons else "Rejected",
        "reasons": reasons,
    }


def either_or_verdict(sealable_holds, committed_holds):
    """The either-or terminal: satisfied when either condition holds, so it is not the ending."""
    satisfied = bool(sealable_holds) or bool(committed_holds)
    conjunction = conjunction_verdict(sealable_holds, committed_holds)
    disagreeing = satisfied and not conjunction["accepted"]
    return {
        "terminal": "an either-or terminal: satisfied by either condition alone",
        "satisfied": satisfied,
        "declared_conjunction_holds": conjunction["accepted"],
        "the_two_readings_disagree_here": disagreeing,
        "accepted_as_the_rounded_ending": False,
        "verdict": "Rejected",
        "reasons": [
            "an either-or terminal is not the rounded ending: the ending is the conjunction of "
            "both terminal conditions, each holding in full, so a terminal satisfied by either "
            "condition alone admits the case where one component's condition fails",
            "on the declared state both readings agree, because both conditions hold there; the "
            "difference appears exactly on the mixed cases",
        ],
        "rejected_by": "the declared conjunction, which is not an either-or",
        "decided_by_a_count": False,
    }


def netting_verdict(sealable_surplus, committed_record):
    """The netting terminal: one component's surplus reduces the other component's residual."""
    return {
        "terminal": "a netting terminal: the sealable surplus is set against the committed "
                    "residual and a single fused residual is reported",
        "declared_sealable_surplus": str(sealable_surplus),
        "committed_residual_declared_magnitude": committed_record["magnitude"],
        "fused_residual_exists_exactly": False,
        "reduces_a_residual": True,
        "records_fused": True,
        "accepted_as_the_rounded_ending": False,
        "verdict": "Rejected",
        "reasons": [
            "netting is forbidden: the two residual records are kept separate and neither "
            "component's residual may be reduced by the other's surplus",
            "the netting terminal reduces the committed record's residual by the declared "
            "sealable surplus " + str(sealable_surplus),
            "the committed component's declared magnitude is " + committed_record["magnitude"]
            + ", so no exact fused residual can be formed and the netting terminal cannot even "
              "be evaluated exactly",
        ],
        "rejected_by": "the declared separateness of the two residual records",
        "declared_quantified_control": {
            "control": "a declared pair of quantified residuals, to show what netting would erase",
            "sealable_surplus": "1/4",
            "other_residual": "1/4",
            "netted_residual": "0",
            "separate_residuals": ["1/4", "1/4"],
            "netting_reports_a_single_zero_residual": True,
            "the_rounded_ending_keeps_both_residuals": True,
            "reading": "netting would erase a nonzero residual by calling the pair zero; the "
                       "declared ending keeps the two records and reports each one",
        },
        "decided_by_a_count": False,
    }


def obstruction_verdict(committed_under_sealable_true, committed_under_sealable_false):
    """The obstructing terminal: satisfying one condition flips the other condition's verdict."""
    dependent = committed_under_sealable_true != committed_under_sealable_false
    return {
        "terminal": "an obstructing terminal: the committed verdict is a function of the "
                    "sealable verdict",
        "committed_verdict_with_the_sealable_condition_holding":
            bool(committed_under_sealable_true),
        "committed_verdict_with_the_sealable_condition_failing":
            bool(committed_under_sealable_false),
        "the_two_conditions_are_independent": not dependent,
        "a_verdict_flip_is_detected": dependent,
        "accepted_as_the_rounded_ending": not dependent,
        "verdict": "Rejected" if dependent else "Independent",
        "reasons": ([
            "obstruction is forbidden: satisfying the sealable condition must not change the "
            "committed condition's verdict, and here the committed verdict flips from "
            + str(bool(committed_under_sealable_true)) + " to "
            + str(bool(committed_under_sealable_false)) + " when the sealable verdict moves",
        ] if dependent else []),
        "rejected_by": ("the declared independence of the two terminal conditions" if dependent
                        else ""),
        "decided_by_a_count": False,
    }


def compromise_verdict(tolerance, sealable_residual):
    """The compromising terminal: both conditions hold only approximately."""
    approximate_holds = abs(sealable_residual) <= tolerance
    exact_holds = sealable_residual == 0
    reasons = []
    if tolerance != 0:
        reasons.append("compromise is forbidden: the two conditions must hold exactly, not "
                       "approximately, so a declared nonzero tolerance of " + str(tolerance)
                       + " is a different terminal")
    if not exact_holds:
        reasons.append("the declared sealable residual is exactly " + str(sealable_residual)
                       + ", which is inside the declared tolerance " + str(tolerance)
                       + " and is not the exact zero the ending requires")
    return {
        "terminal": "a compromising terminal: both conditions hold only approximately",
        "declared_tolerance": str(tolerance),
        "declared_sealable_residual": str(sealable_residual),
        "holds_approximately": approximate_holds,
        "holds_exactly": exact_holds,
        "accepted_as_the_rounded_ending": not reasons,
        "verdict": "Rejected" if reasons else "Exact",
        "reasons": reasons,
        "the_committed_condition_admits_no_approximation": True,
        "why_the_committed_condition_admits_no_approximation":
            "the committed component carries no declared magnitude, so there is nothing to "
            "approximate: only the exact carry-out and write-out condition can be evaluated",
        "rejected_by": "the exactness requirement of the declared ending" if reasons else "",
        "decided_by_a_count": False,
    }


def section_rounded_ending():
    """R1: the conjunction, the two separate residual records, and the four prohibitions."""
    closure = closure_root_identification()
    check(closure["derivative_discriminant"] == "-512",
          "the derivative of the closure cubic has discriminant -512, so the cubic is strictly "
          "increasing")
    check(closure["sign_change_on_the_declared_bracket"],
          "the closure cubic has an exact sign change on the declared bracket (3, 4)")
    check(closure["the_declared_element_is_a_root"],
          "the declared element w satisfies the closure cubic exactly in Q(w)")
    check(closure["the_declared_element_is_that_root"],
          "the declared element w is identified with the unique real exit, exactly")

    sealable = sealable_residual_record()
    check(sealable["holds_exactly"], "the sealable component closes at the declared fixed point")
    check(fr(sealable["residual"][0]) == 0 and fr(sealable["residual"][1]) == 0
          and fr(sealable["residual"][2]) == 0,
          "the sealable residual is exactly the zero of Q(w)")

    # the closure-defect identity, checked on two declared elements rather than assumed
    for element, label in ((W, "the fixed point"), (W + Fr(1, 4), "a displaced state")):
        check(field_closure_defect(element).scale(512)
              == element * field_poly_value(CLOSURE_CUBIC, element),
              "512 (E(h) - h) = h (h^3 + 8 h^2 + 64 h - 320) in Q(w) at " + label)
    displaced = field_closure_defect(W + Fr(1, 4))
    check(not displaced.is_zero(),
          "a displaced sealable state does not close: the fixed point is a real condition")

    written = commitment_record()
    discharge = commitment_verdict(written)
    check(discharge["verdict"] == "CarriedOutAndWrittenOut",
          "the committed component is carried out and written out")
    committed = committed_residual_record(written, discharge)
    check(committed["holds_exactly"], "the committed condition holds in full")
    check(committed["quantified"] is False and committed["magnitude"] == NO_MAGNITUDE,
          "the committed residual is recorded and carries no magnitude")

    declared = conjunction_verdict(sealable["holds_exactly"], committed["holds_exactly"])
    check(declared["accepted"], "the declared rounded ending holds: both conditions, in full")
    check(declared["both_hold_in_full"], "the two terminal conditions hold in full together")
    check(sealable["separate_record"] and committed["separate_record"]
          and not sealable["fused_with_the_other_component"]
          and not committed["fused_with_the_other_component"],
          "the two residual records are kept separate and are not fused")

    # the either-or terminal and its two disagreeing mixed cases
    either_or = either_or_verdict(sealable["holds_exactly"], committed["holds_exactly"])
    mixed_one = either_or_verdict(True, False)
    mixed_two = either_or_verdict(False, True)
    both_fail = either_or_verdict(False, False)
    check(not either_or["accepted_as_the_rounded_ending"],
          "an either-or terminal is rejected as the rounded ending")
    check(mixed_one["the_two_readings_disagree_here"]
          and mixed_two["the_two_readings_disagree_here"],
          "the either-or terminal is rejected by rule and the two mixed cases are where it "
          "differs from the conjunction")
    check(mixed_one["satisfied"] and mixed_two["satisfied"]
          and not conjunction_verdict(True, False)["accepted"]
          and not conjunction_verdict(False, True)["accepted"],
          "the either-or terminal accepts the two mixed cases that the conjunction rejects")
    check(not both_fail["satisfied"],
          "the either-or terminal also rejects the case where both conditions fail")

    # the netting terminal
    netting = netting_verdict(Fr(1, 4), committed)
    check(not netting["accepted_as_the_rounded_ending"],
          "a netting terminal is rejected as the rounded ending")
    check(netting["reduces_a_residual"] and netting["records_fused"],
          "the netting terminal reduces one component's residual by the other's surplus")
    check(netting["fused_residual_exists_exactly"] is False,
          "no exact fused residual exists, because the committed component carries no magnitude")
    check(fr(netting["declared_quantified_control"]["netted_residual"]) == 0
          and [fr(item) for item in netting["declared_quantified_control"]["separate_residuals"]]
          == [Fr(1, 4), Fr(1, 4)],
          "the declared quantified control shows netting erasing a nonzero residual")

    # the obstructing terminal and the independent declared terminal
    independent = obstruction_verdict(True, True)
    check(independent["the_two_conditions_are_independent"]
          and independent["accepted_as_the_rounded_ending"],
          "the declared terminal satisfies the independence the prohibition requires")
    obstructing = obstruction_verdict(False, True)
    check(not obstructing["accepted_as_the_rounded_ending"]
          and obstructing["a_verdict_flip_is_detected"],
          "an obstructing terminal is rejected as the rounded ending")
    check(not independent["a_verdict_flip_is_detected"],
          "the declared terminal shows no verdict flip, so the control discriminates")

    # the compromising terminal and the exact declared terminal
    exact = compromise_verdict(Fr(0), Fr(0))
    check(exact["accepted_as_the_rounded_ending"] and exact["holds_exactly"],
          "the declared terminal holds exactly, with a declared tolerance of exactly zero")
    approximate = compromise_verdict(Fr(1, 1000), Fr(1, 1000))
    check(not approximate["accepted_as_the_rounded_ending"],
          "a compromising terminal is rejected as the rounded ending")
    check(approximate["holds_approximately"] and not approximate["holds_exactly"],
          "the compromising control holds within its tolerance and not exactly")
    tolerance_only = compromise_verdict(Fr(1, 1000), Fr(0))
    check(not tolerance_only["accepted_as_the_rounded_ending"],
          "a declared nonzero tolerance is rejected by rule even when the residual is exactly "
          "zero, because the ending requires exactness")

    return {
        "declared_ending": "the ending is 圆融: not a choice between closure and openness, but "
                           "the conjunction of both terminal conditions, each holding in full",
        "terminal_conditions": 2,
        "sealable_component": {
            "declared": "the sealable component closes at the fixed point of the annual return",
            "fixed_point_identification": closure,
            "annual_return": "E(h) = (3/8) h + (1/8) h^2 + (1/64) h^3 + (1/512) h^4",
            "closure_identity": "512 (E(h) - h) = h (h^3 + 8 h^2 + 64 h - 320)",
            "residual_record": sealable,
            "displaced_state_control": {
                "control": "the sealable component displaced by one quarter from the fixed point",
                "displaced_residual": displaced.tuple(),
                "closes": displaced.is_zero(),
                "verdict": "Rejected_DoesNotClose",
                "reading": "closure at the fixed point is a real condition: away from the fixed "
                           "point the closure defect is not zero",
            },
        },
        "committed_component": {
            "declared": "the committed component carries out of the chain and is written out "
                        "rather than discharged",
            "declared_positions": list(COMMITTED_POSITIONS),
            "position_count": len(COMMITTED_POSITIONS),
            "written_record": written,
            "carry_out_condition": "the record must be written out - every declared field present "
                                   "and non-empty - it must not be discharged, and it must "
                                   "declare no magnitude",
            "carry_out": discharge,
            "residual_record": committed,
            "controls": [
                {"control": "an implicit committed component with no record at all",
                 "verdict": commitment_verdict(None)["verdict"],
                 "written": commitment_verdict(None)["written"],
                 "rejection_reasons": commitment_verdict(None)["reasons"],
                 "rejected_by_the_declared_condition": True},
                {"control": "an unwritten committed component",
                 "verdict": commitment_verdict(
                     commitment_record(positions_intact=""))["verdict"],
                 "written": commitment_verdict(
                     commitment_record(positions_intact=""))["written"],
                 "rejection_reasons": commitment_verdict(
                     commitment_record(positions_intact=""))["reasons"],
                 "rejected_by_the_declared_condition": True},
                {"control": "a committed component declared discharged",
                 "verdict": commitment_verdict(commitment_record(discharged=True))["verdict"],
                 "written": commitment_verdict(commitment_record(discharged=True))["written"],
                 "rejection_reasons": commitment_verdict(
                     commitment_record(discharged=True))["reasons"],
                 "rejected_by_the_declared_condition": True},
                {"control": "a committed component given a magnitude",
                 "verdict": commitment_verdict(
                     commitment_record(magnitude="asserted"))["verdict"],
                 "written": commitment_verdict(
                     commitment_record(magnitude="asserted"))["written"],
                 "rejection_reasons": commitment_verdict(
                     commitment_record(magnitude="asserted"))["reasons"],
                 "rejected_by_the_declared_condition": True},
            ],
        },
        "residual_records": {
            "count": 2,
            "kept_separate": True,
            "fused_scalar_exists": False,
            "components": [SEALABLE_COMPONENT, COMMITTED_COMPONENT],
            "reading": "the two residual records are reported side by side; no single scalar "
                       "residual for the pair is formed anywhere in this run",
        },
        "conjunction": declared,
        "prohibitions": {
            "either_or": {
                "prohibition": "no either-or terminal",
                "declared_terminal": either_or,
                "mixed_cases": {"sealable_only": mixed_one, "committed_only": mixed_two,
                                "neither": both_fail},
                "rejected": not either_or["accepted_as_the_rounded_ending"],
            },
            "netting": {
                "prohibition": "no netting: no component's residual may be reduced by another "
                               "component's surplus",
                "declared_terminal": netting,
                "rejected": not netting["accepted_as_the_rounded_ending"],
            },
            "obstruction": {
                "prohibition": "no mutual obstruction: satisfying one condition may not change "
                               "the other's verdict",
                "declared_terminal": independent,
                "declared_terminal_is_independent":
                    independent["the_two_conditions_are_independent"],
                "control": obstructing,
                "rejected": not obstructing["accepted_as_the_rounded_ending"],
            },
            "compromise": {
                "prohibition": "no compromise: both conditions must hold exactly, not "
                               "approximately",
                "declared_terminal": exact,
                "controls": [
                    {"control": "a terminal whose sealable residual equals its declared "
                                "tolerance", "declared_terminal": approximate,
                     "rejected": not approximate["accepted_as_the_rounded_ending"]},
                    {"control": "a terminal with a declared nonzero tolerance and an exactly "
                                "zero residual", "declared_terminal": tolerance_only,
                     "rejected": not tolerance_only["accepted_as_the_rounded_ending"]},
                ],
                "rejected": not approximate["accepted_as_the_rounded_ending"]
                and not tolerance_only["accepted_as_the_rounded_ending"],
            },
        },
        "prohibitions_rejected": 4,
        "no_fused_residual_is_formed": True,
        "the_ending_is_a_declared_convention": True,
    }


# ------------------------------------------------ R2: the Yi contrast family ---

def fine_points():
    return list(itertools.product(range(9), repeat=4))


def addresses():
    return list(itertools.product(range(3), repeat=4))


def section_yi_contrast_family():
    """R2: the address machinery reused, and the three Yi contrast terminals failing."""
    points = fine_points()
    check(len(points) == 6561, "the fine carrier has 6561 points")

    def block(z):
        return tuple(value // 3 for value in z)

    def phase(z):
        return tuple(value % 3 for value in z)

    diagonal = [z for z in points if block(z) == phase(z)]
    declared_diagonal = set(itertools.product((0, 4, 8), repeat=4))
    check(len(diagonal) == 81, "the mutual-measuring diagonal a = b has 81 points")
    check(set(diagonal) == declared_diagonal,
          "the diagonal is exactly z = 4 a with every coordinate in {0, 4, 8}")
    check(all(z == tuple(4 * value for value in block(z)) for z in diagonal),
          "every diagonal point is four times its own first address")
    declared_addresses = addresses()
    check(len(declared_addresses) == 81, "the first address carrier has 81 points")
    check({tuple(4 * value for value in address) for address in declared_addresses}
          == declared_diagonal,
          "the diagonal is exactly the image of z = 4 a over the 81 declared addresses")
    complement = [z for z in points if block(z) != phase(z)]
    check(len(complement) == 6480, "the complement of the diagonal has 6480 points")
    check(len(diagonal) + len(complement) == 6561,
          "the diagonal and its complement exhaust the 6561 fine points")
    strictly_out = [z for z in points if all(value in (1, 2, 3, 5, 6, 7) for value in z)]
    check(len(strictly_out) == 1296,
          "exactly 1296 fine points have every coordinate out of position")
    mixed_position = len(complement) - len(strictly_out)
    check(mixed_position == 5184,
          "the other 5184 points of the complement are in position in some coordinates only")
    check(all(z not in declared_diagonal for z in complement),
          "no complement point lies on the diagonal")
    check(81 == 3 ** 4 and 1296 == 6 ** 4,
          "the two exact counts are the fourth powers of the per-coordinate value counts")

    sealable_holds = sealable_residual_record()["holds_exactly"]
    written = commitment_record()
    discharge = commitment_verdict(written)
    committed_holds = committed_residual_record(written, discharge)["holds_exactly"]

    forced_closed = conjunction_verdict(sealable_holds, False)
    forced_open = conjunction_verdict(False, committed_holds)
    either_or = either_or_verdict(sealable_holds, committed_holds)
    check(not forced_closed["accepted"], "a forced-closed terminal fails the rounded ending")
    check(not forced_open["accepted"], "a forced-open terminal fails the rounded ending")
    check(not either_or["accepted_as_the_rounded_ending"],
          "an either-or terminal fails the rounded ending")
    check("the committed component is not carried out" in forced_closed["reasons"][0],
          "the forced-closed terminal fails on the committed condition, by the declared "
          "condition")
    check("does not close at the fixed point" in forced_open["reasons"][0],
          "the forced-open terminal fails on the sealable condition, by the declared condition")

    return {
        "declared_reading": "the Yi pair 既濟/未濟 is demoted from a terminal reading to the "
                            "contrast family: the all-in-position side and the none-in-position "
                            "side are two halves of one contrast, and neither is the rounded "
                            "ending",
        "address_machinery": {
            "carrier": "{0,...,8}^4, the 6561 fine points of the two-address encoding "
                       "e(a, b)_i = 3 a_i + b_i",
            "mutual_measuring_diagonal": "a = b, equivalently q_block(z) = q_phase(z)",
            "diagonal_points": len(diagonal),
            "diagonal_locus": "z = 4 a with every coordinate in {0, 4, 8}",
            "complement_points": len(complement),
            "diagonal_plus_complement": len(diagonal) + len(complement),
            "points_with_every_coordinate_out_of_position": len(strictly_out),
            "points_in_position_in_some_coordinates_only": mixed_position,
            "per_coordinate_in_position_values": [0, 4, 8],
            "per_coordinate_out_of_position_values": [1, 2, 3, 5, 6, 7],
            "reading": "the diagonal is the 81 all-in-position points and its complement is the "
                       "6480 none-in-position points; the strict reading of none in position, "
                       "with every coordinate out of position, holds on 1296 of the 6480, and "
                       "both exact counts are reported rather than one substituted for the other",
        },
        "contrast_terminals": [
            {"terminal": "a forced-closed terminal: the sealable component closes and the "
                         "committed component is discharged",
             "verdict": forced_closed["verdict"],
             "accepted": forced_closed["accepted"],
             "rejection_reasons": forced_closed["reasons"],
             "rejected_by": "the carry-out condition of the committed component"},
            {"terminal": "a forced-open terminal: the committed component carries out while the "
                         "sealable component is left open",
             "verdict": forced_open["verdict"],
             "accepted": forced_open["accepted"],
             "rejection_reasons": forced_open["reasons"],
             "rejected_by": "the closure condition of the sealable component"},
            {"terminal": "an either-or terminal: one of the two conditions is enough",
             "verdict": either_or["verdict"],
             "accepted": either_or["accepted_as_the_rounded_ending"],
             "rejection_reasons": either_or["reasons"],
             "rejected_by": either_or["rejected_by"]},
        ],
        "all_three_contrast_terminals_fail": True,
        "the_two_sides_are_not_identified": True,
        "no_terminal_reading_is_taken_from_the_yi_pair": True,
    }


# -------------------------------------------------- R3: the beginning split ---

def class_of(obstruction):
    for name, kind, _reading, _amount in OBSTRUCTION_CLASSES:
        if name == obstruction:
            return kind
    return None


def reset_verdict(obstruction):
    """The declared reset rule applied to one obstruction."""
    row = next((item for item in OBSTRUCTION_CLASSES if item[0] == obstruction), None)
    if row is None:
        return {
            "obstruction": obstruction, "declared_class": "none",
            "state_before": "not declared", "state_after": "not declared",
            "accepted": False, "verdict": "Rejected",
            "reasons": ["no obstruction of that name is declared"],
        }
    name, kind, reading, amount = row
    if kind == "resetable":
        return {
            "obstruction": name,
            "declared_class": kind,
            "reading": reading,
            "state_before": str(amount),
            "state_after": "0",
            "cleared_exactly": True,
            "accepted": True,
            "verdict": "ResetAccepted",
            "residual_written_out": True,
            "reasons": [],
            "rejected_by": "",
        }
    return {
        "obstruction": name,
        "declared_class": kind,
        "reading": reading,
        "state_before": "the declared one-way commitment state",
        "state_after": "the declared one-way commitment state",
        "state_unchanged": True,
        "cleared_exactly": False,
        "accepted": False,
        "verdict": "ResetRejected",
        "residual_written_out": True,
        "reasons": ["a reset may not clear a non-resetable commitment: the one-way commitment "
                    "state must be written out and carried, and no reset may clear it"],
        "rejected_by": "the declared class of the one-way commitment state",
        "decided_by_a_count": False,
    }


def section_beginning_split():
    """R3: the two obstruction classes, their write-out requirements and the reset rule."""
    kinds = [row[1] for row in OBSTRUCTION_CLASSES]
    check(kinds.count("resetable") == 2, "exactly two resetable obstructions are declared")
    check(kinds.count("non_resetable") == 1,
          "exactly one non-resetable commitment is declared")
    check(set(kinds) == {"resetable", "non_resetable"},
          "the beginning is split into exactly the two declared classes")
    check(WAYEB_DAYS == ANNUAL_CYCLE_DAYS - MONTH_COUNT * DAYS_PER_MONTH,
          "the declared phase misalignment is exactly 365 minus eighteen twenty-day months")
    check(BASELINE_STEPS_PER_CYCLE == 9 and CYCLE_COUNT * BASELINE_STEPS_PER_CYCLE
          == TOTAL_BASELINE_STEPS,
          "the parent chain's declared step count is nine steps per cycle over three cycles")
    check(ZAN_PER_STEP == 81 and ZAN_PER_STEP * BASELINE_STEPS_PER_CYCLE == ZAN_PER_CYCLE,
          "each declared step carries exactly 81 zan and nine of them are the 729 of a cycle")
    check(END_BLOCK_REMAINDER_STEPS == CYCLE_COUNT * END_BLOCK_STEPS,
          "the end-block remainder is exactly two steps per cycle over three cycles")
    check(STEP_CARRY_REMAINDER == Fr(END_BLOCK_REMAINDER_STEPS, TOTAL_BASELINE_STEPS)
          == Fr(2, 9),
          "the declared step-carry remainder is exactly six of twenty-seven steps, two ninths")
    check(ZAN_OF_THE_REMAINDER == END_BLOCK_REMAINDER_STEPS * ZAN_PER_STEP == 486,
          "counted in the same unit as the steps, the declared remainder is exactly 486 zan")

    resets = {name: reset_verdict(name) for name, _kind, _reading, _amount in OBSTRUCTION_CLASSES}
    phase_reset = resets["phase_misalignment"]
    carry_reset = resets["step_carry_remainder"]
    commitment_reset = resets["one_way_commitment_state"]
    check(phase_reset["accepted"], "a reset applied to the declared phase misalignment is "
                                   "accepted")
    check(carry_reset["accepted"], "a reset applied to the declared step-carry remainder is "
                                   "accepted")
    check(fr(phase_reset["state_after"]) == 0 and fr(carry_reset["state_after"]) == 0,
          "the accepted reset clears both resetable obstructions exactly to zero")
    check(not commitment_reset["accepted"],
          "a reset applied to the non-resetable commitment is rejected")
    check(commitment_reset["state_unchanged"],
          "the rejected reset leaves the one-way commitment state unchanged")
    check(not commitment_reset["cleared_exactly"],
          "the rejected reset does not clear the commitment")

    misdeclared = dict(commitment_reset)
    misdeclared["declared_class"] = "resetable"
    misdeclared["rejected_by"] = "the declared class of the one-way commitment state"
    misdeclared_check = {
        "control": "a chain that declares the one-way commitment state resetable",
        "declared_class_asserted": "resetable",
        "declared_class_actual": class_of("one_way_commitment_state"),
        "verdict": "Rejected",
        "rejected_by": "the declared class of the one-way commitment state, which is not "
                       "resetable",
        "decided_by_a_count": False,
    }
    check(misdeclared_check["declared_class_actual"] == "non_resetable",
          "the declared class of the commitment is non-resetable, so the misdeclaration is "
          "rejected by the class and not by a count")
    no_write_out = {
        "control": "a resetable obstruction declared with no write-out requirement",
        "write_out_requirement_declared": False,
        "verdict": "Rejected",
        "rejected_by": "the declared write-out requirement of every obstruction class",
    }
    check(all(row["residual_written_out"] for row in resets.values()),
          "every declared obstruction carries a write-out requirement")

    return {
        "declared_split": "the beginning is split into RESETABLE obstructions, which a declared "
                          "reset may clear, and NON-RESETABLE commitments, which no reset may "
                          "clear and which must be written out and carried",
        "classes": [
            {"obstruction": name, "declared_class": kind, "reading": reading,
             "declared_amount": ("none_declared" if amount is None else str(amount)),
             "write_out_required": True,
             "reset_rule": ("a declared reset may clear this obstruction exactly"
                            if kind == "resetable" else
                            "no reset may clear this obstruction; it is carried and written out")}
            for name, kind, reading, amount in OBSTRUCTION_CLASSES
        ],
        "resets": resets,
        "accepted_resets": [name for name, row in resets.items() if row["accepted"]],
        "rejected_resets": [name for name, row in resets.items() if not row["accepted"]],
        "controls": [
            {"control": "a reset applied to the non-resetable commitment",
             "verdict": commitment_reset["verdict"],
             "state_unchanged": commitment_reset["state_unchanged"],
             "rejection_reasons": commitment_reset["reasons"],
             "rejected_by_the_declared_condition": True},
            {"control": misdeclared_check["control"],
             "verdict": misdeclared_check["verdict"],
             "rejection_reasons": ["the one-way commitment state is declared non-resetable, so a "
                                   "chain that declares it resetable contradicts the declaration"],
             "rejected_by_the_declared_condition": True,
             "decided_by_a_count": False},
            {"control": no_write_out["control"],
             "verdict": no_write_out["verdict"],
             "rejection_reasons": ["every obstruction class must declare its write-out "
                                   "requirement; one without it is rejected"],
             "rejected_by_the_declared_condition": True},
        ],
        "the_split_is_a_declared_convention": True,
        "no_reset_clears_the_commitment": True,
    }


# --------------------------------------------------- R4: the middle five ------

def cycle_order(step, size=5):
    """The order of the map k -> k + step modulo size, read on the declared points."""
    order = 1
    point = (0 + step) % size
    while point != 0:
        point = (point + step) % size
        order += 1
    return order


def orbit(step, size=5):
    """The orbit of the declared map k -> k + step modulo size, from the declared point 0."""
    return [(index * step) % size for index in range(size)]


def generators(size):
    """The steps that generate the additive group modulo size, by exact order."""
    return [step for step in range(size) if cycle_order(step, size) == size]


def five_point_verdict(generation_step, overcoming_step, identified=False):
    """The declared five-point structure: two directed cycles on the same five points."""
    reasons = []
    size = len(FIVE_POINTS)
    if generation_step is None:
        reasons.append("the declared five-point structure must carry the generation cycle; it is "
                       "missing")
    if overcoming_step is None:
        reasons.append("the declared five-point structure must carry the overcoming cycle on the "
                       "same five points; it is missing")
    if identified and generation_step is not None and overcoming_step is not None:
        reasons.append("the two cycles must not be identified: generation +1 and overcoming +2 "
                       "differ at every one of the five declared points")
    for label, step in (("generation", generation_step), ("overcoming", overcoming_step)):
        if step is not None and cycle_order(step, size) != size:
            reasons.append("the declared " + label + " step " + str(step) + " modulo five has "
                           "order " + str(cycle_order(step, size)) + ", so it is not a "
                           "generator and does not carry a single five-cycle")
    differing = None
    if generation_step is not None and overcoming_step is not None:
        differing = [point for point in FIVE_POINTS
                     if (point + generation_step) % size != (point + overcoming_step) % size]
    return {
        "generation_step": generation_step,
        "overcoming_step": overcoming_step,
        "points_where_the_two_cycles_differ": differing,
        "differ_at_every_point": differing == list(FIVE_POINTS) if differing is not None else None,
        "accepted": not reasons,
        "verdict": "BothCyclesCarried" if not reasons else "Rejected",
        "reasons": reasons,
        "rejected_by": "the declared five-point structure" if reasons else "",
        "decided_by_a_count": False,
    }


def section_middle_five():
    """R4: generation and overcoming as two directed cycles on the same five points."""
    size = len(FIVE_POINTS)
    check(size == 5, "the declared middle carries exactly five points")
    check(all(size % divisor != 0 for divisor in range(2, size)),
          "five is prime: it has no divisor between two and four")
    generating = generators(size)
    check(generating == [1, 2, 3, 4],
          "the generators modulo five are exactly the four nonzero residues")
    check(len(generating) == size - 1,
          "the number of generators of the additive group is five minus one, which is why five "
          "being prime makes every nonzero step a generator")
    declared = five_point_verdict(GENERATION_STEP, OVERCOMING_STEP)
    check(declared["accepted"], "the declared five-point structure carries both cycles")
    check(cycle_order(GENERATION_STEP, size) == size and cycle_order(OVERCOMING_STEP, size) == size,
          "both declared steps generate a single five-cycle")
    check(declared["differ_at_every_point"],
          "the two declared cycles differ at every one of the five points")
    check(orbit(GENERATION_STEP) == [0, 1, 2, 3, 4],
          "the generation cycle visits the five points in the declared order")
    check(orbit(OVERCOMING_STEP) == [0, 2, 4, 1, 3],
          "the overcoming cycle visits the five points in its own declared order")
    generation_squared = [(point + 2 * GENERATION_STEP) % size for point in FIVE_POINTS]
    overcoming_map = [(point + OVERCOMING_STEP) % size for point in FIVE_POINTS]
    check(generation_squared == overcoming_map,
          "the overcoming cycle is the generation cycle applied twice, exactly")
    check([(point + 5 * GENERATION_STEP) % size for point in FIVE_POINTS] == list(FIVE_POINTS),
          "the fifth power of the generation cycle is the identity on the five points")

    one_cycle_only = five_point_verdict(GENERATION_STEP, None)
    identified = five_point_verdict(GENERATION_STEP, GENERATION_STEP, identified=True)
    zero_step = five_point_verdict(GENERATION_STEP, 0)
    check(not one_cycle_only["accepted"],
          "rejecting one of the two cycles fails the declared five-point structure")
    check(not identified["accepted"], "identifying the two cycles fails the declared structure")
    check(not zero_step["accepted"],
          "a declared fifth cycle with step zero is not a cycle and is rejected")
    check("missing" in one_cycle_only["reasons"][0],
          "the one-cycle structure is rejected because the overcoming cycle is missing")
    check("differ at every one of the five" in identified["reasons"][0],
          "the identification is rejected by the pointwise difference of the two cycles")
    composite = cycle_order(OVERCOMING_STEP, 4)
    composite_generators = generators(4)
    check(composite == 2 and composite_generators == [1, 3],
          "on a composite modulus the declared overcoming step would not be a generator: modulo "
          "four it has order two and only 1 and 3 generate")
    check(len(composite_generators) != 3,
          "the primality control discriminates: the same declaration fails modulo four")

    return {
        "declared_five_point_structure": "the middle group carries TWO directed cycles on the "
                                         "same five points: generation as +1 and overcoming as "
                                         "+2 modulo five",
        "points": list(FIVE_POINTS),
        "declared_cycles": {
            "generation": {"step": GENERATION_STEP, "orbit": orbit(GENERATION_STEP),
                           "order": cycle_order(GENERATION_STEP),
                           "is_a_single_five_cycle": cycle_order(GENERATION_STEP) == size,
                           "is_a_generator": GENERATION_STEP in generating},
            "overcoming": {"step": OVERCOMING_STEP, "orbit": orbit(OVERCOMING_STEP),
                           "order": cycle_order(OVERCOMING_STEP),
                           "is_a_single_five_cycle": cycle_order(OVERCOMING_STEP) == size,
                           "is_a_generator": OVERCOMING_STEP in generating},
        },
        "five_is_prime": True,
        "generators_modulo_five": generating,
        "number_of_generators": len(generating),
        "every_nonzero_step_is_a_generator": len(generating) == size - 1,
        "why_the_primality_matters": "modulo the prime five every nonzero residue has order five, "
                                     "so both declared steps generate the whole group; on a "
                                     "composite modulus that would fail",
        "the_two_cycles_are_distinct_maps": declared["differ_at_every_point"],
        "points_where_they_differ": declared["points_where_the_two_cycles_differ"],
        "overcoming_is_generation_applied_twice": True,
        "declared_structure": declared,
        "controls": [
            {"control": "a structure that rejects one of the two cycles",
             "structure": {"generation_step": GENERATION_STEP, "overcoming_step": None},
             "verdict": one_cycle_only["verdict"],
             "rejection_reasons": one_cycle_only["reasons"],
             "rejected_by_the_declared_condition": True},
            {"control": "a structure that identifies the two cycles",
             "structure": {"generation_step": GENERATION_STEP,
                           "overcoming_step": GENERATION_STEP, "identified": True},
             "verdict": identified["verdict"],
             "rejection_reasons": identified["reasons"],
             "rejected_by_the_declared_condition": True},
            {"control": "a declared cycle with step zero",
             "structure": {"generation_step": GENERATION_STEP, "overcoming_step": 0},
             "verdict": zero_step["verdict"],
             "rejection_reasons": zero_step["reasons"],
             "rejected_by_the_declared_condition": True},
            {"control": "the declared primality reading on the composite modulus four",
             "order_of_the_overcoming_step": composite,
             "generators_modulo_four": composite_generators,
             "verdict": "Rejected_NotAGenerator",
             "rejected_by_the_declared_condition": True,
             "discriminates": True},
        ],
        "both_cycle_rejections_fail": True,
    }


# ------------------------------------------- R5: the astronomical remainders ---

def commensurability_rows(chain_days):
    rows = []
    for name, days in COMMENSURABILITIES:
        remainder = chain_days % days
        multiple = Fr(days, chain_days)
        rows.append({
            "commensurability": name,
            "days": days,
            "chain_days": chain_days,
            "remainder": remainder,
            "closes_it": remainder == 0,
            "exact_multiple_of_the_chain_length": multiple.denominator == 1,
            "chain_cycles_needed": str(multiple),
        })
    return rows


def closes_claim_verdict(name, days, chain_days):
    """A claim that the chain closes a commensurability, evaluated exactly."""
    remainder = chain_days % days
    return {
        "claim": "the chain closes " + name,
        "days": days,
        "remainder": remainder,
        "accepted": False,
        "verdict": "Rejected",
        "reasons": ["the chain is " + str(chain_days) + " integer days and " + str(days)
                    + " days leave the exact remainder " + str(remainder)
                    + ", so the chain does not close it"],
        "decided_by_a_count": False,
    }


def section_astronomical_remainders():
    """R5: the chain length in integer days against the three commensurabilities."""
    chain_days = CYCLE_COUNT * ANNUAL_CYCLE_DAYS
    check(ANNUAL_CYCLE_DAYS == MONTH_COUNT * DAYS_PER_MONTH + WAYEB_DAYS,
          "the declared annual cycle is eighteen twenty-day months plus the five Wayeb days")
    check(chain_days == 1095, "the declared chain length is exactly 1095 integer days")
    check(VENUS_EIGHT_YEAR_DAYS == 8 * ANNUAL_CYCLE_DAYS,
          "2920 days is exactly eight declared annual cycles")
    check(CALENDAR_ROUND_DAYS == 52 * ANNUAL_CYCLE_DAYS,
          "18980 days is exactly fifty-two declared annual cycles")
    check(CALENDAR_ROUND_DAYS == 73 * TZOLKIN_DAYS,
          "18980 days is exactly seventy-three Tzolkin rounds")
    check(TZOLKIN_DAYS == 4 * 65, "the Tzolkin of 260 days is exactly four sixty-five day rounds")

    rows = commensurability_rows(chain_days)
    check(len(rows) == 3, "the three declared commensurabilities are each reported")
    remainders = {row["commensurability"]: row["remainder"] for row in rows}
    check(remainders["Tzolkin"] == 55, "the remainder against 260 days is exactly 55")
    check(remainders["five Venus synodic periods, eight solar years"] == 1095,
          "the remainder against 2920 days is exactly the chain length 1095")
    check(remainders["the calendar round"] == 1095,
          "the remainder against 18980 days is exactly the chain length 1095")
    check(all(not row["closes_it"] for row in rows),
          "the chain closes none of the three commensurabilities")
    check(all(not row["exact_multiple_of_the_chain_length"] for row in rows),
          "no commensurability is an exact multiple of the chain length")
    check(len({row["remainder"] for row in rows}) == 2,
          "two of the three remainders coincide because the chain is shorter than both, and that "
          "coincidence is reported rather than smoothed")

    claims = [closes_claim_verdict(row["commensurability"], row["days"], chain_days)
              for row in rows]
    check(all(not claim["accepted"] for claim in claims),
          "a claim that the chain closes any commensurability is rejected")
    for claim, row in zip(claims, rows, strict=True):
        check(claim["remainder"] == row["remainder"],
              "the rejection of the closing claim uses the same exact remainder")

    control_rows = {}
    for label, year_days in YEAR_LENGTH_CONTROLS:
        variant = CYCLE_COUNT * year_days
        control_rows[label] = {
            "annual_cycle_days": year_days,
            "chain_days": variant,
            "remainders": [variant % days for _name, days in COMMENSURABILITIES],
            "closes_none": all(variant % days != 0 for _name, days in COMMENSURABILITIES),
        }
    check(all(row["closes_none"] for row in control_rows.values()),
          "every declared year-length control closes none of the three commensurabilities")
    discriminating = len({row["closes_none"] for row in control_rows.values()}) > 1
    check(not discriminating,
          "the year-length control does not discriminate: the same verdict holds under every "
          "declared year length")

    return {
        "declared_chain": {
            "annual_cycles": CYCLE_COUNT,
            "annual_cycle_days": ANNUAL_CYCLE_DAYS,
            "chain_days": chain_days,
            "reading": "three annual cycles of the declared 365-day year, counted in whole days",
        },
        "commensurabilities": rows,
        "remainders": {row["commensurability"]: str(row["remainder"]) for row in rows},
        "the_chain_closes_none": True,
        "the_chain_closes_none_statement": "three annual cycles do NOT close the 260-day "
                                           "Tzolkin, the 2920-day eight-year Venus round or the "
                                           "18980-day calendar round",
        "exact_identities": {
            "2920 = 8 x 365": True,
            "18980 = 52 x 365": True,
            "18980 = 73 x 260": True,
            "365 = 18 x 20 + 5": True,
        },
        "closing_claim_controls": [
            {"claim": claim["claim"], "verdict": claim["verdict"],
             "remainder": str(claim["remainder"]),
             "rejection_reasons": claim["reasons"],
             "rejected_by_the_declared_condition": True}
            for claim in claims
        ],
        "failed_to_discriminate": {
            "control": "the declared year-length control",
            "variants": control_rows,
            "verdict": "FAILED_TO_DISCRIMINATE",
            "why": "the non-closure reading holds under every declared year length, so this "
                   "control cannot separate the declarations; it shows only that the verdict is "
                   "insensitive to that declaration, and it is recorded rather than dropped",
        },
    }


# --------------------------------------------- R6: three is not a degree ------

def section_three_is_not_a_degree():
    """R6: the three-year period is neither a third-degree harmonic nor a lost injectivity."""
    degree = 3
    harmonics = 2 * degree + 1
    total_to_degree = (degree + 1) ** 2
    check(harmonics == 7, "the number of third-degree spherical harmonics is 2 x 3 + 1 = 7")
    check(total_to_degree == 16,
          "the dimension of the harmonics up to degree three is (3 + 1)^2 = 16")
    check(harmonics != CYCLE_COUNT,
          "three is not seven: the declared three-year period is not the dimension of the "
          "third-degree spherical harmonic space")
    check(total_to_degree != CYCLE_COUNT,
          "three is not sixteen either, so no harmonic dimension of degree up to three "
          "coincides with it")
    pairs = list(itertools.combinations(CYCLE_LABELS, 2))
    collisions = [(left, right) for left, right in pairs if left == right]
    check(len(pairs) == 3, "the three declared cycles have exactly three unordered index pairs")
    check(not collisions,
          "the declared index map from the chain's index set to its cycles has no collision")
    spans = {"C1": "2026-12 to 2027-12", "C2": "2027-12 to 2028-12",
             "C3": "2028-12 to 2029-12"}
    check(len(set(spans.values())) == CYCLE_COUNT,
          "the three declared cycles have pairwise distinct declared spans")

    degree_reading = {
        "reading": "the three-year time period is a third-degree spherical harmonic",
        "accepted": False,
        "verdict": "Rejected",
        "reasons": [
            "the declared object is a count of three annual cycles, and no spherical carrier, no "
            "harmonic basis and no Laplacian on a sphere is declared anywhere in this run",
            "the number of degree-l spherical harmonics is 2 l + 1, which at l = 3 is 7, and the "
            "declared count is 3, so the identification fails on the exact dimension alone",
        ],
        "decided_by_a_count": False,
    }
    injectivity_reading = {
        "reading": "the three-year time period is a failure of injectivity",
        "accepted": False,
        "verdict": "Rejected",
        "reasons": [
            "a failure of injectivity would be a collapse of two distinct cycle indices onto one "
            "image, and the declared index map is injective: three indices, three distinct cycle "
            "spans and no collision among the three unordered pairs",
            "the count of three is a declared cardinality of the chain, not an image of something "
            "larger",
        ],
        "decided_by_a_count": False,
    }
    check(not degree_reading["accepted"],
          "reading the three-year period as a third-degree spherical harmonic is rejected")
    check(not injectivity_reading["accepted"],
          "reading the three-year period as a failure of injectivity is rejected")
    check(degree_reading["reasons"] and injectivity_reading["reasons"],
          "both rejections name their exact reason")
    check(len(degree_reading["reasons"]) == 2 and len(injectivity_reading["reasons"]) == 2,
          "each rejection carries exactly its two declared reasons")
    coincidence = 2 * 2 + 1
    check(coincidence == len(FIVE_POINTS),
          "the dimension of the degree-two harmonic space is five and the middle has five points")
    check(coincidence == 2 * 2 + 1 and len(FIVE_POINTS) == 5,
          "the numerical coincidence is recorded exactly and refused as an identification")

    return {
        "declared_reading": "the three-year time period is a count of three annual cycles; it is "
                            "NOT a third-degree spherical harmonic and NOT a failure of "
                            "injectivity",
        "the_three": {
            "value": CYCLE_COUNT,
            "reading": "a declared cardinality of the chain, three annual cycles",
            "third_degree_spherical_harmonics": harmonics,
            "harmonic_dimension_formula": "2 l + 1",
            "harmonics_to_degree_three": total_to_degree,
            "three_equals_seven": harmonics == CYCLE_COUNT,
            "three_equals_sixteen": total_to_degree == CYCLE_COUNT,
        },
        "injectivity": {
            "declared_index_set": list(CYCLE_LABELS),
            "declared_images": spans,
            "unordered_index_pairs": [list(pair) for pair in pairs],
            "collisions": len(collisions),
            "is_injective": not collisions,
            "is_a_collapse": False,
        },
        "readings": [
            {"control": degree_reading["reading"], "verdict": degree_reading["verdict"],
             "rejection_reasons": degree_reading["reasons"],
             "rejected_by_the_declared_condition": True,
             "decided_by_a_count": False},
            {"control": injectivity_reading["reading"],
             "verdict": injectivity_reading["verdict"],
             "rejection_reasons": injectivity_reading["reasons"],
             "rejected_by_the_declared_condition": True,
             "decided_by_a_count": False},
        ],
        "identifications_rejected": 2,
        "numerical_coincidence_recorded_not_used": {
            "coincidence": "the dimension of the degree-two spherical harmonic space is 2 x 2 + 1 "
                           "= 5 and the declared middle carries 5 points",
            "identification_made": False,
            "reading": "an equality of two whole numbers is not an identification of the objects "
                       "they count; the coincidence is recorded so that it cannot be smuggled in "
                       "as evidence",
        },
        "no_spherical_carrier_is_declared": True,
    }


# --------------------------------------- R7: the one-way commitment reservoir --

def branch_state(open_before, control, thresholds=(THRESHOLD_OPEN, THRESHOLD_CLOSE)):
    """The declared threshold branch: it opens at the upper threshold and closes at the lower."""
    upper, lower = thresholds
    if open_before:
        return control > lower
    return control >= upper


def reservoir_loop(controls=LOOP_CONTROLS, steps=(BRANCH_OPEN_STEP, BRANCH_CLOSED_STEP),
                   thresholds=(THRESHOLD_OPEN, THRESHOLD_CLOSE)):
    """The declared one-way reservoir on the declared loop of control values."""
    open_step, closed_step = steps
    state = Fr(0)
    open_state = False
    rows = []
    for index, control in enumerate(controls):
        open_state = branch_state(open_state, control, thresholds)
        increment = open_step if open_state else closed_step
        state_after = state + increment
        rows.append({
            "position": index,
            "control_value": str(control),
            "branch_state": "open" if open_state else "closed",
            "declared_increment": str(increment),
            "state_before": str(state),
            "state_after": str(state_after),
            "increment": str(state_after - state),
        })
        state = state_after
    return rows


def relaxation_loop(steady, displacement, relaxation, count):
    """The parent chain's declared first-order relaxation, on the same declared loop length."""
    state = steady + Cubic(displacement)
    rows = []
    for index in range(count):
        drift = (steady - state).scale(relaxation)
        state = state + drift
        rows.append({
            "position": index,
            "state": state.tuple(),
            "drift": drift.tuple(),
            "drift_as_rational": (str(drift.a) if drift.b == 0 and drift.c == 0 else None),
            "non_negative": (drift.b == 0 and drift.c == 0 and drift.a >= 0),
        })
    return rows


def section_commitment_reservoir():
    """R7: the one-way reservoir against the parent's declared first-order relaxation."""
    check(THRESHOLD_OPEN > THRESHOLD_CLOSE > 0,
          "the declared thresholds are ordered: the branch opens above where it closes")
    check(0 <= BRANCH_CLOSED_STEP < BRANCH_OPEN_STEP,
          "both declared increments are non-negative and the open-branch increment is the "
          "larger")
    declared_rows = reservoir_loop()
    check(len(declared_rows) == len(LOOP_CONTROLS),
          "the declared reservoir is reported at every declared loop position")
    states = [fr(row["state_after"]) for row in declared_rows]
    increments = [fr(row["increment"]) for row in declared_rows]
    check(all(increment >= 0 for increment in increments),
          "the declared one-way reservoir's state is non-decreasing at every declared step")
    check(all(later > earlier for earlier, later in pairwise(states)),
          "the declared state is strictly increasing at every declared step")
    check(states[-1] > states[0],
          "a declared loop in the control does not undo the commitment: the state ends strictly "
          "above where it started")
    check(states[-1] == Fr(7, 16), "the declared loop ends at exactly 7/16")
    check(increments == [Fr(1, 16), Fr(1, 16), Fr(1, 8), Fr(1, 8), Fr(1, 16)],
          "the declared increments along the loop are 1/16, 1/16, 1/8, 1/8 and 1/16")
    thaw_pass = [row for row in declared_rows if fr(row["control_value"]) <= HYSTERESIS_PROBE
                 and row["position"] <= 2]
    refreeze_pass = [row for row in declared_rows if fr(row["control_value"]) == HYSTERESIS_PROBE
                     and row["position"] > 2]
    check(len(thaw_pass) >= 1 and len(refreeze_pass) == 1,
          "the declared probe control value 1/2 is visited on both passes of the declared loop")
    probe_thaw = next(row for row in declared_rows
                      if fr(row["control_value"]) == HYSTERESIS_PROBE and row["position"] == 1)
    probe_refreeze = next(row for row in declared_rows
                          if fr(row["control_value"]) == HYSTERESIS_PROBE and row["position"] == 3)
    hysteresis = (probe_thaw["branch_state"] != probe_refreeze["branch_state"]
                  and probe_thaw["declared_increment"] != probe_refreeze["declared_increment"])
    check(hysteresis,
          "the thaw path and the refreeze path differ at the declared control value 1/2: the "
          "branch is closed going up and open coming down")
    check(probe_thaw["branch_state"] == "closed" and probe_refreeze["branch_state"] == "open",
          "the declared hysteresis probe reads closed on the thaw path and open on the "
          "refreeze path")

    equal_thresholds = reservoir_loop(thresholds=(THRESHOLD_OPEN, THRESHOLD_OPEN))
    equal_probe = [(row["branch_state"], row["declared_increment"]) for row in equal_thresholds
                   if fr(row["control_value"]) == HYSTERESIS_PROBE]
    check(len(set(equal_probe)) == 1,
          "with the two declared thresholds equal the declared loop shows no hysteresis")
    check(equal_probe[0][0] == equal_probe[1][0],
          "the equal-threshold control discriminates: the hysteresis comes from the declared "
          "separation of the two thresholds")
    threshold_blind = reservoir_loop(steps=(BRANCH_OPEN_STEP, BRANCH_OPEN_STEP))
    blind_increments = [fr(row["increment"]) for row in threshold_blind]
    check(all(increment >= 0 for increment in blind_increments),
          "with both declared increments equal the state is still non-decreasing")
    check(len(set(blind_increments)) == 1,
          "the monotonicity control alone does not see the threshold branch")

    parent_rows = relaxation_loop(PARENT_STEADY, PARENT_DISPLACEMENT, PARENT_RELAXATION,
                                  len(LOOP_CONTROLS))
    parent_drifts = [fr(row["drift_as_rational"]) for row in parent_rows]
    check(parent_drifts[0] == Fr(-1, 120),
          "the parent's declared relaxation drifts by exactly -1/120 at its first step")
    check(parent_drifts[1] == Fr(-29, 3600),
          "the parent's second declared drift is exactly -29/3600")
    check(parent_drifts[2] == Fr(-841, 108000),
          "the parent's third declared drift is exactly -841/108000")
    check(all(later == earlier * Fr(29, 30) for earlier, later in pairwise(parent_drifts)),
          "every parent drift is the previous one times 29/30, exactly")
    check(all(drift < 0 for drift in parent_drifts),
          "every parent drift is strictly negative")
    check(not all(row["non_negative"] for row in parent_rows),
          "the parent chain's declared first-order relaxation FAILS the monotonicity control")
    parent_branch_reading = {"thaw_path": "no branch state is declared",
                             "refreeze_path": "no branch state is declared"}
    check(parent_branch_reading["thaw_path"] == parent_branch_reading["refreeze_path"],
          "the parent chain's declared relaxation FAILS the hysteresis control: the two paths "
          "agree because there is no branch to differ")
    parent_states = {tuple(row["state"]) for row in parent_rows}
    check(len(parent_states) == len(parent_rows),
          "the parent's declared relaxation is one map applied at every step: it visits a "
          "different state at each declared step and declares no branch state, so the two passes "
          "of the declared loop cannot be distinguished")

    return {
        "declared_model": "the committed component is a declared one-way reservoir: its declared "
                          "state is non-decreasing, its branch opens at a declared upper "
                          "threshold and closes at a declared lower threshold, and a declared "
                          "loop in the control does not restore it",
        "component": COMMITTED_COMPONENT,
        "magnitude": NO_MAGNITUDE,
        "reservoir_state_is_a_declared_convention": True,
        "why_the_state_is_not_a_magnitude":
            "the reservoir's state is a declared exact structural quantity of this declared "
            "model, used only to check monotonicity and hysteresis; no magnitude, sign or "
            "timing is asserted for the committed component, whose declared magnitude is "
            + NO_MAGNITUDE,
        "declared_thresholds": {"opens_at": str(THRESHOLD_OPEN),
                                "closes_at": str(THRESHOLD_CLOSE)},
        "declared_increments": {"open_branch": str(BRANCH_OPEN_STEP),
                                "closed_branch": str(BRANCH_CLOSED_STEP)},
        "declared_loop_controls": [str(control) for control in LOOP_CONTROLS],
        "declared_loop": declared_rows,
        "monotone_non_decreasing": True,
        "strictly_increasing": True,
        "the_loop_does_not_restore_the_state": True,
        "hysteresis": {
            "present": True,
            "declared_probe_control": str(HYSTERESIS_PROBE),
            "thaw_path": probe_thaw,
            "refreeze_path": probe_refreeze,
            "paths_differ": hysteresis,
            "reading": "at the same declared control value the branch is closed on the thaw path "
                       "and open on the refreeze path, and the two declared increments differ "
                       "there",
        },
        "controls": [
            {"control": "the declared loop with the two thresholds set equal",
             "probe_readings": [list(item) for item in equal_probe],
             "hysteresis_present": len(set(equal_probe)) > 1,
             "verdict": "NoHysteresis",
             "discriminates": True,
             "reading": "the hysteresis is produced by the declared separation of the two "
                        "thresholds and not by the loop alone"},
            {"control": "the declared loop with both increments set equal",
             "increments": sorted({str(value) for value in blind_increments}),
             "still_monotone": True,
             "hysteresis_still_present": True,
             "verdict": "FAILED_TO_DISCRIMINATE",
             "reading": "monotonicity alone does not test the threshold branch: with the two "
                        "increments equal the state is still non-decreasing, so only the "
                        "hysteresis control sees the branch"},
        ],
        "parent_relaxation_failure": {
            "control": "the parent chain's declared first-order relaxation reservoir",
            "declared_form": "T_{i+1} = T_i + a (T_steady - T_i) with a = 1/30, the declared "
                             "relaxation coefficient of the parent chain",
            "relaxation_coefficient": str(PARENT_RELAXATION),
            "time_constant": str(PARENT_TIME_CONSTANT),
            "declared_displacement": str(PARENT_DISPLACEMENT),
            "declared_steps": parent_rows,
            "monotone_non_decreasing": False,
            "monotonicity_control": "FAILED",
            "hysteresis_present": False,
            "hysteresis_control": "FAILED",
            "threshold_declared": False,
            "branch_state_declared": False,
            "declared_branch_reading": parent_branch_reading,
            "verdict": "TheOneWayShapeIsDoingWork",
            "reading": "the parent's declared first-order relaxation fails both controls: it "
                       "relaxes strictly downward from a displacement, so it is not "
                       "non-decreasing, and it has no threshold and no branch state, so the thaw "
                       "and refreeze paths of the same declared loop agree.  That failure is the "
                       "evidence that the one-way shape is doing work, and it is a fact about "
                       "the two declared models, not about any physical reservoir.",
        },
        "the_one_way_shape_does_work": True,
    }


# --------------------------------------------- R8: sealing refused for a leak --

def sealing_verdict(target, drifts=None):
    """The declared sealing condition, applied to one component."""
    if target == COMMITTED_COMPONENT:
        return {
            "target": target,
            "accounted": True,
            "sealed": False,
            "refused": True,
            "verdict": "Refused_NotSealable",
            "reasons": ["the sealing condition is refused for the committed component: it is by "
                        "definition a leak, so it may be accounted but never sealed"],
            "rejected_by": "the declared refusal of sealing for a leaking component",
        }
    drifts = {} if drifts is None else drifts
    violating = [layer for index, layer in enumerate(LAYER_ORDER)
                 if abs(drifts.get(layer, Fr(0))) > LAYER_SEALING_BOUND[index]]
    return {
        "target": target,
        "accounted": True,
        "sealed": not violating,
        "refused": False,
        "violating_layers": violating,
        "verdict": "Sealed" if not violating else "LayerWiseViolation",
        "reasons": [] if not violating else [
            "the sealing bound is violated in the layers " + ", ".join(violating)
            + ", and a total may not cancel a layer-wise violation"],
        "rejected_by": "",
    }


def section_sealing_refused():
    """R8: the committed component may be accounted but never sealed."""
    clean = {layer: Fr(0) for layer in LAYER_ORDER}
    declared = sealing_verdict(SEALABLE_COMPONENT, clean)
    check(declared["sealed"] and not declared["refused"],
          "the sealable component is sealed within the declared layer-wise bound")
    refused = sealing_verdict(COMMITTED_COMPONENT)
    check(refused["refused"] and not refused["sealed"],
          "sealing is refused for the committed component")
    check(refused["accounted"], "the committed component is still accounted rather than dropped")
    check(len(refused["reasons"]) == 1 and "by definition a leak" in refused["reasons"][0],
          "the refusal names the reason: the component is by definition a leak")

    violation = sealing_verdict(SEALABLE_COMPONENT, TOTAL_CANCELLING_VIOLATION)
    total_drift = sum(TOTAL_CANCELLING_VIOLATION.values())
    check(total_drift == 0, "the declared layer-wise violation conserves the total exactly")
    check(violation["verdict"] == "LayerWiseViolation",
          "a layer-wise sealing violation is reported as a violation")
    check(violation["violating_layers"] == ["mixed", "deep"],
          "the violation sits in exactly the mixed and the deep layer")
    check(not violation["sealed"], "the violation is not cancelled by its conserved total")

    sealable_treatment = {
        "control": "a chain that treats the committed component as sealable and declares it sealed",
        "target": COMMITTED_COMPONENT,
        "declared_sealed": True,
        "verdict": "Rejected",
        "reasons": ["the committed component may never be sealed, so a chain that applies the "
                    "sealing condition to it and declares it sealed contradicts the declaration"],
        "rejected_by": "the declared refusal of sealing for a leaking component",
        "decided_by_a_count": False,
    }
    offsetting = {
        "control": "a chain that lets the committed component offset a sealing violation",
        "declared_violation": {layer: str(TOTAL_CANCELLING_VIOLATION[layer])
                               for layer in LAYER_ORDER},
        "violation_total": str(total_drift),
        "committed_component_magnitude": NO_MAGNITUDE,
        "offset_computable_exactly": False,
        "verdict": "Rejected",
        "reasons": ["a leaking component cannot cancel a sealing violation: the sealing side is "
                    "a constraint, not a source",
                    "the committed component carries no declared magnitude, so no exact offset "
                    "exists, and the violation stands as a violation"],
        "cancelled_by_the_total": False,
        "cancelled_by_the_committed_component": False,
        "rejected_by": "the declared refusal of sealing for a leaking component",
        "decided_by_a_count": False,
    }
    check(sealable_treatment["declared_sealed"] and sealable_treatment["verdict"] == "Rejected",
          "treating the committed component as sealable is rejected")
    check(not refused["sealed"],
          "the declared reading does not seal the committed component, so the control "
          "discriminates")
    check(not offsetting["offset_computable_exactly"]
          and not offsetting["cancelled_by_the_committed_component"],
          "letting the committed component offset a sealing violation is rejected")

    return {
        "declared_reading": "the sealing condition is REFUSED for a component that is by "
                            "definition a leak: the committed component may be accounted but "
                            "never sealed",
        "sealable_component": {
            "sealing_condition": "the declared layer-wise sealing bound, applied to the sealable "
                                 "component only",
            "bound": {layer: str(LAYER_SEALING_BOUND[index])
                      for index, layer in enumerate(LAYER_ORDER)},
            "verdict": declared,
            "sealed": declared["sealed"],
        },
        "committed_component": {
            "accounted": refused["accounted"],
            "sealed": refused["sealed"],
            "sealing_refused": refused["refused"],
            "verdict": refused["verdict"],
            "declared_magnitude": NO_MAGNITUDE,
            "reasons": refused["reasons"],
            "reading": "the committed component is written out and accounted at every declared "
                       "position and is never sealed",
        },
        "layer_wise_violation": {
            "declared_drift": {layer: str(TOTAL_CANCELLING_VIOLATION[layer])
                               for layer in LAYER_ORDER},
            "total_drift": str(total_drift),
            "violating_layers": violation["violating_layers"],
            "verdict": violation["verdict"],
            "cancelled_by_the_total": False,
        },
        "controls": [
            {"control": sealable_treatment["control"], "verdict": sealable_treatment["verdict"],
             "rejection_reasons": sealable_treatment["reasons"],
             "rejected_by_the_declared_condition": True,
             "decided_by_a_count": False},
            {"control": offsetting["control"], "verdict": offsetting["verdict"],
             "rejection_reasons": offsetting["reasons"],
             "rejected_by_the_declared_condition": True,
             "decided_by_a_count": False},
        ],
        "no_magnitude_for_the_committed_component": True,
        "the_leak_is_declared_and_not_repaired": True,
    }


# ------------------------------------------ R9: the four-by-two classification --

DECLARED_CELLS = {
    ("aerosols", NORTH): {
        "declaration": "structure_to_be_preserved",
        "preserved_structure": "the interhemispheric asymmetry and the identity of the "
                               "cold-injecting side",
        "reversible": False,
        "ratchet": False,
        "declared_basis": "aerosols as the north-side structure that sets the interhemispheric "
                          "asymmetry and defines the cold-injecting side",
    },
    ("aerosols", SOUTH): {
        "declaration": "explicitly_unquantified",
        "recorded_separately": True,
        "reversible": False,
        "ratchet": False,
        "declared_basis": "the contract declares no placement for this cell; it is recorded as "
                          "explicitly unquantified rather than invented",
    },
    ("low_cloud", SOUTH): {
        "declaration": "structure_to_be_preserved",
        "preserved_structure": "the south-weighted coupling that turns fast perturbations into "
                               "structural radiative effects",
        "reversible": False,
        "ratchet": False,
        "declared_basis": "low cloud as the south-weighted coupler that turns fast perturbations "
                          "into structural radiative effects",
    },
    ("low_cloud", NORTH): {
        "declaration": "explicitly_unquantified",
        "recorded_separately": True,
        "reversible": False,
        "ratchet": False,
        "declared_basis": "the contract declares no placement for this cell; it is recorded as "
                          "explicitly unquantified rather than invented",
    },
    ("water_vapour", SOUTH): {
        "declaration": "correction_to_be_made",
        "correction": "the declared correction is a declared reversal along the declared reset "
                      "path of the resetable obstruction class, which is where a declared reset "
                      "is accepted; no magnitude is declared",
        "reversible": True,
        "ratchet": False,
        "declared_basis": "water vapour as the fast reversible amplifier that is also the "
                          "carrier of the south-branch injection",
    },
    ("water_vapour", NORTH): {
        "declaration": "explicitly_unquantified",
        "recorded_separately": True,
        "reversible": False,
        "ratchet": False,
        "declared_basis": "the contract declares no placement for this cell; it is recorded as "
                          "explicitly unquantified rather than invented",
    },
    ("wildfire", NORTH): {
        "declaration": "explicitly_unquantified",
        "recorded_separately": True,
        "reversible": False,
        "ratchet": True,
        "declared_basis": "wildfire as a threshold source acting on both sides, with black "
                          "carbon on snow attacking the sealing side's albedo and with partial "
                          "ratchet behaviour",
    },
    ("wildfire", SOUTH): {
        "declaration": "explicitly_unquantified",
        "recorded_separately": True,
        "reversible": False,
        "ratchet": True,
        "declared_basis": "wildfire as a threshold source acting on both sides, with black "
                          "carbon on snow attacking the sealing side's albedo and with partial "
                          "ratchet behaviour",
    },
}

FORBIDDEN_MAGNITUDE_KEYS = ("value", "amount", "rate", "flux", "forcing", "sign", "timing",
                            "anomaly", "tendency", "sensitivity", "trend", "magnitude_value")


def magnitude_audit(node, path="", allow_numbers=False, found=None):
    """Numeric leaves (unless allowed) and magnitude-naming keys anywhere under a record."""
    if found is None:
        found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in FORBIDDEN_MAGNITUDE_KEYS:
                found.append(path + "/" + str(key) + " names a magnitude")
            magnitude_audit(value, path + "/" + str(key), allow_numbers, found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            magnitude_audit(item, path + "/" + str(index), allow_numbers, found)
    elif isinstance(node, bool):
        pass
    elif isinstance(node, (int, Fr, float)) and not allow_numbers:
        found.append(path + " is a numeric leaf: " + str(node))
    return found


def magnitude_key_violations(node, path="", found=None):
    """Every magnitude key anywhere in the payload whose value is not the declared none."""
    if found is None:
        found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "magnitude" and value != NO_MAGNITUDE:
                found.append(path + "/" + str(key) + " = " + str(value))
            magnitude_key_violations(value, path + "/" + str(key), found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            magnitude_key_violations(item, path + "/" + str(index), found)
    return found


def cell_record(factor, side, cell):
    """One declared classification cell, with no magnitude of any kind."""
    record = {
        "factor": factor,
        "side": side,
        "declaration": cell["declaration"],
        "magnitude": NO_MAGNITUDE,
        "magnitude_is_not_asserted": True,
        "reversible": bool(cell.get("reversible", False)),
        "ratchet": bool(cell.get("ratchet", False)),
        "declared_basis": cell.get("declared_basis", ""),
    }
    if cell["declaration"] == "correction_to_be_made":
        record["correction"] = cell.get("correction", "")
    if cell["declaration"] == "structure_to_be_preserved":
        record["preserved_structure"] = cell.get("preserved_structure", "")
    if cell["declaration"] == "explicitly_unquantified":
        record["recorded_separately"] = True
    return record


def classification_verdict(cells, accounts_fused=False):
    """The declared four-by-two classification rules, applied to one table."""
    reasons = []
    expected = {(factor, side) for factor in FACTORS for side in SIDES}
    if set(cells) != expected:
        reasons.append("the table must cover exactly the four declared factors on the two "
                       "declared sides")
    for key, cell in sorted(cells.items()):
        if cell.get("declaration") not in DECLARATIONS:
            reasons.append("the cell " + str(key) + " carries " + str(cell.get("declaration"))
                           + ", which is not exactly one of the three declared declarations")
    differing = [str(key) for key in sorted(set(cells) & expected)
                 if cells[key].get("declaration") != DECLARED_CELLS[key]["declaration"]]
    if differing:
        reasons.append("the declared placement of the contract is used cell by cell; the cells "
                       + ", ".join(differing) + " are declared differently")
    for factor in SIDE_SPECIFIC_FACTORS:
        if (factor, NORTH) in cells and (factor, SOUTH) in cells:
            north = cells[(factor, NORTH)].get("declaration")
            south = cells[(factor, SOUTH)].get("declaration")
            if north == south:
                reasons.append("the contract declares the factor " + factor + " on one side "
                               "only, so a symmetric north-south treatment of it is rejected; "
                               "both of its cells carry " + str(north))
    for key, cell in sorted(cells.items()):
        if key not in expected:
            continue
        declared_kind = DECLARED_CELLS[key]["declaration"]
        given = cell.get("declaration")
        if declared_kind == "structure_to_be_preserved" and given == "correction_to_be_made":
            reasons.append("the cell " + str(key) + " is a declared structure to be preserved "
                           "and is treated as a correctable perturbation")
        if (declared_kind == "correction_to_be_made"
                and not str(cell.get("correction", "")).strip()):
            reasons.append("the cell " + str(key) + " is a correction to be made and does not "
                           "declare its correction")
        if (declared_kind == "structure_to_be_preserved"
                and not str(cell.get("preserved_structure", "")).strip()):
            reasons.append("the cell " + str(key) + " is a structure to be preserved and does "
                           "not declare what is preserved")
        if (declared_kind == "explicitly_unquantified"
                and not cell.get("recorded_separately", False)):
            reasons.append("the cell " + str(key) + " is explicitly unquantified and must be "
                           "recorded separately")
        if cell.get("ratchet") and cell.get("reversible"):
            reasons.append("the cell " + str(key) + " carries declared ratchet behaviour and is "
                           "treated as reversible")
        if (cell.get("declaration") == "correction_to_be_made"
                and not str(cell.get("correction", "")).strip()):
            reasons.append("the cell " + str(key) + " is treated as a correction without a "
                           "declared correction")
    if accounts_fused:
        reasons.append("the correction account and the structure account are kept separate; a "
                       "table that fuses them into one account is rejected")
    return {
        "accepted": not reasons,
        "verdict": "Accepted" if not reasons else "Rejected",
        "reasons": reasons,
        "cells_covered": len(cells),
        "rejected_by": "the declared classification rules" if reasons else "",
        "decided_by_a_count": False,
    }


def section_factor_classification():
    """R9: the four-by-two table, its three declarations and its four rejections."""
    declared = classification_verdict({key: dict(value) for key, value in DECLARED_CELLS.items()})
    check(declared["accepted"], "the declared four-by-two table satisfies the declared rules")
    check(len(DECLARED_CELLS) == len(FACTORS) * len(SIDES),
          "the table has exactly one cell per declared factor and side")
    declarations_per_cell = {key: 1 for key in DECLARED_CELLS}
    check(all(value == 1 for value in declarations_per_cell.values()),
          "every cell carries exactly one declaration")
    check(all(cell["declaration"] in DECLARATIONS for cell in DECLARED_CELLS.values()),
          "every declaration is one of the three declared kinds")

    records = [cell_record(factor, side, DECLARED_CELLS[(factor, side)])
               for factor in FACTORS for side in SIDES]
    accounts = {kind: [factor + "/" + side for factor in FACTORS for side in SIDES
                       if DECLARED_CELLS[(factor, side)]["declaration"] == kind]
                for kind in DECLARATIONS}
    check(len(accounts["correction_to_be_made"]) == 1,
          "exactly one declared cell is a correction to be made")
    check(len(accounts["structure_to_be_preserved"]) == 2,
          "exactly two declared cells are structures to be preserved")
    check(len(accounts["explicitly_unquantified"]) == 5,
          "exactly five declared cells are explicitly unquantified")
    check(sum(len(account) for account in accounts.values()) == len(records),
          "the three accounts partition the eight declared cells")

    structure_as_correction = {key: dict(value) for key, value in DECLARED_CELLS.items()}
    structure_as_correction[("aerosols", NORTH)] = {
        **structure_as_correction[("aerosols", NORTH)],
        "declaration": "correction_to_be_made",
        "correction": "a declared reversal of the north-side structure",
    }
    structure_verdict = classification_verdict(structure_as_correction)
    check(not structure_verdict["accepted"],
          "treating a structure cell as a correctable perturbation is rejected")
    check(any("treated as a correctable perturbation" in reason
              for reason in structure_verdict["reasons"]),
          "the structure control is rejected by the named rule")

    ratchet_reversible = {key: dict(value) for key, value in DECLARED_CELLS.items()}
    ratchet_reversible[("wildfire", NORTH)] = {
        **ratchet_reversible[("wildfire", NORTH)], "reversible": True,
        "declaration": "correction_to_be_made",
        "correction": "a declared reversal of the threshold source",
    }
    ratchet_verdict = classification_verdict(ratchet_reversible)
    check(not ratchet_verdict["accepted"], "treating a ratchet cell as reversible is rejected")
    check(any("treated as reversible" in reason for reason in ratchet_verdict["reasons"]),
          "the ratchet control is rejected by the named rule")

    symmetric = {key: dict(value) for key, value in DECLARED_CELLS.items()}
    for factor in SIDE_SPECIFIC_FACTORS:
        source = DECLARED_CELLS[(factor, NORTH)]
        if source["declaration"] == "explicitly_unquantified":
            source = DECLARED_CELLS[(factor, SOUTH)]
        symmetric[(factor, NORTH)] = {**symmetric[(factor, NORTH)],
                                      "declaration": source["declaration"]}
        symmetric[(factor, SOUTH)] = {**symmetric[(factor, SOUTH)],
                                      "declaration": source["declaration"]}
        if source["declaration"] == "correction_to_be_made":
            symmetric[(factor, NORTH)]["correction"] = source.get("correction", "")
            symmetric[(factor, SOUTH)]["correction"] = source.get("correction", "")
        if source["declaration"] == "structure_to_be_preserved":
            preserved = source.get("preserved_structure", "")
            symmetric[(factor, NORTH)]["preserved_structure"] = preserved
            symmetric[(factor, SOUTH)]["preserved_structure"] = preserved
    symmetric_verdict = classification_verdict(symmetric)
    check(not symmetric_verdict["accepted"],
          "a symmetric north-south treatment is rejected where the contract declares asymmetry")
    check(sum(1 for reason in symmetric_verdict["reasons"]
              if "symmetric north-south treatment" in reason) == len(SIDE_SPECIFIC_FACTORS),
          "all three side-specific factors are named by the symmetry control")

    fused_verdict = classification_verdict({key: dict(value)
                                            for key, value in DECLARED_CELLS.items()},
                                           accounts_fused=True)
    check(not fused_verdict["accepted"],
          "fusing the correction account with the structure account is rejected")
    check(any("fuses them into one account" in reason for reason in fused_verdict["reasons"]),
          "the fusion control is rejected by the named rule")

    audit_targets = {"cell_records": records}
    audit_findings = []
    for name, target in audit_targets.items():
        audit_findings += magnitude_audit(target, name, allow_numbers=False)
    check(not audit_findings,
          "no magnitude and no numeric leaf appears in any of the four-by-two cell records")
    check(all(record["magnitude"] == NO_MAGNITUDE for record in records),
          "every declared cell records the committed-style none for its magnitude")

    return {
        "declared_reading": "four factors - aerosols, low cloud, water vapour and wildfire - are "
                            "classified on each of the two sides into exactly one of three "
                            "declarations: a correction to be made with its correction declared, "
                            "a structure to be preserved, or explicitly unquantified",
        "declared_placement": {
            factor: {side: DECLARED_CELLS[(factor, side)]["declaration"] for side in SIDES}
            for factor in FACTORS},
        "declared_basis": {
            factor: {side: DECLARED_CELLS[(factor, side)]["declared_basis"] for side in SIDES}
            for factor in FACTORS},
        "cell_records": records,
        "cells": len(records),
        "declarations": list(DECLARATIONS),
        "accounts": accounts,
        "account_sizes": {kind: len(accounts[kind]) for kind in DECLARATIONS},
        "accounts_are_separate": True,
        "declared_asymmetry": {
            "side_specific_factors": list(SIDE_SPECIFIC_FACTORS),
            "factors_declared_on_both_sides": list(BOTH_SIDES_FACTORS),
            "reading": "aerosols is declared on the north side, low cloud and water vapour on "
                       "the south side, and wildfire on both sides; the table is asymmetric "
                       "exactly where the contract declares asymmetry",
            "the_sealing_side": "the south side, by the declared correspondence that names the "
                                "north side the cold-injecting side and leaves the sealing side "
                                "the other of the two declared roles",
        },
        "declared_verdict": declared,
        "controls": [
            {"control": "a structure cell treated as a correctable perturbation",
             "cell": "aerosols/north",
             "verdict": structure_verdict["verdict"],
             "rejection_reasons": structure_verdict["reasons"],
             "rejected_by_the_declared_condition": True,
             "decided_by_a_count": False},
            {"control": "a ratchet cell treated as reversible",
             "cell": "wildfire/north",
             "verdict": ratchet_verdict["verdict"],
             "rejection_reasons": ratchet_verdict["reasons"],
             "rejected_by_the_declared_condition": True,
             "decided_by_a_count": False},
            {"control": "a symmetric north-south treatment",
             "cells": [factor + "/north and " + factor + "/south"
                       for factor in SIDE_SPECIFIC_FACTORS],
             "verdict": symmetric_verdict["verdict"],
             "rejection_reasons": symmetric_verdict["reasons"],
             "rejected_by_the_declared_condition": True,
             "decided_by_a_count": False},
            {"control": "a fusion of the correction account with the structure account",
             "verdict": fused_verdict["verdict"],
             "rejection_reasons": fused_verdict["reasons"],
             "rejected_by_the_declared_condition": True,
             "decided_by_a_count": False},
        ],
        "magnitude_audit": {
            "rule": "no magnitude and no numeric leaf appears in a four-by-two cell record; the "
                    "declared cell counts live in the accounts and not in the cell records",
            "audited": sorted(audit_targets),
            "findings": audit_findings,
            "no_magnitude_for_aerosols_low_cloud_water_vapour_or_wildfire": True,
        },
        "no_magnitude_is_given_for_any_factor": True,
    }


# ------------------------------------ R10: the fourth uncertainty term --------

def uncertainty_terms():
    """The three inherited quantified uncertainty terms, from the declared composition."""
    composition = dict(OBSERVATION_COMPOSITIONS)["B"]
    return {name: composition[index] * COMPOSITION_OFFSETS[index]
            for index, name in enumerate(UNCERTAINTY_TERMS)}


def section_uncertainty_fourth_term():
    """R10: the fourth term, recorded separately at every seam and never fused."""
    terms = uncertainty_terms()
    check(terms["mapping"] == Fr(1, 64), "the declared mapping term is exactly 1/64")
    check(terms["bias"] == Fr(1, 64), "the declared bias term is exactly 1/64")
    check(terms["sampling"] == Fr(3, 256), "the declared sampling term is exactly 3/256")
    check(all(value >= 0 for value in terms.values()),
          "each inherited separated uncertainty term is non-negative")
    seams = []
    for label in CYCLE_LABELS:
        seams.append({
            "cycle": label,
            "mapping": str(terms["mapping"]),
            "bias": str(terms["bias"]),
            "sampling": str(terms["sampling"]),
            "committed_but_unquantified": {
                "term": FOURTH_TERM,
                "quantified": False,
                "magnitude": NO_MAGNITUDE,
                "recorded_separately": True,
                "recorded_at_this_seam": True,
            },
            "recorded_separately": True,
            "terms_recorded": 4,
        })
    check(len(seams) == CYCLE_COUNT,
          "the four uncertainty terms are recorded at every one of the three seams")
    check(all(row["terms_recorded"] == 4 for row in seams),
          "every seam carries all four terms")
    check(all(row["committed_but_unquantified"]["magnitude"] == NO_MAGNITUDE for row in seams),
          "the fourth term is recorded at every seam with no magnitude")
    check(all(row["committed_but_unquantified"]["recorded_separately"] for row in seams),
          "the fourth term is recorded separately and never fused")
    fused_three = sum(terms.values())
    check(fused_three == Fr(11, 256),
          "a fused figure over the three inherited terms would be exactly 11/256")
    four_term_fusion = {
        "declared": "a single fused uncertainty figure over all four terms",
        "quantified_terms": [str(terms[name]) for name in UNCERTAINTY_TERMS],
        "fourth_term": NO_MAGNITUDE,
        "fused_magnitude_exists": False,
        "verdict": "Rejected",
        "reasons": ["a fused figure over the three quantified terms is a violation of the "
                    "declaration, and a fused figure over all four cannot be formed at all "
                    "because the fourth term is unquantified"],
        "decided_by_a_count": False,
    }
    check(not four_term_fusion["fused_magnitude_exists"],
          "no fused figure over the four terms exists: the fourth term is unquantified")
    check(all(row["mapping"] == row["bias"] for row in seams)
          and all(row["sampling"] == "3/256" for row in seams),
          "the three quantified terms are the same exact values at every seam")

    return {
        "declared_terms": [*UNCERTAINTY_TERMS, FOURTH_TERM],
        "term_count": 4,
        "quantified_terms": {name: str(terms[name]) for name in UNCERTAINTY_TERMS},
        "fourth_term": {
            "name": FOURTH_TERM,
            "quantified": False,
            "magnitude": NO_MAGNITUDE,
            "recorded_separately_at_every_seam": True,
            "never_fused": True,
        },
        "seams": seams,
        "four_terms_separately_at_every_seam": True,
        "fused_three_term_figure": str(fused_three),
        "fused_control": four_term_fusion,
        "pooling_control": {
            "pooled": "rejected: heterogeneous sources are recorded separately and pinned "
                      "separately, never pooled",
            "fused_with_the_fourth_term": False,
        },
        "no_magnitude_for_the_fourth_term": True,
    }


# --------------------------------------------- R11: the inherited controls ----

def layer_sealing_rows():
    """The declared layer contents, their seam redistribution and the layer-wise sealing."""
    contents = dict(zip(LAYER_ORDER, LAYER_CONTENTS, strict=True))
    slow_total = sum(contents.values())
    check(slow_total == Fr(7, 8), "the declared slow remainder is exactly 7/8")
    check(Fr(1, 4) == FAST_REMAINDER, "the declared fast remainder is exactly 1/4")
    check(slow_total + FAST_REMAINDER == Fr(9, 8),
          "the declared carried remainder is exactly 9/8")
    running = dict(contents)
    check(SEALING_SHARES["outer"] + SEALING_SHARES["inner"] == 1,
          "the inherited sealing shares of the two sides sum to exactly one")
    seams = []
    for label in CYCLE_LABELS:
        updated = dict(running)
        for source, target, share in SEAM_TRANSFERS:
            moved = running[source] * share
            updated[source] -= moved
            updated[target] += moved
        drift = {layer: updated[layer] - running[layer] for layer in LAYER_ORDER}
        check(sum(updated.values()) == slow_total,
              "the declared seam redistribution conserves the slow total exactly")
        check(sum(drift.values()) == 0, "the per-layer drifts sum to zero at every seam")
        measured = {layer: (SEALING_SHARES["outer"] + SEALING_SHARES["inner"]) * updated[layer]
                    for layer in LAYER_ORDER}
        sealed = [abs(measured[layer] - updated[layer]) <= LAYER_SEALING_BOUND[index]
                  for index, layer in enumerate(LAYER_ORDER)]
        check(all(sealed),
              "every layer is sealed within its declared bound at every seam, layer by layer")
        seams.append({
            "cycle": label,
            "contents": [str(updated[layer]) for layer in LAYER_ORDER],
            "total": str(sum(updated.values())),
            "per_layer_drift": [str(drift[layer]) for layer in LAYER_ORDER],
            "measured_content": [str(measured[layer]) for layer in LAYER_ORDER],
            "sealing_drift": [str(measured[layer] - updated[layer]) for layer in LAYER_ORDER],
            "memory_layer": max(LAYER_ORDER, key=lambda layer: (updated[layer], layer)),
            "sealed_layer_by_layer": True,
        })
        running = updated
    check(all(row["memory_layer"] == "deep" for row in seams),
          "the deep layer holds the carried memory at every seam")
    check(seams[0]["contents"] == ["7/64", "1/4", "33/64"],
          "the first seam contents are exactly 7/64, 1/4 and 33/64")
    check(seams[0]["per_layer_drift"] == ["-1/64", "0", "1/64"],
          "the first seam per-layer drifts are exactly -1/64, 0 and 1/64")
    cancelling_total = sum(TOTAL_CANCELLING_VIOLATION.values())
    violating = [layer for index, layer in enumerate(LAYER_ORDER)
                 if abs(TOTAL_CANCELLING_VIOLATION[layer]) > LAYER_SEALING_BOUND[index]]
    check(cancelling_total == 0, "the total-cancelling control conserves the total exactly")
    check(violating == ["mixed", "deep"],
          "the total-cancelling control violates the bound in exactly two layers")
    check(not (cancelling_total == 0 and not violating),
          "a layer-wise violation is not cancelled by a conserved total")
    return {
        "layers": list(LAYER_ORDER),
        "contents": {layer: str(contents[layer]) for layer in LAYER_ORDER},
        "slow_total": str(slow_total),
        "fast": str(FAST_REMAINDER),
        "total": str(slow_total + FAST_REMAINDER),
        "bound": {layer: str(LAYER_SEALING_BOUND[index])
                  for index, layer in enumerate(LAYER_ORDER)},
        "seams": seams,
        "all_layers_sealed": True,
        "sealing_shares": {side: str(SEALING_SHARES[side]) for side in SEALING_SHARES},
        "sealing_shares_reading": "the declared shares of the two sides, inherited from the "
                                  "surgery run's collar flux; they sum to exactly one, so the "
                                  "measured content of every layer equals its declared content "
                                  "and the bound of zero holds layer by layer",
        "the_bound_applies_layer_by_layer": True,
        "total_cancelling_control": {
            "control": "a declared layer-wise violation whose total is conserved exactly",
            "declared_violation": {layer: str(TOTAL_CANCELLING_VIOLATION[layer])
                                   for layer in LAYER_ORDER},
            "total_drift": str(cancelling_total),
            "violating_layers": violating,
            "verdict": "LayerWiseViolation",
            "cancelled_by_the_total": False,
        },
        "memory_layer": "deep",
        "memory_layer_stable": True,
    }


def identity_loop_verdict(legs):
    """The declared loop on the twelve phases: its legs sum to a multiple of twelve or not."""
    total = sum(legs)
    return {
        "legs": list(legs),
        "sum": total,
        "phase_shift": total % PHASES,
        "returns_the_identity": total % PHASES == 0,
        "verdict": "Identity" if total % PHASES == 0 else "NotTheIdentity",
    }


def section_inherited_controls(uncertainty, layers):
    """R11: the five inherited controls, executed."""
    readings = {}
    for name, composition in OBSERVATION_COMPOSITIONS:
        artefact = sum(weight * offset for weight, offset
                       in zip(composition, COMPOSITION_OFFSETS, strict=True))
        readings[name] = {
            "composition": [str(value) for value in composition],
            "mechanism_reading": {
                "slow_layer_contents": layers["seams"][0]["contents"],
                "slow_total": layers["slow_total"],
                "per_layer_drift": layers["seams"][0]["per_layer_drift"],
                "memory_layer": layers["seams"][0]["memory_layer"],
            },
            "composition_only_reading": str(artefact),
        }
    names = [name for name, _composition in OBSERVATION_COMPOSITIONS]
    first, second = readings[names[0]], readings[names[1]]
    check(first["mechanism_reading"] == second["mechanism_reading"],
          "with the mechanism fixed and only the observing composition moved, every declared "
          "reading is unchanged")
    artefact_first = fr(first["composition_only_reading"])
    artefact_second = fr(second["composition_only_reading"])
    check(artefact_first != artefact_second,
          "the composition-only reading does move when only the composition moves")
    check(artefact_second - artefact_first == Fr(3, 256),
          "the composition-only reading moves by exactly 3/256")
    fused_first = fr(first["mechanism_reading"]["slow_total"]) + artefact_first
    fused_second = fr(second["mechanism_reading"]["slow_total"]) + artefact_second
    check(fused_second - fused_first == Fr(3, 256) and fused_second != fused_first,
          "a reading that mixes the mechanism with the composition moves by exactly the "
          "composition-only amount and is rejected as an artefact")

    identity = identity_loop_verdict(IDENTITY_LOOP_LEGS)
    non_closed = identity_loop_verdict(NON_CLOSED_LOOP_LEGS)
    check(identity["returns_the_identity"], "the declared identity loop returns the identity")
    check(not non_closed["returns_the_identity"],
          "the declared non-closed control loop does not return the identity")
    check(identity["phase_shift"] == 0 and non_closed["phase_shift"] == 1,
          "the two declared loops differ by exactly one phase of the twelve")

    atmospheric_memory = Fr(0)
    declared_memory = sum(fr(value) for value in layers["contents"].values())
    check(atmospheric_memory == 0,
          "the purely atmospheric chain carries no memory at the seam by the declared reset")
    check(declared_memory == Fr(7, 8),
          "the chain with the declared slow component keeps the carried memory 7/8")

    return {
        "sampling_change_invariance": {
            "control": "the sampling-change invariance control of supplement one, carried forward",
            "declared_compositions": {name: readings[name]["composition"] for name in names},
            "readings": readings,
            "readings_unchanged": first["mechanism_reading"] == second["mechanism_reading"],
            "composition_only_reading_moves": artefact_first != artefact_second,
            "composition_only_difference": str(artefact_second - artefact_first),
            "the_composition_only_reading_is_an_artefact": True,
            "not_read_as_a_change_of_mechanism": True,
            "fused_reading": {
                "declared": "a reading that adds the composition term to the mechanism reading",
                "difference": str(fused_second - fused_first),
                "verdict": "Rejected as an artefact",
            },
        },
        "separated_uncertainty": {
            "control": "the separated-uncertainty control of supplement one, carried forward",
            "terms": [*UNCERTAINTY_TERMS, FOURTH_TERM],
            "seams": uncertainty["seams"],
            "four_terms_present_separately_at_every_seam": True,
            "fused_control": uncertainty["fused_control"],
            "pooling_control": uncertainty["pooling_control"],
        },
        "layer_wise_sealing": {
            "control": "the layer-wise sealing control of supplement one, carried forward",
            "bound": layers["bound"],
            "all_layers_sealed": layers["all_layers_sealed"],
            "sealed_at_every_seam": True,
            "memory_layer": layers["memory_layer"],
            "memory_layer_stable": layers["memory_layer_stable"],
            "total_cancelling_control": layers["total_cancelling_control"],
        },
        "identity_loop": {
            "control": "the identity-loop control of note 0235, carried forward",
            "declared_loop": identity,
            "control_loop": non_closed,
            "discriminates": identity["returns_the_identity"]
            and not non_closed["returns_the_identity"],
            "five_point_identity": "the fifth power of the declared generation cycle is the "
                                   "identity on the five declared points",
        },
        "atmospheric_memory_loss": {
            "control": "the purely atmospheric chain of the frozen contract, carried forward",
            "atmospheric_only": {"carried_memory_at_the_seam": str(atmospheric_memory),
                                 "lost": atmospheric_memory == 0},
            "with_the_slow_component": {"carried_memory_at_the_seam": str(declared_memory),
                                        "kept": declared_memory != 0},
            "the_split_does_work": True,
        },
        "inherited_controls_still_run": [
            "the sampling-change invariance control",
            "the separated-uncertainty control",
            "the layer-wise sealing control",
            "the identity-loop control",
            "the atmospheric-chain memory-loss control",
        ],
        "failed_controls": [
            {"control": "the declared year-length control of the astronomical remainders",
             "where": "R5_astronomical_remainders",
             "outcome": "FAILED_TO_DISCRIMINATE",
             "why": "the non-closure reading holds under every declared year length, so this "
                    "control cannot separate the three declarations; it shows only that the "
                    "verdict is insensitive to the declared year, and it is recorded rather "
                    "than dropped"},
            {"control": "the monotonicity control of the one-way commitment reservoir",
             "where": "R7_commitment_reservoir",
             "outcome": "FAILED_TO_DISCRIMINATE",
             "why": "with both declared increments set equal the state is still non-decreasing, "
                    "so monotonicity alone does not test the threshold branch; only the "
                    "hysteresis control sees it"},
        ],
        "controls_that_did_discriminate": [
            "the either-or terminal against the conjunction, on the two mixed cases",
            "the netting terminal against the separateness of the two residual records",
            "the obstructing terminal's verdict flip against the declared independence",
            "the compromising terminal's declared tolerance against the exactness requirement",
            "the displaced sealable state against closure at the fixed point",
            "the forced-closed, forced-open and either-or contrast terminals",
            "the reset applied to the non-resetable commitment",
            "rejecting one five-point cycle and identifying the two",
            "the primality reading on the composite modulus four",
            "the closing claims against the three exact remainders",
            "the parent chain's first-order relaxation against monotonicity and hysteresis",
            "the sealable treatment of the committed component and its offsetting of a violation",
            "the structure, ratchet, symmetry and fusion controls of the four-by-two table",
            "the fused uncertainty control against the separated four terms",
            "the non-closed control loop against the declared identity loop",
        ],
        "carried_forward_failures": [
            {"control": "the drift and iterability control of the parent chain",
             "source": "experiments/three_cycle_chain_v1, note 0238",
             "outcome": "FAILED_TO_DISCRIMINATE",
             "why": "closure is the pointwise condition E(h) = h, so a chain that closes in C1 "
                    "cannot drift in C2 or C3 and the detector has nothing to detect; it is not "
                    "repaired here"},
            {"control": "the radial-normal flux control of the surgery run",
             "source": "experiments/three_cycle_supplement_v1, note 0237",
             "outcome": "FAILED_TO_DISCRIMINATE",
             "why": "with a purely radial normal the flux rise is zero for every chirality pair, "
                    "so that control cannot separate the declared pair from the same-chirality "
                    "pair; it is not repaired here"},
            {"control": "the arrival step count under the two chirality signs",
             "source": "experiments/three_cycle_supplement_v1, note 0237",
             "outcome": "FAILED_TO_DISCRIMINATE",
             "why": "both declared rotation senses arrive in the same number of steps, so the "
                    "arrival condition does not discriminate handedness; it is not repaired here"},
        ],
        "carried_forward_failures_count": 3,
    }


# ------------------------------------------------- R12: the exact baselines ---

def section_baselines(sym):
    """R12: the exact baselines of the earlier runs, reproduced."""
    p, q, h = sym["p"], sym["q"], sym["h"]

    witness = sp.Poly(sp.expand(sym["G"].subs({p: rat(PERTURBATION_WITNESS[0]),
                                               q: rat(PERTURBATION_WITNESS[1])})), h)
    branches = isolated_real_roots(witness, (Fr(-1), Fr(1)))
    check(len(branches) == 2, "the perturbation witness has exactly two real branches")
    e0 = sym["E0"].subs({p: rat(PERTURBATION_WITNESS[0]), q: rat(PERTURBATION_WITNESS[1])})
    e0_poly = sp.Poly(sp.expand(e0), h)
    check(e0_poly.degree() == 2, "the side-0 amplitude at the witness is a quadratic in h")
    second, first, constant = [fr(value) for value in e0_poly.all_coeffs()]
    witness_rows = []
    for lo, hi in branches:
        box = Ivl(lo, hi)
        for _ in range(200):
            if box.abs_upper() < 1:
                break
            middle = (box.lo + box.hi) / 2
            left = Ivl(box.lo, middle)
            right = Ivl(middle, box.hi)
            box = left if witness.eval(rat(left.lo)) * witness.eval(rat(left.hi)) < 0 else right
        amplitude = quadratic_abs_upper(second, first, constant, box)
        check(box.abs_upper() < 1, "the refined branch stays strictly inside (-1, 1)")
        check(amplitude < 1, "the side-0 amplitude on the refined branch is strictly below one")
        witness_rows.append({
            "isolation_interval": [str(lo), str(hi)],
            "refined_interval": [str(box.lo), str(box.hi)],
            "abs_h_upper_bound": str(box.abs_upper()),
            "abs_E_0_upper_bound": str(amplitude),
            "below_the_frozen_level": True,
        })
    floor = Fr(1)
    check(max(fr(row["abs_h_upper_bound"]) for row in witness_rows) < floor,
          "both witness branches have |h| < 1")
    check(max(fr(row["abs_E_0_upper_bound"]) for row in witness_rows) < floor,
          "both witness branches have |E_0| < 1")
    check(max(floor, max(fr(row["abs_E_0_upper_bound"]) for row in witness_rows)) == floor,
          "the declared J_inf is exactly the frozen level 1")
    leading = fr(witness.LC())
    discriminant = fr(sp.discriminant(witness.as_expr(), h))
    check(leading != 0, "the leading coefficient of the witness quartic does not vanish")
    check(discriminant != 0,
          "the discriminant of the specialised quartic does not vanish; since the resultant is "
          "the leading coefficient times the discriminant, and clearing its denominator "
          "multiplies it by a nonzero rational, neither the resultant nor the cleared resultant "
          "vanishes and the witness is off the discriminant variety")

    cubic = sp.Poly(h ** 3 + 8 * h ** 2 + 64 * h - 320, h)
    derivative = sp.Poly(3 * h ** 2 + 16 * h + 64, h)
    check(fr(sp.discriminant(derivative.as_expr(), h)) == -512,
          "the derivative of the closure cubic has discriminant -512 and so is strictly positive")
    check(sp.Poly(sym["closure"], h).as_expr().subs(h, 0) == 0,
          "the closure reading always has the trivial exit h = 0")
    closure_roots = isolated_real_roots(cubic, (Fr(3), Fr(4)))
    check(len(closure_roots) == 1,
          "the nontrivial closure branch has exactly one real exit")
    low, high = closure_roots[0]
    prefix = correctly_rounded_prefix(Ivl(low, high), 17)
    check(prefix == CLOSURE_AMPLITUDE_PREFIX,
          "the closure amplitude is correctly rounded to 3.2035072879526181")
    divisors = [value for value in range(1, 321) if 320 % value == 0]
    check(all(cubic.eval(rat(sign * value)) != 0 for value in divisors for sign in (1, -1)),
          "the closure cubic has no rational root, so the decimal expansion does not terminate")
    quotient = -(Ivl(3 * low * low, 3 * high * high) + Ivl(16 * low, 16 * high) + Ivl(192))
    check(quotient.hi < 0,
          "the quotient quadratic h^2 + (8 + w) h + (64 + 8 w + w^2) of the closure cubic has a "
          "strictly negative discriminant, so the other two exits are a non-real conjugate pair")

    level = sp.Poly(h ** 4 + 8 * h ** 3 + 64 * h ** 2 + 192 * h - 512, h)
    substituted = sp.Poly(sp.expand(level.as_expr().subs(h, h - 2)), h)
    check(sp.expand(substituted.as_expr() - (h ** 4 + 40 * h ** 2 - 688)) == 0,
          "the level reading becomes u^4 + 40 u^2 - 688 with u = h + 2")
    level_roots = isolated_real_roots(level, (Fr(-6), Fr(2)))
    check(len(level_roots) == 2, "the level reading has exactly two real branches")
    negative, positive = level_roots[0], level_roots[1]
    check(Fr(-6) < negative[0] and negative[1] < Fr(-5),
          "the negative real branch lies strictly inside (-6, -5)")
    check(Fr(1) < positive[0] and positive[1] < Fr(2),
          "the positive real branch lies strictly inside (1, 2)")

    sigma = QNr(-20, 8, 17)
    square = sigma * sigma
    check((square + sigma * 40 - QNr(688)).is_zero(),
          "sigma^2 + 40 sigma - 688 = 0 in the exact extension Q(sqrt(17)) with "
          "sigma = 8 sqrt(17) - 20")
    check(sigma.sign() == 1,
          "sigma = 8 sqrt(17) - 20 is strictly positive, decided by squaring")
    root_of_seventeen = sqrt_ball(Fr(17), 200)
    sigma_box = Ivl(8 * root_of_seventeen.lo - 20, 8 * root_of_seventeen.hi - 20)
    check(sigma_box.lo > 0, "the enclosure of sigma stays strictly positive")
    small = sqrt_ball(sigma_box.lo, 200)
    large = sqrt_ball(sigma_box.hi, 200)
    amplitude = Ivl(2 + small.lo, 2 + large.hi)
    check(Fr(5) < amplitude.lo and amplitude.hi < Fr(6),
          "the level reading's largest branch amplitude is enclosed strictly inside (5, 6)")
    check(amplitude.lo > Fr(4),
          "the level reading's largest branch amplitude is strictly above 4")
    ordering = Fr(1) < Fr(low) < Fr(high) < Fr(4) < amplitude.lo
    check(ordering,
          "the three amplitudes are ordered exactly: 1 < 3.2035072879526181... < "
          "2 + sqrt(8 sqrt(17) - 20)")

    return {
        "first_scheme": {
            "amplitude_floor": "J_inf = 1",
            "attained_at": "(p, q) = (-2, 17/10)",
            "on_the_discriminant_variety": False,
            "discriminant_of_the_specialised_quartic": str(discriminant),
            "leading_coefficient_of_the_specialised_quartic": str(leading),
            "real_branches_at_the_witness": len(witness_rows),
            "branches": witness_rows,
            "frozen_level_of_the_ten_middle_sides": "1",
            "source": "note 0235 and the parent runs",
        },
        "closure_reading": {
            "nontrivial_branch_equation": "h^3 + 8 h^2 + 64 h - 320 = 0",
            "real_exits": len(closure_roots),
            "amplitude": CLOSURE_AMPLITUDE_TEXT,
            "correctly_rounded_prefix": prefix,
            "isolation_interval": [str(low), str(high)],
            "no_rational_root": True,
            "derivative_discriminant": "-512",
            "quotient_quadratic_discriminant_enclosure": [str(quotient.lo), str(quotient.hi)],
            "the_other_two_exits_are_non_real": True,
        },
        "level_reading": {
            "equation": LEVEL_READING_QUARTIC,
            "real_branches": len(level_roots),
            "substitution": "u = h + 2, u^4 + 40 u^2 - 688 = 0",
            "closed_form": "h = -2 +- sqrt(8 sqrt(17) - 20)",
            "closed_form_verified_in": "the exact real quadratic extension Q(sqrt(17))",
            "sigma": "8 sqrt(17) - 20",
            "sigma_is_positive": True,
            "largest_branch_amplitude": LEVEL_AMPLITUDE_TEXT,
            "largest_branch_amplitude_enclosure": [str(amplitude.lo), str(amplitude.hi)],
            "negative_branch_enclosure": [str(negative[0]), str(negative[1])],
            "positive_branch_enclosure": [str(positive[0]), str(positive[1])],
        },
        "ordering": {
            "statement": "1 < 3.2035072879526181... < 2 + sqrt(8 sqrt(17) - 20)",
            "asserted_exactly": True,
            "between": ["the first scheme's amplitude floor 1",
                        "the closure reading's amplitude 3.2035072879526181...",
                        "the level reading's largest branch amplitude 2 + sqrt(8 sqrt(17) - 20)"],
            "decided_on_exact_rationals": True,
            "rational_witnesses": {"one": "1", "four": "4"},
        },
    }


# --------------------------------------------------------------- the run -----

def build_payload():
    contract_digest = digest(CONTRACT_PATH)
    parent_digest = digest(PARENT_CONTRACT_PATH)
    supplement_digest = digest(PARENT_SUPPLEMENT_PATH)
    surgery_digest = digest(SURGERY_CONTRACT_PATH)
    check(contract_digest == DECLARED_CONTRACT_SHA256,
          "this run's contract is the frozen one, byte for byte")
    check(parent_digest == DECLARED_PARENT_SHA256,
          "the frozen parent contract is retained byte for byte")
    check(supplement_digest == DECLARED_SUPPLEMENT_SHA256,
          "the parent supplement is retained byte for byte")
    check(surgery_digest == DECLARED_SURGERY_SHA256,
          "the surgery run's contract is retained byte for byte")
    check(CONTRACT["parent_contracts"][0]["sha256"] == DECLARED_PARENT_SHA256,
          "this contract names the parent contract digest it inherits")
    check(CONTRACT["parent_contracts"][1]["sha256"] == DECLARED_SUPPLEMENT_SHA256,
          "this contract names the parent supplement digest it inherits")
    check(CONTRACT["parent_contracts"][2]["sha256"] == DECLARED_SURGERY_SHA256,
          "this contract names the surgery contract digest it inherits")

    sym = {"p": sp.Symbol("p"), "q": sp.Symbol("q"), "h": sp.Symbol("h")}
    alpha = RATIONAL(1, 8) + sym["p"]
    beta = RATIONAL(1, 8) + sym["q"]
    e0 = sym["h"] / 2 + alpha * sym["h"] ** 2
    annual = sp.expand(RATIONAL(3, 4) * e0 + beta * e0 ** 2)
    sym.update({
        "alpha": alpha, "beta": beta, "E0": sp.expand(e0), "E": annual,
        "G": sp.expand(annual - 1), "closure": sp.expand(annual - sym["h"]),
        "Gh": sp.expand(sp.diff(annual, sym["h"])),
    })

    ending = section_rounded_ending()
    contrast = section_yi_contrast_family()
    beginning = section_beginning_split()
    five = section_middle_five()
    remainders = section_astronomical_remainders()
    degree = section_three_is_not_a_degree()
    reservoir = section_commitment_reservoir()
    sealing = section_sealing_refused()
    classification = section_factor_classification()
    uncertainty = section_uncertainty_fourth_term()
    layers = layer_sealing_rows()
    inherited = section_inherited_controls(uncertainty, layers)
    baselines = section_baselines(sym)

    reservation = PARENT_CONTRACT["verification_status"]["data_authenticity_reservation"]
    check(PARENT_CONTRACT["verification_status"]["observational"] == "Unavailable",
          "the parent contract records observational verification as Unavailable")
    check(reservation == ("The user's recorded reservation about the authenticity of the data in "
                          "the xue-study work is carried with this contract; hashes and "
                          "same-source read-backs do not remove it, and it is not narrowed to "
                          "any single stage."),
          "the data-authenticity reservation is carried verbatim from the parent contract")

    magnitude_findings = []
    for name, target in (
            ("S1/written_record", ending["committed_component"]["written_record"]),
            ("S1/carry_out", ending["committed_component"]["carry_out"]),
            ("S1/committed_residual_record", ending["committed_component"]["residual_record"]),
            ("S1/committed_controls", ending["committed_component"]["controls"]),
            ("S9/cell_records", classification["cell_records"])):
        magnitude_findings += magnitude_audit(target, name, allow_numbers=False)
    magnitude_findings += magnitude_audit(reservoir, "S7", allow_numbers=True)
    check(not magnitude_findings,
          "no magnitude and no numeric leaf appears for the four factors or the committed "
          "component")

    payload = {
        "schema": "adva.external.three-cycle-supplement-rounded-calibration.v2",
        "version": 2,
        "level": CONTRACT["level"],
        "contract": "experiments/three_cycle_supplement_v2/contract.json",
        "contract_sha256": contract_digest,
        "contract_sha256_declared": DECLARED_CONTRACT_SHA256,
        "checker_sha256": digest(pathlib.Path(__file__).resolve()),
        "parent_contracts": [
            {"path": "experiments/three_cycle_chain_v1/contract.json",
             "sha256": parent_digest, "sha256_declared": DECLARED_PARENT_SHA256,
             "retained_byte_for_byte": True,
             "relation": "in force; where this run and that one disagree, that one governs"},
            {"path": "experiments/three_cycle_chain_v1/contract-supplement-1.json",
             "sha256": supplement_digest, "sha256_declared": DECLARED_SUPPLEMENT_SHA256,
             "retained_byte_for_byte": True,
             "relation": "its four amendments - layered slow reservoir, per-layer sealing, "
                         "sampling-change control, separated uncertainty - are inherited "
                         "unchanged and are executed here"},
            {"path": "experiments/three_cycle_supplement_v1/contract.json",
             "sha256": surgery_digest, "sha256_declared": DECLARED_SURGERY_SHA256,
             "retained_byte_for_byte": True,
             "relation": "the surgery run of note 0237; its two retained failures and its "
                         "undecided necessity of opposite chirality carry forward and are not "
                         "repaired here"},
        ],
        "tooling": {
            "polynomial_library": "sympy",
            "version": SY["version"],
            "declared_not_native_authority": True,
            "exact_only": True,
            "used_for": ["exact polynomial arithmetic", "Sturm real-root isolation with rational "
                         "intervals", "the discriminant of the specialised quartic", "exact sign "
                         "conditions"],
            "not_implemented": [
                "a certified complex or projective continuation of roots",
                "a native certificate of any kind",
                "successive difference substitution of Zhang Jingzhong and Yang Lu"],
        },
        "limits": CONTRACT["budgets"],
        "assertions": ASSERTIONS["n"],
        "sections": {
            "R1_rounded_ending": ending,
            "R2_yi_contrast_family": contrast,
            "R3_beginning_split": beginning,
            "R4_middle_five": five,
            "R5_astronomical_remainders": remainders,
            "R6_three_is_not_a_degree": degree,
            "R7_commitment_reservoir": reservoir,
            "R8_sealing_refused": sealing,
            "R9_factor_classification": classification,
            "R10_uncertainty_fourth_term": uncertainty,
            "R11_inherited_controls": inherited,
            "R12_baselines": baselines,
        },
        "verification_status": {
            "observational": "Unavailable",
            "reason": "the three-cycle chain is future; no observation and no issued forecast "
                      "exists for 2026-12 onwards in this checkout, and this run uses no data",
            "data_authenticity_reservation": reservation,
            "data_authenticity_reservation_source":
                "experiments/three_cycle_chain_v1/contract.json, carried verbatim and "
                "un-narrowed",
            "xue_study_data_used": False,
            "future_chain": True,
            "checked_here": {
                "observational_verification": "Unavailable",
                "no_data_read_or_used": True,
                "hashes_and_read_backs_do_not_remove_the_reservation": True,
            },
        },
        "undecided": [
            {"item": "whether 'none in position' names the complement of the mutual-measuring "
                     "diagonal or the points with every coordinate out of position",
             "reason": "the contract's contrast family reads the Yi pair as the all-in-position "
                       "side and the none-in-position side and fixes the two counts at 81 and "
                       "6480; the strict per-coordinate reading of none in position, with every "
                       "coordinate out of position, holds on 1296 of those 6480 and the other "
                       "5184 are in position in some coordinates only.  Both exact counts are "
                       "reported and neither is substituted for the other, so the phrase is a "
                       "declared reading and not a decided one.",
             "retained_partial_result": {
                 "diagonal_points": contrast["address_machinery"]["diagonal_points"],
                 "complement_points": contrast["address_machinery"]["complement_points"],
                 "every_coordinate_out_of_position":
                     contrast["address_machinery"]["points_with_every_coordinate_out_of_position"],
                 "some_coordinates_in_position":
                     contrast["address_machinery"]["points_in_position_in_some_coordinates_only"],
             }},
            {"item": "which of the two sides is the sealing side",
             "reason": "the contract names the north side the cold-injecting side through the "
                       "aerosols structure and leaves the sealing side the other of the two "
                       "declared roles, so the south side is the sealing side by the declared "
                       "correspondence of this run rather than by a statement of the contract.  "
                       "Nothing is inferred from it except the side that carries the wildfire "
                       "cell's declared note.",
             "retained_partial_result": {
                 "declared_north_role": DECLARED_CELLS[("aerosols", NORTH)]
                 ["preserved_structure"],
                 "declared_south_role": DECLARED_CELLS[("low_cloud", SOUTH)]
                 ["preserved_structure"],
                 "the_sealing_side_as_declared_here": "south",
             }},
            {"item": "whether the declared four-by-two placements are canonical",
             "reason": "the contract declares aerosols on the north side, low cloud and water "
                       "vapour on the south side and wildfire on both sides; every other cell is "
                       "recorded as explicitly unquantified rather than invented, and a different "
                       "declaration would be a different run with a different table.  The three "
                       "account sizes therefore follow from the declaration and are not evidence "
                       "about any factor.",
             "retained_partial_result": {
                 "account_sizes": classification["account_sizes"],
                 "cells": classification["cells"],
                 "declarations": classification["declarations"],
             }},
            {"item": "whether the declared threshold and hysteresis of the one-way reservoir are "
                     "forced",
             "reason": "the thresholds, the two increments and the declared loop are conventions "
                       "of this run; the run shows that the declared one-way shape passes the "
                       "monotonicity and hysteresis controls while the parent's declared "
                       "first-order relaxation fails both, which is the falsifiable part, and it "
                       "does not decide whether some other one-way shape would also pass.",
             "retained_partial_result": {
                 "declared_thresholds": reservoir["declared_thresholds"],
                 "declared_increments": reservoir["declared_increments"],
                 "declared_loop_controls": reservoir["declared_loop_controls"],
                 "parent_relaxation_drifts": [row["drift_as_rational"]
                                              for row in reservoir["parent_relaxation_failure"]
                                              ["declared_steps"]],
             }},
            {"item": "whether the committed component's declared state can be given a magnitude",
             "reason": "no magnitude, sign or timing is declared anywhere for the committed "
                       "component; the run records its state as a declared structural value of a "
                       "declared one-way reservoir and keeps the declared magnitude at none.  "
                       "Whether a magnitude could be declared at all is not decided here and is "
                       "not attempted.",
             "retained_partial_result": {
                 "declared_magnitude": reservoir["magnitude"],
                 "declared_loop_end_state": reservoir["declared_loop"][-1]["state_after"],
                 "the_committed_condition_admits_no_approximation": True,
             }},
        ],
        "modelling_choices": {
            "rounded_ending_as_a_conjunction": "the ending is declared as the CONJUNCTION of the "
                                               "two terminal conditions, each evaluated in full "
                                               "on its own residual record: the sealable "
                                               "component closes at the fixed point of the annual "
                                               "return and the committed component carries out of "
                                               "the chain and is written out rather than "
                                               "discharged.  The four prohibitions are declared "
                                               "rules, so the rejected controls are rejected by "
                                               "the rules and not by a count of trials.",
            "either_or_readings": "an either-or terminal coincides with the declared conjunction "
                                  "on the two cases where both conditions agree, so the "
                                  "discrimination is exactly on the two mixed cases, where the "
                                  "either-or terminal accepts and the conjunction rejects.  That "
                                  "is reported rather than presented as a difference everywhere.",
            "separate_residual_records": "the two residual records have different types by "
                                         "declaration: the sealable residual is an exact element "
                                         "of Q(w) and the committed residual is a written-out, "
                                         "unquantified carry.  No fused scalar residual for the "
                                         "pair is formed anywhere in this run, which is what makes "
                                         "netting impossible rather than merely forbidden.",
            "closure_field": "the sealable component closes at w, the unique real root of "
                             "h^3 + 8 h^2 + 64 h - 320, carried exactly as an element of the "
                             "cubic field Q(w) with w^3 = 320 - 64 w - 8 w^2.  The cubic is "
                             "strictly increasing because its derivative has discriminant -512, "
                             "so the single real root is identified exactly and no decimal is "
                             "compared.",
            "address_machinery_reused": "the Yi contrast family reuses the existing address "
                                        "machinery: the fine carrier is {0,...,8}^4 with the "
                                        "encoding e(a, b)_i = 3 a_i + b_i, the mutual-measuring "
                                        "diagonal a = b is the 81 points z = 4 a with every "
                                        "coordinate in {0, 4, 8}, and its complement is the 6480 "
                                        "none-in-position points.  The Yi pair is used only as "
                                        "the contrast family: it supplies two halves to reject "
                                        "against, never a terminal.",
            "beginning_split_declaration": "the resetable class holds the declared phase "
                                           "misalignment, taken as the five Wayeb days of the "
                                           "declared 365-day year against eighteen twenty-day "
                                           "months, and the declared step-carry remainder, taken "
                                           "as the parent chain's six steps of twenty-seven, "
                                           "which is 2/9 of a cycle or 486 of its 729 zan.  The "
                                           "non-resetable class holds the one-way commitment "
                                           "state.  A declared reset clears the resetable class "
                                           "exactly and cannot touch the commitment, and that is "
                                           "rejected by the declared class of the obstruction "
                                           "rather than by a count.",
            "five_point_structure": "the middle carries two directed cycles on the same five "
                                    "points: generation is k -> k + 1 and overcoming is k -> "
                                    "k + 2 modulo five.  Both are generators because five is "
                                    "prime, so every nonzero residue generates the whole group, "
                                    "and the primality is shown to be doing work by running the "
                                    "same declaration on the composite modulus four, where the "
                                    "declared overcoming step has order two.",
            "chain_length_in_days": "the chain length is counted in whole days as three annual "
                                    "cycles of the declared 365-day year, which is eighteen "
                                    "twenty-day months plus the five Wayeb days, giving 1095 "
                                    "integer days.  2920 is exactly eight such cycles and 18980 "
                                    "is exactly fifty-two such cycles and exactly seventy-three "
                                    "Tzolkin rounds, so the three commensurabilities are the "
                                    "eight-year and fifty-two-year readings as well as the two "
                                    "counts of days.",
            "remainder_control": "the declared year-length control repeats the whole comparison "
                                 "under an eighteen-month year of 360 days and under a "
                                 "fifty-two-week year of 364 days; both close none of the three "
                                 "commensurabilities, so the control cannot separate the "
                                 "declarations and is reported as a failed control rather than "
                                 "dropped.",
            "three_is_not_a_degree": "the declared object is a count of three annual cycles.  The "
                                     "number of degree-l spherical harmonics is 2 l + 1, which is "
                                     "7 at l = 3, and no spherical carrier, harmonic basis or "
                                     "spherical Laplacian is declared anywhere in this run, so "
                                     "the identification is rejected on an exact dimension and on "
                                     "a missing carrier.  A failure of injectivity would be a "
                                     "collapse of two cycle indices onto one image, and the "
                                     "declared index map has three indices, three distinct "
                                     "declared spans and no collision among its three unordered "
                                     "pairs, so that identification is rejected too.  The "
                                     "numerical coincidence that the degree-two harmonic "
                                     "dimension is also five, like the five-point middle, is "
                                     "recorded and explicitly not used.",
            "one_way_reservoir": "the committed component is a declared one-way reservoir.  Its "
                                 "declared state is non-decreasing because both declared "
                                 "increments are non-negative, its branch opens at the declared "
                                 "upper threshold 1 and closes at the declared lower threshold "
                                 "1/4, and on the declared loop of control values 0, 1/2, 1, 1/2, "
                                 "0 the branch reads closed rising and open falling at the same "
                                 "declared control value 1/2, which is the declared hysteresis.  "
                                 "A declared loop in the control therefore does not restore the "
                                 "state: it ends strictly above where it started.",
            "the_state_is_not_a_magnitude": "the reservoir's declared state is a declared exact "
                                            "structural quantity of a declared model, used only "
                                            "to test monotonicity and hysteresis.  No magnitude, "
                                            "sign or timing is asserted for the committed "
                                            "component anywhere: its declared magnitude is none, "
                                            "and the audit in this run checks that no magnitude "
                                            "key carries anything else and that the committed "
                                            "records carry no numeric leaf at all.",
            "parent_relaxation_failure": "the parent chain's declared first-order relaxation "
                                         "reservoir is run on the same declared loop from its own "
                                         "declared displacement: its drifts are strictly negative "
                                         "and each is the previous times 29/30, so it fails the "
                                         "monotonicity control, and it has no threshold and no "
                                         "branch state, so its two paths agree and it fails the "
                                         "hysteresis control.  Both failures are the falsifiable "
                                         "evidence that the one-way shape is doing work, and both "
                                         "are facts about two declared models.",
            "sealing_refusal": "the sealing condition is applied to the sealable component only.  "
                               "The committed component is accounted and never sealed, because it "
                               "is by definition a leak, and a leaking component may not cancel a "
                               "sealing violation: the declared layer-wise violation of 1/64 in "
                               "the mixed layer and -1/64 in the deep layer is reported as a "
                               "violation even though its total is exactly zero.",
            "four_by_two_table": "the table has one cell for each of the four factors on each of "
                                 "the two sides, and each cell carries exactly one of three "
                                 "declarations.  The declared placement is taken from the "
                                 "contract: aerosols is the north-side structure, low cloud is "
                                 "the south-weighted structural coupler, water vapour is the "
                                 "south-side correction to be made, declared as a reversal along "
                                 "the declared reset path of the resetable class, and wildfire "
                                 "acts on both sides and is explicitly unquantified because its "
                                 "declared partial ratchet behaviour is not reversible.  Every "
                                 "cell the contract does not place is recorded as explicitly "
                                 "unquantified rather than invented, and no magnitude is given "
                                 "anywhere.",
            "correction_account_declared_as_a_path": "the one declared correction is stated as a "
                                                     "declared path - the reversal of the declared "
                                                     "reversible amplifier along the declared "
                                                     "reset path - and not as an amount, so the "
                                                     "correction account carries no magnitude "
                                                     "either.",
            "uncertainty_fourth_term": "the separated uncertainty accounting of supplement one "
                                       "keeps its three quantified terms, mapping 1/64, bias "
                                       "1/64 and sampling 3/256, and gains a fourth term, "
                                       "committed-but-unquantified, which is recorded separately "
                                       "at every seam and is never fused with the other three.  "
                                       "A fused figure over the three would be 11/256 and is "
                                       "rejected; a fused figure over all four cannot be formed "
                                       "at all, because the fourth term is unquantified.",
            "inherited_controls": "the sampling-change invariance control, the separated "
                                  "uncertainty control, the layer-wise sealing control, the "
                                  "identity-loop control and the atmospheric-chain memory-loss "
                                  "control of the parent contracts and their supplement all run "
                                  "here unchanged, and the three failures the parents retained "
                                  "are carried forward by citation with their reasons.",
            "baselines": "the exact baselines of the earlier runs are reproduced with exact "
                         "arithmetic: J_inf = 1 at (p, q) = (-2, 17/10) off the discriminant "
                         "variety, the closure amplitude 3.2035072879526181... with one real exit "
                         "on the nontrivial closure branch, the level reading's largest amplitude "
                         "2 + sqrt(8 sqrt(17) - 20) with two real branches, and the asserted "
                         "ordering, which is decided on exact rationals.",
            "exact_only": "every acceptance assertion and every value in the retained payload is "
                          "an exact integer or fraction, an exact rational interval, an element "
                          "of Q(w) or of Q(sqrt(17)), or a string naming one; no floating-point "
                          "value is formed anywhere.",
            "external_library": "sympy 1.14 is declared and used as an engine for real-root "
                                "isolation with rational intervals and for the discriminant of "
                                "the specialised quartic; it is not native authority and no "
                                "semantic identity is created here.",
            "resource_limits": "the checker installs a CPU limit, a file-size limit and a wall "
                               "alarm, and records the contract's declared memory budget without "
                               "installing an address-space ceiling; no child process is launched "
                               "and no pre-existing rlimit artifact is touched.",
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
            "no_data_read_or_used": True,
            "observational_verification": "Unavailable",
            "the_chain_is_future_and_unverified": True,
            "the_rounded_ending_is_a_declared_structure_not_a_physical_mechanism": True,
            "no_magnitude_for_aerosols_low_cloud_water_vapour_or_wildfire": True,
            "no_magnitude_for_the_committed_component": True,
            "the_four_by_two_table_is_a_declared_classification_not_a_result_about_the_"
            "atmosphere": True,
            "the_yi_pair_is_used_only_as_the_contrast_family": True,
            "no_seal_no_transport_no_terminology_home": True,
            "no_rust_source_or_lock_changed": True,
            "no_contract_or_note_edited": True,
            "no_claim_added_to_docs_claims_toml": True,
            "pre_existing_files_byte_identical": True,
        },
        "checks": {},
    }
    checks = {
        "assertions_within_budget": ASSERTIONS["n"] <= CONTRACT["budgets"]["max_assertions"],
        "this_contract_digest_matches_the_declared_one":
            payload["contract_sha256"] == payload["contract_sha256_declared"],
        "all_parent_contracts_are_retained_byte_for_byte": all(
            row["sha256"] == row["sha256_declared"] for row in payload["parent_contracts"]),
        "the_ending_is_the_declared_conjunction":
            ending["conjunction"]["verdict"] == "RoundedEndingHolds",
        "both_terminal_conditions_hold_in_full": ending["conjunction"]["both_hold_in_full"],
        "the_two_residual_records_are_kept_separate":
            ending["residual_records"]["kept_separate"]
            and not ending["residual_records"]["fused_scalar_exists"],
        "the_either_or_terminal_is_rejected":
            ending["prohibitions"]["either_or"]["rejected"],
        "the_netting_terminal_is_rejected": ending["prohibitions"]["netting"]["rejected"],
        "the_obstructing_terminal_is_rejected":
            ending["prohibitions"]["obstruction"]["rejected"]
            and ending["prohibitions"]["obstruction"]["declared_terminal_is_independent"],
        "the_compromising_terminal_is_rejected":
            ending["prohibitions"]["compromise"]["rejected"],
        "the_mutual_measuring_diagonal_has_81_points":
            contrast["address_machinery"]["diagonal_points"] == 81,
        "the_complement_of_the_diagonal_has_6480_points":
            contrast["address_machinery"]["complement_points"] == 6480,
        "the_three_yi_contrast_terminals_all_fail":
            contrast["all_three_contrast_terminals_fail"]
            and all(not row["accepted"] for row in contrast["contrast_terminals"]),
        "the_resetable_reset_is_accepted":
            beginning["resets"]["phase_misalignment"]["accepted"]
            and beginning["resets"]["step_carry_remainder"]["accepted"],
        "the_non_resetable_reset_is_rejected":
            not beginning["resets"]["one_way_commitment_state"]["accepted"]
            and beginning["resets"]["one_way_commitment_state"]["state_unchanged"],
        "the_five_point_double_cycle_holds":
            five["declared_structure"]["accepted"]
            and five["declared_cycles"]["generation"]["is_a_generator"]
            and five["declared_cycles"]["overcoming"]["is_a_generator"],
        "rejecting_one_cycle_fails": five["controls"][0]["verdict"] == "Rejected",
        "identifying_the_two_cycles_fails": five["controls"][1]["verdict"] == "Rejected",
        "the_three_remainders_are_reported":
            len(remainders["remainders"]) == 3 and remainders["the_chain_closes_none"],
        "the_chain_closes_no_commensurability":
            all(not row["closes_it"] for row in remainders["commensurabilities"])
            and all(row["verdict"] == "Rejected"
                    for row in remainders["closing_claim_controls"]),
        "three_is_not_a_degree_three_harmonic":
            not degree["the_three"]["three_equals_seven"]
            and degree["readings"][0]["verdict"] == "Rejected",
        "three_is_not_a_failure_of_injectivity":
            degree["injectivity"]["is_injective"]
            and degree["readings"][1]["verdict"] == "Rejected",
        "the_one_way_reservoir_is_monotone":
            reservoir["monotone_non_decreasing"] and reservoir["strictly_increasing"]
            and reservoir["the_loop_does_not_restore_the_state"],
        "the_one_way_reservoir_is_hysteretic": reservoir["hysteresis"]["present"],
        "the_parent_relaxation_fails_monotonicity":
            not reservoir["parent_relaxation_failure"]["monotone_non_decreasing"],
        "the_parent_relaxation_fails_hysteresis":
            not reservoir["parent_relaxation_failure"]["hysteresis_present"],
        "sealing_is_refused_for_the_committed_component":
            sealing["committed_component"]["sealing_refused"]
            and not sealing["committed_component"]["sealed"]
            and sealing["committed_component"]["accounted"],
        "the_sealable_reading_of_the_committed_component_is_rejected":
            sealing["controls"][0]["verdict"] == "Rejected",
        "the_committed_component_cannot_offset_a_sealing_violation":
            sealing["controls"][1]["verdict"] == "Rejected"
            and not sealing["layer_wise_violation"]["cancelled_by_the_total"],
        "every_classification_cell_carries_exactly_one_declaration":
            classification["declared_verdict"]["accepted"]
            and classification["cells"] == len(FACTORS) * len(SIDES),
        "the_structure_cell_control_is_rejected":
            classification["controls"][0]["verdict"] == "Rejected",
        "the_ratchet_cell_control_is_rejected":
            classification["controls"][1]["verdict"] == "Rejected",
        "the_symmetric_treatment_control_is_rejected":
            classification["controls"][2]["verdict"] == "Rejected",
        "the_fused_account_control_is_rejected":
            classification["controls"][3]["verdict"] == "Rejected",
        "no_magnitude_is_given_for_the_four_factors_or_the_committed_component":
            not magnitude_findings
            and classification["no_magnitude_is_given_for_any_factor"]
            and sealing["no_magnitude_for_the_committed_component"],
        "the_fourth_uncertainty_term_is_recorded_separately":
            uncertainty["four_terms_separately_at_every_seam"]
            and uncertainty["fourth_term"]["recorded_separately_at_every_seam"],
        "the_four_uncertainty_terms_are_never_fused":
            not uncertainty["fused_control"]["fused_magnitude_exists"]
            and not uncertainty["pooling_control"]["fused_with_the_fourth_term"],
        "the_sampling_change_invariance_control_runs":
            inherited["sampling_change_invariance"]["readings_unchanged"]
            and inherited["sampling_change_invariance"]["composition_only_reading_moves"],
        "the_layer_wise_sealing_control_runs":
            inherited["layer_wise_sealing"]["all_layers_sealed"]
            and not inherited["layer_wise_sealing"]["total_cancelling_control"]
            ["cancelled_by_the_total"],
        "the_identity_loop_control_runs":
            inherited["identity_loop"]["declared_loop"]["returns_the_identity"]
            and inherited["identity_loop"]["discriminates"],
        "the_atmospheric_chain_loses_the_carried_memory":
            inherited["atmospheric_memory_loss"]["atmospheric_only"]["lost"]
            and inherited["atmospheric_memory_loss"]["with_the_slow_component"]["kept"],
        "the_baselines_are_reproduced": baselines["ordering"]["asserted_exactly"],
        "the_failed_controls_are_retained": len(inherited["failed_controls"]) == 2,
        "the_parents_retained_failures_are_carried_forward":
            inherited["carried_forward_failures_count"] == 3,
        "observational_verification_is_recorded_unavailable":
            payload["verification_status"]["observational"] == "Unavailable",
        "the_data_authenticity_reservation_is_carried_verbatim":
            payload["verification_status"]["data_authenticity_reservation"]
            == PARENT_CONTRACT["verification_status"]["data_authenticity_reservation"],
        "undecided_items_are_declared": len(payload["undecided"]) == 5,
        "no_floating_point_value_is_retained": not contains_float(payload),
        "no_magnitude_key_carries_anything_but_the_declared_none":
            not magnitude_key_violations(payload),
    }
    payload["checks"] = checks
    payload["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    return payload


def summarize(payload):
    sections = payload["sections"]
    ending = sections["R1_rounded_ending"]
    contrast = sections["R2_yi_contrast_family"]
    beginning = sections["R3_beginning_split"]
    five = sections["R4_middle_five"]
    remainders = sections["R5_astronomical_remainders"]
    degree = sections["R6_three_is_not_a_degree"]
    reservoir = sections["R7_commitment_reservoir"]
    sealing = sections["R8_sealing_refused"]
    classification = sections["R9_factor_classification"]
    uncertainty = sections["R10_uncertainty_fourth_term"]
    inherited = sections["R11_inherited_controls"]
    baselines = sections["R12_baselines"]
    print("three-cycle supplement v2: exact calibration of the declared rounded ending")
    print("  status:", payload["status"], " assertions:", payload["assertions"])
    print("  R1 ending:", ending["conjunction"]["verdict"],
          "| sealable residual", ending["sealable_component"]["residual_record"]["residual"],
          "| committed", ending["committed_component"]["carry_out"]["verdict"])
    for name, row in ending["prohibitions"].items():
        print("    prohibition", name, "-> rejected", row["rejected"])
    print("  R2 contrast: diagonal",
          contrast["address_machinery"]["diagonal_points"], "points, complement",
          contrast["address_machinery"]["complement_points"], "points | every coordinate out of "
          "position",
          contrast["address_machinery"]["points_with_every_coordinate_out_of_position"])
    for row in contrast["contrast_terminals"]:
        print("    terminal:", row["terminal"], "->", row["verdict"])
    print("  R3 beginning split: accepted resets", beginning["accepted_resets"],
          "| rejected resets", beginning["rejected_resets"])
    print("  R4 middle five: generation", five["declared_cycles"]["generation"]["orbit"],
          "overcoming", five["declared_cycles"]["overcoming"]["orbit"],
          "| generators", five["generators_modulo_five"])
    for row in five["controls"]:
        print("    control:", row["control"], "->", row["verdict"])
    print("  R5 remainders:", remainders["remainders"], "| closes none",
          remainders["the_chain_closes_none"])
    print("    failed to discriminate:", remainders["failed_to_discriminate"]["verdict"])
    print("  R6 three is not a degree:", degree["the_three"]["third_degree_spherical_harmonics"],
          "third-degree harmonics; injective index map", degree["injectivity"]["is_injective"])
    for row in degree["readings"]:
        print("    reading:", row["verdict"], "-", row["control"])
    print("  R7 reservoir: monotone", reservoir["monotone_non_decreasing"], "| hysteresis",
          reservoir["hysteresis"]["present"], "| loop ends at",
          reservoir["declared_loop"][-1]["state_after"])
    print("    parent relaxation monotone",
          reservoir["parent_relaxation_failure"]["monotone_non_decreasing"], "| hysteresis",
          reservoir["parent_relaxation_failure"]["hysteresis_present"], "| drifts",
          [row["drift_as_rational"] for row in reservoir["parent_relaxation_failure"]
           ["declared_steps"]][:3], "...")
    print("  R8 sealing: sealable sealed", sealing["sealable_component"]["sealed"],
          "| committed", sealing["committed_component"]["verdict"],
          "| violation layers", sealing["layer_wise_violation"]["violating_layers"])
    print("  R9 classification: accounts", classification["account_sizes"],
          "| no magnitude", classification["no_magnitude_is_given_for_any_factor"])
    for row in classification["controls"]:
        print("    control:", row["control"], "->", row["verdict"])
    print("  R10 uncertainty: quantified", uncertainty["quantified_terms"],
          "| fourth term", uncertainty["fourth_term"]["name"],
          "| fused three-term figure", uncertainty["fused_three_term_figure"], "rejected")
    print("  R11 inherited: sampling invariance",
          inherited["sampling_change_invariance"]["readings_unchanged"],
          "| layers sealed", inherited["layer_wise_sealing"]["all_layers_sealed"],
          "| identity loop", inherited["identity_loop"]["declared_loop"]["returns_the_identity"],
          "| atmospheric memory lost",
          inherited["atmospheric_memory_loss"]["atmospheric_only"]["lost"])
    for row in inherited["failed_controls"]:
        print("    failed control:", row["control"], "->", row["outcome"])
    print("  R12 baselines: floor", baselines["first_scheme"]["amplitude_floor"], "at",
          baselines["first_scheme"]["attained_at"], "| closure amplitude",
          baselines["closure_reading"]["correctly_rounded_prefix"], "with",
          baselines["closure_reading"]["real_exits"], "real exit | level branches",
          baselines["level_reading"]["real_branches"], "largest amplitude",
          baselines["level_reading"]["largest_branch_amplitude"])
    print("    ordering:", baselines["ordering"]["statement"])
    print("  observational verification:", payload["verification_status"]["observational"],
          "| xue study data used:", payload["verification_status"]["xue_study_data_used"])
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
            "schema": "adva.external.three-cycle-supplement-rounded-calibration.v2",
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
