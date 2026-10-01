import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "terminal_resolution_receiver"


def test_retained_execution_and_claim_boundary():
    evidence = json.loads(
        (EXPERIMENT / "evidence" / "attempt-1" / "execution.json").read_text()
    )
    contract = json.loads((EXPERIMENT / "contract.json").read_text())
    claims = (ROOT / "docs" / "claims.toml").read_text()
    assert evidence["status"] == "Passed"
    assert evidence["assertions"] == 58
    assert evidence["receiver_processes"] == 10
    assert evidence["target_processes"] == 0
    assert evidence["search_candidates"] == 0
    assert evidence["implementation_correction_replays"] == 1
    assert evidence["work_units"] <= contract["limits"]["work_units_total"]
    assert evidence["boundary"]["opens_lock_file"] is False
    assert evidence["boundary"]["opens_mutable_runtime_ledger"] is False
    assert claims.count(
        'claim_id = "adva.bounded-experiment.terminal-resolution-receiver.v0"'
    ) == 1
    assert (
        ROOT
        / "docs"
        / "research"
        / "0252-read-only-terminal-resolution-receiving.md"
    ).exists()


def test_fresh_run_preserves_the_finite_receiving_boundary(tmp_path):
    output = tmp_path / "fresh"
    subprocess.run(
        [
            sys.executable,
            str(EXPERIMENT / "run.py"),
            "--output",
            str(output),
        ],
        check=True,
        timeout=20,
        capture_output=True,
    )
    result = json.loads((output / "execution.json").read_text())
    assert result["status"] == "Passed"
    assert result["assertions"] == 58
    assert result["receiver_processes"] == 10
    assert result["target_processes"] == 0
    assert result["search_candidates"] == 0
    assert result["implementation_correction_replays"] == 1
    assert result["work_units"] <= 30_000
    outcomes = [case["receipt"]["outcome"] for case in result["cases"]]
    assert outcomes.count("ResolutionVerified") == 3
    assert outcomes.count("UnknownResolutionState") == 6
    assert outcomes.count("InvalidEvidence") == 1
    assert all(
        case["metrics"]["input_sha256_before"]
        == case["metrics"]["input_sha256_after"]
        for case in result["cases"]
    )
