import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "recovery_receipt_application"


def test_retained_execution_and_claim_boundary():
    evidence = json.loads(
        (EXPERIMENT / "evidence" / "attempt-1" / "execution.json").read_text()
    )
    contract = json.loads((EXPERIMENT / "contract.json").read_text())
    claims = (ROOT / "docs" / "claims.toml").read_text()
    assert evidence["status"] == "Passed"
    assert evidence["assertions"] == 89
    assert evidence["tool_processes"] == 16
    assert evidence["target_processes"] == 0
    assert evidence["search_candidates"] == 0
    assert evidence["implementation_correction_replays"] == 1
    assert evidence["work_units"] <= contract["limits"]["work_units_total"]
    assert claims.count(
        'claim_id = "adva.bounded-experiment.recovery-receipt-application.v0"'
    ) == 1
    assert (
        ROOT
        / "docs"
        / "research"
        / "0251-atomic-recovery-application-and-scoped-cancellation.md"
    ).exists()


def test_fresh_run_preserves_the_finite_application_invariants(tmp_path):
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
    assert result["assertions"] == 89
    assert result["parent_receiver_processes"] == 6
    assert result["application_processes"] == 10
    assert result["target_processes"] == 0
    assert result["search_candidates"] == 0
    assert result["implementation_correction_replays"] == 1
    assert result["work_units"] <= 50_000
    race = next(case for case in result["cases"] if case["case"] == "epsilon-race")
    assert sorted(receipt["outcome"] for receipt in race["receipts"]) == [
        "ConflictRefused",
        "ResolutionApplied",
    ]
    assert race["terminal_state"] in ("completed", "cancelled")
