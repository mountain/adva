"""One frozen finite calibration; no automatic correction or search expansion."""
import argparse
import copy
from dataclasses import replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import resource
import time

import machine as M
import oracle as O
from syntax import Budget, I, R, Limit, beta, compile_tree, split_code

HERE = Path(__file__).resolve().parent


def words(n):
    for size in range(n + 1):
        for value in range(2**size):
            yield format(value, "0" + str(size) + "b") if size else ""


def dyadic(prefix):
    return Fraction(1, 2**len(prefix))


def ratio(value):
    return [value.numerator, value.denominator]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def run():
    contract = json.loads((HERE / "contract.json").read_text())
    budget = Budget(contract["limits"])
    evidence = {"status": "Running", "profile": M.PROFILE, "checks": [], "cuts": [], "failures": [],
                "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                  for p in sorted(HERE.glob("*.py")) + [HERE / "contract.json"]}}
    assertions = 0
    def check(ok, label):
        nonlocal assertions
        budget.tick()
        assertions += 1
        if not ok:
            raise AssertionError(label)
    def passed(label):
        evidence["checks"].append(label)
    try:
        maximum = contract["family"]["all_binary_strings_through_length"]
        family = list(words(maximum))
        descriptions = sorted({w[:end] for w in family if (end := split_code(w, budget)) is not None})
        for program in descriptions:
            check(compile_tree(program, budget) == O.debruijn(O.compile_string(program, budget), budget),
                  "compiler disagreement: " + program)
        evidence["descriptions_checked"] = len(descriptions)
        passed("independent tree and string-marking compilers agree on the complete description family")
        oracle_rows = {}
        for w in family:
            oracle_rows[w] = O.run(w, budget)
        evidence["oracle_digest"] = digest(oracle_rows)
        last_rows = None
        for fuel in contract["family"]["time_cuts"]:
            direct, cached, prefix = [M.Engine(budget, reuse=x) for x in (False, True, False)]
            start = time.monotonic()
            rows = [M.row(M.advance(M.State.start(w, fuel, budget), direct)) for w in family]
            direct_seconds = time.monotonic() - start
            start = time.monotonic()
            reused = [M.row(M.advance(M.State.start(w, fuel, budget), cached)) for w in family]
            cached_seconds = time.monotonic() - start
            check(rows == reused, "cached ledger at fuel " + str(fuel))
            accepted = sorted((r for r in rows if r["status"] == "Halt"), key=lambda r: r["code"])
            start = time.monotonic()
            search = M.prefix_search(maximum, fuel, prefix)
            prefix_seconds = time.monotonic() - start
            check(sorted(search["accepted"], key=lambda r: r["code"]) == accepted,
                  "prefix traversal ledger at fuel " + str(fuel))
            codes = [r["code"] for r in accepted]
            frontier_codes = [f["source"] for f in search["frontiers"]]
            antichain = sorted(codes + frontier_codes)
            check(all(not b.startswith(a) for a, b in zip(antichain, antichain[1:])), "prefix-cylinder antichain")
            lower = sum(map(dyadic, codes), Fraction(0))
            masses = {}
            for state in search["frontiers"]:
                masses[state["status"]] = masses.get(state["status"], Fraction(0)) + dyadic(state["source"])
            check(lower + sum(masses.values(), Fraction(0)) == 1, "exact Kraft partition")
            status_counts = {}
            for r in rows:
                status_counts[r["status"]] = status_counts.get(r["status"], 0) + 1
                check(r["steps"] + r["fuel_left"] == fuel, "original fuel conservation")
                if fuel == contract["limits"]["max_semantic_steps"]:
                    oracle = oracle_rows[r["code"]]
                    check(r["status"] == oracle["status"], "oracle status: " + r["code"])
                    check(r["cursor"] == oracle["cursor"], "oracle cursor: " + r["code"])
                    check([x[1:] for x in r["reads"]] == oracle["reads"], "oracle read sequence: " + r["code"])
                    check(r.get("whnf") == oracle.get("whnf"), "oracle weak head: " + r["code"])
            evidence["cuts"].append({"fuel": fuel, "codes": len(rows), "status_counts": status_counts,
                                     "accepted_codes": codes, "halting_mass": ratio(lower),
                                     "unresolved_mass": {k: ratio(v) for k, v in masses.items()},
                                     "prefix_nodes_visited": search["visited"], "frontier_count": len(frontier_codes),
                                     "direct": direct.counts, "checked_cache": cached.counts,
                                     "cache_entries": len(cached.cache), "prefix_search": prefix.counts,
                                     "ledger_digest": digest(rows),
                                     "timing": {"direct_seconds": direct_seconds, "cache_seconds": cached_seconds,
                                                "prefix_seconds": prefix_seconds}})
            last_rows = rows
            if fuel == contract["limits"]["max_semantic_steps"]:
                evidence["ledger"] = rows
                evidence["resumable_frontiers"] = search["frontiers"]
        passed("all three fuel cuts preserve direct/cache/prefix ledgers, input order and original fuel")
        passed("accepted codes and unresolved cylinders form exact Kraft partitions")
        passed("independent named-substitution oracle agrees on every full-budget code")

        identity = "11000"
        k_appendix = "11010100110010100"
        k_printed = "110" + "0" + "110" + "10100" + "0"
        omega_abstraction = "1100100"
        omega = "1" + omega_abstraction + omega_abstraction
        one_read = "11101001010011000"
        fixtures = {"I": identity, "K_appendix": k_appendix, "K_printed_section8": k_printed,
                    "omega": omega, "K_I_omega": "11" + k_appendix + identity + omega,
                    "K_appendix_I_R": "11" + k_appendix + identity + "0",
                    "K_printed_I_R": "11" + k_printed + identity + "0"}
        for p in (one_read, "100"):
            for suffix in ("", "0", "1", "10"):
                fixtures[p + ":" + suffix] = p + suffix
        evidence["fixtures"] = {}
        engine = M.Engine(budget, reuse=True)
        for name, code in fixtures.items():
            end = split_code(code, budget)
            check(compile_tree(code[:end], budget) == O.debruijn(O.compile_string(code[:end], budget), budget), "fixture compiler: " + name)
            actual = M.row(M.advance(M.State.start(code, 128, budget), engine))
            reference = O.run(code, budget)
            check(actual["status"] == reference["status"], "fixture status: " + name)
            check(actual["cursor"] == reference["cursor"] and [x[1:] for x in actual["reads"]] == reference["reads"], "fixture reads: " + name)
            check(actual.get("whnf") == reference.get("whnf"), "fixture WHNF: " + name)
            evidence["fixtures"][name] = actual
        check(evidence["fixtures"]["I"]["whnf"] == I, "identity meaning")
        check(evidence["fixtures"]["K_appendix_I_R"]["whnf"] == I, "Appendix K meaning")
        check(evidence["fixtures"]["omega"]["status"] == "UnknownFuel", "loop must not become a negative halting proof")
        check(evidence["fixtures"]["K_I_omega"]["whnf"] == I, "call by name does not force discarded divergence")
        check(evidence["fixtures"][one_read + ":1"]["whnf"] == I, "paper one-read example")
        evidence["source_comparison"] = {
            "printed_section8_K": k_printed, "appendix_B_K": k_appendix,
            "same_compiled_term": compile_tree(k_printed, budget) == compile_tree(k_appendix, budget),
            "same_on_I_R": evidence["fixtures"]["K_printed_I_R"].get("whnf") == evidence["fixtures"]["K_appendix_I_R"].get("whnf"),
            "interpretation": "Compare literal encodings under the declared Appendix-B marking profile; do not silently correct the printed example or infer universality."}
        passed("fixed examples agree with the independent oracle; the printed/source encoding comparison is retained")

        # Open terms distinguish capture avoidance from simple textual replacement.
        check(beta(("l", ("v", 1)), ("v", 0), budget) == ("l", ("v", 1)), "de Bruijn capture avoidance")
        named = O.substitute_named(("lambda", "y", ("var", "x")), "x", ("var", "y"), budget)
        check(named[1] != "y" and named[2] == ("var", "y"), "named capture avoidance")
        passed("both substitution implementations preserve the free variable in the capture control")

        paused = M.advance(M.State.start(one_read, 128, budget), engine)
        check(paused.status == "NeedInput", "expected a read frontier")
        raw = json.dumps(paused.record(), sort_keys=True)
        evidence["checkpoint"] = json.loads(raw)
        restored = M.restore_checkpoint(raw, one_read, 128, engine)
        restored.append_bit("1", budget)
        M.advance(restored, engine)
        check(M.row(restored) == evidence["fixtures"][one_read + ":1"], "resumption equals uninterrupted run")
        check(json.dumps(paused.record(), sort_keys=True) == raw,
              "paused parent was not mutated")
        changed = copy.deepcopy(paused.record())
        changed["stack"].clear()
        check(paused.stack != [], "exported record has independent stack ownership")
        refused = []
        for name in ("cursor", "fuel_left", "steps", "control", "reads", "profile"):
            record = json.loads(raw)
            if name in ("cursor", "fuel_left", "steps"):
                record[name] += 1
            elif name == "control":
                record[name] = ["l", ["v", 0]]
            elif name == "reads":
                record[name].append([1, 0, "1"])
            else:
                record[name] = "different-semantics"
            try:
                M.restore_checkpoint(json.dumps(record), one_read, 128, engine)
            except ValueError:
                refused.append(name)
        check(len(refused) == 6, "all changed checkpoints rejected")
        try:
            M.restore_checkpoint(raw, one_read + "0", 128, engine)
        except ValueError:
            refused.append("receiver_source")
        check(len(refused) == 7, "receiver-selected source binding")
        evidence["checkpoint_refusals"] = refused
        passed("event checkpoint replay, one-bit continuation and caller ownership preserve the original state and fuel")

        initial = M.State.start(one_read, 128, budget).frame()
        receipt = engine.segment(initial, 128)
        mutated = [replace(receipt, start=replace(initial, profile="other")),
                   replace(receipt, start=replace(initial, cursor=initial.cursor + 1)),
                   replace(receipt, steps=receipt.steps - 1),
                   replace(receipt, end=replace(receipt.end, control=I)),
                   replace(receipt, end=replace(receipt.end, cursor=receipt.end.cursor + 1))]
        check(all(not M.check_receipt(r, initial, budget, engine.counts) for r in mutated), "altered segment refused")
        whole = evidence["fixtures"][one_read + ":1"]
        below = M.advance(M.State.start(one_read + "1", whole["steps"] - 1, budget), engine)
        check(below.status == "UnknownFuel", "warm cache cannot bypass original cost")
        evidence["segment_example"] = {"receipt": M.asdict(receipt), "mutations_refused": len(mutated),
                                       "just_below_cost": M.row(below)}
        passed("segment receiver binds profile, cursor, cost and endpoint; cache cannot provide free semantic fuel")
        by_code = {r["code"]: r for r in last_rows}
        check(by_code["1001"]["whnf"] == by_code[identity]["whnf"] == I, "equal-output mass control")
        class_mass = dyadic("1001") + dyadic(identity)
        check(class_mass == Fraction(3, 32) and class_mass != dyadic("1001"), "representative loses source-code mass")
        evidence["mass_control"] = {"codes": ["1001", identity], "total": ratio(class_mass),
                                    "incorrect_representative_only": ratio(dyadic("1001"))}
        passed("equal output does not erase either source code's probability weight")
        evidence["status"] = "Passed"
    except (Limit, MemoryError, RecursionError) as err:
        evidence["status"] = "UnknownResource"
        evidence["failures"].append({"type": type(err).__name__, "message": str(err)})
    except Exception as err:
        evidence["status"] = "InvalidEvidence"
        evidence["failures"].append({"type": type(err).__name__, "message": str(err)})
    evidence["assertions"] = assertions
    evidence["cost"] = {"host_work": budget.work, "elapsed_seconds": time.monotonic() - budget.start,
                        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    return evidence


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = run()
    encoded = json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n"
    if len(encoded.encode()) > 16777216:
        raise SystemExit("UnknownResource: output size")
    with args.output.open("x") as f:
        f.write(encoded)
    print(json.dumps({k: result[k] for k in ("status", "assertions", "checks", "failures", "cost")}))
    raise SystemExit(0 if result["status"] == "Passed" else 1)
