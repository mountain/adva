#!/usr/bin/env python3
"""Run the frozen finite pending-effect witness scenarios."""

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
RECEIVER = HERE / "receiver.py"
PAIR_ALPHA = "8b04c08985545f4392ab7ab62f568889d414b046cb04e15a6b02b2860f2b3611"
PAIR_GAMMA = "51d24380c79274b9ad21b9f45d36013256a2b1e9ef7f340343704d845ed223da"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def write_new(path: Path, value: object | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, bytes) else canonical(value)
    with path.open("xb") as handle:
        handle.write(data)


def ledger(pair: str, attempt: str) -> dict[str, object]:
    return {"attempt_id": attempt, "pair_digest": pair, "profile": "single-consumption-ledger-v0", "receipt_digest": None, "state": "pending"}


def witness(pair: str, attempt: str, complete: bool, events: list[dict[str, object]]) -> dict[str, object]:
    return {"attempt_id": attempt, "channel_id": "project-original-test-channel-v0", "coverage_complete": complete, "events": events, "pair_digest": pair, "profile": "pending-effect-witness-v0", "sequence_end": 3, "sequence_start": 0}


def event(pair: str, attempt: str, seq: int, digest: str) -> dict[str, object]:
    return {"attempt_id": attempt, "kind": "effect", "pair_digest": pair, "result_sha256": digest, "sequence": seq}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    contract = json.loads((HERE / "contract.json").read_text())
    if hashlib.sha256(RECEIVER.read_bytes()).hexdigest() != contract["pins"]["receiver_sha256"]:
        raise SystemExit("receiver pin mismatch")

    artifact = b"project-original-effect-result-alpha-v0\n"
    artifact_digest = hashlib.sha256(artifact).hexdigest()
    cases: list[tuple[str, dict[str, object], dict[str, object] | None, bytes | None, str, str]] = []
    positive = witness(PAIR_ALPHA, "crash-attempt", True, [event(PAIR_ALPHA, "crash-attempt", 1, artifact_digest)])
    cases.append(("positive-alpha", ledger(PAIR_ALPHA, "crash-attempt"), positive, artifact, "EffectWitnessVerified", "OneMatchingEventAndResultDigest"))
    cases.append(("positive-replay", ledger(PAIR_ALPHA, "crash-attempt"), positive, artifact, "EffectWitnessVerified", "OneMatchingEventAndResultDigest"))
    cases.append(("no-effect-gamma", ledger(PAIR_GAMMA, "gamma-pending"), witness(PAIR_GAMMA, "gamma-pending", True, []), None, "NoEffectWitnessVerified", "CompleteFiniteChannelHasNoMatchingEvent"))
    cases.append(("incomplete-empty", ledger(PAIR_ALPHA, "crash-attempt"), witness(PAIR_ALPHA, "crash-attempt", False, []), None, "UnknownConsumptionState", "CoverageIncomplete"))
    cases.append(("missing-witness", ledger(PAIR_ALPHA, "crash-attempt"), None, None, "UnknownConsumptionState", "WitnessMissing"))
    conflict = witness(PAIR_ALPHA, "crash-attempt", True, [event(PAIR_ALPHA, "crash-attempt", 1, artifact_digest), event(PAIR_ALPHA, "crash-attempt", 2, "0" * 64)])
    cases.append(("conflicting-events", ledger(PAIR_ALPHA, "crash-attempt"), conflict, artifact, "UnknownConsumptionState", "ConflictingEffectEvents"))
    cases.append(("wrong-attempt", ledger(PAIR_ALPHA, "crash-attempt"), witness(PAIR_ALPHA, "other-attempt", True, []), None, "InvalidContext", "AttemptMismatch"))
    cases.append(("wrong-pair", ledger(PAIR_ALPHA, "crash-attempt"), witness(PAIR_GAMMA, "crash-attempt", True, []), None, "InvalidContext", "PairMismatch"))
    cases.append(("wrong-artifact", ledger(PAIR_ALPHA, "crash-attempt"), positive, b"wrong-result\n", "InvalidEvidence", "ResultDigestMismatch"))
    duplicate = witness(PAIR_ALPHA, "crash-attempt", True, [event(PAIR_ALPHA, "other", 1, artifact_digest), event(PAIR_GAMMA, "other", 1, artifact_digest)])
    cases.append(("duplicate-sequence", ledger(PAIR_ALPHA, "crash-attempt"), duplicate, None, "InvalidEvidence", "EventSequence"))

    assertions = 0
    receipts = []
    tool_seconds = 0.0
    before_supervisor = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    whole_start = time.perf_counter()
    for name, led, wit, art, expected, reason in cases:
        case = output / "cases" / name
        write_new(case / "ledger.json", led)
        witness_path = case / "witness.json"
        if wit is not None:
            write_new(witness_path, wit)
        artifact_path = case / "artifact.bin"
        if art is not None:
            write_new(artifact_path, art)
        ledger_before = (case / "ledger.json").read_bytes()
        witness_before = witness_path.read_bytes() if witness_path.exists() else None
        cmd = [sys.executable, str(RECEIVER), "--ledger", str(case / "ledger.json"), "--witness", str(witness_path)]
        if art is not None:
            cmd += ["--artifact", str(artifact_path)]
        started = time.perf_counter()
        proc = subprocess.run(cmd, capture_output=True, timeout=1, check=False)
        elapsed = time.perf_counter() - started
        tool_seconds += elapsed
        assert proc.returncode == 0; assertions += 1
        assert len(proc.stdout) <= 4096 and len(proc.stderr) <= 4096; assertions += 2
        receipt = json.loads(proc.stdout)
        assert receipt["outcome"] == expected; assertions += 1
        assert receipt["reason"] == reason; assertions += 1
        assert receipt["work_units"] <= 20_000; assertions += 1
        for flag in ("effect_authority", "retry_authority", "refund_authority", "mutation_authority", "native_authority", "free_authority"):
            assert receipt[flag] is False; assertions += 1
        assert (case / "ledger.json").read_bytes() == ledger_before; assertions += 1
        assert (witness_path.read_bytes() if witness_path.exists() else None) == witness_before; assertions += 1
        write_new(case / "receipt.json", receipt)
        receipts.append({"case": name, "elapsed_seconds": elapsed, "receipt": receipt})

    assert receipts[0]["receipt"] == receipts[1]["receipt"]; assertions += 1
    assert receipts[2]["receipt"]["pair_digest"] == PAIR_GAMMA; assertions += 1
    assert sum(1 for item in receipts if item["receipt"]["outcome"] == "EffectWitnessVerified") == 2; assertions += 1
    assert sum(1 for item in receipts if item["receipt"]["outcome"] == "NoEffectWitnessVerified") == 1; assertions += 1
    assert sum(1 for item in receipts if item["receipt"]["outcome"] == "UnknownConsumptionState") == 3; assertions += 1
    whole = time.perf_counter() - whole_start
    child_rss = resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
    supervisor_rss = max(before_supervisor, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    execution = {
        "profile": "adva.research.pending-effect-witness.execution.v0",
        "status": "Passed",
        "contract_sha256": hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest(),
        "receiver_sha256": hashlib.sha256(RECEIVER.read_bytes()).hexdigest(),
        "assertions": assertions,
        "tool_processes": len(cases),
        "target_processes": 0,
        "search_candidates": 0,
        "implementation_correction_replays": 0,
        "work_units": sum(item["receipt"]["work_units"] for item in receipts),
        "tool_seconds": tool_seconds,
        "whole_seconds": whole,
        "max_child_rss_kib": child_rss,
        "max_supervisor_rss_kib": supervisor_rss,
        "cases": receipts,
        "new_vocabulary": [],
        "limits_note": "No target was started. No-effect is relative only to the exact complete finite channel and sequence interval. RSS values are category maxima, not concurrent total memory.",
    }
    write_new(output / "execution.json", execution)
    write_new(output / "contract.json", (HERE / "contract.json").read_bytes())
    print(canonical(execution).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
