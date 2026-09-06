"""External F7 evidence-applicability model; never native Adva authority."""
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

VERSION = "adva.external.structural-adjustment.v0"
CONTRACT = "a26b331839a7788bc5eee4b70bfb308a286549cd6c6fcc5b1f3d42f9031d4feb"
MAX_BYTES = 131072
RECIPE = {
    "name": "switch-reorganize-revise", "version": 0,
    "domain": "F7", "switch": "h(x)=f(x+s); old observation 0 moves to -s",
    "reorganize": "expand h into a*x^2+(2*a*s+b)*x+(a*s^2+b*s+c)",
    "revise": "k(x)=h(x)+d; derive a new value rather than copy old acceptance",
    "status": "externally supplied finite recipe; proposed vocabulary",
}
SPECS = [{"coefficients": [2, 3, 1], "shift": 1, "delta": 1},
         {"coefficients": [1, 2, 3], "shift": 2, "delta": 2}]


class Meter:
    def __init__(self):
        self.rows = 0
        self.metadata = 0
        self.deadline = time.monotonic() + 5

    def item(self, n=1):
        self.metadata += n
        if self.metadata > 20000 or time.monotonic() > self.deadline:
            raise RuntimeError("metadata or wall limit")

    def row(self):
        self.item()
        self.rows += 1
        if self.rows > 100:
            raise RuntimeError("row-check limit")


def encode(value):
    data = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()
    if len(data) > MAX_BYTES:
        raise ValueError("artifact size limit")
    return data


def digest(value):
    return hashlib.sha256(encode(value)).hexdigest()


def equal(actual, expected, message):
    # Canonical encoding distinguishes booleans from integers.
    if encode(actual) != encode(expected):
        raise ValueError(message)


def validate_spec(s, meter):
    meter.item(6)
    if not isinstance(s, dict) or set(s) != {"coefficients", "shift", "delta"}:
        raise ValueError("invalid spec fields")
    c = s["coefficients"]
    if not isinstance(c, list) or len(c) != 3:
        raise ValueError("three coefficients required")
    if any(type(x) is not int or not 0 <= x < 7 for x in c + [s["shift"], s["delta"]]):
        raise ValueError("canonical field scalars required")
    if s["delta"] == 0:
        raise ValueError("this revision contract requires nonzero delta")


def tasks(s):
    # External content references, not native semantic identities.
    return {role: {"schema": VERSION, "spec": s, "expression": role}
            for role in ("source", "shifted", "expanded", "revised")}


def initial(s):
    source = digest(tasks(s)["source"])
    observation = {"task": source, "x": 0, "value": s["coefficients"][2]}
    return {"active_task": source, "observations": [observation],
            "history": [{"event": "source_observation", "observation": observation}]}


def horner(c, x):
    a, b, d = c
    return ((a*x+b)*x+d) % 7


def expanded_coefficients(s):
    a, b, c = s["coefficients"]
    t = s["shift"]
    return [a, (2*a*t+b) % 7, (a*t*t+b*t+c) % 7]


def produce(s):
    """Construct an untrusted proposal using nested evaluation."""
    a, b, c = s["coefficients"]
    t, d = s["shift"], s["delta"]
    ids = {k: digest(v) for k, v in tasks(s).items()}
    ec = expanded_coefficients(s)
    location = (-t) % 7
    rows = [{"kind": "source", "task": ids["source"], "x": 0,
             "value": horner([a,b,c], 0)}]
    for x in range(7):
        old = (x+t) % 7
        rows.append({"kind": "switch", "x": x, "old_x": old,
                     "source": horner([a,b,c], old), "target": horner([a,b,c], x+t)})
    for x in range(7):
        rows.append({"kind": "reorganize", "x": x,
                     "before": horner([a,b,c], x+t), "after": horner(ec, x)})
    for x in range(7):
        h = horner(ec, x)
        rows.append({"kind": "revise", "x": x, "old": h,
                     "new": (h+d) % 7, "difference": d})
    blind = horner([a,b,c], t)
    rows.append({"kind": "blind_copy", "target": ids["shifted"], "x": 0,
                 "claimed": c, "actual": blind,
                 "verdict": "Refuted" if blind != c else "CoincidentValueOnly"})
    rows.append({"kind": "stale_value", "target": ids["revised"], "x": location,
                 "claimed": c, "actual": (horner(ec, location)+d) % 7, "verdict": "Refuted"})
    return {"schema": VERSION, "recipe": digest(RECIPE), "spec": deepcopy(s),
            "tasks": tasks(s), "expanded_coefficients": ec, "observation_location": location,
            "source_state": digest(initial(s)), "rows": rows}


def oracle_row(s, index):
    """Independent scalar specification: direct powers, not producer Horner."""
    a, b, c = s["coefficients"]
    t, d = s["shift"], s["delta"]
    def f(x):
        return (a*pow(x, 2, 7)+b*x+c) % 7
    def h(x):
        return (a*pow(x, 2, 7)+(2*a*t+b)*x+a*pow(t, 2, 7)+b*t+c) % 7
    if index == 0:
        return {"kind": "source", "task": digest(tasks(s)["source"]), "x": 0, "value": f(0)}
    if 1 <= index <= 7:
        x = index-1
        return {"kind": "switch", "x": x, "old_x": (x+t) % 7,
                "source": f((x+t) % 7), "target": h(x)}
    if 8 <= index <= 14:
        x = index-8
        return {"kind": "reorganize", "x": x, "before": f(x+t), "after": h(x)}
    if 15 <= index <= 21:
        x = index-15
        return {"kind": "revise", "x": x, "old": h(x), "new": (f(x+t)+d) % 7,
                "difference": ((f(x+t)+d)-h(x)) % 7}
    if index == 22:
        actual = h(0)
        return {"kind": "blind_copy", "target": digest(tasks(s)["shifted"]), "x": 0,
                "claimed": c, "actual": actual,
                "verdict": "Refuted" if actual != c else "CoincidentValueOnly"}
    if index == 23:
        return {"kind": "stale_value", "target": digest(tasks(s)["revised"]), "x": (-t) % 7,
                "claimed": c, "actual": (f(0)+d) % 7, "verdict": "Refuted"}
    raise ValueError("unknown obligation")


def validate_header(p, old, meter):
    validate_spec(p["spec"], meter)
    s = p["spec"]
    meter.item(24)
    if set(p) != {"schema", "recipe", "spec", "tasks", "expanded_coefficients",
                  "observation_location", "source_state", "rows"}:
        raise ValueError("proposal fields drift")
    equal(old, initial(s), "stale or altered source state")
    equal(p["schema"], VERSION, "version drift")
    equal(p["recipe"], digest(RECIPE), "recipe drift")
    equal(p["tasks"], tasks(s), "task or expression drift")
    equal(p["source_state"], digest(old), "source binding drift")
    # Header uses independently written coefficient arithmetic.
    a, b, c = s["coefficients"]
    t = s["shift"]
    equal(p["expanded_coefficients"], [a, (b+a*t+a*t) % 7, (c+t*(b+a*t)) % 7], "bad expansion")
    equal(p["observation_location"], (7-t) % 7, "wrong observation direction")
    if not isinstance(p["rows"], list) or len(p["rows"]) != 24:
        raise ValueError("missing or extra obligations")


def judge(p, old, fuel, meter):
    if type(fuel) is not int or not 0 <= fuel <= 24:
        raise ValueError("fuel outside finite contract")
    validate_header(p, old, meter)
    for i in range(fuel):
        meter.row()
        equal(p["rows"][i], oracle_row(p["spec"], i), "arithmetic evidence mismatch")
    receipt = {"proposal": digest(p), "source_state": digest(old), "fuel": fuel,
               "checked_rows": fuel, "state": deepcopy(old)}
    if fuel < 24:
        receipt.update(status="Unknown", reason="fuel_exhausted",
                       pending={"proposal": digest(p), "remaining_rows": list(range(fuel,24))})
        return receipt
    s = p["spec"]
    c, d, x = s["coefficients"][2], s["delta"], p["observation_location"]
    state = deepcopy(old)
    last = state["active_task"]
    for event, role, y, applicability in (
            ("switch", "shifted", c, "transported_coordinate"),
            ("reorganize", "expanded", c, "same_value_new_expression"),
            ("revise", "revised", (c+d) % 7, "new_value_derived_old_value_not_applicable")):
        tid = digest(p["tasks"][role])
        observation = {"task": tid, "x": x, "value": y}
        state["observations"].append(observation)
        state["history"].append({"event": event, "from": last, "to": tid,
                                 "certificate": digest(p), "applicability": applicability})
        last = tid
    state["active_task"] = last
    receipt.update(status="AcceptedAdjustment", reason="all_obligations_checked", pending=None, state=state)
    return receipt


def timed(times, name, fn, *args):
    start = time.perf_counter_ns()
    try:
        return fn(*args)
    finally:
        times[name] = times.get(name, 0) + time.perf_counter_ns()-start


def build(meter, times):
    cases = []
    for index, s in enumerate(SPECS):
        validate_spec(s, meter)
        p = timed(times, "construction", produce, s)
        old = initial(s)
        receipt = timed(times, "primary_verification" if index == 0 else "fresh_reuse_verification",
                        judge, p, old, 24, meter)
        cases.append({"proposal": p, "before": old, "receipt": receipt})
    p, old = cases[0]["proposal"], cases[0]["before"]
    pending = [timed(times, "pending_verification", judge, p, old, n, meter) for n in (0,2)]
    return {"schema": VERSION, "contract_sha256": CONTRACT, "recipe": RECIPE,
            "cases": cases, "pending": pending,
            "residuals": ["external fixed recipe", "no incremental speedup claim",
                          "no native semantic identities", "hard-stop checkpoint not guaranteed"]}


def verify_artifact(a, meter):
    meter.item(10)
    if set(a) != {"schema", "contract_sha256", "recipe", "cases", "pending", "residuals"}:
        raise ValueError("artifact fields drift")
    equal(a["schema"], VERSION, "schema drift")
    equal(a["contract_sha256"], CONTRACT, "contract drift")
    equal(a["recipe"], RECIPE, "recipe changed")
    equal(a["residuals"], ["external fixed recipe", "no incremental speedup claim",
                           "no native semantic identities", "hard-stop checkpoint not guaranteed"], "residual erased")
    if len(a["cases"]) != 2 or len(a["pending"]) != 2:
        raise ValueError("case coverage drift")
    for s, case in zip(SPECS, a["cases"]):
        equal(case["proposal"]["spec"], s, "fixture drift")
        expected = judge(case["proposal"], case["before"], 24, meter)
        equal(case["receipt"], expected, "receipt or history drift")
    case = a["cases"][0]
    for fuel, r in zip((0,2), a["pending"]):
        expected = judge(case["proposal"], case["before"], fuel, meter)
        equal(r, expected, "pending state was promoted")


def load_file(path):
    with open(path, "rb") as stream:
        data = stream.read(MAX_BYTES+1)
    if len(data) > MAX_BYTES:
        raise ValueError("input byte limit")
    return json.loads(data)


def save(path, data):
    path = Path(path)
    temporary = path.with_suffix(path.suffix+".tmp")
    temporary.write_bytes(data)
    temporary.replace(path)


def limits():
    resource.setrlimit(resource.RLIMIT_AS, (268435456, 268435456))
    resource.setrlimit(resource.RLIMIT_CPU, (5,5))
    def alarm(*_):
        raise RuntimeError("wall limit")
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(5)


def main():
    parser = argparse.ArgumentParser(__doc__)
    parser.add_argument("--check")
    parser.add_argument("--output")
    parser.add_argument("--cost-output")
    args = parser.parse_args()
    limits()
    meter, times = Meter(), {}
    start = time.perf_counter_ns()
    if args.check:
        artifact = timed(times, "read_parse", load_file, args.check)
        timed(times, "replay", verify_artifact, artifact, meter)
    else:
        artifact = timed(times, "build_total", build, meter, times)
        data = timed(times, "serialization", encode, artifact)
        restored = timed(times, "parse", json.loads, data)
        timed(times, "replay", verify_artifact, restored, meter)
        if args.output:
            timed(times, "witness_save", save, args.output, data)
    cost = {"schema": "adva.external.structural-adjustment-cost.v0", "witness_sha256": digest(artifact),
            "phase_ns": times, "elapsed_ns": time.perf_counter_ns()-start,
            "row_checks": meter.rows, "metadata_items": meter.metadata,
            "peak_rss_kib_linux": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "artifact_bytes": len(encode(artifact)), "python": sys.version.split()[0],
            "exclusions": "imports, startup, design, network and cost-report write; build_total nests subphases"}
    if args.cost_output:
        save(args.cost_output, encode(cost))
    print(json.dumps(cost, sort_keys=True))


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, MemoryError) as exc:
        print(json.dumps({"status": "Unknown", "reason": str(exc),
                          "checkpoint": "not guaranteed at process resource interruption"}))
        sys.exit(2)
