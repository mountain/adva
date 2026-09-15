"""Allocating the three aperture currencies by the optimal-allocation rule.

Research 0203 applies the rule and checks it rather than inheriting it. The temptation here is to
trust the greedy because it was verified for another shape, to give an exhausted currency a share so
the split looks balanced, or to look for the threshold in whichever variable comes first.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/currency_allocation"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0203-allocating-the-three-currencies.md"
CLAIMS = ROOT / "docs/claims.toml"
INVENTORY = ROOT / "docs/maintenance/float-apertures.json"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def replay(tmp_path):
    completed = subprocess.run([sys.executable, str(EXPERIMENT / "calibration.py"),
                                str(tmp_path / "fresh.json")],
                               cwd=ROOT, capture_output=True, text=True, timeout=600,
                               check=False)
    assert completed.returncode == 0, completed.stderr
    return load(tmp_path / "fresh.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    assert replay(tmp_path) == load(EVIDENCE)


def test_the_costs_and_stocks_are_measured_from_retained_artifacts():
    measured = load(EVIDENCE)["measured"]
    costs = measured["base_cost_per_closure_rounds"]
    assert costs["mass"] == "8/15" and costs["scanner"] == "4/7"
    # the statement figure is live: this line's own corrections add closures to that currency
    assert costs["statement"] == "2/3", "the statement cost moves as corrections are appended"
    assert measured["stock"]["statement"]["closable_statements_left"] == 0
    assert measured["stock"]["mass"]["depths_reachable_without_new_evidence"] == 0
    assert measured["stock"]["scanner"]["deciding_apertures_left"] == 38
    assert measured["stock"]["scanner"]["illustrating_apertures_left"] == 29


def test_the_allocation_goes_to_the_cheap_currency_at_the_declared_budget():
    optimum = load(EVIDENCE)["exhaustive_optimum_at_equal_weights"]
    assert optimum["counts"] == {"scanner": 6, "mass": 0, "statement": 0}
    assert optimum["cost"] == "12"
    assert optimum["prerequisites_paid"] == []


def test_the_budget_threshold_orders_the_work():
    threshold = load(EVIDENCE)["budget_threshold"]
    assert threshold["smallest_budget_at_which_the_mass_prerequisite_is_paid"] == 18
    rows = {row["budget_rounds"]: row for row in threshold["rows"]}
    assert rows[12]["prerequisite_paid"] is False
    assert rows[18]["prerequisite_paid"] is True
    assert rows[18]["counts"] == {"scanner": 4, "mass": 4, "statement": 0}
    assert all(row["counts"]["statement"] == 0 for row in threshold["rows"])


def test_the_greedy_rule_is_checked_and_recorded_as_failing():
    evidence = load(EVIDENCE)
    assert evidence["the_rule_matches_the_exhaustive_optimum_at_equal_weights"] is True
    broken = evidence["the_rule_is_a_greedy_and_prerequisites_break_it"]
    assert broken["matches"] == 4 and broken["failures"] == 5
    assert "bundle" in broken["why"]


def test_the_weights_are_declared_and_the_split_is_honest_about_them():
    evidence = load(EVIDENCE)
    assert evidence["declared"]["weights_are_declared_because_no_measurement_gives_an_exchange_rate"] is True
    assert "every weight tried" in evidence["the_split_does_not_move_with_the_weights_here"]
    assert "the_split_does_not_move_with_the_weights_here" in evidence
    non_claims = " ".join(evidence["non_claims"])
    assert "weights are declared" in non_claims


def test_the_recorded_slips_and_refusals_survive():
    text = NOTE.read_text(encoding="utf-8")
    assert "存量没有进优化器" in text
    assert "把捆绑当单件定价" in text
    assert "门槛找错了地方" in text
    assert len(load(EVIDENCE)["refusals"]) == 3
    assert all(row["refused"] is True for row in load(EVIDENCE)["refusals"])


def test_the_inventory_and_the_currency_counts_agree():
    inventory = load(INVENTORY)
    assert inventory["verdicts"]["imprecision-can-decide"] == 38
    assert inventory["verdicts"]["imprecision-in-illustration-only"] == 29
    assert inventory["experiments_scanned"] >= 82


def test_the_note_is_indexed_and_the_claim_exists():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "currency-allocation" in CLAIMS.read_text(encoding="utf-8")
