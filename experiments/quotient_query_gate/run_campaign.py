"""Bounded supervisor for quotient-query-gate v0."""
from __future__ import annotations

import hashlib
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(destination):
    destination.mkdir(parents=True, exist_ok=False)
    contract_path = HERE / "contract.json"
    contract = json.loads(contract_path.read_text())
    budget = contract["budget"]
    started = time.monotonic(); before = resource.getrusage(resource.RUSAGE_CHILDREN)
    launches = []

    def child(argv):
        if len(launches) >= budget["child_launches"]:
            raise RuntimeError("child launch budget")
        begin = time.monotonic()
        process = subprocess.run(argv, cwd=HERE, capture_output=True, text=True,
                                 timeout=min(10, budget["wall_seconds"] - (time.monotonic() - started)))
        launches.append({"argv": [Path(x).name if "/" in x else x for x in argv],
                         "exit": process.returncode, "elapsed_seconds": round(time.monotonic() - begin, 9),
                         "stderr": process.stderr})
        if process.returncode:
            raise RuntimeError("child failure: " + process.stderr)

    result = destination / "result.json"; optimized = destination / "optimized.json"; receipt = destination / "verification.json"
    child([sys.executable, str(HERE / "producer.py"), str(contract_path), str(result)])
    child([sys.executable, "-O", str(HERE / "producer.py"), str(contract_path), str(optimized)])
    if result.read_bytes() != optimized.read_bytes():
        raise RuntimeError("optimized mismatch")
    child([sys.executable, str(HERE / "verifier.py"), str(contract_path), str(result), str(receipt)])
    report = json.loads(result.read_text()); verified = json.loads(receipt.read_text())
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    telemetry = {
        "schema": "adva.quotient-query-gate.execution.v0", "status": verified["status"],
        "base_commit": contract["base_commit"], "launches": launches,
        "elapsed_seconds": round(time.monotonic() - started, 9),
        "child_cpu_seconds": round((after.ru_utime + after.ru_stime) - (before.ru_utime + before.ru_stime), 9),
        "child_max_rss_kib": after.ru_maxrss,
        "producer_candidate_families": report["producer_candidate_families"],
        "receiver_candidate_families": verified["receiver_candidate_families"],
        "gate_checks": sum(x["gate_checks"] for x in report["fixtures"]),
        "total_counted_work": report["producer_candidate_families"] + verified["receiver_candidate_families"] + sum(x["gate_checks"] for x in report["fixtures"]),
        "search_candidates": 0, "correction_replays": 0,
        "result_sha256": sha(result), "optimized_sha256": sha(optimized), "verification_sha256": sha(receipt)
    }
    if telemetry["total_counted_work"] > budget["candidate_families"] or telemetry["elapsed_seconds"] > budget["wall_seconds"]:
        telemetry["status"] = "Unknown"
    (destination / "execution.json").write_text(json.dumps(telemetry, indent=2, sort_keys=True) + "\n")
    print(json.dumps(telemetry, sort_keys=True))
    return 0 if telemetry["status"] == "Verified" else 3


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: run_campaign.py NEW_DIRECTORY")
    raise SystemExit(run(Path(sys.argv[1]).resolve()))
