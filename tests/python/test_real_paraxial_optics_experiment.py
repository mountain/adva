from __future__ import annotations

import cmath
from typing import Any

import pytest
from adva import link_modules

REAL_PARAXIAL_OPTICS_KERNEL = r"""
(module real-paraxial-optics
  (export
    direct-quarter
    factorized-quarter
    inverse-quarter
    half-turn
    full-turn
    stable-cell
    parabolic-cell
    hyperbolic-cell)

  ; Unit free propagation: (x, s) |-> (x + s, s).
  (def drift-plus-core
    (fn ((x Real) (s-position Real) (s-output Real)) (outputs Real Real)
      (frontier
        (add
          (frontier
            (use x)
            (use s-position)))
        (use s-output))))

  (def drift-plus
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus-core
        (frontier
          (use x)
          (copy (use s))))))

  ; Inverse unit propagation: (x, s) |-> (x - s, s).
  (def drift-minus-core
    (fn ((x Real) (s-position Real) (s-output Real)) (outputs Real Real)
      (frontier
        (add
          (frontier
            (use x)
            (neg (use s-position))))
        (use s-output))))

  (def drift-minus
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-minus-core
        (frontier
          (use x)
          (copy (use s))))))

  ; Unit focusing power: (x, s) |-> (x, s - x).
  (def focus-core
    (fn ((x-output Real) (x-slope Real) (s Real)) (outputs Real Real)
      (frontier
        (use x-output)
        (add
          (frontier
            (use s)
            (neg (use x-slope)))))))

  (def focus
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call focus-core
        (frontier
          (copy (use x))
          (use s)))))

  ; Inverse focusing power: (x, s) |-> (x, s + x).
  (def defocus-core
    (fn ((x-output Real) (x-slope Real) (s Real)) (outputs Real Real)
      (frontier
        (use x-output)
        (add
          (frontier
            (use s)
            (use x-slope))))))

  (def defocus
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call defocus-core
        (frontier
          (copy (use x))
          (use s)))))

  ; A compiled value shadow of the normalized quarter-turn.
  (def direct-quarter
    (fn ((x Real) (s Real)) (outputs Real Real)
      (frontier
        (use s)
        (neg (use x)))))

  ; The physical device history P(1) L(1) P(1).
  (def factorized-quarter
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus
        (call focus
          (call drift-plus
            (frontier
              (use x)
              (use s)))))))

  ; The inverse physical history P(-1) L(-1) P(-1).
  (def inverse-quarter
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-minus
        (call defocus
          (call drift-minus
            (frontier
              (use x)
              (use s)))))))

  (def half-turn
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call factorized-quarter
        (call factorized-quarter
          (frontier
            (use x)
            (use s))))))

  (def full-turn
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call half-turn
        (call half-turn
          (frontier
            (use x)
            (use s))))))

  ; Three repeatable real optical cells with determinant one.
  (def stable-cell
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus
        (call focus
          (frontier
            (use x)
            (use s))))))

  (def parabolic-cell
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus
        (frontier
          (use x)
          (use s)))))

  (def hyperbolic-cell
    (fn ((x Real) (s Real)) (outputs Real Real)
      (call drift-plus
        (call defocus
          (frontier
            (use x)
            (use s))))))
)
"""

Ray = tuple[float, float]
RealizedAction = tuple[tuple[float, float], tuple[float, float]]


def _functions() -> dict[str, Any]:
    workspace = link_modules([REAL_PARAXIAL_OPTICS_KERNEL])
    names = (
        "direct-quarter",
        "factorized-quarter",
        "inverse-quarter",
        "half-turn",
        "full-turn",
        "stable-cell",
        "parabolic-cell",
        "hyperbolic-cell",
    )
    return {
        name: workspace.function("real-paraxial-optics", name)
        for name in names
    }


def _evaluate(function: Any, ray: Ray) -> Ray:
    result = function.evaluate({"x": ray[0], "s": ray[1]})
    if not isinstance(result, tuple) or len(result) != 2:
        raise TypeError("a paraxial optical program must have two ordered Real outputs")
    return result


def _trajectory(function: Any, initial: Ray, steps: int) -> tuple[Ray, ...]:
    states = [initial]
    for _ in range(steps):
        states.append(_evaluate(function, states[-1]))
    return tuple(states)


def _realized_action(function: Any) -> RealizedAction:
    """Observe a two-port numerical action after the program has been checked."""

    x_column = _evaluate(function, (1.0, 0.0))
    s_column = _evaluate(function, (0.0, 1.0))
    return (
        (x_column[0], s_column[0]),
        (x_column[1], s_column[1]),
    )


def _trace(action: RealizedAction) -> float:
    return action[0][0] + action[1][1]


def _determinant(action: RealizedAction) -> float:
    return action[0][0] * action[1][1] - action[0][1] * action[1][0]


def _classification(action: RealizedAction) -> str:
    discriminant = _trace(action) ** 2 - 4.0 * _determinant(action)
    if discriminant < 0.0:
        return "elliptic"
    if discriminant > 0.0:
        return "hyperbolic"
    return "parabolic"


def _finite_projective_fixed_points(action: RealizedAction) -> tuple[complex, ...]:
    """Solve z=(a z+b)/(c z+d) only after observing the real action."""

    (a, b), (c, d) = action
    linear = d - a
    constant = -b
    if c == 0.0:
        if linear == 0.0:
            return ()
        return (complex(-constant / linear),)

    discriminant = complex(linear * linear - 4.0 * c * constant)
    root = cmath.sqrt(discriminant)
    return (
        (-linear + root) / (2.0 * c),
        (-linear - root) / (2.0 * c),
    )


def _output_source_support(function: Any) -> tuple[frozenset[str], ...]:
    diagram = function.ir
    occurrence_sources = {
        occurrence["id"]: occurrence["source"] for occurrence in diagram["occurrences"]
    }
    return tuple(
        frozenset(occurrence_sources[occurrence] for occurrence in output["lineage"])
        for output in diagram["outputs"]
    )


def test_real_optical_programs_cross_the_checked_two_port_boundary() -> None:
    functions = _functions()

    for function in functions.values():
        assert function.validation_certificate["graph"] == "checked"
        assert function.signature.inputs == (("x", "real"), ("s", "real"))
        assert function.signature.outputs == ("real", "real")

    assert _evaluate(functions["direct-quarter"], (2.0, 3.0)) == (3.0, -2.0)
    assert _evaluate(functions["factorized-quarter"], (2.0, 3.0)) == (3.0, -2.0)
    assert _evaluate(functions["inverse-quarter"], (2.0, 3.0)) == (-3.0, 2.0)
    assert _evaluate(functions["half-turn"], (2.0, 3.0)) == (-2.0, -3.0)
    assert _evaluate(functions["full-turn"], (2.0, 3.0)) == (2.0, 3.0)


def test_real_device_chain_derives_negative_reciprocal_and_complex_fixed_points() -> None:
    functions = _functions()
    direct = functions["direct-quarter"]
    factorized = functions["factorized-quarter"]
    inverse = functions["inverse-quarter"]
    fixtures: tuple[Ray, ...] = (
        (1.0, 0.0),
        (0.0, 1.0),
        (2.0, -3.0),
        (-5.0, 7.0),
    )

    for ray in fixtures:
        forward = _evaluate(factorized, ray)
        assert forward == _evaluate(direct, ray)
        assert _evaluate(factorized, forward) == (-ray[0], -ray[1])
        assert _evaluate(inverse, forward) == ray
        assert _evaluate(inverse, ray) == (-forward[0], -forward[1])

    for z in (-3.0, -0.5, 0.25, 2.0, 5.0):
        forward = _evaluate(factorized, (z, 1.0))
        backward = _evaluate(inverse, (z, 1.0))
        assert forward[0] / forward[1] == pytest.approx(-1.0 / z)
        assert backward[0] / backward[1] == pytest.approx(-1.0 / z)

    action = _realized_action(factorized)
    assert action == ((0.0, 1.0), (-1.0, 0.0))
    assert _determinant(action) == 1.0
    assert _trace(action) == 0.0
    roots = _finite_projective_fixed_points(action)
    assert set(roots) == {1j, -1j}


def test_real_program_iteration_recovers_the_three_projective_regimes() -> None:
    functions = _functions()
    stable = functions["stable-cell"]
    parabolic = functions["parabolic-cell"]
    hyperbolic = functions["hyperbolic-cell"]

    actions = tuple(_realized_action(function) for function in (stable, parabolic, hyperbolic))
    assert actions == (
        ((0.0, 1.0), (-1.0, 1.0)),
        ((1.0, 1.0), (0.0, 1.0)),
        ((2.0, 1.0), (1.0, 1.0)),
    )
    assert tuple(_determinant(action) for action in actions) == (1.0, 1.0, 1.0)
    assert tuple(_trace(action) for action in actions) == (1.0, 2.0, 3.0)
    assert tuple(_classification(action) for action in actions) == (
        "elliptic",
        "parabolic",
        "hyperbolic",
    )

    stable_roots = _finite_projective_fixed_points(actions[0])
    parabolic_roots = _finite_projective_fixed_points(actions[1])
    hyperbolic_roots = _finite_projective_fixed_points(actions[2])
    assert len(stable_roots) == 2
    assert stable_roots[0].conjugate() == stable_roots[1]
    assert {root.imag > 0.0 for root in stable_roots} == {False, True}
    assert parabolic_roots == ()
    assert len(hyperbolic_roots) == 2
    assert all(root.imag == 0.0 for root in hyperbolic_roots)

    initial = (1.0, 1.0)
    stable_orbit = _trajectory(stable, initial, 6)
    parabolic_orbit = _trajectory(parabolic, initial, 12)
    hyperbolic_orbit = _trajectory(hyperbolic, initial, 12)
    assert stable_orbit == (
        (1.0, 1.0),
        (1.0, 0.0),
        (0.0, -1.0),
        (-1.0, -1.0),
        (-1.0, 0.0),
        (0.0, 1.0),
        (1.0, 1.0),
    )
    assert parabolic_orbit[-1] == (13.0, 1.0)
    assert hyperbolic_orbit[-1] == (121393.0, 75025.0)


def test_same_numerical_shadow_retains_a_program_geometry_residual() -> None:
    functions = _functions()
    direct = functions["direct-quarter"]
    factorized = functions["factorized-quarter"]

    assert _realized_action(direct) == _realized_action(factorized)
    assert direct.ir != factorized.ir
    assert direct.history != factorized.history
    assert len(factorized.history["prefix"]) > len(direct.history["prefix"])

    direct_support = _output_source_support(direct)
    factorized_support = _output_source_support(factorized)
    assert tuple(map(len, direct_support)) == (1, 1)
    assert direct_support[0].isdisjoint(direct_support[1])
    assert tuple(map(len, factorized_support)) == (2, 2)
    assert factorized_support[0] == factorized_support[1]
