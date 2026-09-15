#!/usr/bin/env python3
"""Two gain curves on one cost axis, and what the measurement does not decide.

Frozen contract: contract.json in this directory (Research 0129 section 3).

Research 0198 recorded a ledger and a sentence: that the cost per unit of resolved mass falls while
the absolute cost rises. The ledger's own margins say the opposite, rising from twelve to millions
of steps per unit, so this run recomputes them rather than remembering the sentence, and the
correction goes to the note while the frozen evidence keeps its wording.

On the same cost axis the run then puts both gains: the wrapper family's increment, 2^-(k+1) per
level, and the Keraia family's acceptance increment, the mass of the accepted cylinders of exactly
that length. The shapes differ, the best layer under each objective differs, and the bridge converts
units between the spaces at a constant two without converting value. So the measurement gives two
curves and a unit ratio; it does not decide when deepening should stop, because that needs an
objective and the record contains two.
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
LEDGER = ROOT / "experiments/protocol_mass_ledger/evidence.json"
CURVE = ROOT / "experiments/depth_curve/evidence.json"
BRIDGE = ROOT / "experiments/declared_bridge/evidence.json"
SHARED_LEVELS = CONTRACT["budget"]["shared_levels"]
COUNTS = {"checks": 0}


def check(condition, message):
    COUNTS["checks"] += 1
    if not condition:
        raise AssertionError(message)


def load_pinned(path):
    check(path.exists(), "TheRetainedEvidenceIsMissing: %s" % path.name)
    raw = path.read_bytes()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


# ------------------------------------------------------------------ the recomputation ----

def recompute_margins(ledger):
    """The margins from the ledger's own level table, and whether the record's sentence agrees."""
    levels = {row["level"]: row for row in ledger["levels"]}
    rows = []
    for level in range(1, SHARED_LEVELS + 1):
        before, after = levels[level - 1], levels[level]
        gain = Fr(after["resolved_mass"]) - Fr(before["resolved_mass"])
        side = after["side_depth_cost_steps"] - before["side_depth_cost_steps"]
        reserve = after["cumulative_reserve_steps"] - before["cumulative_reserve_steps"]
        rows.append({"level": level, "wrapper_gain": str(gain), "side_spent": side,
                     "reserve_spent": reserve,
                     "side_steps_per_unit_gain": Fr(side, 1) / gain,
                     "reserve_steps_per_unit_gain": Fr(reserve, 1) / gain})
    values = [row["side_steps_per_unit_gain"] for row in rows]
    rising = all(later > earlier for earlier, later in zip(values, values[1:]))
    check(rising, "TheMarginalCostWasExpectedToRise")
    recorded_says_falls = any("per unit of resolved mass falls" in text
                              for text in ledger["findings"])
    check(recorded_says_falls,
          "TheFrozenFindingWasExpectedToContainTheSentenceThisRunCorrects")
    return rows, {"first": str(values[0]), "last": str(values[-1]),
                  "strictly_rising": rising,
                  "the_frozen_finding_says_it_falls": recorded_says_falls,
                  "reading": ("the record's sentence and its own numbers point in opposite "
                              "directions; the numbers are recomputed here and the sentence is "
                              "corrected in the note while the frozen evidence keeps its wording")}


# --------------------------------------------------------------------- the two gains ----

def accepted_by_length(curve):
    """The accepted mass of the cylinders of exactly each length, from the depth curve."""
    rows = {row["depth"]: Fr(row["accepted_mass_decided_so_far"]) for row in curve["curve"]}
    deepest = max(rows)
    gains = {}
    for depth in range(1, deepest + 1):
        gains[depth] = rows[depth] - rows[depth - 1]
    check(all(gain >= 0 for gain in gains.values()), "AnAcceptanceIncrementWasNegative")
    check(sum(gains.values(), Fr(0)) == rows[deepest],
          "TheAcceptanceIncrementsDoNotSumToTheAcceptedMass")
    return gains


def link_cost(level):
    measured = 533 + len(str(level)) - 1
    return -(-8 * measured // 533)


def the_two_curves(margins, acceptance):
    rows = []
    for margin in margins:
        level = margin["level"]
        cost = margin["side_spent"] + margin["reserve_spent"]
        wrapper_gain = Fr(margin["wrapper_gain"])
        keraia_gain = acceptance.get(level, Fr(0))
        rows.append({
            "level": level,
            "cost_steps": cost,
            "wrapper_gain": str(wrapper_gain),
            "wrapper_gain_per_step": str(wrapper_gain / cost),
            "keraia_acceptance_gain": str(keraia_gain),
            "keraia_gain_per_step": str(keraia_gain / cost),
        })
    wrapper_sequence = [Fr(row["wrapper_gain_per_step"]) for row in rows]
    check(all(later < earlier for earlier, later in zip(wrapper_sequence, wrapper_sequence[1:])),
          "TheWrapperGainPerStepWasExpectedToFall")
    keraia_sequence = [Fr(row["keraia_gain_per_step"]) for row in rows]
    monotone = (all(later <= earlier for earlier, later in zip(keraia_sequence, keraia_sequence[1:]))
                or all(later >= earlier for earlier, later in zip(keraia_sequence,
                                                                 keraia_sequence[1:])))
    check(not monotone, "TheKeraiaGainPerStepWasExpectedNotToBeMonotone")
    best_keraia = max(rows, key=lambda row: (Fr(row["keraia_gain_per_step"]), -row["level"]))
    worst_keraia = min(rows, key=lambda row: (Fr(row["keraia_gain_per_step"]), row["level"]))
    # the two orderings over the later layers, counted exactly rather than described
    concordant = discordant = 0
    for first in range(len(rows)):
        for second in range(first + 1, len(rows)):
            wrapper_order = wrapper_sequence[first] - wrapper_sequence[second]
            keraia_order = keraia_sequence[first] - keraia_sequence[second]
            if wrapper_order == 0 or keraia_order == 0:
                continue
            if (wrapper_order > 0) == (keraia_order > 0):
                concordant += 1
            else:
                discordant += 1
    check(concordant + discordant > 0, "NoComparablePairs")
    return rows, {"wrapper": {"shape": "strictly falling",
                              "best_layer": rows[0]["level"],
                              "why": "the wrapper increment halves per level while the cost grows"},
                  "keraia": {"shape": "not monotone",
                             "best_layer": best_keraia["level"],
                             "best_gain_per_step": best_keraia["keraia_gain_per_step"],
                             "worst_layer": worst_keraia["level"],
                             "worst_gain_per_step": worst_keraia["keraia_gain_per_step"]},
                  "orderings": {"concordant_pairs": concordant, "discordant_pairs": discordant,
                                "the_two_orderings_differ": discordant > 0,
                                "reading": ("both objectives put their best layer first, which the "
                                            "run expected to differ and did not, so the "
                                            "disagreement is in how they order the later layers")}}


def the_exchange(bridge):
    constant = bridge["counts"]["bridge_constant_keraia_atoms_per_wrapper_tail"]
    check(constant == "1/2", "TheBridgeConstantMoved")
    return {
        "unit_conversion": "one Keraia unit is two wrapper units, verified at every declared depth",
        "unit_conversion_is_measured": True,
        "value_exchange_is_measured": False,
        "why_not": ("converting units says how the two spaces' masses compare, not which of them "
                    "the traversal is for; the two objectives below give different best layers, and "
                    "nothing in the measurements chooses between them"),
        "the_objective_must_be_declared": True,
        "the_two_objectives_in_the_record": {
            "wrapper_resolution": "named by the protocol declaration of Research 0197, whose reserve rule maximises the resolved mass",
            "keraia_acceptance": "the quantity the retained family's partition reports",
        },
        "the_criterion_is_not_free": ("the level at which deepening stops paying depends on which "
                                      "objective is declared, so the stopping rule is a decision "
                                      "and not a measurement"),
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

    ledger, ledger_digest = load_pinned(LEDGER)
    curve, curve_digest = load_pinned(CURVE)
    bridge, bridge_digest = load_pinned(BRIDGE)
    margins, recomputation = recompute_margins(ledger)
    acceptance = accepted_by_length(curve)
    rows, shapes = the_two_curves(margins, acceptance)
    exchange = the_exchange(bridge)
    # the expectation was that the two objectives would disagree at the best layer; they do not,
    # and the disagreement is in the ordering beyond it, which is measured rather than assumed
    check(shapes["wrapper"]["best_layer"] == shapes["keraia"]["best_layer"] == 1,
          "BothObjectivesWereExpectedToPutTheirBestLayerFirst")
    check(shapes["orderings"]["discordant_pairs"] > 0,
          "TheTwoOrderingsWereExpectedToDifferSomewhere")

    refuse("the marginal cost claimed to fall", lambda: check(
        Fr(recomputation["last"]) < Fr(recomputation["first"]), "TheMarginalCostWasExpectedToRise"))
    refuse("the wrapper gain per step claimed to rise", lambda: check(
        Fr(rows[-1]["wrapper_gain_per_step"]) > Fr(rows[0]["wrapper_gain_per_step"]),
        "TheWrapperGainPerStepWasExpectedToFall"))
    refuse("a value exchange claimed to be measured", lambda: check(
        exchange["value_exchange_is_measured"] is True, "TheBridgeConstantMoved"))

    evidence = {
        "schema": "adva.research.marginal-exchange-evidence.v0",
        "status": "ExternalExactPass",
        "authority": "research-only exact arithmetic over retained evidence; no semantics re-run",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_recomputation": OBJ["the_recomputation"],
        "inputs": {"ledger": {"path": str(LEDGER.relative_to(ROOT)), "sha256": ledger_digest},
                   "curve": {"path": str(CURVE.relative_to(ROOT)), "sha256": curve_digest},
                   "bridge": {"path": str(BRIDGE.relative_to(ROOT)), "sha256": bridge_digest},
                   "all_read_only": True},
        "marginal_cost": recomputation,
        "margins": [{"level": row["level"], "wrapper_gain": row["wrapper_gain"],
                     "side_spent": row["side_spent"], "reserve_spent": row["reserve_spent"],
                     "side_steps_per_unit_gain": str(row["side_steps_per_unit_gain"])}
                    for row in margins],
        "two_curves": rows,
        "shapes": shapes,
        "the_exchange": exchange,
        "refusals": refusals,
        "findings": [
            "the record contains a sentence whose direction its own numbers refute: the ledger's marginal cost per unit of resolved mass rises from twelve steps to millions, while the frozen finding says it falls, and the numbers are recomputed here rather than remembered",
            "the correction goes to the note and not to the evidence: the frozen record keeps its wording, which is the point of freezing it, and the recomputation is what carries the corrected direction",
            "on the shared cost axis the wrapper gain per step falls strictly, because its increment halves while the cost grows, so under that objective the best layer is the first one",
            "the Keraia acceptance per step is not monotone, so under that objective a best and a worst layer exist and are named",
            "the two objectives both put their best layer first, which the run expected to differ and did not: the disagreement is not about where each one peaks but about how they order the later layers, which is counted exactly rather than described",
            "the bridge converts units between the spaces and not value, so the measurements give two curves and a unit ratio while the question of when deepening stops paying needs a declared objective, which the record happens to contain two of"],
        "non_claims": [
            "no semantics are re-run: both gain curves rest on retained outcomes, so a mistake there would propagate and is not detectable from inside",
            "the two objectives compared are the ones the record contains; others are not considered, and neither is claimed to be the right one",
            "the cost axis passes through a declared conversion from measured bytes to layer steps, and the key half is unmeasured",
            "the Keraia side covers the depths the retained evidence reaches, and the wrapper side the levels the ledger covers",
            "nothing here computes Omega, decides computability, or touches the three-computation system, and the triadic tension recorded in Research 0192 remains unresolved"],
        "counts": {"checks": COUNTS["checks"], "levels": len(rows),
                   "marginal_cost_first": recomputation["first"],
                   "marginal_cost_last": recomputation["last"],
                   "best_layer_wrapper": shapes["wrapper"]["best_layer"],
                   "best_layer_keraia": shapes["keraia"]["best_layer"],
                   "concordant_pairs": shapes["orderings"]["concordant_pairs"],
                   "discordant_pairs": shapes["orderings"]["discordant_pairs"],
                   "refusals": len(refusals)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    print("  marginal cost per unit gain:", recomputation["first"], "->", recomputation["last"],
          "| rising:", recomputation["strictly_rising"])
    for row in rows[:8]:
        print("    k=%-2d cost %-3d wrapper/step %-14s keraia/step %s" % (
            row["level"], row["cost_steps"], row["wrapper_gain_per_step"],
            row["keraia_gain_per_step"]))


if __name__ == "__main__":
    main()
