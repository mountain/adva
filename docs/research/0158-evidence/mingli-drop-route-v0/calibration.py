#!/usr/bin/env python3
"""An external finite model of one proposed reading; never calls eval or Adva."""
import argparse
import copy
import hashlib
import itertools
import json
import resource
import signal
import time
from pathlib import Path


class Exhausted(Exception):
    pass


class Invalid(Exception):
    pass


def require(value, message):
    if not value:
        raise Invalid(message)


def small_int(value, hi=6):
    return type(value) is int and 0 <= value <= hi


def encode(value):
    return [(value >> i) & 1 for i in range(3)]


def packet(value):
    return {"label": "external-thread-demo", "scope": "F7:t=1:y=1:v0",
            "kind": "root-offer", "value": value, "bits": encode(value)}


def spec(name, value=1, order=None, fuel=4):
    return {"name": name, "thread": packet(value),
            "need": {"label": "external-receiver-demo", "scope": "F7:t=1:y=1:v0",
                     "kind": "root-receiver", "target": 1, "square": 1},
            "order": order or ["offer", "need"], "grant": fuel,
            "profile": "route-profile-v0", "program": "(switch swap break)"}


def fixtures():
    cases = [spec("aligned"), spec("reversed", 6, ["need", "offer"], 6),
             spec("false_thread", 2), spec("missing_thread"),
             spec("unspecified_dual"), spec("stale_scope"), spec("bad_encoding"),
             spec("zero_fuel", fuel=0), spec("fuel_before_drop", fuel=3),
             spec("unbound_interpretation"), spec("unrecognized_form")]
    cases[3]["thread"] = None
    cases[4]["need"]["kind"] = "unspecified-dual"
    cases[5]["thread"]["scope"] = "F7:t=5:y=3:v0"
    cases[6]["thread"]["bits"] = [0, 1, 0]
    cases[9]["profile"] = None
    cases[10]["program"] = "(switch swap drop)"
    return cases


def interpret(source):
    result = {"status": "Active", "live_frame": True, "order": list(source["order"]),
              "result": None, "archive": [], "history": [], "checked": False,
              "grant": source["grant"], "spent": 0, "remaining": source["grant"]}

    def event(name):
        if result["remaining"] < 1:
            raise Exhausted()
        result["spent"] += 1
        result["remaining"] -= 1
        result["history"].append(name)

    if source["profile"] != "route-profile-v0":
        result["status"] = "Surface:MissingInterpretation"
        return result
    form = source["program"].strip()
    if (not form.startswith("(") or not form.endswith(")") or form.count("(") != 1
            or form.count(")") != 1 or form[1:-1].split() != ["switch", "swap", "break"]):
        result["status"] = "Surface:UnsupportedForm"
        return result
    if source["thread"] is None:
        result["status"] = "Surface:MissingThread"
        return result
    if source["need"]["kind"] != "root-receiver":
        result["status"] = "Surface:UnspecifiedDual"
        return result
    if source["thread"]["scope"] != source["need"]["scope"]:
        result["status"] = "Blocked:ScopeMismatch"
        return result
    try:
        # This finite supplied profile permits at most one exchange.
        for _ in range(2):
            event("switch")
            if result["order"] == ["need", "offer"]:
                event("swap")
                result["order"].reverse()
            else:
                require(result["order"] == ["offer", "need"], "bad endpoint order")
                event("break")
                break
        event("cut-check")
        p = source["thread"]
        x = p["value"]
        good = (small_int(x) and p["kind"] == "root-offer" and p["bits"] == encode(x)
                and x*x % 7 == source["need"]["square"]
                and (2*x*x+6) % 7 == source["need"]["target"])
        if not good:
            result["status"] = "Refuted:ThreadDoesNotFill"
            return result
        result["checked"] = True
        event("drop")
        result["archive"] = [{"source": copy.deepcopy(source),
                              "evidence": {"x": x, "square": x*x % 7,
                                           "target": (2*x*x+6) % 7}}]
        result["live_frame"] = False
        result["order"] = []
        result["result"] = x
        result["status"] = "Returned"
    except Exhausted:
        result["status"] = "Unknown:Fuel"
    return result


def verify_receipt(source, out, tick):
    """A separate specification check: no call to the interpreter or encoder."""
    tick()
    history = out["history"]
    require(out["grant"] == source["grant"], "grant changed")
    require(type(out["spent"]) is int and out["spent"] == len(history), "unaccounted event")
    require(out["spent"] + out["remaining"] == out["grant"] and out["remaining"] >= 0, "fuel reset")
    if out["status"].startswith("Surface:") or out["status"].startswith("Blocked:"):
        require(out["live_frame"] and history == [] and out["archive"] == [] and out["result"] is None,
                "preflight changed active data")
        return
    p = source["thread"]
    require(p is not None and source["profile"] == "route-profile-v0", "absent binding")
    order = list(source["order"])
    cut_seen = False
    phase = "route"
    for i, event in enumerate(history):
        tick()
        if event == "switch":
            require(phase == "route", "switch after return")
        elif event == "swap":
            require(phase == "route" and i and history[i-1] == "switch", "ungated swap")
            order = [order[1], order[0]]
        elif event == "break":
            require(phase == "route" and order == ["offer", "need"] and i and history[i-1] == "switch",
                    "unready break")
            phase = "continuation"
        elif event == "cut-check":
            require(phase == "continuation", "cut before continuation")
            phase = "checked"
            cut_seen = True
        elif event == "drop":
            require(phase == "checked" and i == len(history)-1, "unchecked or repeated drop")
            phase = "returned"
        else:
            raise Invalid("unknown event")
    x = p["value"]
    wellformed = (small_int(x) and p["kind"] == "root-offer" and len(p["bits"]) == 3
                  and all(type(b) is int and b in (0, 1) for b in p["bits"]))
    decoded = sum(b*w for b, w in zip(p["bits"], [1, 2, 4])) if wellformed else None
    sq = sum(x for _ in range(x)) % 7 if small_int(x) else None
    valid = (wellformed and decoded == x and sq == source["need"]["square"]
             and (sq+sq+6) % 7 == source["need"]["target"]
             and p["scope"] == source["need"]["scope"])
    require(out["checked"] == bool(cut_seen and valid), "unchecked assertion")
    if out["status"] == "Returned":
        require(phase == "returned" and valid, "unverified return")
        require(not out["live_frame"] and out["order"] == [] and out["result"] == x, "bad return")
        require(out["archive"] == [{"source": source, "evidence": {"x": x, "square": sq,
                                                                  "target": (sq+sq+6) % 7}}], "archive loss")
    else:
        require(phase != "returned" and out["live_frame"] and out["archive"] == []
                and out["result"] is None and out["order"] == order, "uncommitted frame erased")
        if out["status"] == "Unknown:Fuel":
            require(out["remaining"] == 0, "unexplained exhaustion")
        else:
            require(out["status"] == "Refuted:ThreadDoesNotFill" and cut_seen and not valid,
                    "unverified refutation")


def all_checks(tick):
    results = []
    expected = ["Returned", "Returned", "Refuted:ThreadDoesNotFill", "Surface:MissingThread",
                "Surface:UnspecifiedDual", "Blocked:ScopeMismatch", "Refuted:ThreadDoesNotFill",
                "Unknown:Fuel", "Unknown:Fuel", "Surface:MissingInterpretation", "Surface:UnsupportedForm"]
    for source, status in zip(fixtures(), expected):
        tick()
        out = interpret(source)
        require(out["status"] == status, "unexpected fixture: " + source["name"])
        verify_receipt(source, out, tick)
        results.append({"source": source, "receipt": out})
    controls = []
    source, good = results[0]["source"], results[0]["receipt"]
    for name in ["archive_erasure", "unchecked_drop", "duplicate_drop", "fuel_reset", "result_substitution"]:
        out = copy.deepcopy(good)
        if name == "archive_erasure": out["archive"] = []
        if name == "unchecked_drop":
            out["history"].remove("cut-check"); out["spent"] -= 1; out["remaining"] += 1
        if name == "duplicate_drop":
            out["history"].append("drop"); out["spent"] += 1; out["remaining"] -= 1
        if name == "fuel_reset": out["remaining"] = out["grant"]
        if name == "result_substitution": out["result"] = 6
        try:
            verify_receipt(source, out, tick)
        except Invalid as exc:
            controls.append({"name": name, "status": "Rejected", "reason": str(exc)})
        else: raise Invalid("accepted corruption: " + name)
    logic = {"rules_checked": 0, "valid": 0, "invalid": 0, "checker_override": "RejectedAsData"}
    for premise, conclusion in itertools.product(range(16), repeat=2):
        tick()
        proposed = premise & (~conclusion & 15) == 0
        rows = [(bool(premise & (1 << i)), bool(conclusion & (1 << i))) for i in range(4)]
        checked = all((not a) or b for a, b in rows)
        require(proposed == checked, "truth-mask disagreement")
        logic["valid" if checked else "invalid"] += 1
        logic["rules_checked"] += 1
    require(logic["valid"] == 81, "Boolean rule family count")
    # Candidate status is ordinary data and cannot replace the fixed test.
    candidate = {"premise": 15, "conclusion": 0, "claimed_checker": "always-accept"}
    counterexample = next(i for i in range(4) if candidate["premise"] & (1<<i)
                          and not candidate["conclusion"] & (1<<i))
    logic["override_counterexample_valuation"] = counterexample
    codec = []
    for x in range(7):
        tick()
        bits = encode(x)
        require(sum(b*w for b,w in zip(bits, [1,2,4])) == x, "codec mismatch")
        codec.append({"x": x, "bits": bits})
    encoded = json.dumps(results, sort_keys=True)
    for row in json.loads(encoded):
        verify_receipt(row["source"], row["receipt"], tick)
    return {"status": "PassedFiniteCalibration", "cases": results, "corruption_controls": controls,
            "logic_as_data": logic, "codec": codec, "serialized_receipt_replay": "Passed",
            "actual_route_surface": "AwaitingMingliThread; illustrative root is not a supplied user thread"}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()
    root = Path(__file__).parent
    contract_bytes = (root / "contract.json").read_bytes()
    contract = json.loads(contract_bytes)
    bounds = contract["limits"]
    resource.setrlimit(resource.RLIMIT_AS, (bounds["address_space_mib"]*1024**2,)*2)
    resource.setrlimit(resource.RLIMIT_CPU, (bounds["cpu_seconds"],)*2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (bounds["file_bytes"],)*2)
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(Exhausted()))
    signal.alarm(bounds["wall_seconds"])
    used = 0
    def tick():
        nonlocal used
        used += 1
        if used > bounds["logical_units"]: raise Exhausted()
    start = time.monotonic()
    try:
        report = all_checks(tick)
    except Exhausted:
        report = {"status": "Unknown:GlobalBudget", "partial_evidence_promoted": False}
    except (Invalid, AssertionError) as exc:
        report = {"status": "ImplementationFailure", "reason": str(exc)}
    report["source_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    report["contract_sha256"] = hashlib.sha256(contract_bytes).hexdigest()
    report["costs"] = {"logical_units": used, "elapsed_before_checkpoint_seconds": time.monotonic()-start,
                       "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    data = (json.dumps(report, indent=2, sort_keys=True)+"\n").encode()
    require(len(data) <= bounds["file_bytes"], "checkpoint size")
    with args.output.open("xb") as f: f.write(data)
    signal.alarm(0)
    print(json.dumps({"status": report["status"], "cases": len(report.get("cases", [])),
                      "controls": len(report.get("corruption_controls", [])),
                      "logic": report.get("logic_as_data"), "costs": report["costs"],
                      "output_bytes": len(data)}))
    return 0 if report["status"] == "PassedFiniteCalibration" else 1


if __name__ == "__main__":
    raise SystemExit(main())
