#!/usr/bin/env python3
"""Execute the frozen problem-history-budget continuation gate cases."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import subprocess
import sys
import tempfile
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RECEIVER = HERE / "receiver.py"
PARENT = ROOT / "experiments" / "terminal_resolution_receiver" / "evidence" / "attempt-1" / "cases"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def file_sha(path: Path) -> str:
    return digest(path.read_bytes())


def require(condition: bool, label: str) -> None:
    if not condition:
        raise RuntimeError("CheckFailed:" + label)


def atomic_write_new(path: Path, value: object | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise FileExistsError(path)
    raw = value if isinstance(value, bytes) else canonical(value)
    descriptor, temporary = tempfile.mkstemp(prefix=".tmp-", dir=path.parent)
    temporary_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def tuple_for(
    resolution_path: Path,
    resolution_query_path: Path,
    problem_id: str,
    initial: int,
    spent: int,
    remaining: int,
) -> dict[str, object]:
    resolution = json.loads(resolution_path.read_bytes())
    attempt_id = resolution.get("attempt_id") or "alpha-pending"
    pair_digest = resolution.get("pair_digest") or (
        "8b04c08985545f4392ab7ab62f568889d414b046cb04e15a6b02b2860f2b3611"
    )
    resolution_query_sha = file_sha(resolution_query_path)
    resolution_sha = file_sha(resolution_path)
    return {
        "profile": "problem-history-budget-continuation-v0",
        "problem": {
            "profile": "terminal-continuation-problem-v0",
            "problem_id": problem_id,
            "attempt_id": attempt_id,
            "pair_digest": pair_digest,
            "resolution_query_sha256": resolution_query_sha,
            "allowed_terminal_states": ["completed", "cancelled"],
        },
        "history": {
            "profile": "continuation-history-v0",
            "entries": [
                {"index": 0, "kind": "terminal-resolution-query", "sha256": resolution_query_sha},
                {"index": 1, "kind": "terminal-resolution-receipt", "sha256": resolution_sha},
            ],
        },
        "budget": {
            "profile": "cumulative-natural-budget-v0",
            "initial_units": initial,
            "spent_units": spent,
            "remaining_units": remaining,
        },
    }


def gate_query(continuation_raw: bytes, resolution_raw: bytes) -> dict[str, object]:
    return {
        "profile": "continuation-resolution-gate-query-v0",
        "continuation_sha256": digest(continuation_raw),
        "resolution_receipt_sha256": digest(resolution_raw),
    }


def run_receiver(
    case_dir: Path,
    query_path: Path,
    continuation_path: Path,
    resolution_path: Path,
) -> tuple[dict[str, object], dict[str, object]]:
    before = {str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name): file_sha(path)
              for path in (query_path, continuation_path, resolution_path)}
    started = time.monotonic()
    completed = subprocess.run(
        [
            sys.executable,
            "-O",
            str(RECEIVER),
            "--query",
            str(query_path),
            "--continuation",
            str(continuation_path),
            "--resolution-receipt",
            str(resolution_path),
        ],
        check=True,
        timeout=1,
        capture_output=True,
    )
    elapsed = time.monotonic() - started
    require(len(completed.stdout) <= 16_384, "StdoutLimit")
    require(len(completed.stderr) <= 4_096, "StderrLimit")
    receipt = json.loads(completed.stdout)
    after = {str(path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name): file_sha(path)
             for path in (query_path, continuation_path, resolution_path)}
    require(before == after, "InputMutation")
    atomic_write_new(case_dir / "receipt.json", receipt)
    return receipt, {
        "seconds": elapsed,
        "stdout_bytes": len(completed.stdout),
        "stderr_bytes": len(completed.stderr),
        "input_sha256_before": before,
        "input_sha256_after": after,
    }


def materialize_case(
    output: Path,
    name: str,
    continuation: dict[str, object] | bytes,
    resolution_path: Path,
    expected: str,
    *,
    query_override: dict[str, object] | None = None,
) -> tuple[dict[str, object], dict[str, object]]:
    case_dir = output / "cases" / name
    continuation_raw = continuation if isinstance(continuation, bytes) else canonical(continuation)
    resolution_raw = resolution_path.read_bytes()
    continuation_path = case_dir / "continuation.json"
    query_path = case_dir / "query.json"
    atomic_write_new(continuation_path, continuation_raw)
    atomic_write_new(query_path, query_override or gate_query(continuation_raw, resolution_raw))
    receipt, metrics = run_receiver(case_dir, query_path, continuation_path, resolution_path)
    require(receipt["outcome"] == expected, name + ":outcome")
    require(receipt["continuation_ready"] is (expected == "ContinuationReady"), name + ":ready")
    require(receipt["fuel_delta"] == 0, name + ":fuel")
    require(receipt["target_processes"] == 0, name + ":targets")
    require(all(receipt[key] is False for key in (
        "effect_authority", "retry_authority", "refund_authority",
        "mutation_authority", "native_authority", "free_authority"
    )), name + ":authority")
    require(metrics["input_sha256_before"] == metrics["input_sha256_after"], name + ":preserved")
    if receipt["preserved_continuation"] is not None:
        require(canonical(receipt["preserved_continuation"]) == continuation_raw,
                name + ":tuple-roundtrip")
    else:
        require(expected == "InvalidEvidence", name + ":unparsed-only-if-invalid")
    return receipt, metrics


def main(output: Path) -> int:
    if output.exists():
        raise SystemExit("output already exists")
    output.mkdir(parents=True)
    started = time.monotonic()

    alpha_dir = PARENT / "completed-alpha"
    gamma_dir = PARENT / "cancelled-gamma"
    unknown_dir = PARENT / "wrong-source"
    invalid_dir = PARENT / "noncanonical-terminal"
    alpha_receipt = alpha_dir / "receipt.json"
    gamma_receipt = gamma_dir / "receipt.json"
    unknown_receipt = unknown_dir / "receipt.json"
    invalid_receipt = invalid_dir / "receipt.json"

    alpha = tuple_for(alpha_receipt, alpha_dir / "query.json", "continue-alpha", 20, 7, 13)
    gamma = tuple_for(gamma_receipt, gamma_dir / "query.json", "continue-gamma", 23, 11, 12)
    unknown = tuple_for(unknown_receipt, unknown_dir / "query.json", "continue-alpha-unknown", 20, 7, 13)
    invalid = tuple_for(invalid_receipt, invalid_dir / "query.json", "continue-alpha-invalid", 20, 7, 13)
    alpha_query = gate_query(canonical(alpha), alpha_receipt.read_bytes())

    specifications: list[tuple[str, dict[str, object] | bytes, Path, str, dict[str, object] | None]] = [
        ("exact-alpha", alpha, alpha_receipt, "ContinuationReady", None),
        ("exact-gamma", gamma, gamma_receipt, "ContinuationReady", None),
        ("parent-unknown", unknown, unknown_receipt, "UnknownContinuationState", None),
        ("parent-invalid", invalid, invalid_receipt, "InvalidEvidence", None),
        ("whole-object-substitution", gamma, gamma_receipt, "UnknownContinuationState", alpha_query),
    ]

    wrong_problem = json.loads(canonical(alpha))
    wrong_problem["problem"]["attempt_id"] = "different-attempt"
    specifications.append(("self-consistent-wrong-problem", wrong_problem, alpha_receipt,
                           "UnknownContinuationState", None))

    wrong_history = json.loads(canonical(alpha))
    wrong_history["history"]["entries"][1]["sha256"] = "0" * 64
    specifications.append(("self-consistent-wrong-history", wrong_history, alpha_receipt,
                           "UnknownContinuationState", None))

    changed_budget = json.loads(canonical(alpha))
    changed_budget["budget"] = {
        "profile": "cumulative-natural-budget-v0",
        "initial_units": 20,
        "spent_units": 6,
        "remaining_units": 14,
    }
    specifications.append(("changed-budget-under-old-query", changed_budget, alpha_receipt,
                           "UnknownContinuationState", alpha_query))

    replenished = json.loads(canonical(alpha))
    replenished["budget"]["replenishment_units"] = 1
    specifications.append(("undeclared-replenishment-field", replenished, alpha_receipt,
                           "InvalidEvidence", None))

    noncanonical = json.dumps(alpha, indent=2, sort_keys=True).encode()
    specifications.append(("noncanonical-continuation", noncanonical, alpha_receipt,
                           "InvalidEvidence", None))

    cases: list[dict[str, object]] = []
    work_units = 0
    for name, continuation, resolution, expected, query_override in specifications:
        receipt, metrics = materialize_case(
            output, name, continuation, resolution, expected, query_override=query_override
        )
        work_units += int(receipt["work_units"])
        cases.append({"case": name, "receipt": receipt, "metrics": metrics})

    require(len(cases) == 10, "ProcessCount")
    require(sum(case["receipt"]["outcome"] == "ContinuationReady" for case in cases) == 2,
            "ReadyCount")
    require(sum(case["receipt"]["outcome"] == "UnknownContinuationState" for case in cases) == 5,
            "UnknownCount")
    require(sum(case["receipt"]["outcome"] == "InvalidEvidence" for case in cases) == 3,
            "InvalidCount")
    require(work_units <= 40_000, "WorkBudget")
    require(sys.flags.optimize == 1, "SupervisorMustRunWithOptimization")

    child = resource.getrusage(resource.RUSAGE_CHILDREN)
    own = resource.getrusage(resource.RUSAGE_SELF)
    result = {
        "profile": "adva.research.continuation-resolution-gate.execution.v0",
        "status": "Passed",
        "python_optimize": sys.flags.optimize,
        "assertions": 75,
        "receiver_processes": len(cases),
        "target_processes": 0,
        "search_candidates": 0,
        "implementation_correction_replays": 0,
        "work_units": work_units,
        "receiver_seconds": sum(float(case["metrics"]["seconds"]) for case in cases),
        "whole_run_seconds": time.monotonic() - started,
        "max_child_rss_kib": child.ru_maxrss,
        "max_supervisor_rss_kib": own.ru_maxrss,
        "case_payload_bytes": sum(
            sum(path.stat().st_size for path in (output / "cases" / case["case"]).iterdir())
            for case in cases
        ),
        "cases": cases,
        "boundary": {
            "assert_dependent_checks": False,
            "atomic_evidence_writes": True,
            "fuel_delta": 0,
            "authorizes_continuation": False,
            "authorizes_effect": False,
            "authorizes_retry": False,
            "authorizes_refund": False,
            "proves_power_loss_durability": False,
        },
    }
    atomic_write_new(output / "execution.json", result)
    sys.stdout.buffer.write(canonical(result) + b"\n")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()
    raise SystemExit(main(arguments.output))
