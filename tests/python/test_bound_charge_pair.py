import importlib.util
import json
from pathlib import Path
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "experiments" / "bound_charge_pair" / "run.py"


def load_runner():
    spec = importlib.util.spec_from_file_location("bound_charge_pair", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bound_charge_pair():
    runner = load_runner()
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory) / "evidence"
        assert runner.main(output) == 0
        report = json.loads((output / "execution.json").read_bytes())
        assert report["status"] == "Passed"
        assert report["receiver_processes"] == 9
        assert report["target_processes"] == 0
        assert report["implementation_correction_replays"] == 0
        assert report["new_vocabulary"] == []
        outcomes = {item["case"]: item["outcome"] for item in report["receipts"]}
        assert outcomes["exact-alpha"] == "BindingVerified"
        assert outcomes["exact-gamma"] == "BindingVerified"
        assert outcomes["replay-alpha"] == "BindingVerified"
        assert outcomes["reuse-alpha-id-by-beta"] == "InvalidContext"
        assert report["representation_cost"]["baseline_totals_only_authorizations"] == 2
        assert report["representation_cost"]["v1_bound_matches_for_same_charge_id_across_two_tasks"] == 1

    claims = tomllib.loads((ROOT / "docs" / "claims.toml").read_text())["claim"]
    claim = next(item for item in claims
                 if item["claim_id"] == "adva.bounded-experiment.bound-charge-pair.v0")
    assert claim["status"] == "bounded-experiment"
    index = (ROOT / "docs" / "research" / "README.md").read_text()
    assert "0246-one-charge-one-task-bound-pair.md" in index
