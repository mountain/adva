#!/usr/bin/env python3
"""Run the frozen recovery-receipt application scenarios."""

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
APPLY = HERE / "apply.py"
PARENT_RECEIVER = HERE.parent / "pending_effect_witness" / "receiver.py"
PAIR_ALPHA = "8b04c08985545f4392ab7ab62f568889d414b046cb04e15a6b02b2860f2b3611"
PAIR_GAMMA = "51d24380c79274b9ad21b9f45d36013256a2b1e9ef7f340343704d845ed223da"
PAIR_DELTA = "3" * 64
PAIR_EPSILON = "4" * 64


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def write_new(path: Path, value: object | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = value if isinstance(value, bytes) else canonical(value)
    with path.open("xb") as stream:
        stream.write(raw)


def pending(pair: str, attempt: str) -> dict[str, object]:
    return {"attempt_id": attempt, "pair_digest": pair, "profile": "single-consumption-ledger-v0", "receipt_digest": None, "state": "pending"}


def witness(pair: str, attempt: str, events: list[dict[str, object]], complete: bool = True) -> dict[str, object]:
    return {"attempt_id": attempt, "channel_id": "project-original-application-channel-v0", "coverage_complete": complete, "events": events, "pair_digest": pair, "profile": "pending-effect-witness-v0", "sequence_end": 3, "sequence_start": 0}


def event(pair: str, attempt: str, result_digest: str) -> dict[str, object]:
    return {"attempt_id": attempt, "kind": "effect", "pair_digest": pair, "result_sha256": result_digest, "sequence": 1}


def run_process(command: list[str], expected: int = 0) -> tuple[subprocess.CompletedProcess[bytes], float]:
    started = time.perf_counter()
    proc = subprocess.run(command, capture_output=True, timeout=1, check=False)
    elapsed = time.perf_counter() - started
    assert proc.returncode == expected
    assert len(proc.stdout) <= 4096 and len(proc.stderr) <= 4096
    return proc, elapsed


def make_recovery(root: Path, name: str, pair: str, attempt: str, *, effect: bool, complete: bool = True) -> tuple[dict[str, object], float]:
    case = root / "parent" / name
    artifact = ("project-original-" + name + "-result-v0\n").encode()
    artifact_digest = hashlib.sha256(artifact).hexdigest()
    led = pending(pair, attempt)
    events = [event(pair, attempt, artifact_digest)] if effect else []
    write_new(case / "ledger.json", led)
    write_new(case / "witness.json", witness(pair, attempt, events, complete))
    command = [sys.executable, str(PARENT_RECEIVER), "--ledger", str(case / "ledger.json"), "--witness", str(case / "witness.json")]
    if effect:
        write_new(case / "artifact.bin", artifact)
        command += ["--artifact", str(case / "artifact.bin")]
    proc, elapsed = run_process(command)
    receipt = json.loads(proc.stdout)
    write_new(case / "receipt.json", receipt)
    return receipt, elapsed


def apply_once(ledger: Path, receipt: Path, extra: list[str] | None = None, expected: int = 0) -> tuple[dict[str, object] | None, float]:
    command = [sys.executable, str(APPLY), "--ledger", str(ledger), "--recovery", str(receipt)] + (extra or [])
    proc, elapsed = run_process(command, expected)
    return (json.loads(proc.stdout) if proc.stdout else None), elapsed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output
    output.mkdir(parents=True, exist_ok=False)
    contract_raw = (HERE / "contract.json").read_bytes()
    contract = json.loads(contract_raw)
    assert hashlib.sha256(APPLY.read_bytes()).hexdigest() == contract["pins"]["application_sha256"]
    assert hashlib.sha256(PARENT_RECEIVER.read_bytes()).hexdigest() == contract["pins"]["parent_receiver_sha256"]

    assertions = 2
    tool_seconds = 0.0
    summaries: list[dict[str, object]] = []
    before_supervisor = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    whole_start = time.perf_counter()

    specifications = [
        ("alpha-positive", PAIR_ALPHA, "alpha-pending", True, True),
        ("gamma-negative", PAIR_GAMMA, "gamma-pending", False, True),
        ("delta-positive", PAIR_DELTA, "delta-pending", True, True),
        ("epsilon-positive", PAIR_EPSILON, "epsilon-pending", True, True),
        ("epsilon-negative", PAIR_EPSILON, "epsilon-pending", False, True),
        ("alpha-incomplete", PAIR_ALPHA, "alpha-pending", False, False),
    ]
    receipts: dict[str, dict[str, object]] = {}
    receipt_paths: dict[str, Path] = {}
    for name, pair, attempt, effect, complete in specifications:
        value, elapsed = make_recovery(output, name, pair, attempt, effect=effect, complete=complete)
        tool_seconds += elapsed
        receipts[name] = value
        receipt_paths[name] = output / "parent" / name / "receipt.json"
    assert receipts["alpha-positive"]["outcome"] == "EffectWitnessVerified"; assertions += 1
    assert receipts["gamma-negative"]["outcome"] == "NoEffectWitnessVerified"; assertions += 1
    assert receipts["alpha-incomplete"]["outcome"] == "UnknownConsumptionState"; assertions += 1

    def new_ledger(name: str, pair: str, attempt: str) -> Path:
        path = output / "application" / name / "ledger.json"
        write_new(path, pending(pair, attempt))
        return path

    # Positive completion and exact replay refusal.
    alpha = new_ledger("alpha", PAIR_ALPHA, "alpha-pending")
    first, elapsed = apply_once(alpha, receipt_paths["alpha-positive"]); tool_seconds += elapsed
    alpha_terminal = alpha.read_bytes()
    replay, elapsed = apply_once(alpha, receipt_paths["alpha-positive"]); tool_seconds += elapsed
    assert first and first["outcome"] == "ResolutionApplied" and first["state"] == "completed" and first["ledger_mutated"] is True; assertions += 4
    assert replay and replay["outcome"] == "ReplayRefused" and alpha.read_bytes() == alpha_terminal; assertions += 2
    summaries += [{"case": "alpha-complete", "receipt": first}, {"case": "alpha-replay", "receipt": replay}]

    # Scoped cancellation and exact replay refusal.
    gamma = new_ledger("gamma", PAIR_GAMMA, "gamma-pending")
    cancelled, elapsed = apply_once(gamma, receipt_paths["gamma-negative"]); tool_seconds += elapsed
    gamma_terminal = gamma.read_bytes()
    gamma_replay, elapsed = apply_once(gamma, receipt_paths["gamma-negative"]); tool_seconds += elapsed
    terminal_value = json.loads(gamma_terminal)
    assert cancelled and cancelled["outcome"] == "ResolutionApplied" and cancelled["state"] == "cancelled"; assertions += 3
    assert terminal_value["channel_id"] == "project-original-application-channel-v0" and terminal_value["coverage"] == [0, 3] and terminal_value["result_sha256"] is None; assertions += 3
    assert gamma_replay and gamma_replay["outcome"] == "ReplayRefused" and gamma.read_bytes() == gamma_terminal; assertions += 2
    summaries += [{"case": "gamma-cancel", "receipt": cancelled}, {"case": "gamma-replay", "receipt": gamma_replay}]

    # Insufficient and wrong-context evidence preserve pending bytes.
    unknown = new_ledger("unknown", PAIR_ALPHA, "alpha-pending")
    unknown_before = unknown.read_bytes()
    unknown_receipt, elapsed = apply_once(unknown, receipt_paths["alpha-incomplete"]); tool_seconds += elapsed
    wrong = new_ledger("wrong-context", PAIR_GAMMA, "other-gamma")
    wrong_before = wrong.read_bytes()
    wrong_receipt, elapsed = apply_once(wrong, receipt_paths["alpha-positive"]); tool_seconds += elapsed
    assert unknown_receipt and unknown_receipt["outcome"] == "UnknownConsumptionState" and unknown.read_bytes() == unknown_before; assertions += 2
    assert wrong_receipt and wrong_receipt["outcome"] == "InvalidContext" and wrong.read_bytes() == wrong_before; assertions += 2
    summaries += [{"case": "insufficient", "receipt": unknown_receipt}, {"case": "wrong-context", "receipt": wrong_receipt}]

    # Exit after durable replacement leaves a terminal; replay is refused.
    delta = new_ledger("delta-crash", PAIR_DELTA, "delta-pending")
    absent, elapsed = apply_once(delta, receipt_paths["delta-positive"], ["--crash-after-replace"], expected=24); tool_seconds += elapsed
    delta_after = json.loads(delta.read_bytes())
    delta_replay, elapsed = apply_once(delta, receipt_paths["delta-positive"]); tool_seconds += elapsed
    assert absent is None and delta_after["state"] == "completed"; assertions += 2
    assert delta_replay and delta_replay["outcome"] == "ReplayRefused"; assertions += 1
    summaries += [{"case": "post-replace-exit", "process_exit": 24, "ledger_state": delta_after["state"]}, {"case": "post-replace-replay", "receipt": delta_replay}]

    # Two contradictory receipts race for one new slot: one transition, one refusal.
    epsilon = new_ledger("epsilon-race", PAIR_EPSILON, "epsilon-pending")
    commands = []
    for key in ("epsilon-positive", "epsilon-negative"):
        commands.append([sys.executable, str(APPLY), "--ledger", str(epsilon), "--recovery", str(receipt_paths[key])])
    started = time.perf_counter()
    children = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) for command in commands]
    race_receipts = []
    for child in children:
        stdout, stderr = child.communicate(timeout=1)
        assert child.returncode == 0 and len(stdout) <= 4096 and len(stderr) <= 4096; assertions += 3
        race_receipts.append(json.loads(stdout))
    tool_seconds += time.perf_counter() - started
    race_outcomes = sorted(item["outcome"] for item in race_receipts)
    assert race_outcomes == ["ConflictRefused", "ResolutionApplied"]; assertions += 1
    epsilon_terminal = json.loads(epsilon.read_bytes())
    assert epsilon_terminal["state"] in ("completed", "cancelled"); assertions += 1
    summaries += [{"case": "epsilon-race", "receipts": race_receipts, "terminal_state": epsilon_terminal["state"]}]

    for summary in summaries:
        values = summary.get("receipts", [summary.get("receipt")])
        for value in values:
            if not value:
                continue
            for flag in ("effect_authority", "retry_authority", "refund_authority", "native_authority", "free_authority"):
                assert value[flag] is False; assertions += 1
            assert value["target_processes"] == 0; assertions += 1

    whole = time.perf_counter() - whole_start
    all_receipts = [s.get("receipt") for s in summaries if s.get("receipt")] + race_receipts
    work_units = sum(int(item["work_units"]) for item in all_receipts)
    assert work_units <= contract["limits"]["work_units_total"]; assertions += 1
    execution = {
        "profile": "adva.research.recovery-receipt-application.execution.v0",
        "status": "Passed",
        "contract_sha256": hashlib.sha256(contract_raw).hexdigest(),
        "application_sha256": hashlib.sha256(APPLY.read_bytes()).hexdigest(),
        "parent_receiver_sha256": hashlib.sha256(PARENT_RECEIVER.read_bytes()).hexdigest(),
        "assertions": assertions,
        "parent_receiver_processes": 6,
        "application_processes": 10,
        "tool_processes": 16,
        "target_processes": 0,
        "search_candidates": 0,
        "implementation_correction_replays": 1,
        "work_units": work_units,
        "unreceipted_post_replace_exit_work": "unmeasured",
        "tool_seconds": tool_seconds,
        "whole_seconds": whole,
        "max_child_rss_kib": resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
        "max_supervisor_rss_kib": max(before_supervisor, resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "cases": summaries,
        "new_vocabulary": [],
        "limits_note": "RSS values are category maxima, not a concurrent total. Cancelled is scoped to the retained finite channel and interval and grants no retry. The post-replace exit emitted no application receipt, so its structural work is unmeasured rather than zero."
    }
    write_new(output / "execution.json", execution)
    write_new(output / "contract.json", contract_raw)
    print(canonical(execution).decode())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
