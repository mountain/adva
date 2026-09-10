"""Requires the real installed adva extension; no native mock or skip."""
import importlib.util
from pathlib import Path


def test_finite_pairing_transport_and_native_history():
    path = Path(__file__).resolve().parents[2] / "experiments/pairing_transport/replay.py"
    spec = importlib.util.spec_from_file_location("pairing_transport_research", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.run()
    assert report["native"]["status"] == "FiniteNativePass"
    assert report["native"]["evaluations"] == 1155
    assert len(report["exact"]["rows"]) == 384
    assert report["source_drift_control"] == "Rejected"
