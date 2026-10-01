#!/usr/bin/env python3
"""Atomically apply one bounded recovery receipt to one pending ledger."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import sys
from pathlib import Path

MAX_BYTES = 16_384
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class InvalidEvidence(Exception):
    pass


class InvalidContext(Exception):
    pass


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def read_canonical(path: Path) -> tuple[dict[str, object], bytes]:
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise InvalidEvidence("InputTooLarge")
    value = json.loads(raw)
    if not isinstance(value, dict) or canonical(value) != raw:
        raise InvalidEvidence("NonCanonicalJson")
    return value, raw


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def response(outcome: str, reason: str, *, mutated: bool = False,
             state: str | None = None, work: int = 0) -> dict[str, object]:
    return {
        "profile": "recovery-application-receipt-v0",
        "outcome": outcome,
        "reason": reason,
        "state": state,
        "ledger_mutated": mutated,
        "target_processes": 0,
        "effect_authority": False,
        "retry_authority": False,
        "refund_authority": False,
        "native_authority": False,
        "free_authority": False,
        "work_units": work,
    }


def validate_pending(value: dict[str, object]) -> None:
    required = {"profile", "state", "attempt_id", "pair_digest", "receipt_digest"}
    if set(value) != required:
        raise InvalidEvidence("LedgerFields")
    if value["profile"] != "single-consumption-ledger-v0" or value["state"] != "pending":
        raise InvalidContext("LedgerNotPending")
    if not isinstance(value["attempt_id"], str) or not value["attempt_id"]:
        raise InvalidEvidence("AttemptId")
    if not isinstance(value["pair_digest"], str) or not HEX64.fullmatch(value["pair_digest"]):
        raise InvalidEvidence("PairDigest")
    if value["receipt_digest"] is not None:
        raise InvalidContext("PendingHasReceipt")


def validate_recovery(value: dict[str, object]) -> str:
    base = {"profile", "outcome", "reason", "work_units", "effect_authority",
            "retry_authority", "refund_authority", "mutation_authority",
            "native_authority", "free_authority", "attempt_id", "pair_digest",
            "channel_id", "coverage", "witness_sha256"}
    outcome = value.get("outcome")
    required = base | ({"result_sha256"} if outcome == "EffectWitnessVerified" else set())
    if outcome not in ("EffectWitnessVerified", "NoEffectWitnessVerified"):
        raise InvalidEvidence("RecoveryOutcome")
    if set(value) != required or value.get("profile") != "pending-effect-witness-receipt-v0":
        raise InvalidEvidence("RecoveryFields")
    for key in ("effect_authority", "retry_authority", "refund_authority",
                "mutation_authority", "native_authority", "free_authority"):
        if value[key] is not False:
            raise InvalidEvidence("RecoveryAuthority")
    if not isinstance(value["attempt_id"], str) or not value["attempt_id"]:
        raise InvalidEvidence("RecoveryAttempt")
    if not isinstance(value["pair_digest"], str) or not HEX64.fullmatch(value["pair_digest"]):
        raise InvalidEvidence("RecoveryPair")
    if not isinstance(value["channel_id"], str) or not value["channel_id"]:
        raise InvalidEvidence("RecoveryChannel")
    coverage = value["coverage"]
    if (not isinstance(coverage, list) or len(coverage) != 2 or
            any(not isinstance(x, int) or isinstance(x, bool) for x in coverage) or
            coverage[0] < 0 or coverage[1] < coverage[0]):
        raise InvalidEvidence("RecoveryCoverage")
    if not isinstance(value["witness_sha256"], str) or not HEX64.fullmatch(value["witness_sha256"]):
        raise InvalidEvidence("RecoveryWitnessDigest")
    if outcome == "EffectWitnessVerified" and (not isinstance(value["result_sha256"], str) or not HEX64.fullmatch(value["result_sha256"])):
        raise InvalidEvidence("RecoveryResultDigest")
    return outcome


def validate_terminal(value: dict[str, object]) -> None:
    required = {"profile", "state", "attempt_id", "pair_digest", "source_pending_sha256",
                "recovery_receipt_sha256", "witness_sha256", "channel_id", "coverage",
                "result_sha256"}
    if set(value) != required or value["profile"] != "recovery-resolution-ledger-v0":
        raise InvalidEvidence("TerminalFields")
    if value["state"] not in ("completed", "cancelled"):
        raise InvalidEvidence("TerminalState")


def write_atomic(path: Path, value: dict[str, object], crash_before: bool, crash_after: bool) -> None:
    raw = canonical(value)
    temporary = path.with_name(path.name + ".next-" + str(os.getpid()))
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    if crash_before:
        os._exit(23)
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    if crash_after:
        os._exit(24)


def apply(ledger_path: Path, recovery_path: Path, crash_before: bool, crash_after: bool) -> dict[str, object]:
    work = 0
    recovery, recovery_raw = read_canonical(recovery_path)
    work += len(recovery_raw) + 1
    try:
        recovery_outcome = validate_recovery(recovery)
    except InvalidEvidence as exc:
        if recovery.get("profile") == "pending-effect-witness-receipt-v0" and recovery.get("outcome") == "UnknownConsumptionState":
            return response("UnknownConsumptionState", "RecoveryWitnessInsufficient", work=work + 1)
        return response("InvalidEvidence", str(exc), work=work + 1)

    lock_path = ledger_path.with_name(ledger_path.name + ".lock")
    lock_path.touch(exist_ok=True)
    with lock_path.open("rb") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        ledger, ledger_raw = read_canonical(ledger_path)
        work += len(ledger_raw) + 1
        recovery_sha = digest(recovery_raw)
        if ledger.get("profile") == "recovery-resolution-ledger-v0":
            validate_terminal(ledger)
            if ledger.get("recovery_receipt_sha256") == recovery_sha:
                return response("ReplayRefused", "RecoveryReceiptAlreadyApplied", state=str(ledger["state"]), work=work + 1)
            if ledger.get("attempt_id") == recovery.get("attempt_id") and ledger.get("pair_digest") == recovery.get("pair_digest"):
                return response("ConflictRefused", "DifferentRecoveryReceiptAfterTerminal", state=str(ledger["state"]), work=work + 1)
            return response("InvalidContext", "TerminalContextMismatch", state=str(ledger.get("state")), work=work + 1)

        validate_pending(ledger)
        if recovery["attempt_id"] != ledger["attempt_id"] or recovery["pair_digest"] != ledger["pair_digest"]:
            return response("InvalidContext", "RecoveryContextMismatch", state="pending", work=work + 1)
        state = "completed" if recovery_outcome == "EffectWitnessVerified" else "cancelled"
        terminal = {
            "profile": "recovery-resolution-ledger-v0",
            "state": state,
            "attempt_id": ledger["attempt_id"],
            "pair_digest": ledger["pair_digest"],
            "source_pending_sha256": digest(ledger_raw),
            "recovery_receipt_sha256": recovery_sha,
            "witness_sha256": recovery["witness_sha256"],
            "channel_id": recovery["channel_id"],
            "coverage": recovery["coverage"],
            "result_sha256": recovery.get("result_sha256"),
        }
        write_atomic(ledger_path, terminal, crash_before, crash_after)
        work += len(canonical(terminal)) + 1
        return response("ResolutionApplied", "EffectRecorded" if state == "completed" else "BoundedCancellationRecorded", mutated=True, state=state, work=work)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--recovery", type=Path, required=True)
    parser.add_argument("--crash-before-replace", action="store_true")
    parser.add_argument("--crash-after-replace", action="store_true")
    args = parser.parse_args()
    try:
        value = apply(args.ledger, args.recovery, args.crash_before_replace, args.crash_after_replace)
    except InvalidContext as exc:
        value = response("InvalidContext", str(exc))
    except (OSError, ValueError, json.JSONDecodeError, InvalidEvidence) as exc:
        value = response("InvalidEvidence", type(exc).__name__ + ":" + str(exc))
    sys.stdout.buffer.write(canonical(value) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
