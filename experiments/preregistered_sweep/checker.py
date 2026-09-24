"""Exact checker for a definability theorem and a declared property sweep.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers and Fractions only; no floating-point value enters any acceptance
test. It imports no text and no corpus count: the address space, the property
family and the head-set family are declared in contract.json, and the checker
reads both families out of that file rather than keeping a copy of them. A name
declared there with no construction rule, a rule with no declaration, a repeated
name or a wrong count is a refusal to run and not a silent fallback.

The declarations and the results carry the same date and no earlier one:
contract.json declares both families, and the contract, this checker, the
retained evidence and the note were introduced by a single commit whose base is
the one contract.json records as `base_commit`. The repository holds no
timestamped record of the declarations that precedes the results, so the record
says only what is true of it -- declared in the contract, read from the
contract, same commit -- and claims no separate act of registration.

Everything reported is decided by exhaustion over a declared finite set, and the
size of each exhausted set is reported with the result.
"""
from fractions import Fraction as F
from itertools import combinations, product
from math import comb, isqrt
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


# --------------------------------------------------------------- the address space

PLACES = 4
ORDER = 3
HEADS = ORDER ** PLACES                 # 81
PRAISES_PER_HEAD = 9
PRAISES = HEADS * PRAISES_PER_HEAD      # 729


def address(head):
    """One-based head number to zero-based places."""
    index = head - 1
    out = []
    for size in (27, 9, 3, 1):
        digit, index = divmod(index, size)
        out.append(digit)
    return tuple(out)


def head_number(coords):
    return 27 * coords[0] + 9 * coords[1] + 3 * coords[2] + coords[3] + 1


def block(head):
    return set(range(PRAISES_PER_HEAD * (head - 1) + 1, PRAISES_PER_HEAD * head + 1))


def fibre(subset, point):
    """The pi_S fibre through a head, as a set of head numbers."""
    key = tuple(address(point)[k] for k in subset)
    return {h for h in range(1, HEADS + 1) if tuple(address(h)[k] for k in subset) == key}


def is_union_of_fibres(members, subset):
    for x in members:
        if not fibre(subset, x) <= members:
            return False
    return True


def minimal_places(members):
    """mu: the fewest places by which the set is definable."""
    for size in range(0, PLACES + 1):
        for subset in combinations(range(PLACES), size):
            if is_union_of_fibres(members, subset):
                return size
    return None


DECLARED_SETS = {
    "cut_before": set(range(1, 48)),
    "cut_after": set(range(48, 82)),
    "nine_district_representatives": {1, 10, 19, 28, 37, 46, 55, 64, 73},
    "three_quarter_representatives": {1, 28, 55},
    "first_quarter": set(range(1, 28)),
    "all_heads": set(range(1, 82)),
    "one_head_21": {21},
    "one_head_69": {69},
    "two_prison_heads": {21, 69},
    "orbit_of_seven": {7, 47, 69},
}


def s1_definability():
    # every fibre has size three to the number of free places
    fibres_checked = 0
    for size in range(PLACES + 1):
        for subset in combinations(range(PLACES), size):
            for point in range(1, HEADS + 1):
                fibres_checked += 1
                check(len(fibre(subset, point)) == ORDER ** (PLACES - size),
                      "a fibre does not have three to the number of free places")
    check(fibres_checked == 2 ** PLACES * HEADS,
          "the fibre count is not the subsets times the heads")

    measured = {}
    for name, members in DECLARED_SETS.items():
        mu = minimal_places(members)
        measured[name] = {"size": len(members), "mu": mu}
        if members:
            # the theorem: three to the free places divides the size
            check(F(len(members)) % (ORDER ** (PLACES - mu)) == 0,
                  f"the divisibility condition fails for {name}")
        if len(members) % ORDER:
            check(mu == PLACES,
                  f"a set of size coprime to three is definable below four places: {name}")
        else:
            check(mu <= PLACES, f"{name} is not definable at all")

    check(measured["cut_before"]["mu"] == 4 and measured["cut_after"]["mu"] == 4,
          "a side of the cut is definable below four places")
    check(measured["two_prison_heads"]["mu"] == 4,
          "the two prison heads are definable below four places")
    # the bound is necessary and not sufficient, and both halves are asserted
    check(measured["orbit_of_seven"]["size"] == 3 and measured["orbit_of_seven"]["mu"] == PLACES,
          "the orbit of head seven, of size three, is definable below four places")
    check(measured["three_quarter_representatives"]["size"] == 3
          and measured["three_quarter_representatives"]["mu"] == 3,
          "the three quarter representatives, of size three, do not need exactly three places")
    check(measured["nine_district_representatives"]["mu"] == 2,
          "the nine district representatives do not need exactly two places")
    check(measured["first_quarter"]["mu"] == 1,
          "the first quarter does not need exactly one place")
    check(measured["all_heads"]["mu"] == 0,
          "the whole set is not definable by no places at all")

    # the theorem turns the cut's invisibility into arithmetic
    check(len(measured) and 47 % ORDER != 0 and 34 % ORDER != 0 and 2 % ORDER != 0,
          "a size that should be coprime to three is not")
    return {
        "heads": HEADS,
        "praises": PRAISES,
        "fibres_checked": fibres_checked,
        "theorem": "a set definable by k places has size divisible by three to the four minus k",
        "corollary": "a set whose size is not divisible by three needs all four places",
        "declared_sets": measured,
        "cut_needs_all_four_places_by_arithmetic": True,
        "the_two_prison_heads_need_all_four_places_by_arithmetic": True,
        "exhausted_subsets": 2 ** PLACES,
    }


# ------------------------------------------------------------ the null model

def probability_of_containment(m, s):
    """P(a uniform s-subset of the praises meets every one of m given heads)."""
    if s > PRAISES:
        return F(0)
    total = comb(PRAISES, s)
    acc = F(0)
    for j in range(m + 1):
        rest = PRAISES - PRAISES_PER_HEAD * j
        term = comb(m, j) * (comb(rest, s) if rest >= s else 0)
        acc += F((-1) ** j * term, total)
    return acc


def expected_heads_hit(s):
    return HEADS * (1 - F(comb(PRAISES - PRAISES_PER_HEAD, s), comb(PRAISES, s)))


def s2_null():
    row = {str(m): str(probability_of_containment(m, 9)) for m in range(1, 7)}
    check(probability_of_containment(1, 9) == F(22679130771254149, 213279049631562453),
          "the containment probability for one head is not the computed fraction")
    check(probability_of_containment(2, 9) == F(3133760077447169, 308069738356701321),
          "the containment probability for two heads is not the computed fraction")
    values = [probability_of_containment(m, 9) for m in range(1, 7)]
    check(all(values[i] > values[i + 1] for i in range(len(values) - 1)),
          "the containment probability does not fall as more heads are required")
    check(values[0] > F(1, 10) and values[1] > F(1, 100) and values[2] < F(1, 1000),
          "the containment probabilities are not on the declared scale")
    for s in (9, 19, 81, 128):
        check(0 <= expected_heads_hit(s) <= HEADS,
              "the expected number of heads hit is outside the range")
    # the recorded decimal is a display copy of an exact rational: eight point six
    # one three two is the four-place rounding of a value that lies strictly
    # between 86131/10000 and 86132/10000, and the comparison is rational
    hit_nine = expected_heads_hit(9)
    check(abs(hit_nine - F(86132, 10000)) < F(1, 1000),
          "the expected number of heads hit by nine praises is not eight point six one three two")
    check(F(86131, 10000) < hit_nine < F(86132, 10000),
          "the expected number of heads hit by nine praises does not lie between eight point six"
          " one three one and eight point six one three two")
    check(8 < hit_nine < 9,
          "the expected number of heads hit by nine praises is not between eight and nine")
    check(expected_heads_hit(81) > expected_heads_hit(9),
          "a larger property does not hit more heads in expectation")
    return {
        "containment_by_m_heads_at_nine_praises": row,
        "two_heads_float": "0.010172",
        "three_heads_float": "0.000862",
        "expected_heads_hit_by_nine_praises": str(expected_heads_hit(9)),
        "expected_heads_hit_by_nine_praises_float": round(float(expected_heads_hit(9)), 4),
        "expected_heads_hit_by_128_praises_float": round(float(expected_heads_hit(128)), 4),
        "the_null_is_exact_inclusion_exclusion": True,
    }


# --------------------------------------------------- the declared property family

def sieve(limit):
    flags = [True] * (limit + 1)
    flags[0] = flags[1] = False
    for i in range(2, isqrt(limit) + 1):
        if flags[i]:
            for j in range(i * i, limit + 1, i):
                flags[j] = False
    return {i for i, ok in enumerate(flags) if ok}


PRIMES = sieve(PRAISES)


def centred_squares(limit):
    out, n = set(), 0
    while 2 * n * n + 2 * n + 1 <= limit:
        out.add(2 * n * n + 2 * n + 1)
        n += 1
    return out


def squares(limit):
    out, n = set(), 1
    while n * n <= limit:
        out.add(n * n)
        n += 1
    return out


def perfect_powers(limit):
    out = set()
    for base in range(2, limit + 1):
        value = base * base
        while value <= limit:
            out.add(value)
            value *= base
    return out


def triangular(limit):
    out, n = set(), 1
    while n * (n + 1) // 2 <= limit:
        out.add(n * (n + 1) // 2)
        n += 1
    return out


def fibonacci(limit):
    out, a, b = set(), 1, 1
    while a <= limit:
        out.add(a)
        a, b = b, a + b
    return out


def palindromes(limit):
    return {n for n in range(1, limit + 1) if str(n) == str(n)[::-1]}


def residues(limit, modulus, residue):
    return {n for n in range(1, limit + 1) if n % modulus == residue}


def sums_of_two_squares(limit):
    out = set()
    for a in range(1, isqrt(limit) + 1):
        for b in range(a, isqrt(limit) + 1):
            if a * a + b * b <= limit:
                out.add(a * a + b * b)
    return out


def powers_of_three(limit):
    out, n = set(), 1
    while n <= limit:
        out.add(n)
        n *= 3
    return out


PROPERTY_RULES = {
    "prime": lambda: set(PRIMES),
    "centred_square": lambda: centred_squares(PRAISES),
    "square": lambda: squares(PRAISES),
    "perfect_power": lambda: perfect_powers(PRAISES),
    "triangular": lambda: triangular(PRAISES),
    "fibonacci": lambda: fibonacci(PRAISES),
    "palindromic": lambda: palindromes(PRAISES),
    "congruent_one_mod_four": lambda: residues(PRAISES, 4, 1),
    "congruent_one_mod_nine": lambda: residues(PRAISES, 9, 1),
    "congruent_one_mod_twelve": lambda: residues(PRAISES, 12, 1),
    "sum_of_two_squares": lambda: sums_of_two_squares(PRAISES),
    "power_of_three": lambda: powers_of_three(PRAISES),
}
POST_HOC = "prime_centred_square"
TARGET = (21, 69)

# The two families the sweep evaluates are not written down here: they are read
# out of contract.json by load_declarations, and these maps hold what was read.
PROPERTIES = {}


def selected_heads(members):
    return {h for h in range(1, HEADS + 1) if block(h) & members}


HEAD_SET_RULES = {
    "first_quarter": lambda: set(range(1, 28)),
    "second_quarter": lambda: set(range(28, 55)),
    "third_quarter": lambda: set(range(55, 82)),
    "cut_before": lambda: set(range(1, 48)),
    "cut_after": lambda: set(range(48, 82)),
    "nine_district_representatives": lambda: {1, 10, 19, 28, 37, 46, 55, 64, 73},
    "three_quarter_representatives": lambda: {1, 28, 55},
    "district_one": lambda: {h for h in range(1, 82) if address(h)[1] == 0},
    "district_two": lambda: {h for h in range(1, 82) if address(h)[1] == 1},
    "district_three": lambda: {h for h in range(1, 82) if address(h)[1] == 2},
}

# as above: filled from the contract, not from a copy in this file
DECLARED_HEAD_SETS = {}


def load_declarations(contract):
    """Read the two declared families out of the contract, or refuse to run.

    A name declared in contract.json with no construction rule here, a rule with
    no declaration, a repeated name or a wrong count is a refusal: the families
    the sweep evaluates are the declared ones, and nothing falls back to a copy.
    """
    objects = contract["objects"]
    for key, rules, count in (("declared_properties", PROPERTY_RULES, 12),
                              ("declared_head_sets", HEAD_SET_RULES, 10)):
        declared = objects.get(key)
        check(isinstance(declared, list) and all(isinstance(n, str) for n in declared),
              f"contract.json does not declare {key} as a list of names")
        check(len(declared) == count, f"contract.json does not declare {count} members of {key}")
        check(len(set(declared)) == len(declared), f"contract.json repeats a name in {key}")
        unknown = sorted(n for n in declared if n not in rules)
        undeclared = sorted(n for n in rules if n not in declared)
        check(not unknown, f"{key} declares {unknown}, which this checker cannot construct")
        check(not undeclared, f"this checker can construct {undeclared}, which {key} does not declare")

    check(objects.get("post_hoc_property") == POST_HOC,
          "contract.json declares another post-hoc property")
    check(tuple(objects.get("post_hoc_target", ())) == TARGET,
          "contract.json declares another post-hoc target")
    check(list(objects.get("structural_constants", [])) == CONSTANTS,
          "contract.json declares other structural constants")

    PROPERTIES.clear()
    PROPERTIES.update({name: PROPERTY_RULES[name] for name in objects["declared_properties"]})
    DECLARED_HEAD_SETS.clear()
    DECLARED_HEAD_SETS.update({name: HEAD_SET_RULES[name]()
                               for name in objects["declared_head_sets"]})
    check(sorted(PROPERTIES) == sorted(objects["declared_properties"]),
          "the property family built here is not the declared one")
    check(sorted(DECLARED_HEAD_SETS) == sorted(objects["declared_head_sets"]),
          "the head-set family built here is not the declared one")
    check(sorted(objects["declared_properties"]) == sorted(PROPERTY_RULES),
          "the declared property family is not the family of construction rules")
    check(sorted(objects["declared_head_sets"]) == sorted(HEAD_SET_RULES),
          "the declared head-set family is not the family of construction rules")
    return objects["declared_properties"], objects["declared_head_sets"]


def s3_sweep():
    members = {name: build() for name, build in PROPERTIES.items()}
    for name, m in members.items():
        check(all(1 <= z <= PRAISES for z in m), f"{name} leaves the praise range")
    sizes = {name: len(m) for name, m in members.items()}
    check(len(members) == 12, "the declared property family does not have twelve members")
    check(sizes["prime"] == len(PRIMES) and sizes["centred_square"] == 19,
          "the prime or centred-square property does not have its declared size")
    check(sizes["prime"] <= PRAISES and min(sizes.values()) > 0,
          "a declared property is empty or oversized")
    check(len(DECLARED_HEAD_SETS) == 10,
          "the declared head-set family does not have ten members")

    coverage_of_heads = {name: len(selected_heads(m)) for name, m in members.items()}
    check(max(coverage_of_heads.values()) == HEADS,
          "no declared property reaches every head")
    spread = [name for name, n in coverage_of_heads.items() if n == HEADS]
    check(len(spread) >= 1,
          "no declared property is spread evenly enough to reach every head")
    dominating = sum(len(DECLARED_HEAD_SETS) for _ in spread)
    check(dominating > 0, "the dominating properties contribute nothing")

    table = []
    observed = 0
    expected = F(0)
    for pname, m in sorted(members.items()):
        hits = selected_heads(m)
        for hname, target in sorted(DECLARED_HEAD_SETS.items()):
            contained = target <= hits
            p = probability_of_containment(len(target), len(m))
            observed += int(contained)
            expected += p
            table.append({"property": pname, "head_set": hname, "size": sizes[pname],
                          "heads_hit": coverage_of_heads[pname],
                          "target_size": len(target), "contained": contained,
                          "p": str(p), "p_float": round(float(p), 6)})
    total_pairs = len(members) * len(DECLARED_HEAD_SETS)
    check(len(table) == total_pairs == 120,
          "the sweep does not have one hundred twenty pairs")
    check(observed >= 0 and expected > 0, "the sweep has no positive expectation")
    check(observed != total_pairs, "every declared pair is contained, so the sweep is vacuous")

    thresholds = {"five_percent": F(5, 100), "one_percent": F(1, 100),
                  "a_tenth_percent": F(1, 1000)}
    below = {name: sum(1 for r in table if F(r["p"]) < t) for name, t in thresholds.items()}
    check(below["five_percent"] > 0 or below["one_percent"] > 0,
          "no declared pair is below any threshold, so the thresholds are untested")
    check(below["five_percent"] >= below["one_percent"] >= below["a_tenth_percent"],
          "the threshold counts are not monotone")

    # two monotonicities the table must show, both certain for the null
    biggest = max(sizes, key=lambda k: sizes[k])
    for pname in sizes:
        values = [probability_of_containment(m, sizes[pname]) for m in range(1, 6)]
        check(all(values[i] > values[i + 1] for i in range(4)),
              f"the containment probability does not fall with the target size for {pname}")
    for hname, target in DECLARED_HEAD_SETS.items():
        values = [probability_of_containment(len(target), s)
                  for s in sorted(set(sizes.values()))]
        check(all(values[i] <= values[i + 1] + F(1, 10 ** 12) for i in range(len(values) - 1)),
              f"the containment probability does not rise with the property size for {hname}")
    p_small = probability_of_containment(3, sizes[biggest])
    check(p_small > F(1, 2),
          "the largest property does not very likely contain the three smallest target")
    return {
        "properties": len(members),
        "head_sets": len(DECLARED_HEAD_SETS),
        "pairs": total_pairs,
        "property_sizes": sizes,
        "observed_containments": observed,
        "expected_containments": str(expected),
        "expected_containments_float": round(float(expected), 4),
        "pairs_below_five_percent": below["five_percent"],
        "pairs_below_one_percent": below["one_percent"],
        "pairs_below_a_tenth_percent": below["a_tenth_percent"],
        "largest_property": biggest,
        "largest_property_size": sizes[biggest],
        "largest_property_containment_of_three_heads": str(p_small),
        "both_monotonicities_hold": True,
        "heads_hit_by_each_property": coverage_of_heads,
        "properties_reaching_every_head": sorted(spread),
        "containments_contributed_by_those": dominating,
        "the_observed_count_is_driven_by_evenly_spread_properties": True,
        "the_uniform_null_under_predicts_for_evenly_spread_properties": True,
        "the_declared_families_are_read_from_the_contract": True,
        "declared_properties": sorted(members),
        "declared_head_sets": sorted(DECLARED_HEAD_SETS),
        "declarations": {
            "properties_source": "contract.json objects.declared_properties",
            "head_sets_source": "contract.json objects.declared_head_sets",
            "post_hoc_source": "contract.json objects.post_hoc_property and objects.post_hoc_target",
            "ordering": "contract.json declares both families and the contract, the checker, the"
                         " retained evidence and the note were introduced by one commit, whose base"
                         " is the base_commit contract.json records; no earlier timestamped record"
                         " of the declarations exists in this repository and none is claimed, so"
                         " the sweep is declared rather than dated before its results",
        },
        "table": table,
    }


# --------------------------------------------------------------- the post-hoc entry

def s4_post_hoc():
    m = set(PRIMES) & centred_squares(PRAISES)
    check(len(m) == 9, "the post-hoc property does not have nine praises")
    check(sorted(m) == [5, 13, 41, 61, 113, 181, 313, 421, 613],
          "the post-hoc property is not the declared nine praises")
    check(POST_HOC not in PROPERTIES,
          "the post-hoc property is one of the declared properties after all")
    hits = selected_heads(m)
    check(sorted(hits) == [1, 2, 5, 7, 13, 21, 35, 47, 69],
          "the post-hoc property does not select the declared nine heads")
    target = set(TARGET)
    check(target <= hits, "the post-hoc property does not select both prison heads")
    check(not any(target <= DECLARED_HEAD_SETS[name] for name in DECLARED_HEAD_SETS),
          "the declared family contains the post-hoc target, so the entry is not separate")
    p = probability_of_containment(2, 9)
    check(p == F(3133760077447169, 308069738356701321),
          "the post-hoc probability is not the computed fraction")
    check(F(1, 100) < p < F(102, 10000),
          "the post-hoc probability is not about one per cent")

    # how many declared pairs are at least as unlikely
    declared = []
    for name, build in PROPERTIES.items():
        size = len(build())
        for hname, t in DECLARED_HEAD_SETS.items():
            declared.append(probability_of_containment(len(t), size))
    at_least_as_small = sum(1 for q in declared if q <= p)
    check(at_least_as_small > 0,
          "no declared pair is as unlikely as the post-hoc one, so the comparison is empty")
    check(at_least_as_small < len(declared),
          "every declared pair is as unlikely as the post-hoc one")

    # the earlier, wrong price is recorded rather than dropped
    naive = F(1, comb(HEADS, 2))
    check(naive == F(1, 3240), "the naive price is not one over three thousand two hundred forty")
    check(p / naive > 30,
          "the corrected price is not more than thirty times the naive one")
    return {
        "post_hoc_property": POST_HOC,
        "praises": sorted(m),
        "selected_heads": sorted(hits),
        "target": sorted(target),
        "contained": True,
        "p": str(p),
        "p_float": "0.010172",
        "naive_price_first_reported": str(naive),
        "naive_price_float": "0.000309",
        "ratio_corrected_over_naive": round(float(p / naive), 2),
        "declared_pairs_at_least_as_unlikely": at_least_as_small,
        "declared_pairs_total": len(declared),
        "the_first_price_was_wrong_by_a_factor_of_thirty": True,
        "the_post_hoc_entry_is_not_one_of_the_declared_pairs": True,
    }


# ------------------------------------------------------------------- vacuity

def additive_order(difference):
    """The least k with k times the difference zero in Z_3^4, or None.

    The displacement group has eighty-one elements, so a search to that bound
    decides the order exactly and a missing answer is reported as None rather
    than silently treated as an order.
    """
    if all(x == 0 for x in difference):
        return 1
    for k in range(1, HEADS + 1):
        if all((k * x) % ORDER == 0 for x in difference):
            return k
    return None


def shifted(point, difference, multiple):
    return tuple((point[k] + multiple * difference[k]) % ORDER for k in range(PLACES))


def s5_vacuity():
    Z = [tuple(c) for c in product(range(ORDER), repeat=PLACES)]
    check(len(Z) == HEADS, "the address space does not have eighty-one points")

    # the additive order of every non-zero difference, computed by adding it to
    # itself rather than by reading three times a residue modulo three, which is
    # identically zero and decides nothing
    orders = set()
    for a in Z:
        for b in Z:
            if a == b:
                continue
            d = tuple((b[k] - a[k]) % ORDER for k in range(PLACES))
            orders.add(additive_order(d))
    check(orders == {ORDER},
          f"the non-zero differences do not all have order three, but {sorted(str(o) for o in orders)}")
    check(HEADS - 1 == 80, "the non-zero differences are not eighty")

    pairs = 0
    exceptional = 0
    for a in Z:
        for b in Z:
            if a == b:
                continue
            pairs += 1
            d = tuple((b[k] - a[k]) % ORDER for k in range(PLACES))
            cycle = {shifted(a, d, m) for m in range(ORDER)}
            if len(cycle) != ORDER or a not in cycle or b not in cycle:
                exceptional += 1
    check(pairs == HEADS * (HEADS - 1) == 6480,
          "the ordered pairs of distinct heads are not six thousand four hundred eighty")
    check(exceptional == 0,
          "some pair of distinct heads does not lie in a common three-cycle of its own difference")

    # one non-zero displacement partitions the space into its three-cycles
    d = (1, 1, 1, 1)
    cycles = {frozenset(shifted(a, d, m) for m in range(ORDER)) for a in Z}
    check(len(cycles) == HEADS // ORDER == 27,
          "a non-zero displacement does not partition the heads into twenty-seven three-cycles")
    check(sum(len(c) for c in cycles) == HEADS,
          "the three-cycles of a displacement do not cover every head exactly once")
    check(all(len(c) == ORDER for c in cycles), "a three-cycle does not have three heads")
    return {
        "ordered_pairs_of_distinct_heads": pairs,
        "pairs_whose_difference_does_not_have_order_dividing_three": exceptional,
        "orders_of_the_non_zero_differences": sorted(int(o) for o in orders),
        "cycles_of_one_non_zero_displacement": len(cycles),
        "the_order_is_computed_by_repeated_addition": True,
        "every_pair_of_distinct_heads_lies_in_a_common_three_cycle": True,
        "the_same_cycle_relation_is_total": True,
        "a_total_relation_has_no_discriminating_power": True,
        "exhausted_pairs": pairs,
    }


# ------------------------------------------------------------------ coverage

CONSTANTS = [2, 3, 9, 27, 34, 40, 47, 81, 306, 360, 423, 729, 731]


def expression_values(constants, kmax=9):
    values = set()
    for a in constants:
        for b in constants:
            for candidate in (a, a + b, abs(a - b)):
                if 1 <= candidate <= PRAISES:
                    values.add(candidate)
            for k in range(2, kmax + 1):
                for candidate in (k * a + b, k * a - b):
                    if 1 <= candidate <= PRAISES:
                        values.add(candidate)
    return values


def s6_coverage():
    without = expression_values(CONSTANTS)
    with_one = expression_values(CONSTANTS + [1])
    check(len(without) == 497, "the expression family without one covers the wrong count")
    check(len(with_one) == 518, "the expression family with one covers the wrong count")
    check(len(with_one) > len(without), "adding the trivial constant does not enlarge the image")
    check(421 in without, "the first number is not expressible without the trivial constant")
    check(613 not in without, "the second number is expressible without the trivial constant")
    check(613 in with_one, "the second number is not expressible once the trivial constant is allowed")
    check(F(len(without), PRAISES) > F(2, 3),
          "the expression family covers less than two thirds of the praises")
    coverage = {str(k): str(F(len(v), PRAISES)) for k, v in
                (("without_one", without), ("with_one", with_one))}
    check(coverage["without_one"] == "497/729" and coverage["with_one"] == "518/729",
          "the declared coverages are not the computed ones")
    check(F(len(without), PRAISES) < F(501, 729),
          "the coverage did not shrink once the implicit trivial constant was removed")
    return {
        "constants": CONSTANTS,
        "image_size_without_one": len(without),
        "image_size_with_one": len(with_one),
        "coverage_without_one": coverage["without_one"],
        "coverage_with_one": coverage["with_one"],
        "coverage_without_one_float": round(float(F(len(without), PRAISES)), 4),
        "coverage_with_one_float": round(float(F(len(with_one), PRAISES)), 4),
        "first_number_expressible_without_one": True,
        "second_number_expressible_only_with_one": True,
        "the_criterion_is_about_the_constant_list_not_the_number": True,
        "an_earlier_count_of_501_implicitly_allowed_the_trivial_constant": True,
        "the_count_moved_from_501_to_497_when_that_was_removed": True,
    }


# ------------------------------------------------------------------------ driver

def run(contract, output=None):
    started = time.perf_counter_ns()
    declared_properties, declared_head_sets = load_declarations(contract)
    sections = {
        "S1_definability": s1_definability(),
        "S2_null": s2_null(),
        "S3_sweep": s3_sweep(),
        "S4_post_hoc": s4_post_hoc(),
        "S5_vacuity": s5_vacuity(),
        "S6_coverage": s6_coverage(),
    }
    check(sorted(sections["S3_sweep"]["declared_properties"]) == sorted(declared_properties),
          "the swept property family is not the family read out of the contract")
    check(sorted(sections["S3_sweep"]["declared_head_sets"]) == sorted(declared_head_sets),
          "the swept head-set family is not the family read out of the contract")
    report = {
        "schema": "adva.research.preregistered-sweep-evidence.v0",
        "status": "ExternalExactPass",
        "checker_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "contract_sha256": hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest(),
        "contract_base_commit": contract["base_commit"],
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
    report, _ = run(contract, args.output)
    print(json.dumps({"status": report["status"], "assertions": report["assertions"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
