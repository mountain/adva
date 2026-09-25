"""The paired test for the optical-imbalance proposal v1 exact calibration.

The assertions here are about what the retained checker decided by exact arithmetic on a PROPOSAL
ONLY document - 提议性方案: the three derived bounds (the passive spot floor theta_sun * L on three
declared platforms with the near-Earth value cross-checked against the historically reported case
of a 20-metre mirror and a 5 km spot, the étendue-limited single-mode ceiling of order B *
lambda^2, and the second-Lagrange-point usable fraction 1 - (theta_earth / theta_sun)^2 with the
derived annulus and usable flux), the division of labour with the fibre bound as its reason, the two
deployment modes with their own floors and sustainment statements, the declared-target arithmetic
as arithmetic on declared proposal inputs, the six overreach controls each producing a rejection
with the one failed control retained, the two inherited prohibitions executed and the termination
problem recorded as Unaddressed, and the proposal-only bookkeeping.

They are not claims about any physical object.  No effect on any atmosphere, ocean, cloud, surface,
weather or climate is asserted anywhere in the retained payload and the test checks that absence:
the target figures are the arithmetic inputs of a proposal.

The checker is invoked without `-S`; it imports nothing beyond the standard library, so the run is
an external exact calibration with no host package in the path.  Every declared constant is
recomputed here from the payload's own exact strings, so the numbers are checked twice: once by the
checker and once by this test's independent arithmetic on the same declared constants.

The record carries no claim for this run: the parent session adds the claim to `docs/claims.toml`
with its note, so the last test asserts the claim is ABSENT rather than dropping the binding.
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
HERE = ROOT / "experiments/optical_imbalance_proposal_v1"
CHECKER = HERE / "calibration.py"
CONTRACT = HERE / "contract.json"
EVIDENCE = HERE / "evidence.json"
SURGERY_CONTRACT = ROOT / "experiments/three_cycle_supplement_v1/contract.json"
ROUNDED_CONTRACT = ROOT / "experiments/three_cycle_supplement_v2/contract.json"

CLAIM_ID = "adva.bounded-experiment.optical-imbalance-proposal.v0"
DECLARED_CONTRACT_SHA256 = "116913a9369e43666d80cf65a6877164f186fd813955a4d1c05f39777496fa4f"
DECLARED_SURGERY_SHA256 = "157838642e9097ea4a1a1c7461db9e548affb0c6f3af7b830816f37f22b74f5a"
DECLARED_ROUNDED_SHA256 = "823eedfaa492d0524c901793b580d5f02b67d7cf739f26781e326aa667d1e990"

SCHEMA = "adva.external.optical-imbalance-proposal-calibration.v1"
PROPOSAL_STATUS = "PROPOSAL ONLY - 提议性方案"
NO_NONE = "none"
UNASSESSED = "unaddressed"
NO_DATA = "none"
FROZEN_ASSERTION_COUNT = 126

SECTION_NAMES = (
    "R1_derived_bounds", "R2_division_of_labour", "R3_deployment_modes",
    "R4_declared_target_arithmetic", "R5_overreach_controls", "R6_inherited_prohibitions",
    "R7_proposal_only_bookkeeping",
)

TOP_LEVEL_KEYS = (
    "assertions", "checker_sha256", "checks", "contract", "contract_sha256",
    "contract_sha256_declared", "level", "limits", "modelling_choices", "parent_contracts",
    "protected", "residual", "schema", "sections", "status", "tooling", "undecided",
    "verification_status", "version", "what_is_not_claimed",
)

FROZEN_SECTION_SHAPE = {
    "R1_derived_bounds": [
        "all_three_bounds_are_derived_from_declared_constants",
        "bounds_are_bounds_on_instruments_not_effects",
        "declared_constants",
        "declared_constants_count",
        "declared_inputs_are_declared_and_not_measured",
        "declared_inputs_statement",
        "fibre_power_ceiling",
        "l2_usable_fraction",
        "no_physics_is_asserted_by_these_bounds",
        "passive_spot_floor",
        "the_three_bounds",
    ],
    "R2_division_of_labour": [
        "diffractive_stage", "fibres", "mirrors", "no_power_is_routed_through_fibres",
        "statement", "the_division_is_forced_not_stylistic", "the_fibre_bound_is_the_reason", "why",
    ],
    "R3_deployment_modes": [
        "each_mode_has_its_own_geometric_floor", "each_mode_has_its_own_sustainment_statement",
        "floor_ratio_of_the_largest_to_the_smallest", "mode_A_second_lagrange_point",
        "mode_B_near_earth_relay", "mode_B_usable_fraction_is_declared_not_derived",
        "mode_B_usable_fraction_note", "mode_count", "no_fourth_platform_is_declared",
        "separate_accounts_statement", "the_modes_are_a_declared_choice",
        "the_two_modes_are_declared_separately", "the_two_modes_are_not_netted",
    ],
    "R4_declared_target_arithmetic": [
        "areal_mass", "arithmetic_on_declared_proposal_inputs", "declared_target",
        "fibres_the_required_power_would_need", "launch_years", "mirror_elements",
        "no_effect_is_asserted", "required_intercepting_area", "required_power", "statement",
        "the_arithmetic_is_ideal_and_is_a_lower_bound",
        "the_delivery_efficiency_is_declared_exactly_one",
    ],
    "R5_overreach_controls": [
        "control_count", "controls", "controls_executed", "controls_rejected",
        "every_control_produces_a_rejection", "failed_controls", "failed_controls_count",
        "no_control_is_dropped", "why_the_failed_control_is_retained",
    ],
    "R6_inherited_prohibitions": [
        "inherited_prohibitions", "inherited_prohibitions_apply_to_any_use",
        "inherited_prohibitions_count", "no_netting", "parent_contracts_cited",
        "sealing_refused_for_the_termination", "termination_problem",
    ],
    "R7_proposal_only_bookkeeping": [
        "authorization", "authorizes_nothing", "data_used", "decides_nothing", "decision",
        "deployment", "deploys_nothing", "governance", "no_governance_assessment",
        "nothing_said_about_who_might_decide", "physical_effect_asserted",
        "proposal_only_in_chinese_and_english", "proposal_only_statement", "record_purpose",
        "status",
    ],
}

DECLARED_CONSTANT_VALUES = {
    "astronomical_unit": ("149597870700", "m"),
    "solar_radius": ("695700000", "m"),
    "earth_mean_radius": ("6371000", "m"),
    "near_earth_distance": ("400000", "m"),
    "geostationary_distance": ("35786000", "m"),
    "second_lagrange_distance": ("1500000000", "m"),
    "reported_mirror_diameter": ("20", "m"),
    "reported_spot": ("5000", "m"),
    "solar_constant_at_one_au": ("1361", "W m^-2"),
    "target_patch_area": ("100000000", "m^2"),
    "target_flux": ("10000", "W m^-2"),
    "wavelength": ("1/1000000", "m"),
    "spectral_radiance_B": ("1000000", "W m^-2 sr^-1"),
    "areal_density": ("1/10", "kg m^-2"),
    "annual_launch_rate": ("100000", "kg year^-1"),
    "mirror_element_side": ("20", "m"),
    "declared_fibre_count": ("1000000", "1"),
    "coherent_fraction": ("1/1000", "1"),
    "blaze_first_order_share": ("3/5", "1"),
    "other_first_order_share": ("2/5", "1"),
    "symmetric_grating_order_share": ("1/2", "1"),
    "zero_order_share": ("0", "1"),
    "gigawatt_reference_power": ("1000000000", "W"),
}

THETA_SUN_AT_ONE_AU = "4638000/498659569"
THETA_SUN_AT_L2 = "1546000/167886523"
FLOOR_NEAR_EARTH = "1855200000000/498659569"
FLOOR_GEOSTATIONARY = "165975468000000/498659569"
FLOOR_L2 = "2319000000000000/167886523"
FLOOR_RATIO_L2_OVER_NEAR_EARTH = "623324461250/167886523"
EARTH_DIAMETER = "12742000"
L2_FLOOR_MINUS_EARTH_DIAMETER = "179789923934000/167886523"
REPORTED_FLOOR_WITH_THE_APERTURE = "1865173191380/498659569"
REPORTED_SPOT_OVER_THE_FLOOR = "124664892250/93258659569"
REPORTED_IMPLIED_DISTANCE = "41388744227/77300"
PER_MODE_POWER = "1/1000000"
FIBRES_FOR_A_GIGAWATT = "1000000000000000"
FIBRES_FOR_A_MEGAWATT = "1000000000000"
FIBRES_FOR_THE_REQUIRED_POWER = "1000000000000000000"
DECLARED_NETWORK_MAXIMUM_POWER = "1"
OCCULTED_FRACTION = "1144054937385575376509089/5377761000000000000000000"
USABLE_FRACTION = "4233706062614424623490911/5377761000000000000000000"
THETA_RATIO_AT_L2 = "1069605038033/2319000000000"
UMBRA_LENGTH = "953088034229700/689329"
IRRADIANCE_AT_L2 = "338428118792916700721/253672961445265761"
USABLE_FLUX = ("1432805178292766127971612615837653783650646831/"
               "1364192558814853844141121000000000000000000")
REQUIRED_POWER = "1000000000000"
REQUIRED_AREA = ("1364192558814853844141121000000000000000000000000000000/"
                 "1432805178292766127971612615837653783650646831")
AREAL_MASS = ("136419255881485384414112100000000000000000000000000000/"
              "1432805178292766127971612615837653783650646831")
LAUNCH_YEARS = ("1364192558814853844141121000000000000000000000000/"
                "1432805178292766127971612615837653783650646831")
MIRROR_ELEMENTS = ("3410481397037134610352802500000000000000000000000000/"
                   "1432805178292766127971612615837653783650646831")
AREA_OVER_PATCH = ("13641925588148538441411210000000000000000000000/"
                   "1432805178292766127971612615837653783650646831")
LOOSENED_AREA = "253672961445265761000000000000/338428118792916700721"
MODE_B_AREA = "1000000000000/1361"
MODE_B_MASS = "100000000000/1361"
MODE_B_YEARS = "1000000/1361"

CONTROL_ROW_KEYS = (
    "accepted_companion", "claim", "claimed_value", "control", "derived_value", "discriminates",
    "rejected", "rejected_by", "rejection_reasons", "unit", "verdict",
)

FORBIDDEN_EFFECT_KEYS = (
    "effect", "temperature", "forcing", "precipitation", "rainfall", "cloud", "ocean", "weather",
    "climate", "warming", "cooling", "albedo", "damage", "benefit", "yield", "anomaly", "tendency",
    "sensitivity",
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
    rows = {row["name"]: row for row in section("R1_derived_bounds")["declared_constants"]}
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


def test_retained_evidence_is_an_external_pass_inside_the_contract():
    report = load(EVIDENCE)
    contract = load(CONTRACT)
    assert report["status"] == "ExternalExactPass"
    assert report["schema"] == SCHEMA
    assert report["version"] == 1
    assert report["checker_sha256"] == digest(CHECKER)
    assert report["contract"] == "experiments/optical_imbalance_proposal_v1/contract.json"
    assert report["contract_sha256"] == digest(CONTRACT) == DECLARED_CONTRACT_SHA256
    assert report["contract_sha256_declared"] == DECLARED_CONTRACT_SHA256
    assert report["assertions"] == FROZEN_ASSERTION_COUNT
    assert report["assertions"] <= contract["budgets"]["max_assertions"]
    assert report["limits"] == contract["budgets"]
    assert contract["budgets"]["child_processes"] == 0
    assert contract["budgets"]["routes"] == 1
    assert all(report["checks"].values())
    assert len(report["checks"]) == 45
    assert report["level"] == contract["level"]
    assert report["residual"] == contract["residual"]
    assert report["protected"] == contract["protected"]
    assert report["tooling"]["declared_not_native_authority"] is True
    assert report["tooling"]["exact_only"] is True
    assert report["tooling"]["external_libraries_imported"] == []
    assert report["tooling"]["declared_external_library_available_but_unused"] == "sympy 1.14"
    assert report["tooling"]["not_implemented"]
    assert "RLIMIT_AS" not in CHECKER.read_text(encoding="utf-8")
    assert "RLIMIT_CPU" in CHECKER.read_text(encoding="utf-8")
    assert "RLIMIT_FSIZE" in CHECKER.read_text(encoding="utf-8")
    parents = {row["path"]: row for row in report["parent_contracts"]}
    assert len(parents) == 2
    assert parents["experiments/three_cycle_supplement_v1/contract.json"]["sha256"] \
        == digest(SURGERY_CONTRACT) == DECLARED_SURGERY_SHA256
    assert parents["experiments/three_cycle_supplement_v2/contract.json"]["sha256"] \
        == digest(ROUNDED_CONTRACT) == DECLARED_ROUNDED_SHA256
    assert all(row["retained_byte_for_byte"] for row in report["parent_contracts"])
    assert all(row["sha256"] == row["sha256_declared"] for row in report["parent_contracts"])


def test_the_declared_constants_are_exact_declared_rationals_with_units():
    """Every constant is declared, exact, carries its unit, and is not a measurement of the run."""
    bounds = section("R1_derived_bounds")
    rows = {row["name"]: row for row in bounds["declared_constants"]}
    assert len(rows) == 23
    assert bounds["declared_constants_count"] == 23
    assert sorted(rows) == sorted(DECLARED_CONSTANT_VALUES)
    for name, (value, unit) in DECLARED_CONSTANT_VALUES.items():
        assert rows[name]["value"] == value, name
        assert rows[name]["unit"] == unit, name
        assert Fraction(value) is not None, name
        assert rows[name]["declared"] is True
        assert rows[name]["measured_here"] is False
        assert rows[name]["read_from_data"] is False
        assert rows[name]["role"]
    assert bounds["declared_inputs_are_declared_and_not_measured"] is True
    assert "DECLARED input" in bounds["declared_inputs_statement"]
    assert "none of them is a measurement of this run" in bounds["declared_inputs_statement"]
    assert bounds["all_three_bounds_are_derived_from_declared_constants"] is True
    assert bounds["bounds_are_bounds_on_instruments_not_effects"] is True
    assert "not statements about any atmosphere" in bounds["no_physics_is_asserted_by_these_bounds"]

    # the three bounds recomputed here from the payload's own declared constants, independently
    astronomical_unit = declared("astronomical_unit")
    solar_radius = declared("solar_radius")
    earth_radius = declared("earth_mean_radius")
    near_earth = declared("near_earth_distance")
    geostationary = declared("geostationary_distance")
    second_lagrange = declared("second_lagrange_distance")
    solar_constant = declared("solar_constant_at_one_au")
    wavelength = declared("wavelength")
    radiance = declared("spectral_radiance_B")
    theta_one_au = 2 * solar_radius / astronomical_unit
    theta_l2 = 2 * solar_radius / (astronomical_unit + second_lagrange)
    assert theta_one_au == Fraction(THETA_SUN_AT_ONE_AU)
    assert theta_l2 == Fraction(THETA_SUN_AT_L2)
    assert theta_one_au * near_earth == Fraction(FLOOR_NEAR_EARTH)
    assert theta_one_au * geostationary == Fraction(FLOOR_GEOSTATIONARY)
    assert theta_l2 * second_lagrange == Fraction(FLOOR_L2)
    assert radiance * wavelength * wavelength == Fraction(PER_MODE_POWER)
    assert Fraction(1) - (earth_radius / second_lagrange) ** 2 / theta_l2 ** 2 \
        == Fraction(USABLE_FRACTION)
    assert Fraction(USABLE_FRACTION) * solar_constant \
        * (astronomical_unit / (astronomical_unit + second_lagrange)) ** 2 \
        == Fraction(USABLE_FLUX)


def test_the_three_derived_bounds_are_exact():
    bounds = section("R1_derived_bounds")
    floor = bounds["passive_spot_floor"]
    assert floor["rule"].startswith("theta_sun * L")
    assert "full angular size" in floor["theta_sun_declared_as"]
    assert floor["theta_sun_at_one_au"]["value"] == THETA_SUN_AT_ONE_AU
    assert floor["theta_sun_at_one_au"]["unit"] == "rad"
    assert floor["theta_sun_at_the_second_lagrange_point"]["value"] == THETA_SUN_AT_L2
    assert floor["platform_count"] == 3
    platforms = {row["name"]: row for row in floor["platforms"]}
    assert sorted(platforms) == ["a geostationary platform", "a near-Earth platform",
                                 "the second Lagrange point"]
    assert sorted(platforms["a near-Earth platform"]) == [
        "declared_distance", "floor", "name", "theta_sun"]
    assert platforms["a near-Earth platform"]["declared_distance"]["value"] == "400000"
    assert platforms["a near-Earth platform"]["floor"]["value"] == FLOOR_NEAR_EARTH
    assert platforms["a near-Earth platform"]["floor"]["between_the_exact_integers"] == ["3720",
                                                                                         "3721"]
    assert platforms["a geostationary platform"]["declared_distance"]["value"] == "35786000"
    assert platforms["a geostationary platform"]["floor"]["value"] == FLOOR_GEOSTATIONARY
    assert platforms["a geostationary platform"]["floor"]["between_the_exact_integers"] == [
        "332843", "332844"]
    assert platforms["the second Lagrange point"]["declared_distance"]["value"] == "1500000000"
    assert platforms["the second Lagrange point"]["floor"]["value"] == FLOOR_L2
    assert platforms["the second Lagrange point"]["floor"]["between_the_exact_integers"] == [
        "13812901", "13812902"]
    assert floor["smallest_floor"]["value"] == FLOOR_NEAR_EARTH
    assert floor["largest_floor"]["value"] == FLOOR_L2
    assert floor["the_largest_floor_is_at_the_second_lagrange_point"] is True
    assert floor["floor_ratio_of_the_largest_to_the_smallest"] == FLOOR_RATIO_L2_OVER_NEAR_EARTH
    assert Fraction(FLOOR_L2) > Fraction(FLOOR_GEOSTATIONARY) > Fraction(FLOOR_NEAR_EARTH)
    assert floor["the_l2_floor_exceeds_the_earths_diameter"] is True
    assert floor["earth_diameter"]["value"] == EARTH_DIAMETER
    assert Fraction(EARTH_DIAMETER) == 2 * Fraction(declared("earth_mean_radius"))
    assert floor["l2_floor_minus_the_earths_diameter"]["value"] == L2_FLOOR_MINUS_EARTH_DIAMETER
    assert Fraction(L2_FLOOR_MINUS_EARTH_DIAMETER) > 0

    ceiling = bounds["fibre_power_ceiling"]
    assert "B * lambda^2" in ceiling["rule"]
    assert ceiling["declared_spectral_radiance"]["value"] == "1000000"
    assert ceiling["declared_spectral_radiance"]["unit"] == "W m^-2 sr^-1"
    assert ceiling["declared_wavelength"]["value"] == "1/1000000"
    assert ceiling["declared_wavelength"]["unit"] == "m"
    assert ceiling["per_mode_power"]["value"] == PER_MODE_POWER
    assert ceiling["per_mode_power"]["unit"] == "W"
    assert ceiling["per_mode_power_is_microwatts"] is True
    assert Fraction(PER_MODE_POWER) == Fraction(1, 10 ** 6)
    assert ceiling["gigawatt_reference_power"]["value"] == "1000000000"
    assert ceiling["fibres_a_gigawatt_would_need"]["value"] == FIBRES_FOR_A_GIGAWATT
    assert ceiling["fibres_a_megawatt_would_need"]["value"] == FIBRES_FOR_A_MEGAWATT
    assert Fraction(FIBRES_FOR_A_GIGAWATT) == 10 ** 15
    assert Fraction(FIBRES_FOR_A_MEGAWATT) == 10 ** 12
    assert Fraction(ceiling["the_megawatt_is_this_fraction_of_the_declared_gigawatt"]) \
        == Fraction(1, 1000)
    assert ceiling["the_contracts_reported_order"] == "of order a trillion fibres for a gigawatt"
    assert "10^15" in ceiling["the_exact_count_and_the_reported_order"]
    assert "not repaired" in ceiling["the_exact_count_and_the_reported_order"]
    assert ceiling["declared_fibre_count"]["value"] == "1000000"
    assert ceiling["maximum_power_the_declared_fibre_network_can_carry"]["value"] \
        == DECLARED_NETWORK_MAXIMUM_POWER
    assert ceiling["maximum_power_the_declared_fibre_network_can_carry"]["unit"] == "W"
    assert ceiling["fibres_the_required_power_would_need"]["value"] \
        == FIBRES_FOR_THE_REQUIRED_POWER
    assert Fraction(FIBRES_FOR_THE_REQUIRED_POWER) == 10 ** 18
    assert ceiling["fibres_the_coherent_part_would_need"]["value"] == FIBRES_FOR_A_GIGAWATT
    assert ceiling["the_declared_network_can_carry_this_fraction_of_the_required_power"] \
        == "1/1000000000000"

    usable = bounds["l2_usable_fraction"]
    assert usable["rule"] == "1 - (theta_earth / theta_sun)^2, exact in the declared units"
    assert usable["theta_earth_at_the_second_lagrange_point"]["value"] == "6371/1500000"
    assert usable["theta_sun_at_the_second_lagrange_point"]["value"] == THETA_SUN_AT_L2
    assert usable["the_ratio"] == THETA_RATIO_AT_L2
    assert usable["the_occulted_fraction"]["value"] == OCCULTED_FRACTION
    assert usable["usable_fraction"]["value"] == USABLE_FRACTION
    assert usable["usable_fraction"]["unit"] == "1"
    assert Fraction(USABLE_FRACTION) + Fraction(OCCULTED_FRACTION) == 1
    assert Fraction(USABLE_FRACTION) == 1 - Fraction(THETA_RATIO_AT_L2) ** 2
    assert usable["the_earth_is_in_the_antumbra"] is True
    assert usable["umbra_length"]["value"] == UMBRA_LENGTH
    assert usable["umbra_length"]["unit"] == "m"
    assert Fraction(UMBRA_LENGTH) < Fraction(declared("second_lagrange_distance"))
    assert usable["the_declared_distance_exceeds_the_umbra_length"] is True
    assert usable["the_sun_appears_annular"] is True
    assert "antumbra" in usable["annular_statement"]
    assert "annular" in usable["annular_statement"]
    assert usable["declared_solar_constant_at_one_au"]["value"] == "1361"
    assert usable["declared_irradiance_at_the_second_lagrange_point"]["value"] == IRRADIANCE_AT_L2
    assert usable["declared_irradiance_at_the_second_lagrange_point"]["unit"] == "W m^-2"
    assert Fraction(IRRADIANCE_AT_L2) < Fraction(declared("solar_constant_at_one_au"))
    assert usable["inverse_square_scaling_is_declared"] is True
    assert usable["usable_flux"]["value"] == USABLE_FLUX
    assert usable["usable_flux"]["unit"] == "W m^-2"
    assert Fraction(USABLE_FLUX) == Fraction(USABLE_FRACTION) * Fraction(IRRADIANCE_AT_L2)
    assert Fraction(1050) < Fraction(USABLE_FLUX) < Fraction(1051)

    bounds_list = bounds["the_three_bounds"]
    assert [row["bound"] for row in bounds_list] == [
        "the passive spot floor theta_sun * L",
        "the étendue-limited single-mode power",
        "the usable fraction at the second Lagrange point",
    ]
    assert [row["value"] for row in bounds_list] == [FLOOR_L2, PER_MODE_POWER, USABLE_FRACTION]
    assert all(row["derived_from"] for row in bounds_list)


def test_the_reported_case_is_consistent_with_the_near_earth_floor():
    cross = section("R1_derived_bounds")["passive_spot_floor"]["cross_check"]
    assert cross["declared_reported_mirror_diameter"]["value"] == "20"
    assert cross["declared_reported_spot"]["value"] == "5000"
    assert "historically reported case" in cross["declared_reported_case"]
    assert cross["measured_here"] is False
    assert cross["read_from_data"] is False
    assert cross["reported_floor_at_the_declared_distance"]["value"] == FLOOR_NEAR_EARTH
    assert cross["reported_floor_with_the_aperture_included"]["value"] \
        == REPORTED_FLOOR_WITH_THE_APERTURE
    assert Fraction(REPORTED_FLOOR_WITH_THE_APERTURE) \
        == Fraction(declared("reported_mirror_diameter")) + Fraction(FLOOR_NEAR_EARTH)
    assert cross["the_reported_spot_is_not_below_the_floor"] is True
    assert Fraction(REPORTED_FLOOR_WITH_THE_APERTURE) < Fraction(5000)
    assert cross["the_reported_spot_over_the_floor"] == REPORTED_SPOT_OVER_THE_FLOOR
    assert Fraction(REPORTED_SPOT_OVER_THE_FLOOR) > 1
    assert cross["implied_distance_for_exactly_the_reported_spot"]["value"] \
        == REPORTED_IMPLIED_DISTANCE
    assert Fraction(REPORTED_IMPLIED_DISTANCE) > Fraction(declared("near_earth_distance"))
    assert cross["the_reported_spot_over_the_declared_distance"]["value"] == "1/80"
    assert cross["the_reported_spot_over_the_declared_distance"]["unit"] == "rad"
    assert Fraction(1, 80) > Fraction(THETA_SUN_AT_ONE_AU)
    assert cross["the_reported_angular_size_exceeds_the_declared_solar_angular_size"] is True
    assert cross["consistent"] is True
    assert cross["verdict"] == "Consistent_FloorIsNotViolated"
    assert "not read as data" in cross["reading"]


def test_the_division_of_labour_is_forced_by_the_fibre_ceiling():
    division = section("R2_division_of_labour")
    assert division["the_division_is_forced_not_stylistic"] is True
    assert division["the_fibre_bound_is_the_reason"] is True
    assert division["no_power_is_routed_through_fibres"] is True
    assert "not a stylistic choice" in division["statement"]
    assert "FORCED rather than chosen" in division["why"]

    mirrors = division["mirrors"]
    assert mirrors["carries_power"] is True
    assert mirrors["role"] == "carry power"
    assert mirrors["combination_happens_in_free_space"] is True
    assert mirrors["required_power"]["value"] == REQUIRED_POWER
    assert mirrors["declared_element_side"]["value"] == "20"
    assert mirrors["how_many_mirror_elements"]["value"] == MIRROR_ELEMENTS
    assert mirrors["how_many_mirror_elements"]["between_the_exact_integers"] == ["2380282",
                                                                                "2380283"]
    assert Fraction(MIRROR_ELEMENTS) * 400 == Fraction(REQUIRED_AREA)

    fibres = division["fibres"]
    assert fibres["carries_power"] is False
    assert "phase" in fibres["role"] and "coherence" in fibres["role"]
    assert fibres["declared_fibre_count"]["value"] == "1000000"
    assert fibres["maximum_power_the_declared_network_can_carry"]["value"] \
        == DECLARED_NETWORK_MAXIMUM_POWER
    assert fibres["required_power"]["value"] == REQUIRED_POWER
    assert fibres["the_fraction_of_the_required_power_the_network_can_carry"] \
        == "1/1000000000000"
    assert "one microwatt" in fibres["what_forces_the_division"]
    assert "not a stylistic alternative" in fibres["what_forces_the_division"]

    stage = division["diffractive_stage"]
    assert stage["element"] == "a zero-order-suppressed phase grating"
    assert stage["orders"] == ["+1", "-1", "0"]
    assert stage["zero_order_share"]["value"] == "0"
    assert stage["plus_first_order_share"]["value"] == "3/5"
    assert stage["minus_first_order_share"]["value"] == "2/5"
    assert stage["order_share_sum"]["value"] == "1"
    assert Fraction(stage["plus_first_order_share"]["value"]) \
        + Fraction(stage["minus_first_order_share"]["value"]) == 1
    assert stage["order_share_difference"]["value"] == "1/5"
    assert stage["the_two_first_order_shares_are_unequal"] is True
    assert stage["two_sided_by_construction"] is True
    assert stage["the_asymmetry_is_a_declared_asymmetry"] is True
    assert "blaze direction" in stage["blaze_direction"]
    assert "blaze asymmetry" in stage["role"]


def test_the_two_deployment_modes_carry_their_own_floor_and_sustainment():
    modes = section("R3_deployment_modes")
    assert modes["mode_count"] == 2
    assert modes["the_two_modes_are_declared_separately"] is True
    assert modes["each_mode_has_its_own_geometric_floor"] is True
    assert modes["each_mode_has_its_own_sustainment_statement"] is True
    assert modes["the_two_modes_are_not_netted"] is True
    assert modes["no_fourth_platform_is_declared"] is True
    assert modes["the_modes_are_a_declared_choice"] is True
    assert modes["floor_ratio_of_the_largest_to_the_smallest"] == FLOOR_RATIO_L2_OVER_NEAR_EARTH
    assert "no fused figure" in modes["separate_accounts_statement"]
    assert modes["mode_B_usable_fraction_is_declared_not_derived"] is True
    assert "DECLARED fraction of this proposal and not a derived bound" \
        in modes["mode_B_usable_fraction_note"]
    assert sorted(modes) == sorted(FROZEN_SECTION_SHAPE["R3_deployment_modes"])

    mode_a = modes["mode_A_second_lagrange_point"]
    assert sorted(mode_a) == [
        "areal_mass", "declared", "geometric_floor", "launch_years", "required_intercepting_area",
        "sustainment", "usable_flux", "usable_fraction"]
    assert "night side" in mode_a["declared"]
    assert mode_a["geometric_floor"]["value"] == FLOOR_L2
    assert mode_a["geometric_floor"]["between_the_exact_integers"] == ["13812901", "13812902"]
    assert mode_a["usable_fraction"]["value"] == USABLE_FRACTION
    assert mode_a["usable_flux"]["value"] == USABLE_FLUX
    assert mode_a["required_intercepting_area"]["value"] == REQUIRED_AREA
    assert mode_a["required_intercepting_area"]["between_the_exact_integers"] == ["952113085",
                                                                                  "952113086"]
    assert mode_a["areal_mass"]["value"] == AREAL_MASS
    assert mode_a["areal_mass"]["between_the_exact_integers"] == ["95211308", "95211309"]
    assert mode_a["launch_years"]["value"] == LAUNCH_YEARS
    assert mode_a["launch_years"]["between_the_exact_integers"] == ["952", "953"]
    assert mode_a["sustainment"]["statement"] == "station-keeping is required"
    assert mode_a["sustainment"]["required"] is True
    assert mode_a["sustainment"]["feasibility_assessed"] is False
    assert mode_a["sustainment"]["cost_assessed"] is False
    assert mode_a["sustainment"]["cadence_declared"] is False
    assert "station-keeping" in mode_a["sustainment"]["reading"]

    mode_b = modes["mode_B_near_earth_relay"]
    assert "relay chain" in mode_b["declared"]
    assert mode_b["geometric_floor"]["value"] == FLOOR_NEAR_EARTH
    assert mode_b["geometric_floor"]["between_the_exact_integers"] == ["3720", "3721"]
    assert mode_b["usable_fraction"]["value"] == "1"
    assert mode_b["usable_flux"]["value"] == "1361"
    assert mode_b["required_intercepting_area"]["value"] == MODE_B_AREA
    assert Fraction(MODE_B_AREA) == Fraction(REQUIRED_POWER) / 1361
    assert mode_b["required_intercepting_area"]["between_the_exact_integers"] == ["734753857",
                                                                                  "734753858"]
    assert mode_b["areal_mass"]["value"] == MODE_B_MASS
    assert Fraction(MODE_B_MASS) == Fraction(MODE_B_AREA) / 10
    assert mode_b["areal_mass"]["between_the_exact_integers"] == ["73475385", "73475386"]
    assert mode_b["launch_years"]["value"] == MODE_B_YEARS
    assert Fraction(MODE_B_YEARS) == Fraction(MODE_B_MASS) / 100000
    assert mode_b["launch_years"]["between_the_exact_integers"] == ["734", "735"]
    assert "succession of platforms rather than one" in mode_b["sustainment"]["statement"]
    assert mode_b["sustainment"]["required"] is True
    assert mode_b["sustainment"]["cadence_declared"] is False
    assert "NOT declared" in mode_b["sustainment"]["reading"]

    assert Fraction(mode_a["geometric_floor"]["value"]) \
        > Fraction(mode_b["geometric_floor"]["value"])
    assert Fraction(mode_a["areal_mass"]["value"]) != Fraction(mode_b["areal_mass"]["value"])
    assert Fraction(mode_a["required_intercepting_area"]["value"]) \
        > Fraction(mode_b["required_intercepting_area"]["value"])


def test_the_declared_target_arithmetic_is_exact_and_asserts_no_effect():
    target = section("R4_declared_target_arithmetic")
    declared_target = target["declared_target"]
    assert declared_target["patch_area"]["value"] == "100000000"
    assert declared_target["patch_area"]["unit"] == "m^2"
    assert declared_target["flux"]["value"] == "10000"
    assert declared_target["flux"]["unit"] == "W m^-2"
    assert declared_target["declared_as_proposal_inputs"] is True
    assert target["required_power"]["value"] == REQUIRED_POWER
    assert target["required_power"]["unit"] == "W"
    assert Fraction(REQUIRED_POWER) == Fraction(100000000) * Fraction(10000)
    assert target["required_intercepting_area"]["value"] == REQUIRED_AREA
    assert target["required_intercepting_area"]["unit"] == "m^2"
    assert Fraction(REQUIRED_AREA) == Fraction(REQUIRED_POWER) / Fraction(USABLE_FLUX)
    assert target["required_intercepting_area"]["between_the_exact_integers"] == ["952113085",
                                                                                  "952113086"]
    assert target["required_intercepting_area"]["ratio_to_the_declared_patch_area"] \
        == AREA_OVER_PATCH
    assert Fraction(AREA_OVER_PATCH) == Fraction(10000) / Fraction(USABLE_FLUX)
    assert target["areal_mass"]["value"] == AREAL_MASS
    assert target["areal_mass"]["unit"] == "kg"
    assert Fraction(AREAL_MASS) == Fraction(REQUIRED_AREA) * Fraction(1, 10)
    assert target["areal_mass"]["between_the_exact_integers"] == ["95211308", "95211309"]
    assert target["launch_years"]["value"] == LAUNCH_YEARS
    assert target["launch_years"]["unit"] == "years"
    assert Fraction(LAUNCH_YEARS) == Fraction(AREAL_MASS) / 100000
    assert target["launch_years"]["between_the_exact_integers"] == ["952", "953"]
    assert target["mirror_elements"]["value"] == MIRROR_ELEMENTS
    assert target["mirror_elements"]["between_the_exact_integers"] == ["2380282", "2380283"]
    assert target["fibres_the_required_power_would_need"]["value"] \
        == FIBRES_FOR_THE_REQUIRED_POWER
    assert target["the_delivery_efficiency_is_declared_exactly_one"] is True
    assert target["the_arithmetic_is_ideal_and_is_a_lower_bound"] is True
    assert target["arithmetic_on_declared_proposal_inputs"] is True
    assert target["no_effect_is_asserted"] is True
    assert "ARITHMETIC ON DECLARED PROPOSAL INPUTS" in target["statement"]
    assert "no effect" in target["statement"]
    for key in ("required_power", "required_intercepting_area", "areal_mass", "launch_years",
                "mirror_elements", "fibres_the_required_power_would_need"):
        assert target[key]["derivation"]
        assert target[key]["between_the_exact_integers"]


def test_all_six_overreach_controls_are_rejected_and_the_failed_one_is_retained():
    controls = section("R5_overreach_controls")
    assert controls["control_count"] == 6
    assert controls["controls_executed"] == 6
    assert controls["controls_rejected"] == 6
    assert controls["every_control_produces_a_rejection"] is True
    assert controls["no_control_is_dropped"] is True
    assert len(controls["controls"]) == 6
    rows = controls["controls"]
    assert all(row["verdict"] == "Rejected" for row in rows)
    assert all(row["rejected"] is True for row in rows)
    assert all(row["discriminates"] is True for row in rows)
    assert all(sorted(row) == sorted(CONTROL_ROW_KEYS) for row in rows)
    assert all(row["rejection_reasons"] for row in rows)
    assert all(row["rejected_by"] for row in rows)
    assert all(row["accepted_companion"]["accepted"] is True for row in rows)
    assert all(sorted(row["accepted_companion"]) == ["accepted", "claim", "verdict"]
               for row in rows)

    finer, ceiling, coherent, usable, asymmetric, loosened = rows
    assert Fraction(finer["derived_value"]["value"]) == Fraction(FLOOR_L2)
    assert Fraction(finer["claimed_value"]["value"]) == 100
    assert Fraction(finer["claimed_value"]["value"]) < Fraction(finer["derived_value"]["value"])
    assert finer["unit"] == "m"
    assert finer["accepted_companion"]["verdict"] == "Accepted_AtTheFloor"

    assert Fraction(ceiling["derived_value"]["value"]) == Fraction(PER_MODE_POWER)
    assert Fraction(ceiling["claimed_value"]["value"]) == 2 * Fraction(PER_MODE_POWER)
    assert ceiling["unit"] == "W"
    assert "fibres as the power channel" in ceiling["rejection_reasons"][1]
    assert ceiling["accepted_companion"]["verdict"] == "Accepted_AtTheCeiling"

    assert Fraction(coherent["derived_value"]["value"]) == 10 ** 9
    assert Fraction(coherent["claimed_value"]["value"]) == Fraction(REQUIRED_POWER)
    assert Fraction(coherent["derived_value"]["value"]) \
        == Fraction(REQUIRED_POWER) * Fraction(1, 1000)
    assert coherent["accepted_companion"]["verdict"] == "Accepted_AtTheDeclaredCoherentFraction"

    assert Fraction(usable["derived_value"]["value"]) == Fraction(USABLE_FRACTION)
    assert Fraction(usable["claimed_value"]["value"]) == 1
    assert Fraction(usable["derived_value"]["value"]) < 1
    assert "strict and not a tolerance" in usable["rejection_reasons"][1]
    assert usable["accepted_companion"]["verdict"] == "Accepted_AtTheDerivedFraction"

    assert Fraction(asymmetric["derived_value"]["value"]) == Fraction(1, 5)
    assert Fraction(asymmetric["claimed_value"]["value"]) == 0
    assert "declared blaze direction" in asymmetric["rejected_by"]
    assert asymmetric["accepted_companion"]["verdict"] == "Accepted_WithTheDeclaredBlazeDirection"

    assert Fraction(loosened["derived_value"]["value"]) == Fraction(REQUIRED_AREA)
    assert loosened["claimed_value"]["value"] == LOOSENED_AREA
    assert Fraction(LOOSENED_AREA) == Fraction(REQUIRED_AREA) * Fraction(USABLE_FRACTION)
    assert Fraction(LOOSENED_AREA) < Fraction(REQUIRED_AREA)
    assert "loosening the derivation" in loosened["rejection_reasons"][0]
    assert loosened["accepted_companion"]["verdict"] == "Accepted_ByDeclaration"

    failed = controls["failed_controls"]
    assert controls["failed_controls_count"] == 1
    assert len(failed) == 1
    assert failed[0]["outcome"] == "FAILED_TO_DISCRIMINATE"
    assert failed[0]["discriminates"] is False
    assert failed[0]["derived_mass"] == AREAL_MASS
    assert failed[0]["derived_launch_years"] == LAUNCH_YEARS
    assert Fraction(failed[0]["relaxed_mass"]) * 10 == Fraction(failed[0]["derived_mass"])
    assert Fraction(failed[0]["relaxed_launch_years"]) * 10 \
        == Fraction(failed[0]["derived_launch_years"])
    assert Fraction(failed[0]["relaxed_mass"]) < Fraction(failed[0]["derived_mass"])
    assert "1/100" in failed[0]["control"]
    assert "cannot distinguish" in failed[0]["variant"]
    assert "FAILED TO DISCRIMINATE" in failed[0]["why"]
    assert "retained rather than repaired" in failed[0]["why"]
    assert controls["failed_controls_count"] == 1
    assert "failed control" in controls["why_the_failed_control_is_retained"]


def test_the_inherited_prohibitions_apply_and_the_termination_is_unaddressed():
    inherited = section("R6_inherited_prohibitions")
    assert inherited["inherited_prohibitions_count"] == 2
    assert inherited["inherited_prohibitions_apply_to_any_use"] is True
    assert inherited["no_netting"] is True
    assert inherited["sealing_refused_for_the_termination"] is True
    assert inherited["parent_contracts_cited"] == [
        "experiments/three_cycle_supplement_v1/contract.json",
        "experiments/three_cycle_supplement_v2/contract.json",
    ]
    netting, sealing = inherited["inherited_prohibitions"]
    for row in (netting, sealing):
        assert sorted(row) == [
            "applies_to_any_use", "control", "prohibition", "rejected", "rejected_by",
            "rejection_reasons", "source", "verdict"]
        assert row["rejected"] is True
        assert row["verdict"] == "Rejected"
        assert row["applies_to_any_use"] is True
        assert row["rejection_reasons"]
        assert "parent contracts" in row["source"]
    assert netting["prohibition"] == "no netting of one account against another"
    assert "may not be reduced by, or merged with, another" in netting["rejection_reasons"][1]
    assert AREAL_MASS in netting["rejection_reasons"][0]
    assert MODE_B_MASS in netting["rejection_reasons"][0]
    assert "no fused area, mass or launch-years figure" in netting["rejection_reasons"][2]
    assert sealing["prohibition"] == "no sealing of a component that is by definition a leak"
    assert "by definition a leak" in sealing["rejection_reasons"][0]
    assert "NOT solved here" in sealing["rejection_reasons"][2]

    termination = inherited["termination_problem"]
    assert sorted(termination) == [
        "declared_as", "governance", "may_be_accounted_but_never_sealed",
        "no_attempt_is_made_to_solve_it", "status", "the_component_is_by_definition_a_leak", "why"]
    assert termination["status"] == "Unaddressed"
    assert termination["governance"] == UNASSESSED
    assert termination["the_component_is_by_definition_a_leak"] is True
    assert termination["may_be_accounted_but_never_sealed"] is True
    assert termination["no_attempt_is_made_to_solve_it"] is True
    assert "does not attempt to solve the termination problem" in termination["why"]
    assert "who might decide" in termination["why"]


def test_the_payload_records_proposal_only_bookkeeping():
    bookkeeping = section("R7_proposal_only_bookkeeping")
    contract = load(CONTRACT)["proposal_only_bookkeeping"]
    assert bookkeeping["authorization"] == NO_NONE
    assert bookkeeping["decision"] == NO_NONE
    assert bookkeeping["deployment"] == NO_NONE
    assert bookkeeping["governance"] == UNASSESSED
    assert bookkeeping["physical_effect_asserted"] == NO_NONE
    assert bookkeeping["data_used"] == NO_DATA
    assert bookkeeping["record_purpose"] == contract["record_purpose"]
    assert contract["authorization"] == NO_NONE
    assert contract["decision"] == NO_NONE
    assert contract["deployment"] == NO_NONE
    assert contract["governance"] == UNASSESSED
    assert contract["physical_effect_asserted"] == NO_NONE
    assert contract["data_used"] == NO_DATA
    assert bookkeeping["status"] == PROPOSAL_STATUS
    assert load(CONTRACT)["status"] == PROPOSAL_STATUS
    assert "PROPOSAL ONLY" in bookkeeping["proposal_only_statement"]
    assert "authorizes nothing" in bookkeeping["proposal_only_statement"]
    assert bookkeeping["proposal_only_in_chinese_and_english"] == "提议性方案 / proposal only"
    assert bookkeeping["authorizes_nothing"] is True
    assert bookkeeping["decides_nothing"] is True
    assert bookkeeping["deploys_nothing"] is True
    assert bookkeeping["no_governance_assessment"] is True
    assert "who might decide" in bookkeeping["nothing_said_about_who_might_decide"]

    report = load(EVIDENCE)
    claimed = report["what_is_not_claimed"]
    assert claimed["authorization"] == NO_NONE
    assert claimed["decision"] == NO_NONE
    assert claimed["deployment"] == NO_NONE
    assert claimed["governance"] == UNASSESSED
    assert claimed["physical_effect_asserted"] == NO_NONE
    assert claimed["data_used"] == NO_DATA
    assert claimed["physical_claim"] is False
    assert claimed["forecast"] is False
    assert claimed["capability_claim"] is False
    assert claimed["effect_on_any_atmosphere_ocean_cloud_or_surface"] is False
    assert claimed["weather_or_climate_effect"] is False
    assert claimed["meteorological_data_used"] is False
    assert claimed["no_data_read_or_used"] is True
    assert claimed["the_document_is_a_proposal_only"] is True
    assert claimed["the_three_bounds_are_derived_from_declared_constants"] is True
    assert claimed["the_declared_constants_are_declared_inputs_not_measurements"] is True
    assert claimed["the_target_figures_are_proposal_arithmetic"] is True
    assert claimed["the_division_of_labour_is_forced_by_the_fibre_bound"] is True
    assert claimed["no_netting_of_one_account_against_another"] is True
    assert claimed["no_sealing_of_a_component_that_is_by_definition_a_leak"] is True
    assert claimed["the_termination_problem_is_unaddressed"] is True
    assert claimed["native_certificate"] is False
    assert claimed["native_admission"] == "NotGranted"
    assert claimed["stable_api_change"] is False
    assert claimed["no_seal_no_transport_no_terminology_home"] is True
    assert claimed["no_rust_source_or_lock_changed"] is True
    assert claimed["no_contract_or_note_edited"] is True
    assert claimed["no_claim_added_to_docs_claims_toml"] is True
    assert claimed["observational_verification"] == "Unavailable"

    status = report["verification_status"]
    assert status["observational"] == "Unavailable"
    assert status["no_data_read_or_used"] is True
    assert status["physical_effect_asserted"] == NO_NONE
    assert status["deployment"] == NO_NONE
    assert status["checked_here"]["no_data_read_or_used"] is True
    assert status["checked_here"]["no_physical_effect_is_asserted"] is True
    assert status["checked_here"]["the_derived_bounds_are_bounds_on_instruments"] is True
    assert status["checked_here"]["the_target_figures_are_proposal_arithmetic"] is True
    assert status["checked_here"]["governance_is_unaddressed"] is True


def test_the_payload_is_free_of_floating_point_literals_host_paths_and_timestamps():
    text = EVIDENCE.read_text(encoding="utf-8")
    assert load(EVIDENCE)
    assert "NaN" not in text and "Infinity" not in text
    assert "/Users/" not in text and "mingli" not in text
    report = load(EVIDENCE)
    assert report["checks"]["no_floating_point_value_is_retained"] is True
    assert report["checks"]["no_effect_key_appears_anywhere"] is True
    assert key_findings(report, FORBIDDEN_EFFECT_KEYS) == []
    assert key_findings(report, FORBIDDEN_TIME_KEYS) == []
    assert "T00:00" not in text and "elapsed" not in text


def test_the_frozen_shape_of_every_section():
    report = load(EVIDENCE)
    assert sorted(report) == sorted(TOP_LEVEL_KEYS)
    assert sorted(report["sections"]) == sorted(SECTION_NAMES)
    for name, keys in FROZEN_SECTION_SHAPE.items():
        assert sorted(report["sections"][name]) == sorted(keys), name

    bounds = section("R1_derived_bounds")
    assert sorted(bounds["declared_constants"][0]) == [
        "declared", "measured_here", "name", "read_from_data", "role", "unit", "value"]
    floor = bounds["passive_spot_floor"]
    assert sorted(floor["platforms"][0]) == ["declared_distance", "floor", "name", "theta_sun"]
    assert sorted(floor["cross_check"]) == [
        "consistent", "declared_reported_case", "declared_reported_mirror_diameter",
        "declared_reported_spot", "implied_distance_for_exactly_the_reported_spot",
        "measured_here", "read_from_data", "reading",
        "reported_floor_at_the_declared_distance",
        "reported_floor_with_the_aperture_included",
        "the_reported_angular_size_exceeds_the_declared_solar_angular_size",
        "the_reported_spot_is_not_below_the_floor", "the_reported_spot_over_the_declared_distance",
        "the_reported_spot_over_the_floor", "verdict"]
    assert sorted(bounds["fibre_power_ceiling"]) == [
        "declared_fibre_count", "declared_spectral_radiance", "declared_wavelength",
        "fibres_a_gigawatt_would_need", "fibres_a_megawatt_would_need",
        "fibres_the_coherent_part_would_need", "fibres_the_required_power_would_need",
        "gigawatt_reference_power", "maximum_power_the_declared_fibre_network_can_carry",
        "per_mode_power", "per_mode_power_is_microwatts", "reading", "rule",
        "the_contracts_reported_order", "the_declared_network_can_carry_this_fraction_of_the_"
        "required_power", "the_exact_count_and_the_reported_order",
        "the_megawatt_is_this_fraction_of_the_declared_gigawatt"]
    assert sorted(bounds["l2_usable_fraction"]) == [
        "annular_statement", "declared_irradiance_at_the_second_lagrange_point",
        "declared_solar_constant_at_one_au", "inverse_square_scaling_is_declared", "reading",
        "rule", "the_declared_distance_exceeds_the_umbra_length", "the_earth_is_in_the_antumbra",
        "the_occulted_fraction", "the_ratio", "the_sun_appears_annular",
        "theta_earth_at_the_second_lagrange_point",
        "theta_sun_at_the_second_lagrange_point", "umbra_length", "usable_flux",
        "usable_fraction"]
    assert sorted(bounds["the_three_bounds"][0]) == ["bound", "derived_from", "unit", "value"]

    division = section("R2_division_of_labour")
    assert sorted(division["mirrors"]) == [
        "carries_power", "combination_happens_in_free_space", "declared_element_side",
        "how_many_mirror_elements", "reading", "required_power", "role"]
    assert sorted(division["fibres"]) == [
        "carries_power", "declared_fibre_count", "maximum_power_the_declared_network_can_carry",
        "required_power", "role", "the_fraction_of_the_required_power_the_network_can_carry",
        "what_forces_the_division"]
    assert sorted(division["diffractive_stage"]) == [
        "blaze_direction", "element", "minus_first_order_share", "order_share_difference",
        "order_share_sum", "orders", "plus_first_order_share", "reading", "role",
        "the_asymmetry_is_a_declared_asymmetry", "the_two_first_order_shares_are_unequal",
        "two_sided_by_construction", "zero_order_share"]

    modes = section("R3_deployment_modes")
    for name in ("mode_A_second_lagrange_point", "mode_B_near_earth_relay"):
        assert sorted(modes[name]) == [
            "areal_mass", "declared", "geometric_floor", "launch_years",
            "required_intercepting_area", "sustainment", "usable_flux", "usable_fraction"], name
        assert sorted(modes[name]["sustainment"]) == [
            "cadence_declared", "cost_assessed", "feasibility_assessed", "reading", "required",
            "statement"], name

    target = section("R4_declared_target_arithmetic")
    assert sorted(target["declared_target"]) == [
        "declared_as_proposal_inputs", "flux", "patch_area", "reading"]
    for key in ("required_power", "areal_mass", "launch_years", "mirror_elements",
                "fibres_the_required_power_would_need"):
        assert sorted(target[key]) == [
            "between_the_exact_integers", "derivation", "unit", "value"], key
    assert sorted(target["required_intercepting_area"]) == [
        "between_the_exact_integers", "derivation", "ratio_to_the_declared_patch_area", "unit",
        "value"]

    controls = section("R5_overreach_controls")
    assert sorted(controls["controls"][0]) == sorted(CONTROL_ROW_KEYS)
    assert sorted(controls["failed_controls"][0]) == [
        "control", "derived_launch_years", "derived_mass", "discriminates", "outcome", "reading",
        "relaxed_launch_years", "relaxed_mass", "variant", "why"]

    inherited = section("R6_inherited_prohibitions")
    assert sorted(inherited["inherited_prohibitions"][0]) == [
        "applies_to_any_use", "control", "prohibition", "rejected", "rejected_by",
        "rejection_reasons", "source", "verdict"]
    assert sorted(inherited["termination_problem"]) == [
        "declared_as", "governance", "may_be_accounted_but_never_sealed",
        "no_attempt_is_made_to_solve_it", "status", "the_component_is_by_definition_a_leak",
        "why"]


def test_the_undecided_items_and_modelling_choices_are_declared():
    report = load(EVIDENCE)
    undecided = report["undecided"]
    assert len(undecided) == 6
    assert report["checks"]["undecided_items_are_declared"] is True
    items = [row["item"] for row in undecided]
    assert any("theta_sun" in item for item in items)
    assert any("spectral radiance" in item for item in items)
    assert any("5 km" in item for item in items)
    assert any("fibre count" in item for item in items)
    assert any("relay chain" in item for item in items)
    assert any("parent contracts" in item for item in items)
    for row in undecided:
        assert sorted(row) == ["item", "reason", "retained_partial_result"]
        assert row["reason"]
        assert row["retained_partial_result"] is not None
    theta = next(row for row in undecided if "theta_sun" in row["item"])
    assert theta["retained_partial_result"]["near_earth_floor"] == FLOOR_NEAR_EARTH
    assert theta["retained_partial_result"]["theta_sun_at_one_au"] == THETA_SUN_AT_ONE_AU
    assert "factor of two" in theta["reason"]
    fibre = next(row for row in undecided if "fibre count" in row["item"])
    assert fibre["retained_partial_result"]["fibres_the_coherent_part_would_need"] \
        == FIBRES_FOR_A_GIGAWATT
    assert fibre["retained_partial_result"]["declared_fibre_count"] == "1000000"
    assert "NOT decided here" in fibre["reason"]
    relay = next(row for row in undecided if "relay chain" in row["item"])
    assert "succession of platforms" in relay["retained_partial_result"]["mode_B_sustainment"]
    assert "NOT declared in the contract" in relay["reason"]
    parents = next(row for row in undecided if "parent contracts" in row["item"])
    assert parents["retained_partial_result"]["surgery_sha256"] == DECLARED_SURGERY_SHA256
    assert parents["retained_partial_result"]["rounded_sha256"] == DECLARED_ROUNDED_SHA256

    choices = report["modelling_choices"]
    assert len(choices) == 17
    for key in ("theta_sun_declaration", "declared_distances", "floor_ignores_the_aperture",
                "reported_case_is_declared", "spectral_radiance_declaration", "l2_antumbra_check",
                "inverse_square_scaling", "ideal_delivery_efficiency",
                "fibre_ceiling_forces_the_division", "blaze_as_declared_asymmetry",
                "deployment_modes_separate", "target_arithmetic_is_a_proposal_input",
                "inherited_prohibitions", "proposal_only", "exact_only", "external_library",
                "resource_limits"):
        assert choices[key], key
    assert "FULL angular size" in choices["theta_sun_declaration"]
    assert "Undecided" in choices["theta_sun_declaration"]
    assert "not measured here and not read from data" in choices["reported_case_is_declared"]
    assert "DERIVED and not asserted" in choices["l2_antumbra_check"]
    assert "LOWER bound" in choices["ideal_delivery_efficiency"]
    assert "one microwatt" in choices["fibre_ceiling_forces_the_division"]
    assert "zero-order-suppressed" in choices["blaze_as_declared_asymmetry"]
    assert "not netted" in choices["deployment_modes_separate"]
    assert "ARITHMETIC INPUTS" in choices["target_arithmetic_is_a_proposal_input"]
    assert "Unaddressed" in choices["inherited_prohibitions"]
    assert "提议性方案" in choices["proposal_only"]
    assert "no floating-point value" in choices["exact_only"]
    assert "not depend on a host package" in choices["external_library"]
    assert "rlimit" in choices["resource_limits"]
    assert load(EVIDENCE)["checks"]["the_proposal_only_bookkeeping_matches_the_contract"] is True


def test_the_declared_checks_all_pass_and_name_their_conditions():
    checks = load(EVIDENCE)["checks"]
    assert all(checks.values())
    for name in ("assertions_within_budget",
                 "this_contract_digest_matches_the_declared_one",
                 "all_parent_contracts_are_retained_byte_for_byte",
                 "the_contract_declares_itself_a_proposal_only",
                 "the_proposal_only_bookkeeping_matches_the_contract",
                 "every_declared_constant_is_declared_and_not_measured",
                 "the_three_bounds_are_derived_from_the_declared_constants",
                 "the_passive_spot_floor_is_reported_for_three_platforms",
                 "the_l2_floor_exceeds_the_earths_diameter",
                 "the_near_earth_floor_is_consistent_with_the_reported_case",
                 "the_fibre_ceiling_is_microwatts_per_mode",
                 "a_gigawatt_would_need_ten_to_the_fifteen_fibres",
                 "a_megawatt_would_need_ten_to_the_twelve_fibres",
                 "the_declared_fibre_network_cannot_carry_the_required_power",
                 "the_l2_usable_fraction_is_the_derived_annular_fraction",
                 "the_earth_is_in_the_antumbra_at_the_second_lagrange_point",
                 "the_sun_appears_annular_there",
                 "the_division_of_labour_is_forced_by_the_fibre_bound",
                 "the_fibres_do_not_carry_power", "no_power_is_routed_through_fibres",
                 "the_diffractive_stage_carries_the_declared_blaze_asymmetry",
                 "the_two_deployment_modes_are_declared_separately",
                 "mode_B_usable_fraction_is_recorded_as_declared",
                 "each_mode_has_its_own_geometric_floor",
                 "each_mode_has_its_own_sustainment_statement", "the_two_modes_are_not_netted",
                 "the_declared_target_arithmetic_follows_exactly",
                 "the_target_arithmetic_is_ideal_and_is_a_lower_bound",
                 "no_effect_is_asserted_by_the_target_arithmetic",
                 "all_six_overreach_controls_are_rejected",
                 "every_overreach_control_discriminates", "the_failed_control_is_retained",
                 "no_control_is_dropped", "no_netting_is_performed",
                 "sealing_is_refused_for_the_termination",
                 "the_termination_problem_is_recorded_unaddressed",
                 "the_inherited_prohibitions_apply_to_any_use",
                 "the_termination_may_be_accounted_but_never_sealed",
                 "the_payload_records_proposal_only_bookkeeping",
                 "governance_is_unaddressed_and_no_decision_is_claimed",
                 "observational_verification_is_recorded_unavailable",
                 "no_data_is_read_or_used", "undecided_items_are_declared",
                 "no_floating_point_value_is_retained", "no_effect_key_appears_anywhere"):
        assert checks[name] is True, name


def test_a_copied_checkout_reproduces_the_retained_payload(tmp_path):
    """The checker is re-run on a COPY: the payload must not depend on its location."""
    copied = tmp_path / "experiments"
    (copied / "optical_imbalance_proposal_v1").mkdir(parents=True)
    (copied / "three_cycle_supplement_v1").mkdir()
    (copied / "three_cycle_supplement_v2").mkdir()
    shutil.copy(CHECKER, copied / "optical_imbalance_proposal_v1/calibration.py")
    shutil.copy(CONTRACT, copied / "optical_imbalance_proposal_v1/contract.json")
    shutil.copy(SURGERY_CONTRACT, copied / "three_cycle_supplement_v1/contract.json")
    shutil.copy(ROUNDED_CONTRACT, copied / "three_cycle_supplement_v2/contract.json")
    output = tmp_path / "on-a-copy.json"
    completed = invoke(copied / "optical_imbalance_proposal_v1/calibration.py", output)
    assert completed.returncode == 0, completed.stderr
    fresh = load(output)
    retained = load(EVIDENCE)
    assert fresh["status"] == retained["status"]
    assert fresh["assertions"] == retained["assertions"]
    assert fresh["sections"] == retained["sections"]
    assert fresh["checks"] == retained["checks"]
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
    added it, together with the erratum of note 0240; the assertion is inverted rather than dropped,
    so the binding stays checked.
    """
    claims = tomllib.loads((ROOT / "docs/claims.toml").read_text(encoding="utf-8"))["claim"]
    assert claims
    matches = [row for row in claims if row.get("claim_id") == CLAIM_ID]
    assert len(matches) == 1, "exactly one claim must be registered for this run"
    claim = matches[0]
    assert claim["status"] == "bounded-experiment"
    for symbol in ("optical_imbalance_proposal_v1/calibration.py",
                   "optical_imbalance_proposal_v1/contract.json",
                   "optical_imbalance_proposal_v1/evidence.json",
                   "0240-a-proposal-only-optical-scheme"):
        assert symbol in claim["code_symbol"], symbol
    assert "erratum" in claim["counterexample_boundary"].lower(), \
        "the boundary must carry the registered erratum"
    assert "NotGranted" in claim["counterexample_boundary"], "the boundary must record native admission"
    assert claim["forbidden_conflations"], "the claim must name its conflations"

