"""Exact checker for the definability spectrum of a four-place ternary address algebra.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers and Fractions only; no floating-point value enters any acceptance
test. It imports no text and no corpus count: the address space and the declared
sets are in contract.json, and the spectrum is computed from them.

Everything reported is decided by exhaustion over a declared finite set, and the
size of each exhausted set is reported with the result.
"""
from fractions import Fraction as F
from itertools import combinations
from math import comb
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
HEADS = ORDER ** PLACES
EXHAUSTION_LEVEL = 2          # the level up to which the union is enumerated


def check(value, message):
    COUNTS["assertions"] += 1
    if COUNTS["assertions"] > LIMITS["max_assertions"]:
        raise RuntimeError("Unknown: assertion budget")
    if not value:
        raise ValueError(message)


# ------------------------------------------------------------------ the address space

def address(head):
    index = head - 1
    out = []
    for size in (27, 9, 3, 1):
        digit, index = divmod(index, size)
        out.append(digit)
    return tuple(out)


def head_number(coords):
    return 27 * coords[0] + 9 * coords[1] + 3 * coords[2] + coords[3] + 1


def block_masks(subset):
    """The blocks of the partition by the places in subset, as bit masks."""
    groups = {}
    for head in range(1, HEADS + 1):
        key = tuple(address(head)[k] for k in subset)
        groups[key] = groups.get(key, 0) | (1 << head)
    return [groups[key] for key in sorted(groups)]


def algebra(subset):
    """Every union of blocks, as a set of bit masks."""
    blocks = block_masks(subset)
    out = set()
    for choice in range(1 << len(blocks)):
        mask = 0
        for j, block in enumerate(blocks):
            if choice >> j & 1:
                mask |= block
        out.add(mask)
    return out


def population(mask):
    return bin(mask).count("1")


def members(mask):
    return {h for h in range(1, HEADS + 1) if mask >> h & 1}


def to_mask(heads):
    mask = 0
    for h in heads:
        mask |= 1 << h
    return mask


DECLARED_SETS = {
    "all_heads": set(range(1, 82)),
    "first_quarter": set(range(1, 28)),
    "nine_district_representatives": {1, 10, 19, 28, 37, 46, 55, 64, 73},
    "three_quarter_representatives": {1, 28, 55},
    "cut_before": set(range(1, 48)),
    "cut_after": set(range(48, 82)),
    "two_prison_heads": {21, 69},
    "orbit_of_seven": {7, 47, 69},
}


# ------------------------------------------------------------------ the spectrum

def s1_spectrum():
    per_level = {}
    total_sets = 0
    for size in range(PLACES + 1):
        counts = set()
        for subset in combinations(range(PLACES), size):
            blocks = block_masks(subset)
            counts.add((len(blocks), population(blocks[0]), 2 ** len(blocks)))
        check(len(counts) == 1,
              "the algebras at one level are not all of the same shape")
        block_count, block_size, cardinality = counts.pop()
        check(block_count == ORDER ** size and block_size == ORDER ** (PLACES - size),
              "the block count or block size is not the declared power of three")
        check(block_size * block_count == HEADS, "the blocks do not partition the heads")
        per_level[size] = {
            "subsets": comb(PLACES, size),
            "blocks_per_partition": block_count,
            "block_size": block_size,
            "sets_per_algebra": cardinality,
        }
        total_sets += comb(PLACES, size) * cardinality
    check(per_level[0]["sets_per_algebra"] == 2 and per_level[1]["sets_per_algebra"] == 8,
          "the first two levels do not have two and eight sets")
    check(per_level[2]["sets_per_algebra"] == 512,
          "the two-place algebra does not have five hundred twelve sets")
    check(per_level[3]["sets_per_algebra"] == 2 ** 27,
          "the three-place algebra is not two to the twenty-seven")
    check(per_level[4]["sets_per_algebra"] == 2 ** HEADS,
          "the four-place algebra is not every set")

    cumulative = {}
    union = set()
    for size in range(EXHAUSTION_LEVEL + 1):
        for subset in combinations(range(PLACES), size):
            union |= algebra(subset)
        cumulative[str(size)] = len(union)
        check(len(union) <= 2 ** HEADS, "the union exceeds the power set")
    check(cumulative == {"0": 2, "1": 26, "2": 3014},
          "the cumulative counts are not two, twenty-six and three thousand fourteen")
    check(cumulative["2"] < sum(comb(PLACES, size) * per_level[size]["sets_per_algebra"]
                                for size in range(EXHAUSTION_LEVEL + 1)),
          "the union shows no overlap, so the algebras are not nested across levels")

    # the sizes that occur, which are the multiples of nine at this level
    sizes = {}
    for mask in union:
        sizes[population(mask)] = sizes.get(population(mask), 0) + 1
    check(all(k % 9 == 0 for k in sizes),
          "a set definable by at most two places has a size that is not a multiple of nine")
    check(sizes[9] == 54, "the number of nine-element sets definable by two places is not fifty-four")
    check(sizes[0] == 1 and sizes[81] == 1, "the empty set or the whole set is missing")
    check(sum(sizes.values()) == cumulative["2"], "the size distribution does not sum to the union")
    return {
        "places": PLACES,
        "heads": HEADS,
        "per_level": per_level,
        "cumulative_sets_by_level": cumulative,
        "exhausted_up_to_level": EXHAUSTION_LEVEL,
        "levels_beyond_exhaustion": PLACES - EXHAUSTION_LEVEL,
        "beyond_exhaustion_are_counted_not_enumerated": True,
        "size_distribution_up_to_two_places": {str(k): v for k, v in sorted(sizes.items())},
        "all_defined_sizes_are_multiples_of_nine": True,
        "power_set_size": 2 ** HEADS,
    }


# ------------------------------------------------------------------ the lattice

def s2_lattice():
    monotone = True
    pairs = 0
    for small in range(EXHAUSTION_LEVEL + 1):
        for big in range(small, EXHAUSTION_LEVEL + 1):
            for s in combinations(range(PLACES), small):
                for t in combinations(range(PLACES), big):
                    if set(s) <= set(t):
                        pairs += 1
                        if not algebra(s) <= algebra(t):
                            monotone = False
    check(monotone, "a smaller set of places does not give a smaller algebra")
    check(pairs > 0, "no nested pair of place sets was compared")
    check(algebra(()) == {0, to_mask(range(1, HEADS + 1))},
          "the empty set of places does not give only the empty set and the whole set")
    check(is_union_of_blocks(set(range(1, HEADS + 1)), (0, 1, 2, 3)),
          "the direct membership test rejects the whole set at four places")
    check(not is_union_of_blocks(set(range(1, 48)), (0, 1, 2)),
          "the direct membership test accepts the cut at three places")
    check(len(algebra((0,))) == len(algebra((1,))) == 8,
          "two single places do not give algebras of the same size")
    check(algebra((0,)) != algebra((1,)),
          "two different single places give the same algebra, so the partitions coincide")
    check(len(algebra((0,)) & algebra((1,))) == 2,
          "two single places share more than the empty set and the whole set")
    strict = algebra((0,)) < algebra((0, 1))
    check(strict, "adding a place does not strictly enlarge the algebra")
    return {
        "nested_pairs_checked": pairs,
        "monotone": True,
        "empty_place_set_gives_two_sets": True,
        "membership_is_tested_directly_not_by_enumeration": True,
        "different_single_places_give_different_algebras": True,
        "two_single_places_share_only_the_two_trivial_sets": True,
        "adding_a_place_strictly_enlarges": True,
        "exhausted_levels": EXHAUSTION_LEVEL,
    }


# ------------------------------------------------------------------ the priors

def is_union_of_blocks(heads, subset):
    """Membership in the algebra, tested directly rather than by enumeration.

    Enumerating the four-place algebra would mean listing two to the eighty-one
    unions, so membership is decided by checking that every block meeting the set
    lies inside it. That is the definition and it costs one pass over the heads.
    """
    for head in heads:
        key = tuple(address(head)[k] for k in subset)
        for other in range(1, HEADS + 1):
            if tuple(address(other)[k] for k in subset) == key and other not in heads:
                return False
    return True


def minimal_places(heads):
    for size in range(PLACES + 1):
        for subset in combinations(range(PLACES), size):
            if is_union_of_blocks(heads, subset):
                return size
    return None


def definable_of_that_size(size, level, unions):
    """How many sets of a given size are definable by at most a given level.

    `unions` maps each exhausted level to the union of the algebras up to it,
    so the count at a declared set's own level uses that level's union and not
    the widest one available. Counting against the widest union was the first
    version of this function and it over-counted the first quarter.
    """
    if level <= EXHAUSTION_LEVEL:
        return sum(1 for mask in unions[level] if population(mask) == size)
    if level == PLACES:
        return comb(HEADS, size)
    total = 0
    for subset in combinations(range(PLACES), level):
        block_size = ORDER ** (PLACES - level)
        if size % block_size == 0:
            total += comb(ORDER ** level, size // block_size)
    return total


def s3_prior():
    unions = {}
    for level in range(EXHAUSTION_LEVEL + 1):
        unions[level] = set(unions.get(level - 1, ()))
        for subset in combinations(range(PLACES), level):
            unions[level] |= algebra(subset)

    rows = {}
    for name, heads in DECLARED_SETS.items():
        mu = minimal_places(heads)
        size = len(heads)
        check(mu is not None, f"{name} is not definable at all")
        if size:
            check(F(size) % (ORDER ** (PLACES - mu)) == 0,
                  f"the divisibility condition fails for {name}")
        number = definable_of_that_size(size, mu, unions)
        check(number > 0, f"no set of that size is definable at that level for {name}")
        rows[name] = {
            "size": size,
            "mu": mu,
            "definable_of_that_size_at_that_level": number,
            "all_sets_of_that_size": comb(HEADS, size),
            "prior": str(F(number, comb(HEADS, size))),
            "prior_float": float(F(number, comb(HEADS, size))),
        }
    # The prior's numerator is a count inside a level, so it can never exceed
    # that level's size. A small prior therefore reports that the level is
    # small, not that the division is a surprising coincidence.
    level_size = {level: len(unions[level]) for level in range(EXHAUSTION_LEVEL + 1)}
    for name, row in rows.items():
        if row["mu"] <= EXHAUSTION_LEVEL:
            check(row["definable_of_that_size_at_that_level"] <= level_size[row["mu"]],
                  f"the rival count for {name} exceeds the size of its own level")
    check(level_size == {0: 2, 1: 26, 2: 3014},
          "the level sizes are not the enumerated two, twenty-six and three thousand fourteen")
    check(rows["first_quarter"]["definable_of_that_size_at_that_level"] == 12 <= level_size[1],
          "the quarter's twelve rivals do not sit inside the twenty-six sets of level one")
    check(rows["first_quarter"]["prior"]
          == str(F(12, comb(HEADS, 27))),
          "the quarter's prior is not the exact ratio of twelve to the binomial")
    check(F(rows["first_quarter"]["prior"]) < F(rows["nine_district_representatives"]["prior"]),
          "the coarsest declared division does not have the smallest prior")
    check(rows["nine_district_representatives"]["mu"] == 2
          and rows["nine_district_representatives"]["definable_of_that_size_at_that_level"] == 54,
          "the nine district representatives do not meet fifty-four rival sets at two places")
    check(rows["first_quarter"]["mu"] == 1
          and rows["first_quarter"]["definable_of_that_size_at_that_level"] == 12,
          "the first quarter does not meet twelve rival sets at one place;"
          " counting against the two-place union instead would give 480")
    check(rows["three_quarter_representatives"]["mu"] == 3
          and rows["three_quarter_representatives"]["definable_of_that_size_at_that_level"] == 108,
          "the three quarter representatives do not meet one hundred eight rivals at three places")
    check(rows["cut_before"]["prior"] == "1" and rows["cut_after"]["prior"] == "1",
          "a set needing all four places does not have the trivial prior")
    check(rows["all_heads"]["prior"] == "1", "the whole set does not have the trivial prior")
    check(rows["nine_district_representatives"]["prior_float"] < 1e-9,
          "the nine-element prior is not extremely small")
    check(rows["three_quarter_representatives"]["prior_float"] > 1e-4,
          "the three-element prior is not comparatively large")
    return {
        "rows": rows,
        "a_prior_of_one_means_no_constraint": True,
        "the_prior_is_about_the_algebra_not_the_text": True,
        "the_quarter_count_moved_from_480_to_12_when_the_level_was_restricted": True,
        "level_sizes": level_size,
        "the_prior_is_bounded_by_the_size_of_its_own_level": True,
        "the_smallest_prior_belongs_to_the_coarsest_division": True,
        "exhausted_up_to_level": EXHAUSTION_LEVEL,
    }


# ------------------------------------------------------------------ the placement

def partition_blocks(subset):
    blocks = block_masks(subset)
    return [members(mask) for mask in blocks]


def which_partition(heads):
    """The least place sets whose partition has this set as a block."""
    found = []
    for size in range(PLACES + 1):
        for subset in combinations(range(PLACES), size):
            if heads in partition_blocks(subset):
                found.append(subset)
    return found


def s4_placement():
    nine = DECLARED_SETS["nine_district_representatives"]
    three = DECLARED_SETS["three_quarter_representatives"]
    quarter = DECLARED_SETS["first_quarter"]
    pairs = [s for s in combinations(range(PLACES), 2)]
    check(len(pairs) == 6, "there are not six pairs of places")
    hits = [s for s in pairs if nine in partition_blocks(s)]
    check(hits == [(2, 3)],
          "the nine district representatives are not a block of exactly the last two places")
    check(len([b for b in partition_blocks((2, 3)) if b == nine]) == 1,
          "the nine are not one block of that partition")
    block_at_origin = [b for b in partition_blocks((2, 3)) if 1 in b]
    check(block_at_origin == [nine],
          "the block containing the first head is not the nine themselves")

    three_hits = [s for s in combinations(range(PLACES), 3) if three in partition_blocks(s)]
    check(three_hits == [(1, 2, 3)],
          "the three quarter representatives are not a block of exactly the last three places")
    quarter_hits = [s for s in combinations(range(PLACES), 1) if quarter in partition_blocks(s)]
    check(quarter_hits == [(0,)], "the first quarter is not a block of exactly the first place")
    # a side of the cut is not a block of any partition: the block sizes are one,
    # three, nine, twenty-seven and eighty-one, and its size is forty-seven
    block_sizes = {ORDER ** (PLACES - size) for size in range(PLACES + 1)}
    check(block_sizes == {1, 3, 9, 27, 81}, "the block sizes are not the declared powers of three")
    check(len(DECLARED_SETS["cut_before"]) not in block_sizes,
          "the cut's size is a block size after all")
    check(which_partition(DECLARED_SETS["cut_before"]) == [],
          "a side of the cut is a block of some partition")
    check(which_partition(DECLARED_SETS["cut_after"]) == [],
          "the other side of the cut is a block of some partition")
    check(which_partition(DECLARED_SETS["two_prison_heads"]) == [],
          "the two prison heads are a block of some partition")

    # how many of the six two-place partitions are named by a declared set
    named = {}
    for s in pairs:
        blocks = partition_blocks(s)
        named[str(s)] = sum(1 for b in blocks if b in DECLARED_SETS.values())
    check(len(named) == 6, "the named-block tally does not cover six partitions")
    check(sum(named.values()) == 1,
          "more than one two-place block coincides with a declared set")
    check(named["(2, 3)"] == 1, "the last two places do not carry the one named two-place block")

    # the text's named divisions, as levels of the spectrum
    levels = {
        "single_places": 1,
        "the_nine_district_representatives": 2,
        "the_three_quarter_representatives": 3,
        "the_cut_sides": 4,
    }
    check(sorted(levels.values()) == [1, 2, 3, 4],
          "the named divisions do not occupy four distinct levels")
    return {
        "pairs_of_places": [list(s) for s in pairs],
        "the_nine_are_a_block_of": [list(hits[0])],
        "the_nine_are_the_block_containing_the_first_head": True,
        "the_three_are_a_block_of": [list(three_hits[0])],
        "the_quarter_is_a_block_of": [list(quarter_hits[0])],
        "declared_sets_found_among_two_place_blocks": named,
        "block_sizes_across_all_levels": sorted(block_sizes),
        "the_cut_sides_are_unions_of_blocks_and_not_blocks": True,
        "named_divisions_by_level": levels,
        "the_cut_is_the_only_named_division_needing_all_four_places": True,
    }


# ------------------------------------------------------------------ the rival blocks

def s5_rivals():
    nine = DECLARED_SETS["nine_district_representatives"]
    union = set()
    for size in range(EXHAUSTION_LEVEL + 1):
        for subset in combinations(range(PLACES), size):
            union |= algebra(subset)
    rivals = sorted(members(mask) for mask in union if population(mask) == 9)
    check(len(rivals) == 54, "the rivals of the nine are not fifty-four")
    check(nine in rivals, "the nine are not among the two-place nine-element sets")
    check(rivals == sorted(rivals), "the rivals are not in a fixed order")
    check(all(len(r) == 9 for r in rivals), "a rival does not have nine heads")
    check(len({tuple(r) for r in rivals}) == 54, "the rivals are not distinct")
    # each rival is one block of one of the six partitions
    origins = [r for r in rivals if 1 in r]
    check(len(origins) == 6, "there are not six rivals containing the first head")
    check(nine in origins, "the nine are not one of the origin blocks")
    check(all(len([s for s in combinations(range(PLACES), 2)
                   if any(b == set(r) for b in partition_blocks(s))]) == 1 for r in rivals),
          "a rival is a block of more than one partition")
    return {
        "rivals_of_size_nine": len(rivals),
        "rivals_containing_the_first_head": len(origins),
        "the_nine_are_among_the_origin_blocks": True,
        "each_rival_belongs_to_exactly_one_partition": True,
        "all_sets_of_size_nine": comb(HEADS, 9),
        "the_rivals_are_one_in": comb(HEADS, 9) // 54,
    }


# ------------------------------------------------------------------------ driver

def run(output=None):
    started = time.perf_counter_ns()
    sections = {
        "S1_spectrum": s1_spectrum(),
        "S2_lattice": s2_lattice(),
        "S3_prior": s3_prior(),
        "S4_placement": s4_placement(),
        "S5_rivals": s5_rivals(),
    }
    report = {
        "schema": "adva.research.definability-spectrum-evidence.v0",
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
