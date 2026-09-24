"""Exact external checker for a six-place finite interface and its two alphabets.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers and Fractions only; no floating-point value enters any acceptance
test. It imports no text: every object below is a finite combinatorial or
arithmetic object declared in contract.json, and any classical name that might be
attached to one of them stays in the residual.

Everything reported is decided by exhaustion over a declared finite set, and the
size of each exhausted set is reported with the result. One pair of figures is an
exception and is labelled as one: the declared state count of 731 and the two
declared states outside the address space are read from contract.json, because a
declared state set is not enumerated here.
"""
from fractions import Fraction as F
from itertools import product as iproduct
from math import comb, gcd
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


# ------------------------------------------------------------------ primitives

def perm(cycles, n):
    out = list(range(n))
    for cyc in cycles:
        for i, x in enumerate(cyc):
            out[x] = cyc[(i + 1) % len(cyc)]
    return tuple(out)


def compose(a, b):
    """(a after b) as position maps: x -> a[b[x]]."""
    return tuple(a[b[x]] for x in range(len(a)))


def closure(gens, n):
    identity = tuple(range(n))
    seen = {identity}
    frontier = [identity]
    while frontier:
        nxt = []
        for g in frontier:
            for s in gens:
                for h in (compose(g, s), compose(s, g)):
                    if h not in seen:
                        seen.add(h)
                        nxt.append(h)
        frontier = nxt
    return sorted(seen)


def order_of(g):
    identity = tuple(range(len(g)))
    h, k = identity, 0
    while True:
        h = compose(g, h)
        k += 1
        if h == identity:
            return k
        if k > 64:
            raise ValueError("no order")


def fixed_positions(g):
    return [x for x in range(len(g)) if g[x] == x]


# ---------------------------------------------- S1 the two pairings and the group

N_PLACES = 6
KAPPA = perm([(0, 1), (2, 3), (4, 5)], N_PLACES)
TAU = perm([(0, 3), (1, 4), (2, 5)], N_PLACES)
GROUP = closure([KAPPA, TAU], N_PLACES)
CLOCK = perm([(0, 1, 4, 5, 2, 3)], N_PLACES)   # 1-2-5-6-3-4 written on 0-based indices


def s1_pairing_group():
    identity = tuple(range(N_PLACES))
    transversal = all(KAPPA[x] != TAU[x] for x in range(N_PLACES))
    edges = set()
    for g in (KAPPA, TAU):
        for x in range(N_PLACES):
            edges.add(frozenset((x, g[x])))
    degree = {x: sum(1 for e in edges if x in e) for x in range(N_PLACES)}
    walk, y = [0], 0
    for step in range(N_PLACES):
        y = KAPPA[y] if step % 2 == 0 else TAU[y]
        walk.append(y)
    check(transversal, "the two declared matchings share an edge")
    check(len(GROUP) == 6, "the generated group does not have order six")
    check(len(edges) == 6 and set(degree.values()) == {2} and walk[-1] == 0
          and len(set(walk[:-1])) == N_PLACES,
          "the union of the two declared matchings is not a single six-cycle")
    check(all(not fixed_positions(g) for g in GROUP if g != identity),
          "the generated action is not free on the six places")
    orbit_of_first_place = {g[0] for g in GROUP}
    check(orbit_of_first_place == set(range(N_PLACES)),
          "the generated action is not transitive on the six places")
    orders = sorted(order_of(g) for g in GROUP)
    check(orders == [1, 2, 2, 2, 3, 3] and order_of(compose(TAU, KAPPA)) == 3,
          "the element orders of the pairing group are not one, three twos and two threes")
    return {
        "group_order": len(GROUP),
        "element_orders_sorted": orders,
        "action_is_free": all(not fixed_positions(g) for g in GROUP if g != identity),
        "action_is_transitive": orbit_of_first_place == set(range(N_PLACES)),
        "matchings_are_transversal": transversal,
        "union_matching_degree_every_place": sorted(set(degree.values())),
        "alternating_walk_one_based": [w + 1 for w in walk],
        "union_is_a_single_six_cycle": True,
        "six_cycle_is_an_element_of_the_group": CLOCK in set(GROUP),
        "product_of_the_two_pairings_order": order_of(compose(TAU, KAPPA)),
        "regular_action_on_six_places": len(GROUP) == N_PLACES,
    }


# ------------------------------------------------ S2 operators on the binary space

ALL = [tuple((m >> i) & 1 for i in range(N_PLACES)) for m in range(1 << N_PLACES)]
ZERO = tuple([0] * N_PLACES)
ONES = tuple([1] * N_PLACES)
UNIT = [tuple(1 if i == j else 0 for i in range(N_PLACES)) for j in range(N_PLACES)]


def to_mask(v):
    return sum(b << i for i, b in enumerate(v))


def word(v):
    return "".join(map(str, v))


def xor(u, v):
    return tuple(a ^ b for a, b in zip(u, v))


def complement(v):
    return tuple(1 - b for b in v)


def reverse(v):
    return tuple(reversed(v))


def nuclear(v):
    return (v[1], v[2], v[3], v[2], v[3], v[4])


def apply_perm(p, v):
    out = [0] * len(v)
    for x in range(len(v)):
        out[p[x]] = v[x]
    return tuple(out)


def is_linear(f):
    return all(f(xor(u, v)) == xor(f(u), f(v)) for u in ALL for v in ALL)


def s2_operators():
    ker = [v for v in ALL if nuclear(v) == ZERO]
    img = sorted({nuclear(v) for v in ALL})
    check(is_linear(nuclear), "the inner-four reading is not F2-linear")
    check(len(ker) == 4 and len(img) == 16, "the kernel or image has the wrong size")
    check(sorted(ker) == sorted([ZERO, UNIT[0], UNIT[5], xor(UNIT[0], UNIT[5])]),
          "the kernel is not spanned by the two outer places")
    commutes = {
        "inner_after_complement": all(nuclear(complement(v)) == complement(nuclear(v)) for v in ALL),
        "inner_after_reversal": all(nuclear(reverse(v)) == reverse(nuclear(v)) for v in ALL),
        "complement_after_reversal": all(complement(reverse(v)) == reverse(complement(v)) for v in ALL),
    }
    check(all(commutes.values()), "a declared commutation fails")
    invisible = all(nuclear(xor(v, e)) == nuclear(v) for v in ALL for e in (UNIT[0], UNIT[5]))
    check(invisible, "an outer place is visible to the inner reading")
    check(all(nuclear(xor(v, e)) == xor(nuclear(v), nuclear(e)) for v in ALL for e in UNIT),
          "the inner reading does not carry a single-place change to the image of that place")
    return {
        "inner_four_reading_is_f2_linear": True,
        "rank": N_PLACES - 2,
        "kernel_size": len(ker),
        "kernel_words": sorted(word(v) for v in ker),
        "kernel_places_one_based": [1, 6],
        "image_size": len(img),
        "commutations": commutes,
        "outer_places_are_invisible": invisible,
        "image_of_each_unit_place": [word(nuclear(e)) for e in UNIT],
        "pairs_checked_for_linearity": len(ALL) ** 2,
    }


# --------------------------------------- S3 the eventual image of the inner reading

def iterate(f, v, k):
    for _ in range(k):
        v = f(v)
    return v


def s3_eventual_image():
    square = lambda v: iterate(nuclear, v, 2)
    square_form = all(square(v) == (v[2], v[3], v[2], v[3], v[2], v[3]) for v in ALL)
    fourth_is_second = all(iterate(nuclear, v, 4) == square(v) for v in ALL)
    img2 = sorted({square(v) for v in ALL})
    img2_set = set(img2)
    periodic = [v for v in ALL if any(iterate(nuclear, v, k) == v for k in range(1, 9))]
    fixed = [v for v in ALL if nuclear(v) == v]
    two_cycle = [v for v in ALL if square(v) == v and nuclear(v) != v]
    hits = max(min(k for k in range(0, 9) if iterate(nuclear, v, k) in img2_set) for v in ALL)
    check(square_form, "the second iterate is not the declared inner-pair form")
    check(fourth_is_second, "the fourth iterate differs from the second")
    check(len(img2) == 4, "the eventual image does not have four elements")
    check(sorted(periodic) == img2, "a periodic state lies outside the eventual image")
    check(sorted(fixed) == sorted([ZERO, ONES]), "the fixed states are not the two constant states")
    check(len(two_cycle) == 2 and hits <= 2,
          "the non-trivial cycle is not a pair, or a state needs more than two steps")
    kernel2 = [v for v in ALL if square(v) == ZERO]
    check(len(kernel2) == 16, "the second iterate does not forget exactly four of the six places")
    clock_agrees = all(apply_perm(CLOCK, nuclear(v)) == nuclear(apply_perm(CLOCK, v)) for v in img2)
    return {
        "second_iterate_form": "(x3,x4,x3,x4,x3,x4)",
        "second_iterate_rank": 2,
        "second_iterate_kernel_size": len(kernel2),
        "fourth_iterate_equals_second": fourth_is_second,
        "eventual_image_size": len(img2),
        "eventual_image_words": [word(v) for v in img2],
        "periodic_states": [word(v) for v in periodic],
        "every_periodic_state_lies_in_the_eventual_image": sorted(periodic) == img2,
        "fixed_state_words": [word(v) for v in fixed],
        "nontrivial_two_cycle_words": sorted(word(v) for v in two_cycle),
        "max_steps_to_reach_the_eventual_image": hits,
        "clock_and_inner_reading_agree_on_the_eventual_image": clock_agrees,
        "exhausted_states": len(ALL),
    }


# ------------------------------------------------------ S4 orbit counts of the maps

def orbits_under(gens, items, act):
    seen, reps = set(), []
    for x in items:
        if x in seen:
            continue
        comp, frontier = set(), [x]
        while frontier:
            y = frontier.pop()
            if y in comp:
                continue
            comp.add(y)
            for g in gens:
                frontier.append(act(g, y))
        seen |= comp
        reps.append(tuple(sorted(comp)))
    return sorted(reps)


def s4_orbits():
    comp_orbits = orbits_under([None], ALL, lambda _, v: complement(v))
    rev_orbits = orbits_under([None], ALL, lambda _, v: reverse(v))
    group_orbits = orbits_under([g for g in GROUP], ALL, apply_perm)

    def pair_step(g, v):
        return complement(v) if g == 0 else reverse(v)

    pair_orbits = orbits_under([0, 1], ALL, pair_step)
    fixed_by_reverse = [v for v in ALL if reverse(v) == v]
    fixed_by_group = [v for v in ALL if all(apply_perm(g, v) == v for g in GROUP)]
    check(len(comp_orbits) == 32 and all(len(o) == 2 for o in comp_orbits),
          "complement is not a fixed-point-free involution on the 64 states")
    check(len(rev_orbits) == 36 and len(fixed_by_reverse) == 8,
          "reversal does not split the 64 states into 28 pairs and 8 fixed states")
    sizes = sorted(len(o) for o in pair_orbits)
    # the two involutions commute; the third non-identity element of their group is
    # the composite, whose fixed set is also non-empty, so the orbit count is 20
    check(len(pair_orbits) == 20 and sizes.count(4) == 12 and sizes.count(2) == 8,
          "the two commuting involutions do not give 12 orbits of size four and 8 of size two")
    check(len([v for v in ALL if complement(reverse(v)) == v]) == 8,
          "the composite of the two involutions does not fix eight states")
    check(len(group_orbits) == 16 and pair_orbits != group_orbits,
          "the generated group of the two pairings does not give a different partition of sixteen orbits")
    check(sorted(fixed_by_group) == sorted([ZERO, ONES]),
          "the states fixed by the whole declared group are not the two constant states")
    return {
        "complement_orbits": len(comp_orbits),
        "complement_fixed_states": 0,
        "reversal_orbits": len(rev_orbits),
        "reversal_fixed_states": len(fixed_by_reverse),
        "reversal_fixed_state_words": sorted(word(v) for v in fixed_by_reverse),
        "two_involutions_commute": all(complement(reverse(v)) == reverse(complement(v)) for v in ALL),
        "two_involutions_composite_fixed_states": len(
            [v for v in ALL if complement(reverse(v)) == v]),
        "two_involution_group_orbits": len(pair_orbits),
        "two_involution_group_orbit_size_multiset": {"2": sizes.count(2), "4": sizes.count(4)},
        "generated_group_orbits": len(group_orbits),
        "generated_group_orbit_size_multiset": {
            str(s): sum(1 for o in group_orbits if len(o) == s)
            for s in sorted({len(o) for o in group_orbits})},
        "the_two_groups_give_the_same_partition": pair_orbits == group_orbits,
        "reversal_is_an_element_of_the_pairing_group":
            tuple(reversed(range(N_PLACES))) in set(GROUP),
        "states_fixed_by_the_whole_declared_group": sorted(word(v) for v in fixed_by_group),
        "exhausted_states": len(ALL),
    }


# --------------------------------------------- S5 the ternary address interface

N_HEAD = 4
N_ZAN = 2
N_TERN = N_HEAD + N_ZAN
HEAD_COUNT = 3 ** N_HEAD
ZAN_COUNT = 3 ** N_ZAN
ADDRESS_COUNT = 3 ** N_TERN


def declared_states_outside_the_address_space():
    """The declared shortfall, read from contract.json rather than restated here.

    contract.json declares that two declared states lie outside the address space, so
    the interface is declared to carry 731 states against the 729 addresses this
    checker enumerates. This file contains no enumeration of a declared state set: it
    counts no state and measures no shortfall, and the pair "731 against 729" is
    arithmetic on a declared number and a computed one, not a count of anything found.
    Reading the declaration instead of typing it again keeps the two figures from
    drifting apart.
    """
    contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
    return contract["objects"]["declared_states_outside_the_address_space"]


def zan_digits(zero_based):
    return (zero_based % 3, zero_based // 3)


def s5_ternary_interface():
    declared_outside = declared_states_outside_the_address_space()
    check(HEAD_COUNT == 81 and ZAN_COUNT == 9 and ADDRESS_COUNT == 729,
          "the ternary address count is not 81 x 9 = 729")
    check(len({9 * h + z for h in range(HEAD_COUNT) for z in range(ZAN_COUNT)}) == 729,
          "the head and position pair is not a bijection onto 729 addresses")

    advances = boundaries = one_digit = two_digit = 0
    for h in range(HEAD_COUNT):
        for z in range(ZAN_COUNT):
            if z == ZAN_COUNT - 1:
                boundaries += 1
                continue
            advances += 1
            changed = sum(1 for a, b in zip(zan_digits(z), zan_digits(z + 1)) if a != b)
            one_digit += changed == 1
            two_digit += changed == 2
            if changed not in (1, 2):
                raise ValueError("the position successor changed no digit")
    check(advances == 648 and boundaries == 81, "the declared successor counts are wrong")
    check(one_digit == 486 and two_digit == 162,
          "the single and double digit split is not 486 and 162")

    declared, numeral = set(), set()
    for h in range(HEAD_COUNT):
        for z in range(ZAN_COUNT):
            if z < ZAN_COUNT - 1:
                declared.add((h, z, h, z + 1))
    for m in range(ADDRESS_COUNT):
        after = (m + 1) % ADDRESS_COUNT
        numeral.add((m // 9, m % 9, after // 9, after % 9))
    agree = len(declared & numeral)
    check(agree == len(declared),
          "the declared successor is not the numeral successor restricted to its domain")
    check(len(numeral - declared) == 81,
          "the numeral steps outside the declared domain are not exactly the 81 boundaries")
    return {
        "head_places": N_HEAD,
        "head_count": HEAD_COUNT,
        "position_places": N_ZAN,
        "position_count": ZAN_COUNT,
        "address_count": ADDRESS_COUNT,
        "address_bijection_checked": 729,
        "declared_successor_advances": advances,
        "declared_successor_boundaries": boundaries,
        "declared_successor_one_digit_advances": one_digit,
        "declared_successor_two_digit_advances": two_digit,
        "declared_successor_steps_carrying_into_a_head_place": 0,
        "numeral_successor_steps": len(numeral),
        "numeral_successor_steps_carrying_into_a_head_place": 81,
        "declared_and_numeral_agree_on": agree,
        "numeral_steps_outside_the_declared_domain": len(numeral - declared),
        # Declarations, not measurements. The checker enumerates the 729 addresses and
        # nothing else: the 731 declared states and the shortfall of 2 are declared
        # numbers, read at the top of this section from contract.json rather than typed
        # here. The first key keeps its retained name because
        # tests/python/test_six_place_interface.py reads it; the second is renamed so
        # that it does not read as a computed count.
        "declared_states_without_an_address": declared_outside,
        "declared_state_count_declared_in_the_contract": ADDRESS_COUNT + declared_outside,
        "declared_state_count_source":
            "declared, not computed: read from contract.json objects."
            "declared_states_outside_the_address_space = "
            f"{declared_outside}, added to the {ADDRESS_COUNT} computed addresses; this "
            "checker enumerates no declared state set and measures no shortfall",
        "exhausted_addresses": 729,
    }


# -------------------------------------------- S6 the two step relations compared

def s6_step_relations():
    directed = single = 0
    out_degree = set()
    for v in ALL:
        succ = set()
        for i in range(N_PLACES):
            w = list(v)
            w[i] ^= 1
            succ.add(tuple(w))
            directed += 1
            single += sum(1 for a, b in zip(v, w) if a != b) == 1
        out_degree.add(len(succ))
    numeral_single = sum(
        1 for m in range(1 << N_PLACES)
        if sum(1 for a, b in zip(ALL[m], ALL[(m + 1) % (1 << N_PLACES)]) if a != b) == 1)
    check(directed == 384 and single == 384 and out_degree == {6},
          "the single-change relation is not six of sixty-four, six-regular")
    check(numeral_single == 32, "the binary numeral successor is not single-place 32 times")
    return {
        "binary_states": 1 << N_PLACES,
        "binary_directed_single_change_steps": directed,
        "binary_out_degree_every_state": 6,
        "binary_steps_changing_exactly_one_place": single,
        "binary_states_with_no_successor": 0,
        "binary_numeral_successor_single_place_steps": numeral_single,
        "binary_numeral_successor_total_steps": 64,
        "ternary_addresses": ADDRESS_COUNT,
        "ternary_declared_steps": 648,
        "ternary_declared_steps_changing_one_place": 486,
        "ternary_declared_steps_changing_two_places": 162,
        "ternary_states_with_no_successor": 81,
    }


# ------------------------------------ S7 reading one interface through the other

def s7_cross_reading():
    binary_words = [[(m >> i) & 1 for i in range(N_PLACES)] for m in range(64)]
    embedded = {m: tuple(w) for m, w in enumerate(binary_words)}
    distances_preserved = all(
        sum(1 for x, y in zip(binary_words[a], binary_words[b]) if x != y) ==
        sum(1 for x, y in zip(embedded[a], embedded[b]) if x != y)
        for a in range(64) for b in range(64))
    images = set(embedded.values())
    subcube = {v for v in iproduct((0, 1), repeat=N_TERN)}
    check(distances_preserved and len(images) == 64 and images == subcube,
          "the digitwise binary word is not an isometric injection onto the 0-1 subcube")
    third = sum(1 for v in images for d in v if d == 2)
    check(third == 0, "an embedded binary word uses the third digit value")

    # a placewise binary reading of a ternary address: the fibre of a place is
    # (f0, f1) with f0 + f1 = 3, and the largest fibre is the product of the maxima
    options = [(3, 0), (2, 1), (1, 2), (0, 3)]
    best = min(
        (lambda pattern: _product(pattern))(pattern)
        for pattern in iproduct([max(p) for p in options], repeat=N_TERN))
    counting = -(-ADDRESS_COUNT // 64)
    check(best == 64 and counting == 12,
          "the placewise collapse bound or the counting bound is not 64 against 12")
    places_information = 0
    while 2 ** places_information < ADDRESS_COUNT:
        places_information += 1
    check(places_information == 10, "the information-optimal binary place count is not ten")
    check(gcd(64, ADDRESS_COUNT) == 1 and 64 * ADDRESS_COUNT == 6 ** 6,
          "the two interface sizes are not coprime with joint period six to the sixth")
    return {
        "binary_word_embeds_isometrically_onto_the_ternary_zero_one_subcube": True,
        "embedded_pairs_checked": 64 * 64,
        "third_digit_values_used_by_the_embedding": third,
        "ternary_addresses": ADDRESS_COUNT,
        "binary_words": 64,
        "placewise_reading_minimum_largest_fibre": best,
        "counting_minimum_largest_fibre": counting,
        "placewise_binary_places_needed": 2 * N_TERN,
        "information_optimal_binary_places_needed": places_information,
        "placewise_cost_in_binary_places": 2 * N_TERN - places_information,
        "gcd_of_interface_sizes": gcd(64, ADDRESS_COUNT),
        "joint_period": 64 * ADDRESS_COUNT,
        "joint_period_is_six_to_the_sixth": 64 * ADDRESS_COUNT == 6 ** 6,
    }


def _product(pattern):
    out = 1
    for f in pattern:
        out *= f
    return out


# --------------------------------------------------------- S8 the split arithmetic

def residue(x, zero_is_four):
    r = x % 4
    return 4 if (r == 0 and zero_is_four) else r


def splits(pile, zero_is_four=True):
    """Every split (left >= 1, right >= 1) and the strip it removes."""
    rows = []
    for left in range(1, pile):
        right_after = pile - left - 1
        strip = 1 + residue(left, zero_is_four) + residue(right_after, zero_is_four)
        rows.append((left, strip))
    return rows


def s8_split_arithmetic():
    conventions = {}
    for zero_is_four in (True, False):
        rows = splits(49, zero_is_four)
        table = {}
        for _, strip in rows:
            table[strip] = table.get(strip, 0) + 1
        conventions["zero_counts_as_four" if zero_is_four else "zero_counts_as_zero"] = {
            "split_count": len(rows),
            "strip_counts": {str(k): table[k] for k in sorted(table)},
        }
    check(conventions["zero_counts_as_four"]["strip_counts"] == {"5": 36, "9": 12},
          "the four-convention does not close the first strip onto five and nine alone")
    check(conventions["zero_counts_as_zero"]["strip_counts"] == {"1": 12, "5": 36},
          "the zero-convention does not admit a strip of one and drop nine")

    def uniform(pile):
        rows = splits(pile)
        return [(strip, F(1, len(rows))) for _, strip in rows]

    def independent(pile):
        rows = splits(pile)
        total = sum(comb(pile, left) for left, _ in rows)
        return [(strip, F(comb(pile, left), total)) for left, strip in rows]

    def by_residue(pile):
        rows = splits(pile)
        classes = {}
        for left, strip in rows:
            classes.setdefault(left % 4, {})
            classes[left % 4][strip] = classes[left % 4].get(strip, 0) + 1
        out = {}
        for table in classes.values():
            for strip, _ in table.items():
                out[strip] = out.get(strip, F(0)) + F(1, len(classes) * len(table))
        return sorted(out.items())

    def run(policy, start=49, steps=3):
        dist = {start: F(1)}
        for _ in range(steps):
            nxt = {}
            for pile, p in dist.items():
                for strip, q in policy(pile):
                    rest = pile - strip
                    check(rest > 0 and rest % 4 == 0,
                          "the split strip does not leave a positive multiple of four")
                    nxt[rest] = nxt.get(rest, F(0)) + p * q
            dist = nxt
        outcome = {}
        for pile, p in dist.items():
            outcome[pile // 4] = outcome.get(pile // 4, F(0)) + p
        return outcome

    policies = {
        "uniform_over_splits": uniform,
        "independent_stalk_assignment": independent,
        "uniform_over_left_pile_residue_classes": by_residue,
    }
    results = {}
    for name, policy in policies.items():
        outcome = run(policy)
        check(sum(outcome.values()) == 1, f"{name} is not a distribution")
        check(sorted(outcome) == [6, 7, 8, 9], f"{name} does not reach all four outcomes")
        results[name] = {str(k): str(outcome[k]) for k in sorted(outcome, reverse=True)}

    classical = {9: F(3, 16), 8: F(7, 16), 7: F(5, 16), 6: F(1, 16)}
    classical_text = {str(k): str(classical[k]) for k in sorted(classical, reverse=True)}
    check(results["uniform_over_left_pile_residue_classes"] == classical_text,
          "the residue-class policy does not reproduce the classical ratios")
    check(results["uniform_over_splits"] != classical_text,
          "the uniform-split policy reproduces the classical ratios, so the comparison is vacuous")
    check(results["independent_stalk_assignment"] != classical_text,
          "the independent-stalk policy reproduces the classical ratios")

    first = {}
    for name, policy in policies.items():
        table = {}
        for strip, q in policy(49):
            table[strip] = table.get(strip, F(0)) + q
        first[name] = {str(k): str(table[k]) for k in sorted(table)}

    # the two classical step parameters, separated by exact arithmetic
    first_split = 0
    for left, strip in splits(49):
        first_split += strip == 5
    halves = {}
    for pile in (44, 40, 36, 32, 28, 24):
        rows = splits(pile)
        fours = sum(1 for _, strip in rows if strip == 4)
        excess = F(fours, len(rows)) - F(1, 2)
        halves[str(pile)] = {
            "splits": len(rows),
            "strip_four": fours,
            "strip_eight": len(rows) - fours,
            "p_of_four": str(F(fours, len(rows))),
            "excess_over_one_half": str(excess),
        }
        check(excess > 0, "a reachable pile does not exceed one half at the second strip")
        check(excess == F(1, 2 * len(rows)),
              "the excess over one half is not one over twice the split count")
    check(F(first_split, len(splits(49))) == F(3, 4),
          "the first strip is not five with the classical probability three quarters")
    check(all(F(halves[str(p)]["p_of_four"]) != F(1, 2) for p in (44, 40, 36, 32, 28, 24)),
          "some reachable pile attains the classical one half at the second strip")

    differences = {
        name: {k: str(F(results[name][k]) - classical[int(k)]) for k in classical_text}
        for name in policies
    }
    return {
        "remainder_conventions": conventions,
        "classical_ratios": classical_text,
        "outcome_distributions": results,
        "first_strip_distributions": first,
        "difference_from_the_classical_ratios": differences,
        "first_strip_is_five_with_the_classical_probability": "3/4",
        "second_strip_parameter_by_reachable_pile": halves,
        "classical_second_strip_parameter": "1/2",
        "classical_second_strip_parameter_is_attained": False,
    }


# ------------------------------------------ S9 a declared encoding and its scope

FORMS = {"A": (True, False), "E": (True, True), "I": (False, False), "O": (False, True)}
FIGURES = {1: ((1, 2), (0, 1), (0, 2)), 2: ((2, 1), (0, 1), (0, 2)),
           3: ((1, 2), (1, 0), (0, 2)), 4: ((2, 1), (1, 0), (0, 2))}


def proposition_holds(form, subj, pred, mask):
    universal, negative = FORMS[form]
    for region in range(8):
        if not (mask >> region) & 1:
            continue
        has = [(region >> 2) & 1, (region >> 1) & 1, region & 1]
        s, p = has[subj], has[pred]
        if universal and not negative and s and not p:
            return False
        if universal and negative and s and p:
            return False
        if not universal and not negative and s and p:
            return True
        if not universal and negative and s and not p:
            return True
    return universal


def term_nonempty(mask, term):
    return any(((mask >> region) & 1) and ((region >> (2 - term)) & 1) for region in range(8))


def s9_declared_encoding():
    counts, witness = {}, {}
    for assumption in ("boolean", "terms-nonempty"):
        per_figure = {}
        for fig, (major, minor, conclusion) in FIGURES.items():
            valid = 0
            for f1, f2, f3 in iproduct(FORMS, repeat=3):
                failed = None
                for mask in range(1, 256):
                    if assumption == "terms-nonempty" and not all(
                            term_nonempty(mask, t) for t in (0, 1, 2)):
                        continue
                    if not proposition_holds(f1, major[0], major[1], mask):
                        continue
                    if not proposition_holds(f2, minor[0], minor[1], mask):
                        continue
                    if not proposition_holds(f3, conclusion[0], conclusion[1], mask):
                        failed = mask
                        break
                if failed is None:
                    valid += 1
                else:
                    witness.setdefault(f"figure{fig}-{f1}{f2}{f3}-{assumption}", failed)
            per_figure[fig] = valid
        counts[assumption] = per_figure
    check(counts["boolean"] == {1: 4, 2: 4, 3: 4, 4: 3},
          "the boolean reading does not give four, four, four and three")
    check(counts["terms-nonempty"] == {1: 6, 2: 6, 3: 6, 4: 6},
          "the non-empty-terms reading does not give six in every figure")
    check(sum(counts["boolean"].values()) == 15 and sum(counts["terms-nonempty"].values()) == 24,
          "the two declared scopes do not decide fifteen and twenty-four forms")
    return {
        "moods": 64, "figures": 4, "assumptions": 2, "contracts": 512,
        "occupancy_masks_exhausted": 255,
        "valid_forms_boolean": {str(k): v for k, v in counts["boolean"].items()},
        "valid_forms_terms_nonempty": {str(k): v for k, v in counts["terms-nonempty"].items()},
        "forms_gained_by_the_weaker_scope": {
            str(f): counts["terms-nonempty"][f] - counts["boolean"][f] for f in sorted(FIGURES)},
        "countermodel_examples": {k: witness[k] for k in sorted(witness)[:4]},
        "same_syntax_two_declared_scopes": True,
    }


# ------------------------------------------------------------------------ driver

def run(output=None):
    started = time.perf_counter_ns()
    sections = {
        "S1_pairing_group": s1_pairing_group(),
        "S2_operators": s2_operators(),
        "S3_eventual_image": s3_eventual_image(),
        "S4_orbits": s4_orbits(),
        "S5_ternary_address_interface": s5_ternary_interface(),
        "S6_step_relations": s6_step_relations(),
        "S7_cross_reading": s7_cross_reading(),
        "S8_split_arithmetic": s8_split_arithmetic(),
        "S9_declared_encoding": s9_declared_encoding(),
    }
    report = {
        "schema": "adva.research.six-place-interface-evidence.v0",
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
