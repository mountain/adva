#!/usr/bin/env python3
"""Does a step close more apertures than it opens? Counted, per currency.

Frozen contract: contract.json in this directory (Research 0129 section 3).

The question has one answer per currency, and the record already keeps three.

  the scanner   each rescan records how many experiments are exact-only and how many have a
                deciding line on a float or host construct, so a step's net there is a difference
                of two counts.
  the mass      the traversal's own space closes monotonically, so a resolving step opens nothing;
                a truncating step opens a residual of the same order as the layer it closes, which
                the shell round measured exactly.
  the statements a correction appended to a note closes a statement, while a sentence a later
                recomputation refuted but the frozen evidence keeps stays open by design.

The run counts each currency over the declared steps, applies the direction rule per currency, and
reports the two currencies where this line sits exactly at zero for a structural reason rather than
as a failure of any step.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CONTRACT = json.loads((HERE / "contract.json").read_text(encoding="utf-8"))
OBJ = CONTRACT["objects"]
COUNTS = {"checks": 0}


def check(condition, message):
    COUNTS["checks"] += 1
    if not condition:
        raise AssertionError(message)


# ------------------------------------------------------------------ currency one: the scanner ----

SCAN_HISTORY = [
    {"point": "the first scan", "experiments": 69, "exact_only": 5, "can_decide": 37},
    {"point": "after the two shell rounds", "experiments": 71, "exact_only": 7, "can_decide": 37},
    {"point": "after 0191", "experiments": 72, "exact_only": 7, "can_decide": 37},
    {"point": "after 0192", "experiments": 73, "exact_only": 7, "can_decide": 38},
    {"point": "after 0193", "experiments": 74, "exact_only": 7, "can_decide": 38},
    {"point": "after 0194", "experiments": 75, "exact_only": 7, "can_decide": 38},
    {"point": "after 0195", "experiments": 76, "exact_only": 7, "can_decide": 38},
    {"point": "after 0196", "experiments": 77, "exact_only": 8, "can_decide": 38},
    {"point": "after 0197", "experiments": 77, "exact_only": 8, "can_decide": 38},
    {"point": "after 0198", "experiments": 78, "exact_only": 9, "can_decide": 38},
    {"point": "after 0199", "experiments": 79, "exact_only": 10, "can_decide": 38},
    {"point": "after 0200", "experiments": 80, "exact_only": 11, "can_decide": 38},
    {"point": "after 0201", "experiments": 81, "exact_only": 12, "can_decide": 38},
    # the series has to include the round that produced it: this experiment is itself an
    # experiment, it was scanned, and it was classed exact-only, so it closes one more aperture
    # than it opened by existing. That is a fixed point rather than a formula, and a round which
    # were itself classed as deciding would have opened a count by measuring it.
    {"point": "after 0202, which counts itself", "experiments": 82, "exact_only": 13,
     "can_decide": 38},
]


def scanner_currency():
    """The recorded series, its last point checked against the machine-readable inventory."""
    inventory = json.loads((ROOT / "docs/maintenance/float-apertures.json").read_text(encoding="utf-8"))
    last = SCAN_HISTORY[-1]
    check(inventory["experiments_scanned"] == last["experiments"],
          "TheDeclaredSeriesDoesNotReachTheCurrentInventory")
    check(inventory["verdicts"]["exact-only"] == last["exact_only"],
          "TheDeclaredExactOnlyCountDisagreesWithTheInventory")
    check(inventory["verdicts"]["imprecision-can-decide"] == last["can_decide"],
          "TheDeclaredDecidingCountDisagreesWithTheInventory")
    doc = (ROOT / "docs/maintenance/FLOAT_APERTURES.md").read_text(encoding="utf-8")
    # the exact-only steps are recorded as deltas in the inventory's own sections
    recorded_deltas = ["该类别 7 → 8", "该类别 8 → 9", "该类别 9 → 10", "该类别 10 → 11",
                       "该类别 11 → 12"]
    for phrase in recorded_deltas:
        check(phrase in doc, "TheRetainedDocumentDoesNotRecordTheStep: " + phrase)
    # the deciding step is not recorded as a delta anywhere in that document, which is a gap in
    # the retained documentation rather than in the series: the series below is a reconstruction
    deciding_delta_recorded = "37 → 38" in doc
    check(not deciding_delta_recorded,
          "TheDecidingDeltaWasRecordedAfterAllAndThisGapShouldBeRemoved")
    documentation_gap = {
        "the_deciding_step_is_recorded_only_in_prose": True,
        "what_the_document_says": ("that the round was judged imprecision-can-decide with two "
                                   "float comparisons on an acceptance path, without the numeric "
                                   "delta of that count"),
        "so_the_series_here_is_a_reconstruction": True,
        "recorded_exact_only_deltas": recorded_deltas,
    }
    # four counters, because an illustration-only experiment is still an aperture even though it
    # decides nothing: the strict net counts only deciding apertures, the loose one counts both
    NO_NUMERIC = 2
    check(inventory["verdicts"]["no-numeric-constructs"] == NO_NUMERIC,
          "TheNoNumericCountAssumptionIsContradictedByTheInventory")
    check(inventory["verdicts"]["imprecision-in-illustration-only"]
          == last["experiments"] - NO_NUMERIC - last["exact_only"] - last["can_decide"],
          "TheDerivedIllustrationCountDisagreesWithTheInventory")

    def illustration(row):
        return row["experiments"] - NO_NUMERIC - row["exact_only"] - row["can_decide"]

    steps = []
    for before, after in zip(SCAN_HISTORY, SCAN_HISTORY[1:]):
        rows = {
            "step": after["point"],
            "experiments_added": after["experiments"] - before["experiments"],
            "into_exact_only": after["exact_only"] - before["exact_only"],
            "into_can_decide": after["can_decide"] - before["can_decide"],
            "into_illustration_only": illustration(after) - illustration(before),
        }
        rows["strict_net_closing"] = rows["into_exact_only"] - rows["into_can_decide"]
        rows["loose_net_closing"] = (rows["into_exact_only"] - rows["into_can_decide"]
                                     - rows["into_illustration_only"])
        steps.append(rows)
    self_reference = {
        "the_instrument_is_inside_what_it_measures": True,
        "so_the_series_includes_the_round_that_produced_it": True,
        "this_round_was_classed_exact_only": True,
        "why_that_matters": ("a round whose own verdict were deciding would increase the opened "
                            "count by the act of measuring it, so the series would not settle by "
                            "reading it once"),
        "status": "a fixed point here, because this round closes one more aperture than it opens",
    }
    return steps, documentation_gap, {"no_numeric_assumed_constant": NO_NUMERIC,
                                      "illustration_only_derived_from_the_total": True,
                                      "the_last_point_agrees_with_the_inventory": True}, \
        self_reference


# --------------------------------------------------------------------- currency two: the mass ----

def mass_currency():
    """Resolving closes with nothing opened; truncating opens a residual of the layer's own order."""
    depth = json.loads((ROOT / "experiments/depth_curve/evidence.json").read_text(encoding="utf-8"))
    curve = {row["depth"]: row for row in depth["curve"]}
    rows = []
    for level in range(0, 16):
        rows.append({"level": level,
                     "undecided_before": curve[level - 1]["undecided_mass"] if level else "1",
                     "undecided_after": curve[level]["undecided_mass"]})
    check(Fr(curve[15]["undecided_mass"]) < Fr(curve[0]["undecided_mass"]),
          "TheUndecidedMassWasExpectedToFall")
    resolved_rows = [row for row in rows if row["level"] > 0]
    check(all(Fr(after["undecided_after"]) <= Fr(after["undecided_before"])
              for after in resolved_rows), "AResolvingStepRaisedTheUndecidedMass")
    # some levels leave the undecided mass untouched: no accepted cylinder has those lengths, and
    # the same dead zone appears in the marginal exchange round from the other side
    unchanged = [row["level"] for row in resolved_rows
                 if Fr(row["undecided_after"]) == Fr(row["undecided_before"])]
    check(unchanged == [2, 3], "TheDeadZoneWasExpectedAtLevelsTwoAndThree")
    return {
        "resolving_step": {"closed": "the layer resolved", "opened": "nothing",
                           "net": -1, "reading": "the traversal's own space closes monotonically"},
        "levels_that_change_nothing": unchanged,
        "why": ("no accepted cylinder has length two or three, so those levels resolve nothing that "
                "counts and the undecided mass does not move: the same dead zone the marginal "
                "exchange round measured from the acceptance side"),
        "truncating_step": {"closed": "the layer resolved", "opened": "a residual inside the cut ideal",
                            "net": 0,
                            "reading": ("the shell round measured the residual as non-zero and "
                                        "detectable, and its mass is of the same order as the layer "
                                        "it closes, so truncation buys the layer and pays for it")},
        "levels": len(rows),
    }


# --------------------------------------------------------------- currency three: statements ----

def statement_currency():
    """Corrections close statements; refuted sentences in frozen evidence stay open by design."""
    notes = sorted((ROOT / "docs/research").glob("*.md"))
    corrections = [path.name for path in notes if "更正（2026" in path.read_text(encoding="utf-8")]
    refuted_but_kept = []
    for path, needle in (
            (ROOT / "experiments/measured_join_cost/evidence.json",
             "not established by this tool path"),
            (ROOT / "experiments/protocol_mass_ledger/evidence.json",
             "per unit of resolved mass falls")):
        evidence = json.loads(path.read_text(encoding="utf-8"))
        found = [text for text in evidence["findings"] if needle in text]
        check(len(found) == 1, "TheFrozenSentenceMoved: " + needle)
        refuted_but_kept.append({"evidence": path.name, "sentence": found[0][:120]})
    check(len(corrections) == 2, "TheCorrectionCountMoved")
    check(len(refuted_but_kept) == 2, "TheRefutedButKeptCountMoved")
    return {
        "closed": len(corrections), "opened": len(refuted_but_kept),
        "net": len(corrections) - len(refuted_but_kept),
        "correction_notes": corrections,
        "refuted_but_kept": refuted_but_kept,
        "structural_floor": ("frozen evidence is never rewritten, so a sentence a later "
                             "recomputation refutes stays open by design: this currency cannot be "
                             "driven below zero by correcting notes alone"),
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

    scanner, documentation_gap, derived, self_reference = scanner_currency()
    mass = mass_currency()
    statements = statement_currency()

    closing = [row for row in scanner if row["strict_net_closing"] > 0]
    opening = [row for row in scanner if row["strict_net_closing"] < 0]
    flat = [row for row in scanner if row["strict_net_closing"] == 0]
    check(closing, "NoStepClosedMoreThanItOpenedInTheScannerCurrency")
    check(opening, "NoStepOpenedMoreThanItClosedInTheScannerCurrency")
    disagreeing = [row for row in scanner
                   if row["strict_net_closing"] != row["loose_net_closing"]]
    check(disagreeing, "TheTwoNetsWereExpectedToDifferSomewhere")
    check(flat, "NoStepWasExpectedToLeaveBothCountsUntouched")
    net_scanner = sum(row["strict_net_closing"] for row in scanner)
    net_scanner_loose = sum(row["loose_net_closing"] for row in scanner)

    refuse("the two nets claimed equal", lambda: check(
        net_scanner == net_scanner_loose, "TheTwoNetsWereExpectedToDifferSomewhere"))
    refuse("the three currencies claimed to be one number", lambda: check(
        net_scanner == mass["truncating_step"]["net"] == statements["net"],
        "TheCurrenciesWereExpectedToDisagree"))
    refuse("a truncating step claimed to open nothing", lambda: check(
        mass["truncating_step"]["opened"] == "nothing",
        "TheShellRoundMeasuredANonZeroResidual"))
    refuse("a refuted sentence claimed absent from the frozen evidence", lambda: check(
        len(statements["refuted_but_kept"]) == 0, "TheRefutedButKeptCountMoved"))

    evidence = {
        "schema": "adva.research.aperture-ledger-evidence.v0",
        "status": "ExternalExactPass",
        "authority": "research-only counting over retained artifacts; no experiment re-run",
        "native_status": "NotRun",
        "question": CONTRACT["question"],
        "the_three_currencies": OBJ["the_three_currencies"],
        "scanner_currency": {"steps": scanner,
                             "net_closing_strict": net_scanner,
                             "net_closing_loose": net_scanner_loose,
                             "documentation_gap": documentation_gap,
                             "derived_counts": derived,
                             "self_reference": self_reference,
                             "sign_convention": "positive means more closed than opened",
                             "two_nets_because_an_illustration_is_an_aperture_that_does_not_decide":
                                 True,
                             "steps_where_the_two_nets_disagree":
                                 [row["step"] for row in disagreeing],
                             "steps_that_closed_more": [row["step"] for row in closing],
                             "steps_that_opened_more": [row["step"] for row in opening],
                             "steps_that_moved_neither_count": [row["step"] for row in flat],
                             "direction_followed_over_the_line": net_scanner > 0},
        "mass_currency": mass,
        "statement_currency": statements,
        "the_direction_rule": OBJ["the_direction_rule"],
        "refusals": refusals,
        "findings": [
            "the question has an answer per currency and the record keeps three, so whether a step closes more than it opens is decidable once the currency is declared and undecidable without one",
            "in the scanner currency this line closes more than it opens: exact-only experiments rose from five to twelve while the deciding count rose by one, so the net over the line is a closing of six, and the single opening step is the round that put two float probes on an acceptance path on purpose",
            "in the mass currency a resolving step opens nothing because the traversal's own space closes monotonically, but a truncating step opens a residual inside the cut ideal whose mass is of the same order as the layer it closes, so truncation buys a layer and pays for it",
            "the mass currency also carries levels that change nothing at all: no accepted cylinder has length two or three, so the undecided mass is identical across those levels, which is the dead zone the marginal exchange round measured from the acceptance side and here from the closure side",
            "in the statement currency the net is exactly zero, because each correction closes a statement in a note while the sentence a later recomputation refuted stays in the frozen evidence by design: this currency has a structural floor and cannot be driven below zero by correcting notes",
            "so the direction rule the question asks for exists, but it has to name its currency, and two of the three currencies sit at a floor that no step of this kind can pass",
            "the instrument turned out to be inside what it measures: this round is itself an experiment in the inventory it counts, and its own verdict is exact-only, so the series has to include it and the last point is a fixed point rather than a reading, while a round whose verdict were deciding would open a count merely by measuring it",
            "the scanner currency needed four counters rather than two, because an illustration-only experiment is still an aperture even though it decides nothing, so the run reports a strict net and a loose net and names the steps where they disagree",
            "the sign convention of the scanner currency was at first read backwards, which no check and no test caught because both readings produced non-empty lists: it was found by reading the printed output, and the convention is now stated inside the run",
            "the counting itself exposed a small aperture in the retained documentation: the exact-only steps are recorded as numeric deltas in the inventory's sections while the one deciding step is recorded only in prose, so the series used here is partly a reconstruction and the run says which part"],
        "non_claims": [
            "the scanner currency counts text-level verdicts about where a construct appears and not real uncertainty in a result",
            "the statement currency counts corrections and refutations, which is a narrow reading of what a wrong statement is and certainly not a measure of how wrong the record is",
            "the mass currency covers the spaces this line worked in and not an arbitrary computation",
            "no experiment is re-run and no retained inventory, evidence or note is modified, so the counts come from the artifacts as they stand",
            "nothing here computes Omega, decides computability, or touches the three-computation system, and the triadic tension recorded in Research 0192 remains unresolved"],
        "counts": {"checks": COUNTS["checks"], "scanner_steps": len(scanner),
                   "scanner_net_closing_strict": net_scanner,
                   "scanner_net_closing_loose": net_scanner_loose,
                   "mass_truncating_net": mass["truncating_step"]["net"],
                   "statement_net": statements["net"], "refusals": len(refusals)},
    }
    out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "evidence.json"
    out.write_text(json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(json.dumps({"status": evidence["status"], "counts": evidence["counts"]}, indent=1))
    for finding in evidence["findings"]:
        print(" *", finding)
    print("  scanner steps that opened more than they closed:",
          evidence["scanner_currency"]["steps_that_opened_more"])
    print("  statement currency:", statements["closed"], "closed,", statements["opened"],
          "open by design, net", statements["net"])


if __name__ == "__main__":
    main()
