"""Fixed-depth ablation: exact cycles versus cycles plus protected stack growth."""
import argparse
import copy
from dataclasses import asdict
from fractions import Fraction
import json
from pathlib import Path
import resource
import time

from common import (HERE, Budget, Limit, C, M, O, GROW, LOOP, IDENTITY, K,
                    READ_ALIAS, app, canonical, manifest)
import growth as G


def weight(code):
    return Fraction(1, 2 ** len(code))


def fixture_controls(budget, check):
    fuel = 128
    selector = app(app(READ_ALIAS, GROW), IDENTITY)
    cases = {
        "growing_stack": (GROW, "GrowthCandidate"),
        "protected_reader_bottom": (app(GROW, "0"), "GrowthCandidate"),
        "delayed_growth": (app(IDENTITY, GROW), "GrowthCandidate"),
        "selector_pending": (selector, "NeedInput"),
        "selector_zero": (selector + "0", "GrowthCandidate"),
        "selector_one": (selector + "1", "Halt"),
        "discard_growth": (app(app(K, IDENTITY), GROW), "Halt"),
        "returned_lambda_hides_growth": (app(K, GROW), "Halt"),
    }
    rows = {}
    for name, (code, expected) in cases.items():
        proposal = G.propose(code, fuel, budget)
        check(proposal["status"] == expected, "fixture status: " + name)
        if expected == "GrowthCandidate":
            check(G.check(proposal["certificate"], code, fuel, budget), "growth receiver: " + name)
            check(C.propose(code, fuel, budget)["status"] == "UnknownFuel",
                  "exact recurrence must miss growing fixture: " + name)
        elif expected == "Halt":
            reference = O.run(code, budget)
            check(reference["status"] == "Halt", "named oracle return: " + name)
        rows[name] = {"source": code, "source_bits": len(code), "outcome": proposal}
    receipt = rows["growing_stack"]["outcome"]["certificate"]
    negatives = []
    changes = {
        "source": lambda r: r.update(source=LOOP),
        "profile": lambda r: r.update(profile="full-normalization"),
        "cost": lambda r: r.update(cost_convention="free-replay"),
        "boolean_entry": lambda r: r.update(pump_entry=True),
        "boolean_fuel": lambda r: r.update(search_fuel=True),
        "empty_segment": lambda r: r.update(pump_entry=len(r["actions"])),
        "changed_control": lambda r: r["frames"][-1].update(control=["r"]),
        "changed_stack": lambda r: r["frames"][-1]["stack"].append(["r"]),
        "float_cursor": lambda r: r["frames"][0].update(cursor=float(len(GROW))),
        "changed_action": lambda r: r["actions"].__setitem__(0, "Read"),
    }
    for name, change in changes.items():
        wrong = copy.deepcopy(receipt)
        change(wrong)
        check(not G.check(wrong, GROW, fuel, budget), "negative receipt: " + name)
        negatives.append({"case": name, "refused": True})
    for name, source, allowance in (("receiving_source", GROW + "1", fuel),
                                    ("receiving_allowance", GROW, fuel - 1)):
        check(not G.check(receipt, source, allowance, budget), name)
        negatives.append({"case": name, "refused": True})
    cycle = C.propose(LOOP, fuel, budget)["certificate"]
    cycle["schema"] = G.SCHEMA
    cycle["pump_entry"] = cycle.pop("cycle_entry")
    check(not G.check(cycle, LOOP, fuel, budget), "zero-growth exact cycle")
    negatives.append({"case": "zero_growth", "refused": True})
    # A true execution that satisfies repeated control and growing endpoint,
    # but pops the proposed protected bottom before rebuilding it.
    state = M.State.start(GROW, fuel, budget)
    frames, actions = [asdict(state.frame())], []
    counts = {"execution_steps": 0, "read_steps": 0}
    for _ in range(4):
        actions.append(C.microstep(state, budget, counts))
        frames.append(asdict(state.frame()))
    wrong = json.loads(canonical({**receipt, "frames": frames, "actions": actions,
                                  "pump_entry": 1}))
    a, b = frames[1], frames[-1]
    check(a["control"] == b["control"] and b["stack"][:len(a["stack"])] == a["stack"]
          and len(b["stack"]) > len(a["stack"]), "naive endpoint criterion really passes")
    check(not G.check(wrong, GROW, fuel, budget), "consumed bottom must be refused")
    negatives.append({"case": "genuine_trace_consumes_and_rebuilds_bottom", "refused": True,
                      "certificate": wrong})
    wrong = copy.deepcopy(rows["selector_zero"]["outcome"]["certificate"])
    wrong["pump_entry"] = 0
    check(not G.check(wrong, selector + "0", fuel, budget), "read in pumping segment")
    negatives.append({"case": "read_in_segment", "refused": True})
    check(weight(selector + "0") + weight(selector + "1") == weight(selector),
          "selector input cylinders preserve weight")
    # Direct continuation observations preserve original fuel and input position.
    extensions = []
    for suffix in ("", "0", "1", "00", "01", "10", "11"):
        row = M.row(M.advance(M.State.start(GROW + suffix, fuel, budget), M.Engine(budget)))
        check(row["status"] == "UnknownFuel" and row["cursor"] == len(GROW)
              and row["reads"] == [] and row["steps"] == fuel, "suffix-independent finite run")
        extensions.append(row)
    return {"fixtures": rows, "negative_receipts": negatives,
            "finite_extension_controls": extensions,
            "selector_conditional": {"halting": "1/2", "certified_growth": "1/2",
                                     "unresolved": "0", "program_bits": len(selector),
                                     "global_growth_mass": str(weight(selector + "0"))}}


def measure(depth, fuel, budget, check):
    started = time.monotonic()
    engine = M.Engine(budget)
    search = M.prefix_search(depth, fuel, engine)
    search_time = time.monotonic() - started
    accepted = sorted(search["accepted"], key=lambda r: r["code"])
    started = time.monotonic()
    for row in accepted:
        reference = O.run(row["code"], budget)
        check(reference["status"] == row["status"] == "Halt", "accepted oracle status")
        check(reference["cursor"] == row["cursor"], "accepted oracle cursor")
        check(reference["reads"] == [r[1:] for r in row["reads"]], "accepted ordered reads")
        check(reference["whnf"] == row["whnf"], "accepted oracle value")
    oracle_time = time.monotonic() - started
    cycles, growth, unresolved = [], [], {}
    runtime_unknowns = 0
    started = time.monotonic()
    for frontier in search["frontiers"]:
        budget.tick()
        code = frontier["source"]
        if frontier["status"] == "UnknownFuel":
            runtime_unknowns += 1
            proposal = C.propose(code, fuel, budget)
            if proposal["status"] == "CycleCandidate":
                check(C.check(proposal["certificate"], code, fuel, budget), "exact-cycle receiver")
                cycles.append(proposal["certificate"])
                continue
            proposal = G.propose(code, fuel, budget)
            if proposal["status"] == "GrowthCandidate":
                check(G.check(proposal["certificate"], code, fuel, budget), "growth receiver")
                growth.append(proposal["certificate"])
                continue
        unresolved.setdefault(frontier["status"], []).append(code)
    certification_time = time.monotonic() - started
    accepted_codes = [row["code"] for row in accepted]
    cycle_codes = [row["source"] for row in cycles]
    growth_codes = [row["source"] for row in growth]
    remaining_codes = [code for group in unresolved.values() for code in group]
    all_codes = sorted(accepted_codes + cycle_codes + growth_codes + remaining_codes)
    for a, b in zip(all_codes, all_codes[1:]):
        check(not b.startswith(a), "disjoint terminal antichain")
    halt = sum(map(weight, accepted_codes), Fraction())
    exact = sum(map(weight, cycle_codes), Fraction())
    added = sum(map(weight, growth_codes), Fraction())
    pending = sum(map(weight, remaining_codes), Fraction())
    check(halt + exact + added + pending == 1, "four-part Kraft partition")
    baseline_pending = pending + added
    check(1 - exact - halt == baseline_pending, "cycle-only ablation partition")
    check(baseline_pending - pending == added, "additional exclusion equals new cylinder weight")
    if depth == 15:
        check(halt == Fraction(13039, 16384) and exact == Fraction(1, 32768)
              and baseline_pending == Fraction(6689, 32768), "previous depth-15 partition")
    return {
        "depth": depth, "fuel": fuel, "prefix_nodes": search["visited"],
        "runtime_unknown_frontiers_before_certificates": runtime_unknowns,
        "counts": {"accepted": len(accepted_codes), "cycles": len(cycles),
                   "additional_growth": len(growth), "unresolved": len(remaining_codes)},
        "cycle_only": {"accepted": str(halt), "certified_nonhalting": str(exact),
                       "unresolved": str(baseline_pending), "upper": str(1 - exact)},
        "cycle_plus_growth": {"accepted": str(halt), "certified_nonhalting": str(exact + added),
                              "unresolved": str(pending), "upper": str(1 - exact - added)},
        "additional_excluded_mass": str(added),
        "accepted_codes": accepted_codes, "cycle_certificates": cycles,
        "growth_certificates": growth,
        "unresolved_by_status": {k: sorted(v) for k, v in sorted(unresolved.items())},
        "unresolved_mass_by_status": {k: str(sum(map(weight, v), Fraction()))
                                      for k, v in sorted(unresolved.items())},
        "execution_dispatches": engine.counts,
        "timings": {"prefix_seconds": search_time, "oracle_seconds": oracle_time,
                    "certificate_seconds": certification_time},
    }


def run(preflight=False):
    contract = json.loads((HERE / "contract.json").read_text())
    limits = dict(contract["limits"])
    if preflight:
        limits["max_host_work"] = limits["preflight_host_work"]
        limits["wall_seconds"] = limits["preflight_wall_seconds"]
    budget = Budget(limits)
    evidence = {"schema": "adva.external.keraia-growth-mass.evidence.v0", "status": "Running",
                "source_sha256": manifest(), "failures": [], "cuts": [],
                "preflight_only": preflight, "native_status": "NotRun"}
    assertions = 0

    def check(ok, message):
        nonlocal assertions
        assertions += 1
        budget.tick()
        if not ok:
            raise AssertionError(message)
    try:
        evidence["controls"] = fixture_controls(budget, check)
        if not preflight:
            for depth in contract["family"]["prefix_depths"]:
                evidence["cuts"].append(measure(depth, contract["family"]["semantic_fuel"], budget, check))
        check(evidence["source_sha256"] == manifest(), "sources unchanged during run")
        evidence["status"] = "Passed"
    except (Limit, MemoryError, RecursionError) as error:
        evidence["status"] = "UnknownResource"
        evidence["failures"].append({"type": type(error).__name__, "message": str(error)})
    except Exception as error:
        evidence["status"] = "InvalidEvidence"
        evidence["failures"].append({"type": type(error).__name__, "message": str(error)})
    evidence["assertions"] = assertions
    evidence["cost"] = {"host_work": budget.work, "elapsed_seconds": time.monotonic() - budget.start,
                        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    return evidence


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--preflight", action="store_true")
    args = parser.parse_args()
    result = run(args.preflight)
    encoded = canonical(result) + "\n"
    if len(encoded.encode()) > 16777216:
        raise SystemExit("UnknownResource: output limit")
    with args.output.open("x") as stream:
        stream.write(encoded)
    print(canonical({"status": result["status"], "assertions": result["assertions"],
                     "failures": result["failures"], "cost": result["cost"],
                     "cuts": [{k: c[k] for k in ("depth", "counts", "cycle_only",
                                                "cycle_plus_growth", "additional_excluded_mass")}
                              for c in result["cuts"]]}))
    raise SystemExit(0 if result["status"] == "Passed" else 1)
