"""Replay check for the rigorous threshold enclosures.

The retained evidence is not trusted: the calibration is re-run on a temporary
copy and every non-timing field must match. The certification, the two measured
barriers and the explicit non-claims are asserted separately.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/feigenbaum_rigorous_enclosures"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0178-rigorous-enclosures-and-two-barriers.md"
CLAIMS = ROOT / "docs/claims.toml"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    copied = tmp_path / "feigenbaum_rigorous_enclosures"
    shutil.copytree(EXPERIMENT, copied)
    shutil.copytree(EXPERIMENT.parent / "feigenbaum_period_doubling",
                    tmp_path / "feigenbaum_period_doubling")  # the sibling sits beside it
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py")],
        cwd=copied, capture_output=True, text=True, timeout=600, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    fresh = load(copied / "evidence.json")
    retained = load(EVIDENCE)
    fresh.pop("cost", None)
    retained.pop("cost", None)
    assert fresh == retained
    assert retained["status"] == "ExternalExactPass"
    assert all(retained["checks"].values())


def test_the_certified_levels_and_their_signs():
    report = load(EVIDENCE)
    levels = {row["level"]: row for row in report["levels"]}
    for level in (1, 2, 3, 4, 5):
        assert levels[level]["certified"], level
        assert levels[level]["endpoint_signs"][0] * levels[level]["endpoint_signs"][1] == -1
    for level in (6, 7, 8):
        assert levels[level]["certified"] is False
        assert "width cap" in levels[level]["reason"]
    assert report["certification_summary"]["levels_certified"] == [1, 2, 3, 4, 5]
    widths = [float(levels[level]["width"]) for level in (1, 2, 3, 4)]
    assert widths[0] < 1e-17
    assert widths == sorted(widths)


def test_the_level_one_bracket_contains_the_closed_form():
    report = load(EVIDENCE)
    assert report["levels"][0]["contains_the_exact_closed_form_1_plus_sqrt5"] is True


def test_the_precision_control_changes_the_count():
    report = load(EVIDENCE)
    coarse = report["control_coarser_grid"]
    assert coarse["grid"] == "1e-6"
    assert coarse["levels_certified"] == [1, 2]
    assert len(coarse["levels_certified"]) < len(report["certification_summary"]["levels_certified"])


def test_the_two_barriers_are_measured():
    report = load(EVIDENCE)
    amplification = report["width_amplification_per_iteration"]["mean_factor"]
    assert 3.0 < float(amplification) < 4.0
    bits = [row["denominator_bits"] for row in report["exact_rational_route"]["denominator_growth"]]
    assert bits[0] < bits[-1]
    assert bits[-1] > 20000


def test_ratio_enclosures_are_reported_but_no_constant_enclosure_is_claimed():
    report = load(EVIDENCE)
    ratios = {row["level"]: row for row in report["delta_ratio_enclosures"]}
    assert float(ratios[3]["width"]) < 1e-12
    assert float(ratios[4]["width"]) < 1e-8
    not_claimed = report["what_is_not_claimed"]
    assert not_claimed["enclosure_of_delta"] is False
    assert not_claimed["enclosure_of_alpha"] is False
    assert "Newton-Kantorovich" in not_claimed["next_step"]


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    assert "被证明的包围" in note
    assert "没有 `δ` 或 `α` 的包围" in note
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.feigenbaum-rigorous-enclosures.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.feigenbaum-fixed-point.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A certified bracket for a threshold with an enclosure of the constant" in forbidden
    assert "No enclosure of the Feigenbaum constants is claimed" in match[0]["counterexample_boundary"]
