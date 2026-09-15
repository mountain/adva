"""The depth curve derived from retained evidence.

Research 0200 derives per-depth partitions from the retained cycles evidence and pairs them with
the measured cost. The tempting repairs here are the quiet ones: fit the aggregates instead of
reproducing them, read a machine's position as a cylinder's length, or claim a saturation depth
from a hypothesis the curve then refutes.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/depth_curve"
EVIDENCE = EXPERIMENT / "evidence.json"
RETAINED = ROOT / "experiments/keraia_cycle_mass/evidence/attempt-1/primary.json"
NOTE = ROOT / "docs/research/0200-the-depth-curve-from-retained-evidence.md"
CLAIMS = ROOT / "docs/claims.toml"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def replay(tmp_path):
    completed = subprocess.run([sys.executable, str(EXPERIMENT / "calibration-v0.py"),
                                str(tmp_path / "fresh.json")],
                               cwd=ROOT, capture_output=True, text=True, timeout=900,
                               check=False)
    assert completed.returncode == 0, completed.stderr
    return load(tmp_path / "fresh.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    assert replay(tmp_path) == load(EVIDENCE)


def test_the_reconstruction_reproduces_every_retained_aggregate():
    agreement = load(EVIDENCE)["agreement_with_the_retained_aggregates"]
    for computed, retained in (("accepted_total", "retained_accepted"),
                               ("unresolved_total", "retained_unresolved"),
                               ("need_input", "retained_need_input"),
                               ("need_syntax", "retained_need_syntax")):
        assert agreement[computed] == agreement[retained], (computed, agreement)
    assert agreement["accepted_total"] == "13039/16384"
    assert agreement["unresolved_total"] == "6689/32768"


def test_the_retained_evidence_is_read_only_and_pinned():
    recorded = load(EVIDENCE)["retained_evidence"]
    assert recorded["sha256"] == hashlib.sha256(RETAINED.read_bytes()).hexdigest()
    assert recorded["status"] == "Passed"
    assert "three-part mass partition" in recorded["the_check_that_carries_the_partition"]


def test_the_curve_carries_mass_and_cost_at_every_depth():
    curve = {row["depth"]: row for row in load(EVIDENCE)["curve"]}
    assert len(curve) == 16
    assert curve[0]["accepted_mass_decided_so_far"] == "0"
    assert curve[0]["undecided_mass"] == "1"
    assert curve[15]["accepted_mass_decided_so_far"] == "13039/16384"
    assert curve[15]["total_steps"] == 382
    assert curve[14]["accepted_mass_decided_so_far"] == "12927/16384"


def test_the_saturation_is_measured_and_the_last_layer_closes():
    evidence = load(EVIDENCE)
    assert evidence["accepted_mass_saturates_at_depth"] == 15
    marginal = evidence["marginal_layer"]
    assert marginal["undecided_before_it"] == "3457/16384"
    assert marginal["acceptance_bought_by_the_last_layer"] == "7/1024"
    assert marginal["cost_of_the_last_layer_steps"] == 40


def test_the_refuted_hypotheses_stay_on_the_record():
    findings = " ".join(load(EVIDENCE)["findings"])
    assert "refuted" in findings
    text = NOTE.read_text(encoding="utf-8")
    assert "饱和在 **15**，不是 14" in text
    assert "被数据反驳" in text
    assert "ExternalExactPass" in text, "the guessed status word must stay recorded"


def test_the_limits_are_stated():
    non_claims = " ".join(load(EVIDENCE)["non_claims"])
    assert "not re-run" in non_claims
    assert "not detectable from inside" in non_claims
    assert len(load(EVIDENCE)["refusals"]) == 3


def test_the_note_is_indexed_and_the_claim_exists():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "depth-curve" in CLAIMS.read_text(encoding="utf-8")
