import importlib.util
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "continuation_resolution_crosscheck"


def load_runner():
    spec = importlib.util.spec_from_file_location("continuation_resolution_crosscheck",
                                                  EXPERIMENT / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retained_crosscheck_evidence_and_claim():
    result = json.loads((EXPERIMENT / "evidence" / "attempt-1" / "execution.json").read_bytes())
    assert result["status"] == "Passed"
    assert result["assertions"] == 104
    assert result["node_processes"] == 10
    assert result["python_receiver_processes"] == 0
    assert result["target_processes"] == 0
    assert result["implementation_correction_replays"] == 0
    assert result["node_work_units"] <= 40_000
    assert result["comparison_work_units"] <= 1_000
    assert result["source_sha256"]["python_receiver"] != \
        result["source_sha256"]["node_receiver"]
    assert all(case["comparison"]["outcome"] == "ImplementationAgreement"
               for case in result["cases"])
    assert all(control["outcome"] == "UnknownImplementationAgreement"
               for control in result["controls"].values())
    claims = (ROOT / "docs" / "claims.toml").read_text()
    assert claims.count(
        'claim_id = "adva.bounded-experiment.continuation-resolution-crosscheck.v0"'
    ) == 1


def test_fresh_crosscheck_replays_the_frozen_projection():
    runner = load_runner()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "evidence"
        assert runner.main(output) == 0
        result = json.loads((output / "execution.json").read_bytes())
        assert result["status"] == "Passed"
        assert result["node_processes"] == 10
        assert result["node_work_units"] <= 40_000
        assert [case["node_outcome"] for case in result["cases"]].count(
            "ContinuationReady"
        ) == 2
        assert all(case["input_sha256_before"] == case["input_sha256_after"]
                   for case in result["cases"])
