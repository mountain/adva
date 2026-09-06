"""External bounded resource accounting, not native Adva semantics."""
from __future__ import annotations
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import resource
import signal
import time

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/research/0135-resource-reinterpretation-contract.json"
CONTRACT_SHA = "a72f59cddddde17c8650d8fa615106df4600b713392f44848b6cde78ba77cbc2"
WIDTH = {"octet": 8, "nibble": 4}
ROLES = ["cell", "fuel", "task"]
NAMES = ["a", "b", "c"]
BASE_NAMES = dict(zip(ROLES, NAMES))
ROTATED = dict(zip(ROLES, ["b", "c", "a"]))
TASK = {"status": "AwaitingUserTask", "content": None}


class Invalid(ValueError):
    pass


class Limit(RuntimeError):
    pass


class Meter:
    def __init__(self):
        self.start = time.perf_counter_ns()
        self.rows = 0

    def charge(self):
        self.rows += 1
        if self.rows > 2000 or time.perf_counter_ns() - self.start > 5_000_000_000:
            raise Limit("row or wall budget")


def encode(obj):
    data = (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(data) > 131072:
        raise Limit("artifact byte bound")
    return data


def same(a, b, reason):
    if encode(a) != encode(b):
        raise Invalid(reason)


def cases():
    out = []
    for label, slots in [("main", 3), ("fresh", 2)]:
        out.append({"label": label, "substrate": "octet", "slots": slots, "grant": 8,
                    "actions": [{"op": "rename", "names": ROTATED}, {"op": "switch", "target": "nibble", "slots": slots * 2}, {"op": "rename", "names": BASE_NAMES}, {"op": "switch", "target": "octet", "slots": slots}]})
    for substrate in WIDTH:
        for i, permutation in enumerate(itertools.permutations(NAMES)):
            out.append({"label": f"rename-{substrate}-{i}", "substrate": substrate, "slots": 3 if substrate == "octet" else 6, "grant": 3,
                        "actions": [{"op": "rename", "names": dict(zip(ROLES, permutation))}]})
    out.extend([
        {"label": "collision", "substrate": "octet", "slots": 3, "grant": 3, "actions": [{"op": "rename", "names": {"cell": "a", "fuel": "a", "task": "c"}}]},
        {"label": "forged-width", "substrate": "nibble", "slots": 6, "grant": 3, "actions": [{"op": "switch", "target": "octet", "slots": 6}]},
        {"label": "inexact", "substrate": "nibble", "slots": 3, "grant": 3, "actions": [{"op": "switch", "target": "octet", "slots": 1}]},
        {"label": "zero-fuel", "substrate": "octet", "slots": 3, "grant": 0, "actions": [{"op": "rename", "names": ROTATED}]},
        {"label": "rename-cycle", "substrate": "octet", "slots": 3, "grant": 2, "actions": [{"op": "rename", "names": ROTATED}, {"op": "rename", "names": BASE_NAMES}, {"op": "rename", "names": ROTATED}]},
        {"label": "reset-control", "substrate": "octet", "slots": 3, "grant": 3, "actions": [{"op": "spend", "amount": 2}, {"op": "rename", "names": ROTATED}, {"op": "spend", "amount": 1}]},
    ])
    return copy.deepcopy(out)


def initial(q):
    return {"account_label": "external-fixture-account", "frame": {"substrate": q["substrate"], "slots": q["slots"], "names": dict(BASE_NAMES)},
            "capacity_bits": WIDTH[q["substrate"]] * q["slots"], "grant": q["grant"], "remaining": q["grant"], "spent": 0, "task": dict(TASK)}


def action_cost(a):
    return {"rename": 1, "switch": 2}.get(a["op"], a.get("amount", 0))


def produce(q, meter):
    state = initial(q)
    events = []
    for index, action in enumerate(q["actions"]):
        meter.charge()
        before = state["remaining"]
        cost = action_cost(action)
        status, reason, residual, debit = "Committed", None, None, 0
        if before < cost:
            status, reason = "Unknown", "FuelExhausted"
            residual = {"needed": cost, "available": before}
        else:
            debit = cost
            state["remaining"] -= debit
            state["spent"] += debit
            if action["op"] == "rename":
                names = action["names"]
                if len(set(names.values())) != 3 or set(names.values()) != set(NAMES):
                    status, reason = "Rejected", "NameCollision"
                else:
                    state["frame"]["names"] = copy.deepcopy(names)
            elif action["op"] == "switch":
                quotient, remainder = divmod(state["capacity_bits"], WIDTH[action["target"]])
                if remainder:
                    status, reason = "Unknown", "InexactConversion"
                    residual = {"unrepresented_bits": remainder}
                elif quotient != action["slots"]:
                    status, reason = "Rejected", "CapacityMismatch"
                    residual = {"claimed_bits": action["slots"] * WIDTH[action["target"]], "available_bits": state["capacity_bits"]}
                else:
                    state["frame"]["substrate"] = action["target"]
                    state["frame"]["slots"] = action["slots"]
        events.append({"index": index, "action": copy.deepcopy(action), "before_remaining": before, "debit": debit,
                       "status": status, "reason": reason, "residual": residual, "after": copy.deepcopy(state)})
        if status == "Unknown":
            break
    cursor = len(events) - 1 if events[-1]["status"] == "Unknown" else len(events)
    return {"input": q, "events": events, "final": state, "next_action_index": cursor, "task": dict(TASK)}


def check_trace(trace, q, meter):
    same(trace["input"], q, "frozen question")
    start = initial(q)
    bits = q["slots"] * WIDTH[q["substrate"]]
    used = 0
    active = copy.deepcopy(start["frame"])
    pending = False
    for i, event in enumerate(trace["events"]):
        meter.charge()
        if pending or i >= len(q["actions"]):
            raise Invalid("extra action after stop")
        a = q["actions"][i]
        same(event["action"], a, "action/order")
        required = 1 if a["op"] == "rename" else (2 if a["op"] == "switch" else a["amount"])
        available = q["grant"] - used
        debit = 0 if required > available else required
        used += debit
        status, reason, residual = "Committed", None, None
        if required > available:
            status, reason, residual = "Unknown", "FuelExhausted", {"needed": required, "available": available}
        elif a["op"] == "rename":
            if sorted(a["names"]) != sorted(ROLES) or sorted(a["names"].values()) != NAMES:
                status, reason = "Rejected", "NameCollision"
            else:
                active["names"] = dict(a["names"])
        elif a["op"] == "switch":
            unit = WIDTH[a["target"]]
            if bits % unit != 0:
                status, reason, residual = "Unknown", "InexactConversion", {"unrepresented_bits": bits % unit}
            elif a["slots"] * unit != bits:
                status, reason, residual = "Rejected", "CapacityMismatch", {"claimed_bits": a["slots"] * unit, "available_bits": bits}
            else:
                active["substrate"], active["slots"] = a["target"], a["slots"]
        after = {"account_label": start["account_label"], "frame": copy.deepcopy(active), "capacity_bits": bits,
                 "grant": q["grant"], "remaining": q["grant"] - used, "spent": used, "task": dict(TASK)}
        same(event, {"index": i, "action": a, "before_remaining": available, "debit": debit, "status": status, "reason": reason, "residual": residual, "after": after}, "event or common boundary")
        if used + after["remaining"] != q["grant"] or after["remaining"] < 0 or active["slots"] * WIDTH[active["substrate"]] != bits:
            raise Invalid("resource conservation")
        pending = status == "Unknown"
    if not trace["events"] or (not pending and len(trace["events"]) != len(q["actions"])):
        raise Invalid("missing actions")
    same(trace["final"], after, "final state")
    same(trace["next_action_index"], len(trace["events"]) - (1 if pending else 0), "pending action cursor")
    same(trace["task"], TASK, "unsupplied task")


def unsafe_control(meter):
    # Deliberately wrong: budget account lookup uses the current display name.
    q = cases()[-1]
    accounts = {BASE_NAMES["fuel"]: q["grant"]}
    name = BASE_NAMES["fuel"]
    spent = 0
    events = []
    for action in q["actions"]:
        meter.charge()
        cost = action_cost(action)
        accounts[name] -= cost
        spent += cost
        if action["op"] == "rename":
            name = action["names"]["fuel"]
            accounts.setdefault(name, q["grant"])
        events.append({"action": action, "current_name": name, "remaining": accounts[name], "total_spent": spent})
    return {"initial_grant": 3, "events": events, "violation": "rename creates a second grant", "overspend": spent - 3}


def check_unsafe(r, meter):
    meter.charge()
    expected = {"initial_grant": 3, "events": [
        {"action": {"op": "spend", "amount": 2}, "current_name": "b", "remaining": 1, "total_spent": 2},
        {"action": {"op": "rename", "names": ROTATED}, "current_name": "c", "remaining": 3, "total_spent": 3},
        {"action": {"op": "spend", "amount": 1}, "current_name": "c", "remaining": 2, "total_spent": 4}],
        "violation": "rename creates a second grant", "overspend": 1}
    same(r, expected, "unsafe counterexample")
    if sum(action_cost(e["action"]) for e in r["events"]) <= r["initial_grant"]:
        raise Invalid("missing overspend")


def build(meter):
    traces, timings = [], []
    for q in cases():
        start = time.perf_counter_ns()
        trace = produce(q, meter)
        check_trace(trace, q, meter)
        timings.append((time.perf_counter_ns() - start) / 1e6)
        traces.append(trace)
    unsafe = unsafe_control(meter)
    check_unsafe(unsafe, meter)
    return {"schema": "adva.external.resource-frame.v0", "contract_sha256": CONTRACT_SHA, "traces": traces, "unsafe_control": unsafe, "task": dict(TASK)}, timings


def verify(a, meter):
    same(hashlib.sha256(CONTRACT.read_bytes()).hexdigest(), CONTRACT_SHA, "contract hash")
    same(a["schema"], "adva.external.resource-frame.v0", "schema")
    same(a["contract_sha256"], CONTRACT_SHA, "contract binding")
    same(len(a["traces"]), 20, "case count")
    for trace, q in zip(a["traces"], cases()):
        check_trace(trace, q, meter)
    check_unsafe(a["unsafe_control"], meter)
    same(a["task"], TASK, "task remains open")


def limits():
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))
    def alarm(signum, frame):
        raise Limit("wall alarm")
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(5)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", type=Path)
    p.add_argument("--output", type=Path)
    p.add_argument("--cost-output", type=Path)
    args = p.parse_args()
    limits()
    m = Meter()
    timing = {}
    def measured(key, fn):
        start = time.perf_counter_ns()
        result = fn()
        timing[key] = (time.perf_counter_ns() - start) / 1e6
        return result
    if args.check:
        if args.check.stat().st_size > 131072:
            raise Limit("input size")
        a = measured("parse_ms", lambda: json.loads(args.check.read_bytes()))
        measured("replay_ms", lambda: verify(a, m))
        print(json.dumps({"status": "Verified", "rows": m.rows, "timings": timing}))
        return
    if not args.output or not args.cost_output:
        p.error("provide --check or --output and --cost-output")
    a, per_trace = measured("build_and_initial_check_ms", lambda: build(m))
    data = measured("serialization_ms", lambda: encode(a))
    parsed = measured("parse_ms", lambda: json.loads(data))
    measured("replay_ms", lambda: verify(parsed, m))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    measured("witness_save_ms", lambda: args.output.write_bytes(data))
    report = {"times": timing, "per_trace_build_and_check_ms": per_trace, "rows": m.rows, "total_ms": (time.perf_counter_ns()-m.start)/1e6, "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "artifact_bytes": len(data), "artifact_sha256": hashlib.sha256(data).hexdigest(), "excluded": ["startup/imports", "design and discussion", "network", "cost report write"], "units": "model fuel differs from host rows and time; per-trace times are nested in build"}
    args.cost_output.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report))


if __name__ == "__main__":
    try:
        main()
    except Limit as e:
        print(json.dumps({"status": "Unknown", "reason": str(e), "checkpoint_guaranteed": False}))
        raise SystemExit(2)
