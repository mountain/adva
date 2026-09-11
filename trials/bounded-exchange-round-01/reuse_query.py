#!/usr/bin/env python3
"""Index reuse query (child process, fresh interpreter).

Loads a saved word index, verifies source/rule bindings (re-hashing the
source text layers is charged to R), then answers the single token query.
Prints a JSON report with stage timings to stdout.
"""
import hashlib
import json
import sys
import time
import resource

sys.path.insert(0, "/Users/mingli/Adva/AEG/trials/bounded-exchange-round-01")
import reuse_rules as R  # noqa: E402


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main(index_path, sources):
    t = {"start": time.perf_counter()}
    t["load"] = time.perf_counter()
    with open(index_path, "rb") as f:
        idx = json.load(f)
    t["verify"] = time.perf_counter()
    bindings_ok = (idx["source_sha256"] == {k: sha(v) for k, v in sources.items()}
                   and idx["rule_sha256"] == sha(R.__file__))
    if not bindings_ok:
        print(json.dumps({"refused": True, "reason": "binding mismatch"}))
        return 1
    t["lookup"] = time.perf_counter()
    out = {}
    for side in ("left", "right"):
        entry = idx["sides"][side]["tokens"].get(R.TARGET)
        if entry is None:
            out[side] = None
            continue
        lines = idx["sides"][side]["lines"]
        loc, span = R.context_from_lines(lines)
        out[side] = {"frequency": entry["freq"], "rank": entry["rank"],
                     "locator": loc, "context": span}
    t["serialize"] = time.perf_counter()
    report = {
        "refused": False,
        "projection": out,
        "stage_seconds": {
            "load": t["verify"] - t["load"],
            "verify": t["lookup"] - t["verify"],
            "lookup": t["serialize"] - t["lookup"],
            "serialize": time.perf_counter() - t["serialize"],
        },
        "total_seconds": time.perf_counter() - t["start"],
        "peak_memory_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    print(json.dumps(report))
    return 0


if __name__ == "__main__":
    src = {
        "left": "/Users/mingli/Adva/AEG/trials/unrelated-pair-round-01/cookbook-layer.txt",
        "right": "/Users/mingli/Adva/AEG/trials/unrelated-pair-round-01/irs-layer.txt",
    }
    sys.exit(main(sys.argv[1], src))
