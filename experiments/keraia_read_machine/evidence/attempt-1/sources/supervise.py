"""Run one frozen attempt and, only after success, one fresh replay.

Launch under an outer timeout/prlimit as documented in README.md. This file
never repairs a failure or increases a budget. Evidence directories are new.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def deterministic(record):
    result = copy.deepcopy(record)
    # Work counters are reproducible; host time and RSS are observations.
    result["cost"].pop("elapsed_seconds", None)
    result["cost"].pop("peak_rss_kib", None)
    for cut in result.get("cuts", []):
        cut.pop("timing", None)
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    contract = json.loads((HERE / "contract.json").read_text())
    limits = contract["limits"]
    sources = sorted(HERE.glob("*.py")) + [HERE / "contract.json"]
    manifest = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    # Freeze all implementation bytes before invoking the first evaluator.
    frozen = args.output_dir / "sources"
    frozen.mkdir()
    for path in sources:
        (frozen / path.name).write_bytes(path.read_bytes())
    record = {"status": "Running", "source_sha256": manifest, "runs": [],
              "outer_limits": {"wall_seconds": 100, "cpu_seconds": 95, "address_space_mib": 512}}
    def save():
        (args.output_dir / "execution.json").write_text(json.dumps(record, indent=2) + "\n")
    save()
    completed = []
    for name in ("primary", "fresh-replay"):
        output = args.output_dir / (name + ".json")
        command = ["prlimit", "--as=" + str(limits["address_space_mib"] * 1024**2),
                   "--cpu=" + str(limits["cpu_seconds"]),
                   "--fsize=" + str(limits["max_output_bytes"]), "--",
                   sys.executable, "-B", "-S", str(HERE / "calibrate.py"), "--output", str(output)]
        run = {"name": name, "command": command}
        started = time.monotonic()
        with (args.output_dir / (name + ".stdout.txt")).open("x") as stdout, (args.output_dir / (name + ".stderr.txt")).open("x") as stderr:
            try:
                result = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=limits["wall_seconds"], check=False)
                run["returncode"] = result.returncode
            except subprocess.TimeoutExpired:
                run["timeout"] = True
        run["elapsed_seconds"] = time.monotonic() - started
        record["runs"].append(run)
        save()
        if output.exists():
            result = json.loads(output.read_text())
            run["result_status"] = result["status"]
            run["evidence_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
        else:
            result = None
        if run.get("returncode") != 0 or result is None or result["status"] != "Passed":
            record["status"] = "StoppedAfterFailure"
            save()
            print(json.dumps(record))
            return 1
        if result["source_sha256"] != manifest:
            record["status"] = "SourceChanged"
            save()
            return 1
        completed.append(result)
        save()
    record["deterministic_replay_equal"] = deterministic(completed[0]) == deterministic(completed[1])
    record["status"] = "Passed" if record["deterministic_replay_equal"] else "ReplayMismatch"
    save()
    print(json.dumps(record))
    return 0 if record["status"] == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
