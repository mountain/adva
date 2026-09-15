"""One fixture preflight, one primary and one fresh replay; stop at any failure."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from common import HERE, sources, manifest


def deterministic(value):
    result = copy.deepcopy(value)
    for key in ("elapsed_seconds", "peak_rss_kib"):
        result["cost"].pop(key, None)
    for cut in result["cuts"]:
        cut.pop("timings", None)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=False)
    limits = json.loads((HERE / "contract.json").read_text())["limits"]
    frozen_manifest = manifest()
    for name, path in sources().items():
        target = out / "sources" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(path.read_bytes())
    record = {"status": "Running", "source_sha256": frozen_manifest, "runs": [],
              "outer_limits": {"wall_seconds": 140, "cpu_seconds": 130,
                               "address_space_mib": 512}}

    def save():
        (out / "execution.json").write_text(json.dumps(record, indent=2) + "\n")
    save()
    results = []
    for name in ("preflight", "primary", "fresh-replay"):
        preflight = name == "preflight"
        wall = limits["preflight_wall_seconds"] if preflight else limits["wall_seconds"]
        cpu = 10 if preflight else limits["cpu_seconds"]
        output = out / (name + ".json")
        command = ["prlimit", "--as=" + str(limits["address_space_mib"] * 1024**2),
                   "--cpu=" + str(cpu), "--fsize=" + str(limits["max_output_bytes"]), "--",
                   sys.executable, "-B", "-S", str(HERE / "calibrate.py"), "--output", str(output)]
        if preflight:
            command.append("--preflight")
        row = {"name": name, "command": command}
        started = time.monotonic()
        with (out / (name + ".stdout.txt")).open("x") as stdout, (out / (name + ".stderr.txt")).open("x") as stderr:
            try:
                completed = subprocess.run(command, stdout=stdout, stderr=stderr, timeout=wall, check=False)
                row["returncode"] = completed.returncode
            except subprocess.TimeoutExpired:
                row["timeout"] = True
        row["elapsed_seconds"] = time.monotonic() - started
        result = json.loads(output.read_text()) if output.exists() else None
        row["result_status"] = result["status"] if result else "Missing"
        record["runs"].append(row)
        if output.exists():
            row["sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
        if (row.get("returncode") != 0 or result is None or result["status"] != "Passed"
                or result["source_sha256"] != frozen_manifest):
            record["status"] = "StoppedAfterFailure"
            save()
            print(json.dumps(record))
            return 1
        if not preflight:
            results.append(result)
        save()
        print(json.dumps({"run": name, "status": "Passed", "seconds": row["elapsed_seconds"]}), flush=True)
    record["deterministic_replay_equal"] = deterministic(results[0]) == deterministic(results[1])
    record["status"] = "Passed" if record["deterministic_replay_equal"] else "ReplayMismatch"
    record["total_child_work"] = sum(json.loads((out / (r["name"] + ".json")).read_text())["cost"]["host_work"] for r in record["runs"])
    save()
    print(json.dumps({"status": record["status"], "total_child_work": record["total_child_work"]}))
    return 0 if record["status"] == "Passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
