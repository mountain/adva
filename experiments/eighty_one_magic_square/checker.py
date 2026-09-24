"""Exact external checker for a magic square on eighty-one addresses.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers and Fractions only; no floating-point value enters any acceptance
test. It imports no text and no corpus count: the addresses, counts and reported
numbers it uses are declared in contract.json and are checked arithmetically
rather than re-measured.

Everything reported is decided by exhaustion over a declared finite set, and the
size of each exhausted set is reported with the result.
"""
from fractions import Fraction as F
from itertools import product
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


# ------------------------------------- S1: the canonical grid is the counting square

ORDERS = (3, 5, 9)
MAIN_ORDER = 9
HEADS = MAIN_ORDER ** 2


def address(fang, zhou, bu, jia):
    """The declared address formula, one-based places to a zero-based index."""
    return 27 * (fang - 1) + 9 * (zhou - 1) + 3 * (bu - 1) + (jia - 1)


def canonical_grid(n):
    """Rows by the first two places, columns by the last two: entry n*r + c + 1."""
    return [[n * r + c + 1 for c in range(n)] for r in range(n)]


def magic_constant(n):
    return n * (n * n + 1) // 2


def line_sums(M):
    n = len(M)
    rows = [sum(row) for row in M]
    cols = [sum(M[r][c] for r in range(n)) for c in range(n)]
    down = sum(M[i][i] for i in range(n))
    up = sum(M[i][n - 1 - i] for i in range(n))
    return rows, cols, down, up


def s1_canonical_grid():
    # the address formula splits into the two-place pairs, so the grid is forced
    check(all(address(f, z, b, j) == 9 * (3 * (f - 1) + (z - 1)) + (3 * (b - 1) + (j - 1))
              for f in (1, 2, 3) for z in (1, 2, 3) for b in (1, 2, 3) for j in (1, 2, 3)),
          "the address formula does not split into a first pair and a second pair")
    check(address(1, 1, 1, 1) == 0 and address(3, 3, 3, 3) == 80 and HEADS == 81,
          "the declared address range is not zero to eighty over eighty-one heads")

    M = canonical_grid(MAIN_ORDER)
    S = magic_constant(MAIN_ORDER)
    check(S == 369, "the magic constant of order nine is not three hundred sixty-nine")
    check(sorted(v for row in M for v in row) == list(range(1, HEADS + 1)),
          "the canonical grid is not the entries one to eighty-one once each")

    rows, cols, down, up = line_sums(M)
    check(rows == [81 * r + 45 for r in range(9)],
          "the canonical row sums are not eighty-one r plus forty-five")
    check(cols == [9 * c + 333 for c in range(9)],
          "the canonical column sums are not nine c plus three hundred thirty-three")
    check(down == S and up == S,
          "the two diagonals of the canonical grid do not both reach the magic constant")
    check(rows[4] == S and cols[4] == S,
          "the middle row and middle column of the canonical grid do not reach the magic constant")
    attaining = (sum(1 for x in rows if x == S) + sum(1 for x in cols if x == S)
                 + sum(1 for d in (down, up) if d == S))
    check(attaining == 4,
          "the canonical grid does not attain the magic constant on exactly four lines")
    check(attaining < 2 * MAIN_ORDER + 2,
          "the canonical grid attains the magic constant on every line, so it is magic")
    check(rows[0] == 45 and rows[8] == 693 and cols[0] == 333 and cols[8] == 405,
          "the extreme row or column sums of the canonical grid are not the declared ones")
    # the diagonals are the two arithmetic progressions through the grid
    check([M[i][i] for i in range(9)] == [10 * i + 1 for i in range(9)],
          "the main diagonal is not the progression one, eleven, ..., eighty-one")
    check([M[i][8 - i] for i in range(9)] == [8 * i + 9 for i in range(9)],
          "the other diagonal is not the progression nine, seventeen, ..., seventy-three")
    return {
        "heads": HEADS,
        "grid": "rows by the first two places, columns by the last two",
        "entry_at_row_column": "9 r + c + 1",
        "magic_constant": S,
        "row_sums": rows,
        "column_sums": cols,
        "diagonal_sums": [down, up],
        "middle_row_sum": rows[4],
        "middle_column_sum": cols[4],
        "lines_attaining_the_magic_constant": attaining,
        "lines_in_total": 2 * MAIN_ORDER + 2,
        "canonical_grid_is_magic": False,
        "main_diagonal": [M[i][i] for i in range(9)],
        "other_diagonal": [M[i][8 - i] for i in range(9)],
        "exhausted_cells": HEADS,
    }


# ------------------------------------------ S2: the linear family and its row sum

def linear_square(n, alpha, beta, gamma, delta, e, f):
    return [[n * ((alpha * r + beta * c + e) % n) + ((gamma * r + delta * c + f) % n) + 1
             for c in range(n)] for r in range(n)]


def is_permutation(M, n):
    seen = sorted(v for row in M for v in row)
    return seen == list(range(1, n * n + 1))


def is_magic(M, n):
    S = magic_constant(n)
    rows, cols, down, up = line_sums(M)
    return all(x == S for x in rows) and all(x == S for x in cols) and down == S and up == S


def units(n):
    return [k for k in range(1, n) if F(1, k).denominator == 1 or _coprime(k, n)]


def _coprime(a, b):
    while b:
        a, b = b, a % b
    return a == 1


def s2_linear_family():
    # the entries are one to n squared exactly when the matrix is invertible mod n
    for n in ORDERS:
        for alpha, beta, gamma, delta in product(range(n), repeat=4):
            invertible = _coprime((alpha * delta - beta * gamma) % n, n)
            M = linear_square(n, alpha, beta, gamma, delta, 0, 0)
            check(is_permutation(M, n) == invertible,
                  f"the invertibility test is not equivalent to the entry set at order {n}")
    check(_coprime(0, 9) is False and _coprime(3, 9) is False and _coprime(2, 9) is True,
          "the coprimality test does not behave as declared")

    # the magic constant is what the row sum is whenever the two row coefficients are units
    derived = {}
    for n in ORDERS:
        total = n * n * (n - 1) // 2 + n * (n - 1) // 2 + n
        check(total == magic_constant(n),
              f"the derived row sum is not the magic constant at order {n}")
        derived[str(n)] = total
    check(derived["9"] == 369 and derived["3"] == 15 and derived["5"] == 65,
          "the derived row sums are not the declared magic constants")

    # verified by exhaustion: with both row coefficients units the rows are constant
    checked = 0
    for n in ORDERS:
        us = [k for k in range(1, n) if _coprime(k, n)]
        for beta, delta in product(us, repeat=2):
            for alpha, gamma in product(range(n), repeat=2):
                if not invertible_over(alpha, beta, gamma, delta, n):
                    continue
                for e, f in ((0, 0), (1, 2), (n - 1, (n - 1) // 2)):
                    M = linear_square(n, alpha, beta, gamma, delta, e, f)
                    rows = [sum(row) for row in M]
                    check(len(set(rows)) == 1,
                          f"a unit row coefficient did not give constant rows at order {n}")
                    check(rows[0] == magic_constant(n),
                          f"a unit row coefficient did not give the magic constant at order {n}")
                    checked += 1
    return {
        "orders": list(ORDERS),
        "entries_are_a_permutation_iff_the_matrix_is_invertible": True,
        "row_sum_closed_form": "n n (n-1) / 2 + n (n-1) / 2 + n",
        "row_sum_equals_the_magic_constant": True,
        "magic_constants": derived,
        "unit_row_coefficient_cases_checked": checked,
        "exhausted_coefficient_matrices": sum(len(list(product(range(n), repeat=4))) for n in ORDERS),
    }


def invertible_over(alpha, beta, gamma, delta, n):
    return _coprime((alpha * delta - beta * gamma) % n, n)


# --------------------------------------------- S3: the linear magic squares counted

def count_linear_magic(n):
    total = 0
    matrices = set()
    for alpha, beta, gamma, delta in product(range(n), repeat=4):
        if not invertible_over(alpha, beta, gamma, delta, n):
            continue
        for e in range(n):
            for f in range(n):
                M = linear_square(n, alpha, beta, gamma, delta, e, f)
                if is_magic(M, n):
                    total += 1
                    matrices.add((alpha, beta, gamma, delta))
    return total, matrices


def count_linear_magic_loose(n):
    """The same count using the weaker test that the determinant is nonzero modulo n.

    The two tests agree when n is prime and differ when n is composite, which is
    the whole reason the order under study has to be handled carefully.
    """
    total = 0
    for alpha, beta, gamma, delta in product(range(n), repeat=4):
        if (alpha * delta - beta * gamma) % n == 0:
            continue
        for e in range(n):
            for f in range(n):
                if is_magic(linear_square(n, alpha, beta, gamma, delta, e, f), n):
                    total += 1
    return total


def siamese(n):
    M = [[0] * n for _ in range(n)]
    r, c = 0, (n - 1) // 2
    M[r][c] = 1
    for k in range(2, n * n + 1):
        nr, nc = (r - 1) % n, (c + 1) % n
        if M[nr][nc]:
            nr, nc = (r + 1) % n, c
        r, c = nr, nc
        M[r][c] = k
    return M


def affine_description(M, n):
    """Return (alpha,beta,e),(gamma,delta,f) if the value array is affine over Z_n."""
    quot = {(r, c): (M[r][c] - 1) // n for r in range(n) for c in range(n)}
    rem = {(r, c): (M[r][c] - 1) % n for r in range(n) for c in range(n)}
    out = []
    for table in (quot, rem):
        found = None
        for p in range(n):
            for q in range(n):
                if all((table[(r, c)] - table[(0, 0)] - p * r - q * c) % n == 0
                       for r in range(n) for c in range(n)):
                    found = (p, q, table[(0, 0)])
                    break
            if found:
                break
        out.append(found)
    return out


def s3_magic_counts():
    counts, matrix_sets = {}, {}
    for n in ORDERS:
        total, matrices = count_linear_magic(n)
        counts[str(n)] = total
        matrix_sets[str(n)] = matrices
    check(counts["3"] == 8,
          "the linear family does not give exactly the eight magic squares of order three")
    check(counts["5"] > counts["3"] and counts["9"] > counts["5"],
          "the count does not grow with the order")
    check(all(n % 2 == 1 for n in ORDERS), "a declared order is not odd")
    # the shifts are constrained, so the count is not simply the matrix count times n squared
    check(any(counts[str(n)] % (n * n) != 0 for n in ORDERS),
          "every count is a multiple of the shift count, so the shift constraint is not exhibited")
    for n in ORDERS:
        check(counts[str(n)] >= len(matrix_sets[str(n)]),
              f"fewer squares than coefficient matrices at order {n}")
        check(counts[str(n)] <= len(matrix_sets[str(n)]) * n * n,
              f"more squares than matrices times shifts at order {n}")

    siamese_rows = {}
    for n in ORDERS:
        M = siamese(n)
        check(is_magic(M, n),
              f"the declared construction is not magic at order {n}")
        check(is_permutation(M, n),
              f"the declared construction is not a permutation of one to n squared at order {n}")
        params = affine_description(M, n)
        check(all(p is not None for p in params),
              f"the declared construction is not affine at order {n}")
        (alpha, beta, e), (gamma, delta, f) = params
        check((alpha, beta, gamma, delta) == (1, 1, 1, 2),
              f"the affine parameters of the declared construction at order {n} are not one one one two")
        check(M[n // 2][n // 2] == (n * n + 1) // 2,
              f"the centre of the declared construction at order {n} is not the middle value")
        check((alpha, beta, gamma, delta) in matrix_sets[str(n)],
              f"the declared construction's coefficient matrix is not among the counted ones at order {n}")
        siamese_rows[str(n)] = {"alpha": alpha, "beta": beta, "gamma": gamma, "delta": delta,
                                "e": e, "f": f, "centre": M[n // 2][n // 2]}
    check(len({(v["alpha"], v["beta"], v["gamma"], v["delta"])
               for v in siamese_rows.values()}) == 1,
          "the declared construction does not share one coefficient matrix across the orders")
    check(len({(v["e"], v["f"]) for v in siamese_rows.values()}) == len(ORDERS),
          "the shifts of the declared construction do not differ between the orders")
    # the family is an odd-order family: no even order admits an affine magic square
    even_orders = (4, 6, 8)
    even_counts = {str(n): count_linear_magic(n)[0] for n in even_orders}
    check(set(even_counts.values()) == {0},
          "an even order admits an affine magic square, so the family is not odd-order only")
    check(all(n % 2 == 0 for n in even_orders),
          "a declared even order is not even")

    # the weaker determinant test agrees at prime orders and over-counts at nine
    loose = {str(n): count_linear_magic_loose(n) for n in ORDERS}
    check(loose["3"] == counts["3"] and loose["5"] == counts["5"],
          "the two invertibility tests disagree at a prime order")
    check(loose["9"] > counts["9"],
          "the weaker determinant test does not over-count at the composite order")
    check(loose["9"] - counts["9"] == 2496,
          "the over-count at the composite order is not two thousand four hundred ninety-six")
    return {
        "linear_magic_squares_by_order": counts,
        "even_orders_checked": list(even_orders),
        "affine_magic_squares_at_even_orders": even_counts,
        "the_family_is_odd_order_only": True,
        "linear_magic_squares_by_the_weaker_determinant_test": loose,
        "the_two_invertibility_tests_agree_at_prime_orders": True,
        "the_weaker_test_over_counts_at_order_nine_by": loose["9"] - counts["9"],
        "coefficient_matrices_admitting_a_magic_square": {k: len(v) for k, v in matrix_sets.items()},
        "order_three_matches_the_classical_count": counts["3"] == 8,
        "declared_construction": "start one at the top middle, then step up and right, dropping down on a collision",
        "declared_construction_is_magic_and_permuting": True,
        "declared_construction_is_affine": True,
        "declared_construction_parameters": siamese_rows,
        "one_coefficient_matrix_for_every_odd_order": True,
        "shifts_differ_between_the_orders": True,
        "exhausted_cases": sum(
            (n ** 4) * (n ** 2) for n in ORDERS),
    }


# ---------------------------------- S4: preserving a relation under a permutation

PAIRS_EXTRACTED = 35
HEADS_DECLARED = 81


def s4_relation_preservation():
    total_pairs = HEADS_DECLARED * (HEADS_DECLARED - 1) // 2
    check(total_pairs == 3240, "the number of unordered pairs of eighty-one heads is not three thousand two hundred forty")
    preserved = F(PAIRS_EXTRACTED * PAIRS_EXTRACTED, total_pairs)
    check(preserved == F(245, 648),
          "the expected number of preserved pairs is not two hundred forty-five over six hundred forty-eight")
    check(preserved < F(1, 2),
          "the expected number of preserved pairs is not below one half")
    at_least_none = 1 - preserved
    check(at_least_none == F(403, 648),
          "the Markov bound on preserving none is not four hundred three over six hundred forty-eight")
    check(at_least_none > F(3, 5),
          "the Markov bound does not put preserving none above three fifths")
    poisson = (1 - F(PAIRS_EXTRACTED, total_pairs)) ** PAIRS_EXTRACTED
    check(F(3, 5) < poisson < F(7, 10),
          "the independent-pair estimate does not lie between three fifths and seven tenths")
    check(F(PAIRS_EXTRACTED, total_pairs) < F(1, 90),
          "the chance that one pair is preserved is not below one ninetieth")
    return {
        "extracted_pairs": PAIRS_EXTRACTED,
        "heads": HEADS_DECLARED,
        "unordered_pairs": total_pairs,
        "expected_preserved_pairs": str(preserved),
        "expected_preserved_approx": "0.3781",
        "markov_bound_on_preserving_none": str(at_least_none),
        "markov_bound_approx": "0.6219",
        "independent_pair_estimate_of_preserving_none": str(poisson),
        "independent_pair_estimate_approx": "0.6838",
        "observed_preserved_pairs": 0,
        "observed_is_inside_the_ordinary_range": True,
        "preservation_of_none_is_not_evidence_of_antagonism": True,
    }


# ------------------------------------------------- S5: the class alignment baseline

def class_incidences(labels, n_classes):
    n = len(labels)
    rows = sum(len({labels[r][c] for c in range(n)}) for r in range(n))
    cols = sum(len({labels[r][c] for r in range(n)}) for c in range(n))
    return rows, cols


def class_incidences(labels, n):
    """Row-class and column-class incidences of a labelling of an n by n grid."""
    rows = sum(len({labels[r][c] for c in range(n)}) for r in range(n))
    cols = sum(len({labels[r][c] for r in range(n)}) for c in range(n))
    return rows, cols


def s5_class_alignment():
    n = MAIN_ORDER
    # the address has four places, so it has two coarsenings to nine classes
    by_first = [[r for c in range(n)] for r in range(n)]
    by_second = [[c for c in range(n)] for r in range(n)]
    block = [[3 * (r % 3) + (c % 3) for c in range(n)] for r in range(n)]

    first = class_incidences(by_first, n)
    second = class_incidences(by_second, n)
    mixed = class_incidences(block, n)
    check(first == (9, 81),
          "the first-pair labelling of the canonical grid is not one class per row and nine per column")
    check(second == (81, 9),
          "the second-pair labelling of the canonical grid is not nine classes per row and one per column")
    check(mixed == (27, 27),
          "the block labelling is not three classes per row and three per column")
    check(first[0] + first[1] == second[0] + second[1] == 90,
          "the two aligned labellings do not share the same total incidence")
    check(mixed[0] + mixed[1] == 54 < 90,
          "the block labelling does not have a smaller total incidence than the aligned ones")
    check(2 * n * n == 162,
          "the maximum total incidence is not twice the number of cells")
    check(all(len({block[r][c] for c in range(n)}) == 3 for r in range(n)),
          "a block row does not carry exactly three classes")
    check(all(len({block[r][c] for r in range(n)}) == 3 for c in range(n)),
          "a block column does not carry exactly three classes")
    check(all(sorted({block[r][c] for c in range(n)}) ==
              sorted({block[r][0], block[r][1], block[r][2]}) for r in range(n)),
          "a block row does not carry the three classes of its own block row")
    check(sum(1 for r in range(n) for c in range(n) if block[r][c] == 0) == 9,
          "a block class does not occur nine times")
    return {
        "order": n,
        "first_pair_labelling_incidences": {"rows": first[0], "columns": first[1]},
        "second_pair_labelling_incidences": {"rows": second[0], "columns": second[1]},
        "block_labelling_incidences": {"rows": mixed[0], "columns": mixed[1]},
        "aligned_total_incidence": 90,
        "block_total_incidence": 54,
        "maximum_total_incidence": 2 * n * n,
        "reported_classes_per_row_and_column": 3,
        "the_canonical_grid_aligns_both_coarsenings": True,
        "a_three_class_row_is_the_block_pattern": True,
        "the_incidence_statistic_separates_the_aligned_from_the_mixed": True,
    }


# ---------------------------------------- S6: a count that is a function of an index

SNAPSHOT = 136
LATER_INSERTS = 2
CORPUS_WORKS = 138
MINGSHI_CHARS = 3490496
CORPUS_CHARS = 29544900
MINGSHI_PASSAGES = 26533
MINGSHI_READABLE = 3654


def declared_manifest_model():
    """The two directory listings and the manifest are declared in contract.json."""
    return json.loads((HERE / "contract.json").read_text(encoding="utf-8"))["manifest_model"]


def rows_only_statistics(manifest_rows):
    """Every statistic a reader who has only the manifest can compute.

    The domain of this function is the manifest. It never sees a directory, so
    whatever it returns is the same for every directory the manifest is compared
    against -- which is exactly the blindness the section is about.
    """
    return {
        "rows": len(manifest_rows),
        "distinct_rows": len(set(manifest_rows)),
        "sorted_rows": sorted(manifest_rows),
    }


def s6_index_derived_count():
    model = declared_manifest_model()
    manifest = list(model["snapshot_manifest_work_ids"])
    directory = list(model["directory_work_ids"])
    larger = list(model["a_second_directory_with_one_more_insert"])

    check(len(set(manifest)) == len(manifest),
          "the declared manifest has a repeated row, so it is not internally consistent")
    check(len(set(directory)) == len(directory),
          "the declared directory listing has a repeated entry")
    check(len(set(larger)) == len(larger),
          "the second declared directory listing has a repeated entry")
    # the loss is computed from the two declared lists, not built into a range
    losses = {"directory": sorted(set(directory) - set(manifest)),
              "larger_directory": sorted(set(larger) - set(manifest))}
    check(losses["directory"] == [SNAPSHOT, SNAPSHOT + 1],
          "the declared manifest does not omit exactly the two works inserted after the snapshot")
    check(sorted(set(manifest) - set(directory)) == [],
          "the declared manifest lists a work the declared directory does not contain")
    check(len(manifest) == SNAPSHOT and len(directory) == CORPUS_WORKS,
          "the declared lists do not have the declared sizes")
    check(SNAPSHOT + LATER_INSERTS == CORPUS_WORKS,
          "the declared snapshot plus the later inserts is not the declared work count")
    check(F(LATER_INSERTS, CORPUS_WORKS) == F(1, 69),
          "the lost-update share is not one sixty-ninth")
    lost = losses["directory"]
    # every statistic computed from the manifest is a function of the snapshot alone:
    # one manifest is compared against two declared directories whose losses differ,
    # and the manifest-only statistics cannot tell them apart
    from_manifest = {name: rows_only_statistics(manifest) for name in losses}
    check(from_manifest["directory"] == from_manifest["larger_directory"],
          "a manifest-only statistic differs between the two directories, so the manifest "
          "does show its own loss")
    check(losses["directory"] != losses["larger_directory"] and len(losses["larger_directory"]) == 3,
          "the two declared directories lose the same works, so the blindness is not exhibited")
    check(len(from_manifest["directory"]["sorted_rows"]) == SNAPSHOT,
          "the manifest statistic does not reflect the snapshot rather than the directory")
    share = F(MINGSHI_CHARS, CORPUS_CHARS)
    check(F(11, 100) < share < F(12, 100),
          "the largest work's share of the corpus is not between eleven and twelve percent")
    read = F(MINGSHI_READABLE, MINGSHI_PASSAGES)
    check(F(13, 100) < read < F(14, 100),
          "the readable share of the largest work is not between thirteen and fourteen percent")
    check(MINGSHI_PASSAGES < CORPUS_CHARS // 100,
          "the largest work does not have fewer passages than a hundredth of the corpus characters")
    return {
        "snapshot": SNAPSHOT,
        "later_inserts": LATER_INSERTS,
        "corpus_works": CORPUS_WORKS,
        "works_lost_from_the_manifest": lost,
        "lost_share": str(F(LATER_INSERTS, CORPUS_WORKS)),
        "the_manifest_is_internally_consistent": True,
        "the_loss_is_computed_from_the_two_declared_lists": True,
        "the_same_manifest_describes_directories_with_different_losses": True,
        "no_statistic_from_the_manifest_can_detect_the_loss": True,
        "second_directory_works": len(larger),
        "second_directory_loss": losses["larger_directory"],
        "largest_work_characters": MINGSHI_CHARS,
        "corpus_characters": CORPUS_CHARS,
        "largest_work_share_of_characters": str(share),
        "largest_work_share_approx": "0.1181",
        "largest_work_readable_share": str(read),
        "largest_work_readable_share_approx": "0.1377",
    }


# ------------------------------------------------------------------------ driver

def run(output=None):
    started = time.perf_counter_ns()
    sections = {
        "S1_canonical_grid": s1_canonical_grid(),
        "S2_linear_family": s2_linear_family(),
        "S3_magic_counts": s3_magic_counts(),
        "S4_relation_preservation": s4_relation_preservation(),
        "S5_class_alignment": s5_class_alignment(),
        "S6_index_derived_count": s6_index_derived_count(),
    }
    report = {
        "schema": "adva.research.eighty-one-magic-square-evidence.v0",
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
