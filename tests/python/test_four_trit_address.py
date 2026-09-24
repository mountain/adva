"""Bounded four-trit address calibration; external evidence, no admission.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any text, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/four_trit_address"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0214-what-a-four-trit-address-carries-and-no-shift-pairs-it.md"
CLAIM_ID = "adva.bounded-experiment.four-trit-address.v0"
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


def test_no_nonzero_shift_of_the_ternary_address_is_a_pairing():
    s = section("S1_no_shift_is_a_pairing")
    assert s["heads"] == 81 and s["nonzero_shifts"] == 80
    assert s["ternary_shift_orders"] == {"1": 1, "3": 80}
    assert s["shifts_of_order_at_most_two"] == 1
    assert s["no_nontrivial_ternary_shift_is_an_involution"] is True
    assert s["orbits_per_nonzero_ternary_shift"] == 27
    assert s["orbit_size_per_nonzero_ternary_shift"] == 3
    # the binary interface is the exact opposite case
    assert s["binary_shift_orders"] == {"1": 1, "2": 63}
    assert s["every_binary_shift_is_an_involution"] is True
    for v in s["dominant_differences"].values():
        assert sum(v) % 3 != 0 or v != [0, 0, 0, 0]
    assert s["dominant_differences_have_order"] == 3


def test_a_pairing_of_eighty_one_heads_is_bounded_and_leaves_a_fixed_point():
    s = section("S1_no_shift_is_a_pairing")
    assert s["pairing_bound"] == 40
    assert s["fixed_points_of_any_pairing_of_eighty_one"].startswith("odd")
    counts = s["reported_pair_counts"]
    assert counts == {"cross_sentence": 69, "sentence_internal": 35,
                      "section_seven_resolving": 126, "section_seven_consecutive": 131,
                      "deduplicated": 133}
    assert sum(1 for v in counts.values() if v > s["pairing_bound"]) == 4
    assert s["reported_counts_above_the_bound"] == 4
    assert counts["sentence_internal"] <= s["pairing_bound"]


def test_the_capacity_bounds_in_both_directions():
    s = section("S2_capacity")
    assert s["binary_words"] == 64 and s["heads"] == 81
    assert s["counting_minimum_largest_fibre"] == 2
    assert s["placewise_minimum_largest_fibre"] == 4
    assert s["placewise_minimum_largest_fibre_dropping_a_place"] == 3
    assert s["placewise_cost_over_counting"] == "2"
    assert s["placewise_allocation_attaining_the_bound"] == [2, 2, 1, 1]
    assert s["coordinate_wise_largest_image"] == 36
    assert s["coordinate_wise_largest_image_share"] == "9/16"
    assert s["one_bit_per_place_image"] == 16
    assert s["information_optimal_binary_places_needed"] == 7
    assert s["placewise_binary_places_needed"] == 8
    assert s["unconstrained_injection_exists"] is True
    assert s["the_declared_injection_is_coordinate_wise"] is False
    # six places carry all sixty-four, four carry sixteen placewise
    assert s["six_ternary_places_carry_all_sixty_four"] is True
    assert s["four_ternary_places_carry_placewise"] == 16


def test_the_carry_profile_of_a_coordinate_order():
    s = section("S3_odometer")
    assert s["ternary_carry_profile"] == {"1": 54, "2": 18, "3": 6, "4": 3}
    assert s["ternary_single_place_share"] == "2/3"
    assert s["binary_carry_profile"] == {"1": 32, "2": 16, "3": 8, "4": 4, "5": 2, "6": 2}
    assert s["binary_single_place_share"] == "1/2"
    assert s["closed_forms_match_the_exhaustion"] is True
    assert s["single_place_shares"] == {"binding_single_change_relation": "1",
                                        "binary_odometer": "1/2",
                                        "ternary_head_odometer": "2/3",
                                        "position_successor": "3/4"}
    assert s["distinct_single_place_shares"] == 4


def test_a_similarity_measure_cannot_test_an_opposition():
    s = section("S4_opposition")
    assert s["extracted_pairs"] == 126 and s["heads"] == 81
    assert s["mean_percentile"] == "221/500"
    assert s["deviation"] == "29/500"
    assert s["expected_mean_percentile_under_exchangeability"] == "1/2"
    assert s["percentile_convention"].startswith("a rank r out of n")
    assert s["independent_pair_variance_of_the_mean_percentile"] == "1/1512"
    assert s["deviation_in_independent_pair_standard_errors_squared"] == "158949/31250"
    assert s["average_appearances_per_head"] == "28/9"
    assert s["pairs_are_not_disjoint"] is True
    assert s["the_declared_similarity_measure_does_not_separate_the_declared_opposite_and_unrelated_pairs"] is True


def test_the_counting_unit_decides_what_is_visible():
    s = section("S5_counting_unit")
    assert s["documents_declared"] == [{"section_titles": 12, "passages": 60, "restatements": 0},
                                       {"section_titles": 0, "passages": 60, "restatements": 12}]
    assert s["passage_level_counts"] == [0, 12]
    assert s["the_count_is_independent_of_the_title_level_structure"] is True
    assert s["ranking_work_passage_level_share"] == "1/15"
    assert s["reported"]["poetry_grades"]["passage_level_hits"] == 4


def test_a_one_role_frame_costs_no_labels():
    s = section("S6_role_orders")
    assert s["role_orderings_by_role_count"] == {"1": 1, "2": 2, "3": 6, "4": 24}
    assert s["a_one_role_frame_has"] == 1
    assert s["the_single_role_frame_is_pinned_by_arity"] is True
    assert s["declared_role_counts"]["naming"] == 1
    assert s["declared_role_counts"]["declared_label_budget"] == 32
    assert s["declared_role_counts"]["reported_speech_frames"] == 8


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "no corpus count from any external repository is imported",
        "what is established is that a pairing cannot be a coordinate shift",
        "fingerprint a collated order could be tested against",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0214-what-a-four-trit-address-carries-and-no-shift-pairs-it.md"
    )
    assert contract["level"].startswith("External exact")
    assert NOTE.is_file()


def test_the_note_states_the_residual_and_imports_no_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Residual" in text
    flat = " ".join(text.split()).lower()
    for phrase in ("no text and no corpus count is imported",
                   "wenyan-relation-learning",
                   "what is ruled out is a pairing by coordinate shift only"):
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
    assert any("involution" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No text")
