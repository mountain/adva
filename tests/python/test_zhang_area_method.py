"""Replay check for the area-method readable-proof round.

The checker uses the standard library only, so this replay needs no external library.
It re-runs the checker on a copy (the calibration writes its evidence beside itself),
then asserts the frozen shape of the result, including the negative control that was
not detected and the Unknown outcomes that are not disproofs.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/zhang_area_method"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0184-area-method-readable-proofs.md"
CLAIMS = ROOT / "docs/claims.toml"

PROVED = {
    "medians_concurrent": 27,
    "centroid_ratio_2_1": 22,
    "ceva_rational": 27,
    "menelaus": 43,
    "apollonius_pyth": 5,
    "parallelogram_opposite_sides": 12,
}
BODY_SHA256 = "aeb642b15042c4587e398f007ecf2c444f0104b0940c7bad6ed51e11448531f8"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def body_digest(report):
    """The checker's own documented method for its cost-excluded digest."""
    body = json.dumps({k: v for k, v in report.items() if k != "cost"},
                      indent=2, sort_keys=True)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def replay(tmp_path):
    copied = tmp_path / "zhang_area_method"
    shutil.copytree(EXPERIMENT, copied)
    completed = subprocess.run(
        [sys.executable, str(copied / "calibration.py")],
        cwd=tmp_path, capture_output=True, text=True, timeout=900, check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return load(copied / "evidence.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh = replay(tmp_path)
    assert fresh["status"] == "ExternalExactPass"
    assert all(fresh["checks"].values())
    retained = load(EVIDENCE)
    assert fresh["certificate"] == retained["certificate"]
    assert fresh["lemmas"] == retained["lemmas"]
    assert fresh["broken_variants"] == retained["broken_variants"]


def test_the_cost_excluded_body_digest_is_reproducible():
    report = load(EVIDENCE)
    assert body_digest(report) == BODY_SHA256
    assert report["cost"]["evidence_body_sha256_excluding_cost"] == BODY_SHA256


def test_the_six_readable_proofs_have_the_frozen_number_of_steps():
    report = load(EVIDENCE)
    proofs = {proof["name"]: proof for proof in report["certificate"]["proofs"]}
    assert set(proofs) == set(PROVED)
    for name, steps in PROVED.items():
        assert proofs[name]["outcome"] == "Proved", name
        assert proofs[name]["step_count"] == steps, name
        assert proofs[name]["residue_is_zero"], name
    assert sum(PROVED.values()) == 136


def test_every_step_is_reproduced_and_semantically_verified():
    report = load(EVIDENCE)
    assert report["certificate"]["replay_verdict"]["all_reproduced"]
    assert report["certificate"]["replay_verdict"]["all_semantically_verified"]
    for proof in report["certificate"]["proofs"]:
        replay = proof["replay"]
        assert replay["steps_recorded"] == proof["step_count"]
        assert replay["steps_structurally_reproduced"] == proof["step_count"]
        assert replay["steps_semantically_verified"] == proof["step_count"]
        assert replay["failure_count"] == 0


def test_the_unknown_outcomes_are_reasons_and_not_disproofs():
    report = load(EVIDENCE)
    assert [proof["outcome"] for proof in report["certificate"]["proofs"]] == ["Proved"] * 6
    not_run = {entry["name"]: entry for entry in report["certificate"]["statements_not_run"]}
    assert not_run["pappus"]["outcome"] == "Unknown"
    assert "points at infinity" in not_run["pappus"]["reason"]
    middle = not_run["pyth_middle_argument"]
    assert middle["outcome"] == "Unknown"
    assert middle["independent_instances"]["zero_instances"] == 12
    assert middle["independent_instances"]["agrees"]
    assert "disproved" not in json.dumps(report["certificate"]["outcomes"]).lower()
    assert set(report["certificate"]["outcomes"]) == {"Proved", "Unknown"}


def test_the_falsified_companions_are_refuted_on_the_recorded_witness():
    report = load(EVIDENCE)
    companions = {entry["name"]: entry for entry in report["falsified_companions"]}
    assert set(companions) == {"centroid_ratio_3_1_falsified",
                              "ceva_rational_wrong_parameter_falsified"}
    for name, entry in companions.items():
        assert entry["outcome"] == "Unknown", name
        refutation = entry["refutation_on_an_explicit_instance"]
        assert refutation["refuted"]
        assert refutation["non_degeneracy_conditions_hold_at_the_witness"]
        assert "not a kernel outcome" in refutation["meaning"]
    assert companions["centroid_ratio_3_1_falsified"]["residue_constant"]["value"] == "-7/3"


def test_the_broken_lemmas_are_caught_and_the_negative_control_is_retained():
    report = load(EVIDENCE)
    broken = report["broken_variants"]
    detected = [variant["mode"] for variant in broken["lemma_variants"] if variant["detected"]]
    assert sorted(detected) == ["lemma_sign", "midpoint_ratio"]
    for variant in broken["lemma_variants"]:
        assert variant["lemma_symbolic_verification_failed"]
        assert not variant["goal_closed"]
        assert variant["replay_failure_count"] > 0
    order = broken["order_variant"]
    assert order["detected"] is False
    assert order["goal_closed"] is True
    assert "does NOT detect" in order["note"]


def test_the_lemmas_are_verified_symbolically_and_on_instances():
    report = load(EVIDENCE)
    assert len(report["lemmas"]) == 14
    for name, lemma in report["lemmas"].items():
        assert lemma["symbolic_ok"], name
        assert lemma["random_instances"]["instances_checked"] == 40, name
        assert lemma["random_instances"]["all_match"], name


def test_no_float_and_no_external_library_is_used_in_a_certified_step():
    report = load(EVIDENCE)
    assert report["cost"]["floats_in_certified_steps"] == 0
    assert report["cost"]["subprocesses"] == 0
    assert report["tooling"]["sympy_present"] is False
    assert report["tooling"]["sympy_used_for_certified_steps"] is False
    assert report["tooling"]["external_oracle_not_native_authority"] is True


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    for phrase in ("消点法", "面积法", "可读", "Pappus", "Unknown"):
        assert phrase in note, phrase
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.zhang-area-method.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == [
        "adva.bounded-experiment.wu-elimination-plane-incidence.v0",
        "adva.bounded-experiment.zhang-finite-example.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A goal the kernel did not close with a false statement" in forbidden
    assert "No native certificate follows" in match[0]["counterexample_boundary"]
