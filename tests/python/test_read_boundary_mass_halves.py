"""The read boundary halves, and what a shared allowance does to them.

Research 0191 recomputes the retained wrapper family's layer masses exactly, separates the
resolved-against-remaining partition from the first-bit one, and shows that the equal split
of a shared allowance leaves one half resolved only at the small totals. The tempting
repairs here are the quiet ones: let a zero share resolve the first layer for free, quote a
half instead of computing it, or merge the two partitions because their numbers agree.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments/read_boundary_mass_halves"
EVIDENCE = EXPERIMENT / "evidence.json"
NOTE = ROOT / "docs/research/0191-the-read-boundary-splits-the-mass-in-half.md"
CLAIMS = ROOT / "docs/claims.toml"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def replay(tmp_path):
    completed = subprocess.run([sys.executable, str(EXPERIMENT / "calibration.py"),
                                str(tmp_path / "fresh.json")],
                               cwd=ROOT, capture_output=True, text=True, timeout=300,
                               check=False)
    assert completed.returncode == 0, completed.stderr
    return load(tmp_path / "fresh.json")


def strip_host_quantities(evidence):
    """Remove the one declared host quantity, and only that one.

    The elapsed wall time is a host measurement rather than a result, so it is the single
    field excluded from the byte-for-byte comparison; everything the run decides stays in.
    """
    copy = json.loads(json.dumps(evidence))
    counts = copy["counts"]
    excluded = counts.pop("wall_seconds_before_serialization")
    assert isinstance(excluded, float)
    return copy


def test_a_fresh_run_reproduces_the_retained_evidence(tmp_path):
    fresh, retained = replay(tmp_path), load(EVIDENCE)
    assert strip_host_quantities(fresh) == strip_host_quantities(retained)
    assert fresh["counts"]["assertions"] == retained["counts"]["assertions"]


def test_the_layer_and_tail_masses_are_recomputed_not_quoted():
    evidence = load(EVIDENCE)
    assert evidence["wrapper_family"]["code_length"] == "2|w| + 1"
    assert evidence["wrapper_family"]["prefix_free_on_the_declared_family"] is True
    for row in evidence["layers"]:
        depth = row["depth"]
        assert row["layer_mass"] == str(__import__("fractions").Fraction(1, 2 ** (depth + 1)))
        assert row["code_length"] == 2 * depth + 1
        assert row["words"] == 2 ** depth


def test_the_two_halves_hold_at_the_first_boundary_and_nowhere_deeper():
    splits = load(EVIDENCE)["splits"]
    holding = [row["depth_cut"] for row in splits if row["both_halves"]]
    assert holding == [0], holding
    assert splits[0]["resolved"] == "1/2" and splits[0]["remaining"] == "1/2"


def test_the_two_partitions_carry_the_same_numbers_and_stay_distinct():
    partitions = load(EVIDENCE)["partitions"]
    assert len(partitions) == 2
    assert all(row["masses"] == ["1/2", "1/2"] for row in partitions)
    assert partitions[0]["what_the_halves_are"] != partitions[1]["what_the_halves_are"]
    assert partitions[0]["holds_halves_beyond_the_first_boundary"] is False
    assert partitions[1]["holds_halves_beyond_the_first_boundary"] is True


def test_the_equal_split_leaves_both_halves_only_at_the_shallow_totals():
    evidence = load(EVIDENCE)
    assert evidence["equal_split_totals_that_leave_both_halves"] == [2, 4]
    rows = {row["total_allowance"]: row for row in evidence["allocations"]}
    assert rows[2]["equal_split_resolved"] == "1/2"
    assert rows[4]["equal_split_resolved"] == "1/2"
    assert rows[4]["best_resolved"] == "5/8"
    assert rows[4]["worst_resolved"] == "3/8"
    # the equal split is neither the best nor the worst, so it is a fairness value
    assert rows[4]["the_equal_split_is_the_best"] is False
    assert rows[4]["the_equal_split_is_the_worst"] is False
    # the one-step allowance cannot be allocated at all, and the row is kept
    assert rows[1]["allocation_matters"] is False
    assert rows[1]["degenerate_one_step_allowance"] is True


def test_a_zero_share_resolves_nothing():
    """Returning the first layer for a zero share would hand out mass for free."""
    evidence = load(EVIDENCE)
    rows = {row["total_allowance"]: row for row in evidence["allocations"]}
    # the worst split of two steps puts everything on one branch and resolves one quarter
    assert rows[2]["worst_resolved"] == "1/4"


def test_the_quotient_defect_is_exactly_the_erased_cylinder():
    hazard = load(EVIDENCE)["multiplicity_hazard"]
    assert hazard["two_codes"] == ["100", "101"]
    assert hazard["each_mass"] == "1/8"
    assert hazard["counting_one_representative"] == "1/8"
    assert hazard["pushing_weights_with_multiplicity"] == "1/4"
    assert hazard["defect_of_the_quotient"] == "1/8"
    assert hazard["defect_equals_the_erased_cylinder"] is True
    assert "linear combination" in hazard["status"]


def test_the_refusal_controls_are_recorded():
    refusals = load(EVIDENCE)["refusals"]
    assert len(refusals) == 3
    assert all(row["refused"] is True and row["message"] for row in refusals)


def test_the_direction_hypothesis_is_recorded_verbatim_and_the_claim_exists():
    evidence = load(EVIDENCE)
    hypothesis = evidence["the_direction_hypothesis"]
    assert "0.5 和 0.5" in hypothesis
    assert "杨路" in hypothesis
    assert "Q_4" in hypothesis
    assert "read-boundary-mass-halves" in CLAIMS.read_text(encoding="utf-8")
    assert NOTE.exists()
    text = NOTE.read_text(encoding="utf-8")
    assert "杨路论文和 Q_4 结合的时候" in text, "the hypothesis must appear in the note too"
    assert "锥证书在这件问题上没有位置" in text, "the scope statement must survive"
    index = (ROOT / "docs/research/README.md").read_text(encoding="utf-8")
    assert NOTE.name in index and "0191" in index
