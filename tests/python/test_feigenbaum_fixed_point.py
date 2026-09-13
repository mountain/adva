"""Replay check for the Feigenbaum fixed-point calibration.

The retained evidence is not trusted: the calibration is re-run on a temporary
copy and every non-timing field must match. The agreement counts, the internal
relation and the control operator are asserted separately, so a green run states
exactly what it checked.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/feigenbaum_fixed_point"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0177-feigenbaum-fixed-point-collocation.md"
CLAIMS = ROOT / "docs/claims.toml"
DELTA_PREFIX = "4.669201609102990671853203820466201617258185577475768632745651343004134330211314737"
ALPHA_PREFIX = "2.502907875095892822283902873218215786381271376727149977336192056779235463179590206"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    copied = tmp_path / "feigenbaum_fixed_point"
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


def test_the_agreement_grows_with_the_truncation_and_reaches_thirty_digits():
    report = load(EVIDENCE)
    table = report["table"]
    assert [row["degree"] for row in table] == [8, 12, 16, 20, 24, 28, 32]
    residuals = [float(row["truncation_residual_beyond_the_degree"]) for row in table]
    assert all(residuals[i + 1] < residuals[i] for i in range(len(residuals) - 1))
    counts = [row["delta_agreement_characters"] for row in table]
    assert all(counts[i + 1] >= counts[i] for i in range(len(counts) - 1))
    last = table[-1]
    assert last["delta_agreement_characters"] >= 25
    assert last["alpha_agreement_characters"] >= 25
    assert last["delta"] == "4.66920160910299067185320382046381037"
    assert last["alpha"] == "2.50290787509589282228390287321795506"
    for mine, published in ((last["delta_agreement_string"], DELTA_PREFIX),
                            (last["alpha_agreement_string"], ALPHA_PREFIX)):
        common = 0
        for a, b in zip(mine, published):
            if a != b:
                break
            common += 1
        assert common == 31


def test_the_internal_relations_hold():
    report = load(EVIDENCE)
    last = report["table"][-1]
    assert abs(float(last["g_1_times_alpha"]) + 1.0) < 1e-20
    assert last["reciprocal_agreement_characters"] >= 30
    assert last["coefficients_a1_a2_a3"][0].startswith("-1.52763299703630")


def test_the_two_recorded_targets_are_checked_against_each_other():
    report = load(EVIDENCE)
    consistency = report["published_target_consistency"]
    assert consistency["agreement_characters"] >= 30
    assert consistency["agreement_characters"] == 47
    assert consistency["recorded_reciprocal_prefix"].startswith("0.39953528052313448985758046")


def test_the_control_operator_is_kept_and_differs():
    report = load(EVIDENCE)
    control = report["unnormalised_operator_control"]
    assert control["differs_from_delta"]
    assert control["dominant_eigenvalue"].startswith("6.2645478312170374")
    assert "does not preserve" in control["why"]


def test_no_acceleration_is_claimed_and_no_bound_is_claimed():
    report = load(EVIDENCE)
    honesty = report["honesty"]
    assert honesty["no_acceleration_used"]
    assert honesty["verified_error_bound_claimed"] is False
    assert honesty["truncation_residual_is_a_numerical_indicator"]
    assert honesty["published_digits_are_a_target_not_a_derivation"]
    assert honesty["algebraic_status_claimed"] is False
    assert report["precision"]["acceleration_applied"] is False
    assert report["precision"]["binary_floating_point_in_reported_values"] is False
    assert report["published_source"]["bytes_retained_here"] is False


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    assert "解不动点" in note
    assert "不是严格计算" in note
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.feigenbaum-fixed-point.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.feigenbaum-period-doubling.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A numerical truncation residual with a proved error bound" in forbidden
    assert "Thirty agreeing decimal places with a proof of the published digits" in forbidden
    assert "This is not a rigorous computation" in match[0]["counterexample_boundary"]
