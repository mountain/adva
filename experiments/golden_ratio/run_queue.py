#!/usr/bin/env python3
"""Bounded queue runner for the golden-ratio research line.

What this program is: a bounded verifier and dispatcher. It runs the declared
checks, reports which queue items are backed by checks present in the retained
witness, and names the next executable item.

What it is not: it never edits the queue, never closes an item, never invents a
research step and never treats its own report as evidence. A status change is an
explicit edit made by an agent or a person together with the checks that justify
it, so a passing loop is not progress by itself.

Usage:
  python3 -S experiments/golden_ratio/run_queue.py --rounds 2 --output target/queue-run.json

Exit codes: 0 all requested rounds passed, 2 invalid, 3 Unknown (a declared
bound must stop the run rather than be exceeded silently).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

QUEUE = "experiments/golden_ratio/queue.json"
CALIBRATION = "experiments/golden_ratio/calibration.py"
EVIDENCE = "experiments/golden_ratio/evidence.json"
BUDGET = {"max_rounds": 4, "max_seconds": 120.0, "child_timeout_seconds": 60}


class Bound(Exception):
    """A declared bound stopped the run: Unknown, never partial acceptance."""


class Invalid(Exception):
    """A checked requirement failed."""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run_command(command: list[str], cwd: Path) -> tuple[int, str]:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        timeout=BUDGET["child_timeout_seconds"],
        check=False,
    )
    return completed.returncode, (completed.stdout + completed.stderr)[-2000:]


def main() -> int:
    parser = argparse.ArgumentParser(description="bounded golden-ratio queue runner")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--rounds", type=int, default=1)
    parser.add_argument("--output", required=True)
    arguments = parser.parse_args()

    root = Path(arguments.root).resolve()
    destination = Path(arguments.output)
    if destination.exists():
        print(json.dumps({"status": "Invalid", "reason": "output path already exists"}))
        return 2
    if not destination.parent.is_dir():
        print(json.dumps({"status": "Invalid", "reason": "output parent directory does not exist"}))
        return 2
    if not 1 <= arguments.rounds <= BUDGET["max_rounds"]:
        print(json.dumps({"status": "Unknown", "reason": "requested rounds exceed the bound"}))
        return 3

    started = time.perf_counter()
    report: dict = {
        "schema": "adva.golden-ratio-queue-run.research",
        "version": 0,
        "status": "Invalid",
        "reason": None,
        "authority": "verification-and-dispatch-only; the queue is never edited here",
        "rounds": [],
    }
    try:
        queue_bytes = (root / QUEUE).read_bytes()
        queue = json.loads(queue_bytes.decode("utf-8"))
        report["queue"] = {"path": QUEUE, "sha256": hashlib.sha256(queue_bytes).hexdigest()}
        for round_index in range(arguments.rounds):
            if time.perf_counter() - started > BUDGET["max_seconds"]:
                raise Bound("wall-clock budget exhausted")
            fresh = destination.parent / f"queue-round-{round_index}.json"
            if fresh.exists():
                fresh.unlink()
            code, output = run_command(
                [sys.executable, "-S", str(root / CALIBRATION), "--output", str(fresh)],
                root,
            )
            if code != 0:
                raise Invalid(f"round {round_index}: calibration exited {code}: {output[-300:]}")
            calibration = json.loads(fresh.read_text(encoding="utf-8"))
            check_names = calibration.get("check_names", [])
            witness = json.loads((root / EVIDENCE).read_text(encoding="utf-8"))
            report["rounds"].append(
                {
                    "round": round_index,
                    "calibration_status": calibration["status"],
                    "checks": calibration["cost"]["checks"],
                    "witness_matches_fresh": [
                        name
                        for name in witness.get("check_names", [])
                        if name not in check_names
                    ]
                    == [],
                }
            )
            fresh.unlink()
        backed = []
        pending = []
        for item in queue["items"]:
            prefix = item.get("evidence_check_prefix")
            matches = (
                [name for name in check_names if name.startswith(prefix)] if prefix else []
            )
            entry = {
                "id": item["id"],
                "kind": item["kind"],
                "status": item["status"],
                "backed_checks": len(matches),
            }
            if item["kind"] == "executable" and item["status"] == "Open" and not matches:
                pending.append(entry)
            else:
                backed.append(entry)
        report["items"] = {"backed": backed, "pending": pending}
        report["next_item"] = pending[0] if pending else None
        report["stop_condition"] = (
            "no executable item is pending; remaining items are documentary or human"
            if not pending
            else "continue: the next item above is unbacked"
        )
        report["status"] = "Passed"
    except Bound as error:
        report.update(status="Unknown", reason=str(error))
    except (Invalid, KeyError, ValueError, OSError, subprocess.TimeoutExpired) as error:
        report.update(status="Invalid", reason=f"{type(error).__name__}: {error}"[:400])
    finally:
        report["cost"] = {"wall_seconds": time.perf_counter() - started}
        destination.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(
            json.dumps(
                {
                    "status": report["status"],
                    "next_item": report.get("next_item"),
                    "stop_condition": report.get("stop_condition"),
                    "cost": report["cost"],
                },
                ensure_ascii=False,
            )
        )
    return {"Passed": 0, "Invalid": 2, "Unknown": 3}[report["status"]]


if __name__ == "__main__":
    sys.exit(main())
