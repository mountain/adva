"""Is (i - e)^(i - e) an integer? One statement per branch, and the modulus and
the phase decide.

Complex powers are multi-valued, so the conjecture is a family of statements
indexed by the branch of the logarithm. This checker decides the ones that can be
decided with exact rational interval arithmetic, derives e and pi from their
series rather than quoting decimals, and reports the rest as Unknown with the
reason.

The refutation of the principal branch is elementary and needs no estimate at
all. Writing z = i - e gives Re z = -e < 0 and Im z = 1 > 0, and arg z > 0, so
both terms of Re(z log z) = Re(z) ln|z| - Im(z) arg(z) are negative. Hence
|z^z| = exp(Re(z log z)) < 1 on the principal branch, and no integer has a
modulus strictly between 0 and 1.

Everything else is an enclosure, not a proof by approximation: every interval
bound below is exact rational arithmetic.
"""
import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
COUNTS = {"assertions": 0, "series_evaluations": 0, "branches_examined": 0}
LIMITS = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


def jsonable(value):
    if isinstance(value, dict):
        return {k: jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if isinstance(value, Interval):
        return jsonable(value.show())      # show() still returns rationals
    if isinstance(value, Fr):
        return str(value)
    return value


# ------------------------------------------------- exact rational enclosures

GRID = {"digits": 45}


def snap_outward(lo, hi):
    """Round outwards onto a fixed rational grid.

    Carrying an exact denominator such as 80! through every later operation makes
    the numerators of the series terms explode. Rounding outwards keeps the true
    value inside the interval while bounding every denominator, which is what
    makes the enclosures both correct and fast.
    """
    scale = 10 ** GRID["digits"]
    # Fr(integer, scale), not integer / scale: dividing two ints in Python 3 is
    # true division and returns a float, which silently reduced this exact grid
    # to double precision until a measured interval width exposed it.
    low = Fr((lo * scale).__floor__(), scale)
    high = Fr(-((-hi * scale).__floor__()), scale)
    return low, high


class Interval:
    """A closed rational interval: lo <= t <= hi for the true value t.

    Every construction rounds outwards onto GRID, so the true value stays inside
    and the endpoints keep bounded denominators.
    """

    __slots__ = ("lo", "hi")

    def __init__(self, lo, hi=None):
        lo = Fr(lo)
        hi = lo if hi is None else Fr(hi)
        check(lo <= hi, "EmptyInterval")
        self.lo, self.hi = snap_outward(lo, hi)

    def __add__(self, other):
        other = as_interval(other)
        return Interval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other):
        other = as_interval(other)
        return Interval(self.lo - other.hi, self.hi - other.lo)

    def __mul__(self, other):
        other = as_interval(other)
        corners = [self.lo * other.lo, self.lo * other.hi,
                   self.hi * other.lo, self.hi * other.hi]
        return Interval(min(corners), max(corners))

    def __neg__(self):
        return Interval(-self.hi, -self.lo)

    def __truediv__(self, other):
        other = as_interval(other)
        check(other.lo > 0 or other.hi < 0, "DivisionByAnIntervalContainingZero")
        return self * Interval(1 / other.hi, 1 / other.lo)

    __radd__ = __add__
    __rmul__ = __mul__

    def __rsub__(self, other):
        return as_interval(other) - self

    def abs_lower(self):
        if self.lo > 0:
            return self.lo
        if self.hi < 0:
            return -self.hi
        return Fr(0)

    def show(self):
        return {"lo": self.lo, "hi": self.hi, "width_digits": digits(self.hi - self.lo)}


def as_interval(x):
    return x if isinstance(x, Interval) else Interval(x)


def digits(width):
    """A crude decimal-digit count of a positive rational width."""
    if width <= 0:
        return None
    count, scale = 0, Fr(1)
    while width < scale and count < 200:
        scale /= 10
        count += 1
    return count


def factorial(n):
    out = 1
    for i in range(2, n + 1):
        out *= i
    return out


def exp_enclose(x, terms):
    """exp of a non-negative rational, by its series with a geometric tail bound."""
    x = Fr(x)
    check(x >= 0, "ExpEnclosureNeedsANonNegativeArgument")
    COUNTS["series_evaluations"] += 1
    total, power = Fr(0), Fr(1)
    for k in range(terms):
        total += power / factorial(k)
        power *= x
    tail = (power / factorial(terms)) / (1 - x / (terms + 1))
    return Interval(total, total + tail)


def exp_reduced(x, terms):
    """exp of a non-negative rational, with argument halving and squaring.

    The series tail bound is useless at large arguments: at x near 43 with eighty
    terms it is over twenty, which at a modulus of 10^14 destroys the enclosure.
    Halving the argument until it is at most one and then squaring keeps the
    relative width near 10^-117 all the way up.
    """
    x = Fr(x)
    check(x >= 0, "ReducedExpNeedsANonNegativeArgument")
    halvings, y = 0, x
    while y > 1:
        y /= 2
        halvings += 1
    out = exp_enclose(y, terms)
    for _ in range(halvings):
        out = out * out
    return out


def exp_interval(x, terms):
    """exp of any rational interval: exp is increasing, so the ends suffice."""
    x = as_interval(x)
    if x.lo >= 0:
        return Interval(exp_reduced(x.lo, terms).lo, exp_reduced(x.hi, terms).hi)
    if x.hi <= 0:
        return Interval(1, 1) / exp_interval(-x, terms)
    return Interval(exp_reduced(Fr(0), terms).lo,
                    exp_reduced(x.hi, terms).hi)


def ln2_enclose(terms):
    """ln 2 by the artanh series at t = 1/3, which converges geometrically."""
    t = Fr(1, 3)
    total, last = Fr(0), 0
    for k in range(1, terms + 1, 2):
        total += t ** k / k
        last = k
    total *= 2
    # The first omitted term is t^(last+2)/(last+2), not t^(terms+2)/(terms+2):
    # when terms is even those differ, and the smaller bound fails to enclose.
    tail = 2 * t ** (last + 2) / ((last + 2) * (1 - t * t))
    return Interval(total, total + tail)


def ln_enclose(y, terms):
    """ln of a rational above 1, by binary reduction and then a fast series.

    ln y = k ln 2 + ln(y / 2^k) with the second term between 0 and ln 2, so the
    series argument is at most 1/3 and the tail decays geometrically.
    """
    y = Fr(y)
    check(y > 1, "LnEnclosureNeedsAnArgumentAboveOne")
    COUNTS["series_evaluations"] += 1
    k, reduced = 0, y
    while reduced >= 2:
        reduced /= 2
        k += 1
    t = (reduced - 1) / (reduced + 1)
    total, last = Fr(0), 0
    for j in range(1, terms + 1, 2):
        total += t ** j / j
        last = j
    total *= 2
    tail = 2 * t ** (last + 2) / ((last + 2) * (1 - t * t))
    local = Interval(total, total + tail)
    return local + ln2_enclose(terms) * Interval(k)


def atan_enclose(t, terms):
    """atan of a rational in (0, 1), by its alternating series with the classic
    remainder bound: the error is smaller than the first omitted term."""
    t = Fr(t)
    check(0 < t < 1, "AtanEnclosureNeedsAnArgumentInTheOpenUnitInterval")
    COUNTS["series_evaluations"] += 1
    total, sign = Fr(0), 1
    for k in range(terms):
        total += sign * t ** (2 * k + 1) / (2 * k + 1)
        sign = -sign
    bound = t ** (2 * terms + 1) / (2 * terms + 1)
    return Interval(total - bound, total + bound)


def pi_enclose(terms):
    """Machin's formula, with the two arctangents enclosed and never evaluated."""
    a = atan_enclose(Fr(1, 5), terms)
    b = atan_enclose(Fr(1, 239), terms)
    return Interval(16) * a - Interval(4) * b


def taylor_sin_enclose(x, terms):
    """sin by Taylor with the Lagrange remainder, valid for every real argument."""
    x = Fr(x)
    COUNTS["series_evaluations"] += 1
    total, power = Fr(0), x
    for k in range(terms):
        total += (-1) ** k * power / factorial(2 * k + 1)
        power *= x * x
    bound = abs(x) ** (2 * terms + 1) / factorial(2 * terms + 1)
    return Interval(total - bound, total + bound)


def taylor_cos_enclose(x, terms):
    x = Fr(x)
    COUNTS["series_evaluations"] += 1
    total, power = Fr(0), Fr(1)
    for k in range(terms):
        total += (-1) ** k * power / factorial(2 * k)
        power *= x * x
    bound = abs(x) ** (2 * terms) / factorial(2 * terms)
    return Interval(total - bound, total + bound)


def interval_distance(left, right):
    """The distance between two closed intervals, zero when they meet."""
    if left.hi < right.lo:
        return right.lo - left.hi
    if right.hi < left.lo:
        return left.lo - right.hi
    return Fr(0)


# ----------------------------------------------------------- the principal value

def constants(series_terms):
    e = exp_enclose(1, series_terms)
    check(e.lo > 2 and e.hi < 3, "TheExponentialEnclosureIsNotUsable")
    pi = pi_enclose(series_terms)
    check(pi.lo > 3 and pi.hi < 4, "ThePiEnclosureIsNotUsable")
    return e, pi


def principal(series_terms):
    """(i - e)^(i - e) on the principal branch, split into exponent and phase.

    z = i - e has Re z = -e, Im z = 1, |z|^2 = 1 + e^2 exactly, and arg z =
    pi - atan(1/e) because z lies in the second quadrant. With A = ln|z| and
    B = arg z, Log z = A + iB and z Log z = (-e A - B) + i(A - e B). So the value
    is exp(-eA - B) times the unit complex number of angle A - eB.
    """
    e, pi = constants(series_terms)
    one_plus_e2 = Interval(1) + e * e
    check(one_plus_e2.lo > 1, "TheSquaredModulusOfZIsNotAboveOne")
    a = Interval(ln_enclose(one_plus_e2.lo, series_terms).lo / 2,
                 ln_enclose(one_plus_e2.hi, series_terms).hi / 2)
    one_over_e = Interval(1) / e
    atan_part = Interval(atan_enclose(one_over_e.lo, series_terms).lo,
                         atan_enclose(one_over_e.hi, series_terms).hi)
    b = pi - atan_part
    return {"e": e, "pi": pi, "a": a, "b": b,
            "real_exponent": -e * a - b, "phase": a - e * b,
            "one_plus_e2": one_plus_e2}


def consistency_checks(parts, series_terms):
    """Checks on the enclosure code itself, not on the conjecture."""
    # A really is the logarithm of the modulus: exponentiating it must return
    # the squared modulus of z
    squared = exp_interval(parts["a"] * Interval(2), series_terms)
    gap = interval_distance(squared, parts["one_plus_e2"])
    check(gap == 0, "TheLogarithmAndTheSquaredModulusDisagree")
    # and the sine and cosine enclosures must respect the Pythagorean identity
    mid = (parts["phase"].lo + parts["phase"].hi) / 2
    sin_p = taylor_sin_enclose(mid, series_terms)
    cos_p = taylor_cos_enclose(mid, series_terms)
    norm = sin_p * sin_p + cos_p * cos_p
    check(norm.lo <= 1 <= norm.hi, "TheSineAndCosineEnclosuresAreInconsistent")
    # B is an angle: it must lie strictly between pi/2 and pi
    check(parts["b"].lo > parts["pi"].lo / 2, "TheArgumentIsNotInTheSecondQuadrant")
    check(parts["b"].hi < parts["pi"].lo, "TheArgumentIsNotBelowPi")
    check_against_published("Exponential", parts["e"], "e")
    check_against_published("Pi", parts["pi"], "pi")
    check_against_published("LnTwo", ln2_enclose(series_terms), "ln2")
    return {"squared_modulus_recovered": squared, "pythagorean_norm": norm,
            "published_constants_cross_checked": ["e", "pi", "ln2"],
            "note": "the published digits are imported for this cross-check; the "
                    "constant itself is derived from its series"}


def nearest_multiple_of_pi(value, pi, span=3):
    """Whether a multiple of pi can lie in the interval, and the least distance."""
    j_lo = int(value.lo / pi.hi) - span
    j_hi = int(value.hi / pi.lo) + span
    best, inside = None, None
    for j in range(j_lo, j_hi + 1):
        candidate = Interval(j) * pi
        distance = interval_distance(value, candidate)
        if distance == 0 and inside is None:
            inside = j
        if best is None or distance < best:
            best = distance
    return {"contains_a_multiple_of_pi": inside is not None,
            "inside_index": inside, "least_distance": best}


PUBLISHED = {
    # Imported for a cross-check of the series code only, at a length short
    # enough to be certain of. Each entry is a truncation of the classical
    # constant together with the number of digits before its decimal point, so
    # that the enclosure can be compared at the published precision.
    "e": ("2718281828459045235360287", 1),
    "pi": ("3141592653589793238462643", 1),
    "ln2": ("6931471805599453094172321", 0),
}


def check_against_published(label, enclosure, key):
    """The derived enclosure must agree with the published digits at their own
    precision. A containment test is not available here: it would need the
    published string to be far longer than the enclosure is wide."""
    digits, integer_digits = PUBLISHED[key]
    places = len(digits) - integer_digits
    truncated = Fr(int(digits), 10 ** places)
    tolerance = Fr(1, 10 ** (places - 1))
    check(abs(enclosure.lo - truncated) <= tolerance,
          f"The{label}EnclosureLowerEndDisagreesWithThePublishedDigits")
    check(abs(enclosure.hi - truncated) <= tolerance,
          f"The{label}EnclosureUpperEndDisagreesWithThePublishedDigits")
    return {"key": key, "published_places": places,
            "agreement_within": str(tolerance),
            "agreement_decimals": places - 1}


def nearest_integer(value):
    """The nearest integer to an interval, and the certified distance to it."""
    mid = (value.lo + value.hi) / 2
    floor, ceil = mid.__floor__(), -((-mid).__floor__())
    best = None
    for n in {int(floor), int(ceil), int(floor) - 1, int(ceil) + 1}:
        distance = interval_distance(value, Interval(n))
        if best is None or distance < best[1]:
            best = (n, distance)
    return best


def integers_inside(value):
    """Every integer lying in the interval, or None when the width is at least 1.

    A width of at least one cannot decide integrality at all, and that is a
    precision limitation rather than a verdict, so it is reported as such.
    """
    if value.hi - value.lo >= 1:
        return None
    low = -((-value.lo).__floor__())        # ceil
    high = value.hi.__floor__()
    if high < low:
        return []
    return [int(n) for n in range(int(low), int(high) + 1)]


def branch_table(parts, series_terms, branch_range):
    """Every branch: log gains 2 pi i k, so the value gains exp(-2 pi k) and the
    phase gains -2 pi k e."""
    rows = []
    for k in range(branch_range[0], branch_range[1] + 1):
        COUNTS["branches_examined"] += 1
        real_exponent = parts["real_exponent"] - parts["pi"] * Interval(2 * k)
        phase = parts["phase"] - Interval(2) * parts["pi"] * Interval(k) * parts["e"]
        phase_gap = nearest_multiple_of_pi(phase, parts["pi"])
        modulus = exp_interval(real_exponent, series_terms)
        inside = integers_inside(modulus)
        nearest, miss = nearest_integer(modulus)
        row = {"branch_index": k, "real_exponent": real_exponent, "phase": phase,
               "modulus": modulus, "nearest_integer_to_the_modulus": nearest,
               "distance_to_that_integer": miss,
               "integers_inside_the_modulus_enclosure": inside,
               "phase_condition_holds": phase_gap["contains_a_multiple_of_pi"],
               "phase_least_distance_to_a_multiple_of_pi": phase_gap["least_distance"],
               "phase_inside_index": phase_gap["inside_index"]}
        if modulus.hi < 1:
            row["verdict"] = "Refuted"
            row["reason"] = ("the modulus is strictly between 0 and 1, and no integer "
                             "has such a modulus")
        elif inside is None:
            row["verdict"] = "Unknown"
            row["reason"] = ("the modulus enclosure is wider than one unit at this "
                             "magnitude, so integrality is not decided here")
        elif not inside:
            row["verdict"] = "Refuted"
            row["reason"] = ("the modulus enclosure contains no integer and is "
                             "narrower than one unit, so the modulus is not integral")
        elif not row["phase_condition_holds"]:
            row["verdict"] = "Refuted"
            row["reason"] = "the phase is not a multiple of pi, by a certified gap"
        else:
            row["verdict"] = "Unknown"
            row["reason"] = ("both conditions are identities between e, pi and a "
                             "logarithm of an integer that no theorem available here "
                             "supplies")
        rows.append(row)
    return rows


# ------------------------------------------------------------------- the run

def run(contract):
    o = contract["objects"]
    terms = o["series_terms"]
    parts = principal(terms)
    consistency = consistency_checks(parts, terms)

    # the principal branch is refuted, and by a certified margin
    modulus = exp_interval(parts["real_exponent"], terms)
    check(parts["real_exponent"].hi < 0, "TheRealExponentIsNotNegative")
    check(parts["e"].lo > 2 and parts["pi"].lo > 3, "TheElementaryBoundsAreUnavailable")
    check(modulus.hi < Fr(1, 1), "ThePrincipalModulusIsNotBelowOne")
    # A > ln 2 and B > 3/2 give exp(-(eA+B)) < exp(-(2 ln 2 + 3/2)) < 1/10
    check(modulus.hi < Fr(1, 10), "TheCertifiedOneTenthBoundFailed")

    ladder = []
    for digits_target in o["enclosure_ladder"]:
        terms_here = max(30, digits_target + 30)
        p = principal(terms_here)
        m = exp_interval(p["real_exponent"], terms_here)
        ladder.append({"target_digits": digits_target, "series_terms": terms_here,
                       "modulus_upper": m.hi, "below_one": bool(m.hi < 1),
                       "below_one_tenth": bool(m.hi < Fr(1, 10))})
        check(m.hi < 1, "TheLadderLostTheRefutation")

    rows = branch_table(parts, terms, o["branch_range"])
    refuted = [r for r in rows if r["verdict"] == "Refuted"]
    unknown = [r for r in rows if r["verdict"] == "Unknown"]

    return jsonable({
        "status": "ExternalExactPass",
        "native_status": "NotRun",
        "conjecture": "(i - e)^(i - e) is exactly an integer, read as a family of "
                      "statements indexed by the branch of the logarithm",
        "constants": {"e": parts["e"], "pi": parts["pi"],
                      "e_source": "the exponential series at one",
                      "pi_source": "Machin's formula from two arctangent series",
                      "series_terms": terms},
        "principal_branch": {
            "a_is_the_log_of_the_modulus": parts["a"],
            "b_is_the_argument": parts["b"],
            "rational_exponent": parts["real_exponent"],
            "phase": parts["phase"],
            "modulus": modulus,
            "verdict": "Refuted",
            "reason": "Re z = -e < 0 and arg z > 0, so both terms of "
                      "Re(z log z) are negative and the modulus is exp(negative), "
                      "strictly between 0 and 1; no integer has such a modulus",
        },
        "elementary_bound": {
            "a_lower": "A = ln(1+e^2)/2 > ln 2 because 1 + e^2 > 4",
            "b_lower": "B = pi - atan(1/e) > pi/2 > 3/2",
            "conclusion": "e A + B > 2 ln 2 + 3/2, so |z^z| < e^(-3/2)/4 < 1/10",
            "certified_upper_bound": "1/10",
        },
        "consistency_checks": consistency,
        "enclosure_ladder": ladder,
        "branches": rows,
        "verdict_counts": {"refuted": len(refuted), "unknown": len(unknown)},
        "counts": dict(COUNTS),
    })


def main():
    contract = json.loads((HERE / "contract.json").read_text())
    LIMITS.update(contract["budget"])
    report = run(contract)
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: report[k] for k in
                      ("status", "verdict_counts", "counts")}, indent=1))
    print("principal modulus :", report["principal_branch"]["modulus"])
    print("principal verdict :", report["principal_branch"]["verdict"])
    print("branch table:")
    for r in report["branches"]:
        lo = float(Fr(r["real_exponent"]["lo"]))
        hi = float(Fr(r["real_exponent"]["hi"]))
        gap = float(Fr(r["phase_least_distance_to_a_multiple_of_pi"]))
        print("  k=%+d  ln|z|=%+.9f  |z|=%.9f  nearest integer %-4d off by %.2e  %s" % (
            r["branch_index"], lo, __import__("math").exp(lo),
            r["nearest_integer_to_the_modulus"],
            float(Fr(r["distance_to_that_integer"])), r["verdict"]))


if __name__ == "__main__":
    main()

