#!/usr/bin/env python3
"""Project-original finite continuation experiment; Unknown v0.3.

ChatGPT (OpenAI), submitted through Mingli Yuan's account proxy.
No native semantic identities or operations are created here.
"""
import copy
import hashlib
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

PROFILE = "adva.research.continuation-binding.v0"
ROOT = Path(__file__).resolve().parent


def wire(x):
    return json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def digest(text):
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def decode(text):
    def unique(pairs):
        result = {}
        for k, v in pairs:
            if k in result:
                raise ValueError("duplicate key")
            result[k] = v
        return result
    if len(text.encode("utf-8")) > 65536:
        raise ValueError("wire bound")
    return json.loads(text, object_pairs_hook=unique)


def receive(expected, parent, text):
    # These immutable strings are receiver-selected; incoming digests do not
    # define the question. Each result retains the entire trusted checkpoint.
    result = {"outcome": "InvalidEvidence", "checkpoint": expected,
              "parent": parent, "semantic_delta": [], "permitted_effect": "none"}
    try:
        x = decode(text)
        if type(x) is not dict or set(x) != {
                "profile", "state", "parent_sha256", "before", "after", "candidate"}:
            raise ValueError("schema")
        if x["profile"] != PROFILE or x["state"] != expected:
            raise ValueError("question binding")
        p = decode(parent)
        if x["parent_sha256"] != digest(parent):
            raise ValueError("parent binding")
        if p["state_sha256"] != digest(expected) or p["outcome"] != "ImplementationFailure":
            raise ValueError("parent context")
        if type(x["before"]) is not int or type(x["after"]) is not int:
            raise ValueError("allowance type")
        if x["before"] != p["remaining"] or x["before"] < 1 or x["after"] != x["before"] - 1:
            raise ValueError("allowance continuity")
        s = decode(expected)
        c = x["candidate"]
        if type(c) is not dict or set(c) != {"program", "stage"}:
            raise ValueError("candidate schema")
        word, stage = c["program"], c["stage"]
        o = s["object"]
        if type(word) is not str or len(word) != o["width"] or set(word) - {"0", "1"}:
            raise ValueError("word syntax")
        if type(stage) is not int or stage < 0 or o["machine"].get(word) != stage:
            raise ValueError("event")
        if stage <= o["early"] or word in o["proposal"] or word not in s["unresolved"]:
            raise ValueError("not a delayed refutation")
        result.update(outcome="Counterexample", semantic_delta=[c], remaining=x["after"])
    except (ValueError, TypeError, KeyError, RecursionError) as e:
        result["reason"] = str(e)
    return result


def worker(mode):
    resource.setrlimit(resource.RLIMIT_AS, (128 * 1024**2,) * 2)
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_FSIZE, (1024**2,) * 2)
    request = decode(sys.stdin.read(65537))
    if mode == "fail":
        # An actual controlled process exit, with no candidate output.
        sys.stderr.write("controlled implementation failure before candidate production\n")
        return 17
    if mode == "propose":
        s = decode(request["state"])
        o = s["object"]
        word = "1" * (o["width"] - 1) + "0"
        response = {"profile": PROFILE, "state": request["state"],
                    "parent_sha256": digest(request["parent"]),
                    "before": 3, "after": 2,
                    "candidate": {"program": word, "stage": o["machine"][word]}}
    elif mode == "receive":
        if len(request["cases"]) != 12:
            raise ValueError("case bound")
        response = [receive(request["state"], request["parent"], c["wire"])
                    for c in request["cases"]]
    else:
        raise ValueError("mode")
    print(wire(response))
    return 0


def main(output):
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    metrics, results = [], []
    contract = json.loads((ROOT / "contract.json").read_text())
    (output / "contract.json").write_text(wire(contract) + "\n")

    def child(mode, request, path, expected_code=0):
        if len(metrics) >= 6 or time.perf_counter() - started >= 90:
            raise RuntimeError("campaign bound")
        path.mkdir()
        (path / "request.json").write_text(wire(request) + "\n")
        t = time.perf_counter()
        with (path / "stdout.json").open("wb") as out, (path / "stderr.txt").open("wb") as err:
            p = subprocess.run([sys.executable, "-B", "-S", str(Path(__file__).resolve()), mode],
                               input=wire(request).encode(), stdout=out, stderr=err, timeout=10)
        m = {"mode": mode, "returncode": p.returncode,
             "wall_seconds": time.perf_counter() - t,
             "children_rss_highwater_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss}
        metrics.append(m)
        (output / "metrics.json").write_text(wire(metrics) + "\n")
        if p.returncode != expected_code:
            raise RuntimeError("unexpected child exit; raw files retained")
        return (path / "stdout.json").read_text()

    for fixture in contract["instances"]:
        width, early, late = (fixture[k] for k in ("width", "early", "late"))
        folder = output / str(width)
        folder.mkdir()
        zero, delayed = "0" * width, "1" * (width - 1) + "0"
        state = wire({"object": {"width": width, "early": early,
                                 "machine": {zero: early, delayed: late}, "proposal": [zero]},
                      "history": [{"program": zero, "stage": early}],
                      "unresolved": [format(i, f"0{width}b") for i in range(1, 2**width)]})
        (folder / "checkpoint.json").write_text(state)
        raw = child("fail", {"state": state}, folder / "failure", 17)
        assert raw == ""
        parent = wire({"profile": PROFILE, "attempt": f"w{width}-attempt-1",
                       "outcome": "ImplementationFailure", "returncode": 17,
                       "state_sha256": digest(state), "remaining": 3, "semantic_delta": []})
        (folder / "parent.json").write_text(parent)
        # Reload from disk before dispatch into a fresh process.
        state = (folder / "checkpoint.json").read_text()
        parent = (folder / "parent.json").read_text()
        proposal = decode(child("propose", {"state": state, "parent": parent}, folder / "retry"))
        cases = [{"name": "valid", "wire": wire(proposal)}]
        for field in ("object", "history", "unresolved"):
            x = copy.deepcopy(proposal)
            changed = decode(state)
            changed[field] = {} if field == "object" else []
            x["state"] = wire(changed)
            cases.append({"name": "changed " + field, "wire": wire(x)})
        for name, key, val in (("wrong parent", "parent_sha256", "0" * 64),
                               ("fuel renewal", "before", 4),
                               ("extra field", "unrequested", True)):
            x = copy.deepcopy(proposal)
            x[key] = val
            cases.append({"name": name, "wire": wire(x)})
        for name, stage in (("wrong stage", late + 1), ("Boolean stage", True)):
            x = copy.deepcopy(proposal)
            x["candidate"]["stage"] = stage
            cases.append({"name": name, "wire": wire(x)})
        x = copy.deepcopy(proposal)
        del x["after"]
        cases.extend([{"name": "missing field", "wire": wire(x)},
                      {"name": "non-object", "wire": "[]"},
                      {"name": "malformed JSON", "wire": "{"}])
        received = decode(child("receive", {"state": state, "parent": parent, "cases": cases},
                                folder / "receiver"))
        assert received[0]["outcome"] == "Counterexample"
        assert received[0]["semantic_delta"] == [{"program": delayed, "stage": late}]
        assert received[0]["remaining"] == 2
        for i, result in enumerate(received):
            assert result["checkpoint"] == state and result["parent"] == parent
            if i:
                assert result["outcome"] == "InvalidEvidence" and result["semantic_delta"] == []
        results.append({"width": width, "accepted": 1, "refused_controls": len(cases) - 1,
                        "checkpoint_sha256": digest(state), "parent_sha256": digest(parent)})
    report = {"status": "Passed", "families": results, "child_processes": len(metrics),
              "campaign_wall_seconds": time.perf_counter() - started,
              "peak_children_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
              "search_candidates": 0, "timing_scope": "construction, file serialization, process startup, checking and controls combined; not separately measured"}
    (output / "result.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    if sys.argv[1] in ("fail", "propose", "receive"):
        sys.exit(worker(sys.argv[1]))
    main(Path(sys.argv[1]))
