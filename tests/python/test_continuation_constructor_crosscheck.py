import importlib.util
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "continuation_constructor_crosscheck"


def load_runner():
    spec = importlib.util.spec_from_file_location("continuation_constructor_crosscheck",
                                                  EXPERIMENT / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retained_constructor_crosscheck_evidence():
    result = json.loads((EXPERIMENT / "evidence" / "attempt-2" / "execution.json").read_bytes())
    summary = json.loads((EXPERIMENT / "evidence" / "summary.json").read_bytes())
    failure = json.loads((EXPERIMENT / "evidence" /
                          "prior-preexecution-failure.json").read_bytes())
    assert result["status"] == "Passed"
    assert result["java_constructor_processes"] == 1
    assert result["perl_constructor_processes"] == 1
    assert result["receiver_processes"] == 0
    assert result["target_processes"] == 0
    assert result["search_candidates"] == 0
    assert result["implementation_correction_replays"] == 0
    assert result["comparison"]["outcome"] == "ImplementationAgreement"
    assert result["comparison"]["compared_files"] == 14
    assert len(result["payload_sha256"]) == 14
    assert len(set(result["source_sha256"].values())) == 3
    assert all(control["outcome"] == "UnknownImplementationAgreement"
               for control in result["controls"].values())
    assert result["boundary"]["java_ran_before_perl_output_existed"] is True
    assert result["boundary"]["agreement_is_receipt_truth"] is False
    assert summary["aggregate"]["implementation_correction_replays"] == 1
    assert failure["classification"] == "PreExecutionImplementationFailure"
    assert failure["child_processes_started"] == 0


def test_fresh_constructor_crosscheck_replays_the_frozen_projection():
    runner = load_runner()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "evidence"
        assert runner.main(output) == 0
        result = json.loads((output / "execution.json").read_bytes())
        assert result["status"] == "Passed"
        assert result["comparison"]["outcome"] == "ImplementationAgreement"
        assert result["comparison"]["compared_files"] == 14
        assert all(control["outcome"] == "UnknownImplementationAgreement"
                   for control in result["controls"].values())
