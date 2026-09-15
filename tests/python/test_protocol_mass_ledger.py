"""The protocol ledger, and the partition that does not transfer.

Research 0198 walks the protocol's levels against the measured link price and the retained layer
masses, then tests the tempting identification of a protocol level with a unit of the retained
depth. The tempting repairs here are the quiet ones: carry the retained partition onto the ledger
because both are masses, treat cylinder counts as word counts, or pick one currency and call it the
cost.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/protocol_mass_ledger"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0198-the-protocol-ledger-and-why-the-partition-does-not-transfer.md"
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


def test_the_ledger_has_both_currencies_at_every_level():
    levels = {row["level"]: row for row in load(EVIDENCE)["levels"]}
    assert len(levels) == 21
    assert levels[0]["resolved_mass"] == "1/2" and levels[0]["remaining_mass"] == "1/2"
    assert levels[15]["cumulative_reserve_steps"] == 126
    assert levels[15]["side_depth_cost_steps"] == 256
    assert levels[15]["resolved_mass"] == "65535/65536"
    assert levels[20]["remaining_mass"] == "1/2097152"


def test_the_binding_currency_changes_at_a_computable_level():
    evidence = load(EVIDENCE)
    assert evidence["binding_currency_crossover_level"] == 4
    binding = [row["binding_currency"] for row in evidence["margins"]]
    assert "reserve" in binding and "sides" in binding
    assert binding[0] == "reserve", "the shallow levels are reserve-bound"


def test_the_retained_partition_re_verifies_and_its_counts_are_not_a_word_space():
    partition = load(EVIDENCE)["retained_partition"]
    assert partition["unresolved_fraction"] == "6689/32768"
    assert partition["counts"]["accepted"] == 508
    assert partition["cylinder_counts_sum"] == 7198
    assert partition["cylinder_counts_do_not_fill_a_word_space"] is True
    assert sum(1 for name in ("accepted", "certified_nonhalting", "pending_input",
                             "incomplete_syntax") if name in partition["classes"]) == 4


def test_the_bridge_is_refused_with_an_exact_factor():
    bridge = load(EVIDENCE)["bridge"]
    assert bridge["measured_bridge_exists"] is False
    assert bridge["exact_factor_between_the_accounts"] == "13378"
    assert bridge["factor_is_two_times_6689"] is True
    assert bridge["wrapper_remaining_at_that_depth"] == "1/65536"
    assert bridge["retained_unresolved_at_that_depth"] == "6689/32768"
    assert "not identified" in bridge["verdict"] or "no mass is transferred" in bridge["verdict"]


def test_the_end_to_end_number_is_a_cost_and_says_so():
    cost = load(EVIDENCE)["bridge"]["cost_to_reach_that_depth"]
    assert cost["reserve_steps"] == 126 and cost["side_steps"] == 256
    assert cost["reserve_fraction_of_the_side_cost"] == "63/128"
    non_claims = " ".join(load(EVIDENCE)["non_claims"])
    assert "does not produce an end-to-end mass number" in non_claims


def test_the_recorded_errors_survive():
    findings = " ".join(load(EVIDENCE)["findings"])
    assert "wrong-quantity slip" in findings, "the cylinder-count slip must stay recorded"
    text = NOTE.read_text(encoding="utf-8")
    assert "交叉点在 k = 4" in text
    assert "柱计数 vs 码字空间" in text
    assert len(load(EVIDENCE)["refusals"]) == 3


def test_the_note_is_indexed_and_the_claim_exists():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "protocol-mass-ledger" in CLAIMS.read_text(encoding="utf-8")
