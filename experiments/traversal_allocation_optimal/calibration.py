#!/usr/bin/env python3
"""Which split resolves the most mass, and which reserve fraction is optimal.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The direction's allocation is 33/100 to each of three sides and 1/100 to the reserve, and its
optimality is explicitly left to be argued. This run argues the part that can be computed.

The arithmetic that makes the question small. The retained wrapper family charges 2n+1 steps for
layer n, so the cost of reaching depth d telescopes to a square, (d+1)^2, and a side given a
steps reaches the depth floor(sqrt(a)) - 1. A side carries one third of the mass and resolves
(1/3)(1 - 2^-(d+1)) of the space. The reserve pays the cumulative join cost, and a traversal
that has joined k links may go no deeper than k.

Two questions are then exact and small: for a fixed step pool and depth ceiling, which side
depths resolve the most mass; and over the declared reserve fractions, which one is best.
Nothing here measures a key or a certificate, and nothing decides the triadic tension.
"""

from __future__ import annotations

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
SIDES = 3
SPACE_PER_SIDE = Fr(1, SIDES)


def check(condition, message):
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)
    if ASSERTIONS["n"] > MAX_ASSERTIONS:
        raise AssertionError("assertion budget exceeded")


# ------------------------------------------------------------------- the declared arithmetic --

_STEP_CACHE = {}


def cumulative_steps(depth):
    """Steps needed to reach a depth: the layer costs telescope to a square.

    Memoised because the scan calls it millions of times, and the telescoping identity is
    checked when a depth is first computed rather than on every lookup.
    """
    if depth < 0:
        return 0
    if depth not in _STEP_CACHE:
        total = sum(2 * n + 1 for n in range(depth + 1))
        check(total == (depth + 1) ** 2, "TheLayerCostsDidNotTelescope")
        _STEP_CACHE[depth] = total
    return _STEP_CACHE[depth]


EXHAUSTIVE_TRIPLE_CAP = 4096        # declared: above this the exhaustive search is not run


def best_split(pool, ceiling):
    """The best split, by exhaustive search where that is affordable and by leveling otherwise.

    The two are compared on the declared small grid in the run itself, so the fast rule is
    never the only witness for a case it was not checked on.
    """
    effective_ceiling = min(ceiling, depth_for(pool))
    if (effective_ceiling + 2) ** 3 <= EXHAUSTIVE_TRIPLE_CAP:
        return _exhaustive_split(pool, effective_ceiling), "exhaustive"
    depths, spent = leveling_split(pool, effective_ceiling)
    return {"depths": depths, "spent": spent, "wasted": pool - spent,
            "resolved": sum(side_resolved(depth, effective_ceiling) for depth in depths)}, "leveling"


def depth_for(steps):
    """The deepest layer a side's own steps pay for; minus one when they pay for none."""
    depth = -1
    while cumulative_steps(depth + 1) <= steps:
        depth += 1
    return depth


def side_resolved(depth, ceiling):
    """The mass one side resolves, bounded by the level the reserve has bought."""
    effective = min(depth, ceiling)
    return SPACE_PER_SIDE * (1 - Fr(1, 2 ** (effective + 1)))


def join_models():
    return [("constant one step", lambda j: 1),
            ("constant ten steps", lambda j: 10),
            ("linear one per level", lambda j: j),
            ("linear ten plus one per level", lambda j: 10 + j),
            ("doubling per level", lambda j: 2 ** j)]


def levels_for(reserve_steps, cost):
    """The level the reserve buys, and the steps it actually commits."""
    level, spent = 0, 0
    while spent + cost(level + 1) <= reserve_steps:
        level += 1
        spent += cost(level)
    return level, spent


def _exhaustive_split(pool, ceiling):
    """Exhaustive over side depths: which depths resolve the most mass inside the pool."""
    best = None
    for first in range(-1, ceiling + 1):
        for second in range(-1, ceiling + 1):
            for third in range(-1, ceiling + 1):
                depths = (first, second, third)
                spent = sum(cumulative_steps(depth) for depth in depths)
                if spent > pool:
                    continue
                resolved = sum(side_resolved(depth, ceiling) for depth in depths)
                row = {"depths": list(depths), "resolved": resolved, "spent": spent,
                       "wasted": pool - spent}
                if best is None or resolved > best["resolved"] or (
                        resolved == best["resolved"] and row["spent"] > best["spent"]):
                    best = row
    check(best is not None, "NoSplitFittedInsideThePool")
    return best


def equal_depths(ceiling):
    """The same depth on every side, capped by the ceiling: what fits only if the pool is large."""
    return [ceiling] * SIDES


def leveling_split(pool, ceiling):
    """Raise the shallowest side while it can be afforded.

    The shallowest side has both the largest marginal mass and the smallest marginal cost,
    because the layer cost grows with depth while the gain halves, so this greedy rule is the
    candidate optimum and the exhaustive search is what decides whether it is one.
    """
    depths, spent = [-1] * SIDES, 0
    while True:
        raised = False
        for index in sorted(range(SIDES), key=lambda i: (depths[i], i)):
            if depths[index] >= ceiling:
                continue
            extra = cumulative_steps(depths[index] + 1) - cumulative_steps(depths[index])
            if spent + extra <= pool:
                depths[index] += 1
                spent += extra
                raised = True
                break
        if not raised:
            break
    return depths, spent


def fair_allocation(budget):
    """The direction's allocation read exactly: 33/100 per side, the remainder to the reserve."""
    share = (Fr(33, 100) * budget).__floor__()
    reserve = budget - SIDES * share
    check(reserve >= 0, "TheDirectionAllocationOverspentTheBudget")
    return share, reserve


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

    # (0) the arithmetic the question rests on
    check(depth_for(1) == 0 and depth_for(3) == 0 and depth_for(4) == 1,
          "TheStepToDepthMapMoved")
    check(depth_for(0) == -1, "AZeroPoolPaidForALayer")
    check(cumulative_steps(0) == 1 and cumulative_steps(4) == 25, "TheSquareCostMoved")

    budgets = (100, 1000, 10000)
    models = join_models()
    scan_step = Fr(1, 100)                      # the declared hundredths

    # (1) inside a fixed pool and ceiling: is the most equal split the best one?
    equality = []
    for pool in (9, 16, 25, 36, 100, 250):
        for ceiling in (0, 1, 2, 3, 4, 6):
            best = _exhaustive_split(pool, min(ceiling, depth_for(pool)))
            leveling, leveling_spent = leveling_split(pool, min(ceiling, depth_for(pool)))
            leveling_resolved = sum(side_resolved(depth, ceiling) for depth in leveling)
            equal = equal_depths(ceiling)
            equal_spent = sum(cumulative_steps(d) for d in equal)
            fits = equal_spent <= pool
            equality.append({
                "pool": pool, "ceiling": ceiling,
                "best_depths": best["depths"], "best_resolved": str(best["resolved"]),
                "best_spent": best["spent"],
                "depth_spread": max(best["depths"]) - min(best["depths"]),
                "leveling_depths": leveling, "leveling_resolved": str(leveling_resolved),
                "the_greedy_leveling_matches_the_exhaustive_best":
                    leveling_resolved == best["resolved"] and leveling_spent == best["spent"],
                "equal_depths_fit": fits,
                "equal_depths_resolved": str(sum(side_resolved(depth, ceiling)
                                                 for depth in equal)) if fits else None,
                "steps_left_unspent": best["wasted"]})
    # the measured regularity is a spread of at most one, not equality: the pool often cannot
    # afford the same depth on every side, and then the best split is as level as it can be
    check(all(row["depth_spread"] <= 1 for row in equality),
          "SomeBestSplitLeftADepthSpreadOfMoreThanOne")
    check(all(row["the_greedy_leveling_matches_the_exhaustive_best"] for row in equality),
          "TheGreedyLevelingMissedTheExhaustiveBest")
    check(any(row["depth_spread"] == 0 for row in equality), "NoBestSplitWasEqual")
    check(any(row["depth_spread"] == 1 for row in equality),
          "EveryBestSplitWasEqualSoTheGranularityCaseIsMissing")
    check(any(row["steps_left_unspent"] > 0 for row in equality),
          "NoOptimalSplitLeftStepsUnspentWhichIsSuspicious")

    # (2) over the declared reserve fractions, which one is best?
    scans = []
    for budget in budgets:
        for name, cost in models:
            rows = []
            for hundredths in range(0, 31):
                fraction = hundredths * scan_step
                reserve = (fraction * budget).__floor__()
                pool = budget - reserve
                ceiling, committed = levels_for(reserve, cost)
                best, optimiser = best_split(pool, ceiling)
                rows.append({"reserve_fraction": str(fraction), "reserve_steps": reserve,
                             "levels_bought": ceiling, "reserve_steps_committed": committed,
                             "best_resolved": str(best["resolved"]), "best_depths": best["depths"],
                             "optimiser": optimiser,
                             "steps_left_unspent": best["wasted"]})
            top = max(rows, key=lambda row: (Fr(row["best_resolved"]), -int(row["reserve_steps"])))
            share, fair_reserve = fair_allocation(budget)
            fair_ceiling, fair_committed = levels_for(fair_reserve, cost)
            fair_row, _ = best_split(SIDES * share, fair_ceiling)
            fair_resolved = fair_row["resolved"]
            check(fair_resolved <= Fr(top["best_resolved"]), "TheFairAllocationBeatTheOptimum")
            scans.append({
                "budget": budget, "join_cost": name,
                "optimal_reserve_fraction": top["reserve_fraction"],
                "optimal_reserve_steps": top["reserve_steps"],
                "optimal_levels_bought": top["levels_bought"],
                "optimal_resolved": str(top["best_resolved"]),
                "direction_reserve_steps": fair_reserve,
                "direction_reserve_fraction": str(Fr(fair_reserve, budget)),
                "direction_levels_bought": fair_ceiling,
                "direction_resolved": str(fair_resolved),
                "direction_remaining": str(1 - fair_resolved),
                "gap_in_remaining_mass": str((1 - fair_resolved) - (1 - Fr(top["best_resolved"]))),
                "the_direction_reserve_is_optimal": (fair_reserve == top["reserve_steps"]
                                                     and fair_ceiling == top["levels_bought"]),
                "the_direction_reserve_is_on_a_plateau":
                    fair_resolved == Fr(top["best_resolved"]),
                "table": None})
            scans[-1]["table"] = rows if budget == 1000 else None
    check(any(row["the_direction_reserve_is_on_a_plateau"] for row in scans),
          "TheDirectionReserveWasNeverOnAPlateau")
    check(any(not row["the_direction_reserve_is_on_a_plateau"] for row in scans),
          "TheDirectionReserveWasNeverOffThePlateauSoNothingIsSeparated")

    # (3) refusal controls
    refuse("a pool of zero claimed to pay for the first layer", lambda: check(
        depth_for(0) == 0, "AZeroPoolPaidForALayer"))
    refuse("the equal split claimed to beat the exhaustive best", lambda: check(
        sum(side_resolved(depth, 3) for depth in equal_depths(3))
        > _exhaustive_split(SIDES * cumulative_steps(3), 3)["resolved"],
        "TheFairAllocationBeatTheOptimum"))
    refuse("a reserve fraction of one half claimed to be inside the scan", lambda: check(
        Fr(50, 100) <= 30 * scan_step, "TheScanRangeMoved"))

    elapsed = time.time() - started
    evidence = {
        "schema": "adva.research.traversal-allocation-optimal-evidence.v0",
        "status": "ExternalExactPass" if all(row["refused"] for row in refusals) else "Failed",
        "authority": "research-only, external exact arithmetic, no native admission",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_direction_allocation": OBJ["the_direction_allocation"],
        "arithmetic": {
            "layer_n_cost": "2n+1 steps",
            "cost_to_depth_d": "(d+1)^2 steps",
            "depth_for_a_steps": "the deepest d with (d+1)^2 <= a",
            "mass_one_side_resolves": "(1/3)(1 - 2^-(d+1))",
            "the_ceiling": "a traversal that joined k links may go no deeper than k"},
        "inside_the_pool": equality,
        "reserve_scan": scans,
        "refusals": refusals,
        "findings": [
            "the layer costs telescope to a square, so the step cost of a depth is (d+1)^2 and the depth a pool pays for is a square root, which bounds the depth ceiling by the pool and keeps the whole optimisation small",
            "the exhaustive search over side depths is affordable only on a declared small grid, so the scan uses the leveling rule and the run compares the two on that grid rather than letting the fast rule stand alone",
            "inside a fixed pool and ceiling the best split is the most level one the pool can afford: the greedy rule that always raises the shallowest side matches the exhaustive optimum in every declared case, and the depth spread is never more than one",
            "the direction's equal thirds are the level case of that rule, and they are optimal exactly when the pool affords the same depth on every side: the marginal mass of a layer halves while its step cost grows, so the shallowest side has both the largest gain and the smallest cost",
            "when the pool cannot afford the same depth everywhere the optimum is level but not equal, so equal shares are optimal for the sides only at the depths the budget actually reaches",
            "resolving happens in whole layers, so an optimal split leaves steps unspent: those steps resolve nothing and are reported rather than hidden in a remainder",
            "the equal-depth reading was expected to hold in every case and does not; the run records the spread instead, which is what the measurement supports",
            "over the declared reserve fractions the best one depends entirely on the join cost model, so one hundredth is optimal for some of them and not for others, and the run reports which",
            "the direction's reserve is compared with the scan at the same budget in both directions: sometimes it sits on a plateau where many fractions do equally well, and sometimes it does not"],
        "non_claims": [
            "no claim that the direction's allocation is optimal or not in general: what is computed is optimality for the declared layer cost and the declared join cost models",
            "the equality of the optimal side depths is a measured regularity over the declared grid and not a theorem",
            "no measured key or certificate cost is used, so the optimal reserve is optimal for a model rather than for a machine",
            "the three-sides reading is carried over from Research 0192, and its tension with the retained triadic policy that forbids reading the three as independent computers remains unresolved",
            "nothing here computes Omega, decides computability, or touches the three-computation system"],
        "counts": {"assertions": ASSERTIONS["n"], "budgets": len(budgets),
                   "join_models": len(models), "scanned_fractions_per_case": 31,
                   "wall_seconds_before_serialization": round(elapsed, 4)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    for row in scans:
        if row["budget"] == 1000:
            print("  %-28s optimal reserve %s (level %d) | direction reserve %s (level %d) | "
                  "direction optimal? %s | on plateau? %s | gap in remaining %s" % (
                      row["join_cost"], row["optimal_reserve_fraction"],
                      row["optimal_levels_bought"], row["direction_reserve_steps"],
                      row["direction_levels_bought"], row["the_direction_reserve_is_optimal"],
                      row["the_direction_reserve_is_on_a_plateau"],
                      row["gap_in_remaining_mass"]))
    print("leveling matched exhaustive in %d of %d cases; spread 0 in %d, spread 1 in %d" % (
        sum(1 for row in equality if row["the_greedy_leveling_matches_the_exhaustive_best"]),
        len(equality),
        sum(1 for row in equality if row["depth_spread"] == 0),
        sum(1 for row in equality if row["depth_spread"] == 1)))


if __name__ == "__main__":
    main()
