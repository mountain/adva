"""The paired test for the space proposal v3 exact calibration.

The assertions here are about what the retained checker decided by exact arithmetic on a PROPOSAL
ONLY document - 提议性方案 (proposal three): one declared constellation family with a declared
polyhedral placement, its declared point group built by exact integer matrix closure, a declared
two-region reading, declared spacetime-group conditions, declared W1 to W4 entry-window constants,
declared ordinal ablation levels, and a declared stage-one calibration.

They are not claims about any physical object.  Nothing is ablated, melted, moved or heated, no
pattern is projected onto any real surface, no magnitude, sign or timing is asserted for any
physical quantity, and no data is read or used.  The test checks that absence in the retained
payload.

The checker is invoked without `-S`; it imports nothing beyond the standard library.  The orbit
structure, the antipodal count, the group order, the chirality of the alternative, the declared
two-region reading and the W4 inequality are all recomputed here from the payload's OWN declared
parameters by this test's own exact arithmetic, so the numbers are checked twice.

The record carries no claim for this run: this test asserts that NO claim for this experiment is registered in `docs/claims.toml`.
"""

import hashlib
import json
import re
import shutil
import subprocess
import sys
import tomllib
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT / "experiments/space_proposal_v3"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"

CLAIM_ID = "adva.bounded-experiment.space-proposal-v3.v0"
DECLARED_CONTRACT_SHA256 = "d9b8ef6444c24f1d77fb9d64f23b49ddb50e2805baf1446e26d21d432497df3c"

SCHEMA = "adva.external.space-proposal-v3-proposal-calibration.v1"
PROPOSAL_STATUS = "PROPOSAL ONLY - 提议性方案"
NO_NONE = "none"
UNASSESSED = "unaddressed"
UNADDRESSED = "Unaddressed"
TRANSPORT_UNIT = "declared units of net signed flow per declared period"

FORBIDDEN_EFFECT_KEYS = (
    "effect", "physical_effect", "physical_value", "temperature", "forcing", "flux", "power", "heat", "melt", "melting", "ice", "water", "atmosphere", "ocean", "cloud", "weather", "climate",
    "warming", "cooling", "albedo", "damage", "benefit", "yield", "anomaly", "tendency", "sensitivity", "forecast", "joule", "kelvin", "watt", "brownian", "irradiance", "insolation",
    "sunlight",
)

FORBIDDEN_TIME_KEYS = ("timestamp", "created_at", "started_at", "finished_at", "elapsed", "wall_clock", "hostname", "abspath", "cwd")

CUBE_BASE = (1, 1, 1)
PETRIE_BASE = (1, 0, 2)
EXPECTED_GROUP_ORDER = 24
EXPECTED_ROTATION_PART_ORDER = 12
EXPECTED_CUBE_ORBIT = 8
EXPECTED_PETRIE_ORBIT = 12
EXPECTED_VERTEX_COUNT = 20
EXPECTED_ANTIPODAL_PAIRS = 10
EXPECTED_SNUB_CUBE_ORDER = 24
EXPECTED_TRANSPORT_ZERO = "0"
EXPECTED_TRANSPORT_BROKEN = "-15/2"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    """Load JSON and refuse any floating-point literal in it."""
    def no_float(text):
        raise AssertionError(f"a floating-point literal is present: {text}")

    return json.loads(Path(path).read_text(encoding="utf-8"), parse_float=no_float)


def invoke(checker, output, timeout=900):
    return subprocess.run( [sys.executable, str(checker), "--output", str(output)],
        capture_output=True, text=True, timeout=timeout, check=False,
    )


def section(name):
    return load(EVIDENCE)["sections"][name]


def key_findings(node, keys, path="", found=None):
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


# The generated frozen expectations below are long literal records and are wrapped at the
# end of the file so that the readable test bodies stay inside the line budget.
# fmt: off  # the generated frozen expectations below are long literal records
FROZEN_ASSERTION_COUNT = 719
FROZEN_CHECK_COUNT = 68
FROZEN_CONTROL_COUNT = 9
FROZEN_SECTION_SHAPE = {
    'S1_the_constellation_family': ['alternative', 'declared_family', 'primary', 'reading'],
    'S2_the_two_regions': ['antisunward_region', 'declared_reading', 'declared_region_count', 'declared_region_indicator', 'each_antipodal_pair_serves_one_member_of_each_region', 'no_step_is_chosen_in_flight', 'reading', 'sunward_indicator_is_exact_odd_under_the_declared_pairing_element', 'sunward_region', 'the_declared_addressing_table', 'the_declared_addressing_table_step_count', 'the_declared_schedule_is_computed_in_advance', 'the_same_declared_phase_schedule_addresses_both_regions', 'the_two_region_addressings_are_exact_negatives', 'the_two_regions_have_opposite_declared_sense', 'the_two_regions_partition_the_constellation'],
    'S3_the_spacetime_group_conditions': ['declared_broken_pair', 'declared_clause', 'declared_invariance_condition', 'declared_invariant_pair', 'declared_position_field', 'reading', 'the_declared_residual_of_the_transfer', 'the_declared_uniform_measure_is_exactly_stationary', 'the_element_that_shifts_time_without_the_declared_pairing_element', 'the_mechanism_is_re_executed_inside_this_runs_own_declared_model', 'the_mechanism_is_the_one_already_executed_in_the_declared_ratchet_run', 'the_second_declared_broken_pair', 'the_transfer_is_exactly_divergence_free', 'vertex_divergence'],
    'S4_schedule_compatibility': ['declared_reading', 'declared_standing_pattern', 'declared_travelling_pattern', 'reading', 'the_compatibility_rule'],
    'S5_the_entry_window_W1_to_W4': ['W1_the_declared_state_above_the_declared_threshold', 'W1_the_declared_state_at_the_declared_threshold', 'W1_the_declared_state_below_the_declared_threshold', 'W2_the_declared_entry_step', 'W2_the_declared_sealing_step', 'W2_the_declared_window_is_determined_by_the_declared_phase_state', 'W3_a_silent_crossing_is_refused', 'W3_the_declared_connected_phase_topology_invariant', 'W3_the_declared_permitted_silent_crossing_count', 'W3_the_declared_threshold_crossing_count', 'W4_is_the_only_declared_safety_statement_of_this_run', 'W4_the_declared_safety_statement_is_an_exact_inequality_on_declared_numbers', 'declared_constants_and_thresholds_not_measurements', 'declared_window', 'every_declared_refusal_is_executed', 'no_data_is_read_or_used', 'reading', 'refusal_count', 'refusals', 'rejected_claim', 'the_declared_action_is_strictly_below_the_declared_bound', 'the_declared_connected_region_vertex_count', 'the_declared_inequality_stated_exactly', 'the_declared_latent_heat', 'the_declared_latent_heat_of_a_connected_region_at_the_threshold', 'the_declared_percolation_threshold', 'the_declared_safety_bound', 'the_declared_safety_fraction', 'the_declared_single_action_energy'],
    'S6_the_declared_ablation_levels': ['assignment_count', 'assignments', 'control_count', 'controls', 'declared_level_count', 'declared_level_values', 'declared_levels', 'declared_reading', 'every_declared_level_carries_at_least_one_task', 'every_task_is_assigned_to_a_declared_level', 'no_level_outside_the_declared_set_is_used', 'no_magnitude_of_any_physical_quantity_is_used', 'no_task_is_assigned_to_a_platform', 'reading', 'tasks_per_declared_level', 'the_assignment_is_declared'],
    'S7_stage_one': ['aggregated', 'computed', 'control_count', 'controls', 'declared_invariants', 'declared_reading', 'declared_recipient_count', 'declared_unit_count', 'declared_units_per_recipient', 'distributed', 'every_declared_invariant_has_a_rejected_counterpart', 'growth_step_count', 'growth_steps', 'invariant_count', 'learning_enters_at_the_first_declared_step', 'no_data_is_read_or_used', 'reading', 'the_declared_network_grows_strictly', 'the_declared_units_are_declared_not_read', 'the_declared_units_divide_exactly_among_the_recipients', 'the_three_declared_stages_carry_identical_counts_and_identical_index_sums', 'total_declared_launches', 'total_declared_learning_units'],
    'S8_the_declared_overreaches': ['control_count', 'controls', 'declared_corrections_carried', 'every_overreach_is_executed_and_refused', 'reading', 'the_declared_alternative_euler_identity', 'the_declared_combinatorial_type_is_referenced_not_recomputed', 'the_declared_combinatorial_type_source', 'the_declared_euler_characteristic', 'the_declared_primary_euler_identity', 'the_icosahedral_constellation', 'the_two_declared_orbits'],
    'S9_proposal_only_bookkeeping': ['authorization', 'authorizes_nothing', 'data_used', 'decides_nothing', 'decision', 'deployment', 'deploys_nothing', 'governance', 'no_governance_assessment', 'nothing_said_about_who_might_decide', 'physical_effect_asserted', 'proposal_only_in_chinese_and_english', 'proposal_only_statement', 'record_purpose', 'status', 'termination_problem', 'the_status_note_of_the_frozen_contract_is_quoted', 'the_status_of_the_frozen_contract_is_quoted'],
}
SECTION_NAMES = ('S1_the_constellation_family', 'S2_the_two_regions', 'S3_the_spacetime_group_conditions', 'S4_schedule_compatibility', 'S5_the_entry_window_W1_to_W4', 'S6_the_declared_ablation_levels', 'S7_stage_one', 'S8_the_declared_overreaches', 'S9_proposal_only_bookkeeping')
TOP_LEVEL_KEYS = ['acceptance', 'assertions', 'checker_sha256', 'checks', 'contract', 'contract_sha256', 'contract_sha256_declared', 'contract_status', 'controls', 'declared_model', 'limits', 'modelling_choices', 'protected', 'referenced_by_digest', 'residual', 'schema', 'sections', 'status', 'tooling', 'undecided', 'verification_status', 'version', 'what_is_not_claimed']
# fmt: on

# ------------------------------------------- this test's own exact matrix arithmetic -- 
IDENTITY = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def matmul(left, right):
    return tuple(tuple(sum(left[i][k] * right[k][j] for k in range(3)) for j in range(3))
                 for i in range(3))


def matdet(matrix):
    return (matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
            - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
            + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]))


def matapply(matrix, point):
    return tuple(sum(matrix[i][j] * point[j] for j in range(3)) for i in range(3))


def closure(generators, limit=512):
    group = {IDENTITY}
    frontier = [IDENTITY]
    while frontier:
        element = frontier.pop()
        for generator in generators:
            product = matmul(generator, element)
            if product not in group:
                group.add(product)
                assert len(group) <= limit
                frontier.append(product)
    return tuple(sorted(group))


def element_order(matrix):
    element = matrix
    count = 1
    while element != IDENTITY:
        element = matmul(matrix, element)
        count += 1
    return count


def orbit_of(group, point):
    return tuple(sorted({matapply(element, point) for element in group}))


def declared_generators():
    """The declared generators, read from the payload's own declared group construction."""
    primary = section("S1_the_constellation_family")["primary"]
    return tuple(tuple(tuple(int(entry) for entry in row) for row in matrix)
                 for matrix in primary["generators"])


def frozen_generators():
    return (((-1, 0, 0), (0, -1, 0), (0, 0, 1)), ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
            ((-1, 0, 0), (0, -1, 0), (0, 0, -1)))


# --------------------------------------------------------------------------- tests -- 

def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["version"] == 1
    assert report["schema"] == SCHEMA
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract"] == "experiments/space_proposal_v3/contract.json"
    assert report["contract_sha256"] == digest(CONTRACT) == DECLARED_CONTRACT_SHA256
    assert report["contract_sha256_declared"] == DECLARED_CONTRACT_SHA256
    assert PROPOSAL_STATUS in report["contract_status"]
    assert PROPOSAL_STATUS in report["status"]
    assert "ExternalExactPass" in report["status"]
    assert report["assertions"] == FROZEN_ASSERTION_COUNT
    assert report["assertions"] <= contract["budgets"]["max_assertions"]
    assert report["limits"] == contract["budgets"]
    assert contract["budgets"]["child_processes"] == 0
    assert contract["budgets"]["routes"] == 1
    assert all(report["checks"].values())
    assert len(report["checks"]) == FROZEN_CHECK_COUNT
    assert report["residual"] == contract["residual"]
    assert report["protected"] == contract["protected"]
    assert report["acceptance"] == contract["acceptance"]
    assert report["tooling"]["external_libraries_imported"] == []
    assert report["tooling"]["exact_only"] is True
    assert report["tooling"]["declared_not_native_authority"] is True
    assert report["tooling"]["child_processes"] == 0
    source = CHECKER.read_text(encoding="utf-8")
    assert "RLIMIT_AS" not in source
    assert "RLIMIT_CPU" in source
    assert "RLIMIT_FSIZE" in source
    assert "signal.alarm" in source
    assert "float(Fr" not in source and "float(1" not in source


def test_the_shared_geometry_is_referenced_by_digest_and_never_recomputed():
    """The three referenced contracts are present at their declared digests."""
    report = load(EVIDENCE)
    referenced = report["referenced_by_digest"]
    assert sorted(referenced) == ["ratchet_model", "shared_geometry", "spacetime_group_clause"]
    for key in referenced:
        row = referenced[key]
        assert row["matches"] is True, key
        assert row["recomputed_here"] is False, key
        assert row["present_sha256"] == row["declared_sha256"], key
        assert digest(ROOT / row["path"]) == row["declared_sha256"], key
    contract = load(CONTRACT)
    assert referenced["shared_geometry"]["declared_sha256"] \
        == contract["inherits"]["shared_geometry"]["sha256"]
    assert referenced["spacetime_group_clause"]["declared_sha256"] \
        == contract["inherits"]["spacetime_group_clause"]["sha256"]
    assert referenced["ratchet_model"]["declared_sha256"] \
        == contract["inherits"]["ratchet_model"]["sha256"]


def test_the_orbit_structure_the_antipodal_count_and_the_group_are_recomputed_here():
    """The declared vertex construction, the two orbit sizes, the antipodal count and the group
    order are recomputed by this test's own exact integer matrix closure."""
    primary = section("S1_the_constellation_family")["primary"]
    generators = frozen_generators()
    assert declared_generators() == generators, "the payload declares the frozen generators"
    group = closure(generators)
    assert len(group) == EXPECTED_GROUP_ORDER == primary["point_group_order"]
    assert len(group) == primary["group_order_computed"]
    assert all(matdet(element) == 1 or matdet(element) == -1 for element in group)
    rotation_part = tuple(element for element in group if matdet(element) == 1)
    assert len(rotation_part) == EXPECTED_ROTATION_PART_ORDER == primary["rotation_part_order"]
    assert primary["improper_element_count"] == len(group) - len(rotation_part) == 12
    inversion = ((-1, 0, 0), (0, -1, 0), (0, 0, -1))
    assert inversion in group
    assert primary["contains_inversion"] is True
    assert sorted({element_order(element) for element in group}) == [1, 2, 3, 6]
    assert sorted({element_order(element) for element in rotation_part}) == [1, 2, 3]
    assert primary["five_fold_element_count"] == 0
    assert primary["contains_a_five_fold_element"] is False
    assert primary["is_crystallographic"] is True
    assert primary["element_orders"] == [1, 2, 3, 6]

    cube_orbit = orbit_of(group, CUBE_BASE)
    petrie_orbit = orbit_of(group, PETRIE_BASE)
    assert len(cube_orbit) == EXPECTED_CUBE_ORBIT == primary["cube_orbit_size"]
    assert len(petrie_orbit) == EXPECTED_PETRIE_ORBIT == primary["petrie_orbit_size"]
    assert set(cube_orbit) & set(petrie_orbit) == set()

    constellation = sorted(set(cube_orbit) | set(petrie_orbit))
    assert len(constellation) == EXPECTED_VERTEX_COUNT == primary["vertex_count"]
    assert [list(point) for point in constellation] == primary["declared_vertices"]
    assert primary["orbit_sizes"] == [EXPECTED_CUBE_ORBIT, EXPECTED_PETRIE_ORBIT]
    assert primary["orbit_count"] == 2

    antipodal = set()
    for point in constellation:
        image = matapply(inversion, point)
        assert image in set(constellation)
        assert image != point
        antipodal.add(tuple(sorted((point, image))))
    assert len(antipodal) == EXPECTED_ANTIPODAL_PAIRS == primary["antipodal_pair_count"]
    assert len(primary["antipodal_pairs_of_vertices"]) == EXPECTED_ANTIPODAL_PAIRS
    pairs = [tuple(sorted((tuple(a), tuple(b))))
             for a, b in primary["antipodal_pairs_of_vertices"]]
    assert sorted(pairs) == sorted(antipodal)
    assert primary["every_vertex_has_its_antipode_in_the_constellation"] is True

    for element in group:
        for point in constellation:
            assert matapply(element, point) in set(constellation)
    assert primary["invariance_failure_count"] == 0
    assert primary["a_general_pyritohedron_moves_only_within_each_orbit"] is True
    assert primary["every_element_is_a_signed_permutation"] is True
    assert primary["the_group_lies_inside_SO3"] is False
    assert primary["the_rotation_part_lies_inside_SO3"] is True


def test_the_declared_alternative_is_chiral_crystallographic_and_of_order_24():
    alternative = section("S1_the_constellation_family")["alternative"]
    generators = tuple(tuple(tuple(int(entry) for entry in row) for row in matrix)
                       for matrix in alternative["generators"])
    group = closure(generators)
    assert len(group) == EXPECTED_SNUB_CUBE_ORDER == alternative["point_group_order"]
    assert all(matdet(element) == 1 for element in group)
    assert alternative["improper_element_count"] == 0
    assert alternative["is_chiral"] is True
    assert alternative["every_element_has_determinant_plus_one"] is True
    assert 5 not in {element_order(element) for element in group}
    assert alternative["is_crystallographic"] is True
    assert alternative["contains_an_antipodal_pair"] is False
    base = (1, 2, 4)
    vertices = orbit_of(group, base)
    assert len(vertices) == alternative["vertex_count"]
    assert [list(point) for point in vertices] == alternative["declared_vertices"]


def test_the_two_regions_are_recomputed_here():
    regions = section("S2_the_two_regions")
    indicator = [int(value) for value in regions["declared_region_indicator"]]
    assert set(indicator) == {1, -1}
    assert indicator.count(1) == 10
    assert indicator.count(-1) == 10
    assert len(indicator) == EXPECTED_VERTEX_COUNT
    assert len(regions["sunward_region"]["vertex_indices"]) == 10
    assert len(regions["antisunward_region"]["vertex_indices"]) == 10
    assert sorted(regions["sunward_region"]["vertex_indices"]
                  + regions["antisunward_region"]["vertex_indices"]) == list(range(20))
    pairs = section("S1_the_constellation_family")["primary"]["antipodal_pairs_of_vertex_indices"]
    assert len(pairs) == EXPECTED_ANTIPODAL_PAIRS
    for first, second in pairs:
        assert indicator[first] == -indicator[second], (first, second)
    assert regions["each_antipodal_pair_serves_one_member_of_each_region"] is True
    assert regions["the_two_regions_have_opposite_declared_sense"] is True
    assert regions["sunward_indicator_is_exact_odd_under_the_declared_pairing_element"] is True
    assert regions["the_declared_schedule_is_computed_in_advance"] is True
    assert regions["no_step_is_chosen_in_flight"] is True
    assert regions["the_declared_addressing_table_step_count"] == 4
    for row in regions["the_declared_addressing_table"]:
        assert row["the_two_regions_carry_opposite_declared_sense"] is True
        sunward = [entry["declared_amplitude"]
                   for entry in row["sunward_region_declared_addressing"]]
        antisunward = [entry["declared_amplitude"]
                       for entry in row["antisunward_region_declared_addressing"]]
        assert len(sunward) == 10 and len(antisunward) == 10
        assert all(Fraction(value) == Fraction(row["declared_amplitude"]) for value in sunward)
        assert all(Fraction(value) == -Fraction(row["declared_amplitude"])
                   for value in antisunward)


def test_the_zero_the_reversal_and_the_pairing_are_exact():
    conditions = section("S3_the_spacetime_group_conditions")
    invariant = conditions["declared_invariant_pair"]
    broken = conditions["declared_broken_pair"]
    assert invariant["transport"]["value"] == EXPECTED_TRANSPORT_ZERO
    assert invariant["transport"]["unit"] == TRANSPORT_UNIT
    assert invariant["transport_is_zero"] is True
    flows = [Fraction(row["value"]) for row in invariant["per_step_flows"]]
    assert len(flows) == 4
    assert sum(flows) == 0
    assert flows[0] != 0, "the declared zero is not the trivial all-zero flow"
    assert flows[0] == -flows[2] and flows[1] == -flows[3]
    assert invariant["the_declared_per_step_flows_pair_exactly"] is True
    assert invariant["pairing_set_order"] == EXPECTED_GROUP_ORDER
    assert invariant["pairing_set_shifts"] == [2]
    assert invariant["the_declared_pairing_element_is_in_the_set"] is True
    assert invariant["is_non_symmorphic"] is True
    assert invariant["is_symmorphic"] is False
    assert len(invariant["pairing_set_elements"]) == EXPECTED_GROUP_ORDER
    assert invariant["rejected_claim"]["rejected"] is True
    assert invariant["rejected_claim"]["verdict"] == "Rejected"
    assert Fraction(invariant["rejected_claim"]["claimed_value"]["value"]) != 0
    assert Fraction(invariant["rejected_claim"]["derived_value"]["value"]) == 0

    plus = Fraction(broken["transport_at_plus_one"]["value"])
    minus = Fraction(broken["transport_at_minus_one"]["value"])
    assert plus == Fraction(EXPECTED_TRANSPORT_BROKEN)
    assert minus == -plus
    assert plus != 0
    assert plus + minus == 0
    assert broken["exact_reversal"]["the_exact_sum"] == "0"
    assert broken["exact_reversal"]["the_sum_is_exactly_zero"] is True
    assert broken["exact_reversal"]["the_direction_reverses_exactly"] is True
    assert broken["exact_reversal"]["the_transport_is_non_zero"] is True
    assert broken["the_declared_per_step_flows_pair_exactly"] is False
    assert broken["schedule_is_half_period_antisymmetric"] is False
    assert broken["rejected_claim"]["rejected"] is True
    assert broken["rejected_claim"]["discriminates"] is True

    standing_flows = [Fraction(row["value"]) for row in broken["per_step_flows_at_plus_one"]]
    standing_minus = [Fraction(row["value"]) for row in broken["per_step_flows_at_minus_one"]]
    assert sum(standing_flows) == plus
    assert all(left == -right for left, right in zip(standing_flows, standing_minus, strict=True))
    assert Fraction(conditions["declared_broken_pair"]
                    ["transport_at_the_declared_standing_gradient"]["value"]) == 0


def test_schedule_compatibility_discriminates_standing_from_travelling():
    compatibility = section("S4_schedule_compatibility")
    standing = compatibility["declared_standing_pattern"]
    travelling = compatibility["declared_travelling_pattern"]
    assert Fraction(standing["transport"]["value"]) == 0
    assert standing["the_transport_is_zero"] is True
    assert standing["is_a_standing_pattern"] is True
    assert standing["rejected_claim"]["rejected"] is True
    assert Fraction(standing["rejected_claim"]["claimed_value"]["value"]) != 0
    assert Fraction(travelling["transport_at_plus_one"]["value"]) != 0
    assert travelling["the_transport_is_non_zero"] is True
    assert travelling["is_a_travelling_pattern"] is True
    assert Fraction(travelling["transport_at_plus_one"]["value"]) \
        + Fraction(travelling["transport_at_minus_one"]["value"]) == 0
    assert travelling["the_direction_follows_the_gradient_sign"] is True


def test_the_entry_window_constants_are_declared_and_the_W4_inequality_is_recomputed_here():
    """W1 to W4 are recomputed from the payload's own declared numbers."""
    window = section("S5_the_entry_window_W1_to_W4")
    threshold = Fraction(window["the_declared_percolation_threshold"]["value"])
    latent = Fraction(window["the_declared_latent_heat"]["value"])
    region_vertices = Fraction(window["the_declared_connected_region_vertex_count"]["value"])
    fraction = Fraction(window["the_declared_safety_fraction"]["value"])
    bound = Fraction(window["the_declared_safety_bound"]["value"])
    action = Fraction(window["the_declared_single_action_energy"]["value"])
    region_latent = Fraction(window
                             ["the_declared_latent_heat_of_a_connected_region_at_the_threshold"]
                             ["value"])
    assert region_latent == latent * region_vertices
    assert bound == fraction * region_latent
    assert action < bound
    assert window["the_declared_action_is_strictly_below_the_declared_bound"] is True
    assert window["declared_constants_and_thresholds_not_measurements"] is True
    assert window["no_data_is_read_or_used"] is True
    assert threshold not in (bound, action)

    above = window["W1_the_declared_state_above_the_declared_threshold"]
    below = window["W1_the_declared_state_below_the_declared_threshold"]
    at = window["W1_the_declared_state_at_the_declared_threshold"]
    assert Fraction(above["declared_state_value"]["value"]) > threshold
    assert Fraction(below["declared_state_value"]["value"]) < threshold
    assert Fraction(at["declared_state_value"]["value"]) == threshold
    assert above["entry_accepted"] is True
    assert below["entry_accepted"] is False
    assert at["entry_accepted"] is True

    refusals = window["refusals"]
    assert len(refusals) == window["refusal_count"] == 4
    assert all(row["refused"] is True for row in refusals)
    assert all(row["executed"] is True for row in refusals)
    assert {row["refusal_id"] for row in refusals} == {
        "W1-BELOW-THE-DECLARED-PERCOLATION-THRESHOLD", "W2-ENTRY-AFTER-SEALING", "W3-SILENT-THRESHOLD-CROSSING", "W4-A-SINGLE-DECLARED-ACTION-REACHING-THE-DECLARED-BOUND",
    }
    control = window["rejected_claim"]
    assert control["rejected"] is True
    assert Fraction(control["derived_value"]["value"]) >= bound
    assert Fraction(control["claimed_value"]["value"]) == bound


def test_the_declared_ablation_levels_carry_every_task_and_no_magnitude():
    levels = section("S6_the_declared_ablation_levels")
    values = levels["declared_level_values"]
    assert values == sorted(values)
    assert len(values) == levels["declared_level_count"]
    assert len(set(values)) == len(values)
    counts = {row["declared_level_value"]: row["task_count"]
              for row in levels["tasks_per_declared_level"]}
    assert sorted(counts) == values
    assert all(counts[value] > 0 for value in values), "every declared level carries a task"
    assert sum(counts.values()) == levels["assignment_count"] == len(levels["assignments"])
    for row in levels["assignments"]:
        assert row["assigned_to_a_level"] is True
        assert row["assigned_to_a_platform"] is False
        assert row["assigned_level_value"] in values
        assert row["is_a_magnitude_of_a_physical_quantity"] is False
    assert levels["every_task_is_assigned_to_a_declared_level"] is True
    assert levels["no_task_is_assigned_to_a_platform"] is True
    assert levels["no_level_outside_the_declared_set_is_used"] is True
    assert levels["no_magnitude_of_any_physical_quantity_is_used"] is True
    assert levels["control_count"] == 2
    assert all(row["rejected"] is True for row in levels["controls"])
    assert key_findings(levels, FORBIDDEN_EFFECT_KEYS) == []


def test_stage_one_carries_the_declared_units_identically():
    stage = section("S7_stage_one")
    assert Fraction(stage["declared_unit_count"]["value"]) == 4096
    assert Fraction(stage["declared_recipient_count"]["value"]) == 64
    assert Fraction(stage["declared_units_per_recipient"]["value"]) == 64
    assert stage["the_declared_units_divide_exactly_among_the_recipients"] is True
    assert stage["the_three_declared_stages_carry_identical_counts_and_identical_index_sums"] is True
    for name in ("computed", "aggregated", "distributed"):
        row = stage[name]
        assert row["unit_count"] == 4096
        assert row["unit_index_sum"] == 4096 * 4095 // 2
        assert row["unit_index_sum_of_squares"] == (4095 * 4096 * 8191) // 6
    growth = stage["growth_steps"]
    assert len(growth) == stage["growth_step_count"] == 8
    assert growth[0]["declared_launches"] == 1
    assert growth[0]["declared_learning_units"] == 4
    assert all(row["declared_learning_units"] > 0 for row in growth)
    assert all(growth[i]["cumulative_declared_launches"]
               < growth[i + 1]["cumulative_declared_launches"] for i in range(len(growth) - 1))
    assert growth[-1]["cumulative_declared_launches"] == 36
    assert stage["learning_enters_at_the_first_declared_step"] is True
    assert stage["control_count"] == 2
    assert all(row["rejected"] is True for row in stage["controls"])
    assert {row["control_id"] for row in stage["controls"]} == {
        "STAGE-TOPOLOGY-BROKEN", "STAGE-LEARNING-DELAYED"}


def test_every_declared_overreach_is_executed_and_refused():
    overreach = section("S8_the_declared_overreaches")
    controls = overreach["controls"]
    assert len(controls) == overreach["control_count"] == 5
    assert all(row["rejected"] is True for row in controls)
    assert all(row["discriminates"] is True for row in controls)
    assert {row["control_id"] for row in controls} == {
        "OVR-ICOSAHEDRAL-LATTICE-COMPATIBLE", "OVR-PATTERN-SHAPE-FIXES-THE-DIRECTION", "OVR-THE-TWO-ORBITS-ARE-THE-SAME-COMBINATORIAL-KIND", "OVR-THE-FAMILY-MEMBERS-HAVE-DIFFERENT-TOPOLOGY", "OVR-FULL-POINT-GROUP-INSIDE-SO3",
    }
    icosahedral = overreach["the_icosahedral_constellation"]
    assert icosahedral["lattice_compatible"] is False
    assert icosahedral["is_crystallographic"] is False
    assert icosahedral["contains_a_five_fold_element"] is True
    assert icosahedral["five_fold_element_count"] == 24
    assert icosahedral["declared_rotation_group_order"] == 60
    assert icosahedral["element_orders"] == [1, 2, 3, 5]
    orbits = overreach["the_two_declared_orbits"]
    assert orbits["cube_orbit_size"] == 8
    assert orbits["petrie_orbit_size"] == 12
    assert orbits["cube_orbit_point_stabiliser_order"] != orbits["petrie_orbit_point_stabiliser_order"]
    assert orbits["combinatorially_different"] is True
    assert orbits["every_element_stays_inside_its_own_orbit"] is True
    assert orbits["no_element_maps_one_orbit_onto_the_other"] is True
    assert overreach["the_declared_combinatorial_type_is_referenced_not_recomputed"] is True
    assert overreach["the_declared_euler_characteristic"] == 2
    assert overreach["the_declared_primary_euler_identity"] == "20 - 30 + 12 = 2"
    assert overreach["the_declared_alternative_euler_identity"] == "24 - 36 + 14 = 2"


def test_the_payload_records_proposal_only_bookkeeping():
    bookkeeping = section("S9_proposal_only_bookkeeping")
    contract = load(CONTRACT)
    assert bookkeeping["authorization"] == NO_NONE
    assert bookkeeping["decision"] == NO_NONE
    assert bookkeeping["deployment"] == NO_NONE
    assert bookkeeping["governance"] == UNASSESSED
    assert bookkeeping["physical_effect_asserted"] == NO_NONE
    assert bookkeeping["data_used"] == NO_NONE
    assert bookkeeping["status"] == PROPOSAL_STATUS
    assert PROPOSAL_STATUS in contract["status"]
    assert bookkeeping["authorizes_nothing"] is True
    assert bookkeeping["decides_nothing"] is True
    assert bookkeeping["deploys_nothing"] is True
    assert bookkeeping["no_governance_assessment"] is True
    assert bookkeeping["termination_problem"]["status"] == UNADDRESSED
    assert bookkeeping["termination_problem"]["solved_here"] is False
    assert "提议性方案" in bookkeeping["proposal_only_in_chinese_and_english"]
    assert "who might decide" in bookkeeping["nothing_said_about_who_might_decide"]

    claimed = load(EVIDENCE)["what_is_not_claimed"]
    assert claimed["authorization"] == NO_NONE
    assert claimed["decision"] == NO_NONE
    assert claimed["deployment"] == NO_NONE
    assert claimed["governance"] == UNASSESSED
    assert claimed["physical_effect_asserted"] == NO_NONE
    assert claimed["data_used"] == NO_NONE
    assert claimed["physical_claim"] is False
    assert claimed["magnitude_sign_or_timing_of_any_physical_quantity"] == NO_NONE
    assert claimed["no_magnitude_for_any_physical_quantity"] is True
    assert claimed["no_sign_of_any_physical_quantity"] is True
    assert claimed["no_timing_of_any_physical_quantity"] is True
    assert claimed["nothing_is_ablated_melted_moved_or_heated"] is True
    assert claimed["nothing_is_moved"] is True
    assert claimed["nothing_is_heated"] is True
    assert claimed["no_pattern_is_projected_onto_any_real_surface"] is True
    assert claimed["no_data_read_or_used"] is True
    assert claimed["no_clock_read"] is True
    assert claimed["the_document_is_a_proposal_only"] is True
    assert claimed["no_claim_added_to_docs_claims_toml"] is True
    assert claimed["no_parent_contract_or_note_edited"] is True
    assert claimed["no_rust_source_or_lock_changed"] is True
    assert claimed["native_certificate"] is False
    assert claimed["native_admission"] == "NotGranted"
    assert claimed["the_entry_window_thresholds_are_declared_and_not_measured"] is True
    assert claimed["the_termination_problem_is_unaddressed_and_unsolved"] is True

    status = load(EVIDENCE)["verification_status"]
    assert status["observational"] == "Unavailable"
    checked = status["checked_here"]
    assert checked["no_data_read_or_used"] is True
    assert checked["nothing_is_ablated_melted_moved_or_heated"] is True
    assert checked["no_pattern_is_projected_onto_any_real_surface"] is True
    assert checked["every_declared_arithmetic_is_exact"] is True
    assert checked["governance_is_unaddressed"] is True
    assert checked["the_shared_geometry_is_referenced_and_not_recomputed"] is True


def test_the_payload_is_free_of_floating_point_literals_host_paths_and_timestamps():
    raw = EVIDENCE.read_text(encoding="utf-8")
    assert load(EVIDENCE)
    assert "NaN" not in raw and "Infinity" not in raw
    assert "/Users/" not in raw and "mingli" not in raw
    assert ".venv" not in raw and "/tmp" not in raw
    report = load(EVIDENCE)
    assert report["checks"]["no_floating_point_value_is_retained"] is True
    assert report["checks"]["no_magnitude_of_any_physical_quantity_appears_anywhere"] is True
    assert key_findings(report, FORBIDDEN_EFFECT_KEYS) == []
    assert key_findings(report, FORBIDDEN_TIME_KEYS) == []
    assert not re.search(r"\d+\.\d+", raw), "no decimal literal appears anywhere"


def test_the_frozen_shape_of_every_section():
    report = load(EVIDENCE)
    assert sorted(report["sections"]) == sorted(SECTION_NAMES)
    for name, keys in FROZEN_SECTION_SHAPE.items():
        assert sorted(report["sections"][name]) == sorted(keys), name
    assert sorted(report) == [ "acceptance", "assertions", "checker_sha256", "checks", "contract", "contract_sha256", "contract_sha256_declared", "contract_status", "controls", "declared_model", "limits", "modelling_choices", "protected", "referenced_by_digest", "residual", "schema", "sections",
        "status", "tooling", "undecided", "verification_status", "version", "what_is_not_claimed"]
    primary = report["sections"]["S1_the_constellation_family"]["primary"]
    assert sorted(primary["declared_combinatorial_type"]) == [ "declared_edge_count", "declared_euler_characteristic", "declared_face_count", "declared_vertex_count", "euler_identity_stated_exactly", "internally_consistent", "reading", "recomputed_here", "source"]
    assert sorted(report["controls"]["failed_controls"][0]) == [ "control", "control_id", "derived_transport", "discriminates", "outcome", "reading", "variant", "variant_transport", "why"]


def test_the_controls_and_the_failed_control_are_all_reported():
    report = load(EVIDENCE)
    controls = report["controls"]
    assert controls["control_count"] == controls["controls_executed"] == FROZEN_CONTROL_COUNT
    assert controls["controls_rejected"] == FROZEN_CONTROL_COUNT
    assert controls["every_control_produces_a_rejection"] is True
    assert controls["no_control_is_dropped"] is True
    assert len(controls["controls"]) == FROZEN_CONTROL_COUNT
    for row in controls["controls"]:
        assert row["rejected"] is True, row["control_id"]
        assert row["discriminates"] is True, row["control_id"]
        assert row["verdict"] == "Rejected"
        assert row["rejection_reasons"]
        assert row["rejected_by"]
        assert row["accepted_companion"]["accepted"] is True
        assert Fraction(row["derived_value"]["value"]) != Fraction(row["claimed_value"]["value"])
    failed = controls["failed_controls"]
    assert controls["failed_controls_count"] == 1
    assert len(failed) == 1
    assert failed[0]["outcome"] == "FAILED_TO_DISCRIMINATE"
    assert failed[0]["discriminates"] is False
    assert failed[0]["derived_transport"] == failed[0]["variant_transport"]
    assert "FAILED control" in failed[0]["why"]
    assert "rather than repaired" in failed[0]["why"]
    assert "retained" in controls["why_the_failed_control_is_retained"]


def test_a_copied_checkout_reproduces_the_retained_payload(tmp_path):
    """The checker is re-run on a COPY: the payload must not depend on its location."""
    copied = tmp_path / "experiments" / "space_proposal_v3"
    copied.mkdir(parents=True)
    shutil.copy(CHECKER, copied / "calibration.py")
    shutil.copy(CONTRACT, copied / "contract.json")
    for name in ("geometry_foundation_v1", "spatiotemporal_ratchet_v1"):
        shutil.copytree(ROOT / "experiments" / name, tmp_path / "experiments" / name)
    output = tmp_path / "on-a-copy.json"
    completed = invoke(copied / "calibration.py", output)
    assert completed.returncode == 0, completed.stderr
    fresh = load(output)
    retained = load(EVIDENCE)
    assert fresh["status"] == retained["status"]
    assert fresh["assertions"] == retained["assertions"]
    assert fresh["sections"] == retained["sections"]
    assert fresh["checks"] == retained["checks"]
    assert fresh["controls"] == retained["controls"]
    assert fresh["undecided"] == retained["undecided"]
    assert fresh["what_is_not_claimed"] == retained["what_is_not_claimed"]
    assert fresh["modelling_choices"] == retained["modelling_choices"]
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
    added it, WITH the disclosed transport defect of note 0244; the assertion is inverted rather than
    dropped, so the binding stays checked.
    """
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    assert claims
    matches = [row for row in claims if row.get("claim_id") == CLAIM_ID]
    assert len(matches) == 1, "exactly one claim must be registered for this run"
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for symbol in ("space_proposal_v3/calibration.py",
                   "space_proposal_v3/contract.json",
                   "space_proposal_v3/evidence.json",
                   "0244-proposal-three"):
        assert symbol in claim["code_symbol"], symbol
    boundary = claim["counterexample_boundary"].lower()
    assert "failed to discriminate" in boundary, "the boundary must retain the failed control"
    assert "edge sum" in boundary, "the boundary must carry the disclosed transport defect"
    assert "NotGranted" in claim["counterexample_boundary"], "the boundary must record native admission"
    assert claim["forbidden_conflations"], "the claim must name its conflations"

