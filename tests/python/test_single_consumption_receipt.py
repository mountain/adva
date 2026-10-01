import importlib.util
import json
from pathlib import Path
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "experiments" / "single_consumption_receipt" / "run.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("single_consumption_receipt", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_single_consumption_receipt():
    runner = load_runner()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "evidence"
        assert runner.main(output) == 0
        report = json.loads((output / "execution.json").read_bytes())
        assert report["status"] == "Passed"
        assert report["tool_processes"] == 16
        assert report["target_processes"] == 0
        assert report["implementation_correction_replays"] == 0
        assert report["new_vocabulary"] == []
        outcomes = [item["outcome"] for item in report["records"]]
        assert outcomes.count("ConsumedRecorded") == 2
        assert outcomes.count("PendingRecorded") == 3
        assert outcomes.count("UnknownConsumptionState") == 4
        assert "ImplementationExitAfterPending" in outcomes

    claims = tomllib.loads((ROOT / "docs" / "claims.toml").read_text())["claim"]
    claim = next(item for item in claims
                 if item["claim_id"] == "adva.bounded-experiment.single-consumption-receipt.v0")
    assert claim["status"] == "bounded-experiment"
    index = (ROOT / "docs" / "research" / "README.md").read_text()
    assert "0248-one-consumption-chain-and-the-pending-unknown.md" in index
