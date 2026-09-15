"""The measured key and certificate cost: what the retained tooling really answers.

Research 0194 replaces a declared join cost with a measurement. The tempting repairs are the
quiet ones: hope the unit cost is constant when the verification aborts early, treat an empty
predecessor field as a copy mistake, or price the reserve on a failing join that costs less.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/measured_join_cost"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0194-the-measured-key-and-certificate-cost.md"
CLAIMS = ROOT / "docs/claims.toml"

HOST_FIELDS = ("wall_seconds_before_serialization",)
HOST_FIELDS_PER_LINK = ("update_wall_ms_measured", "verify_wall_ms_measured",
                        "update_wall_ms_reported", "verify_wall_ms_reported")


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def strip_host_quantities(evidence):
    copy = json.loads(json.dumps(evidence))
    copy["counts"].pop("wall_seconds_before_serialization")
    for row in copy["links"]:
        for field in HOST_FIELDS_PER_LINK:
            row.pop(field)
    return copy


def replay(tmp_path):
    completed = subprocess.run([sys.executable, str(EXPERIMENT / "calibration.py"),
                                str(tmp_path / "fresh.json")],
                               cwd=ROOT, capture_output=True, text=True, timeout=600,
                               check=False)
    assert completed.returncode == 0, completed.stderr
    return load(tmp_path / "fresh.json")


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh, retained = replay(tmp_path), load(EVIDENCE)
    assert strip_host_quantities(fresh) == strip_host_quantities(retained)


def test_the_certificate_half_is_measured_and_constant():
    growth = load(EVIDENCE)["growth"]
    assert growth["update_units_seen"] == [1]
    assert growth["update_bytes_read_seen"] == [749]
    assert growth["verify_units_where_the_link_verified"] == [2]
    assert growth["the_verification_aborts_before_working_when_the_link_is_missing"] is True


def test_the_anchor_grows_with_the_digits_of_its_sequence_number():
    growth = load(EVIDENCE)["growth"]
    assert growth["anchor_bytes_per_level"] == [533] * 9 + [534] * 3
    assert growth["anchor_bytes_are_constant_with_the_level"] is False
    assert growth["anchor_growth_is_bounded_by_the_digit_count"] is True
    assert "logarithmic" in growth["measured_growth_shape"]


def test_the_link_between_anchors_is_measured_not_to_join():
    chain = load(EVIDENCE)["chain_link"]
    assert chain["established_by_this_tool_path"] is False
    assert chain["tool_verdict_with_a_previous_anchor"].startswith("Tampered")
    rows = [row for row in load(EVIDENCE)["links"] if row["level"] > 1]
    assert all(row["chain_field_empty"] for row in rows)
    assert all(row["prev_anchor_match"] is False for row in rows)
    assert all(row["prev_anchor_reason"] == "prev_anchor mismatch" for row in rows)
    retained = load(EVIDENCE)["retained_anchors"]
    assert retained and all(row["chain_field_empty"] for row in retained)
    assert all(row["signatures"] == 0 for row in retained)


def test_the_key_half_is_recorded_as_unavailable_with_its_reason():
    key = load(EVIDENCE)["key_half"]
    assert key["status"] == "Unknown"
    assert key["exit_code"] == 3
    assert "ed25519" in key["reason"]
    assert key["record_written"] is False and key["private_seed_written"] is False


def test_one_per_cent_is_off_the_optimum_at_every_declared_conversion():
    reserve = load(EVIDENCE)["reserve_under_measured_cost"]
    assert reserve["one_percent_is_optimal_at_conversions"] == []
    rows = {row["declared_conversion_layer_steps_per_link"]: row for row in reserve["rows"]}
    assert rows[1]["optimal_reserve_steps"] == 127
    assert rows[128]["optimal_reserve_steps"] == 128
    assert all(row["optimal_reserve_steps"] != 10 for row in reserve["rows"])


def test_the_refusals_and_the_recorded_errors_survive():
    evidence = load(EVIDENCE)
    assert len(evidence["refusals"]) == 4
    assert all(row["refused"] is True and row["message"] for row in evidence["refusals"])
    text = NOTE.read_text(encoding="utf-8")
    assert "接不起来" in text
    assert "整数平方根" in text, "the removed float aperture must stay recorded"
    assert "假设错了" in text, "the refuted copy hypothesis must stay recorded"
    assert "ed25519 backend missing" in text


def test_the_note_is_indexed_and_the_claim_exists():
    assert NOTE.exists()
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index
    assert "measured-join-cost" in CLAIMS.read_text(encoding="utf-8")
