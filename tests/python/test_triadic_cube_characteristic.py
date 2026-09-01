from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

import sympy

from adva import link_modules


CUBE_CALIBRATION = r"""
(module triadic-cube
  (export
    negate increment double
    square cube
    square-after-negate
    cube-after-negate
    negate-after-cube
    cube-after-increment
    cube-after-double
    scale-eight-after-cube
    shifted-twenty-seventh-power)

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

  (def triple-copy-expanded
    (fn ((left Real) (right Real)) (outputs Real Real Real)
      (frontier
        (use left)
        (copy (use right)))))

  (def triple-product-expanded
    (fn ((x0 Real) (x1 Real) (x2 Real)) Real
      (mul
        (mul (use x0) (use x1))
        (use x2))))

  (def cube
    (fn ((x Real)) Real
      (call triple-product-expanded
        (call triple-copy-expanded
          (copy (use x))))))

  (def square-after-negate
    (fn ((x Real)) Real
      (call square
        (call negate (use x)))))

  (def cube-after-negate
    (fn ((x Real)) Real
      (call cube
        (call negate (use x)))))

  (def negate-after-cube
    (fn ((x Real)) Real
      (call negate
        (call cube (use x)))))

  (def cube-after-increment
    (fn ((x Real)) Real
      (call cube
        (call increment (use x)))))

  (def cube-after-double
    (fn ((x Real)) Real
      (call cube
        (call double (use x)))))

  (def scale-eight-after-cube
    (fn ((x Real)) Real
      (scale 8
        (call cube (use x)))))

  (def shifted-twenty-seventh-power
    (fn ((x Real)) Real
      (call cube
        (call cube
          (call cube
            (call increment (use x)))))))
)
"""


@dataclass(frozen=True, slots=True)
class CubicCharacteristic:
    """One exact member of the bounded cubic hypothesis class."""

    cubic: Fraction
    quadratic: Fraction
    linear: Fraction
    constant: Fraction

    @classmethod
    def from_probes(
        cls,
        at_negative_one: Fraction,
        at_zero: Fraction,
        at_positive_one: Fraction,
        at_two: Fraction,
    ) -> CubicCharacteristic:
        constant = at_zero
        positive = at_positive_one - constant
        negative = at_negative_one - constant
        quadratic = (positive + negative) / 2
        odd_sum = (positive - negative) / 2
        cubic = (at_two - constant - 4 * quadratic - 2 * odd_sum) / 6
        linear = odd_sum - cubic
        return cls(cubic, quadratic, linear, constant)

    def evaluate(self, value: Fraction) -> Fraction:
        return (
            self.cubic * value**3
            + self.quadratic * value**2
            + self.linear * value
            + self.constant
        )


@dataclass(frozen=True, slots=True)
class ExactOpenInterval:
    """An exact real interval used by the bounded spatial observer."""

    lower: Fraction
    upper: Fraction

    def __post_init__(self) -> None:
        if self.lower >= self.upper:
            raise ValueError("an open interval requires lower < upper")

    def contains(self, value: Fraction) -> bool:
        return self.lower < value < self.upper


@dataclass(frozen=True, slots=True)
class CubePullback:
    """The real inverse-image components of x mapsto x^3."""

    target: ExactOpenInterval
    components: tuple[ExactOpenInterval, ...]
    contains_critical_value: bool

    def contains(self, value: Fraction) -> bool:
        return any(component.contains(value) for component in self.components)


def _exact_integer_cube_root(value: int) -> int:
    sign = -1 if value < 0 else 1
    target = abs(value)
    low = 0
    high = target + 1
    while low + 1 < high:
        middle = (low + high) // 2
        if middle**3 <= target:
            low = middle
        else:
            high = middle
    if low**3 != target:
        raise ValueError(f"{value} is not an exact integer cube")
    return sign * low


def _exact_cube_root(value: Fraction) -> Fraction:
    return Fraction(
        _exact_integer_cube_root(value.numerator),
        _exact_integer_cube_root(value.denominator),
    )


def cube_pullback(target: ExactOpenInterval) -> CubePullback:
    """Pull back intervals whose endpoints are exact rational cubes."""

    return CubePullback(
        target=target,
        components=(
            ExactOpenInterval(
                _exact_cube_root(target.lower),
                _exact_cube_root(target.upper),
            ),
        ),
        contains_critical_value=target.lower < 0 < target.upper,
    )


def reverse_cube_fibre(value: Fraction) -> tuple[Fraction, ...]:
    """The real reverse fibre of x mapsto x^3 on exact rational cubes."""

    return (_exact_cube_root(value),)


def _workspace() -> Any:
    return link_modules([CUBE_CALIBRATION])


def _as_fraction(value: float) -> Fraction:
    return Fraction(str(value))


def _copy_tree(function: Any) -> tuple[set[str], tuple[dict[str, Any], ...]]:
    copy_events = tuple(
        event for event in function.history["prefix"] if event["kind"] == "copy"
    )
    assert len(copy_events) == 2

    outer = next(
        event
        for event in copy_events
        if any(
            other["parent"] in event["children"]
            for other in copy_events
            if other is not event
        )
    )
    inner = next(event for event in copy_events if event is not outer)
    assert inner["parent"] in outer["children"]

    leaves = set(outer["children"])
    leaves.remove(inner["parent"])
    leaves.update(inner["children"])
    return leaves, copy_events


def test_temporal_probes_recover_cube_and_separate_invariance_from_equivariance() -> None:
    workspace = _workspace()
    cube = workspace.function("triadic-cube", "cube")
    square = workspace.function("triadic-cube", "square")
    square_after_negate = workspace.function(
        "triadic-cube", "square-after-negate"
    )
    cube_after_negate = workspace.function(
        "triadic-cube", "cube-after-negate"
    )
    negate_after_cube = workspace.function(
        "triadic-cube", "negate-after-cube"
    )

    observations = tuple(
        _as_fraction(cube.evaluate({"x": float(value)}))
        for value in (-1, 0, 1, 2)
    )
    characteristic = CubicCharacteristic.from_probes(*observations)

    assert characteristic == CubicCharacteristic(
        Fraction(1),
        Fraction(0),
        Fraction(0),
        Fraction(0),
    )
    assert characteristic.evaluate(Fraction(3, 2)) == Fraction(27, 8)

    x = sympy.Symbol("x", real=True)
    assert sympy.simplify(cube.to_sympy() - x**3) == 0

    # The square is invariant under reflection; the cube is equivariant:
    # Q(-x)=Q(x), whereas C(-x)=-C(x).
    assert sympy.simplify(
        square_after_negate.to_sympy() - square.to_sympy()
    ) == 0
    assert sympy.simplify(
        cube_after_negate.to_sympy() - negate_after_cube.to_sympy()
    ) == 0
    assert sympy.simplify(cube_after_negate.to_sympy() + x**3) == 0

    assert square.history != square_after_negate.history
    assert cube_after_negate.history != negate_after_cube.history


def test_real_cube_pullback_stays_connected_across_a_differential_critical_value() -> None:
    targets = (
        ExactOpenInterval(Fraction(-8), Fraction(-1)),
        ExactOpenInterval(Fraction(-8), Fraction(27)),
        ExactOpenInterval(Fraction(1), Fraction(8)),
    )
    expected = (
        ExactOpenInterval(Fraction(-2), Fraction(-1)),
        ExactOpenInterval(Fraction(-2), Fraction(3)),
        ExactOpenInterval(Fraction(1), Fraction(2)),
    )

    for target, component in zip(targets, expected):
        pulled = cube_pullback(target)
        assert pulled.components == (component,)
        samples = tuple(Fraction(value, 2) for value in range(-8, 9))
        for value in samples:
            assert pulled.contains(value) == target.contains(value**3)

    assert not cube_pullback(targets[0]).contains_critical_value
    assert cube_pullback(targets[1]).contains_critical_value
    assert not cube_pullback(targets[2]).contains_critical_value

    assert reverse_cube_fibre(Fraction(-8)) == (Fraction(-2),)
    assert reverse_cube_fibre(Fraction(0)) == (Fraction(0),)
    assert reverse_cube_fibre(Fraction(27)) == (Fraction(3),)


def test_complexification_changes_the_generic_fibre_from_one_to_three() -> None:
    z = sympy.Symbol("z")
    omega = -sympy.Rational(1, 2) + sympy.sqrt(3) * sympy.I / 2
    roots = tuple(sympy.simplify(omega**power) for power in range(3))

    assert all(sympy.simplify(root**3 - 1) == 0 for root in roots)
    assert len({sympy.srepr(root) for root in roots}) == 3
    assert {
        sympy.srepr(sympy.simplify(omega * root))
        for root in roots
    } == {sympy.srepr(root) for root in roots}

    assert sympy.roots(z**3) == {sympy.Integer(0): 3}
    assert sum(sympy.roots(z**3 - 1).values()) == 3


def test_constructive_cube_has_three_occurrence_leaves_but_one_real_reverse_branch() -> None:
    cube = _workspace().function("triadic-cube", "cube")
    leaves, copy_events = _copy_tree(cube)

    assert len(leaves) == 3
    assert len(cube.source_partition) == 1
    source_members = set(next(iter(cube.source_partition.values())))
    assert leaves <= source_members

    outer = next(
        event
        for event in copy_events
        if any(
            other["parent"] in event["children"]
            for other in copy_events
            if other is not event
        )
    )
    inner = next(event for event in copy_events if event is not outer)

    first_split = cube.program_slice([], [outer["node"]])
    second_split = cube.program_slice([], [outer["node"], inner["node"]])
    assert first_split.certificate["event_difference"] == "checked"
    assert second_split.certificate["event_difference"] == "checked"
    assert len(first_split.result.lower_boundary) == 1
    assert len(first_split.result.upper_boundary) == 2
    assert len(second_split.result.upper_boundary) == 3

    value, gradient, certificate = cube.value_and_gradient({"x": 2.0})
    assert value == 8.0
    assert gradient == {"x": 12.0}
    assert set(certificate["operation_rules"]) == {
        "adva.builtin:copy@1",
        "adva.builtin:mul@1",
    }

    z = sympy.Symbol("z")
    degree_profile = (
        len(reverse_cube_fibre(Fraction(8))),
        len(
            cube_pullback(
                ExactOpenInterval(Fraction(1), Fraction(8))
            ).components
        ),
        len(leaves),
        sum(sympy.roots(z**3 - 1).values()),
    )
    assert degree_profile == (1, 1, 3, 3)


def test_scaling_and_sign_cross_cube_but_translation_uses_binomial_coaction() -> None:
    workspace = _workspace()
    cube_after_double = workspace.function(
        "triadic-cube", "cube-after-double"
    )
    scale_eight_after_cube = workspace.function(
        "triadic-cube", "scale-eight-after-cube"
    )
    cube_after_increment = workspace.function(
        "triadic-cube", "cube-after-increment"
    )

    x = sympy.Symbol("x", real=True)
    b = sympy.Symbol("b", real=True)

    assert sympy.simplify(
        cube_after_double.to_sympy() - scale_eight_after_cube.to_sympy()
    ) == 0
    assert cube_after_double.history != scale_eight_after_cube.history

    shifted = sympy.Poly(sympy.expand(cube_after_increment.to_sympy()), x)
    assert shifted.as_expr() == x**3 + 3 * x**2 + 3 * x + 1

    binomial_coaction = x**3 + 3 * b * x**2 + 3 * b**2 * x + b**3
    assert sympy.expand((x + b) ** 3 - binomial_coaction) == 0

    # Any former post-affine cube normal form a*x^3+c has zero x^2 and x
    # coefficients. Translation crossing therefore leaves that carrier.
    for scale in range(1, 6):
        for constant in range(5):
            candidate = sympy.Poly(scale * x**3 + constant, x)
            assert candidate != shifted


def test_nested_cube_calls_compress_a_dense_expanded_polynomial() -> None:
    function = _workspace().function(
        "triadic-cube",
        "shifted-twenty-seventh-power",
    )
    x = sympy.Symbol("x", real=True)
    expanded = sympy.Poly(sympy.expand(function.to_sympy()), x)
    high_level_calls = [
        (
            event["function"]["module"],
            event["function"]["function"],
        )
        for event in function.history["prefix"]
        if event["kind"] == "call"
        and event["function"]["function"] in {"increment", "cube"}
    ]

    assert expanded.degree() == 27
    assert len(expanded.terms()) == 28
    assert high_level_calls.count(("triadic-cube", "increment")) == 1
    assert high_level_calls.count(("triadic-cube", "cube")) == 3
    assert sympy.simplify(expanded.as_expr() - (x + 1) ** 27) == 0
