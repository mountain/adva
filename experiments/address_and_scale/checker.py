"""Exact external checker for what an address sees, what a modulus cannot, and a near miss.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers and Fractions only, and every acceptance test compares integers or
exact rationals. It opens no corpus and imports no corpus count: the formulas,
the constants, the four clauses transcribed into the contract and the reported
numbers are declared in contract.json and are checked arithmetically rather than
re-measured. The transcription is of a quotation, so the check is of the
transcription's arithmetic and is not a collation against any edition.

Everything reported is decided by exhaustion over a declared finite set, and the
size of each exhausted set is reported with the result.
"""
from fractions import Fraction as F
from itertools import combinations
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


# ------------------------------------------------- S1: the address algorithm

HEADS = 81
PLACES = 4


def coordinates(head):
    """One-based head number to zero-based places, highest place first."""
    index = head - 1
    out = []
    for size in (27, 9, 3, 1):
        digit, index = divmod(index, size)
        out.append(digit)
    return tuple(out)


def head_number(coords):
    return 27 * coords[0] + 9 * coords[1] + 3 * coords[2] + coords[3] + 1


def text_address_increments():
    """The four clauses the source is quoted to state, transcribed into the contract.

    Each clause gives, for one place, the increment that place contributes at each
    of its three values. The map below is built from these tables rather than from
    a formula typed into this file, so a transcription error changes the computed
    head number and the check fails.
    """
    contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
    declared = contract["objects"]["text_address_increments"]
    check(sorted(declared) == ["comment", "district", "family", "quarter", "section"],
          "the contract declares a key other than the four places and their comment")
    return {k: v for k, v in declared.items() if k != "comment"}


def head_from_clauses(clauses, fang, zhou, bu, jia):
    """The head number the four transcribed clauses give, places counted from one."""
    return (clauses["family"][jia - 1] + clauses["section"][bu - 1]
            + clauses["district"][zhou - 1] + clauses["quarter"][fang - 1])


def s1_declared_algorithm():
    """The four clauses transcribed from the source, and the coordinate formula."""
    clauses = text_address_increments()
    check(sorted(clauses) == ["district", "family", "quarter", "section"],
          "the contract does not declare the four places the source is quoted to state")
    check(all(len(table) == 3 for table in clauses.values()),
          "a transcribed clause does not give three values for its place")

    # each clause is an arithmetic progression, and its step is the place weight;
    # both are derived from the transcribed table rather than restated
    units, weights = {}, {}
    for name in sorted(clauses):
        table = clauses[name]
        unit = table[1] - table[0]
        units[name] = unit
        check(table[2] - table[1] == unit,
              f"the transcribed clause for {name} does not step by the same amount twice")
        check(table == [table[0] + unit * k for k in range(3)],
              f"the transcribed clause for {name} is not an arithmetic progression")
        weights[name] = [table[k] - table[0] for k in range(3)]
    check(weights == {"family": [0, 1, 2], "section": [0, 3, 6],
                      "district": [0, 9, 18], "quarter": [0, 27, 54]},
          "the weight tables derived from the transcribed clauses are not the ones the note reports")
    check(all(weights[name] == [units[name] * k for k in range(3)] for name in clauses),
          "a derived weight table is not the successive multiples of its place weight")
    ordered = [units[name] for name in ("family", "section", "district", "quarter")]
    check(ordered == [3 ** k for k in range(4)],
          "the place weights of the transcribed clauses are not the successive powers of three")
    check(all(a < b for a, b in zip(ordered, ordered[1:])),
          "the place weights of the transcribed clauses do not increase with the place")
    check(sum(clauses[name][0] for name in clauses) == 1,
          "the offsets of the four transcribed clauses do not sum to the one the head numbering starts at")

    # the map built from the transcribed clauses, compared with the coordinate formula
    matches = 0
    from_clauses = {}
    for head in range(1, HEADS + 1):
        fang, zhou, bu, jia = coordinates(head)
        declared = head_from_clauses(clauses, fang + 1, zhou + 1, bu + 1, jia + 1)
        from_clauses[head] = declared
        if declared == head:
            matches += 1
    check(matches == HEADS,
          "the clauses transcribed from the source do not reproduce every head number")
    check(len(set(from_clauses.values())) == HEADS,
          "the clauses transcribed from the source do not give eighty-one distinct head numbers")
    check(all(from_clauses[h] == head_number(coordinates(h)) for h in range(1, HEADS + 1)),
          "the map built from the transcribed clauses is not the coordinate formula")
    check(head_number((0, 0, 0, 0)) == 1 and head_number((2, 2, 2, 2)) == 81,
          "the coordinate formula does not run from one to eighty-one")
    check(len({head_number(c) for c in
               [(a, b, c, d) for a in range(3) for b in range(3) for c in range(3) for d in range(3)]})
          == HEADS,
          "the coordinate formula is not a bijection on the eighty-one heads")
    return {
        "heads": HEADS,
        "text_formula": "head = family + section + district + quarter, the four clauses as transcribed",
        "coordinate_formula": "index = 27·fang + 9·zhou + 3·bu + jia",
        "place_weights": {k: v for k, v in weights.items()},
        "place_weight_units": {k: units[k] for k in sorted(units)},
        "clauses_declared_in_the_contract": True,
        "the_map_is_built_from_the_transcribed_clauses": True,
        "the_transcription_is_checked_against_a_collated_edition": False,
        "heads_reproduced": matches,
        "the_two_formulas_agree_on_every_head": True,
        "exhausted_heads": HEADS,
    }


# ------------------------------------- S2: a division the address does see

def s2_nine_rows():
    rows = [n for n in range(1, HEADS + 1) if coordinates(n)[2] == 0 and coordinates(n)[3] == 0]
    check(rows == [1, 10, 19, 28, 37, 46, 55, 64, 73],
          "the nine heads with the last two places at their first value are not the declared nine")
    check(len(rows) == 9, "there are not nine such heads")
    check(all(rows[i + 1] - rows[i] == 9 for i in range(8)),
          "the nine heads are not equally spaced by nine")
    check(all(coordinates(n)[2] == 0 and coordinates(n)[3] == 0 for n in rows),
          "a member of the nine does not have its last two places at the first value")
    check(all((head_number((a, b, 0, 0)) in rows) for a in range(3) for b in range(3)),
          "the nine are not exactly the fiber over the first value of the last two places")
    constraints = sum(1 for k in (2, 3) if len({coordinates(n)[k] for n in rows}) == 1)
    check(constraints == 2,
          "the nine are not defined by exactly two place constraints")
    check(len({coordinates(n)[0] for n in rows}) == 3
          and len({coordinates(n)[1] for n in rows}) == 3,
          "the first two places do not run freely over the nine")
    return {
        "heads": rows,
        "count": len(rows),
        "spacing": 9,
        "place_constraints_needed": constraints,
        "first_two_places_free": True,
        "the_nine_are_the_fiber_over_two_fixed_places": True,
        "exhausted_heads": HEADS,
    }


# ------------------------------------ S3: a division no nontrivial modulus sees

CUT = 47


def is_union_of_classes(members, modulus, universe):
    for x in members:
        k = -20
        while True:
            y = x + k * modulus
            k += 1
            if y > max(universe):
                break
            if y < min(universe):
                continue
            if y not in members:
                return False, (x, y)
    return True, None


def s3_modulus():
    universe = set(range(1, HEADS + 1))
    prefix = set(range(1, CUT + 1))
    tail = set(range(CUT + 1, HEADS + 1))
    check(len(prefix) == 47 and len(tail) == 34, "the two sides are not forty-seven and thirty-four")

    working = []
    witnesses = {}
    for m in range(2, HEADS + 1):
        ok, witness = is_union_of_classes(prefix, m, universe)
        if ok:
            working.append(m)
        else:
            witnesses[m] = witness
    check(working == [81],
          "a modulus other than the full count makes the prefix a union of residue classes")
    check(81 in working and len(working) == 1,
          "the only working modulus is not the trivial full count")
    check(len(witnesses) == HEADS - 2,
          "the number of failing moduli is not seventy-nine")
    check(all(w is not None for w in witnesses.values()),
          "a failing modulus has no witness pair")

    # the two cases of the proof, checked on the data
    small = [m for m in range(2, 35)]
    large = [m for m in range(35, 81)]
    check(len(small) == 33 and len(large) == 46, "the proof cases do not split at thirty-four")
    small_span_ok = all(len(tail) >= m for m in small)
    check(small_span_ok,
          "the tail does not outnumber the classes for every small modulus")
    distinct_large = all(len({x % m for x in tail}) == len(tail) for m in large)
    check(distinct_large,
          "two elements of the tail are congruent for some large modulus")
    check(CUT + 1 == 48 and HEADS - CUT == 34,
          "the tail does not begin at forty-eight with thirty-four elements")
    return {
        "cut": CUT,
        "sides": [47, 34],
        "moduli_exhausted": HEADS - 1,
        "moduli_that_work": working,
        "nontrivial_moduli_that_work": 0,
        "failing_moduli": len(witnesses),
        "first_witness_pairs": {str(m): witnesses[m] for m in sorted(witnesses)[:4]},
        "small_case_tail_outnumbers_the_classes": small_span_ok,
        "large_case_tail_elements_are_distinct": distinct_large,
        "the_cut_is_not_a_congruence": True,
    }


# ------------------------------- S4: the boundary is a translate of another boundary

SHIFT = (1, 2, 1, 1)
PAIRS = {"before": (7, 47), "after": (8, 48)}


def shifted(coords, shift=SHIFT):
    return tuple((coords[k] + shift[k]) % 3 for k in range(PLACES))


def s4_translate():
    differences = {}
    for name, (a, b) in PAIRS.items():
        diff = tuple((coordinates(b)[k] - coordinates(a)[k]) % 3 for k in range(PLACES))
        differences[name] = diff
        check(diff == SHIFT,
              f"the difference from head {a} to head {b} is not the declared shift")
    check(differences["before"] == differences["after"],
          "the two pairs are not carried by the same shift")
    check(coordinates(PAIRS["before"][0]) == (0, 0, 2, 0),
          "the head before the first pair is not at the declared coordinates")
    check(coordinates(PAIRS["before"][1]) == (1, 2, 0, 1),
          "the head after the first pair is not at the declared coordinates")
    check(all(coordinates(PAIRS["after"][i]) == ((0, 0, 2, 1), (1, 2, 0, 2))[i] for i in range(2)),
          "the second pair is not at the declared coordinates")

    order = 1
    cur = shifted((0, 0, 0, 0))
    while cur != (0, 0, 0, 0):
        cur = shifted(cur)
        order += 1
    check(order == 3, "the declared shift does not have order three")
    check(all(shifted(shifted(shifted(c))) == c
              for c in [(a, b, cc, d) for a in range(3) for b in range(3)
                        for cc in range(3) for d in range(3)]),
          "the shift does not return every head to itself in three steps")

    orbits = {}
    for name, (a, _) in PAIRS.items():
        orb, cur = [], coordinates(a)
        for _ in range(3):
            orb.append(head_number(cur))
            cur = shifted(cur)
        orbits[name] = orb
    check(orbits["before"] == [7, 47, 69], "the orbit of the first head is not seven, forty-seven, sixty-nine")
    check(orbits["after"] == [8, 48, 67], "the orbit of the second head is not eight, forty-eight, sixty-seven")
    check(set(orbits["before"]) & set(orbits["after"]) == set(),
          "the two orbits are not disjoint")

    # the whole space splits into twenty-seven three-cycles under this shift
    seen, cycles = set(), []
    for start in range(1, HEADS + 1):
        if start in seen:
            continue
        orb, cur = [], coordinates(start)
        while head_number(cur) not in seen:
            seen.add(head_number(cur))
            orb.append(head_number(cur))
            cur = shifted(cur)
        cycles.append(orb)
    check(len(cycles) == 27 and all(len(c) == 3 for c in cycles),
          "the shift does not split the eighty-one heads into twenty-seven three-cycles")
    check(sorted(n for c in cycles for n in c) == list(range(1, HEADS + 1)),
          "the three-cycles do not cover the heads exactly once")

    return {
        "pairs": {k: list(v) for k, v in PAIRS.items()},
        "shift": list(SHIFT),
        "the_two_pairs_share_one_shift": True,
        "shift_order": order,
        "orbit_before": orbits["before"],
        "orbit_after": orbits["after"],
        "orbits_disjoint": True,
        "three_cycles": len(cycles),
        "cycle_length": 3,
        "the_boundary_is_the_translate_of_the_other_boundary": True,
    }


# ------------------------------------- S5: the river diagram is a quotient by five

RIVER = {"water": (1, 6), "fire": (2, 7), "wood": (3, 8), "metal": (4, 9), "earth": (5,)}


def s5_river():
    numbers = list(range(1, 10))
    classes = {}
    for x in numbers:
        classes.setdefault(x % 5, []).append(x)
    fibres = sorted(tuple(v) for v in classes.values())
    expected = sorted([(5,), (1, 6), (2, 7), (3, 8), (4, 9)])
    check(fibres == expected,
          "the fibers of reduction modulo five on one to nine are not the declared pairs")
    check(sorted(tuple(sorted(v)) for v in RIVER.values()) == expected,
          "the declared river pairs are not those fibers")
    check(all(len(v) == 2 for k, v in RIVER.items() if k != "earth"),
          "a river pair other than earth does not have two members")
    check(all(v[1] - v[0] == 5 for k, v in RIVER.items() if k != "earth"),
          "a river pair does not differ by five")
    check(RIVER["earth"] == (5,),
          "the earth pair is not the single number five")
    # ten is written as zero, so the shift by five on the ten numbers is fixed-point free
    involution_fixed = [x for x in range(10) if (x + 5) % 10 == x]
    check(involution_fixed == [],
          "the shift by five on the ten residues has a fixed point")
    ten_labels = {x: ((x + 5) % 10) or 10 for x in range(1, 11)}
    check(ten_labels[5] == 10 and ten_labels[10] == 5,
          "the fifth pair is not five against ten on the ten numbers")
    without_a_partner = [x for x in range(1, 10) if ten_labels[x] not in range(1, 10)]
    check(without_a_partner == [5],
          "five is not the only number left without a partner inside one to nine")
    check(ten_labels[5] == 10 and 10 not in range(1, 10),
          "the partner of five does not lie outside the range")
    labels = {x: name for name, vals in RIVER.items() for x in vals}
    check(len(labels) == 9 and sorted(labels) == list(range(1, 10)),
          "the labels do not cover one to nine exactly once")
    check(all(labels[x] == labels[y] for x in range(1, 10) for y in range(1, 10)
              if x % 5 == y % 5),
          "two numbers in the same residue class carry different labels")
    check(len({labels[x] for x in range(1, 10)}) == 5,
          "the labels do not take exactly five values on one to nine")
    check(len({labels[x] for x in range(1, 10)}) == len({tuple(f) for f in fibres}),
          "the number of labels is not the number of fibers")
    return {
        "numbers": numbers,
        "fibers_of_reduction_modulo_five": [list(f) for f in fibres],
        "river_pairs": {k: list(v) for k, v in RIVER.items()},
        "every_pair_differs_by_five": True,
        "the_shift_on_ten_residues_has_no_fixed_point": True,
        "the_shift_restricted_to_one_to_nine_has_exactly_one_fixed_point": 5,
        "the_label_is_a_function_of_the_class": True,
        "the_fifth_pair_is_five_against_ten_on_ten_numbers": True,
        "restricting_to_one_to_nine_leaves_exactly_one_number_without_a_partner": 5,
        "exhausted_numbers": len(numbers),
    }


# ------------------------------- S6: the near miss that the grid already forces

CYCLE = F(729, 2)             # the seven hundred twenty-nine praises of half a day
YEAR = F(731, 2)              # the same cycle plus the two extra praises, that is one more day
NODES = 24
BOUNDARY_SPACING = F(9, 2)    # one head is nine praises, one praise is half a day
BOUNDARY_COUNT = HEADS
CUT_DAY = F(9, 2) * CUT
REPORTED_NODE = 15


def s6_calendar():
    check(F(36 * 729) == F(26244), "the product of the bundle count and the praise count is not the declared total")
    check(F(26244, 72) == CYCLE,
          "the total divided by seventy-two is not three hundred sixty-four and a half days")
    check(CYCLE + 2 * F(1, 2) == YEAR,
          "adding the two extra praises does not give the declared year")
    check(CYCLE == F(729, 2) and YEAR == F(731, 2),
          "the cycle and the year are not seven hundred twenty-nine and seven hundred thirty-one half-days")
    check(YEAR * 2 == 731, "the year is not seven hundred thirty-one half-days")
    check(BOUNDARY_SPACING * 2 == 9, "one head is not nine praises")
    check(CUT_DAY == F(423, 2),
          "the cut is not at two hundred eleven and a half days")
    check(F(9 * (HEADS - CUT), 2) == F(306, 2) and F(423 + 306, 2) == F(729, 2),
          "the two sides do not split the seven hundred twenty-nine praises as four twenty-three and three hundred six")
    check(F(423, 2) + F(306, 2) == F(729, 2), "the two sides do not sum to the whole cycle")

    spacing = YEAR / NODES
    check(spacing == F(731, 48), "the node spacing is not seven hundred thirty-one over forty-eight")
    reach = BOUNDARY_SPACING / 2
    check(reach == F(9, 4), "the grid is not within nine quarters of a day of every node")
    # the gap of a node is its exact distance to the nearest of the eighty-one head
    # boundaries, computed over every boundary rather than taken from a rounding
    rows = []
    for k in range(1, NODES + 1):
        t = (k - 1) * spacing
        gap, nearest = min((abs(t - m * BOUNDARY_SPACING), m) for m in range(0, HEADS + 2))
        rows.append({"node": k, "day": str(t), "day_float": round(float(t), 4),
                     "gap": str(gap), "gap_float": round(float(gap), 6),
                     "nearest_boundary": nearest, "boundaries_compared": HEADS + 2,
                     "relative": str(gap / t) if t else None,
                     "relative_float": round(float(gap / t), 6) if t else None})
        check(gap <= reach, f"node {k} is further than nine quarters of a day from every boundary")
        check(nearest == round(t / BOUNDARY_SPACING),
              f"the nearest boundary of node {k} is not the one a rounding of the quotient names")
    check(len(rows) == NODES, "there are not twenty-four nodes")

    relative = [F(r["relative"]) for r in rows if r["relative"] is not None]
    best = min(relative)
    worst = max(relative)
    ordered = sorted(relative)
    median = ordered[len(ordered) // 2]
    reported = F(rows[REPORTED_NODE - 1]["relative"])
    check(best < reported, "the reported node is not beaten by another node")
    check(F(76) < reported / best, "the best node is not far closer than the reported one")
    check(reported > median, "the reported node is not worse than the median node")
    check(median == F(49, 8041), "the median relative gap is not the declared fraction")
    reported_gap = F(rows[REPORTED_NODE - 1]["gap"])
    check(reported_gap == F(41, 24),
          "the reported node's gap is not forty-one twenty-fourths of a day")
    check(reported_gap > reach / 2,
          "the reported node's gap is not above half the reach, that is above the even-spread value")
    check(rows[REPORTED_NODE - 1]["day"] == str(F(5117, 24)),
          "the reported node's day is not the declared fraction")
    # the reported gap is the exact distance from that node to its nearest boundary,
    # recomputed over all eighty-one boundaries as an exact rational
    reported_day = F(rows[REPORTED_NODE - 1]["day"])
    check(min(abs(reported_day - m * BOUNDARY_SPACING) for m in range(0, HEADS + 2)) == reported_gap,
          "the reported node's gap is not the exact distance to its nearest head boundary")
    check(reported_gap != min(F(r["gap"]) for r in rows),
          "the reported node is the closest node, so the ranking claim would be empty")
    return {
        "cycle": str(CYCLE),
        "cycle_float": 364.5,
        "two_extra_praises_are_one_day": True,
        "year": str(YEAR),
        "year_float": 365.5,
        "boundary_spacing": str(BOUNDARY_SPACING),
        "boundary_count": BOUNDARY_COUNT,
        "grid_reach": str(reach),
        "grid_reach_days": 2.25,
        "cut_day": str(CUT_DAY),
        "cut_day_float": 211.5,
        "sides_in_praises": [423, 306],
        "node_spacing": str(spacing),
        "nodes": rows,
        "best_relative": str(best),
        "best_relative_float": round(float(best), 6),
        "best_node": rows[[F(r["relative"]) for r in rows if r["relative"] is not None].index(best) + 1]["node"],
        "worst_relative": str(worst),
        "median_relative": str(median),
        "reported_node": REPORTED_NODE,
        "reported_relative": str(reported),
        "reported_relative_float": round(float(reported), 6),
        "reported_node_gap_days": str(rows[REPORTED_NODE - 1]["gap"]),
        "reported_rank_by_closeness": ordered.index(reported) + 1,
        "nodes_compared": len(ordered),
        "every_node_is_within_the_reach_by_construction": True,
        "the_reported_near_miss_is_worse_than_the_median": True,
    }


# ------------------------------------------------------------------------ driver

def run(output=None):
    started = time.perf_counter_ns()
    sections = {
        "S1_declared_algorithm": s1_declared_algorithm(),
        "S2_nine_rows": s2_nine_rows(),
        "S3_modulus": s3_modulus(),
        "S4_translate": s4_translate(),
        "S5_river": s5_river(),
        "S6_calendar": s6_calendar(),
    }
    report = {
        "schema": "adva.research.address-and-scale-evidence.v0",
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
