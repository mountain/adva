#!/usr/bin/env python3
"""Read-only finite receiver for evidence about one pending consumption attempt."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

MAX_BYTES = 16_384
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def read_json(path: Path) -> tuple[object, bytes]:
    raw = path.read_bytes()
    if len(raw) > MAX_BYTES:
        raise ValueError("InputTooLarge")
    value = json.loads(raw)
    if canonical_bytes(value) != raw:
        raise ValueError("NonCanonicalJson")
    return value, raw


def base_receipt(outcome: str, reason: str, work_units: int) -> dict[str, object]:
    return {
        "profile": "pending-effect-witness-receipt-v0",
        "outcome": outcome,
        "reason": reason,
        "work_units": work_units,
        "effect_authority": False,
        "retry_authority": False,
        "refund_authority": False,
        "mutation_authority": False,
        "native_authority": False,
        "free_authority": False,
    }


def receive(ledger_path: Path, witness_path: Path, artifact_path: Path | None) -> dict[str, object]:
    work = 0
    try:
        ledger, ledger_raw = read_json(ledger_path)
        work += len(ledger_raw) + 1
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return base_receipt("InvalidEvidence", f"Ledger:{type(exc).__name__}", work + 1)

    if not isinstance(ledger, dict):
        return base_receipt("InvalidEvidence", "LedgerNotObject", work + 1)
    required_ledger = {"profile", "state", "attempt_id", "pair_digest", "receipt_digest"}
    if set(ledger) != required_ledger:
        return base_receipt("InvalidEvidence", "LedgerFields", work + 1)
    work += len(required_ledger)
    if ledger["profile"] != "single-consumption-ledger-v0" or ledger["state"] != "pending":
        return base_receipt("InvalidContext", "LedgerNotPending", work + 1)
    if not isinstance(ledger["attempt_id"], str) or not ledger["attempt_id"]:
        return base_receipt("InvalidEvidence", "AttemptId", work + 1)
    if not isinstance(ledger["pair_digest"], str) or not HEX64.fullmatch(ledger["pair_digest"]):
        return base_receipt("InvalidEvidence", "PairDigest", work + 1)
    if ledger["receipt_digest"] is not None:
        return base_receipt("InvalidContext", "PendingHasReceipt", work + 1)

    try:
        witness, witness_raw = read_json(witness_path)
        work += len(witness_raw) + 1
    except FileNotFoundError:
        return base_receipt("UnknownConsumptionState", "WitnessMissing", work + 1)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return base_receipt("InvalidEvidence", f"Witness:{type(exc).__name__}", work + 1)

    if not isinstance(witness, dict):
        return base_receipt("InvalidEvidence", "WitnessNotObject", work + 1)
    required_witness = {
        "profile", "attempt_id", "pair_digest", "channel_id",
        "sequence_start", "sequence_end", "coverage_complete", "events",
    }
    if set(witness) != required_witness:
        return base_receipt("InvalidEvidence", "WitnessFields", work + 1)
    work += len(required_witness)
    if witness["profile"] != "pending-effect-witness-v0":
        return base_receipt("InvalidEvidence", "WitnessProfile", work + 1)
    if witness["attempt_id"] != ledger["attempt_id"]:
        return base_receipt("InvalidContext", "AttemptMismatch", work + 1)
    if witness["pair_digest"] != ledger["pair_digest"]:
        return base_receipt("InvalidContext", "PairMismatch", work + 1)
    if not isinstance(witness["channel_id"], str) or not witness["channel_id"]:
        return base_receipt("InvalidEvidence", "ChannelId", work + 1)
    start, end = witness["sequence_start"], witness["sequence_end"]
    if not isinstance(start, int) or isinstance(start, bool) or not isinstance(end, int) or isinstance(end, bool) or start < 0 or end < start:
        return base_receipt("InvalidEvidence", "SequenceRange", work + 1)
    if not isinstance(witness["events"], list):
        return base_receipt("InvalidEvidence", "EventsNotList", work + 1)
    if witness["coverage_complete"] is not True:
        return base_receipt("UnknownConsumptionState", "CoverageIncomplete", work + 1)

    seen: set[int] = set()
    matches: list[dict[str, object]] = []
    for event in witness["events"]:
        work += 7
        if not isinstance(event, dict) or set(event) != {"sequence", "kind", "attempt_id", "pair_digest", "result_sha256"}:
            return base_receipt("InvalidEvidence", "EventFields", work + 1)
        seq = event["sequence"]
        if not isinstance(seq, int) or isinstance(seq, bool) or seq < start or seq > end or seq in seen:
            return base_receipt("InvalidEvidence", "EventSequence", work + 1)
        seen.add(seq)
        if event["kind"] != "effect" or not isinstance(event["result_sha256"], str) or not HEX64.fullmatch(event["result_sha256"]):
            return base_receipt("InvalidEvidence", "EventValue", work + 1)
        if event["attempt_id"] == ledger["attempt_id"] and event["pair_digest"] == ledger["pair_digest"]:
            matches.append(event)

    common = {
        "attempt_id": ledger["attempt_id"],
        "pair_digest": ledger["pair_digest"],
        "channel_id": witness["channel_id"],
        "coverage": [start, end],
        "witness_sha256": hashlib.sha256(witness_raw).hexdigest(),
    }
    if len(matches) > 1:
        receipt = base_receipt("UnknownConsumptionState", "ConflictingEffectEvents", work + 1)
        receipt.update(common)
        return receipt
    if not matches:
        receipt = base_receipt("NoEffectWitnessVerified", "CompleteFiniteChannelHasNoMatchingEvent", work + 1)
        receipt.update(common)
        return receipt

    if artifact_path is None:
        receipt = base_receipt("UnknownConsumptionState", "ResultArtifactMissing", work + 1)
        receipt.update(common)
        return receipt
    try:
        artifact = artifact_path.read_bytes()
    except OSError:
        receipt = base_receipt("UnknownConsumptionState", "ResultArtifactMissing", work + 1)
        receipt.update(common)
        return receipt
    if len(artifact) > MAX_BYTES:
        return base_receipt("InvalidEvidence", "ResultArtifactTooLarge", work + 1)
    work += len(artifact) + 1
    digest = hashlib.sha256(artifact).hexdigest()
    if digest != matches[0]["result_sha256"]:
        receipt = base_receipt("InvalidEvidence", "ResultDigestMismatch", work + 1)
        receipt.update(common)
        return receipt
    receipt = base_receipt("EffectWitnessVerified", "OneMatchingEventAndResultDigest", work + 1)
    receipt.update(common)
    receipt["result_sha256"] = digest
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--witness", type=Path, required=True)
    parser.add_argument("--artifact", type=Path)
    args = parser.parse_args()
    receipt = receive(args.ledger, args.witness, args.artifact)
    sys.stdout.buffer.write(canonical_bytes(receipt) + b"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
