"""Halting knowledge must include both certified outcomes and retain every unknown."""
import copy
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/depth_curve"
spec = importlib.util.spec_from_file_location("depth_curve_v1", HERE / "calibration.py")
ledger = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ledger)


def test_fresh_process_replays_corrected_ledger(tmp_path):
    output = tmp_path / "ledger.json"
    subprocess.run([sys.executable, str(HERE / "calibration.py"), str(output)],
                   check=True, timeout=30, capture_output=True)
    assert json.loads(output.read_text()) == json.loads((HERE / "evidence-v1.json").read_text())


def test_every_depth_has_honest_monotone_bounds():
    rows = ledger.build()["curve"]
    for row in rows:
        ledger.validate_row(row)
    for a, b in zip(rows, rows[1:]):
        assert Fraction(a["lower"]) <= Fraction(b["lower"])
        assert Fraction(a["upper"]) >= Fraction(b["upper"])
    final = rows[-1]
    assert final["decided_mass"] == "26079/32768"
    assert final["certified_nonhalting_mass"] == "1/32768"
    assert final["unresolved_mass"] == final["named_unresolved_mass"] == "6689/32768"


@pytest.mark.parametrize("alteration", ["old_classification", "forget_named", "wrong_upper"])
def test_wrong_knowledge_partition_is_rejected(alteration):
    row = copy.deepcopy(ledger.build()["curve"][-1])
    if alteration == "old_classification":
        row["decided_mass"] = "32767/32768"
        row["unresolved_mass"] = "1/32768"
    elif alteration == "forget_named":
        row["unresolved_mass"] = "0"
    else:
        row["upper"] = "1"
    with pytest.raises(ValueError):
        ledger.validate_row(row)
