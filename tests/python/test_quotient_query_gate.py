"""Frozen replay for Research 0262."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments" / "quotient_query_gate"


def load(name):
    spec = importlib.util.spec_from_file_location("adva_qgate_" + name, HERE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


producer, verifier = load("producer"), load("verifier")


def test_frozen_result_and_receiver():
    contract = json.loads((HERE / "contract.json").read_text())
    frozen = json.loads((HERE / "evidence" / "result.json").read_text())
    assert producer.produce(contract) == frozen
    receipt = verifier.verify(contract, frozen)
    assert receipt["status"] == "Verified"
    assert receipt["receiver_candidate_families"] == 65824
    assert all(x["outcome"] == "Rejected" for x in verifier.controls(contract, frozen))


def test_gate_reuse_and_nonunique_lifts():
    frozen = json.loads((HERE / "evidence" / "result.json").read_text())
    three, four = frozen["fixtures"]
    assert three["saturated_exact_masks"] == [0, 3, 4, 7]
    assert three["basic"]["lift_multiplicity"] == {"1,3": 3, "2,3": 1}
    assert three["gates"]["1"] == {"status": "NonSaturated", "counterexample": [0, 1]}
    assert four["saturated_exact_masks"] == [0, 3, 12, 15]
    assert four["basic"]["lift_multiplicity"] == {"1,3": 6, "2,3": 6}
    assert four["gates"]["4"] == {"status": "NonSaturated", "counterexample": [2, 3]}


if __name__ == "__main__":
    test_frozen_result_and_receiver()
    test_gate_reuse_and_nonunique_lifts()
