"""Does a step close more apertures than it opens? Counted per currency.

Research 0202 answers the question by counting, and the temptation here is to add the three
currencies into one number, to let a step that opens nothing hide the residual truncation opens, or
to treat a structural floor as a failure of the step.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/aperture_ledger"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0202-does-a-step-close-more-than-it-opens.md"
INVENTORY = ROOT / "docs/maintenance/float-apertures.json"
CLAIMS = ROOT / "docs/claims.toml"


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


def test_the_scanner_currency_closes_more_than_it_opens_over_the_line():
    scanner = load(EVIDENCE)["scanner_currency"]
    assert scanner["net_closing_strict"] == 7
    assert scanner["net_closing_loose"] == 3
    assert scanner["steps_that_opened_more"] == ["after 0192"]
    assert len(scanner["steps_that_closed_more"]) == 7
    assert scanner["direction_followed_over_the_line"] is True
    assert scanner["sign_convention"].startswith("positive means more closed")


def test_the_two_nets_disagree_where_an_illustration_was_added():
    scanner = load(EVIDENCE)["scanner_currency"]
    assert scanner["steps_where_the_two_nets_disagree"] == [
        "after 0191", "after 0193", "after 0194", "after 0195"]
    rows = {row["step"]: row for row in scanner["steps"]}
    assert rows["after 0193"]["into_illustration_only"] == 1
    assert rows["after 0193"]["strict_net_closing"] == 0
    assert rows["after 0193"]["loose_net_closing"] == -1


def test_the_series_is_checked_against_the_inventory_and_the_gap_is_recorded():
    inventory = load(INVENTORY)
    scanner = load(EVIDENCE)["scanner_currency"]
    assert scanner["derived_counts"]["no_numeric_assumed_constant"] == 2
    assert inventory["verdicts"]["no-numeric-constructs"] == 2
    # the series has to agree with the inventory it counts, including the point for this round
    steps = scanner["steps"]
    assert steps[-1]["step"] == "after 0202, which counts itself"
    assert inventory["verdicts"]["exact-only"] == 13
    assert inventory["verdicts"]["imprecision-in-illustration-only"] == 29
    assert scanner["self_reference"]["the_instrument_is_inside_what_it_measures"] is True
    gap = scanner["documentation_gap"]
    assert gap["the_deciding_step_is_recorded_only_in_prose"] is True
    assert len(gap["recorded_exact_only_deltas"]) == 5


def test_the_mass_currency_separates_resolving_from_truncating():
    mass = load(EVIDENCE)["mass_currency"]
    assert mass["resolving_step"]["net"] == -1
    assert mass["resolving_step"]["opened"] == "nothing"
    assert mass["truncating_step"]["net"] == 0
    assert "residual" in mass["truncating_step"]["opened"]
    assert mass["levels_that_change_nothing"] == [2, 3]


def test_the_statement_currency_has_a_structural_floor():
    statements = load(EVIDENCE)["statement_currency"]
    assert statements["closed"] == 2 and statements["opened"] == 2
    assert statements["net"] == 0
    assert "never rewritten" in statements["structural_floor"]
    assert {row["evidence"] for row in statements["refuted_but_kept"]} == {
        "evidence.json"}


def test_the_recorded_errors_and_refusals_survive():
    text = NOTE.read_text(encoding="utf-8")
    assert "符号约定读反" in text
    assert "只记了散文" in text
    assert "读输出" in text, "the error no check caught must stay recorded"
    assert len(load(EVIDENCE)["refusals"]) == 4
    assert all(row["refused"] is True for row in load(EVIDENCE)["refusals"])


def test_the_currencies_are_not_added_together():
    evidence = load(EVIDENCE)
    nets = {evidence["scanner_currency"]["net_closing_strict"],
            evidence["mass_currency"]["truncating_step"]["net"],
            evidence["statement_currency"]["net"]}
    assert len(nets) > 1, "the three currencies must not collapse to one number"
    assert "currency" in evidence["the_direction_rule"]


def test_the_note_is_indexed_and_the_claim_exists():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "aperture-ledger" in CLAIMS.read_text(encoding="utf-8")
