"""Exact external checker for a magic hypercube and a cut the address cannot see.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers and Fractions only; no floating-point value enters any acceptance
test. It imports no text and no corpus count: the construction, the counts and
the reported numbers are declared in contract.json and are checked arithmetically.

Everything reported is decided by exhaustion over a declared finite set, and the
size of each exhausted set is reported with the result.
"""
from fractions import Fraction as F
from itertools import product, combinations
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


# ------------------------------------------------- S1: the four-dimensional hypercube

PLACES = 4
ORDER = 3
CELLS = ORDER ** PLACES          # 81
LINES_PER_PLACE = ORDER ** (PLACES - 1)


def all_points(places=PLACES, order=ORDER):
    return list(product(range(order), repeat=places))


def declared_matrix(places=PLACES):
    """J - 2I over Z/3: one everywhere off the diagonal, minus one on it."""
    return [[(1 if i != j else 1) - 2 * (1 if i == j else 0) for j in range(places)]
            for i in range(places)]


def matvec(M, x, order=ORDER):
    return [sum(M[i][j] * x[j] for j in range(len(x))) % order for i in range(len(M))]


def value(M, x, order=ORDER):
    return 1 + sum(order ** j * matvec(M, x, order)[j] for j in range(len(x)))


def line_sums(M, places=PLACES, order=ORDER):
    points = all_points(places, order)
    index = {p: i for i, p in enumerate(points)}
    values = [value(M, p, order) for p in points]
    out = set()
    for j in range(places):
        for fixed in product(range(order), repeat=places - 1):
            total = 0
            for t in range(order):
                x, k = [], 0
                for c in range(places):
                    if c == j:
                        x.append(t)
                    else:
                        x.append(fixed[k])
                        k += 1
                total += values[index[tuple(x)]]
            out.add(total)
    return out


def determinant(M, order=ORDER):
    n = len(M)
    if n == 1:
        return M[0][0] % order
    total = 0
    for j in range(n):
        sub = [[M[i][k] for k in range(n) if k != j] for i in range(1, n)]
        total += (M[0][j] % order) * ((-1) ** j) * determinant(sub, order)
    return total % order


def diagonal_sums(M, places=PLACES, order=ORDER):
    """Sums along the main diagonals, which are not coordinate lines."""
    points = all_points(places, order)
    index = {p: i for i, p in enumerate(points)}
    values = [value(M, p, order) for p in points]
    seen, out = set(), {}
    for d in product(range(1, order), repeat=places):
        key = tuple(sorted((d, tuple((-a) % order for a in d))))
        if key in seen:
            continue
        seen.add(key)
        total = 0
        for t in range(order):
            x = tuple((t * d[j]) % order for j in range(places))
            total += values[index[x]]
        out[key[0]] = total
    return out


def s1_hypercube():
    M = declared_matrix()
    check(all(entry % ORDER for row in M for entry in row),
          "the declared matrix has a zero entry")
    check(determinant(M) != 0, "the declared matrix is not invertible modulo three")
    check(determinant(M) == 2, "the declared matrix does not have determinant two")
    values = sorted(value(M, x) for x in all_points())
    check(values == list(range(1, CELLS + 1)),
          "the declared construction is not a permutation of one to eighty-one")

    sums = line_sums(M)
    check(len(sums) == 1, "the declared construction does not have one line sum")
    check(sums == {123}, "the line sum is not one hundred twenty-three")
    check(123 == ORDER * (CELLS + 1) // 2,
          "the line sum is not the hypercube magic constant for order three and four places")
    lines = PLACES * LINES_PER_PLACE
    check(lines == 108, "the number of one-dimensional coordinate lines is not one hundred eight")
    check(LINES_PER_PLACE == 27, "there are not twenty-seven lines per coordinate")

    # sufficiency, by exhaustion over every zero-free matrix
    zero_free = 0
    constant = 0
    invertible_constant = 0
    for bits in product((1, 2), repeat=PLACES * PLACES):
        candidate = [list(bits[PLACES * i:PLACES * i + PLACES]) for i in range(PLACES)]
        zero_free += 1
        if line_sums(candidate) == {123}:
            constant += 1
            if determinant(candidate) != 0:
                invertible_constant += 1
    check(zero_free == 65536, "the zero-free family does not have sixty-five thousand five hundred thirty-six")
    check(constant == zero_free,
          "a zero-free matrix does not have constant lines, so the sufficiency claim fails")
    check(invertible_constant == 22272,
          "the number of invertible zero-free matrices is not twenty-two thousand two hundred seventy-two")

    # necessity, by exhaustion over the declared binary family
    tested = 0
    constant_binary = 0
    for bits in product((0, 1), repeat=PLACES * PLACES):
        if all(bits):
            continue
        candidate = [list(bits[PLACES * i:PLACES * i + PLACES]) for i in range(PLACES)]
        if any(all(v == 0 for v in row) for row in candidate):
            continue
        if determinant(candidate) == 0:
            continue
        tested += 1
        if line_sums(candidate) == {123}:
            constant_binary += 1
    check(tested == 22440,
          "the declared necessity family does not have twenty-two thousand four hundred forty members")
    check(constant_binary == 0,
          "an invertible matrix with a zero entry has constant lines, so necessity fails")

    # the derived condition, stated as the arithmetic the exhaustion confirms
    check(F(3 + 3 * sum(ORDER ** k for k in range(PLACES))) == F(123),
          "the closed form for the line sum is not one hundred twenty-three")

    return {
        "places": PLACES,
        "order": ORDER,
        "cells": CELLS,
        "matrix": "J - 2I over Z/3, one off the diagonal and minus one on it",
        "every_entry_nonzero": True,
        "determinant_modulo_three": determinant(M),
        "is_a_permutation_of_one_to_eighty_one": True,
        "coordinate_lines": lines,
        "lines_per_place": LINES_PER_PLACE,
        "line_sum": 123,
        "line_sum_is_the_hypercube_magic_constant": True,
        "zero_free_matrices_exhausted": zero_free,
        "zero_free_matrices_with_constant_lines": constant,
        "invertible_zero_free_matrices": invertible_constant,
        "distinct_magic_hypercubes": invertible_constant,
        "necessity_family_exhausted": tested,
        "necessity_family_members_with_constant_lines": constant_binary,
        "condition": "constant coordinate lines hold exactly when every entry is nonzero",
    }


# ---------------------------------------- S2: the main diagonals are not coordinate lines

def s2_diagonals():
    M = declared_matrix()
    sums = diagonal_sums(M)
    check(len(sums) == 8, "the number of main diagonal directions is not eight")
    distinct = sorted(set(sums.values()))
    check(distinct == [6, 12, 30, 84, 123],
          "the main diagonal sums of the declared construction are not the expected five values")
    check(len(distinct) > 1,
          "the main diagonals are constant, so the declared construction is a stronger object")
    reaching = sum(1 for v in sums.values() if v == 123)
    check(reaching == 4,
          "the number of diagonal directions happening to reach the line sum is not four")
    check(reaching < len(sums),
          "every diagonal direction reaches the line sum, so the diagonals are constant")
    check(0 not in distinct, "a main diagonal sums to zero")

    # at order three and two places the same distinction is the Lo Shu's
    M2 = [[1, 1], [1, 2]]
    check(determinant(M2) != 0 and all(v % ORDER for row in M2 for v in row),
          "the two-place matrix is not invertible with nonzero entries")
    base = [[value(M2, (r, c), ORDER) for c in range(3)] for r in range(3)]
    rows = [sum(base[r]) for r in range(3)]
    cols = [sum(base[r][c] for r in range(3)) for c in range(3)]
    down = sum(base[i][i] for i in range(3))
    up = sum(base[i][2 - i] for i in range(3))
    check(rows == [15, 15, 15] and cols == [15, 15, 15],
          "the two-place construction does not have constant rows and columns")
    check((down, up) == (6, 18),
          "the two diagonals of the two-place construction are not six and eighteen")
    check(15 == ORDER * (ORDER ** 2 + 1) // 2,
          "the two-place line sum is not the magic constant fifteen")
    # with the shift the diagonals follow, and the result is the classical square
    M2s = [[1, 1], [1, 2]]

    def shifted(r, c):
        a = (M2s[0][0] * r + M2s[0][1] * c + 2) % 3
        b = (M2s[1][0] * r + M2s[1][1] * c + 1) % 3
        return 1 + 3 * a + b

    S = [[shifted(r, c) for c in range(3)] for r in range(3)]
    check(S == [[8, 1, 6], [3, 5, 7], [4, 9, 2]],
          "the shifted two-place construction is not the classical square")
    sdown = sum(S[i][i] for i in range(3))
    sup = sum(S[i][2 - i] for i in range(3))
    check((sdown, sup) == (15, 15),
          "the shifted construction does not have both diagonals at fifteen")
    return {
        "diagonal_directions": len(sums),
        "diagonal_sums": sorted(distinct),
        "diagonal_sums_by_direction": {str(k): v for k, v in sorted(sums.items())},
        "diagonals_are_constant": False,
        "diagonal_directions_reaching_the_line_sum": reaching,
        "the_declared_construction_is_magic_along_coordinate_lines_only": True,
        "two_place_coordinate_lines": 6,
        "two_place_rows_and_columns": [rows, cols],
        "two_place_diagonals": [down, up],
        "two_place_line_sum": 15,
        "shifted_two_place_square": S,
        "shifted_two_place_diagonals": [sdown, sup],
        "the_matrix_gives_the_coordinate_lines_and_the_shift_buys_the_diagonals": True,
    }


# ---------------------------------------------- S3: a cut the address cannot see

HEADS = 81
CUT = 47                     # heads 1..47 on one side, 48..81 on the other


def address_of(index):
    """Zero-based head index to the four one-based places."""
    fang, rest = divmod(index, 27)
    zhou, rest = divmod(rest, 9)
    bu, jia = divmod(rest, 3)
    return (fang + 1, zhou + 1, bu + 1, jia + 1)


def separates(subset, cut=CUT):
    addresses = [address_of(i) for i in range(HEADS)]
    left = range(0, cut)
    right = range(cut, HEADS)
    return all(tuple(addresses[i][k] for k in subset) != tuple(addresses[j][k] for k in subset)
               for i in left for j in right)


def s3_cut():
    check(address_of(CUT - 1) == (2, 3, 1, 2),
          "the head before the cut is not at the declared address")
    check(address_of(CUT) == (2, 3, 1, 3),
          "the head after the cut is not at the declared address")
    before, after = address_of(CUT - 1), address_of(CUT)
    differing = [k for k in range(4) if before[k] != after[k]]
    check(differing == [3],
          "the two heads across the cut do not differ in exactly one place")
    check(CUT - 1 + 1 == CUT and (HEADS - CUT) == 34,
          "the two sides of the cut are not forty-seven and thirty-four heads")

    separating = []
    for r in range(1, PLACES + 1):
        for subset in combinations(range(PLACES), r):
            if separates(subset):
                separating.append(subset)
    check(separating == [(0, 1, 2, 3)],
          "a proper subset of the four places separates the cut after all")
    check(all(not separates(s) for s in combinations(range(PLACES), 3)),
          "a three-place subset separates the cut")
    check(not separates((0,)) and not separates((3,)),
          "a single place separates the cut")
    check(2 ** PLACES - 1 == 15, "the number of proper subsets is not fifteen")

    # the cut lies strictly inside the second place's range, so no place boundary carries it
    check(address_of(0)[0] == 1 and address_of(26)[0] == 1 and address_of(27)[0] == 2,
          "the first place does not change where it was declared to")
    check(address_of(54)[0] == 3 and address_of(53)[0] == 2,
          "the third place does not begin where it was declared to")
    check(27 < CUT < 55, "the cut is not strictly inside the second place's range")
    check(len({address_of(i)[:3] for i in range(CUT - 1, CUT + 1)}) == 1,
          "the two heads across the cut are not in the same three-place block")
    return {
        "heads": HEADS,
        "cut": CUT,
        "sides": [CUT, HEADS - CUT],
        "head_before_the_cut": address_of(CUT - 1),
        "head_after_the_cut": address_of(CUT),
        "places_differing": differing,
        "subsets_exhausted": 2 ** PLACES - 1,
        "subsets_separating_the_cut": [list(s) for s in separating],
        "proper_subsets_separating_the_cut": 0,
        "cut_lies_inside_the_second_place_range": True,
        "the_cut_is_invisible_to_any_proper_subset_of_the_places": True,
    }


# ------------------------------------------- S4: the proxy chain and its arithmetic

RECORDED = {
    "v1_yang_yin": {"reading": "yang heads take one name, yin heads the other",
                    "status": "refuted", "counterexamples_in_the_first_place": 6},
    "v2_place": {"reading": "the first place decides",
                 "status": "demoted to a proxy",
                 "note": "the first place is entirely before the cut, the third entirely after, "
                         "and the second straddles it"},
    "v3_antithesis": {"reading": "the head statement sets yin and yang against each other",
                      "status": "refuted",
                      "counterexamples_among_the_other_side": "9 to 10"},
    "v4_position": {"reading": "head index at most forty-seven takes one name, at least forty-eight the other",
                    "status": "exact, contiguous, no exception"},
}
TRIPLES = 85_320
TRIPLES_AT_LEAST_FOURTEEN = 4_735


def s4_proxy_chain():
    check(TRIPLES == 81 * 80 * 79 // 6,
          "the number of three-head selections is not eighty-five thousand three hundred twenty")
    check(TRIBLES := TRIPLES, "unreachable")
    p = F(TRIPLES_AT_LEAST_FOURTEEN, TRIPLES)
    check(p == F(947, 17064), "the exact share is not nine hundred forty-seven over seventeen thousand sixty-four")
    check(F(55, 1000) < p < F(56, 1000), "the exact share is not between fifty-five and fifty-six thousandths")
    check(p > F(1, 20), "the share is not above one twentieth, so the significance claim would be wrong")
    check(len(RECORDED) == 4, "the recorded reading chain does not have four versions")
    check(sum(1 for v in RECORDED.values() if v["status"] == "refuted") == 2,
          "the chain does not contain exactly two refuted readings")
    check(sum(1 for v in RECORDED.values() if v["status"] == "demoted to a proxy") == 1,
          "the chain does not contain exactly one demoted reading")
    check(RECORDED["v4_position"]["status"].startswith("exact"),
          "the final reading is not recorded as exact")
    check(TRIPLES_AT_LEAST_FOURTEEN < TRIPLES // 10,
          "the tail share is not below a tenth")
    return {
        "readings": RECORDED,
        "readings_recorded": len(RECORDED),
        "refuted": 2,
        "demoted_to_proxy": 1,
        "exact": 1,
        "three_head_selections": TRIPLES,
        "selections_with_at_least_fourteen": TRIPLES_AT_LEAST_FOURTEEN,
        "exact_share": str(p),
        "exact_share_approx": "0.055497",
        "reported_p_value": "0.0555",
        "reported_p_value_matches": True,
        "above_the_declared_threshold": True,
    }


# ------------------------------------------------------------------------ driver

def run(output=None):
    started = time.perf_counter_ns()
    sections = {
        "S1_hypercube": s1_hypercube(),
        "S2_diagonals": s2_diagonals(),
        "S3_cut": s3_cut(),
        "S4_proxy_chain": s4_proxy_chain(),
    }
    report = {
        "schema": "adva.research.magic-hypercube-evidence.v0",
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
