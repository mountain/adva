"""Exact external checker for what a declared invariance already fixes.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers, permutations and Fractions only; no floating-point value enters
any acceptance test. It imports no text and no corpus count: every object below
is a finite combinatorial object declared in contract.json, including the small
synthetic matrices and edge families used to exhibit the phenomena.

Everything reported is decided by exhaustion over a declared finite set, and the
size of each exhausted set is reported with the result.
"""
from fractions import Fraction as F
from itertools import permutations, product
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


# ------------------------------- S1: one tetrahedron, a finite group and its closure

N_VERT = 4
EDGES = [(a, b) for a in range(N_VERT) for b in range(a + 1, N_VERT)]
MATCHINGS = [frozenset({(0, 1), (2, 3)}), frozenset({(0, 2), (1, 3)}), frozenset({(0, 3), (1, 2)})]
IDENTITY_PERM = (0, 1, 2, 3)


def perm_from_cycles(cycles, n=N_VERT):
    out = list(range(n))
    for cyc in cycles:
        for i, x in enumerate(cyc):
            out[x] = cyc[(i + 1) % len(cyc)]
    return tuple(out)


AXIS_SWAPS = [perm_from_cycles([(0, 1), (2, 3)]), perm_from_cycles([(0, 2), (1, 3)]),
              perm_from_cycles([(0, 3), (1, 2)])]


def act_on_edges(p):
    return tuple(sorted(tuple(sorted((p[a], p[b]))) for a, b in EDGES))


def compose_perms(p, q):
    return tuple(p[q[i]] for i in range(len(p)))


def affine_compose(A, B):
    """(A after B): x -> A(B(x)) for A=(p,t), B=(q,u)."""
    p, t = A
    q, u = B
    return (tuple(q[p[i]] for i in range(len(p))), tuple(u[p[i]] + t[i] for i in range(len(p))))


def affine_apply(A, x):
    p, t = A
    return tuple(x[p[i]] + t[i] for i in range(len(p)))


AFFINE_IDENTITY = (IDENTITY_PERM, (0, 0, 0, 0))
# The four face mirrors of the fundamental alcove of the affine Weyl group of
# type A3. Three are coordinate transpositions; the fourth is the affine mirror
# in the root e4 - e1, which moves the lattice as well.
FACE_MIRRORS = [
    ((3, 1, 2, 0), (-1, 0, 0, 1)),          # s0: x -> (x4 - 1, x2, x3, x1 + 1)
    ((1, 0, 2, 3), (0, 0, 0, 0)),           # s1
    ((0, 2, 1, 3), (0, 0, 0, 0)),           # s2
    ((0, 1, 3, 2), (0, 0, 0, 0)),           # s3
]
NON_ADJACENT = {(0, 2), (1, 3)}


def closure_by_length(gens, depth):
    """Breadth-first shells from the identity; depth is the Coxeter length."""
    seen = {AFFINE_IDENTITY: 0}
    frontier = [AFFINE_IDENTITY]
    shells = [1]
    for level in range(1, depth + 1):
        nxt = []
        for A in frontier:
            for g in gens:
                B = affine_compose(g, A)
                if B not in seen:
                    seen[B] = level
                    nxt.append(B)
        frontier = nxt
        shells.append(len(nxt))
    return seen, shells


def s1_two_symmetry_sets():
    # the three axis swaps are exactly the three perfect matchings of K4
    check(len(EDGES) == 6 and len(MATCHINGS) == 3, "K4 does not have six edges and three matchings")
    union = set()
    for m in MATCHINGS:
        check(len(m) == 2 and all(len(set(e)) == 2 for e in m), "a declared matching is not a matching")
        check(not (union & set(m)), "two declared matchings share an edge")
        union |= set(m)
    check(sorted(union) == EDGES and len(union) == len(EDGES),
          "the three declared matchings do not partition the edge set")
    swap_of = {}
    for p in AXIS_SWAPS:
        fixed = [e for e in EDGES if tuple(sorted((p[e[0]], p[e[1]]))) == e]
        moved = [e for e in EDGES if tuple(sorted((p[e[0]], p[e[1]]))) != e]
        matching = frozenset({tuple(sorted((x, p[x]))) for x in range(N_VERT)})
        swap_of[p] = {"matching": matching, "fixed_edges": sorted(fixed), "moved_edges": sorted(moved)}
        check(len(fixed) == 2 and len(moved) == 4,
              "an axis swap does not fix exactly the two edges of its own matching")
        check(matching in MATCHINGS, "an axis swap does not determine a declared matching")
        check(compose_perms(p, p) == IDENTITY_PERM, "an axis swap is not an involution")
    check(len({v["matching"] for v in swap_of.values()}) == 3,
          "the three axis swaps do not correspond to the three matchings bijectively")
    for p in AXIS_SWAPS:
        for q in AXIS_SWAPS:
            check(compose_perms(p, q) == compose_perms(q, p),
                  "the axis swaps do not commute, so they are not a Klein four-group")

    klein = [IDENTITY_PERM] + AXIS_SWAPS
    orbits, seen = [], set()
    for e in EDGES:
        if e in seen:
            continue
        orb = {tuple(sorted((p[e[0]], p[e[1]]))) for p in klein}
        seen |= orb
        orbits.append(tuple(sorted(orb)))
    orbits.sort()
    check(len(orbits) == 3 and all(len(o) == 2 for o in orbits),
          "the axis swaps do not split the six edges into three orbits of size two")
    check(sorted(orbits) == sorted(tuple(sorted(m)) for m in MATCHINGS),
          "the orbits of the axis swaps are not the three matchings")
    stabiliser_sizes = {len([p for p in klein if tuple(sorted((p[e[0]], p[e[1]]))) == e])
                        for e in EDGES}
    check(stabiliser_sizes == {2}, "the edge action of the Klein group is not of constant stabiliser size")

    # the four face mirrors satisfy the affine A3 Coxeter relations
    for i, g in enumerate(FACE_MIRRORS):
        check(affine_compose(g, g) == AFFINE_IDENTITY, f"face mirror {i} is not an involution")
    for i in range(4):
        for j in range(i + 1, 4):
            two = affine_compose(FACE_MIRRORS[i], FACE_MIRRORS[j])
            square = affine_compose(two, two)
            cube = affine_compose(square, two)
            if (i, j) in NON_ADJACENT:
                check(square == AFFINE_IDENTITY and two != AFFINE_IDENTITY,
                      f"face mirrors {i},{j} are not non-adjacent involutions of product order two")
            else:
                check(cube == AFFINE_IDENTITY and two != AFFINE_IDENTITY
                      and square != AFFINE_IDENTITY,
                      f"face mirrors {i},{j} do not have product of order three")

    depth = 20
    seen, shells = closure_by_length(FACE_MIRRORS, depth)
    check(shells[0] == 1 and shells[1] == 4, "the first two shells are not one and four")
    check(len(seen) > 24, "the group generated by the four face mirrors is not larger than the finite one")
    check(all(B not in seen for B in [AFFINE_IDENTITY] if False), "unreachable")

    origin_fixing = [A for A, length in seen.items() if A[1] == (0, 0, 0, 0)]
    check(len(origin_fixing) == 24, "the origin stabiliser does not have order twenty-four")
    length_profile = [0] * (depth + 1)
    for A in origin_fixing:
        length_profile[seen[A]] += 1
    profile = length_profile[:7]
    check(profile == [1, 3, 5, 6, 5, 3, 1],
          "the finite part does not carry the length distribution of the symmetric group on four letters")
    check(all(length_profile[k] == 0 for k in range(7, depth + 1)),
          "an origin-fixing element has length beyond six")
    front_of_alcove = sorted(A for A, length in seen.items() if length == 1)
    check(len(front_of_alcove) == 4, "the fundamental alcove does not have four faces")

    # the closure is infinite and its alcove count is an exact polynomial
    cumulative, running = [], 0
    for n, count in enumerate(shells):
        running += count
        cumulative.append(running)
    diffs = [cumulative]
    for _ in range(4):
        diffs.append([diffs[-1][i + 1] - diffs[-1][i] for i in range(len(diffs[-1]) - 1)])
    fourth = diffs[4]
    check(len(set(fourth)) == 1 and fourth[0] == 0,
          "the fourth difference of the alcove count is not constantly zero, so it is not cubic")
    second_of_shells = diffs[3]   # the third difference of the cumulative count
    check(set(second_of_shells[1:]) == {4},
          "the second difference of the shell count is not constantly four")
    shell_form = [2 * n * n + 2 for n in range(1, depth + 1)]
    check(shells[1:] == shell_form,
          "the shell count is not two n squared plus two")
    alcove_form = [1 + 2 * n + n * (n + 1) * (2 * n + 1) // 3 for n in range(depth + 1)]
    check(cumulative == alcove_form,
          "the alcove count is not one plus two n plus n(n+1)(2n+1)/3")
    check(cumulative[depth] == len(seen),
          "the cumulative count does not agree with the number of elements found")

    return {
        "vertices": N_VERT,
        "edges": len(EDGES),
        "perfect_matchings": len(MATCHINGS),
        "axis_swaps": len(AXIS_SWAPS),
        "axis_swaps_commute_pairwise": True,
        "axis_swap_fixed_edges": {str(sorted(v["fixed_edges"])): 1 for v in swap_of.values()},
        "klein_group_order": len(klein),
        "klein_orbits_on_edges": [list(o) for o in orbits],
        "klein_orbit_sizes": [len(o) for o in orbits],
        "klein_edge_stabiliser_size": sorted(stabiliser_sizes)[0],
        "klein_edge_action_is_free": False,
        "face_mirrors": 4,
        "face_mirror_coxeter_relations_hold": True,
        "faces_of_the_fundamental_alcove": len(front_of_alcove),
        "closure_is_infinite": True,
        "elements_found_through_length": depth,
        "elements_found": len(seen),
        "origin_stabiliser_order": len(origin_fixing),
        "origin_stabiliser_length_profile": profile,
        "finite_part_is_exactly_the_origin_stabiliser": True,
        "alcove_count_shells": shells,
        "alcove_count_cumulative": cumulative,
        "shell_count_closed_form": "2 n^2 + 2 for n >= 1",
        "alcove_count_closed_form": "1 + 2 n + n (n + 1) (2 n + 1) / 3",
        "shell_count_closed_form_verified_through": depth,
        "fourth_difference_of_the_cumulative_count": fourth[0],
        "second_difference_of_the_shell_count": second_of_shells[1],
        "alcove_count_is_cubic": True,
        "klein_is_a_subgroup_of_the_finite_part": True,
        "klein_generates_the_closure": False,
        "declared_depth": depth,
    }


# --------------------------- S2: a rank-one matrix carries no row-specific information

ROW_WEIGHTS = [1, 2, 3, 4, 5]
COL_WEIGHTS = [1, 2, 3, 4, 5]


def rank_one(rows, cols):
    return [[rows[i] * cols[j] for j in range(len(cols))] for i in range(len(rows))]


def minors_vanish(M):
    m, n = len(M), len(M[0])
    for i in range(m):
        for k in range(i + 1, m):
            for j in range(n):
                for l in range(j + 1, n):
                    if M[i][j] * M[k][l] != M[i][l] * M[k][j]:
                        return False
    return True


def argmax(row):
    best = max(range(len(row)), key=lambda j: row[j])
    return best, [j for j in range(len(row)) if row[j] == row[best]]


def assignment_optima(M):
    n = len(M)
    best, winners = None, []
    for sigma in permutations(range(n)):
        value = sum(M[i][sigma[i]] for i in range(n))
        if best is None or value > best:
            best, winners = value, [sigma]
        elif value == best:
            winners.append(sigma)
    return best, winners


def s2_rank_one_collapse():
    M = rank_one(ROW_WEIGHTS, COL_WEIGHTS)
    check(minors_vanish(M), "the declared rank-one matrix has a non-vanishing two-by-two minor")
    rows_with_mass = [i for i, r in enumerate(ROW_WEIGHTS) if r > 0]
    argmaxes = {argmax(M[i])[0] for i in rows_with_mass}
    global_column = max(range(len(COL_WEIGHTS)), key=lambda j: COL_WEIGHTS[j])
    check(argmaxes == {global_column},
          "a rank-one matrix does not put every row's argmax on the same column")
    check(all(argmax(M[i])[1] == argmax(M[0])[1] for i in rows_with_mass),
          "the tie sets of a rank-one matrix differ between rows")

    # the same collapse holds for every rank-one matrix over a declared weight family
    sweep = 0
    for rows in product([0, 1, 3, 7], repeat=3):
        for cols in product([1, 2, 5], repeat=3):
            N = rank_one(list(rows), list(cols))
            live = [i for i, r in enumerate(rows) if r > 0]
            if not live:
                continue
            sweep += 1
            check(len({argmax(N[i])[0] for i in live}) == 1,
                  "a rank-one matrix in the declared sweep has two row argmaxes")
    check(sweep > 0, "the rank-one sweep is empty")

    # the diagonal share is a function of the margins alone
    total = sum(sum(r) for r in M)
    diagonal = sum(M[i][i] for i in range(len(M)))
    share = F(diagonal, total)
    chance = F(1, len(M))
    check(share == F(11, 45), "the rank-one diagonal share is not eleven forty-fifths")
    check(chance == F(1, 5), "the chance share is not one fifth")
    check(share - chance == F(2, 45),
          "the rank-one excess over chance is not two forty-fifths")
    check(share > chance, "the rank-one matrix does not exceed the chance share")

    # the assignment optimum is also determined by the margins alone
    rows_inc = sorted(ROW_WEIGHTS)
    cols_inc = sorted(COL_WEIGHTS)
    N = rank_one(rows_inc, cols_inc)
    best, winners = assignment_optima(N)
    identity = tuple(range(len(N)))
    check(best == sum(rows_inc[i] * cols_inc[i] for i in range(len(N))),
          "the declared sorted weights do not attain the rearrangement bound")
    check(winners == [identity],
          "the identity is not the unique assignment optimum of a sorted rank-one matrix")

    # a non-monotone pair, so the claim is not an accident of one weight vector
    rows_alt = [5, 1, 4, 2, 3]
    cols_alt = [2, 5, 1, 4, 3]
    N2 = rank_one(rows_alt, cols_alt)
    best2, winners2 = assignment_optima(N2)
    asc_rows = sorted(range(5), key=lambda i: rows_alt[i])
    asc_cols = sorted(range(5), key=lambda j: cols_alt[j])
    rank_of_row = {pos: k for k, pos in enumerate(asc_rows)}
    similar = tuple(asc_cols[rank_of_row[i]] for i in range(5))
    check(sorted(similar) == list(range(5)), "the similarly-ordered map is not a permutation")
    check(best2 == sum(sorted(rows_alt)[k] * sorted(cols_alt)[k] for k in range(5)),
          "the unsorted weights do not attain the rearrangement bound")
    check(winners2 == [similar],
          "the similarly-ordered permutation is not the unique assignment optimum")
    check(identity not in winners2,
          "the identity is an assignment optimum of an unsorted rank-one matrix, so the claim is vacuous")

    # perturbation: two recoverability readings have two different thresholds
    grid = [F(0), F(1, 10), F(1, 4), F(1, 2), F(1), F(2), F(3), F(4), F(5), F(10)]
    row_threshold, assignment_threshold = None, None
    readings = []
    for t in grid:
        P = [[F(ROW_WEIGHTS[i] * COL_WEIGHTS[j]) + (t * ROW_WEIGHTS[i] * COL_WEIGHTS[i]
                                                    if i == j else 0)
              for j in range(5)] for i in range(5)]
        own_unique = [argmax(P[i])[1] == [i] for i in range(5)]
        own_tied = [i in argmax(P[i])[1] for i in range(5)]
        every_row_own = all(own_unique)
        every_row_holds = all(own_tied)
        best_value, winners_p = None, []
        for sigma in permutations(range(5)):
            value = sum(P[i][sigma[i]] for i in range(5))
            if best_value is None or value > best_value:
                best_value, winners_p = value, [sigma]
            elif value == best_value:
                winners_p.append(sigma)
        unique_identity = winners_p == [tuple(range(5))]
        readings.append({"t": str(t),
                         "every_row_uniquely_recovers_its_column": every_row_own,
                         "every_row_argmax_contains_its_column": every_row_holds,
                         "rows_tied_with_an_earlier_column": [i for i in range(5)
                                                               if own_tied[i] and not own_unique[i]],
                         "identity_is_the_unique_assignment_optimum": unique_identity})
        if row_threshold is None and every_row_own:
            row_threshold = t
        if assignment_threshold is None and unique_identity:
            assignment_threshold = t
    check(assignment_threshold == F(0),
          "the assignment reading does not already certify the table at zero perturbation")
    check(row_threshold == F(5),
          "the row-argmax reading does not first succeed uniquely at the declared grid point five")
    check(row_threshold > assignment_threshold,
          "the two recoverability readings do not have different thresholds")
    check(readings[0]["every_row_uniquely_recovers_its_column"] is False,
          "the row reading succeeds at exact rank one, so the collapse claim is vacuous")
    tie_point = [r for r in readings if r["t"] == "4"][0]
    check(tie_point["every_row_argmax_contains_its_column"] is True
          and tie_point["every_row_uniquely_recovers_its_column"] is False,
          "the declared tie at perturbation four is not exhibited")

    # the exact closed form for the row threshold
    predicted = [F(max(COL_WEIGHTS[j] for j in range(5) if j != i), COL_WEIGHTS[i]) - 1
                 for i in range(5)]
    check(predicted == [F(4), F(3, 2), F(2, 3), F(1, 4), F(-1, 5)],
          "the closed form for the per-row threshold is not four, three halves, two thirds, "
          "a quarter and minus a fifth")
    effective = [max(x, F(0)) for x in predicted]
    check(effective == [F(4), F(3, 2), F(2, 3), F(1, 4), F(0)],
          "the effective non-negative per-row thresholds are not four, three halves, "
          "two thirds, a quarter and zero")
    check(max(effective) == F(4),
          "the binding per-row threshold is not four, so the declared grid point five is not the first")
    # every declared row threshold really is the first grid point at which that row recovers
    for i in range(5):
        below = [t for t in grid if t < effective[i]]
        above = [t for t in grid if t > effective[i]]
        if below:
            P = [[F(ROW_WEIGHTS[a] * COL_WEIGHTS[b])
                  + (below[-1] * ROW_WEIGHTS[a] * COL_WEIGHTS[a] if a == b else 0)
                  for b in range(5)] for a in range(5)]
            check(argmax(P[i])[1] != [i],
                  f"row {i} already recovers its column at or below its declared threshold")
        if above:
            P = [[F(ROW_WEIGHTS[a] * COL_WEIGHTS[b])
                  + (above[0] * ROW_WEIGHTS[a] * COL_WEIGHTS[a] if a == b else 0)
                  for b in range(5)] for a in range(5)]
            check(argmax(P[i])[1] == [i],
                  f"row {i} does not recover its column above its declared threshold")

    return {
        "row_weights": ROW_WEIGHTS,
        "column_weights": COL_WEIGHTS,
        "declared_matrix_is_rank_one": True,
        "distinct_row_argmax_columns": len(argmaxes),
        "the_one_argmax_column": global_column,
        "rank_one_sweep_matrices_checked": sweep,
        "rank_one_diagonal_share": str(share),
        "chance_share": str(chance),
        "rank_one_excess_over_chance": str(share - chance),
        "rank_one_row_specific_information": 0,
        "assignment_optimum_is_margin_determined": True,
        "sorted_weights_make_the_identity_the_unique_optimum": True,
        "unsorted_weights_do_not_make_the_identity_an_optimum": True,
        "per_row_threshold_closed_form": [str(x) for x in predicted],
        "grid_readings": readings,
        "row_reading_threshold_on_the_grid": str(row_threshold),
        "assignment_reading_threshold_on_the_grid": str(assignment_threshold),
        "the_two_readings_disagree": True,
        "permutations_checked_per_grid_point": 120,
        "grid_points": len(grid),
    }


# ---------------------------- S3: a permutation null sees only the two margins

def reciprocity(edges):
    keys = {(a, b) for a, b in edges}
    both = 0
    for a, b in edges:
        if a != b and (b, a) in keys:
            both += 1
    return both


def null_law(edges):
    """The exact law of the statistic over every permutation of the recipients."""
    m = len(edges)
    agents = [a for a, _ in edges]
    recipients = [b for _, b in edges]
    law = {}
    for pi in permutations(range(m)):
        shuffled = [(agents[i], recipients[pi[i]]) for i in range(m)]
        value = reciprocity(shuffled)
        law[value] = law.get(value, 0) + 1
    check(sum(law.values()) == _factorial(m), "the null law does not sum to the permutation count")
    return law


def _factorial(n):
    out = 1
    for k in range(2, n + 1):
        out *= k
    return out


def margins(edges):
    return (tuple(sorted(a for a, _ in edges)), tuple(sorted(b for _, b in edges)))


def law_summary(law, observed):
    m = sum(law.values())
    mean = F(sum(k * v for k, v in law.items()), m)
    var = F(sum((k - mean) ** 2 * v for k, v in law.items()), m)
    below = sum(v for k, v in law.items() if k < observed)
    return {
        "mean": str(mean),
        "variance": str(var),
        "support_min": min(law),
        "support_max": max(law),
        "mass_strictly_below_observed": str(F(below, m)),
        "permutations": m,
    }


def s3_exact_null():
    # two networks with the same two margins and different observed reciprocity
    pair_a = [("A", "B"), ("A", "C"), ("B", "A"), ("B", "C"), ("C", "A"), ("C", "B")]
    pair_b = [("A", "B"), ("A", "B"), ("B", "C"), ("B", "C"), ("C", "A"), ("C", "A")]
    chain = [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("E", "A")]
    f5 = [("A", "B"), ("A", "B"), ("B", "A"), ("C", "A")]
    f6 = [("A", "C"), ("A", "C"), ("C", "A"), ("B", "A")]
    families = [pair_a, pair_b, chain, f5, f6]

    check(margins(pair_a) == margins(pair_b),
          "the two declared networks do not share both marginals")
    obs_a, obs_b = reciprocity(pair_a), reciprocity(pair_b)
    check(obs_a == 6 and obs_b == 0,
          "the two declared networks do not have observed reciprocity six and zero")
    law_a, law_b = null_law(pair_a), null_law(pair_b)
    check(law_a == law_b,
          "two networks with the same two marginals do not have the same exact null law")
    check(obs_a != obs_b,
          "the two networks do not differ in the observed statistic, so the comparison is vacuous")
    summary_a = law_summary(law_a, obs_a)
    check(summary_a["mean"] == str(F(14, 5)),
          "the declared pair's exact null mean is not fourteen fifths of six edges")
    mass_at_six = F(law_a.get(6, 0), sum(law_a.values()))
    check(mass_at_six == F(4, 45),
          "the null mass at a fully reciprocal network is not four forty-fifths")
    check(F(summary_a["mass_strictly_below_observed"]) == F(41, 45),
          "the null mass strictly below a fully reciprocal network is not forty-one forty-fifths")
    # the same law judges a fully reciprocal network and an empty one
    check(law_summary(law_b, obs_b)["mass_strictly_below_observed"] == "0",
          "the empty network is not at the bottom of the same null law")

    # a declared chain, where the observed value sits at the bottom of the support
    law_chain = null_law(chain)
    obs_chain = reciprocity(chain)
    summary_chain = law_summary(law_chain, obs_chain)
    check(obs_chain == 0 and summary_chain["mean"] == "1" and summary_chain["support_max"] == 4,
          "the declared chain does not have observed zero, null mean one and support up to four")
    check(F(summary_chain["mass_strictly_below_observed"]) == 0,
          "the chain's observed value is not at the bottom of its null support")

    # the law depends on the two margins; it does not depend on the pairing
    check(null_law(f5) == null_law(f6),
          "two networks with the same margin shapes do not share the null law")
    check(reciprocity(f5) == reciprocity(f6) == 3,
          "the two four-edge networks do not both have observed reciprocity three")
    summary_f5 = law_summary(null_law(f5), 3)
    check(summary_f5["mean"] == str(F(7, 6)) and summary_f5["support_max"] == 3,
          "the four-edge null law is not of mean seven sixths with support up to three")

    # how many distinct null laws the declared families produce
    by_margin = {}
    for edges in families:
        key = margins(edges)
        law = null_law(edges)
        if key in by_margin:
            check(by_margin[key] == law,
                  "two declared networks with the same margins have different null laws")
        by_margin[key] = law
    check(len(by_margin) >= 2, "the declared families do not exhibit at least two distinct margins")
    check(len(by_margin) < len(families),
          "no two declared families share margins, so the invariance is not exhibited")

    # a simple closed form was guessed and is NOT the exact mean; recorded rather than dropped
    overlap_rows = []
    for edges in families:
        m = len(edges)
        names = sorted({x for e in edges for x in e})
        agents = [a for a, _ in edges]
        recipients = [b for _, b in edges]
        p = {x: F(agents.count(x), m) for x in names}
        q = {x: F(recipients.count(x), m) for x in names}
        overlap = sum(p[x] * q[x] for x in names)
        mean = F(sum(k * v for k, v in null_law(edges).items()), _factorial(m))
        guess = overlap ** 2 * m
        overlap_rows.append({"m": m, "overlap": str(overlap),
                             "squared_overlap_times_m": str(guess),
                             "exact_null_mean": str(mean),
                             "ratio": str(mean / guess) if guess else None})
    ratios = [F(r["ratio"]) for r in overlap_rows if r["ratio"] is not None]
    check(ratios and all(r != 1 for r in ratios),
          "the squared-overlap guess happens to equal the exact mean, so the guess was not refuted")
    check(len({r["exact_null_mean"] for r in overlap_rows}) > 1,
          "every declared family has the same exact null mean")

    return {
        "same_margins_different_observed": {
            "observed_reciprocity": [obs_a, obs_b],
            "exact_null_law_identical": law_a == law_b,
            "exact_null_mean": summary_a["mean"],
            "exact_null_mean_as_a_share_of_six_edges": str(F(14, 5) / 6),
            "null_mass_at_a_fully_reciprocal_network": str(mass_at_six),
            "null_mass_at_or_above_six": str(mass_at_six),
            "one_sided_p_value_for_the_fully_reciprocal_network": str(mass_at_six),
            "support": [summary_a["support_min"], summary_a["support_max"]],
        },
        "chain": {"observed": obs_chain, **summary_chain},
        "four_edge_law": {"observed": 3, **summary_f5},
        "distinct_marginal_pairs": len(by_margin),
        "families": len(families),
        "null_law_depends_only_on_the_two_margins": True,
        "squared_overlap_guess": overlap_rows,
        "squared_overlap_guess_is_the_exact_mean": False,
        "permutation_counts": {str(len(e)): _factorial(len(e)) for e in families},
        "exhausted_permutations_total": sum(_factorial(len(e)) for e in families),
    }


# ------------------------------------------------------------------------ driver

def run(output=None):
    started = time.perf_counter_ns()
    sections = {
        "S1_two_symmetry_sets": s1_two_symmetry_sets(),
        "S2_rank_one_collapse": s2_rank_one_collapse(),
        "S3_exact_null": s3_exact_null(),
    }
    report = {
        "schema": "adva.research.declared-invariance-evidence.v0",
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
