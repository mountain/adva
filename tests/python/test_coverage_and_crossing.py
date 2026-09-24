"""Coverage of a declared expression family, and the crossing count of a shift.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any text, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/coverage_and_crossing"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0220-what-a-declared-family-and-a-declared-shift-already-fix.md"
CLAIM_ID = "adva.bounded-experiment.coverage-and-crossing.v0"
TIMING_KEYS = ("installed_limits",)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def payload(report):
    """The mathematical payload, with timings and platform facts removed."""
    return {
        key: value
        for key, value in report.items()
        if not key.endswith("_ns")
        and not key.startswith("rss_high_water")
        and key not in TIMING_KEYS
    }


def invoke(checker, output, timeout=600):
    return subprocess.run(
        [sys.executable, "-S", str(checker), "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def section(name):
    return load(EVIDENCE)["sections"][name]


def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["status"] == "ExternalExactPass"
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract_sha256"] == digest(CONTRACT)
    assert report["assertions"] <= contract["budget"]["max_assertions"]
    assert report["limits"] == contract["budget"]


def test_fresh_run_reproduces_the_retained_mathematical_payload(tmp_path):
    output = tmp_path / "fresh.json"
    completed = invoke(CHECKER, output)
    assert completed.returncode == 0, completed.stderr
    assert payload(load(output)) == payload(load(EVIDENCE))


def test_an_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(CHECKER, output)
    assert completed.returncode != 0
    assert output.read_text(encoding="utf-8") == "retained"


def test_the_coverage_of_the_declared_constant_sets():
    s = section("S1_coverage")
    rows = s["rows"]
    assert s["kmax"] == 9
    assert len(rows) == 10
    assert rows["the_thirteen_of_0218"]["image_size"] == 497
    assert rows["the_thirteen_of_0218"]["coverage"] == "497/729"
    assert rows["the_thirteen_with_one"]["image_size"] == 518
    assert rows["the_thirteen_with_one"]["coverage"] == "518/729"
    assert rows["the_structural_constants"]["image_size"] == 319
    assert rows["the_prefix_of_forty"]["coverage"] == "400/729"
    assert F(rows["the_thirteen_of_0218"]["coverage"]) > F(2, 3)
    assert F(rows["the_thirteen_of_0218"]["coverage"]) < F(rows["the_thirteen_with_one"]["coverage"])
    # the image is monotone in the constant set by exhaustion, not by assumption
    assert s["image_is_monotone_in_the_constant_set"] is True
    assert s["nested_pairs_exhausted"] == 32
    # every expression a declared set can write is counted, including out of range
    assert rows["the_thirteen_of_0218"]["expression_count"] == 13 + 18 * 13 ** 2
    # the multiplier range is a declared parameter and the coverage follows it
    assert s["kmax"] == 9 and s["kmax_ladder_is_monotone"] is True
    assert s["kmax_ladder"] == {"2": 223, "3": 280, "4": 339, "5": 385, "6": 420,
                                "7": 460, "8": 497, "9": 497, "12": 569, "20": 664}
    assert s["kmax_ladder"]["9"] == rows["the_thirteen_of_0218"]["image_size"]


def test_the_interval_statement_and_the_cost_of_full_coverage():
    s = section("S1_coverage")
    rows = s["rows"]
    assert s["interval_checked_up_to"] == 90
    assert rows["the_prefix_of_nine"]["image_size"] == 90 == 10 * 9
    assert rows["the_prefix_of_eighteen"]["image_size"] == 180 == 10 * 18
    assert rows["the_prefix_of_twenty_seven"]["coverage"] == "10/27"
    assert rows["the_prefix_of_seventy_two"]["image_size"] == 720
    assert F(rows["the_prefix_of_seventy_two"]["coverage"]) == F(80, 81)
    assert rows["the_prefix_of_seventy_three"]["image_size"] == 729
    assert F(rows["the_prefix_of_seventy_three"]["coverage"]) == 1
    assert "10n" in s["interval_theorem"]


def test_the_greedy_and_the_counting_bound_bracket_the_minimum():
    s = section("S1_coverage")
    assert s["greedy_pool"] == [1, 90]
    assert s["greedy_size"] == 14
    assert s["greedy_image_size"] == 729
    assert len(s["greedy_constants"]) == 14
    assert sorted(s["greedy_constants"]) == [1, 12, 26, 63, 65, 67, 70, 73, 75, 76, 80, 83, 86, 88]
    assert s["counting_lower_bound"] == 7
    assert s["counting_lower_bound"] < s["greedy_size"] < 73
    assert s["smallest_covering_set_is_not_decided"] is True


def test_a_target_that_is_a_constant_proves_nothing():
    s = section("S2_target")
    rows = s["rows"]
    assert rows["the_cut_constant"]["target"] == 423
    assert rows["the_cut_constant"]["is_a_declared_constant"] is True
    assert rows["the_cut_constant"]["expressions_naming_it"] == 7
    assert rows["the_cut_constant"]["expressions_naming_it_with_the_cut_constant_removed"] == 5
    assert rows["first_number"] == {
        "target": 421,
        "is_a_declared_constant": False,
        "expressions_naming_it": 3,
        "expressions_naming_it_with_the_cut_constant_removed": 1,
    }
    assert rows["second_number"]["expressions_naming_it"] == 0
    assert s["image_size_with_the_target_as_a_constant"] == 497
    assert s["image_size_once_it_is_not_a_constant"] == 472
    assert F(s["image_size_once_it_is_not_a_constant"], 729) < F(497, 729)
    assert s["the_family_must_exclude_the_target"] is True
    assert s["coverage_is_the_price_of_a_hit"] is True


def test_the_multiplicity_histogram_and_its_monotonicity():
    s = section("S3_multiplicity")
    assert s["praises_reached"] == 497 and s["praises_total"] == 729
    histogram = s["histogram_of_multiplicity"]
    assert sum(histogram.values()) == 497
    assert histogram["1"] == 173
    assert s["largest_multiplicity"] == 15
    assert s["praise_of_largest_multiplicity"] == 54
    assert s["multiplicity_of_423"] == 7
    assert s["multiplicity_of_421"] == 3
    assert s["multiplicity_of_613"] == 0
    assert s["multiplicity_of_613_with_one"] == 1
    assert s["expression_bound"] == 3055
    assert max(int(k) for k in histogram) <= s["expression_bound"]
    assert s["multiplicity_is_monotone_in_the_constant_set"] is True
    assert s["the_price_of_a_hit_is_the_coverage"] is True
    # the price is compared exactly, and the recorded float is never read here
    assert F(s["praises_reached"], s["praises_total"]) == F(497, 729)


def test_the_crossing_count_is_an_identity_of_the_shift():
    s = section("S4_crossing")
    assert s["shift"] == 40 and s["cut"] == 47
    assert s["pairs"] == 41
    assert s["inside_the_first_side"] == 7 == s["cut"] - s["shift"]
    assert s["crossing_the_cut"] == 34
    assert s["the_second_side_has"] == 34 == 81 - s["cut"]
    assert s["inside_the_first_side"] + s["crossing_the_cut"] == s["pairs"]
    assert s["crossing_at_the_other_side_of_the_boundary"] == 33
    # the same identity holds at forty cuts, so forty-seven singles out nothing
    assert s["crossing_equals_the_second_side_at_this_many_cuts"] == 40
    assert s["the_identity_begins_at"] == 41 == 81 - 40
    assert len(s["cuts_where_it_holds"]) == 40
    assert s["cuts_where_it_holds"][0] == 41 and s["cuts_where_it_holds"][-1] == 80
    assert s["switch_point"] == 41
    assert s["closed_form_checked_over"] == 6400
    assert s["closed_form_mismatches"] == 0
    assert s["the_crossing_count_is_an_identity_not_a_finding"] is True


def test_the_shift_is_not_a_constant_vector_in_coordinates():
    s = section("S5_odometer")
    assert s["shift_digits"] == [1, 1, 1, 1]
    assert s["pairs"] == 41
    assert s["pairs_with_a_constant_coordinate_difference"] == 16 == 2 ** 4
    assert s["difference_patterns"]["1111"] == 16
    assert sum(s["difference_patterns"].values()) == 41
    assert sorted(s["difference_patterns"].values()) == [1, 4, 4, 4, 4, 4, 4, 16]
    assert all(pattern.endswith("1") for pattern in s["difference_patterns"])
    assert s["carry_free_count_is_the_product_of_three_minus_the_digits"] is True
    # the figures recorded elsewhere cannot be reproduced from the stated law
    assert s["reported_pair_count"] == 35 and s["reported_pair_count"] != 41
    assert s["reported_constant_difference_count"] == 13
    assert s["reported_constant_difference_count"] != 16
    assert s["the_recorded_pair_count_is_not_the_computed_one"] is True
    assert s["the_coordinate_reading_is_not_a_constant_vector"] is True


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "No list of constants taken from a text is imported",
        "cited as that record's and are neither reproduced nor re-derived here",
        "a declared parameter and not a natural bound",
        "not a probability",
        "not a claim about pairings, oppositions, seasons, calendars",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0220-what-a-declared-family-and-a-declared-shift-already-fix.md"
    )
    assert contract["level"].startswith("External exact")
    objects = contract["objects"]
    assert objects["expected_thirteen_image"] == 497
    assert objects["expected_thirteen_without_the_target_image"] == 472
    assert objects["expected_greedy_size"] == 14
    assert objects["expected_interval_threshold"] == 73
    assert objects["expected_counting_lower_bound"] == 7
    assert objects["expected_shift_pairs"] == 41
    assert objects["expected_inside"] == 7
    assert objects["expected_crossing"] == 34
    assert objects["expected_constant_difference_pairs"] == 16
    assert objects["expected_kmax_ladder"]["20"] == 664
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "the price of a hit is the coverage",
                   "an identity of the shift",
                   "the smallest covering set is not decided",
                   "cannot be reproduced from the stated law"):
        assert phrase in flat, phrase


def test_the_registered_claim_points_at_existing_artifacts():
    import tomllib

    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    matches = [c for c in claims if c["claim_id"] == CLAIM_ID]
    assert len(matches) == 1
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    assert claim["dimension"].startswith("external")
    assert claim["dependencies"] == []
    assert len(claim["forbidden_conflations"]) >= 8
    assert any("coverage" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No classical text")
