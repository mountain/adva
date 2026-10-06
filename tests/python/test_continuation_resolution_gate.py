import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "continuation_resolution_gate"


def test_retained_gate_evidence_and_claim():
    execution = json.loads(
        (EXPERIMENT / "evidence" / "attempt-2" / "execution.json").read_text()
    )
    summary = json.loads((EXPERIMENT / "evidence" / "summary.json").read_text())
    failure = json.loads(
        (EXPERIMENT / "evidence" / "prior-implementation-failure.json").read_text()
    )
    claims = (ROOT / "docs" / "claims.toml").read_text()
    assert execution["status"] == "Passed"
    assert execution["python_optimize"] == 1
    assert execution["assertions"] == 75
    assert execution["receiver_processes"] == 10
    assert execution["target_processes"] == 0
    assert execution["work_units"] == 25960
    outcomes = [case["receipt"]["outcome"] for case in execution["cases"]]
    assert outcomes.count("ContinuationReady") == 2
    assert outcomes.count("UnknownContinuationState") == 5
    assert outcomes.count("InvalidEvidence") == 3
    assert all(case["receipt"]["fuel_delta"] == 0 for case in execution["cases"])
    assert all(
        case["metrics"]["input_sha256_before"]
        == case["metrics"]["input_sha256_after"]
        for case in execution["cases"]
    )
    assert summary["aggregate"]["receiver_processes"] == 19
    assert summary["aggregate"]["implementation_correction_replays"] == 1
    assert failure["classification"] == "ImplementationFailure"
    assert claims.count(
        'claim_id = "adva.bounded-experiment.continuation-resolution-gate.v0"'
    ) == 1


def test_fresh_optimized_run_preserves_the_gate(tmp_path):
    output = tmp_path / "fresh"
    subprocess.run(
        [
            sys.executable,
            "-O",
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
    assert result["python_optimize"] == 1
    assert result["assertions"] == 75
    assert result["receiver_processes"] == 10
    assert result["target_processes"] == 0
    assert result["work_units"] <= 40000
    assert result["boundary"]["assert_dependent_checks"] is False
    assert result["boundary"]["fuel_delta"] == 0
