"""The paired test for the three-cycle supplement v2 rounded-ending calibration.

The assertions here are about what the retained checker decided by exact arithmetic on one
declared construction: the rounded ending 圆融 as a conjunction of two terminal conditions with
their residual records kept separate, the Yi pair used only as the contrast family over the
existing 81/6480 address machinery, the beginning split into resetable obstructions and a
non-resetable commitment, the five-point double cycle, the three astronomical remainders, the
declared reading that three is neither a degree nor a failure of injectivity, the one-way
commitment reservoir against the parent chain's declared first-order relaxation, the refusal of
sealing for the committed component, the four-by-two classification with three declarations, the
fourth uncertainty term, the inherited controls and the exact baselines.

They are not claims about any physical object, and no magnitude is asserted for aerosols, low
cloud, water vapour, wildfire or the committed component anywhere in the retained payload; the
test checks that absence as well.

The checker is invoked without `-S` because its declared external library (sympy) must be
importable; the run remains an external exact calibration either way.

The record carries no claim for this run: the parent session adds the claim to
`docs/claims.toml` with its note, so the last test asserts the claim is ABSENT rather than
dropping the binding.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from fractions import Fraction
from itertools import pairwise
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/three_cycle_supplement_v2"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
PARENT_DIR = ROOT / "experiments/three_cycle_chain_v1"
PARENT_CONTRACT = PARENT_DIR / "contract.json"
PARENT_SUPPLEMENT = PARENT_DIR / "contract-supplement-1.json"
SURGERY_CONTRACT = ROOT / "experiments/three_cycle_supplement_v1/contract.json"

CLAIM_ID = "adva.bounded-experiment.three-cycle-supplement.v2"
DECLARED_CONTRACT_SHA256 = \
    "823eedfaa492d0524c901793b580d5f02b67d7cf739f26781e326aa667d1e990"
DECLARED_PARENT_SHA256 = \
    "a3dc2e8d86e45139484fceed571ef99ea3b63f18748c6f1c82bb031a3305a965"
DECLARED_SUPPLEMENT_SHA256 = \
    "e125ee4940b838924257d9420bde71cf060a0745dc5d3d482c1691158785ac9f"
DECLARED_SURGERY_SHA256 = \
    "157838642e9097ea4a1a1c7461db9e548affb0c6f3af7b830816f37f22b74f5a"
CLOSURE_CUBIC = "h^3 + 8 h^2 + 64 h - 320 = 0"
NO_MAGNITUDE = "none_declared"

SECTION_NAMES = (
    "R1_rounded_ending", "R2_yi_contrast_family", "R3_beginning_split", "R4_middle_five",
    "R5_astronomical_remainders", "R6_three_is_not_a_degree", "R7_commitment_reservoir",
    "R8_sealing_refused", "R9_factor_classification", "R10_uncertainty_fourth_term",
    "R11_inherited_controls", "R12_baselines",
)

TOP_LEVEL_KEYS = (
    "assertions", "checker_sha256", "checks", "contract", "contract_sha256",
    "contract_sha256_declared", "level", "limits", "modelling_choices", "parent_contracts",
    "protected", "residual", "schema", "sections", "status", "tooling", "undecided",
    "verification_status", "version", "what_is_not_claimed",
)

FROZEN_SECTION_SHAPE = {
    "R1_rounded_ending": [
        "committed_component", "conjunction", "declared_ending", "no_fused_residual_is_formed",
        "prohibitions", "prohibitions_rejected", "residual_records", "sealable_component",
        "terminal_conditions", "the_ending_is_a_declared_convention"],
    "R2_yi_contrast_family": [
        "address_machinery", "all_three_contrast_terminals_fail", "contrast_terminals",
        "declared_reading", "no_terminal_reading_is_taken_from_the_yi_pair",
        "the_two_sides_are_not_identified"],
    "R3_beginning_split": [
        "accepted_resets", "classes", "controls", "declared_split",
        "no_reset_clears_the_commitment", "rejected_resets", "resets",
        "the_split_is_a_declared_convention"],
    "R4_middle_five": [
        "both_cycle_rejections_fail", "controls", "declared_cycles",
        "declared_five_point_structure", "declared_structure", "every_nonzero_step_is_a_generator",
        "five_is_prime", "generators_modulo_five", "number_of_generators",
        "overcoming_is_generation_applied_twice", "points", "points_where_they_differ",
        "the_two_cycles_are_distinct_maps", "why_the_primality_matters"],
    "R5_astronomical_remainders": [
        "closing_claim_controls", "commensurabilities", "declared_chain", "exact_identities",
        "failed_to_discriminate", "remainders", "the_chain_closes_none",
        "the_chain_closes_none_statement"],
    "R6_three_is_not_a_degree": [
        "declared_reading", "identifications_rejected", "injectivity",
        "no_spherical_carrier_is_declared", "numerical_coincidence_recorded_not_used", "readings",
        "the_three"],
    "R7_commitment_reservoir": [
        "component", "controls", "declared_increments", "declared_loop", "declared_loop_controls",
        "declared_model", "declared_thresholds", "hysteresis", "magnitude",
        "monotone_non_decreasing", "parent_relaxation_failure",
        "reservoir_state_is_a_declared_convention", "strictly_increasing",
        "the_loop_does_not_restore_the_state", "the_one_way_shape_does_work",
        "why_the_state_is_not_a_magnitude"],
    "R8_sealing_refused": [
        "committed_component", "controls", "declared_reading", "layer_wise_violation",
        "no_magnitude_for_the_committed_component", "sealable_component",
        "the_leak_is_declared_and_not_repaired"],
    "R9_factor_classification": [
        "account_sizes", "accounts", "accounts_are_separate", "cell_records", "cells", "controls",
        "declarations", "declared_asymmetry", "declared_basis", "declared_placement",
        "declared_reading", "declared_verdict", "magnitude_audit",
        "no_magnitude_is_given_for_any_factor"],
    "R10_uncertainty_fourth_term": [
        "declared_terms", "four_terms_separately_at_every_seam", "fourth_term", "fused_control",
        "fused_three_term_figure", "no_magnitude_for_the_fourth_term", "pooling_control",
        "quantified_terms", "seams", "term_count"],
    "R11_inherited_controls": [
        "atmospheric_memory_loss", "carried_forward_failures", "carried_forward_failures_count",
        "controls_that_did_discriminate", "failed_controls", "identity_loop",
        "inherited_controls_still_run", "layer_wise_sealing", "sampling_change_invariance",
        "separated_uncertainty"],
    "R12_baselines": ["closure_reading", "first_scheme", "level_reading", "ordering"],
}

DECLARED_CELLS = {
    ("aerosols", "north"): "structure_to_be_preserved",
    ("aerosols", "south"): "explicitly_unquantified",
    ("low_cloud", "north"): "explicitly_unquantified",
    ("low_cloud", "south"): "structure_to_be_preserved",
    ("water_vapour", "north"): "explicitly_unquantified",
    ("water_vapour", "south"): "correction_to_be_made",
    ("wildfire", "north"): "explicitly_unquantified",
    ("wildfire", "south"): "explicitly_unquantified",
}

FORBIDDEN_MAGNITUDE_KEYS = ("value", "amount", "rate", "flux", "forcing", "sign", "timing",
                            "anomaly", "tendency", "sensitivity", "trend", "magnitude_value")


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    """Load JSON and refuse any floating-point literal in it."""
    def no_float(text):
        raise AssertionError(f"a floating-point literal is present: {text}")

    return json.loads(Path(path).read_text(encoding="utf-8"), parse_float=no_float)


def invoke(checker, output, timeout=900):
    return subprocess.run(
        [sys.executable, str(checker), "--output", str(output)],
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
    )


def section(name):
    return load(EVIDENCE)["sections"][name]


def numeric_leaves(node, path="", found=None):
    """Every int or Fraction leaf under a record, ignoring booleans."""
    if found is None:
        found = []
    if isinstance(node, bool):
        return found
    if isinstance(node, dict):
        for key, value in node.items():
            if key in FORBIDDEN_MAGNITUDE_KEYS:
                found.append(path + "/" + str(key))
            numeric_leaves(value, path + "/" + str(key), found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            numeric_leaves(item, path + "/" + str(index), found)
    elif isinstance(node, (int, float)):
        found.append(path + " = " + str(node))
    return found


def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["status"] == "ExternalExactPass"
    assert report["schema"] == "adva.external.three-cycle-supplement-rounded-calibration.v2"
    assert report["version"] == 2
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract_sha256"] == digest(CONTRACT) == DECLARED_CONTRACT_SHA256
    assert report["contract_sha256_declared"] == DECLARED_CONTRACT_SHA256
    assert report["contract"] == "experiments/three_cycle_supplement_v2/contract.json"
    assert report["assertions"] <= contract["budgets"]["max_assertions"]
    assert report["assertions"] > 200
    assert report["limits"] == contract["budgets"]
    assert all(report["checks"].values())
    assert contract["budgets"]["child_processes"] == 0
    assert "RLIMIT_AS" not in CHECKER.read_text(encoding="utf-8")
    parents = {row["path"]: row for row in report["parent_contracts"]}
    assert len(parents) == 3
    assert parents["experiments/three_cycle_chain_v1/contract.json"]["sha256"] \
        == digest(PARENT_CONTRACT) == DECLARED_PARENT_SHA256
    assert parents["experiments/three_cycle_chain_v1/contract-supplement-1.json"]["sha256"] \
        == digest(PARENT_SUPPLEMENT) == DECLARED_SUPPLEMENT_SHA256
    assert parents["experiments/three_cycle_supplement_v1/contract.json"]["sha256"] \
        == digest(SURGERY_CONTRACT) == DECLARED_SURGERY_SHA256
    assert all(row["retained_byte_for_byte"] for row in report["parent_contracts"])
    assert report["tooling"]["polynomial_library"] == "sympy"
    assert report["tooling"]["version"].startswith("1.14")
    assert report["tooling"]["declared_not_native_authority"] is True
    assert report["tooling"]["exact_only"] is True
    assert report["tooling"]["not_implemented"]


def test_a_copied_checkout_reproduces_the_retained_payload(tmp_path):
    """The checker is re-run on a COPY: the payload must not depend on its location."""
    copied = tmp_path / "experiments"
    (copied / "three_cycle_supplement_v2").mkdir(parents=True)
    (copied / "three_cycle_chain_v1").mkdir()
    (copied / "three_cycle_supplement_v1").mkdir()
    shutil.copy(CHECKER, copied / "three_cycle_supplement_v2/calibration.py")
    shutil.copy(CONTRACT, copied / "three_cycle_supplement_v2/contract.json")
    shutil.copy(PARENT_CONTRACT, copied / "three_cycle_chain_v1/contract.json")
    shutil.copy(PARENT_SUPPLEMENT, copied / "three_cycle_chain_v1/contract-supplement-1.json")
    shutil.copy(SURGERY_CONTRACT, copied / "three_cycle_supplement_v1/contract.json")
    output = tmp_path / "on-a-copy.json"
    completed = invoke(copied / "three_cycle_supplement_v2/calibration.py", output)
    assert completed.returncode == 0, completed.stderr
    fresh = load(output)
    retained = load(EVIDENCE)
    assert fresh["status"] == retained["status"]
    assert fresh["assertions"] == retained["assertions"]
    assert fresh["sections"] == retained["sections"]
    assert fresh["checks"] == retained["checks"]
    assert fresh["undecided"] == retained["undecided"]
    assert fresh["what_is_not_claimed"] == retained["what_is_not_claimed"]
    assert digest(output) == digest(EVIDENCE)


def test_two_fresh_runs_are_byte_identical(tmp_path):
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    assert invoke(CHECKER, first).returncode == 0
    assert invoke(CHECKER, second).returncode == 0
    assert digest(first) == digest(second) == digest(EVIDENCE)


def test_an_existing_output_is_never_overwritten(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("retained", encoding="utf-8")
    completed = invoke(CHECKER, output)
    assert completed.returncode != 0
    assert output.read_text(encoding="utf-8") == "retained"
    assert "refusing to overwrite" in completed.stdout


def test_the_payload_is_free_of_floating_point_literals():
    text = EVIDENCE.read_text(encoding="utf-8")
    assert load(EVIDENCE)
    assert "NaN" not in text and "Infinity" not in text
    assert "/Users/" not in text and "mingli" not in text
    report = load(EVIDENCE)
    assert report["checks"]["no_floating_point_value_is_retained"] is True
    assert report["checks"]["no_magnitude_key_carries_anything_but_the_declared_none"] is True


def test_the_frozen_shape_of_every_section():
    report = load(EVIDENCE)
    assert sorted(report) == sorted(TOP_LEVEL_KEYS)
    assert sorted(report["sections"]) == sorted(SECTION_NAMES)
    for name, keys in FROZEN_SECTION_SHAPE.items():
        assert sorted(report["sections"][name]) == keys, name
    ending = section("R1_rounded_ending")
    assert sorted(ending["sealable_component"]) == [
        "annual_return", "closure_identity", "declared", "displaced_state_control",
        "fixed_point_identification", "residual_record"]
    assert sorted(ending["committed_component"]) == [
        "carry_out", "carry_out_condition", "controls", "declared", "declared_positions",
        "position_count", "residual_record", "written_record"]
    assert sorted(ending["residual_records"]) == [
        "components", "count", "fused_scalar_exists", "kept_separate", "reading"]
    assert sorted(ending["prohibitions"]) == ["compromise", "either_or", "netting", "obstruction"]
    assert sorted(ending["conjunction"]) == [
        "accepted", "both_hold_in_full", "committed_holds", "reasons", "sealable_holds",
        "terminal", "verdict"]
    assert sorted(section("R2_yi_contrast_family")["contrast_terminals"][0]) == [
        "accepted", "rejected_by", "rejection_reasons", "terminal", "verdict"]
    assert sorted(section("R3_beginning_split")["resets"]["phase_misalignment"]) == [
        "accepted", "cleared_exactly", "declared_class", "obstruction", "reading", "reasons",
        "rejected_by", "residual_written_out", "state_after", "state_before", "verdict"]
    five = section("R4_middle_five")
    assert sorted(five["declared_cycles"]) == ["generation", "overcoming"]
    for row in five["declared_cycles"].values():
        assert sorted(row) == ["is_a_generator", "is_a_single_five_cycle", "orbit", "order",
                              "step"]
    assert sorted(section("R5_astronomical_remainders")["commensurabilities"][0]) == [
        "chain_cycles_needed", "chain_days", "closes_it", "commensurability", "days",
        "exact_multiple_of_the_chain_length", "remainder"]
    assert sorted(section("R6_three_is_not_a_degree")["injectivity"]) == [
        "collisions", "declared_images", "declared_index_set", "is_a_collapse", "is_injective",
        "unordered_index_pairs"]
    reservoir = section("R7_commitment_reservoir")
    assert sorted(reservoir["declared_loop"][0]) == [
        "branch_state", "control_value", "declared_increment", "increment", "position",
        "state_after", "state_before"]
    assert sorted(reservoir["hysteresis"]) == [
        "declared_probe_control", "paths_differ", "present", "reading", "refreeze_path",
        "thaw_path"]
    assert sorted(reservoir["parent_relaxation_failure"]) == [
        "branch_state_declared", "control", "declared_branch_reading", "declared_displacement",
        "declared_form", "declared_steps", "hysteresis_control", "hysteresis_present",
        "monotone_non_decreasing", "monotonicity_control", "reading", "relaxation_coefficient",
        "threshold_declared", "time_constant", "verdict"]
    assert sorted(section("R8_sealing_refused")["committed_component"]) == [
        "accounted", "declared_magnitude", "reading", "reasons", "sealed", "sealing_refused",
        "verdict"]
    classification = section("R9_factor_classification")
    structured = [row for row in classification["cell_records"]
                  if row["declaration"] == "structure_to_be_preserved"]
    corrected = [row for row in classification["cell_records"]
                 if row["declaration"] == "correction_to_be_made"]
    unquantified = [row for row in classification["cell_records"]
                    if row["declaration"] == "explicitly_unquantified"]
    common = ["declaration", "declared_basis", "factor", "magnitude", "magnitude_is_not_asserted",
              "ratchet", "reversible", "side"]
    for row in structured:
        assert sorted(row) == sorted([*common, "preserved_structure"])
    for row in corrected:
        assert sorted(row) == sorted([*common, "correction"])
    for row in unquantified:
        assert sorted(row) == sorted([*common, "recorded_separately"])
    assert sorted(classification["declared_verdict"]) == [
        "accepted", "cells_covered", "decided_by_a_count", "reasons", "rejected_by", "verdict"]
    uncertainty = section("R10_uncertainty_fourth_term")
    assert sorted(uncertainty["seams"][0]) == [
        "bias", "committed_but_unquantified", "cycle", "mapping", "recorded_separately",
        "sampling", "terms_recorded"]
    assert sorted(uncertainty["fourth_term"]) == [
        "magnitude", "name", "never_fused", "quantified", "recorded_separately_at_every_seam"]
    controls = section("R11_inherited_controls")
    assert sorted(controls["sampling_change_invariance"]) == [
        "composition_only_difference", "composition_only_reading_moves", "control",
        "declared_compositions", "fused_reading", "not_read_as_a_change_of_mechanism",
        "readings", "readings_unchanged", "the_composition_only_reading_is_an_artefact"]
    assert sorted(controls["identity_loop"]) == [
        "control", "control_loop", "declared_loop", "discriminates", "five_point_identity"]
    baselines = section("R12_baselines")
    assert sorted(baselines["first_scheme"]) == [
        "amplitude_floor", "attained_at", "branches",
        "discriminant_of_the_specialised_quartic", "frozen_level_of_the_ten_middle_sides",
        "leading_coefficient_of_the_specialised_quartic", "on_the_discriminant_variety",
        "real_branches_at_the_witness", "source"]
    for row in baselines["first_scheme"]["branches"]:
        assert sorted(row) == ["abs_E_0_upper_bound", "abs_h_upper_bound",
                              "below_the_frozen_level", "isolation_interval",
                              "refined_interval"]
    assert sorted(baselines["closure_reading"]) == [
        "amplitude", "correctly_rounded_prefix", "derivative_discriminant", "isolation_interval",
        "no_rational_root", "nontrivial_branch_equation",
        "quotient_quadratic_discriminant_enclosure", "real_exits",
        "the_other_two_exits_are_non_real"]
    assert sorted(baselines["level_reading"]) == [
        "closed_form", "closed_form_verified_in", "equation", "largest_branch_amplitude",
        "largest_branch_amplitude_enclosure", "negative_branch_enclosure",
        "positive_branch_enclosure", "real_branches", "sigma", "sigma_is_positive",
        "substitution"]
    assert sorted(baselines["ordering"]) == [
        "asserted_exactly", "between", "decided_on_exact_rationals", "rational_witnesses",
        "statement"]


def test_the_rounded_ending_is_a_conjunction_with_two_separate_residual_records():
    ending = section("R1_rounded_ending")
    assert ending["terminal_conditions"] == 2
    sealable = ending["sealable_component"]
    assert sealable["residual_record"]["residual"] == ["0", "0", "0"]
    assert sealable["residual_record"]["holds_exactly"] is True
    assert sealable["residual_record"]["quantified"] is True
    identification = sealable["fixed_point_identification"]
    assert identification["cubic"] == CLOSURE_CUBIC
    assert identification["derivative"] == "3 h^2 + 16 h + 64"
    assert identification["derivative_discriminant"] == "-512"
    assert identification["value_at_three"] == ["-29", "0", "0"]
    assert identification["value_at_four"] == ["128", "0", "0"]
    assert identification["real_root_count"] == 1
    assert identification["the_declared_element_is_a_root"] is True
    assert identification["the_declared_element_is_that_root"] is True
    assert identification["declared_bracket"] == ["3", "4"]
    assert "512 (E(h) - h)" in sealable["closure_identity"]
    displaced = sealable["displaced_state_control"]
    assert displaced["closes"] is False
    assert displaced["verdict"] == "Rejected_DoesNotClose"
    assert any(Fraction(value) != 0 for value in displaced["displaced_residual"])

    committed = ending["committed_component"]
    assert committed["declared_positions"] == ["C1", "C2", "C3", "exit"]
    assert committed["position_count"] == 4
    assert committed["carry_out"]["verdict"] == "CarriedOutAndWrittenOut"
    assert committed["carry_out"]["written"] is True
    assert committed["carry_out"]["discharged"] is False
    assert committed["written_record"]["magnitude"] == NO_MAGNITUDE
    assert committed["written_record"]["discharged"] is False
    assert committed["residual_record"]["quantified"] is False
    assert committed["residual_record"]["magnitude"] == NO_MAGNITUDE
    assert len(committed["controls"]) == 4
    assert all(row["verdict"] == "Rejected" for row in committed["controls"])
    assert all(row["rejected_by_the_declared_condition"] is True for row in committed["controls"])

    records = ending["residual_records"]
    assert records["count"] == 2
    assert records["components"] == ["sealable", "committed"]
    assert records["kept_separate"] is True
    assert records["fused_scalar_exists"] is False
    assert ending["no_fused_residual_is_formed"] is True
    conjunction = ending["conjunction"]
    assert conjunction["verdict"] == "RoundedEndingHolds"
    assert conjunction["accepted"] is True
    assert conjunction["both_hold_in_full"] is True
    assert conjunction["sealable_holds"] is True and conjunction["committed_holds"] is True
    assert conjunction["reasons"] == []
    assert ending["prohibitions_rejected"] == 4


def test_the_either_or_terminal_is_rejected_on_the_mixed_cases():
    either_or = section("R1_rounded_ending")["prohibitions"]["either_or"]
    assert either_or["rejected"] is True
    assert either_or["declared_terminal"]["accepted_as_the_rounded_ending"] is False
    assert either_or["declared_terminal"]["satisfied"] is True
    assert either_or["declared_terminal"]["declared_conjunction_holds"] is True
    cases = either_or["mixed_cases"]
    assert sorted(cases) == ["committed_only", "neither", "sealable_only"]
    assert cases["sealable_only"]["satisfied"] is True
    assert cases["sealable_only"]["the_two_readings_disagree_here"] is True
    assert cases["committed_only"]["satisfied"] is True
    assert cases["committed_only"]["the_two_readings_disagree_here"] is True
    assert cases["neither"]["satisfied"] is False
    assert either_or["declared_terminal"]["decided_by_a_count"] is False


def test_the_netting_terminal_is_rejected_and_no_fused_residual_exists():
    netting = section("R1_rounded_ending")["prohibitions"]["netting"]
    assert netting["rejected"] is True
    declared = netting["declared_terminal"]
    assert declared["accepted_as_the_rounded_ending"] is False
    assert declared["declared_sealable_surplus"] == "1/4"
    assert declared["committed_residual_declared_magnitude"] == NO_MAGNITUDE
    assert declared["fused_residual_exists_exactly"] is False
    assert declared["reduces_a_residual"] is True and declared["records_fused"] is True
    control = declared["declared_quantified_control"]
    assert Fraction(control["netted_residual"]) == 0
    assert [Fraction(item) for item in control["separate_residuals"]] == [Fraction(1, 4),
                                                                         Fraction(1, 4)]
    assert control["netting_reports_a_single_zero_residual"] is True
    assert control["the_rounded_ending_keeps_both_residuals"] is True


def test_the_obstructing_and_compromising_terminals_are_rejected():
    prohibitions = section("R1_rounded_ending")["prohibitions"]
    obstruction = prohibitions["obstruction"]
    assert obstruction["rejected"] is True
    assert obstruction["declared_terminal_is_independent"] is True
    assert obstruction["declared_terminal"]["the_two_conditions_are_independent"] is True
    assert obstruction["declared_terminal"]["a_verdict_flip_is_detected"] is False
    control = obstruction["control"]
    assert control["accepted_as_the_rounded_ending"] is False
    assert control["a_verdict_flip_is_detected"] is True
    assert control["committed_verdict_with_the_sealable_condition_holding"] is False
    assert control["committed_verdict_with_the_sealable_condition_failing"] is True
    assert control["reasons"]

    compromise = prohibitions["compromise"]
    assert compromise["rejected"] is True
    declared = compromise["declared_terminal"]
    assert Fraction(declared["declared_tolerance"]) == 0
    assert Fraction(declared["declared_sealable_residual"]) == 0
    assert declared["holds_exactly"] is True
    assert declared["accepted_as_the_rounded_ending"] is True
    assert declared["the_committed_condition_admits_no_approximation"] is True
    assert len(compromise["controls"]) == 2
    approximate, tolerance_only = compromise["controls"]
    assert approximate["rejected"] is True
    assert Fraction(approximate["declared_terminal"]["declared_tolerance"]) == Fraction(1, 1000)
    assert Fraction(approximate["declared_terminal"]["declared_sealable_residual"]) \
        == Fraction(1, 1000)
    assert approximate["declared_terminal"]["holds_approximately"] is True
    assert approximate["declared_terminal"]["holds_exactly"] is False
    assert tolerance_only["rejected"] is True
    assert Fraction(tolerance_only["declared_terminal"]["declared_sealable_residual"]) == 0
    assert tolerance_only["declared_terminal"]["holds_exactly"] is True
    assert tolerance_only["declared_terminal"]["reasons"]


def test_the_yi_contrast_family_uses_the_address_machinery_and_fails_every_terminal():
    contrast = section("R2_yi_contrast_family")
    machinery = contrast["address_machinery"]
    assert machinery["diagonal_points"] == 81
    assert machinery["complement_points"] == 6480
    assert machinery["diagonal_plus_complement"] == 6561
    assert machinery["points_with_every_coordinate_out_of_position"] == 1296
    assert machinery["points_in_position_in_some_coordinates_only"] == 5184
    assert 81 == 3 ** 4 and 1296 == 6 ** 4
    assert machinery["per_coordinate_in_position_values"] == [0, 4, 8]
    assert machinery["per_coordinate_out_of_position_values"] == [1, 2, 3, 5, 6, 7]
    assert "3 a_i + b_i" in machinery["carrier"]
    assert "a = b" in machinery["mutual_measuring_diagonal"]
    assert contrast["all_three_contrast_terminals_fail"] is True
    assert contrast["the_two_sides_are_not_identified"] is True
    assert contrast["no_terminal_reading_is_taken_from_the_yi_pair"] is True
    assert len(contrast["contrast_terminals"]) == 3
    closed, opened, either_or = contrast["contrast_terminals"]
    for row in contrast["contrast_terminals"]:
        assert row["accepted"] is False
        assert row["verdict"] == "Rejected"
        assert row["rejection_reasons"]
    assert "carry-out condition" in closed["rejected_by"]
    assert "closure condition" in opened["rejected_by"]
    assert either_or["rejected_by"]


def test_the_beginning_split_accepts_a_resetable_reset_and_rejects_a_commitment_reset():
    beginning = section("R3_beginning_split")
    classes = {row["obstruction"]: row for row in beginning["classes"]}
    assert sorted(classes) == ["one_way_commitment_state", "phase_misalignment",
                              "step_carry_remainder"]
    assert classes["phase_misalignment"]["declared_class"] == "resetable"
    assert classes["phase_misalignment"]["declared_amount"] == "5"
    assert classes["step_carry_remainder"]["declared_class"] == "resetable"
    assert Fraction(classes["step_carry_remainder"]["declared_amount"]) == Fraction(2, 9)
    assert classes["one_way_commitment_state"]["declared_class"] == "non_resetable"
    assert classes["one_way_commitment_state"]["declared_amount"] == NO_MAGNITUDE
    assert all(row["write_out_required"] is True for row in beginning["classes"])

    resets = beginning["resets"]
    assert beginning["accepted_resets"] == ["phase_misalignment", "step_carry_remainder"]
    assert beginning["rejected_resets"] == ["one_way_commitment_state"]
    assert resets["phase_misalignment"]["accepted"] is True
    assert resets["phase_misalignment"]["state_before"] == "5"
    assert Fraction(resets["phase_misalignment"]["state_after"]) == 0
    assert Fraction(resets["step_carry_remainder"]["state_before"]) == Fraction(2, 9)
    assert Fraction(resets["step_carry_remainder"]["state_after"]) == 0
    assert resets["one_way_commitment_state"]["accepted"] is False
    assert resets["one_way_commitment_state"]["verdict"] == "ResetRejected"
    assert resets["one_way_commitment_state"]["state_unchanged"] is True
    assert resets["one_way_commitment_state"]["cleared_exactly"] is False
    assert resets["one_way_commitment_state"]["reasons"]
    assert beginning["no_reset_clears_the_commitment"] is True
    assert len(beginning["controls"]) == 3
    assert all("Rejected" in row["verdict"] for row in beginning["controls"])
    assert beginning["controls"][0]["verdict"] == "ResetRejected"
    assert beginning["controls"][0]["state_unchanged"] is True


def test_the_middle_five_carries_two_cycles_and_rejects_both_readings():
    five = section("R4_middle_five")
    assert five["points"] == [0, 1, 2, 3, 4]
    generation = five["declared_cycles"]["generation"]
    overcoming = five["declared_cycles"]["overcoming"]
    assert generation["step"] == 1 and overcoming["step"] == 2
    assert generation["orbit"] == [0, 1, 2, 3, 4]
    assert overcoming["orbit"] == [0, 2, 4, 1, 3]
    assert generation["order"] == 5 and overcoming["order"] == 5
    assert generation["is_a_generator"] is True and overcoming["is_a_generator"] is True
    assert generation["is_a_single_five_cycle"] is True
    assert overcoming["is_a_single_five_cycle"] is True
    assert five["five_is_prime"] is True
    assert five["generators_modulo_five"] == [1, 2, 3, 4]
    assert five["number_of_generators"] == 4
    assert five["every_nonzero_step_is_a_generator"] is True
    assert five["the_two_cycles_are_distinct_maps"] is True
    assert five["points_where_they_differ"] == [0, 1, 2, 3, 4]
    assert five["overcoming_is_generation_applied_twice"] is True
    assert five["both_cycle_rejections_fail"] is True
    one_cycle, identified, zero_step, composite = five["controls"]
    assert one_cycle["verdict"] == "Rejected"
    assert identified["verdict"] == "Rejected"
    assert zero_step["verdict"] == "Rejected"
    assert composite["verdict"] == "Rejected_NotAGenerator"
    assert composite["order_of_the_overcoming_step"] == 2
    assert composite["generators_modulo_four"] == [1, 3]
    assert composite["discriminates"] is True


def test_the_three_remainders_are_exact_and_the_chain_closes_none():
    remainders = section("R5_astronomical_remainders")
    assert remainders["declared_chain"]["annual_cycles"] == 3
    assert remainders["declared_chain"]["annual_cycle_days"] == 365
    assert remainders["declared_chain"]["chain_days"] == 1095
    assert remainders["remainders"] == {
        "Tzolkin": "55",
        "five Venus synodic periods, eight solar years": "1095",
        "the calendar round": "1095",
    }
    rows = {row["commensurability"]: row for row in remainders["commensurabilities"]}
    assert rows["Tzolkin"]["days"] == 260
    assert rows["five Venus synodic periods, eight solar years"]["days"] == 2920
    assert rows["the calendar round"]["days"] == 18980
    assert rows["Tzolkin"]["remainder"] == 55
    assert 1095 % 260 == 55 and 1095 % 2920 == 1095 and 1095 % 18980 == 1095
    for row in remainders["commensurabilities"]:
        assert row["closes_it"] is False
        assert row["exact_multiple_of_the_chain_length"] is False
        assert row["chain_cycles_needed"] != "1"
    assert remainders["the_chain_closes_none"] is True
    assert "do NOT close" in remainders["the_chain_closes_none_statement"]
    assert remainders["exact_identities"] == {
        "2920 = 8 x 365": True, "18980 = 52 x 365": True, "18980 = 73 x 260": True,
        "365 = 18 x 20 + 5": True}
    assert len(remainders["closing_claim_controls"]) == 3
    for row in remainders["closing_claim_controls"]:
        assert row["verdict"] == "Rejected"
        assert row["rejection_reasons"]
    variants = remainders["failed_to_discriminate"]["variants"]
    assert variants["declared primary: the declared annual cycle"]["remainders"] == [55, 1095,
                                                                                    1095]
    assert variants["eighteen twenty-day months"]["remainders"] == [40, 1080, 1080]
    assert variants["fifty-two weeks of seven days"]["remainders"] == [52, 1092, 1092]
    assert all(row["closes_none"] is True for row in variants.values())
    assert remainders["failed_to_discriminate"]["verdict"] == "FAILED_TO_DISCRIMINATE"
    assert remainders["failed_to_discriminate"]["why"]


def test_three_is_not_a_degree_and_not_a_failure_of_injectivity():
    degree = section("R6_three_is_not_a_degree")
    assert degree["the_three"]["value"] == 3
    assert degree["the_three"]["third_degree_spherical_harmonics"] == 7
    assert degree["the_three"]["harmonics_to_degree_three"] == 16
    assert degree["the_three"]["harmonic_dimension_formula"] == "2 l + 1"
    assert degree["the_three"]["three_equals_seven"] is False
    assert degree["the_three"]["three_equals_sixteen"] is False
    assert 2 * 3 + 1 == 7 and (3 + 1) ** 2 == 16
    injectivity = degree["injectivity"]
    assert injectivity["is_injective"] is True
    assert injectivity["is_a_collapse"] is False
    assert injectivity["collisions"] == 0
    assert len(injectivity["unordered_index_pairs"]) == 3
    assert injectivity["declared_index_set"] == ["C1", "C2", "C3"]
    assert len(set(injectivity["declared_images"].values())) == 3
    assert degree["no_spherical_carrier_is_declared"] is True
    assert degree["identifications_rejected"] == 2
    assert len(degree["readings"]) == 2
    for row in degree["readings"]:
        assert row["verdict"] == "Rejected"
        assert len(row["rejection_reasons"]) == 2
        assert row["decided_by_a_count"] is False
    coincidence = degree["numerical_coincidence_recorded_not_used"]
    assert "2 x 2 + 1" in coincidence["coincidence"]
    assert coincidence["identification_made"] is False


def test_the_one_way_reservoir_is_monotone_and_hysteretic():
    reservoir = section("R7_commitment_reservoir")
    assert reservoir["magnitude"] == NO_MAGNITUDE
    assert reservoir["declared_thresholds"] == {"opens_at": "1", "closes_at": "1/4"}
    assert reservoir["declared_increments"] == {"open_branch": "1/8", "closed_branch": "1/16"}
    assert reservoir["declared_loop_controls"] == ["0", "1/2", "1", "1/2", "0"]
    loop = reservoir["declared_loop"]
    assert [row["branch_state"] for row in loop] == ["closed", "closed", "open", "open",
                                                    "closed"]
    assert [row["state_after"] for row in loop] == ["1/16", "1/8", "1/4", "3/8", "7/16"]
    assert [Fraction(row["increment"]) for row in loop] == [Fraction(1, 16), Fraction(1, 16),
                                                            Fraction(1, 8), Fraction(1, 8),
                                                            Fraction(1, 16)]
    assert all(Fraction(row["increment"]) >= 0 for row in loop)
    assert reservoir["monotone_non_decreasing"] is True
    assert reservoir["strictly_increasing"] is True
    assert reservoir["the_loop_does_not_restore_the_state"] is True
    hysteresis = reservoir["hysteresis"]
    assert hysteresis["present"] is True
    assert hysteresis["paths_differ"] is True
    assert hysteresis["declared_probe_control"] == "1/2"
    assert hysteresis["thaw_path"]["branch_state"] == "closed"
    assert hysteresis["refreeze_path"]["branch_state"] == "open"
    assert hysteresis["thaw_path"]["declared_increment"] == "1/16"
    assert hysteresis["refreeze_path"]["declared_increment"] == "1/8"
    assert reservoir["the_one_way_shape_does_work"] is True
    equal_thresholds, threshold_blind = reservoir["controls"]
    assert equal_thresholds["verdict"] == "NoHysteresis"
    assert equal_thresholds["hysteresis_present"] is False
    assert equal_thresholds["discriminates"] is True
    assert equal_thresholds["probe_readings"] == [["closed", "1/16"], ["closed", "1/16"]]
    assert threshold_blind["verdict"] == "FAILED_TO_DISCRIMINATE"
    assert threshold_blind["still_monotone"] is True
    assert threshold_blind["hysteresis_still_present"] is True


def test_the_parent_first_order_relaxation_fails_both_controls():
    failure = section("R7_commitment_reservoir")["parent_relaxation_failure"]
    assert failure["relaxation_coefficient"] == "1/30"
    assert failure["time_constant"] == "30"
    assert failure["declared_displacement"] == "1/4"
    assert failure["monotone_non_decreasing"] is False
    assert failure["hysteresis_present"] is False
    assert failure["threshold_declared"] is False
    assert failure["branch_state_declared"] is False
    assert failure["monotonicity_control"] == "FAILED"
    assert failure["hysteresis_control"] == "FAILED"
    assert failure["verdict"] == "TheOneWayShapeIsDoingWork"
    drifts = [Fraction(row["drift_as_rational"]) for row in failure["declared_steps"]]
    assert len(drifts) == 5
    assert drifts[0] == Fraction(-1, 120)
    assert drifts[1] == Fraction(-29, 3600)
    assert drifts[2] == Fraction(-841, 108000)
    assert drifts[3] == Fraction(-24389, 3240000)
    assert drifts[4] == Fraction(-707281, 97200000)
    assert all(later == earlier * Fraction(29, 30) for earlier, later in pairwise(drifts))
    assert all(drift < 0 for drift in drifts)
    assert all(row["non_negative"] is False for row in failure["declared_steps"])
    assert failure["declared_branch_reading"] == {
        "thaw_path": "no branch state is declared",
        "refreeze_path": "no branch state is declared"}


def test_sealing_is_refused_for_the_leaking_component():
    sealing = section("R8_sealing_refused")
    assert sealing["sealable_component"]["sealed"] is True
    assert sealing["sealable_component"]["bound"] == {"mixed": "0", "thermocline": "0",
                                                     "deep": "0"}
    committed = sealing["committed_component"]
    assert committed["sealing_refused"] is True
    assert committed["sealed"] is False
    assert committed["accounted"] is True
    assert committed["verdict"] == "Refused_NotSealable"
    assert committed["declared_magnitude"] == NO_MAGNITUDE
    assert committed["reasons"] and "by definition a leak" in committed["reasons"][0]
    violation = sealing["layer_wise_violation"]
    assert violation["declared_drift"] == {"mixed": "1/64", "thermocline": "0",
                                           "deep": "-1/64"}
    assert Fraction(violation["total_drift"]) == 0
    assert violation["violating_layers"] == ["mixed", "deep"]
    assert violation["verdict"] == "LayerWiseViolation"
    assert violation["cancelled_by_the_total"] is False
    assert sealing["no_magnitude_for_the_committed_component"] is True
    assert len(sealing["controls"]) == 2
    sealable_treatment, offsetting = sealing["controls"]
    assert sealable_treatment["verdict"] == "Rejected"
    assert offsetting["verdict"] == "Rejected"
    assert offsetting["rejection_reasons"]
    assert all(row["rejected_by_the_declared_condition"] is True for row in sealing["controls"])


def test_the_four_by_two_classification_and_no_magnitude_anywhere():
    classification = section("R9_factor_classification")
    assert classification["cells"] == 8
    assert classification["declarations"] == ["correction_to_be_made",
                                              "structure_to_be_preserved",
                                              "explicitly_unquantified"]
    assert classification["account_sizes"] == {"correction_to_be_made": 1,
                                               "structure_to_be_preserved": 2,
                                               "explicitly_unquantified": 5}
    assert classification["accounts"] == {
        "correction_to_be_made": ["water_vapour/south"],
        "explicitly_unquantified": ["aerosols/south", "low_cloud/north", "water_vapour/north",
                                    "wildfire/north", "wildfire/south"],
        "structure_to_be_preserved": ["aerosols/north", "low_cloud/south"],
    }
    assert classification["accounts_are_separate"] is True
    assert classification["declared_verdict"]["accepted"] is True
    assert classification["declared_verdict"]["cells_covered"] == 8
    records = {(row["factor"], row["side"]): row for row in classification["cell_records"]}
    assert len(records) == 8
    assert {key: row["declaration"] for key, row in records.items()} == DECLARED_CELLS
    assert classification["declared_placement"] == {
        "aerosols": {"north": "structure_to_be_preserved",
                     "south": "explicitly_unquantified"},
        "low_cloud": {"north": "explicitly_unquantified",
                      "south": "structure_to_be_preserved"},
        "water_vapour": {"north": "explicitly_unquantified",
                         "south": "correction_to_be_made"},
        "wildfire": {"north": "explicitly_unquantified",
                     "south": "explicitly_unquantified"},
    }
    assert "north-side structure" in records[("aerosols", "north")]["declared_basis"]
    assert "south-weighted coupler" in records[("low_cloud", "south")]["declared_basis"]
    assert "fast reversible amplifier" in records[("water_vapour", "south")]["declared_basis"]
    assert "ratchet behaviour" in records[("wildfire", "north")]["declared_basis"]
    assert records[("wildfire", "north")]["ratchet"] is True
    assert records[("wildfire", "south")]["ratchet"] is True
    assert records[("water_vapour", "south")]["reversible"] is True
    assert records[("water_vapour", "south")]["correction"]
    assert records[("aerosols", "north")]["preserved_structure"]
    assert records[("low_cloud", "south")]["preserved_structure"]
    for row in classification["cell_records"]:
        assert row["declaration"] in classification["declarations"]
        assert row["magnitude"] == NO_MAGNITUDE
        assert row["magnitude_is_not_asserted"] is True
        assert not [key for key in row if key in FORBIDDEN_MAGNITUDE_KEYS]

    assert classification["no_magnitude_is_given_for_any_factor"] is True
    assert classification["magnitude_audit"]["findings"] == []
    assert not numeric_leaves(classification["cell_records"], "cells")
    asymmetry = classification["declared_asymmetry"]
    assert asymmetry["side_specific_factors"] == ["aerosols", "low_cloud", "water_vapour"]
    assert asymmetry["factors_declared_on_both_sides"] == ["wildfire"]
    assert "the south side" in asymmetry["the_sealing_side"]
    assert len(classification["controls"]) == 4
    structure, ratchet, symmetric, fused = classification["controls"]
    for row in classification["controls"]:
        assert row["verdict"] == "Rejected"
        assert row["rejection_reasons"]
        assert row["rejected_by_the_declared_condition"] is True
    assert structure["cell"] == "aerosols/north"
    assert any("correctable perturbation" in reason for reason in structure["rejection_reasons"])
    assert ratchet["cell"] == "wildfire/north"
    assert any("reversible" in reason for reason in ratchet["rejection_reasons"])
    assert any("symmetric north-south treatment" in reason
               for reason in symmetric["rejection_reasons"])
    assert any("fuses them into one account" in reason for reason in fused["rejection_reasons"])

    ending = section("R1_rounded_ending")
    committed_records = [ending["committed_component"]["written_record"],
                         ending["committed_component"]["carry_out"],
                         ending["committed_component"]["residual_record"],
                         ending["committed_component"]["controls"]]
    assert not numeric_leaves(committed_records, "committed")
    assert section("R7_commitment_reservoir")["magnitude"] == NO_MAGNITUDE
    assert section("R8_sealing_refused")["committed_component"]["declared_magnitude"] \
        == NO_MAGNITUDE


def test_the_fourth_uncertainty_term_is_recorded_separately_and_never_fused():
    uncertainty = section("R10_uncertainty_fourth_term")
    assert uncertainty["term_count"] == 4
    assert uncertainty["declared_terms"] == ["mapping", "bias", "sampling",
                                             "committed-but-unquantified"]
    assert uncertainty["quantified_terms"] == {"mapping": "1/64", "bias": "1/64",
                                               "sampling": "3/256"}
    fourth = uncertainty["fourth_term"]
    assert fourth["name"] == "committed-but-unquantified"
    assert fourth["quantified"] is False
    assert fourth["magnitude"] == NO_MAGNITUDE
    assert fourth["recorded_separately_at_every_seam"] is True
    assert fourth["never_fused"] is True
    assert uncertainty["four_terms_separately_at_every_seam"] is True
    assert uncertainty["no_magnitude_for_the_fourth_term"] is True
    assert len(uncertainty["seams"]) == 3
    assert [row["cycle"] for row in uncertainty["seams"]] == ["C1", "C2", "C3"]
    for row in uncertainty["seams"]:
        assert row["terms_recorded"] == 4
        assert Fraction(row["mapping"]) == Fraction(1, 64)
        assert Fraction(row["bias"]) == Fraction(1, 64)
        assert Fraction(row["sampling"]) == Fraction(3, 256)
        assert row["recorded_separately"] is True
        assert row["committed_but_unquantified"]["quantified"] is False
        assert row["committed_but_unquantified"]["magnitude"] == NO_MAGNITUDE
        assert row["committed_but_unquantified"]["term"] == "committed-but-unquantified"
    assert Fraction(uncertainty["fused_three_term_figure"]) == Fraction(11, 256)
    fused = uncertainty["fused_control"]
    assert fused["verdict"] == "Rejected"
    assert fused["fused_magnitude_exists"] is False
    assert fused["fourth_term"] == NO_MAGNITUDE
    assert uncertainty["pooling_control"]["fused_with_the_fourth_term"] is False


def test_the_inherited_controls_run_and_the_failures_are_retained():
    controls = section("R11_inherited_controls")
    invariance = controls["sampling_change_invariance"]
    assert invariance["readings_unchanged"] is True
    assert invariance["composition_only_reading_moves"] is True
    assert Fraction(invariance["composition_only_difference"]) == Fraction(3, 256)
    assert invariance["the_composition_only_reading_is_an_artefact"] is True
    assert invariance["not_read_as_a_change_of_mechanism"] is True
    assert invariance["fused_reading"]["verdict"] == "Rejected as an artefact"
    assert Fraction(invariance["fused_reading"]["difference"]) == Fraction(3, 256)
    readings = invariance["readings"]
    assert sorted(readings) == ["A", "B"]
    assert readings["A"]["mechanism_reading"] == readings["B"]["mechanism_reading"]
    assert readings["A"]["composition_only_reading"] != readings["B"]["composition_only_reading"]
    assert Fraction(readings["A"]["composition_only_reading"]) == Fraction(1, 32)
    assert Fraction(readings["B"]["composition_only_reading"]) == Fraction(11, 256)

    sealing = controls["layer_wise_sealing"]
    assert sealing["bound"] == {"mixed": "0", "thermocline": "0", "deep": "0"}
    assert sealing["all_layers_sealed"] is True
    assert sealing["sealed_at_every_seam"] is True
    assert sealing["memory_layer"] == "deep"
    assert sealing["memory_layer_stable"] is True
    assert sealing["total_cancelling_control"]["cancelled_by_the_total"] is False
    assert sealing["total_cancelling_control"]["violating_layers"] == ["mixed", "deep"]
    assert sealing["total_cancelling_control"]["total_drift"] == "0"

    identity = controls["identity_loop"]
    assert identity["declared_loop"] == {"legs": [3, 3, 3, 3], "sum": 12, "phase_shift": 0,
                                        "returns_the_identity": True, "verdict": "Identity"}
    assert identity["control_loop"]["legs"] == [3, 3, 3, 4]
    assert identity["control_loop"]["returns_the_identity"] is False
    assert identity["control_loop"]["phase_shift"] == 1
    assert identity["discriminates"] is True

    memory = controls["atmospheric_memory_loss"]
    assert memory["atmospheric_only"]["carried_memory_at_the_seam"] == "0"
    assert memory["atmospheric_only"]["lost"] is True
    assert Fraction(memory["with_the_slow_component"]["carried_memory_at_the_seam"]) \
        == Fraction(7, 8)
    assert memory["with_the_slow_component"]["kept"] is True
    assert memory["the_split_does_work"] is True

    separated = controls["separated_uncertainty"]
    assert separated["terms"] == ["mapping", "bias", "sampling", "committed-but-unquantified"]
    assert separated["four_terms_present_separately_at_every_seam"] is True
    assert separated["fused_control"]["fused_magnitude_exists"] is False
    assert len(separated["seams"]) == 3

    assert len(controls["inherited_controls_still_run"]) == 5
    assert len(controls["failed_controls"]) == 2
    for row in controls["failed_controls"]:
        assert row["outcome"] == "FAILED_TO_DISCRIMINATE"
        assert row["why"]
    assert any("year-length" in row["control"] for row in controls["failed_controls"])
    assert any("monotonicity" in row["control"] for row in controls["failed_controls"])
    assert controls["controls_that_did_discriminate"]
    carried = controls["carried_forward_failures"]
    assert controls["carried_forward_failures_count"] == 3
    assert len(carried) == 3
    for row in carried:
        assert row["outcome"] == "FAILED_TO_DISCRIMINATE"
        assert row["why"] and row["source"]
    assert any("0238" in row["source"] for row in carried)
    assert any("0237" in row["source"] for row in carried)


def test_the_exact_baselines_are_reproduced_and_ordered():
    baselines = section("R12_baselines")
    first = baselines["first_scheme"]
    assert first["amplitude_floor"] == "J_inf = 1"
    assert first["attained_at"] == "(p, q) = (-2, 17/10)"
    assert first["on_the_discriminant_variety"] is False
    assert first["real_branches_at_the_witness"] == 2
    assert first["frozen_level_of_the_ten_middle_sides"] == "1"
    assert Fraction(first["leading_coefficient_of_the_specialised_quartic"]) == Fraction(3285,
                                                                                        512)
    assert Fraction(first["discriminant_of_the_specialised_quartic"]) != 0
    for row in first["branches"]:
        assert Fraction(row["abs_h_upper_bound"]) < 1
        assert Fraction(row["abs_E_0_upper_bound"]) < 1
        assert row["below_the_frozen_level"] is True

    closure = baselines["closure_reading"]
    assert closure["nontrivial_branch_equation"] == CLOSURE_CUBIC
    assert closure["real_exits"] == 1
    assert closure["correctly_rounded_prefix"] == "3.2035072879526181"
    assert closure["amplitude"].startswith("3.2035072879526181")
    low, high = (Fraction(closure["isolation_interval"][0]),
                 Fraction(closure["isolation_interval"][1]))
    assert Fraction(3) < low < high < Fraction(4)
    assert closure["no_rational_root"] is True
    assert closure["derivative_discriminant"] == "-512"
    assert closure["the_other_two_exits_are_non_real"] is True
    assert Fraction(closure["quotient_quadratic_discriminant_enclosure"][1]) < 0

    level = baselines["level_reading"]
    assert level["equation"] == "h^4 + 8 h^3 + 64 h^2 + 192 h - 512 = 0"
    assert level["real_branches"] == 2
    assert level["largest_branch_amplitude"] == "2 + sqrt(8 sqrt(17) - 20)"
    assert level["sigma"] == "8 sqrt(17) - 20"
    assert level["sigma_is_positive"] is True
    assert "Q(sqrt(17))" in level["closed_form_verified_in"]
    assert "u^4 + 40 u^2 - 688" in level["substitution"]
    level_low = Fraction(level["largest_branch_amplitude_enclosure"][0])
    level_high = Fraction(level["largest_branch_amplitude_enclosure"][1])
    assert Fraction(5) < level_low < level_high < Fraction(6)
    negative = level["negative_branch_enclosure"]
    positive = level["positive_branch_enclosure"]
    assert Fraction(-6) < Fraction(negative[0]) < Fraction(negative[1]) < Fraction(-5)
    assert Fraction(1) < Fraction(positive[0]) < Fraction(positive[1]) < Fraction(2)

    ordering = baselines["ordering"]
    assert ordering["asserted_exactly"] is True
    assert ordering["decided_on_exact_rationals"] is True
    assert ordering["rational_witnesses"] == {"one": "1", "four": "4"}
    assert ordering["statement"] == "1 < 3.2035072879526181... < 2 + sqrt(8 sqrt(17) - 20)"
    assert len(ordering["between"]) == 3
    assert Fraction(1) < low < high < Fraction(4) < level_low


def test_observational_verification_is_unavailable_and_the_reservation_is_carried():
    report = load(EVIDENCE)
    parent = load(PARENT_CONTRACT)
    status = report["verification_status"]
    assert status["observational"] == "Unavailable"
    assert parent["verification_status"]["observational"] == "Unavailable"
    assert status["data_authenticity_reservation"] \
        == parent["verification_status"]["data_authenticity_reservation"]
    assert "not narrowed to any single stage" in status["data_authenticity_reservation"]
    assert "hashes and same-source read-backs do not remove it" \
        in status["data_authenticity_reservation"]
    assert status["data_authenticity_reservation_source"] \
        == "experiments/three_cycle_chain_v1/contract.json, carried verbatim and un-narrowed"
    assert status["xue_study_data_used"] is False
    assert status["future_chain"] is True
    assert status["checked_here"]["observational_verification"] == "Unavailable"
    assert status["checked_here"]["no_data_read_or_used"] is True
    assert status["checked_here"]["hashes_and_read_backs_do_not_remove_the_reservation"] is True
    assert report["checks"]["observational_verification_is_recorded_unavailable"] is True
    assert report["checks"]["the_data_authenticity_reservation_is_carried_verbatim"] is True
    assert report["what_is_not_claimed"]["xue_study_data_used"] is False
    assert report["what_is_not_claimed"]["observational_verification"] == "Unavailable"
    assert report["what_is_not_claimed"]["no_data_read_or_used"] is True
    assert report["what_is_not_claimed"]["physical_claim"] is False
    assert report["what_is_not_claimed"]["forecast"] is False
    assert report["what_is_not_claimed"]["skill_claim"] is False
    assert report["what_is_not_claimed"]["meteorological_data_used"] is False
    assert report["what_is_not_claimed"]["native_certificate"] is False
    assert report["what_is_not_claimed"]["native_admission"] == "NotGranted"
    assert report["what_is_not_claimed"]["stable_api_change"] is False
    assert report["what_is_not_claimed"]["no_magnitude_for_aerosols_low_cloud_water_vapour_or_"
                                        "wildfire"] is True
    assert report["what_is_not_claimed"]["no_magnitude_for_the_committed_component"] is True
    assert report["what_is_not_claimed"][
        "the_four_by_two_table_is_a_declared_classification_not_a_result_about_the_atmosphere"] \
        is True
    assert report["what_is_not_claimed"]["the_yi_pair_is_used_only_as_the_contrast_family"] is True
    assert report["what_is_not_claimed"]["no_claim_added_to_docs_claims_toml"] is True
    assert report["what_is_not_claimed"]["no_contract_or_note_edited"] is True
    assert report["what_is_not_claimed"]["no_rust_source_or_lock_changed"] is True


def test_the_undecided_items_and_the_modelling_choices_are_declared():
    report = load(EVIDENCE)
    undecided = report["undecided"]
    assert len(undecided) == 5
    assert report["checks"]["undecided_items_are_declared"] is True
    items = [row["item"] for row in undecided]
    assert any("none in position" in item for item in items)
    assert any("sealing side" in item for item in items)
    assert any("four-by-two" in item for item in items)
    assert any("threshold and hysteresis" in item for item in items)
    assert any("committed component's declared state" in item for item in items)
    for row in undecided:
        assert row["reason"]
        assert row["retained_partial_result"] is not None
    none_in_position = next(row for row in undecided if "none in position" in row["item"])
    retained = none_in_position["retained_partial_result"]
    assert retained["diagonal_points"] == 81
    assert retained["complement_points"] == 6480
    assert retained["every_coordinate_out_of_position"] == 1296
    assert retained["some_coordinates_in_position"] == 5184

    choices = report["modelling_choices"]
    for key in ("rounded_ending_as_a_conjunction", "either_or_readings",
                "separate_residual_records", "closure_field", "address_machinery_reused",
                "beginning_split_declaration", "five_point_structure", "chain_length_in_days",
                "remainder_control", "three_is_not_a_degree", "one_way_reservoir",
                "the_state_is_not_a_magnitude", "parent_relaxation_failure",
                "sealing_refusal", "four_by_two_table", "correction_account_declared_as_a_path",
                "uncertainty_fourth_term", "inherited_controls", "baselines", "exact_only",
                "external_library", "resource_limits"):
        assert choices[key], key
    assert len(choices) == 22
    assert "CONJUNCTION" in choices["rounded_ending_as_a_conjunction"]
    assert "mixed cases" in choices["either_or_readings"]
    assert "Q(w)" in choices["closure_field"]
    assert "81" in choices["address_machinery_reused"]
    assert "two directed cycles on the same five points" in choices["five_point_structure"]
    assert "five is prime" in choices["five_point_structure"]
    assert "1095" in choices["chain_length_in_days"]
    assert "not a third-degree spherical harmonic" in choices["three_is_not_a_degree"] or \
        "degree-l spherical harmonics" in choices["three_is_not_a_degree"]
    assert "non-decreasing" in choices["one_way_reservoir"]
    assert "29/30" in choices["parent_relaxation_failure"]
    assert "by definition a leak" in choices["sealing_refusal"]
    assert "no magnitude is given" in choices["four_by_two_table"] or \
        "No magnitude" in choices["four_by_two_table"] or \
        "no magnitude" in choices["four_by_two_table"]
    assert "11/256" in choices["uncertainty_fourth_term"]
    assert "rlimit" in choices["resource_limits"]
    assert "no floating-point value" in choices["exact_only"]
    assert "not native authority" in choices["external_library"]
    assert report["level"] == load(CONTRACT)["level"]
    assert report["residual"] == load(CONTRACT)["residual"]
    assert report["protected"] == load(CONTRACT)["protected"]


def test_the_declared_checks_all_pass_and_name_their_conditions():
    checks = load(EVIDENCE)["checks"]
    assert all(checks.values())
    for name in ("the_ending_is_the_declared_conjunction",
                 "both_terminal_conditions_hold_in_full",
                 "the_two_residual_records_are_kept_separate",
                 "the_either_or_terminal_is_rejected", "the_netting_terminal_is_rejected",
                 "the_obstructing_terminal_is_rejected", "the_compromising_terminal_is_rejected",
                 "the_mutual_measuring_diagonal_has_81_points",
                 "the_complement_of_the_diagonal_has_6480_points",
                 "the_three_yi_contrast_terminals_all_fail",
                 "the_resetable_reset_is_accepted", "the_non_resetable_reset_is_rejected",
                 "the_five_point_double_cycle_holds", "rejecting_one_cycle_fails",
                 "identifying_the_two_cycles_fails", "the_three_remainders_are_reported",
                 "the_chain_closes_no_commensurability",
                 "three_is_not_a_degree_three_harmonic",
                 "three_is_not_a_failure_of_injectivity", "the_one_way_reservoir_is_monotone",
                 "the_one_way_reservoir_is_hysteretic",
                 "the_parent_relaxation_fails_monotonicity",
                 "the_parent_relaxation_fails_hysteresis",
                 "sealing_is_refused_for_the_committed_component",
                 "the_sealable_reading_of_the_committed_component_is_rejected",
                 "the_committed_component_cannot_offset_a_sealing_violation",
                 "every_classification_cell_carries_exactly_one_declaration",
                 "the_structure_cell_control_is_rejected",
                 "the_ratchet_cell_control_is_rejected",
                 "the_symmetric_treatment_control_is_rejected",
                 "the_fused_account_control_is_rejected",
                 "no_magnitude_is_given_for_the_four_factors_or_the_committed_component",
                 "no_magnitude_key_carries_anything_but_the_declared_none",
                 "the_fourth_uncertainty_term_is_recorded_separately",
                 "the_four_uncertainty_terms_are_never_fused",
                 "the_sampling_change_invariance_control_runs",
                 "the_layer_wise_sealing_control_runs", "the_identity_loop_control_runs",
                 "the_atmospheric_chain_loses_the_carried_memory",
                 "the_baselines_are_reproduced", "the_failed_controls_are_retained",
                 "the_parents_retained_failures_are_carried_forward",
                 "observational_verification_is_recorded_unavailable",
                 "the_data_authenticity_reservation_is_carried_verbatim",
                 "all_parent_contracts_are_retained_byte_for_byte",
                 "assertions_within_budget", "no_floating_point_value_is_retained"):
        assert checks[name] is True, name


def test_the_parent_contracts_are_read_only_and_not_edited_by_this_run():
    report = load(EVIDENCE)
    assert digest(PARENT_CONTRACT) == DECLARED_PARENT_SHA256
    assert digest(PARENT_SUPPLEMENT) == DECLARED_SUPPLEMENT_SHA256
    assert digest(SURGERY_CONTRACT) == DECLARED_SURGERY_SHA256
    assert digest(CONTRACT) == DECLARED_CONTRACT_SHA256
    assert report["checks"]["all_parent_contracts_are_retained_byte_for_byte"] is True
    assert report["checks"]["this_contract_digest_matches_the_declared_one"] is True
    assert report["what_is_not_claimed"]["no_contract_or_note_edited"] is True
    assert report["what_is_not_claimed"]["pre_existing_files_byte_identical"] is True


def test_the_claim_is_registered_once_and_binds_the_checker_and_the_note():
    """Exactly one claim for this run is registered, and it names the checker, the evidence and the note.

    The checker was written while this test asserted the claim's ABSENCE, because a claim lives in
    `docs/claims.toml` and is added by the parent session with its note.  The parent session has now
    added it; the assertion is inverted rather than dropped, so the binding stays checked.
    """
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    assert claims
    matches = [row for row in claims if row.get("claim_id") == CLAIM_ID]
    assert len(matches) == 1, "exactly one claim must be registered for this run"
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for symbol in ("three_cycle_supplement_v2/calibration.py",
                   "three_cycle_supplement_v2/contract.json",
                   "three_cycle_supplement_v2/evidence.json",
                   "0239-the-rounded-ending"):
        assert symbol in claim["code_symbol"], symbol
    assert "failed to discriminate" in claim["counterexample_boundary"].lower(), \
        "the boundary must retain the two failed controls"
    assert "NotGranted" in claim["counterexample_boundary"], "the boundary must record native admission"
    assert claim["forbidden_conflations"], "the claim must name its conflations"
    report = load(EVIDENCE)
    assert report["what_is_not_claimed"]["no_claim_added_to_docs_claims_toml"] is True
    parent_claims = [row for row in claims
                     if row.get("claim_id") == "adva.bounded-experiment.three-cycle-supplement.v0"]
    assert len(parent_claims) == 1, "the surgery run's claim stays registered and untouched"
