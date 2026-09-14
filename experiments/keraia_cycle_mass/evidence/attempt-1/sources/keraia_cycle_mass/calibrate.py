"""One fixed family; resource failures and negative evidence are retained."""
import argparse
import copy
from dataclasses import asdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import resource
import time

from support import HERE, manifest, canonical, digest, words, sequence, app, IDENTITY, K, LOOP, GROW, SELECT_LOOP
import cycles as C
import machine as M
import oracle as O
from syntax import Budget, Limit, I, compile_tree, split_code


def ratio(x):
    return [x.numerator, x.denominator]


def mass(code):
    return Fraction(1, 2**len(code))


def resumed(program, data, fuel, engine):
    state = M.advance(M.State.start(program, fuel, engine.budget), engine)
    for bit in data:
        engine.budget.tick()
        if state.status != "NeedInput":
            break
        state.append_bit(bit, engine.budget)
        M.advance(state, engine)
    # Report against the originally selected whole finite word. Bits not
    # requested by the machine remain unread; they are never executed.
    row = M.row(state)
    row["code"] = program + data
    row["code_weight_exponent"] = len(program + data)
    if row["status"] == "Halt" and row["cursor"] != len(program + data):
        row["status"] = "Overflow"
    return row


def run():
    contract = json.loads((HERE / "contract.json").read_text())
    budget = Budget(contract["limits"])
    evidence = {"status": "Running", "source_sha256": manifest(), "failures": [], "checks": [], "timings": {}}
    assertions = 0
    def check(ok, message):
        nonlocal assertions
        budget.tick()
        assertions += 1
        if not ok:
            raise AssertionError(message)
    def agree(actual, oracle, label):
        check(actual["status"] == oracle["status"], label + " status")
        check(actual["cursor"] == oracle["cursor"], label + " cursor")
        check([r[1:] for r in actual["reads"]] == oracle["reads"], label + " reads")
        check(actual.get("whnf") == oracle.get("whnf"), label + " output")
    try:
        maximum, fuel = contract["family"]["all_binary_strings_through_length"], contract["family"]["exhaustive_fuel"]
        descriptions, accepted, statuses, longest = set(), [], {}, 0
        ledger_digest, oracle_digest = hashlib.sha256(), hashlib.sha256()
        direct = M.Engine(budget)
        started = time.monotonic()
        for code in words(maximum):
            end = split_code(code, budget)
            if end is not None:
                program = code[:end]
                if program not in descriptions:
                    check(compile_tree(program, budget) == O.debruijn(O.compile_string(program, budget), budget), "exhaustive compiler " + program)
                    descriptions.add(program)
            row = M.row(M.advance(M.State.start(code, fuel, budget), direct))
            reference = O.run(code, budget)
            agree(row, reference, "exhaustive " + code)
            ledger_digest.update((canonical(row) + "\n").encode())
            oracle_digest.update((canonical(reference) + "\n").encode())
            statuses[row["status"]] = statuses.get(row["status"], 0) + 1
            if row["status"] == "Halt":
                accepted.append(row)
                longest = max(longest, row["steps"])
        evidence["timings"]["direct_plus_oracle_seconds"] = time.monotonic() - started
        evidence["exhaustive"] = {"codes": sum(statuses.values()), "descriptions": len(descriptions),
                                  "status_counts": statuses, "longest_accepted_steps": longest,
                                  "ledger_digest": ledger_digest.hexdigest(), "oracle_digest": oracle_digest.hexdigest(),
                                  "direct_counts": direct.counts}
        check(sum(statuses.values()) == 65535, "complete fixed family")
        evidence["checks"].append("independent compilers and full-budget outcomes agree on the exhaustive family")

        prefix = M.Engine(budget)
        started = time.monotonic()
        search = M.prefix_search(maximum, fuel, prefix)
        evidence["timings"]["prefix_seconds"] = time.monotonic() - started
        check(sorted(search["accepted"], key=lambda r: r["code"]) == sorted(accepted, key=lambda r: r["code"]), "prefix accepted ledger")
        divergent, remaining = [], []
        for frontier in search["frontiers"]:
            budget.tick()
            if frontier["status"] == "UnknownFuel":
                candidate = C.propose(frontier["source"], fuel, budget)
                if candidate["status"] == "CycleCandidate":
                    check(C.check(candidate["certificate"], frontier["source"], fuel, budget), "cycle receiver")
                    divergent.append(candidate)
                    continue
                frontier["cycle_attempt"] = candidate
            remaining.append(frontier)
        codes = [r["code"] for r in accepted]
        divergence_codes = [r["certificate"]["source"] for r in divergent]
        frontier_codes = [r["source"] for r in remaining]
        antichain = sorted(codes + divergence_codes + frontier_codes)
        check(all(not b.startswith(a) for a, b in zip(antichain, antichain[1:])), "three-part prefix antichain")
        lower = sum(map(mass, codes), Fraction(0))
        nonhalting = sum(map(mass, divergence_codes), Fraction(0))
        unresolved = sum(map(mass, frontier_codes), Fraction(0))
        check(lower + nonhalting + unresolved == 1, "three-part exact Kraft partition")
        check(nonhalting > 0, "nontrivial independently checked excluded mass")
        residual_by_status = {}
        for f in remaining:
            residual_by_status[f["status"]] = residual_by_status.get(f["status"], Fraction(0)) + mass(f["source"])
        evidence["mass_partition"] = {"accepted": ratio(lower), "certified_nonhalting": ratio(nonhalting),
                                      "unresolved": ratio(unresolved), "upper": ratio(1 - nonhalting),
                                      "residual_by_status": {k: ratio(v) for k, v in residual_by_status.items()},
                                      "accepted_codes": len(accepted), "divergent_cylinders": len(divergent),
                                      "unresolved_cylinders": len(remaining), "prefix_nodes": search["visited"],
                                      "prefix_counts": prefix.counts}
        evidence["accepted_ledger"] = sorted(accepted, key=lambda r: r["code"])
        evidence["divergence_certificates"] = divergent
        evidence["unresolved_frontiers"] = remaining
        evidence["checks"].append("checked input-free cycles give a strict upper bound and exact three-part mass partition")

        fixture_rows = []
        fixture_engines = [M.Engine(budget, reuse=x) for x in (False, True, False)]
        for reads in contract["family"]["sequence_read_counts"]:
            for delays in contract["family"]["identity_delay_counts"]:
                program = sequence(reads, delays)
                check(compile_tree(program, budget) == O.debruijn(O.compile_string(program, budget), budget), "sequence compiler")
                full_mass = Fraction(0)
                for data in words(reads + 1):
                    for cut in contract["family"]["fixture_fuel_cuts"]:
                        a = M.row(M.advance(M.State.start(program + data, cut, budget), fixture_engines[0]))
                        b = M.row(M.advance(M.State.start(program + data, cut, budget), fixture_engines[1]))
                        c = resumed(program, data, cut, fixture_engines[2])
                        check(a == b == c, "multi-read original fuel and full ledger")
                        check(a["steps"] + a["fuel_left"] == cut, "fixture fuel conservation")
                        if cut == fuel:
                            agree(a, O.run(program + data, budget), "sequence oracle")
                            expected = "NeedInput" if len(data) < reads else "Halt" if len(data) == reads else "Overflow"
                            check(a["status"] == expected, "requested read count")
                            if len(data) == reads:
                                check(len(a["reads"]) == reads and a["whnf"] == I, "all requested bits read in order")
                                full_mass += mass(program + data)
                        fixture_rows.append({"reads": reads, "delays": delays, "fuel": cut, "row": a})
                check(full_mass == mass(program), "all full data words partition the sequence program cylinder")
        evidence["sequence_fixtures"] = fixture_rows
        evidence["fixture_counts"] = [e.counts for e in fixture_engines]
        check(any(r["row"]["status"] == "UnknownFuel" for r in fixture_rows), "low cuts actually exercise delayed returns")
        evidence["checks"].append("two/three-read sequences with three delay counts preserve direct/cache/resumed ledgers at four fuel cuts")

        diagnostics = {"loop": LOOP, "growing_stack": GROW, "discard_loop": app(app(K, IDENTITY), LOOP),
                       "returned_lambda_hides_loop": app(K, LOOP), "selector_empty": SELECT_LOOP,
                       "selector_zero": SELECT_LOOP + "0", "selector_one": SELECT_LOOP + "1"}
        evidence["diagnostics"] = {}
        for name, code in diagnostics.items():
            row = M.row(M.advance(M.State.start(code, fuel, budget), M.Engine(budget)))
            agree(row, O.run(code, budget), "diagnostic " + name)
            candidate = C.propose(code, fuel, budget)
            if candidate["status"] == "CycleCandidate":
                check(C.check(candidate["certificate"], code, fuel, budget), "diagnostic independent cycle")
            else:
                check(candidate["row"] == row, "one-step proposer agrees with existing segment machine")
            evidence["diagnostics"][name] = {"direct": row, "cycle_search": candidate}
        ds = evidence["diagnostics"]
        check(ds["loop"]["cycle_search"]["status"] == ds["selector_zero"]["cycle_search"]["status"] == "CycleCandidate", "positive cycle controls")
        check(ds["growing_stack"]["cycle_search"]["status"] == "UnknownFuel", "growing stack stays unresolved")
        check(ds["growing_stack"]["cycle_search"]["head_only_repeat"] is not None, "repeated head is not a full-state cycle")
        check(ds["discard_loop"]["direct"]["status"] == ds["returned_lambda_hides_loop"]["direct"]["status"] == "Halt", "discard and weak-head boundaries")
        check(ds["selector_empty"]["direct"]["status"] == "NeedInput" and ds["selector_one"]["direct"]["status"] == "Halt", "one-read branches")
        check(mass(SELECT_LOOP + "0") + mass(SELECT_LOOP + "1") == mass(SELECT_LOOP), "selector exact partition")
        evidence["selector_conditional_mass"] = {"program": SELECT_LOOP, "halting": [1, 2], "nonhalting": [1, 2], "unresolved": [0, 1]}
        evidence["checks"].append("one-read selector has exact conditional halting probability 1/2; head-only, discarded and hidden-loop controls preserve Unknown/return")

        receipt = ds["loop"]["cycle_search"]["certificate"]
        mutations = []
        for name in ("source", "profile", "cost_convention", "bool_index", "negative_index", "end_index", "initial", "control", "stack", "cursor", "float_cursor", "empty_cycle"):
            wrong = copy.deepcopy(receipt)
            if name in ("source", "profile", "cost_convention"):
                wrong[name] += "1"
            elif name == "bool_index": wrong["cycle_entry"] = True
            elif name == "negative_index": wrong["cycle_entry"] = -1
            elif name == "end_index": wrong["cycle_entry"] = len(wrong["actions"])
            elif name == "initial": wrong["frames"][0]["control"] = ["r"]
            elif name == "control": wrong["frames"][-1]["control"] = ["r"]
            elif name == "stack": wrong["frames"][-1]["stack"].append(["r"])
            elif name == "cursor": wrong["frames"][-1]["cursor"] -= 1
            elif name == "float_cursor": wrong["frames"][-1]["cursor"] = float(wrong["frames"][-1]["cursor"])
            else: wrong["frames"] = wrong["frames"][:1]; wrong["actions"] = []; wrong["cycle_entry"] = 0
            check(not C.check(wrong, LOOP, fuel, budget), "refuse " + name)
            mutations.append({"case": name, "refused": True})
        wrong = copy.deepcopy(ds["selector_zero"]["cycle_search"]["certificate"])
        wrong["cycle_entry"] = 0
        check(not C.check(wrong, SELECT_LOOP + "0", fuel, budget), "read cannot be included in exact cycle")
        mutations.append({"case": "false_cycle_through_read", "refused": True})
        wrong = copy.deepcopy(receipt)
        initial = asdict(M.State.start(IDENTITY, fuel, budget).frame())
        wrong.update(source=IDENTITY, cycle_entry=0, frames=json.loads(canonical([initial, initial])), actions=["Pure"])
        check(not C.check(wrong, IDENTITY, fuel, budget), "returning frame does not certify a loop")
        mutations.append({"case": "returning_frame", "refused": True})
        check(not C.check(receipt, LOOP, fuel - 1, budget), "receiver allowance")
        mutations.append({"case": "receiver_allowance", "refused": True})
        evidence["negative_receipts"] = mutations
        evidence["checks"].append("all fifteen altered or invalid cycle claims are refused")
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
    args = parser.parse_args()
    result = run()
    encoded = canonical(result) + "\n"
    if len(encoded.encode()) > 16777216:
        raise SystemExit("UnknownResource: evidence output limit")
    with args.output.open("x") as handle:
        handle.write(encoded)
    print(canonical({k: result[k] for k in ("status", "assertions", "checks", "failures", "cost")}))
    raise SystemExit(0 if result["status"] == "Passed" else 1)
