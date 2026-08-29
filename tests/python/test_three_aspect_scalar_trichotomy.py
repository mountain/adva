from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

import pytest
import sympy
from adva import link_modules

SCALAR_TRICHOTOMY_KERNEL = r"""
(module scalar-trichotomy
  (export complex-product dual-product split-product)

  (def complex-product-expanded
    (fn
      ((a0 Real) (a1 Real) (b0 Real) (b1 Real)
       (c0 Real) (c1 Real) (d0 Real) (d1 Real))
      (outputs Real Real)
      (frontier
        (add
          (mul (use a0) (use c0))
          (neg (mul (use b0) (use d0))))
        (add
          (mul (use a1) (use d1))
          (mul (use b1) (use c1))))))

  (def dual-product-expanded
    (fn
      ((a0 Real) (a1 Real) (b0 Real) (b1 Real)
       (c0 Real) (c1 Real) (d0 Real) (d1 Real))
      (outputs Real Real)
      (frontier
        (add
          (mul (use a0) (use c0))
          (scale 0 (mul (use b0) (use d0))))
        (add
          (mul (use a1) (use d1))
          (mul (use b1) (use c1))))))

  (def split-product-expanded
    (fn
      ((a0 Real) (a1 Real) (b0 Real) (b1 Real)
       (c0 Real) (c1 Real) (d0 Real) (d1 Real))
      (outputs Real Real)
      (frontier
        (add
          (mul (use a0) (use c0))
          (mul (use b0) (use d0)))
        (add
          (mul (use a1) (use d1))
          (mul (use b1) (use c1))))))

  (def complex-product
    (fn ((a Real) (b Real) (c Real) (d Real)) (outputs Real Real)
      (call complex-product-expanded
        (frontier
          (copy (use a))
          (copy (use b))
          (copy (use c))
          (copy (use d))))))

  (def dual-product
    (fn ((a Real) (b Real) (c Real) (d Real)) (outputs Real Real)
      (call dual-product-expanded
        (frontier
          (copy (use a))
          (copy (use b))
          (copy (use c))
          (copy (use d))))))

  (def split-product
    (fn ((a Real) (b Real) (c Real) (d Real)) (outputs Real Real)
      (call split-product-expanded
        (frontier
          (copy (use a))
          (copy (use b))
          (copy (use c))
          (copy (use d))))))
)
"""


Scalar = tuple[float, float]


@dataclass(frozen=True, slots=True)
class CheckedQuadraticAlgebra:
    """A checked presentation of R[j]/(j^2-kappa)."""

    name: str
    kappa: int
    function: Any

    @property
    def unit(self) -> Scalar:
        return (1.0, 0.0)

    @property
    def generator(self) -> Scalar:
        return (0.0, 1.0)

    def multiply(self, left: Scalar, right: Scalar) -> Scalar:
        result = self.function.evaluate({"a": left[0], "b": left[1], "c": right[0], "d": right[1]})
        if not isinstance(result, tuple) or len(result) != 2:
            raise TypeError("quadratic product must have an ordered two-Real frontier")
        return result

    def conjugate(self, value: Scalar) -> Scalar:
        return (value[0], -value[1])

    def norm(self, value: Scalar) -> float:
        return value[0] * value[0] - self.kappa * value[1] * value[1]

    def inverse(self, value: Scalar) -> Scalar | None:
        norm = self.norm(value)
        if norm == 0.0:
            return None
        return (value[0] / norm, -value[1] / norm)

    def negative_inverse(self, value: Scalar) -> Scalar | None:
        inverse = self.inverse(value)
        if inverse is None:
            return None
        return (-inverse[0], -inverse[1])

    def divide(self, numerator: Scalar, denominator: Scalar) -> Scalar:
        inverse = self.inverse(denominator)
        if inverse is None:
            raise ZeroDivisionError("quadratic scalar denominator is non-invertible")
        return self.multiply(numerator, inverse)

    def left_action(self, characteristic: Scalar, argument: Scalar) -> Scalar:
        """The rank-one function whose characteristic is recovered at 1."""

        return self.multiply(characteristic, argument)


@dataclass(frozen=True, slots=True)
class ThreeAspectUnits:
    """One cyclic rank-one model of temporal, spatial, and relational units."""

    temporal: Scalar
    spatial: Scalar
    relational: Scalar

    def cycle_characteristic(self, algebra: CheckedQuadraticAlgebra) -> Scalar:
        return algebra.multiply(
            self.relational,
            algebra.multiply(self.spatial, self.temporal),
        )

    def cycle_action(
        self,
        algebra: CheckedQuadraticAlgebra,
        argument: Scalar,
    ) -> Scalar:
        after_temporal = algebra.left_action(self.temporal, argument)
        after_spatial = algebra.left_action(self.spatial, after_temporal)
        return algebra.left_action(self.relational, after_spatial)


def _algebras() -> tuple[CheckedQuadraticAlgebra, ...]:
    workspace = link_modules([SCALAR_TRICHOTOMY_KERNEL])
    return (
        CheckedQuadraticAlgebra(
            "complex",
            -1,
            workspace.function("scalar-trichotomy", "complex-product"),
        ),
        CheckedQuadraticAlgebra(
            "dual",
            0,
            workspace.function("scalar-trichotomy", "dual-product"),
        ),
        CheckedQuadraticAlgebra(
            "split",
            1,
            workspace.function("scalar-trichotomy", "split-product"),
        ),
    )


def _expected(kappa: int, left: Scalar, right: Scalar) -> Scalar:
    a, b = left
    c, d = right
    return (a * c + kappa * b * d, a * d + b * c)


def test_two_by_two_by_two_rank_one_closure_does_not_select_complex() -> None:
    fixtures = (
        ((2.0, 3.0), (-1.0, 4.0)),
        ((0.0, 1.0), (0.0, 1.0)),
        ((-2.0, 1.0), (3.0, -2.0)),
    )
    units = ThreeAspectUnits(
        temporal=(1.0, 1.0),
        spatial=(2.0, -1.0),
        relational=(-1.0, 2.0),
    )
    argument = (3.0, -2.0)

    for algebra in _algebras():
        assert algebra.function.validation_certificate["graph"] == "checked"
        assert algebra.function.signature.inputs == (
            ("a", "real"),
            ("b", "real"),
            ("c", "real"),
            ("d", "real"),
        )
        assert algebra.function.signature.outputs == ("real", "real")
        for left, right in fixtures:
            assert algebra.multiply(left, right) == _expected(algebra.kappa, left, right)
        assert algebra.left_action(units.temporal, algebra.unit) == units.temporal
        assert units.cycle_action(algebra, argument) == algebra.left_action(
            units.cycle_characteristic(algebra),
            argument,
        )


def test_conjugation_and_multiplicative_norm_still_do_not_select_complex() -> None:
    samples = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (2.0, -3.0))
    for algebra in _algebras():
        for left, right in product(samples, repeat=2):
            multiplied = algebra.multiply(left, right)
            assert algebra.conjugate(multiplied) == algebra.multiply(
                algebra.conjugate(left),
                algebra.conjugate(right),
            )
            assert algebra.norm(multiplied) == algebra.norm(left) * algebra.norm(right)


def test_extra_nondegeneracy_conditions_distinguish_the_three_algebras() -> None:
    complex_algebra, dual_algebra, split_algebra = _algebras()

    # Complex: the tested quadratic norm is positive on every nonzero lattice
    # point.  The accompanying note records the elementary unrestricted proof.
    lattice = tuple(
        (float(a), float(b)) for a, b in product(range(-3, 4), repeat=2) if (a, b) != (0, 0)
    )
    assert all(complex_algebra.norm(value) > 0 for value in lattice)

    # Dual: the nonzero generator is nilpotent, so the norm is degenerate.
    assert dual_algebra.generator != (0.0, 0.0)
    assert dual_algebra.multiply(dual_algebra.generator, dual_algebra.generator) == (
        0.0,
        0.0,
    )
    assert dual_algebra.norm(dual_algebra.generator) == 0.0

    # Split: two nonzero lightlike elements multiply to zero, and the norm is
    # indefinite rather than positive.
    positive = (1.0, 1.0)
    negative = (1.0, -1.0)
    assert split_algebra.multiply(positive, negative) == (0.0, 0.0)
    assert split_algebra.norm(positive) == 0.0
    assert split_algebra.norm((0.0, 1.0)) < 0.0


def test_symbolic_norm_forms_expose_elliptic_parabolic_hyperbolic_trichotomy() -> None:
    a, b = sympy.symbols("a b", real=True)
    forms = {algebra.name: sympy.expand(a**2 - algebra.kappa * b**2) for algebra in _algebras()}
    assert forms == {
        "complex": a**2 + b**2,
        "dual": a**2,
        "split": a**2 - b**2,
    }


def test_global_minus_inverse_on_the_punctured_plane_selects_complex() -> None:
    complex_algebra, dual_algebra, split_algebra = _algebras()
    nonzero_lattice = tuple(
        (float(a), float(b)) for a, b in product(range(-3, 4), repeat=2) if (a, b) != (0, 0)
    )

    assert all(complex_algebra.negative_inverse(value) is not None for value in nonzero_lattice)
    for value in ((0.0, 1.0), (1.0, 2.0), (-2.0, 3.0)):
        transformed = complex_algebra.negative_inverse(value)
        assert transformed is not None
        assert transformed[1] > 0.0
        assert complex_algebra.multiply(value, transformed) == pytest.approx((-1.0, 0.0))
        assert complex_algebra.negative_inverse(transformed) == pytest.approx(value)

    # Dual inversion is undefined on the nonzero nilpotent axis.
    assert dual_algebra.negative_inverse(dual_algebra.generator) is None

    # Split inversion is undefined on both nonzero light rays.  Away from the
    # rays it can also reverse the sign of the second component, so it does not
    # preserve one global upper-half-plane chart.
    assert split_algebra.negative_inverse((1.0, 1.0)) is None
    assert split_algebra.negative_inverse((1.0, -1.0)) is None
    assert split_algebra.negative_inverse((0.0, 1.0)) == (0.0, -1.0)


def test_minus_inverse_changes_aeg_frame_chirality_not_plane_orientation() -> None:
    complex_algebra = _algebras()[0]
    value = (2.0, 1.0)
    scale = 3.0

    first_inversion = complex_algebra.negative_inverse(value)
    assert first_inversion is not None
    scaled = (scale * first_inversion[0], scale * first_inversion[1])
    conjugated_scale = complex_algebra.negative_inverse(scaled)
    assert conjugated_scale == pytest.approx((value[0] / scale, value[1] / scale))

    # S A S is the parabolic ripple chart z/(1-z), where A(z)=z+1.
    translated = (first_inversion[0] + 1.0, first_inversion[1])
    conjugated_translation = complex_algebra.negative_inverse(translated)
    ripple = complex_algebra.divide(value, (1.0 - value[0], -value[1]))
    assert conjugated_translation == pytest.approx(ripple)

    # The Möbius involution is holomorphic and hence preserves the ambient
    # real-plane orientation.  The chirality reversal above belongs to the
    # ordered AEG generator frame because scale is sent to inverse scale.
    x, y = sympy.symbols("x y", real=True)
    radius_squared = x**2 + y**2
    real_part = -x / radius_squared
    imaginary_part = y / radius_squared
    jacobian = sympy.Matrix(
        [
            [sympy.diff(real_part, x), sympy.diff(real_part, y)],
            [sympy.diff(imaginary_part, x), sympy.diff(imaginary_part, y)],
        ]
    )
    assert sympy.simplify(jacobian.det() - 1 / radius_squared**2) == 0


def test_projective_time_space_swap_has_two_oriented_lift_directions() -> None:
    time, space = sympy.symbols("time space", nonzero=True, real=True)
    oriented_swap = sympy.Matrix([[0, -1], [1, 0]])
    identity = sympy.eye(2)

    # The oriented lift has order four.  Its inverse differs by the central
    # sign that projectivization forgets.
    assert oriented_swap**2 == -identity
    assert oriented_swap.inv() == -oriented_swap

    homogeneous = sympy.Matrix([time, space])
    forward = oriented_swap * homogeneous
    backward = oriented_swap.inv() * homogeneous
    forward_projective = sympy.simplify(forward[0] / forward[1])
    backward_projective = sympy.simplify(backward[0] / backward[1])
    assert forward_projective == -space / time
    assert backward_projective == -space / time

    # A bare split swap has square +I and equals its own inverse already in
    # the oriented lift, so it cannot retain the forward/backward central sign.
    split_swap = sympy.Matrix([[0, 1], [1, 0]])
    assert split_swap**2 == identity
    assert split_swap.inv() == split_swap

    # The three quadratic generators act by matrices whose squares are
    # respectively -I, 0, and +I.  Only the complex generator is an
    # orientation-preserving order-four lift of the projective exchange.
    dual_generator = sympy.Matrix([[0, 0], [1, 0]])
    assert dual_generator**2 == sympy.zeros(2)
    assert dual_generator.det() == 0
    assert oriented_swap.det() == 1
    assert split_swap.det() == -1
