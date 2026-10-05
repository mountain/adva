import importlib.util
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / "continuation_resolution_heldout"


def load_runner():
    spec = importlib.util.spec_from_file_location("continuation_resolution_heldout",
                                                  EXPERIMENT / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retained_heldout_evidence():
    result = json.loads((EXPERIMENT / "evidence" / "attempt-1" / "execution.json").read_bytes())
    assert result["status"] == "Passed"
    assert result["assertions"] == 71
    assert result["constructor_processes"] == 1
    assert result["python_receiver_processes"] == 2
    assert result["node_receiver_processes"] == 2
    assert result["target_processes"] == 0
    assert result["search_candidates"] == 0
    assert result["implementation_correction_replays"] == 0
    assert result["constructor_work_units"] <= 40_000
    assert result["receiver_work_units"] <= 50_000
    assert result["comparison_work_units"] <= 100
    assert len(set(result["source_sha256"].values())) == 3
    assert all(case["comparison"]["outcome"] == "ImplementationAgreement"
               for case in result["cases"])
    assert all(case["input_sha256_before"] == case["input_sha256_after"]
               for case in result["cases"])
    assert all(control["outcome"] == "UnknownImplementationAgreement"
               for control in result["controls"].values())


def test_fresh_heldout_construction_has_no_answer_input():
    runner = load_runner()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "evidence"
        assert runner.main(output) == 0
        result = json.loads((output / "execution.json").read_bytes())
        manifest = json.loads((output / "constructed" / "manifest.json").read_bytes())
        assert result["status"] == "Passed"
        assert result["boundary"]["constructor_supplies_expected_classification"] is False
        assert result["boundary"]["comparator_supplies_expected_classification"] is False
        assert manifest["receiver_classification_supplied"] is False
        assert all(set(case) == {"case_id", "input_sha256"}
                   for case in manifest["cases"])
        assert [case["case_id"] for case in result["cases"]] == ["rho", "tau"]
