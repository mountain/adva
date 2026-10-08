import importlib.util
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "continuation_constructor_generalization"


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "continuation_constructor_generalization", EXPERIMENT / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retained_third_instance_evidence():
    result = json.loads(
        (EXPERIMENT / "evidence" / "attempt-1" / "execution.json").read_bytes())
    manifest = json.loads((EXPERIMENT / "evidence" / "manifest.json").read_bytes())
    assert result["status"] == "Passed"
    assert result["assertions"] == 37
    assert result["source_freeze_commit"] == \
        "3c448a2358f8ab3a325b9fe7ea28f1b4d9ae6b6c"
    assert result["java_constructor_processes"] == 1
    assert result["perl_constructor_processes"] == 1
    assert result["receiver_processes"] == 0
    assert result["target_processes"] == 0
    assert result["search_candidates"] == 0
    assert result["implementation_correction_replays"] == 0
    assert result["comparison"]["outcome"] == "ImplementationAgreement"
    assert result["comparison"]["compared_files"] == 7
    assert len(result["payload_sha256"]) == 7
    assert len(set(result["source_sha256"].values())) == 3
    assert result["third_instance"]["identifiers_absent_from_frozen_sources"] is True
    assert all(control["outcome"] == "UnknownImplementationAgreement"
               for control in result["controls"].values())
    assert result["boundary"]["agreement_is_mathematical_truth"] is False
    assert result["boundary"]["new_vocabulary"] == []
    assert manifest["status"] == "Complete"
    assert manifest["file_count"] == 21
    assert manifest["total_bytes"] == 10050


def test_fresh_generic_constructors_replay_third_instance():
    runner = load_runner()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "evidence"
        assert runner.main(output) == 0
        result = json.loads((output / "execution.json").read_bytes())
        assert result["status"] == "Passed"
        assert result["comparison"]["outcome"] == "ImplementationAgreement"
        assert result["comparison"]["compared_files"] == 7
        assert all(control["outcome"] == "UnknownImplementationAgreement"
                   for control in result["controls"].values())
