"""Bounded pre-registered sweep calibration; external evidence, no admission.

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
HERE = ROOT / "experiments/preregistered_sweep"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0218-a-definability-theorem-and-a-pre-registered-property-sweep.md"
CLAIM_ID = "adva.bounded-experiment.preregistered-sweep.v0"
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


def test_every_fibre_has_three_to_the_free_places():
    s = section("S1_definability")
    assert s["heads"] == 81 and s["praises"] == 729
    assert s["fibres_checked"] == 2 ** 4 * 81 == 1296
    assert s["exhausted_subsets"] == 16
    assert s["theorem"].startswith("a set definable by k places")
    assert s["corollary"].startswith("a set whose size is not divisible by three")


def test_the_minimal_place_counts_and_the_cut_by_arithmetic():
    sets = section("S1_definability")["declared_sets"]
    assert sets["all_heads"] == {"size": 81, "mu": 0}
    assert sets["first_quarter"] == {"size": 27, "mu": 1}
    assert sets["nine_district_representatives"] == {"size": 9, "mu": 2}
    assert sets["three_quarter_representatives"] == {"size": 3, "mu": 3}
    assert sets["cut_before"] == {"size": 47, "mu": 4}
    assert sets["cut_after"] == {"size": 34, "mu": 4}
    assert sets["two_prison_heads"] == {"size": 2, "mu": 4}
    assert sets["one_head_21"] == {"size": 1, "mu": 4}
    # the bound is necessary and not sufficient: two sets of size three differ
    assert sets["orbit_of_seven"] == {"size": 3, "mu": 4}
    top = section("S1_definability")
    assert top["cut_needs_all_four_places_by_arithmetic"] is True
    assert top["the_two_prison_heads_need_all_four_places_by_arithmetic"] is True


def test_the_null_model_is_exact():
    s = section("S2_null")
    assert s["two_heads_float"] == "0.010172"
    assert s["three_heads_float"] == "0.000862"
    assert s["expected_heads_hit_by_nine_praises_float"] == 8.6132
    assert s["expected_heads_hit_by_128_praises_float"] == 66.9006
    assert s["the_null_is_exact_inclusion_exclusion"] is True
    row = s["containment_by_m_heads_at_nine_praises"]
    assert F(row["1"]) > F(row["2"]) > F(row["3"]) > F(row["4"]) > F(row["5"]) > F(row["6"])
    assert F(row["1"]) > F(1, 10) and F(row["3"]) < F(1, 1000)


def test_the_sweep_is_declared_and_the_observed_count_is_explained():
    s = section("S3_sweep")
    assert s["properties"] == 12 and s["head_sets"] == 10 and s["pairs"] == 120
    assert len(s["table"]) == 120
    assert s["observed_containments"] == 34
    assert s["expected_containments_float"] == 8.2883
    assert s["pairs_below_five_percent"] == 95
    assert s["pairs_below_one_percent"] == 90
    assert s["pairs_below_a_tenth_percent"] == 81
    assert s["both_monotonicities_hold"] is True
    # the families are read out of the contract, and the record claims no ordering
    # in which the declarations preceded the counting
    assert s["the_declared_families_are_read_from_the_contract"] is True
    assert s["declared_properties"] == sorted(s["property_sizes"])
    assert s["declared_head_sets"] == ["cut_after", "cut_before", "district_one",
                                       "district_three", "district_two", "first_quarter",
                                       "nine_district_representatives", "second_quarter",
                                       "third_quarter", "three_quarter_representatives"]
    assert s["declarations"]["properties_source"] == (
        "contract.json objects.declared_properties")
    assert s["declarations"]["head_sets_source"] == (
        "contract.json objects.declared_head_sets")
    assert "no earlier timestamped record" in s["declarations"]["ordering"]
    assert "the_sweep_is_declared_before_any_coincidence_is_evaluated" not in s
    # three properties reach every head and carry most of the observed count
    assert s["properties_reaching_every_head"] == ["congruent_one_mod_four",
                                                   "congruent_one_mod_nine",
                                                   "sum_of_two_squares"]
    assert s["containments_contributed_by_those"] == 30
    assert all(v == 81 for k, v in s["heads_hit_by_each_property"].items()
               if k in s["properties_reaching_every_head"])
    assert s["the_uniform_null_under_predicts_for_evenly_spread_properties"] is True


def test_the_post_hoc_entry_and_the_corrected_price():
    s = section("S4_post_hoc")
    assert s["praises"] == [5, 13, 41, 61, 113, 181, 313, 421, 613]
    assert s["selected_heads"] == [1, 2, 5, 7, 13, 21, 35, 47, 69]
    assert s["target"] == [21, 69] and s["contained"] is True
    assert s["p"] == "3133760077447169/308069738356701321"
    assert s["p_float"] == "0.010172"
    assert s["naive_price_first_reported"] == "1/3240"
    assert s["ratio_corrected_over_naive"] == 32.96
    # the coincidence is less unlikely than three quarters of the declared table
    assert s["declared_pairs_at_least_as_unlikely"] == 90
    assert s["declared_pairs_total"] == 120
    assert s["the_first_price_was_wrong_by_a_factor_of_thirty"] is True
    assert s["the_post_hoc_entry_is_not_one_of_the_declared_pairs"] is True


def test_the_same_cycle_relation_is_total_and_therefore_vacuous():
    s = section("S5_vacuity")
    assert s["ordered_pairs_of_distinct_heads"] == 6480
    assert s["pairs_whose_difference_does_not_have_order_dividing_three"] == 0
    assert s["the_same_cycle_relation_is_total"] is True
    assert s["a_total_relation_has_no_discriminating_power"] is True


def test_whether_a_number_is_expressible_depends_on_the_constant_list():
    s = section("S6_coverage")
    assert s["constants"] == [2, 3, 9, 27, 34, 40, 47, 81, 306, 360, 423, 729, 731]
    assert s["image_size_without_one"] == 497 and s["image_size_with_one"] == 518
    assert s["coverage_without_one"] == "497/729"
    assert s["coverage_with_one"] == "518/729"
    assert s["coverage_without_one_float"] == 0.6818
    assert s["coverage_with_one_float"] == 0.7106
    assert s["first_number_expressible_without_one"] is True
    assert s["second_number_expressible_only_with_one"] is True
    assert s["the_count_moved_from_501_to_497_when_that_was_removed"] is True
    assert s["the_criterion_is_about_the_constant_list_not_the_number"] is True


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "declared in this contract and read from it by the checker",
        "it is a declared family of arithmetic predicates",
        "not readings of any text",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0218-a-definability-theorem-and-a-pre-registered-property-sweep.md"
    )
    assert contract["level"].startswith("External exact")
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "was wrong by a factor of thirty-three",
                   "90 of the 120 declared pairs are at least as unlikely"):
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
    assert any("declared table entry" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No text")
