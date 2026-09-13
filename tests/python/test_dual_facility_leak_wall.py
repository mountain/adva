"""Replay check for the dual-facility leak-wall round.

The checker uses the standard library only. It is replayed on a copy, because it writes its
evidence beside itself, and the frozen numbers are asserted rather than described.
"""

import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/dual_facility_leak_wall"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0186-dual-facility-leak-wall.md"
CLAIMS = ROOT / "docs/claims.toml"

KEY_POINT = ["hole_F1", "hole_F2", "hole_F3", "opening_near", "segment"]


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def replay(tmp_path):
    copied = tmp_path / "dual_facility_leak_wall"
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
    for key in ("strong_reading", "weaker_reading", "reading_two_ends_sealed",
                "perturbation", "structural", "network"):
        assert fresh[key] == retained[key], key


def test_the_cheapest_containing_plan_is_the_recorded_key_point():
    strong = load(EVIDENCE)["strong_reading"]
    assert strong["plans_examined"] == 1024
    assert strong["containing_plans"] == 81
    assert strong["key_point"] == {"cheapest_cost": "11", "sealed": KEY_POINT}
    assert strong["all_containing_plans_of_minimum_cost"] == [KEY_POINT]


def test_the_key_point_switches_at_the_segment_sealing_cost():
    strong = load(EVIDENCE)["strong_reading"]
    switches = strong["switches"]
    assert len(switches) == 1
    switch = switches[0]
    assert switch["segment_sealing_cost"] == "5"
    assert switch["from"] == KEY_POINT
    assert switch["to"] == ["channel", "hole_F1", "hole_F2", "hole_F3"]
    assert switch["cheapest_cost"] == "12"
    assert len(strong["key_point_family"]) == 12


def test_the_second_reading_differs_by_exactly_one():
    second = load(EVIDENCE)["reading_two_ends_sealed"]
    assert second["key_point"]["cheapest_cost"] == "10"
    assert second["key_point"]["sealed"] == ["hole_F1", "hole_F2", "hole_F3", "segment"]
    assert second["difference_from_reading_one_in_cost"] == "-1"


def test_the_perturbation_leaks_through_the_truncated_end():
    perturbation = load(EVIDENCE)["perturbation"]
    stale = perturbation["stale_plan"]
    assert stale["escapes"] is True
    assert stale["residual_flow_in_the_reading_with_the_ends_open"] == "1"
    assert stale["plan_from_the_reading_with_the_ends_sealed"] == [
        "hole_F1", "hole_F2", "hole_F3", "segment"]
    negative = perturbation["negative_control"]
    assert negative["residual_flow"] == "0"
    assert "not in a number" in negative["finding"]


def test_both_containment_readings_are_reported():
    report = load(EVIDENCE)
    criterion = report["containment_criterion"]
    assert "zero" in criterion["strong_reading"]
    assert "below the demand" in criterion["weaker_reading"]
    rows = report["weaker_reading"]["rows"]
    assert len(rows) == 47
    assert rows[0]["demand"] == "1"
    assert rows[-1]["demand"] == "24"
    assert all(row["cheapest_cost"] is not None for row in rows)


def test_the_structural_claim_is_about_the_segment_endpoints():
    structural = load(EVIDENCE)["structural"]
    assert structural["openings_on_the_segment"] == ["opening_near", "opening_far"]
    assert len(structural["openings_inside_a_facility"]) == 6
    assert "does not formalise" in structural["alexandrov_note"]


def test_the_reading_is_declared_and_the_limits_are_recorded():
    report = load(EVIDENCE)
    assert "reading" in report["the_reading"].lower()
    text = " | ".join(report["what_is_not_claimed"])
    assert "agent's declared reading" in text
    assert "no float" in report["tooling"]["arithmetic"] or "Fraction" in report["tooling"]["arithmetic"]
    assert report["cost"]["subprocesses"] == 0


def test_the_reading_is_visible_in_the_note_and_the_registry():
    note = NOTE.read_text(encoding="utf-8")
    for phrase in ("关键点", "截断口", "对偶", "亚历山大洛夫", "扰动"):
        assert phrase in note, phrase
    claims = tomllib.loads(CLAIMS.read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.dual-facility-leak-wall.v0"]
    assert len(match) == 1
    assert match[0]["dependencies"] == ["adva.bounded-experiment.yang-sds-inequalities.v0"]
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A declared reading of a loose description with what the direction meant" in forbidden
    assert "No native certificate follows" in match[0]["counterexample_boundary"]
