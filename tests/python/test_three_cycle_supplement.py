"""The paired test for the three-cycle supplement surgery calibration; external evidence only.

The assertions here are about what the retained checker decided by exact arithmetic on one
declared construction: a declared singular locus, a declared collar with its orientation and
normal, two declared spirals with opposite declared chirality, a declared flux pairing, a
written obstruction on side O and a bounded arrival on side I.  They are not claims about any
physical object, they promote no native identity, and the cold/heat reading is checked only as
the declared projection map.

The checker is invoked without `-S` because its declared external library (sympy) must be
importable; the run remains an external exact calibration either way.

The record carries no claim for this run: the parent session adds the claim to
`docs/claims.toml` with its note, so the last test asserts the claim is absent rather than
dropping the binding.
"""

import hashlib
import json
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/three_cycle_supplement_v1"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
PARENT_CONTRACT = ROOT / "experiments/three_cycle_chain_v1/contract.json"
PARENT_SUPPLEMENT = ROOT / "experiments/three_cycle_chain_v1/contract-supplement-1.json"
CLAIM_ID = "adva.bounded-experiment.three-cycle-supplement.v0"
DECLARED_CONTRACT_SHA256 = \
    "157838642e9097ea4a1a1c7461db9e548affb0c6f3af7b830816f37f22b74f5a"
DECLARED_PARENT_SHA256 = \
    "a3dc2e8d86e45139484fceed571ef99ea3b63f18748c6f1c82bb031a3305a965"
DECLARED_SUPPLEMENT_SHA256 = \
    "e125ee4940b838924257d9420bde71cf060a0745dc5d3d482c1691158785ac9f"

SECTION_NAMES = (
    "S1_surgery_and_collar", "S2_spirals_and_chirality", "S3_flux_and_attribution",
    "S4_side_O_obstruction", "S5_side_I_arrival", "S6_resource_accounting", "S7_projection",
    "S8_baselines", "S9_controls",
)

TOP_LEVEL_KEYS = (
    "assertions", "checker_sha256", "checks", "contract", "contract_sha256",
    "contract_sha256_declared", "level", "limits", "modelling_choices", "parent_contracts",
    "protected", "residual", "schema", "sections", "status", "tooling", "undecided",
    "verification_status", "version", "what_is_not_claimed",
)

FROZEN_SECTION_SHAPE = {
    "S1_surgery_and_collar": ["collar", "declared_singular_locus", "excision"],
    "S2_spirals_and_chirality": ["chirality_condition", "chirality_condition_on_the_declared_pair",
                                 "declared_spiral_map", "degenerate_spiral_controls",
                                 "opposite_chirality_declared", "spirals"],
    "S3_flux_and_attribution": ["attribution", "collar_normal", "declared_pairing", "flux_after",
                                "flux_after_from_the_rise_formula", "flux_after_terms",
                                "flux_before", "flux_before_reason",
                                "introduced_resource_per_turn", "radial_cancellation",
                                "radial_normal_control", "rise", "rise_formula",
                                "same_chirality_control", "sign_pairs", "strictly_greater",
                                "unattributed_control"],
    "S4_side_O_obstruction": ["computed_values", "controls", "declared_obstruction", "discharge",
                              "discharge_condition", "discharge_is_a_condition_on_the_record",
                              "record_agrees_with_the_computed_values", "side", "written_record"],
    "S5_side_I_arrival": ["arrival", "collar_diameter", "controls", "declared_start",
                          "declared_step_budget", "declared_time_domain_target",
                          "failed_to_discriminate", "radial_distance_equals_the_collar_diameter",
                          "side", "step_accounting"],
    "S6_resource_accounting": ["atmospheric_memory_control", "carried_remainder",
                               "grand_total_unchanged", "layer_sealing",
                               "no_resource_created_by_the_surgery",
                               "per_layer_sums_equal_the_carried_remainder",
                               "seam_redistribution", "surgery_split", "total_cancelling_control",
                               "zero_redistribution_control"],
    "S7_projection": ["checked_as_a_map", "controls", "declared_codomain", "declared_domain",
                      "declared_projection", "no_cold_heat_quantity_asserted",
                      "the_cold_heat_reading_exists_only_as_this_map",
                      "the_projection_is_declared_only", "verdict"],
    "S8_baselines": ["closure_reading", "first_scheme", "level_reading", "ordering"],
    "S9_controls": ["atmospheric_memory_loss", "controls_that_did_discriminate", "failed_controls",
                    "inherited_controls_still_run", "sampling_change_invariance",
                    "separated_uncertainty"],
}


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


def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["status"] == "ExternalExactPass"
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract_sha256"] == digest(CONTRACT) == DECLARED_CONTRACT_SHA256
    assert report["contract_sha256_declared"] == DECLARED_CONTRACT_SHA256
    assert report["assertions"] <= contract["budgets"]["max_assertions"]
    assert report["limits"] == contract["budgets"]
    assert all(report["checks"].values())
    assert contract["budgets"]["child_processes"] == 0
    parents = {row["path"]: row for row in report["parent_contracts"]}
    assert parents["experiments/three_cycle_chain_v1/contract.json"]["sha256"] \
        == digest(PARENT_CONTRACT) == DECLARED_PARENT_SHA256
    assert parents["experiments/three_cycle_chain_v1/contract-supplement-1.json"]["sha256"] \
        == digest(PARENT_SUPPLEMENT) == DECLARED_SUPPLEMENT_SHA256
    assert all(row["retained_byte_for_byte"] for row in report["parent_contracts"])


def test_a_fresh_run_reproduces_the_retained_payload_on_a_fresh_copy(tmp_path):
    output = tmp_path / "fresh.json"
    completed = invoke(CHECKER, output)
    assert completed.returncode == 0, completed.stderr
    fresh = load(output)
    retained = load(EVIDENCE)
    assert fresh["status"] == retained["status"]
    assert fresh["assertions"] == retained["assertions"]
    assert fresh["sections"] == retained["sections"]
    assert fresh["tooling"] == retained["tooling"]
    assert fresh["undecided"] == retained["undecided"]
    assert fresh["modelling_choices"] == retained["modelling_choices"]
    assert fresh["verification_status"] == retained["verification_status"]
    assert fresh["what_is_not_claimed"] == retained["what_is_not_claimed"]
    assert fresh["checks"] == retained["checks"]
    assert fresh["parent_contracts"] == retained["parent_contracts"]
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


def test_the_frozen_shape_of_every_section():
    report = load(EVIDENCE)
    assert sorted(report) == sorted(TOP_LEVEL_KEYS)
    assert sorted(report["sections"]) == sorted(SECTION_NAMES)
    for name, keys in FROZEN_SECTION_SHAPE.items():
        assert sorted(report["sections"][name]) == keys, name
    surgery = section("S1_surgery_and_collar")
    assert sorted(surgery["collar"]) == ["carrier", "cell_set", "cells", "definition",
                                         "normal", "orientation", "phase_extent",
                                         "radial_extent", "radial_index", "side_normals"]
    assert sorted(surgery["declared_singular_locus"]) == [
        "annual_seam", "collision_branch", "collision_parameter",
        "collision_parameter_on_the_branch", "discriminant_at_the_collision", "discriminant_form",
        "discriminant_is_the_cleared_resultant", "factor_multiplicities", "number_of_terms",
        "sign_rule_off_the_branch", "total_degree"]
    assert sorted(surgery["excision"]) == [
        "boundary_components", "carried_out", "carrier_after_the_surgery", "exactness",
        "excised_cell_set", "excised_cells", "sides", "sides_are_distinct_objects",
        "two_sides_replace_the_singular_carrier"]
    spirals = section("S2_spirals_and_chirality")
    assert sorted(spirals["spirals"]) == ["inner", "outer"]
    for row in spirals["spirals"].values():
        assert sorted(row) == ["after_twelve_turns", "after_twenty_four_turns", "angular_step",
                              "chirality_sign", "declared_map", "handedness", "radial_advance",
                              "rotation_compounded_with_a_radial_advance", "side", "start",
                              "well_defined_on_the_declared_lattice"]
    flux = section("S3_flux_and_attribution")
    assert sorted(flux["flux_after_terms"]) == ["inner", "outer"]
    for row in flux["flux_after_terms"].values():
        assert sorted(row) == ["normal", "resource", "term"]
    assert sorted(flux["attribution"]) == ["attributed_rise", "attributed_to", "rule",
                                           "unattributed_rise", "verdict"]
    assert sorted(flux["same_chirality_control"]) == [
        "chirality_condition", "control", "decided_by_a_count", "flux_after", "rejected_by",
        "rejection_reasons", "rose"]
    side_o = section("S4_side_O_obstruction")
    assert sorted(side_o["written_record"]) == [
        "boundary_object", "collar_normal", "kind", "locus_branch", "parameter_p", "parameter_q",
        "record_id", "vanishing_factor_value", "written_by"]
    assert sorted(side_o["discharge"]) == ["agrees", "reasons", "rejected_by", "verdict", "written"]
    for row in side_o["controls"]:
        assert sorted(row) == ["control", "rejected_by_the_declared_condition",
                               "rejection_reasons", "verdict", "written"]
    side_i = section("S5_side_I_arrival")
    assert sorted(side_i["arrival"]) == [
        "angular_step", "excess", "excised_cells_on_the_orbit",
        "orbit_cells_on_the_declared_lattice", "phase_congruence_holds", "radial_advance",
        "radial_distance_covered", "reasons", "slack", "solvable", "start", "step_budget",
        "steps", "target", "verdict", "within_budget"]
    assert sorted(side_i["step_accounting"]) == [
        "budget", "cycles", "end_block_steps", "phases_per_cycle",
        "the_budget_is_the_declared_convention", "total_with_the_inherited_end_block", "unit"]
    resources = section("S6_resource_accounting")
    assert sorted(resources["carried_remainder"]) == ["fast", "slow_layers", "slow_total", "total"]
    assert sorted(resources["surgery_split"]) == ["fast", "flux_terms", "per_layer", "shares",
                                                  "shares_derived_from", "totals"]
    assert sorted(resources["layer_sealing"]) == ["all_layers_sealed", "bound", "layers",
                                                  "sealed_at_every_seam",
                                                  "the_bound_applies_layer_by_layer"]
    for row in resources["seam_redistribution"]["seams"]:
        assert sorted(row) == ["contents", "cycle", "memory_layer", "per_layer_drift",
                              "sealed_layer_by_layer", "total"]
    projection = section("S7_projection")
    assert sorted(projection["checked_as_a_map"]) == [
        "accepted", "images", "reasons", "single_valued_on_the_declared_domain",
        "the_two_sides_have_distinct_images", "the_two_spirals_have_distinct_images", "verdict"]
    assert sorted(projection["declared_codomain"]) == ["rotation_senses", "sides"]
    baselines = section("S8_baselines")
    assert sorted(baselines["first_scheme"]) == [
        "amplitude_floor", "attained_at", "branches", "frozen_level_of_the_ten_middle_sides",
        "on_the_discriminant_variety", "real_branches_at_the_witness", "source"]
    for row in baselines["first_scheme"]["branches"]:
        assert sorted(row) == ["abs_E_0_upper_bound", "abs_h_upper_bound", "below_the_frozen_level",
                              "isolation_interval", "refined_interval"]
    assert sorted(baselines["closure_reading"]) == [
        "amplitude", "correctly_rounded_prefix", "derivative_discriminant",
        "isolation_interval", "no_rational_root", "nontrivial_branch_equation",
        "quotient_quadratic_discriminant_enclosure", "real_exits",
        "the_other_two_exits_are_non_real"]
    assert sorted(baselines["level_reading"]) == [
        "closed_form", "closed_form_verified_in", "equation", "largest_branch_amplitude",
        "largest_branch_amplitude_enclosure", "negative_branch_enclosure",
        "positive_branch_enclosure", "real_branches", "sigma", "sigma_is_positive", "substitution"]
    assert sorted(baselines["ordering"]) == ["asserted_exactly", "between", "statement"]
    controls = section("S9_controls")
    assert sorted(controls["sampling_change_invariance"]) == [
        "composition_only_difference", "composition_only_reading_moves", "control",
        "declared_compositions", "fused_reading", "not_read_as_a_change_of_mechanism",
        "readings", "readings_unchanged", "the_composition_only_reading_is_an_artefact"]
    assert sorted(controls["separated_uncertainty"]) == [
        "control", "fused_control", "pooling_control", "seams", "terms",
        "three_terms_present_separately_at_every_seam"]
    for row in controls["separated_uncertainty"]["seams"]:
        assert sorted(row) == ["bias", "cycle", "mapping", "recorded_separately", "sampling"]


def test_the_collar_the_orientation_and_the_excision_are_exact():
    surgery = section("S1_surgery_and_collar")
    locus = surgery["declared_singular_locus"]
    assert locus["collision_parameter"] == {"p": "-2", "q": "7019/8"}
    assert locus["collision_parameter_on_the_branch"] is True
    assert "256 p^2 + 76 p + 43/8" in locus["collision_branch"]
    assert "2048 p^2 + 608 p - 8 q + 43" in locus["discriminant_form"]
    assert locus["discriminant_at_the_collision"] == "0"
    assert locus["discriminant_is_the_cleared_resultant"] is True
    assert locus["total_degree"] == 12
    assert locus["number_of_terms"] == 52
    assert locus["factor_multiplicities"] == {"8*p + 1": 6, "8*q + 1": 2, "64*q + 17": 2,
                                              "2048*p^2 + 608*p - 8*q + 43": 1}
    seam = locus["annual_seam"]
    assert seam["cycle_phases"] == 12
    assert seam["seam_phase"] == 0
    assert seam["time_coupling"][:2] == ["-31/512", "-15/512"]
    assert seam["time_coupling"][2:] == ["0"] * 10
    assert seam["coupling_maximum"] == "31/512"
    assert seam["coupling_maximum_at_phase"] == 0

    collar = surgery["collar"]
    assert collar["radial_index"] == 0
    assert collar["cells"] == 12
    assert collar["radial_extent"] == 1
    assert collar["cell_set"] == [[0, phase] for phase in range(12)]
    assert collar["normal"]["vector"] == ["1", "1"]
    assert collar["normal"]["radial_component"] == "1"
    assert collar["normal"]["phase_component"] == "1"
    assert collar["orientation"]["ordered_frame"] == ["radial outward", "phase increasing"]
    assert collar["orientation"]["orientation_sign"] == "1"
    assert collar["orientation"]["the_two_side_normals_are_opposite"] is True
    assert collar["side_normals"] == {"outer": ["1", "1"], "inner": ["-1", "-1"]}

    excision = surgery["excision"]
    assert excision["excised_cells"] == 12
    assert excision["excised_cell_set"] == [[0, phase] for phase in range(12)]
    assert excision["boundary_components"] == 2
    assert excision["two_sides_replace_the_singular_carrier"] is True
    assert excision["sides_are_distinct_objects"] is True
    for side, radial in (("outer", "1"), ("inner", "-1")):
        assert excision["sides"][side]["radial_index"] == radial
        assert excision["sides"][side]["cells"] == 12
        assert excision["sides"][side]["cell_set"] == [[int(radial), phase] for phase in range(12)]
        assert excision["sides"][side]["disjoint_from_the_other_side"] is True


def test_the_two_spirals_carry_opposite_declared_chirality():
    spirals = section("S2_spirals_and_chirality")
    outer, inner = spirals["spirals"]["outer"], spirals["spirals"]["inner"]
    assert outer["chirality_sign"] == "+1"
    assert inner["chirality_sign"] == "-1"
    assert spirals["opposite_chirality_declared"] is True
    assert "sigma_outer = -sigma_inner" in spirals["chirality_condition"]
    for row in (outer, inner):
        assert row["radial_advance"] == "1/12"
        assert row["rotation_compounded_with_a_radial_advance"] is True
        assert row["well_defined_on_the_declared_lattice"] is True
        assert Fraction(row["radial_advance"]) != 0
    assert outer["angular_step"] == 1 and inner["angular_step"] == -1
    assert "positive" in outer["handedness"] and "negative" in inner["handedness"]
    assert outer["after_twenty_four_turns"] == ["3", 0]
    assert inner["after_twenty_four_turns"] == ["1", 0]
    accepted = spirals["chirality_condition_on_the_declared_pair"]
    assert accepted["accepted"] is True
    assert accepted["signs_are_opposite"] is True
    assert accepted["decided_by_a_count"] is False
    degenerate = spirals["degenerate_spiral_controls"]
    assert degenerate["both_rejected"] is True
    assert degenerate["pure_rotation"]["reasons"]
    assert degenerate["pure_radial_advance"]["reasons"]


def test_the_flux_rises_and_the_rise_is_attributed():
    flux = section("S3_flux_and_attribution")
    assert Fraction(flux["flux_before"]) == 0
    assert Fraction(flux["flux_after"]) == 2
    assert Fraction(flux["flux_after"]) > Fraction(flux["flux_before"])
    assert flux["strictly_greater"] is True
    assert flux["flux_after"] == flux["flux_after_from_the_rise_formula"]
    assert flux["flux_after_terms"]["outer"]["term"] == "13/12"
    assert flux["flux_after_terms"]["inner"]["term"] == "11/12"
    assert Fraction(flux["rise"]) == 2
    assert "w n_phase (sigma_outer - sigma_inner)" in flux["rise_formula"]
    assert flux["attribution"]["verdict"] == "Attributed"
    assert flux["attribution"]["attributed_rise"] == "2"
    assert flux["attribution"]["unattributed_rise"] == "0"
    assert "before the helical introduction" in flux["flux_before_reason"]

    same = flux["same_chirality_control"]
    assert same["chirality_condition"]["accepted"] is False
    assert same["chirality_condition"]["reasons"]
    assert same["rejected_by"] == "the declared chirality condition sigma_outer = -sigma_inner"
    assert same["decided_by_a_count"] is False
    assert same["flux_after"] == "0"
    assert same["rose"] is False
    assert Fraction(same["flux_after"]) <= Fraction(flux["flux_before"])

    sign_pairs = {row["signs"]: row for row in flux["sign_pairs"]}
    assert sign_pairs["+1/-1"]["rose"] is True
    assert sign_pairs["+1/+1"]["rose"] is False
    assert sign_pairs["-1/+1"]["chirality_condition"] == "Accepted"
    assert sign_pairs["-1/+1"]["rose"] is False
    assert sign_pairs["-1/+1"]["flux_after"] == "-2"

    unattributed = flux["unattributed_control"]
    assert Fraction(unattributed["flux_observed"]) == Fraction(17, 8)
    assert Fraction(unattributed["unattributed_rise"]) == Fraction(1, 8)
    assert unattributed["verdict"] == "Unattributed"

    cancellation = flux["radial_cancellation"]
    assert cancellation["radial_contributions"] == {"outer": "1/12", "inner": "-1/12"}
    assert Fraction(cancellation["radial_sum"]) == 0
    assert Fraction(cancellation["angular_sum"]) == 2
    assert "angular component alone" in cancellation["reading"]

    radial = flux["radial_normal_control"]
    assert radial["verdict"] == "FAILED_TO_DISCRIMINATE"
    assert set(radial["flux_after_by_sign_pair"].values()) == {"0"}


def test_side_O_writes_out_and_discharges_the_obstruction():
    side_o = section("S4_side_O_obstruction")
    assert side_o["side"] == "outer"
    assert side_o["declared_obstruction"]["explicit_object_declared"] is True
    assert side_o["discharge_is_a_condition_on_the_record"] is True
    assert "written out" in side_o["discharge_condition"]
    record = side_o["written_record"]
    assert record["record_id"] == "O-1"
    assert record["parameter_p"] == "-2"
    assert record["parameter_q"] == "7019/8"
    assert record["vanishing_factor_value"] == "0"
    assert record["collar_normal"] == "(1, 1)"
    assert record["boundary_object"]
    assert side_o["computed_values"]["parameter_q"] == "7019/8"
    assert side_o["computed_values"] == {key: value for key, value in record.items()
                                         if key in side_o["computed_values"]}
    discharge = side_o["discharge"]
    assert discharge["verdict"] == "Discharged"
    assert discharge["written"] is True and discharge["agrees"] is True
    assert discharge["reasons"] == []
    assert len(side_o["controls"]) == 3
    unwritten, implicit, disagreeing = side_o["controls"]
    assert unwritten["verdict"] == "Rejected" and unwritten["written"] is False
    assert "not written out" in unwritten["rejection_reasons"][0]
    assert implicit["verdict"] == "Rejected" and implicit["written"] is False
    assert "implicit" in implicit["rejection_reasons"][0]
    assert disagreeing["verdict"] == "Rejected" and disagreeing["written"] is True
    assert "does not equal" in disagreeing["rejection_reasons"][0] \
        or "7019/7" in disagreeing["rejection_reasons"][0]
    assert all(row["rejected_by_the_declared_condition"] is True for row in side_o["controls"])


def test_side_I_arrives_within_the_declared_step_budget():
    side_i = section("S5_side_I_arrival")
    assert side_i["side"] == "inner"
    assert side_i["declared_step_budget"] == 36
    target = side_i["declared_time_domain_target"]
    assert target["radial_index"] == "1" and target["phase"] == 0
    assert side_i["declared_start"] == {"radial_index": "-1", "phase": 0}
    arrival = side_i["arrival"]
    assert arrival["solvable"] is True
    assert arrival["steps"] == 24
    assert arrival["within_budget"] is True
    assert arrival["verdict"] == "ArrivedWithinBudget"
    assert arrival["slack"] == 12
    assert arrival["excess"] == 0
    assert arrival["step_budget"] == side_i["declared_step_budget"]
    assert arrival["phase_congruence_holds"] is True
    assert arrival["radial_distance_covered"] == side_i["collar_diameter"] == "2"
    assert side_i["radial_distance_equals_the_collar_diameter"] is True
    assert arrival["orbit_cells_on_the_declared_lattice"] == [[-1, 0], [0, 0], [1, 0]]
    assert arrival["excised_cells_on_the_orbit"] == [[0, 0]]
    accounting = side_i["step_accounting"]
    assert accounting["cycles"] == 3 and accounting["phases_per_cycle"] == 12
    assert accounting["budget"] == 36
    assert accounting["end_block_steps"] == 2
    assert accounting["total_with_the_inherited_end_block"] == 42
    assert arrival["steps"] <= accounting["budget"] <= \
        accounting["total_with_the_inherited_end_block"]

    over, swapped, early = side_i["controls"]
    assert over["verdict"] == "Rejected_OverBudget"
    assert over["steps"] == 48 and over["within_budget"] is False and over["excess"] == 12
    assert over["rejection_reasons"]
    assert swapped["verdict"] == "Rejected_NoArrival" and swapped["solvable"] is False
    assert swapped["rejection_reasons"]
    assert early["steps"] == 12 and early["excised_cells_on_the_orbit"] == [[0, 0]]
    failed = side_i["failed_to_discriminate"]
    assert failed["verdict"] == "FAILED_TO_DISCRIMINATE"
    assert failed["steps_under_minus_one"] == failed["steps_under_plus_one"] == 24
    assert failed["why"]


def test_the_resources_are_not_created_and_the_layers_are_sealed():
    resources = section("S6_resource_accounting")
    carried = resources["carried_remainder"]
    assert carried["fast"] == "1/4"
    assert carried["slow_layers"] == {"mixed": "1/8", "thermocline": "1/4", "deep": "1/2"}
    assert Fraction(carried["slow_total"]) == sum(
        Fraction(value) for value in carried["slow_layers"].values()) == Fraction(7, 8)
    assert Fraction(carried["total"]) == Fraction(9, 8)

    split = resources["surgery_split"]
    assert split["shares"] == {"outer": "13/24", "inner": "11/24"}
    assert Fraction(split["shares"]["outer"]) + Fraction(split["shares"]["inner"]) == 1
    assert split["flux_terms"] == {"outer": "13/12", "inner": "11/12"}
    assert "derived" in split["shares_derived_from"]
    for layer, row in split["per_layer"].items():
        assert Fraction(row["outer"]) + Fraction(row["inner"]) == Fraction(row["sum"])
        assert row["sum"] == carried["slow_layers"][layer]
        assert row["equals_the_carried_content"] is True
    assert Fraction(split["fast"]["outer"]) + Fraction(split["fast"]["inner"]) == Fraction(1, 4)
    assert Fraction(split["totals"]["outer"]) + Fraction(split["totals"]["inner"]) \
        == Fraction(carried["total"]) == Fraction(9, 8)
    assert resources["no_resource_created_by_the_surgery"] is True
    assert resources["per_layer_sums_equal_the_carried_remainder"] is True
    assert resources["grand_total_unchanged"] is True

    sealing = resources["layer_sealing"]
    assert sealing["bound"] == {"mixed": "0", "thermocline": "0", "deep": "0"}
    assert sealing["all_layers_sealed"] is True
    assert sealing["the_bound_applies_layer_by_layer"] is True
    assert sealing["sealed_at_every_seam"] is True
    for row in sealing["layers"].values():
        assert Fraction(row["drift"]) == 0
        assert Fraction(row["post_surgery_content"]) == Fraction(row["carried_content"])
        assert row["sealed"] is True

    cancelling = resources["total_cancelling_control"]
    assert Fraction(cancelling["total_drift"]) == 0
    assert cancelling["total_looks_sealed"] is True
    assert cancelling["violating_layers"] == ["mixed", "deep"]
    assert cancelling["verdict"] == "LayerWiseViolation"
    assert cancelling["cancelled_by_the_total"] is False

    seams = resources["seam_redistribution"]["seams"]
    assert [row["cycle"] for row in seams] == ["C1", "C2", "C3"]
    for row in seams:
        assert Fraction(row["total"]) == Fraction(7, 8)
        assert sum(Fraction(value) for value in row["per_layer_drift"]) == 0
        assert row["memory_layer"] == "deep"
        assert row["sealed_layer_by_layer"] is True
    assert resources["seam_redistribution"]["memory_layer_stable"] is True
    assert resources["seam_redistribution"]["slow_total_conserved_at_every_seam"] is True
    assert seams[0]["contents"] == ["7/64", "1/4", "33/64"]
    assert seams[0]["per_layer_drift"] == ["-1/64", "0", "1/64"]

    zero = resources["zero_redistribution_control"]
    assert zero["per_layer_drift"] == ["0", "0", "0"]
    assert zero["total_conserved"] is True
    assert "does no work" in zero["verdict"]

    atmospheric = resources["atmospheric_memory_control"]
    assert Fraction(atmospheric["atmospheric_only"]["carried_memory_at_the_seam"]) == 0
    assert atmospheric["atmospheric_only"]["lost"] is True
    assert Fraction(atmospheric["with_the_slow_component"]["carried_memory_at_the_seam"]) \
        == Fraction(7, 8)
    assert atmospheric["with_the_slow_component"]["kept"] is True
    assert atmospheric["the_split_does_work"] is True


def test_the_projection_is_checked_as_a_map():
    projection = section("S7_projection")
    assert projection["verdict"] == "Accepted"
    assert projection["declared_projection"] == {
        "inner_side": "supplying_or_injecting_side",
        "inner_spiral": "rotation_sense_negative",
        "outer_side": "sealing_side",
        "outer_spiral": "rotation_sense_positive",
    }
    assert sorted(projection["declared_domain"]) == ["inner_side", "inner_spiral", "outer_side",
                                                     "outer_spiral"]
    assert projection["declared_codomain"]["sides"] == ["sealing_side",
                                                        "supplying_or_injecting_side"]
    assert projection["declared_codomain"]["rotation_senses"] == ["rotation_sense_positive",
                                                                  "rotation_sense_negative"]
    checked = projection["checked_as_a_map"]
    assert checked["accepted"] is True
    assert checked["single_valued_on_the_declared_domain"] is True
    assert checked["the_two_sides_have_distinct_images"] is True
    assert checked["the_two_spirals_have_distinct_images"] is True
    assert checked["reasons"] == []
    assert len(projection["controls"]) == 3
    identifying, single_sense, wrong_codomain = projection["controls"]
    assert identifying["verdict"] == "Rejected"
    assert "distinct projections" in identifying["rejection_reasons"][0]
    assert single_sense["verdict"] == "Rejected"
    assert "two distinct rotation senses" in single_sense["rejection_reasons"][0]
    assert wrong_codomain["verdict"] == "Rejected"
    assert projection["no_cold_heat_quantity_asserted"] is True
    assert projection["the_projection_is_declared_only"] is True
    assert projection["the_cold_heat_reading_exists_only_as_this_map"] is True


def test_the_exact_baselines_are_reproduced_and_ordered():
    baselines = section("S8_baselines")
    first = baselines["first_scheme"]
    assert first["amplitude_floor"] == "J_inf = 1"
    assert first["attained_at"] == "(p, q) = (-2, 17/10)"
    assert first["on_the_discriminant_variety"] is False
    assert first["real_branches_at_the_witness"] == 2
    assert first["frozen_level_of_the_ten_middle_sides"] == "1"
    for row in first["branches"]:
        assert Fraction(row["abs_h_upper_bound"]) < 1
        assert Fraction(row["abs_E_0_upper_bound"]) < 1
        assert row["below_the_frozen_level"] is True

    closure = baselines["closure_reading"]
    assert closure["nontrivial_branch_equation"] == "h^3 + 8 h^2 + 64 h - 320 = 0"
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
    assert level["real_branches"] == 2
    assert level["largest_branch_amplitude"] == "2 + sqrt(8 sqrt(17) - 20)"
    assert level["sigma"] == "8 sqrt(17) - 20"
    assert level["sigma_is_positive"] is True
    assert "Q(sqrt(17))" in level["closed_form_verified_in"]
    assert "u^4 + 40 u^2 - 688" in level["substitution"]
    level_low = Fraction(level["largest_branch_amplitude_enclosure"][0])
    level_high = Fraction(level["largest_branch_amplitude_enclosure"][1])
    assert Fraction(5) < level_low < level_high < Fraction(6)
    assert level_low > Fraction(4) > high > low > Fraction(1)
    negative = level["negative_branch_enclosure"]
    assert Fraction(-6) < Fraction(negative[0]) < Fraction(negative[1]) < Fraction(-5)

    ordering = baselines["ordering"]
    assert ordering["asserted_exactly"] is True
    assert ordering["statement"] == "1 < 3.2035072879526181... < 2 + sqrt(8 sqrt(17) - 20)"
    assert len(ordering["between"]) == 3


def test_the_inherited_controls_still_run_and_the_failures_are_retained():
    controls = section("S9_controls")
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

    separated = controls["separated_uncertainty"]
    assert separated["three_terms_present_separately_at_every_seam"] is True
    assert separated["fused_control"]["verdict"] == "Rejected"
    assert Fraction(separated["fused_control"]["fused_figure"]) == Fraction(11, 256)
    assert separated["terms"] == ["mapping", "bias", "sampling"]
    assert len(separated["seams"]) == 3
    for row in separated["seams"]:
        assert row["recorded_separately"] is True
        assert Fraction(row["mapping"]) == Fraction(1, 64)
        assert Fraction(row["bias"]) == Fraction(1, 64)
        assert Fraction(row["sampling"]) == Fraction(3, 256)
    assert separated["pooling_control"]["pooled"]

    assert controls["atmospheric_memory_loss"]["atmospheric_only"]["lost"] is True
    assert len(controls["inherited_controls_still_run"]) == 3
    failed = controls["failed_controls"]
    assert len(failed) == 2
    for row in failed:
        assert row["outcome"] == "FAILED_TO_DISCRIMINATE"
        assert row["why"]
    assert any("radial-normal" in row["control"] for row in failed)
    assert any("arrival step count" in row["control"] for row in failed)
    assert controls["controls_that_did_discriminate"]


def test_the_boundaries_are_retained_and_nothing_physical_is_claimed():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["protected"] == contract["protected"]
    assert report["residual"] == contract["residual"]
    assert report["level"] == contract["level"]
    assert report["tooling"]["declared_not_native_authority"] is True
    assert report["tooling"]["polynomial_library"] == "sympy"
    assert report["tooling"]["exact_only"] is True
    assert report["tooling"]["not_implemented"]
    claims = report["what_is_not_claimed"]
    assert claims["native_certificate"] is False
    assert claims["native_admission"] == "NotGranted"
    assert claims["stable_api_change"] is False
    assert claims["physical_claim"] is False
    assert claims["forecast"] is False
    assert claims["meteorological_data_used"] is False
    assert claims["no_data_read_or_used"] is True
    assert claims["cold_heat_reading_exists_only_as_the_declared_projection"] is True
    assert claims["no_cold_heat_wind_ocean_plateau_or_forecast_quantity_asserted"] is True
    assert claims["the_surgery_is_a_declared_construction_not_a_physical_mechanism"] is True
    assert claims["opposite_chirality_necessity_not_claimed"] is True
    assert claims["no_native_admission_no_seal_no_transport_no_terminology_home"] is True
    assert claims["no_rust_source_or_lock_changed"] is True
    assert claims["no_contract_or_note_edited"] is True
    assert claims["no_claim_added_to_docs_claims_toml"] is True


def test_observational_verification_is_unavailable_and_the_reservation_is_carried():
    report = load(EVIDENCE)
    parent = load(PARENT_CONTRACT)
    status = report["verification_status"]
    assert status["observational"] == "Unavailable"
    assert "Unavailable" in parent["verification_status"]["observational"]
    assert status["data_authenticity_reservation"] \
        == parent["verification_status"]["data_authenticity_reservation"]
    assert "not narrowed to any single stage" in status["data_authenticity_reservation"]
    assert "hashes and same-source read-backs do not remove it" \
        in status["data_authenticity_reservation"]
    assert status["checked_here"]["observational_verification"] == "Unavailable"
    assert status["checked_here"]["no_data_read_or_used"] is True
    assert status["checked_here"]["hashes_and_read_backs_do_not_remove_the_reservation"] is True
    assert report["checks"]["observational_verification_is_recorded_unavailable"] is True
    assert report["checks"]["the_data_authenticity_reservation_is_carried_verbatim"] is True


def test_the_undecided_items_and_the_modelling_choices_are_declared():
    report = load(EVIDENCE)
    undecided = report["undecided"]
    assert len(undecided) == 4
    items = [row["item"] for row in undecided]
    assert any("opposite chirality is necessary" in item for item in items)
    assert any("collar" in item for item in items)
    assert any("projection" in item for item in items)
    assert any("excised collar" in item for item in items)
    for row in undecided:
        assert row["reason"]
        assert row["retained_partial_result"] is not None
    chirality_item = next(row for row in undecided if "opposite chirality" in row["item"])
    retained = chirality_item["retained_partial_result"]
    assert retained["declared_pair_flux"] == "2"
    assert retained["same_chirality_flux"] == "0"
    assert retained["reversed_opposite_pair_flux"] == "-2"
    assert retained["radial_normal_rise_for_every_pair"] == "0"
    assert "another declaration is another run" in chirality_item["reason"]

    choices = report["modelling_choices"]
    for key in ("carrier_and_lattice", "singular_locus", "collar_and_orientation",
                "collar_normal_tilt", "excision_and_the_two_sides", "spiral_declaration",
                "chirality_condition", "flux_pairing", "flux_before_is_the_declared_zero",
                "attribution_rule_and_unattributed_rise", "obstruction_record_and_discharge",
                "arrival_condition_and_role_swap", "step_budget", "resource_split",
                "layer_sealing_bound", "seam_redistribution_and_memory",
                "projection_and_codomain_labels", "baselines", "inherited_controls", "exact_only",
                "external_library", "resource_limits"):
        assert choices[key], key
    assert "declared conventions" in choices["carrier_and_lattice"]
    assert "discriminant collision" in choices["singular_locus"]
    assert "seam" in choices["singular_locus"]
    assert "declared" in choices["collar_and_orientation"]
    assert "rejected" in choices["spiral_declaration"]
    assert "sigma_outer = -sigma_inner" in choices["chirality_condition"]
    assert "not by a count" in choices["chirality_condition"]
    assert "unattributed" in choices["attribution_rule_and_unattributed_rise"]
    assert "unwritten" in choices["obstruction_record_and_discharge"]
    assert "budget" in choices["step_budget"]
    assert "derived from the declared collar flux" in choices["resource_split"]
    assert "layer by layer" in choices["layer_sealing_bound"] or "per layer" in \
        choices["layer_sealing_bound"]
    assert "rlimit" in choices["resource_limits"]
    assert "no floating-point value" in choices["exact_only"]
    assert "not native authority" in choices["external_library"]


def test_the_declared_checks_all_pass_and_name_their_conditions():
    checks = load(EVIDENCE)["checks"]
    assert all(checks.values())
    for name in ("the_collar_has_exactly_two_sides", "the_flux_strictly_rises",
                 "the_rise_is_attributed", "the_same_chirality_pair_is_rejected_by_the_condition",
                 "the_same_chirality_control_does_not_raise_the_flux",
                 "side_O_discharges_a_written_obstruction", "the_unwritten_obstruction_fails",
                 "side_I_arrives_within_the_budget", "the_over_budget_arrival_fails",
                 "the_roles_swapped_fail_both_conditions",
                 "no_resource_is_created_by_the_surgery", "every_layer_is_sealed",
                 "a_layer_wise_violation_is_not_cancelled_by_a_total",
                 "the_projection_is_accepted_as_a_map", "the_baselines_are_reproduced",
                 "the_atmospheric_chain_loses_the_carried_memory",
                 "the_sampling_change_invariance_control_runs",
                 "the_separated_uncertainty_control_runs", "the_failed_controls_are_retained",
                 "both_parent_contracts_are_retained_byte_for_byte"):
        assert checks[name] is True, name


def test_the_two_parent_contracts_are_read_only_and_not_edited_by_this_run():
    report = load(EVIDENCE)
    assert digest(PARENT_CONTRACT) == DECLARED_PARENT_SHA256
    assert digest(PARENT_SUPPLEMENT) == DECLARED_SUPPLEMENT_SHA256
    assert (HERE / "contract.json").exists()
    assert report["what_is_not_claimed"]["no_contract_or_note_edited"] is True
    assert report["checks"]["this_contract_digest_matches_the_declared_one"] is True


def test_the_claim_is_registered_once_and_binds_the_checker_and_the_note():
    """The record carries exactly one claim for this run, and it names the checker and the note.

    The checker and its evidence were written by this session and asserted the claim's ABSENCE,
    because a claim lives in `docs/claims.toml` and is added by the parent session with its note.
    The parent session has now added it; the assertion is inverted rather than dropped, so the
    binding stays checked.
    """
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    assert claims
    matches = [row for row in claims if row.get("claim_id") == CLAIM_ID]
    assert len(matches) == 1, "exactly one claim must be registered for this run"
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for symbol in ("three_cycle_supplement_v1/calibration.py",
                   "three_cycle_supplement_v1/contract.json",
                   "three_cycle_supplement_v1/evidence.json",
                   "0237-singularity-surgery"):
        assert symbol in claim["code_symbol"], symbol
    assert "Undecided" in claim["counterexample_boundary"], "the boundary must retain the undecided necessity"
    assert "NotGranted" in claim["counterexample_boundary"], "the boundary must record native admission"
    assert claim["forbidden_conflations"], "the claim must name its conflations"
    report = load(EVIDENCE)
    assert report["what_is_not_claimed"]["no_claim_added_to_docs_claims_toml"] is True
