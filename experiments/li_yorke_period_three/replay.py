"""Exact external calibration for the period-three interval graph.

This checker never constructs, reads or authorizes an Adva semantic identity.
It uses exact integers and Fractions only; no floating-point value enters any
acceptance test. The theorems it leans on (the 1975 Li-Yorke statement, the
Sharkovsky ordering, the intermediate value theorem) are imported, not reproved.
"""
from fractions import Fraction as F
import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import time

HERE = Path(__file__).resolve().parent
COUNTS = {"assertions": 0, "pieces": 0, "roots": 0, "pairs": 0}
LIMITS = {}
INSTALLED = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


# ---------------------------------------------------------------- exact 2x2 data

def mm(a, b):
    return ((a[0][0] * b[0][0] + a[0][1] * b[1][0], a[0][0] * b[0][1] + a[0][1] * b[1][1]),
            (a[1][0] * b[0][0] + a[1][1] * b[1][0], a[1][0] * b[0][1] + a[1][1] * b[1][1]))


def mpow(a, n):
    r = ((1, 0), (0, 1))
    for _ in range(n):
        r = mm(r, a)
    return r


def trace(a):
    return a[0][0] + a[1][1]


def charpoly(a):
    """(leading, linear, constant) coefficients of det(tI - a)."""
    return (1, -trace(a), a[0][0] * a[1][1] - a[0][1] * a[1][0])


def fib(n):
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a


def lucas(n):
    a, b = 2, 1
    for _ in range(n):
        a, b = b, a + b
    return a


# ------------------------------------------------------- the tent map on [0,1]

def tent(x):
    """T(x) = 1 - |2x - 1|, evaluated exactly; 2x on [0,1/2], 2-2x on [1/2,1]."""
    if not (0 <= x <= 1):
        raise ValueError("TentDomain")
    return 2 * x if x <= F(1, 2) else 2 - 2 * x


def tent_iter(x, n):
    for _ in range(n):
        x = tent(x)
    return x


def tent_image(p, q):
    """Exact image of [p,q] under the piecewise-affine tent map."""
    half = F(1, 2)
    if q <= half:
        return (tent(p), tent(q))
    if p >= half:
        return (tent(q), tent(p))
    lo = min(tent(p), tent(q))
    return (lo, tent(half))


def contains(outer, inner):
    return outer[0] <= inner[0] and inner[1] <= outer[1]


# ------------------------------------------------------------- exact controls

def circ_dist(u, v):
    d = abs(u - v) % 1
    return min(d, 1 - d)


def rotate(x, k, d):
    return (x + F(k, d)) % 1


def run(contract):
    start = time.perf_counter_ns()
    o = contract["objects"]
    n_max = o["max_matrix_power"]
    depth_max = o["max_tent_depth"]

    # --- Group 1: the two exact matrices -------------------------------------
    a_graph = tuple(tuple(r) for r in o["li_yorke_interval_graph"])
    m_golden = tuple(tuple(r) for r in o["golden_one_hole_matrix"])
    swap = tuple(tuple(r) for r in o["basis_swap"])
    atlas_square = tuple(tuple(r) for r in o["atlas_matrix_square"])
    wrong = tuple(tuple(r) for r in o["wrong_matrix_control"])

    check(charpoly(a_graph) == (1, -1, -1), "IntervalGraphCharacteristic")
    check(charpoly(m_golden) == (1, -1, -1), "GoldenMatrixCharacteristic")
    check(charpoly(a_graph) == charpoly(m_golden), "SharedCharacteristicPolynomial")
    check(mm(mm(swap, a_graph), swap) == m_golden, "BasisSwapDoesNotConjugate")
    check(mm(swap, swap) == ((1, 0), (0, 1)), "SwapIsInvolution")
    check(mm(m_golden, m_golden) == atlas_square, "AtlasSquareMismatch")
    check(trace(atlas_square) == 3, "AtlasTraceMismatch")
    check(charpoly(atlas_square) == (1, -3, 1), "AtlasCharacteristicMismatch")
    check(charpoly(wrong) == (1, -2, -1), "WrongMatrixControlVoid")
    check(charpoly(wrong) != charpoly(a_graph), "WrongMatrixControlNotRefused")

    for n in range(1, n_max + 1):
        check(mpow(m_golden, n) == ((fib(n + 1), fib(n)), (fib(n), fib(n - 1))), "FibonacciPowerMismatch")
        check(trace(mpow(a_graph, n)) == lucas(n), "LucasClosedWalkMismatch")
        check(lucas(n) <= 2 ** n, "LucasExceedsTentCount")

    matrix_checks_ns = time.perf_counter_ns() - start

    # --- Group 2: derive the interval graph from a concrete exact 3-cycle -----
    a, b, c = (F(s) for s in o["tent_cycle_a"])
    d = tent_iter(a, 3)
    check(d == a, "CycleDoesNotClose")
    check(d <= a < b < c, "LiYorkeHypothesisViolated")
    check(tent(a) == b and tent(b) == c and tent(c) == a, "CycleOrbitMismatch")
    check(len({a, b, c}) == 3, "CycleNotPeriodThree")
    check(tent(a) != a, "CyclePointFixed")

    i1 = (a, b)
    i2 = (b, c)
    check(contains(tent_image(*i1), i2), "MissingCoveringI1ToI2")
    check(not contains(tent_image(*i1), i1), "UnexpectedCoveringI1ToI1")
    check(contains(tent_image(*i2), i1), "MissingCoveringI2ToI1")
    check(contains(tent_image(*i2), i2), "MissingCoveringI2ToI2")
    intervals = [i1, i2]
    derived = tuple(
        tuple(1 if contains(tent_image(*src), dst) else 0 for dst in intervals)
        for src in intervals
    )
    check(derived == a_graph, "DerivedIntervalGraphMismatch")
    covering_ns = time.perf_counter_ns() - start

    # --- Group 3: every period occurs, exactly, by full branches -------------
    fixed_counts = {}
    least_period = {}
    for n in range(1, depth_max + 1):
        roots = set()
        for k in range(2 ** n):
            COUNTS["pieces"] += 1
            p, q = F(k, 2 ** n), F(k + 1, 2 ** n)
            vp, vq = tent_iter(p, n), tent_iter(q, n)
            check({vp, vq} == {F(0), F(1)}, "NotAFullBranch")
            slope = (vq - vp) / (q - p)
            check(abs(slope) == 2 ** n, "BranchSlopeMismatch")
            x = (slope * p - vp) / (slope - 1)
            check(0 <= x <= 1, "RootOutsideInterval")
            check(tent_iter(x, n) == x, "RootNotFixed")
            roots.add(x)
        COUNTS["roots"] += len(roots)
        check(len(roots) == 2 ** n, "FixedPointCountMismatch")
        fixed_counts[n] = len(roots)
        exact_n = 0
        for x in roots:
            if all(tent_iter(x, dv) != x for dv in range(1, n) if n % dv == 0):
                exact_n += 1
        least_period[n] = exact_n
    for n in (3, 5, 7):
        check(fixed_counts[n] == 2 ** n, "PeriodCountMismatch")
        check(least_period[n] > 0, "NoPointOfLeastPeriod")
        check(least_period[n] == fixed_counts[n] - 2, "LeastPeriodCountMismatch")
    for n in range(1, depth_max + 1):
        check(lucas(n) <= fixed_counts[n], "LucasBoundViolated")

    period_checks_ns = time.perf_counter_ns() - start

    # --- Group 4: control one, the golden one-hole map is tame ---------------
    lo, hi = (F(s) for s in o["golden_one_hole_interval"])

    def one_hole(x):
        return 1 + 1 / x

    check(one_hole(lo) == 2 and one_hole(hi) == F(3, 2), "OneHoleEndpointMismatch")
    check(one_hole(hi) <= one_hole(lo), "OneHoleNotDecreasing")
    check(lo <= one_hole(hi) and one_hole(lo) <= hi, "OneHoleNotASelfMap")
    for x in (F(1), F(6, 5), F(4, 3), F(3, 2), F(8, 5), F(13, 8), F(2)):
        for y in (F(1), F(6, 5), F(4, 3), F(3, 2), F(8, 5), F(13, 8), F(2)):
            if x < y:
                check(one_hole(x) > one_hole(y), "OneHoleMonotonicityCounterexample")
    # F(F(x)) = (2x+1)/(x+1) exactly, checked on exact samples and as coefficients.
    def poly_mul(p, q):
        out = [0] * (len(p) + len(q) - 1)
        for i, pi in enumerate(p):
            for j, qj in enumerate(q):
                out[i + j] += pi * qj
        return tuple(out)

    def poly_sub(p, q):
        n = max(len(p), len(q))
        return tuple((p[i] if i < len(p) else 0) - (q[i] if i < len(q) else 0) for i in range(n))

    for x in (F(1), F(3, 2), F(2), F(7, 5), F(9, 4)):
        check(one_hole(one_hole(x)) == (2 * x + 1) / (x + 1), "SecondIterateRationalForm")
    numerator = (1, 2)          # 2x + 1, little-endian in x
    denominator = (1, 1)        # x + 1, little-endian in x
    # charpoly is big-endian in t; its negation in little-endian in x must equal
    # the numerator of F(F(x)) - x, which is -(x^2 - x - 1).
    expected = tuple(reversed(tuple(-v for v in charpoly(m_golden))))
    observed = poly_sub(numerator, poly_mul((0, 1), denominator))
    check(observed == (1, 1, -1), "TwoCycleNumeratorMismatch")
    check(observed == expected, "TwoCyclePolynomialDiffersFromGoldenMatrix")
    # x^2 - x - 1 has no rational root and exactly one root inside [1,2].
    def poly(x):
        return x * x - x - 1

    check(poly(1) != 0 and poly(-1) != 0, "RationalRootNotRefused")
    check(poly(F(8, 5)) < 0 < poly(F(13, 8)), "GoldenBracketMismatch")
    check(poly(-1) > 0 > poly(0), "NegativeRootBracketMismatch")
    check(poly(F(1)) < 0 < poly(F(2)), "OneHoleRootBracketMismatch")
    check(charpoly(m_golden) == (1, -1, -1), "TwoCyclePolynomialDiffersFromMatrix")

    # --- Group 5: control two, the third-turn rotation is an isometry --------
    den = o["rotation_denominator"]
    grid = [F(k, 12) for k in range(12)]
    for x in grid:
        check(rotate(rotate(rotate(x, 1, den), 1, den), 1, den) == x, "RotationCubeNotIdentity")
        check(rotate(x, 1, den) != x, "RotationHasFixedPoint")
        check(rotate(rotate(x, 1, den), 1, den) != x, "RotationHasTwoCycle")
        for y in grid:
            COUNTS["pairs"] += 1
            check(circ_dist(rotate(x, 1, den), rotate(y, 1, den)) == circ_dist(x, y), "RotationNotIsometry")
            if x != y:
                check(circ_dist(x, y) > 0, "DistinctGridPointsCollide")
    control_ns = time.perf_counter_ns() - start

    return {
        "status": "ExternalExactPass",
        "native_status": "NotRun",
        "shared_characteristic": list(charpoly(a_graph)),
        "interval_graph": [list(r) for r in a_graph],
        "golden_matrix": [list(r) for r in m_golden],
        "atlas_matrix_square_trace": trace(atlas_square),
        "atlas_matrix_square_characteristic": list(charpoly(atlas_square)),
        "wrong_matrix_control_characteristic": list(charpoly(wrong)),
        "tent_cycle": [str(v) for v in (a, b, c, d)],
        "derived_interval_graph": [list(r) for r in derived],
        "fixed_point_counts": {str(k): v for k, v in fixed_counts.items()},
        "least_period_counts": {str(k): v for k, v in least_period.items()},
        "lucas_lower_bounds": {str(n): lucas(n) for n in range(1, depth_max + 1)},
        "one_hole_self_map_image": [str(one_hole(hi)), str(one_hole(lo))],
        "one_hole_two_cycle_polynomial": [1, -1, -1],
        "golden_bracket": [str(F(8, 5)), str(F(13, 8))],
        "one_hole_cycle_roots_in_interval": 1,
        "rotation_isometry_grid": len(grid),
        "rotation_period_exactly_three": str(F(1, 4)),
        "matrix_checks_ns": matrix_checks_ns,
        "covering_checks_ns": covering_ns,
        "period_checks_ns": period_checks_ns,
        "control_checks_ns": control_ns,
        "construction_and_checks_ns": time.perf_counter_ns() - start,
        "counts": dict(COUNTS),
    }


def install_limits():
    for name, key in (("RLIMIT_CPU", "cpu_seconds"), ("RLIMIT_AS", "memory_bytes"),
                      ("RLIMIT_FSIZE", "output_bytes")):
        try:
            resource.setrlimit(getattr(resource, name), (LIMITS[key], LIMITS[key]))
            INSTALLED[name] = "installed"
        except (ValueError, OSError) as error:  # recorded, not hidden
            INSTALLED[name] = "refused: %s" % error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = (HERE / "contract.json").read_bytes()
    contract = json.loads(data)
    LIMITS.update(contract["budget"])
    install_limits()
    signal.alarm(LIMITS["wall_seconds"])
    report = run(contract)
    report["installed_limits"] = dict(INSTALLED)
    report["contract_sha256"] = hashlib.sha256(data).hexdigest()
    report["code_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["rss_high_water_KiB_before_codec"] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    start = time.perf_counter_ns()
    encoded = json.dumps(report, default=str, sort_keys=True, indent=2) + "\n"
    decoded = json.loads(encoded)
    check(decoded["status"] == report["status"], "SerializationStatus")
    codec_ns = time.perf_counter_ns() - start
    if len(encoded.encode()) > LIMITS["output_bytes"]:
        raise RuntimeError("Unknown: output budget")
    with args.output.open("x") as output:
        output.write(encoded)
    print(json.dumps({"codec_ns": codec_ns,
                      "assertions_including_codec": COUNTS["assertions"],
                      "output_bytes": len(encoded.encode()),
                      "rss_high_water_KiB_final": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))


if __name__ == "__main__":
    main()
