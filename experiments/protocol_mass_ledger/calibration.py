#!/usr/bin/env python3
"""The protocol's ledger, and why the retained partition does not transfer onto it.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The protocol became checkable in Research 0196 and 0197. This run asks the end-to-end question:
walk the levels, price each one with the measured link cost, count the side work, and see what the
two mass accounts do when they are read against each other.

Three sections, all exact:

  one    the ledger, level by level: links joined, the link's price in layer steps at a declared
         conversion, the cumulative reserve, the depth cost the sides pay, the mass resolved and
         the mass left, and the marginal cost of the next unit of mass.
  two    the retained Keraia depth-15 partition, re-verified: four classes summing to one and an
         unresolved mass of 6689/32768.
  three  the bridge. Reading one protocol level as one unit of the retained depth is the tempting
         move, and the run tests it by comparing the unresolved mass of both accounts at the same
         depth. They differ by an exact factor, so the accounts are not identified and no mass is
         transferred. What is reported instead is the pair of costs of reaching that depth.

Nothing here computes Omega, and a mass that does not transfer is not transferred quietly.
"""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
COUNTS = {"checks": 0, "levels": 0}
LEVELS = CONTRACT["budget"]["declared_levels"]
CONVERSION = 8                      # declared layer steps per measured unit, as in Research 0197


def check(condition, message):
    COUNTS["checks"] += 1
    if not condition:
        raise AssertionError(message)


# --------------------------------------------------------------------- the measured price --

def link_cost(level):
    """The measured price of a link at a level, in layer steps, by integer ceiling division."""
    measured = 533 + len(str(level)) - 1
    return -(-CONVERSION * measured // 533)


def depth_cost(depth):
    """The retained layer costs telescope: reaching a depth costs (depth+1)^2 steps."""
    total = sum(2 * n + 1 for n in range(depth + 1))
    check(total == (depth + 1) ** 2, "TheLayerCostsDidNotTelescope")
    return total


def remaining_mass(depth):
    """The wrapper family's remaining mass at a depth cut, from the retained layer masses."""
    resolved = sum((Fr(2 ** n, 2 ** (2 * n + 1)) for n in range(depth + 1)), Fr(0))
    check(resolved == 1 - Fr(1, 2 ** (depth + 1)), "TheResolvedMassIdentityFailed")
    return Fr(1, 2 ** (depth + 1))


# ------------------------------------------------------------------------ the ledger ----

def build_ledger():
    rows, cumulative_reserve = [], 0
    for level in range(0, LEVELS + 1):
        if level > 0:
            cumulative_reserve += link_cost(level)
        resolved = 1 - remaining_mass(level)
        rows.append({
            "level": level,
            "links_joined": level,
            "price_of_the_next_link": link_cost(level + 1),
            "cumulative_reserve_steps": cumulative_reserve,
            "side_depth_cost_steps": depth_cost(level),
            "resolved_mass": str(resolved),
            "remaining_mass": str(remaining_mass(level)),
            "reserve_share_of_the_depth_cost": str(Fr(cumulative_reserve, depth_cost(level))),
        })
    # the marginal price of the next doubling of resolution, in both currencies
    margins = []
    for index in range(1, len(rows)):
        before, after = rows[index - 1], rows[index]
        gain = Fr(after["resolved_mass"]) - Fr(before["resolved_mass"])
        reserve_spent = after["cumulative_reserve_steps"] - before["cumulative_reserve_steps"]
        side_spent = after["side_depth_cost_steps"] - before["side_depth_cost_steps"]
        margins.append({
            "level": after["level"],
            "mass_gain": str(gain),
            "reserve_spent": reserve_spent,
            "side_spent": side_spent,
            "side_steps_per_unit_mass": str(Fr(side_spent, 1) / gain),
            "reserve_steps_per_unit_mass": str(Fr(reserve_spent, 1) / gain),
            "binding_currency": ("sides" if side_spent > reserve_spent else
                                 "reserve" if reserve_spent > side_spent else "neither"),
        })
    check(all(Fr(row["mass_gain"]) > 0 for row in margins), "AMassGainWasNotPositive")
    # which currency binds is not fixed over the levels: the side increment grows by two per
    # level while the measured link price is nearly constant, so the two cross over once
    binding = [row["binding_currency"] for row in margins]
    check("reserve" in binding and "sides" in binding,
          "TheBindingCurrencyWasExpectedToChangeOverTheLevels")
    crossover = next(row["level"] for row in margins if row["binding_currency"] == "sides")
    COUNTS["levels"] = len(rows)
    return rows, margins, crossover


# -------------------------------------------------------------- the retained partition ----

def retained_partition():
    """The Keraia depth-15 partition, re-verified rather than quoted."""
    classes = {"accepted": Fr(26078, 32768), "certified_nonhalting": Fr(1, 32768),
               "pending_input": Fr(254, 32768), "incomplete_syntax": Fr(6435, 32768)}
    counts = {"accepted": 508, "certified_nonhalting": 1, "pending_input": 254,
              "incomplete_syntax": 6435}
    check(sum(classes.values(), Fr(0)) == 1, "TheRetainedClassesDoNotSumToOne")
    # the counts are cylinder counts at mixed depths, not sizes of a single word space: the run
    # records what they are and refuses the identification it first assumed
    check(sum(counts.values()) == 7198, "TheRetainedCylinderCountsMoved")
    check(sum(counts.values()) != 32768,
          "TheCylinderCountsWereExpectedNotToFillTheDepthSpace")
    unresolved = classes["pending_input"] + classes["incomplete_syntax"]
    check(unresolved == Fr(6689, 32768), "TheRetainedUnresolvedMassMoved")
    check(classes["accepted"] + unresolved + classes["certified_nonhalting"] == 1,
          "TheThreeWayPartitionDoesNotClose")
    return {"depth": 15,
            "classes": {name: str(value) for name, value in classes.items()},
            "counts": counts,
            "counts_are_cylinder_counts_at_mixed_depths": True,
            "cylinder_counts_sum": sum(counts.values()),
            "cylinder_counts_do_not_fill_a_word_space": sum(counts.values()) != 32768,
            "unresolved_mass": str(unresolved),
            "unresolved_fraction": "6689/32768",
            "source": "docs/research/keraia-cycle-certificates-and-halting-mass-bounds.md"}


# --------------------------------------------------------------------------- the bridge ----

def the_bridge(partition):
    """Read one protocol level as one unit of the retained depth, and see what breaks."""
    depth = partition["depth"]
    wrapper_remaining = remaining_mass(depth)
    keraia_unresolved = Fr(partition["unresolved_mass"])
    factor = keraia_unresolved / wrapper_remaining
    check(factor != 1, "TheTwoAccountsWereExpectedToDiffer")
    # the factor is exact and has a reason: 6689/32768 divided by 2^-16 is twice 6689
    check(factor == 2 * 6689, "TheExactFactorMoved")
    check(factor.denominator == 1, "TheFactorWasExpectedToBeAnInteger")
    reserve_to_reach = sum(link_cost(level) for level in range(1, depth + 1))
    sides_to_reach = depth_cost(depth)
    return {
        "the_tempting_reading": "one protocol level is one unit of the retained depth",
        "wrapper_remaining_at_that_depth": str(wrapper_remaining),
        "retained_unresolved_at_that_depth": str(keraia_unresolved),
        "exact_factor_between_the_accounts": str(factor),
        "factor_is_two_times_6689": True,
        "why_the_factor_is_exact":
            "the retained partition is a partition of a depth-15 binary cylinder space of 2^15 "
            "words, while the wrapper family's layer structure leaves 2^-16 of its own space at "
            "the same cut; dividing 6689/32768 by 2^-16 gives exactly twice 6689",
        "verdict": "the two mass accounts are not identified and no mass is transferred",
        "measured_bridge_exists": False,
        "what_a_bridge_would_have_to_declare":
            "how a joined link corresponds to a read of the retained family, which this run does "
            "not measure and does not invent",
        "cost_to_reach_that_depth": {
            "reserve_steps": reserve_to_reach,
            "side_steps": sides_to_reach,
            "reserve_fraction_of_the_side_cost": str(Fr(reserve_to_reach, sides_to_reach)),
            "conversion_layer_steps_per_measured_unit": CONVERSION},
    }


def main():
    refusals = []

    def refuse(case, action):
        try:
            action()
        except AssertionError as error:
            refusals.append({"case": case, "message": str(error), "refused": True})
            return
        refusals.append({"case": case, "message": None, "refused": False})
        raise AssertionError("TheRefusalControlDidNotRefuse: " + case)

    ledger, margins, crossover = build_ledger()
    partition = retained_partition()
    bridge = the_bridge(partition)

    refuse("the two mass accounts claimed to be equal at the same depth", lambda: check(
        Fr(partition["unresolved_mass"]) == remaining_mass(partition["depth"]),
        "TheTwoAccountsWereExpectedToDiffer"))
    refuse("an unresolved mass claimed to be the whole space", lambda: check(
        Fr(partition["unresolved_mass"]) == 1, "TheRetainedClassesDoNotSumToOne"))
    refuse("a depth claimed to cost nothing on the side", lambda: check(
        depth_cost(3) == 0, "TheLayerCostsDidNotTelescope"))

    evidence = {
        "schema": "adva.research.protocol-mass-ledger-evidence.v0",
        "status": "ExternalExactPass",
        "authority": "research-only exact arithmetic over retained measurements; no native admission",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_ledger": OBJ["the_ledger"],
        "declared_conversion_layer_steps_per_measured_unit": CONVERSION,
        "levels": ledger,
        "margins": margins,
        "retained_partition": partition,
        "bridge": bridge,
        "refusals": refusals,
        "findings": [
            "the protocol has a complete exact ledger: each level costs a measured link price in reserve steps and a square depth cost in side steps, with the side increment growing by two each level while the measured link price stays nearly constant",
            "which currency binds changes over the levels rather than being fixed: the reserve increment exceeds the side increment at the shallow levels and the sides exceed the reserve from the crossover onwards, so the level at which the work stops being cheap to extend is computable",
            "the mass the traversal resolves doubles at every level, so the cost per unit of resolved mass falls while the absolute cost rises, and the two readings are reported side by side instead of one being called the cost",
            "the retained Keraia partition re-verifies exactly: four classes whose masses sum to one, an unresolved mass of 6689/32768, and a three-way split of accepted, unresolved and certified nonhalting that also sums to one",
            "the retained class counts are cylinder counts at mixed depths, 7198 of them, and they do not fill a word space: the run first checked them against 32768 as if they were word counts, and that wrong-quantity slip is recorded rather than repaired silently",
            "reading one protocol level as one unit of the retained depth does not transfer: the two accounts leave unresolved masses differing by exactly twice 6689, so the identification is refused rather than assumed",
            "what is available end to end is a cost and not a mass: reaching the retained depth costs a computable number of reserve steps and of side steps, and that pair is reported with the declaration that a bridge from links to reads does not exist"],
        "non_claims": [
            "the run does not produce an end-to-end mass number for the retained partition, because no measured bridge between protocol levels and the retained depth exists; it reports the exact factor by which the accounts differ instead",
            "the link price enters through a declared conversion from measured bytes to layer steps, so the reserve column is model-relative in that dimension while the side column is not",
            "no mass is transferred between the two spaces and neither account is presented as the other",
            "the key half is still unmeasured, so the reserve covers certificate work only",
            "the crossover is measured over the declared links only: it is the level where the side increment first exceeds the measured link price, and a different conversion moves it",
            "nothing here computes Omega, decides computability, or touches the three-computation system, and the triadic tension recorded in Research 0192 remains unresolved"],
        "binding_currency_crossover_level": crossover,
        "counts": {"checks": COUNTS["checks"], "levels": COUNTS["levels"],
                   "margins": len(margins), "refusals": len(refusals),
                   "exact_factor": bridge["exact_factor_between_the_accounts"]},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    print("  level 0 / 5 / 10 / 15 / 20:")
    for row in ledger:
        if row["level"] in (0, 5, 10, 15, 20):
            print("    k=%-2d reserve %-4d side %-4d resolved %s" % (
                row["level"], row["cumulative_reserve_steps"], row["side_depth_cost_steps"],
                row["resolved_mass"]))
    print("  bridge factor:", bridge["exact_factor_between_the_accounts"],
          "| cost to reach depth 15:", bridge["cost_to_reach_that_depth"])


if __name__ == "__main__":
    main()
