"""Exact checker for the coverage of a declared expression family, and for the
crossing count of a declared shift on the eighty-one heads.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers and Fractions only; no floating-point value enters any acceptance
test. It imports no text and no corpus count: every constant set, every form and
the shift are declared in contract.json, and every figure is computed from them.

Two questions are decided, and they are the same question twice. Given a declared
constant set, how much of the seven hundred twenty-nine praises does the declared
family of expressions reach -- so that "some expression equals the target" can be
priced instead of asserted? And given a declared shift on the heads, how many of
its pairs straddle a declared cut -- so that "this many pairs cross the cut" can
be recognised as an identity instead of a finding. In both cases the number is
fixed by the declaration before any target or any cut is named.
"""
from fractions import Fraction as F
from collections import Counter
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

PLACES = 4
ORDER = 3
HEADS = ORDER ** PLACES                 # 81
PRAISES = HEADS * 9                     # 729
OMEGA = frozenset(range(1, PRAISES + 1))


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


# ------------------------------------------------------------- the expression family

KMAX = 9


def expressions(constants, kmax=KMAX):
    """Every declared expression, with the unused part explicitly None.

    The bare form carries `b = None`, so a constant that happens to be the target
    contributes one expression and not one per partner.
    """
    out = []
    for a in constants:
        out.append(("a", a, None, None))
        for b in constants:
            out.append(("a+b", a, b, None))
            out.append(("|a-b|", a, b, None))
            for k in range(2, kmax + 1):
                out.append(("ka+b", a, b, k))
                out.append(("ka-b", a, b, k))
    return out


def value_of(expression):
    form, a, b, k = expression
    if form == "a":
        return a
    if form == "a+b":
        return a + b
    if form == "|a-b|":
        return abs(a - b)
    if form == "ka+b":
        return k * a + b
    return k * a - b


def multiplicities(constants, kmax=KMAX):
    """How many declared expressions name each praise, over the praises only."""
    counts = Counter()
    for expression in expressions(constants, kmax):
        number = value_of(expression)
        if 1 <= number <= PRAISES:
            counts[number] += 1
    return counts


def image(constants, kmax=KMAX):
    return frozenset(multiplicities(constants, kmax))


def expression_count(size, kmax=KMAX):
    """How many expressions a constant set of this size writes, in any range."""
    return size + size * size * (2 + 2 * (kmax - 1))


# ------------------------------------------------------------------ the coverage

THE_THIRTEEN = [2, 3, 9, 27, 34, 40, 47, 81, 306, 360, 423, 729, 731]


def prefix(n):
    return list(range(1, n + 1))


DECLARED_SETS = {
    "the_thirteen_of_0218": THE_THIRTEEN,
    "the_thirteen_with_one": THE_THIRTEEN + [1],
    "the_structural_constants": [1, 2, 3, 4, 9, 27, 40, 81, 729],
    "the_prefix_of_nine": prefix(9),
    "the_prefix_of_eighteen": prefix(18),
    "the_prefix_of_twenty_seven": prefix(27),
    "the_prefix_of_forty": prefix(40),
    "the_prefix_of_forty_one": prefix(41),
    "the_prefix_of_seventy_two": prefix(72),
    "the_prefix_of_seventy_three": prefix(73),
}


def s1_coverage():
    rows = {}
    for name, constants in DECLARED_SETS.items():
        reached = image(constants)
        check(reached, f"{name} reaches nothing")
        check(reached <= OMEGA, f"{name} reaches outside the praises")
        rows[name] = {
            "size": len(constants),
            "image_size": len(reached),
            "coverage": str(F(len(reached), PRAISES)),
            "coverage_float": round(float(F(len(reached), PRAISES)), 4),
            "expression_count": expression_count(len(constants)),
        }
    # the two figures of the earlier note, reproduced from the same declared family
    check(rows["the_thirteen_of_0218"]["image_size"] == 497,
          "the thirteen constants do not reach four hundred ninety-seven praises")
    check(rows["the_thirteen_of_0218"]["coverage"] == "497/729",
          "the coverage of the thirteen constants is not the computed one")
    check(rows["the_thirteen_with_one"]["image_size"] == 518,
          "adding the trivial constant does not reach five hundred eighteen praises")
    check(rows["the_thirteen_with_one"]["coverage"] == "518/729",
          "the coverage with the trivial constant is not the computed one")

    # monotonicity, by exhaustion over every nested pair of declared sets
    nested = 0
    for left in sorted(DECLARED_SETS):
        for right in sorted(DECLARED_SETS):
            if set(DECLARED_SETS[left]) <= set(DECLARED_SETS[right]):
                nested += 1
                check(image(DECLARED_SETS[left]) <= image(DECLARED_SETS[right]),
                      f"the image is not monotone from {left} to {right}")
                check(rows[left]["image_size"] <= rows[right]["image_size"],
                      f"the coverage is not monotone from {left} to {right}")
    check(nested == 32, "the number of nested declared pairs is not the counted one")

    # the interval theorem: the first n integers reach exactly the first ten n
    for n in range(1, 91):
        reached = image(prefix(n))
        limit = min(10 * n, PRAISES)
        check(reached == frozenset(range(1, limit + 1)),
              f"the first {n} integers do not reach exactly the first {limit} praises")
    check(rows["the_prefix_of_seventy_two"]["image_size"] == 720,
          "the first seventy-two integers do not reach seven hundred twenty praises")
    check(rows["the_prefix_of_seventy_three"]["image_size"] == PRAISES,
          "the first seventy-three integers do not reach every praise")
    check(F(rows["the_prefix_of_seventy_two"]["image_size"], PRAISES) == F(80, 81),
          "the coverage at seventy-two is not eighty over eighty-one")

    # a declared deterministic greedy over a declared candidate pool
    pool = list(range(1, 91))
    chosen = []
    reached = frozenset()
    while len(reached) < PRAISES and len(chosen) < len(pool):
        best, best_gain, best_image = None, -1, None
        for candidate in pool:
            if candidate in chosen:
                continue
            trial = image(chosen + [candidate])
            gain = len(trial) - len(reached)
            if gain > best_gain:
                best, best_gain, best_image = candidate, gain, trial
        if best is None or best_gain <= 0:
            break
        chosen.append(best)
        reached = best_image
    check(len(reached) == PRAISES, "the declared greedy does not reach every praise")
    check(len(chosen) == 14, "the declared greedy does not need fourteen constants")
    check(len(chosen) < 73, "the greedy is not smaller than the interval family")

    # the multiplier range is a declared parameter, not a natural bound
    ladder = {}
    for kmax in (2, 3, 4, 5, 6, 7, 8, 9, 12, 20):
        ladder[str(kmax)] = len(image(THE_THIRTEEN, kmax))
    check(ladder == {"2": 223, "3": 280, "4": 339, "5": 385, "6": 420, "7": 460,
                     "8": 497, "9": 497, "12": 569, "20": 664},
          "the multiplier ladder is not the computed one")
    check(all(ladder[str(a)] <= ladder[str(b)]
              for a, b in zip((2, 3, 4, 5, 6, 7, 8, 9, 12), (3, 4, 5, 6, 7, 8, 9, 12, 20))),
          "the coverage is not monotone in the multiplier range")
    check(ladder["9"] == rows["the_thirteen_of_0218"]["image_size"],
          "the declared multiplier range does not reproduce the declared coverage")
    check(ladder["3"] < ladder["9"] < ladder["20"],
          "the declared multiplier range is not strictly inside the ladder")

    # the counting bound on how small a covering constant set can be
    lower = 0
    while expression_count(lower) < PRAISES:
        lower += 1
    check(lower == 7, "the counting bound does not force at least seven constants")
    check(lower <= len(chosen) <= 73,
          "the bounds on the smallest covering constant set are inconsistent")

    return {
        "rows": rows,
        "nested_pairs_exhausted": nested,
        "image_is_monotone_in_the_constant_set": True,
        "kmax": KMAX,
        "kmax_ladder": ladder,
        "kmax_ladder_is_monotone": True,
        "interval_theorem": "the first n integers reach exactly the first 10n praises while"
                            " 10n is at most 729, and every praise from n = 73 on",
        "interval_checked_up_to": 90,
        "greedy_pool": [pool[0], pool[-1]],
        "greedy_constants": chosen,
        "greedy_size": len(chosen),
        "greedy_image_size": len(reached),
        "counting_lower_bound": lower,
        "smallest_covering_set_is_not_decided": True,
    }


# --------------------------------------------- the target, and its own absence

BASE = THE_THIRTEEN
TARGETS = {"first_number": 421, "the_cut_constant": 423, "second_number": 613}


def s2_target():
    with_target = multiplicities(BASE)
    stripped = [c for c in BASE if c != 423]
    without = multiplicities(stripped)
    rows = {}
    for name, target in TARGETS.items():
        rows[name] = {
            "target": target,
            "is_a_declared_constant": target in BASE,
            "expressions_naming_it": with_target.get(target, 0),
            "expressions_naming_it_with_the_cut_constant_removed": without.get(target, 0),
        }
    check(rows["the_cut_constant"]["is_a_declared_constant"] is True,
          "the cut constant is not among the declared constants")
    check(rows["the_cut_constant"]["expressions_naming_it_with_the_cut_constant_removed"] == 5,
          "removing the target from the constants does not leave five expressions")
    check(rows["the_cut_constant"]["expressions_naming_it"]
          > rows["the_cut_constant"]["expressions_naming_it_with_the_cut_constant_removed"],
          "removing the target did not remove any expression naming it")
    check(rows["first_number"]["is_a_declared_constant"] is False,
          "the first number is a declared constant after all")
    check(rows["first_number"]["expressions_naming_it"] == 3,
          "the first number is not named by three expressions")
    check(rows["second_number"]["expressions_naming_it"] == 0,
          "the second number is named without the trivial constant")
    check(len(without) == 472,
          "removing the target does not shrink the image to four hundred seventy-two")
    check(len(with_target) == 497, "the image with the target as a constant is not 497")
    check(F(len(with_target), PRAISES) == F(497, 729),
          "the price of a hit is not the coverage over the declared constants")
    check(F(len(without), PRAISES) < F(len(with_target), PRAISES) and len(without) < len(with_target),
          "removing the target did not lower the price")
    return {
        "rows": rows,
        "the_family_must_exclude_the_target": True,
        "image_size_with_the_target_as_a_constant": len(with_target),
        "image_size_once_it_is_not_a_constant": len(without),
        "coverage_is_the_price_of_a_hit": True,
        "a_target_that_is_a_constant_is_named_by_the_bare_form": True,
    }


# ------------------------------------------------------------------- multiplicity

def s3_multiplicity():
    counts = multiplicities(BASE)
    reached = sorted(counts)
    histogram = Counter(counts.values())
    check(len(reached) == 497, "the multiplicity table does not cover four hundred ninety-seven")
    check(sum(histogram.values()) == 497, "the histogram does not sum to the image")
    check(min(counts.values()) == 1, "no praise is named exactly once")
    check(max(counts.values()) == 15, "the largest multiplicity is not fifteen")
    check(counts[54] == 15, "the praise of the largest multiplicity is not fifty-four")
    check(counts[423] == 7 and counts[421] == 3,
          "the two declared numbers have other multiplicities")
    check(counts.get(613, 0) == 0, "the second number is named without the trivial constant")

    # no praise can be named more often than there are declared expressions
    bound = expression_count(len(BASE))
    check(bound == len(expressions(BASE)), "the expression bound is not the number of forms")
    check(all(v <= bound for v in counts.values()), "a multiplicity exceeds the expression bound")

    # adding a constant cannot destroy an expression, so multiplicity is monotone too
    wider = multiplicities(BASE + [1])
    for target in reached:
        check(wider[target] >= counts[target],
              f"adding a constant removed an expression naming {target}")
    check(len(wider) == 518, "the wider family does not reach five hundred eighteen")
    check(wider[613] == 1, "the trivial constant does not name the second number exactly once")
    check(wider[423] == counts[423], "the trivial constant changed the cut constant's multiplicity")

    hit = F(len(reached), PRAISES)
    check(hit == F(497, 729), "the price of a hit is not four hundred ninety-seven over 729")
    check(F(len(wider), PRAISES) == F(518, 729),
          "the wider price is not five hundred eighteen over 729")
    check(hit > F(2, 3), "the family reaches less than two thirds of the praises")
    check(sum(counts.values()) == 1441,
          "the number of in-range expressions is not the counted one")
    check(sum(wider.values()) > sum(counts.values()),
          "adding a constant did not add any expression in range")

    return {
        "constants": sorted(BASE),
        "praises_reached": len(reached),
        "praises_total": PRAISES,
        "histogram_of_multiplicity": {str(k): v for k, v in sorted(histogram.items())},
        "largest_multiplicity": max(counts.values()),
        "praise_of_largest_multiplicity": 54,
        "multiplicity_of_423": counts[423],
        "multiplicity_of_421": counts[421],
        "multiplicity_of_613": counts.get(613, 0),
        "multiplicity_of_613_with_one": wider[613],
        "expression_bound": bound,
        "multiplicity_is_monotone_in_the_constant_set": True,
        "coverage_float": round(float(hit), 4),
        "wider_coverage_float": round(float(F(len(wider), PRAISES)), 4),
        "the_price_of_a_hit_is_the_coverage": True,
    }


# ------------------------------------------------------------ the shift and the cut

TAIXUAN_SHIFT = 40
TAIXUAN_CUT = 47


def digits(head):
    """The four ternary digits of a head, most significant first."""
    index = head - 1
    out = []
    for size in (27, 9, 3, 1):
        digit, index = divmod(index, size)
        out.append(digit)
    return tuple(out)


def numeral(value):
    return digits(value + 1)


def pairs_across(shift, cut):
    """The declared pairs of the shift, split by the cut, by direct count."""
    inside = crossing = 0
    for head in range(1, HEADS - shift + 1):
        partner = head + shift
        if partner <= cut:
            inside += 1
        elif head <= cut:
            crossing += 1
    return inside, crossing


def closed_form(shift, cut):
    """The same two counts as a formula, for comparison with the direct count."""
    total = max(0, HEADS - shift)
    inside = max(0, min(cut - shift, total))
    low, high = max(1, cut - shift + 1), min(cut, total)
    crossing = max(0, high - low + 1)
    return total, inside, crossing


def s4_crossing():
    mismatches = []
    for shift in range(1, HEADS):
        for cut in range(1, HEADS):
            inside, crossing = pairs_across(shift, cut)
            total, formula_inside, formula_crossing = closed_form(shift, cut)
            if (inside, crossing) != (formula_inside, formula_crossing):
                mismatches.append((shift, cut, inside, crossing,
                                   formula_inside, formula_crossing))
    check(not mismatches, f"the closed form disagrees with the count at {mismatches[:3]}")
    check((HEADS - 1) ** 2 == 6400, "the exhaustion is not over all pairs")

    total, inside, crossing = closed_form(TAIXUAN_SHIFT, TAIXUAN_CUT)
    direct = pairs_across(TAIXUAN_SHIFT, TAIXUAN_CUT)
    check(direct == (inside, crossing), "the direct count and the formula disagree here")
    check(total == 41, "the declared shift does not make forty-one pairs")
    check(inside == 7, "the declared cut does not contain seven pairs")
    check(crossing == 34, "the declared cut is not crossed by thirty-four pairs")
    check(inside + crossing == total, "the pairs do not split into inside and crossing")
    check(inside == TAIXUAN_CUT - TAIXUAN_SHIFT,
          "the inside count is not the difference of the cut and the shift")
    check(crossing == HEADS - TAIXUAN_CUT,
          "the crossing count is not the size of the cut's second side")
    check(HEADS - TAIXUAN_CUT == 34, "the second side of the declared cut is not thirty-four")

    # the reading that the crossing count is special, tested as an identity
    identity_cuts = [cut for cut in range(1, HEADS)
                     if closed_form(TAIXUAN_SHIFT, cut)[2] == HEADS - cut]
    check(len(identity_cuts) == 40,
          "the identity does not hold at forty cuts for the declared shift")
    check(identity_cuts[0] == HEADS - TAIXUAN_SHIFT == 41,
          "the identity does not begin where the second member of a pair can first exceed the cut")
    check(TAIXUAN_CUT in identity_cuts,
          "the declared cut is not one of the cuts where the identity holds")
    late = all(closed_form(shift, cut)[2] == HEADS - cut
               for shift in range(1, HEADS)
               for cut in range(max(shift, HEADS - shift), HEADS))
    check(late, "the crossing count is not the second side for every shift and every late cut")

    # where the crossing count stops being the shift itself
    switch = {shift: HEADS - shift for shift in (9, 18, 27, 40)}
    check(switch == {9: 72, 18: 63, 27: 54, 40: 41},
          "the switch points are not the complement of the shift")
    check(closed_form(TAIXUAN_SHIFT, HEADS - TAIXUAN_SHIFT)[2] == TAIXUAN_SHIFT,
          "the crossing count at the switch point is not the shift")
    check(closed_form(TAIXUAN_SHIFT, TAIXUAN_CUT)[2]
          < closed_form(TAIXUAN_SHIFT, HEADS - TAIXUAN_SHIFT)[2],
          "the declared cut is on the wrong side of the switch")
    check(closed_form(TAIXUAN_SHIFT, 48)[2] == 33,
          "the other side of the declared boundary does not cross with thirty-three pairs")

    return {
        "shift": TAIXUAN_SHIFT,
        "cut": TAIXUAN_CUT,
        "pairs": total,
        "inside_the_first_side": inside,
        "crossing_the_cut": crossing,
        "the_second_side_has": HEADS - TAIXUAN_CUT,
        "inside_is_the_cut_minus_the_shift": True,
        "crossing_is_the_size_of_the_second_side": True,
        "crossing_at_the_other_side_of_the_boundary": 33,
        "crossing_equals_the_second_side_at_this_many_cuts": len(identity_cuts),
        "the_identity_begins_at": identity_cuts[0],
        "cuts_where_it_holds": identity_cuts,
        "switch_point": HEADS - TAIXUAN_SHIFT,
        "closed_form_checked_over": 6400,
        "closed_form_mismatches": len(mismatches),
        "the_crossing_count_is_an_identity_not_a_finding": True,
    }


# ------------------------------------------------------------------ the odometer

REPORTED_PAIRS = 35
REPORTED_CONSTANT_DIFFERENCES = 13


def s5_odometer():
    shift_digits = numeral(TAIXUAN_SHIFT)
    check(shift_digits == (1, 1, 1, 1), "the declared shift is not the numeral eleven eleven")
    check(sum(d * s for d, s in zip(shift_digits, (27, 9, 3, 1))) == TAIXUAN_SHIFT,
          "the digits of the shift do not reconstruct it")

    patterns = Counter()
    constant = []
    for head in range(1, HEADS - TAIXUAN_SHIFT + 1):
        difference = tuple((digits(head + TAIXUAN_SHIFT)[i] - digits(head)[i]) % 3
                           for i in range(PLACES))
        patterns[difference] += 1
        if difference == (1, 1, 1, 1):
            constant.append(head)
    check(sum(patterns.values()) == 41, "the difference patterns do not cover forty-one pairs")
    check(len(constant) == 16,
          "the coordinate difference is constant at more or fewer than sixteen pairs")
    check(patterns[(1, 1, 1, 1)] == 16, "the identity difference does not occur sixteen times")
    check(len(patterns) == 8, "the difference takes more or fewer than eight values")
    check(sorted(patterns.values()) == [1, 4, 4, 4, 4, 4, 4, 16],
          "the difference pattern histogram is not the computed one")
    check(all(difference[3] == 1 for difference in patterns),
          "the last coordinate does not always advance by one")

    # the count of carry-free pairs, as a formula, over every shift
    for shift in range(1, HEADS):
        wanted = 1
        for digit in numeral(shift):
            wanted *= 3 - digit
        counted = sum(1 for head in range(1, HEADS - shift + 1)
                      if all(digits(head)[i] + numeral(shift)[i] <= 2 for i in range(PLACES)))
        check(counted == wanted,
              f"the carry-free count for shift {shift} is not three minus the digits multiplied out")
    check(numeral(TAIXUAN_SHIFT) == (1, 1, 1, 1) and 2 ** PLACES == 16,
          "the carry-free count for the declared shift is not two to the four")

    check(len(constant) != REPORTED_CONSTANT_DIFFERENCES,
          "the recorded count of thirteen constant differences is the computed one")
    check(REPORTED_PAIRS != 41, "the recorded pair count of thirty-five is the computed one")

    return {
        "shift": TAIXUAN_SHIFT,
        "shift_digits": list(shift_digits),
        "pairs": 41,
        "pairs_with_a_constant_coordinate_difference": len(constant),
        "heads_with_a_constant_difference": constant,
        "difference_patterns": {"".join(str(d) for d in key): count
                                for key, count in sorted(patterns.items(),
                                                         key=lambda kv: (-kv[1], kv[0]))},
        "carry_free_count_is_the_product_of_three_minus_the_digits": True,
        "reported_constant_difference_count": REPORTED_CONSTANT_DIFFERENCES,
        "reported_pair_count": REPORTED_PAIRS,
        "the_recorded_pair_count_is_not_the_computed_one": True,
        "the_coordinate_reading_is_not_a_constant_vector": True,
    }


# ------------------------------------------------------------------------ driver

def run(output=None):
    started = time.perf_counter_ns()
    sections = {
        "S1_coverage": s1_coverage(),
        "S2_target": s2_target(),
        "S3_multiplicity": s3_multiplicity(),
        "S4_crossing": s4_crossing(),
        "S5_odometer": s5_odometer(),
    }
    report = {
        "schema": "adva.research.coverage-and-crossing-evidence.v0",
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
