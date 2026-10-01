#!/usr/bin/env python3
"""Run the frozen read-only terminal-resolution receiving cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import resource
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECEIVER = HERE / "receiver.py"
DEFAULT_ARCHIVE = ROOT / "experiments" / "recovery_receipt_application" / "evidence" / "attempt-1"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_new(path: Path, value: object | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else canonical(value)
    with path.open("xb") as stream:
        stream.write(raw)


def file_sha(path: Path) -> str:
    return digest(path.read_bytes())


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT.resolve()))
    except ValueError:
        return "external-archive/" + path.name


def query_for(source: Path, recovery: Path, terminal: Path) -> dict[str, object]:
    source_value = json.loads(source.read_bytes())
    return {
        "profile": "terminal-resolution-query-v0",
        "attempt_id": source_value["attempt_id"],
        "pair_digest": source_value["pair_digest"],
        "source_pending_sha256": file_sha(source),
        "recovery_receipt_sha256": file_sha(recovery),
        "terminal_sha256": file_sha(terminal),
    }


def run_receiver(case_dir: Path, query: Path, source: Path, recovery: Path, terminal: Path) -> tuple[dict[str, object], dict[str, object]]:
    before = {
        display_path(path): file_sha(path)
        for path in (query, source, recovery, terminal)
        if path.exists()
    }
    started = time.monotonic()
    completed = subprocess.run(
        [
            sys.executable,
            str(RECEIVER),
            "--query",
            str(query),
            "--source-pending",
            str(source),
            "--recovery-receipt",
            str(recovery),
            "--terminal",
            str(terminal),
        ],
        check=True,
        timeout=1,
        capture_output=True,
    )
    elapsed = time.monotonic() - started
    if len(completed.stdout) > 4096 or len(completed.stderr) > 4096:
        raise AssertionError("OutputLimit")
    receipt = json.loads(completed.stdout)
    after = {
        display_path(path): file_sha(path)
        for path in (query, source, recovery, terminal)
        if path.exists()
    }
    if before != after:
        raise AssertionError("ArchiveMutation")
    write_new(case_dir / "receipt.json", receipt)
    return receipt, {
        "seconds": elapsed,
        "stdout_bytes": len(completed.stdout),
        "stderr_bytes": len(completed.stderr),
        "input_sha256_before": before,
        "input_sha256_after": after,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--archive-root", type=Path, default=DEFAULT_ARCHIVE)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("output already exists")
    args.output.mkdir(parents=True)
    start = time.monotonic()
    assertions = 0
    processes = 0
    work_units = 0
    cases: list[dict[str, object]] = []

    archive = args.archive_root
    triples = {
        "completed-alpha": (
            archive / "parent" / "alpha-positive" / "ledger.json",
            archive / "parent" / "alpha-positive" / "receipt.json",
            archive / "application" / "alpha" / "ledger.json",
            "ResolutionVerified",
            "completed",
        ),
        "cancelled-gamma": (
            archive / "parent" / "gamma-negative" / "ledger.json",
            archive / "parent" / "gamma-negative" / "receipt.json",
            archive / "application" / "gamma" / "ledger.json",
            "ResolutionVerified",
            "cancelled",
        ),
        "post-replace-delta": (
            archive / "parent" / "delta-positive" / "ledger.json",
            archive / "parent" / "delta-positive" / "receipt.json",
            archive / "application" / "delta-crash" / "ledger.json",
            "ResolutionVerified",
            "completed",
        ),
    }

    base_queries: dict[str, Path] = {}
    for name, (source, recovery, terminal, expected, state) in triples.items():
        case_dir = args.output / "cases" / name
        query_path = case_dir / "query.json"
        write_new(query_path, query_for(source, recovery, terminal))
        base_queries[name] = query_path
        receipt, metrics = run_receiver(case_dir, query_path, source, recovery, terminal)
        processes += 1
        work_units += int(receipt["work_units"])
        for condition in (
            receipt["outcome"] == expected,
            receipt["state"] == state,
            receipt["archive_mutated"] is False,
            receipt["target_processes"] == 0,
            all(receipt[key] is False for key in (
                "effect_authority", "retry_authority", "refund_authority",
                "mutation_authority", "native_authority", "free_authority"
            )),
            metrics["input_sha256_before"] == metrics["input_sha256_after"],
        ):
            assert condition
            assertions += 1
        cases.append({"case": name, "receipt": receipt, "metrics": metrics})

    alpha = triples["completed-alpha"]
    gamma = triples["cancelled-gamma"]
    alpha_query = json.loads(base_queries["completed-alpha"].read_bytes())

    controls: list[tuple[str, Path, Path, Path, Path, str]] = []

    missing_dir = args.output / "cases" / "missing-terminal"
    missing_query = missing_dir / "query.json"
    write_new(missing_query, alpha_query)
    controls.append(("missing-terminal", missing_query, alpha[0], alpha[1], missing_dir / "absent.json", "UnknownResolutionState"))

    wrong_source_dir = args.output / "cases" / "wrong-source"
    wrong_source_query = wrong_source_dir / "query.json"
    write_new(wrong_source_query, alpha_query)
    controls.append(("wrong-source", wrong_source_query, gamma[0], alpha[1], alpha[2], "UnknownResolutionState"))

    wrong_recovery_dir = args.output / "cases" / "wrong-recovery"
    wrong_recovery_query = wrong_recovery_dir / "query.json"
    write_new(wrong_recovery_query, alpha_query)
    controls.append(("wrong-recovery", wrong_recovery_query, alpha[0], gamma[1], alpha[2], "UnknownResolutionState"))

    tampered_dir = args.output / "cases" / "tampered-terminal"
    tampered_query = tampered_dir / "query.json"
    tampered_terminal = tampered_dir / "terminal.json"
    write_new(tampered_query, alpha_query)
    tampered = json.loads(alpha[2].read_bytes())
    tampered["coverage"] = [0, 2]
    write_new(tampered_terminal, tampered)
    controls.append(("tampered-terminal", tampered_query, alpha[0], alpha[1], tampered_terminal, "UnknownResolutionState"))

    substituted_dir = args.output / "cases" / "whole-object-substitution"
    substituted_query = substituted_dir / "query.json"
    write_new(substituted_query, alpha_query)
    controls.append(("whole-object-substitution", substituted_query, gamma[0], gamma[1], gamma[2], "UnknownResolutionState"))

    noncanonical_dir = args.output / "cases" / "noncanonical-terminal"
    noncanonical_query = noncanonical_dir / "query.json"
    noncanonical_terminal = noncanonical_dir / "terminal.json"
    write_new(noncanonical_query, alpha_query)
    write_new(noncanonical_terminal, json.dumps(json.loads(alpha[2].read_bytes()), indent=2).encode())
    controls.append(("noncanonical-terminal", noncanonical_query, alpha[0], alpha[1], noncanonical_terminal, "InvalidEvidence"))

    projection_dir = args.output / "cases" / "wrong-state-projection"
    projection_terminal = projection_dir / "terminal.json"
    projection = json.loads(alpha[2].read_bytes())
    projection["state"] = "cancelled"
    write_new(projection_terminal, projection)
    projection_query_value = dict(alpha_query)
    projection_query_value["terminal_sha256"] = file_sha(projection_terminal)
    projection_query = projection_dir / "query.json"
    write_new(projection_query, projection_query_value)
    controls.append(("wrong-state-projection", projection_query, alpha[0], alpha[1], projection_terminal, "UnknownResolutionState"))

    for name, query, source, recovery, terminal, expected in controls:
        case_dir = args.output / "cases" / name
        receipt, metrics = run_receiver(case_dir, query, source, recovery, terminal)
        processes += 1
        work_units += int(receipt["work_units"])
        for condition in (
            receipt["outcome"] == expected,
            receipt["archive_mutated"] is False,
            receipt["target_processes"] == 0,
            all(receipt[key] is False for key in (
                "effect_authority", "retry_authority", "refund_authority",
                "mutation_authority", "native_authority", "free_authority"
            )),
            metrics["input_sha256_before"] == metrics["input_sha256_after"],
        ):
            assert condition
            assertions += 1
        cases.append({"case": name, "receipt": receipt, "metrics": metrics})

    assert processes == 10
    assertions += 1
    assert work_units <= 30_000
    assertions += 1
    assert sum(1 for case in cases if case["receipt"]["outcome"] == "ResolutionVerified") == 3
    assertions += 1
    assert sum(1 for case in cases if case["receipt"]["outcome"] == "UnknownResolutionState") == 6
    assertions += 1
    assert sum(1 for case in cases if case["receipt"]["outcome"] == "InvalidEvidence") == 1
    assertions += 1

    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    self_usage = resource.getrusage(resource.RUSAGE_SELF)
    result = {
        "profile": "adva.research.terminal-resolution-receiver.execution.v0",
        "status": "Passed",
        "assertions": assertions,
        "receiver_processes": processes,
        "target_processes": 0,
        "search_candidates": 0,
        "implementation_correction_replays": 1,
        "work_units": work_units,
        "receiver_seconds": sum(float(case["metrics"]["seconds"]) for case in cases),
        "whole_run_seconds": time.monotonic() - start,
        "max_child_rss_kib": child.ru_maxrss,
        "max_supervisor_rss_kib": self_usage.ru_maxrss,
        "archive_root": display_path(archive),
        "cases": cases,
        "boundary": {
            "opens_lock_file": False,
            "opens_mutable_runtime_ledger": False,
            "authorizes_retry": False,
            "authorizes_refund": False,
            "authorizes_effect": False,
            "proves_global_nonoccurrence": False,
        },
    }
    write_new(args.output / "execution.json", result)
    sys.stdout.buffer.write(canonical(result) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
