from __future__ import annotations

from itertools import permutations
from typing import Any

import pytest
import sympy
from adva import link_modules

THREE_ASPECT_CHIRALITY_KERNEL = r"""
(module three-aspect-chirality
  (export pseudoscalar-action inverse-pseudoscalar-action time-space-swap)

  (def pseudoscalar-action
    (fn
      ((t Real) (s Real) (r Real) (sr Real) (rt Real) (ts Real))
      (outputs Real Real Real Real Real Real)
      (frontier
        (neg (use sr))
        (neg (use rt))
        (neg (use ts))
        (use t)
        (use s)
        (use r))))

  (def inverse-pseudoscalar-action
    (fn
      ((t Real) (s Real) (r Real) (sr Real) (rt Real) (ts Real))
      (outputs Real Real Real Real Real Real)
      (frontier
        (use sr)
        (use rt)
        (use ts)
        (neg (use t))
        (neg (use s))
        (neg (use r)))))

  (def time-space-swap
    (fn
      ((t Real) (s Real) (r Real) (sr Real) (rt Real) (ts Real))
      (outputs Real Real Real Real Real Real)
      (frontier
        (use s)
        (use t)
        (use r)
        (neg (use rt))
        (neg (use sr))
        (neg (use ts)))))
)
"""

Carrier = tuple[float, float, float, float, float, float]
Metric = tuple[int, int, int]

PORTS = ("t", "s", "r", "sr", "rt", "ts")

# Basis blades use ascending bit-mask order internally.  The relational basis
# follows the cyclic orientation SR, RT, TS; RT = -TR accounts for its sign.
CARRIER_BASIS = (
    (0b001, 1),
    (0b010, 1),
    (0b100, 1),
    (0b110, 1),
    (0b101, -1),
    (0b011, 1),
)
VOLUME_BLADE = 0b111


def _checked_functions() -> tuple[Any, Any, Any]:
    workspace = link_modules([THREE_ASPECT_CHIRALITY_KERNEL])
    return (
        workspace.function("three-aspect-chirality", "pseudoscalar-action"),
        workspace.function("three-aspect-chirality", "inverse-pseudoscalar-action"),
        workspace.function("three-aspect-chirality", "time-space-swap"),
    )


def _evaluate(function: Any, value: Carrier) -> Carrier:
    result = function.evaluate(dict(zip(PORTS, value, strict=True)))
    if not isinstance(result, tuple) or len(result) != 6:
        raise TypeError("three-aspect carrier must have six ordered Real outputs")
    return result


def _scale(scale: float, value: Carrier) -> Carrier:
    return tuple(scale * coordinate for coordinate in value)  # type: ignore[return-value]


def _basis(index: int) -> Carrier:
    return tuple(float(position == index) for position in range(6))  # type: ignore[return-value]


def _geometric_product(left: int, right: int, metric: Metric) -> tuple[int, int]:
    """Multiply canonical basis blades in a diagonal real Clifford algebra."""

    coefficient = 1
    for index in range(3):
        if left & (1 << index):
            lower_right_bits = right & ((1 << index) - 1)
            if lower_right_bits.bit_count() % 2:
                coefficient = -coefficient
        if left & right & (1 << index):
            coefficient *= metric[index]
    return coefficient, left ^ right


def _left_volume_action(value: Carrier, metric: Metric = (1, 1, 1)) -> Carrier:
    """Research oracle for left multiplication by Omega = T S R."""

    output = [0.0] * 6
    for coordinate, (blade, basis_sign) in zip(value, CARRIER_BASIS, strict=True):
        coefficient, output_blade = _geometric_product(VOLUME_BLADE, blade, metric)
        if coefficient == 0:
            continue
        output_index = next(
            index
            for index, (candidate, _sign) in enumerate(CARRIER_BASIS)
            if candidate == output_blade
        )
        output_basis_sign = CARRIER_BASIS[output_index][1]
        output[output_index] += coordinate * basis_sign * coefficient / output_basis_sign
    return tuple(output)  # type: ignore[return-value]


def _permutation_sign(permutation: tuple[int, int, int]) -> int:
    inversions = sum(
        permutation[left] > permutation[right] for left in range(3) for right in range(left + 1, 3)
    )
    return -1 if inversions % 2 else 1


def _inverse_permutation(permutation: tuple[int, int, int]) -> tuple[int, int, int]:
    inverse = [0, 0, 0]
    for source, target in enumerate(permutation):
        inverse[target] = source
    return tuple(inverse)  # type: ignore[return-value]


def _permuted_blade(blade: int, permutation: tuple[int, int, int]) -> tuple[int, int]:
    targets = [permutation[index] for index in range(3) if blade & (1 << index)]
    sign = (
        -1
        if sum(
            targets[left] > targets[right]
            for left in range(len(targets))
            for right in range(left + 1, len(targets))
        )
        % 2
        else 1
    )
    output_blade = sum(1 << target for target in targets)
    return sign, output_blade


def _permute_aspects(value: Carrier, permutation: tuple[int, int, int]) -> Carrier:
    output = [0.0] * 6
    for coordinate, (blade, basis_sign) in zip(value, CARRIER_BASIS, strict=True):
        permutation_sign, output_blade = _permuted_blade(blade, permutation)
        output_index = next(
            index
            for index, (candidate, _sign) in enumerate(CARRIER_BASIS)
            if candidate == output_blade
        )
        output_basis_sign = CARRIER_BASIS[output_index][1]
        output[output_index] += coordinate * basis_sign * permutation_sign / output_basis_sign
    return tuple(output)  # type: ignore[return-value]


def _action_matrix(metric: Metric = (1, 1, 1)) -> sympy.Matrix:
    columns = [
        sympy.Matrix(_left_volume_action(_basis(index), metric)).applyfunc(sympy.nsimplify)
        for index in range(6)
    ]
    return sympy.Matrix.hstack(*columns)


def test_checked_six_carrier_realizes_aspect_opposite_relation_duality() -> None:
    action, inverse_action, time_space_swap = _checked_functions()
    for function in (action, inverse_action, time_space_swap):
        assert function.validation_certificate["graph"] == "checked"
        assert function.signature.inputs == tuple((port, "real") for port in PORTS)
        assert function.signature.outputs == ("real",) * 6

    fixtures: tuple[Carrier, ...] = (
        (1.0, 0.0, 0.0, 0.0, 0.0, 0.0),
        (0.0, 1.0, 0.0, 0.0, 0.0, 0.0),
        (0.0, 0.0, 1.0, 0.0, 0.0, 0.0),
        (2.0, -3.0, 5.0, 7.0, -11.0, 13.0),
    )
    for value in fixtures:
        forward = _evaluate(action, value)
        assert forward == _left_volume_action(value)
        assert _evaluate(action, forward) == _scale(-1.0, value)
        assert _evaluate(inverse_action, value) == _scale(-1.0, forward)
        assert _evaluate(inverse_action, forward) == value

        swapped = _evaluate(time_space_swap, value)
        conjugated = _evaluate(
            time_space_swap,
            _evaluate(action, swapped),
        )
        assert conjugated == _scale(-1.0, forward)


def test_three_aspects_pair_with_the_oriented_relation_of_the_other_two() -> None:
    action = _action_matrix()
    expected_pair_action = sympy.Matrix([[0, -1], [1, 0]])

    # T <-> SR, S <-> RT, R <-> TS.
    for aspect, opposite_relation in ((0, 3), (1, 4), (2, 5)):
        assert (
            action.extract(
                (aspect, opposite_relation),
                (aspect, opposite_relation),
            )
            == expected_pair_action
        )

    assert action**2 == -sympy.eye(6)
    spectral_parameter = sympy.symbols("lambda")
    assert (
        sympy.factor(action.charpoly(spectral_parameter).as_expr())
        == (spectral_parameter**2 + 1) ** 3
    )


@pytest.mark.parametrize("permutation", tuple(permutations(range(3))))
def test_aspect_permutation_changes_chirality_by_its_orientation_character(
    permutation: tuple[int, int, int],
) -> None:
    inverse = _inverse_permutation(permutation)
    parity = float(_permutation_sign(permutation))

    for index in range(6):
        value = _basis(index)
        conjugated = _permute_aspects(
            _left_volume_action(_permute_aspects(value, inverse)),
            permutation,
        )
        assert conjugated == _scale(parity, _left_volume_action(value))


def test_aspect_metric_determinant_recovers_complex_split_dual_trichotomy() -> None:
    identity = sympy.eye(6)
    zero = sympy.zeros(6)

    elliptic = _action_matrix((1, 1, 1))
    hyperbolic = _action_matrix((-1, 1, 1))
    parabolic = _action_matrix((0, 1, 1))

    assert elliptic**2 == -identity
    assert hyperbolic**2 == identity
    assert parabolic**2 == zero
    assert elliptic.det() == 1
    assert hyperbolic.det() == -1
    assert parabolic.det() == 0
