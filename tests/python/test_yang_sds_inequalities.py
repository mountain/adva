"""Replay check for the difference-substitution inequality round.

The checker uses the standard library only, so no import guard is needed. It is
replayed on a copy, because it writes its evidence beside itself.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/yang_sds_inequalities"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0185-yang-difference-substitution-inequalities.md"
CLAIMS = ROOT / "docs/claims.toml"

CERTIFIED = {"schur_t1": 6, "amgm3": 6, "nesbitt": 6, "amgm4": 24,
             "weitzenbock": 6, "motzkin": 6}
UNKNOWN = ["false_companion_power_mean", "marginal_wall_discriminant"]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def replay(tmp_path):
    copied = tmp_path / "yang_sds_inequalities"
    shutil.copytree(EXPERIMENT, copied)
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py")],
        cwd=tmp_path, capture_output=True, text=True, timeout=600, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return load(copied / "evidence.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh = replay(tmp_path)
    assert fresh["status"] == "ExternalExactPass"
    assert all(fresh["checks"].values())
    retained = load(EVIDENCE)
    for key in ("statements", "outcomes", "ordered_certificates",
                "sum_of_squares_identity", "naive_iteration"):
        assert fresh[key] == retained[key], key


def test_the_six_certificates_and_their_ordering_counts():
    report = load(EVIDENCE)
    assert report["outcomes"] == {
        "schur_t1": "Certified", "amgm3": "Certified", "nesbitt": "Certified",
        "amgm4": "Certified", "weitzenbock": "Certified", "motzkin": "Certified",
        "false_companion_power_mean": "Unknown", "marginal_wall_discriminant": "Unknown"}
    for name, orderings in CERTIFIED.items():
        certificate = report["statements"][name]["certificate"]
        assert certificate["outcome"] == "Certified", name
        assert certificate["orderings"] == orderings, name
        assert certificate["orderings_certifying"] == orderings, name


def test_a_failure_to_certify_is_not_a_counterexample():
    report = load(EVIDENCE)
    for name in UNKNOWN:
        statement = report["statements"][name]
        assert statement["outcome"] == "Unknown", name
        assert statement["certificate"]["orderings_certifying"] == 0, name
        assert "first_failing_order" in statement["certificate"]
    wall = report["statements"]["marginal_wall_discriminant"]
    assert wall["expected_true"] is True
    assert wall["soundness_audit"]["negative_points"] == 0
    assert wall["witness_if_any"] is None


def test_the_false_companion_is_refuted_on_an_explicit_point():
    statement = load(EVIDENCE)["statements"]["false_companion_power_mean"]
    assert statement["expected_true"] is False
    witness = statement["witness"]
    assert witness is not None
    assert witness["value"].startswith("-")
    assert len(witness["point"]) == 3


def test_every_statement_declared_true_survives_the_witness_search():
    report = load(EVIDENCE)
    for name, statement in report["statements"].items():
        if statement["expected_true"]:
            assert statement["witness_if_any"] is None, name
    assert report["checks"]["every_statement_declared_true_survives_the_witness_search"]


def test_the_ordered_and_sum_of_squares_certificates_are_separate_objects():
    report = load(EVIDENCE)
    ordered = report["ordered_certificates"]["schur_t1"]
    assert ordered["identity_verified_exactly"]
    assert ordered["identity"] == "sum_cyc x(x-y)(x-z) = (x-y)^2 (x+y-z) + z(x-z)(y-z)"
    assert ordered["soundness_audit"]["negative_points"] == 0
    sos = report["sum_of_squares_identity"]
    assert sos["identity_verified_exactly"]
    assert sos["sos_soundness_audit"]["negative_points"] == 0
    assert report["statements"]["marginal_wall_discriminant"]["outcome"] == "Unknown"


def test_naive_iteration_is_measured_and_not_assumed():
    iteration = load(EVIDENCE)["naive_iteration"]
    assert iteration["counterexample"]["point_is_in_the_ordered_cone"]
    assert not iteration["counterexample"]["differences_are_ordered"]
    assert iteration["counterexample"]["differences"] == ["0", "2", "1"]


def test_the_two_errors_of_this_round_are_retained():
    report = load(EVIDENCE)
    surprises = report["surprises_kept"]
    schur = surprises["the_schur_statement_was_mis_written_first"]
    assert "-2" in schur["measured_first"]
    assert "random orthant points essentially never have equal coordinates" in schur["how_it_was_found"]
    assert report["statements"]["schur_t1"]["statement_error"]["what_was_written"].startswith(
        "x^3+y^3+z^3+xyz")
    assert surprises["motzkin_is_certified"]["measured"].startswith("Certified")
    assert surprises["the_repository_inequality_is_not_certified_by_this_route"]["measured"].startswith("Unknown")


def test_motzkin_is_certified_and_the_classical_fact_is_only_cited():
    report = load(EVIDENCE)
    motzkin = report["statements"]["motzkin"]
    assert motzkin["outcome"] == "Certified"
    assert motzkin["certificate"]["orderings_certifying"] == 6
    text = " | ".join(report["what_is_not_claimed"])
    assert "cited and not verified" in text


def test_no_external_library_and_no_float_is_used():
    report = load(EVIDENCE)
    assert report["tooling"]["external_library"] == "none"
    assert "Fraction" in report["tooling"]["arithmetic"]
    assert report["cost"]["subprocesses"] == 0
    assert report["certificate_method"]["published_method_not_read"].startswith(
        "the reference chapter")


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    for phrase in ("杨路", "BOTTEMA", "cell-decomposition", "差分代换", "Unknown"):
        assert phrase in note, phrase
    assert "百度安全验证" in note
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.yang-sds-inequalities.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == [
        "adva.bounded-experiment.wu-elimination-plane-incidence.v0",
        "adva.bounded-experiment.zhang-finite-example.v0",
        "adva.bounded-experiment.zhang-area-method.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A failure to certify with a counterexample" in forbidden
    assert "No native certificate follows" in match[0]["counterexample_boundary"]
