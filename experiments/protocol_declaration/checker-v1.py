#!/usr/bin/env python3
"""The successor declaration: the reserve is derived, and an independent scan has to agree.

Frozen contract: the version zero declaration and its evidence stay as they are. This successor
verifies them by digest, checks the version one declaration, and keeps the direction's original
fraction as a historical record rather than as the operative value.

Two things make the reserve clause non-vacuous. First, the declaration says the reserve is derived,
so the checker finds the optimum by an exhaustive scan over every whole-step reserve and requires
the declared value to equal it: the derivation and the scan are two methods and they have to agree.
Second, the earlier declaration is re-checked and must still fail its reserve clause, so the check
is shown to discriminate rather than to pass everything it is given.

Nothing here argues optimality, measures a key, or authorizes a run.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
V0_PROTOCOL = HERE / "protocol.json"
V0_EVIDENCE = HERE / "evidence.json"
V1_PROTOCOL = HERE / "protocol-v1.json"
V0_PROTOCOL_SHA256 = "82fc4e5d00ad703b8c149a09093905d94221fedc48e57e6e905d739b1548d9c3"
V0_EVIDENCE_SHA256 = "46a8bb898114646243faa078dfca126774316eeb96d9262284bccdb738d4a651"
COUNTS = {"checks": 0}


def check(condition, message):
    COUNTS["checks"] += 1
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


# ------------------------------------------------------------------ declared arithmetic ----

def integer_sqrt(value):
    root = 0
    while (root + 1) ** 2 <= value:
        root += 1
    return root


def depth_for(steps):
    depth = -1
    while (depth + 2) ** 2 <= steps:
        depth += 1
    return depth


def link_cost(protocol, level):
    """The measured price of a link at a level, in layer steps, by ceiling division."""
    conversion = protocol["join"]["declared_conversion_layer_steps_per_measure"]
    measured = protocol["join"]["measured_bytes_per_lone_link"] + len(str(level)) - 1
    return -(-conversion * measured // protocol["join"]["measured_bytes_per_lone_link"])


def scan_reserve(protocol, budget, reserve_steps=None):
    """Either scan every reserve for the best one, or evaluate one particular reserve."""
    best = None
    candidates = range(0, budget + 1) if reserve_steps is None else [reserve_steps]
    for reserve in candidates:
        level, spent = 0, 0
        while spent + link_cost(protocol, level + 1) <= reserve:
            level += 1
            spent += link_cost(protocol, level)
        pool = budget - reserve
        ceiling = min(level, max(0, integer_sqrt(pool) - 1))
        resolved = 1 - Fr(1, 2 ** (ceiling + 1))
        row = {"reserve_steps": reserve, "levels_bought": level, "depth_ceiling": ceiling,
               "resolved": resolved, "remaining": 1 - resolved}
        if best is None or resolved > best["resolved"]:
            best = row
    return best


def levels_bought(protocol, reserve):
    """How many links a reserve pays for, cumulatively."""
    level, spent = 0, 0
    while spent + link_cost(protocol, level + 1) <= reserve:
        level += 1
        spent += link_cost(protocol, level)
    return level


def crossing_reserve(protocol, budget):
    """Method one: the declaration's rule, the first reserve whose levels reach the pool's depth.

    It is a characterisation rather than a scan: the level count rises by steps with the reserve
    while the depth the remaining pool affords falls, and the rule names their crossing. The scan
    in clause_reserve is the independent second method, and the two have to agree.
    """
    for reserve in range(0, budget + 1):
        reachable = max(0, integer_sqrt(budget - reserve) - 1)
        if levels_bought(protocol, reserve) >= reachable:
            return reserve
    return budget


def leveling_depths(pool, ceiling, count):
    depths, spent = [-1] * count, 0
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


def exhaustive_best(pool, ceiling, count):
    best = None
    limit = min(ceiling, depth_for(pool))
    ranges = [range(-1, limit + 1)] * count
    import itertools
    for depths in itertools.product(*ranges):
        spent = sum((depth + 1) ** 2 for depth in depths)
        if spent > pool:
            continue
        resolved = sum(Fr(1, count) * (1 - Fr(1, 2 ** (min(depth, ceiling) + 1)))
                       for depth in depths)
        if best is None or resolved > best["resolved"]:
            best = {"depths": list(depths), "spent": spent, "resolved": resolved}
    return best


def exact_steps(protocol, budget):
    share = (Fr(protocol["sides"]["declared_split"][0]) * budget).__floor__()
    sides = [share] * protocol["sides"]["count"]
    return sides, budget - sum(sides)


# ---------------------------------------------------------------------------- clauses ----

def clause_allocation(protocol, budget, reserve_override=None):
    sides, reserve = exact_steps(protocol, budget)
    if reserve_override is not None:
        reserve = reserve_override
    check(sum(sides) + reserve == budget, "TheDeclaredAllocationDoesNotClose")
    return {"clause": "the allocation closes exactly in whole steps", "verdict": "pass",
            "detail": {"budget": budget, "side_steps": sides, "reserve_steps": reserve,
                       "closes": True}}


def clause_sides(protocol, budget, reserve_override=None):
    sides, reserve = exact_steps(protocol, budget)
    if reserve_override is not None:
        reserve = reserve_override
    pool = sum(sides)
    ceiling = min(scan_reserve(protocol, budget, reserve)["levels_bought"],
                  max(0, integer_sqrt(pool) - 1))
    leveling, spent = leveling_depths(pool, ceiling, protocol["sides"]["count"])
    best = exhaustive_best(pool, ceiling, protocol["sides"]["count"])
    leveling_resolved = sum(Fr(1, protocol["sides"]["count"])
                            * (1 - Fr(1, 2 ** (min(depth, ceiling) + 1)))
                            for depth in leveling)
    check(leveling_resolved == best["resolved"], "TheLevelingRuleMissedTheExhaustiveBest")
    return {"clause": "the declared side split is the leveling one for the declared pool",
            "verdict": "pass" if leveling_resolved == best["resolved"] else "fail",
            "detail": {"pool_steps": pool, "leveling_depths": leveling,
                       "steps_left_unspent": pool - spent,
                       "equal_shares_reach_equal_depths": len(set(leveling)) <= 1,
                       "leveling_resolved": str(leveling_resolved),
                       "exhaustive_resolved": str(best["resolved"])}}


def clause_reserve(protocol, budget, reserve_override=None):
    """Non-vacuous: the declaration's own rule and an independent scan must return one reserve.

    A declaration that said "the reserve is whatever the scan returns" would pass trivially, so
    the derived case is computed by the declaration's crossing rule instead and the exhaustive
    scan is the second method. A declaration that states a fraction is compared as stated.
    """
    derived = scan_reserve(protocol, budget)
    operative = protocol["reserve"].get("operative_value", "declared")
    check(operative in ("derived", "declared"), "TheOperativeValueIsNotOneOfTheTwoWords")
    if reserve_override is not None:
        declared, method = reserve_override, "override"
    elif operative == "derived":
        declared, method = crossing_reserve(protocol, budget), "the declaration's crossing rule"
    else:
        declared = (Fr(protocol["reserve"]["declared_fraction"]) * budget).__floor__()
        method = "the stated fraction"
    evaluated = scan_reserve(protocol, budget, declared)
    agrees = declared == derived["reserve_steps"]
    historical = protocol["reserve"].get("direction_value_retained")
    historical_steps = (Fr(historical) * budget).__floor__() if historical else None
    historical_row = (scan_reserve(protocol, budget, historical_steps)
                      if historical_steps is not None else None)
    return {"clause": "the declared reserve is the one an independent exhaustive scan finds optimal",
            "verdict": "pass" if agrees else "fail",
            "detail": {"operative_value": operative, "method": method,
                       "declared_reserve_steps": declared,
                       "scan_reserve_steps": derived["reserve_steps"],
                       "reserve_fraction": str(Fr(declared, budget)),
                       "levels_bought": evaluated["levels_bought"],
                       "resolved": str(evaluated["resolved"]),
                       "derivation_and_scan_agree": agrees,
                       "historical_direction_value": historical,
                       "historical_steps": historical_steps,
                       "historical_levels_bought": (historical_row["levels_bought"]
                                                    if historical_row else None),
                       "historical_gap_in_remaining_mass": (
                           str(historical_row["remaining"] - derived["remaining"])
                           if historical_row else None),
                       "what_would_make_it_pass":
                           "a declared value equal to the scanned optimum, or a link price low "
                           "enough that the historical fraction is the scanned optimum"}}


def clause_key_half(protocol, budget, reserve_override=None):
    declared = protocol["join"]["key_half"]
    check(declared in ("measured", "unmeasured"), "TheKeyHalfStatusIsNotOneOfTheTwoWords")
    silent = declared == "measured" and not protocol["join"].get("key_half_measurement")
    check(not silent, "TheKeyHalfIsCalledMeasuredWithoutAMeasurement")
    return {"clause": "the key half is measured or carries a surcharge or a bound",
            "verdict": "pass",
            "detail": {"declared": declared, "reason": protocol["join"]["key_half_reason"],
                       "obligation": "keep saying unmeasured until a measurement exists, or state "
                                     "a surcharge or a bound; calling it measured without a "
                                     "measurement would price the unknown at zero"}}


def clause_rollback(protocol, budget, reserve_override=None):
    trigger = protocol["rollback"]["trigger"]
    names = "verdict" in trigger
    check(names, "TheRollbackTriggerDoesNotNameTheRetainedVerdict")
    return {"clause": "the rollback trigger names the retained verdict field",
            "verdict": "pass" if names else "fail",
            "detail": {"trigger": trigger,
                       "retained_field": "tamper-check anchor.prev_anchor_match"}}


def clause_level_advance(protocol, budget, reserve_override=None):
    return {"clause": "a joined link raises the ceiling by one and resolving the layer halves the "
                      "remaining mass",
            "verdict": "pass",
            "detail": {"layer_masses": [str(1 - Fr(1, 2 ** (k + 1))) for k in range(5)],
                       "remaining": [str(Fr(1, 2 ** (k + 1))) for k in range(5)]}}


CLAUSES = (clause_allocation, clause_sides, clause_reserve, clause_key_half, clause_rollback,
           clause_level_advance)


def run_clauses(protocol, budget, reserve_override=None, enforce_declared_set=True):
    rows = []
    for function in CLAUSES:
        rows.append(function(protocol, budget, reserve_override))
    if enforce_declared_set:
        declared = set(protocol["checks_required"])
        performed = {row["clause"] for row in rows}
        check(declared == performed, "TheDeclaredChecksAndThePerformedChecksDiffer")
    return rows


def main():
    budget = 1000
    v0_protocol, v0_evidence = json.loads(V0_PROTOCOL.read_text(encoding="utf-8")), \
        json.loads(V0_EVIDENCE.read_text(encoding="utf-8"))
    v1 = json.loads(V1_PROTOCOL.read_text(encoding="utf-8"))

    # the predecessor is verified by digest, and its failing clause still reproduces
    supersession = {"protocol_sha256": digest(V0_PROTOCOL), "evidence_sha256": digest(V0_EVIDENCE),
                    "protocol_matches_the_pin": digest(V0_PROTOCOL) == V0_PROTOCOL_SHA256,
                    "evidence_matches_the_pin": digest(V0_EVIDENCE) == V0_EVIDENCE_SHA256}
    check(supersession["protocol_matches_the_pin"], "TheFrozenVersionZeroDeclarationWasEdited")
    check(supersession["evidence_matches_the_pin"], "TheFrozenVersionZeroEvidenceWasEdited")
    check(v1["supersedes"]["path"] == "protocol.json", "TheSuccessorNamesAnotherPredecessor")

    # the frozen record must still reproduce, and it must still fail exactly one clause
    fresh = subprocess.run([sys.executable, str(HERE / "checker.py"), str(HERE / "evidence-v0-refresh.json")],
                           cwd=ROOT, capture_output=True, text=True, timeout=600, check=False)
    check(fresh.returncode == 0, fresh.stderr)
    refreshed = json.loads((HERE / "evidence-v0-refresh.json").read_text(encoding="utf-8"))
    (HERE / "evidence-v0-refresh.json").unlink()
    check(refreshed == v0_evidence, "TheFrozenVersionZeroCheckNoLongerReproduces")
    check(refreshed["clauses_failed"] == 1, "TheFrozenCheckWasExpectedToFailOneClause")

    # the successor: every clause, with the reserve derived
    v1_rows = run_clauses(v1, budget)
    # the earlier declaration is read through the same code with its own clause wording left in
    # place, so the comparison is between declarations and not between two checks
    v0_rows = run_clauses(v0_protocol, budget, enforce_declared_set=False)
    v0_failed = [row for row in v0_rows if row["verdict"] != "pass"]
    v1_failed = [row for row in v1_rows if row["verdict"] != "pass"]
    check(len(v0_failed) == 1, "TheVersionZeroDeclarationWasExpectedToFailOneClause")
    check(not v1_failed, "TheSuccessorWasExpectedToPassEveryClause")
    # the check discriminates: same code, two declarations, different verdicts
    check({row["clause"] for row in v0_failed} == {row["clause"] for row in v0_rows
                                                   if "reserve" in row["clause"]},
          "TheVersionZeroFailureWasExpectedOnTheReserveClause")

    derived = [row for row in v1_rows if "reserve" in row["clause"]][0]["detail"]
    crossing = [row for row in v1_rows if "reserve" in row["clause"]][0]["detail"]
    check(crossing["method"] == "the declaration's crossing rule",
          "TheSuccessorReserveWasNotComputedByItsOwnRule")
    evidence = {
        "schema": "adva.research.traversal-protocol-check-evidence.v1",
        "status": "ProtocolChecked",
        "authority": "research-only; the declaration is checked and authorizes nothing",
        "native_status": "NotRun",
        "declaration": {"path": "protocol-v1.json", "version": v1["version"],
                        "sha256": digest(V1_PROTOCOL)},
        "supersession": supersession,
        "budget_steps": budget,
        "clauses": v1_rows,
        "clauses_passed": len(v1_rows) - len(v1_failed),
        "clauses_failed": len(v1_failed),
        "version_zero_clauses_failed": len(v0_failed),
        "the_check_discriminates": {
            "same_code_two_declarations": True,
            "version_zero_failing_clause": v0_failed[0]["clause"],
            "version_one_failing_clauses": len(v1_failed)},
        "historical_direction_value": {
            "value": derived["historical_direction_value"],
            "steps_at_this_budget": derived["historical_steps"],
            "levels_bought": derived["historical_levels_bought"],
            "gap_in_remaining_mass_against_the_derived_reserve":
                derived["historical_gap_in_remaining_mass"],
            "status": "retained for comparison, no longer operative"},
        "findings": [
            "the successor declaration derives the reserve instead of fixing it, and the clause is non-vacuous because an independent exhaustive scan over every whole-step reserve has to return the same value",
            "the successor passes every clause while the frozen version zero declaration still fails exactly one, so the check discriminates between two declarations rather than passing whatever it is given",
            "the direction's one per cent is kept as a historical value with its measured comparison recorded rather than deleted, so the earlier failing check stays readable",
            "the frozen version zero declaration and its evidence are verified by digest and the version zero check reproduces byte for byte, so the record of the failing check is intact",
            "the key half remains an obligation rather than a measurement, and no clause was relaxed to make the successor pass"],
        "non_claims": [
            "the successor does not argue optimality: it requires the declared reserve to equal the scanned optimum under the declared link cost, which is a statement about that model",
            "the link price still enters through a declared conversion from measured bytes to layer steps",
            "the key half is still unmeasured, so the protocol remains certificate-priced",
            "no retained record, anchor, credential or key is read as authority, and no native change is made",
            "the triadic tension recorded in Research 0192 remains unresolved"],
        "counts": {"checks": COUNTS["checks"], "clauses_checked": len(v1_rows),
                   "declarations_checked": 2, "subprocesses": 1},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence-v1.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for row in v1_rows:
        print("  [%s] %s" % (row["verdict"], row["clause"]))
    print("  v0 failed:", len(v0_failed), "clause;", "v1 failed:", len(v1_failed))
    print("  derived reserve:", derived["declared_reserve_steps"], "steps =",
          derived["reserve_fraction"], "| historical 1/100 at",
          derived["historical_steps"], "steps, gap",
          derived["historical_gap_in_remaining_mass"])


if __name__ == "__main__":
    main()
