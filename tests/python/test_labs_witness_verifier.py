from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_verifier() -> ModuleType:
    path = Path(__file__).parents[2] / "experiments" / "labs-search" / "verify.py"
    spec = importlib.util.spec_from_file_location("adva_labs_verify", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load verifier at {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_independent_labs_verifier_accepts_an_exact_witness() -> None:
    verifier = _load_verifier()
    sequence = [1, -1, 1, 1, -1, 1, 1, 1, -1, -1, -1]
    evaluation = verifier.evaluate_sequence(sequence)
    payload = {
        "best": {
            "length": len(sequence),
            "sequence": sequence,
            "correlations": list(evaluation.correlations),
            "energy": evaluation.energy,
            "merit_factor": evaluation.merit_factor,
        }
    }

    checked = verifier.verify_payload(payload)

    assert checked.energy == 5
    assert checked.length == 11


def test_independent_labs_verifier_rejects_a_corrupted_energy() -> None:
    verifier = _load_verifier()
    sequence = [1, 1, 1, -1, 1, -1, -1]
    evaluation = verifier.evaluate_sequence(sequence)
    payload = {
        "length": len(sequence),
        "sequence": sequence,
        "correlations": list(evaluation.correlations),
        "energy": evaluation.energy + 1,
        "merit_factor": evaluation.merit_factor,
    }

    try:
        verifier.verify_payload(payload)
    except ValueError as error:
        assert "energy" in str(error)
    else:
        raise AssertionError("corrupted energy must be rejected")
