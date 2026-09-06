"""Goal-relative stopping over one explicit F7 universe. External evidence only."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import resource
import signal
import sys
import time

VERSION = "adva.external.goal-exploration.v0"
CONTRACT = "5b4717c3f85847184b35a0115c2d546a4a0fc9ea2d7b206585ae6c3760771d7d"
UNIVERSE = list(range(7))
MAX_BYTES = 131072
INSTANCES = {"main": ([2,0,6],1), "fresh": ([1,2,3],3),
             "unique": ([1,0,0],0), "empty": ([2,0,6],2)}
RESIDUALS = ["finite declared universe, not the physical world", "fixed supplied goal rules",
             "no native semantic identities", "no novel algorithmic speedup",
             "hard-stop checkpoint not guaranteed"]


class Meter:
    def __init__(self):
        self.producer = 0
        self.checker = 0
        self.metadata = 0
        self.deadline = time.monotonic()+5

    def item(self, n=1):
        self.metadata += n
        if self.metadata > 20000 or time.monotonic() > self.deadline:
            raise RuntimeError("metadata or wall limit")

    def scalar(self, kind):
        self.item()
        if kind == "producer":
            self.producer += 1
        else:
            self.checker += 1
        if self.producer+self.checker > 1000:
            raise RuntimeError("scalar-work limit")


class MissingInput(ValueError):
    pass


def encode(value):
    data = (json.dumps(value, sort_keys=True, separators=(",", ":"))+"\n").encode()
    if len(data) > MAX_BYTES:
        raise ValueError("artifact size limit")
    return data


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def equal(a, b, message):
    if encode(a) != encode(b):
        raise ValueError(message)


def task(coefficients, rhs):
    if coefficients is None:
        raise MissingInput("no equation supplied; no exploration started")
    if not isinstance(coefficients, list) or len(coefficients) != 3:
        raise ValueError("exactly three coefficients required")
    if any(type(v) is not int or not 0 <= v < 7 for v in coefficients+[rhs]):
        raise ValueError("canonical field scalars required")
    return {"schema": VERSION, "universe": UNIVERSE[:],
            "open": {"variable": "x", "type": "F7", "coefficients": coefficients[:], "rhs": rhs}}


def query(label, goal, policy="goal_aware", fuel=7, order=None):
    coefficients, rhs = INSTANCES[label]
    return {"task": task(coefficients, rhs), "goal": goal, "policy": policy,
            "fuel": fuel, "order": UNIVERSE[:] if order is None else order[:]}


def validate_query(q, meter):
    meter.item(15)
    if set(q) != {"task", "goal", "policy", "fuel", "order"}:
        raise ValueError("query fields drift")
    t = q["task"]
    equal(t, task(t["open"]["coefficients"], t["open"]["rhs"]), "task or universe drift")
    if q["goal"] not in ("exists", "all", "unique") or q["policy"] not in ("goal_aware", "exhaustive"):
        raise ValueError("unsupported goal or policy")
    if type(q["fuel"]) is not int or not 0 <= q["fuel"] <= 7:
        raise ValueError("fuel outside contract")
    order = q["order"]
    if (not isinstance(order, list) or len(order) != 7
            or any(type(x) is not int for x in order) or sorted(order) != UNIVERSE):
        raise ValueError("schedule must cover every universe element exactly once")


def early(goal, hits):
    return (goal == "exists" and len(hits) >= 1) or (goal == "unique" and len(hits) >= 2)


def explore(q, meter):
    validate_query(q, meter)
    a,b,c = q["task"]["open"]["coefficients"]
    rhs = q["task"]["open"]["rhs"]
    rows, hits = [], []
    for x in q["order"][:q["fuel"]]:
        meter.scalar("producer")
        y = ((a*x+b)*x+c) % 7
        rows.append([x,y,y == rhs])
        if y == rhs:
            hits.append(x)
        if q["policy"] == "goal_aware" and early(q["goal"], hits):
            break
    full = len(rows) == 7
    reason = "fuel_exhausted"
    if full:
        reason = "domain_exhausted"
    if q["policy"] == "goal_aware" and early(q["goal"], hits):
        reason = "goal_reached"
    status, answer, basis = "Unknown", None, "insufficient_evidence"
    if q["goal"] == "exists" and hits:
        status, answer, basis = "Verified", True, "one_witness"
    elif q["goal"] == "unique" and len(hits) >= 2:
        status, answer, basis = "Verified", False, "two_distinct_witnesses"
    elif full:
        status, basis = "Verified", "complete_domain"
        if q["goal"] == "exists":
            answer = False
        elif q["goal"] == "all":
            answer = sorted(hits)
        else:
            answer = len(hits) == 1
    return {"query": deepcopy(q), "binding": digest(q), "rows": rows,
            "execution_stop": reason, "discovered": hits,
            "coverage_complete": full, "unvisited": q["order"][len(rows):],
            "judgment": {"status": status, "answer": answer, "basis": basis}}


def verify_record(r, meter):
    if set(r) != {"query", "binding", "rows", "execution_stop", "discovered", "coverage_complete", "unvisited", "judgment"}:
        raise ValueError("record fields drift")
    q = r["query"]
    validate_query(q, meter)
    equal(r["binding"], digest(q), "goal or task binding drift")
    if not isinstance(r["rows"], list) or len(r["rows"]) > q["fuel"]:
        raise ValueError("trace exceeds fuel")
    coefficients = q["task"]["open"]["coefficients"]
    rhs = q["task"]["open"]["rhs"]
    hits = []
    stop_at_witness = False
    for i, row in enumerate(r["rows"]):
        if stop_at_witness:
            raise ValueError("goal-aware trace continued past its stopping rule")
        x = q["order"][i]
        meter.scalar("checker")
        # Independently expanded powers, not the nested producer evaluation.
        y = (coefficients[0]*pow(x,2,7)+coefficients[1]*x+coefficients[2]) % 7
        equal(row, [x,y,y == rhs], "wrong observation or schedule prefix")
        if y == rhs:
            hits.append(x)
        if q["policy"] == "goal_aware":
            stop_at_witness = (q["goal"] == "exists" and bool(hits)) or (q["goal"] == "unique" and len(hits) > 1)
    n = len(r["rows"])
    if n < q["fuel"] and not stop_at_witness:
        raise ValueError("unjustified early termination")
    full = n == 7
    expected_reason = "goal_reached" if stop_at_witness else ("domain_exhausted" if full else "fuel_exhausted")
    equal(r["execution_stop"], expected_reason, "wrong execution exit")
    equal(r["discovered"], hits, "wrong witness list")
    equal(r["coverage_complete"], full, "false domain coverage")
    equal(r["unvisited"], q["order"][n:], "remaining alternatives erased")
    # Goal judgment is reconstructed here, rather than accepted from the search.
    if q["goal"] == "all":
        expected = {"status": "Verified", "answer": sorted(hits), "basis": "complete_domain"} if full else {
            "status": "Unknown", "answer": None, "basis": "insufficient_evidence"}
    elif q["goal"] == "exists":
        expected = {"status": "Verified", "answer": True, "basis": "one_witness"} if hits else (
            {"status": "Verified", "answer": False, "basis": "complete_domain"} if full else
            {"status": "Unknown", "answer": None, "basis": "insufficient_evidence"})
    elif len(hits) > 1:
        expected = {"status": "Verified", "answer": False, "basis": "two_distinct_witnesses"}
    elif full:
        expected = {"status": "Verified", "answer": len(hits) == 1, "basis": "complete_domain"}
    else:
        expected = {"status": "Unknown", "answer": None, "basis": "insufficient_evidence"}
    equal(r["judgment"], expected, "unsupported goal judgment")


def queries():
    result = {}
    for label in INSTANCES:
        for goal in ("exists", "all", "unique"):
            result[f"{label}:{goal}"] = query(label, goal)
    for goal in ("exists", "all", "unique"):
        result[f"baseline:{goal}"] = query("main", goal, "exhaustive")
        result[f"fuel2:{goal}"] = query("main", goal, fuel=2)
    result["fuel0:exists"] = query("main", "exists", fuel=0)
    result["reordered:unique"] = query("main", "unique", fuel=2, order=[6,1,0,2,3,4,5])
    return result


def timed(times, key, fn, *args):
    start = time.perf_counter_ns()
    try:
        return fn(*args)
    finally:
        times[key] = times.get(key,0)+time.perf_counter_ns()-start


def build(meter, times):
    records = {}
    for label, q in queries().items():
        r = timed(times, f"explore:{label}", explore, q, meter)
        timed(times, "initial_verification", verify_record, r, meter)
        records[label] = r
    try:
        task(None, 1)
    except MissingInput:
        missing = {"status": "MissingInput", "exploration_started": False}
    else:
        raise RuntimeError("missing-input boundary failed")
    return {"schema": VERSION, "contract_sha256": CONTRACT, "records": records,
            "missing_input": missing, "residuals": RESIDUALS[:]}


def verify_artifact(a, meter):
    if set(a) != {"schema", "contract_sha256", "records", "missing_input", "residuals"}:
        raise ValueError("artifact fields drift")
    equal(a["schema"], VERSION, "version drift")
    equal(a["contract_sha256"], CONTRACT, "contract drift")
    equal(a["missing_input"], {"status": "MissingInput", "exploration_started": False}, "missing-input judgment drift")
    equal(a["residuals"], RESIDUALS, "residual erased")
    expected = queries()
    if set(a["records"]) != set(expected):
        raise ValueError("fixture case omitted")
    for label, q in expected.items():
        equal(a["records"][label]["query"], q, "frozen instance changed")
        verify_record(a["records"][label], meter)


def load_file(path):
    with open(path,"rb") as f:
        data = f.read(MAX_BYTES+1)
    if len(data) > MAX_BYTES:
        raise ValueError("input size limit")
    return json.loads(data)


def save(path, data):
    path = Path(path)
    temp = path.with_suffix(path.suffix+".tmp")
    temp.write_bytes(data)
    temp.replace(path)


def limits():
    resource.setrlimit(resource.RLIMIT_AS,(268435456,268435456))
    resource.setrlimit(resource.RLIMIT_CPU,(5,5))
    def alarm(*_):
        raise RuntimeError("wall limit")
    signal.signal(signal.SIGALRM,alarm)
    signal.alarm(5)


def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("--check")
    p.add_argument("--output")
    p.add_argument("--cost-output")
    args = p.parse_args()
    limits()
    meter, times = Meter(), {}
    start = time.perf_counter_ns()
    if args.check:
        a = timed(times,"read_parse",load_file,args.check)
        timed(times,"replay",verify_artifact,a,meter)
    else:
        a = timed(times,"build_total",build,meter,times)
        data = timed(times,"serialization",encode,a)
        restored = timed(times,"parse",json.loads,data)
        timed(times,"replay",verify_artifact,restored,meter)
        if args.output:
            timed(times,"witness_save",save,args.output,data)
    costs = {"schema":"adva.external.goal-exploration-cost.v0","witness_sha256":digest(a),
             "elapsed_ns":time.perf_counter_ns()-start,"phase_ns":times,
             "producer_evaluations":meter.producer,"checker_evaluations":meter.checker,"metadata_items":meter.metadata,
             "peak_rss_kib_linux":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
             "artifact_bytes":len(encode(a)),"python":sys.version.split()[0],
             "exclusions":"imports, startup, design, network and cost-report writing; build_total nests subphases"}
    if args.cost_output:
        save(args.cost_output,encode(costs))
    print(json.dumps(costs,sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError,MemoryError) as exc:
        print(json.dumps({"status":"Unknown","reason":str(exc),"checkpoint":"not guaranteed at process resource interruption"}))
        sys.exit(2)
