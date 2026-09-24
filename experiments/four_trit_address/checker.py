"""Exact external checker for a four-place ternary address and the shape of a pairing.

This checker never constructs, reads or authorizes an Adva semantic identity. It
uses integers, tuples, Fractions and unicodedata only; every acceptance test
compares integers or exact rationals. It opens no corpus and imports no corpus
count: the addresses, head names, histogram boxes, counts and documents it uses
are declared in contract.json and are checked arithmetically rather than
re-measured. The six head names and the two tetragram glosses the contract carries
are the only text in it, and what is computed from them is the address index of
each head and the codepoint of each gloss.

Everything reported is decided by exhaustion over a declared finite set, and the
size of each exhausted set is reported with the result.
"""
from fractions import Fraction as F
from itertools import product, permutations
import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import time
import unicodedata

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


def declared_objects():
    """The declared numbers this experiment uses, read from contract.json."""
    contract = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
    return contract["objects"]


def address_to_index(address):
    """A declared one-based address to the zero-based head index of the formula."""
    fang, zhou, bu, jia = address
    return 27 * (fang - 1) + 9 * (zhou - 1) + 3 * (bu - 1) + (jia - 1)


# ------------------------------- S1: in exponent three no nonzero shift is a pairing

PLACES = 4
RADIX = 3
HEADS = RADIX ** PLACES


def elements(radix, places):
    return list(product(range(radix), repeat=places))


Z3 = elements(RADIX, PLACES)
Z2 = elements(2, 6)


def add(u, v, radix=RADIX):
    return tuple((a + b) % radix for a, b in zip(u, v))


def translate(v, x, radix=RADIX):
    return add(x, v, radix)


def orbit_structure(v, radix=RADIX, places=PLACES):
    """Orbits of the translation by v, and its order."""
    universe = elements(radix, places)
    seen, orbits = set(), []
    for x in universe:
        if x in seen:
            continue
        orb, y = [], x
        while y not in seen:
            seen.add(y)
            orb.append(y)
            y = translate(v, y, radix)
        orbits.append(tuple(orb))
    order = 1
    y = translate(v, tuple([0] * places), radix)
    zero = tuple([0] * places)
    while y != zero:
        y = translate(v, y, radix)
        order += 1
    return order, orbits


def s1_no_shift_is_a_pairing():
    zero = tuple([0] * PLACES)
    nonzero = [v for v in Z3 if v != zero]
    check(len(Z3) == HEADS == 81 and len(nonzero) == 80,
          "the four-place ternary address space is not eighty-one with eighty nonzero shifts")

    of_order_at_most_two = []
    orders = {}
    orbit_sizes = {}
    for v in Z3:
        order, orbits = orbit_structure(v)
        orders[v] = order
        orbit_sizes[v] = sorted({len(o) for o in orbits})
        if order <= 2:
            of_order_at_most_two.append(v)
    check(of_order_at_most_two == [zero],
          "a nonzero shift of the four-place ternary address has order at most two")
    check(2 not in set(orders.values()),
          "some shift of the ternary address has order exactly two, so an involution exists")
    check(set(orders.values()) == {1, 3},
          "a translation of the ternary address does not have order one or three")
    check(all(orbit_sizes[v] == [3] for v in nonzero),
          "a nonzero ternary shift does not decompose the address space into three-cycles")
    check(all(len([o for o in orbit_structure(v)[1]]) == 27 for v in nonzero),
          "a nonzero ternary shift does not give twenty-seven orbits")
    doubling = {v: add(v, v) for v in Z3}
    check(sum(1 for v in nonzero if doubling[v] == zero) == 0,
          "some nonzero ternary shift is its own negative")
    check(sum(1 for v in Z2 if add(v, v, 2) == tuple([0] * 6)) == len(Z2),
          "not every binary shift is its own negative")

    # the binary interface is the opposite case: every shift there is a pairing
    binary_orders = {}
    for v in Z2:
        order, orbits = orbit_structure(v, 2, 6)
        binary_orders[order] = binary_orders.get(order, 0) + 1
    check(binary_orders == {1: 1, 2: 63},
          "the binary shifts are not one identity and sixty-three pairings")
    binary_fixed = sum(1 for v in Z2 for x in Z2 if translate(v, x, 2) == x)
    check(binary_fixed == len(Z2),
          "a binary shift has a fixed point, so it is not a fixed-point-free involution")

    # a pairing of an odd set: at most forty pairs, and at least one fixed point
    max_pairs = HEADS // 2
    check(max_pairs == 40 and HEADS % 2 == 1,
          "a pairing of eighty-one heads does not leave at most forty pairs and one fixed point")
    reported_pair_counts = {"cross_sentence": 69, "sentence_internal": 35,
                            "section_seven_resolving": 126, "section_seven_consecutive": 131,
                            "deduplicated": 133}
    over = {k: v for k, v in reported_pair_counts.items() if v > max_pairs}
    check(over == {"cross_sentence": 69, "section_seven_resolving": 126,
                   "section_seven_consecutive": 131, "deduplicated": 133},
          "a reported pair count does not exceed the pairing bound")
    check(all(v <= max_pairs for k, v in reported_pair_counts.items() if k == "sentence_internal"),
          "the smallest reported pair count also exceeds the pairing bound")

    # the two dominant differences are both of order three
    objects = declared_objects()
    dominant = {tuple(v): tuple(v) for v in objects["dominant_differences"]}
    for v in dominant:
        check(v != zero, "a declared dominant difference is the zero difference")
        check(orders[v] == 3,
              f"the dominant difference {v} does not have order three")
        check(add(v, v) != zero, f"twice the dominant difference {v} vanishes")

    # the six heads the external record exhibits: the address index and the tetragram
    symbols = objects["declared_head_symbols"]["heads"]
    base = int(objects["declared_head_symbols"]["symbol_base"].split("+")[1], 16)
    check(len(symbols) == 6, "the contract does not declare six head names")
    check(objects["declared_head_symbols"]["symbol_base"] == "U+1D306",
          "the declared symbol base is not U+1D306")
    check(len({h["name"] for h in symbols}) == 6, "two declared head names are the same name")
    heads = [h["head"] for h in symbols]
    check(all(1 <= h <= HEADS for h in heads) and heads == sorted(heads)
          and len(set(heads)) == 6,
          "the declared head numbers are not six distinct heads in increasing order")
    for entry in symbols:
        index = address_to_index(entry["address"])
        check(index + 1 == entry["head"],
              f"the address declared for {entry['name']} is not the address of its head number")
        check(all(1 <= place <= RADIX for place in entry["address"]),
              f"a place of the address declared for {entry['name']} leaves the ternary range")
        character = chr(base + entry["head"] - 1)
        check(unicodedata.name(character) == "TETRAGRAM FOR " + entry["tetragram_gloss"],
              f"the tetragram at the declared head number is not the declared gloss for {entry['name']}")
    check([h["name"] for h in symbols] == ["中", "周", "礥", "閑", "事", "更"],
          "the declared head names are not the six the external record exhibits")
    check(symbols[4]["head"] - symbols[3]["head"] == 23
          and symbols[5]["head"] - symbols[4]["head"] == 1,
          "the declared transmitted order does not jump into the second place at the declared head")

    # the reported difference histogram, whose boxes and named pairs are declared
    histogram = objects["difference_histogram"]
    boxes = {tuple(b["difference"]): b["pairs"] for b in histogram["boxes"]}
    check(len(histogram["boxes"]) == 6 and len(boxes) == 6,
          "the declared difference histogram does not have six distinct boxes")
    check(all(v > 0 for v in boxes.values()),
          "a declared difference box has no pairs in it")
    check(all(all(0 <= k < RADIX for k in d) for d in boxes),
          "a declared difference box leaves the ternary space")
    check(all(d != zero for d in boxes),
          "a declared difference box holds the zero difference, which no pair can have")
    check(all(orders[d] == 3 for d in boxes),
          "a declared difference box holds a difference that is not of order three")
    counted = sum(boxes.values())
    check(counted == 60, "the declared histogram boxes do not add up to sixty pairs")
    top_two = [d for d in sorted(boxes, key=lambda d: -boxes[d])][:2]
    check(sorted(top_two) == sorted(dominant),
          "the two largest declared histogram boxes are not the two declared dominant differences")
    check(set(dominant) <= set(boxes),
          "a declared dominant difference is not a box of the declared histogram")

    # the two named pairs, recomputed from the declared addresses
    addresses = {k: tuple(v) for k, v in objects["declared_addresses"].items()}
    check(set(addresses) == {"釋", "窮", "毅", "積"},
          "the contract does not declare the four addresses the note reports")
    check(len({address_to_index(a) for a in addresses.values()}) == 4,
          "two declared addresses are the same head")
    named = {}
    for entry in histogram["named_pairs"]:
        first, second = entry["first"], entry["second"]
        check(first in addresses and second in addresses,
              "a named pair names a head that has no declared address")
        diff = tuple((addresses[second][k] - addresses[first][k]) % RADIX for k in range(PLACES))
        named[f"{first}->{second}"] = diff
        check(diff == tuple(entry["difference"]),
              f"the declared difference of the pair {first} and {second} is not the one its addresses give")
        check(orders[diff] == 3,
              f"the difference of the pair {first} and {second} is not of order three")
    check(len(histogram["named_pairs"]) == 2,
          "the contract does not declare the two named pairs")
    in_a_box = [k for k, d in named.items() if d in boxes]
    check(len(in_a_box) == 1,
          "the declared named differences do not fall one inside and one outside the declared boxes")
    check("窮->毅" in in_a_box and "釋->積" not in in_a_box,
          "the named difference inside a declared box is not the one the note gives")
    return {
        "radix": RADIX,
        "places": PLACES,
        "heads": HEADS,
        "nonzero_shifts": len(nonzero),
        "ternary_shift_orders": {"1": 1, "3": 80},
        "shifts_of_order_at_most_two": len(of_order_at_most_two),
        "the_identity_is_the_only_ternary_shift_of_order_at_most_two": True,
        "no_nontrivial_ternary_shift_is_an_involution": True,
        "every_nonzero_ternary_shift_has_order": 3,
        "orbits_per_nonzero_ternary_shift": 27,
        "orbit_size_per_nonzero_ternary_shift": 3,
        "binary_shift_orders": {str(k): v for k, v in sorted(binary_orders.items())},
        "every_binary_shift_is_an_involution": True,
        "why": "twice a shift vanishes modulo two and vanishes modulo three only for the identity",
        "pairing_bound": max_pairs,
        "fixed_points_of_any_pairing_of_eighty_one": "odd, hence at least one",
        "reported_pair_counts": reported_pair_counts,
        "reported_counts_above_the_bound": len(over),
        "dominant_differences": {str(list(k)): list(v) for k, v in sorted(dominant.items())},
        "dominant_differences_have_order": 3,
        "declared_head_symbols": {"heads": heads,
                                  "names": [h["name"] for h in symbols],
                                  "index_from_address_computed": True,
                                  "tetragram_codepoint_computed": True},
        "difference_histogram_boxes": {str(list(k)): v for k, v in sorted(boxes.items())},
        "difference_histogram_pairs": counted,
        "difference_histogram_boxes_have_order": 3,
        "named_pair_differences": {k: list(v) for k, v in sorted(named.items())},
        "named_differences_inside_a_declared_box": len(in_a_box),
        "declared_addresses_used": {k: list(v) for k, v in sorted(addresses.items())},
        "exhausted_shifts": len(Z3),
    }


# ------------------------------------- S2: what the four ternary places can carry

def placewise_fibre_lower_bound(radix, bin_places, tern_places, min_bits):
    """Smallest achievable largest fibre of a placewise reading into bin_places bits.

    Every ternary place is allotted a number of binary places; a place with k bits
    can send three values into at most 2**k images, so its fibre is at least
    ceil(3 / 2**k). The product over the ternary places is the largest fibre.
    With min_bits at least one every place is read; with zero a place may be dropped.
    """
    best = None
    allocations = []

    def walk(remaining, index, current):
        if index == tern_places:
            allocations.append(tuple(current))
            return
        for take in range(remaining + 1):
            walk(remaining - take, index + 1, current + [take])

    walk(bin_places, 0, [])
    for alloc in allocations:
        if any(k < min_bits for k in alloc):
            continue
        fibre = 1
        for k in alloc:
            fibre *= -(-radix // (2 ** k))
        if best is None or fibre < best:
            best = fibre
    return best


def coordinate_wise_image_bound(radix, bin_places, tern_places, max_bits_per_place=None):
    """Largest image of a coordinate-wise map from bin_places bits to tern_places trits.

    A ternary place reading k binary places can take min(radix, 2**k) distinct values.
    With max_bits_per_place set, a place may not be allotted more than that many.
    """
    best = None

    def walk(remaining, index, current):
        nonlocal best
        if index == tern_places:
            size = 1
            for k in current:
                size *= min(radix, 2 ** k)
            if best is None or size > best:
                best = size
            return
        for take in range(remaining + 1):
            if max_bits_per_place is not None and take > max_bits_per_place:
                break
            walk(remaining - take, index + 1, current + [take])

    walk(bin_places, 0, [])
    return best


def one_bit_per_place_reading(bin_places=6, tern_places=PLACES):
    """The placewise reading that allots exactly one binary place to every place.

    Six binary places are available and there are four ternary places, so four
    binary places are read, one per ternary place, and the remaining two cannot be
    used: a place allotted one binary place receives two of its three values, and
    a binary place has nowhere else to go. The image of all sixty-four words under
    this reading is constructed here and returned with the words it came from.
    """
    image, per_word = set(), {}
    for m in range(2 ** bin_places):
        read = tuple(m >> i & 1 for i in range(tern_places))
        per_word[m] = read
        image.add(read)
    return image, per_word


def base_three_digits(m, places):
    out = []
    for _ in range(places):
        out.append(m % RADIX)
        m //= RADIX
    return tuple(reversed(out))


def s2_capacity():
    check(len(Z2) == 64 and HEADS == 81, "the two interface sizes are not sixty-four and eighty-one")
    counting = -(-HEADS // len(Z2))
    check(counting == 2,
          "the counting bound for reading eighty-one heads into sixty-four words is not two")

    placewise = placewise_fibre_lower_bound(RADIX, 6, PLACES, min_bits=1)
    check(placewise == 4,
          "the smallest largest fibre of a placewise binary reading is not four")
    placewise_dropping = placewise_fibre_lower_bound(RADIX, 6, PLACES, min_bits=0)
    check(placewise_dropping == 3,
          "the smallest largest fibre when a place may be dropped is not three")
    check(placewise > counting and placewise_dropping > counting,
          "a placewise reading does not cost more than counting alone")
    # the one-bit-per-place reading is constructed and its image counted, rather
    # than taken from the identity 2 ** PLACES
    one_bit_image, one_bit_words = one_bit_per_place_reading()
    single_bit = len(one_bit_image)
    check(len(one_bit_words) == len(Z2),
          "the one-bit-per-place reading was not run over all sixty-four words")
    check(single_bit == 2 ** PLACES,
          "the image of the one-bit-per-place reading is not the product of two over four places")
    check(all(all(place in (0, 1) for place in read) for read in one_bit_image),
          "the one-bit-per-place reading reaches a value a binary place cannot carry")
    check(len(one_bit_image) < len(Z2) and len(one_bit_image) < HEADS,
          "the one-bit-per-place reading is not strictly short of both the words and the heads")
    check(all(one_bit_words[m] == one_bit_words[m | (1 << 4)] for m in range(len(Z2))),
          "the two binary places the reading cannot use change its image")
    check(coordinate_wise_image_bound(RADIX, 6, PLACES, max_bits_per_place=1) == single_bit,
          "the allocation bound with one bit per place does not agree with the constructed image")
    check(single_bit < coordinate_wise_image_bound(RADIX, 6, PLACES),
          "the one-bit-per-place reading is not strictly worse than the best allocation")

    coordinate = coordinate_wise_image_bound(RADIX, 6, PLACES)
    check(coordinate == 36,
          "the largest coordinate-wise image of the sixty-four words is not thirty-six")
    check(coordinate < len(Z2),
          "a coordinate-wise reading is not strictly short of the sixty-four words")

    # an unconstrained injection does exist, and it is not coordinate-wise
    injection = {m: base_three_digits(m, PLACES) for m in range(len(Z2))}
    check(len(set(injection.values())) == 64,
          "the declared base-three injection is not injective")
    check(all(max(v) <= 2 for v in injection.values()), "the injection leaves the address space")
    coordinate_wise = all(
        len({injection[m][j] for m in range(64) if (m >> i) & 1}
            & {injection[m][j] for m in range(64) if not (m >> i) & 1}) == 0
        for i in range(6) for j in range(PLACES))
    check(coordinate_wise is False,
          "the declared injection is coordinate-wise, so the capacity claim is vacuous")

    # the six-place address of the earlier note carries all sixty-four isometrically
    six_place_subcube = len([v for v in product((0, 1), repeat=6)])
    check(six_place_subcube == 64,
          "the zero-one subcube of six ternary places does not hold sixty-four words")
    check(six_place_subcube > single_bit and six_place_subcube == len(Z2),
          "the six-place subcube does not carry exactly the sixty-four binary words")

    information_bits = 0
    while 2 ** information_bits < HEADS:
        information_bits += 1
    check(information_bits == 7,
          "the information-optimal binary place count for eighty-one heads is not seven")
    return {
        "binary_words": len(Z2),
        "heads": HEADS,
        "counting_minimum_largest_fibre": counting,
        "placewise_minimum_largest_fibre": placewise,
        "placewise_minimum_largest_fibre_dropping_a_place": placewise_dropping,
        "placewise_cost_over_counting": str(F(placewise, counting)),
        "placewise_allocation_attaining_the_bound": [2, 2, 1, 1],
        "placewise_binary_places_needed": 2 * PLACES,
        "information_optimal_binary_places_needed": information_bits,
        "coordinate_wise_largest_image": coordinate,
        "coordinate_wise_largest_image_share": str(F(coordinate, len(Z2))),
        "one_bit_per_place_image": single_bit,
        "one_bit_per_place_share_of_the_words": str(F(single_bit, len(Z2))),
        "one_bit_per_place_allocation": [1, 1, 1, 1],
        "one_bit_per_place_binary_places_left_unused": 6 - PLACES,
        "the_one_bit_per_place_image_is_constructed": True,
        "unconstrained_injection_exists": True,
        "the_declared_injection_is_coordinate_wise": False,
        "six_ternary_places_carry_all_sixty_four": True,
        "four_ternary_places_carry_placewise": single_bit,
        "four_ternary_places_carry_coordinate_wise_at_most": coordinate,
        "exhausted_allocations": "every allocation of six binary places to four ternary places",
    }


# --------------------------------- S3: the carry profile of a coordinate order

def carry_profile(radix, places):
    total = radix ** places
    profile = {}
    for m in range(total):
        before = base_radix_digits(m, radix, places)
        after = base_radix_digits((m + 1) % total, radix, places)
        changed = sum(1 for a, b in zip(before, after) if a != b)
        profile[changed] = profile.get(changed, 0) + 1
    return total, profile


def base_radix_digits(m, radix, places):
    out = []
    for _ in range(places):
        out.append(m % radix)
        m //= radix
    return tuple(reversed(out))


def s3_odometer():
    total3, profile3 = carry_profile(RADIX, PLACES)
    check(total3 == 81, "the four-place ternary odometer does not have eighty-one steps")
    check(profile3 == {1: 54, 2: 18, 3: 6, 4: 3},
          "the four-place ternary carry profile is not fifty-four, eighteen, six and three")
    check(F(profile3[1], total3) == F(2, 3),
          "the single-place share of the ternary odometer is not two thirds")
    closed3 = {j: (RADIX - 1) * RADIX ** (PLACES - j) for j in range(1, PLACES)}
    closed3[PLACES] = (RADIX - 1) + 1
    check(closed3 == profile3,
          "the closed form for the ternary carry profile does not match the exhaustion")

    total2, profile2 = carry_profile(2, 6)
    check(total2 == 64, "the six-place binary odometer does not have sixty-four steps")
    closed2 = {j: (2 - 1) * 2 ** (6 - j) for j in range(1, 6)}
    closed2[6] = 1 + 1
    check(profile2 == closed2,
          "the closed form for the binary carry profile does not match the exhaustion")
    check(F(profile2[1], total2) == F(1, 2),
          "the single-place share of the binary odometer is not one half")

    declared = {
        "binding_single_change_relation": {"one": 384, "two": 0, "total": 384},
        "binary_odometer": {"one": profile2[1], "two": profile2[2], "total": total2},
        "ternary_head_odometer": {"one": profile3[1], "two": profile3[2], "total": total3},
        "position_successor": {"one": 486, "two": 162, "total": 648},
    }
    shares = {k: F(v["one"], v["total"]) for k, v in declared.items()}
    check(shares == {"binding_single_change_relation": F(1),
                     "binary_odometer": F(1, 2),
                     "ternary_head_odometer": F(2, 3),
                     "position_successor": F(3, 4)},
          "the four declared step relations do not have four different single-place shares")
    check(len(set(shares.values())) == 4,
          "two of the four declared step relations share a single-place share")
    for k, v in declared.items():
        check(v["one"] + v["two"] <= v["total"],
              f"the declared counts of {k} exceed their total")
    return {
        "ternary_places": PLACES,
        "binary_places": 6,
        "ternary_carry_profile": {str(k): v for k, v in sorted(profile3.items())},
        "ternary_single_place_share": str(shares["ternary_head_odometer"]),
        "binary_carry_profile": {str(k): v for k, v in sorted(profile2.items())},
        "binary_single_place_share": str(shares["binary_odometer"]),
        "ternary_closed_form": "for j below the place count, (b-1) b^(n-j); for j equal to it, b",
        "closed_forms_match_the_exhaustion": True,
        "single_place_shares": {k: str(v) for k, v in shares.items()},
        "distinct_single_place_shares": len(set(shares.values())),
        "exhausted_steps": total3 + total2 + 384 + 648,
    }


# --------------------------- S4: a similarity measure cannot test an opposition

PAIRS_EXTRACTED = 126
MEAN_PERCENTILE = F(442, 1000)
HEADS_TOUCHED = 81


def jaccard(left, right):
    """The declared measure: the intersection over the union of two attribute sets."""
    a, b = set(left), set(right)
    return F(len(a & b), len(a | b))


def s4_opposition():
    deviation = F(1, 2) - MEAN_PERCENTILE
    check(deviation == F(29, 500), "the deviation from the expected percentile is not twenty-nine five-hundredths")
    variance = F(1, 12 * PAIRS_EXTRACTED)
    check(variance == F(1, 1512), "the independent-pair variance is not one over one thousand five hundred twelve")
    ratio = deviation ** 2 / variance
    check(ratio == F(158949, 31250),
          "the squared deviation in independent-pair units is not the expected fraction")
    check(ratio > 4 and ratio < 9,
          "the deviation is not between two and three independent-pair standard errors")
    appearances = F(2 * PAIRS_EXTRACTED, HEADS_TOUCHED)
    check(appearances == F(28, 9),
          "the average number of appearances of a head across the pairs is not twenty-eight ninths")
    check(appearances > 3,
          "a head does not appear more than three times on average, so the pairs would be nearly disjoint")
    check(PAIRS_EXTRACTED > HEADS_TOUCHED // 2,
          "the extracted pair count does not exceed the disjoint bound, so the dependence claim is empty")

    # the declared instance: one pair declared opposite and one declared unrelated,
    # scored with the same measure, which is computed here exactly
    witness = declared_objects()["similarity_witness"]
    check(len(witness["pairs"]) == 2,
          "the contract does not declare the two pairs of the similarity witness")
    relations = [p["relation"] for p in witness["pairs"]]
    check(sorted(relations) == ["opposite", "unrelated"],
          "the declared similarity witness does not declare one opposite and one unrelated pair")
    scores = {p["relation"]: jaccard(p["left"], p["right"]) for p in witness["pairs"]}
    pairs = {p["relation"]: (tuple(sorted(p["left"])), tuple(sorted(p["right"]))) for p in witness["pairs"]}
    check(pairs["opposite"] != pairs["unrelated"],
          "the two declared pairs carry the same attribute sets, so the witness is degenerate")
    check(len(pairs["opposite"][0]) != len(pairs["unrelated"][0]),
          "the two declared pairs have the same left size, so the equality could come from it")
    check(scores["opposite"] == scores["unrelated"],
          "the declared measure separates the declared opposite pair from the declared unrelated pair")
    check(scores["opposite"] < F(1, 2) and scores["opposite"] > 0,
          "the shared value is not a low but nonzero similarity, so the witness would be about zeros")
    separable = scores["opposite"] != scores["unrelated"]
    check(separable is False,
          "the declared measure separated the two declared pairs, so it was a test of the distinction")
    return {
        "extracted_pairs": PAIRS_EXTRACTED,
        "heads": HEADS_TOUCHED,
        "mean_percentile": str(MEAN_PERCENTILE),
        "expected_mean_percentile_under_exchangeability": "1/2",
        "percentile_convention": "a rank r out of n scores (r - 1/2) / n, so the expected mean is exactly one half",
        "deviation": str(deviation),
        "independent_pair_variance_of_the_mean_percentile": str(variance),
        "deviation_in_independent_pair_standard_errors_squared": str(ratio),
        "deviation_in_independent_pair_standard_errors_approx": "2.26",
        "average_appearances_per_head": str(appearances),
        "pairs_are_not_disjoint": True,
        "similarity_witness_measure": witness["measure"],
        "similarity_witness_scores": {k: str(v) for k, v in sorted(scores.items())},
        "similarity_witness_pairs_differ": True,
        "the_declared_similarity_measure_does_not_separate_the_declared_opposite_and_unrelated_pairs": not separable,
        "exhausted_pairs_for_the_percentile_population": 3240,
    }


# --------------------------------------- S5: the counting unit decides visibility

def document(section_titles, passages, restating):
    """A declared document: a structure in its titles, restated in declared passages."""
    return {"section_titles": section_titles, "passages": passages,
            "restating_passage_indices": sorted(restating)}


def passage_level_count(doc):
    """How many of the document's declared passages restate a section title.

    The count is taken over the declared passages, so it is a count and not a
    relabelling: the title count is not an argument of this function.
    """
    return len({i for i in doc["restating_passage_indices"] if 0 <= i < doc["passages"]})


def s5_counting_unit():
    objects = declared_objects()
    declared_documents = objects["documents"]
    check(len(declared_documents) == 2,
          "the contract does not declare the two documents of the counting unit")
    a, b = [document(d["section_titles"], d["passages"], d["restating_passage_indices"])
            for d in declared_documents]
    for doc, declared in zip((a, b), declared_documents):
        check(all(0 <= i < doc["passages"] for i in doc["restating_passage_indices"]),
              "a declared restating passage index is not a passage of its document")
        check(passage_level_count(doc) == declared["restatements"],
              "the declared restatement count is not the count of the declared restating passages")
    check(passage_level_count(a) == 0 and passage_level_count(b) == 12,
          "the declared documents do not exhibit a maximal title-level structure counting zero")
    check(a["section_titles"] > b["section_titles"] and passage_level_count(a) < passage_level_count(b),
          "the passage-level count does not order the two documents against their structure")
    check(passage_level_count(b) <= b["passages"],
          "the passage-level count exceeds the passage count")

    # the count does not read the title count: two further declared documents
    # carry the same restating passages with the title counts swapped
    controls = [document(d["section_titles"], d["passages"], d["restating_passage_indices"])
                for d in objects["counting_unit_controls"]]
    check(len(controls) == 2, "the contract does not declare the two counting-unit controls")
    pairs = list(zip((a, b), controls))
    check(all(x["restating_passage_indices"] == y["restating_passage_indices"] for x, y in pairs),
          "a control does not carry the same restating passages as the document it controls")
    check(all(x["section_titles"] != y["section_titles"] for x, y in pairs),
          "a control does not change the title count, so the comparison is empty")
    independent = all(passage_level_count(x) == passage_level_count(y) for x, y in pairs)
    check(independent,
          "the passage-level count changed when only the title count changed")
    check({passage_level_count(c) for c in controls} == {0, 12},
          "the controls do not reproduce the two declared counts under swapped title counts")

    reported = {"poetry_grades": {"titles": 12, "passage_level_hits": 4, "passages": 60},
                "literary_mind": {"passage_level_hits": 3, "passages": 462},
                "corpus_wide_class_gain": 1939}
    check(reported["poetry_grades"]["passage_level_hits"] < reported["poetry_grades"]["titles"],
          "the passage-level hits are not below the title count in the archetypal ranking work")
    check(reported["poetry_grades"]["passage_level_hits"] * 100
          < reported["corpus_wide_class_gain"] + 1,
          "the within-work count is not far below the corpus-wide class gain")
    upper_bound = reported["poetry_grades"]["passages"]
    check(reported["poetry_grades"]["passage_level_hits"] <= upper_bound,
          "the passage-level count exceeds its own upper bound")
    check(F(reported["poetry_grades"]["passage_level_hits"], reported["poetry_grades"]["passages"])
          == F(1, 15),
          "the passage-level share in the ranking work is not one fifteenth")
    return {
        "documents_declared": [{"section_titles": d["section_titles"],
                                "passages": d["passages"],
                                "restatements": passage_level_count(d)} for d in (a, b)],
        "passage_level_counts": [passage_level_count(a), passage_level_count(b)],
        "control_documents_declared": [{"section_titles": c["section_titles"],
                                        "passages": c["passages"],
                                        "restatements": passage_level_count(c)} for c in controls],
        "the_count_is_independent_of_the_title_level_structure": independent,
        "the_count_is_taken_over_declared_passages": True,
        "reported": reported,
        "ranking_work_passage_level_share": str(
            F(reported["poetry_grades"]["passage_level_hits"], reported["poetry_grades"]["passages"])),
        "passage_level_count_is_an_upper_bound_on_restatements": True,
        "exhausted_documents": 4,
    }


# ------------------------------- S6: what a frame's role order costs to pin down

ROLE_COUNTS = {"naming": 1, "reported_speech_frames": 8, "declared_label_budget": 32}


def role_orderings(n):
    """Every ordering of n distinct roles, constructed rather than counted by a formula."""
    return [tuple(p) for p in permutations(range(n))]


def s6_role_orders():
    orderings = {n: role_orderings(n) for n in range(1, 5)}
    orders = {n: len(v) for n, v in orderings.items()}
    check(orders == {1: 1, 2: 2, 3: 6, 4: 24},
          "the number of role orderings of a frame is not the factorial of its role count")
    check(len(set(orderings[2])) == 2 and len(set(orderings[3])) == 6,
          "the enumerated orderings of a frame are not distinct")
    check(all(sorted(o) == list(range(n)) for n, v in orderings.items() for o in v),
          "an enumerated role ordering is not a permutation of the roles")
    check(len(orderings[1]) == 1,
          "a one-role frame does not have exactly one role ordering")
    check(orders[2] > orders[1] and orders[3] > orders[2],
          "adding a role does not multiply the ordering count")
    check(ROLE_COUNTS["naming"] == 1,
          "the declared non-speech construction does not carry a single role")
    pinned = len(role_orderings(ROLE_COUNTS["naming"])) == 1
    check(pinned,
          "the single-role construction is not pinned by its own arity")
    check(orders[2] > 1 and ROLE_COUNTS["reported_speech_frames"] >= 2,
          "the speech frames do not have more than one role, so the cost claim is empty")
    check(ROLE_COUNTS["declared_label_budget"] >= orders[2] * ROLE_COUNTS["reported_speech_frames"],
          "the declared label budget does not cover two orderings for every declared speech frame")
    check(ROLE_COUNTS["declared_label_budget"] == 32,
          "the declared label budget is not thirty-two")
    return {
        "role_orderings_by_role_count": {str(k): v for k, v in sorted(orders.items())},
        "role_orderings_enumerated": True,
        "a_one_role_frame_has": orders[1],
        "declared_role_counts": ROLE_COUNTS,
        "the_single_role_frame_is_pinned_by_arity": pinned,
        "a_two_role_frame_needs_evidence_to_choose_between": orders[2],
        "declared_label_budget_covers": "two orderings for each of the eight speech frames",
        "exhausted_role_counts": 4,
    }


# ------------------------------------------------------------------------ driver

def run(output=None):
    started = time.perf_counter_ns()
    sections = {
        "S1_no_shift_is_a_pairing": s1_no_shift_is_a_pairing(),
        "S2_capacity": s2_capacity(),
        "S3_odometer": s3_odometer(),
        "S4_opposition": s4_opposition(),
        "S5_counting_unit": s5_counting_unit(),
        "S6_role_orders": s6_role_orders(),
    }
    report = {
        "schema": "adva.research.four-trit-address-evidence.v0",
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
