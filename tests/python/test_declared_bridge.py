"""Declaring the two spaces, and the row that can then carry both currencies.

Research 0199 finds that the factor between the two mass accounts is an atom-measure ratio, the
same at every declared depth. The tempting repairs here are the quiet ones: compute the ratio at
one depth and call it a bridge, let the row claim the traversal resolves the family, or forget to
say that the correspondence is declared.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/declared_bridge"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0199-declaring-the-two-spaces.md"
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


def test_the_atom_ratio_is_the_same_at_every_declared_depth():
    evidence = load(EVIDENCE)
    ratios = evidence["atom_ratios"]
    assert [row["depth"] for row in ratios] == list(range(21))
    assert {row["keraia_atoms_in_the_wrapper_tail"] for row in ratios} == {"1/2"}
    assert evidence["the_constant_is_depth_independent"] is True
    assert load(EVIDENCE)["counts"]["atom_ratios_computed"] == 21


def test_the_earlier_factor_decomposes_into_an_atom_count_and_a_ratio():
    decomposition = load(EVIDENCE)["decomposition_of_the_earlier_factor"]
    assert decomposition["factor_between_the_accounts"] == "13378"
    assert decomposition["unresolved_atoms"] == 6689
    assert decomposition["atom_over_tail"] == "2"
    assert decomposition["the_factor_is_the_atom_count_over_the_atom_ratio"] is True


def test_the_one_row_carries_the_mass_and_the_cost_together():
    row = load(EVIDENCE)["the_one_row"]
    assert row["depth"] == 15
    assert row["unresolved_mass"] == "6689/32768"
    assert row["mass_account_as_retained"]["accepted"] == "26078/32768"
    assert row["mass_account"]["accepted"] == "13039/16384", "the reduced form"
    assert "reduce" in row["notation_note"]
    assert row["cost_account"]["reserve_steps"] == 126
    assert row["cost_account"]["side_steps"] == 256
    assert row["cost_account"]["reserve_to_side_ratio"] == "63/128"


def test_the_row_names_its_declarations_and_its_limits():
    row = load(EVIDENCE)["the_one_row"]
    assert row["correspondence_status"] == "declared, not measured"
    assert row["depths_with_a_retained_partition"] == [15]
    assert "no retained partition exists" in row["other_depths"]
    assert "bridge constant" in " ".join(row).lower() or row["bridge_constant"]
    assert "does not" in row["what_this_row_does_not_say"]


def test_the_refused_reading_is_refused_with_a_reason():
    refused = load(EVIDENCE)["the_refused_reading"]
    assert "more protocol levels resolve more" in refused["the_tempting_reading"]
    assert "reach" in refused["why_it_is_refused"]
    non_claims = " ".join(load(EVIDENCE)["non_claims"])
    assert "does not merge them" in non_claims


def test_the_recorded_error_and_the_refusals_survive():
    text = NOTE.read_text(encoding="utf-8")
    assert "分解公式" in text
    assert "声明，不是测量" in text or "声明，非测量" in text
    assert len(load(EVIDENCE)["refusals"]) == 3
    assert all(row["refused"] is True for row in load(EVIDENCE)["refusals"])


def test_the_note_is_indexed_and_the_claim_exists():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "declared-bridge" in CLAIMS.read_text(encoding="utf-8")
