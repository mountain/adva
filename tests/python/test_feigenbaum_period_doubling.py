"""Replay check for the Feigenbaum period-doubling calibration.

The retained evidence is not trusted: the calibration is re-run on a temporary
copy and every non-timing field must match. The digit counts, the exact control
and the two control maps are asserted separately, so a green run states exactly
what it checked.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/feigenbaum_period_doubling"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0176-feigenbaum-period-doubling-calibration.md"
CLAIMS = ROOT / "docs/claims.toml"
DELTA_PREFIX = "4.669201609102990671853203820466201617258185577475768632745651343004134330211314737"
ALPHA_PREFIX = "2.502907875095892822283902873218215786381271376727149977336192056779235463179590206"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    copied = tmp_path / "feigenbaum_period_doubling"
    shutil.copytree(EXPERIMENT, copied)
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


def test_the_cascade_reaches_the_declared_level_and_agrees_with_the_published_digits():
    report = load(EVIDENCE)
    primary = report["primary"]
    assert primary["levels_completed"] == 16
    assert primary["stop_notes"] == []
    assert len(primary["delta_per_level"]) == 15
    assert primary["delta_agreement_characters"] >= 12
    assert primary["alpha_agreement_characters"] >= 12
    for mine, published in ((primary["delta_agreement_string"], DELTA_PREFIX),
                            (primary["alpha_agreement_string"], ALPHA_PREFIX)):
        common = 0
        for a, b in zip(mine, published):
            if a != b:
                break
            common += 1
        assert common == 14
    assert primary["delta_aitken"].startswith("4.6692016091027313")
    assert primary["alpha_aitken"].startswith("2.5029078750959265")


def test_the_exact_level_one_control_is_exact():
    control = load(EVIDENCE)["exact_level_one_control"]
    assert control["polynomial"] == "r^3 - 4 r^2 + 8"
    assert control["polynomial_value_at_closed_form_as_pair_in_Q_sqrt5"] == [0, 0]
    assert control["polynomial_identity_holds_exactly"]
    assert control["gap_below_declared_tolerance"]
    assert control["computed_r_1"].startswith("3.2360679774997896964091736687")


def test_the_universality_control_agrees_and_the_different_class_control_does_not():
    report = load(EVIDENCE)
    universality = report["universality_control"]
    assert universality["levels_completed"] >= 8
    assert universality["agreement_with_the_logistic_delta_characters"] >= 8
    different = report["different_class_control"]
    assert different["literature_value_claimed"] is False
    assert float(different["difference_from_the_logistic_delta"]) > 0.1
    assert different["stop_notes"] == []


def test_the_records_keep_the_limits_visible():
    report = load(EVIDENCE)
    honesty = report["honesty"]
    assert honesty["published_digits_are_a_target_not_a_derivation"]
    assert honesty["aitken_is_an_accelerator_not_part_of_the_definition"]
    assert honesty["algebraic_status_claimed"] is False
    assert honesty["digits_beyond_the_counted_agreement_claimed"] is False
    source = report["published_source"]
    assert source["bytes_retained_here"] is False
    assert source["b_file_sha256"]["A006890"].startswith("eb69c6ed")
    assert source["b_file_sha256"]["A006891"].startswith("5a5256d4")


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    assert "从定义重算" in note
    assert "Aitken" in note
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.feigenbaum-period-doubling.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == []
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A reproduced leading digit count with a proof of the published digits" in forbidden
    assert "An accelerated sequence with the definition of the constant" in forbidden
    boundary = match[0]["counterexample_boundary"]
    assert "Only the digits counted as agreeing are claimed." in boundary
