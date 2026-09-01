from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from typing import Callable, Mapping


Axis = str
Point = tuple[int, int, int]
CoarsePoint = tuple[int, int]
Scalar = Fraction
Feature = dict[Point, Scalar]
CoarseFeature = dict[CoarsePoint, Scalar]

AXES: tuple[Axis, ...] = ("t", "X", "K")
AXIS_INDEX: dict[Axis, int] = {"t": 0, "X": 1, "K": 2}
POINTS: tuple[Point, ...] = tuple(product((0, 1), repeat=3))
COARSE_POINTS: tuple[CoarsePoint, ...] = tuple(product((0, 1), repeat=2))


@dataclass(frozen=True, slots=True)
class EnergyReport:
    """Exact directional variation; no scalar total is implied."""

    temporal: Scalar
    spatial: Scalar
    construction: Scalar

    def as_mapping(self) -> dict[Axis, Scalar]:
        return {
            "t": self.temporal,
            "X": self.spatial,
            "K": self.construction,
        }


def _feature(function: Callable[[int, int, int], int | Fraction]) -> Feature:
    return {point: Fraction(function(*point)) for point in POINTS}


def _directional_edges(axis: Axis) -> tuple[tuple[Point, Point], ...]:
    index = AXIS_INDEX[axis]
    edges: list[tuple[Point, Point]] = []
    for point in POINTS:
        if point[index] != 0:
            continue
        endpoint = list(point)
        endpoint[index] = 1
        edges.append((point, tuple(endpoint)))
    return tuple(edges)


def directional_energy(feature: Mapping[Point, Scalar], axis: Axis) -> Scalar:
    """Count every unoriented unit-weight cube edge exactly once."""

    return sum(
        (feature[right] - feature[left]) ** 2
        for left, right in _directional_edges(axis)
    )


def energy_report(feature: Mapping[Point, Scalar]) -> EnergyReport:
    return EnergyReport(
        temporal=directional_energy(feature, "t"),
        spatial=directional_energy(feature, "X"),
        construction=directional_energy(feature, "K"),
    )


def weighted_total(
    report: EnergyReport,
    calibration: Mapping[Axis, Scalar],
) -> Scalar:
    """Scalarization is allowed only with all three declared positive scales."""

    if set(calibration) != set(AXES):
        raise ValueError("all three directional calibration weights are required")
    if any(calibration[axis] <= 0 for axis in AXES):
        raise ValueError("directional calibration weights must be positive")
    energies = report.as_mapping()
    return sum(calibration[axis] * energies[axis] for axis in AXES)


def forget_construction(feature: Mapping[Point, Scalar]) -> CoarseFeature:
    """Conditional average over each two-point construction fibre."""

    return {
        (temporal, spatial): (
            feature[(temporal, spatial, 0)]
            + feature[(temporal, spatial, 1)]
        )
        / 2
        for temporal, spatial in COARSE_POINTS
    }


def pull_back(coarse: Mapping[CoarsePoint, Scalar]) -> Feature:
    return {
        (temporal, spatial, construction): coarse[(temporal, spatial)]
        for temporal, spatial, construction in POINTS
    }


def subtract(
    left: Mapping[Point, Scalar],
    right: Mapping[Point, Scalar],
) -> Feature:
    return {point: left[point] - right[point] for point in POINTS}


def add_reports(left: EnergyReport, right: EnergyReport) -> EnergyReport:
    return EnergyReport(
        temporal=left.temporal + right.temporal,
        spatial=left.spatial + right.spatial,
        construction=left.construction + right.construction,
    )


def test_binary_characteristics_have_exact_directional_cut_energies() -> None:
    features = {
        "constant": _feature(lambda _t, _x, _k: 0),
        "temporal": _feature(lambda t, _x, _k: t),
        "spatial": _feature(lambda _t, x, _k: x),
        "construction": _feature(lambda _t, _x, k: k),
        "conjunction": _feature(lambda t, x, k: t * x * k),
        "majority": _feature(lambda t, x, k: int(t + x + k >= 2)),
        "parity": _feature(lambda t, x, k: (t + x + k) % 2),
    }

    assert energy_report(features["constant"]) == EnergyReport(0, 0, 0)
    assert energy_report(features["temporal"]) == EnergyReport(4, 0, 0)
    assert energy_report(features["spatial"]) == EnergyReport(0, 4, 0)
    assert energy_report(features["construction"]) == EnergyReport(0, 0, 4)
    assert energy_report(features["conjunction"]) == EnergyReport(1, 1, 1)
    assert energy_report(features["majority"]) == EnergyReport(2, 2, 2)
    assert energy_report(features["parity"]) == EnergyReport(4, 4, 4)


def test_no_scalar_total_exists_without_three_domain_calibration() -> None:
    temporal = EnergyReport(4, 0, 0)
    construction = EnergyReport(0, 0, 4)

    try:
        weighted_total(temporal, {"t": Fraction(1), "X": Fraction(1)})
    except ValueError as error:
        assert "all three" in str(error)
    else:
        raise AssertionError("an incomplete calibration must be rejected")

    temporal_cheap = {axis: Fraction(1) for axis in AXES}
    temporal_expensive = {
        "t": Fraction(10),
        "X": Fraction(1),
        "K": Fraction(1),
    }
    construction_expensive = {
        "t": Fraction(1),
        "X": Fraction(1),
        "K": Fraction(10),
    }

    assert weighted_total(temporal, temporal_expensive) > weighted_total(
        construction,
        temporal_expensive,
    )
    assert weighted_total(temporal, construction_expensive) < weighted_total(
        construction,
        construction_expensive,
    )
    assert weighted_total(temporal, temporal_cheap) == weighted_total(
        construction,
        temporal_cheap,
    )


def test_conditional_forgetting_has_exact_energy_residual() -> None:
    feature = _feature(
        lambda t, x, k: (
            3 * t
            - 2 * x
            + 5 * k
            + 7 * t * x
            - 11 * x * k
            + 13 * t * k
        )
    )
    coarse = forget_construction(feature)
    lifted_coarse = pull_back(coarse)
    residual = subtract(feature, lifted_coarse)

    for temporal, spatial in COARSE_POINTS:
        assert (
            residual[(temporal, spatial, 0)]
            + residual[(temporal, spatial, 1)]
            == 0
        )

    assert energy_report(feature) == add_reports(
        energy_report(lifted_coarse),
        energy_report(residual),
    )
    assert directional_energy(lifted_coarse, "K") == 0
    assert directional_energy(feature, "K") == directional_energy(
        residual,
        "K",
    )


def test_zero_construction_energy_is_exact_descent_on_the_cube() -> None:
    descends = _feature(lambda t, x, _k: t * (1 - x))
    does_not_descend = _feature(lambda t, x, k: (t + x + k) % 2)

    assert directional_energy(descends, "K") == 0
    assert pull_back(forget_construction(descends)) == descends

    assert directional_energy(does_not_descend, "K") == 4
    assert pull_back(forget_construction(does_not_descend)) != does_not_descend


def test_parity_energy_is_completely_hidden_by_coarse_averaging() -> None:
    parity = _feature(lambda t, x, k: (t + x + k) % 2)
    coarse = forget_construction(parity)
    lifted_coarse = pull_back(coarse)
    residual = subtract(parity, lifted_coarse)

    assert set(coarse.values()) == {Fraction(1, 2)}
    assert energy_report(parity) == EnergyReport(4, 4, 4)
    assert energy_report(lifted_coarse) == EnergyReport(0, 0, 0)
    assert energy_report(residual) == EnergyReport(4, 4, 4)

