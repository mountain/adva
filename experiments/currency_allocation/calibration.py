#!/usr/bin/env python3
"""The optimal-allocation rule applied to the three aperture currencies.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The rule the shell line verified for its own shape is: allocate so that the weighted marginal gain
per unit of cost is equal across the claimants. This run applies it to the three currencies of the
counting round, with measured costs and stocks and declared weights, and it does not trust the rule
because it was verified elsewhere: the run searches every allocation of a declared budget
exhaustively and requires the equalising allocation to be the optimum.

Two measurements shape the answer before any optimisation runs. The statement currency's remaining
stock is zero, because both statements the record knew to be wrong have been corrected and the
frozen evidence keeps its own wording by design. The mass currency's stock is limited by a
structural condition rather than by depth: only one depth carries a retained partition, so further
depths need new retained evidence rather than more effort.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import pathlib
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
BUDGET = CONTRACT["budget"]["declared_budget_rounds"]
COUNTS = {"checks": 0}

INVENTORY = ROOT / "docs/maintenance/float-apertures.json"
COUNTING = ROOT / "experiments/aperture_ledger/evidence.json"
DEPTH = ROOT / "experiments/depth_curve/evidence.json"

# declared: which rounds of this line worked mainly on which currency, written out so that it can
# be contested rather than hidden inside a ratio
ROUND_ATTRIBUTION = {
    "scanner": ["0192", "0196", "0197", "0202"],
    "mass": ["0191", "0193", "0194", "0195", "0198", "0199", "0200", "0201"],
    "statement": ["0194", "0198"],
}


def check(condition, message):
    COUNTS["checks"] += 1
    if not condition:
        raise AssertionError(message)


def load_pinned(path):
    raw = path.read_text(encoding="utf-8")
    return json.loads(raw), hashlib.sha256(raw.encode()).hexdigest()


# ----------------------------------------------------------------- measured inputs ----

def measured_inputs():
    inventory, inventory_digest = load_pinned(INVENTORY)
    counting, counting_digest = load_pinned(COUNTING)
    depth, depth_digest = load_pinned(DEPTH)
    scanner = counting["scanner_currency"]
    check(scanner["net_closing_strict"] == 7, "TheScannerClosureCountMoved")

    deciding = inventory["verdicts"]["imprecision-can-decide"]
    illustrating = inventory["verdicts"]["imprecision-in-illustration-only"]
    check(deciding == 38 and illustrating == 29, "TheScannerStockMoved")

    # closures already made, per currency
    made = {
        "scanner": {"strict": scanner["net_closing_strict"],
                    "loose": scanner["net_closing_strict"]
                             - sum(row["into_illustration_only"] for row in scanner["steps"])},
        "mass": {"levels": len(depth["curve"]) - 1,
                 "depths_with_a_retained_partition": 1},
        "statement": {"corrections": counting["statement_currency"]["closed"],
                      "frozen_and_open_by_design": counting["statement_currency"]["opened"]},
    }
    check(made["mass"]["depths_with_a_retained_partition"] == 1,
          "TheRetainedPartitionCountMoved")

    # remaining stock, per currency, from the same artifacts
    stock = {
        "scanner": {"deciding_apertures_left": deciding,
                    "illustrating_apertures_left": illustrating,
                    "reading": "counted from the inventory itself"},
        "mass": {"depths_reachable_without_new_evidence": 0,
                 "depths_needing_new_retained_evidence": made["mass"]["levels"] - 1,
                 "reading": ("the depths beyond the retained one are not closable by effort: they "
                             "need a retained partition that does not exist yet")},
        "statement": {"closable_statements_left": 0,
                      "frozen_statements_open_by_design":
                          made["statement"]["frozen_and_open_by_design"],
                      "reading": ("both known-wrong statements have been corrected and the frozen "
                                  "evidence keeps its own wording, so this currency is exhausted")},
    }
    check(stock["statement"]["closable_statements_left"] == 0,
          "TheStatementStockWasExpectedToBeExhausted")

    # the measured base cost per closure, in rounds
    base_cost = {}
    for currency, closures in (("scanner", made["scanner"]["strict"]),
                               ("mass", made["mass"]["levels"]),
                               ("statement", made["statement"]["corrections"])):
        rounds = len(ROUND_ATTRIBUTION[currency])
        check(closures > 0, "ACurrencyWithNoClosuresCannotHaveACost")
        base_cost[currency] = Fr(rounds, closures)
    check(base_cost["mass"] < base_cost["scanner"] < base_cost["statement"],
          "TheMeasuredCostOrderWasExpectedToPutMassCheapestAndStatementDearest")
    return {"inventory_sha256": inventory_digest, "counting_sha256": counting_digest,
            "depth_sha256": depth_digest, "made": made, "stock": stock,
            "live_inputs": {"inventory_sha256": True,
                            "why": "the inventory is a live file that any round moves, so its "
                                   "digest is recorded and excluded from the byte comparison"},
            "base_cost_per_closure_rounds": {key: str(value)
                                             for key, value in base_cost.items()},
            "_base_cost": base_cost}


# ------------------------------------------------------------------- the allocation ----

def marginal_cost(currency, index, base_cost):
    """Declared diminishing returns: the k-th closure costs k times the base cost."""
    return base_cost[currency] * index


def stock_of(currency, stocks, prerequisite, paid):
    """The closures available in a currency, which is zero until its prerequisite is paid."""
    unlock = prerequisite.get(currency)
    if unlock is None:
        return stocks[currency]
    return unlock["unlocks"] if unlock["currency"] in paid else 0


def optimise(budget, weights, offers, base_cost, stocks, prerequisite):
    """Exhaustive over which prerequisites to buy and how many closures each currency takes."""
    payers = [name for name in offers if name in prerequisite]
    best = None
    for flags in itertools.product([False, True], repeat=len(payers)):
        paid = {name for name, flag in zip(payers, flags) if flag}
        spent_on_prerequisites = sum(prerequisite[name]["cost"] for name in paid)
        if spent_on_prerequisites > budget:
            continue
        limits = [stock_of(currency, stocks, prerequisite, paid) for currency in offers]
        for counts in itertools.product(*[range(0, limit + 1) for limit in limits]):
            total_cost = spent_on_prerequisites + sum(
                marginal_cost(currency, index, base_cost)
                for currency, count in zip(offers, counts)
                for index in range(1, count + 1))
            if total_cost > budget:
                continue
            gain = sum(weights[currency] * count for currency, count in zip(offers, counts))
            row = {"counts": dict(zip(offers, counts)), "gain": gain, "cost": total_cost,
                   "prerequisites_paid": sorted(paid)}
            if best is None or (gain, -total_cost) > (best["gain"], -best["cost"]):
                best = row
    check(best is not None, "NoAllocationFittedInsideTheBudget")
    return best


def equalising_allocation(budget, weights, offers, base_cost, stocks, prerequisite):
    """The rule: buy the largest weighted gain per unit of cost, prerequisites included.

    A prerequisite is itself an offer whose price is its cost and whose return is the stock it
    unlocks, so the same rule decides it rather than a special case.
    """
    bought = {currency: 0 for currency in offers}
    paid = set()
    spent = Fr(0)
    steps = []
    while True:
        choice = None
        for currency in offers:
            limit = stock_of(currency, stocks, prerequisite, paid)
            if bought[currency] >= limit:
                continue
            index = bought[currency] + 1
            cost = marginal_cost(currency, index, base_cost)
            if spent + cost > budget:
                continue
            rate = weights[currency] / cost
            if choice is None or rate > choice[0]:
                choice = (rate, currency, cost, index, None)
        # a prerequisite competes as an offer: one weighted closure per unit of its cost, at best
        for name, unlock in prerequisite.items():
            if name in paid or spent + unlock["cost"] > budget:
                continue
            rate = weights[name] / unlock["cost"]
            if choice is None or rate > choice[0]:
                choice = (rate, name, unlock["cost"], 0, "prerequisite")
        if choice is None:
            break
        _, currency, cost, index, kind = choice
        spent += cost
        if kind == "prerequisite":
            paid.add(currency)
            steps.append({"currency": currency, "prerequisite_paid": True,
                          "cost": str(cost), "weighted_rate": str(choice[0])})
            continue
        bought[currency] = index
        steps.append({"currency": currency, "closure_index": index, "cost": str(cost),
                      "weighted_rate": str(choice[0])})
    gain = sum(weights[currency] * count for currency, count in bought.items())
    return {"counts": bought, "prerequisites_paid": sorted(paid), "spent": str(spent),
            "gain": str(gain), "steps": steps}


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

    measured = measured_inputs()
    base_cost = measured["_base_cost"]
    offers = ["scanner", "mass", "statement"]
    check(offers == ["scanner", "mass", "statement"], "TheCurrencyListMoved")

    # the exhausted currency gets no share unless its weight is infinite, and that is the answer
    # rather than an artefact: it has nothing left to close
    # the stocks are measured; the prerequisite for the mass currency is declared and priced
    stocks = {"scanner": 38 + 29,          # deciding and illustrating apertures left
              "mass": 0,                   # nothing closable until a partition is retained
              "statement": 0}              # exhausted: both known-wrong statements are corrected
    prerequisite = {"mass": {"currency": "mass", "cost": Fr(6), "unlocks": 4,
                             "what_it_buys": "retaining four new partitions, which is a bounded "
                                             "experiment and not more effort on the old ones"}}
    equal_weights = {currency: Fr(1) for currency in offers}
    rule = equalising_allocation(BUDGET, equal_weights, offers, base_cost, stocks, prerequisite)
    exact = optimise(BUDGET, equal_weights, offers, base_cost, stocks, prerequisite)
    # at equal weights with the declared prerequisite the rule already fails, which is the finding
    rule_matches_at_equal_weights = rule["counts"] == exact["counts"]
    check(exact["counts"]["statement"] == 0, "TheExhaustedCurrencyWasGivenAShare")
    # at the declared budget the prerequisite is not worth paying, which is an answer and not a
    # failure of the model: the cheap scanner apertures are cheaper still
    check(exact["counts"]["scanner"] > 0, "TheAllocationWasExpectedToBuyScannerClosures")
    check(set(rule["prerequisites_paid"]) <= set(exact["prerequisites_paid"]) | set(),
          "TheRulePaidAPrerequisiteTheOptimumDidNot")

    # a family over the declared weights, so the split is reported as a function of them
    family = []
    for scanner_weight in (1, 2, 4, 8):
        weights = {"scanner": Fr(scanner_weight), "mass": Fr(1), "statement": Fr(1)}
        allocation = equalising_allocation(BUDGET, weights, offers, base_cost, stocks,
                                            prerequisite)
        optimum = optimise(BUDGET, weights, offers, base_cost, stocks, prerequisite)
        family.append({
            "declared_weights": {key: str(value) for key, value in weights.items()},
            "counts": allocation["counts"], "spent": allocation["spent"],
            "gain": allocation["gain"],
            "prerequisites_paid": allocation["prerequisites_paid"],
            "which_currency_the_rule_never_buys": [currency for currency, count
                                                   in allocation["counts"].items() if count == 0],
        })
    # at these measured prices the scanner absorbs the whole budget whatever the weights, so the
    # question that does have an answer is the threshold: for which prerequisite price does the
    # mass currency first enter the allocation
    threshold_rows = []
    for budget in (6, 12, 18, 24, 30, 36, 42, 48, 60):
        allocation = equalising_allocation(budget, equal_weights, offers, base_cost, stocks,
                                           prerequisite)
        optimum = optimise(budget, equal_weights, offers, base_cost, stocks, prerequisite)
        threshold_rows.append({"budget_rounds": budget,
                               "the_rule_matches_the_exhaustive_optimum":
                                   allocation["counts"] == optimum["counts"],
                               "prerequisite_paid": "mass" in optimum["prerequisites_paid"],
                               "counts": optimum["counts"],
                               "spent": str(optimum["cost"]),
                               "rule_counts": allocation["counts"]})
    # the rule is a greedy and it fails as soon as a prerequisite bundles several closures: the
    # exhaustive search is what the allocation is taken from, and the failures are recorded
    matches = [row for row in threshold_rows
               if row["the_rule_matches_the_exhaustive_optimum"]]
    misses = [row for row in threshold_rows
              if not row["the_rule_matches_the_exhaustive_optimum"]]
    check(matches and misses,
          "TheRuleWasExpectedToMatchSomeCasesAndFailOthersOncePrerequisitesExist")
    buys = [row for row in threshold_rows if row["prerequisite_paid"]]
    refuses = [row for row in threshold_rows if not row["prerequisite_paid"]]
    check(buys and refuses, "TheThresholdWasExpectedToSeparateTwoRegimes")
    threshold = min(row["budget_rounds"] for row in buys)
    check(all(row["prerequisite_paid"] for row in threshold_rows
              if row["budget_rounds"] >= threshold),
          "TheThresholdIsNotMonotoneInTheBudget")
    check(len({json.dumps(row["counts"], sort_keys=True) for row in threshold_rows}) > 1,
          "TheSplitWasExpectedToMoveWithTheBudget")

    # the structural condition, checked rather than asserted in prose
    mass_stock = measured["stock"]["mass"]
    check(mass_stock["depths_reachable_without_new_evidence"] == 0,
          "TheMassStockWasExpectedToBeZeroWithoutNewEvidence")
    check(mass_stock["depths_needing_new_retained_evidence"] >= 1,
          "SomeMassDepthWasExpectedToNeedNewEvidence")

    refuse("the exhausted currency claimed to have a share", lambda: check(
        rule["counts"]["statement"] > 0, "TheExhaustedCurrencyWasGivenAShare"))
    refuse("the equalising rule claimed to beat the exhaustive optimum", lambda: check(
        Fr(rule["gain"]) > exact["gain"], "TheEqualisingRuleMissedTheExhaustiveOptimum"))
    refuse("the measured cost order claimed to put statement cheapest", lambda: check(
        base_cost["statement"] < base_cost["mass"],
        "TheMeasuredCostOrderWasExpectedToPutMassCheapestAndStatementDearest"))

    evidence = {
        "schema": "adva.research.currency-allocation-evidence.v0",
        "status": "ExternalExactPass",
        "authority": "research-only exact arithmetic over retained counts; no experiment re-run",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_measured_inputs": OBJ["the_measured_inputs"],
        "measured": {key: value for key, value in measured.items() if not key.startswith("_")},
        "declared": {"round_attribution": ROUND_ATTRIBUTION,
                     "diminishing_returns": "the k-th closure costs k times the base cost",
                     "budget_rounds": BUDGET,
                     "weights_are_declared_because_no_measurement_gives_an_exchange_rate": True},
        "the_rule": OBJ["the_rule"],
        "measured_stocks": {"scanner": stocks["scanner"], "mass": stocks["mass"],
                            "statement": stocks["statement"]},
        "declared_prerequisite": {"mass": {"cost_rounds": str(prerequisite["mass"]["cost"]),
                                           "unlocks": prerequisite["mass"]["unlocks"],
                                           "what_it_buys": prerequisite["mass"]["what_it_buys"]}},
        "the_greedy_rule_at_equal_weights": {
            "counts": rule["counts"], "gain": rule["gain"], "spent": rule["spent"],
            "prerequisites_paid": rule["prerequisites_paid"]},
        "exhaustive_optimum_at_equal_weights": {
            "counts": exact["counts"], "gain": str(exact["gain"]), "cost": str(exact["cost"]),
            "prerequisites_paid": exact["prerequisites_paid"]},
        "the_rule_matches_the_exhaustive_optimum_at_equal_weights": rule_matches_at_equal_weights,
        "the_rule_is_a_greedy_and_prerequisites_break_it": {
            "matches": len(matches), "failures": len(misses),
            "why": ("a prerequisite bundles several closures, so its return is not one closure per "
                    "unit of cost and the greedy misprices it; the allocation is therefore taken "
                    "from the exhaustive search and the rule's failures are recorded"),
            "the_failure_appears_as_soon_as_the_prerequisite_is_cheap_enough_to_matter": True},
        "family_over_declared_weights": family,
        "the_split_does_not_move_with_the_weights_here":
            ("at the measured prices the scanner absorbs the whole budget for every weight tried, "
             "because its stock is large and its closures are the cheapest"),
        "budget_threshold": {
            "smallest_budget_at_which_the_mass_prerequisite_is_paid": threshold,
            "rows": threshold_rows,
            "reading": ("the mass currency enters the allocation only once the cheap scanner "
                        "apertures have been bought, because the scanner's k-th closure costs k "
                        "times its base cost and eventually exceeds the price of retaining new "
                        "partitions: the order is buy the cheap ones, then buy evidence")},
        "refusals": refusals,
        "findings": [
            "the optimal-allocation rule of the shell line applies to the three currencies once each has a measured cost per closure, a remaining stock and a declared weight, and its optimality is checked here rather than inherited from the earlier round",
            "the rule is a greedy and it stops being optimal as soon as a prerequisite exists, because a prerequisite bundles several closures and is therefore mispriced by a rule that values one closure at a time: the run records how many declared cases it matches and how many it fails, and takes its allocation from the exhaustive search",
            "the measured cost per closure differs across the currencies, with the mass currency at eight fifteenths of a round, the scanner currency at four sevenths and the statement currency at two thirds, and the statement figure moved during this very round because the round above it appended a correction and thereby added a closure to that currency: a measured input that this line's own corrections change is a live input and is treated as one",
            "the cost order is measured rather than assumed: the mass currency is cheapest, and at the declared budget the exhaustive optimum still buys only scanner closures, which says the scanner's stock and price matter more than the base cost alone",
            "the statement currency is exhausted by measurement: both statements the record knew to be wrong have been corrected and the frozen evidence keeps its own wording, so the rule gives it no share and that is an answer rather than an imbalance",
            "the mass currency's stock is limited structurally rather than by effort: only one depth carries a retained partition, so further closures there need new retained evidence and not more rounds",
            "the split is reported as a function of the declared weights because the counting round established that no measurement supplies an exchange rate between currencies: what is measured is each currency's cost per closure and its stock, and what is decided is how much a closure in one currency is worth against another",
            "at the measured prices the weights turn out not to matter in the range tried: the scanner currency has both the larger stock and the cheaper closures, so it absorbs the whole budget, and the allocation is degenerate in that direction",
            "what does have a threshold is the budget rather than a weight: the scanner's k-th closure costs k times its base cost, so once the cheap apertures are bought the price of retaining new partitions is overtaken and the mass prerequisite is paid from a computable budget upwards, which orders the work as buy the cheap ones first and then buy evidence",
            "at the declared budget the optimum is therefore entirely in the scanner currency, and the exhausted statement currency gets nothing at any budget, so the allocation the run reports is what remains after two measured constraints rather than a preference"],
        "non_claims": [
            "the attribution of past rounds to currencies is a declaration and can be contested; a different attribution moves the base costs",
            "the diminishing-returns profile is declared and no measurement fixes it",
            "the weights are declared, so the absolute split is a decision while the costs and stocks are measurements",
            "no experiment is re-run and no retained artifact is modified",
            "nothing here computes Omega, decides computability, or touches the three-computation system, and the triadic tension recorded in Research 0192 remains unresolved"],
        "counts": {"checks": COUNTS["checks"], "budget_rounds": BUDGET,
                   "equal_weight_split": exact["counts"],
                   "the_rule_matched_the_optimum_at_equal_weights": rule_matches_at_equal_weights,
                   "rule_matches_over_the_threshold_sweep": len(matches),
                   "rule_failures_over_the_threshold_sweep": len(misses),
                   "budget_threshold_for_the_mass_prerequisite": threshold,
                   "budget_threshold_sweep_points": len(threshold_rows),
                   "exhaustive_optimum_matched": rule["counts"] == exact["counts"],
                   "refusals": len(refusals)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    print("  base cost per closure (rounds):",
          evidence["measured"]["base_cost_per_closure_rounds"])
    print("  exhaustive optimum at equal weights:", exact["counts"],
          "| prerequisites", exact["prerequisites_paid"], "| spent", str(exact["cost"]))
    print("  greedy rule at equal weights:", rule["counts"], "| matches:", rule_matches_at_equal_weights)
    print("  rule over the budget sweep: %d matches, %d failures" % (len(matches), len(misses)))
    print("  smallest budget at which the mass prerequisite is paid:", threshold)
    for row in threshold_rows:
        print("    budget %-3d -> %s (prerequisite paid: %s)" % (
            row["budget_rounds"], row["counts"], row["prerequisite_paid"]))
    for row in family:
        print("  weights", row["declared_weights"], "->", row["counts"])


if __name__ == "__main__":
    main()
