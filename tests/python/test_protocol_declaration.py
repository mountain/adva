"""The protocol as a declaration with verdicts per clause.

Research 0196 turns the direction's proposal into a file a checker reads. The tempting repairs
here are the quiet ones: paraphrase a clause so it passes, let the declaration and the checker
drift apart, or call the key half measured because no measurement refused.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/protocol_declaration"
PROTOCOL = EXPERIMENT / "protocol.json"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0196-the-protocol-as-a-checkable-declaration.md"
CLAIMS = ROOT / "docs/claims.toml"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def replay(tmp_path):
    completed = subprocess.run([sys.executable, str(EXPERIMENT / "checker.py"),
                                str(tmp_path / "fresh.json")],
                               cwd=ROOT, capture_output=True, text=True, timeout=600,
                               check=False)
    assert completed.returncode == 0, completed.stderr
    return load(tmp_path / "fresh.json")


def test_a_fresh_check_reproduces_the_retained_evidence(tmp_path):
    assert replay(tmp_path) == load(EVIDENCE)


def test_declared_checks_and_performed_checks_are_the_same_set():
    declared = set(load(PROTOCOL)["checks_required"])
    performed = {row["clause"] for row in load(EVIDENCE)["clauses"]}
    assert declared == performed, declared ^ performed


def test_five_clauses_pass_and_the_reserve_clause_fails():
    evidence = load(EVIDENCE)
    assert evidence["status"] == "ProtocolContradictsTheMeasurements"
    failed = [row for row in evidence["clauses"] if row["verdict"] != "pass"]
    assert len(failed) == 1
    assert "reserve" in failed[0]["clause"]
    assert evidence["clauses_passed"] == 5 and evidence["clauses_failed"] == 1


def test_the_failing_clause_carries_the_numbers_that_fail_it():
    detail = [row for row in load(EVIDENCE)["clauses"] if row["verdict"] != "pass"][0]["detail"]
    assert detail["declared_reserve_steps"] == "10"
    assert detail["priced_reserve_steps"] == 225
    assert detail["priced_reserve_fraction"] == "9/40"
    assert detail["declared_levels_bought"] == 1
    assert detail["priced_levels_bought"] == 26
    assert detail["declared_resolved"] == "3/4"
    assert detail["gap_in_remaining_mass"] == "33554431/134217728"
    assert "what_would_make_it_pass" in detail


def test_the_sides_clause_is_checked_against_exhaustive_search():
    detail = [row for row in load(EVIDENCE)["clauses"]
              if row["clause"].startswith("the declared side split")][0]["detail"]
    assert detail["leveling_resolved"] == detail["exhaustive_resolved"]
    assert detail["equal_shares_reach_equal_depths"] is True


def test_the_key_half_clause_is_an_obligation():
    clause = [row for row in load(EVIDENCE)["clauses"] if "key half" in row["clause"]][0]
    assert clause["verdict"] == "pass"
    assert clause["detail"]["declared"] == "unmeasured"
    assert clause["detail"]["measured_on_this_host"] is False
    assert "zero" in clause["detail"]["obligation"] or "surcharge" in clause["detail"]["obligation"]


def test_the_declaration_is_not_a_permission_slip():
    protocol = load(PROTOCOL)
    assert "authorizes no run of its own" in protocol["authority"]
    evidence = load(EVIDENCE)
    assert "does not argue optimality" in " ".join(evidence["non_claims"])
    assert evidence["native_status"] == "NotRun"


def test_the_note_and_the_claim_exist_and_are_indexed():
    assert NOTE.exists()
    text = NOTE.read_text(encoding="utf-8")
    assert "declaration" in text or "声明" in text
    assert "5 过 / 1 不过" in text or "五过一不过" in text
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "protocol-declaration" in CLAIMS.read_text(encoding="utf-8")
