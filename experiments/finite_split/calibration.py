#!/usr/bin/env python3
"""External finite split calibration. Not a native adva/free implementation."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import resource
import signal
import time

CONTRACT_SHA = "29c2db4ac3e23256a81a050a2466bc566fb735c5648443b16976b9a5c756ebfb"
MAX_BYTES = 262144
D = list(range(-3, 4))


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(encoded(value)).hexdigest()


def integer(value, lower, upper):
    if type(value) is not int or not lower <= value <= upper:
        raise ValueError("strict bounded integer required")
    return value


class Meter:
    def __init__(self):
        self.spent = 0

    def charge(self):
        if self.spent >= 2000:
            raise RuntimeError("global budget exhausted")
        self.spent += 1


class Ledger:
    def __init__(self, meter, work, audit_only=False):
        self.meter, self.work = meter, work
        self.initial = work + 64
        self.spent = {"work": 0, "verification": 0, "serialization": 0}
        self.audit_only = audit_only

    def charge(self, phase):
        if phase == "work" and (self.audit_only or self.spent[phase] >= self.work):
            raise RuntimeError("work fuel exhausted")
        if phase != "work" and self.spent["verification"] + self.spent["serialization"] >= 64:
            raise RuntimeError("reserved audit fuel exhausted")
        self.meter.charge()
        self.spent[phase] += 1

    def snapshot(self):
        return {"initial": self.initial, "work_limit": self.work, "reserve": 64,
                "spent": dict(self.spent), "remaining": self.initial - sum(self.spent.values()),
                "audit_only": self.audit_only}


def question(coefficients, name="polynomial-preservation"):
    return {"schema": "adva.finite-point-preservation.research", "version": 0,
            "display_name": name, "domain": "bounded-exact-Z", "inputs": D.copy(),
            "quantifier": "forall-declared-inputs", "observer": "exact-integer-value",
            "input_map": "identity", "output_map": "identity",
            "source": {"version": "expanded-v0", "coefficients": list(coefficients)},
            "target": {"version": "horner-v0", "coefficients": list(coefficients)}}


def scope(q):
    return digest({k: v for k, v in q.items() if k != "display_name"})


def validate_question(q):
    if set(q) != set(question([2, 3, 1])):
        raise ValueError("question schema mismatch")
    base = question([2, 3, 1])
    for key in ("schema", "version", "domain", "quantifier", "observer", "input_map", "output_map"):
        if q[key] != base[key] or type(q[key]) is not type(base[key]):
            raise ValueError("unsupported observation contract")
    if type(q["display_name"]) is not str or len(q["display_name"]) > 128:
        raise ValueError("invalid display name")
    xs = q["inputs"]
    if type(xs) is not list or not 1 <= len(xs) <= 7:
        raise ValueError("invalid finite input set")
    for x in xs:
        integer(x, -3, 3)
    if xs != sorted(set(xs)):
        raise ValueError("input set must be ordered and unique")
    for role, version in (("source", "expanded-v0"), ("target", "horner-v0")):
        r = q[role]
        if set(r) != {"version", "coefficients"} or r["version"] != version:
            raise ValueError("representation version mismatch")
        if type(r["coefficients"]) is not list or len(r["coefficients"]) != 3:
            raise ValueError("three coefficients required")
        for c in r["coefficients"]:
            integer(c, -3, 3)


def evaluate(q, x):
    a, b, c = q["source"]["coefficients"]
    u = a * x
    v = u * x
    w = b * x
    y = v + w
    source = [u, v, w, y, y + c]
    a, b, c = q["target"]["coefficients"]
    u = a * x
    v = u + b
    w = v * x
    target = [u, v, w, w + c]
    for value in source + target:
        integer(value, -(2**127), 2**127 - 1)
    return {"x": x, "source_trace": source, "target_trace": target,
            "source_value": source[-1], "target_value": target[-1]}


def proposal_valid(parent, children):
    if type(children) is not list or len(children) != 2:
        return False
    flattened = []
    for child in children:
        if type(child) is not dict or set(child) != {"points", "depth"}:
            return False
        if type(child["depth"]) is not int or child["depth"] != parent["depth"] + 1 or child["depth"] > 6:
            return False
        xs = child["points"]
        if type(xs) is not list or not 0 < len(xs) < len(parent["points"]):
            return False
        if any(type(x) is not int for x in xs):
            return False
        flattened.extend(xs)
    return flattened == parent["points"] and len(set(flattened)) == len(flattened)


def coverage(q, pending, checked):
    flat = checked + [x for node in pending for x in node["points"]]
    return sorted(flat) == q["inputs"] and len(set(flat)) == len(flat)


def potential(pending):
    return {"phi": sum(len(n["points"]) - 1 for n in pending),
            "psi": sum(2 * len(n["points"]) - 1 for n in pending)}


def produce(q, ledger, mode):
    validate_question(q)
    pending, checked, events = [{"points": q["inputs"].copy(), "depth": 0}], [], []
    status, reason, counterexample = "Unknown", "work fuel exhausted", None
    while pending and ledger.spent["work"] < ledger.work:
        ledger.charge("work")
        parent = copy.deepcopy(pending[0])
        event = {"step": len(events) + 1, "parent": parent, "potential_before": potential(pending)}
        if len(parent["points"]) > 1:
            mid = len(parent["points"]) // 2
            children = [{"points": xs, "depth": parent["depth"] + 1}
                        for xs in (parent["points"][:mid], parent["points"][mid:])]
            if not events:
                if mode == "missing-child":
                    children = children[:1]
                elif mode == "overlapping-children":
                    children[1]["points"].insert(0, children[0]["points"][-1])
                elif mode == "copied-child-fuel":
                    for child in children:
                        child["fuel"] = ledger.work
                elif mode == "self-child-split":
                    children[0]["points"] = parent["points"].copy()
            event.update(kind="split", proposal=children)
            if proposal_valid(parent, children):
                pending = children + pending[1:]
                event["result"] = "Committed"
            else:
                event["result"] = "Rejected"
                status, reason = "Blocked", "invalid split proposal"
        else:
            values = evaluate(q, parent["points"][0])
            event.update(kind="point", values=values)
            if values["source_value"] == values["target_value"]:
                checked.append(parent["points"][0])
                pending.pop(0)
                event["result"] = "Equal"
            else:
                event["result"] = "Different"
                counterexample = values
                status, reason = "Refuted", "exact value counterexample; failed point retained in pending"
        assert coverage(q, pending, checked)
        event["potential_after"] = potential(pending)
        events.append(event)
        if status in ("Blocked", "Refuted"):
            break
    if not pending:
        status, reason = "FinitePreservationVerified", "all declared points checked"
    return {"schema": "adva.finite-split-receipt.research", "version": 0,
            "question": copy.deepcopy(q), "scope": scope(q), "events": events,
            "pending": pending, "checked": checked, "status": status, "reason": reason,
            "counterexample": counterexample, "execution_ledger": ledger.snapshot(),
            "native_free": "Unimplemented"}


def independently_check(q, receipt, ledger):
    """Reconstruct without producer split gate/evaluator/coverage/potential helpers."""
    started = time.perf_counter_ns()
    def need(test, reason):
        if not test:
            raise ValueError(reason)
    def rank(nodes):
        return {"phi": sum(len(n["points"]) - 1 for n in nodes),
                "psi": sum(2 * len(n["points"]) - 1 for n in nodes)}
    try:
        ledger.charge("verification")
        validate_question(q)
        need(receipt["schema"] == "adva.finite-split-receipt.research" and
             type(receipt["version"]) is int and receipt["version"] == 0, "receipt schema")
        need(scope(q) == receipt["scope"] == scope(receipt["question"]), "changed question scope")
        state = [{"points": q["inputs"].copy(), "depth": 0}]
        done, stop, counterexample = [], None, None
        events = receipt["events"]
        need(type(events) is list and len(events) <= 13, "event bound")
        for index, event in enumerate(events):
            ledger.charge("verification")
            need(stop is None and bool(state), "event after termination")
            need(type(event["step"]) is int and event["step"] == index + 1, "step ledger")
            parent = state[0]
            need(encoded(event["parent"]) == encoded(parent) and encoded(event["potential_before"]) == encoded(rank(state)), "parent or rank")
            if event["kind"] == "split":
                children = event["proposal"]
                valid = type(children) is list and len(children) == 2 and len(parent["points"]) > 1
                chunks = []
                if valid:
                    for child in children:
                        if type(child) is not dict or set(child) != {"points", "depth"}:
                            valid = False
                            break
                        points, depth = child["points"], child["depth"]
                        if (type(points) is not list or not 0 < len(points) < len(parent["points"])
                                or any(type(x) is not int for x in points)
                                or type(depth) is not int or depth != parent["depth"] + 1 or depth > 6):
                            valid = False
                            break
                        chunks.extend(points)
                valid = valid and chunks == parent["points"] and len(chunks) == len(set(chunks))
                if valid:
                    need(event["result"] == "Committed", "valid split not committed")
                    state = copy.deepcopy(children) + state[1:]
                else:
                    need(event["result"] == "Rejected", "invalid split admitted")
                    stop = "Blocked"
            elif event["kind"] == "point":
                ledger.charge("verification")
                need(len(parent["points"]) == 1, "point check on non-singleton")
                x = parent["points"][0]
                values = event["values"]
                a, b, c = q["source"]["coefficients"]
                sa = a * x
                sb = sa * x
                sc = b * x
                source_trace = [sa, sb, sc, sb + sc, sb + sc + c]
                aa, bb, cc = q["target"]["coefficients"]
                target_trace = [aa * x, aa * x + bb, (aa * x + bb) * x, (aa * x + bb) * x + cc]
                source_value = sum(coef * x**power for power, coef in enumerate([c, b, a]))
                target_value = sum(coef * x**power for power, coef in enumerate([cc, bb, aa]))
                expected = {"x": x, "source_trace": source_trace, "target_trace": target_trace,
                            "source_value": source_value, "target_value": target_value}
                need(encoded(values) == encoded(expected), "point value or separate trace mismatch")
                for v in source_trace + target_trace:
                    integer(v, -(2**127), 2**127 - 1)
                if source_value == target_value:
                    need(event["result"] == "Equal", "equal point rejected")
                    done.append(x)
                    state.pop(0)
                else:
                    need(event["result"] == "Different", "counterexample suppressed")
                    counterexample, stop = expected, "Refuted"
            else:
                raise ValueError("unknown event")
            flat = done + [x for node in state for x in node["points"]]
            need(sorted(flat) == q["inputs"] and len(flat) == len(set(flat)), "coverage invariant")
            need(encoded(event["potential_after"]) == encoded(rank(state)), "incorrect rank after transition")
            if event["result"] in ("Committed", "Equal"):
                need(event["potential_before"]["psi"] - rank(state)["psi"] == 1, "work rank did not decrease")
        ledger.charge("verification")
        r = receipt["execution_ledger"]
        work = integer(r["work_limit"], 0, 13)
        need(encoded(r) == encoded({"initial": work + 64, "work_limit": work, "reserve": 64,
                   "spent": {"work": len(events), "verification": 1, "serialization": 0},
                   "remaining": work + 63 - len(events), "audit_only": False}), "execution resource ledger")
        need(len(events) <= work, "work exceeded allocation")
        need(encoded(receipt["pending"]) == encoded(state) and encoded(receipt["checked"]) == encoded(done), "final frontier mismatch")
        if stop is None:
            stop = "FinitePreservationVerified" if not state else "Unknown"
            if state:
                need(len(events) == work, "unexplained early stop")
        need(receipt["status"] == stop and encoded(receipt["counterexample"]) == encoded(counterexample), "terminal status")
        need(receipt["native_free"] == "Unimplemented", "native capability escalation")
        return {"decision": "Accepted", "verified_status": stop,
                "reason": "scope, transitions, coverage, traces and resource ledger reconstructed",
                "elapsed_ns": time.perf_counter_ns() - started}
    except (ValueError, TypeError, KeyError, IndexError) as error:
        return {"decision": "Blocked", "verified_status": "Blocked", "reason": str(error),
                "elapsed_ns": time.perf_counter_ns() - started}


def run(contract):
    meter, cases, saved = Meter(), [], {}
    phases = {"construction_work_ns": 0, "verification_ns": 0, "serialization_ns": 0,
              "serialized_replay_ns": 0, "fresh_case_total_ns": 0}
    base = question(contract["main_coefficients"])
    for spec in contract["cases"]:
        started = time.perf_counter_ns()
        name = spec["id"]
        ledger = Ledger(meter, spec.get("work_fuel", 0), audit_only="work_fuel" not in spec)
        # One reserved unit pays for this bounded input/proposal construction batch.
        ledger.charge("verification")
        q = copy.deepcopy(base)
        if "work_fuel" in spec:
            if name == "fresh-coefficients":
                q = question(contract["fresh_coefficients"], "fresh-polynomial")
            if name == "wrong-target":
                q["target"]["coefficients"][2] += 1
            receipt = produce(q, ledger, name)
            audit_kind = "same-case reserved continuation"
        else:
            receipt = copy.deepcopy(saved["main"]["receipt"])
            audit_kind = "separately declared 64-unit audit; original execution ledger unchanged"
            if name == "display-rename":
                q["display_name"] = "same-question-new-display-name"
            elif name == "changed-scope-stale-receipt":
                q["inputs"] = D[:-1]
            elif name == "inconsistent-final-frontier":
                receipt["pending"].append({"points": [-3], "depth": 0})
        phases["construction_work_ns"] += time.perf_counter_ns() - started
        decision = independently_check(q, receipt, ledger)
        phases["verification_ns"] += decision["elapsed_ns"]
        status = decision["verified_status"]
        t = time.perf_counter_ns()
        ledger.charge("serialization")
        case = {"id": name, "task": q, "receipt": receipt, "checker": decision,
                "result": status, "audit_kind": audit_kind, "resource_after": ledger.snapshot()}
        payload = encoded(case)
        if len(payload) > MAX_BYTES:
            raise ValueError("case serialization exceeds bound")
        phases["serialization_ns"] += time.perf_counter_ns() - t
        expected_checker = "Blocked" if name in ("changed-scope-stale-receipt", "inconsistent-final-frontier") else "Accepted"
        case["agrees_with_frozen_expectation"] = status == spec["expected"] and decision["decision"] == expected_checker
        cases.append(case)
        saved[name] = {"receipt": receipt, "ledger": ledger, "case": case}
        if name == "fresh-coefficients":
            phases["fresh_case_total_ns"] = time.perf_counter_ns() - started
    replays = []
    for name in ("main", "partial-work-fuel"):
        item = saved[name]
        t = time.perf_counter_ns()
        item["ledger"].charge("serialization")
        rebuilt = json.loads(encoded(item["case"]))
        decision = independently_check(rebuilt["task"], rebuilt["receipt"], item["ledger"])
        elapsed = time.perf_counter_ns() - t
        phases["serialized_replay_ns"] += elapsed
        replays.append({"case": name, "checker": decision, "elapsed_ns": elapsed,
                        "same_verified_result": decision["verified_status"] == rebuilt["result"],
                        "resource_after_replay": item["ledger"].snapshot()})
    # Reserve pays for final report encoding/write as one checkpoint operation too.
    saved["main"]["ledger"].charge("serialization")
    final_ledgers = {name: item["ledger"].snapshot() for name, item in saved.items()}
    charged = sum(sum(value["spent"].values()) for value in final_ledgers.values())
    if charged != meter.spent:
        raise ValueError("global ledger mismatch")
    return {"schema": "adva.finite-split-calibration.research", "version": 0,
            "contract_sha256": CONTRACT_SHA, "cases": cases, "serialized_replays": replays,
            "all_frozen_expectations_met": all(c["agrees_with_frozen_expectation"] for c in cases),
            "all_replays_match": all(r["same_verified_result"] for r in replays),
            "resource": {"global_charged_units": meter.spent, "global_limit": 2000,
                         "final_case_ledgers": final_ledgers, "native_calls": 0, "search_nodes": 0},
            "costs": {**phases, "phase_note": "Fresh total overlaps construction, checking and serialization; serialized replay includes its checking. Construction includes work. Final report disk write measured by outer supervisor.",
                      "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      "peak_rss_scope": "this Linux Python process; ru_maxrss",
                      "authoring_research_network": "Missing"},
            "residuals": ["Finite seven-point observation claim only; no universal polynomial/compiler theorem claimed.",
                          "Separate checker shares Python exact integers and question schema validation with producer.",
                          "No native free, arbitrary new-obligation termination, directory migration or automatic continuation."]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024**2, 256 * 1024**2))
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    signal.alarm(5)
    with args.contract.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES or hashlib.sha256(raw).hexdigest() != CONTRACT_SHA:
        raise ValueError("frozen contract mismatch")
    contract = json.loads(raw)
    report = run(contract)
    payload = encoded(report) + b"\n"
    if len(payload) > MAX_BYTES:
        raise ValueError("report file bound exceeded")
    with args.output.open("xb") as stream:
        stream.write(payload)
    print(json.dumps({"all_frozen_expectations_met": report["all_frozen_expectations_met"],
                      "all_replays_match": report["all_replays_match"], "cases": len(report["cases"]),
                      "global_charged_units": report["resource"]["global_charged_units"],
                      "report_bytes": len(payload)}))
    if not report["all_frozen_expectations_met"] or not report["all_replays_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
