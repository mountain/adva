"""Replay check for the Kantorovich preflight.

The retained evidence is not trusted: the calibration is re-run on a temporary
copy and every non-timing field must match. What is exact, what is only
truncated, and what is missing are asserted separately.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/feigenbaum_kantorovich_preflight"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0179-kantorovich-preflight.md"
CLAIMS = ROOT / "docs/claims.toml"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    copied = tmp_path / "feigenbaum_kantorovich_preflight"
    shutil.copytree(EXPERIMENT, copied)
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


def test_the_defect_is_exact_and_small():
    report = load(EVIDENCE)
    defect = report["defect"]
    assert float(defect["weighted_norm_eta"]) < 1e-20
    assert defect["eta_exact_numerator_bits"] > 10000
    assert defect["highest_nonzero_degree"] == 60
    assert report["exact_candidate"]["degree"] == 10
    assert report["precision"]["binary_floating_point_in_reported_bounds"] is False
    assert report["precision"]["acceleration_applied"] is False


def test_the_hypothesis_holds_and_its_control_fails():
    report = load(EVIDENCE)
    hypothesis = report["disk_mapping_hypothesis"]
    assert hypothesis["holds"]
    assert float(hypothesis["weighted_norm_of_x0"]) < 1.2
    controls = report["controls"]
    assert controls["perturbed_candidate_has_larger_defect"]["larger_than_the_candidate"]
    assert controls["scaled_candidate_fails_the_disk_mapping"]["fails"]
    assert report["coefficient_decay"]["ratio_test_locates_the_radius"] is False


def test_the_truncated_inverse_is_verified_but_not_the_full_one():
    report = load(EVIDENCE)
    inverse = report["truncated_inverse"]
    assert inverse["verified"]
    assert float(inverse["residual_infinity_norm"]) == 0.0
    assert "not the weighted norm of the space" in inverse["norm_mismatch"]


def test_the_preflight_obstruction_lists_three_missing_bounds():
    report = load(EVIDENCE)
    obstruction = report["preflight_obstruction"]
    assert len(obstruction["what_is_missing"]) == 3
    assert "not launched" in obstruction["conclusion"]
    not_claimed = report["what_is_not_claimed"]
    assert not_claimed["enclosure_of_alpha"] is False
    assert not_claimed["enclosure_of_delta"] is False
    assert not_claimed["existence_or_uniqueness_of_the_fixed_point"] is False
    assert not_claimed["the_truncated_inverse_bound_is_not_the_full_inverse_bound"] is True


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    assert "Kantorovich 预检" in note
    assert "不启动" in note
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.feigenbaum-kantorovich-preflight.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.feigenbaum-rigorous-enclosures.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A verified truncated inverse with the inverse of the full operator" in forbidden
    assert "No enclosure of alpha or delta is claimed" in match[0]["counterexample_boundary"]
