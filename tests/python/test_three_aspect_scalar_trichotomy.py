from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any

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
