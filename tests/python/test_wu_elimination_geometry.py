"""Replay check for Wu's elimination round.

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
EXPERIMENT = ROOT / "experiments/wu_elimination_geometry"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0181-wu-elimination-on-plane-incidence.md"
CLAIMS = ROOT / "docs/claims.toml"

pytest.importorskip("sympy")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    """The calibration writes its evidence beside itself, so it is replayed on a
    copy: running it in place would dirty the repository."""
    import shutil
    copied = tmp_path / "wu_elimination_geometry"
    shutil.copytree(EXPERIMENT, copied)
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py")],
        cwd=tmp_path, capture_output=True, text=True, timeout=900, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    fresh = load(copied / "evidence.json")
    retained = load(EVIDENCE)
    assert fresh["status"] == retained["status"] == "ExternalExactPass"
    assert all(retained["checks"].values())


def test_true_statements_reduce_to_zero_and_falsified_ones_do_not():
    results = {row["statement"]: row for row in load(EVIDENCE)["results"]}
    for name in ("ceva", "pappus", "pascal_on_a_parabola"):
        assert results[name]["remainder_is_zero"], name
        assert results[name]["groebner_membership"], name
        assert results[name]["methods_agree"], name
    for name in ("ceva_falsified", "pappus_falsified", "pascal_on_a_parabola_falsified"):
        assert not results[name]["remainder_is_zero"], name
        assert not results[name]["groebner_membership"], name
    assert results["pascal_on_a_parabola"]["conclusion_terms"] == 720
    assert len(results["pascal_on_a_parabola"]["chain"]) == 6
    assert results["pappus"]["conclusion_terms"] == 0


def test_non_degeneracy_conditions_and_instances_are_recorded():
    results = {row["statement"]: row for row in load(EVIDENCE)["results"]}
    pascal = results["pascal_on_a_parabola"]
    assert pascal["chain_initials_non_degeneracy_conditions"] == ["-1"] * 6
    assert all(instance["is_zero"] for instance in pascal["random_instances"])
    assert all(instance["is_zero"] for instance in results["pappus"]["random_instances"])


def test_the_limits_are_recorded():
    report = load(EVIDENCE)
    limits = report["wu_method_reach_and_limits"]
    assert "not done here" in limits["pascal_for_a_general_conic"]
    assert any("functional equation" in item for item in limits["relation_to_the_repository"])
    assert any("growth obligation stays Open" in item for item in limits["relation_to_the_repository"])
    assert report["what_is_not_claimed"]["native_certificate"] is False
    assert report["what_is_not_claimed"]["general_conic_pascal"] is False


def test_the_tooling_is_declared():
    tooling = load(EVIDENCE)["tooling"]
    assert tooling["polynomial_library"] == "sympy"
    assert tooling["available"]
    assert tooling["external_oracle_not_native_authority"]


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    assert "吴消元法" in note
    assert "KLM" in note.upper().replace("KLMM", "KLM")
    assert "不是原生证书" in note
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.wu-elimination-plane-incidence.v0"]
    assert len(match) == 1
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "An external symbolic computation with a native certificate" in forbidden
    assert "No native certificate follows" in match[0]["counterexample_boundary"]
