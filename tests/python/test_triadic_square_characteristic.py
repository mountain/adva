from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isqrt
from typing import Any

import sympy

from adva import link_modules


SQUARE_CALIBRATION = r"""
(module triadic-square
  (export
    negate increment double square
    square-after-negate
    square-after-increment
    square-after-double
    scale-four-after-square
    shifted-sixteenth-power)

  (def negate
    (fn ((x Real)) Real
      (neg (use x))))

  (def increment
    (fn ((x Real)) Real
      (add (use x) 1)))

  (def double
    (fn ((x Real)) Real
      (scale 2 (use x))))

  (def square
    (fn ((x Real)) Real
      (mul (copy (use x)))))

  (def square-after-negate
    (fn ((x Real)) Real
      (call square
        (call negate (use x)))))

  (def square-after-increment
    (fn ((x Real)) Real
      (call square
        (call increment (use x)))))

  (def square-after-double
    (fn ((x Real)) Real
      (call square
        (call double (use x)))))

  (def scale-four-after-square
    (fn ((x Real)) Real
      (scale 4
        (call square (use x)))))

  (def shifted-sixteenth-power
    (fn ((x Real)) Real
      (call square
        (call square
          (call square
            (call square
              (call increment (use x)))))))))
"""


@dataclass(frozen=True, slots=True)
class QuadraticCharacteristic:
    """One exact member of the bounded quadratic hypothesis class."""

    quadratic: Fraction
    linear: Fraction
    constant: Fraction

    @classmethod
    def from_probes(
        cls,
        at_negative_one: Fraction,
        at_zero: Fraction,
        at_positive_one: Fraction,
    ) -> QuadraticCharacteristic:
        constant = at_zero
        quadratic = (
            at_positive_one + at_negative_one - 2 * at_zero
        ) / 2
        linear = (at_positive_one - at_negative_one) / 2
        return cls(quadratic, linear, constant)

    def evaluate(self, value: Fraction) -> Fraction:
        return (
            self.quadratic * value * value
            + self.linear * value
            + self.constant
        )


@dataclass(frozen=True, slots=True)
class ExactOpenInterval:
    """An exact one-dimensional spatial probe."""

    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if self.lower >= self.upper:
            raise ValueError("an open interval requires lower < upper")

    def contains(self, value: Fraction) -> bool:
        return self.lower < value < self.upper

    def reflected(self) -> ExactOpenInterval:
        return ExactOpenInterval(-self.upper, -self.lower)


@dataclass(frozen=True, slots=True)
class BranchComponent:
    """One labelled component of a square-map inverse image."""

    label: str
    interval: ExactOpenInterval


@dataclass(frozen=True, slots=True)
class SquarePullback:
    """A finite exact branch presentation for q(x)=x^2."""

    target: ExactOpenInterval
    components: tuple[BranchComponent, ...]
    contains_critical_value: bool

    def contains(self, value: Fraction) -> bool:
        return any(component.interval.contains(value) for component in self.components)


def _exact_sqrt(value: Fraction) -> Fraction:
    if value < 0:
        raise ValueError("the exact square root is only defined here for non-negative values")
    numerator = isqrt(value.numerator)
    denominator = isqrt(value.denominator)
    if numerator * numerator != value.numerator:
        raise ValueError(f"{value} does not have a rational square root")
    if denominator * denominator != value.denominator:
        raise ValueError(f"{value} does not have a rational square root")
    return Fraction(numerator, denominator)


def square_pullback(target: ExactOpenInterval) -> SquarePullback:
    """Pull back selected exact intervals through q(x)=x^2.

    The calibration deliberately uses rational-square endpoints. This is a
    bounded exact model, not a general semialgebraic-set implementation.
    """

    if target.upper <= 0:
        return SquarePullback(target, (), False)

    upper_root = _exact_sqrt(target.upper)

    if target.lower < 0:
        return SquarePullback(
            target,
            (
                BranchComponent(
                    "merged",
                    ExactOpenInterval(-upper_root, upper_root),
                ),
            ),
            True,
        )

    lower_root = _exact_sqrt(target.lower)
    return SquarePullback(
        target,
        (
            BranchComponent(
                "negative",
                ExactOpenInterval(-upper_root, -lower_root),
            ),
            BranchComponent(
                "positive",
                ExactOpenInterval(lower_root, upper_root),
            ),
        ),
        target.lower < 0 < target.upper,
    )


def reverse_square_fibre(value: Fraction) -> tuple[Fraction, ...]:
    """The exact reverse relation associated with q(x)=x^2."""

    if value < 0:
        return ()
    root = _exact_sqrt(value)
    if root == 0:
        return (Fraction(0),)
    return (-root, root)


def _workspace() -> Any:
    return link_modules([SQUARE_CALIBRATION])


def _as_fraction(value: float) -> Fraction:
    return Fraction(str(value))


def test_temporal_probes_recover_square_and_expose_the_sign_quotient() -> None:
    workspace = _workspace()
    square = workspace.function("triadic-square", "square")
    square_after_negate = workspace.function(
        "triadic-square",
        "square-after-negate",
    )

    observations = tuple(
        _as_fraction(square.evaluate({"x": float(value)}))
        for value in (-1, 0, 1)
    )
    characteristic = QuadraticCharacteristic.from_probes(*observations)

    assert characteristic == QuadraticCharacteristic(
        Fraction(1),
        Fraction(0),
        Fraction(0),
    )
    assert characteristic.evaluate(Fraction(3, 2)) == Fraction(9, 4)

    x = sympy.Symbol("x", real=True)
    assert sympy.simplify(square.to_sympy() - x**2) == 0
    assert sympy.simplify(square_after_negate.to_sympy() - x**2) == 0

    # q(x)=q(-x) identifies the two generic temporal states extensionally,
    # while the checked construction histories remain distinct.
    for value in (-3.0, -1.0, 0.0, 1.0, 3.0):
        assert square.evaluate({"x": value}) == square_after_negate.evaluate(
            {"x": value}
        )
    assert square.history != square_after_negate.history
    assert square.ir != square_after_negate.ir


def test_spatial_pullback_splits_into_two_sheets_and_merges_at_zero() -> None:
    positive_target = ExactOpenInterval(Fraction(1), Fraction(4))
    split = square_pullback(positive_target)

    assert split.components == (
        BranchComponent(
            "negative",
            ExactOpenInterval(Fraction(-2), Fraction(-1)),
        ),
        BranchComponent(
            "positive",
            ExactOpenInterval(Fraction(1), Fraction(2)),
        ),
    )
    assert (
        split.components[0].interval.reflected()
        == split.components[1].interval
    )
    assert not split.contains_critical_value

    crossing_target = ExactOpenInterval(Fraction(-1), Fraction(1))
    merged = square_pullback(crossing_target)
    assert merged.components == (
        BranchComponent(
            "merged",
            ExactOpenInterval(Fraction(-1), Fraction(1)),
        ),
    )
    assert merged.contains_critical_value

    samples = tuple(Fraction(value, 2) for value in range(-6, 7))
    for value in samples:
        assert split.contains(value) == positive_target.contains(value * value)
        assert merged.contains(value) == crossing_target.contains(value * value)

    assert reverse_square_fibre(Fraction(4)) == (
        Fraction(-2),
        Fraction(2),
    )
    assert reverse_square_fibre(Fraction(0)) == (Fraction(0),)
    assert reverse_square_fibre(Fraction(-1)) == ()


def test_constructive_square_requires_a_checked_explicit_copy() -> None:
    square = _workspace().function("triadic-square", "square")

    copy_slice = square.program_slice([], [0])
    assert copy_slice.certificate["event_difference"] == "checked"
    assert [event["id"] for event in copy_slice.result.events] == [0]
    assert len(copy_slice.result.lower_boundary) == 1
    assert len(copy_slice.result.upper_boundary) == 2

    left, right = copy_slice.result.upper_boundary
    assert left["wire"]["lineage"][0] != right["wire"]["lineage"][0]
    assert left["sources"] == right["sources"]

    whole = square.program_slice([], [0, 1])
    assert [event["id"] for event in whole.result.events] == [0, 1]

    value, gradient, certificate = square.value_and_gradient({"x": 3.0})
    assert value == 9.0
    assert gradient == {"x": 6.0}
    assert set(certificate["operation_rules"]) == {
        "adva.builtin:copy@1",
        "adva.builtin:mul@1",
    }


def test_scaling_crosses_square_but_translation_forces_a_cross_term() -> None:
    workspace = _workspace()
    square_after_double = workspace.function(
        "triadic-square",
        "square-after-double",
    )
    scale_four_after_square = workspace.function(
        "triadic-square",
        "scale-four-after-square",
    )
    square_after_increment = workspace.function(
        "triadic-square",
        "square-after-increment",
    )

    x = sympy.Symbol("x", real=True)
    assert sympy.simplify(
        square_after_double.to_sympy() - scale_four_after_square.to_sympy()
    ) == 0
    assert square_after_double.history != scale_four_after_square.history

    shifted = sympy.Poly(sympy.expand(square_after_increment.to_sympy()), x)
    assert shifted.as_expr() == x**2 + 2 * x + 1
    assert shifted.coeff_monomial(x) == 2

    # Every old post-affine square normal form 2^k*x^2+b has zero linear
    # coefficient. Thus S;Q cannot be rewritten as Q followed only by the
    # former binary-affine characteristic language.
    for exponent in range(5):
        for constant in range(5):
            candidate = sympy.Poly(2**exponent * x**2 + constant, x)
            assert candidate != shifted


def test_nested_square_calls_compress_a_dense_expanded_polynomial() -> None:
    function = _workspace().function(
        "triadic-square",
        "shifted-sixteenth-power",
    )
    x = sympy.Symbol("x", real=True)
    expanded = sympy.Poly(sympy.expand(function.to_sympy()), x)
    calls = [
        event
        for event in function.history["prefix"]
        if event["kind"] == "call"
    ]

    assert expanded.degree() == 16
    assert len(expanded.terms()) == 17
    assert len(calls) == 5
    assert sympy.simplify(expanded.as_expr() - (x + 1) ** 16) == 0
