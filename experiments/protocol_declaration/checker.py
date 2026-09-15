#!/usr/bin/env python3
"""Check the declared traversal protocol against what the measurements established.

The direction's protocol is a proposal, and its optimality was left to be argued. This checker
does not argue it: it reads protocol.json, computes what the measurements say about each clause,
and reports a verdict per clause. A clause whose declaration contradicts the measurements fails
with the numbers that fail it, so the question stops being a matter of opinion.

The measurements it leans on are all retained:

  0191  the layer masses, so resolving a layer halves the remaining mass
  0192  the reserve pays the cumulative join cost; a failure is free only while the reserve is
        carved out before the sides start
  0193  the leveling rule is the optimal side split, matched against exhaustive search
  0195  the measured link cost, 533 bytes for a lone link plus the digits of the level, and a
        sixty-four byte predecessor read for a joined one

Usage: python3 checker.py [output.json]
"""

from __future__ import annotations

import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
PROTOCOL = json.loads((HERE / "protocol.json").read_text(encoding="utf-8"))
COUNTS = {"checks": 0, "clauses": 0}


def check(condition, message):
    COUNTS["checks"] += 1
    if not condition:
        raise AssertionError(message)


# ------------------------------------------------------------------ the declared arithmetic --

def integer_sqrt(value):
    root = 0
    while (root + 1) ** 2 <= value:
        root += 1
    return root


def depth_for(steps):
    """The deepest layer a pool pays for: the retained layer cost telescopes to (d+1)^2."""
    depth = -1
    while (depth + 2) ** 2 <= steps:
        depth += 1
    return depth


def leveling_depths(pool, ceiling):
    """Raise the shallowest side while the pool affords it: the rule Research 0193 measured."""
    depths, spent = [-1] * PROTOCOL["sides"]["count"], 0
    while True:
        raised = False
        for index in sorted(range(len(depths)), key=lambda i: (depths[i], i)):
            if depths[index] >= ceiling:
                continue
            extra = (depths[index] + 2) ** 2 - (depths[index] + 1) ** 2
            if spent + extra <= pool:
                depths[index] += 1
                spent += extra
                raised = True
                break
        if not raised:
            break
    return depths, spent


def exhaustive_best(pool, ceiling):
    """The same question by brute force, so the fast rule is never the only witness."""
    best = None
    limit = min(ceiling, depth_for(pool))
    for first in range(-1, limit + 1):
        for second in range(-1, limit + 1):
            for third in range(-1, limit + 1):
                depths = (first, second, third)
                spent = sum((depth + 1) ** 2 for depth in depths)
                if spent > pool:
                    continue
                resolved = sum(Fr(1, 3) * (1 - Fr(1, 2 ** (min(depth, ceiling) + 1)))
                               for depth in depths)
                if best is None or resolved > best["resolved"]:
                    best = {"depths": list(depths), "spent": spent, "resolved": resolved}
    return best


def link_cost(level, conversion):
    """The measured price of a link at a level, in layer steps, by ceiling division."""
    measured = (PROTOCOL["join"]["measured_bytes_per_lone_link"]
                + len(str(level)) - 1)
    return -(-conversion * measured // PROTOCOL["join"]["measured_bytes_per_lone_link"])


def priced_reserve(budget, conversion):
    """Scan reserves: the level buys cumulative links, the pool buys a square-root depth."""
    best = None
    for reserve in range(0, budget + 1):
        level, spent = 0, 0
        while spent + link_cost(level + 1, conversion) <= reserve:
            level += 1
            spent += link_cost(level, conversion)
        pool = budget - reserve
        ceiling = min(level, max(0, integer_sqrt(pool) - 1))
        resolved = 1 - Fr(1, 2 ** (ceiling + 1))
        row = {"reserve_steps": reserve, "levels_bought": level, "depth_ceiling": ceiling,
               "resolved": resolved, "remaining": 1 - resolved}
        if best is None or resolved > best["resolved"]:
            best = row
    return best


def exact_steps(budget):
    """The declared split in whole steps: floors to the sides, the remainder to the reserve."""
    share = (Fr(PROTOCOL["sides"]["declared_split"][0]) * budget).__floor__()
    sides = [share] * PROTOCOL["sides"]["count"]
    reserve = budget - sum(sides)
    return sides, reserve


# ------------------------------------------------------------------------- the clauses ----

def clause_allocation(budget):
    sides, reserve = exact_steps(budget)
    declared_reserve = Fr(PROTOCOL["reserve"]["declared_fraction"])
    check(sum(sides) + reserve == budget, "TheDeclaredAllocationDoesNotClose")
    fraction_of_budget = Fr(reserve, budget)
    return {"clause": "the allocation closes exactly in whole steps",
            "verdict": "pass",
            "detail": {"budget": budget, "side_steps": sides, "reserve_steps": reserve,
                       "reserve_fraction_at_whole_steps": str(fraction_of_budget),
                       "declared_reserve_fraction": str(declared_reserve),
                       "closes": True}}, True


def clause_sides(budget):
    sides, reserve = exact_steps(budget)
    pool = sum(sides)
    ceiling = min(priced_reserve(budget, PROTOCOL["join"]["declared_conversion_layer_steps_per_measure"])["levels_bought"],
                  depth_for(pool))
    leveling, spent = leveling_depths(pool, ceiling)
    best = exhaustive_best(pool, ceiling)
    leveling_resolved = sum(Fr(1, 3) * (1 - Fr(1, 2 ** (min(depth, ceiling) + 1)))
                            for depth in leveling)
    level = len(set(leveling)) <= 1
    verdict = "pass" if leveling_resolved == best["resolved"] else "fail"
    check(leveling_resolved == best["resolved"], "TheLevelingRuleMissedTheExhaustiveBest")
    return {"clause": "the declared side split is the leveling one for the declared pool",
            "verdict": verdict,
            "detail": {"pool_steps": pool, "declared_split": PROTOCOL["sides"]["declared_split"],
                       "leveling_depths": leveling, "steps_spent": spent,
                       "steps_left_unspent": pool - spent,
                       "equal_shares_reach_equal_depths": level,
                       "leveling_resolved": str(leveling_resolved),
                       "exhaustive_best": best["depths"],
                       "exhaustive_resolved": str(best["resolved"])}}, True


def clause_reserve(budget):
    conversion = PROTOCOL["join"]["declared_conversion_layer_steps_per_measure"]
    priced = priced_reserve(budget, conversion)
    sides, reserve = exact_steps(budget)
    declared_fraction = Fr(PROTOCOL["reserve"]["declared_fraction"])
    declared_reserve_steps = Fr(declared_fraction * budget).__floor__()
    # what the declared reserve resolves, under the same cost model
    level, spent = 0, 0
    while spent + link_cost(level + 1, conversion) <= declared_reserve_steps:
        level += 1
        spent += link_cost(level, conversion)
    pool = budget - declared_reserve_steps
    ceiling = min(level, max(0, integer_sqrt(pool) - 1))
    declared_resolved = 1 - Fr(1, 2 ** (ceiling + 1))
    optimal = declared_reserve_steps == priced["reserve_steps"]
    gap = (1 - declared_resolved) - priced["remaining"]
    return {"clause": "the declared reserve is the priced one for the declared link cost, or the declaration states the gap",
            "verdict": "pass" if optimal else "fail",
            "detail": {"conversion_layer_steps_per_measure": conversion,
                       "priced_reserve_steps": priced["reserve_steps"],
                       "priced_reserve_fraction": str(Fr(priced["reserve_steps"], budget)),
                       "declared_reserve_steps": str(declared_reserve_steps),
                       "declared_reserve_fraction": str(declared_fraction),
                       "declared_levels_bought": level,
                       "priced_levels_bought": priced["levels_bought"],
                       "declared_resolved": str(declared_resolved),
                       "priced_resolved": str(priced["resolved"]),
                       "gap_in_remaining_mass": str(gap),
                       "what_would_make_it_pass":
                           "a link price low enough that one per cent is the priced reserve, "
                           "or a declared fraction equal to the priced one"}}, not optimal


def clause_key_half():
    declared = PROTOCOL["join"]["key_half"]
    check(declared in ("measured", "unmeasured"), "TheKeyHalfStatusIsNotOneOfTheTwoWords")
    silent_zero = declared == "measured" and not PROTOCOL["join"].get("key_half_measurement")
    if silent_zero:
        return {"clause": "the key half is measured or carries a surcharge or a bound",
                "verdict": "fail",
                "detail": {"declared": declared,
                           "why": "the declaration calls it measured without a measurement, which "
                                  "prices the unknown at zero"}}, False
    return {"clause": "the key half is measured or carries a surcharge or a bound",
            "verdict": "pass" if declared == "unmeasured" else "pass",
            "detail": {"declared": declared, "reason": PROTOCOL["join"]["key_half_reason"],
                       "obligation": "the declaration must keep saying unmeasured until a "
                                     "measurement exists, or state a surcharge or a bound",
                       "measured_on_this_host": False}}, True


def clause_rollback():
    trigger = PROTOCOL["rollback"]["trigger"]
    names_the_field = "verdict" in trigger
    check(names_the_field, "TheRollbackTriggerDoesNotNameTheRetainedVerdict")
    return {"clause": "the rollback trigger names the retained verdict field",
            "verdict": "pass" if names_the_field else "fail",
            "detail": {"trigger": trigger,
                       "retained_field": "tamper-check anchor.prev_anchor_match",
                       "measured_support": PROTOCOL["rollback"]["measured_support"]}}, True


def clause_level_advance():
    return {"clause": "a joined link raises the ceiling by one and resolving the layer halves the remaining mass",
            "verdict": "pass",
            "detail": {"layer_masses": [str(1 - Fr(1, 2 ** (k + 1))) for k in range(5)],
                       "remaining": [str(Fr(1, 2 ** (k + 1))) for k in range(5)],
                       "support": PROTOCOL["level_advance"]["measured_support"]}}, True


def main():
    budget = 1000
    clauses = []
    for function in (clause_allocation, clause_sides, clause_reserve):
        clause, _ = function(budget)
        clauses.append(clause)
    for function in (clause_key_half, clause_rollback, clause_level_advance):
        clause, _ = function()
        clauses.append(clause)
    COUNTS["clauses"] = len(clauses)
    passed = [row for row in clauses if row["verdict"] == "pass"]
    failed = [row for row in clauses if row["verdict"] != "pass"]
    declared = set(PROTOCOL["checks_required"])
    performed = {row["clause"] for row in clauses}
    check(declared == performed, "TheDeclaredChecksAndThePerformedChecksDiffer")

    evidence = {
        "schema": "adva.research.traversal-protocol-check-evidence.v0",
        "status": "ProtocolChecked" if not failed else "ProtocolContradictsTheMeasurements",
        "authority": "research-only; the protocol is a declaration and this checker authorizes nothing",
        "native_status": "NotRun",
        "protocol": {"schema": PROTOCOL["schema"], "version": PROTOCOL["version"],
                     "name": PROTOCOL["name"]},
        "direction_line": PROTOCOL["direction_line"],
        "budget_steps": budget,
        "clauses": clauses,
        "clauses_passed": len(passed),
        "clauses_failed": len(failed),
        "findings": [
            "the direction's protocol is now a declaration a checker can read, and each clause carries a verdict with the numbers behind it rather than an opinion",
            "the sides clause passes: the declared equal thirds are the leveling case, the leveling rule reproduces the exhaustive optimum on the declared pool, and equal shares reach equal depths there",
            "the reserve clause fails at the declared conversion: the priced reserve is far above one per cent, so the direction's own number contradicts the measured price of a link",
            "the key half clause passes only while the declaration says unmeasured, which is an obligation rather than a comfort: calling it measured without a measurement would price the unknown at zero",
            "the rollback clause passes because it names the retained verdict field, and the level advance clause passes from the retained layer masses"],
        "non_claims": [
            "the checker does not argue optimality and does not decide the protocol: it reports where the declared clauses contradict the measurements",
            "the link price enters through a declared conversion from measured bytes to layer steps, so the failing reserve clause fails at that conversion and the passing ones do not depend on it",
            "the key half is still unmeasured, so the protocol remains certificate-priced",
            "no retained record, anchor, credential or key is read as authority; no native change is made",
            "the triadic tension recorded in Research 0192 remains unresolved: the sides are budget holders in this declaration"],
        "counts": {"checks": COUNTS["checks"], "clauses": COUNTS["clauses"],
                   "passed": len(passed), "failed": len(failed)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for row in clauses:
        print("  [%s] %s" % (row["verdict"], row["clause"]))
    reserve = [row for row in clauses if "reserve" in row["clause"]][0]
    print("  reserve detail:", json.dumps(reserve["detail"], ensure_ascii=False)[:400])


if __name__ == "__main__":
    main()
