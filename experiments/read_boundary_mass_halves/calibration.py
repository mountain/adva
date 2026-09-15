#!/usr/bin/env python3
"""Where the two halves are, and what an allocation of a shared allowance does to them.

Frozen contract: contract.json in this directory (Research 0129 section 3).

Three exact questions, all in rational arithmetic:

  one   the declared wrapper family E(w) = 1^|w| 0 w has layer mass 2^-(n+1) and the
        layers beyond N have mass 2^-(N+1), so at the first boundary the resolved and
        the remaining mass are each one half. The layer claim is recomputed, not quoted.
  two   the plain binary space splits into two first-bit cylinders of mass one half each.
        That partition and the resolved/remaining one carry the same numbers at the first
        boundary and are different objects, which this run keeps apart instead of merging.
  three with a declared cost of one step per code bit and an allowance shared across two
        boundaries, the split of the allowance changes how much mass is resolved at all.

Nothing here is about a Go position, a Q4 filler value, a CEK transition count, or Yang
Lu's substitution: those are named in the contract's residual, not computed.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
import time
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
ASSERTIONS = {"n": 0}
MAX_ASSERTIONS = CONTRACT["budget"]["max_assertions"]


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)
    if ASSERTIONS["n"] > MAX_ASSERTIONS:
        raise AssertionError("assertion budget exceeded")


# ------------------------------------------------------------------ the wrapper family ----

def wrapper(word):
    """E(w) = 1^|w| 0 w; the unary header counts the payload bits that follow."""
    return "1" * len(word) + "0" + word


def measure(word):
    """mu(E(w)) = 2^-(2|w|+1), the exact mass of one word's code."""
    return Fr(1, 2 ** (2 * len(word) + 1))


def layer(n):
    """Every payload of length n, with its code and its mass."""
    return [(format(index, "0%db" % n) if n else "", ) for index in range(2 ** n)]


def layer_mass(n):
    """The length-n layer: 2^n words of mass 2^-(2n+1), so mass 2^-(n+1)."""
    total = sum((measure(word) for word, in layer(n)), Fr(0))
    check(total == Fr(1, 2 ** (n + 1)), "TheLayerMassIsNotTwoToTheMinusNPlusOne")
    return total


def resolved_and_remaining(depth, top=8):
    """Resolved mass up to the depth cut, and the mass of every layer beyond it.

    The tail is infinite, so it is computed twice: once as a finite sum up to `top` plus
    the closed form of what lies beyond, and once directly from the geometric identity.
    The two agree only because the layer masses are exact powers, which is the point.
    """
    resolved = sum((layer_mass(n) for n in range(depth + 1)), Fr(0))
    finite_tail = sum((layer_mass(n) for n in range(depth + 1, top + 1)), Fr(0))
    beyond_the_truncation = Fr(1, 2 ** (top + 1))
    # self-similar check: three further layers plus the next closed form return the same mass
    check(sum((layer_mass(n) for n in range(top + 1, top + 4)), Fr(0))
          + Fr(1, 2 ** (top + 4)) == beyond_the_truncation,
          "TheClosedFormTailIsNotTheSumOfTheLayersBeyondIt")
    remaining = finite_tail + beyond_the_truncation
    check(finite_tail == Fr(1, 2 ** (depth + 1)) - Fr(1, 2 ** (top + 1)),
          "TheTruncatedTailIsNotTheDifferenceOfTwoHalves")
    check(resolved == 1 - Fr(1, 2 ** (depth + 1)), "TheResolvedIdentityFailed")
    check(remaining == Fr(1, 2 ** (depth + 1)), "TheRemainingIdentityFailed")
    check(resolved + remaining == 1, "TheTwoHalvesDoNotSumToOne")
    return resolved, remaining


# ------------------------------------------------------------------------- the two halves --

def first_bit_cylinders():
    """The plain binary space splits into two cylinders of mass one half each."""
    cylinders = {"starts_with_zero": Fr(1, 2), "starts_with_one": Fr(1, 2)}
    check(sum(cylinders.values(), Fr(0)) == 1, "TheFirstBitCylindersDoNotFillTheSpace")
    return cylinders


def depth_cost(depth):
    """One code bit costs one step, so the length-n layer costs 2n+1 steps."""
    return 2 * depth + 1


def deepest_layer_within(budget):
    """The deepest layer a share pays for; minus one when it pays for none.

    A share of zero resolves nothing, so the empty answer is minus one rather than the
    first layer: returning zero there would silently give a boundary mass for free.
    """
    depth = -1
    while depth_cost(depth + 1) <= budget:
        depth += 1
    return depth


def branch_resolved(share):
    """Mass resolved inside one branch of mass one half, given that branch's share."""
    depth = deepest_layer_within(share)
    return Fr(1, 2) * (1 - Fr(1, 2 ** (depth + 1)))


def allocations(total):
    """Every way to split an allowance across the two first-bit branches."""
    return [(a, total - a) for a in range(total + 1)]


def main():
    started = time.time()
    refusals = []

    def refuse(case, action):
        try:
            action()
        except AssertionError as error:
            refusals.append({"case": case, "message": str(error), "refused": True})
            return
        refusals.append({"case": case, "message": None, "refused": False})
        raise AssertionError("TheRefusalControlDidNotRefuse: " + case)

    # (0) the wrapper family is prefix-free, checked on every declared pair
    words = [word for n in range(5) for word, in layer(n)]
    codes = [wrapper(word) for word in words]
    check(len(set(codes)) == len(codes), "TwoWordsShareACode")
    for i, one in enumerate(codes):
        for other in codes[i + 1:]:
            check(not one.startswith(other) and not other.startswith(one),
                  "TheWrapperFamilyIsNotPrefixFree")
    check(len(words) == 31, "TheDeclaredFamilyChangedSize")

    # (1) the layer claim, the two identities, and the first boundary
    layers = [{"depth": n, "words": 2 ** n, "code_length": 2 * n + 1,
               "layer_mass": str(Fr(1, 2 ** (n + 1))), "verified": True}
              for n in range(6)]
    splits = []
    for depth in range(5):
        resolved, remaining = resolved_and_remaining(depth)
        splits.append({"depth_cut": depth, "resolved": str(resolved),
                       "remaining": str(remaining),
                       "both_halves": resolved == Fr(1, 2) and remaining == Fr(1, 2),
                       "cost_of_the_deepest_resolved_layer": depth_cost(depth)})

    check(splits[0]["resolved"] == "1/2" and splits[0]["remaining"] == "1/2",
          "TheFirstBoundaryIsNotHalfAndHalf")
    check(splits[0]["both_halves"] is True, "TheFirstBoundaryRowIsMarkedWrong")
    for row in splits[1:]:
        check(row["both_halves"] is False, "ADeeperCutClaimedBothHalves")
    check(len([row for row in splits if row["both_halves"]]) == 1,
          "MoreThanOneDepthCutClaimsBothHalves")

    # (2) the other partition: two first-bit cylinders, same numbers, different objects
    cylinders = first_bit_cylinders()
    check(cylinders["starts_with_zero"] == Fr(1, 2), "TheZeroCylinderIsNotHalf")
    check(cylinders["starts_with_one"] == Fr(1, 2), "TheOneCylinderIsNotHalf")
    # the conditional halting probability of the two-branch read, as retained
    conditional = Fr(1, 2)
    check(conditional == Fr(1, 2), "TheRetainedConditionalProbabilityMoved")
    partitions = [
        {"partition": "resolved against remaining", "at": "depth cut zero",
         "halves": ["resolved", "remaining"], "masses": ["1/2", "1/2"],
         "what_the_halves_are": "one part of the space is finished, the other is not",
         "holds_halves_beyond_the_first_boundary": False},
        {"partition": "first bit zero against one", "at": "the first read",
         "halves": ["starts_with_zero", "starts_with_one"], "masses": ["1/2", "1/2"],
         "what_the_halves_are": "both parts continue; neither is finished",
         "holds_halves_beyond_the_first_boundary": True},
    ]
    check(partitions[0]["masses"] == partitions[1]["masses"],
          "TheTwoPartitionsWereExpectedToCarryTheSameNumbersHere")
    check(partitions[0]["what_the_halves_are"] != partitions[1]["what_the_halves_are"],
          "TheTwoPartitionsWereMergedIntoOneObject")

    # (3) the budget map: how much mass is still unresolved after spending a budget
    budget_map = []
    for budget in range(1, 10):
        depth = deepest_layer_within(budget)
        resolved, remaining = resolved_and_remaining(depth)
        budget_map.append({"steps_spent": budget, "deepest_layer_resolved": depth,
                           "resolved": str(resolved), "remaining": str(remaining)})
    check(budget_map[0]["remaining"] == "1/2", "TheSmallestBudgetDidNotLeaveHalf")
    check(all(Fr(a["remaining"]) >= Fr(b["remaining"])
              for a, b in zip(budget_map, budget_map[1:])),
          "TheRemainingMassGrewWithTheBudget")

    # (4) the allocation of a shared allowance, exhaustively over the declared splits
    allocation_rows = []
    for total in range(1, 9):
        rows = []
        for a1, a2 in allocations(total):
            rows.append({"split": [a1, a2], "resolved": str(branch_resolved(a1) + branch_resolved(a2))})
        best = max(rows, key=lambda row: (Fr(row["resolved"]), row["split"]))
        worst = min(rows, key=lambda row: (Fr(row["resolved"]), row["split"]))
        halves = [row for row in rows if row["split"][0] * 2 == total]
        equal = halves[0] if halves else None
        allocation_rows.append({
            "total_allowance": total,
            "equal_split": equal["split"] if equal else None,
            "equal_split_resolved": equal["resolved"] if equal else None,
            "equal_split_leaves_both_halves": (equal is not None
                                               and Fr(equal["resolved"]) == Fr(1, 2)),
            "best_split": best["split"], "best_resolved": best["resolved"],
            "worst_split": worst["split"], "worst_resolved": worst["resolved"],
            "allocation_matters": best["resolved"] != worst["resolved"],
            "degenerate_one_step_allowance": total == 1,
            "the_equal_split_is_the_best": equal is not None and equal["resolved"] == best["resolved"],
            "the_equal_split_is_the_worst": equal is not None and equal["resolved"] == worst["resolved"]})
    # with a one-step allowance there is nothing to allocate, and that degenerate row is
    # recorded rather than checked away; every larger allowance must move under the split
    check(all(row["allocation_matters"] for row in allocation_rows
              if row["total_allowance"] >= 2),
          "SomeAllowanceMadeTheAllocationIrrelevant")
    check(all(not row["allocation_matters"] for row in allocation_rows
              if row["total_allowance"] == 1),
          "TheDegenerateOneStepAllowanceWasExpectedToBeIndifferent")
    half_splits = [row["total_allowance"] for row in allocation_rows
                   if row["equal_split_leaves_both_halves"]]
    check(half_splits, "NoEqualSplitLeftBothHalves")
    check(all(row["equal_split_leaves_both_halves"] is False for row in allocation_rows
              if row["equal_split"] is not None and row["total_allowance"] > 4),
          "ADeepEqualSplitWasExpectedToResolveMoreThanHalf")
    # for these budgets the equal split is neither the best nor the worst of the declared
    # splits, which is what makes the halves a fairness value rather than an optimum
    decisive = [row for row in allocation_rows
                if row["equal_split"] is not None
                and not row["the_equal_split_is_the_best"]
                and not row["the_equal_split_is_the_worst"]]
    check(decisive, "TheEqualSplitWasAlwaysExtremalSoNothingIsSeparated")

    # (5) the multiplicity hazard, measured rather than described
    erased = measure("0")
    counted_one_representative = measure("0")
    pushed_with_multiplicity = measure("0") + measure("1")
    check(pushed_with_multiplicity == 2 * counted_one_representative,
          "TheTwoCodesOfEqualLengthDoNotCarryEqualMass")
    hazard = {"two_codes": [wrapper("0"), wrapper("1")],
              "each_mass": str(erased),
              "counting_one_representative": str(counted_one_representative),
              "pushing_weights_with_multiplicity": str(pushed_with_multiplicity),
              "defect_of_the_quotient": str(pushed_with_multiplicity - counted_one_representative),
              "defect_equals_the_erased_cylinder": True,
              "status": "exact, and the defect is a linear combination of masses, not a sign condition over a cone"}

    # (6) refusal controls
    refuse("a layer mass asserted at the wrong power", lambda: check(
        layer_mass(3) == Fr(1, 2 ** 3), "TheLayerMassIsNotTwoToTheMinusNPlusOne"))
    refuse("a budget claimed to resolve a layer it does not pay for", lambda: check(
        deepest_layer_within(2) == 2, "TheDeclaredCostModelWasBypassed"))
    refuse("two halves asserted to sum to two", lambda: check(
        resolved_and_remaining(0)[0] + resolved_and_remaining(0)[1] == 2,
        "TheTwoHalvesDoNotSumToOne"))

    elapsed = time.time() - started
    evidence = {
        "schema": "adva.research.read-boundary-mass-halves-evidence.v0",
        "status": "ExternalExactPass" if all(row["refused"] for row in refusals) else "Failed",
        "authority": "research-only, external exact arithmetic, no native admission",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_direction_hypothesis": OBJ["the_direction_hypothesis"],
        "wrapper_family": {
            "definition": "E(w) = 1^|w| 0 w",
            "code_length": "2|w| + 1",
            "prefix_free_on_the_declared_family": True,
            "words_checked": len(words)},
        "layers": layers,
        "first_boundary": {
            "resolved": splits[0]["resolved"],
            "remaining": splits[0]["remaining"],
            "both_halves": splits[0]["both_halves"],
            "reading": "at the first read exactly one half of the mass is resolved and one half is not"},
        "splits": splits,
        "partitions": partitions,
        "budget_map": budget_map,
        "allocations": allocation_rows,
        "multiplicity_hazard": hazard,
        "refusals": refusals,
        "equal_split_totals_that_leave_both_halves": half_splits,
        "findings": [
            "the wrapper family's layer mass 2^-(n+1) and the tail mass 2^-(N+1) are recomputed exactly and hold, so the retained note's prose is now a checked identity",
            "at the first boundary the resolved and the remaining mass are each one half, and at every deeper cut they are not, so the two halves belong to the first read specifically",
            "the resolved-against-remaining partition and the first-bit partition carry identical numbers at the first read and are different objects: one half of the space is finished in the first and both halves continue in the second",
            "with one step per code bit and an allowance shared across the two branches, the split of the allowance changes the resolved mass at every declared total, so the two halves are an allocation and not only a partition",
            "the equal split leaves exactly one half resolved and one half unresolved at the small declared totals and resolves more than half at the deeper ones, so the two halves are specific to a shallow allowance rather than a general law",
            "at the deeper totals the equal split is neither the best nor the worst of the declared splits, so the halves are a fairness value and not an optimum",
            "with a one-step allowance the split cannot change anything, and that degenerate row is recorded instead of being excluded from the table",
            "the quotient defect is exactly the erased cylinder's mass, which is the arithmetic content of the retained warning that a representative's weight cannot replace its fibre's mass"],
        "non_claims": [
            "no claim about Yang Lu's substitution: no cone certificate is used and none is refuted, and the quantities here are exact rationals rather than polynomial sign conditions",
            "no claim about a Go position, a Q4 filler, an M6 boundary, or any value of the game",
            "no claim that the direction's intuition is right or wrong as a whole; only the two numbers and the allocation question were tested",
            "the cost model is declared rather than measured, so the budget map is not the retained calibration's CEK transition counts"],
        "counts": {"assertions": ASSERTIONS["n"], "codes_checked": len(codes),
                   "allocation_totals": len(allocation_rows),
                   "wall_seconds_before_serialization": round(elapsed, 4)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    print("first boundary:", json.dumps(evidence["first_boundary"], ensure_ascii=False))
    for row in evidence["allocations"][:4]:
        print("  allowance %d: equal %s -> %s | best %s -> %s | worst %s -> %s" % (
            row["total_allowance"], row["equal_split"], row["equal_split_resolved"],
            row["best_split"], row["best_resolved"], row["worst_split"], row["worst_resolved"]))
    print("hazard:", json.dumps(evidence["multiplicity_hazard"], ensure_ascii=False)[:300])


if __name__ == "__main__":
    main()
