"""The traversal allocation and its reserve: closure, starvation, and rollback.

Research 0192 tests the direction's protocol only where it can be tested exactly. The tempting
repairs here are the quiet ones: trust a closure test that passes by rounding, let per-part
rounding eat the reserve, treat a failed join as free when the reserve came out of a side, or
identify a budget share with a probability mass.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/traversal_allocation_and_reserve"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0192-the-traversal-allocation-and-its-reserve.md"
CLAIMS = ROOT / "docs/claims.toml"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def strip_host_quantities(evidence):
    """Drop the single declared host field: the elapsed wall time, and nothing else."""
    copy = json.loads(json.dumps(evidence))
    excluded = copy["counts"].pop("wall_seconds_before_serialization")
    assert isinstance(excluded, float)
    return copy


def replay(tmp_path):
    completed = subprocess.run([sys.executable, str(EXPERIMENT / "calibration.py"),
                                str(tmp_path / "fresh.json")],
                               cwd=ROOT, capture_output=True, text=True, timeout=300,
                               check=False)
    assert completed.returncode == 0, completed.stderr
    return load(tmp_path / "fresh.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh, retained = replay(tmp_path), load(EVIDENCE)
    assert strip_host_quantities(fresh) == strip_host_quantities(retained)


def test_the_allocation_closes_in_hundredths_and_the_naive_test_hides_the_defect():
    allocation = load(EVIDENCE)["allocation"]
    assert allocation["shares"] == ["33/100"] * 3
    assert allocation["reserve"] == "1/100"
    assert allocation["closes_in_hundredths"] is True
    # the closure test that passes is the finding: it passes by rounding
    assert allocation["the_naive_binary64_closure_test_passes"] is True
    assert allocation["the_binary64_parts_are_exact"] is False
    binary64 = allocation["binary64"]
    assert binary64["naive_test_passes"] is True
    assert binary64["exact_defect_of_the_hundredths"] != "0"
    assert binary64["exact_defect_of_the_hundredths"].startswith("-"), "over-allocation expected"
    assert binary64["naive_test_on_three_thirds"] == "1.0"


def test_rounding_each_part_starves_the_reserve_and_the_exact_rule_never_does():
    rows = {row["budget"]: row for row in load(EVIDENCE)["steps"]}
    assert rows[100]["exact_reserve"] == "1" and rows[1000]["exact_reserve"] == "10"
    assert rows[10]["exact_reserve"] == "1" and rows[10]["rounded_reserve"] == "0"
    assert rows[10]["the_rounded_reserve_falls_below_the_declared_percent"] is True
    assert rows[3]["the_rounded_reserve_falls_below_the_declared_percent"] is True
    assert rows[100]["the_rounded_reserve_falls_below_the_declared_percent"] is False
    for row in rows.values():
        assert row["exact_reserve_is_at_least_the_declared_percent"] is True


def test_the_reserve_pays_for_joins_so_its_value_is_a_question_about_join_cost():
    rows = {row["cost_model"]: row for row in load(EVIDENCE)["reserve_critical_level"]}
    assert rows["constant one step"]["unbounded"] is True
    assert rows["linear, one step per level"]["largest_level_the_reserve_pays"] == 9
    assert rows["linear, ten plus one per level"]["largest_level_the_reserve_pays"] == 0
    assert rows["doubling per level"]["largest_level_the_reserve_pays"] == 3


def test_the_traversal_stops_where_the_reserve_says_and_the_chain_reproduces():
    traversal = load(EVIDENCE)["traversal"]
    joins = [(row["level"], row.get("joined")) for row in traversal["chain"]]
    assert joins == [(0, None), (1, True), (2, True), (3, True), (4, False),
                     (5, False), (6, False), (7, False)], joins
    assert traversal["successes"] == 3 and traversal["failures"] == 4
    assert traversal["successes"] == [
        row for row in load(EVIDENCE)["reserve_critical_level"]
        if row["cost_model"] == "doubling per level"][0]["largest_level_the_reserve_pays"]


def test_a_failed_join_leaves_the_head_and_the_level_unchanged():
    chain = load(EVIDENCE)["traversal"]["chain"]
    for before, after in zip(chain, chain[1:]):
        if after.get("joined") is False:
            assert after["anchor"] == before["anchor"]
            assert after["resolved"] == before["resolved"]


def test_rollback_is_free_only_while_the_reserve_belongs_to_no_side():
    carve = load(EVIDENCE)["reserve_carve"]
    assert carve["units"].startswith("steps")
    assert carve["side_pool"] == "33" and carve["reserve_pool"] == "1"
    before = carve["carved_out_before_the_sides_start"]
    carved = carve["carved_out_of_a_side"]
    assert before["unchanged"] is True and before["side_after_a_failed_join"] == "33"
    assert carved["unchanged"] is False and carved["side_after_a_failed_join"] == "31"
    assert carved["defect_in_steps"] == carve["cost_of_a_failed_join"]


def test_budget_shares_and_probability_masses_are_kept_apart():
    evidence = load(EVIDENCE)
    separation = evidence["quantities_kept_apart"]
    assert separation["the_two_are_different_quantities"] is True
    assert separation["budget_shares"] != separation["probability_masses_at_level_zero"]
    levels = {row["joins"]: row for row in evidence["level_map"]}
    assert (levels[0]["resolved_mass"], levels[0]["remaining_mass"]) == ("1/2", "1/2")
    assert (levels[3]["resolved_mass"], levels[3]["remaining_mass"]) == ("15/16", "1/16")


def test_the_recorded_errors_stay_on_the_record():
    findings = " ".join(load(EVIDENCE)["findings"])
    assert "dimensionless" in findings, "the unit-mixing error must remain recorded"
    non_claims = " ".join(load(EVIDENCE)["non_claims"])
    assert "optimality" in non_claims
    text = NOTE.read_text(encoding="utf-8")
    assert "本轮记录在案的错误" in text
    assert "未化解的张力" in text, "the tension with the triadic policy must be stated"
    assert "每侧启动前" in text


def test_the_note_is_indexed_and_the_claim_exists():
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert NOTE.exists()
    assert "traversal-allocation-and-reserve" in CLAIMS.read_text(encoding="utf-8")
