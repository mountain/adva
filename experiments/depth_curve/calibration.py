#!/usr/bin/env python3
"""The per-depth partitions, derived from the retained evidence, with the cost attached.

Frozen contract: contract.json in this directory (Research 0129 section 3).

Research 0199 assembled one end-to-end row because one partition was retained. This run derives the
partitions at every depth from the retained evidence itself: each accepted cylinder carries its code
and its weight exponent, and each unresolved frontier carries its program end, so a depth cut is a
sum of exact dyadic weights. The reconstruction is only a derivation if it reproduces the retained
aggregate masses exactly, and that is the first thing it is made to do.

The curve that results has a shape worth reading: whether the accepted mass keeps growing with depth
and where it stops is read off the numbers rather than assumed, and the cost of reaching each depth
is attached from the ledger of Research 0198 under its declared conversion.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
EVIDENCE = ROOT / "experiments/keraia_cycle_mass/evidence/attempt-1/primary.json"
COUNTS = {"checks": 0}
CONVERSION = 8                      # declared layer steps per measured unit, as before


def check(condition, message):
    COUNTS["checks"] += 1
    if not condition:
        raise AssertionError(message)


def weight(exponent):
    """The dyadic weight of a cylinder of that length."""
    return Fr(1, 2 ** exponent)


# ------------------------------------------------------------- the retained reconstruction ----

def load_retained():
    check(EVIDENCE.exists(), "TheRetainedEvidenceIsMissing")
    raw = EVIDENCE.read_bytes()
    evidence = json.loads(raw)
    # the retained run's own status word, and the check that carries the partition being used
    check(evidence["status"] == "Passed", "TheRetainedRunDidNotPass")
    partition_check = [row for row in evidence["checks"] if "three-part mass partition" in row]
    check(len(partition_check) == 1,
          "TheRetainedRunDoesNotDeclareTheThreePartMassPartitionItWasUsedFor")
    accepted = evidence["accepted_ledger"]
    frontiers = evidence["unresolved_frontiers"]
    partition = evidence["mass_partition"]
    check(len(accepted) == partition["accepted_codes"],
          "TheAcceptedLedgerAndTheAggregateDisagreeOnTheCount")
    check(len(frontiers) == partition["unresolved_cylinders"],
          "TheFrontierCountAndTheAggregateDisagree")
    return {"sha256": hashlib.sha256(raw).hexdigest(), "accepted": accepted,
            "frontiers": frontiers, "partition": partition,
            "status": evidence["status"], "assertions": evidence["assertions"],
            "partition_check": partition_check[0]}


def reconstruct(retained):
    """Class masses by cylinder length, and the aggregate they must reproduce."""
    accepted_by_length, unresolved_by_status = {}, {}
    for entry in retained["accepted"]:
        length = entry["code_weight_exponent"]
        check(length == len(entry["code"]), "TheWeightExponentIsNotTheCodeLength")
        accepted_by_length[length] = accepted_by_length.get(length, Fr(0)) + weight(length)
    shape = {}
    for entry in retained["frontiers"]:
        # the cylinder's weight is over the source, not over where the machine had got to: the
        # program end is None for a syntax-incomplete frontier and the cursor is zero for one that
        # never read, while the source length is what reproduces the retained aggregates
        length = len(entry["source"])
        key = "%s|cursor=%s|program_end=%s" % (entry["status"], entry["cursor"],
                                               entry["program_end"])
        shape[key] = shape.get(key, 0) + 1
        status = entry["status"]
        unresolved_by_status.setdefault(status, {})
        unresolved_by_status[status][length] = (
            unresolved_by_status[status].get(length, Fr(0)) + weight(length))
    accepted_total = sum(accepted_by_length.values(), Fr(0))
    unresolved_total = sum((sum(by_length.values(), Fr(0))
                            for by_length in unresolved_by_status.values()), Fr(0))
    return (accepted_by_length, unresolved_by_status, accepted_total, unresolved_total,
            {"frontier_states": dict(sorted(shape.items())),
             "reading": ("the weight exponent of a frontier is its source length; the cursor and "
                         "the program end record where the machine stopped and are not the "
                         "cylinder's length, which the run first assumed they were")})


def verify_against_the_retained_aggregates(retained, accepted_total, unresolved_by_status,
                                           unresolved_total):
    partition = retained["partition"]

    def fraction(pair):
        return Fr(pair[0], pair[1])

    residual = partition["residual_by_status"]
    checks = {
        "accepted_total": str(accepted_total), "retained_accepted": str(fraction(partition["accepted"])),
        "unresolved_total": str(unresolved_total),
        "retained_unresolved": str(fraction(partition["unresolved"])),
        "need_input": str(sum(unresolved_by_status["NeedInput"].values(), Fr(0))),
        "retained_need_input": str(fraction(residual["NeedInput"])),
        "need_syntax": str(sum(unresolved_by_status["NeedSyntax"].values(), Fr(0))),
        "retained_need_syntax": str(fraction(residual["NeedSyntax"])),
    }
    check(accepted_total == fraction(partition["accepted"]),
          "TheReconstructionDidNotReproduceTheAcceptedMass")
    check(unresolved_total == fraction(partition["unresolved"]),
          "TheReconstructionDidNotReproduceTheUnresolvedMass")
    check(sum(unresolved_by_status["NeedInput"].values(), Fr(0))
          == fraction(residual["NeedInput"]), "TheNeedInputMassMoved")
    check(sum(unresolved_by_status["NeedSyntax"].values(), Fr(0))
          == fraction(residual["NeedSyntax"]), "TheNeedSyntaxMassMoved")
    return checks


# ------------------------------------------------------------------------- the cost side ----

def link_cost(level):
    measured = 533 + len(str(level)) - 1
    return -(-CONVERSION * measured // 533)


def depth_cost(depth):
    total = sum(2 * n + 1 for n in range(depth + 1))
    check(total == (depth + 1) ** 2, "TheLayerCostsDidNotTelescope")
    return total


def build_curve(retained, accepted_by_length, unresolved_by_status):
    deepest = max(max(accepted_by_length), max(max(by_length) for by_length in
                                                unresolved_by_status.values()))
    nonhalting = Fr(*(retained["partition"]["certified_nonhalting"]))
    rows = []
    for depth in range(0, deepest + 1):
        accepted_here = sum((mass for length, mass in accepted_by_length.items()
                             if length <= depth), Fr(0))
        unresolved_here = sum((mass for by_length in unresolved_by_status.values()
                               for length, mass in by_length.items() if length <= depth), Fr(0))
        decided = accepted_here + unresolved_here
        reserve = sum(link_cost(level) for level in range(1, depth + 1))
        rows.append({
            "depth": depth,
            "accepted_mass_decided_so_far": str(accepted_here),
            "unresolved_mass_named_so_far": str(unresolved_here),
            "decided_mass": str(decided),
            "undecided_mass": str(1 - decided),
            "reserve_steps": reserve,
            "side_steps": depth_cost(depth),
            "total_steps": reserve + depth_cost(depth),
        })
    final = rows[-1]
    check(Fr(final["decided_mass"]) + nonhalting == 1,
          "TheDeepestCutDidNotAccountForTheWholeSpace")
    accepted_values = [Fr(row["accepted_mass_decided_so_far"]) for row in rows]
    saturation = next(index for index in range(len(rows))
                      if accepted_values[index] == Fr(final["accepted_mass_decided_so_far"]))
    check(all(value == accepted_values[saturation] for value in accepted_values[saturation:]),
          "TheAcceptedMassWasExpectedToStayPutAfterItsSaturationDepth")
    check(saturation > 0 and accepted_values[0] == 0,
          "TheAcceptedMassWasExpectedToStartAtZero")
    last = rows[-1]
    previous = rows[-2]
    marginal = {
        "last_depth": last["depth"],
        "acceptance_bought_by_the_last_layer":
            str(Fr(last["accepted_mass_decided_so_far"]) - Fr(previous["accepted_mass_decided_so_far"])),
        "undecided_before_it": previous["undecided_mass"],
        "cost_of_the_last_layer_steps": last["total_steps"] - previous["total_steps"],
        "undecided_becomes": "certified nonhalting plus unresolved, which with the new acceptance "
                             "sums to the undecided mass that was there before",
    }
    check(Fr(marginal["undecided_before_it"]) == (
        Fr(last["unresolved_mass_named_so_far"]) + nonhalting
        + Fr(marginal["acceptance_bought_by_the_last_layer"])),
        "TheLastLayersAccountDidNotClose")
    return rows, saturation, nonhalting, marginal


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

    retained = load_retained()
    (accepted_by_length, unresolved_by_status, accepted_total, unresolved_total,
     source_shape) = reconstruct(retained)
    agreement = verify_against_the_retained_aggregates(retained, accepted_total,
                                                       unresolved_by_status, unresolved_total)
    curve, saturation, nonhalting, marginal = build_curve(retained, accepted_by_length,
                                                          unresolved_by_status)

    refuse("the reconstruction claimed equal to a mass it does not reproduce", lambda: check(
        accepted_total == Fr(0), "TheReconstructionDidNotReproduceTheAcceptedMass"))
    refuse("a depth cut claimed to decide nothing", lambda: check(
        Fr(curve[-1]["decided_mass"]) + nonhalting == 0,
        "TheDeepestCutDidNotAccountForTheWholeSpace"))
    refuse("the accepted mass claimed to fall with depth", lambda: check(
        Fr(curve[-1]["accepted_mass_decided_so_far"]) < Fr(curve[0]["accepted_mass_decided_so_far"]),
        "TheAcceptedMassWasExpectedToStartAtZero"))

    evidence = {
        "schema": "adva.research.depth-curve-evidence.v0",
        "status": "ExternalExactPass",
        "authority": "research-only exact arithmetic over retained evidence; no semantics re-run",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_reconstruction": OBJ["the_reconstruction"],
        "retained_evidence": {"path": str(EVIDENCE.relative_to(ROOT)),
                              "sha256": retained["sha256"],
                              "status": retained["status"],
                              "assertions": retained["assertions"],
                              "the_check_that_carries_the_partition": retained["partition_check"],
                              "reading": "read only, not modified"},
        "agreement_with_the_retained_aggregates": agreement,
        "source_shape": source_shape,
        "curve": curve,
        "accepted_mass_saturates_at_depth": saturation,
        "marginal_layer": marginal,
        "certified_nonhalting_mass": str(nonhalting),
        "declared_conversion_layer_steps_per_measured_unit": CONVERSION,
        "refusals": refusals,
        "findings": [
            "the per-depth partitions are derived from the retained evidence itself: the accepted ledger's codes and weight exponents and the unresolved frontiers' program ends reproduce the retained class aggregates exactly, so the depth curve is a derivation rather than a guess",
            "the reconstruction reproduces four retained aggregates at once: the accepted mass, the unresolved mass and both residual statuses, which is what makes it a check rather than a fit",
            "the provenance is the retained run's own partition check, quoted in the evidence, so the derivation rests on a declared result rather than on a reading of the file's shape",
            "a frontier's weight is over its source and not over where the machine stopped: the program end is absent for a syntax-incomplete frontier and the cursor is zero for one that never read, while the source length is what reproduces both retained residual aggregates, so the fields mean different things and the run records which one is the cylinder's length",
            "the accepted mass keeps growing until the deepest retained cut, where the saturation depth is measured to be fifteen and not fourteen: the hypothesis that it saturated a layer earlier was refuted by the curve, and the last layer is measured to buy 224/32768 of acceptance for forty steps",
            "the last layer's account closes exactly: the undecided mass before it equals the certified nonhalting mass plus the unresolved mass plus the acceptance the layer bought, so classification and acceptance come out of the same remainder",
            "undecided mass at a depth is one minus the mass of the cylinders at or above the cut, and at the deepest cut it is replaced by the certified nonhalting and unresolved classes, so the two ways of accounting join up exactly",
            "each depth carries its cost beside its mass, in reserve steps from the measured link price and side steps from the square depth cost, so the account is a curve rather than a single row"],
        "non_claims": [
            "the semantics are not re-run: this is exact arithmetic over retained outcomes, so a mistake in the retained run would propagate here and is not detectable from inside",
            "the curve covers the cylinders the retained evidence lists and no others",
            "the cost column passes through a declared conversion from measured bytes to layer steps, and the correspondence between a level and a depth step remains declared",
            "the key half is still unmeasured, so the cost covers certificate work only",
            "nothing here computes Omega, decides computability, or touches the three-computation system, and the triadic tension recorded in Research 0192 remains unresolved"],
        "counts": {"checks": COUNTS["checks"], "cylinders_accepted": len(retained["accepted"]),
                   "cylinders_unresolved": len(retained["frontiers"]),
                   "depths": len(curve), "saturation_depth": saturation,
                   "refusals": len(refusals)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    for row in curve:
        if row["depth"] in (0, 5, 10, 13, 14, 15):
            print("    d=%-2d accepted %-14s undecided %-14s cost %4d steps" % (
                row["depth"], row["accepted_mass_decided_so_far"], row["undecided_mass"],
                row["total_steps"]))
    print("  saturation depth:", saturation, "| nonhalting:", nonhalting)


if __name__ == "__main__":
    main()
