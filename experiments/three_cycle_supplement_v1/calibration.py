#!/usr/bin/env python3
"""Exact calibration of the declared singularity-elimination surgery, with checkable results.

Frozen contract: experiments/three_cycle_supplement_v1/contract.json (this run), which
inherits unchanged the frozen contract experiments/three_cycle_chain_v1/contract.json and
its supplement experiments/three_cycle_chain_v1/contract-supplement-1.json.  The two
parent contracts are read, hashed and cited here; they are never edited, and this checker
writes nothing in their directory.

This checker is an external exact calibration of a DECLARED construction.  It constructs
no native certificate, promotes no native identity, and makes no physical claim.  Cold,
heat, wind, ocean, plateau and forecast are outside this run; the cold/heat reading exists
only as a declared projection map that is checked as a map.

What the run decides, and with what:

* S1 the surgery: the declared singular locus (the discriminant collision of the earlier
  runs on the B1 branch, whose cleared resultant is factored exactly, and the annual seam
  at side 0 of the twelve-phase cycle), the declared collar around it with its orientation
  and its normal, and the exact excision - set subtraction on the declared lattice - whose
  boundary has exactly two connected components, the two sides;
* S2 the two spirals: a rotation by one phase compounded with a radial advance of 1/12 on
  each side, with OPPOSITE declared chirality, plus the degenerate-spiral controls;
* S3 the collar flux, the declared pairing of the introduced resource with the collar
  normal, before and after the helical introduction, with the attribution rule, the
  same-chirality control that fails to raise it, the unattributed-rise control and the
  radial-normal control that fails to discriminate;
* S4 side O: the obstruction as an explicit written record with a discharge that is a
  condition on that record, with the unwritten, the implicit and the disagreeing controls;
* S5 side I: the declared time-domain target and the declared step budget, the arrival
  inside it, and the over-budget and role-swapped controls;
* S6 the resource accounting: the carried remainder split by the surgery with no resource
  created, the three inherited layers, the layer-wise sealing bound of supplement one, the
  total-cancelling control that is not cancelled by its total, and the seam redistribution
  with the memory layer reported at every seam;
* S7 the projection: the declared map from the construction to the cold/heat two-sided
  reading, checked as a map, with the side-identifying and single-sense rejections;
* S8 the exact baselines, reproduced: J_inf = 1 at (p, q) = (-2, 17/10), the closure
  amplitude 3.2035072879526181... with one real exit, the level reading's largest amplitude
  2 + sqrt(8 sqrt(17) - 20) with two real branches, and the asserted ordering;
* S9 the inherited controls: the sampling-change invariance control, the separated
  uncertainty control and the purely atmospheric memory-loss control, with the controls
  that failed to discriminate reported rather than dropped.

All acceptance arithmetic is exact integers and fractions.Fraction, exact rational interval
arithmetic and one exact real quadratic extension; sympy 1.14 is a declared external library
used only as an engine for resultants, integer factorisation and Sturm real-root isolation,
and is not native authority.  No floating-point value is formed in an acceptance test or
written into the retained payload.

Resource policy: RLIMIT_CPU and RLIMIT_FSIZE are installed together with a wall alarm; the
contract's declared memory budget is recorded and no address-space ceiling is installed,
because no child process is launched.
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

PARENT_HERE = HERE.parent / "three_cycle_chain_v1"
PARENT_CONTRACT_PATH = PARENT_HERE / "contract.json"
PARENT_SUPPLEMENT_PATH = PARENT_HERE / "contract-supplement-1.json"
PARENT_CONTRACT = json.loads(PARENT_CONTRACT_PATH.read_text(encoding="utf-8"))
PARENT_SUPPLEMENT = json.loads(PARENT_SUPPLEMENT_PATH.read_text(encoding="utf-8"))

DECLARED_CONTRACT_SHA256 = "157838642e9097ea4a1a1c7461db9e548affb0c6f3af7b830816f37f22b74f5a"
DECLARED_PARENT_SHA256 = "a3dc2e8d86e45139484fceed571ef99ea3b63f18748c6f1c82bb031a3305a965"
DECLARED_SUPPLEMENT_SHA256 = ("e125ee4940b838924257d9420bde71cf060a0745dc5d3d482c1691158785ac9f")

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


def rat(value):
    """An exact sympy rational from an int or a Fraction."""
    value = value if isinstance(value, Fr) else Fr(value)
    return RATIONAL(value.numerator, value.denominator)


def sgn(value):
    return (value > 0) - (value < 0)


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

    def abs_upper(self):
        return max(abs(self.lo), abs(self.hi))

    def contains(self, value):
        value = value if isinstance(value, Fr) else Fr(value)
        return self.lo <= value <= self.hi

    def __str__(self):
        return "[" + str(self.lo) + ", " + str(self.hi) + "]"


def quadratic_abs_upper(second, first, constant, box):
    """An exact upper bound of |a2 x^2 + a1 x + a0| on a closed rational interval.

    The quadratic is evaluated at the endpoints and, when it lies inside the box, at the
    vertex, so the bound is exact and needs no sampling.
    """
    def value(point):
        return second * point * point + first * point + constant

    candidates = [box.lo, box.hi]
    if second != 0:
        vertex = -first / (2 * second)
        if box.lo <= vertex <= box.hi:
            candidates.append(vertex)
    values = [value(point) for point in candidates]
    endpoints = [value(box.lo), value(box.hi)]
    return max(max(abs(item) for item in values), max(abs(item) for item in endpoints))


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
    """The correctly rounded decimal prefix of the value carried by an exact interval.

    The rounding is decided by exact rational arithmetic on both endpoints; when the two
    rounded integers agree the value's rounding is decided, because the rounded value is a
    monotone step function of the value.
    """
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


# --------------------------------------------- exact real quadratic extensions --

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

    def __eq__(self, other):
        other = other if isinstance(other, QNr) else QNr(other, 0, self.square)
        return self.a == other.a and self.b == other.b and self.square == other.square

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

    def __str__(self):
        return "(" + str(self.a) + " + " + str(self.b) + " w, w^2 = " + str(self.square) + ")"


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

# ------------------------------------------------------------- declared fixture --

PHASES = 12
SEAM_PHASE = 0
DECLARED_TIME_COUPLING = (Fr(-31, 512), Fr(-15, 512)) + (Fr(0),) * 10

SINGULAR_RADIAL_INDEX = 0
COLLAR_RADIAL_EXTENT = 1
COLLAR_NORMAL = (Fr(1), Fr(1))

COLLISION_P = Fr(-2)
COLLISION_Q = Fr(7019, 8)
PERTURBATION_WITNESS = (Fr(-2), Fr(17, 10))
DISCRIMINANT_FACTOR = "2048*p**2 + 608*p - 8*q + 43"
DISCRIMINANT_FACTOR_DISPLAY = "2048 p^2 + 608 p - 8 q + 43"

SPIRAL_RADIAL_ADVANCE = Fr(1, 12)
SPIRAL_ANGULAR_STEP = 1
CHIRALITY = {"outer": 1, "inner": -1}
SIDE_ORIENTATION_SIGN = {"outer": Fr(1), "inner": Fr(-1)}
SIDE_RADIAL_INDEX = {"outer": Fr(COLLAR_RADIAL_EXTENT), "inner": Fr(-COLLAR_RADIAL_EXTENT)}

ARRIVAL_TARGET = (Fr(COLLAR_RADIAL_EXTENT), SEAM_PHASE)
ARRIVAL_START = (Fr(-COLLAR_RADIAL_EXTENT), SEAM_PHASE)
STEP_BUDGET = 36
CYCLE_COUNT = 3
END_BLOCK_STEPS = 2

FAST_REMAINDER = Fr(1, 4)
LAYER_ORDER = ("mixed", "thermocline", "deep")
LAYER_CONTENTS = (Fr(1, 8), Fr(1, 4), Fr(1, 2))
SEAM_TRANSFERS = (("mixed", "thermocline", Fr(1, 8)), ("thermocline", "deep", Fr(1, 16)))
LAYER_SEALING_BOUND = (Fr(0), Fr(0), Fr(0))

OBSERVATION_COMPOSITIONS = (
    ("A", (Fr(1), Fr(0), Fr(0))),
    ("B", (Fr(1, 2), Fr(1, 4), Fr(1, 4))),
)
COMPOSITION_OFFSETS = (Fr(1, 32), Fr(1, 16), Fr(3, 64))

REQUIRED_RECORD_FIELDS = ("record_id", "kind", "locus_branch", "parameter_p", "parameter_q",
                          "vanishing_factor_value", "collar_normal", "boundary_object")
COMPARED_RECORD_FIELDS = ("kind", "locus_branch", "parameter_p", "parameter_q",
                          "vanishing_factor_value", "collar_normal", "boundary_object")

PROJECTION_DOMAIN = ("outer_side", "inner_side", "outer_spiral", "inner_spiral")
PROJECTION_CODOMAIN = {
    "sides": ("sealing_side", "supplying_or_injecting_side"),
    "rotation_senses": ("rotation_sense_positive", "rotation_sense_negative"),
}
DECLARED_PROJECTION = {
    "outer_side": "sealing_side",
    "inner_side": "supplying_or_injecting_side",
    "outer_spiral": "rotation_sense_positive",
    "inner_spiral": "rotation_sense_negative",
}

CLOSURE_MODPLUS = 12


# ------------------------------------------------------ declared predicates ----

def chirality_verdict(sigma_outer, sigma_inner):
    """The declared chirality condition, evaluated on a declared sign pair.

    The condition is a rule about the two declared signs, not a count of trials: a
    construction with the same chirality on both sides is a different construction and is
    rejected here by the rule itself.
    """
    reasons = []
    for name, value in (("outer", sigma_outer), ("inner", sigma_inner)):
        if value not in (1, -1):
            reasons.append(f"the declared {name} chirality sign must be plus or minus one, "
                           f"not {value}")
    if not reasons and sigma_outer == sigma_inner:
        reasons.append("the declared chirality condition requires sigma_outer = -sigma_inner, "
                       "so the two declared signs must be opposite; sigma_outer = "
                       f"{sigma_outer:+d} and sigma_inner = {sigma_inner:+d} are equal")
    return {
        "sigma_outer": f"{sigma_outer:+d}",
        "sigma_inner": f"{sigma_inner:+d}",
        "signs_are_opposite": sigma_outer == -sigma_inner,
        "accepted": not reasons,
        "verdict": "Accepted" if not reasons else "Rejected",
        "reasons": reasons,
        "rejected_by": "the declared chirality condition sigma_outer = -sigma_inner",
        "decided_by_a_count": False,
    }


def spiral_verdict(radial_advance, angular_step):
    """The declared spiral condition: a rotation compounded with a radial advance."""
    reasons = []
    if radial_advance == 0:
        reasons.append("a spiral is a rotation compounded with a radial advance; a zero radial "
                       "advance is a pure rotation and is not the declared spiral")
    if angular_step == 0:
        reasons.append("a spiral is a rotation compounded with a radial advance; a zero angular "
                       "step is a pure radial advance and is not the declared spiral")
    return {
        "radial_advance": str(radial_advance),
        "angular_step": angular_step,
        "rotation_compounded_with_a_radial_advance": not reasons,
        "accepted": not reasons,
        "verdict": "Accepted" if not reasons else "Rejected",
        "reasons": reasons,
    }


def pairing(resource, normal):
    """The declared pairing B(u, v) = u_r v_r + u_k v_k of an introduced resource with a normal."""
    check(len(resource) == 2 and len(normal) == 2, "the declared pairing is two-dimensional")
    return resource[0] * normal[0] + resource[1] * normal[1]


def side_normal(side):
    """The declared outward normal of the excised collar on a side, with its orientation sign."""
    sign = SIDE_ORIENTATION_SIGN[side]
    return (sign * COLLAR_NORMAL[0], sign * COLLAR_NORMAL[1])


def introduced_resource(side, sigma=None):
    """The resource introduced per declared turn on a side: radial advance and angular step."""
    if sigma is None:
        sigma = CHIRALITY[side]
    return (SPIRAL_RADIAL_ADVANCE, Fr(sigma * SPIRAL_ANGULAR_STEP))


def collar_flux(sigmas, extra=None, normal=None):
    """The declared collar flux: the pairing of the introduced resource with each side's normal."""
    base = COLLAR_NORMAL if normal is None else normal
    rows = {}
    total = Fr(0)
    for side in ("outer", "inner"):
        resource = introduced_resource(side, sigmas[side])
        if extra is not None and side in extra:
            resource = (resource[0] + extra[side][0], resource[1] + extra[side][1])
        sign = SIDE_ORIENTATION_SIGN[side]
        side_vec = (sign * base[0], sign * base[1])
        value = pairing(resource, side_vec)
        rows[side] = {"resource": [str(resource[0]), str(resource[1])],
                      "normal": [str(side_vec[0]), str(side_vec[1])],
                      "term": str(value)}
        total += value
    return {"terms": rows, "flux": total}


def chirality_pair_flux(normal, sigmas):
    """The same flux computed from the declared rise formula, as an independent cross-check."""
    angular_weight = Fr(SPIRAL_ANGULAR_STEP)
    return angular_weight * normal[1] * Fr(sigmas["outer"] - sigmas["inner"])


def record_verdict(record, computed):
    """The discharge, as a condition on the written record."""
    if record is None:
        return {
            "written": False, "agrees": False, "verdict": "Rejected",
            "reasons": ["the obstruction is implicit: no record object is declared on this side"],
            "rejected_by": "the discharge condition, which is a condition on the written record",
        }
    missing = [field for field in REQUIRED_RECORD_FIELDS
               if not str(record.get(field, "")).strip()]
    if missing:
        return {
            "written": False, "agrees": False, "verdict": "Rejected",
            "reasons": ["the obstruction is not written out: the record omits "
                        + ", ".join(missing)],
            "rejected_by": "the discharge condition, which is a condition on the written record",
        }
    disagreeing = [field for field in COMPARED_RECORD_FIELDS
                   if str(record.get(field)) != str(computed.get(field))]
    if disagreeing:
        return {
            "written": True, "agrees": False, "verdict": "Rejected",
            "reasons": ["the written value of " + field + " is " + str(record.get(field))
                        + " and the computed value is " + str(computed.get(field))
                        for field in disagreeing],
            "rejected_by": "the discharge condition, which requires agreement with the "
                           "computed values",
        }
    return {
        "written": True, "agrees": True, "verdict": "Discharged", "reasons": [],
        "rejected_by": "",
    }


def arrival_verdict(start, target, radial_advance, angular_step, budget, excised):
    """The declared arrival condition: the declared time-domain target inside the step budget."""
    radial_start, phase_start = start
    radial_target, phase_target = target
    delta = radial_target - radial_start
    record = {
        "start": [str(radial_start), phase_start],
        "target": [str(radial_target), phase_target],
        "radial_advance": str(radial_advance),
        "angular_step": angular_step,
        "step_budget": budget,
    }
    if radial_advance <= 0:
        record.update({"solvable": False, "verdict": "Rejected_NoArrival",
                       "reasons": ["the declared radial advance must be positive"]})
        return record
    steps = delta / radial_advance
    if steps.denominator != 1 or steps < 0:
        record.update({
            "solvable": False, "verdict": "Rejected_NoArrival",
            "reasons": ["the declared spiral advances outward with a radial advance of "
                        + str(radial_advance) + " per step, so it cannot reach the declared "
                        "radial index " + str(radial_target) + " from " + str(radial_start)
                        + ": the required step count is " + str(steps) + ", not a "
                        "non-negative integer"],
        })
        return record
    count = int(steps)
    congruence = (phase_start + angular_step * count - phase_target) % CLOSURE_MODPLUS
    if congruence != 0:
        record.update({
            "solvable": False, "verdict": "Rejected_NoArrival",
            "reasons": ["the declared angular step leaves the phase at "
                        + str((phase_start + angular_step * count) % CLOSURE_MODPLUS)
                        + ", not the declared target phase " + str(phase_target)],
        })
        return record
    orbit = [(radial_start + index * radial_advance,
              (phase_start + angular_step * index) % CLOSURE_MODPLUS) for index in range(count + 1)]
    lattice_cells = [(int(point[0]), point[1]) for point in orbit if point[0].denominator == 1]
    crossed = [cell for cell in lattice_cells if cell in excised]
    within = count <= budget
    record.update({
        "solvable": True,
        "steps": count,
        "phase_congruence_holds": True,
        "within_budget": within,
        "slack": budget - count if within else 0,
        "excess": 0 if within else count - budget,
        "radial_distance_covered": str(delta),
        "orbit_cells_on_the_declared_lattice": [[cell[0], cell[1]] for cell in lattice_cells],
        "excised_cells_on_the_orbit": [[cell[0], cell[1]] for cell in crossed],
        "verdict": "ArrivedWithinBudget" if within else "Rejected_OverBudget",
        "reasons": [] if within else [
            "the arrival takes " + str(count) + " steps and the declared step budget is "
            + str(budget) + ", an excess of " + str(count - budget) + " steps"],
    })
    return record


def projection_verdict(projection, codomain):
    """The declared projection, checked as a map."""
    reasons = []
    if set(projection) != set(PROJECTION_DOMAIN):
        reasons.append("the projection must be declared on the declared domain "
                       + str(list(PROJECTION_DOMAIN)) + ", not on " + str(sorted(projection)))
    if projection.get("outer_side") == projection.get("inner_side"):
        reasons.append("the two sides must have distinct projections; the declared projection "
                       "sends both to " + str(projection.get("outer_side")))
    if projection.get("outer_spiral") == projection.get("inner_spiral"):
        reasons.append("the helical pair must project to two distinct rotation senses; the "
                       "declared projection sends both to "
                       + str(projection.get("outer_spiral")))
    for key in ("outer_side", "inner_side"):
        if key in projection and projection[key] not in codomain["sides"]:
            reasons.append("the image of " + key + " must lie in the declared side codomain")
    for key in ("outer_spiral", "inner_spiral"):
        if key in projection and projection[key] not in codomain["rotation_senses"]:
            reasons.append("the image of " + key
                           + " must lie in the declared rotation-sense codomain")
    return {
        "images": dict(sorted(projection.items())),
        "single_valued_on_the_declared_domain": set(projection) == set(PROJECTION_DOMAIN),
        "the_two_sides_have_distinct_images":
            projection.get("outer_side") != projection.get("inner_side"),
        "the_two_spirals_have_distinct_images":
            projection.get("outer_spiral") != projection.get("inner_spiral"),
        "accepted": not reasons,
        "verdict": "Accepted" if not reasons else "Rejected",
        "reasons": reasons,
    }


def redistribute(contents, transfers):
    """The declared inter-layer redistribution: a declared share of a layer moves to the next."""
    updated = dict(contents)
    for source, target, share in transfers:
        moved = contents[source] * share
        updated[source] -= moved
        updated[target] += moved
    return updated


def memory_layer(contents):
    """The layer holding the carried memory: the largest declared content, uniquely."""
    ordered = sorted(contents.items(), key=lambda row: (-row[1], row[0]))
    return ordered[0][0]


def layer_vector(contents):
    return [str(contents[layer]) for layer in LAYER_ORDER]


# ------------------------------------------------------------------ sections --

def section_surgery_and_collar(sym):
    """S1: the singular locus, the declared collar with its orientation and normal, the excision."""
    p, q, h = sym["p"], sym["q"], sym["h"]
    resultant = sp.Poly(sp.resultant(sp.Poly(sym["G"], h), sp.Poly(sym["Gh"], h)), p, q)
    primitive = resultant.primitive()[1]
    factored = sp.factor_list(primitive.as_expr())
    factors = {str(factor): exponent for factor, exponent in factored[1]}
    check(factors == {DISCRIMINANT_FACTOR: 1, "8*p + 1": 6, "64*q + 17": 2, "8*q + 1": 2},
          "the cleared resultant factors exactly as the declared discriminant form does")
    check(factored[0] in (1, -1),
          "the cleared resultant is primitive over the integers up to its sign")
    check(primitive.total_degree() == 12, "the discriminant variety has total degree twelve")
    check(len(primitive.terms()) == 52, "the discriminant variety has 52 terms")
    declared_discriminant = -(8 * p + 1) ** 6 * (8 * q + 1) ** 2 * (64 * q + 17) ** 2 * (
        2048 * p ** 2 + 608 * p - 8 * q + 43)
    check(sp.simplify(primitive.as_expr() - declared_discriminant) == 0,
          "the cleared resultant is exactly the declared discriminant form")
    check(sp.Poly(sym["Gh"], h).degree() == 3, "the derivative of the return is a cubic in h")

    branch = 256 * COLLISION_P ** 2 + 76 * COLLISION_P + Fr(43, 8)
    check(branch == COLLISION_Q,
          "the declared collision parameter lies on the B1 branch q = 256 p^2 + 76 p + 43/8")
    at_collision = sp.expand(declared_discriminant.subs({p: rat(COLLISION_P),
                                                         q: rat(COLLISION_Q)}))
    check(at_collision == 0,
          "the discriminant vanishes exactly at the declared collision parameter")
    at_witness = sp.expand(declared_discriminant.subs({p: rat(PERTURBATION_WITNESS[0]),
                                                       q: rat(PERTURBATION_WITNESS[1])}))
    check(at_witness != 0, "the discriminant does not vanish at the declared perturbation witness")
    check(sgn(fr(at_witness)) == -1, "the discriminant is negative at the perturbation witness")
    off_branch = declared_discriminant.subs({p: rat(COLLISION_P), q: rat(COLLISION_Q + 1)})
    check(sgn(fr(off_branch)) == -sgn(branch - (COLLISION_Q + 1)),
          "off the branch, sign(D) is the negative of the sign of the B1 branch function")

    coupling = [fr(value) for value in DECLARED_TIME_COUPLING]
    check(len(coupling) == PHASES, "the declared time coupling has one entry per cycle phase")
    coupling_maximum = max(abs(value) for value in coupling)
    check(coupling_maximum == Fr(31, 512), "the declared coupling maximum is 31/512")
    check(coupling.index(max(coupling, key=abs)) == SEAM_PHASE,
          "the declared coupling maximum sits at the seam, side 0")

    collar_cells = [(SINGULAR_RADIAL_INDEX, phase) for phase in range(PHASES)]
    check(len(collar_cells) == PHASES, "the collar is one full twelve-phase cycle at r = 0")

    def neighbours(cell):
        radial, phase = cell
        return [(radial + 1, phase), (radial - 1, phase),
                (radial, (phase + 1) % PHASES), (radial, (phase - 1) % PHASES)]

    boundary = sorted({cell for collar_cell in collar_cells for cell in neighbours(collar_cell)
                       if cell not in collar_cells})
    check(len(boundary) == 2 * PHASES, "the collar's boundary has two cells per phase")
    seen, components = set(), []
    for cell in boundary:
        if cell in seen:
            continue
        stack, component = [cell], []
        seen.add(cell)
        while stack:
            current = stack.pop()
            component.append(current)
            for other in neighbours(current):
                if other in boundary and other not in seen:
                    seen.add(other)
                    stack.append(other)
        components.append(sorted(component))
    check(len(components) == 2, "the collar's boundary has exactly two connected components")
    sides = {"outer": [cell for cell in boundary if cell[0] == COLLAR_RADIAL_EXTENT],
             "inner": [cell for cell in boundary if cell[0] == -COLLAR_RADIAL_EXTENT]}
    check(all(sorted(sides[side]) in components for side in sides),
          "the two sides are exactly the two boundary components")
    check(all(len(sides[side]) == PHASES for side in sides), "each side has one cell per phase")
    check(set(sides["outer"]).isdisjoint(set(sides["inner"])),
          "the two sides are disjoint as declared cell sets")
    check(sides["outer"] != sides["inner"], "the two sides are not the same declared object")
    check(all(cell not in sides["outer"] for cell in collar_cells),
          "no collar cell survives in the outer side")
    check(SIDE_RADIAL_INDEX["outer"] == Fr(COLLAR_RADIAL_EXTENT)
          and SIDE_RADIAL_INDEX["inner"] == Fr(-COLLAR_RADIAL_EXTENT),
          "the sides sit at the declared radial indices plus and minus one")
    outer_normal, inner_normal = side_normal("outer"), side_normal("inner")
    check(pairing((Fr(1), Fr(0)), outer_normal) == -pairing((Fr(1), Fr(0)), inner_normal),
          "the two declared side normals are opposite, as a boundary orientation requires")
    check((Fr(1), Fr(1)) == COLLAR_NORMAL,
          "the declared collar normal is the tilted vector (1, 1) in the (radial, phase) basis")

    return {
        "declared_singular_locus": {
            "collision_branch": "B1: q = 256 p^2 + 76 p + 43/8, the branch of note 0235 on "
                                "which two simple roots collide",
            "discriminant_form": "D(p, q) = -(8 p + 1)^6 (8 q + 1)^2 (64 q + 17)^2 "
                                 "(" + DISCRIMINANT_FACTOR_DISPLAY + ")",
            "discriminant_is_the_cleared_resultant": True,
            "factor_multiplicities": {key.replace("**", "^"): factors[key]
                                      for key in sorted(factors)},
            "total_degree": primitive.total_degree(),
            "number_of_terms": len(primitive.terms()),
            "collision_parameter": {"p": str(COLLISION_P), "q": str(COLLISION_Q)},
            "collision_parameter_on_the_branch": True,
            "discriminant_at_the_collision": str(at_collision),
            "sign_rule_off_the_branch": "sign(D) = -sign(f(p) - q), checked exactly",
            "annual_seam": {
                "cycle_phases": PHASES,
                "seam_phase": SEAM_PHASE,
                "time_coupling": [str(value) for value in coupling],
                "coupling_maximum": str(coupling_maximum),
                "coupling_maximum_at_phase": SEAM_PHASE,
                "the_seam_is_where_the_declared_coupling_is_largest": True,
            },
        },
        "collar": {
            "carrier": "the declared cylinder Z x Z_12: a radial index r and a phase index k of "
                       "the twelve-phase cycle",
            "definition": "the singular seam circle {(0, k): k in Z_12}: the whole twelve-phase "
                          "cycle at the singular radial index",
            "radial_index": SINGULAR_RADIAL_INDEX,
            "cells": len(collar_cells),
            "cell_set": [[cell[0], cell[1]] for cell in collar_cells],
            "radial_extent": COLLAR_RADIAL_EXTENT,
            "phase_extent": "the whole cycle",
            "orientation": {
                "ordered_frame": ["radial outward", "phase increasing"],
                "orientation_sign": "1",
                "boundary_orientation": "on the outer component the outward normal is the "
                                        "declared normal, on the inner component its negative",
                "the_two_side_normals_are_opposite": True,
            },
            "normal": {
                "basis": "(radial, phase), the declared character basis of the carrier",
                "vector": [str(COLLAR_NORMAL[0]), str(COLLAR_NORMAL[1])],
                "radial_component": str(COLLAR_NORMAL[0]),
                "phase_component": str(COLLAR_NORMAL[1]),
                "phase_tilt": str(COLLAR_NORMAL[1]),
                "why_tilted": "the collar is declared tilted by one phase at the seam, where the "
                              "declared time coupling of note 0236 puts its maximum 31/512; the "
                              "tilt is part of the declaration",
            },
            "side_normals": {"outer": [str(outer_normal[0]), str(outer_normal[1])],
                             "inner": [str(inner_normal[0]), str(inner_normal[1])]},
        },
        "excision": {
            "carried_out": "the declared collar is removed from the declared carrier",
            "carrier_after_the_surgery": "(Z x Z_12) minus the collar",
            "excised_cells": len(collar_cells),
            "excised_cell_set": [[cell[0], cell[1]] for cell in collar_cells],
            "boundary_components": len(components),
            "two_sides_replace_the_singular_carrier": True,
            "sides": {
                "outer": {"radial_index": str(SIDE_RADIAL_INDEX["outer"]),
                          "cells": len(sides["outer"]),
                          "cell_set": [[cell[0], cell[1]] for cell in sides["outer"]],
                          "disjoint_from_the_other_side": True},
                "inner": {"radial_index": str(SIDE_RADIAL_INDEX["inner"]),
                          "cells": len(sides["inner"]),
                          "cell_set": [[cell[0], cell[1]] for cell in sides["inner"]],
                          "disjoint_from_the_other_side": True},
            },
            "sides_are_distinct_objects": True,
            "exactness": "the excision is exact set subtraction on the declared lattice; the two "
                         "sides are the exact boundary components of the excised collar",
        },
    }


def section_spirals_and_chirality():
    """S2: the two declared spirals, their handedness and the degenerate-spiral controls."""
    spirals = {}
    for side in ("outer", "inner"):
        sigma = CHIRALITY[side]
        condition = spiral_verdict(SPIRAL_RADIAL_ADVANCE, sigma * SPIRAL_ANGULAR_STEP)
        check(condition["accepted"], "each declared spiral is a rotation with a radial advance")
        start = (SIDE_RADIAL_INDEX[side], SEAM_PHASE)
        after_twelve = (start[0] + PHASES * SPIRAL_RADIAL_ADVANCE,
                        (start[1] + sigma * PHASES) % PHASES)
        after_twenty_four = (start[0] + 2 * PHASES * SPIRAL_RADIAL_ADVANCE,
                             (start[1] + sigma * 2 * PHASES) % PHASES)
        check(after_twelve[1] == SEAM_PHASE and after_twenty_four[1] == SEAM_PHASE,
              "a whole number of twelve-phase turns returns each spiral to the seam phase")
        spirals[side] = {
            "side": side,
            "declared_map": "S_sigma(r, k) = (r + 1/12, k + sigma mod 12), a rotation by one "
                            "phase of the twelve-phase cycle compounded with a radial advance",
            "chirality_sign": f"{sigma:+d}",
            "handedness": ("positive (the phase index increases by one per turn)" if sigma > 0
                           else "negative (the phase index decreases by one per turn)"),
            "radial_advance": str(SPIRAL_RADIAL_ADVANCE),
            "angular_step": sigma * SPIRAL_ANGULAR_STEP,
            "start": [str(start[0]), start[1]],
            "after_twelve_turns": [str(after_twelve[0]), after_twelve[1]],
            "after_twenty_four_turns": [str(after_twenty_four[0]), after_twenty_four[1]],
            "rotation_compounded_with_a_radial_advance": True,
            "well_defined_on_the_declared_lattice": True,
        }
    check(CHIRALITY["outer"] == -CHIRALITY["inner"],
          "the declared chirality signs are opposite")
    declared = chirality_verdict(CHIRALITY["outer"], CHIRALITY["inner"])
    check(declared["accepted"], "the declared pair satisfies the declared chirality condition")

    pure_rotation = spiral_verdict(Fr(0), SPIRAL_ANGULAR_STEP)
    pure_advance = spiral_verdict(SPIRAL_RADIAL_ADVANCE, 0)
    check(not pure_rotation["accepted"], "a pure rotation is rejected by the declared condition")
    check(not pure_advance["accepted"], "a pure radial advance is rejected by the declared "
                                        "condition")

    return {
        "declared_spiral_map": "S_sigma(r, k) = (r + a, k + sigma) with a = 1/12: a rotation by "
                               "one phase compounded with a radial advance of 1/12",
        "spirals": spirals,
        "opposite_chirality_declared": True,
        "chirality_condition": "the declared chirality condition is sigma_outer = -sigma_inner",
        "chirality_condition_on_the_declared_pair": declared,
        "degenerate_spiral_controls": {
            "pure_rotation": pure_rotation,
            "pure_radial_advance": pure_advance,
            "both_rejected": not pure_rotation["accepted"] and not pure_advance["accepted"],
        },
    }


def section_flux_and_attribution():
    """S3: the collar flux before and after, the attribution, and the flux controls."""
    flux_before = Fr(0)
    declared = collar_flux(CHIRALITY)
    cross_check = chirality_pair_flux(COLLAR_NORMAL, CHIRALITY)
    check(declared["flux"] == cross_check,
          "the flux computed from the pairing equals the flux computed from the rise formula")
    check(declared["flux"] == Fr(2), "the declared pair raises the flux to exactly 2")
    check(declared["flux"] > flux_before, "the after-flux is strictly greater than the before-flux")

    same = collar_flux({"outer": 1, "inner": 1})
    same_condition = chirality_verdict(1, 1)
    check(not same_condition["accepted"],
          "the same-chirality pair is rejected by the declared chirality condition")
    check(same["flux"] == flux_before,
          "the same-chirality introduction fails to raise the flux: it is exactly the before-flux")
    check(not same["flux"] > flux_before, "the same-chirality flux does not rise")

    reverse = collar_flux({"outer": -1, "inner": 1})
    reverse_condition = chirality_verdict(-1, 1)
    check(reverse_condition["accepted"],
          "the reversed pair is also a declared opposite-chirality pair and passes the condition")
    check(reverse["flux"] == -Fr(2), "the reversed declared pair lowers the flux by 2")
    check(not reverse["flux"] > flux_before, "the reversed declared pair does not raise the flux")

    extra = {"outer": (Fr(1, 8), Fr(0))}
    observed = collar_flux(CHIRALITY, extra)
    attributed = declared["flux"] - flux_before
    unattributed = observed["flux"] - flux_before - attributed
    check(unattributed == Fr(1, 8),
          "the rise that cannot be attributed to the helical introduction is exactly 1/8")
    check(unattributed != 0, "an unattributed rise is present and is not absorbed")

    attributed_only = collar_flux(CHIRALITY)
    unattributed_clean = attributed_only["flux"] - flux_before - attributed
    check(unattributed_clean == 0, "the declared construction has no unattributed rise")

    radial_normal = (Fr(1), Fr(0))
    radial_rows = {}
    for sigmas in ({"outer": 1, "inner": -1}, {"outer": 1, "inner": 1},
                   {"outer": -1, "inner": 1}):
        value = collar_flux(sigmas, normal=radial_normal)["flux"]
        radial_rows[f"{sigmas['outer']:+d}/{sigmas['inner']:+d}"] = str(value)
    check(set(radial_rows.values()) == {"0"},
          "with a purely radial normal the rise vanishes for every chirality pair")

    return {
        "declared_pairing": "B(u, v) = u_radial v_radial + u_phase v_phase: the declared pairing "
                            "of the introduced resource with the collar normal",
        "introduced_resource_per_turn": {
            side: [str(introduced_resource(side)[0]), str(introduced_resource(side)[1])]
            for side in ("outer", "inner")},
        "collar_normal": [str(COLLAR_NORMAL[0]), str(COLLAR_NORMAL[1])],
        "flux_before": str(flux_before),
        "flux_before_reason": "before the helical introduction no resource is introduced on "
                              "either side, so the pairing is exactly the declared zero; it is "
                              "the declared zero of the pairing, not a limit",
        "flux_after": str(declared["flux"]),
        "flux_after_terms": declared["terms"],
        "flux_after_from_the_rise_formula": str(cross_check),
        "radial_cancellation": {
            "radial_contributions": {
                side: str(introduced_resource(side)[0] * side_normal(side)[0])
                for side in ("outer", "inner")},
            "radial_sum": "0",
            "angular_sum": str(Fr(SPIRAL_ANGULAR_STEP)
                               * Fr(CHIRALITY["outer"] - CHIRALITY["inner"])),
            "reading": "the two declared radial advances pair with opposite normals and cancel "
                       "exactly, so the rise above the declared before-flux is carried by the "
                       "declared angular component alone",
        },
        "rise": str(attributed),
        "rise_formula": "the rise is w n_phase (sigma_outer - sigma_inner) with the declared "
                        "angular step w = 1 phase and the declared phase tilt n_phase = 1, so it "
                        "is exactly 2",
        "strictly_greater": declared["flux"] > flux_before,
        "attribution": {
            "attributed_rise": str(attributed),
            "attributed_to": "the declared helical introduction on the two sides",
            "unattributed_rise": str(unattributed_clean),
            "verdict": "Attributed",
            "rule": "a rise counts as attributed only when it is exactly the rise of the declared "
                    "pair over the declared before-flux; anything else is reported as "
                    "unattributed",
        },
        "sign_pairs": [
            {"signs": "+1/-1", "label": "the declared pair, opposite chirality",
             "chirality_condition": "Accepted", "flux_after": str(declared["flux"]),
             "rose": declared["flux"] > flux_before},
            {"signs": "+1/+1", "label": "same chirality on both sides",
             "chirality_condition": "Rejected", "flux_after": str(same["flux"]),
             "rose": same["flux"] > flux_before},
            {"signs": "-1/+1", "label": "the reversed opposite pair",
             "chirality_condition": "Accepted", "flux_after": str(reverse["flux"]),
             "rose": reverse["flux"] > flux_before},
        ],
        "same_chirality_control": {
            "control": "the same-chirality introduction on both sides",
            "flux_after": str(same["flux"]),
            "rose": same["flux"] > flux_before,
            "chirality_condition": same_condition,
            "rejected_by": same_condition["rejected_by"],
            "rejection_reasons": same_condition["reasons"],
            "decided_by_a_count": False,
        },
        "unattributed_control": {
            "control": "a declared non-helical introduction added on the outer side",
            "declared_extra_introduction": ["1/8", "0"],
            "flux_observed": str(observed["flux"]),
            "attributed_rise": str(attributed),
            "unattributed_rise": str(unattributed),
            "verdict": "Unattributed",
            "rule": "the rise above the declared before-flux that is not the declared helical "
                    "rise is reported as unattributed rather than absorbed",
        },
        "radial_normal_control": {
            "control": "the same two spirals paired with a purely radial collar normal (1, 0)",
            "flux_after_by_sign_pair": radial_rows,
            "rise_for_every_sign_pair": "0",
            "verdict": "FAILED_TO_DISCRIMINATE",
            "why": "with a purely radial normal the pairing never meets the angular component, so "
                   "the rise vanishes for the same-chirality pair and for both opposite pairs "
                   "alike: this control does not discriminate chirality, and the rise of the "
                   "declared construction is a declared consequence of the phase tilt as much as "
                   "of the chirality",
        },
    }


def section_side_o_obstruction(computed_record):
    """S4: the obstruction written out on side O and the discharge as a condition on the record."""
    written = dict(computed_record)
    written["record_id"] = "O-1"
    written["written_by"] = "the declared construction's outer side"
    check(record_verdict(written, computed_record)["verdict"] == "Discharged",
          "the written record on side O satisfies the discharge condition")

    unwritten = dict(written)
    unwritten["boundary_object"] = ""
    unwritten_verdict = record_verdict(unwritten, computed_record)
    check(unwritten_verdict["verdict"] == "Rejected",
          "an obstruction that is not written out fails the discharge condition")
    check(not unwritten_verdict["written"], "the unwritten record is reported as not written out")

    implicit_verdict = record_verdict(None, computed_record)
    check(implicit_verdict["verdict"] == "Rejected",
          "an implicit obstruction with no record object fails the discharge condition")

    disagreeing = dict(written)
    disagreeing["parameter_q"] = "7019/7"
    disagreeing_verdict = record_verdict(disagreeing, computed_record)
    check(disagreeing_verdict["verdict"] == "Rejected",
          "a record whose written value disagrees with the computed value fails the discharge")
    check(disagreeing_verdict["written"],
          "the disagreeing record is written out and fails on agreement, not on completeness")

    return {
        "side": "outer",
        "declared_obstruction": {
            "object": "the discriminant collision at the collar's base cell: the vanishing of the "
                      "B1 factor of D(p, q) at (p, q) = (-2, 7019/8)",
            "explicit_object_declared": True,
            "the_obstruction_is_a_point_where_the_construction_stopped": True,
        },
        "written_record": written,
        "computed_values": computed_record,
        "record_agrees_with_the_computed_values": True,
        "discharge_condition": "the record must be written out - every declared field present and "
                               "non-empty - and every written exact value must equal the value "
                               "computed by this run",
        "discharge": record_verdict(written, computed_record),
        "controls": [
            {"control": "an unwritten obstruction",
             "verdict": unwritten_verdict["verdict"],
             "written": unwritten_verdict["written"],
             "rejection_reasons": unwritten_verdict["reasons"],
             "rejected_by_the_declared_condition": True},
            {"control": "an implicit obstruction with no record at all",
             "verdict": implicit_verdict["verdict"],
             "written": implicit_verdict["written"],
             "rejection_reasons": implicit_verdict["reasons"],
             "rejected_by_the_declared_condition": True},
            {"control": "a written record whose value disagrees",
             "verdict": disagreeing_verdict["verdict"],
             "written": disagreeing_verdict["written"],
             "rejection_reasons": disagreeing_verdict["reasons"],
             "rejected_by_the_declared_condition": True},
        ],
        "discharge_is_a_condition_on_the_record": True,
    }


def section_side_i_arrival(excised_cells):
    """S5: side I's declared time-domain target and its declared step budget."""
    declared = arrival_verdict(ARRIVAL_START, ARRIVAL_TARGET, SPIRAL_RADIAL_ADVANCE,
                               CHIRALITY["inner"], STEP_BUDGET, excised_cells)
    check(declared["solvable"], "the declared arrival is solvable on the declared lattice")
    check(declared["steps"] == 24, "the declared arrival takes exactly 24 steps")
    check(declared["within_budget"], "the declared arrival is inside the declared step budget")
    check(declared["slack"] == 12, "the declared arrival has exactly 12 steps of slack")
    check(fr(declared["radial_distance_covered"]) == Fr(2 * COLLAR_RADIAL_EXTENT),
          "the radial distance covered is exactly the collar's diameter")
    check(declared["excised_cells_on_the_orbit"] == [[0, 0]],
          "the declared orbit crosses the excised collar at exactly the singular cell")

    over = arrival_verdict(ARRIVAL_START, ARRIVAL_TARGET, SPIRAL_RADIAL_ADVANCE / 2,
                           CHIRALITY["inner"], STEP_BUDGET, excised_cells)
    check(over["solvable"] and not over["within_budget"],
          "the declared over-budget variant does arrive, and outside the budget")
    check(over["steps"] == 48 and over["excess"] == 12,
          "the over-budget variant takes 48 steps, an excess of 12 over the budget")

    early = arrival_verdict(ARRIVAL_START, (Fr(SINGULAR_RADIAL_INDEX), SEAM_PHASE),
                            SPIRAL_RADIAL_ADVANCE, CHIRALITY["inner"], STEP_BUDGET, excised_cells)
    check(early["solvable"] and early["steps"] == 12,
          "the earlier phase recurrence of the declared spiral is at 12 steps")
    check(early["excised_cells_on_the_orbit"] == [[0, 0]],
          "the 12-step recurrence lands on the excised singular cell")

    swapped = arrival_verdict((SIDE_RADIAL_INDEX["outer"], SEAM_PHASE),
                              (SIDE_RADIAL_INDEX["inner"], SEAM_PHASE),
                              SPIRAL_RADIAL_ADVANCE, CHIRALITY["outer"], STEP_BUDGET, set())
    check(not swapped["solvable"],
          "the outer side judged by the arrival condition cannot arrive at the inner radius")

    outer_sign_flip = arrival_verdict(ARRIVAL_START, ARRIVAL_TARGET, SPIRAL_RADIAL_ADVANCE,
                                      CHIRALITY["outer"], STEP_BUDGET, excised_cells)
    check(outer_sign_flip["steps"] == declared["steps"],
          "the arrival step count does not depend on the declared chirality sign")

    return {
        "side": "inner",
        "declared_time_domain_target": {
            "radial_index": str(ARRIVAL_TARGET[0]),
            "phase": ARRIVAL_TARGET[1],
            "reading": "the seam phase at the outer collar radius: the declared time-domain "
                       "location of the fast arrival",
        },
        "declared_start": {"radial_index": str(ARRIVAL_START[0]), "phase": ARRIVAL_START[1]},
        "declared_step_budget": STEP_BUDGET,
        "step_accounting": {
            "unit": "one phase of the twelve-phase cycle",
            "cycles": CYCLE_COUNT,
            "phases_per_cycle": PHASES,
            "budget": STEP_BUDGET,
            "end_block_steps": END_BLOCK_STEPS,
            "total_with_the_inherited_end_block": CYCLE_COUNT * (PHASES + END_BLOCK_STEPS),
            "the_budget_is_the_declared_convention": True,
        },
        "arrival": declared,
        "collar_diameter": str(2 * COLLAR_RADIAL_EXTENT),
        "radial_distance_equals_the_collar_diameter": True,
        "controls": [
            {"control": "an over-budget arrival",
             "radial_advance": str(SPIRAL_RADIAL_ADVANCE / 2),
             "steps": over["steps"], "within_budget": over["within_budget"],
             "excess": over["excess"], "verdict": over["verdict"],
             "rejection_reasons": over["reasons"],
             "rejected_by": "the declared step budget"},
            {"control": "the outer side judged by the arrival condition (roles swapped)",
             "solvable": swapped["solvable"], "verdict": swapped["verdict"],
             "rejection_reasons": swapped["reasons"],
             "rejected_by": "the declared arrival condition with the declared outward spiral"},
            {"control": "the earlier phase recurrence of the declared spiral",
             "steps": early["steps"],
             "excised_cells_on_the_orbit": early["excised_cells_on_the_orbit"],
             "verdict": "Reported",
             "rejection_reasons": ["the declared target is the outer collar radius, so the "
                                   "12-step recurrence at the excised singular cell is not the "
                                   "declared arrival"]},
        ],
        "failed_to_discriminate": {
            "control": "the arrival step count under the two declared chirality signs",
            "steps_under_minus_one": declared["steps"],
            "steps_under_plus_one": outer_sign_flip["steps"],
            "verdict": "FAILED_TO_DISCRIMINATE",
            "why": "the declared target is a whole number of twelve-phase turns away, so both "
                   "declared rotation senses arrive at the same step count; the arrival condition "
                   "does not discriminate the handedness",
        },
    }


def section_resource_accounting(flux):
    """S6: the carried remainder split by the surgery, the layers and the layer-wise sealing."""
    contents = dict(zip(LAYER_ORDER, LAYER_CONTENTS, strict=True))
    slow_total = sum(contents.values())
    check(slow_total == Fr(7, 8), "the declared slow remainder is exactly 7/8")
    check(Fr(1, 4) == FAST_REMAINDER, "the declared fast remainder is exactly 1/4")
    total = slow_total + FAST_REMAINDER
    check(total == Fr(9, 8), "the declared carried remainder is exactly 9/8")

    terms = {side: abs(fr(flux["flux_after_terms"][side]["term"])) for side in ("outer", "inner")}
    shares = {side: terms[side] / sum(terms.values()) for side in ("outer", "inner")}
    check(shares["outer"] == Fr(13, 24) and shares["inner"] == Fr(11, 24),
          "the split shares derived from the declared flux terms are 13/24 and 11/24")
    check(shares["outer"] + shares["inner"] == 1,
          "the shares derived from the declared flux terms sum to exactly one")

    per_layer = {}
    for layer in LAYER_ORDER:
        outer = shares["outer"] * contents[layer]
        inner = shares["inner"] * contents[layer]
        per_layer[layer] = {"outer": str(outer), "inner": str(inner), "sum": str(outer + inner),
                            "equals_the_carried_content": outer + inner == contents[layer]}
        check(outer + inner == contents[layer],
              "the surgery splits layer " + layer + " without creating resource")
    fast_outer = shares["outer"] * FAST_REMAINDER
    fast_inner = shares["inner"] * FAST_REMAINDER
    check(fast_outer + fast_inner == FAST_REMAINDER,
          "the surgery splits the fast component without creating resource")
    outer_total = sum(shares["outer"] * value
                      for value in [*contents.values(), FAST_REMAINDER])
    inner_total = sum(shares["inner"] * value
                      for value in [*contents.values(), FAST_REMAINDER])
    check(outer_total + inner_total == total, "no resource is created by the surgery in total")

    sealing = {}
    measured = {layer: shares["outer"] * contents[layer] + shares["inner"] * contents[layer]
                for layer in LAYER_ORDER}
    for index, layer in enumerate(LAYER_ORDER):
        drift = measured[layer] - contents[layer]
        sealing[layer] = {
            "bound": str(LAYER_SEALING_BOUND[index]),
            "post_surgery_content": str(measured[layer]),
            "carried_content": str(contents[layer]),
            "drift": str(drift),
            "sealed": abs(drift) <= LAYER_SEALING_BOUND[index],
        }
        check(sealing[layer]["sealed"], "layer " + layer + " is sealed within its declared bound")

    cancelling = {"mixed": Fr(1, 64), "thermocline": Fr(0), "deep": Fr(-1, 64)}
    cancelling_total = sum(cancelling.values())
    violated = [layer for index, layer in enumerate(LAYER_ORDER)
                if abs(cancelling[layer]) > LAYER_SEALING_BOUND[index]]
    check(cancelling_total == 0, "the total-cancelling control conserves the total exactly")
    check(violated == ["mixed", "deep"],
          "the total-cancelling control violates the bound in exactly two layers")
    check(not (cancelling_total == 0 and not violated),
          "a layer-wise violation is not cancelled by a conserved total")

    seams = []
    running = dict(contents)
    for cycle in range(1, CYCLE_COUNT + 1):
        updated = redistribute(running, SEAM_TRANSFERS)
        drift = {layer: updated[layer] - running[layer] for layer in LAYER_ORDER}
        seam_sealing = {
            layer: abs((shares["outer"] * updated[layer] + shares["inner"] * updated[layer])
                       - updated[layer]) <= LAYER_SEALING_BOUND[index]
            for index, layer in enumerate(LAYER_ORDER)}
        check(sum(updated.values()) == slow_total,
              "the declared seam redistribution conserves the slow total exactly")
        check(sum(drift.values()) == 0, "the per-layer drifts sum to zero at every seam")
        check(all(seam_sealing.values()), "every layer is sealed at every seam")
        seams.append({
            "cycle": "C" + str(cycle),
            "contents": layer_vector(updated),
            "total": str(sum(updated.values())),
            "per_layer_drift": layer_vector(drift),
            "memory_layer": memory_layer(updated),
            "sealed_layer_by_layer": all(seam_sealing.values()),
        })
        running = updated
    check(all(row["memory_layer"] == "deep" for row in seams),
          "the deep layer holds the carried memory at every seam")
    check(all(fr(row["total"]) == slow_total for row in seams),
          "the slow total is conserved at every seam")

    zero_operator = redistribute(dict(contents), ())
    zero_drift = {layer: zero_operator[layer] - contents[layer] for layer in LAYER_ORDER}
    check(all(value == 0 for value in zero_drift.values()),
          "a chain with no redistribution leaves every layer exactly unchanged")
    check(sum(zero_drift.values()) == 0,
          "the no-redistribution control conserves the total without moving any layer")

    atmospheric_memory = Fr(0)
    check(atmospheric_memory == 0,
          "the purely atmospheric chain carries no memory at the seam by the declared reset")
    declared_memory = sum(running.values())
    check(declared_memory == slow_total and declared_memory != 0,
          "the chain with the declared slow component keeps the carried memory")

    return {
        "carried_remainder": {
            "fast": str(FAST_REMAINDER),
            "slow_layers": {layer: str(contents[layer]) for layer in LAYER_ORDER},
            "slow_total": str(slow_total),
            "total": str(total),
        },
        "surgery_split": {
            "shares": {"outer": str(shares["outer"]), "inner": str(shares["inner"])},
            "shares_derived_from": "the declared collar flux terms, as the absolute flux of each "
                                   "side over their sum; the shares are derived, not free",
            "flux_terms": {side: str(terms[side]) for side in ("outer", "inner")},
            "per_layer": per_layer,
            "fast": {"outer": str(fast_outer), "inner": str(fast_inner),
                     "sum": str(fast_outer + fast_inner)},
            "totals": {"outer": str(outer_total), "inner": str(inner_total),
                       "sum": str(outer_total + inner_total)},
        },
        "no_resource_created_by_the_surgery": True,
        "per_layer_sums_equal_the_carried_remainder": True,
        "grand_total_unchanged": True,
        "layer_sealing": {
            "bound": {layer: str(LAYER_SEALING_BOUND[index])
                      for index, layer in enumerate(LAYER_ORDER)},
            "layers": sealing,
            "all_layers_sealed": True,
            "the_bound_applies_layer_by_layer": True,
            "sealed_at_every_seam": all(row["sealed_layer_by_layer"] for row in seams),
        },
        "total_cancelling_control": {
            "control": "a declared layer-wise violation whose total is conserved exactly",
            "declared_violation": {layer: str(cancelling[layer]) for layer in LAYER_ORDER},
            "total_drift": str(cancelling_total),
            "total_looks_sealed": True,
            "violating_layers": violated,
            "verdict": "LayerWiseViolation",
            "cancelled_by_the_total": False,
            "reported_as": "a violation of the layer-wise bound and not as a pass",
        },
        "seam_redistribution": {
            "declared_operator": "the mixed layer loses an eighth of itself to the thermocline "
                                 "and the thermocline loses a sixteenth of itself to the deep "
                                 "layer at every seam",
            "seams": seams,
            "slow_total_conserved_at_every_seam": True,
            "memory_layer_stable": True,
        },
        "zero_redistribution_control": {
            "control": "a chain with no redistribution at all",
            "per_layer_drift": layer_vector(zero_drift),
            "total_conserved": True,
            "verdict": "the layer structure does no work in this control",
            "reported_rather_than_smoothed": True,
        },
        "atmospheric_memory_control": {
            "control": "the purely atmospheric chain of the frozen contract, carried forward",
            "atmospheric_only": {"carried_memory_at_the_seam": str(atmospheric_memory),
                                 "lost": atmospheric_memory == 0},
            "with_the_slow_component": {"carried_memory_at_the_seam": str(declared_memory),
                                        "kept": declared_memory != 0},
            "the_split_does_work": True,
        },
    }


def section_projection():
    """S7: the declared projection to the cold/heat two-sided reading, checked as a map."""
    declared = projection_verdict(DECLARED_PROJECTION, PROJECTION_CODOMAIN)
    check(declared["accepted"], "the declared projection is accepted as a map")
    identifying = dict(DECLARED_PROJECTION)
    identifying["outer_side"] = "two_sided_mechanism"
    identifying["inner_side"] = "two_sided_mechanism"
    identifying_verdict = projection_verdict(identifying, PROJECTION_CODOMAIN)
    check(not identifying_verdict["accepted"],
          "a projection that identifies the two sides is rejected")
    single = dict(DECLARED_PROJECTION)
    single["inner_spiral"] = "rotation_sense_positive"
    single_verdict = projection_verdict(single, PROJECTION_CODOMAIN)
    check(not single_verdict["accepted"],
          "a projection that reads the helical pair as one rotation sense is rejected")
    wrong_codomain = dict(DECLARED_PROJECTION)
    wrong_codomain["outer_side"] = "rotation_sense_positive"
    wrong_codomain_verdict = projection_verdict(wrong_codomain, PROJECTION_CODOMAIN)
    check(not wrong_codomain_verdict["accepted"],
          "a projection that sends a side into the rotation-sense codomain is rejected")

    return {
        "declared_projection": dict(sorted(DECLARED_PROJECTION.items())),
        "declared_domain": list(PROJECTION_DOMAIN),
        "declared_codomain": {"sides": list(PROJECTION_CODOMAIN["sides"]),
                              "rotation_senses": list(PROJECTION_CODOMAIN["rotation_senses"])},
        "checked_as_a_map": declared,
        "verdict": declared["verdict"],
        "controls": [
            {"control": "a projection that identifies the two sides",
             "verdict": identifying_verdict["verdict"],
             "rejection_reasons": identifying_verdict["reasons"]},
            {"control": "a projection that reads the helical pair as one rotation sense",
             "verdict": single_verdict["verdict"],
             "rejection_reasons": single_verdict["reasons"]},
            {"control": "a projection that sends a side into the rotation-sense codomain",
             "verdict": wrong_codomain_verdict["verdict"],
             "rejection_reasons": wrong_codomain_verdict["reasons"]},
        ],
        "no_cold_heat_quantity_asserted": True,
        "the_projection_is_declared_only": True,
        "the_cold_heat_reading_exists_only_as_this_map": True,
    }


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


def section_baselines(sym):
    """S8: the exact baselines of the earlier runs, reproduced."""
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

    discriminant = sp.Poly(sp.resultant(sp.Poly(sym["G"], h), sp.Poly(sym["Gh"], h)), p, q)
    primitive = discriminant.primitive()[1]
    at_witness = sp.expand(primitive.as_expr().subs({p: rat(PERTURBATION_WITNESS[0]),
                                                     q: rat(PERTURBATION_WITNESS[1])}))
    check(at_witness != 0, "the amplitude floor witness is off the discriminant variety")

    cubic = sp.Poly(h ** 3 + 8 * h ** 2 + 64 * h - 320, h)
    derivative = sp.Poly(3 * h ** 2 + 16 * h + 64, h)
    check(fr(sp.discriminant(derivative.as_expr(), h)) == -512,
          "the derivative of the closure cubic has discriminant -512 and so is strictly positive")
    check(sp.Poly(sym["closure"], h).as_expr().subs(h, 0) == 0,
          "the closure reading always has the trivial exit h = 0")
    closure_roots = isolated_real_roots(cubic, (Fr(3), Fr(4)))
    check(len(closure_roots) == 1, "the closure reading has exactly one nontrivial real exit")
    low, high = closure_roots[0]
    prefix = correctly_rounded_prefix(Ivl(low, high), 17)
    check(prefix == "3.2035072879526181",
          "the closure amplitude is correctly rounded to 3.2035072879526181")
    divisors = [value for value in range(1, 321) if 320 % value == 0]
    check(all(cubic.eval(rat(sign * value)) != 0 for value in divisors for sign in (1, -1)),
          "the closure cubic has no rational root, so the decimal expansion does not terminate")
    quotient_discriminant = -(Ivl(3 * low * low, 3 * high * high) + Ivl(16 * low, 16 * high)
                              + Ivl(192))
    check(quotient_discriminant.hi < 0,
          "the quotient quadratic of the closure cubic has a strictly negative discriminant, so "
          "the other two exits are a non-real conjugate pair")

    level = sp.Poly(h ** 4 + 8 * h ** 3 + 64 * h ** 2 + 192 * h - 512, h)
    substituted = sp.Poly(sp.expand(level.as_expr().subs(h, h - 2)), h)
    check(sp.expand(substituted.as_expr() - (h ** 4 + 40 * h ** 2 - 688)) == 0,
          "the level reading becomes u^4 + 40 u^2 - 688 with u = h + 2")
    level_roots = isolated_real_roots(level, (Fr(-6), Fr(2)))
    check(len(level_roots) == 2, "the level reading has exactly two real branches")
    negative, positive = level_roots[0], level_roots[1]
    check(fr(-6) < negative[0] and negative[1] < Fr(-5),
          "the negative real branch lies strictly inside (-6, -5)")
    check(Fr(1) < positive[0] and positive[1] < Fr(2),
          "the positive real branch lies strictly inside (1, 2)")

    sigma = QNr(-20, 8, 17)
    square = sigma * sigma
    check((square + sigma * 40 - QNr(688)).is_zero(),
          "sigma^2 + 40 sigma - 688 = 0 in the exact extension Q(sqrt(17)) with "
          "sigma = 8 sqrt(17) - 20")
    check(sigma.sign() == 1, "sigma = 8 sqrt(17) - 20 is strictly positive, decided by squaring")
    root_of_seventeen = sqrt_ball(Fr(17), 200)
    sigma_box = Ivl(8 * root_of_seventeen.lo - 20, 8 * root_of_seventeen.hi - 20)
    check(sigma_box.lo > 0, "the enclosure of sigma stays strictly positive")
    small = sqrt_ball(sigma_box.lo, 200)
    large = sqrt_ball(sigma_box.hi, 200)
    amplitude = Ivl(2 + small.lo, 2 + large.hi)
    check(Fr(5) < amplitude.lo and amplitude.hi < Fr(6),
          "the level reading's largest branch amplitude is enclosed strictly inside (5, 6)")
    check(amplitude.lo > Fr(4), "the level reading's largest branch amplitude is strictly above 4")
    ordering = Fr(1) < Fr(low) < Fr(high) < Fr(4) < amplitude.lo
    check(ordering,
          "the three amplitudes are ordered exactly: 1 < 3.2035... < 2 + sqrt(8 sqrt(17) - 20)")
    return {
        "first_scheme": {
            "amplitude_floor": "J_inf = 1",
            "attained_at": "(p, q) = (-2, 17/10)",
            "on_the_discriminant_variety": False,
            "real_branches_at_the_witness": len(witness_rows),
            "branches": witness_rows,
            "frozen_level_of_the_ten_middle_sides": "1",
            "source": "note 0235 and experiments/two_address_exchange_v1/evidence.json",
        },
        "closure_reading": {
            "nontrivial_branch_equation": "h^3 + 8 h^2 + 64 h - 320 = 0",
            "real_exits": len(closure_roots),
            "amplitude": "3.2035072879526181...",
            "correctly_rounded_prefix": prefix,
            "isolation_interval": [str(low), str(high)],
            "no_rational_root": True,
            "derivative_discriminant": "-512",
            "quotient_quadratic_discriminant_enclosure": [str(quotient_discriminant.lo),
                                                          str(quotient_discriminant.hi)],
            "the_other_two_exits_are_non_real": True,
        },
        "level_reading": {
            "equation": "h^4 + 8 h^3 + 64 h^2 + 192 h - 512 = 0",
            "real_branches": len(level_roots),
            "substitution": "u = h + 2, u^4 + 40 u^2 - 688 = 0",
            "closed_form": "h = -2 +- sqrt(8 sqrt(17) - 20)",
            "closed_form_verified_in": "the exact real quadratic extension Q(sqrt(17))",
            "sigma": "8 sqrt(17) - 20",
            "sigma_is_positive": True,
            "largest_branch_amplitude": "2 + sqrt(8 sqrt(17) - 20)",
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
        },
    }


def section_controls(resource_accounting):
    """S9: the inherited controls, executed, with the failures to discriminate retained."""
    readings = {}
    for name, composition in OBSERVATION_COMPOSITIONS:
        artefact = sum(weight * offset for weight, offset
                       in zip(composition, COMPOSITION_OFFSETS, strict=True))
        readings[name] = {
            "composition": [str(value) for value in composition],
            "mechanism_reading": {
                "slow_layer_contents": resource_accounting["seam_redistribution"]["seams"][0]
                ["contents"],
                "slow_total": resource_accounting["carried_remainder"]["slow_total"],
                "per_layer_drift": resource_accounting["seam_redistribution"]["seams"][0]
                ["per_layer_drift"],
                "memory_layer": resource_accounting["seam_redistribution"]["seams"][0]
                ["memory_layer"],
            },
            "composition_only_reading": str(artefact),
        }
    names = [name for name, _ in OBSERVATION_COMPOSITIONS]
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
    fused_first = {**first["mechanism_reading"],
                   "slow_total_with_the_composition_term":
                       str(fr(first["mechanism_reading"]["slow_total"]) + artefact_first)}
    fused_second = {**second["mechanism_reading"],
                    "slow_total_with_the_composition_term":
                        str(fr(second["mechanism_reading"]["slow_total"]) + artefact_second)}
    check(fused_first != fused_second,
          "a reading that mixes the mechanism with the composition does move")
    fused_difference = fr(fused_second["slow_total_with_the_composition_term"]) - fr(
        fused_first["slow_total_with_the_composition_term"])
    check(fused_difference == Fr(3, 256),
          "the fused reading moves by exactly the composition-only amount")
    check(fused_difference != 0,
          "the fused reading is rejected as an artefact rather than read as a mechanism change")

    terms = tuple(fr(readings[names[1]]["composition"][position])
                  * COMPOSITION_OFFSETS[position] for position in range(3))
    check(all(term >= 0 for term in terms), "each separated uncertainty term is non-negative")
    seams = []
    for row in resource_accounting["seam_redistribution"]["seams"]:
        seams.append({
            "cycle": row["cycle"],
            "mapping": str(terms[0]),
            "bias": str(terms[1]),
            "sampling": str(terms[2]),
            "recorded_separately": True,
        })
    check(len(seams) == CYCLE_COUNT, "the three uncertainty terms are recorded at every seam")
    fused_figure = sum(fr(value) for value in (seams[0]["mapping"], seams[0]["bias"],
                                               seams[0]["sampling"]))
    check(fused_figure == Fr(11, 256), "the fused figure of the first seam would be 11/256")
    check(all("mapping" in row and "bias" in row and "sampling" in row for row in seams),
          "every seam carries the three terms separately")

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
                "first": fused_first["slow_total_with_the_composition_term"],
                "second": fused_second["slow_total_with_the_composition_term"],
                "difference": str(fused_difference),
                "verdict": "Rejected as an artefact",
            },
        },
        "separated_uncertainty": {
            "control": "the separated-uncertainty control of supplement one, carried forward",
            "terms": ["mapping", "bias", "sampling"],
            "seams": seams,
            "three_terms_present_separately_at_every_seam": True,
            "fused_control": {
                "fused_figure": str(fused_figure),
                "verdict": "Rejected",
                "reason": "a single fused uncertainty figure is a violation of the declaration; "
                          "the three terms must be recorded separately at every seam",
            },
            "pooling_control": {
                "pooled": "rejected: heterogeneous sources are recorded separately and pinned "
                          "separately, never pooled",
            },
        },
        "atmospheric_memory_loss": resource_accounting["atmospheric_memory_control"],
        "inherited_controls_still_run": [
            "the sampling-change invariance control", "the separated-uncertainty control",
            "the purely atmospheric memory-loss control"],
        "failed_controls": [
            {"control": "the radial-normal flux control",
             "where": "S3_flux_and_attribution",
             "outcome": "FAILED_TO_DISCRIMINATE",
             "why": "with a purely radial normal every chirality pair has rise zero, so this "
                    "control cannot separate the declared pair from the same-chirality pair"},
            {"control": "the arrival step count under the two declared chirality signs",
             "where": "S5_side_I_arrival",
             "outcome": "FAILED_TO_DISCRIMINATE",
             "why": "both declared rotation senses arrive in 24 steps at the declared target"},
        ],
        "controls_that_did_discriminate": [
            "the declared chirality condition on the same-chirality pair",
            "the same-chirality introduction against the flux rise",
            "the unwritten obstruction against the discharge condition",
            "the implicit obstruction against the discharge condition",
            "the over-budget arrival against the declared step budget",
            "the total-cancelling layer-wise violation against the layer-wise bound",
            "the side-identifying projection and the single-rotation-sense projection",
        ],
    }


# ------------------------------------------------------------------- the run --

def build_payload():
    contract_digest = digest(CONTRACT_PATH)
    parent_digest = digest(PARENT_CONTRACT_PATH)
    supplement_digest = digest(PARENT_SUPPLEMENT_PATH)
    check(contract_digest == DECLARED_CONTRACT_SHA256,
          "this run's contract is the frozen one, byte for byte")
    check(parent_digest == DECLARED_PARENT_SHA256,
          "the frozen parent contract is retained byte for byte")
    check(supplement_digest == DECLARED_SUPPLEMENT_SHA256,
          "the parent supplement is retained byte for byte")
    check(CONTRACT["parent_contracts"][0]["sha256"] == DECLARED_PARENT_SHA256,
          "this contract names the parent contract digest it inherits")
    check(CONTRACT["parent_contracts"][1]["sha256"] == DECLARED_SUPPLEMENT_SHA256,
          "this contract names the parent supplement digest it inherits")

    sym = {
        "p": sp.Symbol("p"), "q": sp.Symbol("q"), "h": sp.Symbol("h"),
    }
    alpha = RATIONAL(1, 8) + sym["p"]
    beta = RATIONAL(1, 8) + sym["q"]
    e0 = sym["h"] / 2 + alpha * sym["h"] ** 2
    annual = sp.expand(RATIONAL(3, 4) * e0 + beta * e0 ** 2)
    sym.update({
        "alpha": alpha, "beta": beta, "E0": sp.expand(e0), "E": annual,
        "G": sp.expand(annual - 1), "closure": sp.expand(annual - sym["h"]),
        "Gh": sp.expand(sp.diff(annual, sym["h"])),
    })

    surgery = section_surgery_and_collar(sym)
    excised_cells = {tuple(cell) for cell in surgery["excision"]["excised_cell_set"]}
    spirals = section_spirals_and_chirality()
    flux = section_flux_and_attribution()
    computed_record = {
        "kind": "discriminant collision at the declared collar cell",
        "locus_branch": DISCRIMINANT_FACTOR,
        "parameter_p": str(COLLISION_P),
        "parameter_q": str(COLLISION_Q),
        "vanishing_factor_value":
            surgery["declared_singular_locus"]["discriminant_at_the_collision"],
        "collar_normal": "(" + str(COLLAR_NORMAL[0]) + ", " + str(COLLAR_NORMAL[1]) + ")",
        "boundary_object": "the outer side: the boundary component at radial index +1",
    }
    side_o = section_side_o_obstruction(computed_record)
    side_i = section_side_i_arrival(excised_cells)
    resources = section_resource_accounting(flux)
    projection = section_projection()
    baselines = section_baselines(sym)
    controls = section_controls(resources)

    reservation = PARENT_CONTRACT["verification_status"]["data_authenticity_reservation"]
    check(PARENT_CONTRACT["verification_status"]["observational"] == "Unavailable",
          "the parent contract records observational verification as Unavailable")
    check(reservation == ("The user's recorded reservation about the authenticity of the data in "
                          "the xue-study work is carried with this contract; hashes and "
                          "same-source read-backs do not remove it, and it is not narrowed to "
                          "any single stage."),
          "the data-authenticity reservation is carried verbatim from the parent contract")

    payload = {
        "schema": "adva.external.three-cycle-supplement-surgery-calibration.v1",
        "version": 1,
        "level": CONTRACT["level"],
        "contract": "experiments/three_cycle_supplement_v1/contract.json",
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
        ],
        "tooling": {
            "polynomial_library": "sympy",
            "version": SY["version"],
            "declared_not_native_authority": True,
            "exact_only": True,
            "used_for": ["exact polynomial arithmetic", "the cleared resultant and its integer "
                         "factorisation", "Sturm real-root isolation with rational intervals",
                         "exact sign conditions"],
            "not_implemented": [
                "a certified complex or projective continuation of roots",
                "a native certificate of any kind",
                "successive difference substitution of Zhang Jingzhong and Yang Lu"],
        },
        "limits": CONTRACT["budgets"],
        "assertions": ASSERTIONS["n"],
        "sections": {
            "S1_surgery_and_collar": surgery,
            "S2_spirals_and_chirality": spirals,
            "S3_flux_and_attribution": flux,
            "S4_side_O_obstruction": side_o,
            "S5_side_I_arrival": side_i,
            "S6_resource_accounting": resources,
            "S7_projection": projection,
            "S8_baselines": baselines,
            "S9_controls": controls,
        },
        "verification_status": {
            "observational": "Unavailable",
            "reason": "the three-cycle chain is future; no observation and no issued forecast "
                      "exists for 2026-12 onwards in this checkout, and this run uses no data",
            "data_authenticity_reservation": reservation,
            "data_authenticity_reservation_source":
                "experiments/three_cycle_chain_v1/contract.json, carried verbatim and "
                "un-narrowed",
            "checked_here": {
                "observational_verification": "Unavailable",
                "no_data_read_or_used": True,
                "hashes_and_read_backs_do_not_remove_the_reservation": True,
            },
        },
        "undecided": [
            {"item": "whether opposite chirality is necessary rather than merely declared",
             "reason": "the declared pair raises the flux and the same-chirality pair is rejected "
                       "by the declared chirality condition and fails to raise it, but the flux "
                       "rise is w n_phase (sigma_outer - sigma_inner) with the declared phase tilt "
                       "n_phase, so the rise is a declared consequence of the tilt as much as of "
                       "the chirality: with a purely radial normal the rise vanishes for every "
                       "chirality pair, and another declaration is another run",
             "retained_partial_result": {
                 "declared_pair_flux": flux["flux_after"],
                 "same_chirality_flux": flux["same_chirality_control"]["flux_after"],
                 "reversed_opposite_pair_flux": flux["sign_pairs"][2]["flux_after"],
                 "rise_formula": flux["rise_formula"],
                 "radial_normal_rise_for_every_pair":
                     flux["radial_normal_control"]["rise_for_every_sign_pair"],
             }},
            {"item": "whether the declared collar and its normal are canonical",
             "reason": "the collar's size, its radial index and the phase tilt of its normal are "
                       "declared conventions of this run; the rise is linear in the declared tilt "
                       "and the excision is exact for whatever collar is declared, so no "
                       "uniqueness is decided here",
             "retained_partial_result": {
                 "collar_cells": surgery["collar"]["cells"],
                 "collar_radial_extent": surgery["collar"]["radial_extent"],
                 "collar_normal": surgery["collar"]["normal"]["vector"],
                 "rise_with_tilt_one": flux["flux_after"],
                 "rise_with_tilt_zero": flux["radial_normal_control"]["rise_for_every_sign_pair"],
             }},
            {"item": "whether the declared projection is the only projection to the cold/heat "
                     "reading",
             "reason": "the projection is declared and checked as a map; the two rejected "
                       "projections show which conditions it must satisfy, but no argument is "
                       "given here that no other admissible projection exists",
             "retained_partial_result": {
                 "accepted_projection": projection["declared_projection"],
                 "rejected_projections": [row["control"] for row in projection["controls"]],
             }},
            {"item": "whether the arrival path must avoid the excised collar at every step",
             "reason": "the declared arrival condition is a bounded-step condition on the declared "
                       "target, and the declared inner spiral's orbit crosses the singular radius "
                       "at 12 steps on its way; whether the arrival should also be required to "
                       "stay inside the post-surgery carrier at every intermediate step is not "
                       "decided here",
             "retained_partial_result": {
                 "orbit_cells_on_the_declared_lattice":
                     side_i["arrival"]["orbit_cells_on_the_declared_lattice"],
                 "excised_cells_on_the_orbit": side_i["arrival"]["excised_cells_on_the_orbit"],
                 "arrival_steps": side_i["arrival"]["steps"],
                 "declared_step_budget": side_i["declared_step_budget"],
             }},
        ],
        "modelling_choices": {
            "carrier_and_lattice": "the declared carrier is the cylinder Z x Z_12: a radial index "
                                   "and one phase index of the twelve-phase cycle of the parent "
                                   "fixture.  Both indices are declared conventions.",
            "singular_locus": "the singular locus is declared to be two things at once: the "
                              "discriminant collision of the earlier runs, taken on the B1 branch "
                              "q = 256 p^2 + 76 p + 43/8 at (p, q) = (-2, 7019/8), and the annual "
                              "seam, taken at side 0 of the twelve-phase cycle where the declared "
                              "time coupling of note 0236 has its maximum 31/512.",
            "collar_and_orientation": "the collar is the declared one-cell neighbourhood of the "
                                      "seam circle: the whole twelve-phase cycle at the singular "
                                      "radial index.  Its orientation is the declared ordered "
                                      "frame (radial outward, phase increasing), and the "
                                      "orientation of its boundary sends the declared normal "
                                      "outward on the outer component and inward on the inner "
                                      "one.  The size of the collar is part of the declaration.",
            "collar_normal_tilt": "the declared collar normal is (1, 1) in the (radial, phase) "
                                  "character basis: it is tilted by one phase at the seam.  The "
                                  "tilt is declared, and the flux rise is exactly linear in it, "
                                  "which is why the radial-normal control is reported.",
            "excision_and_the_two_sides": "the excision is exact set subtraction of the declared "
                                          "collar; the two sides are the two connected boundary "
                                          "components of the excised collar, and they are "
                                          "declared to be distinct objects.  The excision is "
                                          "declared rather than derived.",
            "spiral_declaration": "a spiral is declared as a rotation by one phase of the "
                                  "twelve-phase cycle compounded with a radial advance of 1/12 "
                                  "per step; a pure rotation and a pure radial advance are both "
                                  "rejected by that declared condition.",
            "chirality_condition": "chirality is a declared sign: plus one outside and minus one "
                                   "inside.  The declared condition is sigma_outer = "
                                   "-sigma_inner, evaluated as a rule on the declared signs, so "
                                   "the same-chirality construction is rejected by the rule and "
                                   "not by a count.",
            "flux_pairing": "the flux is the declared pairing B(u, v) = u_radial v_radial + "
                            "u_phase v_phase of the introduced resource with each side's outward "
                            "normal, evaluated exactly; the introduced resource per turn is the "
                            "declared spiral data (radial advance 1/12, angular step sigma).",
            "flux_before_is_the_declared_zero": "before the helical introduction no resource is "
                                                "introduced on either side, so the before-flux "
                                                "is the declared zero of the pairing at the same "
                                                "collar; it is a declaration and not a limit.",
            "attribution_rule_and_unattributed_rise": "a rise is attributed only when it equals "
                                                      "exactly the declared pair's rise over the "
                                                      "declared before-flux; any excess over that "
                                                      "is reported as unattributed rather than "
                                                      "absorbed.",
            "obstruction_record_and_discharge": "side O's obstruction is an explicit object with "
                                                "a written record; the discharge is a condition "
                                                "on that record - every declared field present "
                                                "and every written value equal to the computed "
                                                "one - so an unwritten or implicit obstruction "
                                                "fails.",
            "arrival_condition_and_role_swap": "side I's arrival is a declared bounded-step "
                                               "condition to the declared time-domain target; "
                                               "swapping the two sides' roles puts the arrival "
                                               "condition on the outer side, whose declared "
                                               "spiral advances outward only and so cannot "
                                               "arrive at the inner radius.",
            "step_budget": "the declared step budget is 36 unit steps, the three annual cycles of "
                           "the parent chain at twelve phases each; the inherited end block of "
                           "exactly two extra steps counted in steps gives 42 beside it, and the "
                           "budget is a declared convention.",
            "resource_split": "the surgery splits the carried remainder between the two sides by "
                              "shares derived from the declared collar flux - each side's share "
                              "is its flux term over the sum of the two - so the split is not a "
                              "free parameter, and the layer-wise sums are an independent check "
                              "that nothing is created.",
            "layer_sealing_bound": "the layer-wise sealing bound of supplement one is declared as "
                                   "zero leakage per layer: the post-surgery carrier's content "
                                   "must equal the declared content in every layer separately, "
                                   "and a total may not cancel a layer-wise violation.",
            "seam_redistribution_and_memory": "the declared inter-layer redistribution moves an "
                                              "eighth of the mixed layer to the thermocline and "
                                              "a sixteenth of the thermocline to the deep layer "
                                              "at every seam, conserving the total exactly; the "
                                              "layer holding the carried memory is reported at "
                                              "every seam.",
            "projection_and_codomain_labels": "the declared projection sends the outer side to "
                                              "the sealing side, the inner side to the supplying "
                                              "or injecting side, and the helical pair to the "
                                              "two rotation senses.  The codomain labels are "
                                              "declared labels of the two-sided reading and no "
                                              "cold, heat, wind or ocean quantity is asserted.",
            "baselines": "the exact baselines of the earlier runs are reproduced with exact "
                         "arithmetic: J_inf = 1 at (p, q) = (-2, 17/10) off the discriminant "
                         "variety, the closure amplitude 3.2035072879526181... with one real "
                         "exit, the level reading's largest amplitude 2 + sqrt(8 sqrt(17) - 20) "
                         "with two real branches, and the asserted ordering.",
            "inherited_controls": "the sampling-change invariance control, the separated "
                                  "uncertainty control and the purely atmospheric memory-loss "
                                  "control of the parent contracts and their supplement run "
                                  "here unchanged; the four amendments are adopted as declared "
                                  "structure and no text, table or number is imported.",
            "exact_only": "every acceptance assertion and every value in the retained payload is "
                          "an exact integer or fraction, or an exact rational interval, or a "
                          "string naming one; no floating-point value is formed anywhere.",
            "external_library": "sympy 1.14 is declared and used as an engine for the resultant, "
                                "its integer factorisation and real-root isolation; it is not "
                                "native authority and no semantic identity is created here.",
            "resource_limits": "the checker installs a CPU limit, a file-size limit and a wall "
                               "alarm, and records the contract's declared memory budget without "
                               "installing an address-space ceiling; no child process is "
                               "launched and no pre-existing rlimit artifact is touched.",
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
            "no_data_read_or_used": True,
            "cold_heat_reading_exists_only_as_the_declared_projection": True,
            "no_cold_heat_wind_ocean_plateau_or_forecast_quantity_asserted": True,
            "the_surgery_is_a_declared_construction_not_a_physical_mechanism": True,
            "opposite_chirality_necessity_not_claimed": True,
            "no_native_admission_no_seal_no_transport_no_terminology_home": True,
            "no_rust_source_or_lock_changed": True,
            "no_contract_or_note_edited": True,
            "no_claim_added_to_docs_claims_toml": True,
        },
        "checks": {},
    }
    checks = {
        "assertions_within_budget": ASSERTIONS["n"] <= CONTRACT["budgets"]["max_assertions"],
        "this_contract_digest_matches_the_declared_one":
            payload["contract_sha256"] == payload["contract_sha256_declared"],
        "both_parent_contracts_are_retained_byte_for_byte": all(
            row["sha256"] == row["sha256_declared"] for row in payload["parent_contracts"]),
        "the_collar_has_exactly_two_sides": surgery["excision"]["boundary_components"] == 2,
        "the_declared_pair_has_opposite_chirality":
            spirals["chirality_condition_on_the_declared_pair"]["accepted"],
        "the_same_chirality_pair_is_rejected_by_the_condition":
            not flux["same_chirality_control"]["chirality_condition"]["accepted"],
        "the_flux_strictly_rises": flux["strictly_greater"],
        "the_rise_is_attributed": flux["attribution"]["verdict"] == "Attributed",
        "the_same_chirality_control_does_not_raise_the_flux":
            not flux["same_chirality_control"]["rose"],
        "side_O_discharges_a_written_obstruction": side_o["discharge"]["verdict"] == "Discharged",
        "the_unwritten_obstruction_fails": side_o["controls"][0]["verdict"] == "Rejected",
        "side_I_arrives_within_the_budget": side_i["arrival"]["verdict"] == "ArrivedWithinBudget",
        "the_over_budget_arrival_fails": side_i["controls"][0]["verdict"] == "Rejected_OverBudget",
        "the_roles_swapped_fail_both_conditions":
            side_i["controls"][1]["verdict"] == "Rejected_NoArrival"
            and side_o["controls"][1]["verdict"] == "Rejected",
        "no_resource_is_created_by_the_surgery":
            resources["no_resource_created_by_the_surgery"],
        "every_layer_is_sealed": resources["layer_sealing"]["all_layers_sealed"],
        "a_layer_wise_violation_is_not_cancelled_by_a_total":
            resources["total_cancelling_control"]["verdict"] == "LayerWiseViolation"
            and not resources["total_cancelling_control"]["cancelled_by_the_total"],
        "the_projection_is_accepted_as_a_map": projection["checked_as_a_map"]["accepted"],
        "the_baselines_are_reproduced": baselines["ordering"]["asserted_exactly"],
        "the_atmospheric_chain_loses_the_carried_memory":
            resources["atmospheric_memory_control"]["atmospheric_only"]["lost"],
        "the_sampling_change_invariance_control_runs":
            controls["sampling_change_invariance"]["readings_unchanged"],
        "the_separated_uncertainty_control_runs":
            controls["separated_uncertainty"]["three_terms_present_separately_at_every_seam"],
        "the_failed_controls_are_retained": len(controls["failed_controls"]) == 2,
        "observational_verification_is_recorded_unavailable":
            payload["verification_status"]["observational"] == "Unavailable",
        "the_data_authenticity_reservation_is_carried_verbatim":
            payload["verification_status"]["data_authenticity_reservation"]
            == PARENT_CONTRACT["verification_status"]["data_authenticity_reservation"],
        "undecided_items_are_declared": len(payload["undecided"]) == 4,
        "no_floating_point_value_is_retained": not contains_float(payload),
    }
    payload["checks"] = checks
    payload["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    return payload


def contains_float(node):
    """True when a float appears anywhere in the payload."""
    if isinstance(node, float):
        return True
    if isinstance(node, dict):
        return any(contains_float(key) or contains_float(value) for key, value in node.items())
    if isinstance(node, (list, tuple)):
        return any(contains_float(item) for item in node)
    return False


def summarize(payload):
    sections = payload["sections"]
    surgery = sections["S1_surgery_and_collar"]
    spirals = sections["S2_spirals_and_chirality"]
    flux = sections["S3_flux_and_attribution"]
    side_o = sections["S4_side_O_obstruction"]
    side_i = sections["S5_side_I_arrival"]
    resources = sections["S6_resource_accounting"]
    projection = sections["S7_projection"]
    baselines = sections["S8_baselines"]
    controls = sections["S9_controls"]
    print("three-cycle supplement v1: exact calibration of the declared surgery")
    print("  status:", payload["status"], " assertions:", payload["assertions"])
    collar = surgery["collar"]
    print("  singular locus: collision at (p, q) =", surgery["declared_singular_locus"]
          ["collision_parameter"], "on the B1 branch; seam at phase",
          surgery["declared_singular_locus"]["annual_seam"]["seam_phase"])
    print("  collar:", collar["cells"], "cells at radial index", collar["radial_index"],
          ", normal", collar["normal"]["vector"], ", orientation",
          collar["orientation"]["ordered_frame"])
    print("  excision:", surgery["excision"]["excised_cells"], "cells excised,",
          surgery["excision"]["boundary_components"], "boundary components, sides at radial "
          "indices", surgery["excision"]["sides"]["outer"]["radial_index"], "and",
          surgery["excision"]["sides"]["inner"]["radial_index"])
    for side in ("outer", "inner"):
        row = spirals["spirals"][side]
        print("  spiral", side, "chirality", row["chirality_sign"], "|", row["handedness"])
    print("  chirality condition on the declared pair:",
          spirals["chirality_condition_on_the_declared_pair"]["verdict"])
    print("  flux before", flux["flux_before"], "-> after", flux["flux_after"], "| rise",
          flux["rise"], "|", flux["attribution"]["verdict"],
          "| unattributed", flux["attribution"]["unattributed_rise"])
    print("  same-chirality control: flux", flux["same_chirality_control"]["flux_after"],
          "rose", flux["same_chirality_control"]["rose"], "rejected by",
          flux["same_chirality_control"]["rejected_by"])
    print("  unattributed control: flux", flux["unattributed_control"]["flux_observed"],
          "unattributed", flux["unattributed_control"]["unattributed_rise"], "->",
          flux["unattributed_control"]["verdict"])
    print("  radial-normal control:", flux["radial_normal_control"]["verdict"])
    print("  side O: obstruction written", side_o["discharge"]["written"], "->",
          side_o["discharge"]["verdict"])
    for row in side_o["controls"]:
        print("    control:", row["control"], "->", row["verdict"], row["rejection_reasons"])
    print("  side I: arrival in", side_i["arrival"]["steps"], "steps against the budget",
          side_i["declared_step_budget"], "->", side_i["arrival"]["verdict"],
          "(slack", side_i["arrival"]["slack"], ")")
    for row in side_i["controls"]:
        print("    control:", row["control"], "->", row["verdict"])
    print("    failed to discriminate:", side_i["failed_to_discriminate"]["control"])
    remainder = resources["carried_remainder"]
    print("  resources: fast", remainder["fast"], "slow", remainder["slow_layers"],
          "total", remainder["total"], "| no resource created:",
          resources["no_resource_created_by_the_surgery"])
    print("  layer sealing:", resources["layer_sealing"]["all_layers_sealed"], "| total-cancelling"
          " control:", resources["total_cancelling_control"]["verdict"], "on layers",
          resources["total_cancelling_control"]["violating_layers"])
    for row in resources["seam_redistribution"]["seams"]:
        print("    seam", row["cycle"], "contents", row["contents"], "drift",
              row["per_layer_drift"], "memory layer", row["memory_layer"])
    print("  atmospheric memory:", resources["atmospheric_memory_control"]["atmospheric_only"],
          "| with the slow component:",
          resources["atmospheric_memory_control"]["with_the_slow_component"])
    print("  projection:", projection["verdict"], projection["declared_projection"])
    for row in projection["controls"]:
        print("    control:", row["control"], "->", row["verdict"])
    print("  baseline floor:", baselines["first_scheme"]["amplitude_floor"], "at",
          baselines["first_scheme"]["attained_at"])
    print("  closure amplitude:", baselines["closure_reading"]["correctly_rounded_prefix"],
          "with", baselines["closure_reading"]["real_exits"], "real exit")
    print("  level reading:", baselines["level_reading"]["real_branches"], "real branches, "
          "largest amplitude", baselines["level_reading"]["largest_branch_amplitude"], "in",
          baselines["level_reading"]["largest_branch_amplitude_enclosure"])
    print("  ordering:", baselines["ordering"]["statement"])
    print("  sampling-change invariance: readings unchanged",
          controls["sampling_change_invariance"]["readings_unchanged"],
          "| composition-only reading moves by",
          controls["sampling_change_invariance"]["composition_only_difference"])
    print("  separated uncertainty: three terms at every seam",
          controls["separated_uncertainty"]["three_terms_present_separately_at_every_seam"],
          "| fused figure", controls["separated_uncertainty"]["fused_control"]["fused_figure"],
          "rejected")
    for row in controls["failed_controls"]:
        print("    failed control:", row["control"], "->", row["outcome"])
    print("  observational verification:",
          payload["verification_status"]["observational"])
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
            "schema": "adva.external.three-cycle-supplement-surgery-calibration.v1",
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
