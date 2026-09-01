from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

from adva import link_modules


TRICUSP_REDUCTION_KERNEL = r"""
(module finite-observer-tricusp
  (export three-chart rotate-charge a2-energy)

  ;; Explicit fan-out remains a checked program operation.  These helpers
  ;; create the exact number of occurrences used by the finite calibration.
  (def fan-three-expanded
    (fn ((x0 Real) (x1 Real)) (outputs Real Real Real)
      (frontier
        (use x0)
        (copy (use x1)))))

  (def fan-three
    (fn ((x Real)) (outputs Real Real Real)
      (call fan-three-expanded
        (copy (use x)))))

  (def fan-four-expanded
    (fn ((x0 Real) (x1 Real)) (outputs Real Real Real Real)
      (frontier
        (copy (use x0))
        (copy (use x1)))))

  (def fan-four
    (fn ((x Real)) (outputs Real Real Real Real)
      (call fan-four-expanded
        (copy (use x)))))

  ;; Store one global charge h = x*a + y*b and derive, in order, the C, T,
  ;; and S readings:
  ;;
  ;;   C = (x, y)
  ;;   T = (y - x, -x)
  ;;   S = (-y, x - y)
  ;;
  ;; The eight inputs are distinct checked occurrences produced by fan-four.
  (def three-chart-expanded
    (fn
      ((x0 Real) (x1 Real) (x2 Real) (x3 Real)
       (y0 Real) (y1 Real) (y2 Real) (y3 Real))
      (outputs Real Real Real Real Real Real)
      (frontier
        (use x0)
        (use y0)
        (add (use y1) (neg (use x1)))
        (neg (use x2))
        (neg (use y2))
        (add (use x3) (neg (use y3))))))

  (def three-chart
    (fn ((x Real) (y Real))
      (outputs Real Real Real Real Real Real)
      (call three-chart-expanded
        (frontier
          (call fan-four (use x))
          (call fan-four (use y))))))

  ;; R(p,q) = (-q, p-q) cycles the oriented primitive directions.  Applying
  ;; R three times is the identity.
  (def rotate-charge-expanded
    (fn ((p Real) (q0 Real) (q1 Real)) (outputs Real Real)
      (frontier
        (neg (use q0))
        (add (use p) (neg (use q1))))))

  (def rotate-charge
    (fn ((p Real) (q Real)) (outputs Real Real)
      (call rotate-charge-expanded
        (frontier
          (use p)
          (copy (use q))))))

  ;; At tau = exp(2*pi*i/3), the normalized energy is proportional to the A2
  ;; norm p^2 - p*q + q^2.  This program is only its exact small-integer
  ;; numerical realization; it is not a promoted spectral or complex API.
  (def a2-energy-expanded
    (fn
      ((p0 Real) (p1 Real) (p2 Real)
       (q0 Real) (q1 Real) (q2 Real))
      Real
      (add
        (mul (use p0) (use p1))
        (add
          (neg (mul (use p2) (use q0)))
          (mul (use q1) (use q2))))))

  (def a2-energy
    (fn ((p Real) (q Real)) Real
      (call a2-energy-expanded
        (frontier
          (call fan-three (use p))
          (call fan-three (use q))))))
)
"""


Charge = tuple[int, int]


@dataclass(frozen=True, slots=True)
class TriChartReading:
    """Three derived coordinate views of one global integral charge."""

    construction: Charge
    temporal: Charge
    spatial: Charge


@dataclass(frozen=True, slots=True)
class ObserverBudget:
    """A bounded research observer, not a stable Adva semantic type."""

    construction_radius: int
    energy_cutoff: int

    def __post_init__(self) -> None:
        if self.construction_radius < 0:
            raise ValueError("construction radius must be nonnegative")
        if self.energy_cutoff < 0:
            raise ValueError("energy cutoff must be nonnegative")


@dataclass(frozen=True, slots=True)
class ObservedMode:
    global_charge: Charge
    charts: TriChartReading
    energy: int


@dataclass(frozen=True, slots=True)
class CertifiedFiniteCut:
    """A finite Conway presentation with an exact rational order witness."""

    left: tuple[Fraction, ...]
    right: tuple[Fraction, ...]

    def __post_init__(self) -> None:
        if not self.left or not self.right:
            raise ValueError("this calibration uses a two-sided finite cut")
        if max(self.left) >= min(self.right):
            raise ValueError("every left option must be below every right option")

    @property
    def certificate(self) -> dict[str, Any]:
        return {
            "scope": "finite-rational-options",
            "order": "checked",
            "left_max": str(max(self.left)),
            "right_min": str(min(self.right)),
            "ordering_source": "declared-rational-order-not-period-energy",
        }


@dataclass(frozen=True, slots=True)
class FiniteObserverSnapshot:
    """One operational reduction with visible modes and an explicit tail."""

    budget: ObserverBudget
    visible_modes: tuple[ObservedMode, ...]
    residual_modes: tuple[ObservedMode, ...]
    cut: CertifiedFiniteCut

    @property
    def certificate(self) -> dict[str, Any]:
        visible = {mode.global_charge for mode in self.visible_modes}
        residual = {mode.global_charge for mode in self.residual_modes}
        return {
            "finite": "checked",
            "partition": "checked" if visible.isdisjoint(residual) else "failed",
            "energy_selection": "checked",
            "cut_order": self.cut.certificate["order"],
            "order_energy_separation": "checked",
        }


def _checked_functions() -> tuple[Any, Any, Any]:
    workspace = link_modules([TRICUSP_REDUCTION_KERNEL])
    return (
        workspace.function("finite-observer-tricusp", "three-chart"),
        workspace.function("finite-observer-tricusp", "rotate-charge"),
        workspace.function("finite-observer-tricusp", "a2-energy"),
    )


def _integral_tuple(value: object, size: int) -> tuple[int, ...]:
    if not isinstance(value, tuple) or len(value) != size:
        raise TypeError(f"expected an ordered {size}-Real frontier")
    integers = tuple(int(coordinate) for coordinate in value)
    if tuple(float(integer) for integer in integers) != value:
        raise AssertionError(f"expected exact small-integer realization, got {value}")
    return integers


def _read_charts(function: Any, charge: Charge) -> TriChartReading:
    values = _integral_tuple(function.evaluate({"x": charge[0], "y": charge[1]}), 6)
    return TriChartReading(
        construction=(values[0], values[1]),
        temporal=(values[2], values[3]),
        spatial=(values[4], values[5]),
    )


def _rotate(function: Any, charge: Charge) -> Charge:
    p, q = _integral_tuple(function.evaluate({"p": charge[0], "q": charge[1]}), 2)
    return p, q


def _energy(function: Any, charge: Charge) -> int:
    value = function.evaluate({"p": charge[0], "q": charge[1]})
    if not isinstance(value, float) or not value.is_integer():
        raise AssertionError(f"expected exact integral A2 energy, got {value!r}")
    return int(value)


def _a2_energy_oracle(charge: Charge) -> int:
    p, q = charge
    return p * p - p * q + q * q


def _three_chart_oracle(charge: Charge) -> TriChartReading:
    x, y = charge
    return TriChartReading(
        construction=(x, y),
        temporal=(y - x, -x),
        spatial=(-y, x - y),
    )


def _reduce(
    three_chart: Any,
    energy: Any,
    budget: ObserverBudget,
    cut: CertifiedFiniteCut,
) -> FiniteObserverSnapshot:
    visible: list[ObservedMode] = []
    residual: list[ObservedMode] = []
    radius = budget.construction_radius
    for p in range(-radius, radius + 1):
        for q in range(-radius, radius + 1):
            charge = (p, q)
            mode = ObservedMode(
                global_charge=charge,
                charts=_read_charts(three_chart, charge),
                energy=_energy(energy, charge),
            )
            (visible if mode.energy <= budget.energy_cutoff else residual).append(mode)
    return FiniteObserverSnapshot(
        budget=budget,
        visible_modes=tuple(visible),
        residual_modes=tuple(residual),
        cut=cut,
    )


def _ceil(value: Fraction) -> int:
    return -((-value.numerator) // value.denominator)


def _dyadic_birthday(value: Fraction) -> int:
    denominator = value.denominator
    if denominator & (denominator - 1):
        raise ValueError("candidate is not dyadic")
    if denominator == 1:
        return abs(value.numerator)
    exponent = denominator.bit_length() - 1
    return abs(value.numerator) // denominator + exponent + 1


def _objectify(cut: CertifiedFiniteCut) -> Fraction:
    """Research oracle: the least-birthday dyadic in one bounded cut."""

    lower = max(cut.left)
    upper = min(cut.right)
    candidates: set[Fraction] = set()
    for exponent in range(8):
        denominator = 1 << exponent
        first = (lower.numerator * denominator) // lower.denominator + 1
        last = _ceil(upper * denominator) - 1
        candidates.update(Fraction(numerator, denominator) for numerator in range(first, last + 1))
    least_birthday = min(_dyadic_birthday(value) for value in candidates)
    simplest = sorted(value for value in candidates if _dyadic_birthday(value) == least_birthday)
    if len(simplest) != 1:
        raise AssertionError(f"expected one simplest dyadic, got {simplest}")
    return simplest[0]


def test_checked_adva_program_derives_three_views_from_one_global_charge() -> None:
    three_chart, rotate, energy = _checked_functions()
    for function in (three_chart, rotate, energy):
        assert function.validation_certificate["graph"] == "checked"

    fixtures = ((0, 0), (1, 0), (0, 1), (1, 1), (2, -3), (-5, 4))
    for charge in fixtures:
        charts = _read_charts(three_chart, charge)
        assert charts == _three_chart_oracle(charge)

        # With the chosen orientation, cyclic rotation reads C -> S -> T -> C.
        spatial = _rotate(rotate, charts.construction)
        temporal = _rotate(rotate, spatial)
        construction = _rotate(rotate, temporal)
        assert spatial == charts.spatial
        assert temporal == charts.temporal
        assert construction == charts.construction


def test_checked_a2_energy_has_a_finite_cyclic_unit_shell() -> None:
    _, rotate, energy = _checked_functions()
    visible: set[Charge] = set()
    for p in range(-4, 5):
        for q in range(-4, 5):
            charge = (p, q)
            observed = _energy(energy, charge)
            assert observed == _a2_energy_oracle(charge)
            assert observed == _energy(energy, _rotate(rotate, charge))
            if observed <= 1:
                visible.add(charge)

    assert visible == {
        (0, 0),
        (1, 0),
        (0, 1),
        (-1, 0),
        (0, -1),
        (1, 1),
        (-1, -1),
    }


def test_finite_observer_keeps_energy_selection_cut_order_and_residual_distinct() -> None:
    three_chart, _, energy = _checked_functions()
    cut = CertifiedFiniteCut(
        left=(Fraction(-1), Fraction(0)),
        right=(Fraction(1), Fraction(2)),
    )
    snapshot = _reduce(
        three_chart,
        energy,
        ObserverBudget(construction_radius=2, energy_cutoff=1),
        cut,
    )

    assert len(snapshot.visible_modes) == 7
    assert len(snapshot.residual_modes) == 18
    assert all(mode.energy <= 1 for mode in snapshot.visible_modes)
    assert all(mode.energy > 1 for mode in snapshot.residual_modes)
    assert snapshot.certificate == {
        "finite": "checked",
        "partition": "checked",
        "energy_selection": "checked",
        "cut_order": "checked",
        "order_energy_separation": "checked",
    }
    assert snapshot.cut.certificate["ordering_source"] == (
        "declared-rational-order-not-period-energy"
    )
    assert _objectify(snapshot.cut) == Fraction(1, 2)


def test_observer_refinement_adds_modes_without_reversing_the_certified_cut() -> None:
    three_chart, _, energy = _checked_functions()
    cut = CertifiedFiniteCut((Fraction(0),), (Fraction(1),))
    coarse = _reduce(
        three_chart,
        energy,
        ObserverBudget(construction_radius=3, energy_cutoff=1),
        cut,
    )
    fine = _reduce(
        three_chart,
        energy,
        ObserverBudget(construction_radius=3, energy_cutoff=3),
        cut,
    )

    coarse_visible = {mode.global_charge for mode in coarse.visible_modes}
    fine_visible = {mode.global_charge for mode in fine.visible_modes}
    assert coarse_visible < fine_visible
    assert len(fine.residual_modes) < len(coarse.residual_modes)
    assert coarse.cut == fine.cut
    assert coarse.cut.certificate == fine.cut.certificate
    assert _objectify(coarse.cut) == _objectify(fine.cut) == Fraction(1, 2)


def test_runtime_presentations_remain_distinct_after_surreal_objectification() -> None:
    three_chart, _, energy = _checked_functions()
    budget = ObserverBudget(construction_radius=1, energy_cutoff=1)
    narrow = _reduce(
        three_chart,
        energy,
        budget,
        CertifiedFiniteCut((Fraction(0),), (Fraction(2),)),
    )
    wide = _reduce(
        three_chart,
        energy,
        budget,
        CertifiedFiniteCut((Fraction(0),), (Fraction(3),)),
    )

    assert narrow != wide
    assert _objectify(narrow.cut) == _objectify(wide.cut) == Fraction(1)
    assert narrow.cut != wide.cut
