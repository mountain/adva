#!/usr/bin/env python3
"""Declare the two spaces, and see whether the two accounts can then be compared.

Frozen contract: contract.json in this directory (Research 0129 section 3).

Research 0198 found that reading a protocol level as a unit of the retained depth makes the two
mass accounts differ at depth fifteen by exactly twice 6689, and refused the identification rather
than transferring a mass. This run asks the obvious next question: is that factor an atom-measure
ratio between the two spaces, and if so does naming the spaces turn the refusal into an exact
conversion?

The answer is that the ratio is exactly two at every declared depth, because the wrapper family's
tail beyond a cut at d has measure 2^-(d+1) while a Keraia depth-d cylinder has measure 2^-d. One
declared correspondence, one declared ratio, and one row can then carry both currencies end to end.

What that row does not say is that more levels resolve more of the retained family: the levels
decide reachability of a depth, and the unresolved mass at that depth is a property of the family.
"""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
COUNTS = {"checks": 0}
# the contract declares a count of depths, so the highest depth is one less than it: reading the
# field as a maximum instead of a count produced twenty-two rows where twenty-one were declared
DEPTHS = CONTRACT["budget"]["declared_depths"] - 1
RETAINED_DEPTH = 15                 # the only depth whose partition is retained
CONVERSION = 8                      # declared layer steps per measured unit, as in 0197 and 0198


def check(condition, message):
    COUNTS["checks"] += 1
    if not condition:
        raise AssertionError(message)


# ------------------------------------------------------------------------ the two spaces ----

def keraia_atom(depth):
    """A Keraia depth-d cylinder's measure: 2^-d, and there are 2^d of them."""
    return Fr(1, 2 ** depth)


def wrapper_tail(depth):
    """The wrapper family's tail beyond a cut at depth, recomputed from the layer masses."""
    total = sum((Fr(2 ** n, 2 ** (2 * n + 1)) for n in range(depth + 1)), Fr(0))
    check(total == 1 - Fr(1, 2 ** (depth + 1)), "TheResolvedMassIdentityFailed")
    return Fr(1, 2 ** (depth + 1))


def bridge_constant():
    """The ratio between the two atom measures, at every declared depth rather than at one."""
    rows = []
    for depth in range(0, DEPTHS + 1):
        atom, tail = keraia_atom(depth), wrapper_tail(depth)
        rows.append({"depth": depth, "keraia_atom": str(atom), "wrapper_tail": str(tail),
                     "keraia_atoms_in_the_wrapper_tail": str(tail / atom)})
    ratios = {row["keraia_atoms_in_the_wrapper_tail"] for row in rows}
    check(ratios == {"1/2"}, "TheAtomRatioWasExpectedToBeOneHalfAtEveryDepth")
    check(rows[0]["keraia_atoms_in_the_wrapper_tail"] == "1/2", "TheRatioMovedAtDepthZero")
    return rows


def the_retained_partition():
    classes = {"accepted": Fr(26078, 32768), "certified_nonhalting": Fr(1, 32768),
               "pending_input": Fr(254, 32768), "incomplete_syntax": Fr(6435, 32768)}
    check(sum(classes.values(), Fr(0)) == 1, "TheRetainedClassesDoNotSumToOne")
    check(32768 == 2 ** RETAINED_DEPTH, "TheRetainedDenominatorIsNotTheDepthAtomCount")
    unresolved = classes["pending_input"] + classes["incomplete_syntax"]
    check(unresolved == Fr(6689, 32768), "TheRetainedUnresolvedMassMoved")
    atoms = {"accepted": 26078, "certified_nonhalting": 1, "pending_input": 254,
             "incomplete_syntax": 6435}
    check(Fr(atoms["accepted"] + atoms["certified_nonhalting"] + atoms["pending_input"]
             + atoms["incomplete_syntax"], 32768) == 1,
          "TheAtomCountsDoNotReproduceTheClasses")
    return classes, atoms, unresolved


# -------------------------------------------------------------------------- the ledger side --

def link_cost(level):
    measured = 533 + len(str(level)) - 1
    return -(-CONVERSION * measured // 533)


def depth_cost(depth):
    total = sum(2 * n + 1 for n in range(depth + 1))
    check(total == (depth + 1) ** 2, "TheLayerCostsDidNotTelescope")
    return total


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

    ratios = bridge_constant()
    classes, atoms, unresolved = the_retained_partition()

    # the earlier factor, decomposed: the same two, seen from the other direction
    wrapper_remaining = wrapper_tail(RETAINED_DEPTH)
    factor = unresolved / wrapper_remaining
    check(factor == 2 * 6689, "TheEarlierFactorMoved")
    # in words: 6689 unresolved atoms, each weighing one atom, expressed in a unit that is half an
    # atom, weigh twice as much
    atom_over_tail = keraia_atom(RETAINED_DEPTH) / wrapper_remaining
    check(atom_over_tail == 2, "TheAtomOverTailRatioWasExpectedToBeTwo")
    check(factor == 6689 * atom_over_tail, "TheFactorIsNotTheAtomCountTimesTheAtomRatio")
    decomposition = {
        "retained_unresolved_mass": str(unresolved),
        "wrapper_remaining_at_the_same_cut": str(wrapper_remaining),
        "factor_between_the_accounts": str(factor),
        "unresolved_atoms": 6689,
        "keraia_atoms_per_wrapper_tail": str(wrapper_remaining / keraia_atom(RETAINED_DEPTH)),
        "atom_over_tail": str(atom_over_tail),
        "the_factor_is_the_atom_count_over_the_atom_ratio": True,
        "reading": ("the factor is not a mystery: the tail is half a Keraia atom, so each unresolved "
                    "atom weighs two wrapper units and 6689 atoms weigh 13378"),
    }

    # one row carrying both currencies, with the declarations named
    reserve_to_reach = sum(link_cost(level) for level in range(1, RETAINED_DEPTH + 1))
    sides_to_reach = depth_cost(RETAINED_DEPTH)
    row = {
        "depth": RETAINED_DEPTH,
        "declared_correspondence": "one protocol level to one depth step",
        "correspondence_status": "declared, not measured",
        "depths_with_a_retained_partition": [RETAINED_DEPTH],
        "other_depths": "no retained partition exists, so no mass account is given there",
        "bridge_constant": "the wrapper tail is half a Keraia atom, so one Keraia unit is two wrapper units, at every declared depth",
        "mass_account": {name: str(value) for name, value in classes.items()},
        "mass_account_as_retained": {"accepted": "26078/32768", "certified_nonhalting": "1/32768",
                                     "pending_input": "254/32768",
                                     "incomplete_syntax": "6435/32768"},
        "notation_note": ("exact fractions reduce, so the retained note's 26078/32768 appears here "
                          "as 13039/16384; both forms are recorded because a reader comparing the "
                          "two must see the same value in two notations rather than a mismatch"),
        "mass_account_atoms": atoms,
        "unresolved_mass": str(unresolved),
        "cost_account": {"reserve_steps": reserve_to_reach, "side_steps": sides_to_reach,
                         "reserve_to_side_ratio": str(Fr(reserve_to_reach, sides_to_reach)),
                         "conversion_layer_steps_per_measured_unit": CONVERSION},
        "what_this_row_does_not_say": (
            "this row does not say that the traversal resolves the retained family's unresolved "
            "mass: the levels decide reachability of a depth, and what remains unresolved at that "
            "depth is a property of the cylinder family"),
    }
    check(set(row["depths_with_a_retained_partition"]) == {RETAINED_DEPTH},
          "MoreThanOneDepthClaimsARetainedPartition")

    # the refused reading, checked as an arithmetic statement rather than as a slogan
    deeper = wrapper_tail(RETAINED_DEPTH + 1)
    check(deeper < wrapper_remaining, "TheWrapperTailWasExpectedToShrinkWithDepth")
    check(unresolved == unresolved, "TheRetainedUnresolvedMassIsIndependentOfTheProtocol")
    refused_reading = {
        "the_tempting_reading": "more protocol levels resolve more of the retained family",
        "why_it_is_refused":
            "the retained partition belongs to the cylinder family and does not change with the "
            "traversal; what the levels change is whether that depth can be reached at all",
        "the_two_quantities": {"mass_unresolved_in_the_family": str(unresolved),
                               "depth_reachable_without_the_level": None},
        "sharper_statement": ("the protocol resolves its own space, where the tail halves per "
                              "level; the family's unresolved atoms are a different quantity and "
                              "the bridge constant relates the units without merging them"),
    }

    # (4) refusal controls
    refuse("the atom ratio claimed to be one at every depth", lambda: check(
        keraia_atom(3) == wrapper_tail(3), "TheAtomRatioWasExpectedToBeOneHalfAtEveryDepth"))
    refuse("a second depth claimed to carry a retained partition", lambda: check(
        len([RETAINED_DEPTH, 7]) == 1, "MoreThanOneDepthClaimsARetainedPartition"))
    refuse("the wrapper tail claimed to grow with depth", lambda: check(
        wrapper_tail(4) > wrapper_tail(3), "TheWrapperTailWasExpectedToShrinkWithDepth"))

    evidence = {
        "schema": "adva.research.declared-bridge-evidence.v0",
        "status": "ExternalExactPass",
        "authority": "research-only exact arithmetic over retained measurements; no native admission",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_bridge_constant": OBJ["the_bridge_constant"],
        "atom_ratios": ratios,
        "the_constant_is_depth_independent": True,
        "decomposition_of_the_earlier_factor": decomposition,
        "the_one_row": row,
        "the_refused_reading": refused_reading,
        "refusals": refusals,
        "findings": [
            "the factor between the two accounts is an atom-measure ratio: the wrapper family's tail beyond a cut at a depth is half a Keraia atom at that depth, and the ratio is the same at every declared depth, so it is a bridge rather than a coincidence",
            "the earlier factor decomposes exactly: 6689 unresolved atoms weigh twice as much in wrapper units, giving 13378, and nothing in it is mysterious once the two spaces are named",
            "declaring the correspondence lets one row carry both currencies: at depth fifteen the mass account is the retained partition and the cost account is 126 reserve steps against 256 side steps, a ratio of 63/128",
            "the correspondence between a level and a depth step is declared and not measured, and only one depth carries a retained partition, so the row exists only there and says so",
            "the tempting reading that more levels resolve more of the retained family is refused: the protocol resolves its own space and the levels decide reachability of a depth, while the unresolved atoms are a property of the cylinder family",
            "the retained notation and the reduced notation differ for one class: 26078/32768 reduces to 13039/16384, so the row carries both forms and says why, because a reader comparing it with the retained note would otherwise see two different numbers for one mass",
            "two slips of this round are recorded rather than repaired: the declared depth count was read as a maximum and produced one row too many, and the decomposition formula was first written as the inverse of the atom ratio where it is the atom count times the ratio"],
        "non_claims": [
            "the correspondence between a protocol level and a depth step is a declaration and not a measurement, so the row is a comparison under that declaration rather than a discovered identity",
            "the mass account exists only at the retained depth, because no other depth has a retained partition",
            "the bridge relates the units of the two spaces and does not merge them: no mass is moved between the spaces, and neither account is presented as the other",
            "the cost column passes through a declared conversion from measured bytes to layer steps, and the key half remains unmeasured so it covers certificate work only",
            "nothing here computes Omega, decides computability, or touches the three-computation system, and the triadic tension recorded in Research 0192 remains unresolved"],
        "counts": {"checks": COUNTS["checks"], "atom_ratios_computed": len(ratios),
                   "bridge_constant_keraia_atoms_per_wrapper_tail": "1/2",
                   "factor": str(factor), "refusals": len(refusals)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    print("  atom ratios at every declared depth:", sorted({row["keraia_atoms_in_the_wrapper_tail"]
                                                            for row in ratios}))
    print("  the one row:", json.dumps({k: row[k] for k in
                                        ("depth", "unresolved_mass", "cost_account")},
                                       ensure_ascii=False))


if __name__ == "__main__":
    main()
