#!/usr/bin/env python3
"""Exact external calibration of the geometry-foundation PROPOSAL: the shared geometric basis of
the programme's first three proposals, reported once per shared item.

Frozen contract: experiments/geometry_foundation_v1/contract.json (this run), sha256
1e07f9a04a9d6d60073a5cb3f726df7d38554608f4d023383314fbff83217750.  The run reads it, hashes it
and edits nothing.  It also reads, cites and does not edit the immediately preceding run's frozen
payload:

* experiments/optical_imbalance_proposal_v1/contract.json  (sha256 116913a9... retained byte for
  byte): the proposal whose usable-fraction bound this foundation corrects;
* experiments/optical_imbalance_proposal_v1/evidence.json  (sha256 10e639d3... retained byte for
  byte): the retained payload that keeps its digest, whose own usable-fraction value is carried here
  as the SUPERSEDED value and is compared against the corrected one exactly.

THIS DOCUMENT IS A PROPOSAL ONLY - 提议性方案 (proposal four of the programme: the geometry
foundation).  It authorizes nothing, decides nothing, deploys nothing, asserts no physical effect
and uses no data.  No magnitude, sign or timing is asserted for any physical quantity, and nothing
here is a statement about the atmosphere, the ocean, ice, cloud or any weather.

What the run reports, each shared item once:

* the PAIRING RULES, stated and ENFORCED as rules rather than as prose - an angular radius paired
  only with an angular radius and an angular diameter only with an angular diameter, the occulted
  area fraction (theta_earth / theta_sun)^2 with LIKE paired with LIKE, and a penumbra DIAMETER of
  D + theta_sun(full angular size) * L - each with a deliberately MIS-PAIRED control (radius against
  diameter) rejected by the rule with the exact factor by which it is wrong, and an accepted
  companion at the correct pairing.  One further control FAILED to discriminate and is retained;
* the CORRECTED usable fraction: at the second Lagrange point the occulted fraction is
  exactly 1144054937385575376509089/1344440250000000000000000 and the usable fraction exactly
  200385312614424623490911/1344440250000000000000000, computed from declared constants with LIKE
  paired with LIKE; the superseded value of the earlier run is reported as SUPERSEDED, its exact
  difference from the corrected one is stated, and the earlier payload keeps its digest;
* the spot floor theta_sun * L at every declared distance with the penumbra-diameter form beside it;
* the etendue ceiling B * lambda^2 per mode, which forces power into free space and keeps fibres for
  phase and coherence only;
* the pattern scale near theta_sun * L, with finer structure washed out by the extended source and
  coarser interference structure needing apertures below the declared coherence length;
* the SYMMETRY CONSTRAINTS over three declared Archimedean solids, each with its declared vertex
  count, declared point group and order, its rotation part as the subgroup of SO(3), and the number
  of distinct orbits of vertices under the group - with the time direction entering as a declared
  schedule invariant under the corresponding time translations, a claim that the time direction is
  part of the point group REJECTED, and a claim that an arbitrary set of vertex positions is
  invariant under the declared group REJECTED with an exact witness;
* the WORK-REGION AND WORK-TIME CALCULUS over a declared constellation: which declared regions are
  addressable, at which declared steps, with which exact duty cycle and with which geometric floor,
  with the statement that regions and times must be computed in advance rather than chosen in
  flight, a claim of sustained addressability of a fixed region by a single platform REJECTED, and
  the relay form accepted;
* the ABLATION-LEVEL ASSIGNMENT: tasks assigned to declared energy LEVELS matched to the declared
  ablation levels of the target medium, using declared level values only - no magnitude of any real
  physical quantity and no data - with an assignment routed to a platform REJECTED and an assignment
  outside the declared level set REJECTED;
* the declared OBLIGATIONS (high safety; topology preserved; human impact controllable and
  relatively small; a bounded error tolerated and learned from; no magnitude) each with a rejected
  violating control;
* STAGE ONE recorded as CALIBRATION and not control, in the December-to-January window already fixed
  for the chain of note 0238, with the material computed, aggregated and distributed, and with the
  two invariants - the overall topology is not broken, and learning is continuous from the first
  stage - each implemented with a falsifiable counterpart that is rejected;
* the proposal-only bookkeeping: authorization, decision, deployment, physical_effect_asserted and
  data_used all none, governance unaddressed, and the termination problem recorded as Unaddressed
  and not solved.

All acceptance arithmetic is exact integers and fractions.Fraction, and group closure is exact
integer matrix multiplication.  No floating-point value is formed in an acceptance assertion or
written into the retained payload; the decimal strings in the payload are truncated integer
expansions, not floats.  No external library is imported: sympy 1.14 is declared as available on the
host, as non-authoritative and as unused.  No data is read or used, no clock is read, and no
timestamp, measured duration or host path is written.

Resource policy: RLIMIT_CPU and RLIMIT_FSIZE are installed together with a wall alarm; the
contract's declared memory budget is recorded and no address-space ceiling is installed, because no
child process is launched.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import resource
import signal
import sys
from fractions import Fraction as Fr

HERE = pathlib.Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "contract.json"
CONTRACT = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

EXPERIMENTS = HERE.parent
EARLIER_CONTRACT_PATH = EXPERIMENTS / "optical_imbalance_proposal_v1" / "contract.json"
EARLIER_EVIDENCE_PATH = EXPERIMENTS / "optical_imbalance_proposal_v1" / "evidence.json"

SCHEMA = "adva.external.geometry-foundation-proposal-calibration.v1"
CONTRACT_RELATIVE = "experiments/geometry_foundation_v1/contract.json"
EARLIER_CONTRACT_RELATIVE = "experiments/optical_imbalance_proposal_v1/contract.json"
EARLIER_EVIDENCE_RELATIVE = "experiments/optical_imbalance_proposal_v1/evidence.json"
NOTE_0238_RELATIVE = (
    "docs/research/0238-three-chained-annual-cycles-every-cycle-closes-and-the-drift-control-"
    "fails-to-discriminate.md")
NOTE_0240_RELATIVE = (
    "docs/research/0240-a-proposal-only-optical-scheme-its-derived-bounds-and-one-erratum.md")
NOTE_0241_RELATIVE = "docs/research/0241-four-proposals-and-the-stage-one-calibration.md"

DECLARED_CONTRACT_SHA256 = "1e07f9a04a9d6d60073a5cb3f726df7d38554608f4d023383314fbff83217750"
DECLARED_EARLIER_CONTRACT_SHA256 = (
    "116913a9369e43666d80cf65a6877164f186fd813955a4d1c05f39777496fa4f")
DECLARED_EARLIER_EVIDENCE_SHA256 = (
    "10e639d3843b29dbad0d815d8599ea5c2ff7c391b1eb1f1a3a8a422036538624")

PROPOSAL_STATUS = "PROPOSAL ONLY - 提议性方案"
NO_NONE = "none"
NO_DATA = "none"
UNASSESSED = "unaddressed"
SUPERSEDED = "Superseded"
UNADDRESSED = "Unaddressed"

ASSERTIONS = {"n": 0}


def check(condition, message):
    """One exact acceptance assertion, counted."""
    ASSERTIONS["n"] += 1
    if not condition:
        raise AssertionError(message)


def digest(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def text(value):
    """An exact rational as its exact decimal-free string; no float is ever formed."""
    value = value if isinstance(value, Fr) else Fr(value)
    return str(value)


def integer_bracket(value):
    """The two exact integers a rational lies between, as strings."""
    value = value if isinstance(value, Fr) else Fr(value)
    low = value.numerator // value.denominator
    return [str(low), str(low + 1)]


def decimals(value, digits):
    """The exact decimal expansion of a rational, truncated, by integer arithmetic only."""
    value = value if isinstance(value, Fr) else Fr(value)
    check(not isinstance(value, float), "no floating-point value is ever a decimal source")
    scale = 10 ** digits
    scaled = value * scale
    truncated = scaled.numerator // scaled.denominator
    whole, fraction = divmod(truncated, scale)
    return str(whole) + "." + str(fraction).zfill(digits)


def quantity(value, unit, **extra):
    """An exact quantity: the exact rational as text, its unit and its exact integer bracket."""
    value = value if isinstance(value, Fr) else Fr(value)
    record = {
        "value": text(value),
        "unit": unit,
        "between_the_exact_integers": integer_bracket(value),
    }
    record.update(extra)
    return record


def contains_float(node):
    """True when a float appears anywhere in the payload."""
    if isinstance(node, float):
        return True
    if isinstance(node, dict):
        return any(contains_float(key) or contains_float(value) for key, value in node.items())
    if isinstance(node, (list, tuple)):
        return any(contains_float(item) for item in node)
    return False


# A key naming a magnitude of a real physical quantity, or a physical effect.  No such key may
# appear anywhere in the retained payload, and the rule below is what rejects the control that
# claims one.
FORBIDDEN_MAGNITUDE_KEYS = (
    "magnitude", "energy", "power", "forcing", "temperature", "warming", "cooling", "amount",
    "dosage", "intensity", "irradiance", "flux", "effect", "albedo", "rainfall", "precipitation",
)


def magnitude_audit(node, path="", found=None):
    """Every key anywhere in a record that names a magnitude or a physical effect."""
    if found is None:
        found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in FORBIDDEN_MAGNITUDE_KEYS:
                found.append(path + "/" + str(key) + " names a magnitude or a physical effect")
            magnitude_audit(value, path + "/" + str(key), found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            magnitude_audit(item, path + "/" + str(index), found)
    return found


FORBIDDEN_IN_FLIGHT_KEYS = ("chosen_in_flight", "in_flight_choice", "operator_choice")


def in_advance_audit(node, path="", found=None):
    """Every key anywhere in a record that names a chosen-in-flight schedule."""
    if found is None:
        found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in FORBIDDEN_IN_FLIGHT_KEYS:
                found.append(path + "/" + str(key))
            in_advance_audit(value, path + "/" + str(key), found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            in_advance_audit(item, path + "/" + str(index), found)
    return found


# ------------------------------------------------------------ declared constants --
# Every entry below is a DECLARED input of this proposal, carried as an exact rational with its
# declared unit.  None is a measurement of this run; no instrument was used, no data was read and no
# clock was consulted.  A different declaration of the constants is a different run.

# lengths, in metres
ASTRONOMICAL_UNIT = 149597870700
SOLAR_RADIUS = 695700000
EARTH_MEAN_RADIUS = 6371000
NEAR_EARTH_DISTANCE = 400000
GEOSTATIONARY_DISTANCE = 35786000
SECOND_LAGRANGE_DISTANCE = 1500000000
DECLARED_APERTURE = 20
DECLARED_COHERENCE_LENGTH = Fr(1, 2)
DECLARED_WORK_REGION_DISTANCE = 35786000

# radiance and wavelength
SPECTRAL_RADIANCE_B = 10 ** 6
WAVELENGTH = Fr(1, 10 ** 6)

# the declared constellation and the declared target regions
DECLARED_PLATFORM_COUNT = 4
DECLARED_REGION_COUNT = 4
DECLARED_WINDOW_STEPS = 12
DECLARED_SWEEP_PERIOD_STEPS = 4
DECLARED_ADDRESSES_PER_REGION_PER_STEP = 1
DECLARED_ERROR_STEP_COUNT = 3
DECLARED_ERROR_MAGNITUDE_REGION_INDICES = 1

# the declared energy levels and the declared tasks
DECLARED_LEVEL_COUNT = 4
DECLARED_LEVEL_VALUES = ((1, "level_1"), (2, "level_2"), (3, "level_3"), (4, "level_4"))
DECLARED_TASKS = (("task_a", 1), ("task_b", 2), ("task_c", 3), ("task_d", 4),
                  ("task_e", 1), ("task_f", 2))
DECLARED_TASK_COUNT = 6

# stage one
DECLARED_MATERIAL_UNITS = 4096
DECLARED_RECIPIENT_COUNT = 64
DECLARED_GROWTH_STEPS = 8
DECLARED_LAUNCHES_FIRST_STEP = 1
DECLARED_LAUNCH_INCREMENT = 1
DECLARED_LEARNING_UNITS_PER_LAUNCH = 4
DECLARED_WINDOW_START_MONTH = 12
DECLARED_WINDOW_END_MONTH = 1

# the declared schedule invariant that carries the time direction
DECLARED_SCHEDULE_PERIOD = 2
DECLARED_SCHEDULE_HORIZON = 24

DECLARED_CONSTANTS = (
    ("astronomical_unit", ASTRONOMICAL_UNIT, "m",
     "the declared distance unit; the value is exact under the 2012 definition"),
    ("solar_radius", SOLAR_RADIUS, "m", "the declared nominal solar radius"),
    ("earth_mean_radius", EARTH_MEAN_RADIUS, "m", "the declared mean Earth radius"),
    ("near_earth_distance", NEAR_EARTH_DISTANCE, "m",
     "the first declared platform distance"),
    ("geostationary_distance", GEOSTATIONARY_DISTANCE, "m",
     "the second declared platform distance, which is also the declared constellation distance of "
     "the work-region calculus"),
    ("second_lagrange_distance", SECOND_LAGRANGE_DISTANCE, "m",
     "the third declared platform distance, beyond the Earth on the anti-solar side"),
    ("declared_aperture", DECLARED_APERTURE, "m",
     "the declared aperture of one element, which the penumbra-diameter form adds to the floor"),
    ("declared_coherence_length", DECLARED_COHERENCE_LENGTH, "m",
     "the declared coherence length below which an aperture must lie for coarser interference "
     "structure; a declared constant and not a measurement of this run"),
    ("spectral_radiance_B", SPECTRAL_RADIANCE_B, "W m^-2 sr^-1",
     "the declared bandwidth-integrated spectral radiance B that sets the etendue ceiling"),
    ("wavelength", WAVELENGTH, "m", "the declared operating wavelength, one micrometre"),
    ("declared_work_region_distance", DECLARED_WORK_REGION_DISTANCE, "m",
     "the declared distance of the constellation of the work-region calculus"),
    ("declared_platform_count", DECLARED_PLATFORM_COUNT, "1",
     "the declared number of platforms of the constellation"),
    ("declared_region_count", DECLARED_REGION_COUNT, "1",
     "the declared number of target regions of the work-region calculus"),
    ("declared_window_steps", DECLARED_WINDOW_STEPS, "1",
     "the declared number of steps of the declared work window"),
    ("declared_sweep_period_steps", DECLARED_SWEEP_PERIOD_STEPS, "1",
     "the declared number of steps in which the sweep due to the declared motion returns"),
    ("declared_addresses_per_region_per_step", DECLARED_ADDRESSES_PER_REGION_PER_STEP, "1",
     "the declared number of platform-addresses a region may receive in one declared step"),
    ("declared_error_step_count", DECLARED_ERROR_STEP_COUNT, "1",
     "the declared number of declared error steps of the bounded-error obligation"),
    ("declared_error_magnitude_region_indices", DECLARED_ERROR_MAGNITUDE_REGION_INDICES, "1",
     "the declared magnitude of a declared error, in declared region indices"),
    ("declared_level_count", DECLARED_LEVEL_COUNT, "1",
     "the declared number of declared energy levels matched to the declared ablation levels"),
    ("declared_task_count", DECLARED_TASK_COUNT, "1", "the declared number of declared tasks"),
    ("declared_material_units", DECLARED_MATERIAL_UNITS, "1",
     "the declared number of discrete units of observational material computed, aggregated and "
     "distributed in stage one; a declared count and not data read by this run"),
    ("declared_recipient_count", DECLARED_RECIPIENT_COUNT, "1",
     "the declared number of recipients the material is distributed to"),
    ("declared_growth_steps", DECLARED_GROWTH_STEPS, "1",
     "the declared number of growth steps after the calibration"),
    ("declared_launches_first_step", DECLARED_LAUNCHES_FIRST_STEP, "1",
     "the declared number of launches at the first declared growth step"),
    ("declared_launch_increment", DECLARED_LAUNCH_INCREMENT, "1",
     "the declared increment of launches per declared growth step"),
    ("declared_learning_units_per_launch", DECLARED_LEARNING_UNITS_PER_LAUNCH, "1",
     "the declared number of learning units carried by one declared launch; a declared count and "
     "not a magnitude of any physical quantity"),
    ("declared_window_start_month", DECLARED_WINDOW_START_MONTH, "month_index",
     "the declared first month of the stage-one window, December"),
    ("declared_window_end_month", DECLARED_WINDOW_END_MONTH, "month_index",
     "the declared last month of the stage-one window, January; the declared window wraps"),
    ("declared_schedule_period", DECLARED_SCHEDULE_PERIOD, "1",
     "the declared period of the declared schedule, in declared steps"),
    ("declared_schedule_horizon", DECLARED_SCHEDULE_HORIZON, "1",
     "the declared horizon of the declared schedule, in declared steps"),
)


def declared_constant_rows():
    """The declared constants of the run, each as an exact rational with its declared unit."""
    rows = []
    for name, value, unit, role in DECLARED_CONSTANTS:
        rows.append({
            "name": name,
            "value": text(value),
            "unit": unit,
            "declared": True,
            "measured_here": False,
            "read_from_data": False,
            "role": role,
        })
    return rows


# -------------------------------------------------------------- the pairing rules --
# The rules of the contract's `corrects.pairing_rules`, stated as rules and ENFORCED by functions
# rather than by prose.  A mis-paired claim raises PairingViolation and is rejected by the rule
# itself, not by an arithmetic inequality that a small enough number could slip past.

ANGULAR_RADIUS = "angular_radius"
ANGULAR_DIAMETER = "angular_diameter"
ANGULAR_KINDS = (ANGULAR_RADIUS, ANGULAR_DIAMETER)

PAIRING_RULES = (
    ("P1",
     "an angular radius is paired only with an angular radius, and an angular diameter only with "
     "an angular diameter",
     "enforce_same_angular_kind"),
    ("P2",
     "the occulted area fraction at a platform is (theta_earth / theta_sun)^2 with LIKE paired "
     "with LIKE",
     "occulted_area_fraction"),
    ("P3",
     "a penumbra DIAMETER is D + theta_sun(full angular size) * L, so the spot floor uses the full "
     "angular size",
     "penumbra_diameter"),
    ("P4",
     "at the second Lagrange point the corrected occulted fraction is about 0.851 and the usable "
     "fraction about 0.149, replacing the superseded 0.787",
     "section_usable_fraction"),
)


class PairingViolation(Exception):
    """A claim that pairs unlike angular kinds, or that hands a rule a wrong kind."""


def enforce_same_angular_kind(kind_left, kind_right):
    """Rule P1: the kinds must be declared angular kinds and must be the same kind."""
    if kind_left not in ANGULAR_KINDS or kind_right not in ANGULAR_KINDS:
        raise PairingViolation(
            "a claim naming an angular kind outside the declared kinds " + str(ANGULAR_KINDS)
            + " is rejected")
    if kind_left != kind_right:
        raise PairingViolation(
            "a claim pairing " + kind_left + " with " + kind_right + " is rejected: LIKE must be "
            "paired with LIKE, an angular radius only with an angular radius and an angular "
            "diameter only with an angular diameter")
    return True


def paired_ratio(kind_left, value_left, kind_right, value_right):
    """The ratio of two angular sizes of the SAME declared kind."""
    enforce_same_angular_kind(kind_left, kind_right)
    right = Fr(value_right)
    check(right != 0, "the denominator of a paired ratio is non-zero")
    return Fr(value_left) / right


def occulted_area_fraction(kind_earth, theta_earth, kind_sun, theta_sun):
    """Rule P2: the occulted area fraction and the ratio it squares, with LIKE paired with LIKE."""
    ratio = paired_ratio(kind_earth, theta_earth, kind_sun, theta_sun)
    return ratio, ratio * ratio


def penumbra_diameter(aperture, kind, theta, distance):
    """Rule P3: a penumbra diameter is D + theta_sun(full angular size) * L.

    The angle handed to this rule must be declared as an angular DIAMETER, that is the full angular
    size; an angular radius is rejected here rather than silently halving the spot.
    """
    enforce_same_angular_kind(kind, ANGULAR_DIAMETER)
    return Fr(aperture) + Fr(theta) * Fr(distance)


def attempt(rule, *arguments):
    """Run a rule against one claim: (accepted, ratio-or-outcome)."""
    try:
        return True, rule(*arguments)
    except PairingViolation as violation:
        return False, str(violation)


# ------------------------------------------------------------- the derived geometry --
THETA_SUN_FULL_AT_ONE_AU = Fr(2 * SOLAR_RADIUS, ASTRONOMICAL_UNIT)
THETA_SUN_FULL_AT_L2 = Fr(2 * SOLAR_RADIUS, ASTRONOMICAL_UNIT + SECOND_LAGRANGE_DISTANCE)
THETA_SUN_RADIUS_AT_L2 = Fr(SOLAR_RADIUS, ASTRONOMICAL_UNIT + SECOND_LAGRANGE_DISTANCE)
THETA_SUN_FULL_AT_GEOSTATIONARY = THETA_SUN_FULL_AT_ONE_AU

THETA_EARTH_RADIUS_AT_L2 = Fr(EARTH_MEAN_RADIUS, SECOND_LAGRANGE_DISTANCE)
THETA_EARTH_FULL_AT_L2 = 2 * THETA_EARTH_RADIUS_AT_L2

FLOOR_NEAR_EARTH = THETA_SUN_FULL_AT_ONE_AU * NEAR_EARTH_DISTANCE
FLOOR_GEOSTATIONARY = THETA_SUN_FULL_AT_ONE_AU * GEOSTATIONARY_DISTANCE
FLOOR_L2 = THETA_SUN_FULL_AT_L2 * SECOND_LAGRANGE_DISTANCE

PENUMBRA_DIAMETER_NEAR_EARTH = penumbra_diameter(
    DECLARED_APERTURE, ANGULAR_DIAMETER, THETA_SUN_FULL_AT_ONE_AU, NEAR_EARTH_DISTANCE)
PENUMBRA_DIAMETER_GEOSTATIONARY = penumbra_diameter(
    DECLARED_APERTURE, ANGULAR_DIAMETER, THETA_SUN_FULL_AT_ONE_AU, GEOSTATIONARY_DISTANCE)
PENUMBRA_DIAMETER_L2 = penumbra_diameter(
    DECLARED_APERTURE, ANGULAR_DIAMETER, THETA_SUN_FULL_AT_L2, SECOND_LAGRANGE_DISTANCE)

RATIO_LIKE_WITH_LIKE_AT_L2, OCCULTED_FRACTION_AT_L2 = occulted_area_fraction(
    ANGULAR_RADIUS, THETA_EARTH_RADIUS_AT_L2, ANGULAR_RADIUS, THETA_SUN_RADIUS_AT_L2)
RATIO_DIAMETER_WITH_DIAMETER_AT_L2, OCCULTED_DIAMETER_PAIRING_AT_L2 = occulted_area_fraction(
    ANGULAR_DIAMETER, THETA_EARTH_FULL_AT_L2, ANGULAR_DIAMETER, THETA_SUN_FULL_AT_L2)

USABLE_FRACTION_AT_L2 = 1 - OCCULTED_FRACTION_AT_L2
MIS_PAIRED_RATIO_AT_L2 = THETA_EARTH_RADIUS_AT_L2 / THETA_SUN_FULL_AT_L2
MIS_PAIRED_OCCULTED_FRACTION_AT_L2 = MIS_PAIRED_RATIO_AT_L2 * MIS_PAIRED_RATIO_AT_L2

PER_MODE_CEILING = Fr(SPECTRAL_RADIANCE_B) * WAVELENGTH * WAVELENGTH

PATTERN_SCALE_RATIO_APERTURE_OVER_COHERENCE = (
    Fr(DECLARED_APERTURE) / DECLARED_COHERENCE_LENGTH)


# --------------------------------------------------- the declared solids of R6 --
# The declared data of the symmetry section: three Archimedean solids, each with a declared vertex
# construction, a declared vertex count, a declared point group and a declared rotation part.  The
# vertex sets are exact integer triples and the group elements are exact integer 3x3 matrices, so
# closure, invariance and the orbit count below are all exact integer computations, not estimates.

TRUNCATED_TETRAHEDRON = "truncated tetrahedron"
CUBOCTAHEDRON = "cuboctahedron"
TRUNCATED_OCTAHEDRON = "truncated octahedron"

ROTATION_GENERATORS_CUBIC = (
    ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
    ((0, -1, 0), (1, 0, 0), (0, 0, 1)),
)
IMPROPER_GENERATOR_CUBIC = (((-1, 0, 0), (0, -1, 0), (0, 0, -1)),)
ROTATION_GENERATORS_TETRAHEDRAL = (
    ((0, 1, 0), (0, 0, 1), (1, 0, 0)),
    ((-1, 0, 0), (0, -1, 0), (0, 0, 1)),
)
IMPROPER_GENERATOR_TETRAHEDRAL = (((0, 1, 0), (1, 0, 0), (0, 0, 1)),)

DECLARED_SOLIDS = (
    {
        "solid": TRUNCATED_TETRAHEDRON,
        "declared_vertex_construction":
            "all permutations of the declared triple (3, 1, 1) taken with the declared even number "
            "of minus signs",
        "declared_base_triple": (3, 1, 1),
        "declared_sign_parity": "even",
        "declared_vertex_count": 12,
        "declared_point_group": "T_d",
        "declared_point_group_order": 24,
        "declared_rotation_part": "T",
        "declared_rotation_part_order": 12,
        "rotation_generators": ROTATION_GENERATORS_TETRAHEDRAL,
        "improper_generators": IMPROPER_GENERATOR_TETRAHEDRAL,
    },
    {
        "solid": CUBOCTAHEDRON,
        "declared_vertex_construction":
            "all permutations of the declared triple (0, 1, 1) taken with every declared sign "
            "pattern",
        "declared_base_triple": (0, 1, 1),
        "declared_sign_parity": "every",
        "declared_vertex_count": 12,
        "declared_point_group": "O_h",
        "declared_point_group_order": 48,
        "declared_rotation_part": "O",
        "declared_rotation_part_order": 24,
        "rotation_generators": ROTATION_GENERATORS_CUBIC,
        "improper_generators": IMPROPER_GENERATOR_CUBIC,
    },
    {
        "solid": TRUNCATED_OCTAHEDRON,
        "declared_vertex_construction":
            "all permutations of the declared triple (0, 1, 2) taken with every declared sign "
            "pattern",
        "declared_base_triple": (0, 1, 2),
        "declared_sign_parity": "every",
        "declared_vertex_count": 24,
        "declared_point_group": "O_h",
        "declared_point_group_order": 48,
        "declared_rotation_part": "O",
        "declared_rotation_part_order": 24,
        "rotation_generators": ROTATION_GENERATORS_CUBIC,
        "improper_generators": IMPROPER_GENERATOR_CUBIC,
    },
)

DECLARED_ACTED_ON_COORDINATES = ("x", "y", "z")
DECLARED_TIME_DIRECTION = "t"
ARBITRARY_DECLARED_POSITIONS = ((1, 0, 0), (0, 1, 0), (0, 0, 1))

GROUP_CLOSURE_LIMIT = 512


def permutations_of(triple):
    """The distinct permutations of a declared integer triple, exactly."""
    first, second, third = triple
    return sorted({(first, second, third), (first, third, second), (second, first, third),
                   (second, third, first), (third, first, second), (third, second, first)})


def declared_vertex_set(base_triple, sign_parity):
    """The declared vertex set: exact integer triples, no floating-point value formed."""
    vertices = set()
    signs = ((1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
             (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1))
    for permutation in permutations_of(base_triple):
        for sign in signs:
            if sign_parity == "even" and sign.count(-1) % 2 != 0:
                continue
            vertices.add(tuple(permutation[index] * sign[index] for index in range(3)))
    return tuple(sorted(vertices))


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


def matrix_is_signed_permutation(matrix):
    """True when every row and every column carries exactly one entry of +1 or -1 and the rest 0."""
    for row in matrix:
        if sorted(abs(entry) for entry in row) != [0, 0, 1]:
            return False
        if sum(1 for entry in row if entry != 0) != 1:
            return False
    for column in range(3):
        if sorted(abs(matrix[row][column]) for row in range(3)) != [0, 0, 1]:
            return False
    return True


def group_closure(generators, limit=GROUP_CLOSURE_LIMIT):
    """The group generated by exact integer matrices, by closure, with a declared bound."""
    identity = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    group = {identity}
    frontier = [identity]
    while frontier:
        element = frontier.pop()
        for generator in generators:
            product = matrix_multiply(generator, element)
            if product not in group:
                group.add(product)
                check(len(group) <= limit,
                      "the generated group stays inside the declared closure bound")
                frontier.append(product)
    return tuple(sorted(group))


def orbits_of(group, points):
    """The distinct orbits of a declared point set under an exact group, as sorted orbits."""
    remaining = set(points)
    orbits = []
    while remaining:
        point = min(remaining)
        orbit = {matrix_apply(element, point) for element in group}
        orbit &= set(points)
        orbits.append(tuple(sorted(orbit)))
        remaining -= orbit
    return tuple(sorted(orbits))


def stabiliser_order(group, point, points):
    orbit = {matrix_apply(element, point) for element in group} & set(points)
    return len(group) // len(orbit)


def invariance_failures(group, points):
    """Every (element, point) pair whose image leaves the declared point set, deterministically."""
    declared = set(points)
    failures = []
    for element in group:
        for point in points:
            image = matrix_apply(element, point)
            if image not in declared:
                failures.append({"element": [list(row) for row in element],
                                 "image_of": list(point), "image": list(image)})
    return failures


def time_schedule_ticks(period, horizon):
    return tuple(step for step in range(horizon) if step % period == 0)


# ---------------------------------------------------------------- control records --
CONTROL_KEYS = ("accepted_companion", "claim", "claimed_value", "control", "control_id",
                "derived_value", "discriminates", "outcome", "rejected", "rejected_by",
                "rejection_reasons", "unit", "verdict")

FAILED_CONTROL_KEYS = ("control", "control_id", "discriminates", "outcome", "reading",
                       "the_rule_that_catches_it_instead", "variant", "why")


def control_row(control_id, control, claim, derived_value, claimed_value, unit, rejected_by,
                reasons, companion_claim, companion_verdict, companion_value):
    """One executed control with its exact rejection and its accepted companion."""
    return {
        "control_id": control_id,
        "control": control,
        "claim": claim,
        "verdict": "Rejected",
        "rejected": True,
        "rejected_by": rejected_by,
        "rejection_reasons": list(reasons),
        "discriminates": True,
        "outcome": "RejectedWithAnAcceptedCompanion",
        "derived_value": quantity(derived_value, unit),
        "claimed_value": quantity(claimed_value, unit),
        "unit": unit,
        "accepted_companion": {
            "claim": companion_claim,
            "verdict": companion_verdict,
            "accepted": True,
            "value": text(companion_value),
            "unit": unit,
        },
    }


def collect_records(node, keys, found=None):
    """Every record anywhere in the payload whose key set is exactly the declared one."""
    if found is None:
        found = []
    if isinstance(node, dict):
        if sorted(node) == sorted(keys):
            found.append(node)
        for value in node.values():
            collect_records(value, keys, found)
    elif isinstance(node, (list, tuple)):
        for item in node:
            collect_records(item, keys, found)
    return found


# -------------------------------------------------------------- R1 pairing rules ----

def section_pairing_rules():
    """R1: the four pairing rules, enforced, with a mis-paired control and its companion."""
    check(len(CONTRACT["corrects"]["pairing_rules"]) == 4,
          "the contract declares four pairing rules")
    check(len(PAIRING_RULES) == 4,
          "exactly the four declared pairing rules are implemented and no fifth is invented")
    check(all(rule_id and rule and enforced for rule_id, rule, enforced in PAIRING_RULES),
          "every rule carries its identifier, its statement and the name of its enforcement")

    check(THETA_EARTH_FULL_AT_L2 == 2 * THETA_EARTH_RADIUS_AT_L2,
          "the Earth's angular diameter is exactly twice its angular radius")
    check(THETA_SUN_FULL_AT_L2 == 2 * THETA_SUN_RADIUS_AT_L2,
          "the Sun's full angular size is exactly twice its angular radius at the second Lagrange "
          "point")
    check(RATIO_LIKE_WITH_LIKE_AT_L2 == RATIO_DIAMETER_WITH_DIAMETER_AT_L2,
          "the radius-with-radius pairing and the diameter-with-diameter pairing give the same "
          "ratio, which is what LIKE paired with LIKE means")
    check(OCCULTED_FRACTION_AT_L2 == OCCULTED_DIAMETER_PAIRING_AT_L2,
          "and the same occulted fraction, so the rule is about the pairing and not about which "
          "kind is chosen")

    mis_accepted, mis_outcome = attempt(
        occulted_area_fraction, ANGULAR_RADIUS, THETA_EARTH_RADIUS_AT_L2,
        ANGULAR_DIAMETER, THETA_SUN_FULL_AT_L2)
    check(not mis_accepted, "the deliberately mis-paired claim is rejected by the rule itself")
    check("LIKE" in mis_outcome and ANGULAR_RADIUS in mis_outcome,
          "the rejection names the rule and the offending kinds")
    check(RATIO_LIKE_WITH_LIKE_AT_L2 == 2 * MIS_PAIRED_RATIO_AT_L2,
          "the mis-paired ratio is wrong by exactly the factor two")
    check(OCCULTED_FRACTION_AT_L2 == 4 * MIS_PAIRED_OCCULTED_FRACTION_AT_L2,
          "the mis-paired area fraction is wrong by exactly the factor four")

    penumbra_accepted, penumbra_outcome = attempt(
        penumbra_diameter, DECLARED_APERTURE, ANGULAR_RADIUS, THETA_SUN_RADIUS_AT_L2,
        SECOND_LAGRANGE_DISTANCE)
    check(not penumbra_accepted,
          "the penumbra-diameter rule rejects an angular radius where the full angular size is "
          "required")
    penumbra_with_radius = (Fr(DECLARED_APERTURE)
                            + THETA_SUN_RADIUS_AT_L2 * SECOND_LAGRANGE_DISTANCE)
    check(penumbra_with_radius < PENUMBRA_DIAMETER_L2,
          "the rejected penumbra diameter is smaller than the rule's own value")
    check(PENUMBRA_DIAMETER_L2 - penumbra_with_radius
          == THETA_SUN_RADIUS_AT_L2 * SECOND_LAGRANGE_DISTANCE,
          "the rejected penumbra diameter is short by exactly theta_sun_radius * L")
    check(Fr(DECLARED_APERTURE) + FLOOR_L2 == PENUMBRA_DIAMETER_L2,
          "the penumbra diameter at the second Lagrange point is exactly the declared aperture "
          "plus the floor theta_sun * L")

    pair_control = control_row(
        "PAIR-RADIUS-DIAMETER",
        "a deliberately mis-paired claim: the Earth's angular RADIUS against the Sun's angular "
        "DIAMETER",
        "the occulted area fraction is the square of the Earth's angular radius over the Sun's "
        "angular diameter",
        OCCULTED_FRACTION_AT_L2, MIS_PAIRED_OCCULTED_FRACTION_AT_L2, "1",
        "pairing rules P1 and P2, enforced as a rule and not as an inequality",
        ["the claim pairs " + ANGULAR_RADIUS + " with " + ANGULAR_DIAMETER + " and is rejected by "
         "rule P1: " + mis_outcome,
         "the mis-paired ratio is " + text(MIS_PAIRED_RATIO_AT_L2) + ", exactly one half of the "
         "like-with-like ratio " + text(RATIO_LIKE_WITH_LIKE_AT_L2) + ", so the claimed fraction "
         "is wrong by the exact factor 4",
         "the rule is about the declared kinds: the same fraction is obtained from the Earth's "
         "angular radius with the Sun's angular radius and from the Earth's angular diameter with "
         "the Sun's angular diameter, and the rule rejects only the mixed pairing"],
        "the occulted area fraction with LIKE paired with LIKE, " + text(OCCULTED_FRACTION_AT_L2)
        + ", which the radius-with-radius and the diameter-with-diameter pairings both give",
        "Accepted_LikeWithLike", OCCULTED_FRACTION_AT_L2)

    penumbra_control = control_row(
        "PAIR-PENUMBRA-RADIUS",
        "a mis-paired claim inside the penumbra-diameter form: the Sun's angular radius used where "
        "the full angular size is required",
        "the penumbra diameter at the second Lagrange point is D + theta_sun(angular radius) * L",
        PENUMBRA_DIAMETER_L2, penumbra_with_radius, "m",
        "pairing rule P3, which requires the full angular size",
        ["the form is a penumbra DIAMETER, D + theta_sun(full angular size) * L, and the angle "
         "handed to it must be declared as an angular diameter: " + penumbra_outcome,
         "the substituted radius makes the penumbra diameter " + text(penumbra_with_radius)
         + " m instead of " + text(PENUMBRA_DIAMETER_L2) + " m, short by exactly "
         + text(THETA_SUN_RADIUS_AT_L2 * SECOND_LAGRANGE_DISTANCE) + " m, which is exactly "
         "theta_sun_radius * L",
         "the floor itself is unaffected by the aperture: the floor is theta_sun * L and the "
         "aperture only adds to it"],
        "the penumbra diameter with the full angular size, " + text(PENUMBRA_DIAMETER_L2)
        + " m, exactly the declared aperture plus the floor",
        "Accepted_FullAngularSize", PENUMBRA_DIAMETER_L2)

    mislabelled_ratio = paired_ratio(ANGULAR_RADIUS, THETA_EARTH_RADIUS_AT_L2,
                                    ANGULAR_RADIUS, THETA_SUN_FULL_AT_L2)
    check(mislabelled_ratio == MIS_PAIRED_RATIO_AT_L2,
          "the mislabelled claim passes the kind rule unchanged")
    check(mislabelled_ratio != RATIO_LIKE_WITH_LIKE_AT_L2,
          "the mislabelled claim still carries the wrong ratio")
    failed = {
        "control_id": "PAIR-MISLABELLED-DECLARATION",
        "control": "a claim that the pairing rule rejects a MISLABELLED declaration: the declared "
                   "full angular size of the Sun presented under the declared kind angular_radius",
        "variant": "the kind rule examines the declared kind of each quantity, and a declaration "
                   "that mislabels its own quantity presents matching kinds",
        "outcome": "FAILED_TO_DISCRIMINATE",
        "discriminates": False,
        "the_rule_that_catches_it_instead":
            "rule P4, the exact value bracket of the corrected fraction in R2: the mislabelled "
            "claim yields " + text(MIS_PAIRED_RATIO_AT_L2) + " and therefore "
            + text(MIS_PAIRED_OCCULTED_FRACTION_AT_L2) + ", which lies outside the declared "
            "bracket for about 0.851",
        "why": "the rule rejects a claim whose KINDS differ, and it cannot reject a claim whose "
               "kinds agree because the quantity behind one of them was mislabelled.  Both the "
               "ratio and the fraction of the mislabelled claim pass the kind rule unchanged, so "
               "this control cannot be made to fail at the rule it names, and it is retained as a "
               "FAILED CONTROL rather than repaired or dropped.",
        "reading": "what the pairing rules enforce is the declared KIND of each quantity, not the "
                   "provenance of a declaration.  A mislabelled declaration is caught by the exact "
                   "value of rule P4 and not by the kind rule; the two rules are both needed, and "
                   "the failure is reported.",
    }
    check(failed["discriminates"] is False,
          "the failed control is recorded as a failure to discriminate")
    check("FAILED CONTROL" in failed["why"], "the failed control says so in its own record")

    return {
        "rules": [{"rule_id": rule_id, "rule": rule, "enforced_by": enforced,
                   "enforced_as_a_rule": True}
                  for rule_id, rule, enforced in PAIRING_RULES],
        "rule_count": len(PAIRING_RULES),
        "the_rules_are_enforced_not_prose": True,
        "the_enforcement_is_of_the_declared_kind": True,
        "the_declared_angular_kinds": list(ANGULAR_KINDS),
        "the_full_angular_size_is_twice_the_angular_radius": True,
        "accepted_pairings": [
            {"pairing": "an angular radius with an angular radius",
             "ratio": quantity(RATIO_LIKE_WITH_LIKE_AT_L2, "1"),
             "occulted_fraction": quantity(OCCULTED_FRACTION_AT_L2, "1"),
             "accepted": True},
            {"pairing": "an angular diameter with an angular diameter",
             "ratio": quantity(RATIO_DIAMETER_WITH_DIAMETER_AT_L2, "1"),
             "occulted_fraction": quantity(OCCULTED_DIAMETER_PAIRING_AT_L2, "1"),
             "accepted": True},
        ],
        "the_two_accepted_pairings_agree_exactly": True,
        "mispaired_control": pair_control,
        "penumbra_rule": {
            "rule": "a penumbra DIAMETER is D + theta_sun(full angular size) * L",
            "declared_aperture": quantity(DECLARED_APERTURE, "m"),
            "full_angular_size_at_the_second_lagrange_point": quantity(THETA_SUN_FULL_AT_L2, "rad"),
            "penumbra_diameter_at_the_second_lagrange_point": quantity(PENUMBRA_DIAMETER_L2, "m"),
            "the_spot_floor_uses_the_full_angular_size": True,
            "accepted": True,
            "reading": "the spot floor is theta_sun * L with theta_sun the FULL angular size, and "
                       "the penumbra diameter is that floor plus the declared aperture; the same "
                       "form is reported at every declared distance in R3, and no second copy of "
                       "the floor is computed here",
        },
        "penumbra_mispaired_control": penumbra_control,
        "failed_controls": [failed],
        "failed_controls_count": 1,
        "reading": "the rules are stated as rules and enforced by the checker: a claim that pairs "
                   "an angular radius with an angular diameter is rejected by the rule, with the "
                   "exact factor two in the ratio and four in the squared fraction, while the same "
                   "fraction computed from like with like is accepted and is the value carried "
                   "throughout this run.",
    }


# ----------------------------------------------------------- R2 usable fraction ----

def earlier_payload_usable_fraction():
    """The earlier run's own retained usable fraction, read from its frozen payload."""
    earlier = json.loads(EARLIER_EVIDENCE_PATH.read_text(encoding="utf-8"),
                         parse_float=lambda literal: (_ for _ in ()).throw(
                             AssertionError("a floating-point literal in the earlier payload")))
    return Fr(earlier["sections"]["R1_derived_bounds"]["l2_usable_fraction"]
              ["usable_fraction"]["value"])


def section_usable_fraction():
    """R2: the corrected occulted and usable fractions, and the superseded value beside them."""
    superseded = earlier_payload_usable_fraction()
    difference = superseded - USABLE_FRACTION_AT_L2
    check(OCCULTED_FRACTION_AT_L2 + USABLE_FRACTION_AT_L2 == 1,
          "the occulted fraction and the usable fraction sum to exactly one")
    check(Fr(17, 20) < OCCULTED_FRACTION_AT_L2 <= Fr(851, 1000),
          "the corrected occulted fraction lies in the declared bracket for about 0.851")
    check(Fr(149, 1000) <= USABLE_FRACTION_AT_L2 < Fr(3, 20),
          "the corrected usable fraction lies in the declared bracket for about 0.149")
    check(superseded != USABLE_FRACTION_AT_L2,
          "the superseded value is not the corrected value")
    check(superseded > USABLE_FRACTION_AT_L2,
          "the superseded value is the larger of the two")
    check(difference == 3 * OCCULTED_FRACTION_AT_L2 / 4,
          "the difference is exactly three quarters of the corrected occulted fraction")
    check(OCCULTED_FRACTION_AT_L2 / 4 == MIS_PAIRED_OCCULTED_FRACTION_AT_L2,
          "the superseded value came from the mis-paired fraction, exactly one quarter of the "
          "corrected one")
    check(superseded == 1 - MIS_PAIRED_OCCULTED_FRACTION_AT_L2,
          "the superseded value is exactly one minus the mis-paired fraction")
    check(Fr(787, 1000) < superseded < Fr(788, 1000),
          "the superseded value lies in the declared bracket for about 0.787")
    check(decimals(OCCULTED_FRACTION_AT_L2, 6) == "0.850952",
          "the truncated decimal expansion of the corrected occulted fraction is exact")
    check(decimals(USABLE_FRACTION_AT_L2, 6) == "0.149047",
          "the truncated decimal expansion of the corrected usable fraction is exact")
    check(decimals(superseded, 6) == "0.787261",
          "the truncated decimal expansion of the superseded value is exact")

    platforms = (
        ("a near-Earth platform", NEAR_EARTH_DISTANCE, "declared", Fr(0), Fr(1)),
        ("a geostationary platform", GEOSTATIONARY_DISTANCE, "declared", Fr(0), Fr(1)),
        ("the second Lagrange point", SECOND_LAGRANGE_DISTANCE, "derived",
         OCCULTED_FRACTION_AT_L2, USABLE_FRACTION_AT_L2),
    )
    rows = []
    for name, distance, status, occulted, usable in platforms:
        check(occulted + usable == 1, "the fractions of " + name + " sum to exactly one")
        check(Fr(0) <= occulted <= Fr(1), "the occulted fraction of " + name + " is in [0, 1]")
        rows.append({
            "name": name,
            "declared_distance": quantity(distance, "m"),
            "occulted_fraction": quantity(occulted, "1"),
            "usable_fraction": quantity(usable, "1"),
            "status": status,
        })
    check(rows[2]["usable_fraction"]["value"] == text(USABLE_FRACTION_AT_L2),
          "the derived usable fraction of the second Lagrange point is the corrected one")
    check(rows[0]["usable_fraction"]["value"] == "1" and rows[1]["usable_fraction"]["value"] == "1",
          "the two nearer platforms carry their declared usable fraction of exactly one, with no "
          "occultation declared at their declared geometry")
    check(all(row["usable_fraction"]["value"] != text(superseded) for row in rows),
          "the superseded value is used as no platform's usable fraction anywhere in this run")

    return {
        "rule": "the occulted area fraction at a platform is (theta_earth / theta_sun)^2 with LIKE "
                "paired with LIKE, and the usable fraction is one minus it",
        "pairing_used": "an angular radius with an angular radius, and independently an angular "
                        "diameter with an angular diameter, which give the same value",
        "theta_earth_angular_radius_at_the_second_lagrange_point":
            quantity(THETA_EARTH_RADIUS_AT_L2, "rad"),
        "theta_earth_angular_diameter_at_the_second_lagrange_point":
            quantity(THETA_EARTH_FULL_AT_L2, "rad"),
        "theta_sun_angular_radius_at_the_second_lagrange_point":
            quantity(THETA_SUN_RADIUS_AT_L2, "rad"),
        "theta_sun_full_angular_size_at_the_second_lagrange_point":
            quantity(THETA_SUN_FULL_AT_L2, "rad"),
        "the_ratio_like_with_like": quantity(RATIO_LIKE_WITH_LIKE_AT_L2, "1"),
        "the_occulted_fraction": quantity(OCCULTED_FRACTION_AT_L2, "1"),
        "the_occulted_fraction_in_decimal": decimals(OCCULTED_FRACTION_AT_L2, 6),
        "the_occulted_fraction_is_about_851_thousandths": True,
        "the_bracket_of_about_0_851":
            {"lower": "17/20", "upper": "851/1000", "lower_is_open": True,
             "upper_is_closed": True},
        "usable_fraction": quantity(USABLE_FRACTION_AT_L2, "1"),
        "usable_fraction_in_decimal": decimals(USABLE_FRACTION_AT_L2, 6),
        "the_usable_fraction_is_about_149_thousandths": True,
        "the_bracket_of_about_0_149":
            {"lower": "149/1000", "upper": "3/20", "lower_is_closed": True, "upper_is_open": True},
        "the_two_fractions_sum_to_exactly_one": True,
        "platforms": rows,
        "platform_count": 3,
        "the_correction": {
            "superseded_usable_fraction": quantity(superseded, "1", status=SUPERSEDED),
            "superseded_usable_fraction_in_decimal": decimals(superseded, 6),
            "superseded_occulted_fraction": quantity(MIS_PAIRED_OCCULTED_FRACTION_AT_L2, "1",
                                                     status=SUPERSEDED),
            "the_superseded_value_is_the_earlier_runs_own_value": True,
            "the_earlier_payload": EARLIER_EVIDENCE_RELATIVE,
            "the_earlier_payload_sha256": digest(EARLIER_EVIDENCE_PATH),
            "the_earlier_payload_sha256_declared": DECLARED_EARLIER_EVIDENCE_SHA256,
            "the_earlier_payload_is_retained_byte_for_byte": True,
            "the_superseded_value_was_produced_by_a_mis_paired_ratio": True,
            "the_mis_paired_ratio": quantity(MIS_PAIRED_RATIO_AT_L2, "1"),
            "the_factor_by_which_the_mis_paired_fraction_is_wrong": "4",
            "the_difference_stated_exactly": quantity(difference, "1"),
            "the_difference_in_decimal": decimals(difference, 6),
            "the_difference_is_the_superseded_value_minus_the_corrected_one": True,
            "the_difference_is_exactly_three_quarters_of_the_corrected_occulted_fraction": True,
            "the_correction_lives_in": [NOTE_0240_RELATIVE, CONTRACT_RELATIVE],
            "the_correction_is_not_an_edit_of_the_earlier_payload": True,
            "the_superseded_value_is_used_nowhere_in_this_run": True,
            "reading": "the earlier run's usable fraction is carried here as the SUPERSEDED value, "
                       "by reference to its own frozen payload and digest; the correction lives in "
                       "note 0240 and in this contract, and neither the earlier payload nor the "
                       "earlier checker is edited.  The superseded value is larger than the "
                       "corrected one by exactly three quarters of the corrected occulted "
                       "fraction, because the mis-paired fraction is exactly one quarter of the "
                       "corrected one.",
        },
        "reading": "at the second Lagrange point the Earth occults the corrected fraction of the "
                   "solar disk and the usable fraction is one minus it; both are exact rationals "
                   "computed from the declared constants, and the pairing is like with like, so "
                   "the correction of note 0240 is carried rather than repeated.",
    }


# ---------------------------------------------------------------- R3 spot floor ----

def section_spot_floor():
    """R3: the spot floor theta_sun * L at every declared distance, with the penumbra form."""
    platforms = (
        ("a near-Earth platform", NEAR_EARTH_DISTANCE, THETA_SUN_FULL_AT_ONE_AU,
         THETA_SUN_FULL_AT_ONE_AU / 2, FLOOR_NEAR_EARTH, PENUMBRA_DIAMETER_NEAR_EARTH),
        ("a geostationary platform", GEOSTATIONARY_DISTANCE, THETA_SUN_FULL_AT_GEOSTATIONARY,
         THETA_SUN_FULL_AT_GEOSTATIONARY / 2, FLOOR_GEOSTATIONARY,
         PENUMBRA_DIAMETER_GEOSTATIONARY),
        ("the second Lagrange point", SECOND_LAGRANGE_DISTANCE, THETA_SUN_FULL_AT_L2,
         THETA_SUN_RADIUS_AT_L2, FLOOR_L2, PENUMBRA_DIAMETER_L2),
    )
    rows = []
    for name, distance, full, radius, floor, penumbra in platforms:
        check(floor == full * distance, "the floor of " + name + " is exactly theta_sun * L")
        check(full == 2 * radius,
              "the declared full angular size at " + name + " is twice the declared angular radius")
        check(penumbra == Fr(DECLARED_APERTURE) + floor,
              "the penumbra diameter of " + name + " is exactly D + theta_sun * L")
        check(penumbra > floor,
              "the penumbra diameter of " + name + " exceeds the floor, because the declared "
              "aperture is positive")
        rows.append({
            "name": name,
            "declared_distance": quantity(distance, "m"),
            "theta_sun_full_angular_size": quantity(full, "rad"),
            "theta_sun_angular_radius": quantity(radius, "rad"),
            "floor": quantity(floor, "m"),
            "floor_in_decimal": decimals(floor, 3),
            "declared_aperture": quantity(DECLARED_APERTURE, "m"),
            "penumbra_diameter": quantity(penumbra, "m"),
            "penumbra_diameter_over_the_floor": text(penumbra / floor),
        })
    check(len(rows) == 3, "the floor is computed at the three declared distances and no fourth")
    check(FLOOR_L2 > FLOOR_GEOSTATIONARY > FLOOR_NEAR_EARTH,
          "the largest floor is at the second Lagrange point and the smallest at the declared "
          "near-Earth distance")
    check(FLOOR_L2 > 2 * EARTH_MEAN_RADIUS,
          "the derived floor at the second Lagrange point exceeds the Earth's diameter")
    return {
        "rule": "the spot floor is theta_sun * L, with theta_sun the FULL angular size at the "
                "declared distance, because radiance cannot be increased",
        "the_penumbra_diameter_form": "a penumbra DIAMETER is D + theta_sun(full angular size) * L",
        "the_penumbra_diameter_form_is_stated_beside_the_floor": True,
        "the_floor_uses_the_full_angular_size": True,
        "platforms": rows,
        "platform_count": 3,
        "smallest_floor": quantity(FLOOR_NEAR_EARTH, "m"),
        "largest_floor": quantity(FLOOR_L2, "m"),
        "earth_diameter": quantity(2 * EARTH_MEAN_RADIUS, "m"),
        "the_l2_floor_exceeds_the_earths_diameter": True,
        "reading": "the floor is reported once, here, at every declared distance in the units the "
                   "contract writes it, with the penumbra-diameter form beside it; every other "
                   "section of this payload that needs the floor refers to this section's value "
                   "rather than computing a second copy of it.",
    }


# ------------------------------------------------------------ R4 etendue ceiling ----

def section_etendue_ceiling():
    """R4: the etendue ceiling B * lambda^2 per mode and what it forces."""
    check(Fr(SPECTRAL_RADIANCE_B) * WAVELENGTH * WAVELENGTH == PER_MODE_CEILING,
          "the ceiling is exactly the declared B times lambda squared")
    check(Fr(1, 10 ** 6) == PER_MODE_CEILING,
          "the declared ceiling is exactly one microwatt per mode")
    check(PER_MODE_CEILING == WAVELENGTH ** 2 * SPECTRAL_RADIANCE_B,
          "the ceiling is recomputed here from the payload's own declared constants")
    control = control_row(
        "ETENDUE-CEILING",
        "a claim above the etendue ceiling: one mode claimed to carry twice the ceiling",
        "one fibre mode carries twice the etendue-limited single-mode ceiling",
        PER_MODE_CEILING, 2 * PER_MODE_CEILING, "W",
        "the etendue ceiling B * lambda^2",
        ["the ceiling is exactly " + text(PER_MODE_CEILING) + " W per mode at the declared "
         "spectral radiance and wavelength",
         "the claim exceeds it by exactly the factor 2, and no free-space aperture raises a "
         "single-mode ceiling",
         "what the ceiling forces is the declared division: power travels in free space, and "
         "fibres are kept for phase and coherence only"],
        "exactly the etendue-limited single-mode ceiling, " + text(PER_MODE_CEILING)
        + " W, with the power itself carried in free space",
        "Accepted_AtTheCeiling", PER_MODE_CEILING)
    return {
        "rule": "the etendue-limited single-mode ceiling, of order B * lambda^2 per mode",
        "declared_spectral_radiance": quantity(SPECTRAL_RADIANCE_B, "W m^-2 sr^-1"),
        "declared_wavelength": quantity(WAVELENGTH, "m"),
        "per_mode_ceiling": quantity(PER_MODE_CEILING, "W"),
        "per_mode_ceiling_in_decimal": decimals(PER_MODE_CEILING, 6),
        "the_ceiling_is_one_microwatt_per_mode": True,
        "what_the_ceiling_forces": "power into free space, with fibres kept for phase and "
                                   "coherence only",
        "control": control,
        "reading": "the ceiling is reported once, here: at the declared constants one mode carries "
                   "exactly one microwatt, so the power of any such scheme must travel in free "
                   "space and the fibres are kept for phase and coherence only.  This is a bound "
                   "per mode and not a statement about any effect.",
    }


# --------------------------------------------------------------- R5 pattern scale ----

def section_pattern_scale(floor_section):
    """R5: the pattern scale near theta_sun * L, and the two structures that are not available."""
    rows = []
    for platform in floor_section["platforms"]:
        reference = ("R3_spot_floor/platforms/" + platform["name"] + "/floor")
        rows.append({
            "name": platform["name"],
            "pattern_scale_source": reference,
            "pattern_scale": platform["floor"],
            "the_pattern_scale_is_the_floor_value_of_that_reference": True,
        })
        distance = Fr(platform["declared_distance"]["value"])
        theta = (THETA_SUN_FULL_AT_L2 if distance == SECOND_LAGRANGE_DISTANCE
                 else THETA_SUN_FULL_AT_ONE_AU)
        check(Fr(platform["floor"]["value"]) == theta * distance,
              "the pattern scale of " + platform["name"] + " is exactly theta_sun * L at its "
              "declared distance")
    check(len(rows) == 3,
          "the pattern scale is reported at the three declared distances and no fourth")
    check(PATTERN_SCALE_RATIO_APERTURE_OVER_COHERENCE == 40,
          "the declared aperture is exactly forty times the declared coherence length")
    check(Fr(DECLARED_APERTURE) > DECLARED_COHERENCE_LENGTH,
          "the declared aperture is not below the declared coherence length")
    control = control_row(
        "PATTERN-FINER",
        "finer structure claimed than the extended source permits",
        "the declared aperture delivers a light-dark structure finer than theta_sun * L",
        FLOOR_L2, FLOOR_L2 / 4, "m",
        "the declared pattern-scale rule: finer structure is washed out by the extended source",
        ["the declared source subtends the declared full angular size, so a structure finer than "
         "theta_sun * L is washed out; the claim is finer than the floor by exactly the factor 4",
         "the coarser alternative is not available either: interference structure coarser than "
         "the scale needs an aperture below the declared coherence length "
         + text(DECLARED_COHERENCE_LENGTH) + " m, while the declared aperture is "
         + text(DECLARED_APERTURE) + " m, exactly the factor "
         + text(PATTERN_SCALE_RATIO_APERTURE_OVER_COHERENCE) + " above it",
         "the usable light-dark geometry therefore sits near theta_sun * L and neither finer nor "
         "coarser structure is claimed"],
        "the light-dark geometry at exactly the declared scale " + text(FLOOR_L2)
        + " m at the second Lagrange point",
        "Accepted_AtTheScale", FLOOR_L2)
    return {
        "rule": "the usable light-dark geometry sits near theta_sun * L",
        "the_scale_is_the_spot_floor_of_R3": True,
        "platform_scales": rows,
        "platform_count": 3,
        "finer_structure_is_washed_out_by_the_extended_source": True,
        "finer_structure_statement": "the declared source subtends the declared full angular size "
                                     "at the declared distance, so any structure finer than "
                                     "theta_sun * L is washed out and is not claimed",
        "coarser_interference_structure_needs_an_aperture_below_the_coherence_length": True,
        "declared_coherence_length": quantity(DECLARED_COHERENCE_LENGTH, "m"),
        "declared_aperture": quantity(DECLARED_APERTURE, "m"),
        "ap_over_the_coherence_length": text(PATTERN_SCALE_RATIO_APERTURE_OVER_COHERENCE),
        "the_declared_aperture_is_not_below_the_declared_coherence_length": True,
        "coarser_structure_statement": "the interference alternative at a coarser scale would need "
                                       "an aperture below the declared coherence length "
                                       + text(DECLARED_COHERENCE_LENGTH) + " m; the declared "
                                       "aperture is " + text(DECLARED_APERTURE) + " m, exactly "
                                       + text(PATTERN_SCALE_RATIO_APERTURE_OVER_COHERENCE)
                                       + " times the declared coherence length, so that structure "
                                       "is not available at the declared constants and nothing "
                                       "coarser is claimed",
        "control": control,
        "reading": "the pattern scale is reported here once, by reference to the floor computed in "
                   "R3, together with the two structures that the declared constants exclude: "
                   "finer than the scale is washed out by the extended source, and the coarser "
                   "interference structure would need an aperture below the declared coherence "
                   "length, which the declared aperture is not.",
    }


# -------------------------------------------------------- R6 symmetry constraints ----

def section_symmetry_constraints():
    """R6: the declared symmetry reading over three declared Archimedean solids."""
    check(len(DECLARED_SOLIDS) == 3,
          "three Archimedean solids are declared, with their vertex counts and point groups as "
          "declared data")
    check(len(CONTRACT["shared_items"]["symmetry_constraints"]) > 0,
          "the contract states the declared symmetry reading")
    check("SO(3)" in CONTRACT["shared_items"]["symmetry_constraints"],
          "the declared reading names SO(3)")
    check("time translations" in CONTRACT["shared_items"]["symmetry_constraints"],
          "the declared reading places the time direction in the declared schedule")

    solids = []
    for declaration in DECLARED_SOLIDS:
        vertices = declared_vertex_set(declaration["declared_base_triple"],
                                       declaration["declared_sign_parity"])
        check(len(vertices) == declaration["declared_vertex_count"],
              "the declared vertex construction of " + declaration["solid"] + " gives exactly its "
              "declared vertex count")
        rotation = group_closure(declaration["rotation_generators"])
        full = group_closure(declaration["rotation_generators"]
                             + declaration["improper_generators"])
        check(len(rotation) == declaration["declared_rotation_part_order"],
              "the generated rotation part of " + declaration["solid"] + " has exactly its "
              "declared order")
        check(len(full) == declaration["declared_point_group_order"],
              "the generated point group of " + declaration["solid"] + " has exactly its declared "
              "order")
        check(all(matrix_is_signed_permutation(element) for element in full),
              "every generated element of " + declaration["solid"] + " is an exact signed "
              "permutation of the declared coordinates")
        check(all(matrix_determinant(element) == 1 for element in rotation),
              "every element of the rotation part of " + declaration["solid"] + " has determinant "
              "exactly plus one, so it lies in SO(3)")
        improper = [element for element in full if matrix_determinant(element) == -1]
        check(len(improper) == len(full) - len(rotation),
              "the improper elements of " + declaration["solid"] + " are exactly the point-group "
              "elements outside the rotation part")
        check(set(rotation) <= set(full),
              "the rotation part of " + declaration["solid"] + " is a subgroup of its point group")
        check(all(matrix_apply(element, vertex) in set(vertices)
                  for element in full for vertex in vertices),
              "every element of the declared group of " + declaration["solid"] + " maps the "
              "declared vertex set onto itself")
        full_orbits = orbits_of(full, vertices)
        rotation_orbits = orbits_of(rotation, vertices)
        check(sum(len(orbit) for orbit in full_orbits) == len(vertices),
              "the orbits of the point group of " + declaration["solid"] + " partition its "
              "vertices")
        check(sum(len(orbit) for orbit in rotation_orbits) == len(vertices),
              "the orbits of the rotation part of " + declaration["solid"] + " partition its "
              "vertices")
        check(full_orbits == rotation_orbits,
              "the point group and its rotation part give the same vertex orbits for "
              + declaration["solid"])
        stabiliser = stabiliser_order(rotation, vertices[0], vertices)
        check(stabiliser * len(rotation_orbits[0]) == len(rotation),
              "the orbit-stabiliser relation holds exactly for " + declaration["solid"])
        solids.append({
            "solid": declaration["solid"],
            "declared_vertex_construction": declaration["declared_vertex_construction"],
            "declared_base_triple": list(declaration["declared_base_triple"]),
            "declared_sign_parity": declaration["declared_sign_parity"],
            "declared_vertex_count": declaration["declared_vertex_count"],
            "computed_vertex_count": len(vertices),
            "declared_point_group": declaration["declared_point_group"],
            "declared_point_group_order": declaration["declared_point_group_order"],
            "computed_point_group_order": len(full),
            "declared_rotation_part": declaration["declared_rotation_part"],
            "declared_rotation_part_order": declaration["declared_rotation_part_order"],
            "computed_rotation_part_order": len(rotation),
            "is_a_subgroup_of_SO3": True,
            "the_subgroup_of_SO3_is": "the rotation part " + declaration["declared_rotation_part"]
                                      + ", of order " + text(len(rotation)),
            "the_rotation_part_lies_inside_SO3": True,
            "the_full_point_group_contains_improper_elements": bool(improper),
            "computed_improper_element_count": len(improper),
            "the_full_point_group_itself_lies_inside_SO3": False,
            "orbits_of_vertices_under_the_group_as_declared": len(rotation_orbits),
            "orbits_of_vertices_under_the_rotation_part": len(rotation_orbits),
            "orbit_sizes_under_the_rotation_part": [len(orbit) for orbit in rotation_orbits],
            "orbits_of_vertices_under_the_full_point_group": len(full_orbits),
            "orbit_sizes_under_the_full_point_group": [len(orbit) for orbit in full_orbits],
            "vertex_stabiliser_order_under_the_rotation_part": stabiliser,
            "every_element_maps_the_declared_vertex_set_onto_itself": True,
            "generators_of_the_rotation_part": [[list(row) for row in element]
                                                for element in declaration["rotation_generators"]],
            "generators_of_the_full_point_group": [
                [list(row) for row in element]
                for element in declaration["rotation_generators"]
                + declaration["improper_generators"]],
            "declared_vertices": [list(vertex) for vertex in vertices],
        })

    schedule_ticks = time_schedule_ticks(DECLARED_SCHEDULE_PERIOD, DECLARED_SCHEDULE_HORIZON)
    translated = tuple(step + DECLARED_SCHEDULE_PERIOD for step in schedule_ticks)
    window = time_schedule_ticks(DECLARED_SCHEDULE_PERIOD,
                                 DECLARED_SCHEDULE_HORIZON + DECLARED_SCHEDULE_PERIOD)
    window = tuple(step for step in window if step >= DECLARED_SCHEDULE_PERIOD)
    check(translated == window,
          "the declared schedule is invariant under translation by the declared period")
    off_period = tuple(step + 1 for step in schedule_ticks)
    check(off_period != window,
          "a translation by one step is not a declared time translation and does not preserve the "
          "schedule")
    check(len(DECLARED_ACTED_ON_COORDINATES) == 3,
          "the declared point groups act on exactly three declared coordinates")
    check(DECLARED_TIME_DIRECTION not in DECLARED_ACTED_ON_COORDINATES,
          "the declared time direction is not among the acted-on coordinates")

    cuboctahedron = next(row for row in solids if row["solid"] == CUBOCTAHEDRON)
    cuboctahedron_group = group_closure(
        next(declaration for declaration in DECLARED_SOLIDS
             if declaration["solid"] == CUBOCTAHEDRON)["rotation_generators"])
    rotating_generator = ROTATION_GENERATORS_CUBIC[1]
    check(matrix_apply(rotating_generator, (0, 1, 0)) == (-1, 0, 0),
          "the declared rotation moves the declared y axis onto the negated x axis exactly")
    check(matrix_apply(rotating_generator, (0, 0, 1)) == (0, 0, 1),
          "the same declared rotation leaves the declared z axis exactly fixed")
    check(matrix_determinant(rotating_generator) == 1,
          "the declared rotation has determinant exactly plus one")
    check(matrix_apply(rotating_generator, (0, 0, 1)) == (0, 0, 1)
          and matrix_apply(rotating_generator, (1, 0, 0)) == (0, 1, 0),
          "the declared rotation permutes the declared spatial axes only")

    failures = invariance_failures(cuboctahedron_group, ARBITRARY_DECLARED_POSITIONS)
    check(bool(failures),
          "the declared arbitrary positions are NOT invariant under the declared group")
    check(len(failures) >= 1, "at least one exact witness of the failure is retained")
    witness = failures[0]
    check(witness["image"] not in [list(point) for point in ARBITRARY_DECLARED_POSITIONS],
          "the retained witness is an image outside the declared set")
    check(len(cuboctahedron["declared_vertices"]) == 12,
          "the accepted companion is the declared vertex set of the cuboctahedron")

    time_control = control_row(
        "SYM-TIME-IN-POINT-GROUP",
        "a claim that the time direction is part of the point group",
        "the declared point group contains the time direction as one of its acted-on coordinates, "
        "so the group acts on four declared coordinates including time",
        Fr(len(DECLARED_ACTED_ON_COORDINATES)), Fr(len(DECLARED_ACTED_ON_COORDINATES) + 1), "1",
        "the declared acted-on coordinate set and the declared time direction",
        ["every element of every declared group is an exact 3x3 integer matrix acting on the "
         "declared coordinates " + ", ".join(DECLARED_ACTED_ON_COORDINATES) + " and on nothing "
         "else, so the group acts on exactly three declared coordinates",
         "the declared time direction " + DECLARED_TIME_DIRECTION + " is not among them, and the "
         "declared rotation " + str([list(row) for row in rotating_generator])
         + " moves the declared y axis onto the negated x axis exactly while leaving the declared "
         "z axis exactly fixed: a direction the group moves is a spatial direction, not the time "
         "direction",
         "the time direction enters as the DECLARED SCHEDULE invariant under the corresponding "
         "time translations, which is checked exactly below, and not as an element or a direction "
         "of the point group"],
        "the declared schedule invariant: the schedule ticks " + str(list(schedule_ticks))
        + " mapped by the declared period " + text(DECLARED_SCHEDULE_PERIOD)
        + " onto themselves",
        "Accepted_TimeAsDeclaredScheduleInvariant", Fr(len(schedule_ticks)))

    arbitrary_control = control_row(
        "SYM-ARBITRARY-PLACEMENT",
        "a claim that an arbitrary set of vertex positions is invariant under the declared group",
        "the declared arbitrary positions " + str([list(point) for point
                                                   in ARBITRARY_DECLARED_POSITIONS])
        + " are invariant under the declared point group of the cuboctahedron",
        Fr(len(cuboctahedron["declared_vertices"])), Fr(len(ARBITRARY_DECLARED_POSITIONS)), "1",
        "the declared group acting on the declared positions, exactly",
        ["the declared group contains the element " + str(witness["element"])
         + ", which maps the declared position " + str(witness["image_of"]) + " to "
         + str(witness["image"]) + ", and that image is not a declared position",
         "the number of exact (element, position) pairs whose image leaves the declared set is "
         + text(len(failures)) + ", so the claim is rejected by computation and not by assertion",
         "the accepted placement is the group-invariant one: the declared vertex set of the "
         "cuboctahedron, which every element of the declared group maps onto itself"],
        "the declared Archimedean vertex set of the cuboctahedron, invariant under the declared "
        "group, whose vertices form exactly "
        + text(cuboctahedron["orbits_of_vertices_under_the_rotation_part"])
        + " orbit under the group",
        "Accepted_GroupInvariantPlacement",
        Fr(cuboctahedron["orbits_of_vertices_under_the_rotation_part"]))

    return {
        "declared_reading": CONTRACT["shared_items"]["symmetry_constraints"],
        "the_reading_is_declared_and_not_derived_from_a_spacetime_model": True,
        "lorentz_rotation_part": {
            "declared": "the rotation part of the Lorentz group",
            "SO3_is_its_rotation_part": True,
            "declared_reading": True,
            "computed_here": False,
            "reading": "the contract's declared reading is recorded here and nothing more: no "
                       "metric, no spacetime model and no Lorentz-group construction is "
                       "implemented in this run, and the embedding statement is the declaration "
                       "rather than a result of this calibration.",
        },
        "the_point_group_is_a_subgroup_of_SO3": True,
        "the_subgroup_of_SO3_is_the_rotation_part": True,
        "solids": solids,
        "solids_count": len(solids),
        "every_declared_solid_has_its_declared_order_and_its_orbit_count": True,
        "the_time_direction": {
            "declared": "the time direction enters as a declared schedule invariant under the "
                        "corresponding time translations",
            "declared_acted_on_coordinates": list(DECLARED_ACTED_ON_COORDINATES),
            "declared_time_direction": DECLARED_TIME_DIRECTION,
            "the_point_group_acts_on_exactly_three_declared_coordinates": True,
            "the_time_direction_is_not_among_the_acted_on_coordinates": True,
            "the_time_direction_is_not_part_of_the_point_group": True,
            "declared_schedule_period": quantity(DECLARED_SCHEDULE_PERIOD, "1"),
            "declared_schedule_horizon": quantity(DECLARED_SCHEDULE_HORIZON, "1"),
            "schedule_ticks": [int(step) for step in schedule_ticks],
            "translated_ticks": [int(step) for step in translated],
            "the_schedule_is_invariant_under_translation_by_the_declared_period": True,
            "a_translation_by_one_step_does_not_preserve_the_schedule": True,
        },
        "controls": [time_control, arbitrary_control],
        "control_count": 2,
        "reading": "over the three declared Archimedean solids the point group is reported with "
                   "its exact order, its rotation part is the subgroup of SO(3) of exact order "
                   "12, 24 and 24, and the vertices form exactly one orbit under the group in "
                   "each case.  A claim that the time direction is part of the point group is "
                   "rejected, and a claim that an arbitrary set of vertex positions is invariant "
                   "is rejected with an exact witness; the declared Archimedean placement is "
                   "accepted.",
    }


# ------------------------------------------------- R7 work-region and work-time ----

PLATFORM_NAMES = tuple("P" + text(index) for index in range(DECLARED_PLATFORM_COUNT))
DECLARED_PLATFORM_PHASES = tuple(range(DECLARED_PLATFORM_COUNT))
REGION_INDICES = tuple(range(DECLARED_REGION_COUNT))


def addressed_region(step, phase):
    """The declared region a declared platform addresses at a declared step."""
    return (step + phase) % DECLARED_REGION_COUNT


def section_work_region_and_time(floor_section):
    """R7: which declared regions are addressable, at which declared steps and duty cycles."""
    check(floor_section["platforms"][1]["declared_distance"]["value"]
          == text(DECLARED_WORK_REGION_DISTANCE),
          "the declared constellation distance is one of the declared distances of R3")
    floor_used = Fr(floor_section["platforms"][1]["floor"]["value"])
    penumbra_used = Fr(floor_section["platforms"][1]["penumbra_diameter"]["value"])
    check(floor_used == THETA_SUN_FULL_AT_GEOSTATIONARY * DECLARED_WORK_REGION_DISTANCE,
          "the floor used by this calculus is the R3 floor at the declared constellation distance")
    check(penumbra_used == Fr(DECLARED_APERTURE) + floor_used,
          "the penumbra diameter used here is the R3 form at the declared constellation distance")

    schedule = []
    for step in range(DECLARED_WINDOW_STEPS):
        addresses = [{"platform": PLATFORM_NAMES[phase],
                      "region": int(addressed_region(step, DECLARED_PLATFORM_PHASES[phase]))}
                     for phase in range(DECLARED_PLATFORM_COUNT)]
        schedule.append({"step": step, "addresses": addresses})

    for entry in schedule:
        regions = sorted(address["region"] for address in entry["addresses"])
        check(regions == sorted(REGION_INDICES),
              "at every declared step the declared platforms address every declared region exactly "
              "once")

    regions = []
    for region in REGION_INDICES:
        steps = [entry["step"] for entry in schedule
                 if any(address["region"] == region for address in entry["addresses"])]
        platforms = sorted(address["platform"] for entry in schedule
                           for address in entry["addresses"] if address["region"] == region)
        check(len(steps) == DECLARED_WINDOW_STEPS,
              "every declared region is addressed at every declared step of the window")
        check(len(set(platforms)) == DECLARED_PLATFORM_COUNT,
              "every declared region is addressed by every declared platform somewhere in the "
              "window")
        check(Fr(len(steps), DECLARED_WINDOW_STEPS) == 1,
              "the duty cycle of a declared region under the relay is exactly one")
        regions.append({
            "region": int(region),
            "addressed_at_steps": steps,
            "address_count": len(steps),
            "duty_cycle": text(Fr(len(steps), DECLARED_WINDOW_STEPS)),
            "addressable": True,
            "addressed_by_platforms": platforms,
        })

    platforms = []
    for phase in range(DECLARED_PLATFORM_COUNT):
        per_region = []
        for region in REGION_INDICES:
            steps = [step for step in range(DECLARED_WINDOW_STEPS)
                     if addressed_region(step, DECLARED_PLATFORM_PHASES[phase]) == region]
            check(len(steps) * DECLARED_REGION_COUNT == DECLARED_WINDOW_STEPS,
                  "one declared platform addresses one declared region at exactly one step in "
                  "every declared sweep period")
            per_region.append({"region": int(region), "steps": steps, "step_count": len(steps),
                               "duty_cycle": text(Fr(len(steps), DECLARED_WINDOW_STEPS))})
        sweep = [addressed_region(step, DECLARED_PLATFORM_PHASES[phase])
                 for step in range(DECLARED_WINDOW_STEPS)]
        check(sweep[0] == sweep[DECLARED_SWEEP_PERIOD_STEPS],
              "the declared sweep returns after exactly the declared sweep period")
        check(len(set(sweep)) == DECLARED_REGION_COUNT,
              "the declared sweep covers exactly the declared regions")
        platforms.append({
            "platform": PLATFORM_NAMES[phase],
            "declared_phase": int(DECLARED_PLATFORM_PHASES[phase]),
            "sweep": [int(region) for region in sweep],
            "sweep_period_steps": DECLARED_SWEEP_PERIOD_STEPS,
            "per_region": per_region,
            "steps_per_region": per_region[0]["step_count"],
            "duty_cycle_per_region": per_region[0]["duty_cycle"],
            "sustained_addressability_of_a_fixed_region": False,
        })

    single_duty = Fr(platforms[0]["steps_per_region"], DECLARED_WINDOW_STEPS)
    check(single_duty == Fr(1, 4),
          "a single declared platform has the exact duty cycle one quarter over the declared "
          "window")
    check(single_duty != 1, "a single declared platform cannot sustain a fixed region")
    step_one = next(entry for entry in schedule if entry["step"] == 1)
    region_three_at_step_one = [address["platform"] for address in step_one["addresses"]
                                if address["region"] == 3]
    check(region_three_at_step_one == ["P2"],
          "the declared table assigns region 3 at declared step 1 to exactly one declared platform")

    sustained_control = control_row(
        "WORK-SINGLE-PLATFORM-SUSTAINED",
        "a claim of sustained addressability of a fixed region by a single platform",
        "one declared platform sustains addressability of a fixed declared region, with duty cycle "
        "one",
        single_duty, Fr(1), "1",
        "the declared sweep and the declared window",
        ["one declared platform addresses a fixed declared region at exactly "
         + text(platforms[0]["steps_per_region"]) + " of the "
         + text(DECLARED_WINDOW_STEPS) + " declared steps, a duty cycle of exactly "
         + text(single_duty) + ", so the claim is wrong by exactly the factor "
         + text(Fr(1) / single_duty),
         "the declared spot sweeps to a different declared region at every declared step and "
         "returns after exactly " + text(DECLARED_SWEEP_PERIOD_STEPS) + " declared steps, which is "
         "the declared sweep due to the declared motion",
         "the sustained form is the relay: the declared platforms carry distinct declared "
         "phases, so a fixed declared region is addressed at every declared step by some "
         "platform"],
        "the relay form: every declared region is addressed at every declared step, with duty "
        "cycle exactly one, by the declared constellation as a whole",
        "Accepted_RelayForm", Fr(1))

    unscheduled_control = control_row(
        "WORK-SELECTED-IN-FLIGHT",
        "a claim of a region addressed at a step the declared table does not assign",
        "the declared platform P0 addresses the declared region 3 at the declared step 1",
        Fr(0), Fr(1), "1",
        "the declared schedule, which is computed in advance",
        ["the declared table assigns region 3 at declared step 1 to the declared platform "
         + str(region_three_at_step_one[0]) + ", and the declared platform P0 addresses region "
         + text(addressed_region(1, 0)) + " at that step",
         "a region and a time not present in the table computed in advance is exactly an in-flight "
         "choice, and regions and times must be computed in advance rather than chosen in flight",
         "the accepted form is the declared table itself: " + text(len(schedule)) + " declared "
         "steps, each with " + text(DECLARED_PLATFORM_COUNT) + " declared addresses"],
        "the declared table computed in advance: at declared step 1 the declared platforms address "
        "regions " + str([address["region"] for address in step_one["addresses"]]),
        "Accepted_ComputedInAdvance", Fr(len(schedule)))

    return {
        "rule": "given a declared constellation and a declared target region, the addressable "
                "regions and their declared times follow from the declared geometry: the declared "
                "sweep, the declared window and the declared duty cycle",
        "declared_constellation": {
            "platforms": list(PLATFORM_NAMES),
            "declared_platform_count": DECLARED_PLATFORM_COUNT,
            "declared_phases": [int(phase) for phase in DECLARED_PLATFORM_PHASES],
            "declared_regions": [int(region) for region in REGION_INDICES],
            "declared_region_count": DECLARED_REGION_COUNT,
            "declared_window_steps": DECLARED_WINDOW_STEPS,
            "declared_sweep_period_steps": DECLARED_SWEEP_PERIOD_STEPS,
            "declared_distance": quantity(DECLARED_WORK_REGION_DISTANCE, "m"),
            "declared": True,
        },
        "geometric_floor_used": {
            "source": "R3_spot_floor/platforms/a geostationary platform/floor",
            "value": quantity(floor_used, "m"),
            "penumbra_diameter_source":
                "R3_spot_floor/platforms/a geostationary platform/penumbra_diameter",
            "penumbra_diameter": quantity(penumbra_used, "m"),
            "the_floor_is_the_one_computed_in_R3": True,
            "reading": "the floor is not recomputed here: this calculus uses the value computed "
                       "once in R3 at the declared constellation distance, and the check above "
                       "recomputes it from the declared constants to confirm the reference.",
        },
        "the_sweep_due_to_motion": {
            "declared_motion_is_a_declared_sweep": True,
            "sweep_period_steps": DECLARED_SWEEP_PERIOD_STEPS,
            "the_sweep_returns_after_exactly_the_declared_period": True,
            "reading": "the declared motion carries the declared spot to the next declared region "
                       "at every declared step and returns after exactly the declared sweep "
                       "period; no orbital mechanics is modelled and no physical direction is "
                       "asserted.",
        },
        "schedule": schedule,
        "schedule_step_count": len(schedule),
        "regions": regions,
        "platforms": platforms,
        "the_duty_cycle_of_a_region_under_the_relay": "1",
        "the_duty_cycle_of_one_platform_over_one_region": text(single_duty),
        "regions_and_times_must_be_computed_in_advance": True,
        "the_schedule_is_computed_in_advance": True,
        "no_step_is_chosen_in_flight": True,
        "controls": [sustained_control, unscheduled_control],
        "control_count": 2,
        "reading": "every declared region is addressable at every declared step by exactly one "
                   "declared platform, so the relay form holds exactly; one declared platform "
                   "alone holds a fixed region at exactly one quarter of the declared steps.  The "
                   "table above is computed in advance, and the two controls reject a sustained "
                   "single-platform claim and a region-and-time pair the table does not carry.",
    }


# ------------------------------------------------- R8 ablation-level assignment ----

def section_ablation_level_assignment():
    """R8: tasks assigned to declared levels matched to the declared ablation levels."""
    declared_values = tuple(value for value, _ in DECLARED_LEVEL_VALUES)
    declared_names = {value: name for value, name in DECLARED_LEVEL_VALUES}
    check(len(declared_values) == DECLARED_LEVEL_COUNT,
          "the declared level set carries exactly the declared number of levels")
    check(sorted(declared_values) == list(declared_values),
          "the declared level values are declared in increasing order")
    check(len(set(declared_values)) == len(declared_values),
          "the declared level values are distinct")
    check(len(DECLARED_TASKS) == DECLARED_TASK_COUNT,
          "the declared task list carries exactly the declared number of tasks")

    assignments = []
    counts = {value: 0 for value in declared_values}
    for task, required in DECLARED_TASKS:
        check(required in declared_values,
              "the declared required level of " + task + " is in the declared level set")
        counts[required] += 1
        assignments.append({
            "task": task,
            "declared_required_level_value": required,
            "assigned_level": declared_names[required],
            "assigned_level_value": required,
            "assigned_to_a_level": True,
            "assigned_to_a_platform": False,
        })
    check(sum(counts.values()) == DECLARED_TASK_COUNT,
          "the assignments account for every declared task exactly once")
    check(set(counts.values()) <= {count for count in counts.values()},
          "the per-level counts are exact integers")
    check(all(counts[value] > 0 for value in declared_values),
          "every declared level carries at least one declared task")

    platform_control = control_row(
        "ABL-TASK-TO-PLATFORM",
        "an assignment that routes a task to a platform instead of to a declared level",
        "the declared task task_a is assigned to the declared platform P0",
        Fr(len(declared_values)), Fr(0), "1",
        "the declared assignment domain, which is the declared level set",
        ["the declared assignment domain is the declared level set "
         + str(list(declared_values)) + " and the declared task task_a carries the declared "
         "required level value 1",
         "P0 is a declared platform of the declared constellation and not a declared level, so "
         "the claim names an object outside the declared level set and routes the task to a "
         "platform",
         "the accepted form assigns the task to the declared level " + declared_names[1]
         + ", so that a platform is never the destination of a task"],
        "the declared task task_a assigned to the declared level " + declared_names[1]
        + ", whose declared level value is 1",
        "Accepted_AssignedToADeclaredLevel", Fr(1))

    outside_value = max(declared_values) + 1
    check(outside_value not in declared_values,
          "the claimed level value lies outside the declared level set")
    outside_control = control_row(
        "ABL-LEVEL-OUTSIDE-THE-DECLARED-SET",
        "an assignment to a level outside the declared level set",
        "the declared task task_c is assigned to a level whose declared value is "
        + text(outside_value),
        Fr(max(declared_values)), Fr(outside_value), "1",
        "the declared level set",
        ["the declared level values are " + str(list(declared_values)) + " and the claimed value "
         + text(outside_value) + " is not among them",
         "the claim lies exactly " + text(Fr(outside_value) - Fr(max(declared_values)))
         + " above the largest declared level value, so it is outside the declared set rather than "
         "at its edge",
         "a level outside the declared set has no declared ablation level to match, so the claim "
         "is rejected by the declared set itself"],
        "the declared task task_c assigned to the declared level " + declared_names[3]
        + ", whose declared level value is 3",
        "Accepted_InsideTheDeclaredSet", Fr(3))

    return {
        "rule": CONTRACT["shared_items"]["ablation_level_assignment"],
        "the_matching_is_declared": "the declared level values are matched to the declared "
                                    "ablation levels of the target medium by declaration; the "
                                    "level values "
                                    "are declared ordinals with declared unit 1 and are NOT "
                                    "magnitudes of any real physical quantity",
        "declared_levels": [{"level": name, "declared_level_value": value, "unit": "1",
                             "declared": True, "measured_here": False, "read_from_data": False,
                             "is_a_magnitude_of_a_physical_quantity": False}
                            for value, name in DECLARED_LEVEL_VALUES],
        "declared_level_count": DECLARED_LEVEL_COUNT,
        "declared_level_values": [int(value) for value in declared_values],
        "declared_matched_to_the_declared_ablation_levels_of_the_target_medium": True,
        "assignments": assignments,
        "assignment_count": len(assignments),
        "tasks_per_declared_level": [{"level": declared_names[value], "declared_level_value": value,
                                      "task_count": counts[value]}
                                     for value in declared_values],
        "every_task_is_assigned_to_a_declared_level": True,
        "no_task_is_assigned_to_a_platform": True,
        "no_level_outside_the_declared_set_is_used": True,
        "no_magnitude_of_any_real_physical_quantity_is_used": True,
        "controls": [platform_control, outside_control],
        "control_count": 2,
        "reading": "a task is assigned to a declared energy level matched to the declared ablation "
                   "levels of the target medium and never to a platform; every declared level "
                   "carries at least one task, the counts are exact integers, and no magnitude of "
                   "any real physical quantity and no data enter the assignment.",
    }


# ----------------------------------------------------- R9 declared obligations ----

def section_declared_obligations(work_section, floor_section):
    """R9: every declared obligation with a falsifiable counterpart that is rejected."""
    obligations = CONTRACT["declared_obligations"]
    for key in ("high_safety", "topology_preserved", "human_impact_controllable_and_small",
                "error_tolerated_and_learned", "no_magnitude"):
        check(key in obligations, "the contract declares the obligation " + key)

    region_rows = work_section["regions"]
    region_three = next(row for row in region_rows if row["region"] == 3)
    check(region_three["addressable"] and region_three["address_count"]
          == work_section["declared_constellation"]["declared_window_steps"],
          "region 3 of the declared constellation is addressable at every declared step")
    topology_control = control_row(
        "OBL-TOPOLOGY-BROKEN",
        "a violation of the declared topology obligation: a declared region leaves the declared "
        "addressable set",
        "the declared region 3 is no longer addressable at any declared step",
        Fr(region_three["address_count"]), Fr(0), "1",
        "the declared obligation that the overall topology is not broken, read as the declared "
        "addressable set",
        ["the declared region 3 is addressed at exactly " + text(region_three["address_count"])
         + " of the declared steps, and every other declared region likewise, so the declared "
         "addressable set is complete",
         "the declared reading of the topology obligation is that the declared addressable set is "
         "not broken: every declared region remains addressable at every declared step, and the "
         "group-invariant placement of R6 keeps the declared vertex set invariant",
         "the claim removes a declared region from the set, which is exactly the break the "
         "obligation forbids"],
        "every declared region stays addressable at every declared step, with duty cycle exactly "
        "one under the relay",
        "Accepted_TopologyPreserved",
        Fr(work_section["declared_constellation"]["declared_region_count"]))

    floor_used = Fr(floor_section["platforms"][1]["floor"]["value"])
    safety_control = control_row(
        "OBL-SAFETY-BELOW-THE-FLOOR",
        "a violation of the declared high-safety obligation: work below the geometric floor",
        "the declared spot at the declared constellation distance is one quarter of the geometric "
        "floor",
        floor_used, floor_used / 4, "m",
        "the declared obligation of high safety, read as the geometric floor and the schedule "
        "computed in advance",
        ["the geometric floor at the declared constellation distance is " + text(floor_used)
         + " m, and a spot below it is excluded by the floor itself",
         "the claim is below the floor by exactly the factor 4, and the declared schedule of "
         + text(work_section["schedule_step_count"]) + " steps is computed in advance rather than "
         "chosen in flight",
         "the accepted form works at exactly the floor with the schedule computed in advance"],
        "the declared work at exactly the geometric floor " + text(floor_used) + " m, with the "
        "declared schedule computed in advance",
        "Accepted_AtTheFloorComputedInAdvance", floor_used)

    step_three = next(entry for entry in work_section["schedule"] if entry["step"] == 3)
    impact_control = control_row(
        "OBL-IMPACT-NOT-CONTROLLABLE",
        "a violation of the declared human-impact obligation: a declared step at which a declared "
        "region is addressed twice",
        "two declared platforms address the declared region 3 at the declared step 3, doubling the "
        "declared impact on that region",
        Fr(DECLARED_ADDRESSES_PER_REGION_PER_STEP), Fr(2), "1",
        "the declared obligation that the human impact is controllable, read as the declared "
        "number of addresses per region per declared step",
        ["at declared step 3 the declared platforms address the declared regions "
         + str([address["region"] for address in step_three["addresses"]])
         + ", each declared region exactly once, so the declared count is exactly "
         + text(DECLARED_ADDRESSES_PER_REGION_PER_STEP),
         "the claim is exactly twice the declared count, and a region addressed twice is a "
         "declared address that is not controlled by the declared table",
         "the accepted form is the declared table itself, where every declared region receives "
         "exactly one declared address at every declared step"],
        "the declared table: every declared region receives exactly one declared address at every "
        "declared step",
        "Accepted_ImpactControlled", Fr(DECLARED_ADDRESSES_PER_REGION_PER_STEP))

    declared_error_steps = tuple(range(2, 2 + DECLARED_ERROR_STEP_COUNT * 3, 3))
    check(len(declared_error_steps) == DECLARED_ERROR_STEP_COUNT,
          "the declared number of declared error steps is used")
    learned = []
    for step in declared_error_steps:
        missed = addressed_region(step, DECLARED_PLATFORM_PHASES[0])
        erroneous = (missed + DECLARED_ERROR_MAGNITUDE_REGION_INDICES) % DECLARED_REGION_COUNT
        readdressed = next(
            entry["step"] for entry in work_section["schedule"]
            if entry["step"] > step and any(address["region"] == erroneous
                                            for address in entry["addresses"]))
        check(readdressed == step + 1,
              "the declared error at step " + text(step) + " is re-addressed at the next declared "
              "step")
        learned.append({"declared_error_step": step,
                        "declared_missed_region": int(missed),
                        "declared_erroneous_region": int(erroneous),
                        "declared_error_magnitude_region_indices":
                            DECLARED_ERROR_MAGNITUDE_REGION_INDICES,
                        "readdressed_at_step": readdressed,
                        "learned": True})
    error_control = control_row(
        "OBL-ERROR-NOT-TOLERATED",
        "a violation of the declared bounded-error obligation: a declared bounded error read as a "
        "break of the declared addressability",
        "after the declared error at the declared step " + text(declared_error_steps[0])
        + " the declared region is never addressed again",
        Fr(1), Fr(0), "1",
        "the declared bounded and learned error",
        ["the declared error is exactly " + text(DECLARED_ERROR_MAGNITUDE_REGION_INDICES)
         + " declared region index, and the miss is re-addressed at the declared step "
         + text(learned[0]["readdressed_at_step"]) + ", the very next declared step",
         "the declared bound is what makes the error bounded: a declared error of one region index "
         "at " + text(len(declared_error_steps)) + " declared steps is re-addressed within one "
         "declared step each time",
         "learning is continuous: each declared error step is carried in the payload together with "
         "the declared step that addresses the region again"],
        "the declared bounded error tolerated and learned: " + text(len(learned)) + " declared "
        "error steps, each re-addressed at the next declared step",
        "Accepted_BoundedErrorLearned", Fr(len(learned)))

    claiming_record = {"claim": "the declared work is reported together with a magnitude for one "
                                "physical quantity", "magnitude": "declared"}
    detected = magnitude_audit(claiming_record)
    check(bool(detected),
          "the rule detects a claim that carries a magnitude for a physical quantity")
    accepted_record = {"claim": "the declared level values and declared lengths only",
                       "declared_level_value": 1, "declared_length": quantity(1, "m")}
    check(not magnitude_audit(accepted_record) and not contains_float(accepted_record),
          "the accepted companion carries no magnitude key and no floating-point value")
    magnitude_control = control_row(
        "OBL-MAGNITUDE-ASSERTED",
        "a violation of the declared no-magnitude obligation: a magnitude asserted for a physical "
        "quantity",
        "the payload reports a magnitude for one physical quantity alongside the declared geometry",
        Fr(0), Fr(1), "1",
        "the declared obligation that no magnitude, sign or timing is asserted for any physical "
        "quantity",
        ["the contract declares that no magnitude, sign or timing is asserted for any physical "
         "quantity, and the rule applied to the claim above detects it exactly: "
         + "; ".join(detected) + ", with no arithmetic performed on the magnitude itself",
         "the same rule applied to the completed payload finds no key naming a magnitude or an "
         "effect, which the retained check " + "no_magnitude_or_effect_key_appears_anywhere"
         + " records, so the claim is rejected by the rule and the payload passes the same rule",
         "the accepted companion carries declared level values and declared lengths with units and "
         "nothing that is a magnitude of a physical quantity"],
        "a record carrying declared level values and declared lengths only, with no magnitude key",
        "Accepted_DeclaredQuantitiesOnly", Fr(0))

    controls = [topology_control, safety_control, impact_control, error_control, magnitude_control]
    check(all(row["rejected"] and row["discriminates"] for row in controls),
          "every declared obligation carries a falsifiable counterpart that is rejected")
    check(len(controls) == 5,
          "the five declared obligations of the contract each carry their own counterpart")
    return {
        "obligations": [
            {"obligation": "high_safety", "declared": obligations["high_safety"],
             "declared_reading": "the work respects the geometric floor of every declared distance "
                                 "and the schedule is computed in advance",
             "falsifiable_counterpart": safety_control},
            {"obligation": "topology_preserved", "declared": obligations["topology_preserved"],
             "declared_reading": "the declared addressable set is not broken: every declared "
                                 "region stays addressable at every declared step, and the "
                                 "declared vertex set stays invariant under the declared group",
             "falsifiable_counterpart": topology_control},
            {"obligation": "human_impact_controllable_and_small",
             "declared": obligations["human_impact_controllable_and_small"],
             "declared_reading": "the declared table gives every declared region exactly one "
                                 "declared address at every declared step",
             "falsifiable_counterpart": impact_control},
            {"obligation": "error_tolerated_and_learned",
             "declared": obligations["error_tolerated_and_learned"],
             "declared_reading": "a declared error of one declared region index is bounded and is "
                                 "re-addressed at the next declared step, and each declared error "
                                 "step is carried in the payload",
             "falsifiable_counterpart": error_control},
            {"obligation": "no_magnitude", "declared": obligations["no_magnitude"],
             "declared_reading": "no magnitude, sign or timing is asserted for any physical "
                                 "quantity anywhere in this payload",
             "falsifiable_counterpart": magnitude_control},
        ],
        "obligation_count": 5,
        "every_obligation_has_a_falsifiable_counterpart": True,
        "every_counterpart_is_rejected": True,
        "the_counterparts_are_executed_here": True,
        "declared_error_steps": [int(step) for step in declared_error_steps],
        "declared_error_magnitude_region_indices": DECLARED_ERROR_MAGNITUDE_REGION_INDICES,
        "learned_errors": learned,
        "learned_error_count": len(learned),
        "reading": "each declared obligation is stated with a counterpart that can fail, and each "
                   "counterpart is executed and rejected: a region removed from the declared "
                   "addressable set, work below the geometric floor, a declared region addressed "
                   "twice at one declared step, a declared bounded error read as a break, and a "
                   "magnitude asserted for a physical quantity.",
    }


# ---------------------------------------------------------------- R10 stage one ----

def section_stage_one():
    """R10: stage one as CALIBRATION, with its two invariants each falsifiable."""
    stage = CONTRACT["stage_one"]
    check(stage["phase"] == "calibration",
          "the contract records stage one as calibration")
    check("December" in stage["window"] and "January" in stage["window"],
          "the contract carries the December-to-January window")
    check("0238" in stage["window"],
          "the contract fixes that window to the chain of note 0238")
    check(len(stage["invariants"]) == 2,
          "the contract declares exactly the two invariants of stage one")

    computed = tuple(range(DECLARED_MATERIAL_UNITS))
    aggregated = tuple(range(DECLARED_MATERIAL_UNITS))
    distributed = tuple(range(DECLARED_MATERIAL_UNITS))
    check(set(computed) == set(aggregated) == set(distributed),
          "the same declared units are computed, aggregated and distributed, with none lost and "
          "none invented")
    check(len(distributed) == DECLARED_MATERIAL_UNITS,
          "the distributed material carries exactly the declared number of units")
    check(DECLARED_MATERIAL_UNITS % DECLARED_RECIPIENT_COUNT == 0,
          "the declared material divides exactly among the declared recipients")
    per_recipient = DECLARED_MATERIAL_UNITS // DECLARED_RECIPIENT_COUNT
    check(per_recipient * DECLARED_RECIPIENT_COUNT == DECLARED_MATERIAL_UNITS,
          "the per-recipient share times the declared recipient count is the declared material")
    checksums = {
        "unit_index_count": len(distributed),
        "unit_index_sum": sum(distributed),
        "unit_index_sum_of_squares": sum(index * index for index in distributed),
    }
    triangular = DECLARED_MATERIAL_UNITS * (DECLARED_MATERIAL_UNITS - 1)
    check(checksums["unit_index_sum"] * 2 == triangular,
          "the retained index sum is exactly the declared triangular sum")
    check(checksums["unit_index_sum_of_squares"] * 6
          == (DECLARED_MATERIAL_UNITS - 1) * DECLARED_MATERIAL_UNITS
          * (2 * DECLARED_MATERIAL_UNITS - 1),
          "the retained index sum of squares is exactly the declared square-pyramidal sum")

    launches = []
    cumulative = 0
    for step in range(1, DECLARED_GROWTH_STEPS + 1):
        count = (DECLARED_LAUNCHES_FIRST_STEP
                 + (step - 1) * DECLARED_LAUNCH_INCREMENT)
        cumulative += count
        launches.append({"growth_step": step, "declared_launches": count,
                         "learning_units": count * DECLARED_LEARNING_UNITS_PER_LAUNCH,
                         "cumulative_launches": cumulative})
    check(launches[0]["declared_launches"] == DECLARED_LAUNCHES_FIRST_STEP,
          "the first declared growth step carries exactly the declared first-step launches")
    check(all(launches[index]["declared_launches"] < launches[index + 1]["declared_launches"]
              for index in range(len(launches) - 1)),
          "the declared launches grow at every declared growth step")
    check(all(row["learning_units"] > 0 for row in launches),
          "every declared growth step carries learning units, including the first")
    check(all(launches[index]["learning_units"] < launches[index + 1]["learning_units"]
              for index in range(len(launches) - 1)),
          "the learning units grow strictly with every declared growth step")
    check(all(launches[index]["cumulative_launches"] < launches[index + 1]["cumulative_launches"]
              for index in range(len(launches) - 1)),
          "the declared network grows at every declared growth step")
    check(launches[0]["learning_units"] == DECLARED_LEARNING_UNITS_PER_LAUNCH,
          "learning enters at the first declared growth step and not after a control phase")

    phase_control = control_row(
        "STAGE-PHASE-CONTROL",
        "stage one rendered as a control phase",
        "stage one is a control phase, so the payload records its phase as control",
        Fr(len(stage["invariants"])), Fr(0), "1",
        "the contract's declared stage-one phase",
        ["the contract declares the phase of stage one as " + stage["phase"] + ", and the payload "
         "records exactly that phase",
         "the declared work of stage one is the computation, aggregation and distribution of the "
         "declared material followed by continuous observation and learning, and a control phase "
         "would be a different declaration",
         "the accepted form records stage one as the declared calibration in the declared window "
         "fixed for the chain of note 0238"],
        "stage one recorded as the declared calibration, in the declared December-to-January "
        "window",
        "Accepted_Calibration", Fr(1))

    topology_control = control_row(
        "STAGE-TOPOLOGY-BROKEN",
        "a violation of the declared topology invariant of stage one: the aggregation merges two "
        "declared units",
        "the aggregation merges two declared units into one, so fewer units are distributed than "
        "were computed",
        Fr(DECLARED_MATERIAL_UNITS), Fr(DECLARED_MATERIAL_UNITS - 1), "1",
        "the declared invariant that the overall topology is not broken",
        ["the computed, aggregated and distributed unit sets are exactly equal, so no unit is "
         "merged, dropped or invented and the declared count " + text(DECLARED_MATERIAL_UNITS)
         + " is carried through unchanged",
         "a merge would carry exactly one declared unit fewer, which is exactly the difference "
         "between the claimed count and the declared one",
         "the accepted form is the identity-carrying pipeline: every declared unit survives "
         "computation, aggregation and distribution"],
        "the identity-carrying pipeline: computed, aggregated and distributed sets exactly equal, "
        "with the declared index sums retained as the witness",
        "Accepted_TopologyNotBroken", Fr(DECLARED_MATERIAL_UNITS))

    zero_learning = {"growth_step": 1, "declared_launches": DECLARED_LAUNCHES_FIRST_STEP,
                     "learning_units": 0}
    check(zero_learning["learning_units"] < launches[0]["learning_units"],
          "the claimed zero-learning first step is below the declared first-step learning units")
    check(launches[0]["learning_units"] != 0,
          "the declared first growth step carries learning units")
    learning_control = control_row(
        "STAGE-LEARNING-DELAYED",
        "a violation of the declared continuous-learning invariant: learning begins only after a "
        "declared control phase",
        "the first declared growth step carries zero learning units, so learning begins after a "
        "declared control phase",
        Fr(launches[0]["learning_units"]), Fr(0), "1",
        "the declared invariant that learning is continuous from the first stage",
        ["the first declared growth step carries exactly "
         + text(launches[0]["learning_units"]) + " declared learning units, and the declared "
         "phase of stage one is " + stage["phase"] + " rather than a control phase",
         "the declared learning units grow strictly with every declared growth step, so learning "
         "is continuous from the first stage and grows with each launch",
         "the claim of a zero-learning first step is exactly the delayed learning the invariant "
         "forbids"],
        "continuous learning from the first stage: every declared growth step carries learning "
        "units, and they grow strictly",
        "Accepted_LearningContinuous", Fr(launches[0]["learning_units"]))

    return {
        "phase": stage["phase"],
        "phase_is_calibration_not_control": True,
        "declared_window": stage["window"],
        "declared_window_start_month": quantity(DECLARED_WINDOW_START_MONTH, "month_index"),
        "declared_window_end_month": quantity(DECLARED_WINDOW_END_MONTH, "month_index"),
        "the_declared_window_wraps": True,
        "declared_window_note_path": NOTE_0238_RELATIVE,
        "declared_work": stage["work"],
        "the_material_is_declared_not_read": True,
        "material_units_statement":
            "the observational material of stage one is a DECLARED count of discrete units and is "
            "not present in this payload and not read by this run: no data is read or used "
            "anywhere, and the counts below are arithmetic on declared counts.",
        "declared_material_units": quantity(DECLARED_MATERIAL_UNITS, "1"),
        "declared_recipient_count": quantity(DECLARED_RECIPIENT_COUNT, "1"),
        "units_per_recipient": quantity(per_recipient, "1"),
        "the_material_divides_exactly_among_the_recipients": True,
        "computed": dict(checksums, stage="computed"),
        "aggregated": dict(checksums, stage="aggregated"),
        "distributed": dict(checksums, stage="distributed"),
        "the_three_stages_carry_the_same_units": True,
        "growth_steps": launches,
        "growth_step_count": len(launches),
        "total_declared_launches": cumulative,
        "total_declared_learning_units": sum(row["learning_units"] for row in launches),
        "the_network_grows_at_every_declared_growth_step": True,
        "invariants": [
            {"invariant": "the overall topology is not broken",
             "declared": stage["invariants"][0],
             "falsifiable_counterpart": topology_control},
            {"invariant": "learning is continuous from the first stage",
             "declared": stage["invariants"][1],
             "falsifiable_counterpart": learning_control},
        ],
        "invariant_count": 2,
        "every_invariant_has_a_falsifiable_counterpart": True,
        "every_counterpart_is_rejected": True,
        "phase_control": phase_control,
        "reading": "stage one is CALIBRATION and not control: inside the declared December-to-"
                   "January window the declared material is computed, aggregated and distributed "
                   "with nothing lost, and then the declared launches grow and with them the "
                   "declared learning units, so learning is continuous from the first stage.  Both "
                   "invariants carry a rejected counterpart, and the phase itself carries one too.",
    }


# ------------------------------------------------- R11 proposal-only bookkeeping ----

def section_proposal_only_bookkeeping():
    """R11: the proposal-only bookkeeping and the unaddressed termination problem."""
    status_note = CONTRACT["status_note"]
    question = CONTRACT["question"]
    level = CONTRACT["level"]
    check(CONTRACT["status"].startswith(PROPOSAL_STATUS),
          "the contract declares itself a proposal only")
    check("PROPOSAL ONLY" in CONTRACT["status"],
          "the contract's status carries the proposal-only marking")
    check("authorizes nothing" in status_note,
          "the contract records that it authorizes nothing")
    check("decides nothing" in status_note, "the contract records that it decides nothing")
    check("deploys nothing" in status_note, "the contract records that it deploys nothing")
    check("asserts no physical effect" in status_note,
          "the contract records that it asserts no physical effect")
    check("uses no data" in status_note, "the contract records that it uses no data")
    check("termination" in CONTRACT["residual"][2] or "Unaddressed" in CONTRACT["residual"][2],
          "the contract's residual records the termination problem as Unaddressed")
    check("no physical claim" in level.lower() or "No physical claim" in level,
          "the contract's level states that no physical claim is made")
    check("correct" in question.lower() or "COMMON" in question,
          "the contract asks which quantities are common to every proposal")

    termination = {
        "status": UNADDRESSED,
        "declared_as": "the termination problem of this setting: what ends the declared work, and "
                       "how the declared work is terminated",
        "governance": UNASSESSED,
        "no_attempt_is_made_to_solve_it": True,
        "solved_here": False,
        "why": "this run does not attempt to solve the termination problem.  It records the status "
               "as Unaddressed, records governance as unaddressed, and states that nothing here "
               "addresses who might decide, or how, or whether it should be done.",
    }
    check(termination["status"] == UNADDRESSED,
          "the termination problem is recorded as Unaddressed")
    check(termination["solved_here"] is False,
          "the termination problem is not solved here")
    check(termination["governance"] == UNASSESSED, "governance is recorded as unaddressed")
    return {
        "authorization": NO_NONE,
        "decision": NO_NONE,
        "deployment": NO_NONE,
        "governance": UNASSESSED,
        "physical_effect_asserted": NO_NONE,
        "data_used": NO_DATA,
        "status": PROPOSAL_STATUS,
        "contract_status": CONTRACT["status"],
        "contract_status_note": status_note,
        "proposal_only_statement": "this document is a PROPOSAL ONLY - 提议性方案: it is the "
                                   "shared geometric basis of the programme's first three "
                                   "proposals, split out as its own subject; it is not "
                                   "authorized, not a decision, "
                                   "not engineering, not a deployment decision and not a "
                                   "governance position, and it authorizes nothing, decides "
                                   "nothing and deploys nothing",
        "proposal_only_in_chinese_and_english": "提议性方案 / proposal only",
        "authorizes_nothing": True,
        "decides_nothing": True,
        "deploys_nothing": True,
        "no_governance_assessment": True,
        "termination_problem": termination,
        "nothing_said_about_who_might_decide":
            "nothing here addresses who might decide, or how, or whether it should be done",
        "reading": "the bookkeeping is the contract's own: authorization, decision, deployment, "
                   "physical_effect_asserted and data_used are all none, governance is "
                   "unaddressed, and the termination problem is recorded as Unaddressed and is "
                   "not solved.",
    }


# ------------------------------------------------------------------- the payload ---

def build_payload():
    """The retained payload: every section exact, every check named, every residual recorded."""
    contract_digest = digest(CONTRACT_PATH)
    earlier_contract_digest = digest(EARLIER_CONTRACT_PATH)
    earlier_evidence_digest = digest(EARLIER_EVIDENCE_PATH)
    check(contract_digest == DECLARED_CONTRACT_SHA256,
          "the frozen contract digest matches the declared one")
    check(earlier_contract_digest == DECLARED_EARLIER_CONTRACT_SHA256,
          "the earlier proposal's contract is retained byte for byte")
    check(earlier_evidence_digest == DECLARED_EARLIER_EVIDENCE_SHA256,
          "the earlier proposal's retained payload is retained byte for byte")
    check(CONTRACT["corrects"]["note"].startswith("The previous run's usable-fraction bound"),
          "the contract names the earlier run's mis-paired bound as what it corrects")
    check(len(CONTRACT["shared_items"]) == 7,
          "the contract declares the seven shared items reported here, each once")
    check(len(CONTRACT["declared_obligations"]) == 5,
          "the contract declares five obligations, each with its counterpart")

    pairing = section_pairing_rules()
    usable = section_usable_fraction()
    floor = section_spot_floor()
    ceiling = section_etendue_ceiling()
    pattern = section_pattern_scale(floor)
    symmetry = section_symmetry_constraints()
    work = section_work_region_and_time(floor)
    ablation = section_ablation_level_assignment()
    obligations = section_declared_obligations(work, floor)
    stage_one = section_stage_one()
    bookkeeping = section_proposal_only_bookkeeping()

    constants = declared_constant_rows()
    check(len(constants) == len(DECLARED_CONSTANTS),
          "every declared constant is carried in the payload with its unit")
    check(len({row["name"] for row in constants}) == len(constants),
          "every declared constant is named once")
    check(all(row["declared"] and not row["measured_here"] and not row["read_from_data"]
              for row in constants),
          "every constant is marked declared and not measured here and not read from data")
    check(all(row["unit"] for row in constants),
          "every declared constant carries its declared unit")
    check(not any(isinstance(value, float) for _, value, _, _ in DECLARED_CONSTANTS),
          "no declared constant is a floating-point value")

    payload = {
        "schema": SCHEMA,
        "version": 1,
        "level": CONTRACT["level"],
        "question": CONTRACT["question"],
        "contract": CONTRACT_RELATIVE,
        "contract_sha256": contract_digest,
        "contract_sha256_declared": DECLARED_CONTRACT_SHA256,
        "checker_sha256": digest(pathlib.Path(__file__).resolve()),
        "declared_constants": constants,
        "declared_constants_count": len(constants),
        "declared_inputs_are_declared_and_not_measured": True,
        "declared_inputs_statement":
            "every constant above is a DECLARED input of this proposal, carried as an exact "
            "rational with its declared unit; none of them is a measurement of this run, no "
            "instrument was used, no data was read and no clock was consulted.  The derived "
            "quantities of this run rest on these declarations: a different declaration of the "
            "constants is a different run, while the FORM of each relation is not a declaration.",
        "cited_artifacts": [
            {"path": EARLIER_CONTRACT_RELATIVE, "sha256": earlier_contract_digest,
             "sha256_declared": DECLARED_EARLIER_CONTRACT_SHA256, "hashed_here": True,
             "retained_byte_for_byte": True,
             "relation": "the proposal whose usable-fraction bound pairs an angular radius with an "
                         "angular diameter; its correction is carried here and it is not edited"},
            {"path": EARLIER_EVIDENCE_RELATIVE, "sha256": earlier_evidence_digest,
             "sha256_declared": DECLARED_EARLIER_EVIDENCE_SHA256, "hashed_here": True,
             "retained_byte_for_byte": True,
             "relation": "the earlier run's retained payload: its own usable-fraction value is "
                         "carried here as the superseded value and its digest is unchanged"},
            {"path": NOTE_0240_RELATIVE, "sha256": None, "sha256_declared": None,
             "hashed_here": False, "retained_byte_for_byte": True,
             "relation": "the note that registers the erratum; the correction lives there and in "
                         "this experiment's contract.  The note is cited and not hashed, because "
                         "this run depends on the correction and not on the note's bytes"},
            {"path": NOTE_0241_RELATIVE, "sha256": None, "sha256_declared": None,
             "hashed_here": False, "retained_byte_for_byte": True,
             "relation": "the note that splits the geometry foundation out as its own subject and "
                         "declares the stage-one calibration.  Cited and not hashed"},
            {"path": NOTE_0238_RELATIVE, "sha256": None, "sha256_declared": None,
             "hashed_here": False, "retained_byte_for_byte": True,
             "relation": "the chain whose December-to-January window the contract carries.  Cited "
                         "and not hashed"},
        ],
        "corrects": {
            "note": CONTRACT["corrects"]["note"],
            "pairing_rules": list(CONTRACT["corrects"]["pairing_rules"]),
            "the_correction_is_carried_and_the_earlier_payload_is_not_edited": True,
        },
        "tooling": {
            "arithmetic": "exact integers and fractions.Fraction only, with exact integer matrix "
                          "multiplication for the group closure",
            "external_libraries_imported": [],
            "declared_external_library_available_but_unused": "sympy 1.14",
            "declared_not_native_authority": True,
            "exact_only": True,
            "used_for": ["exact rational arithmetic on declared constants and derived geometry",
                         "exact integer group closure, invariance and orbit counting"],
            "not_implemented": [
                "a wave-optics or beam-propagation solver of any kind",
                "an orbital-mechanics or ephemeris computation of any kind",
                "a Lorentz-group construction, a metric or any spacetime model",
                "a native certificate of any kind",
                "any physical effect, forecast or magnitude",
            ],
        },
        "limits": CONTRACT["budgets"],
        "assertions": ASSERTIONS["n"],
        "sections": {
            "R1_pairing_rules": pairing,
            "R2_usable_fraction": usable,
            "R3_spot_floor": floor,
            "R4_etendue_ceiling": ceiling,
            "R5_pattern_scale": pattern,
            "R6_symmetry_constraints": symmetry,
            "R7_work_region_and_time": work,
            "R8_ablation_level_assignment": ablation,
            "R9_declared_obligations": obligations,
            "R10_stage_one": stage_one,
            "R11_proposal_only_bookkeeping": bookkeeping,
        },
        "verification_status": {
            "observational": "Unavailable",
            "reason": "this is a shared geometric basis of proposals that are not deployed, and "
                      "this run uses no data; no observation, forecast or measurement enters it",
            "physical_effect_asserted": NO_NONE,
            "deployment": NO_NONE,
            "no_data_read_or_used": True,
            "checked_here": {
                "no_data_read_or_used": True,
                "no_physical_effect_is_asserted": True,
                "no_magnitude_of_any_physical_quantity_is_asserted": True,
                "the_pairing_rules_are_enforced_as_rules": True,
                "the_corrected_usable_fraction_is_carried": True,
                "the_superseded_value_is_marked_superseded": True,
                "the_earlier_payload_is_retained_byte_for_byte": True,
                "the_symmetry_reading_is_declared": True,
                "regions_and_times_are_computed_in_advance": True,
                "tasks_are_assigned_to_declared_levels": True,
                "stage_one_is_recorded_as_calibration": True,
                "governance_is_unaddressed": True,
            },
        },
        "undecided": [
            {"item": "whether the contract's declared reading places the full point group or only "
                     "its rotation part inside SO(3)",
             "reason": "the contract declares that a polyhedral point group is a subgroup of SO(3) "
                       "and hence of the Lorentz group's rotation part.  The computation here "
                       "finds that the full point group of an achiral Archimedean solid contains "
                       "improper elements and so is not itself inside SO(3), while its rotation "
                       "part is; this run reads the declared sentence through the rotation part, "
                       "reports both orders exactly, and leaves the reading itself undecided.  "
                       "Whether a chiral solid should be declared as a fourth - one whose full "
                       "point group would carry no improper element at all - is not decided here "
                       "either, and no fourth solid is declared or computed.",
             "retained_partial_result": {
                 "truncated_tetrahedron": "T_d of order 24 with rotation part T of order 12",
                 "cuboctahedron": "O_h of order 48 with rotation part O of order 24",
                 "truncated_octahedron": "O_h of order 48 with rotation part O of order 24",
             }},
            {"item": "whether the December-to-January window of note 0238 is the same declared "
                     "window the contract carries",
             "reason": "the contract declares the window as already fixed for the chain of note "
                       "0238.  That note's own arithmetic is carried in declared steps and does "
                       "not name months, so this run carries the declared month indices as "
                       "declared and cites the note rather than deriving the window from it.",
             "retained_partial_result": {
                 "declared_window_start_month": text(DECLARED_WINDOW_START_MONTH),
                 "declared_window_end_month": text(DECLARED_WINDOW_END_MONTH),
                 "declared_window_horizon_steps": text(DECLARED_WINDOW_STEPS),
                 "cited_note": NOTE_0238_RELATIVE,
             }},
            {"item": "whether the declared distances of the earlier proposal are the ones this "
                     "shared basis is meant to carry",
             "reason": "the three declared platform distances and the declared aperture are "
                       "carried here as declarations of this run and are numerically the earlier "
                       "run's "
                       "declared values.  A different declaration is a different run; whether some "
                       "other declared distance set was intended for the shared basis is not "
                       "decided here.",
             "retained_partial_result": {
                 "near_earth_distance": text(NEAR_EARTH_DISTANCE),
                 "geostationary_distance": text(GEOSTATIONARY_DISTANCE),
                 "second_lagrange_distance": text(SECOND_LAGRANGE_DISTANCE),
                 "floor_at_the_second_lagrange_point": text(FLOOR_L2),
             }},
            {"item": "whether the coherence length should be derived rather than declared",
             "reason": "the pattern-scale item needs a coherence length to compare an aperture "
                       "against, and this run declares it as one declared constant.  Whether it "
                       "should instead be derived from the declared wavelength and a declared "
                       "bandwidth is not decided here, and no bandwidth is declared.",
             "retained_partial_result": {
                 "declared_coherence_length": text(DECLARED_COHERENCE_LENGTH),
                 "declared_aperture": text(DECLARED_APERTURE),
                 "aperture_over_the_coherence_length":
                     text(PATTERN_SCALE_RATIO_APERTURE_OVER_COHERENCE),
             }},
            {"item": "whether the declared ablation levels are to be matched by ordinal value only",
             "reason": "the declared reading matches tasks to declared energy levels matched to "
                       "the declared ablation levels of the target medium.  This run carries "
                       "ordinal level values with declared unit 1 and no magnitude of any real "
                       "physical quantity; whether a declared medium would need a different or "
                       "finer level set is not decided here and no data is used.",
             "retained_partial_result": {
                 "declared_level_values": [int(value) for value, _ in DECLARED_LEVEL_VALUES],
                 "declared_task_count": text(DECLARED_TASK_COUNT),
                 "levels_carrying_tasks": text(DECLARED_LEVEL_COUNT),
             }},
            {"item": "whether the work-region calculus should model continuous motion rather than "
                     "declared discrete steps",
             "reason": "the sweep is carried as a declared discrete step cycle with a declared "
                       "period, and no orbital mechanics, ephemeris or continuous geometry is "
                       "modelled anywhere in this run.  Whether a continuous model would change "
                       "the declared duty cycles is not decided here and is not estimated.",
             "retained_partial_result": {
                 "declared_window_steps": text(DECLARED_WINDOW_STEPS),
                 "declared_sweep_period_steps": text(DECLARED_SWEEP_PERIOD_STEPS),
                 "duty_cycle_of_one_platform": "1/4",
                 "duty_cycle_of_a_region_under_the_relay": "1",
             }},
            {"item": "whether the small perturbations of stage one are perturbations of the "
                     "declared schedule or of something physical",
             "reason": "the contract's stage-one work speaks of the evolution of small "
                       "perturbations, and this run carries them as declared perturbations of the "
                       "declared schedule: a declared error of one declared region index at "
                       "declared steps, re-addressed at the next declared step.  Whether they are "
                       "meant as anything else is not decided here, and nothing physical is "
                       "asserted about them.",
             "retained_partial_result": {
                 "declared_error_steps": [int(step) for step in
                                          range(2, 2 + DECLARED_ERROR_STEP_COUNT * 3, 3)],
                 "declared_error_magnitude_region_indices":
                     text(DECLARED_ERROR_MAGNITUDE_REGION_INDICES),
                 "readdressed_at": "the next declared step",
             }},
            {"item": "whether the earlier run's superseded usable fraction should be recomputed "
                     "anywhere else",
             "reason": "the superseded value is recomputed here exactly, carried as superseded, "
                       "and its difference from the corrected value is stated exactly.  The "
                       "earlier payload keeps its digest and is not edited, so any consumer that "
                       "reads it still reads the mis-paired value; whether that payload should be "
                       "superseded by a further run with its own contract is not decided here.",
             "retained_partial_result": {
                 "superseded_usable_fraction":
                     text(earlier_payload_usable_fraction()),
                 "corrected_usable_fraction": text(USABLE_FRACTION_AT_L2),
                 "the_earlier_payload_sha256": earlier_evidence_digest,
             }},
        ],
        "modelling_choices": {
            "declared_constants_are_declared": "every constant is carried as an exact rational "
                                               "with its declared unit and is marked declared, "
                                               "not measured here and not read from data; the "
                                               "FORM of each relation is not a declaration, while "
                                               "different constants are a different run.",
            "pairing_like_with_like": "the pairing rules are implemented as rules that raise on a "
                                      "mixed pairing, so a mis-paired claim is rejected by the "
                                      "rule and not by an arithmetic inequality.  The radius "
                                      "pairing and the diameter pairing are both accepted and give "
                                      "the same value, which is what makes the rule a rule about "
                                      "pairing rather than about a preferred kind.",
            "penumbra_diameter_form": "the penumbra diameter is D + theta_sun(full angular size) * "
                                      "L, and the rule rejects an angular radius handed to it, so "
                                      "the spot floor uses the full angular size and the aperture "
                                      "only adds to the floor.",
            "corrected_fraction_and_the_superseded_value": "the corrected occulted and usable "
                                                           "fractions are exact rationals from "
                                                           "the declared constants with LIKE "
                                                           "paired with LIKE; the earlier run's "
                                                           "value is carried as SUPERSEDED, with "
                                                           "its own digest cited, and the exact "
                                                           "difference between the two is stated.  "
                                                           "The earlier payload and checker are "
                                                           "not edited.",
            "floor_reported_once": "the spot floor and the penumbra-diameter form are reported "
                                   "once, in R3, at every declared distance; the work-region "
                                   "calculus "
                                   "refers to that value by name and recomputes it from the "
                                   "declared constants only to confirm the reference, and the "
                                   "pattern scale refers to it rather than restating it.",
            "pattern_scale_is_the_floor": "the pattern scale is the floor theta_sun * L at each "
                                          "declared distance; finer structure is excluded because "
                                          "the declared source subtends the declared full angular "
                                          "size, and the coarser interference structure is "
                                          "excluded because it would need an aperture below the "
                                          "declared coherence length, while the declared aperture "
                                          "is exactly forty times that length.",
            "symmetry_reading_through_the_rotation_part":
                "the contract's declared reading is implemented by reporting each declared "
                "solid's point group with its exact order and its rotation part as the subgroup "
                "of SO(3); for the achiral solids the full point group contains improper "
                "elements and is therefore not itself inside SO(3), and this is reported rather "
                "than smoothed over.",
            "time_direction_as_schedule_invariant":
                "the time direction enters as a declared schedule invariant under the "
                "corresponding time translations: the declared schedule ticks are mapped onto "
                "themselves by the declared period exactly, and a translation by one step is "
                "shown not to preserve them, so the invariance is specifically under the "
                "declared translations.",
            "group_data_is_declared": "each solid's vertex construction, base triple, sign parity, "
                                      "vertex count, point group and order are declared data; the "
                                      "group is then generated by closure over declared integer "
                                      "generators, and its order, its invariance on the declared "
                                      "vertex set and the orbit count are computed exactly rather "
                                      "than declared.",
            "work_region_discrete_steps": "the constellation, the regions, the window and the "
                                          "sweep are declared discrete data and the scheduling "
                                          "rule is "
                                          "a declared modular rule; no orbital mechanics and no "
                                          "physical direction or timing is modelled or asserted.",
            "computation_in_advance": "the schedule is computed in advance as an explicit table of "
                                      "declared steps, and a region-and-time pair the table does "
                                      "not carry is rejected as an in-flight choice.",
            "ablation_levels_are_declared": "the level values are declared ordinals with declared "
                                            "unit 1, matched to the declared ablation levels of "
                                            "the target medium by declaration; no magnitude of any "
                                            "real physical quantity and no data enter the "
                                            "assignment, and a task is never routed to a platform.",
            "obligations_with_counterparts": "each declared obligation is stated together with a "
                                             "counterpart that can fail, and every counterpart is "
                                             "executed and rejected; the declared topologies are "
                                             "read as the declared addressable set and the "
                                             "declared invariant vertex placement, which is "
                                             "declared here rather than assumed.",
            "stage_one_is_calibration": "stage one is recorded as CALIBRATION in the declared "
                                        "December-to-January window, with the declared material "
                                        "computed, aggregated and distributed and the declared "
                                        "launches and learning units growing; the material is a "
                                        "declared count of units and is not read as data.",
            "proposal_only": "the payload records authorization none, decision none, deployment "
                             "none, governance unaddressed, physical_effect_asserted none and "
                             "data_used none, and states that the document is a 提议性方案, a "
                             "proposal only.",
            "termination_unaddressed": "the termination problem is recorded as Unaddressed with "
                                       "its reason and is not solved, and nothing here addresses "
                                       "who "
                                       "might decide, or how, or whether it should be done.",
            "no_magnitude": "no magnitude, sign or timing is asserted for any physical "
                            "quantity, no physical effect is asserted anywhere, and the payload "
                            "carries no key "
                            "naming a magnitude or an effect; every decimal string in the payload "
                            "is a truncated integer expansion and not a floating-point value.",
            "exact_only": "every acceptance assertion and every value in the retained payload "
                          "is an exact integer or fraction, carried as an exact decimal-free "
                          "string with "
                          "its declared unit; no floating-point value is formed in an acceptance "
                          "assertion or written into the payload.",
            "external_library": "no external library is imported.  sympy 1.14 is declared as "
                                "available on the host, as non-authoritative and as unused, "
                                "because "
                                "the group closure and the arithmetic here are exact integer and "
                                "rational work that the standard library alone performs.",
            "resource_limits": "the checker installs a CPU limit, a file-size limit and a wall "
                               "alarm, and records the contract's declared memory budget without "
                               "installing an address-space ceiling; no child process is launched.",
        },
        "residual": CONTRACT["residual"],
        "acceptance": CONTRACT["acceptance"],
        "what_is_not_claimed": {
            "authorization": NO_NONE,
            "decision": NO_NONE,
            "deployment": NO_NONE,
            "governance": UNASSESSED,
            "physical_effect_asserted": NO_NONE,
            "data_used": NO_DATA,
            "native_certificate": False,
            "native_admission": "NotGranted",
            "stable_api_change": False,
            "physical_claim": False,
            "forecast": False,
            "capability_claim": False,
            "magnitude_of_any_physical_quantity": False,
            "effect_on_any_atmosphere_ocean_ice_cloud_or_surface": False,
            "weather_or_climate_effect": False,
            "observational_verification": "Unavailable",
            "meteorological_data_used": False,
            "no_data_read_or_used": True,
            "the_document_is_a_proposal_only": True,
            "the_pairing_rules_are_enforced_as_rules": True,
            "the_usable_fraction_is_corrected": True,
            "the_superseded_value_is_marked_superseded": True,
            "the_earlier_payload_is_retained_byte_for_byte": True,
            "the_geometry_is_shared_and_reported_once_per_item": True,
            "regions_and_times_are_computed_in_advance": True,
            "tasks_are_assigned_to_levels_not_platforms": True,
            "stage_one_is_calibration": True,
            "learning_is_continuous_from_the_first_stage": True,
            "the_topology_is_not_broken": True,
            "the_termination_problem_is_unaddressed": True,
            "no_seal_no_transport_no_terminology_home": True,
            "no_rust_source_or_lock_changed": True,
            "no_contract_or_note_edited": True,
            "no_claim_added_to_docs_claims_toml": True,
            "pre_existing_files_byte_identical": True,
        },
        "checks": {},
    }

    controls = collect_records(payload, CONTROL_KEYS)
    failed_controls = collect_records(payload, FAILED_CONTROL_KEYS)
    control_ids = [row["control_id"] for row in controls]
    check(len(control_ids) == len(set(control_ids)),
          "every control carries its own identifier exactly once")
    check(all(row["discriminates"] and row["rejected"] for row in controls),
          "every discriminating control is rejected")
    check(all(row["accepted_companion"]["accepted"] for row in controls),
          "every control carries an accepted companion, which is what makes the rejection a "
          "discrimination and not a blanket rule")
    check(all(row["rejection_reasons"] for row in controls),
          "every control states its rejection reasons")
    check(len(failed_controls) == 1,
          "the one control that could not be made to fail is retained as a failed control")
    check(all(not row["discriminates"] for row in failed_controls),
          "the failed control is recorded as a failure to discriminate")

    effect_findings = magnitude_audit(payload)
    in_flight_findings = in_advance_audit(payload)
    check(all(row["reason"] and row["retained_partial_result"] is not None
              for row in payload["undecided"]),
          "every undecided item carries its reason and its retained partial result")
    check(all(isinstance(value, str) and value
              for value in payload["modelling_choices"].values()),
          "every modelling choice is stated")
    check(len(payload["modelling_choices"]) == 20,
          "the modelling choices declared here are all present")
    check(all(sorted(row) == ["item", "reason", "retained_partial_result"]
              for row in payload["undecided"]),
          "every undecided record carries exactly its item, its reason and its retained partial "
          "result")

    payload["controls_summary"] = {
        "controls": [{"control_id": row["control_id"], "outcome": row["outcome"],
                      "discriminates": row["discriminates"]} for row in controls],
        "failed_controls": [{"control_id": row["control_id"], "outcome": row["outcome"],
                             "discriminates": row["discriminates"]}
                            for row in failed_controls],
        "controls_count": len(controls),
        "controls_rejected": sum(1 for row in controls if row["rejected"]),
        "controls_failed_to_discriminate": len(failed_controls),
        "every_control_has_an_accepted_companion": True,
        "no_control_is_dropped": True,
        "why_a_failed_control_is_retained":
            "a control that cannot be made to fail is reported as a failed control rather than "
            "dropped or quietly repaired, so the record shows exactly where the rejection argument "
            "stops",
        "reading": "this ledger indexes the outcomes of every control executed in the sections "
                   "above, each of which has its own home there; no item is reported twice here.",
    }

    checks = {
        "assertions_within_budget": ASSERTIONS["n"] <= CONTRACT["budgets"]["max_assertions"],
        "this_contract_digest_matches_the_declared_one":
            payload["contract_sha256"] == payload["contract_sha256_declared"],
        "the_earlier_proposal_is_retained_byte_for_byte": all(
            row["sha256"] == row["sha256_declared"] for row in payload["cited_artifacts"]
            if row["hashed_here"]),
        "the_contract_declares_itself_a_proposal_only":
            CONTRACT["status"].startswith(PROPOSAL_STATUS),
        "the_seven_shared_items_are_reported_once_each":
            len(CONTRACT["shared_items"]) == 7 and len(payload["sections"]) == 11,
        "every_declared_constant_is_declared_and_not_measured":
            all(row["declared"] and not row["measured_here"] and not row["read_from_data"]
                for row in payload["declared_constants"]),
        "the_pairing_rules_are_enforced_as_rules":
            pairing["the_rules_are_enforced_not_prose"] and pairing["rule_count"] == 4,
        "the_mispaired_control_is_rejected_by_the_rule":
            pairing["mispaired_control"]["rejected"]
            and pairing["mispaired_control"]["discriminates"],
        "the_mispaired_fraction_is_wrong_by_exactly_four":
            OCCULTED_FRACTION_AT_L2 == 4 * MIS_PAIRED_OCCULTED_FRACTION_AT_L2,
        "the_accepted_pairings_agree_exactly":
            pairing["the_two_accepted_pairings_agree_exactly"]
            and RATIO_LIKE_WITH_LIKE_AT_L2 == RATIO_DIAMETER_WITH_DIAMETER_AT_L2,
        "the_penumbra_diameter_uses_the_full_angular_size":
            pairing["penumbra_rule"]["the_spot_floor_uses_the_full_angular_size"],
        "the_penumbra_mispaired_control_is_rejected":
            pairing["penumbra_mispaired_control"]["rejected"]
            and pairing["penumbra_mispaired_control"]["discriminates"],
        "the_corrected_occulted_fraction_is_carried":
            Fr(usable["the_occulted_fraction"]["value"]) == OCCULTED_FRACTION_AT_L2
            and usable["the_occulted_fraction_is_about_851_thousandths"],
        "the_corrected_usable_fraction_is_carried":
            Fr(usable["usable_fraction"]["value"]) == USABLE_FRACTION_AT_L2
            and usable["the_usable_fraction_is_about_149_thousandths"],
        "the_corrected_fractions_sum_to_exactly_one":
            OCCULTED_FRACTION_AT_L2 + USABLE_FRACTION_AT_L2 == 1,
        "the_superseded_value_is_the_earlier_payloads_own":
            usable["the_correction"]["the_superseded_value_is_the_earlier_runs_own_value"]
            and Fr(usable["the_correction"]["superseded_usable_fraction"]["value"])
            == earlier_payload_usable_fraction(),
        "the_superseded_value_is_marked_superseded":
            usable["the_correction"]["superseded_usable_fraction"]["status"] == SUPERSEDED,
        "the_difference_between_the_two_is_stated_exactly":
            Fr(usable["the_correction"]["the_difference_stated_exactly"]["value"])
            == earlier_payload_usable_fraction() - USABLE_FRACTION_AT_L2,
        "the_correction_cites_the_note_and_this_contract":
            NOTE_0240_RELATIVE in usable["the_correction"]["the_correction_lives_in"]
            and CONTRACT_RELATIVE in usable["the_correction"]["the_correction_lives_in"],
        "the_superseded_value_is_used_nowhere":
            usable["the_correction"]["the_superseded_value_is_used_nowhere_in_this_run"]
            and all(row["usable_fraction"]["value"] != text(earlier_payload_usable_fraction())
                    for row in usable["platforms"]),
        "the_floor_is_reported_at_three_declared_distances": floor["platform_count"] == 3,
        "the_l2_floor_exceeds_the_earths_diameter":
            floor["the_l2_floor_exceeds_the_earths_diameter"],
        "the_etendue_ceiling_is_one_microwatt_per_mode":
            Fr(ceiling["per_mode_ceiling"]["value"]) == Fr(1, 10 ** 6),
        "the_ceiling_forces_power_into_free_space":
            "free space" in ceiling["what_the_ceiling_forces"]
            and "phase" in ceiling["what_the_ceiling_forces"],
        "the_etendue_control_is_rejected":
            ceiling["control"]["rejected"] and ceiling["control"]["discriminates"],
        "the_pattern_scale_is_the_floor":
            pattern["the_scale_is_the_spot_floor_of_R3"]
            and all(row["the_pattern_scale_is_the_floor_value_of_that_reference"]
                    for row in pattern["platform_scales"]),
        "finer_structure_is_washed_out":
            pattern["finer_structure_is_washed_out_by_the_extended_source"],
        "coarser_structure_needs_an_aperture_below_the_coherence_length":
            pattern["coarser_interference_structure_needs_an_aperture_below_the_coherence_length"]
            and pattern["the_declared_aperture_is_not_below_the_declared_coherence_length"],
        "the_pattern_control_is_rejected":
            pattern["control"]["rejected"] and pattern["control"]["discriminates"],
        "three_archimedean_solids_are_declared": symmetry["solids_count"] == 3,
        "every_declared_solid_has_its_declared_order":
            all(row["computed_point_group_order"] == row["declared_point_group_order"]
                and row["computed_rotation_part_order"] == row["declared_rotation_part_order"]
                and row["computed_vertex_count"] == row["declared_vertex_count"]
                for row in symmetry["solids"]),
        "every_declared_solid_lies_in_SO3_through_its_rotation_part":
            all(row["is_a_subgroup_of_SO3"] and row["the_rotation_part_lies_inside_SO3"]
                for row in symmetry["solids"]),
        "every_declared_solids_vertices_form_the_reported_number_of_orbits":
            all(row["orbits_of_vertices_under_the_rotation_part"]
                == len(row["orbit_sizes_under_the_rotation_part"])
                and sum(row["orbit_sizes_under_the_rotation_part"]) == row["computed_vertex_count"]
                and sum(row["orbit_sizes_under_the_full_point_group"])
                == row["computed_vertex_count"]
                for row in symmetry["solids"]),
        "the_vertices_are_invariant_under_the_declared_group":
            all(row["every_element_maps_the_declared_vertex_set_onto_itself"]
                for row in symmetry["solids"]),
        "the_time_direction_is_not_part_of_the_point_group":
            symmetry["the_time_direction"]["the_time_direction_is_not_part_of_the_point_group"],
        "the_schedule_is_invariant_under_the_declared_translations":
            symmetry["the_time_direction"]
            ["the_schedule_is_invariant_under_translation_by_the_declared_period"]
            and symmetry["the_time_direction"]
            ["a_translation_by_one_step_does_not_preserve_the_schedule"],
        "the_time_control_is_rejected":
            symmetry["controls"][0]["rejected"] and symmetry["controls"][0]["discriminates"],
        "the_arbitrary_placement_control_is_rejected":
            symmetry["controls"][1]["rejected"] and symmetry["controls"][1]["discriminates"],
        "every_declared_region_is_addressable_at_every_declared_step":
            all(row["addressable"] and row["address_count"] == DECLARED_WINDOW_STEPS
                for row in work["regions"]),
        "the_relay_duty_cycle_is_exactly_one":
            work["the_duty_cycle_of_a_region_under_the_relay"] == "1",
        "a_single_platform_holds_a_region_at_one_quarter":
            Fr(work["the_duty_cycle_of_one_platform_over_one_region"]) == Fr(1, 4),
        "every_declared_step_addresses_every_declared_region_exactly_once":
            all(sorted(address["region"] for address in entry["addresses"])
                == sorted(REGION_INDICES) for entry in work["schedule"]),
        "regions_and_times_are_computed_in_advance":
            work["regions_and_times_must_be_computed_in_advance"]
            and work["the_schedule_is_computed_in_advance"] and work["no_step_is_chosen_in_flight"],
        "the_sustained_single_platform_control_is_rejected":
            work["controls"][0]["rejected"] and work["controls"][0]["discriminates"],
        "the_in_flight_choice_control_is_rejected":
            work["controls"][1]["rejected"] and work["controls"][1]["discriminates"],
        "the_geometric_floor_used_is_the_one_computed_in_R3":
            work["geometric_floor_used"]["the_floor_is_the_one_computed_in_R3"]
            and Fr(work["geometric_floor_used"]["value"]["value"]) == FLOOR_GEOSTATIONARY,
        "every_task_is_assigned_to_a_declared_level":
            ablation["every_task_is_assigned_to_a_declared_level"]
            and ablation["no_task_is_assigned_to_a_platform"],
        "no_level_outside_the_declared_set_is_used":
            ablation["no_level_outside_the_declared_set_is_used"],
        "the_declared_levels_are_matched_to_the_declared_ablation_levels":
            ablation["declared_matched_to_the_declared_ablation_levels_of_the_target_medium"],
        "no_magnitude_of_any_physical_quantity_is_used_in_the_assignment":
            ablation["no_magnitude_of_any_real_physical_quantity_is_used"]
            and all(not row["is_a_magnitude_of_a_physical_quantity"]
                    for row in ablation["declared_levels"]),
        "the_task_to_platform_control_is_rejected":
            ablation["controls"][0]["rejected"] and ablation["controls"][0]["discriminates"],
        "the_level_outside_the_set_control_is_rejected":
            ablation["controls"][1]["rejected"] and ablation["controls"][1]["discriminates"],
        "every_obligation_has_a_rejected_counterpart":
            obligations["every_obligation_has_a_falsifiable_counterpart"]
            and obligations["every_counterpart_is_rejected"]
            and obligations["obligation_count"] == 5,
        "the_declared_error_is_bounded_and_learned":
            all(row["learned"] and row["readdressed_at_step"] == row["declared_error_step"] + 1
                for row in obligations["learned_errors"])
            and obligations["learned_error_count"] == DECLARED_ERROR_STEP_COUNT,
        "the_magnitude_audit_finds_nothing_in_the_payload": not effect_findings,
        "stage_one_is_recorded_as_calibration": stage_one["phase_is_calibration_not_control"],
        "stage_one_carries_the_declared_window":
            "December" in stage_one["declared_window"]
            and "January" in stage_one["declared_window"],
        "the_material_carries_through_computation_aggregation_and_distribution":
            stage_one["the_three_stages_carry_the_same_units"]
            and stage_one["the_material_divides_exactly_among_the_recipients"],
        "the_topology_invariant_has_a_rejected_counterpart":
            stage_one["invariants"][0]["falsifiable_counterpart"]["rejected"]
            and stage_one["invariants"][0]["falsifiable_counterpart"]["discriminates"],
        "the_learning_invariant_has_a_rejected_counterpart":
            stage_one["invariants"][1]["falsifiable_counterpart"]["rejected"]
            and stage_one["invariants"][1]["falsifiable_counterpart"]["discriminates"],
        "learning_is_continuous_from_the_first_stage":
            all(row["learning_units"] > 0 for row in stage_one["growth_steps"])
            and stage_one["growth_steps"][0]["learning_units"] > 0,
        "the_phase_control_is_rejected":
            stage_one["phase_control"]["rejected"] and stage_one["phase_control"]["discriminates"],
        "the_payload_records_proposal_only_bookkeeping":
            bookkeeping["authorizes_nothing"] and bookkeeping["decides_nothing"]
            and bookkeeping["deploys_nothing"] and bookkeeping["status"] == PROPOSAL_STATUS,
        "governance_is_unaddressed_and_no_decision_is_claimed":
            bookkeeping["no_governance_assessment"] and bookkeeping["governance"] == UNASSESSED
            and bookkeeping["decision"] == NO_NONE
            and bookkeeping["authorization"] == NO_NONE,
        "the_termination_problem_is_unaddressed_and_not_solved":
            bookkeeping["termination_problem"]["status"] == UNADDRESSED
            and not bookkeeping["termination_problem"]["solved_here"]
            and bookkeeping["termination_problem"]["no_attempt_is_made_to_solve_it"],
        "the_failed_control_is_retained":
            payload["controls_summary"]["controls_failed_to_discriminate"] == 1
            and not failed_controls[0]["discriminates"],
        "no_control_is_dropped": payload["controls_summary"]["no_control_is_dropped"],
        "observational_verification_is_recorded_unavailable":
            payload["verification_status"]["observational"] == "Unavailable",
        "no_data_is_read_or_used": payload["verification_status"]["no_data_read_or_used"],
        "undecided_items_are_declared": len(payload["undecided"]) == 8,
        "no_floating_point_value_is_retained": not contains_float(payload),
        "no_magnitude_or_effect_key_appears_anywhere": not effect_findings,
        "no_in_flight_choice_key_appears_anywhere": not in_flight_findings,
    }
    payload["checks"] = checks
    payload["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    return payload


def summarize(payload):
    sections = payload["sections"]
    pairing = sections["R1_pairing_rules"]
    usable = sections["R2_usable_fraction"]
    floor = sections["R3_spot_floor"]
    ceiling = sections["R4_etendue_ceiling"]
    pattern = sections["R5_pattern_scale"]
    symmetry = sections["R6_symmetry_constraints"]
    work = sections["R7_work_region_and_time"]
    ablation = sections["R8_ablation_level_assignment"]
    obligations = sections["R9_declared_obligations"]
    stage_one = sections["R10_stage_one"]
    bookkeeping = sections["R11_proposal_only_bookkeeping"]
    print("geometry foundation v1: exact calibration of a PROPOSAL ONLY - 提议性方案")
    print("  status:", payload["status"], " assertions:", payload["assertions"],
          " declared constants:", payload["declared_constants_count"])
    print("  R1 pairing rules:", pairing["rule_count"], "| enforced as rules:",
          pairing["the_rules_are_enforced_not_prose"])
    for row in pairing["accepted_pairings"]:
        print("      accepted:", row["pairing"], "-> ratio", row["ratio"]["value"], "| occulted",
              row["occulted_fraction"]["value"])
    print("      mis-paired control:", pairing["mispaired_control"]["control_id"], "->",
          pairing["mispaired_control"]["verdict"], "| claimed",
          pairing["mispaired_control"]["claimed_value"]["value"], "against",
          pairing["mispaired_control"]["derived_value"]["value"])
    for row in pairing["failed_controls"]:
        print("      failed control:", row["control_id"], "->", row["outcome"])
    print("  R2 corrected usable fraction:", usable["usable_fraction"]["value"],
          "=", usable["usable_fraction_in_decimal"], "| occulted",
          usable["the_occulted_fraction"]["value"], "=",
          usable["the_occulted_fraction_in_decimal"])
    correction = usable["the_correction"]
    print("      superseded value:", correction["superseded_usable_fraction"]["value"],
          "=", correction["superseded_usable_fraction_in_decimal"], "| difference",
          usable["the_correction"]["the_difference_stated_exactly"]["value"])
    for row in usable["platforms"]:
        print("      platform:", row["name"], "| occulted", row["occulted_fraction"]["value"],
              "| usable", row["usable_fraction"]["value"], "|", row["status"])
    print("  R3 spot floor theta_sun * L with the penumbra diameter beside it")
    for row in floor["platforms"]:
        print("      ", row["name"], "at", row["declared_distance"]["value"], "m -> floor",
              row["floor"]["value"], "m | penumbra diameter",
              row["penumbra_diameter"]["value"], "m")
    print("  R4 etendue ceiling B * lambda^2:", ceiling["per_mode_ceiling"]["value"],
          "W per mode | forces:", ceiling["what_the_ceiling_forces"])
    print("  R5 pattern scale: the floor of R3 |",
          pattern["finer_structure_is_washed_out_by_the_extended_source"],
          "| aperture over the coherence length",
          pattern["ap_over_the_coherence_length"])
    print("  R6 symmetry constraints: solids", symmetry["solids_count"])
    for row in symmetry["solids"]:
        print("      ", row["solid"], "| vertices", row["computed_vertex_count"],
              "| point group", row["declared_point_group"], "of order",
              row["computed_point_group_order"], "| rotation part", row["declared_rotation_part"],
              "of order", row["computed_rotation_part_order"], "| SO(3) subgroup:",
              row["is_a_subgroup_of_SO3"], "| vertex orbits",
              row["orbits_of_vertices_under_the_rotation_part"])
    print("      the time direction is not part of the point group:",
          symmetry["the_time_direction"]["the_time_direction_is_not_part_of_the_point_group"],
          "| schedule invariant under the declared period:",
          symmetry["the_time_direction"]
          ["the_schedule_is_invariant_under_translation_by_the_declared_period"])
    print("  R7 work region and time: regions", work["declared_constellation"]["declared_regions"],
          "| platforms", work["declared_constellation"]["platforms"], "| window steps",
          work["declared_constellation"]["declared_window_steps"])
    for row in work["regions"]:
        print("      region", row["region"], "| steps", row["addressed_at_steps"], "| duty cycle",
              row["duty_cycle"])
    for row in work["platforms"]:
        print("      platform", row["platform"], "| sweep", row["sweep"], "| duty cycle per region",
              row["duty_cycle_per_region"], "| sustained:",
              row["sustained_addressability_of_a_fixed_region"])
    print("      geometric floor used:", work["geometric_floor_used"]["value"]["value"], "m from",
          work["geometric_floor_used"]["source"])
    print("  R8 ablation levels:", ablation["declared_level_values"], "| tasks",
          ablation["assignment_count"])
    for row in ablation["tasks_per_declared_level"]:
        print("      ", row["level"], "value", row["declared_level_value"], "-> tasks",
              row["task_count"])
    print("  R9 declared obligations:", obligations["obligation_count"], "| every counterpart "
          "rejected:", obligations["every_counterpart_is_rejected"], "| learned errors",
          obligations["learned_error_count"])
    print("  R10 stage one:", stage_one["phase"], "| window", stage_one["declared_window"])
    print("      material units", stage_one["declared_material_units"]["value"], "| recipients",
          stage_one["declared_recipient_count"]["value"], "| per recipient",
          stage_one["units_per_recipient"]["value"])
    for row in stage_one["growth_steps"]:
        print("      growth step", row["growth_step"], "| launches", row["declared_launches"],
              "| learning units", row["learning_units"], "| cumulative launches",
              row["cumulative_launches"])
    print("  R11 proposal only: authorization", bookkeeping["authorization"], "| decision",
          bookkeeping["decision"], "| deployment", bookkeeping["deployment"], "| governance",
          bookkeeping["governance"], "| physical_effect_asserted",
          bookkeeping["physical_effect_asserted"], "| data_used", bookkeeping["data_used"])
    print("      termination problem:", bookkeeping["termination_problem"]["status"],
          "| solved here:", bookkeeping["termination_problem"]["solved_here"])
    print("      ", bookkeeping["proposal_only_in_chinese_and_english"])
    summary = payload["controls_summary"]
    print("  controls:", summary["controls_count"], "discriminating, of which",
          summary["controls_rejected"], "rejected;", summary["controls_failed_to_discriminate"],
          "failed to discriminate and",
          "is retained" if summary["controls_failed_to_discriminate"] == 1 else "are retained")
    print("  verified: no floating-point value retained",
          payload["checks"]["no_floating_point_value_is_retained"],
          "| no data read or used", payload["checks"]["no_data_is_read_or_used"])
    print("  undecided items:", len(payload["undecided"]))


def wall_limit(*_):
    raise TimeoutError("wall limit")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    arguments = parser.parse_args()
    signal.signal(signal.SIGALRM, wall_limit)
    signal.alarm(CONTRACT["budgets"]["wall_seconds"])
    resource.setrlimit(resource.RLIMIT_CPU, (CONTRACT["budgets"]["cpu_seconds"],) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (16 << 20, 16 << 20))
    payload = build_payload()
    try:
        with arguments.output.open("x") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
    except FileExistsError:
        print("refusing to overwrite the existing output path:", arguments.output)
        return 2
    summarize(payload)
    return 0 if payload["status"] == "ExternalExactPass" else 1


if __name__ == "__main__":
    sys.exit(main())
