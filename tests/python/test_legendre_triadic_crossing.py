from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import sympy

from adva import link_modules


LEGENDRE_CROSSING = r"""
(module legendre-triadic-crossing
  (export
    legendre-affine
    legendre-at-zero
    legendre-at-one
    cusp-zero-factorized
    cusp-one-factorized)

  (def triple-copy-expanded
    (fn ((left Real) (right Real)) (outputs Real Real Real)
      (frontier
        (use left)
        (copy (use right)))))

  (def triple-copy
    (fn ((x Real)) (outputs Real Real Real)
      (call triple-copy-expanded
        (copy (use x)))))

  (def legendre-affine-expanded
    (fn ((x0 Real) (x1 Real) (x2 Real) (parameter Real)) Real
      (mul
        (mul
          (use x0)
          (add (use x1) (neg 1)))
        (add (use x2) (neg (use parameter))))))

  (def legendre-affine
    (fn ((x Real) (parameter Real)) Real
      (call legendre-affine-expanded
        (frontier
          (call triple-copy (use x))
          (use parameter)))))

  (def legendre-at-zero
    (fn ((x Real)) Real
      (call legendre-affine
        (frontier (use x) 0))))

  (def legendre-at-one
    (fn ((x Real)) Real
      (call legendre-affine
        (frontier (use x) 1))))

  (def cusp-zero-expanded
    (fn ((x0 Real) (x1 Real) (x2 Real)) Real
      (mul
        (mul (use x0) (use x1))
        (add (use x2) (neg 1)))))

  (def cusp-zero-factorized
    (fn ((x Real)) Real
      (call cusp-zero-expanded
        (call triple-copy (use x)))))

  (def cusp-one-expanded
    (fn ((x0 Real) (x1 Real) (x2 Real)) Real
      (mul
        (use x0)
        (mul
          (add (use x1) (neg 1))
          (add (use x2) (neg 1))))))

  (def cusp-one-factorized
    (fn ((x Real)) Real
      (call cusp-one-expanded
        (call triple-copy (use x)))))
)
"""


@dataclass(frozen=True, slots=True)
class CuspCrossing:
    """One bounded three-domain reading of a Legendre cusp."""

    name: str
    collision_factor: sympy.Expr
    vanishing_cycle: sympy.Matrix
    primitive_twist: sympy.Matrix
    unipotent_lift: sympy.Matrix
    actual_monodromy: sympy.Matrix


def _workspace() -> Any:
    return link_modules([LEGENDRE_CROSSING])


J = sympy.Matrix([[0, 1], [-1, 0]])
IDENTITY = sympy.eye(2)
NEGATIVE_IDENTITY = -IDENTITY


def _intersection(left: sympy.Matrix, right: sympy.Matrix) -> sympy.Expr:
    return sympy.expand((left.T * J * right)[0])


def _primitive_twist(delta: sympy.Matrix) -> sympy.Matrix:
    """A fixed column-vector convention for a positive Dehn transvection."""

    return IDENTITY - delta * (J * delta).T


def _projectively_equal(left: sympy.Matrix, right: sympy.Matrix) -> bool:
    return left == right or left == -right


def _output_source_contributions(function: Any) -> tuple[int, ...]:
    output_lineage = set(function.ir["outputs"][0]["lineage"])
    return tuple(
        sorted(
            len(output_lineage & set(occurrences))
            for occurrences in function.source_partition.values()
        )
    )


def test_legendre_discriminant_and_j_detect_the_three_cusps() -> None:
    x, parameter, mu = sympy.symbols("x parameter mu")
    cubic = x * (x - 1) * (x - parameter)

    discriminant = sympy.factor(sympy.discriminant(cubic, x))
    assert sympy.simplify(
        discriminant - parameter**2 * (parameter - 1) ** 2
    ) == 0

    j_invariant = sympy.factor(
        256
        * (1 - parameter + parameter**2) ** 3
        / (parameter**2 * (1 - parameter) ** 2)
    )

    assert sympy.limit(parameter**2 * j_invariant, parameter, 0) == 256
    assert sympy.limit((parameter - 1) ** 2 * j_invariant, parameter, 1) == 256
    assert sympy.limit(
        mu**2 * j_invariant.subs(parameter, 1 / mu),
        mu,
        0,
    ) == 256

    # The anharmonic transformations permute branch-point charts while
    # retaining the same elliptic isomorphism class.
    assert sympy.simplify(j_invariant.subs(parameter, 1 - parameter) - j_invariant) == 0
    assert sympy.simplify(j_invariant.subs(parameter, 1 / parameter) - j_invariant) == 0


def test_binary_quartic_exhibits_three_typed_factor_collisions() -> None:
    X, Z, parameter, mu = sympy.symbols("X Z parameter mu")
    branch_quartic = X * (X - Z) * (X - parameter * Z) * Z

    cusp_zero = sympy.factor(branch_quartic.subs(parameter, 0))
    cusp_one = sympy.factor(branch_quartic.subs(parameter, 1))
    infinity_chart = sympy.factor(
        mu * branch_quartic.subs(parameter, 1 / mu)
    )
    cusp_infinity = sympy.factor(sympy.limit(infinity_chart, mu, 0))

    assert cusp_zero == X**2 * Z * (X - Z)
    assert cusp_one == X * Z * (X - Z) ** 2
    assert cusp_infinity == -X * Z**2 * (X - Z)

    # The repeated linear factors identify the branch-point collisions at
    # 0, 1, and infinity respectively.  They are construction-side data,
    # not yet homology classes or period matrices.
    assert sympy.Poly(cusp_zero, X, Z).total_degree() == 4
    assert sympy.Poly(cusp_one, X, Z).total_degree() == 4
    assert sympy.Poly(cusp_infinity, X, Z).total_degree() == 4


def test_picard_fuchs_period_has_exact_three_regular_singular_locations() -> None:
    parameter = sympy.symbols("parameter")
    period = sympy.hyper(
        [sympy.Rational(1, 2), sympy.Rational(1, 2)],
        [1],
        parameter,
    )

    picard_fuchs = (
        parameter * (1 - parameter) * sympy.diff(period, parameter, 2)
        + (1 - 2 * parameter) * sympy.diff(period, parameter)
        - sympy.Rational(1, 4) * period
    )
    assert sympy.simplify(picard_fuchs) == 0

    leading_coefficient = sympy.factor(parameter * (1 - parameter))
    assert sympy.solve(leading_coefficient, parameter) == [0, 1]
    # The third singular location is the point at infinity of P^1.
    mu = sympy.symbols("mu")
    assert sympy.degree(
        sympy.together(leading_coefficient.subs(parameter, 1 / mu)).as_numer_denom()[1],
        mu,
    ) > 0


def test_vanishing_cycles_generate_the_three_cusp_monodromies() -> None:
    delta_zero = sympy.Matrix([1, 0])
    delta_one = sympy.Matrix([0, 1])
    delta_infinity = -delta_zero - delta_one

    assert delta_zero + delta_one + delta_infinity == sympy.zeros(2, 1)
    assert _intersection(delta_zero, delta_one) == 1
    assert _intersection(delta_one, delta_infinity) == 1
    assert _intersection(delta_infinity, delta_zero) == 1

    twists = tuple(
        _primitive_twist(delta)
        for delta in (delta_zero, delta_one, delta_infinity)
    )
    unipotent_lifts = tuple(twist**2 for twist in twists)

    for delta, twist, lift in zip(
        (delta_zero, delta_one, delta_infinity),
        twists,
        unipotent_lifts,
    ):
        assert twist.det() == 1
        assert twist.T * J * twist == J
        assert twist * delta == delta
        assert lift == IDENTITY - 2 * delta * (J * delta).T
        assert lift * delta == delta

    U_zero, U_one, U_infinity = unipotent_lifts
    assert U_zero == sympy.Matrix([[1, 2], [0, 1]])
    assert U_one == sympy.Matrix([[1, 0], [-2, 1]])
    assert U_infinity == sympy.Matrix([[-1, 2], [-2, 3]])

    # Choosing trace +2 unipotent representatives at all three projective
    # cusps leaves a central sign in the SL(2,Z) lift.
    assert U_zero * U_one * U_infinity == NEGATIVE_IDENTITY

    # A compatible H_1 monodromy convention absorbs that sign into the
    # infinity matrix.  The fundamental-group relation then closes exactly.
    M_zero = U_zero
    M_one = U_one
    M_infinity = -U_infinity
    assert M_zero * M_one * M_infinity == IDENTITY
    assert _projectively_equal(M_infinity, U_infinity)
    assert M_infinity * delta_infinity == -delta_infinity


def test_branch_braid_dehn_twist_and_period_action_form_one_crossing_chain() -> None:
    delta_zero = sympy.Matrix([1, 0])
    delta_one = sympy.Matrix([0, 1])
    L_zero = _primitive_twist(delta_zero)
    L_one = _primitive_twist(delta_one)

    # The two primitive crossing generators satisfy the B_3 braid relation.
    assert L_zero * L_one * L_zero == L_one * L_zero * L_one

    # The centre of B_3 acts as the deck sign on the lifted homology lattice.
    assert (L_zero * L_one) ** 3 == NEGATIVE_IDENTITY
    assert (L_zero * L_one) ** 6 == IDENTITY

    # A full labelled branch-point circuit gives the squared Dehn action used
    # by the cusp monodromy above.
    assert L_zero**2 == sympy.Matrix([[1, 2], [0, 1]])
    assert L_one**2 == sympy.Matrix([[1, 0], [-2, 1]])

    # Moving a crossing through another transport changes its vanishing label
    # by conjugation rather than commuting it unchanged.
    transported_delta = L_one * delta_zero
    assert _primitive_twist(transported_delta) == (
        L_one * L_zero * L_one.inv()
    )


def test_adva_preserves_generic_and_specialized_construction_histories() -> None:
    workspace = _workspace()
    generic = workspace.function(
        "legendre-triadic-crossing",
        "legendre-affine",
    )
    at_zero = workspace.function(
        "legendre-triadic-crossing",
        "legendre-at-zero",
    )
    at_one = workspace.function(
        "legendre-triadic-crossing",
        "legendre-at-one",
    )
    zero_factorized = workspace.function(
        "legendre-triadic-crossing",
        "cusp-zero-factorized",
    )
    one_factorized = workspace.function(
        "legendre-triadic-crossing",
        "cusp-one-factorized",
    )

    x = sympy.Symbol("x", real=True)
    parameter = sympy.Symbol("parameter", real=True)

    assert sympy.simplify(
        generic.to_sympy() - x * (x - 1) * (x - parameter)
    ) == 0
    assert generic.evaluate({"x": 2.0, "parameter": 3.0}) == -2.0

    assert sympy.simplify(at_zero.to_sympy() - x**2 * (x - 1)) == 0
    assert sympy.simplify(at_one.to_sympy() - x * (x - 1) ** 2) == 0
    assert sympy.simplify(at_zero.to_sympy() - zero_factorized.to_sympy()) == 0
    assert sympy.simplify(at_one.to_sympy() - one_factorized.to_sympy()) == 0

    # Extensional specialization does not identify the generic-call history
    # with a separately factorized cusp construction.
    assert at_zero.history != zero_factorized.history
    assert at_zero.ir != zero_factorized.ir
    assert at_one.history != one_factorized.history
    assert at_one.ir != one_factorized.ir

    assert generic.validation_certificate["graph"] == "checked"
    assert zero_factorized.validation_certificate["graph"] == "checked"
    assert one_factorized.validation_certificate["graph"] == "checked"

    # The generic polynomial uses three x occurrences and one parameter
    # occurrence.  Each specialized factorization uses three x occurrences.
    assert _output_source_contributions(generic) == (1, 3)
    assert len(zero_factorized.ir["outputs"][0]["lineage"]) == 3
    assert len(one_factorized.ir["outputs"][0]["lineage"]) == 3


def test_finite_cusp_table_keeps_the_three_domains_typed() -> None:
    X, Z = sympy.symbols("X Z")
    delta_zero = sympy.Matrix([1, 0])
    delta_one = sympy.Matrix([0, 1])
    delta_infinity = -delta_zero - delta_one

    primitive = tuple(
        _primitive_twist(delta)
        for delta in (delta_zero, delta_one, delta_infinity)
    )
    unipotent = tuple(item**2 for item in primitive)
    actual = (unipotent[0], unipotent[1], -unipotent[2])

    cusps = (
        CuspCrossing(
            "zero",
            X,
            delta_zero,
            primitive[0],
            unipotent[0],
            actual[0],
        ),
        CuspCrossing(
            "one",
            X - Z,
            delta_one,
            primitive[1],
            unipotent[1],
            actual[1],
        ),
        CuspCrossing(
            "infinity",
            Z,
            delta_infinity,
            primitive[2],
            unipotent[2],
            actual[2],
        ),
    )

    assert tuple(cusp.name for cusp in cusps) == ("zero", "one", "infinity")
    assert tuple(cusp.collision_factor for cusp in cusps) == (X, X - Z, Z)
    assert all(cusp.primitive_twist**2 == cusp.unipotent_lift for cusp in cusps)
    assert cusps[0].actual_monodromy * cusps[1].actual_monodromy * cusps[2].actual_monodromy == IDENTITY

    # Equality between these typed fields is neither required nor meaningful:
    # a branch factor, a homology class, a Dehn twist, and a period matrix are
    # linked by interpretation maps and certificates, not by one untyped ID.
    assert all(cusp.collision_factor != cusp.vanishing_cycle for cusp in cusps)
