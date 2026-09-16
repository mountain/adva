"""Run the fixed Gold-pair check and one fresh-process replay."""
import argparse
import json
from pathlib import Path
import resource
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent


def limits(limits):
    def apply():
        resource.setrlimit(resource.RLIMIT_CPU, (limits["cpu_seconds"], limits["cpu_seconds"]))
        space = limits["address_space_mib"] * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (space, space))
        resource.setrlimit(resource.RLIMIT_FSIZE, (limits["max_output_bytes"], limits["max_output_bytes"]))
    return apply


def stable(evidence):
    return {k: v for k, v in evidence.items() if k not in ("timings", "cost")}


def main(output_dir):
    if output_dir.exists():
        raise SystemExit("refusing to overwrite " + str(output_dir))
    output_dir.mkdir(parents=True)
    contract = json.loads((HERE / "contract.json").read_text())
    cap = contract["limits"]
    runs = []
    started = time.monotonic()
    for name in ("primary", "replay"):
        output = output_dir / (name + ".json")
        t0 = time.monotonic()
        process = subprocess.run(
            [sys.executable, "-B", "-S", str(HERE / "calibrate.py"), "--output", str(output)],
            capture_output=True, text=True, timeout=cap["wall_seconds"],
            preexec_fn=limits(cap), check=False)
        evidence = json.loads(output.read_text()) if output.exists() else None
        runs.append({
            "name": name,
            "returncode": process.returncode,
            "wall_seconds": time.monotonic() - t0,
            "stdout": process.stdout,
            "stderr": process.stderr,
            "evidence": evidence
        })
        if process.returncode != 0:
            break
    equal = len(runs) == 2 and stable(runs[0]["evidence"]) == stable(runs[1]["evidence"])
    report = {
        "schema": "adva.external.gold-twin-close.execution.v0",
        "status": "Passed" if equal and all(x["returncode"] == 0 for x in runs) else "Failed",
        "base": contract["base"],
        "runs": [
            {k: v for k, v in run.items() if k != "evidence"}
            | {
                "host_work_units": (run["evidence"] or {}).get("cost", {}).get("host_work_units"),
                "peak_rss_kib": (run["evidence"] or {}).get("cost", {}).get("peak_rss_kib")
            }
            for run in runs
        ],
        "deterministic_replay_equal": equal,
        "aggregate_host_work_units": sum((x["evidence"] or {}).get("cost", {}).get("host_work_units", 0) for x in runs),
        "total_wall_seconds": time.monotonic() - started,
        "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "notes": [
            "Child and supervisor RSS are process high-water marks, not incremental memory.",
            "Research, authoring, source retrieval, network and later integration time are not measured."
        ]
    }
    (output_dir / "execution.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report["status"] == "Passed"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    raise SystemExit(0 if main(args.output_dir) else 1)
