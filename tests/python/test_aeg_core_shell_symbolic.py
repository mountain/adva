"""The core-plus-shell carrier: frozen record, successor, and the reduction rule.

Research 0189 records the first rung and then its successor. The version-zero
contract and evidence are a frozen record of the run that found the structural gap;
the version-one successor adds exact canonicalisation and closes it. This test holds
both in place, because the tempting repairs here are the quiet ones: emit the new
sections under the old contract until the frozen record no longer reproduces, or
drop the provenance so that two shells look alike.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/aeg_core_shell_symbolic"
CHECKER = HERE / "calibration.py"
FROZEN_CONTRACT = HERE / "contract.json"
FROZEN_EVIDENCE = HERE / "evidence.json"
ACTIVE_CONTRACT = HERE / "contract-v1.json"
ACTIVE_EVIDENCE = HERE / "evidence-v1.json"
NOTE = ROOT / "docs/research/0189-core-shell-and-symbolically-unexpanded-shell.md"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run(checker=CHECKER, contract=None, output=None, cwd=ROOT):
    argv = [sys.executable, str(checker)]
    if contract:
        argv += ["--contract", str(contract)]
    if output:
        argv += [str(output)]
    return subprocess.run(argv, capture_output=True, text=True, timeout=300, check=False, cwd=cwd)


def test_the_frozen_contract_still_reproduces_its_own_evidence(tmp_path):
    """The version-zero record must stay reproducible, not merely retained."""
    fresh = tmp_path / "v0.json"
    completed = run(contract=FROZEN_CONTRACT, output=fresh)
    assert completed.returncode == 0, completed.stderr
    assert load(fresh) == load(FROZEN_EVIDENCE), (
        "the frozen evidence no longer follows from its own contract")


def test_the_successor_verifies_the_predecessor_by_digest():
    supersession = load(ACTIVE_EVIDENCE)["supersession"]
    assert supersession["status"] == "Unchanged"
    assert supersession["sha256"] == hashlib.sha256(FROZEN_CONTRACT.read_bytes()).hexdigest()
    assert supersession["predecessor_evidence_sha256"] == hashlib.sha256(
        FROZEN_EVIDENCE.read_bytes()).hexdigest()


def test_editing_the_frozen_record_would_fail_the_successor(tmp_path):
    """The digest pin must be load bearing, not decorative."""
    work = tmp_path / "work"
    (work / "experiments").mkdir(parents=True)
    shutil.copytree(HERE, work / "experiments/aeg_core_shell_symbolic")
    copy = work / "experiments/aeg_core_shell_symbolic"
    contract = copy / "contract.json"
    contract.write_text(contract.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    completed = run(checker=copy / "calibration.py", contract=copy / "contract-v1.json",
                    output=tmp_path / "out.json")
    assert completed.returncode != 0, "an edited predecessor must fail the successor"
    assert "TheSupersededContractWasEdited" in completed.stderr


def test_canonicalisation_closes_the_gap_the_first_run_recorded():
    frozen = load(FROZEN_EVIDENCE)["structural_cost_of_the_pair"]
    assert frozen and all(row["literal_pair_equality"] is False for row in frozen), (
        "the frozen run must still record the gap it found")
    active = load(ACTIVE_EVIDENCE)["canonicalisation"]
    assert active
    for row in active:
        assert row["literally_equal_before"] is False
        assert row["literally_equal_after"] is True
        assert row["value_preserved"] is True and row["idempotent"] is True
        assert row["left_canonical"] == row["right_canonical"]
        assert row["normalisation_convention"]


def test_the_shell_participates_and_provenance_stays_load_bearing():
    participation = load(ACTIVE_EVIDENCE)["shell_participation"]
    assert participation
    for row in participation:
        assert row["content_equal"] is True, "shell content must reach a shared canonical form"
        assert row["object_equal"] is False, (
            "object identity must additionally require the provenance")
        assert row["provenance_differs"] is True
    controls = load(ACTIVE_EVIDENCE)["provenance_controls"]
    assert len(controls) >= 3
    assert any(row["object_equal"] is False for row in controls)
    assert any(row["object_equal"] is True for row in controls), (
        "provenance must be load bearing in both directions")
    for row in controls:
        assert row["content_equal"] is True
        assert row["object_equal"] == row["object_equality_expected"]


def test_the_first_rung_findings_survive_in_the_successor():
    report = load(ACTIVE_EVIDENCE)
    findings = " | ".join(report["findings"])
    assert "one shared truncation preserves the identity" in findings
    assert "the pollution needs both a per-branch truncation and distinct outer terms" in findings
    assert "identifiability" in findings
    shared = [r for r in report["truncation_controls"]
              if r["kind"].startswith("one shared truncation")]
    assert shared and all(r["identity_holds"] for r in shared)


def test_a_fresh_run_reproduces_the_active_evidence(tmp_path):
    fresh = tmp_path / "fresh.json"
    completed = run(output=fresh)
    assert completed.returncode == 0, completed.stderr
    assert load(fresh) == load(ACTIVE_EVIDENCE)


def test_the_note_records_the_closure_and_the_registry_agrees():
    note = NOTE.read_text(encoding="utf-8")
    assert "典范化" in note and "来源" in note
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    match = [c for c in claims
             if c["claim_id"] == "adva.bounded-experiment.aeg-core-shell-canonical.v0"]
    assert len(match) == 1
    forbidden = " | ".join(match[0]["forbidden_conflations"])
    assert "A shared canonical form with a shared object identity" in forbidden
    assert "A canonical shell with a discarded provenance" in forbidden
    earlier = [c for c in claims
               if c["claim_id"] == "adva.bounded-experiment.aeg-core-shell-symbolic.v0"]
    assert len(earlier) == 1, "the first rung keeps its own claim"
