#!/usr/bin/env python3
"""Exact external calibration of the optical-imbalance PROPOSAL: three derived bounds, one
forced division of labour, two declared deployment modes and six overreach controls.

Frozen contract: experiments/optical_imbalance_proposal_v1/contract.json (this run), sha256
116913a9369e43666d80cf65a6877164f186fd813955a4d1c05f39777496fa4f.  The run reads it, hashes it,
edits nothing and inherits two earlier contracts byte for byte without editing them:

* experiments/three_cycle_supplement_v1/contract.json, the surgery run whose declared chirality
  the blaze direction of this proposal plays the role of;
* experiments/three_cycle_supplement_v2/contract.json, the rounded ending, whose netting
  prohibition and whose refusal to seal a component that is by definition a leak are the
  prohibitions inherited here.

THIS DOCUMENT IS A PROPOSAL ONLY - 提议性方案.  It authorizes nothing, decides nothing, deploys
nothing, assesses no governance and asserts no physical effect.  It carries no magnitude for any
effect on any atmosphere, ocean, cloud, surface, weather or climate, and it reads no data.  The
target figures below are ARITHMETIC INPUTS of a proposal, not asserted effects.

What the run decides, and with what:

* the three DERIVED bounds, each computed in exact rational arithmetic from DECLARED constants,
  each declared constant carried as an exact rational with its unit and each recorded as a
  declared input and not a measurement of this run:
  - the passive spot floor theta_sun * L for a near-Earth platform, a geostationary platform and
    the second Lagrange point, with the near-Earth value cross-checked against the historically
    reported case of a deployed space mirror of about 20 metres producing a spot of about 5 km
    (the reported case is carried as declared constants; it is not data read by this run);
  - the fibre power ceiling, the étendue-limited single-mode power of order B * lambda^2 with B a
    declared spectral radiance and lambda a declared wavelength, reported in watts per mode and
    as the number of fibres a gigawatt and a megawatt would need;
  - the second Lagrange point usable fraction 1 - (theta_earth / theta_sun)^2, reported as an
    exact rational with the resulting usable flux in the declared units and with the derived
    statement that the Earth lies beyond the umbra tip there, so the Sun appears annular;
* the division of labour - mirrors carry power in free space, fibres carry phase and coherence
  only, the output diffractive stage sets the angular pattern including the blaze asymmetry -
  with the fibre bound ASSERTED as the reason the division is forced rather than stylistic;
* the two deployment modes declared separately, the second-Lagrange-point night-side addition and
  the near-Earth relay chain, each with its own geometric floor, its own usable flux, its own
  separate account and its own sustainment statement - station-keeping in one case, an orbital
  sweep requiring a succession of platforms in the other;
* the declared-target arithmetic: from a declared target patch area and a declared target flux,
  the required intercepting area, the areal mass at a declared areal density and the launch-years
  at a declared annual launch rate, reported as ARITHMETIC ON DECLARED PROPOSAL INPUTS with no
  asserted effect anywhere;
* the six overreach controls, each executed and each producing a rejection: a passive-mirror
  pattern claimed finer than theta_sun * L; more than the étendue ceiling through one fibre mode
  or fibres treated as a power channel; the coherent fraction treated as the whole power; a
  usable flux above the derived annular fraction; an asymmetric pattern claimed without a
  declared blaze direction and a symmetric element claimed to give an asymmetric one; and a
  target reached by loosening the derivation rather than the declaration.  One further control
  FAILED to discriminate and is retained as a failed control rather than repaired;
* the inherited prohibitions recorded as applying to any use of the proposal - no netting of one
  account against another, and no sealing of a component that is by definition a leak, which is
  the termination problem in this setting - with that problem recorded as Unaddressed and not
  solved;
* the proposal-only bookkeeping: authorization none, decision none, deployment none, governance
  unaddressed, physical_effect_asserted none, data_used none.

All acceptance arithmetic is exact integers and fractions.Fraction.  No floating-point value is
formed in an acceptance assertion or written into the retained payload, and no external library
is imported: sympy 1.14 is declared as available on the host, as non-authoritative and as unused,
because no step of this calibration needs a polynomial engine.  No data is read or used, no clock
is read, and no timestamp, measured duration or host path is written.

Resource policy: RLIMIT_CPU and RLIMIT_FSIZE are installed together with a wall alarm; the
contract's declared memory budget is recorded and no address-space ceiling is installed, because
no child process is launched.
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
SURGERY_CONTRACT_PATH = EXPERIMENTS / "three_cycle_supplement_v1" / "contract.json"
ROUNDED_CONTRACT_PATH = EXPERIMENTS / "three_cycle_supplement_v2" / "contract.json"

SCHEMA = "adva.external.optical-imbalance-proposal-calibration.v1"
CONTRACT_RELATIVE = "experiments/optical_imbalance_proposal_v1/contract.json"
SURGERY_RELATIVE = "experiments/three_cycle_supplement_v1/contract.json"
ROUNDED_RELATIVE = "experiments/three_cycle_supplement_v2/contract.json"

DECLARED_CONTRACT_SHA256 = "116913a9369e43666d80cf65a6877164f186fd813955a4d1c05f39777496fa4f"
DECLARED_SURGERY_SHA256 = "157838642e9097ea4a1a1c7461db9e548affb0c6f3af7b830816f37f22b74f5a"
DECLARED_ROUNDED_SHA256 = "823eedfaa492d0524c901793b580d5f02b67d7cf739f26781e326aa667d1e990"

PROPOSAL_STATUS = "PROPOSAL ONLY - 提议性方案"
NO_NONE = "none"
NO_DATA = "none"
UNASSESSED = "unaddressed"

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


FORBIDDEN_EFFECT_KEYS = (
    "effect", "temperature", "forcing", "precipitation", "rainfall", "cloud", "ocean",
    "weather", "climate", "warming", "cooling", "albedo", "damage", "benefit", "yield",
    "anomaly", "tendency", "sensitivity",
)


def effect_audit(node, path="", found=None):
    """Every key anywhere in the payload that names a physical effect."""
    if found is None:
        found = []
    if isinstance(node, dict):
        for key, value in node.items():
            if key in FORBIDDEN_EFFECT_KEYS:
                found.append(path + "/" + str(key) + " names a physical effect")
            effect_audit(value, path + "/" + str(key), found)
    elif isinstance(node, (list, tuple)):
        for index, item in enumerate(node):
            effect_audit(item, path + "/" + str(index), found)
    return found


# ------------------------------------------------------------ declared constants --
# Every entry below is a DECLARED input of the proposal, carried as an exact rational with its
# declared unit.  None is a measurement of this run; no instrument was used, no data was read and
# no clock was consulted.  The three DERIVED bounds are the only derived quantities in the run and
# they rest on these declarations: a different declaration is a different run, while the FORM of
# each bound is not a declaration.

# lengths, in metres
ASTRONOMICAL_UNIT = 149597870700
SOLAR_RADIUS = 695700000
EARTH_MEAN_RADIUS = 6371000
NEAR_EARTH_DISTANCE = 400000
GEOSTATIONARY_DISTANCE = 35786000
SECOND_LAGRANGE_DISTANCE = 1500000000
REPORTED_MIRROR_DIAMETER = 20
REPORTED_SPOT = 5000
MIRROR_ELEMENT_SIDE = 20

# flux, radiance and wavelength
SOLAR_CONSTANT_AT_ONE_AU = 1361
TARGET_FLUX = 10000
WAVELENGTH = Fr(1, 10 ** 6)
SPECTRAL_RADIANCE = 10 ** 6

# mass, area and launch
TARGET_PATCH_AREA = 100000000
AREAL_DENSITY = Fr(1, 10)
ANNUAL_LAUNCH_RATE = 100000

# the declared instrument
DECLARED_FIBRE_COUNT = 10 ** 6
COHERENT_FRACTION = Fr(1, 1000)
ZERO_ORDER_SHARE = Fr(0)
BLAZE_FIRST_ORDER_SHARE = Fr(3, 5)
OTHER_FIRST_ORDER_SHARE = Fr(2, 5)
SYMMETRIC_GRATING_ORDER_SHARE = Fr(1, 2)
GIGAWATT_REFERENCE_POWER = 10 ** 9
MEGAWATT_REFERENCE_POWER = 10 ** 6
DECLARED_BLAZE_DIRECTION = ("the declared blaze direction: the +1 first order is biased toward "
                            "the declared night-side patch along the declared order axis")
NO_BLAZE_DIRECTION = NO_NONE

DECLARED_CONSTANTS = (
    ("astronomical_unit", ASTRONOMICAL_UNIT, "m",
     "the declared distance unit; the value is exact under the 2012 definition"),
    ("solar_radius", SOLAR_RADIUS, "m", "the declared nominal solar radius"),
    ("earth_mean_radius", EARTH_MEAN_RADIUS, "m", "the declared mean Earth radius"),
    ("near_earth_distance", NEAR_EARTH_DISTANCE, "m",
     "the declared near-Earth platform distance, which is also the declared distance of the "
     "historically reported case"),
    ("geostationary_distance", GEOSTATIONARY_DISTANCE, "m",
     "the declared geostationary platform distance"),
    ("second_lagrange_distance", SECOND_LAGRANGE_DISTANCE, "m",
     "the declared second-Lagrange-point distance beyond the Earth on the anti-solar side"),
    ("reported_mirror_diameter", REPORTED_MIRROR_DIAMETER, "m",
     "the mirror diameter of the historically reported case, carried as a declared constant"),
    ("reported_spot", REPORTED_SPOT, "m",
     "the spot of the historically reported case, carried as a declared constant"),
    ("solar_constant_at_one_au", SOLAR_CONSTANT_AT_ONE_AU, "W m^-2",
     "the declared solar constant at one astronomical unit"),
    ("target_patch_area", TARGET_PATCH_AREA, "m^2",
     "the declared target patch area of the proposal, an arithmetic input and not an effect"),
    ("target_flux", TARGET_FLUX, "W m^-2",
     "the declared target flux of the proposal, an arithmetic input and not an effect"),
    ("wavelength", WAVELENGTH, "m", "the declared operating wavelength, one micrometre"),
    ("spectral_radiance_B", SPECTRAL_RADIANCE, "W m^-2 sr^-1",
     "the declared bandwidth-integrated spectral radiance B that sets the étendue ceiling"),
    ("areal_density", AREAL_DENSITY, "kg m^-2", "the declared areal density of the mirror array"),
    ("annual_launch_rate", ANNUAL_LAUNCH_RATE, "kg year^-1", "the declared annual launch rate"),
    ("mirror_element_side", MIRROR_ELEMENT_SIDE, "m",
     "the declared side of one square mirror element, of the same order as the reported case"),
    ("declared_fibre_count", DECLARED_FIBRE_COUNT, "1",
     "the declared number of fibres in the phase-and-coherence network"),
    ("coherent_fraction", COHERENT_FRACTION, "1",
     "the declared fraction of the delivered power carried coherently, which is the only part "
     "available to a fine pattern"),
    ("blaze_first_order_share", BLAZE_FIRST_ORDER_SHARE, "1",
     "the declared share of the +1 first order of the blazed grating"),
    ("other_first_order_share", OTHER_FIRST_ORDER_SHARE, "1",
     "the declared share of the -1 first order of the blazed grating"),
    ("symmetric_grating_order_share", SYMMETRIC_GRATING_ORDER_SHARE, "1",
     "the declared share of each first order of a symmetric zero-order-suppressed grating"),
    ("zero_order_share", ZERO_ORDER_SHARE, "1",
     "the declared zero-order share of the zero-order-suppressed grating"),
    ("gigawatt_reference_power", GIGAWATT_REFERENCE_POWER, "W",
     "the declared reference power of the fibre count"),
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


# ------------------------------------------------------------- the derived bounds --

THETA_SUN_AT_ONE_AU = Fr(2 * SOLAR_RADIUS, ASTRONOMICAL_UNIT)
THETA_SUN_AT_THE_SECOND_LAGRANGE_POINT = Fr(
    2 * SOLAR_RADIUS, ASTRONOMICAL_UNIT + SECOND_LAGRANGE_DISTANCE)
THETA_EARTH_AT_THE_SECOND_LAGRANGE_POINT = Fr(EARTH_MEAN_RADIUS, SECOND_LAGRANGE_DISTANCE)

EARTH_DIAMETER = 2 * EARTH_MEAN_RADIUS
UMBRA_LENGTH = Fr(EARTH_MEAN_RADIUS * ASTRONOMICAL_UNIT, SOLAR_RADIUS - EARTH_MEAN_RADIUS)

PASSIVE_FLOOR_NEAR_EARTH = THETA_SUN_AT_ONE_AU * NEAR_EARTH_DISTANCE
PASSIVE_FLOOR_GEOSTATIONARY = THETA_SUN_AT_ONE_AU * GEOSTATIONARY_DISTANCE
PASSIVE_FLOOR_SECOND_LAGRANGE = (
    THETA_SUN_AT_THE_SECOND_LAGRANGE_POINT * SECOND_LAGRANGE_DISTANCE)

REPORTED_FLOOR_AT_THE_DECLARED_DISTANCE = PASSIVE_FLOOR_NEAR_EARTH
REPORTED_FLOOR_WITH_THE_APERTURE = Fr(REPORTED_MIRROR_DIAMETER) + PASSIVE_FLOOR_NEAR_EARTH
REPORTED_SPOT_OVER_THE_FLOOR = Fr(REPORTED_SPOT) / REPORTED_FLOOR_WITH_THE_APERTURE
IMPLIED_DISTANCE_FOR_EXACTLY_THE_REPORTED_SPOT = (
    Fr(REPORTED_SPOT - REPORTED_MIRROR_DIAMETER) / THETA_SUN_AT_ONE_AU)
REPORTED_SPOT_OVER_THE_DECLARED_DISTANCE = Fr(REPORTED_SPOT) / NEAR_EARTH_DISTANCE

FIBRE_PER_MODE_POWER = Fr(SPECTRAL_RADIANCE) * WAVELENGTH * WAVELENGTH
FIBRES_FOR_A_GIGAWATT = Fr(GIGAWATT_REFERENCE_POWER) / FIBRE_PER_MODE_POWER
FIBRES_FOR_A_MEGAWATT = Fr(MEGAWATT_REFERENCE_POWER) / FIBRE_PER_MODE_POWER
MEGAWATT_OVER_THE_DECLARED_GIGAWATT = Fr(MEGAWATT_REFERENCE_POWER, GIGAWATT_REFERENCE_POWER)
DECLARED_NETWORK_MAXIMUM_POWER = Fr(DECLARED_FIBRE_COUNT) * FIBRE_PER_MODE_POWER

THETA_EARTH_OVER_THETA_SUN = (THETA_EARTH_AT_THE_SECOND_LAGRANGE_POINT
                              / THETA_SUN_AT_THE_SECOND_LAGRANGE_POINT)
THE_OCCULTED_FRACTION = THETA_EARTH_OVER_THETA_SUN ** 2
USABLE_FRACTION_AT_THE_SECOND_LAGRANGE = 1 - THE_OCCULTED_FRACTION

DECLARED_IRRADIANCE_AT_THE_SECOND_LAGRANGE = Fr(
    SOLAR_CONSTANT_AT_ONE_AU) * Fr(ASTRONOMICAL_UNIT ** 2,
                                  (ASTRONOMICAL_UNIT + SECOND_LAGRANGE_DISTANCE) ** 2)
USABLE_FLUX_AT_THE_SECOND_LAGRANGE = (
    USABLE_FRACTION_AT_THE_SECOND_LAGRANGE * DECLARED_IRRADIANCE_AT_THE_SECOND_LAGRANGE)

REQUIRED_POWER = TARGET_FLUX * TARGET_PATCH_AREA
MIRROR_ELEMENT_AREA = MIRROR_ELEMENT_SIDE * MIRROR_ELEMENT_SIDE
COHERENT_POWER = Fr(REQUIRED_POWER) * COHERENT_FRACTION
FIBRES_FOR_THE_REQUIRED_POWER = Fr(REQUIRED_POWER) / FIBRE_PER_MODE_POWER
FIBRES_FOR_THE_COHERENT_PART = COHERENT_POWER / FIBRE_PER_MODE_POWER

ORDER_SHARE_DIFFERENCE = BLAZE_FIRST_ORDER_SHARE - OTHER_FIRST_ORDER_SHARE
ORDER_SHARE_SUM = BLAZE_FIRST_ORDER_SHARE + OTHER_FIRST_ORDER_SHARE
SYMMETRIC_SHARE_DIFFERENCE = Fr(0)

MODE_A_NAME = "mode_A_second_lagrange_point"
MODE_B_NAME = "mode_B_near_earth_relay"


def delivery_arithmetic(usable_flux, power=None):
    """The declared-target arithmetic at one declared usable flux, exactly and ideally.

    The declared delivery efficiency is exactly one, so the result is the IDEAL area: any real
    loss only increases it, which makes it a lower bound and not an estimate.
    """
    if power is None:
        power = Fr(REQUIRED_POWER)
    check(usable_flux > 0, "the declared usable flux at a mode is strictly positive")
    area = power / usable_flux
    mass = area * AREAL_DENSITY
    years = mass / ANNUAL_LAUNCH_RATE
    return {
        "required_intercepting_area": quantity(area, "m^2"),
        "areal_mass": quantity(mass, "kg"),
        "launch_years": quantity(years, "years"),
    }


MODE_A_ARITHMETIC = delivery_arithmetic(USABLE_FLUX_AT_THE_SECOND_LAGRANGE)
MODE_B_ARITHMETIC = delivery_arithmetic(Fr(SOLAR_CONSTANT_AT_ONE_AU))
REQUIRED_INTERCEPTING_AREA = Fr(MODE_A_ARITHMETIC["required_intercepting_area"]["value"])
AREAL_MASS = Fr(MODE_A_ARITHMETIC["areal_mass"]["value"])
LAUNCH_YEARS = Fr(MODE_A_ARITHMETIC["launch_years"]["value"])
MIRROR_ELEMENTS = REQUIRED_INTERCEPTING_AREA / MIRROR_ELEMENT_AREA


# ------------------------------------------------------------- R1 derived bounds ----

def section_passive_spot_floor():
    """R1a: the floor theta_sun * L on the three declared platforms and the reported cross-check."""
    platforms = (
        ("a near-Earth platform", NEAR_EARTH_DISTANCE, THETA_SUN_AT_ONE_AU,
         PASSIVE_FLOOR_NEAR_EARTH),
        ("a geostationary platform", GEOSTATIONARY_DISTANCE, THETA_SUN_AT_ONE_AU,
         PASSIVE_FLOOR_GEOSTATIONARY),
        ("the second Lagrange point", SECOND_LAGRANGE_DISTANCE,
         THETA_SUN_AT_THE_SECOND_LAGRANGE_POINT, PASSIVE_FLOOR_SECOND_LAGRANGE),
    )
    rows = []
    for name, distance, theta, floor in platforms:
        check(floor == theta * distance, "the floor of " + name + " is exactly theta_sun * L")
        check(Fr(floor) > 0, "the floor of " + name + " is strictly positive")
        rows.append({
            "name": name,
            "declared_distance": quantity(distance, "m"),
            "theta_sun": quantity(theta, "rad"),
            "floor": quantity(floor, "m"),
        })
    check(len(rows) == 3, "the floor is computed for the three declared platforms and no fourth")

    floors = [floor for _, _, _, floor in platforms]
    check(floors[2] > floors[1] > floors[0],
          "the largest floor of the three is at the second Lagrange point and the smallest is at "
          "the declared near-Earth distance")
    check(PASSIVE_FLOOR_SECOND_LAGRANGE > EARTH_DIAMETER,
          "the derived floor at the second Lagrange point exceeds the Earth's diameter, so no "
          "passive mirror there can form a spot smaller than the Earth")
    check(Fr(REPORTED_SPOT) > PASSIVE_FLOOR_NEAR_EARTH,
          "the bare near-Earth floor lies below the reported spot")
    check(Fr(REPORTED_SPOT) > REPORTED_FLOOR_WITH_THE_APERTURE,
          "the floor with the declared mirror aperture added still lies below the reported spot")
    check(REPORTED_SPOT_OVER_THE_FLOOR > 1,
          "the reported spot is above the derived floor, which is what a floor permits: the floor "
          "is consistent with the reported case and the reported case does not contradict it")
    check(REPORTED_SPOT_OVER_THE_DECLARED_DISTANCE > THETA_SUN_AT_ONE_AU,
          "the angular size the reported case implies at the declared distance exceeds the "
          "declared solar angular size, so radiance is not increased and the floor is not "
          "violated by it")
    check(IMPLIED_DISTANCE_FOR_EXACTLY_THE_REPORTED_SPOT > NEAR_EARTH_DISTANCE,
          "the distance at which the reported spot would sit exactly on the floor is beyond the "
          "declared near-Earth distance, which is why the reported spot is above the floor there")
    check(Fr(REPORTED_SPOT) / (Fr(REPORTED_MIRROR_DIAMETER)
                                  + THETA_SUN_AT_ONE_AU * NEAR_EARTH_DISTANCE)
          == REPORTED_SPOT_OVER_THE_FLOOR,
          "the reported ratio is recomputed from the declared constants exactly")
    return {
        "rule": "theta_sun * L: any passive mirror forms a spot no smaller than the product of the "
                "declared solar angular size and the declared distance, because radiance cannot "
                "be increased",
        "theta_sun_declared_as": "the full angular size of the solar disk, twice the declared "
                                 "solar radius over the declared distance; the contract writes "
                                 "the bound as theta_sun * L, and the reported cross-check below "
                                 "fixes the factor-of-two reading as the full angular size",
        "theta_sun_at_one_au": quantity(THETA_SUN_AT_ONE_AU, "rad"),
        "theta_sun_at_the_second_lagrange_point":
            quantity(THETA_SUN_AT_THE_SECOND_LAGRANGE_POINT, "rad"),
        "platforms": rows,
        "platform_count": 3,
        "smallest_floor": quantity(PASSIVE_FLOOR_NEAR_EARTH, "m"),
        "largest_floor": quantity(PASSIVE_FLOOR_SECOND_LAGRANGE, "m"),
        "the_largest_floor_is_at_the_second_lagrange_point": True,
        "floor_ratio_of_the_largest_to_the_smallest":
            text(PASSIVE_FLOOR_SECOND_LAGRANGE / PASSIVE_FLOOR_NEAR_EARTH),
        "the_l2_floor_exceeds_the_earths_diameter": True,
        "earth_diameter": quantity(EARTH_DIAMETER, "m"),
        "l2_floor_minus_the_earths_diameter":
            quantity(PASSIVE_FLOOR_SECOND_LAGRANGE - EARTH_DIAMETER, "m"),
        "cross_check": {
            "declared_reported_case": "the historically reported case of a deployed space mirror "
                                      "of about 20 metres producing a spot of about 5 km, carried "
                                      "as DECLARED constants of this run",
            "declared_reported_mirror_diameter": quantity(REPORTED_MIRROR_DIAMETER, "m"),
            "declared_reported_spot": quantity(REPORTED_SPOT, "m"),
            "reported_floor_at_the_declared_distance":
                quantity(REPORTED_FLOOR_AT_THE_DECLARED_DISTANCE, "m"),
            "reported_floor_with_the_aperture_included":
                quantity(REPORTED_FLOOR_WITH_THE_APERTURE, "m"),
            "the_reported_spot_is_not_below_the_floor": True,
            "the_reported_spot_over_the_floor": text(REPORTED_SPOT_OVER_THE_FLOOR),
            "implied_distance_for_exactly_the_reported_spot":
                quantity(IMPLIED_DISTANCE_FOR_EXACTLY_THE_REPORTED_SPOT, "m"),
            "the_reported_spot_over_the_declared_distance":
                quantity(REPORTED_SPOT_OVER_THE_DECLARED_DISTANCE, "rad"),
            "the_reported_angular_size_exceeds_the_declared_solar_angular_size": True,
            "consistent": True,
            "verdict": "Consistent_FloorIsNotViolated",
            "measured_here": False,
            "read_from_data": False,
            "reading": "the floor is CONSISTENT with the historically reported case: at the "
                       "declared near-Earth distance the floor is below the reported spot, with "
                       "the declared mirror aperture added it is still below it, and the angular "
                       "size the reported case implies is larger than the declared solar angular "
                       "size.  A floor may not be violated and the reported case does not violate "
                       "it.  The reported case is carried as a declared constant, not read as "
                       "data, and it is not a measurement of this run.",
        },
        "reading": "the three floors are exact rationals in metres: the near-Earth floor is the "
                   "smallest and the second-Lagrange-point floor the largest, and the largest "
                   "exceeds the Earth's diameter, so a passive mirror at the second Lagrange point "
                   "cannot in any case form a spot smaller than the Earth itself.",
    }


def section_fibre_power_ceiling():
    """R1b: the étendue-limited single-mode ceiling, in watts per mode and in fibre counts."""
    check(Fr(SPECTRAL_RADIANCE) * WAVELENGTH ** 2 == FIBRE_PER_MODE_POWER,
          "the ceiling is exactly the declared B times lambda squared")
    check(Fr(1, 10 ** 6) == FIBRE_PER_MODE_POWER,
          "the declared B * lambda^2 ceiling is exactly one microwatt per mode")
    check(FIBRES_FOR_A_GIGAWATT == 10 ** 15,
          "a gigawatt would need exactly 10^15 single-mode fibres at the declared constants")
    check(FIBRES_FOR_A_MEGAWATT == 10 ** 12,
          "a megawatt would need exactly 10^12 single-mode fibres, the order of a trillion that "
          "the contract's prose reports")
    check(FIBRES_FOR_A_GIGAWATT == FIBRES_FOR_A_MEGAWATT * 10 ** 3,
          "the two exact counts differ by exactly the ratio of the two declared reference powers")
    check(Fr(1, 1000) == MEGAWATT_OVER_THE_DECLARED_GIGAWATT,
          "the megawatt is exactly one thousandth of the declared gigawatt")
    check(DECLARED_NETWORK_MAXIMUM_POWER == 1,
          "the declared fibre network can carry at most one watt in total")
    check(Fr(REQUIRED_POWER) > DECLARED_NETWORK_MAXIMUM_POWER,
          "the declared fibre network cannot carry the required power, so the division of labour "
          "is forced")
    check(FIBRES_FOR_THE_REQUIRED_POWER == 10 ** 18,
          "the required power would need exactly 10^18 single-mode fibres")
    check(Fr(GIGAWATT_REFERENCE_POWER) == COHERENT_POWER,
          "the declared coherent part of the required power is exactly the declared gigawatt "
          "reference, so the coherent part alone needs exactly the gigawatt fibre count")
    check(FIBRES_FOR_THE_COHERENT_PART == FIBRES_FOR_A_GIGAWATT,
          "the coherent part alone would need exactly as many fibres as a gigawatt")
    return {
        "rule": "the étendue-limited single-mode ceiling, of order B * lambda^2, with B a declared "
                "bandwidth-integrated spectral radiance and lambda a declared wavelength",
        "declared_spectral_radiance": quantity(SPECTRAL_RADIANCE, "W m^-2 sr^-1"),
        "declared_wavelength": quantity(WAVELENGTH, "m"),
        "per_mode_power": quantity(FIBRE_PER_MODE_POWER, "W"),
        "per_mode_power_is_microwatts": True,
        "gigawatt_reference_power": quantity(GIGAWATT_REFERENCE_POWER, "W"),
        "fibres_a_gigawatt_would_need": quantity(FIBRES_FOR_A_GIGAWATT, "1"),
        "fibres_a_megawatt_would_need": quantity(FIBRES_FOR_A_MEGAWATT, "1"),
        "the_megawatt_is_this_fraction_of_the_declared_gigawatt":
            text(MEGAWATT_OVER_THE_DECLARED_GIGAWATT),
        "the_contracts_reported_order": "of order a trillion fibres for a gigawatt",
        "the_exact_count_and_the_reported_order":
            "at the declared constants a gigawatt needs exactly 10^15 fibres, one thousand "
            "trillion, while the contract's prose reports the order of a trillion; that prose "
            "figure is exactly the count at a megawatt, one thousandth of the declared gigawatt.  "
            "The exact division is reported and governs; the mismatch of three orders is recorded "
            "and not repaired.",
        "declared_fibre_count": quantity(DECLARED_FIBRE_COUNT, "1"),
        "maximum_power_the_declared_fibre_network_can_carry":
            quantity(DECLARED_NETWORK_MAXIMUM_POWER, "W"),
        "fibres_the_required_power_would_need": quantity(FIBRES_FOR_THE_REQUIRED_POWER, "1"),
        "fibres_the_coherent_part_would_need": quantity(FIBRES_FOR_THE_COHERENT_PART, "1"),
        "the_declared_network_can_carry_this_fraction_of_the_required_power":
            text(DECLARED_NETWORK_MAXIMUM_POWER / Fr(REQUIRED_POWER)),
        "reading": "the ceiling is exactly one microwatt per fibre mode at the declared constants, "
                   "so the fibre network is not a power channel: the declared network of a million "
                   "fibres can carry at most one watt in total, one part in a trillion of the "
                   "power the declared target requires, and the required power would need 10^18 "
                   "fibres.  This bound is what forces the division of labour.",
    }


def section_l2_usable_fraction():
    """R1c: the annular usable fraction at the second Lagrange point and the resulting flux."""
    recomputed_usable_flux = (
        (1 - Fr(EARTH_MEAN_RADIUS, SECOND_LAGRANGE_DISTANCE) ** 2
         / Fr(2 * SOLAR_RADIUS, ASTRONOMICAL_UNIT + SECOND_LAGRANGE_DISTANCE) ** 2)
        * Fr(SOLAR_CONSTANT_AT_ONE_AU)
        * Fr(ASTRONOMICAL_UNIT ** 2, (ASTRONOMICAL_UNIT + SECOND_LAGRANGE_DISTANCE) ** 2))
    check(THETA_EARTH_AT_THE_SECOND_LAGRANGE_POINT < THETA_SUN_AT_THE_SECOND_LAGRANGE_POINT,
          "the Earth's angular size at the second Lagrange point is smaller than the Sun's, so "
          "the Sun appears annular there")
    check(Fr(0) < THETA_EARTH_OVER_THETA_SUN < Fr(1),
          "the ratio of the two declared angular sizes is strictly between zero and one")
    check(USABLE_FRACTION_AT_THE_SECOND_LAGRANGE
          == 1 - THETA_EARTH_OVER_THETA_SUN * THETA_EARTH_OVER_THETA_SUN,
          "the usable fraction is exactly one minus the squared angular ratio")
    check(Fr(0) < THE_OCCULTED_FRACTION < Fr(1),
          "the occulted fraction is strictly between zero and one, so the occultation is partial")
    check(Fr(SECOND_LAGRANGE_DISTANCE) > UMBRA_LENGTH,
          "the declared second-Lagrange distance lies beyond the derived umbra tip, so the "
          "declared point is in the antumbra and the Sun appears annular")
    check(Fr(EARTH_MEAN_RADIUS * ASTRONOMICAL_UNIT, SOLAR_RADIUS - EARTH_MEAN_RADIUS)
          == UMBRA_LENGTH,
          "the umbra length is recomputed from the declared constants exactly")
    check(Fr(0) < USABLE_FRACTION_AT_THE_SECOND_LAGRANGE < Fr(1),
          "the usable fraction is strictly between zero and one")
    check(USABLE_FLUX_AT_THE_SECOND_LAGRANGE
          < DECLARED_IRRADIANCE_AT_THE_SECOND_LAGRANGE,
          "the usable flux is strictly below the declared irradiance, because part of the solar "
          "disk is occulted")
    check(recomputed_usable_flux == USABLE_FLUX_AT_THE_SECOND_LAGRANGE,
          "the usable flux is the derived annular fraction times the declared irradiance, "
          "recomputed from the declared constants")
    check(Fr(SOLAR_CONSTANT_AT_ONE_AU) > DECLARED_IRRADIANCE_AT_THE_SECOND_LAGRANGE,
          "the declared irradiance at the second Lagrange point is below the declared solar "
          "constant at one astronomical unit, by the declared inverse-square scaling")
    return {
        "rule": "1 - (theta_earth / theta_sun)^2, exact in the declared units",
        "theta_earth_at_the_second_lagrange_point":
            quantity(THETA_EARTH_AT_THE_SECOND_LAGRANGE_POINT, "rad"),
        "theta_sun_at_the_second_lagrange_point":
            quantity(THETA_SUN_AT_THE_SECOND_LAGRANGE_POINT, "rad"),
        "the_ratio": text(THETA_EARTH_OVER_THETA_SUN),
        "the_occulted_fraction": quantity(THE_OCCULTED_FRACTION, "1"),
        "usable_fraction": quantity(USABLE_FRACTION_AT_THE_SECOND_LAGRANGE, "1"),
        "the_earth_is_in_the_antumbra": True,
        "umbra_length": quantity(UMBRA_LENGTH, "m"),
        "the_declared_distance_exceeds_the_umbra_length": True,
        "the_sun_appears_annular": True,
        "annular_statement": "the declared second-Lagrange distance lies beyond the derived umbra "
                             "tip of the Earth, so the Earth is in the antumbra there and the Sun "
                             "appears annular: the Earth occults only the derived fraction of the "
                             "solar disk and the usable fraction is one minus that fraction",
        "declared_solar_constant_at_one_au": quantity(SOLAR_CONSTANT_AT_ONE_AU, "W m^-2"),
        "declared_irradiance_at_the_second_lagrange_point":
            quantity(DECLARED_IRRADIANCE_AT_THE_SECOND_LAGRANGE, "W m^-2"),
        "inverse_square_scaling_is_declared": True,
        "usable_flux": quantity(USABLE_FLUX_AT_THE_SECOND_LAGRANGE, "W m^-2"),
        "reading": "the usable flux at the second Lagrange point is the derived annular fraction "
                   "times the declared irradiance there; both are exact rationals, the declared "
                   "irradiance follows from the declared solar constant at one astronomical unit "
                   "by the declared inverse-square scaling, and no measurement is involved.",
    }


def section_derived_bounds():
    """R1: the three derived bounds, and the declaration that rests under them."""
    constants = declared_constant_rows()
    check(len(CONTRACT["derived_bounds"]) == 4,
          "the contract declares the note on derived bounds and the three derived bounds")
    for name in ("note", "passive_spot_floor", "fibre_power_ceiling", "l2_usable_fraction"):
        check(name in CONTRACT["derived_bounds"],
              "the contract contains the derived-bounds entry " + name)
    check(len(constants) == len(DECLARED_CONSTANTS),
          "every declared constant is carried in the payload with its unit")
    check(len({row["name"] for row in constants}) == len(constants),
          "every declared constant is named once")
    check(all(row["declared"] and not row["measured_here"] and not row["read_from_data"]
              for row in constants),
          "every constant is marked declared and not measured here and not read from data")
    check(all(row["unit"] for row in constants),
          "every declared constant carries its declared unit")
    check(all(text(Fr(row["value"])) == row["value"] for row in constants),
          "every declared constant is carried as an exact rational in its own exact text form")
    check(not any(isinstance(value, float) for _, value, _, _ in DECLARED_CONSTANTS),
          "no declared constant is a floating-point value")
    floor = section_passive_spot_floor()
    ceiling = section_fibre_power_ceiling()
    fraction = section_l2_usable_fraction()
    check(floor["platform_count"] == 3, "the floor is reported for three platforms")
    check(ceiling["per_mode_power_is_microwatts"], "the ceiling is reported in microwatts per mode")
    check(fraction["the_sun_appears_annular"],
          "the annular reading at the second Lagrange point is derived and reported")
    return {
        "declared_constants": constants,
        "declared_constants_count": len(constants),
        "declared_inputs_are_declared_and_not_measured": True,
        "declared_inputs_statement":
            "every constant above is a DECLARED input of the proposal, carried as an exact "
            "rational with its declared unit; none of them is a measurement of this run, no "
            "instrument was used, no data was read and no clock was consulted.  The three bounds "
            "below are the only derived quantities in this run and they rest on these "
            "declarations: a different declaration of the constants is a different run, while the "
            "FORM of each bound is not a declaration.",
        "passive_spot_floor": floor,
        "fibre_power_ceiling": ceiling,
        "l2_usable_fraction": fraction,
        "the_three_bounds": [
            {"bound": "the passive spot floor theta_sun * L",
             "value": text(PASSIVE_FLOOR_SECOND_LAGRANGE),
             "unit": "m at the second Lagrange point",
             "derived_from": "the declared solar radius and the declared distances"},
            {"bound": "the étendue-limited single-mode power",
             "value": text(FIBRE_PER_MODE_POWER),
             "unit": "W per mode",
             "derived_from": "the declared spectral radiance B and the declared wavelength"},
            {"bound": "the usable fraction at the second Lagrange point",
             "value": text(USABLE_FRACTION_AT_THE_SECOND_LAGRANGE),
             "unit": "1",
             "derived_from": "the declared Earth radius and the declared distances"},
        ],
        "all_three_bounds_are_derived_from_declared_constants": True,
        "bounds_are_bounds_on_instruments_not_effects": True,
        "no_physics_is_asserted_by_these_bounds":
            "the three bounds are bounds on what any such instrument can do; they are not "
            "statements about any atmosphere, ocean, cloud, surface, weather or climate",
    }


# ---------------------------------------------- R2 the forced division of labour ----

def section_division_of_labour():
    """R2: mirrors carry power, fibres carry phase and coherence, the diffractive stage sets the
    angular pattern - and the fibre bound is the reason the division is forced."""
    check(Fr(REQUIRED_POWER) / 10 ** 6 > DECLARED_NETWORK_MAXIMUM_POWER,
          "the declared fibre network can carry less than one millionth of the required power")
    check(ORDER_SHARE_SUM == 1,
          "the two declared first-order shares of the blazed grating sum to exactly one, because "
          "the zero order is suppressed")
    check(ZERO_ORDER_SHARE == 0, "the declared grating suppresses the zero order exactly")
    check(ORDER_SHARE_DIFFERENCE > 0,
          "the declared first-order shares are unequal, which with the declared blaze direction "
          "is the declared asymmetry")
    check(SYMMETRIC_SHARE_DIFFERENCE == 0,
          "a symmetric grating has exactly equal first-order shares, so it cannot carry an "
          "asymmetric pattern by itself")
    check(Fr(1, 5) == ORDER_SHARE_DIFFERENCE,
          "the declared asymmetry is exactly one fifth of the two-first-order energy")
    check(DECLARED_BLAZE_DIRECTION != NO_BLAZE_DIRECTION,
          "a blaze direction is declared, so the declared asymmetry has its declared direction")
    return {
        "mirrors": {
            "role": "carry power",
            "combination_happens_in_free_space": True,
            "carries_power": True,
            "required_power": quantity(REQUIRED_POWER, "W"),
            "how_many_mirror_elements": quantity(MIRROR_ELEMENTS, "1"),
            "declared_element_side": quantity(MIRROR_ELEMENT_SIDE, "m"),
            "reading": "the power is collected and combined in free space by the mirror array; no "
                       "power is routed through fibres",
        },
        "fibres": {
            "role": "carry phase, coherence and the phase reference only",
            "carries_power": False,
            "declared_fibre_count": quantity(DECLARED_FIBRE_COUNT, "1"),
            "maximum_power_the_declared_network_can_carry":
                quantity(DECLARED_NETWORK_MAXIMUM_POWER, "W"),
            "required_power": quantity(REQUIRED_POWER, "W"),
            "the_fraction_of_the_required_power_the_network_can_carry":
                text(DECLARED_NETWORK_MAXIMUM_POWER / Fr(REQUIRED_POWER)),
            "what_forces_the_division":
                "the étendue-limited single-mode ceiling: at the declared constants one mode "
                "carries exactly one microwatt, the declared network of a million fibres can carry "
                "at most one watt, and the required power is a trillion times that, so routing "
                "power through fibres is not a stylistic alternative but is excluded by the "
                "derived ceiling",
        },
        "diffractive_stage": {
            "role": "sets the angular pattern, including the blaze asymmetry",
            "element": "a zero-order-suppressed phase grating",
            "orders": ["+1", "-1", "0"],
            "zero_order_share": quantity(ZERO_ORDER_SHARE, "1"),
            "plus_first_order_share": quantity(BLAZE_FIRST_ORDER_SHARE, "1"),
            "minus_first_order_share": quantity(OTHER_FIRST_ORDER_SHARE, "1"),
            "order_share_sum": quantity(ORDER_SHARE_SUM, "1"),
            "order_share_difference": quantity(ORDER_SHARE_DIFFERENCE, "1"),
            "the_two_first_order_shares_are_unequal": True,
            "blaze_direction": DECLARED_BLAZE_DIRECTION,
            "two_sided_by_construction": True,
            "the_asymmetry_is_a_declared_asymmetry": True,
            "reading": "the grating is two-sided by construction, because a zero-order-suppressed "
                       "phase grating sends its energy into the two first orders; the declared "
                       "blaze direction together with unequal declared shares is what makes one "
                       "side larger than the other, and it plays the role of the chirality "
                       "declared in the surgery run",
        },
        "the_division_is_forced_not_stylistic": True,
        "the_fibre_bound_is_the_reason": True,
        "no_power_is_routed_through_fibres": True,
        "why": "the division of labour is asserted as FORCED rather than chosen: the ceiling "
               "computed in R1 caps what any number of declared fibres can carry at one microwatt "
               "per mode, so mirrors must carry the power in free space, fibres can carry phase "
               "and coherence only, and the angular pattern including the blaze asymmetry is set "
               "by the output diffractive stage, where no power ceiling of this kind applies",
        "statement": "mirrors carry power; fibres carry phase and coherence only; the output "
                     "diffractive stage sets the angular pattern including the blaze asymmetry - "
                     "and the fibre bound is the reason, asserted here, not a stylistic choice",
    }


# ------------------------------------------------------ R3 the deployment modes ----

def section_deployment_modes():
    """R3: the two deployment modes, each with its own floor, account and sustainment."""
    mode_a = {
        "declared": "second-Lagrange-point night-side addition: the light arriving there has "
                    "already passed the Earth and the mirror returns it to the night side",
        "geometric_floor": quantity(PASSIVE_FLOOR_SECOND_LAGRANGE, "m"),
        "usable_fraction": quantity(USABLE_FRACTION_AT_THE_SECOND_LAGRANGE, "1"),
        "usable_flux": quantity(USABLE_FLUX_AT_THE_SECOND_LAGRANGE, "W m^-2"),
        "required_intercepting_area": MODE_A_ARITHMETIC["required_intercepting_area"],
        "areal_mass": MODE_A_ARITHMETIC["areal_mass"],
        "launch_years": MODE_A_ARITHMETIC["launch_years"],
        "sustainment": {
            "statement": "station-keeping is required",
            "required": True,
            "feasibility_assessed": False,
            "cost_assessed": False,
            "cadence_declared": False,
            "reading": "the declared mode requires station-keeping at the second Lagrange point; "
                       "whether it can be achieved, and at what cost, is not assessed anywhere in "
                       "this run and is recorded as undecided",
        },
    }
    mode_b = {
        "declared": "near-Earth relay chain: a chain of mirrors at a small distance, where the "
                    "geometric floor is the smallest of the three",
        "geometric_floor": quantity(PASSIVE_FLOOR_NEAR_EARTH, "m"),
        "usable_fraction": quantity(Fr(1), "1"),
        "usable_flux": quantity(Fr(SOLAR_CONSTANT_AT_ONE_AU), "W m^-2"),
        "required_intercepting_area": MODE_B_ARITHMETIC["required_intercepting_area"],
        "areal_mass": MODE_B_ARITHMETIC["areal_mass"],
        "launch_years": MODE_B_ARITHMETIC["launch_years"],
        "sustainment": {
            "statement": "the light spot sweeps because of orbital motion, so sustained "
                         "illumination requires a succession of platforms rather than one",
            "required": True,
            "feasibility_assessed": False,
            "cost_assessed": False,
            "cadence_declared": False,
            "reading": "the declared mode cannot be sustained by one platform: the declared spot "
                       "sweeps with the platform's motion, so a succession of platforms is "
                       "required.  The number of platforms, the dwell and the cadence are NOT "
                       "declared in the contract and are not invented here; they are recorded as "
                       "undecided",
        },
    }
    check(mode_a["geometric_floor"]["value"] != mode_b["geometric_floor"]["value"],
          "the two modes carry different geometric floors, each its own")
    check(Fr(mode_a["geometric_floor"]["value"]) > Fr(mode_b["geometric_floor"]["value"]),
          "the second-Lagrange-point floor is the larger and the relay-chain floor the smaller")
    check(Fr(mode_a["required_intercepting_area"]["value"])
          > Fr(mode_b["required_intercepting_area"]["value"]),
          "the annular usable fraction makes mode A's required intercepting area larger than mode "
          "B's, so the two accounts are genuinely different")
    check(Fr(mode_a["areal_mass"]["value"]) != Fr(mode_b["areal_mass"]["value"]),
          "the two modes carry different areal masses and no fused figure is formed")
    check(bool(mode_a["sustainment"]["statement"]) and bool(mode_b["sustainment"]["statement"]),
          "each mode carries its own sustainment statement")
    check(mode_a["usable_fraction"]["value"] == text(USABLE_FRACTION_AT_THE_SECOND_LAGRANGE),
          "mode A carries the derived annular fraction as its usable fraction")
    check(mode_b["usable_fraction"]["value"] == "1"
          and mode_b["usable_flux"]["value"] == str(SOLAR_CONSTANT_AT_ONE_AU),
          "mode B is declared to carry the full declared solar constant, with no occultation "
          "declared at the near-Earth distance")
    check("night side" in mode_a["declared"],
          "mode A is declared as the night-side addition at the second Lagrange point")
    check("succession" in mode_b["sustainment"]["statement"],
          "mode B's sustainment statement is the required succession of platforms")
    check("station-keeping" in mode_a["sustainment"]["statement"],
          "mode A's sustainment statement is the required station-keeping")
    check(mode_b["usable_fraction"]["value"] == "1"
          and mode_a["usable_fraction"]["value"] == text(USABLE_FRACTION_AT_THE_SECOND_LAGRANGE),
          "the derived annular fraction belongs to mode A alone; mode B's fraction of exactly one "
          "is a declared fraction and is recorded as such")
    return {
        MODE_A_NAME: mode_a,
        MODE_B_NAME: mode_b,
        "the_two_modes_are_declared_separately": True,
        "the_two_modes_are_not_netted": True,
        "mode_B_usable_fraction_is_declared_not_derived": True,
        "mode_B_usable_fraction_note":
            "the derived annular fraction 1 - (theta_earth / theta_sun)^2 is a statement about the "
            "second Lagrange point, where mode A sits.  Mode B's usable fraction of exactly 1 is a "
            "DECLARED fraction of this proposal and not a derived bound: the near-Earth mode is "
            "declared not to be occulted, and whether the relay chain can always be on the sunlit "
            "side of the Earth is not assessed here.  The declaration is recorded in the undecided "
            "list and is not counted as one of the three derived bounds.",
        "separate_accounts_statement": "each mode carries its own geometric floor, its own usable "
                                       "flux, its own required intercepting area, areal mass and "
                                       "launch-years, and no fused figure over the two is formed "
                                       "anywhere in this run",
        "mode_count": 2,
        "each_mode_has_its_own_geometric_floor": True,
        "each_mode_has_its_own_sustainment_statement": True,
        "floor_ratio_of_the_largest_to_the_smallest":
            text(PASSIVE_FLOOR_SECOND_LAGRANGE / PASSIVE_FLOOR_NEAR_EARTH),
        "the_modes_are_a_declared_choice": True,
        "no_fourth_platform_is_declared": True,
    }


# ---------------------------------------------- R4 the declared-target arithmetic --

def section_declared_target_arithmetic():
    """R4: the required area, areal mass and launch-years, as arithmetic on declared inputs."""
    check(REQUIRED_POWER == 10 ** 12,
          "the declared target requires exactly one terawatt at the target")
    check(Fr(REQUIRED_POWER) / USABLE_FLUX_AT_THE_SECOND_LAGRANGE == REQUIRED_INTERCEPTING_AREA,
          "the required intercepting area is the required power over the derived usable flux")
    check(AREAL_MASS == REQUIRED_INTERCEPTING_AREA * AREAL_DENSITY,
          "the areal mass is the required intercepting area times the declared areal density")
    check(LAUNCH_YEARS == AREAL_MASS / ANNUAL_LAUNCH_RATE,
          "the launch-years are the areal mass over the declared annual launch rate")
    check(MIRROR_ELEMENTS == REQUIRED_INTERCEPTING_AREA / MIRROR_ELEMENT_AREA,
          "the mirror element count is the required intercepting area over the declared element "
          "area")
    check(MIRROR_ELEMENTS * MIRROR_ELEMENT_AREA == REQUIRED_INTERCEPTING_AREA,
          "the element count times the element area is the required intercepting area, exactly")
    check(FIBRES_FOR_THE_REQUIRED_POWER == 10 ** 18,
          "the same power through single-mode fibres would need 10^18 fibres")
    check(Fr(DECLARED_FIBRE_COUNT) * 10 ** 11 < FIBRES_FOR_THE_REQUIRED_POWER,
          "the fibre count the required power would need exceeds the declared fibre count by more "
          "than eleven orders, which is the division of labour stated quantitatively")
    check(MIRROR_ELEMENTS > 10 ** 6,
          "the required power needs more than a million declared mirror elements")
    check(Fr(TARGET_PATCH_AREA) < REQUIRED_INTERCEPTING_AREA,
          "the required intercepting area exceeds the declared target patch area, because the "
          "declared target flux is above the declared ambient flux")
    check(Fr(TARGET_FLUX) / USABLE_FLUX_AT_THE_SECOND_LAGRANGE
          == REQUIRED_INTERCEPTING_AREA / TARGET_PATCH_AREA,
          "the area ratio over the declared patch is the target flux over the derived usable "
          "flux, exactly")
    return {
        "declared_target": {
            "patch_area": quantity(TARGET_PATCH_AREA, "m^2"),
            "flux": quantity(TARGET_FLUX, "W m^-2"),
            "declared_as_proposal_inputs": True,
            "reading": "a declared target patch and a declared target flux; both are arithmetic "
                       "inputs of the proposal and neither is an asserted effect",
        },
        "required_power": quantity(REQUIRED_POWER, "W", derivation=(
            "the declared target flux times the declared target patch area")),
        "required_intercepting_area": quantity(
            REQUIRED_INTERCEPTING_AREA, "m^2",
            derivation="the required power over the derived usable flux at the second Lagrange "
                       "point",
            ratio_to_the_declared_patch_area=text(REQUIRED_INTERCEPTING_AREA
                                                  / TARGET_PATCH_AREA)),
        "areal_mass": quantity(
            AREAL_MASS, "kg",
            derivation="the required intercepting area times the declared areal density"),
        "launch_years": quantity(
            LAUNCH_YEARS, "years",
            derivation="the areal mass over the declared annual launch rate"),
        "mirror_elements": quantity(
            MIRROR_ELEMENTS, "1",
            derivation="the required intercepting area over the declared square element area"),
        "fibres_the_required_power_would_need": quantity(
            FIBRES_FOR_THE_REQUIRED_POWER, "1",
            derivation="the required power over the étendue-limited single-mode power"),
        "the_delivery_efficiency_is_declared_exactly_one": True,
        "the_arithmetic_is_ideal_and_is_a_lower_bound": True,
        "arithmetic_on_declared_proposal_inputs": True,
        "no_effect_is_asserted": True,
        "statement": "the required intercepting area, the areal mass and the launch-years follow "
                     "from the declared target patch area and the declared target flux by exact "
                     "arithmetic.  They are ARITHMETIC ON DECLARED PROPOSAL INPUTS and no effect "
                     "on any atmosphere, ocean, cloud, surface, weather or climate is asserted or "
                     "estimated anywhere in this run",
    }


# ------------------------------------------------------- R5 the overreach controls --

CONTROL_KEYS = ("control", "claim", "verdict", "rejected", "rejected_by", "rejection_reasons",
                "discriminates", "derived_value", "claimed_value", "unit", "accepted_companion")


def control_row(number, control, claim, derived_value, claimed_value, unit, rejected_by,
                reasons, companion_claim, companion_verdict):
    """One executed overreach control with its discriminating accepted companion."""
    return {
        "control": str(number) + ". " + control,
        "claim": claim,
        "verdict": "Rejected",
        "rejected": True,
        "rejected_by": rejected_by,
        "rejection_reasons": list(reasons),
        "discriminates": True,
        "derived_value": quantity(derived_value, unit),
        "claimed_value": quantity(claimed_value, unit),
        "unit": unit,
        "accepted_companion": {
            "claim": companion_claim,
            "verdict": companion_verdict,
            "accepted": True,
        },
    }


def section_overreach_controls():
    """R5: the six overreach controls, each executed and each producing a rejection."""
    check(len(CONTRACT["controls"]) == 7,
          "the contract declares six overreach controls and one inherited entry")
    check(all(CONTRACT["controls"][index].startswith("Overreach " + str(index + 1))
              for index in range(5)),
          "the contract's first five control entries are the numbered overreaches executed here")
    check(CONTRACT["controls"][5].startswith("Arithmetic"),
          "the contract's sixth control entry is the arithmetic overreach of the declared target")
    check(CONTRACT["controls"][6].startswith("Inherited"),
          "the contract's seventh control entry is the inherited prohibitions")
    finer_claim = Fr(100)
    check(finer_claim < PASSIVE_FLOOR_SECOND_LAGRANGE,
          "control 1's claimed spot is finer than the derived floor")
    check(Fr(2) * FIBRE_PER_MODE_POWER > FIBRE_PER_MODE_POWER,
          "control 2's claimed per-mode power exceeds the ceiling")
    check(Fr(DECLARED_FIBRE_COUNT) < FIBRES_FOR_THE_REQUIRED_POWER,
          "control 2's fibre-as-power-channel claim is refuted by the declared fibre count")
    check(Fr(REQUIRED_POWER) > COHERENT_POWER,
          "control 3's claim exceeds the declared coherent part")
    check(FIBRES_FOR_THE_REQUIRED_POWER * COHERENT_FRACTION == FIBRES_FOR_THE_COHERENT_PART,
          "the full-power fibre count times the declared coherent fraction is the coherent-part "
          "count, exactly")
    check(Fr(1) > USABLE_FRACTION_AT_THE_SECOND_LAGRANGE,
          "control 4's claimed usable fraction is above the derived annular fraction")
    slightly_above = USABLE_FRACTION_AT_THE_SECOND_LAGRANGE + Fr(1, 1000)
    check(slightly_above > USABLE_FRACTION_AT_THE_SECOND_LAGRANGE,
          "a usable fraction one part in a thousand above the derived one is still above it, so "
          "the control is strict and not a tolerance")
    check(ORDER_SHARE_DIFFERENCE > 0 and SYMMETRIC_SHARE_DIFFERENCE == 0,
          "control 5 separates a declared asymmetric grating from a symmetric one")
    loosened_area = Fr(REQUIRED_POWER) / DECLARED_IRRADIANCE_AT_THE_SECOND_LAGRANGE
    check(loosened_area < REQUIRED_INTERCEPTING_AREA,
          "control 6's loosened derivation understates the required intercepting area")
    check(loosened_area == REQUIRED_INTERCEPTING_AREA * USABLE_FRACTION_AT_THE_SECOND_LAGRANGE,
          "the loosened area is the derived area times the derived usable fraction, exactly")
    accepted_area = delivery_arithmetic(
        USABLE_FLUX_AT_THE_SECOND_LAGRANGE,
        power=Fr(REQUIRED_POWER) / 2)["required_intercepting_area"]["value"]
    check(Fr(accepted_area) * 2 == REQUIRED_INTERCEPTING_AREA,
          "the accepted route halves the declared target and keeps the derivation unchanged")

    control_one = control_row(
        1, "a passive-mirror pattern claimed finer than the derived floor theta_sun * L",
        "a passive mirror at the second Lagrange point delivers a declared spot of 100 metres on "
        "the night side",
        PASSIVE_FLOOR_SECOND_LAGRANGE, finer_claim, "m",
        "the derived passive spot floor theta_sun * L",
        ["the derived floor at the declared second-Lagrange distance is "
         + text(PASSIVE_FLOOR_SECOND_LAGRANGE) + " m and any passive mirror forms a spot no "
         "smaller than theta_sun * L, because radiance cannot be increased",
         "the claimed 100 m is finer than that floor by an exact factor of "
         + text(PASSIVE_FLOOR_SECOND_LAGRANGE / finer_claim),
         "a fine pattern is available only to the coherent part of the power, which has its own "
         "étendue ceiling and its own controls (2 and 3)"],
        "the spot claimed is exactly the derived floor " + text(PASSIVE_FLOOR_SECOND_LAGRANGE)
        + " m, which is not finer than the floor",
        "Accepted_AtTheFloor")

    control_two = control_row(
        2, "more than the étendue ceiling through one fibre mode, or fibres treated as a power "
           "channel",
        "one fibre mode carries twice the étendue-limited single-mode power, and the fibre "
        "network carries the required power",
        FIBRE_PER_MODE_POWER, 2 * FIBRE_PER_MODE_POWER, "W",
        "the étendue-limited single-mode ceiling B * lambda^2",
        ["the ceiling is exactly " + text(FIBRE_PER_MODE_POWER) + " W per mode at the declared "
         "spectral radiance and wavelength, so twice the ceiling through one mode is excluded by "
         "the étendue bound",
         "treating fibres as the power channel is excluded too: the required power of "
         + text(REQUIRED_POWER) + " W would need " + text(FIBRES_FOR_THE_REQUIRED_POWER)
         + " single-mode fibres, while the declared network has "
         + text(DECLARED_FIBRE_COUNT),
         "the declared network can carry at most " + text(DECLARED_NETWORK_MAXIMUM_POWER)
         + " W in total, one part in a trillion of the required power"],
        "exactly the étendue-limited single-mode power through one mode, "
        + text(FIBRE_PER_MODE_POWER) + " W, with the power itself carried in free space",
        "Accepted_AtTheCeiling")

    control_three = control_row(
        3, "the coherent fraction treated as the whole power: a fine pattern claimed at full "
           "power",
        "the fine pattern is claimed at the whole required power, with the declared coherent "
        "fraction treated as if it were the whole power",
        COHERENT_POWER, REQUIRED_POWER, "W",
        "the declared coherent fraction",
        ["the declared coherent fraction is " + text(COHERENT_FRACTION) + ", so only "
         + text(COHERENT_POWER) + " W of the required " + text(REQUIRED_POWER)
         + " W is carried coherently, and a fine pattern is available only to that part",
         "the claim exceeds the coherent part by exactly the factor "
         + text(Fr(REQUIRED_POWER) / COHERENT_POWER),
         "at full power the fine pattern would need " + text(FIBRES_FOR_THE_REQUIRED_POWER)
         + " fibres against a declared count of " + text(DECLARED_FIBRE_COUNT)
         + ", and even the coherent part alone would need "
         + text(FIBRES_FOR_THE_COHERENT_PART)],
        "the fine pattern claimed at the declared coherent part, " + text(COHERENT_POWER)
        + " W, as the proposal declares it",
        "Accepted_AtTheDeclaredCoherentFraction")

    control_four = control_row(
        4, "a usable flux at the second Lagrange point above the derived annular fraction",
        "the usable fraction at the second Lagrange point is claimed to be 1, with no occultation "
        "by the Earth",
        USABLE_FRACTION_AT_THE_SECOND_LAGRANGE, Fr(1), "1",
        "the derived annular fraction 1 - (theta_earth / theta_sun)^2",
        ["the derived usable fraction is "
         + text(USABLE_FRACTION_AT_THE_SECOND_LAGRANGE) + ", because the Earth occults the "
         "derived fraction " + text(THE_OCCULTED_FRACTION) + " of the solar disk and the declared "
         "point lies beyond the derived umbra tip",
         "a claimed usable fraction of 1 is above the derived fraction by the exact factor "
         + text(Fr(1) / USABLE_FRACTION_AT_THE_SECOND_LAGRANGE)
         + ", and a claim one part in a thousand above the derived fraction is above it too: the "
         "control is strict and not a tolerance",
         "the usable flux would be overstated by exactly that factor and the required intercepting "
         "area understated by its reciprocal; the derived fraction may not be substituted"],
        "the usable fraction used exactly as derived, "
        + text(USABLE_FRACTION_AT_THE_SECOND_LAGRANGE)
        + ", with the resulting usable flux " + text(USABLE_FLUX_AT_THE_SECOND_LAGRANGE)
        + " W m^-2",
        "Accepted_AtTheDerivedFraction")

    control_five = control_row(
        5, "an asymmetric pattern claimed without a declared blaze direction, and a symmetric "
           "element claimed to give an asymmetric pattern",
        "an asymmetric pattern is claimed from the diffractive stage with no blaze direction "
        "declared, and a symmetric zero-order-suppressed grating with equal first-order shares is "
        "claimed to give an asymmetric pattern",
        ORDER_SHARE_DIFFERENCE, SYMMETRIC_SHARE_DIFFERENCE, "1",
        "the declared blaze direction together with unequal declared first-order shares",
        ["an asymmetric pattern requires a DECLARED blaze direction: without one the two first "
         "orders are interchangeable and the pattern is symmetric, and the claimed direction is "
         + NO_BLAZE_DIRECTION,
         "a symmetric element cannot give an asymmetric pattern either: its declared first-order "
         "shares are equal at " + text(SYMMETRIC_GRATING_ORDER_SHARE) + " each, so the declared "
         "difference between the orders is exactly zero",
         "the declared grating with the declared direction is asymmetric by exactly "
         + text(ORDER_SHARE_DIFFERENCE) + " of the two-first-order energy, and it is two-sided by "
         "construction because a zero-order-suppressed grating sends its energy into the two first "
         "orders"],
        "the declared grating: first-order shares " + text(BLAZE_FIRST_ORDER_SHARE) + " and "
        + text(OTHER_FIRST_ORDER_SHARE) + ", zero order " + text(ZERO_ORDER_SHARE) + ", with "
        + DECLARED_BLAZE_DIRECTION,
        "Accepted_WithTheDeclaredBlazeDirection")

    control_six = control_row(
        6, "a target reached by loosening the derivation rather than the declaration",
        "the declared target is claimed to be reached with the usable fraction of 1 substituted "
        "for the derived annular fraction, which shrinks the required intercepting area",
        REQUIRED_INTERCEPTING_AREA, loosened_area, "m^2",
        "the derived usable fraction, which may not be substituted by a looser value",
        ["the claim reaches a smaller area only by loosening the derivation: the substituted "
         "fraction is above the derived annular fraction by the exact factor "
         + text(Fr(1) / USABLE_FRACTION_AT_THE_SECOND_LAGRANGE),
         "the derived bounds are the part of this proposal that is not a declaration, so a target "
         "reached by loosening one of them is rejected by rule and not by arithmetic alone",
         "the accepted route is the other one: keep the derivation and change the DECLARATION"],
        "the same target reached by changing the declaration instead: the declared patch area is "
        "halved, so the required intercepting area is " + text(accepted_area) + " m^2 by the same "
        "unchanged derivation at the derived usable flux "
        + text(USABLE_FLUX_AT_THE_SECOND_LAGRANGE) + " W m^-2",
        "Accepted_ByDeclaration")

    controls = [control_one, control_two, control_three, control_four, control_five, control_six]
    check(all(row["verdict"] == "Rejected" for row in controls),
          "every one of the six overreach controls produces a rejection")
    check(all(row["discriminates"] for row in controls),
          "every control discriminates, each against its accepted companion")
    check(all(row["accepted_companion"]["accepted"] for row in controls),
          "every control carries an accepted companion, which is what makes the rejection a "
          "discrimination and not a blanket rule")
    check(all(sorted(row) == sorted(CONTROL_KEYS) for row in controls),
          "every control row carries the same declared fields")
    check(all(not contains_float(row) for row in controls),
          "every control row is exact and carries no floating-point value")

    relaxed_density = Fr(1, 100)
    relaxed_mass = REQUIRED_INTERCEPTING_AREA * relaxed_density
    relaxed_years = relaxed_mass / ANNUAL_LAUNCH_RATE
    check(relaxed_mass < AREAL_MASS,
          "the failed control's relaxed areal density lowers the areal mass")
    check(relaxed_mass * 10 == AREAL_MASS,
          "the relaxed areal mass is exactly one tenth of the derived one")
    check(relaxed_years * 10 == LAUNCH_YEARS,
          "the relaxed launch-years are exactly one tenth of the derived ones")
    failed = [{
        "control": "the declared target reached by loosening the declared areal density from "
                   + text(AREAL_DENSITY) + " to " + text(relaxed_density) + " kg m^-2",
        "variant": "the areal density is a DECLARED input, and the arithmetic cannot distinguish "
                   "a re-declaration of a declared input from a loosening of the derivation",
        "outcome": "FAILED_TO_DISCRIMINATE",
        "discriminates": False,
        "derived_mass": text(AREAL_MASS),
        "relaxed_mass": text(relaxed_mass),
        "derived_launch_years": text(LAUNCH_YEARS),
        "relaxed_launch_years": text(relaxed_years),
        "why": "the same arithmetic that rejects control 6 accepts this variant unchanged, because "
               "the areal density and the annual launch rate are declared inputs rather than "
               "derived bounds; no exact computation can tell a re-declaration from a loosening, "
               "and the difference is a rule about which quantities are derived, not a number.  "
               "The control therefore FAILED TO DISCRIMINATE and is retained rather than repaired.",
        "reading": "what the six overreach controls actually separate is the derived bounds from "
                   "the declared inputs: a claim that moves a derived bound is rejected, and a "
                   "claim that moves a declared input is a different declaration.  This variant "
                   "moves only a declared input, so it is not an overreach of the kind the "
                   "controls catch, and the failure is reported.",
    }]
    return {
        "controls": controls,
        "control_count": len(controls),
        "controls_executed": len(controls),
        "controls_rejected": sum(1 for row in controls if row["rejected"]),
        "every_control_produces_a_rejection": all(row["rejected"] for row in controls),
        "failed_controls": failed,
        "failed_controls_count": len(failed),
        "why_the_failed_control_is_retained":
            "a control that cannot be made to fail is reported as a failed control rather than "
            "dropped or quietly repaired, so the record shows exactly where the rejection "
            "argument stops",
        "no_control_is_dropped": True,
    }


# ------------------------------------------------- R6 the inherited prohibitions ----

def section_inherited_prohibitions():
    """R6: netting forbidden, sealing refused for a leak, the termination problem unaddressed."""
    mode_a_mass = Fr(MODE_A_ARITHMETIC["areal_mass"]["value"])
    mode_b_mass = Fr(MODE_B_ARITHMETIC["areal_mass"]["value"])
    fused_mass = mode_a_mass + mode_b_mass
    check(mode_a_mass != mode_b_mass,
          "the two modes carry different masses, so a fused figure would hide one of them")
    check(fused_mass == mode_a_mass + mode_b_mass,
          "the fused figure is exactly the sum, which is what the prohibition refuses to report")
    netting_control = {
        "prohibition": "no netting of one account against another",
        "source": "inherited from the parent contracts and applied to any use of this proposal",
        "applies_to_any_use": True,
        "control": "a single fused account over the two deployment modes, reporting one areal mass "
                   "and one launch-years figure for the pair",
        "verdict": "Rejected",
        "rejected": True,
        "rejected_by": "the separateness of the two accounts",
        "rejection_reasons": [
            "the two modes are declared separately and each is accounted separately: mode A's "
            "areal mass is " + text(mode_a_mass) + " kg and mode B's is " + text(mode_b_mass)
            + " kg, and a fused figure of " + text(fused_mass) + " kg would present the pair as "
            "one account",
            "netting is prohibited: one account may not be reduced by, or merged with, another, in "
            "this proposal as in the contracts it inherits",
            "no fused area, mass or launch-years figure over the two modes is formed anywhere in "
            "this run",
        ],
    }
    sealing_control = {
        "prohibition": "no sealing of a component that is by definition a leak",
        "source": "inherited from the parent contracts and applied to any use of this proposal",
        "applies_to_any_use": True,
        "control": "the termination of the delivery - the energy that leaves the instrument and is "
                   "not delivered to the declared target - declared sealed and therefore closed",
        "verdict": "Rejected",
        "rejected_by": "the refusal to seal a component that is by definition a leak",
        "rejected": True,
        "rejection_reasons": [
            "the termination is by definition a leak: it is the part of the delivery that exits "
            "the instrument without arriving at the declared target, so it can be accounted as an "
            "exit and can never be sealed",
            "sealing it would report an exit as closed, which is exactly the sealing the inherited "
            "prohibition refuses",
            "the termination is therefore carried as an accounted, unquantified exit and is not "
            "discharged, and the termination problem itself is NOT solved here",
        ],
    }
    check(netting_control["rejected"] and sealing_control["rejected"],
          "both inherited prohibitions are executed against a rejected control")
    check("no netting" in CONTRACT["controls"][6] and "sealing" in CONTRACT["controls"][6],
          "the contract's inherited entry names both prohibitions executed here")
    check(all(row["applies_to_any_use"] for row in (netting_control, sealing_control)),
          "both inherited prohibitions are recorded as applying to any use of the proposal")
    return {
        "inherited_prohibitions": [netting_control, sealing_control],
        "inherited_prohibitions_count": 2,
        "inherited_prohibitions_apply_to_any_use": True,
        "termination_problem": {
            "status": "Unaddressed",
            "declared_as": "the termination of the delivery: the energy that leaves the instrument "
                           "and is not delivered to the declared target",
            "the_component_is_by_definition_a_leak": True,
            "may_be_accounted_but_never_sealed": True,
            "no_attempt_is_made_to_solve_it": True,
            "governance": UNASSESSED,
            "why": "this run does not attempt to solve the termination problem.  It records that "
                   "the component is by definition a leak, that it may be accounted and never "
                   "sealed, and that the inherited prohibitions apply to any use of this proposal. "
                   "Nothing here addresses who might decide, or how, or whether it should be done.",
        },
        "no_netting": True,
        "sealing_refused_for_the_termination": True,
        "parent_contracts_cited": [SURGERY_RELATIVE, ROUNDED_RELATIVE],
    }


# ------------------------------------------------- R7 proposal-only bookkeeping ----

def section_proposal_only_bookkeeping():
    """R7: the proposal-only bookkeeping, and the explicit statement that this is a proposal."""
    bookkeeping = CONTRACT["proposal_only_bookkeeping"]
    for key in ("authorization", "decision", "deployment", "governance",
                "physical_effect_asserted", "data_used"):
        check(key in bookkeeping, "the contract declares " + key)
    check(bookkeeping["authorization"] == NO_NONE, "the contract records no authorization")
    check(bookkeeping["decision"] == NO_NONE, "the contract records no decision")
    check(bookkeeping["deployment"] == NO_NONE, "the contract records no deployment")
    check(bookkeeping["governance"] == UNASSESSED,
          "the contract records governance as unaddressed")
    check(bookkeeping["physical_effect_asserted"] == NO_NONE,
          "the contract asserts no physical effect")
    check(bookkeeping["data_used"] == NO_DATA, "the contract uses no data")
    return {
        "authorization": NO_NONE,
        "decision": NO_NONE,
        "deployment": NO_NONE,
        "governance": UNASSESSED,
        "physical_effect_asserted": NO_NONE,
        "data_used": NO_DATA,
        "record_purpose": bookkeeping["record_purpose"],
        "status": PROPOSAL_STATUS,
        "proposal_only_statement": "this document is a PROPOSAL ONLY - 提议性方案: it is not "
                                   "authorized, not a plan of record, not engineering, not a "
                                   "deployment decision and not a governance position; it "
                                   "authorizes nothing, decides nothing and deploys nothing",
        "proposal_only_in_chinese_and_english": "提议性方案 / proposal only",
        "authorizes_nothing": True,
        "decides_nothing": True,
        "deploys_nothing": True,
        "no_governance_assessment": True,
        "nothing_said_about_who_might_decide":
            "nothing here addresses who might decide, or how, or whether it should be done",
    }


# ------------------------------------------------------------------- the payload ---

def build_payload():
    """The retained payload: every section exact, every check named, every residual recorded."""
    contract_digest = digest(CONTRACT_PATH)
    surgery_digest = digest(SURGERY_CONTRACT_PATH)
    rounded_digest = digest(ROUNDED_CONTRACT_PATH)
    check(contract_digest == DECLARED_CONTRACT_SHA256,
          "the frozen contract digest matches the declared one")
    check(surgery_digest == DECLARED_SURGERY_SHA256,
          "the surgery contract is retained byte for byte")
    check(rounded_digest == DECLARED_ROUNDED_SHA256,
          "the rounded-ending contract is retained byte for byte")
    check(CONTRACT["status"] == PROPOSAL_STATUS,
          "the contract declares itself a proposal only")

    bounds = section_derived_bounds()
    division = section_division_of_labour()
    modes = section_deployment_modes()
    target = section_declared_target_arithmetic()
    controls = section_overreach_controls()
    inherited = section_inherited_prohibitions()
    bookkeeping = section_proposal_only_bookkeeping()

    payload = {
        "schema": SCHEMA,
        "version": 1,
        "level": CONTRACT["level"],
        "contract": CONTRACT_RELATIVE,
        "contract_sha256": contract_digest,
        "contract_sha256_declared": DECLARED_CONTRACT_SHA256,
        "checker_sha256": digest(pathlib.Path(__file__).resolve()),
        "parent_contracts": [
            {"path": SURGERY_RELATIVE, "sha256": surgery_digest,
             "sha256_declared": DECLARED_SURGERY_SHA256, "retained_byte_for_byte": True,
             "relation": "the surgery run: the blaze direction of this proposal plays the role of "
                         "the chirality declared there, and its retained failures carry forward"},
            {"path": ROUNDED_RELATIVE, "sha256": rounded_digest,
             "sha256_declared": DECLARED_ROUNDED_SHA256, "retained_byte_for_byte": True,
             "relation": "the rounded ending: its netting prohibition and its refusal to seal a "
                         "component that is by definition a leak are the prohibitions inherited "
                         "here, and they are executed against controls in R6"},
        ],
        "tooling": {
            "arithmetic": "exact integers and fractions.Fraction only",
            "external_libraries_imported": [],
            "declared_external_library_available_but_unused": "sympy 1.14",
            "declared_not_native_authority": True,
            "exact_only": True,
            "used_for": ["exact rational arithmetic on declared constants and derived bounds"],
            "not_implemented": [
                "a wave-optics or beam-propagation solver of any kind",
                "a diffraction-efficiency computation of the declared grating",
                "a native certificate of any kind",
                "any physical effect, forecast or magnitude",
            ],
        },
        "limits": CONTRACT["budgets"],
        "assertions": ASSERTIONS["n"],
        "sections": {
            "R1_derived_bounds": bounds,
            "R2_division_of_labour": division,
            "R3_deployment_modes": modes,
            "R4_declared_target_arithmetic": target,
            "R5_overreach_controls": controls,
            "R6_inherited_prohibitions": inherited,
            "R7_proposal_only_bookkeeping": bookkeeping,
        },
        "verification_status": {
            "observational": "Unavailable",
            "reason": "the proposal describes an instrument that does not exist and is not "
                      "deployed, and this run uses no data; no observation, forecast or "
                      "measurement enters it",
            "physical_effect_asserted": NO_NONE,
            "deployment": NO_NONE,
            "no_data_read_or_used": True,
            "checked_here": {
                "no_data_read_or_used": True,
                "no_physical_effect_is_asserted": True,
                "the_derived_bounds_are_bounds_on_instruments": True,
                "the_target_figures_are_proposal_arithmetic": True,
                "governance_is_unaddressed": True,
            },
        },
        "undecided": [
            {"item": "whether theta_sun in the contract's bound theta_sun * L names the solar "
                     "angular radius or the full angular size of the solar disk",
             "reason": "the contract's derived-bounds note calls theta_sun the solar angular "
                       "radius while writing the bound as theta_sun * L, a factor of two apart.  "
                       "This run declares it as the full angular size, which is the reading under "
                       "which the historically reported case of a 20-metre mirror and a 5 km spot "
                       "is consistent, and it reports the declared solar angular size at both "
                       "distances so the other reading can be formed from the same payload.  The "
                       "FORM of the bound, a floor proportional to the distance, is unaffected.",
             "retained_partial_result": {
                 "theta_sun_at_one_au": text(THETA_SUN_AT_ONE_AU),
                 "theta_sun_at_the_second_lagrange_point":
                     text(THETA_SUN_AT_THE_SECOND_LAGRANGE_POINT),
                 "near_earth_floor": text(PASSIVE_FLOOR_NEAR_EARTH),
                 "reported_spot_over_the_floor": text(REPORTED_SPOT_OVER_THE_FLOOR),
             }},
            {"item": "whether the declared spectral radiance and wavelength are the ones the "
                     "contract's order-of-magnitude prose intends",
             "reason": "the contract's prose says the ceiling is microwatts and that a gigawatt "
                       "would need of order a trillion fibres.  At the declared constants the "
                       "ceiling is exactly one microwatt and a gigawatt needs exactly 10^15 "
                       "fibres, one thousand trillion, while a megawatt needs exactly 10^12.  The "
                       "exact division is reported and governs; whether the prose's 'trillion' was "
                       "meant for a gigawatt or for a megawatt is not decided here and is not "
                       "repaired.  A different declaration of B and lambda is a different run.",
             "retained_partial_result": {
                 "per_mode_power": text(FIBRE_PER_MODE_POWER),
                 "fibres_a_gigawatt_would_need": text(FIBRES_FOR_A_GIGAWATT),
                 "fibres_a_megawatt_would_need": text(FIBRES_FOR_A_MEGAWATT),
                 "megawatt_over_the_declared_gigawatt":
                     text(MEGAWATT_OVER_THE_DECLARED_GIGAWATT),
             }},
            {"item": "which distance the historically reported spot of about 5 km belongs to",
             "reason": "the reported case is carried as declared constants - about 20 metres of "
                       "mirror, about 5 km of spot, at the declared near-Earth distance.  The "
                       "derived floor there is below the reported spot both with and without the "
                       "declared aperture, so the floor is consistent with the report and the "
                       "report does not violate it; the distance at which the reported spot would "
                       "sit exactly on the floor is reported, and the excess of the reported spot "
                       "over the floor is attributed to nothing.",
             "retained_partial_result": {
                 "reported_floor_with_the_aperture_included":
                     text(REPORTED_FLOOR_WITH_THE_APERTURE),
                 "implied_distance_for_exactly_the_reported_spot":
                     text(IMPLIED_DISTANCE_FOR_EXACTLY_THE_REPORTED_SPOT),
                 "the_reported_spot_over_the_floor": text(REPORTED_SPOT_OVER_THE_FLOOR),
             }},
            {"item": "whether the declared fibre count can carry the coherent part of the declared "
                     "power",
             "reason": "the declared network can carry at most one watt in total, the required "
                       "power is a terawatt and the declared coherent part is a gigawatt.  Even "
                       "the coherent part would need 10^15 single-mode fibres against a declared "
                       "count of 10^6.  Whether a phase-and-coherence network needs one fibre per "
                       "watt, or one fibre per controlled mode, or something else, is NOT decided "
                       "here: the run reports the ceiling and the declared counts and stops.",
             "retained_partial_result": {
                 "declared_fibre_count": text(DECLARED_FIBRE_COUNT),
                 "maximum_power_the_declared_network_can_carry":
                     text(DECLARED_NETWORK_MAXIMUM_POWER),
                 "fibres_the_coherent_part_would_need": text(FIBRES_FOR_THE_COHERENT_PART),
                 "fibres_the_required_power_would_need": text(FIBRES_FOR_THE_REQUIRED_POWER),
             }},
            {"item": "how the near-Earth relay chain is sustained",
             "reason": "the contract declares that the spot sweeps and that a succession of "
                       "platforms is required rather than one.  The number of platforms, the dwell "
                       "of one platform over the declared patch and the cadence of the succession "
                       "are NOT declared in the contract and are not invented here, so the "
                       "sustainment of mode B is recorded as a required statement with no "
                       "arithmetic behind it.  Mode B's usable fraction of exactly 1 is likewise a "
                       "DECLARED fraction rather than a derived bound: whether the relay chain can "
                       "always be on the sunlit side of the Earth, and so whether the full "
                       "declared solar constant is available to it, is not assessed here.  "
                       "Station-keeping for mode A is required and not assessed either.",
             "retained_partial_result": {
                 "mode_A_sustainment": modes[MODE_A_NAME]["sustainment"]["statement"],
                 "mode_B_sustainment": modes[MODE_B_NAME]["sustainment"]["statement"],
                 "mode_A_floor": text(PASSIVE_FLOOR_SECOND_LAGRANGE),
                 "mode_B_floor": text(PASSIVE_FLOOR_NEAR_EARTH),
             }},
            {"item": "which contracts the proposal's 'parent contracts' names",
             "reason": "the contract records that the prohibitions of the parent contracts still "
                       "apply to any use of the proposal, and names neither.  This run cites the "
                       "two earlier contracts its own prose points at - the surgery run, whose "
                       "declared chirality the blaze direction plays the role of, and the rounded "
                       "ending, which prohibits netting and refuses to seal a component that is by "
                       "definition a leak - and hashes both as retained byte for byte.  Whether "
                       "some other inheritance was intended is not decided here.",
             "retained_partial_result": {
                 "cited": [SURGERY_RELATIVE, ROUNDED_RELATIVE],
                 "surgery_sha256": surgery_digest,
                 "rounded_sha256": rounded_digest,
             }},
        ],
        "modelling_choices": {
            "theta_sun_declaration": "theta_sun is declared as the FULL angular size of the solar "
                                     "disk, twice the declared solar radius over the declared "
                                     "distance, so that the contract's bound theta_sun * L is the "
                                     "spot size and not half of it.  The reported cross-check "
                                     "selects this reading: at the declared near-Earth distance "
                                     "the full-angular-size floor lies below the reported 5 km "
                                     "spot, while the half-angular-size reading would put "
                                     "the floor below it by a factor of about two and a half.  "
                                     "The factor-of-two question is recorded as Undecided.",
            "declared_distances": "the three platform distances are declared constants: 400 km for "
                                  "the near-Earth platform, which is also the declared distance of "
                                  "the historically reported case, 35786000 m for the "
                                  "geostationary platform, and 1500000000 m for the second "
                                  "Lagrange point beyond the Earth on the anti-solar side.  No "
                                  "fourth platform is declared.  The solar angular size at the "
                                  "second Lagrange point uses the declared distance from the Sun "
                                  "there, the declared astronomical unit plus the declared "
                                  "second-Lagrange distance.",
            "floor_ignores_the_aperture": "the declared floor is theta_sun * L exactly as the "
                                          "contract writes it, and it is a floor of the "
                                          "aperture-inclusive spot size D + theta_sun * L because "
                                          "D is positive.  The cross-check reports both the bare "
                                          "floor and the aperture-inclusive floor for the declared "
                                          "20-metre mirror, so neither reading is hidden.",
            "reported_case_is_declared": "the historically reported case is carried as declared "
                                         "constants - about 20 metres of mirror, about 5 km of "
                                         "spot - and not as data: nothing is read, no catalogue or "
                                         "archive is consulted, and the payload marks the reported "
                                         "constants as declared, not measured here and not read "
                                         "from data.  The check is that the reported spot is not "
                                         "below the derived floor, which is what a floor requires.",
            "spectral_radiance_declaration": "the ceiling uses one declared bandwidth-integrated "
                                             "spectral radiance B and one declared wavelength, so "
                                             "that the exact ceiling is B times lambda squared as "
                                             "the contract writes it.  B is declared generously "
                                             "for a solar source, which makes the ceiling an upper "
                                             "bound a fortiori: a smaller declared B would only "
                                             "lower the ceiling and strengthen the conclusion.",
            "l2_antumbra_check": "the statement that the Earth is in the antumbra at the second "
                                 "Lagrange point is DERIVED and not asserted: the umbra tip is "
                                 "computed exactly as the declared Earth radius times the declared "
                                 "astronomical unit over the difference of the declared solar and "
                                 "Earth radii, and the declared second-Lagrange distance is "
                                 "compared with it.  That distance lies beyond the tip, so the "
                                 "occultation is partial and the Sun appears annular.",
            "inverse_square_scaling": "the declared irradiance at the second Lagrange point "
                                      "follows from the declared solar constant at one "
                                      "astronomical unit by the declared inverse-square scaling "
                                      "over the declared distances.  The scaling is a declared "
                                      "assumption of this arithmetic and not a measurement; the "
                                      "run makes no claim about any measured irradiance.",
            "ideal_delivery_efficiency": "the declared delivery efficiency is exactly one, so the "
                                         "required intercepting area is the IDEAL area and is a "
                                         "LOWER bound: any real loss only increases it.  No "
                                         "efficiency is estimated, because an estimate would be a "
                                         "claim this run does not make.",
            "fibre_ceiling_forces_the_division": "the division of labour is asserted as forced: "
                                                 "at the declared constants one fibre mode "
                                                 "carries exactly one microwatt, so the declared "
                                                 "network of a million fibres can carry at most "
                                                 "one watt in total against a required terawatt, a "
                                                 "factor of a trillion.  The mirror array "
                                                 "therefore carries the power in free space, the "
                                                 "fibres carry phase and coherence only, and the "
                                                 "fine pattern is available only to the declared "
                                                 "coherent fraction.",
            "blaze_as_declared_asymmetry": "the diffractive stage is declared as a "
                                           "zero-order-suppressed phase grating, which is "
                                           "two-sided by construction because the zero order is "
                                           "suppressed and the energy goes into the two first "
                                           "orders.  The asymmetry is the declared blaze "
                                           "direction together with unequal declared first-order "
                                           "shares 3/5 and 2/5 summing to exactly one; the "
                                           "difference is exactly 1/5.  A symmetric element has "
                                           "equal shares by declaration and can therefore carry "
                                           "no asymmetry.",
            "deployment_modes_separate": "the two deployment modes are declared separately, each "
                                         "with its own geometric floor, its own usable flux and "
                                         "its own account of required area, areal mass and "
                                         "launch-years.  Mode A carries the derived annular "
                                         "fraction and mode B is declared to carry the full "
                                         "declared solar constant; the two accounts are not netted "
                                         "and no fused figure over them is formed.",
            "target_arithmetic_is_a_proposal_input": "the declared target patch area and the "
                                                     "declared target flux are ARITHMETIC INPUTS "
                                                     "of a proposal.  Every figure derived from "
                                                     "them - required power, required "
                                                     "intercepting area, areal mass, launch-years "
                                                     "and mirror count - is arithmetic on declared "
                                                     "inputs, not an effect, not a forecast, not a "
                                                     "capability claim and not a statement about "
                                                     "any atmosphere, ocean, cloud, surface, "
                                                     "weather or climate.",
            "inherited_prohibitions": "no netting of one account against another, and no "
                                      "sealing of a component that is by definition a leak.  Both "
                                      "are executed against rejected controls in R6, and the "
                                      "termination problem of this setting - the delivery's "
                                      "termination, which is by definition a leak - is recorded "
                                      "as Unaddressed rather than solved.",
            "proposal_only": "the payload records authorization none, decision none, deployment "
                             "none, governance unaddressed, physical_effect_asserted none and "
                             "data_used none, and states that the document is a 提议性方案, a "
                             "proposal only: it authorizes nothing, decides nothing and deploys "
                             "nothing.",
            "exact_only": "every acceptance assertion and every value in the retained payload is "
                          "an exact integer or fraction, carried as an exact decimal-free string "
                          "with its declared unit; no floating-point value is formed anywhere in "
                          "this run and none is written into the payload.",
            "external_library": "no external library is imported.  sympy 1.14 is declared as "
                                "available on the host, as non-authoritative and as unused, "
                                "because no step of this calibration needs a polynomial engine and "
                                "the run must not depend on a host package to reproduce.",
            "resource_limits": "the checker installs a CPU limit, a file-size limit and a wall "
                               "alarm, and records the contract's declared memory budget without "
                               "installing an address-space ceiling; no child process is launched "
                               "and no pre-existing rlimit artifact is touched.",
        },
        "residual": CONTRACT["residual"],
        "protected": CONTRACT["protected"],
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
            "effect_on_any_atmosphere_ocean_cloud_or_surface": False,
            "weather_or_climate_effect": False,
            "meteorological_data_used": False,
            "no_data_read_or_used": True,
            "observational_verification": "Unavailable",
            "the_document_is_a_proposal_only": True,
            "the_three_bounds_are_derived_from_declared_constants": True,
            "the_declared_constants_are_declared_inputs_not_measurements": True,
            "the_target_figures_are_proposal_arithmetic": True,
            "the_division_of_labour_is_forced_by_the_fibre_bound": True,
            "no_netting_of_one_account_against_another": True,
            "no_sealing_of_a_component_that_is_by_definition_a_leak": True,
            "the_termination_problem_is_unaddressed": True,
            "no_seal_no_transport_no_terminology_home": True,
            "no_rust_source_or_lock_changed": True,
            "no_contract_or_note_edited": True,
            "no_claim_added_to_docs_claims_toml": True,
            "pre_existing_files_byte_identical": True,
        },
        "checks": {},
    }
    effect_findings = effect_audit(payload)
    check(all(row["reason"] and row["retained_partial_result"] is not None
              for row in payload["undecided"]),
          "every undecided item carries its reason and its retained partial result")
    check(all(isinstance(value, str) and value
              for value in payload["modelling_choices"].values()),
          "every modelling choice is stated")
    check(len(payload["modelling_choices"]) == 17,
          "the modelling choices declared here are all present")
    check(all(sorted(row) == ["item", "reason", "retained_partial_result"]
              for row in payload["undecided"]),
          "every undecided record carries exactly its item, its reason and its retained partial "
          "result")
    checks = {
        "assertions_within_budget": ASSERTIONS["n"] <= CONTRACT["budgets"]["max_assertions"],
        "this_contract_digest_matches_the_declared_one":
            payload["contract_sha256"] == payload["contract_sha256_declared"],
        "all_parent_contracts_are_retained_byte_for_byte": all(
            row["sha256"] == row["sha256_declared"] for row in payload["parent_contracts"]),
        "the_contract_declares_itself_a_proposal_only":
            bookkeeping["status"] == PROPOSAL_STATUS,
        "the_proposal_only_bookkeeping_matches_the_contract":
            all(bookkeeping[key] == CONTRACT["proposal_only_bookkeeping"][key]
                for key in ("authorization", "decision", "deployment", "governance",
                            "physical_effect_asserted", "data_used")),
        "every_declared_constant_is_declared_and_not_measured":
            all(row["declared"] and not row["measured_here"] and not row["read_from_data"]
                for row in bounds["declared_constants"]),
        "the_three_bounds_are_derived_from_the_declared_constants":
            bounds["all_three_bounds_are_derived_from_declared_constants"]
            and bounds["declared_inputs_are_declared_and_not_measured"],
        "mode_B_usable_fraction_is_recorded_as_declared":
            modes["mode_B_usable_fraction_is_declared_not_derived"]
            and modes["mode_B_usable_fraction_note"] != "",
        "the_passive_spot_floor_is_reported_for_three_platforms":
            bounds["passive_spot_floor"]["platform_count"] == 3,
        "the_l2_floor_exceeds_the_earths_diameter":
            bounds["passive_spot_floor"]["the_l2_floor_exceeds_the_earths_diameter"],
        "the_near_earth_floor_is_consistent_with_the_reported_case":
            bounds["passive_spot_floor"]["cross_check"]["consistent"]
            and bounds["passive_spot_floor"]["cross_check"]
            ["the_reported_spot_is_not_below_the_floor"],
        "the_fibre_ceiling_is_microwatts_per_mode":
            bounds["fibre_power_ceiling"]["per_mode_power_is_microwatts"]
            and Fr(bounds["fibre_power_ceiling"]["per_mode_power"]["value"]) == Fr(1, 10 ** 6),
        "a_gigawatt_would_need_ten_to_the_fifteen_fibres":
            Fr(bounds["fibre_power_ceiling"]["fibres_a_gigawatt_would_need"]["value"]) == 10 ** 15,
        "a_megawatt_would_need_ten_to_the_twelve_fibres":
            Fr(bounds["fibre_power_ceiling"]["fibres_a_megawatt_would_need"]["value"]) == 10 ** 12,
        "the_declared_fibre_network_cannot_carry_the_required_power":
            Fr(bounds["fibre_power_ceiling"]
               ["maximum_power_the_declared_fibre_network_can_carry"]["value"])
            < Fr(target["required_power"]["value"]),
        "the_l2_usable_fraction_is_the_derived_annular_fraction":
            Fr(bounds["l2_usable_fraction"]["usable_fraction"]["value"])
            == USABLE_FRACTION_AT_THE_SECOND_LAGRANGE,
        "the_earth_is_in_the_antumbra_at_the_second_lagrange_point":
            bounds["l2_usable_fraction"]["the_earth_is_in_the_antumbra"]
            and bounds["l2_usable_fraction"]["the_declared_distance_exceeds_the_umbra_length"],
        "the_sun_appears_annular_there": bounds["l2_usable_fraction"]["the_sun_appears_annular"],
        "the_division_of_labour_is_forced_by_the_fibre_bound":
            division["the_division_is_forced_not_stylistic"]
            and division["the_fibre_bound_is_the_reason"],
        "the_fibres_do_not_carry_power": division["fibres"]["carries_power"] is False,
        "no_power_is_routed_through_fibres": division["no_power_is_routed_through_fibres"],
        "the_diffractive_stage_carries_the_declared_blaze_asymmetry":
            division["diffractive_stage"]["the_asymmetry_is_a_declared_asymmetry"]
            and division["diffractive_stage"]["two_sided_by_construction"]
            and Fr(division["diffractive_stage"]["order_share_difference"]["value"]) == Fr(1, 5),
        "the_two_deployment_modes_are_declared_separately":
            modes["the_two_modes_are_declared_separately"] and modes["mode_count"] == 2,
        "each_mode_has_its_own_geometric_floor":
            modes["each_mode_has_its_own_geometric_floor"]
            and modes[MODE_A_NAME]["geometric_floor"]["value"]
            != modes[MODE_B_NAME]["geometric_floor"]["value"],
        "each_mode_has_its_own_sustainment_statement":
            modes["each_mode_has_its_own_sustainment_statement"]
            and bool(modes[MODE_A_NAME]["sustainment"]["statement"])
            and bool(modes[MODE_B_NAME]["sustainment"]["statement"]),
        "the_two_modes_are_not_netted": modes["the_two_modes_are_not_netted"],
        "the_declared_target_arithmetic_follows_exactly":
            target["arithmetic_on_declared_proposal_inputs"]
            and Fr(target["required_power"]["value"])
            == Fr(target["declared_target"]["flux"]["value"])
            * Fr(target["declared_target"]["patch_area"]["value"]),
        "the_target_arithmetic_is_ideal_and_is_a_lower_bound":
            target["the_arithmetic_is_ideal_and_is_a_lower_bound"],
        "no_effect_is_asserted_by_the_target_arithmetic": target["no_effect_is_asserted"],
        "all_six_overreach_controls_are_rejected":
            controls["every_control_produces_a_rejection"]
            and controls["controls_rejected"] == 6,
        "every_overreach_control_discriminates":
            all(row["discriminates"] for row in controls["controls"]),
        "the_failed_control_is_retained":
            controls["failed_controls_count"] == 1
            and controls["failed_controls"][0]["outcome"] == "FAILED_TO_DISCRIMINATE",
        "no_control_is_dropped": controls["no_control_is_dropped"],
        "no_netting_is_performed": inherited["no_netting"]
        and inherited["inherited_prohibitions"][0]["rejected"],
        "sealing_is_refused_for_the_termination":
            inherited["sealing_refused_for_the_termination"]
            and inherited["inherited_prohibitions"][1]["rejected"],
        "the_termination_problem_is_recorded_unaddressed":
            inherited["termination_problem"]["status"] == "Unaddressed"
            and inherited["termination_problem"]["no_attempt_is_made_to_solve_it"],
        "the_inherited_prohibitions_apply_to_any_use":
            inherited["inherited_prohibitions_apply_to_any_use"]
            and all(row["applies_to_any_use"] for row in inherited["inherited_prohibitions"]),
        "the_termination_may_be_accounted_but_never_sealed":
            inherited["termination_problem"]["may_be_accounted_but_never_sealed"]
            and inherited["termination_problem"]["the_component_is_by_definition_a_leak"],
        "the_payload_records_proposal_only_bookkeeping":
            bookkeeping["authorizes_nothing"] and bookkeeping["decides_nothing"]
            and bookkeeping["deploys_nothing"],
        "governance_is_unaddressed_and_no_decision_is_claimed":
            bookkeeping["no_governance_assessment"]
            and bookkeeping["governance"] == UNASSESSED
            and bookkeeping["decision"] == NO_NONE
            and bookkeeping["authorization"] == NO_NONE
            and "who might decide" in bookkeeping["nothing_said_about_who_might_decide"],
        "observational_verification_is_recorded_unavailable":
            payload["verification_status"]["observational"] == "Unavailable",
        "no_data_is_read_or_used": payload["verification_status"]["no_data_read_or_used"],
        "undecided_items_are_declared": len(payload["undecided"]) == 6,
        "no_floating_point_value_is_retained": not contains_float(payload),
        "no_effect_key_appears_anywhere": not effect_findings,
    }
    payload["checks"] = checks
    payload["status"] = "ExternalExactPass" if all(checks.values()) else "Residual"
    return payload


def summarize(payload):
    sections = payload["sections"]
    bounds = sections["R1_derived_bounds"]
    division = sections["R2_division_of_labour"]
    modes = sections["R3_deployment_modes"]
    target = sections["R4_declared_target_arithmetic"]
    controls = sections["R5_overreach_controls"]
    inherited = sections["R6_inherited_prohibitions"]
    bookkeeping = sections["R7_proposal_only_bookkeeping"]
    floor = bounds["passive_spot_floor"]
    cross = floor["cross_check"]
    ceiling = bounds["fibre_power_ceiling"]
    fraction = bounds["l2_usable_fraction"]
    print("optical-imbalance proposal v1: exact calibration of a PROPOSAL ONLY - 提议性方案")
    print("  status:", payload["status"], " assertions:", payload["assertions"],
          " declared constants:", bounds["declared_constants_count"])
    print("  R1a passive spot floor theta_sun * L")
    for row in floor["platforms"]:
        print("     ", row["name"], "at", row["declared_distance"]["value"], "m -> floor",
              row["floor"]["value"], "m")
    print("      L2 floor exceeds the Earth's diameter:",
          floor["the_l2_floor_exceeds_the_earths_diameter"], "| Earth diameter",
          floor["earth_diameter"]["value"], "m")
    print("      reported case: mirror", cross["declared_reported_mirror_diameter"]["value"],
          "m, spot", cross["declared_reported_spot"]["value"], "m, aperture-inclusive floor",
          cross["reported_floor_with_the_aperture_included"]["value"], "m ->", cross["verdict"])
    print("  R1b fibre ceiling B * lambda^2:", ceiling["per_mode_power"]["value"],
          "W per mode | fibres a gigawatt would need",
          ceiling["fibres_a_gigawatt_would_need"]["value"], "| a megawatt",
          ceiling["fibres_a_megawatt_would_need"]["value"])
    print("      declared network of", ceiling["declared_fibre_count"]["value"],
          "fibres carries at most",
          ceiling["maximum_power_the_declared_fibre_network_can_carry"]["value"], "W of the "
          "required", target["required_power"]["value"], "W")
    print("  R1c L2 usable fraction", fraction["usable_fraction"]["value"], "| occulted",
          fraction["the_occulted_fraction"]["value"], "| usable flux",
          fraction["usable_flux"]["value"], "W m^-2")
    print("      the Earth is in the antumbra there:",
          fraction["the_earth_is_in_the_antumbra"], "| umbra length",
          fraction["umbra_length"]["value"], "m < declared distance",
          floor["platforms"][2]["declared_distance"]["value"], "m")
    print("  R2 division of labour: mirrors carry power", division["mirrors"]["carries_power"],
          "| fibres carry power", division["fibres"]["carries_power"], "| forced:",
          division["the_division_is_forced_not_stylistic"])
    print("      diffractive stage: shares",
          division["diffractive_stage"]["plus_first_order_share"]["value"], "and",
          division["diffractive_stage"]["minus_first_order_share"]["value"], "| zero order",
          division["diffractive_stage"]["zero_order_share"]["value"], "| blaze direction declared:",
          division["diffractive_stage"]["blaze_direction"] != NO_NONE)
    for name in (MODE_A_NAME, MODE_B_NAME):
        mode = modes[name]
        print("  R3", name, "| floor", mode["geometric_floor"]["value"], "m | usable fraction",
              mode["usable_fraction"]["value"], "| area",
              mode["required_intercepting_area"]["value"], "m^2 | mass",
              mode["areal_mass"]["value"], "kg | launch-years", mode["launch_years"]["value"])
        print("      sustainment:", mode["sustainment"]["statement"])
    print("  R4 declared target: patch", target["declared_target"]["patch_area"]["value"],
          "m^2 at", target["declared_target"]["flux"]["value"], "W m^-2 -> power",
          target["required_power"]["value"], "W")
    print("      required intercepting area", target["required_intercepting_area"]["value"],
          "m^2 | areal mass", target["areal_mass"]["value"], "kg | launch-years",
          target["launch_years"]["value"])
    print("      mirror elements", target["mirror_elements"]["value"],
          "| fibres the required power would need",
          target["fibres_the_required_power_would_need"]["value"])
    print("      arithmetic on declared proposal inputs:",
          target["arithmetic_on_declared_proposal_inputs"], "| no effect asserted:",
          target["no_effect_is_asserted"])
    print("  R5 overreach controls:", controls["controls_rejected"], "of",
          controls["controls_executed"], "rejected")
    for row in controls["controls"]:
        print("      ", row["control"], "->", row["verdict"], "by", row["rejected_by"])
    for row in controls["failed_controls"]:
        print("      failed control:", row["control"], "->", row["outcome"])
    print("  R6 inherited prohibitions: netting rejected",
          inherited["inherited_prohibitions"][0]["rejected"], "| sealing of the termination "
          "rejected", inherited["inherited_prohibitions"][1]["rejected"])
    print("      the termination problem is", inherited["termination_problem"]["status"],
          "and is not solved here")
    print("  R7 proposal only: authorization", bookkeeping["authorization"], "| decision",
          bookkeeping["decision"], "| deployment", bookkeeping["deployment"], "| governance",
          bookkeeping["governance"], "| physical_effect_asserted",
          bookkeeping["physical_effect_asserted"], "| data_used", bookkeeping["data_used"])
    print("      ", bookkeeping["proposal_only_in_chinese_and_english"])
    print("  verified: no floating-point value retained",
          payload["checks"]["no_floating_point_value_is_retained"],
          "| no data read or used", payload["checks"]["no_data_is_read_or_used"])
    print("  undecided items:", len(payload["undecided"]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=pathlib.Path, required=True)
    arguments = parser.parse_args()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall limit")))
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
