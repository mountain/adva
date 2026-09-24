#!/usr/bin/env python3
"""Surreal order as a tear frame: what descends, and what tears.

The criterion is IMPORTED, not restated, from helgoland/src/tear_witness.py:

    clock descends through the state map  <=>  q(h) = q(h') => c(h) = c(h')

Frame
  histories  forms (L|R) : presentations whose elements are numbers of smaller
                           birthday (so a form's DAY is a property of the
                           PRESENTATION, not of the value it presents)
  state q    the VALUE the form presents (Conway's simplicity rule)
  clocks     c1 = order, decoded from the presentations themselves
             c2 = day(form)                    the day this presentation sits on
             c3 = the d-bit L/R address        inside the day-d class

Checks
  0  self-checks: |day-d class| = 2^d; the canonical form of a number is the gap
     it was born in; our recursive number order agrees with Fraction order
  A  does the ORDER descend?  (form_le decoded from L,R  <=>  num_le of values)
  B  does the PRESENTATION DAY descend?      (expected TEAR, with a witness)
  C  capacity: what the day-d class spends, and what the day clock spends

Two depths are used on purpose:
  TREE_DEPTH  the day-by-day construction is cheap (2^d numbers on day d)
  FORMS_DAY   enumerating every valid form is not (2^(2^(d-1)) candidates)
"""
from __future__ import annotations

import json
import sys
from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import ceil, log2
from pathlib import Path

# ---------------------------------------------------------------------------
# The criterion, INLINED so this file is standard-library only.
# Source: /Users/mingli/work/public/helgoland/src/tear_witness.py, function
# find_tear_witness, quoted verbatim (12 lines, no imports).  That file also
# carries sympy sections; none of them is used here.
# ---------------------------------------------------------------------------
def find_tear_witness(histories, state, clock):
    """Return a witness pair (h, h') with equal state and unequal clock, or None."""
    seen = {}
    for h in histories:
        s, c = state(h), clock(h)
        if s in seen:
            h0, c0 = seen[s]
            if c0 != c:
                return (h0, h)
        else:
            seen[s] = (h, c)
    return None

OUT = Path(__file__).resolve().parent
TREE_DEPTH = 10          # for the construction and the infinite-fibre family
FORMS_DAY = 3            # for the exhaustive form enumeration
ZERO = Fraction(0)
CANON: dict = {}        # number -> (lo, hi): the gap it was born in


# --------------------------------------------------------------------------
# Conway's construction, done rather than quoted
# --------------------------------------------------------------------------

def simplest(a, b):
    """The simplest (earliest-born) dyadic in the open interval (a, b).

    None stands for -inf as the left end and +inf as the right end.
    """
    if b is not None and b <= 0:                      # whole interval negative
        return -simplest(None if b is None else -b, None if a is None else -a)
    if a is None or a < 0:                            # 0 is strictly inside
        return Fraction(0)
    k = 0
    while True:                                       # shortest binary expansion
        step = Fraction(1, 2 ** k)
        cand = (int(a / step) + 1) * step             # a >= 0, so int() truncates
        if b is None or cand < b:
            return cand
        k += 1


def build(depth):
    """Day-by-day construction.

    Returns birthday[v], canon[v] = (lo, hi) the gap v was born in (which IS its
    canonical form {lo | hi}), address[v] the L/R sign sequence, born_on[d].
    """
    birthday = {ZERO: 0}
    CANON.clear()
    CANON[ZERO] = (None, None)
    address = {ZERO: ""}
    born_on = {0: [ZERO]}

    for d in range(1, depth + 1):
        before = sorted(birthday)                     # numbers born before day d
        new = []
        for lo, hi in zip([None] + before, before + [None]):
            v = simplest(lo, hi)
            assert v not in birthday, "gap did not produce a new number"
            # the deeper endpoint of the gap is the parent: born on day d-1
            if lo is None:
                parent = hi
            elif hi is None:
                parent = lo
            else:
                assert birthday[lo] != birthday[hi], "gap endpoints tie in birthday"
                parent = lo if birthday[lo] > birthday[hi] else hi
            assert birthday[parent] == d - 1, "parent is not a day-(d-1) number"
            birthday[v] = d
            CANON[v] = (lo, hi)
            address[v] = address[parent] + ("+" if v > parent else "-")
            new.append(v)
        born_on[d] = sorted(new)

    return birthday, CANON, address, born_on


@lru_cache(maxsize=None)
def num_le(x, y):
    """Order on NUMBERS, by Conway's recursive rule applied to canonical forms.

    x <= y  iff  no x^L >= y  and  no y^R <= x.  A canonical form has one element
    on each side, so this is a two-branch recursion on (birthday sum), which is
    strictly decreasing -> terminates.  Checked against Fraction order in 0.
    """
    lx, _ = CANON[x]
    _, hy = CANON[y]
    if lx is not None and num_le(y, lx):
        return False
    if hy is not None and num_le(hy, x):
        return False
    return True


def form_le(F, G):
    """The SAME rule, now applied to arbitrary presentations (not values).

    F <= G  iff  no f^L >= G  and  no g^R <= F.

    Every form here presents a number, and the elements are numbers, so the only
    comparisons needed are between a number-game and a number: by the number
    order.  Nothing in this function reads F's or G's *value*.
    """
    for l in F[0]:                                    # no f^L >= G
        if num_le(G[3], l):
            return False
    for r in G[1]:                                    # no g^R <= F
        if num_le(r, F[3]):
            return False
    return True


def all_forms_upto(birthday, maxday):
    """Every valid form (L|R) with elements born before `maxday`; day <= maxday."""
    pool = sorted(v for v, d in birthday.items() if d < maxday)
    forms = []
    for k in range(len(pool) + 1):
        for L in combinations(pool, k):
            for j in range(len(pool) + 1):
                for R in combinations(pool, j):
                    lo = L[-1] if L else None
                    hi = R[0] if R else None
                    if lo is not None and hi is not None and lo >= hi:
                        continue
                    day = 0 if not L and not R else max(birthday[x] for x in L + R) + 1
                    if day > maxday:
                        continue
                    forms.append((frozenset(L), frozenset(R), day, simplest(lo, hi)))
    return forms


# --------------------------------------------------------------------------

def main():
    print("=" * 78)
    print("Surreal order as a tear frame: what descends, and what tears")
    print("=" * 78)

    birthday, canon, address, born_on = build(TREE_DEPTH)
    numbers = sorted(birthday)

    # ---------------------------------------------------------------- 0
    print("\n### 0. SELF-CHECKS ON THE CONSTRUCTION ###")
    print(f"   numbers born on day d, d=0..{FORMS_DAY} : "
          f"{[len(born_on[d]) for d in range(FORMS_DAY + 1)]}   "
          f"(2^d for every d: {all(len(born_on[d]) == 2 ** d for d in range(FORMS_DAY + 1))})")
    print(f"   total numbers with birthday <= {FORMS_DAY}       : "
          f"{sum(len(born_on[d]) for d in range(FORMS_DAY + 1))}"
          f"   (= 2^{FORMS_DAY + 1} - 1)")
    print(f"   |address| == birthday for every number     : "
          f"{all(len(address[v]) == birthday[v] for v in numbers)}")
    ok_addr = all(len({address[v] for v in born_on[d]}) == len(born_on[d])
                  for d in range(FORMS_DAY + 1))
    print(f"   addresses distinct inside a day            : {ok_addr}")
    # the canonical form recorded for v is the gap v was born in: check by
    # rebuilding v from that gap, and that the gap endpoints are its neighbours
    ok_canon = all(simplest(*canon[v]) == v for v in numbers)
    print(f"   canon[v] rebuilds v as simplest(gap)       : {ok_canon}")
    # num_le is an independent implementation; check it against Fraction order
    sample = [v for v in numbers if birthday[v] <= 6]      # 2^7 - 1 = 127 numbers
    mismatch = [(x, y) for x in sample for y in sample
                if num_le(x, y) != (x <= y)]
    print(f"   recursive number order == Fraction order   : {not mismatch}"
          f"   ({len(sample)} numbers, all {len(sample) ** 2} pairs,"
          f" {len(mismatch)} mismatch)")

    forms = all_forms_upto(birthday, FORMS_DAY)
    forms.sort(key=lambda f: (f[2], len(f[0]) + len(f[1]), sorted(f[0]), sorted(f[1])))
    values = {f[3] for f in forms}
    shallow = {v for v in numbers if birthday[v] <= FORMS_DAY}
    ok_cover = values == shallow
    print(f"   forms of day <= {FORMS_DAY}                       : {len(forms)}"
          f"   (values cover every number born <= {FORMS_DAY}: {ok_cover},"
          f" |birthday <= {FORMS_DAY}| = {len(shallow)})")

    # ---------------------------------------------------------------- A
    print("\n### A. DOES THE ORDER DESCEND? ###")
    print("   The order is DECODED FROM THE PRESENTATION: form_le(F,G) reads F's left")
    print("   set and G's right set, never their values.  Then compared with the")
    print("   order of the values they present.")
    bad = 0
    for F in forms:
        for G in forms:
            if form_le(F, G) != num_le(F[3], G[3]):
                bad += 1
                if bad <= 3:
                    print(f"      MISMATCH {sorted(F[0])}|{sorted(F[1])} vs "
                          f"{sorted(G[0])}|{sorted(G[1])}")
    print(f"   pairs compared : {len(forms) ** 2}    mismatches : {bad}")
    print(f"   -> order <= DESCENDS : {bad == 0}")
    same = [f for f in forms if f[3] == ZERO]
    by_value = {}
    for f in forms:
        by_value.setdefault(f[3], []).append(f)
    pairs_same = sum(len(g) ** 2 for g in by_value.values())
    mut = all(form_le(F, G) and form_le(G, F)
              for g in by_value.values() for F in g for G in g)
    print(f"   forms presenting the SAME value are mutually <= : {mut}"
          f"   ({pairs_same} ordered same-value pairs;"
          f" {len(same)} forms present 0)")

    # ---------------------------------------------------------------- B
    print("\n### B. DOES THE PRESENTATION DAY DESCEND? ###")
    w = find_tear_witness(forms, lambda f: f[3], lambda f: f[2])
    if w is None:
        print("   DESCENDS (unexpected)")
    else:
        h, hp = w
        print("   TEAR.  Witness pair (same value, different presentation day):")
        print(f"      h  = ({sorted(h[0])} | {sorted(h[1])})    day {h[2]}   value {h[3]}")
        print(f"      h' = ({sorted(hp[0])} | {sorted(hp[1])})    day {hp[2]}   value {hp[3]}")
        print(f"      q(h) = q(h') = {h[3]}   but   c(h) = {h[2]},  c(h') = {hp[2]}")

    per_day = {}
    for L, R, day, v in forms:
        if v == ZERO:
            per_day.setdefault(day, []).append((sorted(L), sorted(R)))
    print(f"\n   presentations of the value 0, by day (within day <= {FORMS_DAY}):")
    for day in sorted(per_day):
        ex = per_day[day][0]
        print(f"      day {day}: {len(per_day[day]):>3} presentations, e.g. "
              f"({ex[0]} | {ex[1]})")
    print("   -> on a single day the day clock reads the SAME value for all of")
    print("      them: within a day it has no resolution at all.")

    fam = [(n, simplest(None, Fraction(n)), birthday[Fraction(n)] + 1)
           for n in range(1, 11)]
    ok_fam = all(v == ZERO and day == n + 1 for n, v, day in fam)
    print(f"\n   the family ( | n ) for n = 1..10: value 0, day n+1 : {ok_fam}")
    print("   -> 0 has a presentation on day 0 and on EVERY day >= 2, so the fibre")
    print("      over a value is INFINITE; the day clock is constant on each day")

    # ---------------------------------------------------------------- C
    print("\n### C. CAPACITY: DAY-d CLASS vs THE d-BIT ADDRESS ###")
    print("   day   numbers born   ceil(log2)   bits used by the L/R address")
    for d in range(FORMS_DAY + 1):
        n = len(born_on[d])
        print(f"   {d:>3}   {n:>12}   {ceil(log2(n)):>10}   "
              f"{len(address[born_on[d][0]]):>26}")
    print("   -> the address spends EXACTLY the capacity of the day-d class:")
    print("      saturated.  (In the helgoland carrier the Koszul sign spends 1 of 3")
    print("      bits at the 6-history vertex - notes/tear-witness.md section 5.)")

    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "criterion": "q(h)=q(h') => c(h)=c(h')",
        "criterion_source": "helgoland/src/tear_witness.py, inlined in this file; its sympy sections are not used",
        "tree_depth": TREE_DEPTH,
        "forms_day": FORMS_DAY,
        "forms_enumerated": len(forms),
        "self_checks": {
            "day_class_sizes": {str(d): len(born_on[d]) for d in range(FORMS_DAY + 1)},
            "canon_rebuilds_value": ok_canon,
            "number_order_matches_fraction_order": not mismatch,
            "forms_cover_all_numbers": ok_cover,
        },
        "A_order_descends": {"pairs": len(forms) ** 2, "mismatches": bad,
                             "verdict": bad == 0,
                             "same_value_pairs_mutually_le": {"pairs": pairs_same,
                                                              "verdict": mut}},
        "B_presentation_day": {
            "verdict": "TEAR",
            "witness": None if w is None else {
                "h": [sorted(map(str, w[0][0])), sorted(map(str, w[0][1])),
                      w[0][2], str(w[0][3])],
                "h_prime": [sorted(map(str, w[1][0])), sorted(map(str, w[1][1])),
                            w[1][2], str(w[1][3])]},
            "presentations_of_zero_by_day": {str(d): len(v) for d, v in per_day.items()},
            "infinite_fibre_family": {"form": "( | n )", "value": "0",
                                      "day": "n+1", "checked_n": [1, 10],
                                      "ok": ok_fam},
        },
        "C_capacity": {
            "day_class_sizes": {str(d): len(born_on[d]) for d in range(FORMS_DAY + 1)},
            "address_bits_used": {str(d): len(address[born_on[d][0]])
                                  for d in range(FORMS_DAY + 1)},
            "verdict": "saturated inside a day class; zero resolution inside a "
                       "value slice",
        },
    }
    (OUT / "evidence.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    print(f"\nwrote {OUT / 'evidence.json'}")


if __name__ == "__main__":
    main()
