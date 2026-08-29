from __future__ import annotations

from collections.abc import Mapping

import numpy as np

from adva import link_modules


SPECTRAL_KERNEL = r"""
(module spectral-kernel
  (export action paired-action shared-double scale-double)

  (def action-expanded
    (fn ((a Real) (b Real) (c Real) (d Real)
         (x0 Real) (x1 Real) (y0 Real) (y1 Real))
        (outputs Real Real)
      (frontier
        (add (mul (use a) (use x0))
             (mul (use b) (use y0)))
        (add (mul (use c) (use x1))
             (mul (use d) (use y1))))))

  (def action
    (fn ((a Real) (b Real) (c Real) (d Real) (x Real) (y Real))
        (outputs Real Real)
      (call action-expanded
        (frontier
          (use a) (use b) (use c) (use d)
          (copy (use x))
          (copy (use y))))))

  (def paired-expanded
    (fn ((a Real) (b Real) (c Real) (d Real)
         (x0 Real) (x1 Real) (y0 Real) (y1 Real)
         (l0 Real) (l1 Real))
        Real
      (add
        (mul
          (use l0)
          (add (mul (use a) (use x0))
               (mul (use b) (use y0))))
        (mul
          (use l1)
          (add (mul (use c) (use x1))
               (mul (use d) (use y1)))))))

  (def paired-action
    (fn ((a Real) (b Real) (c Real) (d Real)
         (x Real) (y Real) (l0 Real) (l1 Real))
        Real
      (call paired-expanded
        (frontier
          (use a) (use b) (use c) (use d)
          (copy (use x))
          (copy (use y))
          (use l0) (use l1)))))

  (def shared-double
    (fn ((x Real)) Real
      (add (copy (use x)))))

  (def scale-double
    (fn ((x Real)) Real
      (scale 2 (use x)))))
"""


def _workspace():
    return link_modules([SPECTRAL_KERNEL])


def _matrix_inputs(matrix: np.ndarray, vector: np.ndarray) -> dict[str, float]:
    return {
        "a": float(matrix[0, 0]),
        "b": float(matrix[0, 1]),
        "c": float(matrix[1, 0]),
        "d": float(matrix[1, 1]),
        "x": float(vector[0]),
        "y": float(vector[1]),
    }


def _paired_inputs(
    matrix: np.ndarray, vector: np.ndarray, observer: np.ndarray
) -> dict[str, float]:
    return {
        **_matrix_inputs(matrix, vector),
        "l0": float(observer[0]),
        "l1": float(observer[1]),
    }


def _action(function, matrix: np.ndarray, vector: np.ndarray) -> np.ndarray:
    value = function.evaluate(_matrix_inputs(matrix, vector))
    assert isinstance(value, tuple)
    return np.asarray(value, dtype=float)


def _paired_differential(
    function, matrix: np.ndarray, vector: np.ndarray, observer: np.ndarray
) -> tuple[float, Mapping[str, float], Mapping[str, object]]:
    value, gradient, certificate = function.value_and_gradient(
        _paired_inputs(matrix, vector, observer)
    )
    assert isinstance(value, float)
    assert isinstance(gradient, Mapping)
    return value, gradient, certificate


def _spectral_family(theta: float, shear: float, ratio: float) -> tuple[np.ndarray, np.ndarray]:
    cosine = np.cos(theta)
    sine = np.sin(theta)
    rotation = np.asarray([[cosine, -sine], [sine, cosine]])
    skew_basis = np.asarray([[1.0, shear], [0.0, 1.0]])
    basis = rotation @ skew_basis
    action = basis @ np.diag([1.0, ratio]) @ np.linalg.inv(basis)
    return action, basis


def _projective_error(vector: np.ndarray, target: np.ndarray) -> float:
    vector = vector / np.linalg.norm(vector)
    target = target / np.linalg.norm(target)
    return float(abs(vector[0] * target[1] - vector[1] * target[0]))


def test_pairing_differential_derives_pullback_and_action_gradient():
    workspace = _workspace()
    action = workspace.function("spectral-kernel", "action")
    paired = workspace.function("spectral-kernel", "paired-action")

    matrix = np.asarray([[1.2, -0.4], [0.3, 0.7]])
    vector = np.asarray([0.8, -1.1])
    observer = np.asarray([0.25, 1.4])

    np.testing.assert_allclose(_action(action, matrix, vector), matrix @ vector)

    value, gradient, certificate = _paired_differential(
        paired, matrix, vector, observer
    )
    np.testing.assert_allclose(value, observer @ matrix @ vector)

    derived_pullback = np.asarray([gradient["x"], gradient["y"]])
    np.testing.assert_allclose(derived_pullback, matrix.T @ observer)

    derived_action_gradient = np.asarray(
        [
            [gradient["a"], gradient["b"]],
            [gradient["c"], gradient["d"]],
        ]
    )
    np.testing.assert_allclose(derived_action_gradient, np.outer(observer, vector))

    assert certificate["method"] == "forward-mode structural differential"
    assert certificate["diagram_integrity"] == "checked"
    assert {
        "adva.builtin:add@1",
        "adva.builtin:copy@1",
        "adva.builtin:mul@1",
    }.issubset(set(certificate["operation_rules"]))


def test_checked_world_and_derived_observer_iterations_select_paired_modes():
    workspace = _workspace()
    action = workspace.function("spectral-kernel", "action")
    paired = workspace.function("spectral-kernel", "paired-action")

    ratio = 0.2
    matrix, basis = _spectral_family(theta=0.37, shear=0.6, ratio=ratio)
    right_eigenvector = basis[:, 0]
    left_eigenvector = np.linalg.inv(basis).T[:, 0]
    np.testing.assert_allclose(left_eigenvector @ right_eigenvector, 1.0)

    generator = np.asarray([[0.0, -1.0], [1.0, 0.0]])
    matrix_derivative = generator @ matrix - matrix @ generator
    _, eigenvalue_gradient, _ = _paired_differential(
        paired, matrix, right_eigenvector, left_eigenvector
    )
    entry_gradient = np.asarray(
        [
            [eigenvalue_gradient["a"], eigenvalue_gradient["b"]],
            [eigenvalue_gradient["c"], eigenvalue_gradient["d"]],
        ]
    )
    np.testing.assert_allclose(np.sum(entry_gradient * matrix_derivative), 0.0, atol=1e-12)

    right_mode = right_eigenvector.copy()
    left_mode = left_eigenvector.copy()
    right_mode /= np.linalg.norm(right_mode)
    left_mode /= np.linalg.norm(left_mode)

    np.testing.assert_allclose(matrix @ right_mode, right_mode, atol=1e-12)
    np.testing.assert_allclose(matrix.T @ left_mode, left_mode, atol=1e-12)
    np.testing.assert_allclose(np.sort(np.linalg.eigvals(matrix)), [ratio, 1.0])

    world = np.asarray([0.8, -0.3])
    observer = np.asarray([-0.2, 0.9])
    world_errors = [_projective_error(world, right_mode)]
    observer_errors = [_projective_error(observer, left_mode)]

    for _ in range(10):
        world = _action(action, matrix, world)
        world /= np.linalg.norm(world)

        _, gradient, _ = _paired_differential(
            paired, matrix, np.asarray([0.4, -0.7]), observer
        )
        observer = np.asarray([gradient["x"], gradient["y"]])
        observer /= np.linalg.norm(observer)

        world_errors.append(_projective_error(world, right_mode))
        observer_errors.append(_projective_error(observer, left_mode))

    assert world_errors[-1] < 1e-6
    assert observer_errors[-1] < 1e-6
    assert world_errors[-1] < world_errors[0] * ratio**7
    assert observer_errors[-1] < observer_errors[0] * ratio**7


def test_fixed_basis_covariance_and_parameter_dependent_chart_correction():
    workspace = _workspace()
    paired = workspace.function("spectral-kernel", "paired-action")

    matrix = np.asarray([[1.0, 0.35], [-0.2, 0.6]])
    vector = np.asarray([0.7, -0.5])
    observer = np.asarray([0.3, 1.1])
    basis_change = np.asarray([[1.4, 0.2], [-0.1, 0.9]])

    changed_matrix = basis_change @ matrix @ np.linalg.inv(basis_change)
    changed_vector = basis_change @ vector
    changed_observer = np.linalg.inv(basis_change).T @ observer

    value, gradient, _ = _paired_differential(paired, matrix, vector, observer)
    changed_value, changed_gradient, _ = _paired_differential(
        paired, changed_matrix, changed_vector, changed_observer
    )
    np.testing.assert_allclose(changed_value, value)

    pullback = np.asarray([gradient["x"], gradient["y"]])
    changed_pullback = np.asarray([changed_gradient["x"], changed_gradient["y"]])
    np.testing.assert_allclose(basis_change.T @ changed_pullback, pullback)

    theta = 0.41
    shear = 0.5
    ratio = 0.3
    charted_matrix, chart = _spectral_family(theta, shear, ratio)
    base_world = np.asarray([0.4, -0.8])
    base_observer = np.asarray([1.2, 0.3])
    charted_world = chart @ base_world
    charted_observer = np.linalg.inv(chart).T @ base_observer

    generator = np.asarray([[0.0, -1.0], [1.0, 0.0]])
    matrix_derivative = generator @ charted_matrix - charted_matrix @ generator

    _, chart_gradient, _ = _paired_differential(
        paired, charted_matrix, charted_world, charted_observer
    )
    entry_gradient = np.asarray(
        [
            [chart_gradient["a"], chart_gradient["b"]],
            [chart_gradient["c"], chart_gradient["d"]],
        ]
    )
    naive_coordinate_gradient = float(np.sum(entry_gradient * matrix_derivative))
    assert abs(naive_coordinate_gradient) > 1e-3

    world_derivative = generator @ charted_world
    observer_derivative = -generator.T @ charted_observer
    total_covariant_derivative = (
        observer_derivative @ charted_matrix @ charted_world
        + naive_coordinate_gradient
        + charted_observer @ charted_matrix @ world_derivative
    )
    np.testing.assert_allclose(total_covariant_derivative, 0.0, atol=1e-12)


def test_value_differential_powers_and_spectrum_do_not_recover_history():
    workspace = _workspace()
    shared = workspace.function("spectral-kernel", "shared-double")
    scaled = workspace.function("spectral-kernel", "scale-double")

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
