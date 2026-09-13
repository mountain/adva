"""Replay check for the inverse-norm obstruction.

The retained evidence is not trusted: the calibration is re-run on a temporary
copy carrying the sibling round, and every non-timing field must match. The exact
conversion, the constant-term argument and the measured growth are asserted
separately.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/feigenbaum_inverse_norm_obstruction"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0180-inverse-norm-obstruction.md"
CLAIMS = ROOT / "docs/claims.toml"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    copied = tmp_path / "feigenbaum_inverse_norm_obstruction"
    shutil.copytree(EXPERIMENT, copied)
    shutil.copytree(EXPERIMENT.parent / "feigenbaum_kantorovich_preflight",
                    tmp_path / "feigenbaum_kantorovich_preflight")
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py")],
        cwd=copied, capture_output=True, text=True, timeout=900, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    fresh = load(copied / "evidence.json")
    retained = load(EVIDENCE)
    fresh.pop("cost", None)
    retained.pop("cost", None)
    assert fresh == retained
    assert retained["status"] == "ExternalExactPass"
    assert all(retained["checks"].values())


def test_the_conversion_is_exact_but_the_numbers_are_hopeless():
    conversion = load(EVIDENCE)["norm_conversion"]
    assert conversion["exactly_invertible"]
    assert float(conversion["residual_max_abs_entry"]) == 0.0
    assert float(conversion["weighted_l1_norm_of_the_inverse"]) > 1e9
    assert float(conversion["infinity_norm_of_the_inverse"]) < 1e4
    assert float(conversion["ratio_to_the_previous_rounds_infinity_norm"]) > 1e6


def test_the_inner_series_forces_the_obstruction():
    report = load(EVIDENCE)
    inner = report["inner_series"]
    assert inner["constant_term"] == "1"
    assert float(inner["weighted_l1_norm_of_the_inner_series"]) > 1.0
    assert inner["norm_exceeds_one"]
    controls = report["radius_control"]["alternatives"]
    assert set(controls) == {"1/64", "1/128"}
    assert all(entry["still_exceeds_one"] for entry in controls.values())


def test_the_tail_action_grows_and_the_folding_is_measured():
    report = load(EVIDENCE)
    rows = report["tail_action"]["rows"]
    assert [row["j"] for row in rows] == [1, 2, 3, 5, 8, 12, 20, 30]
    norms = [float(row["weighted_norm_of_the_image"]) for row in rows]
    assert norms[-1] > norms[0]
    assert norms[-1] > 1.0
    assert report["tail_action"]["grows_with_the_degree"]
    folds = report["folding"]["rows"]
    assert all(row["lowest_degree_present"] == 1 for row in folds)


def test_no_new_bound_and_no_enclosure_is_claimed():
    report = load(EVIDENCE)
    assert report["what_is_not_claimed"]["any_new_bound_on_the_inverse"] is False
    assert report["what_is_not_claimed"]["enclosure_of_alpha"] is False
    assert report["what_is_not_claimed"]["enclosure_of_delta"] is False
    assert "unobtainable in this norm" in report["redirection"]["bound_one_status"]
    assert any("sup-norm" in item for item in report["redirection"]["still_missing"])


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    assert "不可能" in note
    assert "圆盘上的上确界范数" in note
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.feigenbaum-inverse-norm-obstruction.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.feigenbaum-kantorovich-preflight.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "An obstruction in one norm with an obstruction in every norm" in forbidden
    assert "No enclosure of alpha or delta is claimed" in match[0]["counterexample_boundary"]
