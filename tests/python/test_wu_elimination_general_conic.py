"""Replay check for the general-conic Pascal round.

Skipped when sympy is absent, since the calibration declares its external library
and reports its own unavailability rather than assuming it.
"""

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/wu_elimination_general_conic"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0182-wu-elimination-general-conic.md"
CLAIMS = ROOT / "docs/claims.toml"

pytest.importorskip("sympy")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    """The calibration writes its evidence beside itself, so it is replayed on a
    copy: running it in place would dirty the repository."""
    import shutil
    copied = tmp_path / "wu_elimination_general_conic"
    shutil.copytree(EXPERIMENT, copied)
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py")],
        cwd=tmp_path, capture_output=True, text=True, timeout=900, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    fresh = load(copied / "evidence.json")
    assert fresh["status"] == "ExternalExactPass"
    assert all(fresh["checks"].values())


def test_the_certificate_is_a_zero_pseudo_remainder():
    certificate = load(EVIDENCE)["certificate"]
    assert certificate["pseudo_remainder_is_zero"]
    assert certificate["hypothesis_terms"] == 720
    assert certificate["conclusion_terms"] == 720
    assert certificate["conclusion_is_not_identically_zero"]
    assert certificate["pseudo_divisibility_not_ideal_membership"]
    assert certificate["non_degeneracy_condition"]["terms"] == 120
    assert certificate["main_variable"] == "y6"


def test_the_controls_are_two_sided():
    controls = load(EVIDENCE)["controls"]
    assert controls["falsified_pairing_is_detected"]
    assert not controls["falsified_pairing_remainder_is_zero"]
    assert controls["hypothesis_is_required"]
    instances = load(EVIDENCE)["random_exact_instances"]
    assert len(instances) == 3
    assert all(instance["is_zero"] for instance in instances)


def test_the_cost_facts_are_measured():
    report = load(EVIDENCE)
    cost = report["certificate"]["cost"]
    assert cost["reduction_seconds"] < 2.0
    assert cost["build_hypothesis_seconds"] < 5.0
    comparison = report["determinant_method_comparison"]
    assert comparison["seconds"]["berkowitz"] < comparison["seconds"]["bareiss"]
    reconnaissance = report["reconnaissance_not_rerun"]
    assert reconnaissance["default_determinant_method"]["cost_seconds"] > 100
    assert reconnaissance["parametrised_general_conic"]["cost_seconds"] > 100


def test_the_limits_are_recorded():
    report = load(EVIDENCE)
    assert report["what_is_not_claimed"]["native_certificate"] is False
    assert report["what_is_not_claimed"]["ideal_membership"] is False
    assert report["what_is_not_claimed"]["proof_without_non_degeneracy_conditions"] is False


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    assert "一般圆锥曲线" in note
    assert "伪可除性" in note
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.wu-elimination-general-conic.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.wu-elimination-plane-incidence.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A zero pseudo-remainder with ideal membership" in forbidden
    assert "No native certificate follows" in match[0]["counterexample_boundary"]
