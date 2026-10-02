#!/usr/bin/env python3
"""Read-only gate from a terminal-resolution receipt to one exact continuation tuple."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


MAX_BYTES = 16_384
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class InvalidEvidence(Exception):
    pass


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode()


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def is_hex64(value: object) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def read_canonical(path: Path) -> tuple[dict[str, object], bytes]:
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise InvalidEvidence("InputTooLarge")
    value = json.loads(raw)
    if not isinstance(value, dict) or canonical(value) != raw:
        raise InvalidEvidence("NonCanonicalJson")
    return value, raw


def validate_query(value: dict[str, object]) -> None:
    required = {
        "profile",
        "continuation_sha256",
        "resolution_receipt_sha256",
    }
    if set(value) != required or value["profile"] != "continuation-resolution-gate-query-v0":
        raise InvalidEvidence("QueryFields")
    for key in ("continuation_sha256", "resolution_receipt_sha256"):
        if not is_hex64(value[key]):
            raise InvalidEvidence("QueryDigest:" + key)


def natural(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate_continuation(value: dict[str, object]) -> None:
    if set(value) != {"profile", "problem", "history", "budget"}:
        raise InvalidEvidence("TupleFields")
    if value["profile"] != "problem-history-budget-continuation-v0":
        raise InvalidEvidence("TupleProfile")

    problem = value["problem"]
    if not isinstance(problem, dict) or set(problem) != {
        "profile",
        "problem_id",
        "attempt_id",
        "pair_digest",
        "resolution_query_sha256",
        "allowed_terminal_states",
    }:
        raise InvalidEvidence("TupleProblemFields")
    if problem["profile"] != "terminal-continuation-problem-v0":
        raise InvalidEvidence("TupleProblemProfile")
    if any(not isinstance(problem[key], str) or not problem[key] for key in ("problem_id", "attempt_id")):
        raise InvalidEvidence("TupleProblemText")
    if not is_hex64(problem["pair_digest"]) or not is_hex64(problem["resolution_query_sha256"]):
        raise InvalidEvidence("TupleProblemDigest")
    states = problem["allowed_terminal_states"]
    if (
        not isinstance(states, list)
        or not states
        or len(states) != len(set(states))
        or any(state not in ("completed", "cancelled") for state in states)
    ):
        raise InvalidEvidence("TupleProblemStates")

    history = value["history"]
    if not isinstance(history, dict) or set(history) != {"profile", "entries"}:
        raise InvalidEvidence("TupleHistoryFields")
    if history["profile"] != "continuation-history-v0":
        raise InvalidEvidence("TupleHistoryProfile")
    entries = history["entries"]
    if not isinstance(entries, list) or len(entries) != 2:
        raise InvalidEvidence("TupleHistoryLength")
    expected_kinds = ("terminal-resolution-query", "terminal-resolution-receipt")
    for index, (entry, expected_kind) in enumerate(zip(entries, expected_kinds)):
        if not isinstance(entry, dict) or set(entry) != {"index", "kind", "sha256"}:
            raise InvalidEvidence("TupleHistoryEntryFields")
        if entry["index"] != index or entry["kind"] != expected_kind or not is_hex64(entry["sha256"]):
            raise InvalidEvidence("TupleHistoryEntry")
    if entries[0]["sha256"] != problem["resolution_query_sha256"]:
        raise InvalidEvidence("TupleHistoryProblemDivergence")

    budget = value["budget"]
    if not isinstance(budget, dict) or set(budget) != {
        "profile",
        "initial_units",
        "spent_units",
        "remaining_units",
    }:
        raise InvalidEvidence("TupleBudgetFields")
    if budget["profile"] != "cumulative-natural-budget-v0":
        raise InvalidEvidence("TupleBudgetProfile")
    if any(not natural(budget[key]) for key in ("initial_units", "spent_units", "remaining_units")):
        raise InvalidEvidence("TupleBudgetNatural")
    if budget["initial_units"] != budget["spent_units"] + budget["remaining_units"]:
        raise InvalidEvidence("TupleBudgetEquation")


def validate_resolution(value: dict[str, object]) -> None:
    required = {
        "profile",
        "outcome",
        "reason",
        "state",
        "attempt_id",
        "pair_digest",
        "source_pending_sha256",
        "recovery_receipt_sha256",
        "terminal_sha256",
        "archive_mutated",
        "target_processes",
        "effect_authority",
        "retry_authority",
        "refund_authority",
        "mutation_authority",
        "native_authority",
        "free_authority",
        "work_units",
    }
    if set(value) != required or value["profile"] != "terminal-resolution-receipt-v0":
        raise InvalidEvidence("ResolutionFields")
    if value["outcome"] not in (
        "ResolutionVerified",
        "UnknownResolutionState",
        "InvalidEvidence",
    ):
        raise InvalidEvidence("ResolutionOutcome")
    if not isinstance(value["reason"], str) or not value["reason"]:
        raise InvalidEvidence("ResolutionReason")
    if value["archive_mutated"] is not False or value["target_processes"] != 0:
        raise InvalidEvidence("ResolutionBoundary")
    for key in (
        "effect_authority",
        "retry_authority",
        "refund_authority",
        "mutation_authority",
        "native_authority",
        "free_authority",
    ):
        if value[key] is not False:
            raise InvalidEvidence("ResolutionAuthority")
    if not natural(value["work_units"]):
        raise InvalidEvidence("ResolutionWork")

    optional_digests = (
        "pair_digest",
        "source_pending_sha256",
        "recovery_receipt_sha256",
        "terminal_sha256",
    )
    for key in optional_digests:
        if value[key] is not None and not is_hex64(value[key]):
            raise InvalidEvidence("ResolutionDigest:" + key)
    if value["attempt_id"] is not None and (
        not isinstance(value["attempt_id"], str) or not value["attempt_id"]
    ):
        raise InvalidEvidence("ResolutionAttempt")
    if value["state"] is not None and value["state"] not in ("completed", "cancelled"):
        raise InvalidEvidence("ResolutionState")

    if value["outcome"] == "ResolutionVerified":
        if value["state"] not in ("completed", "cancelled"):
            raise InvalidEvidence("VerifiedState")
        if not isinstance(value["attempt_id"], str) or not value["attempt_id"]:
            raise InvalidEvidence("VerifiedAttempt")
        if any(not is_hex64(value[key]) for key in optional_digests):
            raise InvalidEvidence("VerifiedDigest")


def response(
    outcome: str,
    reason: str,
    *,
    continuation: dict[str, object] | None = None,
    continuation_sha: str | None = None,
    resolution_sha: str | None = None,
    state: str | None = None,
    work: int = 0,
) -> dict[str, object]:
    return {
        "profile": "continuation-resolution-gate-receipt-v0",
        "outcome": outcome,
        "reason": reason,
        "state": state,
        "continuation_sha256": continuation_sha,
        "resolution_receipt_sha256": resolution_sha,
        "preserved_continuation": continuation,
        "continuation_ready": outcome == "ContinuationReady",
        "fuel_delta": 0,
        "input_mutated": False,
        "target_processes": 0,
        "effect_authority": False,
        "retry_authority": False,
        "refund_authority": False,
        "mutation_authority": False,
        "native_authority": False,
        "free_authority": False,
        "work_units": work,
    }


def receive(query_path: Path, continuation_path: Path, resolution_path: Path) -> dict[str, object]:
    work = 0
    query, query_raw = read_canonical(query_path)
    work += len(query_raw) + 1
    validate_query(query)

    continuation, continuation_raw = read_canonical(continuation_path)
    work += len(continuation_raw) + 1
    validate_continuation(continuation)
    continuation_sha = digest(continuation_raw)

    try:
        resolution, resolution_raw = read_canonical(resolution_path)
        work += len(resolution_raw) + 1
        validate_resolution(resolution)
    except (OSError, ValueError, json.JSONDecodeError, InvalidEvidence) as exc:
        return response(
            "InvalidEvidence",
            type(exc).__name__ + ":" + str(exc),
            continuation=continuation,
            continuation_sha=continuation_sha,
            work=work + 1,
        )

    resolution_sha = digest(resolution_raw)
    work += len(continuation_raw) + len(resolution_raw) + 2
    if (
        continuation_sha != query["continuation_sha256"]
        or resolution_sha != query["resolution_receipt_sha256"]
    ):
        return response(
            "UnknownContinuationState",
            "GateQueryDigestDivergence",
            continuation=continuation,
            continuation_sha=continuation_sha,
            resolution_sha=resolution_sha,
            work=work + 1,
        )

    history = continuation["history"]
    if history["entries"][1]["sha256"] != resolution_sha:
        return response(
            "UnknownContinuationState",
            "HistoryReceiptDivergence",
            continuation=continuation,
            continuation_sha=continuation_sha,
            resolution_sha=resolution_sha,
            work=work + 1,
        )

    if resolution["outcome"] == "InvalidEvidence":
        return response(
            "InvalidEvidence",
            "ParentResolutionInvalid",
            continuation=continuation,
            continuation_sha=continuation_sha,
            resolution_sha=resolution_sha,
            work=work + 1,
        )
    if resolution["outcome"] == "UnknownResolutionState":
        return response(
            "UnknownContinuationState",
            "ParentResolutionUnknown",
            continuation=continuation,
            continuation_sha=continuation_sha,
            resolution_sha=resolution_sha,
            work=work + 1,
        )

    problem = continuation["problem"]
    if (
        problem["attempt_id"] != resolution["attempt_id"]
        or problem["pair_digest"] != resolution["pair_digest"]
        or resolution["state"] not in problem["allowed_terminal_states"]
    ):
        return response(
            "UnknownContinuationState",
            "ProblemResolutionDivergence",
            continuation=continuation,
            continuation_sha=continuation_sha,
            resolution_sha=resolution_sha,
            state=str(resolution["state"]),
            work=work + 1,
        )

    return response(
        "ContinuationReady",
        "ExactTupleAndResolutionBound",
        continuation=continuation,
        continuation_sha=continuation_sha,
        resolution_sha=resolution_sha,
        state=str(resolution["state"]),
        work=work + 1,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--continuation", type=Path, required=True)
    parser.add_argument("--resolution-receipt", type=Path, required=True)
    args = parser.parse_args()
    continuation_sha = None
    try:
        if args.continuation.exists():
            continuation_sha = digest(args.continuation.read_bytes())
        value = receive(args.query, args.continuation, args.resolution_receipt)
    except (OSError, ValueError, json.JSONDecodeError, InvalidEvidence) as exc:
        value = response(
            "InvalidEvidence",
            type(exc).__name__ + ":" + str(exc),
            continuation_sha=continuation_sha,
        )
    sys.stdout.buffer.write(canonical(value) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
