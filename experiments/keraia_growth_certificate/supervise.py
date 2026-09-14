"""Run one primary and one fresh replay under explicit process limits."""
import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent


def limited(limits):
    def apply():
        resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds"], limits["cpu_seconds"]))
        space = limits["address_space_mib"] * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (space, space))
        resource.setrlimit(resource.RLIMIT_FSIZE, (limits["max_output_bytes"], limits["max_output_bytes"]))
    return apply


def deterministic(data):
    return {k: v for k, v in data.items() if k not in ("timings", "cost")}


def main(output_dir):
    if output_dir.exists():
        raise SystemExit("refusing to overwrite " + str(output_dir))
    output_dir.mkdir(parents=True)
    contract = json.loads((HERE / "contract.json").read_text())
    limits = contract["limits"]
    runs = []
    started = time.monotonic()
    for name in ("primary", "replay"):
        path = output_dir / (name + ".json")
        before = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        t0 = time.monotonic()
        completed = subprocess.run(
            [sys.executable, "-B", "-S", str(HERE / "calibrate.py"), "--output", str(path)],
            text=True, capture_output=True, timeout=limits["wall_seconds"],
            preexec_fn=limited(limits), check=False)
        after = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        runs.append({"name": name, "returncode": completed.returncode,
                     "wall_seconds": time.monotonic() - t0,
                     "max_rss_kib_upper": after,
                     "stdout": completed.stdout, "stderr": completed.stderr,
                     "evidence": json.loads(path.read_text()) if path.exists() else None})
        if completed.returncode != 0:
            break
    equal = (len(runs) == 2 and runs[0]["evidence"] is not None and runs[1]["evidence"] is not None
             and deterministic(runs[0]["evidence"]) == deterministic(runs[1]["evidence"]))
    report = {
        "schema": "adva.external.keraia-parametric-frame-recurrence.execution.v0",
        "status": "Passed" if equal and all(r["returncode"] == 0 for r in runs) else "Failed",
        "base": contract["base"],
        "runs": [{k: v for k, v in r.items() if k != "evidence"} for r in runs],
        "deterministic_replay_equal": equal,
        "total_wall_seconds": time.monotonic() - started,
        "aggregate_host_work_units": sum((r["evidence"] or {}).get("cost", {}).get("host_work_units", 0) for r in runs),
        "highest_child_rss_kib_upper": max((r["max_rss_kib_upper"] for r in runs), default=0),
        "supervisor_self_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "notes": [
            "Child RSS is an upper bound from RUSAGE_CHILDREN and may include prior child maxima.",
            "Phase times overlap and must not be summed.",
            "Research, authoring, network and later integration checks are not timed."
        ]
    }
    (output_dir / "execution.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report["status"] == "Passed"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if main(args.output_dir) else 1)
