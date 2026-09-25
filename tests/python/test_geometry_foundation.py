"""The paired test for the geometry-foundation v1 exact calibration.

The assertions here are about what the retained checker decided by exact arithmetic on a PROPOSAL
ONLY document - 提议性方案, the shared geometric basis of the programme's first three proposals: the
pairing rules enforced as rules with a mis-paired control rejected by exactly the factor by which it
is wrong, the corrected usable fraction at the second Lagrange point with the earlier run's value
carried as superseded, the spot floor and the penumbra diameter at every declared distance, the
etendue ceiling, the pattern scale, the symmetry constraints over three declared Archimedean solids
with the time direction as a declared schedule invariant, the work-region and work-time calculus,
the ablation-level task assignment, the declared obligations and stage one, and the proposal-only
bookkeeping with the termination problem recorded as Unaddressed.

They are not claims about any physical object: no physical effect is asserted anywhere and no
magnitude is asserted for any physical quantity, and the test checks that absence.

The checker is invoked without `-S`; it imports nothing beyond the standard library, so the run is
an external exact calibration with no host package in the path.  The headline quantities are
recomputed
here from the payload's own declared constants - the occulted and usable fractions, the three spot
floors, the etendue ceiling, the duty cycles, the group orders and vertex orbits, and the stage-one
learning sequence - so the numbers are checked twice, once by the checker and once by this test's
independent arithmetic on the same declarations.

The record carries no claim for this run: the parent session adds the claim to `docs/claims.toml`
with its note, so the claim test asserts the claim is ABSENT rather than dropping the binding.
"""

import hashlib
import json
import shutil
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/geometry_foundation_v1"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
EARLIER = ROOT / "experiments/optical_imbalance_proposal_v1"
EARLIER_CONTRACT = EARLIER / "contract.json"
EARLIER_EVIDENCE = EARLIER / "evidence.json"

CLAIM_ID = "adva.bounded-experiment.geometry-foundation.v0"
DECLARED_CONTRACT_SHA256 = "1e07f9a04a9d6d60073a5cb3f726df7d38554608f4d023383314fbff83217750"
DECLARED_EARLIER_CONTRACT_SHA256 = (
    "116913a9369e43666d80cf65a6877164f186fd813955a4d1c05f39777496fa4f")
DECLARED_EARLIER_EVIDENCE_SHA256 = (
    "10e639d3843b29dbad0d815d8599ea5c2ff7c391b1eb1f1a3a8a422036538624")

SCHEMA = "adva.external.geometry-foundation-proposal-calibration.v1"
PROPOSAL_STATUS = "PROPOSAL ONLY - 提议性方案"
NO_NONE = "none"
UNASSESSED = "unaddressed"
NO_DATA = "none"
SUPERSEDED = "Superseded"
UNADDRESSED = "Unaddressed"

FROZEN_ASSERTION_COUNT = 451
FROZEN_CHECK_COUNT = 73
FROZEN_CONTROL_COUNT = 18
FROZEN_FAILED_CONTROL_COUNT = 1
FROZEN_UNDECIDED_COUNT = 8
FROZEN_MODELLING_CHOICE_COUNT = 20
FROZEN_DECLARED_CONSTANT_COUNT = 30
FROZEN_SECTION_COUNT = 11

SECTION_NAMES = (
    "R1_pairing_rules", "R2_usable_fraction", "R3_spot_floor", "R4_etendue_ceiling",
    "R5_pattern_scale", "R6_symmetry_constraints", "R7_work_region_and_time",
    "R8_ablation_level_assignment", "R9_declared_obligations", "R10_stage_one",
    "R11_proposal_only_bookkeeping",
)

TOP_LEVEL_KEYS = (
    "acceptance", "assertions", "checker_sha256", "checks", "cited_artifacts", "contract",
    "contract_sha256", "contract_sha256_declared", "controls_summary", "corrects",
    "declared_constants", "declared_constants_count",
    "declared_inputs_are_declared_and_not_measured", "declared_inputs_statement", "level",
    "limits", "modelling_choices", "question", "residual",
    "schema", "sections", "status", "tooling", "undecided", "verification_status", "version",
    "what_is_not_claimed",
)

FROZEN_SECTION_SHAPE = {
    "R1_pairing_rules": [
        "accepted_pairings", "failed_controls", "failed_controls_count", "mispaired_control",
        "penumbra_mispaired_control", "penumbra_rule", "reading", "rule_count", "rules",
        "the_declared_angular_kinds", "the_enforcement_is_of_the_declared_kind",
        "the_full_angular_size_is_twice_the_angular_radius", "the_rules_are_enforced_not_prose",
        "the_two_accepted_pairings_agree_exactly",
    ],
    "R2_usable_fraction": [
        "pairing_used", "platform_count", "platforms", "reading", "rule",
        "the_bracket_of_about_0_149", "the_bracket_of_about_0_851", "the_correction",
        "the_occulted_fraction", "the_occulted_fraction_in_decimal",
        "the_occulted_fraction_is_about_851_thousandths", "the_ratio_like_with_like",
        "the_two_fractions_sum_to_exactly_one", "the_usable_fraction_is_about_149_thousandths",
        "theta_earth_angular_diameter_at_the_second_lagrange_point",
        "theta_earth_angular_radius_at_the_second_lagrange_point",
        "theta_sun_angular_radius_at_the_second_lagrange_point",
        "theta_sun_full_angular_size_at_the_second_lagrange_point", "usable_fraction",
        "usable_fraction_in_decimal",
    ],
    "R3_spot_floor": [
        "earth_diameter", "largest_floor", "platform_count", "platforms", "reading", "rule",
        "smallest_floor", "the_floor_uses_the_full_angular_size",
        "the_l2_floor_exceeds_the_earths_diameter", "the_penumbra_diameter_form",
        "the_penumbra_diameter_form_is_stated_beside_the_floor",
    ],
    "R4_etendue_ceiling": [
        "control", "declared_spectral_radiance", "declared_wavelength", "per_mode_ceiling",
        "per_mode_ceiling_in_decimal", "reading", "rule", "the_ceiling_is_one_microwatt_per_mode",
        "what_the_ceiling_forces",
    ],
    "R5_pattern_scale": [
        "ap_over_the_coherence_length",
        "coarser_interference_structure_needs_an_aperture_below_the_coherence_length",
        "coarser_structure_statement", "control", "declared_aperture", "declared_coherence_length",
        "finer_structure_is_washed_out_by_the_extended_source", "finer_structure_statement",
        "platform_count", "platform_scales", "reading", "rule",
        "the_declared_aperture_is_not_below_the_declared_coherence_length",
        "the_scale_is_the_spot_floor_of_R3",
    ],
    "R6_symmetry_constraints": [
        "control_count", "controls", "declared_reading",
        "every_declared_solid_has_its_declared_order_and_its_orbit_count",
        "lorentz_rotation_part", "reading", "solids", "solids_count",
        "the_point_group_is_a_subgroup_of_SO3",
        "the_reading_is_declared_and_not_derived_from_a_spacetime_model",
        "the_subgroup_of_SO3_is_the_rotation_part", "the_time_direction",
    ],
    "R7_work_region_and_time": [
        "control_count", "controls", "declared_constellation", "geometric_floor_used",
        "no_step_is_chosen_in_flight", "platforms", "reading", "regions",
        "regions_and_times_must_be_computed_in_advance", "rule", "schedule", "schedule_step_count",
        "the_duty_cycle_of_a_region_under_the_relay",
        "the_duty_cycle_of_one_platform_over_one_region", "the_schedule_is_computed_in_advance",
        "the_sweep_due_to_motion",
    ],
    "R8_ablation_level_assignment": [
        "assignment_count", "assignments", "control_count", "controls", "declared_level_count",
        "declared_level_values", "declared_levels",
        "declared_matched_to_the_declared_ablation_levels_of_the_target_medium",
        "every_task_is_assigned_to_a_declared_level", "no_level_outside_the_declared_set_is_used",
        "no_magnitude_of_any_real_physical_quantity_is_used",
        "no_task_is_assigned_to_a_platform", "reading", "rule", "tasks_per_declared_level",
        "the_matching_is_declared",
    ],
    "R9_declared_obligations": [
        "declared_error_magnitude_region_indices", "declared_error_steps",
        "every_counterpart_is_rejected", "every_obligation_has_a_falsifiable_counterpart",
        "learned_error_count", "learned_errors", "obligation_count", "obligations", "reading",
        "the_counterparts_are_executed_here",
    ],
    "R10_stage_one": [
        "aggregated", "computed", "declared_material_units", "declared_recipient_count",
        "declared_window", "declared_window_end_month", "declared_window_note_path",
        "declared_window_start_month", "declared_work", "distributed",
        "every_counterpart_is_rejected", "every_invariant_has_a_falsifiable_counterpart",
        "growth_step_count", "growth_steps", "invariant_count", "invariants",
        "material_units_statement", "phase", "phase_control", "phase_is_calibration_not_control",
        "reading", "the_declared_window_wraps",
        "the_material_divides_exactly_among_the_recipients", "the_material_is_declared_not_read",
        "the_network_grows_at_every_declared_growth_step", "the_three_stages_carry_the_same_units",
        "total_declared_launches", "total_declared_learning_units", "units_per_recipient",
    ],
    "R11_proposal_only_bookkeeping": [
        "authorization", "authorizes_nothing", "contract_status", "contract_status_note",
        "data_used", "decides_nothing", "decision", "deployment", "deploys_nothing", "governance",
        "no_governance_assessment", "nothing_said_about_who_might_decide",
        "physical_effect_asserted", "proposal_only_in_chinese_and_english",
        "proposal_only_statement", "reading", "status", "termination_problem",
    ],
}

DECLARED_CONSTANT_VALUES = {
    "astronomical_unit": ("149597870700", "m"),
    "solar_radius": ("695700000", "m"),
    "earth_mean_radius": ("6371000", "m"),
    "near_earth_distance": ("400000", "m"),
    "geostationary_distance": ("35786000", "m"),
    "second_lagrange_distance": ("1500000000", "m"),
    "declared_aperture": ("20", "m"),
    "declared_coherence_length": ("1/2", "m"),
    "spectral_radiance_B": ("1000000", "W m^-2 sr^-1"),
    "wavelength": ("1/1000000", "m"),
    "declared_work_region_distance": ("35786000", "m"),
    "declared_platform_count": ("4", "1"),
    "declared_region_count": ("4", "1"),
    "declared_window_steps": ("12", "1"),
    "declared_sweep_period_steps": ("4", "1"),
    "declared_addresses_per_region_per_step": ("1", "1"),
    "declared_error_step_count": ("3", "1"),
    "declared_error_magnitude_region_indices": ("1", "1"),
    "declared_level_count": ("4", "1"),
    "declared_task_count": ("6", "1"),
    "declared_material_units": ("4096", "1"),
    "declared_recipient_count": ("64", "1"),
    "declared_growth_steps": ("8", "1"),
    "declared_launches_first_step": ("1", "1"),
    "declared_launch_increment": ("1", "1"),
    "declared_learning_units_per_launch": ("4", "1"),
    "declared_window_start_month": ("12", "month_index"),
    "declared_window_end_month": ("1", "month_index"),
    "declared_schedule_period": ("2", "1"),
    "declared_schedule_horizon": ("24", "1"),
}

THETA_SUN_FULL_AT_ONE_AU = "4638000/498659569"
THETA_SUN_RADIUS_AT_L2 = "773000/167886523"
THETA_SUN_FULL_AT_L2 = "1546000/167886523"
THETA_EARTH_RADIUS_AT_L2 = "6371/1500000"
THETA_EARTH_DIAMETER_AT_L2 = "6371/750000"
RATIO_LIKE_WITH_LIKE = "1069605038033/1159500000000"
RATIO_MIS_PAIRED = "1069605038033/2319000000000"
OCCULTED_FRACTION = "1144054937385575376509089/1344440250000000000000000"
USABLE_FRACTION = "200385312614424623490911/1344440250000000000000000"
SUPERSEDED_OCCULTED_FRACTION = "1144054937385575376509089/5377761000000000000000000"
SUPERSEDED_USABLE_FRACTION = "4233706062614424623490911/5377761000000000000000000"
THE_DIFFERENCE = "1144054937385575376509089/1792587000000000000000000"
FLOOR_NEAR_EARTH = "1855200000000/498659569"
FLOOR_GEOSTATIONARY = "165975468000000/498659569"
FLOOR_L2 = "2319000000000000/167886523"
PENUMBRA_NEAR_EARTH = "1865173191380/498659569"
PENUMBRA_GEOSTATIONARY = "165985441191380/498659569"
PENUMBRA_L2 = "2319003357730460/167886523"
PENUMBRA_L2_WITH_THE_RADIUS = "1159503357730460/167886523"
PER_MODE_CEILING = "1/1000000"
EARTH_DIAMETER = "12742000"
FLAG_FINER_CLAIM = "579750000000000/167886523"

CONTROL_ROW_KEYS = (
    "accepted_companion", "claim", "claimed_value", "control", "control_id", "derived_value",
    "discriminates", "outcome", "rejected", "rejected_by", "rejection_reasons", "unit", "verdict",
)

ACCEPTED_COMPANION_KEYS = ("accepted", "claim", "unit", "value", "verdict")

FAILED_CONTROL_KEYS = (
    "control", "control_id", "discriminates", "outcome", "reading",
    "the_rule_that_catches_it_instead", "variant", "why",
)

CONTROL_IDS = (
    "PAIR-RADIUS-DIAMETER", "PAIR-PENUMBRA-RADIUS", "ETENDUE-CEILING", "PATTERN-FINER",
    "SYM-TIME-IN-POINT-GROUP", "SYM-ARBITRARY-PLACEMENT", "WORK-SINGLE-PLATFORM-SUSTAINED",
    "WORK-SELECTED-IN-FLIGHT", "ABL-TASK-TO-PLATFORM", "ABL-LEVEL-OUTSIDE-THE-DECLARED-SET",
    "OBL-SAFETY-BELOW-THE-FLOOR", "OBL-TOPOLOGY-BROKEN", "OBL-IMPACT-NOT-CONTROLLABLE",
    "OBL-ERROR-NOT-TOLERATED", "OBL-MAGNITUDE-ASSERTED", "STAGE-PHASE-CONTROL",
    "STAGE-TOPOLOGY-BROKEN", "STAGE-LEARNING-DELAYED",
)

FORBIDDEN_MAGNITUDE_KEYS = (
    "magnitude", "energy", "power", "forcing", "temperature", "warming", "cooling", "amount",
    "dosage", "intensity", "irradiance", "flux", "effect", "albedo", "rainfall", "precipitation",
)

FORBIDDEN_TIME_KEYS = ("timestamp", "created_at", "started_at", "finished_at", "elapsed",
                       "duration", "elapsed_seconds", "wall_clock")


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


def declared(name):
    """The payload's own exact value for a declared constant, as a Fraction."""
    rows = {row["name"]: row for row in load(EVIDENCE)["declared_constants"]}
    return Fraction(rows[name]["value"])


def key_findings(node, keys, path="", found=None):
    """Every key anywhere under a record that is one of the declared forbidden keys."""
    if found is None:
        found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in keys:
                found.append(path + "/" + str(key))
            key_findings(value, keys, path + "/" + str(key), found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            key_findings(item, keys, path + "/" + str(index), found)
    return found


def controls_in(node, found=None):
    """Every control row anywhere in the payload, by its own declared shape."""
    if found is None:
        found = []
    if isinstance(node, dict):
        if sorted(node) == sorted(CONTROL_ROW_KEYS):
            found.append(node)
        for value in node.values():
            controls_in(value, found)
    elif isinstance(node, (list, tuple)):
        for item in node:
            controls_in(item, found)
    return found


def matrix_multiply(left, right):
    return tuple(tuple(sum(left[row][inner] * right[inner][column] for inner in range(3))
                       for column in range(3)) for row in range(3))


def matrix_determinant(matrix):
    return (matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
            - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
            + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]))


def matrix_apply(matrix, point):
    return tuple(sum(matrix[row][column] * point[column] for column in range(3))
                 for row in range(3))


def group_closure(generators):
    """The group generated by exact integer matrices, recomputed here independently."""
    identity = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    group = {identity}
    frontier = [identity]
    while frontier:
        element = frontier.pop()
        for generator in generators:
            product = matrix_multiply(generator, element)
            if product not in group:
                group.add(product)
                frontier.append(product)
    return group


def orbit_count(group, vertices):
    remaining = set(vertices)
    orbits = 0
    while remaining:
        point = min(remaining)
        remaining -= {matrix_apply(element, point) for element in group} & set(vertices)
        orbits += 1
    return orbits


def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["status"] == "ExternalExactPass"
    assert report["schema"] == SCHEMA
    assert report["version"] == 1
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract"] == "experiments/geometry_foundation_v1/contract.json"
    assert report["contract_sha256"] == digest(CONTRACT) == DECLARED_CONTRACT_SHA256
    assert report["contract_sha256_declared"] == DECLARED_CONTRACT_SHA256
    assert report["assertions"] == FROZEN_ASSERTION_COUNT
    assert report["assertions"] <= contract["budgets"]["max_assertions"]
    assert report["limits"] == contract["budgets"]
    assert contract["budgets"]["child_processes"] == 0
    assert contract["budgets"]["routes"] == 1
    assert contract["budgets"]["correction_replays"] == 1
    assert all(report["checks"].values())
    assert len(report["checks"]) == FROZEN_CHECK_COUNT
    assert report["level"] == contract["level"]
    assert report["question"] == contract["question"]
    assert report["residual"] == contract["residual"]
    assert report["acceptance"] == contract["acceptance"]
    assert contract["status"].startswith(PROPOSAL_STATUS)
    assert report["tooling"]["declared_not_native_authority"] is True
    assert report["tooling"]["exact_only"] is True
    assert report["tooling"]["external_libraries_imported"] == []
    assert report["tooling"]["declared_external_library_available_but_unused"] == "sympy 1.14"
    assert report["tooling"]["not_implemented"]
    assert "RLIMIT_AS" not in CHECKER.read_text(encoding="utf-8")
    assert "RLIMIT_CPU" in CHECKER.read_text(encoding="utf-8")
    assert "RLIMIT_FSIZE" in CHECKER.read_text(encoding="utf-8")
    citations = {row["path"]: row for row in report["cited_artifacts"]}
    assert citations["experiments/optical_imbalance_proposal_v1/contract.json"]["sha256"] \
        == digest(EARLIER_CONTRACT) == DECLARED_EARLIER_CONTRACT_SHA256
    assert citations["experiments/optical_imbalance_proposal_v1/evidence.json"]["sha256"] \
        == digest(EARLIER_EVIDENCE) == DECLARED_EARLIER_EVIDENCE_SHA256
    assert citations["experiments/optical_imbalance_proposal_v1/evidence.json"] \
        ["retained_byte_for_byte"] is True
    assert all(row["retained_byte_for_byte"] for row in report["cited_artifacts"])
    assert report["corrects"]["the_correction_is_carried_and_the_earlier_payload_is_not_edited"]
    assert len(report["corrects"]["pairing_rules"]) == 4
    assert report["corrects"]["pairing_rules"] == contract["corrects"]["pairing_rules"]
    assert len(contract["shared_items"]) == 7
    assert len(contract["declared_obligations"]) == 5
    assert len(report["sections"]) == FROZEN_SECTION_COUNT


def test_the_declared_constants_are_exact_declared_rationals_with_units():
    """Every constant is declared, exact, carries its unit, and is not a measurement of the run."""
    report = load(EVIDENCE)
    rows = {row["name"]: row for row in report["declared_constants"]}
    assert len(rows) == FROZEN_DECLARED_CONSTANT_COUNT
    assert report["declared_constants_count"] == FROZEN_DECLARED_CONSTANT_COUNT
    assert sorted(rows) == sorted(DECLARED_CONSTANT_VALUES)
    for name, (value, unit) in DECLARED_CONSTANT_VALUES.items():
        assert rows[name]["value"] == value, name
        assert rows[name]["unit"] == unit, name
        assert Fraction(value) is not None, name
        assert rows[name]["declared"] is True
        assert rows[name]["measured_here"] is False
        assert rows[name]["read_from_data"] is False
        assert rows[name]["role"]
    assert report["declared_inputs_are_declared_and_not_measured"] is True
    assert "DECLARED input" in report["declared_inputs_statement"]
    assert "none of them is a measurement of this run" in report["declared_inputs_statement"]


def test_the_three_headline_quantities_are_recomputed_independently():
    """The pairing, the floor and the ceiling are recomputed here from the declared constants."""
    astronomical_unit = declared("astronomical_unit")
    solar_radius = declared("solar_radius")
    earth_radius = declared("earth_mean_radius")
    near_earth = declared("near_earth_distance")
    geostationary = declared("geostationary_distance")
    second_lagrange = declared("second_lagrange_distance")
    aperture = declared("declared_aperture")
    radiance = declared("spectral_radiance_B")
    wavelength = declared("wavelength")

    theta_sun_one_au = 2 * solar_radius / astronomical_unit
    theta_sun_radius_l2 = solar_radius / (astronomical_unit + second_lagrange)
    theta_sun_full_l2 = 2 * theta_sun_radius_l2
    theta_earth_radius_l2 = earth_radius / second_lagrange
    assert theta_sun_one_au == Fraction(THETA_SUN_FULL_AT_ONE_AU)
    assert theta_sun_full_l2 == Fraction(THETA_SUN_FULL_AT_L2)
    assert theta_sun_radius_l2 == Fraction(THETA_SUN_RADIUS_AT_L2)
    assert theta_earth_radius_l2 == Fraction(THETA_EARTH_RADIUS_AT_L2)
    assert 2 * theta_earth_radius_l2 == Fraction(THETA_EARTH_DIAMETER_AT_L2)

    # headline quantity one: the corrected occulted and usable fractions, LIKE with LIKE
    ratio = theta_earth_radius_l2 / theta_sun_radius_l2
    assert ratio == Fraction(RATIO_LIKE_WITH_LIKE)
    assert ratio == (2 * theta_earth_radius_l2) / theta_sun_full_l2
    occulted = ratio ** 2
    assert occulted == Fraction(OCCULTED_FRACTION)
    assert 1 - occulted == Fraction(USABLE_FRACTION)
    assert Fraction(17, 20) < occulted <= Fraction(851, 1000)
    assert Fraction(149, 1000) <= 1 - occulted < Fraction(3, 20)
    mis_paired = theta_earth_radius_l2 / theta_sun_full_l2
    assert mis_paired == Fraction(RATIO_MIS_PAIRED)
    assert ratio == 2 * mis_paired
    assert occulted == 4 * mis_paired ** 2

    # headline quantity two: the spot floor and the penumbra diameter at every declared distance
    assert theta_sun_one_au * near_earth == Fraction(FLOOR_NEAR_EARTH)
    assert theta_sun_one_au * geostationary == Fraction(FLOOR_GEOSTATIONARY)
    assert theta_sun_full_l2 * second_lagrange == Fraction(FLOOR_L2)
    assert aperture + theta_sun_one_au * near_earth == Fraction(PENUMBRA_NEAR_EARTH)
    assert aperture + theta_sun_one_au * geostationary == Fraction(PENUMBRA_GEOSTATIONARY)
    assert aperture + theta_sun_full_l2 * second_lagrange == Fraction(PENUMBRA_L2)

    # headline quantity three: the etendue ceiling
    assert radiance * wavelength * wavelength == Fraction(PER_MODE_CEILING)
    assert Fraction(PER_MODE_CEILING) == Fraction(1, 10 ** 6)


def test_the_superseded_value_is_recomputed_and_matches_the_earlier_payload():
    """The earlier run's own retained value is exactly the mis-paired fraction's complement."""
    earlier = load(EARLIER_EVIDENCE)
    earlier_usable = Fraction(earlier["sections"]["R1_derived_bounds"]["l2_usable_fraction"]
                              ["usable_fraction"]["value"])
    solar_radius = declared("solar_radius")
    astronomical_unit = declared("astronomical_unit")
    second_lagrange = declared("second_lagrange_distance")
    earth_radius = declared("earth_mean_radius")
    mis_paired = (earth_radius / second_lagrange) / (2 * solar_radius
                                                     / (astronomical_unit + second_lagrange))
    assert Fraction(SUPERSEDED_OCCULTED_FRACTION) == mis_paired ** 2
    assert Fraction(SUPERSEDED_USABLE_FRACTION) == 1 - mis_paired ** 2
    assert earlier_usable == Fraction(SUPERSEDED_USABLE_FRACTION)
    correction = section("R2_usable_fraction")["the_correction"]
    assert Fraction(correction["superseded_usable_fraction"]["value"]) == earlier_usable
    assert correction["superseded_usable_fraction"]["status"] == SUPERSEDED
    assert Fraction(correction["the_difference_stated_exactly"]["value"]) \
        == earlier_usable - Fraction(USABLE_FRACTION)
    assert Fraction(THE_DIFFERENCE) == earlier_usable - Fraction(USABLE_FRACTION)
    assert Fraction(THE_DIFFERENCE) \
        == 3 * Fraction(OCCULTED_FRACTION) / 4
    assert correction["the_correction_lives_in"] == [
        "docs/research/0240-a-proposal-only-optical-scheme-its-derived-bounds-and-one-erratum.md",
        "experiments/geometry_foundation_v1/contract.json",
    ]


def test_the_pairing_rules_are_enforced_and_the_mispairing_is_rejected():
    pairing = section("R1_pairing_rules")
    assert pairing["rule_count"] == 4
    assert pairing["the_rules_are_enforced_not_prose"] is True
    assert pairing["the_enforcement_is_of_the_declared_kind"] is True
    assert pairing["the_declared_angular_kinds"] == ["angular_radius", "angular_diameter"]
    assert pairing["the_full_angular_size_is_twice_the_angular_radius"] is True
    rules = {row["rule_id"]: row for row in pairing["rules"]}
    assert sorted(rules) == ["P1", "P2", "P3", "P4"]
    assert all(row["enforced_as_a_rule"] and row["enforced_by"] and row["rule"]
               for row in pairing["rules"])
    assert "paired only with an angular radius" in rules["P1"]["rule"]
    assert "LIKE" in rules["P2"]["rule"]
    assert "full angular size" in rules["P3"]["rule"]

    accepted = pairing["accepted_pairings"]
    assert [row["pairing"] for row in accepted] == [
        "an angular radius with an angular radius",
        "an angular diameter with an angular diameter",
    ]
    assert all(row["accepted"] for row in accepted)
    assert [row["ratio"]["value"] for row in accepted] == [RATIO_LIKE_WITH_LIKE,
                                                           RATIO_LIKE_WITH_LIKE]
    assert [row["occulted_fraction"]["value"] for row in accepted] == [OCCULTED_FRACTION,
                                                                      OCCULTED_FRACTION]
    assert pairing["the_two_accepted_pairings_agree_exactly"] is True

    mis_paired = pairing["mispaired_control"]
    assert sorted(mis_paired) == sorted(CONTROL_ROW_KEYS)
    assert mis_paired["control_id"] == "PAIR-RADIUS-DIAMETER"
    assert mis_paired["verdict"] == "Rejected"
    assert mis_paired["rejected"] is True
    assert mis_paired["discriminates"] is True
    assert "P1" in mis_paired["rejected_by"] and "P2" in mis_paired["rejected_by"]
    assert "RADIUS" in mis_paired["control"] and "DIAMETER" in mis_paired["control"]
    assert Fraction(mis_paired["derived_value"]["value"]) == Fraction(OCCULTED_FRACTION)
    assert Fraction(mis_paired["claimed_value"]["value"]) == Fraction(SUPERSEDED_OCCULTED_FRACTION)
    assert Fraction(mis_paired["derived_value"]["value"]) \
        == 4 * Fraction(mis_paired["claimed_value"]["value"])
    assert Fraction(mis_paired["accepted_companion"]["value"]) == Fraction(OCCULTED_FRACTION)
    assert mis_paired["accepted_companion"]["verdict"] == "Accepted_LikeWithLike"
    assert any("factor 4" in reason for reason in mis_paired["rejection_reasons"])
    assert any("one half" in reason for reason in mis_paired["rejection_reasons"])

    penumbra = pairing["penumbra_mispaired_control"]
    assert penumbra["control_id"] == "PAIR-PENUMBRA-RADIUS"
    assert penumbra["rejected"] is True and penumbra["discriminates"] is True
    assert Fraction(penumbra["derived_value"]["value"]) == Fraction(PENUMBRA_L2)
    assert Fraction(penumbra["claimed_value"]["value"]) == Fraction(PENUMBRA_L2_WITH_THE_RADIUS)
    assert Fraction(PENUMBRA_L2) > Fraction(PENUMBRA_L2_WITH_THE_RADIUS)
    assert Fraction(PENUMBRA_L2) - Fraction(PENUMBRA_L2_WITH_THE_RADIUS) \
        == Fraction(THETA_SUN_RADIUS_AT_L2) * declared("second_lagrange_distance")
    assert penumbra["accepted_companion"]["verdict"] == "Accepted_FullAngularSize"

    rule = pairing["penumbra_rule"]
    assert rule["the_spot_floor_uses_the_full_angular_size"] is True
    assert rule["accepted"] is True
    assert Fraction(rule["penumbra_diameter_at_the_second_lagrange_point"]["value"]) \
        == Fraction(PENUMBRA_L2)
    assert Fraction(rule["declared_aperture"]["value"]) == declared("declared_aperture")

    failed = pairing["failed_controls"]
    assert pairing["failed_controls_count"] == FROZEN_FAILED_CONTROL_COUNT
    assert len(failed) == FROZEN_FAILED_CONTROL_COUNT
    assert sorted(failed[0]) == sorted(FAILED_CONTROL_KEYS)
    assert failed[0]["control_id"] == "PAIR-MISLABELLED-DECLARATION"
    assert failed[0]["outcome"] == "FAILED_TO_DISCRIMINATE"
    assert failed[0]["discriminates"] is False
    assert "FAILED CONTROL" in failed[0]["why"]
    assert "repaired or dropped" in failed[0]["why"]
    assert "rule P4" in failed[0]["the_rule_that_catches_it_instead"]
    assert RATIO_MIS_PAIRED in failed[0]["the_rule_that_catches_it_instead"]


def test_the_corrected_usable_fraction_and_the_superseded_value():
    usable = section("R2_usable_fraction")
    assert "LIKE" in usable["rule"]
    assert "angular radius with an angular radius" in usable["pairing_used"]
    assert "angular diameter with an angular diameter" in usable["pairing_used"]
    assert usable["theta_earth_angular_radius_at_the_second_lagrange_point"]["value"] \
        == THETA_EARTH_RADIUS_AT_L2
    assert usable["theta_earth_angular_diameter_at_the_second_lagrange_point"]["value"] \
        == THETA_EARTH_DIAMETER_AT_L2
    assert usable["theta_sun_angular_radius_at_the_second_lagrange_point"]["value"] \
        == THETA_SUN_RADIUS_AT_L2
    assert usable["theta_sun_full_angular_size_at_the_second_lagrange_point"]["value"] \
        == THETA_SUN_FULL_AT_L2
    assert usable["the_ratio_like_with_like"]["value"] == RATIO_LIKE_WITH_LIKE
    assert usable["the_occulted_fraction"]["value"] == OCCULTED_FRACTION
    assert usable["the_occulted_fraction"]["unit"] == "1"
    assert usable["the_occulted_fraction_in_decimal"] == "0.850952"
    assert usable["the_occulted_fraction_is_about_851_thousandths"] is True
    assert usable["the_bracket_of_about_0_851"] == {
        "lower": "17/20", "upper": "851/1000", "lower_is_open": True, "upper_is_closed": True}
    assert usable["usable_fraction"]["value"] == USABLE_FRACTION
    assert usable["usable_fraction"]["unit"] == "1"
    assert usable["usable_fraction_in_decimal"] == "0.149047"
    assert usable["the_usable_fraction_is_about_149_thousandths"] is True
    assert usable["the_bracket_of_about_0_149"] == {
        "lower": "149/1000", "upper": "3/20", "lower_is_closed": True, "upper_is_open": True}
    assert Fraction(OCCULTED_FRACTION) + Fraction(USABLE_FRACTION) == 1
    assert usable["the_two_fractions_sum_to_exactly_one"] is True

    assert usable["platform_count"] == 3
    platforms = {row["name"]: row for row in usable["platforms"]}
    assert sorted(platforms) == ["a geostationary platform", "a near-Earth platform",
                                 "the second Lagrange point"]
    assert sorted(platforms["a near-Earth platform"]) == [
        "declared_distance", "name", "occulted_fraction", "status", "usable_fraction"]
    assert platforms["a near-Earth platform"]["usable_fraction"]["value"] == "1"
    assert platforms["a geostationary platform"]["usable_fraction"]["value"] == "1"
    assert platforms["a near-Earth platform"]["status"] == "declared"
    assert platforms["the second Lagrange point"]["status"] == "derived"
    assert platforms["the second Lagrange point"]["occulted_fraction"]["value"] \
        == OCCULTED_FRACTION
    assert platforms["the second Lagrange point"]["usable_fraction"]["value"] == USABLE_FRACTION
    assert all(row["usable_fraction"]["value"] != SUPERSEDED_USABLE_FRACTION
               for row in usable["platforms"])

    correction = usable["the_correction"]
    assert correction["superseded_usable_fraction_in_decimal"] == "0.787261"
    assert Fraction(787, 1000) < Fraction(SUPERSEDED_USABLE_FRACTION) < Fraction(788, 1000)
    assert correction["the_superseded_value_was_produced_by_a_mis_paired_ratio"] is True
    assert correction["the_mis_paired_ratio"]["value"] == RATIO_MIS_PAIRED
    assert correction["the_factor_by_which_the_mis_paired_fraction_is_wrong"] == "4"
    assert correction["the_difference_in_decimal"] == "0.638214"
    assert correction["the_difference_is_the_superseded_value_minus_the_corrected_one"] is True
    assert correction["the_difference_is_exactly_three_quarters_of_the_corrected_occulted_"
                      "fraction"] is True
    assert correction["the_earlier_payload"] == \
        "experiments/optical_imbalance_proposal_v1/evidence.json"
    assert correction["the_earlier_payload_sha256"] == DECLARED_EARLIER_EVIDENCE_SHA256
    assert correction["the_earlier_payload_is_retained_byte_for_byte"] is True
    assert correction["the_superseded_value_is_used_nowhere_in_this_run"] is True
    assert "SUPERSEDED" in correction["reading"]


def test_the_spot_floor_and_the_penumbra_diameter_at_every_declared_distance():
    floor = section("R3_spot_floor")
    assert "theta_sun * L" in floor["rule"] and "FULL angular size" in floor["rule"]
    assert floor["the_penumbra_diameter_form"].endswith(
        "D + theta_sun(full angular size) * L")
    assert floor["the_penumbra_diameter_form_is_stated_beside_the_floor"] is True
    assert floor["the_floor_uses_the_full_angular_size"] is True
    assert floor["platform_count"] == 3
    platforms = {row["name"]: row for row in floor["platforms"]}
    assert sorted(platforms) == ["a geostationary platform", "a near-Earth platform",
                                 "the second Lagrange point"]
    assert sorted(platforms["the second Lagrange point"]) == [
        "declared_aperture", "declared_distance", "floor", "floor_in_decimal", "name",
        "penumbra_diameter", "penumbra_diameter_over_the_floor", "theta_sun_angular_radius",
        "theta_sun_full_angular_size"]
    near_earth = platforms["a near-Earth platform"]
    assert near_earth["declared_distance"]["value"] == "400000"
    assert near_earth["theta_sun_full_angular_size"]["value"] == THETA_SUN_FULL_AT_ONE_AU
    assert near_earth["theta_sun_angular_radius"]["value"] == "2319000/498659569"
    assert near_earth["floor"]["value"] == FLOOR_NEAR_EARTH
    assert near_earth["floor_in_decimal"] == "3720.373"
    assert near_earth["penumbra_diameter"]["value"] == PENUMBRA_NEAR_EARTH
    geostationary = platforms["a geostationary platform"]
    assert geostationary["declared_distance"]["value"] == "35786000"
    assert geostationary["floor"]["value"] == FLOOR_GEOSTATIONARY
    assert geostationary["floor_in_decimal"] == "332843.242"
    assert geostationary["penumbra_diameter"]["value"] == PENUMBRA_GEOSTATIONARY
    l2 = platforms["the second Lagrange point"]
    assert l2["declared_distance"]["value"] == "1500000000"
    assert l2["theta_sun_full_angular_size"]["value"] == THETA_SUN_FULL_AT_L2
    assert l2["theta_sun_angular_radius"]["value"] == THETA_SUN_RADIUS_AT_L2
    assert l2["floor"]["value"] == FLOOR_L2
    assert l2["floor_in_decimal"] == "13812901.467"
    assert l2["penumbra_diameter"]["value"] == PENUMBRA_L2
    assert l2["penumbra_diameter_over_the_floor"] == "115950167886523/115950000000000"
    assert Fraction(floor["smallest_floor"]["value"]) == Fraction(FLOOR_NEAR_EARTH)
    assert Fraction(floor["largest_floor"]["value"]) == Fraction(FLOOR_L2)
    assert Fraction(FLOOR_L2) > Fraction(FLOOR_GEOSTATIONARY) > Fraction(FLOOR_NEAR_EARTH)
    assert floor["earth_diameter"]["value"] == EARTH_DIAMETER
    assert Fraction(floor["earth_diameter"]["value"]) == 2 * declared("earth_mean_radius")
    assert floor["the_l2_floor_exceeds_the_earths_diameter"] is True
    assert Fraction(FLOOR_L2) > Fraction(EARTH_DIAMETER)


def test_the_etendue_ceiling_the_pattern_scale_and_their_controls():
    ceiling = section("R4_etendue_ceiling")
    assert "B * lambda^2" in ceiling["rule"]
    assert ceiling["declared_spectral_radiance"]["value"] == "1000000"
    assert ceiling["declared_spectral_radiance"]["unit"] == "W m^-2 sr^-1"
    assert ceiling["declared_wavelength"]["value"] == "1/1000000"
    assert ceiling["per_mode_ceiling"]["value"] == PER_MODE_CEILING
    assert ceiling["per_mode_ceiling"]["unit"] == "W"
    assert ceiling["per_mode_ceiling_in_decimal"] == "0.000001"
    assert ceiling["the_ceiling_is_one_microwatt_per_mode"] is True
    assert "free space" in ceiling["what_the_ceiling_forces"]
    assert "phase and coherence only" in ceiling["what_the_ceiling_forces"]
    control = ceiling["control"]
    assert sorted(control) == sorted(CONTROL_ROW_KEYS)
    assert control["control_id"] == "ETENDUE-CEILING"
    assert control["rejected"] is True and control["discriminates"] is True
    assert Fraction(control["derived_value"]["value"]) == Fraction(PER_MODE_CEILING)
    assert Fraction(control["claimed_value"]["value"]) == 2 * Fraction(PER_MODE_CEILING)
    assert control["accepted_companion"]["verdict"] == "Accepted_AtTheCeiling"
    assert any("factor 2" in reason for reason in control["rejection_reasons"])

    pattern = section("R5_pattern_scale")
    assert "theta_sun * L" in pattern["rule"]
    assert pattern["the_scale_is_the_spot_floor_of_R3"] is True
    assert pattern["platform_count"] == 3
    assert all(row["the_pattern_scale_is_the_floor_value_of_that_reference"]
               for row in pattern["platform_scales"])
    sources = {row["name"]: row for row in pattern["platform_scales"]}
    assert sources["the second Lagrange point"]["pattern_scale"]["value"] == FLOOR_L2
    assert sources["the second Lagrange point"]["pattern_scale_source"] == \
        "R3_spot_floor/platforms/the second Lagrange point/floor"
    assert pattern["finer_structure_is_washed_out_by_the_extended_source"] is True
    assert "washed out" in pattern["finer_structure_statement"]
    assert pattern["coarser_interference_structure_needs_an_aperture_below_the_coherence_length"] \
        is True
    assert pattern["declared_coherence_length"]["value"] == "1/2"
    assert pattern["declared_aperture"]["value"] == "20"
    assert pattern["ap_over_the_coherence_length"] == "40"
    assert pattern["the_declared_aperture_is_not_below_the_declared_coherence_length"] is True
    assert "coherence" in pattern["coarser_structure_statement"]
    finer = pattern["control"]
    assert finer["control_id"] == "PATTERN-FINER"
    assert finer["rejected"] is True and finer["discriminates"] is True
    assert Fraction(finer["claimed_value"]["value"]) == Fraction(FLAG_FINER_CLAIM)
    assert Fraction(finer["claimed_value"]["value"]) * 4 \
        == Fraction(finer["derived_value"]["value"])
    assert Fraction(finer["derived_value"]["value"]) == Fraction(FLOOR_L2)


def test_the_symmetry_constraints_with_the_exact_orders_and_orbits():
    """Every declared solid's order and orbit count is recomputed here by exact closure."""
    symmetry = section("R6_symmetry_constraints")
    assert symmetry["solids_count"] == 3
    assert symmetry["the_point_group_is_a_subgroup_of_SO3"] is True
    assert symmetry["the_subgroup_of_SO3_is_the_rotation_part"] is True
    assert symmetry["the_reading_is_declared_and_not_derived_from_a_spacetime_model"] is True
    assert "SO(3)" in symmetry["declared_reading"]
    assert "time translations" in symmetry["declared_reading"]
    assert symmetry["lorentz_rotation_part"]["computed_here"] is False
    assert symmetry["lorentz_rotation_part"]["declared_reading"] is True
    assert symmetry["every_declared_solid_has_its_declared_order_and_its_orbit_count"] is True

    expected = {
        "truncated tetrahedron": (12, "T_d", 24, "T", 12, 12, 1, 1),
        "cuboctahedron": (12, "O_h", 48, "O", 24, 24, 1, 2),
        "truncated octahedron": (24, "O_h", 48, "O", 24, 24, 1, 1),
    }
    assert [row["solid"] for row in symmetry["solids"]] == list(expected)
    for row in symmetry["solids"]:
        vertices, point_group, point_order, rotation, rotation_order, improper, orbits, stab = \
            expected[row["solid"]]
        assert row["declared_vertex_count"] == vertices
        assert row["computed_vertex_count"] == vertices
        assert len(row["declared_vertices"]) == vertices
        assert row["declared_point_group"] == point_group
        assert row["declared_point_group_order"] == point_order
        assert row["computed_point_group_order"] == point_order
        assert row["declared_rotation_part"] == rotation
        assert row["declared_rotation_part_order"] == rotation_order
        assert row["computed_rotation_part_order"] == rotation_order
        assert row["computed_improper_element_count"] == improper
        assert row["is_a_subgroup_of_SO3"] is True
        assert row["the_rotation_part_lies_inside_SO3"] is True
        assert row["the_full_point_group_contains_improper_elements"] is True
        assert row["the_full_point_group_itself_lies_inside_SO3"] is False
        assert row["orbits_of_vertices_under_the_group_as_declared"] == orbits
        assert row["orbits_of_vertices_under_the_rotation_part"] == orbits
        assert row["orbits_of_vertices_under_the_full_point_group"] == orbits
        assert row["orbit_sizes_under_the_rotation_part"] == [vertices]
        assert row["vertex_stabiliser_order_under_the_rotation_part"] == stab
        assert stab * vertices == rotation_order
        assert row["every_element_maps_the_declared_vertex_set_onto_itself"] is True
        assert row["the_subgroup_of_SO3_is"].startswith("the rotation part " + rotation)

        # independent recomputation from the payload's own declared generators
        rotation_group = group_closure(tuple(tuple(tuple(entry) for entry in matrix)
                                             for matrix in row["generators_of_the_rotation_part"]))
        full_group = group_closure(tuple(tuple(tuple(entry) for entry in matrix)
                                         for matrix in row["generators_of_the_full_point_group"]))
        assert len(rotation_group) == rotation_order
        assert len(full_group) == point_order
        assert all(matrix_determinant(element) == 1 for element in rotation_group)
        assert len([element for element in full_group if matrix_determinant(element) == -1]) \
            == improper
        declared_vertices = {tuple(vertex) for vertex in row["declared_vertices"]}
        assert len(declared_vertices) == vertices
        assert all(matrix_apply(element, vertex) in declared_vertices
                   for element in full_group for vertex in declared_vertices)
        assert orbit_count(rotation_group, declared_vertices) == orbits
        assert orbit_count(full_group, declared_vertices) == orbits

    controls = {row["control_id"]: row for row in symmetry["controls"]}
    assert sorted(controls) == ["SYM-ARBITRARY-PLACEMENT", "SYM-TIME-IN-POINT-GROUP"]
    assert all(row["rejected"] and row["discriminates"] for row in controls.values())
    time_control = controls["SYM-TIME-IN-POINT-GROUP"]
    assert "time direction" in time_control["control"]
    assert Fraction(time_control["derived_value"]["value"]) == 3
    assert Fraction(time_control["claimed_value"]["value"]) == 4
    assert time_control["accepted_companion"]["verdict"] == \
        "Accepted_TimeAsDeclaredScheduleInvariant"
    assert any("3x3" in reason for reason in time_control["rejection_reasons"])

    arbitrary = controls["SYM-ARBITRARY-PLACEMENT"]
    assert "arbitrary" in arbitrary["control"]
    assert Fraction(arbitrary["derived_value"]["value"]) == 12
    assert Fraction(arbitrary["claimed_value"]["value"]) == 3
    assert arbitrary["accepted_companion"]["verdict"] == "Accepted_GroupInvariantPlacement"
    assert any("is not a declared position" in reason
               for reason in arbitrary["rejection_reasons"])

    time_direction = symmetry["the_time_direction"]
    assert time_direction["declared_acted_on_coordinates"] == ["x", "y", "z"]
    assert time_direction["declared_time_direction"] == "t"
    assert time_direction["the_point_group_acts_on_exactly_three_declared_coordinates"] is True
    assert time_direction["the_time_direction_is_not_among_the_acted_on_coordinates"] is True
    assert time_direction["the_time_direction_is_not_part_of_the_point_group"] is True
    assert time_direction["declared_schedule_period"]["value"] == "2"
    assert time_direction["declared_schedule_horizon"]["value"] == "24"
    ticks = time_direction["schedule_ticks"]
    assert ticks == list(range(0, 24, 2))
    assert time_direction["translated_ticks"] == [step + 2 for step in ticks]
    assert time_direction["the_schedule_is_invariant_under_translation_by_the_declared_period"] \
        is True
    assert time_direction["a_translation_by_one_step_does_not_preserve_the_schedule"] is True


def test_the_work_region_and_work_time_calculus():
    work = section("R7_work_region_and_time")
    constellation = work["declared_constellation"]
    assert constellation["platforms"] == ["P0", "P1", "P2", "P3"]
    assert constellation["declared_platform_count"] == 4
    assert constellation["declared_phases"] == [0, 1, 2, 3]
    assert constellation["declared_regions"] == [0, 1, 2, 3]
    assert constellation["declared_region_count"] == 4
    assert constellation["declared_window_steps"] == 12
    assert constellation["declared_sweep_period_steps"] == 4
    assert Fraction(constellation["declared_distance"]["value"]) \
        == declared("declared_work_region_distance")
    assert constellation["declared"] is True

    floor_used = work["geometric_floor_used"]
    assert floor_used["the_floor_is_the_one_computed_in_R3"] is True
    assert floor_used["source"] == "R3_spot_floor/platforms/a geostationary platform/floor"
    assert Fraction(floor_used["value"]["value"]) == Fraction(FLOOR_GEOSTATIONARY)
    assert Fraction(floor_used["penumbra_diameter"]["value"]) == Fraction(PENUMBRA_GEOSTATIONARY)

    sweep = work["the_sweep_due_to_motion"]
    assert sweep["declared_motion_is_a_declared_sweep"] is True
    assert sweep["sweep_period_steps"] == 4
    assert sweep["the_sweep_returns_after_exactly_the_declared_period"] is True

    # the declared table, recomputed here from the declared phases and region count
    assert work["schedule_step_count"] == 12
    assert len(work["schedule"]) == 12
    for entry in work["schedule"]:
        assert sorted(entry) == ["addresses", "step"]
        assert sorted(address["region"] for address in entry["addresses"]) == [0, 1, 2, 3]
        for address in entry["addresses"]:
            assert sorted(address) == ["platform", "region"]
            phase = int(address["platform"][1:])
            assert address["region"] == (entry["step"] + phase) % 4
    step_one = next(entry for entry in work["schedule"] if entry["step"] == 1)
    assert [(address["platform"], address["region"]) for address in step_one["addresses"]] == [
        ("P0", 1), ("P1", 2), ("P2", 3), ("P3", 0)]
    step_three = next(entry for entry in work["schedule"] if entry["step"] == 3)
    assert [(address["platform"], address["region"]) for address in step_three["addresses"]] == [
        ("P0", 3), ("P1", 0), ("P2", 1), ("P3", 2)]

    assert len(work["regions"]) == 4
    for row in work["regions"]:
        assert sorted(row) == ["address_count", "addressable", "addressed_at_steps",
                               "addressed_by_platforms", "duty_cycle", "region"]
        assert row["addressable"] is True
        assert row["addressed_at_steps"] == list(range(12))
        assert row["address_count"] == 12
        assert row["duty_cycle"] == "1"
        assert Fraction(row["address_count"], 12) == 1
    assert work["the_duty_cycle_of_a_region_under_the_relay"] == "1"

    assert len(work["platforms"]) == 4
    for row in work["platforms"]:
        assert row["sweep_period_steps"] == 4
        assert row["steps_per_region"] == 3
        assert row["duty_cycle_per_region"] == "1/4"
        assert Fraction(row["steps_per_region"], 12) == Fraction(1, 4)
        assert row["sustained_addressability_of_a_fixed_region"] is False
        assert len(row["per_region"]) == 4
        for region in row["per_region"]:
            assert region["step_count"] == 3
            assert region["steps"] == [step for step in range(12)
                                       if (step + row["declared_phase"]) % 4 == region["region"]]
            assert region["duty_cycle"] == "1/4"
        assert row["sweep"] == [(step + row["declared_phase"]) % 4 for step in range(12)]
    assert work["the_duty_cycle_of_one_platform_over_one_region"] == "1/4"

    assert work["regions_and_times_must_be_computed_in_advance"] is True
    assert work["the_schedule_is_computed_in_advance"] is True
    assert work["no_step_is_chosen_in_flight"] is True
    controls = {row["control_id"]: row for row in work["controls"]}
    assert sorted(controls) == ["WORK-SELECTED-IN-FLIGHT", "WORK-SINGLE-PLATFORM-SUSTAINED"]
    sustained = controls["WORK-SINGLE-PLATFORM-SUSTAINED"]
    assert Fraction(sustained["derived_value"]["value"]) == Fraction(1, 4)
    assert Fraction(sustained["claimed_value"]["value"]) == 1
    assert sustained["accepted_companion"]["verdict"] == "Accepted_RelayForm"
    assert any("factor 4" in reason for reason in sustained["rejection_reasons"])
    in_flight = controls["WORK-SELECTED-IN-FLIGHT"]
    assert Fraction(in_flight["derived_value"]["value"]) == 0
    assert Fraction(in_flight["claimed_value"]["value"]) == 1
    assert in_flight["accepted_companion"]["verdict"] == "Accepted_ComputedInAdvance"
    assert any("in-flight" in reason for reason in in_flight["rejection_reasons"])
    assert all(row["rejected"] and row["discriminates"] for row in controls.values())


def test_the_ablation_level_assignment():
    ablation = section("R8_ablation_level_assignment")
    assert "declared energy LEVELS" in ablation["rule"]
    assert "rather than to individual platforms" in ablation["rule"]
    assert ablation["declared_level_values"] == [1, 2, 3, 4]
    assert ablation["declared_level_count"] == 4
    assert [row["level"] for row in ablation["declared_levels"]] == [
        "level_1", "level_2", "level_3", "level_4"]
    assert all(row["declared"] and not row["measured_here"] and not row["read_from_data"]
               and row["unit"] == "1"
               and row["is_a_magnitude_of_a_physical_quantity"] is False
               for row in ablation["declared_levels"])
    assert ablation["declared_matched_to_the_declared_ablation_levels_of_the_target_medium"] is True
    assert ablation["assignment_count"] == 6
    assignments = {row["task"]: row for row in ablation["assignments"]}
    assert sorted(assignments) == ["task_a", "task_b", "task_c", "task_d", "task_e", "task_f"]
    assert assignments["task_a"]["assigned_level"] == "level_1"
    assert assignments["task_e"]["assigned_level"] == "level_1"
    assert assignments["task_c"]["assigned_level"] == "level_3"
    assert all(row["assigned_to_a_level"] is True and row["assigned_to_a_platform"] is False
               for row in ablation["assignments"])
    assert all(row["assigned_level_value"] == row["declared_required_level_value"]
               for row in ablation["assignments"])
    assert ablation["tasks_per_declared_level"] == [
        {"declared_level_value": 1, "level": "level_1", "task_count": 2},
        {"declared_level_value": 2, "level": "level_2", "task_count": 2},
        {"declared_level_value": 3, "level": "level_3", "task_count": 1},
        {"declared_level_value": 4, "level": "level_4", "task_count": 1},
    ]
    assert sum(row["task_count"] for row in ablation["tasks_per_declared_level"]) \
        == ablation["assignment_count"]
    assert ablation["every_task_is_assigned_to_a_declared_level"] is True
    assert ablation["no_task_is_assigned_to_a_platform"] is True
    assert ablation["no_level_outside_the_declared_set_is_used"] is True
    assert ablation["no_magnitude_of_any_real_physical_quantity_is_used"] is True

    controls = {row["control_id"]: row for row in ablation["controls"]}
    assert sorted(controls) == ["ABL-LEVEL-OUTSIDE-THE-DECLARED-SET", "ABL-TASK-TO-PLATFORM"]
    platform_control = controls["ABL-TASK-TO-PLATFORM"]
    assert "P0" in platform_control["claim"]
    assert Fraction(platform_control["derived_value"]["value"]) == 4
    assert Fraction(platform_control["claimed_value"]["value"]) == 0
    assert platform_control["accepted_companion"]["verdict"] == "Accepted_AssignedToADeclaredLevel"
    assert any("not a declared level" in reason
               for reason in platform_control["rejection_reasons"])
    outside = controls["ABL-LEVEL-OUTSIDE-THE-DECLARED-SET"]
    assert Fraction(outside["claimed_value"]["value"]) == 5
    assert Fraction(outside["derived_value"]["value"]) == 4
    assert Fraction(outside["claimed_value"]["value"]) - Fraction(
        outside["derived_value"]["value"]) == 1
    assert outside["accepted_companion"]["verdict"] == "Accepted_InsideTheDeclaredSet"
    assert all(row["rejected"] and row["discriminates"] for row in controls.values())


def test_the_declared_obligations_and_their_rejected_counterparts():
    obligations = section("R9_declared_obligations")
    contract = load(CONTRACT)["declared_obligations"]
    assert obligations["obligation_count"] == 5
    assert obligations["every_obligation_has_a_falsifiable_counterpart"] is True
    assert obligations["every_counterpart_is_rejected"] is True
    assert obligations["the_counterparts_are_executed_here"] is True
    names = [row["obligation"] for row in obligations["obligations"]]
    assert names == ["high_safety", "topology_preserved", "human_impact_controllable_and_small",
                     "error_tolerated_and_learned", "no_magnitude"]
    assert "high_safety" in contract and "topology_preserved" in contract
    assert "human_impact_controllable_and_small" in contract
    assert "error_tolerated_and_learned" in contract and "no_magnitude" in contract
    for row in obligations["obligations"]:
        assert sorted(row) == ["declared", "declared_reading", "falsifiable_counterpart",
                               "obligation"]
        assert row["declared"] == contract[row["obligation"]]
        assert row["declared_reading"]
        counterpart = row["falsifiable_counterpart"]
        assert sorted(counterpart) == sorted(CONTROL_ROW_KEYS)
        assert counterpart["rejected"] is True
        assert counterpart["discriminates"] is True
        assert counterpart["verdict"] == "Rejected"
        assert counterpart["rejection_reasons"]
        assert counterpart["accepted_companion"]["accepted"] is True
    identifiers = [row["falsifiable_counterpart"]["control_id"]
                   for row in obligations["obligations"]]
    assert identifiers == ["OBL-SAFETY-BELOW-THE-FLOOR", "OBL-TOPOLOGY-BROKEN",
                           "OBL-IMPACT-NOT-CONTROLLABLE", "OBL-ERROR-NOT-TOLERATED",
                           "OBL-MAGNITUDE-ASSERTED"]
    safety = obligations["obligations"][0]["falsifiable_counterpart"]
    assert Fraction(safety["derived_value"]["value"]) == Fraction(FLOOR_GEOSTATIONARY)
    assert Fraction(safety["claimed_value"]["value"]) * 4 == Fraction(FLOOR_GEOSTATIONARY)
    topology = obligations["obligations"][1]["falsifiable_counterpart"]
    assert Fraction(topology["derived_value"]["value"]) == 12
    assert Fraction(topology["claimed_value"]["value"]) == 0
    impact = obligations["obligations"][2]["falsifiable_counterpart"]
    assert Fraction(impact["derived_value"]["value"]) == 1
    assert Fraction(impact["claimed_value"]["value"]) == 2
    error = obligations["obligations"][3]["falsifiable_counterpart"]
    assert Fraction(error["derived_value"]["value"]) == 1
    assert Fraction(error["claimed_value"]["value"]) == 0
    magnitude = obligations["obligations"][4]["falsifiable_counterpart"]
    assert magnitude["control_id"] == "OBL-MAGNITUDE-ASSERTED"
    assert "magnitude" in magnitude["rejected_by"]

    assert obligations["declared_error_steps"] == [2, 5, 8]
    assert obligations["declared_error_magnitude_region_indices"] == 1
    assert obligations["learned_error_count"] == 3
    for row in obligations["learned_errors"]:
        assert row["learned"] is True
        assert row["declared_error_magnitude_region_indices"] == 1
        assert row["readdressed_at_step"] == row["declared_error_step"] + 1
        assert (row["declared_erroneous_region"]
                == (row["declared_missed_region"] + 1) % 4)


def test_stage_one_is_calibration_with_falsifiable_invariants():
    stage = section("R10_stage_one")
    contract = load(CONTRACT)["stage_one"]
    assert stage["phase"] == "calibration"
    assert stage["phase_is_calibration_not_control"] is True
    assert contract["phase"] == "calibration"
    assert stage["declared_window"] == contract["window"]
    assert "December" in stage["declared_window"] and "January" in stage["declared_window"]
    assert "0238" in stage["declared_window"]
    assert stage["declared_window_start_month"]["value"] == "12"
    assert stage["declared_window_end_month"]["value"] == "1"
    assert stage["declared_window_note_path"].startswith("docs/research/0238-")
    assert stage["declared_work"] == contract["work"]
    assert "aggregated and distributed" in stage["declared_work"]
    assert "continuous observation and learning" in stage["declared_work"]
    assert stage["the_material_is_declared_not_read"] is True
    assert "not read by this run" in stage["material_units_statement"]

    units = int(stage["declared_material_units"]["value"])
    recipients = int(stage["declared_recipient_count"]["value"])
    assert units == 4096 and recipients == 64
    assert int(stage["units_per_recipient"]["value"]) == units // recipients
    assert units % recipients == 0
    assert stage["the_material_divides_exactly_among_the_recipients"] is True
    for name in ("computed", "aggregated", "distributed"):
        record = stage[name]
        assert record["unit_index_count"] == units
        assert record["unit_index_sum"] == units * (units - 1) // 2
        assert record["unit_index_sum_of_squares"] == (units - 1) * units * (2 * units - 1) // 6
        assert record["stage"] == name
    assert stage["computed"] == {**stage["aggregated"], "stage": "computed"}
    assert stage["the_three_stages_carry_the_same_units"] is True

    steps = stage["growth_steps"]
    assert len(steps) == 8 == stage["growth_step_count"]
    for row in steps:
        assert row["declared_launches"] == row["growth_step"]
        assert row["learning_units"] == 4 * row["declared_launches"]
        assert row["cumulative_launches"] == row["growth_step"] * (row["growth_step"] + 1) // 2
    assert [row["learning_units"] for row in steps] == [4, 8, 12, 16, 20, 24, 28, 32]
    assert [row["cumulative_launches"] for row in steps] == [1, 3, 6, 10, 15, 21, 28, 36]
    assert stage["total_declared_launches"] == 36
    assert stage["total_declared_learning_units"] == 144
    assert stage["the_network_grows_at_every_declared_growth_step"] is True

    assert stage["invariant_count"] == 2
    assert [row["invariant"] for row in stage["invariants"]] == list(contract["invariants"])
    assert stage["every_invariant_has_a_falsifiable_counterpart"] is True
    assert stage["every_counterpart_is_rejected"] is True
    for row in stage["invariants"]:
        counterpart = row["falsifiable_counterpart"]
        assert counterpart["rejected"] is True and counterpart["discriminates"] is True
    topology = stage["invariants"][0]["falsifiable_counterpart"]
    assert topology["control_id"] == "STAGE-TOPOLOGY-BROKEN"
    assert Fraction(topology["derived_value"]["value"]) == 4096
    assert Fraction(topology["claimed_value"]["value"]) == 4095
    learning = stage["invariants"][1]["falsifiable_counterpart"]
    assert learning["control_id"] == "STAGE-LEARNING-DELAYED"
    assert Fraction(learning["derived_value"]["value"]) == 4
    assert Fraction(learning["claimed_value"]["value"]) == 0
    assert any("first declared growth step carries exactly 4" in reason
               for reason in learning["rejection_reasons"])
    phase_control = stage["phase_control"]
    assert phase_control["control_id"] == "STAGE-PHASE-CONTROL"
    assert phase_control["rejected"] is True and phase_control["discriminates"] is True
    assert "control" in phase_control["claim"]


def test_the_proposal_only_bookkeeping_and_the_unaddressed_termination():
    bookkeeping = section("R11_proposal_only_bookkeeping")
    contract = load(CONTRACT)
    assert bookkeeping["authorization"] == NO_NONE
    assert bookkeeping["decision"] == NO_NONE
    assert bookkeeping["deployment"] == NO_NONE
    assert bookkeeping["governance"] == UNASSESSED
    assert bookkeeping["physical_effect_asserted"] == NO_NONE
    assert bookkeeping["data_used"] == NO_DATA
    assert bookkeeping["status"] == PROPOSAL_STATUS
    assert bookkeeping["contract_status"] == contract["status"]
    assert bookkeeping["contract_status_note"] == contract["status_note"]
    assert "authorizes nothing" in contract["status_note"]
    assert "decides nothing" in contract["status_note"]
    assert "deploys nothing" in contract["status_note"]
    assert "asserts no physical effect" in contract["status_note"]
    assert "uses no data" in contract["status_note"]
    assert "PROPOSAL ONLY" in bookkeeping["proposal_only_statement"]
    assert "authorizes nothing" in bookkeeping["proposal_only_statement"]
    assert bookkeeping["proposal_only_in_chinese_and_english"] == "提议性方案 / proposal only"
    assert bookkeeping["authorizes_nothing"] is True
    assert bookkeeping["decides_nothing"] is True
    assert bookkeeping["deploys_nothing"] is True
    assert bookkeeping["no_governance_assessment"] is True
    assert "who might decide" in bookkeeping["nothing_said_about_who_might_decide"]

    termination = bookkeeping["termination_problem"]
    assert sorted(termination) == ["declared_as", "governance", "no_attempt_is_made_to_solve_it",
                                   "solved_here", "status", "why"]
    assert termination["status"] == UNADDRESSED
    assert termination["governance"] == UNASSESSED
    assert termination["solved_here"] is False
    assert termination["no_attempt_is_made_to_solve_it"] is True
    assert "does not attempt to solve the termination problem" in termination["why"]
    assert "who might decide" in termination["why"]

    report = load(EVIDENCE)
    claimed = report["what_is_not_claimed"]
    assert claimed["authorization"] == NO_NONE
    assert claimed["decision"] == NO_NONE
    assert claimed["deployment"] == NO_NONE
    assert claimed["governance"] == UNASSESSED
    assert claimed["physical_effect_asserted"] == NO_NONE
    assert claimed["data_used"] == NO_DATA
    assert claimed["physical_claim"] is False
    assert claimed["magnitude_of_any_physical_quantity"] is False
    assert claimed["forecast"] is False
    assert claimed["capability_claim"] is False
    assert claimed["weather_or_climate_effect"] is False
    assert claimed["no_data_read_or_used"] is True
    assert claimed["meteorological_data_used"] is False
    assert claimed["the_document_is_a_proposal_only"] is True
    assert claimed["the_termination_problem_is_unaddressed"] is True
    assert claimed["the_usable_fraction_is_corrected"] is True
    assert claimed["the_superseded_value_is_marked_superseded"] is True
    assert claimed["the_earlier_payload_is_retained_byte_for_byte"] is True
    assert claimed["native_admission"] == "NotGranted"
    assert claimed["native_certificate"] is False
    assert claimed["stable_api_change"] is False
    assert claimed["no_contract_or_note_edited"] is True
    assert claimed["no_claim_added_to_docs_claims_toml"] is True

    status = report["verification_status"]
    assert status["observational"] == "Unavailable"
    assert status["no_data_read_or_used"] is True
    assert status["physical_effect_asserted"] == NO_NONE
    assert status["deployment"] == NO_NONE
    for key in ("no_data_read_or_used", "no_physical_effect_is_asserted",
                "no_magnitude_of_any_physical_quantity_is_asserted",
                "the_pairing_rules_are_enforced_as_rules",
                "the_corrected_usable_fraction_is_carried",
                "the_superseded_value_is_marked_superseded",
                "the_earlier_payload_is_retained_byte_for_byte",
                "the_symmetry_reading_is_declared",
                "regions_and_times_are_computed_in_advance",
                "tasks_are_assigned_to_declared_levels",
                "stage_one_is_recorded_as_calibration",
                "governance_is_unaddressed"):
        assert status["checked_here"][key] is True, key


def test_every_control_is_recorded_once_with_its_outcome():
    report = load(EVIDENCE)
    rows = controls_in(report)
    summary = report["controls_summary"]
    identifiers = [row["control_id"] for row in rows]
    assert len(identifiers) == FROZEN_CONTROL_COUNT
    assert len(set(identifiers)) == FROZEN_CONTROL_COUNT
    assert sorted(identifiers) == sorted(CONTROL_IDS)
    assert all(row["verdict"] == "Rejected" for row in rows)
    assert all(row["rejected"] is True for row in rows)
    assert all(row["discriminates"] is True for row in rows)
    assert all(row["rejection_reasons"] for row in rows)
    assert all(row["rejected_by"] for row in rows)
    assert all(sorted(row["accepted_companion"]) == sorted(ACCEPTED_COMPANION_KEYS)
               for row in rows)
    assert all(row["accepted_companion"]["accepted"] is True for row in rows)
    assert all(row["outcome"] == "RejectedWithAnAcceptedCompanion" for row in rows)
    assert len(summary["controls"]) == FROZEN_CONTROL_COUNT
    assert summary["controls_count"] == FROZEN_CONTROL_COUNT
    assert summary["controls_rejected"] == FROZEN_CONTROL_COUNT
    assert summary["controls_failed_to_discriminate"] == FROZEN_FAILED_CONTROL_COUNT
    assert summary["every_control_has_an_accepted_companion"] is True
    assert summary["no_control_is_dropped"] is True
    assert sorted(row["control_id"] for row in summary["controls"]) == sorted(CONTROL_IDS)
    assert [row["control_id"] for row in summary["failed_controls"]] == [
        "PAIR-MISLABELLED-DECLARATION"]
    assert summary["failed_controls"][0]["discriminates"] is False
    assert summary["failed_controls"][0]["outcome"] == "FAILED_TO_DISCRIMINATE"
    assert "failed control" in summary["why_a_failed_control_is_retained"]
    assert report["checks"]["the_failed_control_is_retained"] is True
    assert report["checks"]["no_control_is_dropped"] is True


def test_the_payload_is_free_of_floating_point_literals_host_paths_and_timestamps():
    raw = EVIDENCE.read_text(encoding="utf-8")
    assert load(EVIDENCE)
    assert "NaN" not in raw and "Infinity" not in raw
    assert "/Users/" not in raw and "mingli" not in raw
    report = load(EVIDENCE)
    assert report["checks"]["no_floating_point_value_is_retained"] is True
    assert report["checks"]["no_magnitude_or_effect_key_appears_anywhere"] is True
    assert report["checks"]["no_in_flight_choice_key_appears_anywhere"] is True
    assert key_findings(report, FORBIDDEN_MAGNITUDE_KEYS) == []
    assert key_findings(report, FORBIDDEN_TIME_KEYS) == []


def test_the_frozen_shape_of_every_section():
    report = load(EVIDENCE)
    assert sorted(report) == sorted(TOP_LEVEL_KEYS)
    assert sorted(report["sections"]) == sorted(SECTION_NAMES)
    for name, keys in FROZEN_SECTION_SHAPE.items():
        assert sorted(report["sections"][name]) == sorted(keys), name

    constants = report["declared_constants"]
    assert sorted(constants[0]) == ["declared", "measured_here", "name", "read_from_data", "role",
                                    "unit", "value"]
    citations = report["cited_artifacts"]
    assert sorted(citations[0]) == ["hashed_here", "path", "relation", "retained_byte_for_byte",
                                    "sha256", "sha256_declared"]
    assert sorted(report["corrects"]) == ["note", "pairing_rules",
                                          "the_correction_is_carried_and_the_earlier_payload_is_"
                                          "not_edited"]
    assert sorted(report["tooling"]) == [
        "arithmetic", "declared_external_library_available_but_unused",
        "declared_not_native_authority", "exact_only", "external_libraries_imported",
        "not_implemented", "used_for"]
    assert sorted(report["verification_status"]) == [
        "checked_here", "deployment", "no_data_read_or_used", "observational",
        "physical_effect_asserted", "reason"]

    pairing = section("R1_pairing_rules")
    assert sorted(pairing["rules"][0]) == ["enforced_as_a_rule", "enforced_by", "rule", "rule_id"]
    assert sorted(pairing["accepted_pairings"][0]) == ["accepted", "occulted_fraction", "pairing",
                                                       "ratio"]
    assert sorted(pairing["penumbra_rule"]) == [
        "accepted", "declared_aperture", "full_angular_size_at_the_second_lagrange_point",
        "penumbra_diameter_at_the_second_lagrange_point", "reading", "rule",
        "the_spot_floor_uses_the_full_angular_size"]

    usable = section("R2_usable_fraction")
    assert sorted(usable["platforms"][0]) == ["declared_distance", "name", "occulted_fraction",
                                              "status", "usable_fraction"]
    assert sorted(usable["the_correction"]) == [
        "reading", "superseded_occulted_fraction", "superseded_usable_fraction",
        "superseded_usable_fraction_in_decimal",
        "the_correction_is_not_an_edit_of_the_earlier_payload", "the_correction_lives_in",
        "the_difference_in_decimal",
        "the_difference_is_exactly_three_quarters_of_the_corrected_occulted_fraction",
        "the_difference_is_the_superseded_value_minus_the_corrected_one",
        "the_difference_stated_exactly", "the_earlier_payload",
        "the_earlier_payload_is_retained_byte_for_byte", "the_earlier_payload_sha256",
        "the_earlier_payload_sha256_declared",
        "the_factor_by_which_the_mis_paired_fraction_is_wrong", "the_mis_paired_ratio",
        "the_superseded_value_is_the_earlier_runs_own_value",
        "the_superseded_value_is_used_nowhere_in_this_run",
        "the_superseded_value_was_produced_by_a_mis_paired_ratio"]

    floor = section("R3_spot_floor")
    assert sorted(floor["platforms"][0]) == [
        "declared_aperture", "declared_distance", "floor", "floor_in_decimal", "name",
        "penumbra_diameter", "penumbra_diameter_over_the_floor", "theta_sun_angular_radius",
        "theta_sun_full_angular_size"]
    pattern = section("R5_pattern_scale")
    assert sorted(pattern["platform_scales"][0]) == [
        "name", "pattern_scale", "pattern_scale_source",
        "the_pattern_scale_is_the_floor_value_of_that_reference"]

    symmetry = section("R6_symmetry_constraints")
    solid = symmetry["solids"][0]
    assert sorted(solid) == [
        "computed_improper_element_count", "computed_point_group_order",
        "computed_rotation_part_order", "computed_vertex_count", "declared_base_triple",
        "declared_point_group", "declared_point_group_order", "declared_rotation_part",
        "declared_rotation_part_order", "declared_sign_parity", "declared_vertex_construction",
        "declared_vertex_count", "declared_vertices",
        "every_element_maps_the_declared_vertex_set_onto_itself",
        "generators_of_the_full_point_group", "generators_of_the_rotation_part",
        "is_a_subgroup_of_SO3", "orbit_sizes_under_the_full_point_group",
        "orbit_sizes_under_the_rotation_part", "orbits_of_vertices_under_the_full_point_group",
        "orbits_of_vertices_under_the_group_as_declared",
        "orbits_of_vertices_under_the_rotation_part", "solid",
        "the_full_point_group_contains_improper_elements",
        "the_full_point_group_itself_lies_inside_SO3", "the_rotation_part_lies_inside_SO3",
        "the_subgroup_of_SO3_is", "vertex_stabiliser_order_under_the_rotation_part"]
    assert len(solid["declared_vertices"]) == 12
    assert all(len(vertex) == 3 for vertex in solid["declared_vertices"])
    assert all(isinstance(entry, int) for vertex in solid["declared_vertices"] for entry in vertex)
    time_direction = symmetry["the_time_direction"]
    assert sorted(time_direction) == [
        "a_translation_by_one_step_does_not_preserve_the_schedule", "declared",
        "declared_acted_on_coordinates", "declared_schedule_horizon", "declared_schedule_period",
        "declared_time_direction", "schedule_ticks",
        "the_point_group_acts_on_exactly_three_declared_coordinates",
        "the_schedule_is_invariant_under_translation_by_the_declared_period",
        "the_time_direction_is_not_among_the_acted_on_coordinates",
        "the_time_direction_is_not_part_of_the_point_group", "translated_ticks"]

    work = section("R7_work_region_and_time")
    assert sorted(work["declared_constellation"]) == [
        "declared", "declared_distance", "declared_phases", "declared_platform_count",
        "declared_region_count", "declared_regions", "declared_sweep_period_steps",
        "declared_window_steps", "platforms"]
    assert sorted(work["geometric_floor_used"]) == [
        "penumbra_diameter", "penumbra_diameter_source", "reading", "source",
        "the_floor_is_the_one_computed_in_R3", "value"]
    assert sorted(work["regions"][0]) == ["address_count", "addressable", "addressed_at_steps",
                                          "addressed_by_platforms", "duty_cycle", "region"]
    assert sorted(work["platforms"][0]) == [
        "declared_phase", "duty_cycle_per_region", "per_region", "platform", "steps_per_region",
        "sustained_addressability_of_a_fixed_region", "sweep", "sweep_period_steps"]
    assert sorted(work["platforms"][0]["per_region"][0]) == ["duty_cycle", "region", "step_count",
                                                             "steps"]
    assert sorted(work["schedule"][0]) == ["addresses", "step"]
    assert sorted(work["schedule"][0]["addresses"][0]) == ["platform", "region"]

    ablation = section("R8_ablation_level_assignment")
    assert sorted(ablation["declared_levels"][0]) == [
        "declared", "declared_level_value", "is_a_magnitude_of_a_physical_quantity", "level",
        "measured_here", "read_from_data", "unit"]
    assert sorted(ablation["assignments"][0]) == [
        "assigned_level", "assigned_level_value", "assigned_to_a_level", "assigned_to_a_platform",
        "declared_required_level_value", "task"]
    assert sorted(ablation["tasks_per_declared_level"][0]) == ["declared_level_value", "level",
                                                               "task_count"]

    obligations = section("R9_declared_obligations")
    assert sorted(obligations["obligations"][0]) == ["declared", "declared_reading",
                                                     "falsifiable_counterpart", "obligation"]
    assert sorted(obligations["learned_errors"][0]) == [
        "declared_erroneous_region", "declared_error_magnitude_region_indices",
        "declared_error_step", "declared_missed_region", "learned", "readdressed_at_step"]

    stage = section("R10_stage_one")
    assert sorted(stage["invariants"][0]) == ["declared", "falsifiable_counterpart", "invariant"]
    assert sorted(stage["growth_steps"][0]) == ["cumulative_launches", "declared_launches",
                                                "growth_step", "learning_units"]
    assert sorted(stage["computed"]) == ["stage", "unit_index_count", "unit_index_sum",
                                         "unit_index_sum_of_squares"]

    bookkeeping = section("R11_proposal_only_bookkeeping")
    assert sorted(bookkeeping["termination_problem"]) == [
        "declared_as", "governance", "no_attempt_is_made_to_solve_it", "solved_here", "status",
        "why"]

    controls = load(EVIDENCE)["controls_summary"]
    assert sorted(controls) == ["controls", "controls_count", "controls_failed_to_discriminate",
                                "controls_rejected", "every_control_has_an_accepted_companion",
                                "failed_controls", "no_control_is_dropped", "reading",
                                "why_a_failed_control_is_retained"]
    assert sorted(controls["controls"][0]) == ["control_id", "discriminates", "outcome"]


def test_the_undecided_items_and_modelling_choices_are_declared():
    report = load(EVIDENCE)
    undecided = report["undecided"]
    assert len(undecided) == FROZEN_UNDECIDED_COUNT
    assert report["checks"]["undecided_items_are_declared"] is True
    items = [row["item"] for row in undecided]
    assert any("SO(3)" in item for item in items)
    assert any("December" in item for item in items)
    assert any("distances" in item for item in items)
    assert any("coherence length" in item for item in items)
    assert any("ablation" in item for item in items)
    assert any("continuous motion" in item for item in items)
    assert any("perturbations" in item for item in items)
    assert any("superseded" in item for item in items)
    for row in undecided:
        assert sorted(row) == ["item", "reason", "retained_partial_result"]
        assert row["reason"]
        assert row["retained_partial_result"] is not None
    orders = next(row for row in undecided if "SO(3)" in row["item"])
    assert "order 24" in orders["retained_partial_result"]["truncated_tetrahedron"]
    assert "order 48" in orders["retained_partial_result"]["cuboctahedron"]
    assert "order 12" in orders["retained_partial_result"]["truncated_tetrahedron"]
    superseded = next(row for row in undecided if "superseded" in row["item"])
    assert superseded["retained_partial_result"]["superseded_usable_fraction"] \
        == SUPERSEDED_USABLE_FRACTION
    assert superseded["retained_partial_result"]["corrected_usable_fraction"] == USABLE_FRACTION
    assert superseded["retained_partial_result"]["the_earlier_payload_sha256"] \
        == DECLARED_EARLIER_EVIDENCE_SHA256

    choices = report["modelling_choices"]
    assert len(choices) == FROZEN_MODELLING_CHOICE_COUNT
    for key in ("declared_constants_are_declared", "pairing_like_with_like",
                "penumbra_diameter_form", "corrected_fraction_and_the_superseded_value",
                "floor_reported_once", "pattern_scale_is_the_floor",
                "symmetry_reading_through_the_rotation_part",
                "time_direction_as_schedule_invariant", "group_data_is_declared",
                "work_region_discrete_steps", "computation_in_advance",
                "ablation_levels_are_declared", "obligations_with_counterparts",
                "stage_one_is_calibration", "proposal_only", "termination_unaddressed",
                "no_magnitude", "exact_only", "external_library", "resource_limits"):
        assert choices[key], key
    assert "raise on a mixed pairing" in choices["pairing_like_with_like"]
    assert "SUPERSEDED" in choices["corrected_fraction_and_the_superseded_value"]
    assert "not edited" in choices["corrected_fraction_and_the_superseded_value"]
    assert "reported once" in choices["floor_reported_once"]
    assert "forty times" in choices["pattern_scale_is_the_floor"]
    assert "not itself inside SO(3)" in choices["symmetry_reading_through_the_rotation_part"]
    assert "mapped onto themselves" in choices["time_direction_as_schedule_invariant"]
    assert "computed exactly rather than declared" in choices["group_data_is_declared"]
    assert "no orbital mechanics" in choices["work_region_discrete_steps"]
    assert "declared ordinals" in choices["ablation_levels_are_declared"]
    assert "CALIBRATION" in choices["stage_one_is_calibration"]
    assert "提议性方案" in choices["proposal_only"]
    assert "Unaddressed" in choices["termination_unaddressed"]
    assert "not a floating-point value" in choices["no_magnitude"]
    assert "standard library alone" in choices["external_library"]
    assert "CPU limit" in choices["resource_limits"]
    assert "address-space ceiling" in choices["resource_limits"]


def test_the_declared_checks_all_pass_and_name_their_conditions():
    checks = load(EVIDENCE)["checks"]
    assert all(checks.values())
    assert len(checks) == FROZEN_CHECK_COUNT
    for name in ("assertions_within_budget",
                 "this_contract_digest_matches_the_declared_one",
                 "the_earlier_proposal_is_retained_byte_for_byte",
                 "the_contract_declares_itself_a_proposal_only",
                 "the_seven_shared_items_are_reported_once_each",
                 "every_declared_constant_is_declared_and_not_measured",
                 "the_pairing_rules_are_enforced_as_rules",
                 "the_mispaired_control_is_rejected_by_the_rule",
                 "the_mispaired_fraction_is_wrong_by_exactly_four",
                 "the_accepted_pairings_agree_exactly",
                 "the_penumbra_diameter_uses_the_full_angular_size",
                 "the_penumbra_mispaired_control_is_rejected",
                 "the_corrected_occulted_fraction_is_carried",
                 "the_corrected_usable_fraction_is_carried",
                 "the_corrected_fractions_sum_to_exactly_one",
                 "the_superseded_value_is_the_earlier_payloads_own",
                 "the_superseded_value_is_marked_superseded",
                 "the_difference_between_the_two_is_stated_exactly",
                 "the_correction_cites_the_note_and_this_contract",
                 "the_superseded_value_is_used_nowhere",
                 "the_floor_is_reported_at_three_declared_distances",
                 "the_l2_floor_exceeds_the_earths_diameter",
                 "the_etendue_ceiling_is_one_microwatt_per_mode",
                 "the_ceiling_forces_power_into_free_space",
                 "the_etendue_control_is_rejected",
                 "the_pattern_scale_is_the_floor",
                 "finer_structure_is_washed_out",
                 "coarser_structure_needs_an_aperture_below_the_coherence_length",
                 "the_pattern_control_is_rejected",
                 "three_archimedean_solids_are_declared",
                 "every_declared_solid_has_its_declared_order",
                 "every_declared_solid_lies_in_SO3_through_its_rotation_part",
                 "every_declared_solids_vertices_form_the_reported_number_of_orbits",
                 "the_vertices_are_invariant_under_the_declared_group",
                 "the_time_direction_is_not_part_of_the_point_group",
                 "the_schedule_is_invariant_under_the_declared_translations",
                 "the_time_control_is_rejected",
                 "the_arbitrary_placement_control_is_rejected",
                 "every_declared_region_is_addressable_at_every_declared_step",
                 "the_relay_duty_cycle_is_exactly_one",
                 "a_single_platform_holds_a_region_at_one_quarter",
                 "every_declared_step_addresses_every_declared_region_exactly_once",
                 "regions_and_times_are_computed_in_advance",
                 "the_sustained_single_platform_control_is_rejected",
                 "the_in_flight_choice_control_is_rejected",
                 "the_geometric_floor_used_is_the_one_computed_in_R3",
                 "every_task_is_assigned_to_a_declared_level",
                 "no_level_outside_the_declared_set_is_used",
                 "the_declared_levels_are_matched_to_the_declared_ablation_levels",
                 "no_magnitude_of_any_physical_quantity_is_used_in_the_assignment",
                 "the_task_to_platform_control_is_rejected",
                 "the_level_outside_the_set_control_is_rejected",
                 "every_obligation_has_a_rejected_counterpart",
                 "the_declared_error_is_bounded_and_learned",
                 "the_magnitude_audit_finds_nothing_in_the_payload",
                 "stage_one_is_recorded_as_calibration",
                 "stage_one_carries_the_declared_window",
                 "the_material_carries_through_computation_aggregation_and_distribution",
                 "the_topology_invariant_has_a_rejected_counterpart",
                 "the_learning_invariant_has_a_rejected_counterpart",
                 "learning_is_continuous_from_the_first_stage",
                 "the_phase_control_is_rejected",
                 "the_payload_records_proposal_only_bookkeeping",
                 "governance_is_unaddressed_and_no_decision_is_claimed",
                 "the_termination_problem_is_unaddressed_and_not_solved",
                 "the_failed_control_is_retained", "no_control_is_dropped",
                 "observational_verification_is_recorded_unavailable",
                 "no_data_is_read_or_used", "undecided_items_are_declared",
                 "no_floating_point_value_is_retained",
                 "no_magnitude_or_effect_key_appears_anywhere",
                 "no_in_flight_choice_key_appears_anywhere"):
        assert checks[name] is True, name


def test_a_copied_checkout_reproduces_the_retained_payload(tmp_path):
    """The checker is re-run on a COPY: the payload must not depend on its location."""
    copied = tmp_path / "experiments"
    (copied / "geometry_foundation_v1").mkdir(parents=True)
    (copied / "optical_imbalance_proposal_v1").mkdir()
    shutil.copy(CHECKER, copied / "geometry_foundation_v1/calibration.py")
    shutil.copy(CONTRACT, copied / "geometry_foundation_v1/contract.json")
    shutil.copy(EARLIER_CONTRACT, copied / "optical_imbalance_proposal_v1/contract.json")
    shutil.copy(EARLIER_EVIDENCE, copied / "optical_imbalance_proposal_v1/evidence.json")
    output = tmp_path / "on-a-copy.json"
    completed = invoke(copied / "geometry_foundation_v1/calibration.py", output)
    assert completed.returncode == 0, completed.stderr
    fresh = load(output)
    retained = load(EVIDENCE)
    assert fresh["status"] == retained["status"]
    assert fresh["assertions"] == retained["assertions"]
    assert fresh["sections"] == retained["sections"]
    assert fresh["checks"] == retained["checks"]
    assert fresh["controls_summary"] == retained["controls_summary"]
    assert fresh["undecided"] == retained["undecided"]
    assert fresh["what_is_not_claimed"] == retained["what_is_not_claimed"]
    assert fresh["modelling_choices"] == retained["modelling_choices"]
    assert fresh["declared_constants"] == retained["declared_constants"]
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


def test_the_claim_is_registered_once_and_binds_the_checker_and_the_note():
    """Exactly one claim for this run is registered, and it names the checker, the evidence and the note.

    The checker was written while this test asserted the claim's ABSENCE, because a claim lives in
    `docs/claims.toml` and is added by the parent session with its note.  The parent session has now
    added it, together with the spacetime-group supplement; the assertion is inverted rather than
    dropped, so the binding stays checked.
    """
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    assert claims
    matches = [row for row in claims if row.get("claim_id") == CLAIM_ID]
    assert len(matches) == 1, "exactly one claim must be registered for this run"
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for symbol in ("geometry_foundation_v1/calibration.py",
                   "geometry_foundation_v1/contract.json",
                   "geometry_foundation_v1/contract-supplement-1.json",
                   "geometry_foundation_v1/evidence.json",
                   "0243-the-geometry-foundation"):
        assert symbol in claim["code_symbol"], symbol
    assert "failed to discriminate" in claim["counterexample_boundary"].lower(), \
        "the boundary must retain the failed control"
    assert "NotGranted" in claim["counterexample_boundary"], "the boundary must record native admission"
    assert claim["forbidden_conflations"], "the claim must name its conflations"

