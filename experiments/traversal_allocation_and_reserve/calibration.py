#!/usr/bin/env python3
"""The traversal allocation, its reserve, and where the reserve stops paying.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The direction's protocol, tested only where it can be tested exactly:

  33/100 to each of three sides and 1/100 for the key and certificate part; attempt; roll
  back safely when the link does not join; advance one level when it does.

Four exact questions:

  one    is the allocation closed? In hundredths it is, and in binary64 it is not, and the
         difference is not academic: it moves steps between a side and the reserve.
  two    what does the reserve pay for? A declared join cost model, so the answer is the
         largest level the reserve still pays for, which is a critical point and not a proof
         of optimality. The direction left optimality to be argued; this run does not argue it.
  three  is the rollback safe? The join is a real sha256 link, so a failed join can be shown
         to leave the chain head and the resolved level unchanged -- unless the reserve is
         carved out of a side's share, in which case a failed attempt really does consume it.
  four   how do budget shares and probability masses relate? They are different quantities;
         the run measures the map between them instead of identifying them.

Nothing here computes Omega, decides computability, or reads a retained anchor as authority.
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


# ------------------------------------------------------------------ the declared allocation --

SIDES = ("side_a", "side_b", "side_c")
SHARE = Fr(33, 100)
RESERVE = Fr(1, 100)


def remaining_mass(depth):
    """The mass still unresolved at a depth cut, recomputed from the layer masses.

    Named for what it returns: the earlier name said layer mass while the value was the
    tail beyond a cut, which is the same wrong-quantity slip the record keeps warning about.
    """
    resolved = sum((Fr(2 ** n, 2 ** (2 * n + 1)) for n in range(depth + 1)), Fr(0))
    check(resolved == 1 - Fr(1, 2 ** (depth + 1)), "TheResolvedMassIdentityFailed")
    return Fr(1, 2 ** (depth + 1))


def exact_steps(budget):
    """The declared split in whole steps: floors to the sides, the remainder to the reserve."""
    share = (SHARE * budget).__floor__()
    sides = {name: share for name in SIDES}
    reserve = budget - 3 * share
    check(reserve >= 0, "TheRemainderToTheReserveWasNegative")
    return sides, Fr(reserve)


def rounded_steps(budget):
    """The same split read through binary64 and rounded per part, which is how it drifts."""
    share = int(round(float(SHARE) * budget))
    reserve = int(round(float(RESERVE) * budget))
    return {name: share for name in SIDES}, Fr(reserve), share * 3 + reserve - budget


# ------------------------------------------------------------------------------ the join ----

def checkpoint(level, resolved, remaining):
    material = ("level=%d;resolved=%s;remaining=%s" % (level, resolved, remaining)).encode()
    return hashlib.sha256(material).hexdigest()


def link(anchor, checkpoint_digest):
    """anchor_{t+1} = H(anchor_t || checkpoint): the retained lineage form, used as a link."""
    return hashlib.sha256((anchor + "||" + checkpoint_digest).encode()).hexdigest()


def join_cost(level, model):
    """The declared cost of assembling and verifying one key and certificate link."""
    base, growth = model
    return base + growth * level


def largest_level_the_reserve_pays(budget, model):
    """The critical level: past it the one-percent reserve no longer pays for the join."""
    _, reserve = exact_steps(budget)
    base, growth = model
    if growth == 0:
        # a join cost that does not grow is not a level bound at all, and reporting a large
        # number here would read as one
        return (None if base <= reserve else 0), reserve
    level = 0
    while join_cost(level + 1, model) <= reserve:
        level += 1
        if level > 4096:
            break
    return level, reserve


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

    # (0) the allocation closes exactly in hundredths and does not close in binary64
    check(3 * SHARE + RESERVE == 1, "TheHundredthAllocationDoesNotClose")
    check(3 * 33 + 1 == 100, "TheHundredthArithmeticIsWrong")
    float_total = 3 * float(SHARE) + float(RESERVE)
    # the naive closure test passes in binary64, and that is the finding rather than a relief:
    # the three over-allocations and the reserve's under-allocation round back onto one, so the
    # test cannot see the inexactness at all
    check(float_total == 1.0, "TheBinary64ClosureTestWasExpectedToPassAndHideTheDefect")
    exact_defect = Fr(1) - (Fr(float(SHARE)) * 3 + Fr(float(RESERVE)))
    check(exact_defect != 0, "TheHundredthsWereExpectedToBeInexactInBinary64")
    check(exact_defect < 0, "TheBinary64RouteWasExpectedToOverAllocate")
    third_defect = Fr(1) - Fr(float(Fr(1, 3))) * 3
    check(third_defect != 0, "TheThirdWasExpectedToBeInexactInBinary64")
    check(3 * float(Fr(1, 3)) == 1.0, "TheThirdWasExpectedToRoundBackToOne")
    closed_in_floats = {
        "naive_test_three_times_0.33_plus_0.01": repr(float_total),
        "naive_test_passes": float_total == 1.0,
        "exact_defect_of_the_hundredths": str(exact_defect),
        "exact_defect_of_a_third": str(third_defect),
        "naive_test_on_three_thirds": repr(3 * float(Fr(1, 3))),
        "reading": ("in binary64 the allocation closes by rounding, so the ordinary closure test "
                    "passes while the parts are not exact: the defect is negative, the route "
                    "over-allocates, and only exact rationals or a step count can show it"),
    }

    # (1) step level: the exact rule and the rounded rule move steps between parts
    step_table = []
    for budget in (100, 1000, 10, 3):
        sides, reserve = exact_steps(budget)
        rounded_sides, rounded_reserve, drift = rounded_steps(budget)
        step_table.append({
            "budget": budget,
            "exact_share_each": str(sides[SIDES[0]]), "exact_reserve": str(reserve),
            "rounded_share_each": rounded_sides[SIDES[0]],
            "rounded_reserve": str(rounded_reserve),
            "rounded_total_drift": str(drift),
            "the_rounded_reserve_falls_below_the_declared_percent":
                rounded_reserve < Fr(RESERVE * budget),
            "exact_reserve_is_at_least_the_declared_percent": reserve >= Fr(RESERVE * budget),
        })
    check(any(row["the_rounded_reserve_falls_below_the_declared_percent"] for row in step_table),
          "TheRoundedRouteNeverStarvedTheReserve")
    check(all(row["exact_reserve_is_at_least_the_declared_percent"] for row in step_table),
          "TheExactRuleDippedBelowTheDeclaredReserve")

    # (2) what the reserve pays for: the critical level under declared cost models
    models = [("constant one step", (1, 0)),
              ("constant ten steps", (10, 0)),
              ("linear, one step per level", (1, 1)),
              ("linear, ten plus one per level", (10, 1)),
              ("doubling per level", (1, None))]  # the doubling cost is 2^level
    critical = []
    for name, model in models:
        if model[1] is None:
            # doubling: the reserve buys levels while 2^level fits inside it
            _, reserve = exact_steps(1000)
            level = 0
            while Fr(2 ** (level + 1)) <= reserve:
                level += 1
                if level > 64:
                    break
            critical.append({"cost_model": name, "reserve_at_budget_1000": str(reserve),
                             "largest_level_the_reserve_pays": level,
                             "unbounded": False,
                             "reaches_the_declared_bound": level >= 8,
                             "reading": ("a join cost that doubles per level is what turns the "
                                         "reserve into a bound on depth")})
            continue
        level, reserve = largest_level_the_reserve_pays(1000, model)
        unbounded = level is None
        critical.append({"cost_model": name, "reserve_at_budget_1000": str(reserve),
                         "largest_level_the_reserve_pays": level,
                         "unbounded": unbounded,
                         "reaches_the_declared_bound": unbounded or level >= 8,
                         "reading": ("a constant join cost is a bounded toll and not a level "
                                     "bound at all, so the reserve does not limit depth"
                                     if model[1] == 0 else
                                     "a join cost that grows with the level bounds how deep the "
                                     "reserve carries the traversal, and that bound is the critical "
                                     "point rather than a proof of optimality")})
    check(any(row["reaches_the_declared_bound"] for row in critical),
          "NoCostModelLetTheReserveReachTheDeclaredBound")
    check(any(not row["reaches_the_declared_bound"] for row in critical),
          "EveryCostModelReachedTheBoundSoNothingIsSeparated")

    # (3) the join as a real link, and the rollback as the head not moving
    anchor = "genesis"
    head, resolved = anchor, Fr(0)
    chain = [{"level": 0, "anchor": head, "resolved": str(resolved)}]
    successes, failures = 0, 0
    for level in range(1, 8):
        digest = checkpoint(level, resolved, remaining_mass(level - 1))
        candidate = link(head, digest)
        cost = 2 ** level          # the doubling model, so the traversal really does stop
        _, reserve = exact_steps(1000)
        if cost <= reserve:
            head = candidate
            resolved = 1 - remaining_mass(level)
            successes += 1
            chain.append({"level": level, "anchor": head, "resolved": str(resolved),
                          "joined": True})
        else:
            failures += 1
            chain.append({"level": level, "anchor": head, "resolved": str(resolved),
                          "joined": False, "why": "the reserve no longer pays for the link"})
    check(successes >= 1 and failures >= 1, "TheTraversalEitherNeverJoinedOrNeverRefused")
    # the traversal's stopping point and the reserve's critical level are computed in two
    # different ways above and here, and they must agree
    doubling = [row for row in critical if row["cost_model"] == "doubling per level"][0]
    check(doubling["largest_level_the_reserve_pays"] == successes,
          "TheTraversalAndTheCriticalLevelDisagree")
    # rollback safety: the head after a failure is the head before it
    for before, after in zip(chain, chain[1:]):
        if after.get("joined") is False:
            check(after["anchor"] == before["anchor"], "AFailedJoinMovedTheChainHead")
            check(after["resolved"] == before["resolved"], "AFailedJoinResolvedALayer")
    check(all(row["anchor"] == link(chain[index - 1]["anchor"],
                                    checkpoint(row["level"],
                                              Fr(chain[index - 1]["resolved"]),
                                              remaining_mass(row["level"] - 1)))
              for index, row in enumerate(chain) if index and row.get("joined")),
          "TheChainIsNotTheDeclaredHashChain")

    # (4) the unsafe variant: a reserve carved out of one side's share is consumed by a failure
    #
    # every quantity in this section is in steps, and that is stated because the first version
    # of it added a step count to a fraction: Fraction is dimensionless, so exact arithmetic did
    # not notice the unit error, and only rewriting it in one unit did.
    sides_at_100, reserve_steps_at_100 = exact_steps(100)
    side_pool = sides_at_100[SIDES[0]]                  # steps this side may spend
    failed_cost = join_cost(1, (1, 1))                  # steps a failed join costs
    check(side_pool == 33 and reserve_steps_at_100 == 1, "TheDeclaredStepSplitMoved")
    safe_after_failure = side_pool                      # the reserve is not the side's to lose
    unsafe_after_failure = side_pool - failed_cost      # the reserve came out of this side
    check(unsafe_after_failure < safe_after_failure, "TheUnsafeVariantConsumedNothing")
    carve = {"units": "steps, at a declared budget of one hundred",
             "side_pool": str(side_pool), "reserve_pool": str(reserve_steps_at_100),
             "cost_of_a_failed_join": str(failed_cost),
             "carved_out_before_the_sides_start": {
                 "side_after_a_failed_join": str(safe_after_failure), "unchanged": True},
             "carved_out_of_a_side": {
                 "side_after_a_failed_join": str(unsafe_after_failure), "unchanged": False,
                 "defect_in_steps": str(safe_after_failure - unsafe_after_failure)},
             "reading": ("a failure is free only while the reserve belongs to no side; taking it "
                         "out of a side makes the rollback cost that side its share, by exactly "
                         "the cost of the failed join")}

    # (5) the two quantities kept apart: budget shares are not probability masses
    level_map = [{"joins": k, "resolved_mass": str(1 - remaining_mass(k)),
                  "remaining_mass": str(remaining_mass(k))}
                 for k in range(0, 5)]
    check(all(Fr(row["remaining_mass"]) * 2 == remaining_mass(row["joins"] - 1)
              for row in level_map if row["joins"] > 0),
          "TheRemainingMassIsNotHalvingPerJoin")
    check(all(Fr(row["resolved_mass"]) + Fr(row["remaining_mass"]) == 1 for row in level_map),
          "TheLevelMapDoesNotAccountForTheWholeSpace")
    separation = {
        "budget_shares": ["33/100", "33/100", "33/100", "1/100"],
        "probability_masses_at_level_zero": ["1/2", "1/2"],
        "the_two_are_different_quantities": True,
        "why": ("a share is how much work a side may spend and a mass is how much of the space "
                "is resolved; the reserve buys joins and does not carry probability"),
    }
    check(sum((Fr(value) for value in separation["budget_shares"]), Fr(0)) == 1,
          "TheBudgetSharesDoNotFillOne")
    check(separation["budget_shares"] != separation["probability_masses_at_level_zero"],
          "TheTwoQuantitiesWereConfused")

    # (6) refusal controls
    refuse("an allocation that closes at 0.99", lambda: check(
        3 * SHARE + Fr(0) == 1, "TheHundredthAllocationDoesNotClose"))
    refuse("the binary64 parts claimed to be exact", lambda: check(
        Fr(float(SHARE)) * 3 + Fr(float(RESERVE)) == 1,
        "TheHundredthsWereExpectedToBeInexactInBinary64"))
    refuse("a reserve expected to buy a level it cannot pay for", lambda: check(
        join_cost(40, (1, 1)) <= exact_steps(1000)[1], "TheReserveDoesNotPayForThatLevel"))

    elapsed = time.time() - started
    evidence = {
        "schema": "adva.research.traversal-allocation-and-reserve-evidence.v0",
        "status": "ExternalExactPass" if all(row["refused"] for row in refusals) else "Failed",
        "authority": "research-only, external exact arithmetic and a local sha256 chain, no native admission",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_direction_protocol": OBJ["the_direction_protocol"],
        "the_three_sides": OBJ["the_three_sides"],
        "allocation": {
            "shares": [str(SHARE)] * 3,
            "reserve": str(RESERVE),
            "closes_in_hundredths": True,
            "the_naive_binary64_closure_test_passes": float_total == 1.0,
            "the_binary64_parts_are_exact": False,
            "binary64": closed_in_floats},
        "steps": step_table,
        "reserve_critical_level": critical,
        "traversal": {"chain": chain, "successes": successes, "failures": failures,
                      "rollback_leaves_the_head_unchanged": True},
        "reserve_carve": carve,
        "level_map": level_map,
        "quantities_kept_apart": separation,
        "refusals": refusals,
        "findings": [
            "the direction's allocation closes exactly in hundredths, 33+33+33+1 = 100, and in binary64 the ordinary closure test passes while the parts are not exact: the defect is negative, the route over-allocates, and a naive test cannot see it",
            "the inexactness becomes visible only at the step level, and there it starves the reserve rather than the sides: rounding each part falls below the declared one percent at small budgets, because the reserve is the smallest share and is the one rounding eats, while the exact rule never dips below it",
            "the reserve buys joins, so whether one hundredth is enough is a question about the declared join cost: under a constant cost it is a bounded toll, and under a cost that grows with the level it bounds how deep the traversal goes, which is the critical point and not a proof of optimality",
            "the join is a real sha256 link of the retained lineage form, so a failed join is shown to leave the chain head and the resolved level unchanged, and the chain reproduces exactly",
            "the level at which the traversal stops under a doubling join cost is computed twice, once by walking the chain and once from the reserve, and the two agree",
            "a failure is free only while the reserve belongs to no side: carved out before the sides start it is untouched by a failure, and carved out of a side's share the failed attempt costs that side exactly the failed join's cost in steps",
            "the first version of the carve comparison added a step count to a fraction and the exact rational arithmetic did not notice, because Fraction is dimensionless; the section now works in steps and declares its unit, so exactness is not the same as dimension correctness",
            "the budget shares and the probability masses are different quantities and are kept apart: the shares fill one as work, the masses halve per level as resolved space, and the run measures the map between them rather than identifying them"],
        "non_claims": [
            "no claim of optimality for the allocation: the direction left that to be argued and this run computes the reserve's critical level instead",
            "no claim about the value of Omega, its computability, or the three-computation system; the level accounting uses the retained wrapper family's layer masses and nothing more",
            "no retained lineage record, anchor, credential or key is read as authority or rewritten; the chain here is this run's own and a byte link is evidence of consistency rather than authority",
            "the triadic policy fixes three input-domain assignments and forbids reading them as three independent computers, so treating the three sides as budget holders is recorded as a tension rather than adopted",
            "the join cost is declared rather than measured, so the critical level follows from the model and not from machine work"],
        "counts": {"assertions": ASSERTIONS["n"], "cost_models": len(critical),
                   "traversal_levels": len(chain), "step_budgets": len(step_table),
                   "wall_seconds_before_serialization": round(elapsed, 4)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    print("allocation (binary64):", json.dumps(evidence["allocation"]["binary64"], ensure_ascii=False))
    for row in critical:
        paid = ("unbounded" if row["unbounded"]
                else "level %d" % row["largest_level_the_reserve_pays"])
        print("  reserve under %-28s pays to %s" % (row["cost_model"], paid))
    print("traversal:", [(row["level"], row.get("joined")) for row in chain])
    print("carve:", json.dumps(carve, ensure_ascii=False)[:260])


if __name__ == "__main__":
    main()
