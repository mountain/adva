"""The optimal shares: leveling for the sides, the price of a level for the reserve.

Research 0193 computes the half of the direction's open optimality question that can be computed.
The tempting repairs here are the quiet ones: assert that the optimal side depths are equal
everywhere when they are not, let the exhaustive search run to a ceiling the reserve can push to
the horizon, or report a gap in the remaining mass without saying which model produced it.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/traversal_allocation_optimal"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0193-the-optimal-shares-and-the-price-of-a-level.md"
CLAIMS = ROOT / "docs/claims.toml"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def strip_host_quantities(evidence):
    copy = json.loads(json.dumps(evidence))
    excluded = copy["counts"].pop("wall_seconds_before_serialization")
    assert isinstance(excluded, float)
    return copy


def replay(tmp_path):
    completed = subprocess.run([sys.executable, str(EXPERIMENT / "calibration.py"),
                                str(tmp_path / "fresh.json")],
                               cwd=ROOT, capture_output=True, text=True, timeout=900,
                               check=False)
    assert completed.returncode == 0, completed.stderr
    return load(tmp_path / "fresh.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh, retained = replay(tmp_path), load(EVIDENCE)
    assert strip_host_quantities(fresh) == strip_host_quantities(retained)


def test_the_layer_costs_telescope_to_a_square():
    arithmetic = load(EVIDENCE)["arithmetic"]
    assert arithmetic["cost_to_depth_d"] == "(d+1)^2 steps"
    assert arithmetic["layer_n_cost"] == "2n+1 steps"


def test_the_leveling_rule_matches_the_exhaustive_search_on_the_declared_grid():
    rows = load(EVIDENCE)["inside_the_pool"]
    assert all(row["the_greedy_leveling_matches_the_exhaustive_best"] for row in rows)
    spreads = sorted({row["depth_spread"] for row in rows})
    assert spreads == [0, 1], spreads
    # equal depths are optimal only where the pool affords the same depth everywhere
    equal = [row for row in rows if row["depth_spread"] == 0]
    assert equal, "the equal case must appear"
    assert any(row["steps_left_unspent"] > 0 for row in rows), "whole layers only"


def test_the_direction_reserve_is_not_optimal_in_most_declared_cases():
    scans = load(EVIDENCE)["reserve_scan"]
    assert len(scans) == 15
    optimal = [row for row in scans if row["the_direction_reserve_is_optimal"]]
    assert len(optimal) == 1, "exactly one declared case should make one per cent optimal"
    assert optimal[0]["budget"] == 10000
    assert optimal[0]["join_cost"] == "constant one step"
    assert optimal[0]["optimal_reserve_fraction"] == "1/100"
    assert optimal[0]["the_direction_reserve_is_on_a_plateau"] is True
    assert len([row for row in scans if not row["the_direction_reserve_is_on_a_plateau"]]) == 14


def test_the_recorded_optima_are_the_ones_the_note_states():
    rows = {row["join_cost"]: row for row in load(EVIDENCE)["reserve_scan"]
            if row["budget"] == 1000}
    assert rows["constant one step"]["optimal_reserve_fraction"] == "1/50"
    assert rows["constant ten steps"]["optimal_reserve_fraction"] == "4/25"
    assert rows["linear one per level"]["optimal_reserve_fraction"] == "7/50"
    assert rows["linear ten plus one per level"]["optimal_reserve_fraction"] == "27/100"
    assert rows["doubling per level"]["optimal_reserve_fraction"] == "13/50"
    # the starkest cell: one per cent buys no level at all and half the space stays unresolved
    stark = rows["linear ten plus one per level"]
    assert stark["direction_levels_bought"] == 0
    assert stark["gap_in_remaining_mass"] == "98299/196608"


def test_the_scan_reaches_both_answers_and_the_controls_refuse():
    evidence = load(EVIDENCE)
    assert any(row["the_direction_reserve_is_on_a_plateau"] for row in evidence["reserve_scan"])
    assert any(not row["the_direction_reserve_is_on_a_plateau"] for row in evidence["reserve_scan"])
    refusals = evidence["refusals"]
    assert len(refusals) == 3
    assert all(row["refused"] is True and row["message"] for row in refusals)


def test_the_recorded_error_about_equal_depths_stays_on_the_record():
    findings = " ".join(load(EVIDENCE)["findings"])
    assert "did not hold" in findings or "does not" in findings
    non_claims = " ".join(load(EVIDENCE)["non_claims"])
    assert "measured regularity" in non_claims
    text = NOTE.read_text(encoding="utf-8")
    assert "预期是错的" in text
    assert "断言预算被击穿" in text


def test_the_note_is_indexed_and_the_claim_exists():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "traversal-allocation-optimal" in CLAIMS.read_text(encoding="utf-8")
