"""Bounded six-place interface calibration; external evidence, no admission.

The assertions here are about what the retained checker decided by exhaustion.
They are not claims about any text, and they promote no native identity.
"""

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/six_place_interface"
CHECKER = HERE / "checker.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
NOTE = ROOT / "docs/research/0211-six-places-two-alphabets-and-the-policy-of-a-finite-arithmetic-truth.md"
CLAIM_ID = "adva.bounded-experiment.six-place-interface.v0"
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


def invoke(checker, output, timeout=300):
    return subprocess.run(
        [sys.executable, "-S", str(checker), "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


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


def test_the_two_pairings_generate_a_regular_group_and_not_the_six_cycle():
    section = load(EVIDENCE)["sections"]["S1_pairing_group"]
    assert section["group_order"] == 6
    assert section["element_orders_sorted"] == [1, 2, 2, 2, 3, 3]
    assert section["matchings_are_transversal"] is True
    assert section["union_is_a_single_six_cycle"] is True
    assert section["alternating_walk_one_based"] == [1, 2, 5, 6, 3, 4, 1]
    # the walk is a cycle in the union graph, not an element of the group
    assert section["six_cycle_is_an_element_of_the_group"] is False
    assert section["regular_action_on_six_places"] is True
    assert section["action_is_free"] is True


def test_the_inner_reading_is_linear_with_the_two_outer_places_in_its_kernel():
    section = load(EVIDENCE)["sections"]["S2_operators"]
    assert section["inner_four_reading_is_f2_linear"] is True
    assert section["rank"] == 4 and section["image_size"] == 16
    assert section["kernel_words"] == ["000000", "000001", "100000", "100001"]
    assert section["outer_places_are_invisible"] is True
    assert all(section["commutations"].values())
    # exactly two of the six unit places have a zero image, and they are the outer two
    images = section["image_of_each_unit_place"]
    assert images[0] == "000000" and images[5] == "000000"
    assert sum(1 for w in images if w == "000000") == 2
    assert images[1] == "100000" and images[4] == "000001"


def test_the_eventual_image_is_four_states_split_into_rest_and_one_two_cycle():
    section = load(EVIDENCE)["sections"]["S3_eventual_image"]
    assert section["second_iterate_form"] == "(x3,x4,x3,x4,x3,x4)"
    assert section["second_iterate_rank"] == 2
    assert section["fourth_iterate_equals_second"] is True
    assert section["eventual_image_words"] == ["000000", "010101", "101010", "111111"]
    assert section["fixed_state_words"] == ["000000", "111111"]
    assert section["nontrivial_two_cycle_words"] == ["010101", "101010"]
    assert section["every_periodic_state_lies_in_the_eventual_image"] is True
    assert section["max_steps_to_reach_the_eventual_image"] == 2
    assert section["clock_and_inner_reading_agree_on_the_eventual_image"] is True


def test_the_three_orbit_partitions_are_three_different_partitions():
    section = load(EVIDENCE)["sections"]["S4_orbits"]
    assert section["complement_orbits"] == 32 and section["complement_fixed_states"] == 0
    assert section["reversal_orbits"] == 36 and section["reversal_fixed_states"] == 8
    assert section["two_involutions_commute"] is True
    assert section["two_involutions_composite_fixed_states"] == 8
    assert section["two_involution_group_orbits"] == 20
    assert section["two_involution_group_orbit_size_multiset"] == {"2": 8, "4": 12}
    assert section["generated_group_orbits"] == 16
    assert section["generated_group_orbit_size_multiset"] == {"1": 2, "2": 1, "3": 6, "6": 7}
    assert section["the_two_groups_give_the_same_partition"] is False
    assert section["reversal_is_an_element_of_the_pairing_group"] is False
    # the eight states the inner reading rests on and cycles through
    assert section["states_fixed_by_the_whole_declared_group"] == ["000000", "111111"]
    assert "001100" in section["reversal_fixed_state_words"]


def test_the_ternary_successor_is_the_numeral_successor_with_the_carry_refused():
    section = load(EVIDENCE)["sections"]["S5_ternary_address_interface"]
    assert section["head_count"] == 81 and section["position_count"] == 9
    assert section["address_count"] == 729 and section["address_bijection_checked"] == 729
    assert section["declared_successor_advances"] == 648
    assert section["declared_successor_boundaries"] == 81
    assert section["declared_successor_one_digit_advances"] == 486
    assert section["declared_successor_two_digit_advances"] == 162
    assert section["declared_and_numeral_agree_on"] == section["declared_successor_advances"]
    assert section["numeral_steps_outside_the_declared_domain"] == 81
    assert section["numeral_successor_steps_carrying_into_a_head_place"] == 81
    assert section["declared_states_without_an_address"] == 2


def test_one_step_is_a_different_relation_on_the_two_interfaces():
    section = load(EVIDENCE)["sections"]["S6_step_relations"]
    assert section["binary_directed_single_change_steps"] == 384
    assert section["binary_steps_changing_exactly_one_place"] == 384
    assert section["binary_out_degree_every_state"] == 6
    assert section["binary_states_with_no_successor"] == 0
    assert section["ternary_declared_steps_changing_one_place"] == 486
    assert section["ternary_declared_steps_changing_two_places"] == 162
    assert section["ternary_states_with_no_successor"] == 81
    assert section["binary_numeral_successor_single_place_steps"] == 32


def test_the_two_interfaces_read_each_other_one_way_only():
    section = load(EVIDENCE)["sections"]["S7_cross_reading"]
    assert section["binary_word_embeds_isometrically_onto_the_ternary_zero_one_subcube"] is True
    assert section["embedded_pairs_checked"] == 4096
    assert section["third_digit_values_used_by_the_embedding"] == 0
    # placewise addressability is strictly worse than counting alone
    assert section["placewise_reading_minimum_largest_fibre"] == 64
    assert section["counting_minimum_largest_fibre"] == 12
    assert section["placewise_binary_places_needed"] == 12
    assert section["information_optimal_binary_places_needed"] == 10
    assert section["placewise_cost_in_binary_places"] == 2
    assert section["gcd_of_interface_sizes"] == 1
    assert section["joint_period"] == 46656
    assert section["joint_period_is_six_to_the_sixth"] is True


def test_the_classical_outcome_table_is_reproduced_by_one_declared_policy_only():
    section = load(EVIDENCE)["sections"]["S8_split_arithmetic"]
    classical = {"9": "3/16", "8": "7/16", "7": "5/16", "6": "1/16"}
    assert section["classical_ratios"] == classical
    assert section["outcome_distributions"]["uniform_over_left_pile_residue_classes"] == classical
    for name in ("uniform_over_splits", "independent_stalk_assignment"):
        assert section["outcome_distributions"][name] != classical
        assert any(v != "0" for v in section["difference_from_the_classical_ratios"][name].values())
    # the first classical parameter is attained, the second is not
    assert section["first_strip_is_five_with_the_classical_probability"] == "3/4"
    assert section["first_strip_distributions"]["uniform_over_splits"] == {"5": "3/4", "9": "1/4"}
    assert section["classical_second_strip_parameter_is_attained"] is False
    for pile, row in section["second_strip_parameter_by_reachable_pile"].items():
        assert row["p_of_four"] != "1/2", pile
        assert row["strip_four"] * 2 == row["splits"] + 1, pile


def test_the_remainder_convention_is_separated_by_the_declared_outcome_set():
    section = load(EVIDENCE)["sections"]["S8_split_arithmetic"]["remainder_conventions"]
    assert section["zero_counts_as_four"]["strip_counts"] == {"5": 36, "9": 12}
    assert section["zero_counts_as_zero"]["strip_counts"] == {"1": 12, "5": 36}
    # exactly one convention closes the first strip onto the two declared values
    assert set(section["zero_counts_as_four"]["strip_counts"]) == {"5", "9"}
    assert "9" not in section["zero_counts_as_zero"]["strip_counts"]


def test_the_same_syntax_carries_two_declared_scopes():
    section = load(EVIDENCE)["sections"]["S9_declared_encoding"]
    assert section["contracts"] == 512 and section["occupancy_masks_exhausted"] == 255
    assert section["valid_forms_boolean"] == {"1": 4, "2": 4, "3": 4, "4": 3}
    assert section["valid_forms_terms_nonempty"] == {"1": 6, "2": 6, "3": 6, "4": 6}
    assert section["forms_gained_by_the_weaker_scope"] == {"1": 2, "2": 2, "3": 2, "4": 3}
    assert section["same_syntax_two_declared_scopes"] is True
    assert section["countermodel_examples"]


def test_the_contract_states_its_protected_boundaries():
    contract = load(CONTRACT)
    protected = " ".join(contract["protected"])
    for phrase in (
        "classical text",
        "truth value",
        "six Adva primitive words",
        "No floating-point value",
        "No native Rust witness",
    ):
        assert phrase in protected, phrase
    assert contract["input_document"] == (
        "docs/research/0211-six-places-two-alphabets-and-the-policy-of-a-finite-arithmetic-truth.md"
    )
    assert contract["level"].startswith("External exact")
    assert NOTE.is_file()


def test_the_note_keeps_its_residual_and_does_not_identify_a_text():
    text = NOTE.read_text(encoding="utf-8")
    assert "Not established" in text or "not established" in text
    for phrase in ("does not", "no text", "residual"):
        assert phrase in text.lower(), phrase


def test_the_registered_claim_points_at_existing_artifacts():
    import tomllib

    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    matches = [c for c in claims if c["claim_id"] == CLAIM_ID]
    assert len(matches) == 1
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    assert claim["dimension"].startswith("external")
    assert claim["dependencies"] == []
    assert len(claim["forbidden_conflations"]) >= 10
    assert any("outcome table" in item for item in claim["forbidden_conflations"])
    for symbol in claim["code_symbol"].split("; "):
        assert (ROOT / symbol).is_file(), symbol
    assert claim["counterexample_boundary"].startswith("No text, edition")
