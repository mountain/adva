"""Replay check for the finite-example verification round.

The calibration declares its own tooling and reports the absence of the external
library rather than assuming it, so the replay accepts a run either with or without
sympy: the retained evidence was produced with sympy 1.14.0 present, and the checks
are asserted in both cases.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/zhang_finite_example"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0183-zhang-finite-example-verification.md"
CLAIMS = ROOT / "docs/claims.toml"

CERTIFIED = ["pappus", "parabola_pascal", "hyperbola_pascal", "circle_pascal", "ceva_chart"]
REFUSED = ["wrong_pairing", "ceva_conclusion"]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def replay(tmp_path, *arguments):
    """The calibration writes its evidence beside itself, so it is replayed on a copy:
    running it in place would dirty the repository."""
    copied = tmp_path / "zhang_finite_example"
    shutil.copytree(EXPERIMENT, copied)
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py"), *arguments],
        cwd=tmp_path, capture_output=True, text=True, timeout=900, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return load(copied / "evidence.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh = replay(tmp_path)
    assert fresh["status"].startswith("ExternalExactPass")
    assert all(fresh["checks"].values())
    retained = load(EVIDENCE)
    for key in ("certificate", "sharpness", "ceva_degeneracy", "controls", "criterion"):
        assert fresh[key] == retained[key], key


def test_the_certificate_path_does_not_call_the_external_library(tmp_path):
    fresh = replay(tmp_path, "--no-external")
    assert all(fresh["checks"].values())
    assert fresh["certificate_path_external_library_calls"] == 0
    assert fresh["tooling"]["external_library"] == "absent"
    assert all(certificate["symbolic_confirmation"] is None
               for certificate in fresh["certificate"].values())


def test_the_five_identities_are_certified_by_the_grid():
    report = load(EVIDENCE)
    assert report["certificate"]["pappus"]["degree_bound"] == [2] * 6
    assert report["certificate"]["pappus"]["grid_size"] == 729
    for name in CERTIFIED:
        certificate = report["certificate"][name]
        assert certificate["certified_by_the_criterion"], name
        assert certificate["integer_grid"]["nonzero_cells"] == 0
        assert certificate["rational_grid"]["nonzero_cells"] == 0
    for name in ("parabola_pascal", "hyperbola_pascal", "circle_pascal"):
        assert report["certificate"][name]["degree_bound"] == [4] * 6
        assert report["certificate"][name]["grid_size"] == 15625
    assert report["certificate"]["ceva_chart"]["grid_size"] == 9


def test_the_two_non_identities_are_refused_with_witnesses():
    report = load(EVIDENCE)
    for name in REFUSED:
        certificate = report["certificate"][name]
        assert not certificate["certified_by_the_criterion"], name
        assert certificate["integer_grid"]["nonzero_cells"] > 0
        assert certificate["rational_grid"]["nonzero_cells"] > 0
        witness = certificate["integer_grid"]["witnesses"][0]
        assert witness["value"] != "0"
    assert report["certificate"]["wrong_pairing"]["integer_grid"]["witnesses"][0]["value"] == "16"
    assert report["certificate"]["ceva_conclusion"]["grid_size"] == 8
    assert report["controls"]["falsified_witnesses"]["wrong_pairing"][0]["value"] == "16"


def test_the_numeric_pass_encloses_zero_and_excludes_it_where_it_must():
    report = load(EVIDENCE)
    for name in CERTIFIED:
        intervals = report["certificate"][name]["interval_pass"]
        assert intervals["cells_containing_zero"] == intervals["cells_sampled"]
    for name in REFUSED:
        intervals = report["certificate"][name]["interval_pass"]
        assert intervals["cells_excluding_zero"] > 0


def test_the_grid_size_cannot_be_reduced():
    report = load(EVIDENCE)
    for witnesses in report["sharpness"].values():
        for witness in witnesses:
            assert witness["short_witness_nonzero"]
            assert witness["short_witness_degree"] <= witness["declared_bound"]
            assert witness["short_witness_vanishes_on_short_grid"]
            assert witness["over_bound_witness_degree"] == witness["declared_bound"] + 1
            assert witness["over_bound_witness_vanishes_on_full_grid"]
    criterion = report["criterion"]["checked_on_random_polynomials"]
    assert criterion["trials"] == 60


def test_the_certificate_does_not_require_nondegenerate_samples():
    report = load(EVIDENCE)
    for name in CERTIFIED:
        integer = report["certificate"][name]["integer_grid_degenerate_cells"]
        assert integer["cells_with_a_repeated_parameter"] <= integer["cells"]
    assert report["certificate"]["pappus"]["integer_grid_degenerate_cells"] == {
        "cells": 729, "cells_with_a_repeated_parameter": 729}
    assert report["certificate"]["hyperbola_pascal"]["rational_grid_degenerate_cells"][
        "cells_with_a_repeated_parameter"] == 0
    assert report["grid_filter_control"]["an_antipodal_circle_pair_is_refused"]


def test_the_chart_denominator_is_the_wu_initial():
    chart = load(EVIDENCE)["ceva_degeneracy"]
    assert chart["chart_denominator_is_the_coefficient_of_f"]
    assert chart["coefficient_of_f"] == "t + e - 2te"
    assert chart["coefficient_of_t"] == "f + e - 2ef"
    assert chart["same_polynomial_after_renaming"]


def test_the_symbolic_cross_check_is_declared_as_a_cross_check_only():
    report = load(EVIDENCE)
    for name in CERTIFIED:
        confirmation = report["certificate"][name]["symbolic_confirmation"]
        assert confirmation is not None and confirmation["expansion_is_zero"]
    for name in REFUSED:
        confirmation = report["certificate"][name]["symbolic_confirmation"]
        assert confirmation is not None and not confirmation["expansion_is_zero"]
    assert report["certificate"]["wrong_pairing"]["symbolic_confirmation"]["terms"] == 1009
    assert report["tooling"]["external_library_used_for"].startswith(
        "an exact symbolic expansion of the same formula")


def test_the_limits_are_recorded():
    report = load(EVIDENCE)
    assert report["comparison_with_wu"]["sibling_evidence_read_not_re_run"]
    assert all(status["status"] == "ExternalExactPass"
               for status in report["comparison_with_wu"]["sibling_evidence_read_not_re_run"].values())
    text = " | ".join(report["what_is_not_claimed"])
    assert "not a native Adva certificate" in text
    assert "not the geometry of a degenerate figure" in text


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    for phrase in ("例证法", "消点法", "张杨定理", "数值并行法", "弱非退化条件"):
        assert phrase in note, phrase
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.zhang-finite-example.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == [
        "adva.bounded-experiment.wu-elimination-plane-incidence.v0",
        "adva.bounded-experiment.wu-elimination-general-conic.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A grid certificate with a native Adva certificate" in forbidden
    assert "No native certificate follows" in match[0]["counterexample_boundary"]
