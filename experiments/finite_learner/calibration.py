"""External finite model only. No native Adva types, identities or commands.

Producer: Horner evaluation. Checker: expanded powers over exactly F_7.
No eval, recursive syntax, unbounded search or automatic continuation.
"""
from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
import json
import resource
import signal
import sys
import time
from pathlib import Path

VERSION = "external-f7-quadratic-v0"
CONTRACT = "643ad235e4b2ad65e395fc705d33ffc7a42731e1f755f64b976693eca9b65474"
LIMIT = 524288
WORK = Counter()
TIMES = Counter()
DEADLINE = float("inf")


def charge(kind, n=1):
    WORK[kind] += n
    if sum(WORK.values()) > 50000 or time.monotonic() > DEADLINE:
        raise RuntimeError("aggregate resource limit")


def bounded_runtime():
    global DEADLINE
    DEADLINE = time.monotonic() + 5
    resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    def expired(*_):
        raise RuntimeError("wall resource limit")
    signal.signal(signal.SIGALRM, expired)
    signal.alarm(5)


def measured(name, fn, *args):
    start = time.perf_counter_ns()
    try:
        return fn(*args)
    finally:
        TIMES[name] += time.perf_counter_ns() - start


def encode(value):
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(data) > LIMIT:
        raise ValueError("artifact byte limit")
    return data


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def triple(value):
    charge("schema", 3)
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError("three coefficients required")
    if any(type(v) is not int or not 0 <= v < 7 for v in value):
        raise ValueError("coefficients must be canonical F7 integers")
    return value


def task(coefficients):
    return {"version": VERSION, "coefficients": list(triple(coefficients)),
            "domain": list(range(7)), "quantifier": "forall x in F7"}


def validate_task(q):
    charge("validation")
    if encode(q) != encode(task(q["coefficients"])):
        raise ValueError("task or domain drift")


def oracle(c, x):
    # Independent of the producer's nested evaluation.
    charge("checker_point")
    return (c[0] * pow(x, 2, 7) + c[1] * x + c[2]) % 7


def horner(c, x):
    charge("producer_point")
    a, b, d = c
    return ((a * x + b) * x + d) % 7


def candidate_at(i):
    if type(i) is not int or not 0 <= i < 343:
        raise ValueError("candidate ordinal outside grammar")
    return [i // 49, (i // 7) % 7, i % 7]


def trial(q, c):
    validate_task(q)
    triple(c)
    observations = []
    for x in range(7):
        wanted = oracle(q["coefficients"], x)
        got = horner(c, x)
        observations.append([x, wanted, got])
        if wanted != got:
            break
    return {"task": digest(q), "candidate": c, "observations": observations,
            "status": "Accepted" if len(observations) == 7 and wanted == got else "Refuted"}


def verify_trial(q, r):
    validate_task(q)
    c = triple(r["candidate"])
    observations = []
    for x in range(7):
        wanted, got = oracle(q["coefficients"], x), oracle(c, x)
        observations.append([x, wanted, got])
        if wanted != got:
            break
    expected = {"task": digest(q), "candidate": c, "observations": observations,
                "status": "Accepted" if len(observations) == 7 and wanted == got else "Refuted"}
    if r != expected:
        raise ValueError("invalid or incomplete trial evidence")


def search(q, fuel, cursor=0):
    validate_task(q)
    if type(fuel) is not int or not 0 <= fuel <= 343:
        raise ValueError("fuel outside contract")
    if type(cursor) is not int or not 0 <= cursor <= 343:
        raise ValueError("invalid cursor")
    rows = []
    for ordinal in range(cursor, min(343, cursor + fuel)):
        charge("candidate")
        row = trial(q, candidate_at(ordinal))
        rows.append(row)
        if row["status"] == "Accepted":
            break
    accepted = bool(rows and rows[-1]["status"] == "Accepted")
    end = cursor + len(rows)
    return {"task": digest(q), "start": cursor, "fuel": fuel, "cursor": end,
            "rows": rows, "status": "Accepted" if accepted else "Unknown",
            "reason": "witness" if accepted else ("family_exhausted" if end == 343 else "fuel_exhausted")}


def verify_search(q, r):
    validate_task(q)
    start, fuel, end = r["start"], r["fuel"], r["cursor"]
    if (type(start) is not int or type(fuel) is not int or type(end) is not int
            or not 0 <= start <= end <= 343 or not 0 <= fuel <= 343):
        raise ValueError("invalid search budget or cursor")
    if r["task"] != digest(q) or end != start + len(r["rows"]):
        raise ValueError("unbound search record")
    accepted = False
    for i, row in enumerate(r["rows"], start):
        charge("validation")
        if accepted or row["candidate"] != candidate_at(i):
            raise ValueError("noncanonical or post-success search")
        verify_trial(q, row)
        accepted = row["status"] == "Accepted"
    expected_end = min(343, start + fuel)
    if end > expected_end or (not accepted and end != expected_end):
        raise ValueError("missing search prefix")
    if r["status"] != ("Accepted" if accepted else "Unknown"):
        raise ValueError("unsupported logical verdict")
    reason = "witness" if accepted else ("family_exhausted" if end == 343 else "fuel_exhausted")
    if r["reason"] != reason:
        raise ValueError("wrong exit reason")


def initial(q):
    validate_task(q)
    return {"task": digest(q), "cursor": 0, "constraints": [], "words": [], "ledger": []}


def update(q, old, record, kind):
    """Never trusts status alone. All state writes follow evidence checking."""
    charge("state_update")
    if old["task"] != digest(q):
        raise ValueError("stale learner task")
    if kind == "search":
        verify_search(q, record)
        if record["start"] != old["cursor"]:
            raise ValueError("continuation cursor mismatch")
        rows = record["rows"]
    elif kind == "trial":
        verify_trial(q, record)
        rows = [record]
    else:
        raise ValueError("unknown record kind")
    new = deepcopy(old)
    for r in rows:
        if r["status"] == "Refuted":
            x, y, _ = r["observations"][-1]
            if [x, y] not in new["constraints"]:
                new["constraints"].append([x, y])
        else:
            new["words"].append({"name": "checked-quadratic-instance", "version": VERSION,
                "task": digest(q), "coefficients": r["candidate"], "witness": r,
                "definition": "external Horner expression with this exact coefficient triple",
                "residual": "no claim about another task until fresh verification"})
    if kind == "search":
        new["cursor"] = record["cursor"]
    new["ledger"].append({"kind": kind, "record": digest(record), "status": record["status"]})
    return new


def propose(q, state):
    if state["task"] != digest(q):
        raise ValueError("stale proposal state")
    for x, y in state["constraints"]:
        if type(x) is not int or not 0 <= x < 7 or y != oracle(q["coefficients"], x):
            raise ValueError("unverified constraint")
    for i in range(343):
        charge("proposal_candidate")
        c = candidate_at(i)
        if all(horner(c, x) == y for x, y in state["constraints"]):
            return c
    return None


def shift(c):
    """Supplied algebraic policy, NOT a discovered general theorem."""
    a, b, d = triple(c)
    return [a, (2 * a + b) % 7, (a + b + d) % 7]


def reuse(source, word, target):
    # Revalidate the stored instance and never import its status to target.
    verify_trial(source, word["witness"])
    if word["witness"]["status"] != "Accepted" or word["task"] != digest(source):
        raise ValueError("word lacks accepted source evidence")
    expected = update(source, initial(source), word["witness"], "trial")["words"][0]
    if word != expected:
        raise ValueError("word binding or definition drift")
    c = shift(word["coefficients"])
    result = trial(target, c)
    verify_trial(target, result)
    return {"source_word": digest(word), "substitution": "x -> x+1 in F7",
            "expanded_coefficients": c, "trial": result}


def boundary(q, r):
    verify_trial(q, r)
    if r["status"] != "Accepted":
        raise ValueError("cannot read equality from refutation")
    rows = []
    for x, y, z in r["observations"]:
        charge("boundary")
        ratio = None if y == 0 else (z * pow(y, -1, 7)) % 7
        rows.append({"x": x, "difference": (z-y) % 7, "ratio": ratio,
                     "ratio_status": "undefined_at_zero" if y == 0 else "unit"})
    return rows


def build():
    q, q2 = task([2, 3, 1]), task([2, 0, 6])
    s = initial(q)
    wrong = measured("refutation", trial, q, [2, 3, 0])
    failed = measured("state_update", update, q, s, wrong, "trial")
    proposal_before, proposal_after = propose(q, s), propose(q, failed)
    zero = measured("zero_fuel", search, q, 0)
    paused = measured("state_update", update, q, s, zero, "search")
    prefix = measured("prefix_search", search, q, 3)
    prefix_state = measured("state_update", update, q, s, prefix, "search")
    continued = measured("explicit_continuation", search, q, 340, prefix_state["cursor"])
    continued_state = measured("state_update", update, q, prefix_state, continued, "search")
    positive = measured("full_search", search, q, 343)
    learned = measured("success_verification_and_word_formation", update, q, s, positive, "search")
    word = learned["words"][0]
    baseline = measured("reuse_search_baseline", search, q2, 343)
    reused = measured("checked_reuse", reuse, q, word, q2)
    # A fair conventional control uses the same substitution and fresh checker.
    def ordinary():
        r = trial(q2, shift(positive["rows"][-1]["candidate"]))
        verify_trial(q2, r)
        return r
    control = measured("ordinary_reuse", ordinary)
    return {"schema": VERSION, "contract_sha256": CONTRACT,
        "task": q, "reuse_task": q2, "initial": s,
        "failure": {"trial": wrong, "state": failed, "proposal_before": proposal_before, "proposal_after": proposal_after},
        "zero_fuel": {"search": zero, "state": paused},
        "continuation": {"prefix": prefix, "prefix_state": prefix_state, "suffix": continued, "state": continued_state},
        "success": {"search": positive, "state": learned},
        "arithmetic_boundary": boundary(q, positive["rows"][-1]),
        "reuse": {"search_baseline": baseline, "checked": reused, "ordinary": control},
        "residuals": ["fixed external grammar and supplied substitution", "finite function equality only",
            "no native semantic certificate", "no grammar completeness or general speedup",
            "human interpretation and customer utility untested"]}


def verify_artifact(a):
    if a["schema"] != VERSION or a["contract_sha256"] != CONTRACT:
        raise ValueError("artifact version drift")
    q, q2 = a["task"], a["reuse_task"]
    if q != task([2, 3, 1]) or q2 != task([2, 0, 6]) or a["initial"] != initial(q):
        raise ValueError("frozen input drift")
    s = a["initial"]
    f, z, c, p = a["failure"], a["zero_fuel"], a["continuation"], a["success"]
    if f["trial"]["candidate"] != [2, 3, 0] or f["state"] != update(q, s, f["trial"], "trial"):
        raise ValueError("failure update drift")
    if f["proposal_before"] != propose(q, s) or f["proposal_after"] != propose(q, f["state"]):
        raise ValueError("failure feedback missing")
    if z["search"]["fuel"] != 0 or z["state"] != update(q, s, z["search"], "search"):
        raise ValueError("timeout update drift")
    if c["prefix"]["fuel"] != 3 or c["prefix_state"] != update(q, s, c["prefix"], "search"):
        raise ValueError("prefix drift")
    if c["suffix"]["fuel"] != 340 or c["state"] != update(q, c["prefix_state"], c["suffix"], "search"):
        raise ValueError("continuation drift")
    if p["search"]["fuel"] != 343 or p["state"] != update(q, s, p["search"], "search"):
        raise ValueError("success update drift")
    if not p["state"]["words"] or c["state"]["words"] != p["state"]["words"]:
        raise ValueError("witness lost across continuation")
    if a["arithmetic_boundary"] != boundary(q, p["search"]["rows"][-1]):
        raise ValueError("zero or unit boundary drift")
    r = a["reuse"]
    verify_search(q2, r["search_baseline"])
    if r["search_baseline"]["start"] != 0 or r["search_baseline"]["fuel"] != 343:
        raise ValueError("baseline budget drift")
    word = p["state"]["words"][0]
    if r["checked"] != reuse(q, word, q2):
        raise ValueError("reuse provenance drift")
    verify_trial(q2, r["ordinary"])
    if r["ordinary"] != r["checked"]["trial"] or r["ordinary"]["status"] != "Accepted":
        raise ValueError("ordinary reuse comparison drift")


def load_bounded(path):
    with open(path, "rb") as stream:
        data = stream.read(LIMIT + 1)
    if len(data) > LIMIT:
        raise ValueError("input byte limit")
    return json.loads(data)


def save(path, data):
    path = Path(path)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_bytes(data)
    temp.replace(path)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--check")
    parser.add_argument("--output")
    parser.add_argument("--cost-output")
    args = parser.parse_args()
    bounded_runtime()
    started = time.perf_counter_ns()
    if args.check:
        value = measured("read_parse", load_bounded, args.check)
        measured("replay", verify_artifact, value)
    else:
        value = measured("build_total", build)
        data = measured("serialization", encode, value)
        restored = measured("parse", json.loads, data)
        measured("replay", verify_artifact, restored)
        if args.output:
            measured("file_save", save, args.output, data)
    costs = {"schema": "adva.external.finite-learner-cost.v0", "witness_sha256": digest(value),
        "work": dict(WORK), "work_total": sum(WORK.values()), "phase_ns": dict(TIMES),
        "elapsed_ns": time.perf_counter_ns() - started,
        "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python": sys.version.split()[0], "artifact_bytes": len(encode(value)),
        "exclusions": "imports, interpreter startup, design, network and cost-report write; build_total nests subphases, do not sum them"}
    if args.cost_output:
        save(args.cost_output, encode(costs))
    print(json.dumps(costs, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, MemoryError) as exc:
        print(json.dumps({"status": "Unknown", "reason": type(exc).__name__,
                          "detail": str(exc), "checkpoint": "not guaranteed for process resource interruption"}))
        sys.exit(2)
