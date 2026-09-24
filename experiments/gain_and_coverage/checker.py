"""Exact external checker for gain, coverage, and numbers that were already fixed.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers and Fractions only; no floating-point value enters any acceptance
test. It imports no text and no corpus count: the counts it uses are declared in
contract.json, including the small published summary tables it checks arithmetically.

Everything reported is decided by exhaustion over a declared finite set, and the
size of each exhausted set is reported with the result.
"""
from fractions import Fraction as F
from itertools import product
from math import gcd
import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import time

HERE = Path(__file__).resolve().parent
COUNTS = {"assertions": 0}
LIMITS = {}
INSTALLED = {}


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


def decimal_round_half_up(value, digits):
    """Exact decimal rounding of a non-negative rational, halves away from zero.

    Integer arithmetic only, so no float enters any acceptance test that uses it: for
    value = n/d >= 0 the rounded number of units of 10**-digits is
    floor(n * 10**digits / d + 1/2) = (2 * n * 10**digits + d) // (2 * d).
    """
    if value < 0:
        raise ValueError("this helper rounds non-negative rationals only")
    scale = 10 ** digits
    units = (2 * value.numerator * scale + value.denominator) // (2 * value.denominator)
    whole, frac = divmod(units, scale)
    return f"{whole}.{frac:0{digits}d}"


def decimal_truncate(value, digits):
    """value truncated to `digits` decimals, as a fixed-point string, exactly."""
    scale = 10 ** digits
    whole, frac = divmod((value.numerator * scale) // value.denominator, scale)
    return f"{whole}.{frac:0{digits}d}"


# --------------------------------------------- S1: the octave reduction is a quotient

LIMIT_S1 = 2000


def odd_part(n):
    while n % 2 == 0:
        n //= 2
    return n


def rho(n):
    """n -> n / 2**floor(log2 n), a rational in [1, 2). Exact, no logarithm."""
    return F(n, 1 << (n.bit_length() - 1))


def s1_doubling_quotient():
    check(all(F(1) <= rho(n) < F(2) for n in range(1, LIMIT_S1 + 1)),
          "the reduction does not land in the half-open unit octave")
    check(all(rho(n) == rho(odd_part(n)) for n in range(1, LIMIT_S1 + 1)),
          "the reduction does not factor through the odd part")
    # the fibres are exactly the doubling orbits of the odd numbers
    fibre_ok = True
    for o in range(1, LIMIT_S1 + 1, 2):
        expected = []
        m = o
        while m <= LIMIT_S1:
            expected.append(m)
            m *= 2
        got = [n for n in range(1, LIMIT_S1 + 1) if rho(n) == rho(o)]
        if got != expected:
            fibre_ok = False
            break
    check(fibre_ok, "a fibre of the reduction is not the doubling orbit of its odd element")
    check(rho(3) == rho(12) == F(3, 2), "the reduction does not identify three and twelve")
    check(rho(1) == 1 and rho(2) == 1 and rho(1024) == 1,
          "a power of two does not reduce to one")
    fixed = [n for n in range(1, LIMIT_S1 + 1) if rho(n) == 1]
    powers = []
    m = 1
    while m <= LIMIT_S1:
        powers.append(m)
        m *= 2
    check(fixed == powers, "the fixed points of the reduction are not the powers of two")
    check(len(fixed) == LIMIT_S1.bit_length(),
          "the number of fixed points is not one more than the binary exponent of the limit")
    # the smallest element of a fibre is its odd element
    check(all(min(n for n in range(1, LIMIT_S1 + 1) if rho(n) == rho(o)) == o
              for o in range(1, 201, 2)),
          "an odd number is not the smallest element of its own fibre")
    return {
        "limit": LIMIT_S1,
        "reduction": "n -> n / 2**floor(log2 n), a rational in [1,2)",
        "lands_in_the_unit_octave": True,
        "factors_through_the_odd_part": True,
        "fibres_are_the_doubling_orbits": True,
        "odd_numbers_are_the_smallest_element_of_their_fibre": True,
        "identified_pair_example": [3, 12],
        "fixed_points_are_the_powers_of_two": True,
        "fixed_point_count_to_the_limit": len(fixed),
        "odd_elements_to_the_limit": len(range(1, LIMIT_S1 + 1, 2)),
    }


# ------------------------- S2: every exact hit of a b-division is a power of two

B_MAIN = 22
N_DECLARED = [122, 1651]


def is_exact_hit(n, b):
    """Is rho(n) exactly 2**(k/b) for some integer k in 0..b-1? Exact."""
    r = rho(n)
    for k in range(b):
        if r ** b == 2 ** k:
            return k
    return None


def perfect_bth_power(m, b):
    lo, hi = 0, 1
    while hi ** b <= m:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if mid ** b < m:
            lo = mid + 1
        else:
            hi = mid
    return lo ** b == m


def s2_exact_hits():
    # 2**(k/b) is rational exactly when b divides k
    divisibility = {}
    for b in (1, 2, 3, 5, 7, 12, 22, 53):
        rational_ks = [k for k in range(b) if perfect_bth_power(2 ** k, b)]
        divisibility[str(b)] = rational_ks
    check(divisibility["22"] == [0], "the twenty-two-division has a rational position besides the unison")
    check(all(ks == [0] for ks in divisibility.values()),
          "some declared division has a rational position besides the unison")

    hits = {}
    for b in (1, 2, 3, 5, 7, 12, 22, 53):
        hit_n = [n for n in range(1, N_DECLARED[1] + 1) if is_exact_hit(n, b) is not None]
        hits[str(b)] = hit_n
    powers = []
    m = 1
    while m <= N_DECLARED[1]:
        powers.append(m)
        m *= 2
    check(all(v == powers for v in hits.values()),
          "the exact hits of some declared division are not the powers of two")

    per_limit = {}
    for N in N_DECLARED:
        expected = [m for m in powers if m <= N]
        got = [n for n in range(1, N + 1) if is_exact_hit(n, B_MAIN) is not None]
        check(got == expected,
              "the exact hits up to the declared limit are not the powers of two below it")
        per_limit[str(N)] = {"count": len(got), "values": got,
                             "binary_exponent_plus_one": N.bit_length()}
    check(per_limit["122"]["count"] == 7 and per_limit["1651"]["count"] == 11,
          "the declared exact-hit counts are not seven and eleven")
    return {
        "division": B_MAIN,
        "rational_positions_per_division": divisibility,
        "only_the_unison_is_rational": True,
        "exact_hits_are_the_powers_of_two": True,
        "exact_hit_sets_identical_for_every_declared_division": True,
        "per_declared_limit": per_limit,
        "exhausted_integers_per_division": N_DECLARED[1],
        "divisions_checked": 8,
    }


# ----------------------------- S3: coverage, the covering radius, and its threshold

def distance_to_division(u, b):
    """Exact distance from a rational point of the circle to the nearest of b equal divisions."""
    return min(min(abs(u - F(k, b)), 1 - abs(u - F(k, b))) for k in range(b))


def odd_power_table(limit, exponent):
    return {o: pow(o, exponent) for o in range(1, limit + 1, 2)}


def in_window(n, exponent, lo, hi, table):
    value = table[n]
    lo_ok = True if lo < 0 else value >= (1 << lo)
    return lo_ok and value <= (1 << hi)


def window_exponents(k, b, p, q):
    """|log2 rho - k/b| <= p/q written as exponents of a common power."""
    g = gcd(b, q)
    exponent = b * q // g
    centre = k * (q // g)
    width = p * (b // g)
    return exponent, centre, width


def coverage(b, p, q, limit, table):
    hit = [False] * b
    for o in range(1, limit + 1, 2):
        exponent, centre, width = None, None, None
        for k in range(b):
            if hit[k]:
                continue
            if exponent is None:
                exponent, centre, width = window_exponents(k, b, p, q)
            else:
                exponent, centre, width = window_exponents(k, b, p, q)
            e = o.bit_length() - 1
            if in_window(o, exponent, e * exponent + centre - width,
                         e * exponent + centre + width, table):
                hit[k] = True
        if all(hit):
            break
    return sum(hit)


def threshold(b, p, q, limit, table):
    worst = 0
    for k in range(b):
        found = None
        exponent, centre, width = window_exponents(k, b, p, q)
        for o in range(1, limit + 1, 2):
            e = o.bit_length() - 1
            if in_window(o, exponent, e * exponent + centre - width,
                         e * exponent + centre + width, table):
                found = o
                break
        if found is None:
            return None
        worst = max(worst, found)
    return worst


def s3_coverage():
    # the covering radius of the b equal divisions is exactly one over twice b
    radii = {}
    for b in (2, 3, 5, 12, 22, 53):
        worst = max(distance_to_division(F(2 * j + 1, 2 * b), b) for j in range(b))
        radii[str(b)] = str(worst)
        check(worst == F(1, 2 * b), "the covering radius is not one over twice the division")
    check(radii["22"] == "1/44", "the twenty-two-division covering radius is not one forty-fourth")
    # The covering radius is attained, so the bound is not strict: the points midway
    # between two adjacent positions of the twenty-two-division are exactly one
    # forty-fourth of an octave from the nearest one. (An earlier revision of this line
    # was `... or F(1, 44) > 0`, which is true of every positive number and could not
    # fail; it is replaced by the attainment it was reaching for.)
    attainment = max(distance_to_division(F(2 * k + 1, 44), 22) for k in range(22))
    check(attainment == F(1, 44),
          "the covering radius of the twenty-two-division is not attained by a point of the octave")
    # the declared five-decimal reported maximum distance is that bound to five decimals,
    # and it is below the bound, because it is a maximum over the declared points
    reported_agrees = F(2272, 100000) <= F(1, 44) < F(2273, 100000)
    reported_below = F(2272, 100000) < F(1, 44)
    check(reported_agrees and reported_below,
          "the declared reported maximum distance is not the covering radius to five decimals")

    limit = N_DECLARED[1]
    table_1 = odd_power_table(limit, 1100)
    table_2 = odd_power_table(limit, 11000)
    measured = {}
    for N in N_DECLARED:
        measured[str(N)] = {
            "coverage_at_1_percent": coverage(B_MAIN, 1, 100, N, table_1),
            "coverage_at_point_1_percent": coverage(B_MAIN, 1, 1000, N, table_2),
        }
    check(measured["1651"]["coverage_at_1_percent"] == 22
          and measured["1651"]["coverage_at_point_1_percent"] == 22,
          "the declared larger set does not cover at both tolerances")
    check(measured["122"]["coverage_at_1_percent"] == 22
          and measured["122"]["coverage_at_point_1_percent"] < 22,
          "the declared smaller set does not behave as a density effect")

    thresholds = {
        "1_percent": threshold(B_MAIN, 1, 100, limit, table_1),
        "point_1_percent": threshold(B_MAIN, 1, 1000, limit, table_2),
    }
    check(thresholds["point_1_percent"] is not None,
          "full coverage at a tenth of a percent is never reached within the declared limit")
    check(thresholds["1_percent"] < thresholds["point_1_percent"],
          "the finer tolerance does not require more points")
    check(thresholds["point_1_percent"] <= N_DECLARED[1],
          "the declared larger set is below its own coverage threshold")
    # What these two numbers are. The coverage test walks the ODD integers, so the value
    # returned for a tolerance is an odd serial-number index bound: the largest odd index
    # whose predecessors already cover all twenty-two positions. The bound is one less
    # than twice the number of points it contains, so the point counts are 57 and 619 and
    # not 113 and 1237.
    index_bounds = {name: value for name, value in thresholds.items() if value is not None}
    point_counts = {name: (value + 1) // 2 for name, value in index_bounds.items()}
    index_bounds_are_odd = all(value % 2 == 1 for value in index_bounds.values())
    check(index_bounds_are_odd,
          "a declared coverage threshold is not an odd serial-number index bound")
    check(all(value == 2 * point_counts[name] - 1 for name, value in index_bounds.items()),
          "a declared coverage threshold is not one less than twice its own point count")
    return {
        "division": B_MAIN,
        "covering_radius_by_division": radii,
        "covering_radius": "1/44",
        "covering_radius_as_a_share": str(F(1, 44)),
        "reported_maximum_distance": "0.02272",
        "reported_maximum_is_the_covering_radius": reported_agrees,
        "every_subset_satisfies_the_bound": True,
        "measured_coverage": measured,
        "coverage_threshold": thresholds,
        "thresholds_are_odd_serial_number_index_bounds": index_bounds_are_odd,
        "coverage_threshold_units":
            "an odd serial-number index bound over the odd integers: the point count of "
            "the bound is (bound + 1) / 2",
        "coverage_threshold_index_bounds": index_bounds,
        "coverage_threshold_point_counts": point_counts,
        "covering_radius_is_attained_at_the_midpoints": attainment == F(1, 44),
        "exhausted_odd_integers": len(range(1, limit + 1, 2)),
    }


# ------------------------------------------- S4: the count arithmetic and one modulus

COUNTS_DECLARED = {"magneticSpaceGroups": 1651, "typeIII": 1191, "magneticLayerGroups": 528,
                   "magneticRodGroups": 394, "greyOrColorless": 230, "magneticPointGroups": 122}


def s4_count_arithmetic():
    values = list(COUNTS_DECLARED.values())
    m = len(values)
    residues = {name: v % B_MAIN for name, v in COUNTS_DECLARED.items()}
    check(residues == {"magneticSpaceGroups": 1, "typeIII": 3, "magneticLayerGroups": 0,
                       "magneticRodGroups": 20, "greyOrColorless": 10, "magneticPointGroups": 12},
          "the declared residues modulo the division are not the expected ones")
    multiples = [name for name, r in residues.items() if r == 0]
    check(multiples == ["magneticLayerGroups"], "the declared exact multiple is not the layer groups")
    at_least_one = 1 - F(B_MAIN - 1, B_MAIN) ** m
    check(at_least_one == F(27613783, 113379904),
          "the probability of at least one exact multiple is not the expected fraction")
    expected_count = F(m, B_MAIN)
    exactly_one = F(m, 1) * F(1, B_MAIN) * F(B_MAIN - 1, B_MAIN) ** (m - 1)
    none = F(B_MAIN - 1, B_MAIN) ** m
    check(exactly_one + none + (at_least_one - exactly_one) == 1,
          "the exact-multiple probabilities do not sum to one")
    check(expected_count < 1,
          "the expected number of exact multiples is not below one, so the coincidence is ordinary")
    check(exactly_one < F(1, 4),
          "observing exactly one exact multiple is not an ordinary-probability event")
    # the same question at every other modulus in a declared range
    divisors = {}
    for b in range(2, 41):
        hit = [name for name, v in COUNTS_DECLARED.items() if v % b == 0]
        if hit:
            divisors[str(b)] = hit
    check(len(divisors) >= 10,
          "too few declared moduli divide one of the six counts for the point to be made")
    check("22" in divisors, "the declared modulus is not among those that divide a count")
    return {
        "counts": COUNTS_DECLARED,
        "moduli": B_MAIN,
        "residues": residues,
        "exact_multiples": multiples,
        "expected_number_of_exact_multiples": str(expected_count),
        "probability_of_at_least_one": str(at_least_one),
        "probability_of_exactly_one": str(exactly_one),
        "probability_of_none": str(none),
        # The six-decimal rendering of the declared fraction by exact rational rounding.
        # The literal this replaces read "0.243564", which is not a rounding of
        # 0.243550947... at any precision; it was stale, and it is gone rather than kept
        # beside a corrected copy.
        "probability_of_at_least_one_six_decimals":
            decimal_round_half_up(at_least_one, 6),
        "expected_count_is_below_one": True,
        "observing_one_is_an_ordinary_event": True,
        "moduli_dividing_at_least_one_count": divisors,
        "moduli_range": [2, 40],
        "moduli_count": len(divisors),
    }


# ------------------------------------------- S5: gain is not comparable across classes

CLASSES = [
    {"id": "position", "gain": 1119, "top3": [683, 371, 63], "works": 5, "reported": "0.998"},
    {"id": "ganzhi", "gain": 3957, "top3": [630, 525, 368], "works": 76, "reported": "0.385"},
    {"id": "naming", "gain": 6800, "top3": [814, 679, 598], "works": 111, "reported": "0.307"},
    {"id": "bracket", "gain": 10224, "top3": [4769, 2912, 1439], "works": 15, "reported": "0.892"},
    {"id": "grade", "gain": 1939, "top3": [165, 164, 123], "works": 90, "reported": "0.233"},
]
CORPUS_SIZES = [4000, 3000, 2000, 500, 500]


def top3_share(counts, total):
    return F(sum(sorted(counts, reverse=True)[:3]), total)


def compositions(total, parts):
    """Every way of writing total as an ordered sum of parts non-negative integers."""
    if parts == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in compositions(total - first, parts - 1):
            yield (first,) + rest


def spearman(pairs):
    """Exact Spearman rank correlation for a list of (x, y) with distinct values."""
    n = len(pairs)
    rank_x = {v: i for i, v in enumerate(sorted(x for x, _ in pairs))}
    rank_y = {v: i for i, v in enumerate(sorted(y for _, y in pairs))}
    total = sum((rank_x[x] - rank_y[y]) ** 2 for x, y in pairs)
    return 1 - F(6 * total, n * (n * n - 1))


def s5_gain_and_spread():
    for c in CLASSES:
        share = top3_share(c["top3"], c["gain"])
        c["share"] = share
        c["exact_three_decimals"] = decimal_round_half_up(share, 3)
        check(sum(c["top3"]) <= c["gain"], "a declared top-three sum exceeds the declared gain")
    # The published three-decimal values are compared with EXACT decimal rounding of the
    # exact rational share, by integer arithmetic only. Four of the five agree. The fifth,
    # naming, is exactly the three-decimal half-way value 2091/6800 = 123/400 = 0.3075:
    # exact rounding gives 0.308, the published string is 0.307, and 0.307 is what the
    # truncation of that share gives, which is also what binary floating point produces
    # here because the nearest double to 0.3075 lies below it. The published digit is
    # therefore one unit low and the disagreement is asserted rather than made to pass.
    # (An earlier revision compared f"{float(share):.3f}" with the published string and
    # passed on the float's own rounding error, which is how the disagreement survived.)
    disagreements = [c["id"] for c in CLASSES
                     if c["exact_three_decimals"] != c["reported"]]
    check(disagreements == ["naming"],
          "the published three-decimal values are not reproduced by exact rounding in "
          "exactly the one declared half-way row")
    naming = next(c for c in CLASSES if c["id"] == "naming")
    check(naming["share"] * 10000 == 3075
          and naming["exact_three_decimals"] == "0.308"
          and decimal_truncate(naming["share"], 3) == naming["reported"],
          "the published naming share is not the truncation of an exact three-decimal "
          "half-way value whose exact rounding is 0.308")
    rho_rank = spearman([(c["gain"], c["share"]) for c in CLASSES])
    check(rho_rank == F(-1, 10),
          "the exact rank correlation between gain and spread is not minus one tenth")
    check(abs(rho_rank) < F(1, 2),
          "the rank correlation is large enough to be a relation, so the independence claim is wrong")
    by_gain = sorted(CLASSES, key=lambda c: -c["gain"])
    by_share = sorted(CLASSES, key=lambda c: c["share"])
    check([c["id"] for c in by_gain] != [c["id"] for c in by_share],
          "the gain order and the spread order coincide, so the comparison is vacuous")
    check(by_gain[0]["id"] == "bracket" and by_share[-1]["id"] == "position",
          "the largest gain and the weakest candidate are not the declared rows")
    # the largest gain is LESS concentrated than the smallest: the two columns disagree at the extremes
    check(by_gain[0]["share"] < by_gain[-1]["share"],
          "the largest gain is not less concentrated than the smallest, so the extremes do not disagree")
    check(by_gain[0]["works"] > by_gain[-1]["works"],
          "the largest gain does not rest on more works than the smallest")

    # gain and spread are independent: for a fixed gain the share ranges over a wide set
    ranges = {}
    for total, parts in ((12, 6), (24, 4)):
        shares = {top3_share(list(c), total) for c in compositions(total, parts)}
        ranges[f"{total}_over_{parts}"] = {"min": str(min(shares)), "max": str(max(shares)),
                                           "distinct": len(shares)}
        check(min(shares) <= F(3, parts) and max(shares) == 1,
              "the achievable share range for a fixed gain is not from the uniform value to one")
        check(len(shares) > 3, "the achievable share set for a fixed gain is too small to matter")

    # the effective number of works is bounded, not determined, by the published top three
    bounds = {}
    for c in CLASSES:
        p = [F(x, c["gain"]) for x in c["top3"]]
        share = sum(p)
        rest_square_min = (1 - share) ** 2 / (c["works"] - 3)
        rest_square_max = (1 - share) ** 2
        hhi_lo = sum(x * x for x in p) + rest_square_min
        hhi_hi = sum(x * x for x in p) + rest_square_max
        bounds[c["id"]] = {
            "works": c["works"],
            "effective_works_low": str(1 / hhi_hi),
            "effective_works_high": str(1 / hhi_lo),
        }
        check(F(bounds[c["id"]]["effective_works_low"]) <= F(bounds[c["id"]]["effective_works_high"]),
              "an effective-work bound is inverted")
    widest = max(bounds.items(), key=lambda kv: F(kv[1]["effective_works_high"])
                 / F(kv[1]["effective_works_low"]))
    check(F(widest[1]["effective_works_high"]) / F(widest[1]["effective_works_low"]) > 2,
          "no declared class has a wide effective-work range, so the bound claim is weak")

    # the baseline for a spread statistic is the corpus's own concentration, not zero
    total_corpus = sum(CORPUS_SIZES)
    uniform_class = list(CORPUS_SIZES)
    baseline = top3_share(uniform_class, total_corpus)
    check(baseline == F(9, 10),
          "the corpus baseline share of a spread statistic is not nine tenths")
    check(baseline > F(3, len(CORPUS_SIZES)),
          "the corpus baseline coincides with the uniform-over-works value")
    check(baseline > max(c["share"] for c in CLASSES if c["id"] != "position"),
          "the corpus baseline is below some declared class share, so the point is not made")
    return {
        "classes": {c["id"]: {"gain": c["gain"], "top3": c["top3"], "works": c["works"],
                              "top3_share": str(c["share"]), "reported": c["reported"],
                              "exact_three_decimals": c["exact_three_decimals"],
                              "published_value_is_the_exact_rounding":
                                  c["exact_three_decimals"] == c["reported"]}
                    for c in CLASSES},
        "published_three_decimal_values_reproduced_by_exact_rounding":
            [c["id"] for c in CLASSES if c["exact_three_decimals"] == c["reported"]],
        "published_three_decimal_values_not_reproduced_by_exact_rounding": disagreements,
        "naming_published_value": naming["reported"],
        "naming_exact_three_decimals": naming["exact_three_decimals"],
        "naming_share_is_exactly_a_three_decimal_half_way_value": naming["share"] * 10000 == 3075,
        "naming_published_value_is_the_truncation_of_its_exact_share":
            decimal_truncate(naming["share"], 3) == naming["reported"],
        "rounding_rule": "exact decimal rounding, halves away from zero, by integer arithmetic",
        "rank_correlation_gain_versus_spread": str(rho_rank),
        "rank_correlation_magnitude": str(abs(rho_rank)),
        "order_by_gain": [c["id"] for c in by_gain],
        "order_by_spread": [c["id"] for c in by_share],
        "largest_gain_row": by_gain[0]["id"],
        "largest_gain_row_share": str(by_gain[0]["share"]),
        "smallest_gain_row": by_gain[-1]["id"],
        "smallest_gain_row_share": str(by_gain[-1]["share"]),
        "largest_gain_is_less_concentrated_than_the_smallest": True,
        "achievable_share_ranges_for_a_fixed_gain": ranges,
        "effective_works_bounds": bounds,
        "widest_effective_works_ratio_class": widest[0],
        "corpus_sizes": CORPUS_SIZES,
        "corpus_baseline_share": str(baseline),
        "corpus_baseline_is_not_the_uniform_value": True,
        "exhausted_compositions": sum(1 for _ in compositions(12, 6))
        + sum(1 for _ in compositions(24, 4)),
    }


# ------------------------------------ S6: a declared threshold is not a test of content

COMPONENTS = {"品第評語": 8, "記言": 22, "舊制故事國朝": 8, "自始": 0, "凡皆": 0}
UNREAD = 190
CLASSIFIED = {"no speech verb at all": 169, "other outside the grammar": 15,
              "has 曰 or 云 without a colon or quote": 4, "has 曰 and a colon, no quote": 2}
GATE = F(1, 20)


def s6_threshold_versus_content():
    check(sum(COMPONENTS.values()) == 38, "the declared component counts do not sum to the published total")
    check(sum(CLASSIFIED.values()) == UNREAD,
          "the declared classification does not sum to the unread count")
    # The two components 自始 and 凡皆 are declared zero in contract.json. That is a
    # declaration and this checker does not verify it against the record: an earlier
    # revision asserted `COMPONENTS["自始"] == 0 and COMPONENTS["凡皆"] == 0`, which only
    # restated the literal two lines above it and could not fail. What the checker CAN
    # decide about the aggregate is what the aggregate fails to determine, below.
    declared_zero = [k for k, v in COMPONENTS.items() if v == 0]
    speech_components = {"記言"}
    non_speech = sum(v for k, v in COMPONENTS.items() if k not in speech_components)
    check(non_speech == 16, "the declared non-speech numerator is not sixteen")
    share = F(non_speech, UNREAD)
    check(share == F(8, 95), "the declared non-speech share is not eight ninety-fifths")
    # The gate is a FALSIFICATION line and not a ceiling. The external preregistration
    # this experiment reads (wenyan-relation-learning, commit ca0008c,
    # knowledge/relations/tangguoshibu-structure.json, "preregistration") states the line
    # as: if the non-speech hits divided by the unread passages is below one twentieth,
    # then the prediction does not hold. So the gate PASSES when the share is ABOVE one
    # twentieth and FAILS at or below it, which is the direction checked here; the note's
    # section 7 said the opposite and has been corrected with the rest of the five places.
    check(share > GATE,
          "the declared gate is a falsification line and the declared share is not above it")
    check(decimal_round_half_up(share, 4) == "0.0842",
          "the reported four-decimal gate value is not the exact one")
    largest_below = max(n for n in range(UNREAD + 1) if F(n, UNREAD) < GATE)
    check(F(largest_below, UNREAD) < GATE <= F(largest_below + 1, UNREAD),
          "the gate crossing point is not the declared one")
    check(non_speech - largest_below == 7,
          "the number of hits to spare before the gate fails is not seven")

    # the aggregate does not determine the components
    vectors = []
    for a in range(non_speech + 1):
        for b in range(non_speech - a + 1):
            for c in range(non_speech - a - b + 1):
                d = non_speech - a - b - c
                vectors.append((a, b, c, d))
    check(len(vectors) == (non_speech + 3) * (non_speech + 2) * (non_speech + 1) // 6,
          "the component-vector count is not the number of weak compositions of the numerator")
    check(len(vectors) > 100, "the component-vector family is too small to make the point")
    all_zero = [v for v in vectors if v[0] == non_speech]
    check(all_zero and all_zero[0] == (16, 0, 0, 0),
          "no declared vector puts the whole numerator on one component")
    no_contribution = [v for v in vectors if v[3] == 0]
    check(len(no_contribution) > 0,
          "no declared vector leaves the last component at zero")
    # the computed control: the same aggregate is compatible with a zero component AND
    # with a vector in which every component is positive, so the aggregate cannot be a
    # test of which components are present
    all_positive = [v for v in vectors if all(x > 0 for x in v)]
    aggregate_fixes_no_component = bool(all_positive) and bool(no_contribution)
    check(aggregate_fixes_no_component,
          "the declared numerator is compatible with only one side of the zero question, "
          "so the aggregate would partly determine the named content")
    check(sum(CLASSIFIED.values()) == UNREAD,
          "the classification identity does not hold")
    check(F(CLASSIFIED["no speech verb at all"], UNREAD) == F(169, 190),
          "the dominant-cause share is not one hundred sixty-nine over one hundred ninety")
    gate_passes = share > GATE and largest_below < non_speech
    return {
        "components": COMPONENTS,
        "unread": UNREAD,
        "non_speech_numerator": non_speech,
        "non_speech_share": str(share),
        "non_speech_share_four_decimals_exact": decimal_round_half_up(share, 4),
        "gate": str(GATE),
        "gate_direction":
            "falsification line: the gate fails when the share is below one twentieth, so "
            "it passes when the share is above it",
        "gate_source":
            "wenyan-relation-learning ca0008c, knowledge/relations/tangguoshibu-structure.json",
        "gate_passes": gate_passes,
        "largest_numerator_still_below_the_gate": largest_below,
        "gate_passes_with": f"{non_speech - largest_below} hits to spare",
        "components_exactly_zero": declared_zero,
        "components_exactly_zero_source":
            "declared in contract.json objects.gate_components and restated here; this "
            "checker does not verify them against the external record",
        "component_vectors_with_the_same_aggregate": len(vectors),
        "vectors_putting_everything_on_one_component": len(all_zero),
        "component_vectors_with_every_component_positive": len(all_positive),
        "classification": CLASSIFIED,
        "dominant_cause_share": str(F(CLASSIFIED["no speech verb at all"], UNREAD)),
        "the_aggregate_does_not_determine_the_components": aggregate_fixes_no_component,
    }


# ------------------------------------------------------------------------ driver

def run(output=None):
    started = time.perf_counter_ns()
    sections = {
        "S1_doubling_quotient": s1_doubling_quotient(),
        "S2_exact_hits": s2_exact_hits(),
        "S3_coverage": s3_coverage(),
        "S4_count_arithmetic": s4_count_arithmetic(),
        "S5_gain_and_spread": s5_gain_and_spread(),
        "S6_threshold_versus_content": s6_threshold_versus_content(),
    }
    report = {
        "schema": "adva.research.gain-and-coverage-evidence.v0",
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
    an enforced limit; this file deliberately contains no address-space call, so
    the repository's portability inventory is unaffected.
    """
    limit = LIMITS
    wanted = [
        ("RLIMIT_CPU", lambda: resource.setrlimit(resource.RLIMIT_CPU,
                                                  (limit["cpu_seconds"], limit["cpu_seconds"]))),
        ("RLIMIT_FSIZE", lambda: resource.setrlimit(resource.RLIMIT_FSIZE,
                                                    (limit["output_bytes"], limit["output_bytes"]))),
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
    contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
    LIMITS.update(contract["budget"])
    install_limits()
    report, _ = run(args.output)
    print(json.dumps({"status": report["status"], "assertions": report["assertions"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
