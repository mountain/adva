"""The join, measured after the procedure was corrected.

Research 0195 withdraws Research 0194's finding that the anchor-to-anchor link is not established,
and measures what a joined link costs. The tempting repairs here are the quiet ones: keep the
earlier conclusion because its evidence still reproduces, treat the join as free, or let the
anchor's byte series be assumed rather than read.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/joined_chain_cost"
EVIDENCE = EXPERIMENT / "evidence.json"
EARLIER_NOTE = ROOT / "docs/research/0194-the-measured-key-and-certificate-cost.md"
NOTE = ROOT / "docs/research/0195-the-join-measured.md"
CLAIMS = ROOT / "docs/claims.toml"

HOST_FIELDS = ("update_wall_ms_measured", "verify_wall_ms_measured")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def strip_host_quantities(evidence):
    copy = json.loads(json.dumps(evidence))
    copy["counts"].pop("wall_seconds_before_serialization")
    for row in copy["links"]:
        for field in HOST_FIELDS:
            row.pop(field)
    return copy


def replay(tmp_path):
    completed = subprocess.run([sys.executable, str(EXPERIMENT / "calibration.py"),
                                str(tmp_path / "fresh.json")],
                               cwd=ROOT, capture_output=True, text=True, timeout=900,
                               check=False)
    assert completed.returncode == 0, completed.stderr
    return load(tmp_path / "fresh.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh, retained = replay(tmp_path), load(EVIDENCE)
    assert strip_host_quantities(fresh) == strip_host_quantities(retained)


def test_the_join_holds_at_every_level_above_the_first():
    links = load(EVIDENCE)["links"]
    assert [row["level"] for row in links] == list(range(1, 13))
    assert links[0]["prev_anchor_match"] is None
    assert all(row["prev_anchor_match"] is True for row in links[1:])
    assert all(row["chain_field_is_the_previous_self_hash"] is True for row in links[1:])
    assert all(row["status"] == "Intact" for row in links)


def test_the_join_rule_is_read_out_of_the_retained_implementation():
    rule = load(EVIDENCE)["retained_rule"]
    assert rule["scan_directory"] == "root/lineage/anchors"
    assert "self_sha256" in rule["join_rule"]
    assert rule["read_from"] == "python/adva/lineage.py"


def test_joining_costs_bytes_and_then_only_the_digits_move_the_size():
    growth = load(EVIDENCE)["growth"]
    assert growth["lone_anchor_bytes"] == 533
    assert growth["the_join_costs_bytes_per_anchor"] > 0
    assert growth["anchor_bytes_per_level"] == [533] + [597] * 8 + [598] * 3
    assert growth["beyond_the_join_only_the_digits_move_the_size"] is True
    assert growth["the_join_costs_reading_the_predecessor"] == 64
    assert growth["units_are_constant"] is True


def test_one_per_cent_stays_off_the_optimum_under_the_measured_growth():
    rows = {row["declared_conversion_layer_steps_per_measure"]: row
            for row in load(EVIDENCE)["reserve_under_measured_growth"]}
    assert all(row["one_percent_is_optimal"] is False for row in rows.values())
    assert rows[1]["optimal_reserve_steps"] == 49
    assert rows[128]["optimal_reserve_steps"] == 896
    # the optimum grows with the price of a link, which is the direction the table shows
    order = [rows[key]["optimal_reserve_steps"] for key in (1, 2, 4, 8, 16, 32, 64, 128)]
    assert order == sorted(order)


def test_the_correction_is_recorded_in_both_places():
    text = EARLIER_NOTE.read_text(encoding="utf-8")
    assert "更正（2026-09-15" in text
    assert "本文 §3 的结论被撤回" in text
    assert "lineage/anchors" in text
    later = NOTE.read_text(encoding="utf-8")
    assert "错在**程序**，不在**工具**" in later or "不在**工具**" in later
    assert "撤回" in later


def test_the_refusals_and_the_claim_registry():
    evidence = load(EVIDENCE)
    assert len(evidence["refusals"]) == 3
    assert all(row["refused"] is True and row["message"] for row in evidence["refusals"])
    claims = CLAIMS.read_text(encoding="utf-8")
    assert "joined-chain-cost" in claims
    assert "withdrawn" in claims or "撤回" in claims


def test_the_note_is_indexed():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
