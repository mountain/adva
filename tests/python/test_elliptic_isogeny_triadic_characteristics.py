from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

import sympy

from adva import link_modules


ELLIPTIC_ISOGENY_CALIBRATION = r"""
(module elliptic-isogeny
  (export
    duplication-x-projective
    gaussian-two-x-projective
    eisenstein-three-x-projective)

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

  (def duplication-x-from-cube
    (fn ((x Real) (cube-num Real) (cube-den Real))
        (outputs Real Real)
      (frontier
        (mul
          (use x)
          (add (use cube-num) (neg 8)))
        (scale 4
          (add (use cube-den) 1)))))

  (def duplication-x-seed
    (fn ((x-num Real) (x-cube Real)) (outputs Real Real)
      (call duplication-x-from-cube
        (frontier
          (use x-num)
          (copy
            (call cube (use x-cube)))))))

  (def duplication-x-projective
    (fn ((x Real)) (outputs Real Real)
      (call duplication-x-seed
        (copy (use x)))))

  (def gaussian-two-x-expanded
    (fn ((x0 Real) (x1 Real) (x-den Real))
        (outputs Real Real)
      (frontier
        (add
          (mul (use x0) (use x1))
          (neg 25))
        (use x-den))))

  (def gaussian-two-x-projective
    (fn ((x Real)) (outputs Real Real)
      (call gaussian-two-x-expanded
        (call triple-copy-expanded
          (copy (use x))))))

  (def eisenstein-three-x-from-square
    (fn ((x Real) (square-num Real) (square-den Real))
        (outputs Real Real)
      (frontier
        (add
          (mul (use x) (use square-num))
          4)
        (use square-den))))

  (def eisenstein-three-x-seed
    (fn ((x-cube Real) (x-square Real))
        (outputs Real Real)
      (call eisenstein-three-x-from-square
        (frontier
          (use x-cube)
          (copy
            (call square (use x-square)))))))

  (def eisenstein-three-x-projective
    (fn ((x Real)) (outputs Real Real)
      (call eisenstein-three-x-seed
        (copy (use x)))))
)
"""


Point = tuple[Fraction, Fraction] | None


@dataclass(frozen=True, slots=True)
class ShortWeierstrassCurve:
    """An exact short Weierstrass model ``y^2=x^3+a*x+b``."""

    a: Fraction
    b: Fraction

    def contains(self, point: Point) -> bool:
        if point is None:
            return True
        x, y = point
        return y * y == x**3 + self.a * x + self.b

    def double(self, point: Point) -> Point:
        if point is None:
            return None
        x, y = point
        if y == 0:
            return None
        slope = (3 * x * x + self.a) / (2 * y)
        x2 = slope * slope - 2 * x
        y2 = slope * (x - x2) - y
        result = (x2, y2)
        if not self.contains(result):
            raise AssertionError("doubling left the curve")
        return result


def _j_invariant(curve: ShortWeierstrassCurve) -> Fraction:
    denominator = 4 * curve.a**3 + 27 * curve.b**2
    if denominator == 0:
        raise ValueError("singular cubic")
    return Fraction(1728) * 4 * curve.a**3 / denominator


@dataclass(frozen=True, slots=True)
class IsogenyProfile:
    """A bounded cross-domain profile for one classical isogeny."""

    name: str
    tangent_multiplier: sympy.Expr
    lattice_matrix: sympy.Matrix
    dual_lattice_matrix: sympy.Matrix
    kernel_order: int

    @property
    def degree(self) -> int:
        return abs(int(self.lattice_matrix.det()))

    def norm(self) -> sympy.Expr:
        return sympy.simplify(
            self.tangent_multiplier
            * sympy.conjugate(self.tangent_multiplier)
        )


def _workspace() -> Any:
    return link_modules([ELLIPTIC_ISOGENY_CALIBRATION])


def _reduce_on_curve(
    expression: sympy.Expr,
    *,
    x: sympy.Symbol,
    y: sympy.Symbol,
    a: int,
    b: int,
) -> sympy.Expr:
    numerator, denominator = sympy.fraction(sympy.together(expression))
    reduced = sympy.rem(
        sympy.Poly(numerator, y),
        sympy.Poly(y**2 - (x**3 + a * x + b), y),
    ).as_expr()
    return sympy.simplify(reduced / denominator)


def _assert_rational_map(
    *,
    source_a: int,
    source_b: int,
    target_a: int,
    target_b: int,
    x_map: sympy.Expr,
    y_map: sympy.Expr,
) -> None:
    x, y = sympy.symbols("x y", real=True)
    residual = y_map**2 - (
        x_map**3 + target_a * x_map + target_b
    )
    assert _reduce_on_curve(
        residual,
        x=x,
        y=y,
        a=source_a,
        b=source_b,
    ) == 0


def _differential_multiplier(
    *,
    source_a: int,
    source_b: int,
    x_map: sympy.Expr,
    y_map: sympy.Expr,
) -> sympy.Expr:
    x, y = sympy.symbols("x y", real=True)
    ratio = sympy.diff(x_map, x) * y / y_map
    return _reduce_on_curve(
        ratio,
        x=x,
        y=y,
        a=source_a,
        b=source_b,
    )


def _duplication(point: Point) -> Point:
    if point is None:
        return None
    x, y = point
    if y == 0:
        return None
    denominator = 4 * (x**3 + 1)
    return (
        x * (x**3 - 8) / denominator,
        (x**6 + 20 * x**3 - 8) / (8 * y * (x**3 + 1)),
    )


def _gaussian_two_isogeny(point: Point) -> Point:
    if point is None:
        return None
    x, y = point
    if x == 0:
        return None
    return (
        (x * x - 25) / x,
        y * (x * x + 25) / (x * x),
    )


def _eisenstein_three_isogeny(point: Point) -> Point:
    if point is None:
        return None
    x, y = point
    if x == 0:
        return None
    return (
        (x**3 + 4) / (x * x),
        y * (x**3 - 8) / (x**3),
    )


def test_multiplication_by_two_is_one_feature_in_three_classical_readings() -> None:
    curve = ShortWeierstrassCurve(Fraction(0), Fraction(1))
    point = (Fraction(2), Fraction(3))
    assert _j_invariant(curve) == 0
    assert curve.contains(point)
    assert curve.double(point) == (Fraction(0), Fraction(1))
    assert _duplication(point) == curve.double(point)

    x, y = sympy.symbols("x y", real=True)
    x_map = x * (x**3 - 8) / (4 * (x**3 + 1))
    y_map = (x**6 + 20 * x**3 - 8) / (
        8 * y * (x**3 + 1)
    )
    _assert_rational_map(
        source_a=0,
        source_b=1,
        target_a=0,
        target_b=1,
        x_map=x_map,
        y_map=y_map,
    )
    assert _differential_multiplier(
        source_a=0,
        source_b=1,
        x_map=x_map,
        y_map=y_map,
    ) == 2

    profile = IsogenyProfile(
        name="[2]",
        tangent_multiplier=sympy.Integer(2),
        lattice_matrix=sympy.Matrix([[2, 0], [0, 2]]),
        dual_lattice_matrix=sympy.Matrix([[2, 0], [0, 2]]),
        kernel_order=4,
    )
    assert profile.degree == profile.kernel_order == 4
    assert profile.norm() == 4
    assert (
        profile.dual_lattice_matrix * profile.lattice_matrix
        == 4 * sympy.eye(2)
    )

    # The three finite x-coordinates of nonzero 2-torsion solve x^3+1=0;
    # the point at infinity is the fourth kernel point.
    assert sum(sympy.roots(x**3 + 1).values()) + 1 == 4

    numerator, denominator = _workspace().function(
        "elliptic-isogeny", "duplication-x-projective"
    ).to_sympy()
    assert sympy.expand(numerator - x * (x**3 - 8)) == 0
    assert sympy.expand(denominator - 4 * (x**3 + 1)) == 0
    assert sympy.simplify(numerator / denominator - x_map) == 0


def test_lemniscatic_two_isogeny_matches_gaussian_norm_two() -> None:
    source = ShortWeierstrassCurve(Fraction(-25), Fraction(0))
    target = ShortWeierstrassCurve(Fraction(100), Fraction(0))
    point = (Fraction(-4), Fraction(6))
    image = (Fraction(9, 4), Fraction(123, 8))

    assert _j_invariant(source) == 1728
    assert _j_invariant(target) == 1728
    assert source.contains(point)
    assert target.contains(image)
    assert _gaussian_two_isogeny(point) == image
    assert _gaussian_two_isogeny((Fraction(0), Fraction(0))) is None

    x, y = sympy.symbols("x y", real=True)
    x_map = (x**2 - 25) / x
    y_map = y * (x**2 + 25) / x**2
    _assert_rational_map(
        source_a=-25,
        source_b=0,
        target_a=100,
        target_b=0,
        x_map=x_map,
        y_map=y_map,
    )
    assert _differential_multiplier(
        source_a=-25,
        source_b=0,
        x_map=x_map,
        y_map=y_map,
    ) == 1

    gaussian = IsogenyProfile(
        name="1+i",
        tangent_multiplier=1 + sympy.I,
        lattice_matrix=sympy.Matrix([[1, -1], [1, 1]]),
        dual_lattice_matrix=sympy.Matrix([[1, 1], [-1, 1]]),
        kernel_order=2,
    )
    assert gaussian.degree == gaussian.kernel_order == 2
    assert gaussian.norm() == 2
    assert (
        gaussian.dual_lattice_matrix * gaussian.lattice_matrix
        == 2 * sympy.eye(2)
    )

    # The quotient model y^2=x^3+100*x is carried back to the source
    # CM model by (x,y) |-> (u^2*x,u^3*y), with u=(1-i)/2.
    # The normalized quotient map has differential multiplier 1, while
    # the composite endomorphism has multiplier u^{-1}=1+i.
    u = (1 - sympy.I) / 2
    assert sympy.simplify(100 * u**4 + 25) == 0
    assert sympy.simplify(1 / u - (1 + sympy.I)) == 0

    numerator, denominator = _workspace().function(
        "elliptic-isogeny", "gaussian-two-x-projective"
    ).to_sympy()
    assert sympy.expand(numerator - (x**2 - 25)) == 0
    assert denominator == x
    assert sympy.simplify(numerator / denominator - x_map) == 0


def test_equianharmonic_three_isogeny_matches_eisenstein_norm_three() -> None:
    source = ShortWeierstrassCurve(Fraction(0), Fraction(1))
    target = ShortWeierstrassCurve(Fraction(0), Fraction(-27))
    point = (Fraction(2), Fraction(3))
    image = (Fraction(3), Fraction(0))

    assert _j_invariant(source) == 0
    assert _j_invariant(target) == 0
    assert source.contains(point)
    assert target.contains(image)
    assert _eisenstein_three_isogeny(point) == image
    assert _eisenstein_three_isogeny(
        (Fraction(0), Fraction(1))
    ) is None
    assert _eisenstein_three_isogeny(
        (Fraction(0), Fraction(-1))
    ) is None

    x, y = sympy.symbols("x y", real=True)
    x_map = (x**3 + 4) / x**2
    y_map = y * (x**3 - 8) / x**3
    _assert_rational_map(
        source_a=0,
        source_b=1,
        target_a=0,
        target_b=-27,
        x_map=x_map,
        y_map=y_map,
    )
    assert _differential_multiplier(
        source_a=0,
        source_b=1,
        x_map=x_map,
        y_map=y_map,
    ) == 1

    omega = -sympy.Rational(1, 2) + sympy.sqrt(3) * sympy.I / 2
    eisenstein = IsogenyProfile(
        name="1-omega",
        tangent_multiplier=1 - omega,
        lattice_matrix=sympy.Matrix([[1, 1], [-1, 2]]),
        dual_lattice_matrix=sympy.Matrix([[2, -1], [1, 1]]),
        kernel_order=3,
    )
    assert eisenstein.degree == eisenstein.kernel_order == 3
    assert sympy.simplify(eisenstein.norm() - 3) == 0
    assert (
        eisenstein.dual_lattice_matrix
        * eisenstein.lattice_matrix
        == 3 * sympy.eye(2)
    )

    # The quotient model y^2=x^3-27 is carried back to y^2=x^3+1
    # by u=1/(1-omega). The composite CM endomorphism has multiplier
    # 1-omega.
    u = 1 / (1 - omega)
    assert sympy.simplify(-27 * u**6 - 1) == 0
    assert sympy.simplify(1 / u - (1 - omega)) == 0

    numerator, denominator = _workspace().function(
        "elliptic-isogeny", "eisenstein-three-x-projective"
    ).to_sympy()
    assert sympy.expand(numerator - (x**3 + 4)) == 0
    assert sympy.expand(denominator - x**2) == 0
    assert sympy.simplify(numerator / denominator - x_map) == 0


def test_generic_x_fibre_degree_matches_lattice_index_in_all_three_examples() -> None:
    x, target_x = sympy.symbols("x target_x", real=True)
    projective_pairs = (
        (
            x * (x**3 - 8),
            4 * (x**3 + 1),
            4,
        ),
        (
            x**2 - 25,
            x,
            2,
        ),
        (
            x**3 + 4,
            x**2,
            3,
        ),
    )

    for numerator, denominator, degree in projective_pairs:
        fibre_polynomial = sympy.Poly(
            sympy.expand(numerator - target_x * denominator),
            x,
        )
        assert fibre_polynomial.degree() == degree


def test_dual_isogeny_is_not_an_inverse_but_closes_at_degree_scaling() -> None:
    omega = -sympy.Rational(1, 2) + sympy.sqrt(3) * sympy.I / 2
    profiles = (
        IsogenyProfile(
            "[2]",
            sympy.Integer(2),
            sympy.Matrix([[2, 0], [0, 2]]),
            sympy.Matrix([[2, 0], [0, 2]]),
            4,
        ),
        IsogenyProfile(
            "1+i",
            1 + sympy.I,
            sympy.Matrix([[1, -1], [1, 1]]),
            sympy.Matrix([[1, 1], [-1, 1]]),
            2,
        ),
        IsogenyProfile(
            "1-omega",
            1 - omega,
            sympy.Matrix([[1, 1], [-1, 2]]),
            sympy.Matrix([[2, -1], [1, 1]]),
            3,
        ),
    )

    for profile in profiles:
        assert profile.degree == profile.kernel_order
        assert (
            profile.dual_lattice_matrix * profile.lattice_matrix
            == profile.degree * sympy.eye(2)
        )
        assert profile.lattice_matrix.det() != 1
