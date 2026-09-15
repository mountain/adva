"""The successor declaration: the reserve derived, and the check still discriminating.

Research 0197 removes the last magic number from the protocol by deriving the reserve, while the
frozen version zero declaration and its evidence stay as they are. The tempting repairs here are
the quiet ones: let a derived declaration compare itself against the scan that produced it, relax a
clause so the successor passes, or overwrite the frozen record because it now fails.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/protocol_declaration"
V0_PROTOCOL = EXPERIMENT / "protocol.json"
V1_PROTOCOL = EXPERIMENT / "protocol-v1.json"
V0_EVIDENCE = EXPERIMENT / "evidence.json"
V1_EVIDENCE = EXPERIMENT / "evidence-v1.json"
NOTE = ROOT / "docs/research/0197-the-protocol-without-a-magic-number.md"
CLAIMS = ROOT / "docs/claims.toml"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def replay(tmp_path):
    completed = subprocess.run([sys.executable, str(EXPERIMENT / "checker-v1.py"),
                                str(tmp_path / "fresh.json")],
                               cwd=ROOT, capture_output=True, text=True, timeout=900,
                               check=False)
    assert completed.returncode == 0, completed.stderr
    return load(tmp_path / "fresh.json")


def test_a_fresh_successor_run_reproduces_the_retained_evidence(tmp_path):
    assert replay(tmp_path) == load(V1_EVIDENCE)


def test_the_successor_passes_every_clause_and_the_frozen_one_still_fails_one():
    evidence = load(V1_EVIDENCE)
    assert evidence["status"] == "ProtocolChecked"
    assert evidence["clauses_failed"] == 0 and evidence["clauses_passed"] == 6
    assert evidence["version_zero_clauses_failed"] == 1
    assert evidence["the_check_discriminates"]["same_code_two_declarations"] is True
    assert "reserve" in evidence["the_check_discriminates"]["version_zero_failing_clause"]


def test_the_derived_reserve_is_computed_by_the_declaration_rule_not_by_the_scan():
    detail = [row for row in load(V1_EVIDENCE)["clauses"] if "reserve" in row["clause"]][0]["detail"]
    assert detail["method"] == "the declaration's crossing rule"
    assert detail["operative_value"] == "derived"
    assert detail["declared_reserve_steps"] == 225
    assert detail["scan_reserve_steps"] == 225
    assert detail["derivation_and_scan_agree"] is True


def test_the_historical_fraction_is_retained_with_its_gap():
    evidence = load(V1_EVIDENCE)
    historical = evidence["historical_direction_value"]
    assert historical["value"] == "1/100"
    assert historical["steps_at_this_budget"] == 10
    assert historical["levels_bought"] == 1
    assert historical["gap_in_remaining_mass_against_the_derived_reserve"] == "33554431/134217728"
    assert "no longer operative" in historical["status"]


def test_the_successor_strengthened_the_reserve_clause_and_left_the_others_alone():
    v0 = set(load(V0_PROTOCOL)["checks_required"])
    v1 = set(load(V1_PROTOCOL)["checks_required"])
    assert len(v0) == len(v1) == 6
    assert len(v0 - v1) == 1 and len(v1 - v0) == 1
    changed = (v0 - v1).pop()
    assert "reserve" in changed
    assert "or the declaration states the gap" in changed, "the escape hatch was in the old clause"
    new = (v1 - v0).pop()
    assert "or the declaration states the gap" not in new, "the escape hatch must be gone"


def test_the_frozen_record_is_pinned_and_reproduces():
    evidence = load(V1_EVIDENCE)
    supersession = evidence["supersession"]
    assert supersession["protocol_matches_the_pin"] is True
    assert supersession["evidence_matches_the_pin"] is True
    import hashlib
    for path, key in ((V0_PROTOCOL, "protocol_sha256"), (V0_EVIDENCE, "evidence_sha256")):
        assert hashlib.sha256(path.read_bytes()).hexdigest() == supersession[key]
    # the frozen version zero check still reproduces byte for byte
    assert load(V0_EVIDENCE)["clauses_failed"] == 1


def test_the_vacuity_hazard_stays_on_the_record():
    text = NOTE.read_text(encoding="utf-8")
    assert "同义反复" in text
    assert "两条独立方法" in text
    findings = " ".join(load(V1_EVIDENCE)["findings"])
    assert "non-vacuous" in findings or "vacuous" in findings


def test_the_note_is_indexed_and_the_claim_exists():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "protocol-without-a-magic-number" in CLAIMS.read_text(encoding="utf-8")
