import importlib.util
import json
from pathlib import Path
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "experiments" / "cumulative_charge_gap" / "run.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("cumulative_charge_gap", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_cumulative_charge_gap():
    runner = load_runner()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "evidence"
        assert runner.main(output) == 0
        report = json.loads((output / "execution.json").read_bytes())
        assert report["status"] == "Passed"
        assert report["receiver_processes"] == 5
        assert report["target_processes"] == 0
        assert report["implementation_correction_replays"] == 0
        assert report["new_vocabulary"] == []
        assert all(item["outcome"] == "UnknownAttemptState"
                   for item in report["receipts"])

    claims = tomllib.loads((ROOT / "docs" / "claims.toml").read_text())["claim"]
    claim = next(item for item in claims
                 if item["claim_id"] == "adva.bounded-experiment.cumulative-charge-gap.v0")
    assert claim["status"] == "bounded-experiment"
    index = (ROOT / "docs" / "research" / "README.md").read_text()
    assert "0245-a-charge-without-a-task-binding-cannot-authorize-a-launch.md" in index
