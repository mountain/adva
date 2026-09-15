"""Two gain curves on one cost axis, and the correction of a recorded sentence.

Research 0201 recomputes the ledger's margins because a recorded finding states their direction
backwards, then puts both objectives' gains on the shared cost axis. The tempting repairs here are
the quiet ones: remember the sentence instead of recomputing it, let a corrected number be written
into the frozen evidence, or claim the measurement decides which objective wins.
"""

import hashlib
import json
import subprocess
import sys
from fractions import Fraction as Fr
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/marginal_exchange"
EVIDENCE = EXPERIMENT / "evidence.json"
LEDGER = ROOT / "experiments/protocol_mass_ledger/evidence.json"
CURVE = ROOT / "experiments/depth_curve/evidence.json"
NOTE = ROOT / "docs/research/0201-two-curves-on-one-cost-axis.md"
EARLIER_NOTE = ROOT / "docs/research/0198-the-protocol-ledger-and-why-the-partition-does-not-transfer.md"
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


def test_the_marginal_cost_is_recomputed_and_rises():
    evidence = load(EVIDENCE)
    marginal = evidence["marginal_cost"]
    assert marginal["first"] == "12"
    assert marginal["last"] == "2031616"
    assert marginal["strictly_rising"] is True
    assert marginal["the_frozen_finding_says_it_falls"] is True
    values = [Fr(row["side_steps_per_unit_gain"]) for row in evidence["margins"]]
    assert all(later > earlier for earlier, later in zip(values, values[1:]))


def test_the_frozen_evidence_keeps_its_wording_and_the_note_carries_the_correction():
    assert any("per unit of resolved mass falls" in text
               for text in load(LEDGER)["findings"]), "the frozen wording must stay"
    text = EARLIER_NOTE.read_text(encoding="utf-8")
    assert "更正（2026-09-15" in text
    assert "严格上升" in text
    assert "冻结的证据不改写" in text


def test_both_objectives_put_their_best_layer_first():
    shapes = load(EVIDENCE)["shapes"]
    assert shapes["wrapper"]["shape"] == "strictly falling"
    assert shapes["keraia"]["shape"] == "not monotone"
    assert shapes["wrapper"]["best_layer"] == 1
    assert shapes["keraia"]["best_layer"] == 1
    assert shapes["orderings"]["the_two_orderings_differ"] is True
    assert shapes["orderings"]["discordant_pairs"] > 0


def test_the_dead_zone_for_acceptance_is_measured_not_described():
    rows = {row["level"]: row for row in load(EVIDENCE)["two_curves"]}
    assert rows[2]["keraia_acceptance_gain"] == "0"
    assert rows[3]["keraia_acceptance_gain"] == "0"
    assert Fr(rows[2]["wrapper_gain"]) > 0, "those layers still buy resolution"
    assert Fr(rows[1]["keraia_gain_per_step"]) > 0


def test_the_exchange_separates_units_from_value():
    exchange = load(EVIDENCE)["the_exchange"]
    assert exchange["unit_conversion_is_measured"] is True
    assert exchange["value_exchange_is_measured"] is False
    assert exchange["the_objective_must_be_declared"] is True
    assert "decision" in exchange["the_criterion_is_not_free"]


def test_the_inputs_are_pinned_and_read_only():
    inputs = load(EVIDENCE)["inputs"]
    for key, path in (("ledger", LEDGER), ("curve", CURVE)):
        assert inputs[key]["sha256"] == hashlib.sha256(path.read_bytes()).hexdigest()
    assert inputs["all_read_only"] is True


def test_the_recorded_errors_and_refusals_survive():
    text = NOTE.read_text(encoding="utf-8")
    assert "最优层会不同" in text
    assert len(load(EVIDENCE)["refusals"]) == 3
    assert all(row["refused"] is True for row in load(EVIDENCE)["refusals"])


def test_the_note_is_indexed_and_the_claim_exists():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "marginal-exchange" in CLAIMS.read_text(encoding="utf-8")
