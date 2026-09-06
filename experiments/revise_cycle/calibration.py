"""External F7 boundary receipts; no Adva semantic identities are allocated."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import resource
import signal
import time

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/research/0134-three-turn-revise-contract.json"
CONTRACT_SHA = "e88d4ce8730d269cd3e3ee2677db1335fcb6ed52c15214a7d9fea45cf9f112b2"
U = list(range(7))
SCHEMA = "adva.external.three-turn-revise.v0"
INSTANCES = {"main": ([2, 0, 6], 1, 1, 6), "fresh": ([1, 2, 3], 3, 0, 5)}


class Invalid(ValueError):
    pass


class Budget(RuntimeError):
    pass


class Meter:
    def __init__(self):
        self.start = time.perf_counter_ns()
        self.counts = {"producer": 0, "checker": 0, "metadata": 0}

    def charge(self, key, n=1):
        self.counts[key] += n
        if self.counts["producer"] + self.counts["checker"] > 2000:
            raise Budget("scalar allowance")
        if self.counts["metadata"] > 30000:
            raise Budget("metadata allowance")
        if time.perf_counter_ns() - self.start > 5_000_000_000:
            raise Budget("wall allowance")


def require(condition, message, meter):
    meter.charge("metadata")
    if not condition:
        raise Invalid(message)


def field(x):
    return type(x) is int and 0 <= x < 7


def validate_spec(s, goal, version, meter):
    require(type(s) is dict and set(s) == {"version", "goal", "domain", "coefficients", "rhs"}, "spec shape", meter)
    require(type(s["version"]) is int and s["version"] == version and s["goal"] == goal, "spec version/goal", meter)
    require(type(s["domain"]) is list and all(field(x) for x in s["domain"]) and s["domain"] == U, "domain", meter)
    require(type(s["coefficients"]) is list and len(s["coefficients"]) == 3 and all(field(x) for x in s["coefficients"]), "coefficients", meter)
    require(field(s["rhs"]), "rhs", meter)


def spec(coefficients, rhs, goal, version):
    return {"version": version, "goal": goal, "domain": U.copy(), "coefficients": list(coefficients), "rhs": rhs}


def lower(s):
    a, b, c = s["coefficients"]
    return [["CONST", a], ["X"], ["MUL"], ["CONST", b], ["ADD"], ["X"], ["MUL"], ["CONST", c], ["ADD"]]


def validate_code(code, meter):
    require(type(code) is list and len(code) == 9, "code size", meter)
    expected = ["CONST", "X", "MUL", "CONST", "ADD", "X", "MUL", "CONST", "ADD"]
    for instruction, op in zip(code, expected):
        require(type(instruction) is list and len(instruction) == (2 if op == "CONST" else 1) and instruction[0] == op, "instruction type", meter)
        if op == "CONST":
            require(field(instruction[1]), "constant type", meter)


def execute(code, x, meter, role="producer"):
    meter.charge(role)
    stack = []
    for ins in code:
        op = ins[0]
        if op == "CONST":
            stack.append(ins[1])
        elif op == "X":
            stack.append(x)
        else:
            right, left = stack.pop(), stack.pop()
            stack.append((left * right if op == "MUL" else left + right) % 7)
    return stack[0]


def source(s, x, meter):
    meter.charge("checker")
    return sum(c * (x ** degree) for c, degree in zip(s["coefficients"], [2, 1, 0])) % 7


def frozen_queries():
    out = []
    for label, (_, _, old_x, next_x) in INSTANCES.items():
        out.extend([
            {"label": label, "mode": "cached", "order": [next_x], "fuel": 1},
            {"label": label, "mode": "uncached", "order": [old_x, next_x], "fuel": 2},
        ])
    out.extend([
        {"label": "main", "mode": "cached", "order": [6], "fuel": 0},
        {"label": "main", "mode": "cached", "order": [2], "fuel": 1},
        {"label": "main", "mode": "cached", "order": [2, 6], "fuel": 1},
    ])
    return out


def judgment(s, observations):
    roots = [r[0] for r in observations if r[1] == s["rhs"]]
    done = len(roots) >= 2
    return {"task_version": s["version"], "goal": s["goal"], "status": "Close" if done else "Unknown", "answer": True if done else None, "witnesses": roots, "obligations": [] if done else ["a second distinct satisfying input"]}


def turn_receipts(old, new, result):
    return [
        {"from": "specification", "to": "syntax", "changed": "exists v1 to nonunique v2; expanded form to stack form", "preserved": ["domain", "polynomial", "old existence claim"], "inapplicable": ["v1 completion as v2 completion"], "owed": ["whole-domain compilation check", "validate imported observations", "new goal judgment"]},
        {"from": "syntax", "to": "interpretation", "changed": "bounded continuation observations", "preserved": ["old history", "v2 task binding"], "inapplicable": [], "owed": ["new goal judgment"]},
        {"from": "interpretation", "to": "specification", "changed": "knowledge and next action", "preserved": ["v1 existence remains true", "unvisited positions"], "inapplicable": ["nonunique as complete enumeration", "phase return as identity"], "owed": list(result["obligations"])},
    ]


def build_record(q, meter):
    coefficients, rhs, old_x, _ = INSTANCES[q["label"]]
    old = spec(coefficients, rhs, "exists", 1)
    new = spec(coefficients, rhs, "nonunique", 2)
    code = lower(new)
    old_rows = [[old_x, execute(code, old_x, meter)]]
    compilation = [[x, execute(code, x, meter)] for x in U]
    observed = list(old_rows) if q["mode"] == "cached" else []
    rows = []
    for x in q["order"][:q["fuel"]]:
        row = [x, execute(code, x, meter)]
        observed.append(row)
        rows.append(row)
        if judgment(new, observed)["status"] == "Close":
            break
    result = judgment(new, observed)
    remainder = [x for x in U if x not in [r[0] for r in observed]]
    cursor = len(rows)
    next_action = "retain_unvisited; do_not_schedule_uniqueness_search" if result["status"] == "Close" else "request_finite_continuation_for_second_witness"
    return {"query": q, "old_spec": old, "new_spec": new, "code": code,
            "old_evidence": {"spec": old, "observations": old_rows, "status": "Close"},
            "compiler_rows": compilation, "new_rows": rows, "judgment": result,
            "turns": turn_receipts(old, new, result), "unvisited": remainder,
            "cursor": cursor, "remaining_schedule": q["order"][cursor:],
            "stop": "goal_reached" if result["status"] == "Close" else ("fuel_exhausted" if cursor < len(q["order"]) else "schedule_exhausted"),
            "learn": {"before": "nonuniqueness Unknown", "after": "nonuniqueness True" if result["status"] == "Close" else "nonuniqueness Unknown", "next_action": next_action}}


def verify_record(r, q, meter):
    require(type(r) is dict, "record shape", meter)
    require(encoded(r.get("query")) == encoded(q), "frozen query", meter)
    old, new = r["old_spec"], r["new_spec"]
    validate_spec(old, "exists", 1, meter)
    validate_spec(new, "nonunique", 2, meter)
    coefficients, rhs, old_x, _ = INSTANCES[q["label"]]
    require(old == spec(coefficients, rhs, "exists", 1) and new == spec(coefficients, rhs, "nonunique", 2), "question binding", meter)
    code = r["code"]
    validate_code(code, meter)
    require(type(r["compiler_rows"]) is list and len(r["compiler_rows"]) == 7, "compilation coverage", meter)
    for x, row in enumerate(r["compiler_rows"]):
        require(type(row) is list and len(row) == 2 and all(field(v) for v in row) and row[0] == x, "compiler row", meter)
        require(row[1] == source(new, x, meter) == execute(code, x, meter, "checker"), "compilation mismatch", meter)
    evidence = r["old_evidence"]
    validate_spec(evidence["spec"], "exists", 1, meter)
    require(evidence["spec"] == old and evidence["status"] == "Close", "old evidence scope", meter)
    old_value = source(old, old_x, meter)
    require(type(evidence["observations"]) is list and len(evidence["observations"]) == 1 and type(evidence["observations"][0]) is list and len(evidence["observations"][0]) == 2 and all(field(v) for v in evidence["observations"][0]), "old observation type", meter)
    require(evidence["observations"] == [[old_x, old_value]] and old_value == rhs, "old existence witness", meter)
    observations = [[old_x, old_value]] if q["mode"] == "cached" else []
    rows = r["new_rows"]
    require(type(rows) is list and len(rows) <= min(q["fuel"], len(q["order"])), "fuel", meter)
    for i, row in enumerate(rows):
        require(sum(y == rhs for _, y in observations) < 2, "unnecessary continuation", meter)
        require(type(row) is list and len(row) == 2 and all(field(v) for v in row), "observation type", meter)
        require(row[0] == q["order"][i] and row[0] not in [p[0] for p in observations], "order/distinctness", meter)
        require(row[1] == source(new, row[0], meter), "new observation value", meter)
        observations.append(row)
    roots = [x for x, y in observations if y == rhs]
    done = len(roots) >= 2
    require(done or len(rows) == min(q["fuel"], len(q["order"])), "premature stop", meter)
    expected = {"task_version": 2, "goal": "nonunique", "status": "Close" if done else "Unknown", "answer": True if done else None, "witnesses": roots, "obligations": [] if done else ["a second distinct satisfying input"]}
    require(encoded(r["judgment"]) == encoded(expected), "stale or unsupported close", meter)
    require(r["turns"] == turn_receipts(old, new, expected), "turn obligations/history", meter)
    require(type(r["unvisited"]) is list and all(field(x) for x in r["unvisited"]) and r["unvisited"] == [x for x in U if x not in [p[0] for p in observations]], "frontier", meter)
    cursor = len(rows)
    require(type(r["cursor"]) is int and r["cursor"] == cursor and type(r["remaining_schedule"]) is list and all(field(x) for x in r["remaining_schedule"]) and r["remaining_schedule"] == q["order"][cursor:], "continuation cursor", meter)
    require(r["stop"] == ("goal_reached" if done else ("fuel_exhausted" if cursor < len(q["order"]) else "schedule_exhausted")), "exit reason", meter)
    require(r["learn"] == {"before": "nonuniqueness Unknown", "after": "nonuniqueness True" if done else "nonuniqueness Unknown", "next_action": "retain_unvisited; do_not_schedule_uniqueness_search" if done else "request_finite_continuation_for_second_witness"}, "learner update", meter)


def build(meter):
    records = []
    durations = []
    for q in frozen_queries():
        start = time.perf_counter_ns()
        r = build_record(q, meter)
        verify_record(r, q, meter)
        durations.append((time.perf_counter_ns() - start) / 1e6)
        records.append(r)
    return {"schema": SCHEMA, "contract_sha256": CONTRACT_SHA, "records": records}, durations


def verify_artifact(a, meter):
    require(hashlib.sha256(CONTRACT.read_bytes()).hexdigest() == CONTRACT_SHA, "frozen contract", meter)
    require(a["schema"] == SCHEMA and a["contract_sha256"] == CONTRACT_SHA, "artifact binding", meter)
    require(len(a["records"]) == 7, "frozen record count", meter)
    for r, q in zip(a["records"], frozen_queries()):
        verify_record(r, q, meter)


def encoded(a):
    b = (json.dumps(a, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(b) > 131072:
        raise Budget("artifact bytes")
    return b


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))
    def timeout(signum, frame):
        raise Budget("supervisor alarm")
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--cost-output", type=Path)
    parser.add_argument("--check", type=Path)
    args = parser.parse_args()
    limits()
    meter = Meter()
    times = {}
    def measured(name, fn):
        start = time.perf_counter_ns()
        value = fn()
        times[name] = (time.perf_counter_ns() - start) / 1e6
        return value
    if args.check:
        if args.check.stat().st_size > 131072:
            raise Budget("input bytes")
        artifact = measured("parse_ms", lambda: json.loads(args.check.read_bytes()))
        measured("replay_ms", lambda: verify_artifact(artifact, meter))
        print(json.dumps({"status": "Verified", "costs": meter.counts, "times": times}))
        return
    if args.output is None or args.cost_output is None:
        parser.error("provide --check or both --output and --cost-output")
    artifact, record_times = measured("build_and_initial_check_ms", lambda: build(meter))
    data = measured("serialization_ms", lambda: encoded(artifact))
    parsed = measured("parse_ms", lambda: json.loads(data))
    measured("replay_ms", lambda: verify_artifact(parsed, meter))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    measured("witness_save_ms", lambda: args.output.write_bytes(data))
    cost = {"times": times, "per_record_build_and_check_ms": record_times, "counts": meter.counts, "total_ms": (time.perf_counter_ns() - meter.start) / 1e6, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "artifact_bytes": len(data), "artifact_sha256": hashlib.sha256(data).hexdigest(), "excluded": ["imports/startup", "design", "network", "cost report write"], "note": "Linux peak process RSS; record times are nested in build time. Includes old-observation construction and rechecking. Compiler checks see all seven values; learner observation separation is imposed, not information-theoretic secrecy."}
    args.cost_output.write_text(json.dumps(cost, indent=2) + "\n")
    print(json.dumps(cost))


if __name__ == "__main__":
    try:
        main()
    except Budget as e:
        print(json.dumps({"status": "Unknown", "reason": str(e), "checkpoint_guaranteed": False}))
        raise SystemExit(2)
