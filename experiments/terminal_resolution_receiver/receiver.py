#!/usr/bin/env python3
"""Read-only independent receiver for one archived recovery terminal."""

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


def read_canonical(path: Path) -> tuple[dict[str, object], bytes]:
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise InvalidEvidence("InputTooLarge")
    value = json.loads(raw)
    if not isinstance(value, dict) or canonical(value) != raw:
        raise InvalidEvidence("NonCanonicalJson")
    return value, raw


def is_hex64(value: object) -> bool:
    return isinstance(value, str) and HEX64.fullmatch(value) is not None


def validate_query(value: dict[str, object]) -> None:
    required = {
        "profile",
        "attempt_id",
        "pair_digest",
        "source_pending_sha256",
        "recovery_receipt_sha256",
        "terminal_sha256",
    }
    if set(value) != required or value["profile"] != "terminal-resolution-query-v0":
        raise InvalidEvidence("QueryFields")
    if not isinstance(value["attempt_id"], str) or not value["attempt_id"]:
        raise InvalidEvidence("QueryAttempt")
    for key in (
        "pair_digest",
        "source_pending_sha256",
        "recovery_receipt_sha256",
        "terminal_sha256",
    ):
        if not is_hex64(value[key]):
            raise InvalidEvidence("QueryDigest:" + key)


def validate_pending(value: dict[str, object]) -> None:
    required = {"profile", "state", "attempt_id", "pair_digest", "receipt_digest"}
    if set(value) != required:
        raise InvalidEvidence("PendingFields")
    if value["profile"] != "single-consumption-ledger-v0" or value["state"] != "pending":
        raise InvalidEvidence("PendingProfileOrState")
    if not isinstance(value["attempt_id"], str) or not value["attempt_id"]:
        raise InvalidEvidence("PendingAttempt")
    if not is_hex64(value["pair_digest"]):
        raise InvalidEvidence("PendingPair")
    if value["receipt_digest"] is not None:
        raise InvalidEvidence("PendingReceipt")


def validate_recovery(value: dict[str, object]) -> str:
    base = {
        "profile",
        "outcome",
        "reason",
        "work_units",
        "effect_authority",
        "retry_authority",
        "refund_authority",
        "mutation_authority",
        "native_authority",
        "free_authority",
        "attempt_id",
        "pair_digest",
        "channel_id",
        "coverage",
        "witness_sha256",
    }
    outcome = value.get("outcome")
    required = base | ({"result_sha256"} if outcome == "EffectWitnessVerified" else set())
    if outcome not in ("EffectWitnessVerified", "NoEffectWitnessVerified"):
        raise InvalidEvidence("RecoveryOutcome")
    if set(value) != required or value.get("profile") != "pending-effect-witness-receipt-v0":
        raise InvalidEvidence("RecoveryFields")
    for key in (
        "effect_authority",
        "retry_authority",
        "refund_authority",
        "mutation_authority",
        "native_authority",
        "free_authority",
    ):
        if value[key] is not False:
            raise InvalidEvidence("RecoveryAuthority")
    if not isinstance(value["attempt_id"], str) or not value["attempt_id"]:
        raise InvalidEvidence("RecoveryAttempt")
    if not is_hex64(value["pair_digest"]):
        raise InvalidEvidence("RecoveryPair")
    if not isinstance(value["channel_id"], str) or not value["channel_id"]:
        raise InvalidEvidence("RecoveryChannel")
    coverage = value["coverage"]
    if (
        not isinstance(coverage, list)
        or len(coverage) != 2
        or any(not isinstance(item, int) or isinstance(item, bool) for item in coverage)
        or coverage[0] < 0
        or coverage[1] < coverage[0]
    ):
        raise InvalidEvidence("RecoveryCoverage")
    if not is_hex64(value["witness_sha256"]):
        raise InvalidEvidence("RecoveryWitnessDigest")
    if outcome == "EffectWitnessVerified" and not is_hex64(value["result_sha256"]):
        raise InvalidEvidence("RecoveryResultDigest")
    return str(outcome)


def validate_terminal(value: dict[str, object]) -> None:
    required = {
        "profile",
        "state",
        "attempt_id",
        "pair_digest",
        "source_pending_sha256",
        "recovery_receipt_sha256",
        "witness_sha256",
        "channel_id",
        "coverage",
        "result_sha256",
    }
    if set(value) != required or value.get("profile") != "recovery-resolution-ledger-v0":
        raise InvalidEvidence("TerminalFields")
    if value["state"] not in ("completed", "cancelled"):
        raise InvalidEvidence("TerminalState")
    for key in (
        "pair_digest",
        "source_pending_sha256",
        "recovery_receipt_sha256",
        "witness_sha256",
    ):
        if not is_hex64(value[key]):
            raise InvalidEvidence("TerminalDigest:" + key)
    if value["result_sha256"] is not None and not is_hex64(value["result_sha256"]):
        raise InvalidEvidence("TerminalResultDigest")


def response(
    outcome: str,
    reason: str,
    *,
    query: dict[str, object] | None = None,
    state: str | None = None,
    source_sha: str | None = None,
    recovery_sha: str | None = None,
    terminal_sha: str | None = None,
    work: int = 0,
) -> dict[str, object]:
    return {
        "profile": "terminal-resolution-receipt-v0",
        "outcome": outcome,
        "reason": reason,
        "state": state,
        "attempt_id": None if query is None else query.get("attempt_id"),
        "pair_digest": None if query is None else query.get("pair_digest"),
        "source_pending_sha256": source_sha,
        "recovery_receipt_sha256": recovery_sha,
        "terminal_sha256": terminal_sha,
        "archive_mutated": False,
        "target_processes": 0,
        "effect_authority": False,
        "retry_authority": False,
        "refund_authority": False,
        "mutation_authority": False,
        "native_authority": False,
        "free_authority": False,
        "work_units": work,
    }


def receive(query_path: Path, pending_path: Path, recovery_path: Path, terminal_path: Path) -> dict[str, object]:
    work = 0
    query, query_raw = read_canonical(query_path)
    work += len(query_raw) + 1
    validate_query(query)

    loaded: list[tuple[dict[str, object], bytes]] = []
    for path in (pending_path, recovery_path, terminal_path):
        try:
            item = read_canonical(path)
        except FileNotFoundError:
            return response(
                "UnknownResolutionState",
                "ArchiveComponentMissing",
                query=query,
                work=work + 1,
            )
        loaded.append(item)
        work += len(item[1]) + 1

    (pending, pending_raw), (recovery, recovery_raw), (terminal, terminal_raw) = loaded
    validate_pending(pending)
    recovery_outcome = validate_recovery(recovery)
    validate_terminal(terminal)
    source_sha = digest(pending_raw)
    recovery_sha = digest(recovery_raw)
    terminal_sha = digest(terminal_raw)
    work += len(pending_raw) + len(recovery_raw) + len(terminal_raw) + 6

    if (
        source_sha != query["source_pending_sha256"]
        or recovery_sha != query["recovery_receipt_sha256"]
        or terminal_sha != query["terminal_sha256"]
    ):
        return response(
            "UnknownResolutionState",
            "ArchiveDigestDivergence",
            query=query,
            source_sha=source_sha,
            recovery_sha=recovery_sha,
            terminal_sha=terminal_sha,
            work=work + 1,
        )

    if any(
        value != query[key]
        for key in ("attempt_id", "pair_digest")
        for value in (pending[key], recovery[key], terminal[key])
    ):
        return response(
            "UnknownResolutionState",
            "QuestionBindingDivergence",
            query=query,
            source_sha=source_sha,
            recovery_sha=recovery_sha,
            terminal_sha=terminal_sha,
            work=work + 1,
        )

    expected_state = "completed" if recovery_outcome == "EffectWitnessVerified" else "cancelled"
    expected_terminal = {
        "profile": "recovery-resolution-ledger-v0",
        "state": expected_state,
        "attempt_id": pending["attempt_id"],
        "pair_digest": pending["pair_digest"],
        "source_pending_sha256": source_sha,
        "recovery_receipt_sha256": recovery_sha,
        "witness_sha256": recovery["witness_sha256"],
        "channel_id": recovery["channel_id"],
        "coverage": recovery["coverage"],
        "result_sha256": recovery.get("result_sha256"),
    }
    work += len(canonical(expected_terminal)) + 1
    if terminal != expected_terminal:
        return response(
            "UnknownResolutionState",
            "TerminalProjectionDivergence",
            query=query,
            state=str(terminal["state"]),
            source_sha=source_sha,
            recovery_sha=recovery_sha,
            terminal_sha=terminal_sha,
            work=work + 1,
        )

    return response(
        "ResolutionVerified",
        "ArchivedProjectionMatches",
        query=query,
        state=expected_state,
        source_sha=source_sha,
        recovery_sha=recovery_sha,
        terminal_sha=terminal_sha,
        work=work + 1,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--source-pending", type=Path, required=True)
    parser.add_argument("--recovery-receipt", type=Path, required=True)
    parser.add_argument("--terminal", type=Path, required=True)
    args = parser.parse_args()
    try:
        value = receive(
            args.query,
            args.source_pending,
            args.recovery_receipt,
            args.terminal,
        )
    except (OSError, ValueError, json.JSONDecodeError, InvalidEvidence) as exc:
        value = response("InvalidEvidence", type(exc).__name__ + ":" + str(exc))
    sys.stdout.buffer.write(canonical(value) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
