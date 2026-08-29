from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import sympy

from adva import link_modules


AFFINE_OBSERVER_KERNEL = r"""
(module affine-observer
  (export
    add-state scale-state
    affine-state q-after-affine
    scale-after-add add-after-scale
    y-after-add q-after-add
    y-after-scale q-after-scale
    q-after-scale-after-add q-after-add-after-scale
    q-after-reciprocal-perturb
    shared-double scale-double)

  (def add-state
    (fn ((x Real) (a Real)) Real
      (add (use x) (use a))))

  (def scale-state
    (fn ((x Real) (m Real)) Real
      (mul (use m) (use x))))

  (def affine-state
    (fn ((x Real) (m Real) (a Real)) Real
      (add (mul (use m) (use x)) (use a))))

  (def q-after-affine
    (fn ((x Real) (m Real) (a Real)) Real
      (exp
        (neg
          (log
            (add (mul (use m) (use x)) (use a)))))))

  (def scale-after-add
    (fn ((x Real) (a Real) (m Real)) Real
      (mul (use m) (add (use x) (use a)))))

  (def add-after-scale
    (fn ((x Real) (b Real) (m Real)) Real
      (add (mul (use m) (use x)) (use b))))

  (def y-after-add
    (fn ((x Real) (a Real)) Real
      (log (add (use x) (use a)))))

  (def q-after-add
    (fn ((x Real) (a Real)) Real
      (exp (neg (log (add (use x) (use a)))))))

  (def y-after-scale
    (fn ((x Real) (m Real)) Real
      (log (mul (use m) (use x)))))

  (def q-after-scale
    (fn ((x Real) (m Real)) Real
      (exp (neg (log (mul (use m) (use x)))))))

  (def q-after-scale-after-add
    (fn ((x Real) (a Real) (m Real)) Real
      (exp
        (neg
          (log
            (mul (use m) (add (use x) (use a))))))))

  (def q-after-add-after-scale
    (fn ((x Real) (b Real) (m Real)) Real
      (exp
        (neg
          (log
            (add (mul (use m) (use x)) (use b)))))))

  (def reciprocal-perturb-expanded
    (fn ((x0 Real) (x1 Real) (b Real)) Real
      (add
        (use x0)
        (mul
          (use b)
          (exp (neg (log (use x1))))))))

  (def q-after-reciprocal-perturb
    (fn ((x Real) (b Real)) Real
      (exp
        (neg
          (log
            (call reciprocal-perturb-expanded
              (frontier (copy (use x)) (use b))))))))

  (def shared-double
    (fn ((x Real)) Real
      (add (copy (use x)))))

  (def scale-double
    (fn ((x Real)) Real
      (scale 2 (use x)))))
"""


@dataclass(frozen=True, slots=True)
class TruncatedPullback:
    """Research-local coordinates of a checked pullback on an exp ray.

    Columns are the pullbacks of ``q, q^2, ..., q^order``.  The matrix is a
    derived finite presentation; it is not Adva IR or semantic authority.
    ``first_omitted`` records the coefficient of ``q^(order + 1)`` for every
    column instead of pretending that truncation is exact.
    """

    matrix: sympy.Matrix
    first_omitted: tuple[sympy.Expr, ...]


@dataclass(frozen=True, slots=True)
class BoundaryTwoJet:
    """Marked ``q = 1/x`` coefficients through ``q^2``."""

    linear: sympy.Expr
    quadratic: sympy.Expr

    def reconstruct_marked_affine_parameters(self) -> tuple[sympy.Expr, sympy.Expr]:
        """Recover ``D(x) = m*x + a`` relative to the declared marked chart."""

        scale = sympy.simplify(1 / self.linear)
        translation = sympy.simplify(-self.quadratic / self.linear**2)
        return scale, translation


def _workspace():
    return link_modules([AFFINE_OBSERVER_KERNEL])


def _symbols_by_name(expression: sympy.Expr) -> dict[str, sympy.Symbol]:
    return {str(symbol): symbol for symbol in expression.free_symbols}


def _checked_chart_image(function: Any, parameters: dict[str, sympy.Expr]) -> sympy.Expr:
    """Translate checked IR, then express its output in ``q = exp(-y) = 1/x``."""

    expression = function.to_sympy()
    symbols = _symbols_by_name(expression)
    q = sympy.Symbol("q", positive=True)
    substitutions: dict[sympy.Symbol, sympy.Expr] = {symbols["x"]: 1 / q}
    substitutions.update({symbols[name]: value for name, value in parameters.items()})
    charted = expression.subs(substitutions)
    return sympy.cancel(sympy.powdenest(charted, force=True))


def _derive_exp_ray_pullback(q_image: sympy.Expr, order: int) -> TruncatedPullback:
    """Compile observer pullback from the checked image of the generator ``q``."""

    q = sympy.Symbol("q", positive=True)
    matrix = sympy.zeros(order, order)
    first_omitted: list[sympy.Expr] = []
    for column in range(order):
        pulled = sympy.series(q_image ** (column + 1), q, 0, order + 2).removeO().expand()
        for row in range(order):
            matrix[row, column] = sympy.expand(pulled).coeff(q, row + 1)
        first_omitted.append(sympy.expand(pulled).coeff(q, order + 1))
    return TruncatedPullback(matrix=matrix, first_omitted=tuple(first_omitted))


def _boundary_two_jet(q_image: sympy.Expr) -> BoundaryTwoJet:
    q = sympy.Symbol("q", positive=True)
    series = sympy.series(q_image, q, 0, 3).removeO().expand()
    return BoundaryTwoJet(linear=series.coeff(q, 1), quadratic=series.coeff(q, 2))


def test_affine_program_generates_exp_polynomial_observer_carrier():
    workspace = _workspace()
    a = sympy.Symbol("a", positive=True)
    m = sympy.Symbol("m", positive=True)
    q = sympy.Symbol("q", positive=True)

    y_add = _checked_chart_image(workspace.function("affine-observer", "y-after-add"), {"a": a})
    q_add = _checked_chart_image(workspace.function("affine-observer", "q-after-add"), {"a": a})
    y_scale = _checked_chart_image(
        workspace.function("affine-observer", "y-after-scale"), {"m": m}
    )
    q_scale = _checked_chart_image(
        workspace.function("affine-observer", "q-after-scale"), {"m": m}
    )

    # y = -log(q).  Addition becomes an exponential-logarithmic residual,
    # while multiplication becomes affine translation in the y chart.
    assert sympy.simplify(y_add + sympy.log(q) - sympy.log(1 + a * q)) == 0
    assert sympy.simplify(y_scale + sympy.log(q) - sympy.log(m)) == 0
    assert sympy.simplify(q_add - q / (1 + a * q)) == 0
    assert sympy.simplify(q_scale - q / m) == 0

    residual = sympy.series(y_add + sympy.log(q), q, 0, 6)
    expected = sympy.series(sympy.log(1 + a * q), q, 0, 6)
    assert residual == expected

    certificate = workspace.function("affine-observer", "q-after-add").validation_certificate
    assert certificate["graph"] == "checked"
    assert certificate["linear_use"] == "checked"
    assert certificate["source_partition"] == "checked"


def test_matrix_like_transport_is_derived_from_dual_observer_pullback():
    workspace = _workspace()
    a = sympy.Symbol("a", positive=True)
    m = sympy.Symbol("m", positive=True)
    order = 5

    q_add = _checked_chart_image(workspace.function("affine-observer", "q-after-add"), {"a": a})
    q_scale = _checked_chart_image(
        workspace.function("affine-observer", "q-after-scale"), {"m": m}
    )
    add_pullback = _derive_exp_ray_pullback(q_add, order)
    scale_pullback = _derive_exp_ray_pullback(q_scale, order)

    expected_add = sympy.zeros(order, order)
    for column in range(order):
        k = column + 1
        for row in range(column, order):
            j = row - column
            expected_add[row, column] = (-1) ** j * sympy.binomial(k + j - 1, j) * a**j
    assert add_pullback.matrix == expected_add
    assert scale_pullback.matrix == sympy.diag(*(m ** (-k) for k in range(1, order + 1)))

    expected_first_omitted = tuple(
        (-1) ** (order - column)
        * sympy.binomial(order, order - column)
        * a ** (order - column)
        for column in range(order)
    )
    assert add_pullback.first_omitted == expected_first_omitted
    assert scale_pullback.first_omitted == (sympy.Integer(0),) * order


def test_contravariant_transport_recovers_the_affine_semidirect_law():
    workspace = _workspace()
    a = sympy.Symbol("a", positive=True)
    m = sympy.Symbol("m", positive=True)
    order = 5

    q_add_a = _checked_chart_image(
        workspace.function("affine-observer", "q-after-add"), {"a": a}
    )
    q_add_ma = _checked_chart_image(
        workspace.function("affine-observer", "q-after-add"), {"a": m * a}
    )
    q_scale = _checked_chart_image(
        workspace.function("affine-observer", "q-after-scale"), {"m": m}
    )
    c_add_a = _derive_exp_ray_pullback(q_add_a, order).matrix
    c_add_ma = _derive_exp_ray_pullback(q_add_ma, order).matrix
    c_scale = _derive_exp_ray_pullback(q_scale, order).matrix

    # M_m after A_a equals A_(ma) after M_m on states.  Pullback reverses
    # composition order, and the derived action tables retain that law.
    assert sympy.simplify(c_add_a * c_scale - c_scale * c_add_ma) == sympy.zeros(
        order, order
    )

    scale_after_add = workspace.function("affine-observer", "scale-after-add")
    add_after_scale = workspace.function("affine-observer", "add-after-scale")
    q_scale_after_add = workspace.function("affine-observer", "q-after-scale-after-add")
    q_add_after_scale = workspace.function("affine-observer", "q-after-add-after-scale")
    for x_value, a_value, m_value in ((3.0, 0.25, 2.0), (1.5, 0.4, 3.0)):
        b_value = m_value * a_value
        left = scale_after_add.evaluate({"x": x_value, "a": a_value, "m": m_value})
        right = add_after_scale.evaluate({"x": x_value, "b": b_value, "m": m_value})
        assert math.isclose(left, right, rel_tol=1e-14, abs_tol=1e-14)
        q_left = q_scale_after_add.evaluate({"x": x_value, "a": a_value, "m": m_value})
        q_right = q_add_after_scale.evaluate({"x": x_value, "b": b_value, "m": m_value})
        assert math.isclose(q_left, q_right, rel_tol=1e-14, abs_tol=1e-14)


def test_marked_boundary_two_jet_reconstructs_affine_program():
    workspace = _workspace()
    a = sympy.Symbol("a", positive=True)
    m = sympy.Symbol("m", positive=True)
    q = sympy.Symbol("q", positive=True)

    q_affine = _checked_chart_image(
        workspace.function("affine-observer", "q-after-affine"), {"m": m, "a": a}
    )
    assert sympy.simplify(q_affine - q / (m + a * q)) == 0

    jet = _boundary_two_jet(q_affine)
    assert jet == BoundaryTwoJet(linear=1 / m, quadratic=-a / m**2)
    assert jet.reconstruct_marked_affine_parameters() == (m, a)

    # Once the affine hypothesis and marked chart are declared, the two-jet
    # determines every higher coefficient of this particular rational germ.
    series = sympy.series(q_affine, q, 0, 7).removeO().expand()
    for power in range(1, 7):
        expected = (-1) ** (power - 1) * a ** (power - 1) / m**power
        assert sympy.simplify(series.coeff(q, power) - expected) == 0

    affine = workspace.function("affine-observer", "affine-state")
    q_after_affine = workspace.function("affine-observer", "q-after-affine")
    for x_value, m_value, a_value in ((2.0, 3.0, 0.25), (5.0, 0.5, 1.5)):
        state_value = affine.evaluate({"x": x_value, "m": m_value, "a": a_value})
        q_value = q_after_affine.evaluate({"x": x_value, "m": m_value, "a": a_value})
        assert math.isclose(q_value, 1.0 / state_value, rel_tol=1e-14, abs_tol=1e-14)


def test_affine_two_jet_action_is_faithful_and_contravariant():
    workspace = _workspace()
    m1, m2 = sympy.symbols("m1 m2", positive=True)
    a1, a2 = sympy.symbols("a1 a2", positive=True)
    q_after_affine = workspace.function("affine-observer", "q-after-affine")

    q_first = _checked_chart_image(q_after_affine, {"m": m1, "a": a1})
    q_second = _checked_chart_image(q_after_affine, {"m": m2, "a": a2})
    q_composite = _checked_chart_image(
        q_after_affine, {"m": m2 * m1, "a": m2 * a1 + a2}
    )

    c_first = _derive_exp_ray_pullback(q_first, 2).matrix
    c_second = _derive_exp_ray_pullback(q_second, 2).matrix
    c_composite = _derive_exp_ray_pullback(q_composite, 2).matrix

    # D2 o D1 has parameters (m2*m1, m2*a1+a2), whereas observer pullback
    # reverses the order: (D2 o D1)^* = D1^* o D2^*.
    assert sympy.simplify(c_first * c_second - c_composite) == sympy.zeros(2, 2)

    composite_jet = _boundary_two_jet(q_composite)
    assert composite_jet.reconstruct_marked_affine_parameters() == (
        m1 * m2,
        a1 * m2 + a2,
    )


def test_unmarked_chart_changes_quadratic_extension_but_not_linear_multiplier():
    c1, c2, u, v, t = sympy.symbols("c1 c2 u v t", nonzero=True)

    # h(q)=u*q+v*q^2 is a change between adapted local parameters.  This is
    # research-side formal algebra, deliberately not presented as Adva IR.
    inverse_chart = t / u - v * t**2 / u**3
    old_coordinate = c1 * inverse_chart + c2 * inverse_chart**2
    new_coordinate = u * old_coordinate + v * old_coordinate**2
    transformed = sympy.series(new_coordinate, t, 0, 3).removeO().expand()
    expected_quadratic = c2 / u + v * (c1**2 - c1) / u**2

    assert sympy.simplify(transformed.coeff(t, 1) - c1) == 0
    assert sympy.simplify(transformed.coeff(t, 2) - expected_quadratic) == 0

    # The same statement appears matrix-like only after choosing the jet basis
    # (q,q^2): it is ordinary filtered conjugacy, not state-space ontology.
    action = sympy.Matrix([[c1, 0], [c2, c1**2]])
    chart = sympy.Matrix([[u, 0], [v, u**2]])
    transformed_action = sympy.simplify(chart.inv() * action * chart)
    expected_action = sympy.Matrix([[c1, 0], [expected_quadratic, c1**2]])
    assert (transformed_action - expected_action).applyfunc(sympy.simplify) == sympy.zeros(2, 2)


def test_non_affine_reciprocal_perturbation_is_neighboring_two_jet_no_go():
    workspace = _workspace()
    b = sympy.Symbol("b", positive=True)
    q = sympy.Symbol("q", positive=True)

    q_perturbed = _checked_chart_image(
        workspace.function("affine-observer", "q-after-reciprocal-perturb"), {"b": b}
    )
    q_identity = _checked_chart_image(
        workspace.function("affine-observer", "q-after-scale"), {"m": sympy.Integer(1)}
    )

    assert sympy.simplify(q_perturbed - q / (1 + b * q**2)) == 0
    assert _boundary_two_jet(q_perturbed) == _boundary_two_jet(q_identity)
    assert _boundary_two_jet(q_identity) == BoundaryTwoJet(
        linear=sympy.Integer(1), quadratic=sympy.Integer(0)
    )
    assert sympy.simplify(q_perturbed - q_identity) != 0

    perturbed_series = sympy.series(q_perturbed, q, 0, 5).removeO().expand()
    assert perturbed_series.coeff(q, 3) == -b

    perturb = workspace.function("affine-observer", "q-after-reciprocal-perturb")
    for x_value, b_value in ((2.0, 0.25), (4.0, 1.5)):
        checked = perturb.evaluate({"x": x_value, "b": b_value})
        expected = 1.0 / (x_value + b_value / x_value)
        assert math.isclose(checked, expected, rel_tol=1e-14, abs_tol=1e-14)


def test_filtered_spectrum_separates_scale_from_additive_unipotent_residual():
    workspace = _workspace()
    order = 5
    q_add_one = _checked_chart_image(
        workspace.function("affine-observer", "q-after-add"), {"a": sympy.Integer(1)}
    )
    q_add_two = _checked_chart_image(
        workspace.function("affine-observer", "q-after-add"), {"a": sympy.Integer(2)}
    )
    q_scale_two = _checked_chart_image(
        workspace.function("affine-observer", "q-after-scale"), {"m": sympy.Integer(2)}
    )
    add_one = _derive_exp_ray_pullback(q_add_one, order)
    add_two = _derive_exp_ray_pullback(q_add_two, order)
    scale_two = _derive_exp_ray_pullback(q_scale_two, order)

    assert add_one.matrix.eigenvals() == {sympy.Integer(1): order}
    assert add_two.matrix.eigenvals() == {sympy.Integer(1): order}
    assert add_one.matrix != add_two.matrix
    assert add_one.first_omitted != add_two.first_omitted

    nilpotent = add_two.matrix - sympy.eye(order)
    assert nilpotent ** order == sympy.zeros(order, order)
    assert nilpotent ** (order - 1) != sympy.zeros(order, order)
    assert scale_two.matrix.eigenvals() == {
        sympy.Rational(1, 2**k): 1 for k in range(1, order + 1)
    }


def test_value_differential_powers_and_scalar_spectrum_do_not_recover_history():
    workspace = _workspace()
    shared = workspace.function("affine-observer", "shared-double")
    scaled = workspace.function("affine-observer", "scale-double")

    for initial in (-1.25, 0.0, 2.75):
        shared_value, shared_gradient, shared_certificate = shared.value_and_gradient(
            {"x": initial}
        )
        scaled_value, scaled_gradient, scaled_certificate = scaled.value_and_gradient(
            {"x": initial}
        )
        assert shared_value == scaled_value == 2.0 * initial
        assert shared_gradient == scaled_gradient == {"x": 2.0}
        assert shared_certificate["operation_rules"] != scaled_certificate["operation_rules"]

        shared_iterate = initial
        scaled_iterate = initial
        for _ in range(6):
            shared_iterate = shared.evaluate({"x": shared_iterate})
            scaled_iterate = scaled.evaluate({"x": scaled_iterate})
        assert shared_iterate == scaled_iterate == (2.0**6) * initial

    assert shared.ir != scaled.ir
    assert shared.history != scaled.history
    assert shared.source_partition != scaled.source_partition
