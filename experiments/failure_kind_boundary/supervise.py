#!/usr/bin/env python3
"""Run the failure-kind calibration twice under finite host limits."""

from __future__ import annotations

import argparse
import json
import resource
import subprocess
import sys
import time
from pathlib import Path


CPU_SECONDS = 25
ADDRESS_SPACE = 256 * 1024 * 1024
FILE_SIZE = 1024 * 1024


def limits() -> None:
    resource.setrlimit(resource.RLIMIT_CPU, (CPU_SECONDS, CPU_SECONDS))
    resource.setrlimit(resource.RLIMIT_AS, (ADDRESS_SPACE, ADDRESS_SPACE))
    resource.setrlimit(resource.RLIMIT_FSIZE, (FILE_SIZE, FILE_SIZE))


def run_once(script: Path, contract: Path, output: Path) -> dict[str, object]:
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-B", "-S", str(script), "--contract", str(contract), "--output", str(output)],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
        text=True,
        preexec_fn=limits,
    )
    wall = time.perf_counter() - start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    if proc.returncode != 0:
        raise RuntimeError(f"child failed ({proc.returncode}): {proc.stderr[:1000]}")
    if len(proc.stdout.encode()) + len(proc.stderr.encode()) > FILE_SIZE:
        raise RuntimeError("child output limit exceeded")
    evidence = json.loads(output.read_text(encoding="utf-8"))
    return {
        "returncode": proc.returncode,
        "wall_seconds": wall,
        "peak_rss_kib": after.ru_maxrss,
        "user_cpu_seconds": after.ru_utime - before.ru_utime,
        "system_cpu_seconds": after.ru_stime - before.ru_stime,
        "host_work_units": evidence["host_work_units"],
        "stdout": proc.stdout,
        "stderr": proc.stderr,
    }


def normalized(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    args.output_dir.mkdir(parents=True, exist_ok=True)
    primary_path = args.output_dir / "primary.json"
    replay_path = args.output_dir / "replay.json"
    total_start = time.perf_counter()
    primary = run_once(root / "calibrate.py", root / "contract.json", primary_path)
    replay = run_once(root / "calibrate.py", root / "contract.json", replay_path)
    same = normalized(primary_path) == normalized(replay_path)
    if not same:
        raise RuntimeError("deterministic replay mismatch")
    report = {
        "schema": "adva.external.failure-kind-boundary.execution.v0",
        "base": normalized(primary_path)["base"],
        "status": "Passed",
        "deterministic_replay_equal": same,
        "runs": [
            {"name": "primary", **primary},
            {"name": "replay", **replay},
        ],
        "aggregate_host_work_units": primary["host_work_units"] + replay["host_work_units"],
        "total_wall_seconds": time.perf_counter() - total_start,
        "supervisor_peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "notes": [
            "Child and supervisor RSS are process high-water marks, not incremental memory.",
            "Research, authoring, source retrieval, network and later integration time are not measured."
        ],
    }
    (args.output_dir / "execution.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
