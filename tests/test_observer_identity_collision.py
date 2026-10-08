import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT / "experiments" / "observer_identity_collision"


def load_runner():
    spec = importlib.util.spec_from_file_location(
        "observer_identity_collision", EXPERIMENT / "run.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_retained_observer_identity_collision():
    result = json.loads((EXPERIMENT / "evidence" / "result.json").read_bytes())
    execution = json.loads((EXPERIMENT / "evidence" / "execution.json").read_bytes())
    assert result["status"] == "PassedFiniteCounterexample"
    assert result["scope"]["exact_states"] == 40
    assert result["scope"]["unordered_state_pairs"] == 780
    assert result["result"]["fixed_carrier_membership_collisions"] == 0
    assert result["result"]["cross_carrier_membership_collisions"] == 140
    assert result["result"]["profile_collision_counts"] == {
        "event-only": 140,
        "event-source": 60,
        "event-source-occurrence": 20,
        "event-source-occurrence-history": 0,
    }
    assert result["boundary"]["native_adva_carrier"] is False
    assert result["boundary"]["new_vocabulary"] == []
    assert execution["comparison_units"] == 3900
    assert execution["implementation_correction_replays"] == 1
    assert execution["result_sha256"] == hashlib.sha256(
        (EXPERIMENT / "evidence" / "result.json").read_bytes()).hexdigest()


def test_fresh_observer_identity_collision_replay():
    runner = load_runner()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "evidence"
        assert runner.main(output) == 0
        assert (output / "result.json").read_bytes() == (
            EXPERIMENT / "evidence" / "result.json").read_bytes()
        for retained in sorted((EXPERIMENT / "evidence" / "controls").glob("*.json")):
            assert (output / "controls" / retained.name).read_bytes() == retained.read_bytes()
