from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Any

import sympy

from adva import link_modules


ELLIPTIC_ISOGENY_CONSTRUCTION = r"""
(module elliptic-isogeny-characteristics
  (export gaussian-two-x-projective eisenstein-three-x-projective)

  (def triple-copy-expanded
    (fn ((left Real) (right Real)) (outputs Real Real Real)
      (frontier
        (use left)
        (copy (use right)))))

  (def triple-copy
    (fn ((x Real)) (outputs Real Real Real)
      (call triple-copy-expanded
        (copy (use x)))))

  (def five-copy-expanded
    (fn ((left Real) (middle Real) (right Real))
      (outputs Real Real Real Real Real)
      (frontier
        (copy (use left))
        (copy (use middle))
        (use right))))

  (def five-copy
    (fn ((x Real)) (outputs Real Real Real Real Real)
      (call five-copy-expanded
        (call triple-copy (use x)))))

  (def gaussian-two-x-expanded
    (fn ((x0 Real) (x1 Real) (x2 Real)) (outputs Real Real)
      (frontier
        (add
          (mul (use x0) (use x1))
          (neg 25))
        (use x2))))

  (def gaussian-two-x-projective
    (fn ((x Real)) (outputs Real Real)
      (call gaussian-two-x-expanded
        (call triple-copy (use x)))))

  (def eisenstein-three-x-expanded
    (fn ((x0 Real) (x1 Real) (x2 Real) (x3 Real) (x4 Real))
      (outputs Real Real)
      (frontier
        (add
          (mul
            (mul (use x0) (use x1))
            (use x2))
          4)
        (mul (use x3) (use x4)))))

  (def eisenstein-three-x-projective
    (fn ((x Real)) (outputs Real Real)
      (call eisenstein-three-x-expanded
        (call five-copy (use x)))))
)
"""


@dataclass(frozen=True, slots=True)
class ShortWeierstrassCurve:
    """An exact short Weierstrass model ``y^2 = x^3 + A*x + B``."""

    linear: sympy.Expr
    constant: sympy.Expr

    def rhs(self, x_value: sympy.Expr) -> sympy.Expr:
        return x_value**3 + self.linear * x_value + self.constant

    def contains(self, point: tuple[sympy.Expr, sympy.Expr]) -> bool:
        x_value, y_value = point
        return sympy.simplify(y_value**2 - self.rhs(x_value)) == 0

    @property
    def j_invariant(self) -> sympy.Expr:
        numerator = sympy.Integer(1728) * 4 * self.linear**3
        denominator = 4 * self.linear**3 + 27 * self.constant**2
        return sympy.simplify(numerator / denominator)


@dataclass(frozen=True, slots=True)
class StandardIsogeny:
    """A research-local affine presentation of one separable isogeny."""

    name: str
    domain: ShortWeierstrassCurve
    codomain: ShortWeierstrassCurve
    x_map: sympy.Expr
    y_map: sympy.Expr
    degree: int
    kernel_size: int

    def maps_curve_symbolically(self, x: sympy.Symbol, y: sympy.Symbol) -> bool:
        relation = sympy.together(self.y_map**2 - self.codomain.rhs(self.x_map))
        numerator = sympy.expand(relation.as_numer_denom()[0])
        reduced = sympy.factor(numerator.subs(y**2, self.domain.rhs(x)))
        return reduced == 0

    def image(
        self,
        point: tuple[sympy.Expr, sympy.Expr],
        x: sympy.Symbol,
        y: sympy.Symbol,
    ) -> tuple[sympy.Expr, sympy.Expr]:
        substitutions = {x: point[0], y: point[1]}
        return (
            sympy.simplify(self.x_map.subs(substitutions)),
            sympy.simplify(self.y_map.subs(substitutions)),
        )

    def invariant_differential_multiplier(
        self,
        x: sympy.Symbol,
        y: sympy.Symbol,
    ) -> sympy.Expr:
        # Relative to omega = dx/(2y), pullback is X'(x)*y/Y * omega.
        return sympy.simplify(sympy.diff(self.x_map, x) * y / self.y_map)

    @property
    def x_coordinate_degree(self) -> int:
        numerator, denominator = sympy.cancel(self.x_map).as_numer_denom()
        return max(
            sympy.Poly(numerator, x).degree(),
            sympy.Poly(denominator, x).degree(),
        )


x, y = sympy.symbols("x y")
I = sympy.I
omega = -sympy.Rational(1, 2) + sympy.sqrt(3) * I / 2

E_EISENSTEIN = ShortWeierstrassCurve(sympy.Integer(0), sympy.Integer(1))
E_EISENSTEIN_THREE = ShortWeierstrassCurve(sympy.Integer(0), sympy.Integer(-27))
E_GAUSSIAN = ShortWeierstrassCurve(sympy.Integer(-25), sympy.Integer(0))
E_GAUSSIAN_TWO = ShortWeierstrassCurve(sympy.Integer(100), sympy.Integer(0))

DOUBLE = StandardIsogeny(
    name="[2]",
    domain=E_EISENSTEIN,
    codomain=E_EISENSTEIN,
    x_map=x * (x**3 - 8) / (4 * (x**3 + 1)),
    y_map=(x**6 + 20 * x**3 - 8) / (8 * y * (x**3 + 1)),
    degree=4,
    kernel_size=4,
)

GAUSSIAN_TWO = StandardIsogeny(
    name="phi_2",
    domain=E_GAUSSIAN,
    codomain=E_GAUSSIAN_TWO,
    x_map=(x**2 - 25) / x,
    y_map=y * (x**2 + 25) / x**2,
    degree=2,
    kernel_size=2,
)

EISENSTEIN_THREE = StandardIsogeny(
    name="phi_3",
    domain=E_EISENSTEIN,
    codomain=E_EISENSTEIN_THREE,
    x_map=(x**3 + 4) / x**2,
    y_map=y * (x**3 - 8) / x**3,
    degree=3,
    kernel_size=3,
)


def _workspace() -> Any:
    return link_modules([ELLIPTIC_ISOGENY_CONSTRUCTION])


def _lineage_profile(function: Any) -> tuple[int, ...]:
    return tuple(len(output["lineage"]) for output in function.ir["outputs"])


def test_three_explicit_isogenies_preserve_curves_and_compute_points() -> None:
    for isogeny in (DOUBLE, GAUSSIAN_TWO, EISENSTEIN_THREE):
        assert isogeny.maps_curve_symbolically(x, y)
        assert isogeny.x_coordinate_degree == isogeny.degree
        assert isogeny.kernel_size == isogeny.degree

    point = (sympy.Integer(2), sympy.Integer(3))
    assert E_EISENSTEIN.contains(point)
    doubled = DOUBLE.image(point, x, y)
    assert doubled == (sympy.Integer(0), sympy.Integer(1))
    assert E_EISENSTEIN.contains(doubled)

    gaussian_point = (sympy.Integer(-4), sympy.Integer(6))
    assert E_GAUSSIAN.contains(gaussian_point)
    gaussian_image = GAUSSIAN_TWO.image(gaussian_point, x, y)
    assert gaussian_image == (
        sympy.Rational(9, 4),
        sympy.Rational(123, 8),
    )
    assert E_GAUSSIAN_TWO.contains(gaussian_image)

    eisenstein_image = EISENSTEIN_THREE.image(point, x, y)
    assert eisenstein_image == (sympy.Integer(3), sympy.Integer(0))
    assert E_EISENSTEIN_THREE.contains(eisenstein_image)


def test_normalized_differentials_and_cm_reidentification() -> None:
    double_multiplier_residual = sympy.together(
        DOUBLE.invariant_differential_multiplier(x, y) - 2
    ).as_numer_denom()[0]
    assert sympy.factor(
        double_multiplier_residual.subs(y**2, E_EISENSTEIN.rhs(x))
    ) == 0
    assert GAUSSIAN_TWO.invariant_differential_multiplier(x, y) == 1
    assert EISENSTEIN_THREE.invariant_differential_multiplier(x, y) == 1

    assert E_GAUSSIAN.j_invariant == 1728
    assert E_GAUSSIAN_TWO.j_invariant == 1728
    assert E_EISENSTEIN.j_invariant == 0
    assert E_EISENSTEIN_THREE.j_invariant == 0

    # Reidentify the quotient models with their CM source curves.  For
    # (X,Y)=(u^2*x',u^3*y'), invariant differentials scale by u^(-1).
    gaussian_u = (1 - I) / 2
    assert sympy.simplify(100 * gaussian_u**4 + 25) == 0
    assert sympy.simplify(1 / gaussian_u - (1 + I)) == 0

    eisenstein_u = 1 / (1 - omega)
    assert sympy.simplify(-27 * eisenstein_u**6 - 1) == 0
    assert sympy.simplify(1 / eisenstein_u - (1 - omega)) == 0

    # The extra automorphisms exhibit the Gaussian and Eisenstein orders.
    gaussian_automorphism_residual = sympy.simplify(
        (I * y) ** 2 - E_GAUSSIAN.rhs(-x)
    ).subs(y**2, E_GAUSSIAN.rhs(x))
    assert sympy.simplify(gaussian_automorphism_residual) == 0

    eisenstein_automorphism_residual = sympy.simplify(
        y**2 - E_EISENSTEIN.rhs(omega * x)
    ).subs(y**2, E_EISENSTEIN.rhs(x))
    assert sympy.simplify(eisenstein_automorphism_residual) == 0


def test_lattice_matrices_match_norm_degree_and_dual_composition() -> None:
    scalar_two = sympy.Matrix([[2, 0], [0, 2]])
    scalar_two_dual = scalar_two

    gaussian = sympy.Matrix([[1, -1], [1, 1]])
    gaussian_dual = sympy.Matrix([[1, 1], [-1, 1]])

    eisenstein = sympy.Matrix([[1, 1], [-1, 2]])
    eisenstein_dual = sympy.Matrix([[2, -1], [1, 1]])

    fixtures = (
        (scalar_two, scalar_two_dual, 4),
        (gaussian, gaussian_dual, 2),
        (eisenstein, eisenstein_dual, 3),
    )
    for matrix, dual, degree in fixtures:
        assert matrix.det() == degree
        assert dual.det() == degree
        assert dual * matrix == degree * sympy.eye(2)
        assert matrix * dual == degree * sympy.eye(2)


def test_kernels_and_coordinate_degrees_are_typed_not_one_number() -> None:
    two_torsion_x = sympy.roots(x**3 + 1, x)
    assert sum(two_torsion_x.values()) == 3
    assert DOUBLE.kernel_size == 1 + sum(two_torsion_x.values())

    gaussian_kernel = (
        "O",
        (sympy.Integer(0), sympy.Integer(0)),
    )
    assert E_GAUSSIAN.contains(gaussian_kernel[1])
    assert len(gaussian_kernel) == GAUSSIAN_TWO.kernel_size

    eisenstein_kernel = (
        "O",
        (sympy.Integer(0), sympy.Integer(1)),
        (sympy.Integer(0), sympy.Integer(-1)),
    )
    assert all(E_EISENSTEIN.contains(point) for point in eisenstein_kernel[1:])
    assert len(eisenstein_kernel) == EISENSTEIN_THREE.kernel_size

    assert (
        DOUBLE.x_coordinate_degree,
        GAUSSIAN_TWO.x_coordinate_degree,
        EISENSTEIN_THREE.x_coordinate_degree,
    ) == (4, 2, 3)


def test_projective_coordinate_circuits_preserve_explicit_occurrences() -> None:
    workspace = _workspace()
    gaussian = workspace.function(
        "elliptic-isogeny-characteristics",
        "gaussian-two-x-projective",
    )
    eisenstein = workspace.function(
        "elliptic-isogeny-characteristics",
        "eisenstein-three-x-projective",
    )

    assert gaussian.validation_certificate["graph"] == "checked"
    assert eisenstein.validation_certificate["graph"] == "checked"

    gaussian_value = gaussian.evaluate({"x": -4.0})
    assert gaussian_value == (-9.0, -4.0)
    assert Fraction(str(gaussian_value[0])) / Fraction(
        str(gaussian_value[1])
    ) == Fraction(9, 4)

    eisenstein_value = eisenstein.evaluate({"x": 2.0})
    assert eisenstein_value == (12.0, 4.0)
    assert Fraction(str(eisenstein_value[0])) / Fraction(
        str(eisenstein_value[1])
    ) == Fraction(3)

    # Projective x-coordinate degree and constructive input multiplicity are
    # deliberately different typed quantities.
    assert _lineage_profile(gaussian) == (2, 1)
    assert _lineage_profile(eisenstein) == (3, 2)

    for function, expected_leaves in ((gaussian, 3), (eisenstein, 5)):
        output_lineages = [set(output["lineage"]) for output in function.ir["outputs"]]
        assert output_lineages[0].isdisjoint(output_lineages[1])
        leaves = output_lineages[0] | output_lineages[1]
        assert len(leaves) == expected_leaves
        assert len(function.source_partition) == 1
        source_members = set(next(iter(function.source_partition.values())))
        assert leaves <= source_members


def test_classical_feature_table_is_internally_consistent() -> None:
    rows = (
        {
            "name": "[2]",
            "temporal_scalar": sympy.Integer(2),
            "spatial_degree": 4,
            "kernel_size": 4,
            "coordinate_degree": DOUBLE.x_coordinate_degree,
        },
        {
            "name": "1+i",
            "temporal_scalar": 1 + I,
            "spatial_degree": 2,
            "kernel_size": 2,
            "coordinate_degree": GAUSSIAN_TWO.x_coordinate_degree,
        },
        {
            "name": "1-omega",
            "temporal_scalar": 1 - omega,
            "spatial_degree": 3,
            "kernel_size": 3,
            "coordinate_degree": EISENSTEIN_THREE.x_coordinate_degree,
        },
    )

    for row in rows:
        norm = sympy.simplify(
            row["temporal_scalar"] * sympy.conjugate(row["temporal_scalar"])
        )
        assert norm == row["spatial_degree"]
        assert row["spatial_degree"] == row["kernel_size"]
        assert row["spatial_degree"] == row["coordinate_degree"]
