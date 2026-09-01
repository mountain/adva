from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from itertools import combinations, product
from typing import Any, Callable

import sympy

from adva import link_modules


TRIADIC_ACTIVATION = r"""
(module triadic-residual-activation
  (export activate-construction)

  (def activate-construction
    (fn ((space Real) (gate Real) (construction Real)) Real
      (add
        (use space)
        (mul (use gate) (use construction)))))
)
"""


Axis = str
Point = tuple[int, int, int]
Relation = frozenset[Point]

AXES: tuple[Axis, ...] = ("t", "X", "K")
BINARY_POINTS: tuple[Point, ...] = tuple(product((0, 1), repeat=3))


@dataclass(frozen=True, slots=True)
class TriadicState:
    temporal_gate: int
    spatial_value: int
    construction_sign: int
    history: tuple[str, ...]

    def extensional_projection(self) -> tuple[int, int, int]:
        return (
            self.temporal_gate,
            self.spatial_value,
            self.construction_sign,
        )


@dataclass(frozen=True, slots=True)
class RunReport:
    schedule: tuple[Axis, ...]
    states: tuple[TriadicState, ...]

    @property
    def final(self) -> TriadicState:
        return self.states[-1]


def _workspace() -> Any:
    return link_modules([TRIADIC_ACTIVATION])


def _pairwise_marginals(relation: Relation) -> tuple[Counter, Counter, Counter]:
    return (
        Counter((temporal, spatial) for temporal, spatial, _ in relation),
        Counter((spatial, construction) for _, spatial, construction in relation),
        Counter((construction, temporal) for temporal, _, construction in relation),
    )


def _section_on_construction(
    relation: Relation,
    temporal: int,
    spatial: int,
) -> frozenset[int]:
    return frozenset(
        construction
        for current_temporal, current_spatial, construction in relation
        if (current_temporal, current_spatial) == (temporal, spatial)
    )


def _open_temporal_gate(state: TriadicState) -> TriadicState:
    return replace(
        state,
        temporal_gate=1,
        history=(*state.history, "temporal:open"),
    )


def _activate_spatial(function: Any, state: TriadicState) -> TriadicState:
    value = function.evaluate(
        {
            "space": state.spatial_value,
            "gate": state.temporal_gate,
            "construction": state.construction_sign,
        }
    )
    assert float(value).is_integer()
    return replace(
        state,
        spatial_value=int(value),
        history=(*state.history, "spatial:activate"),
    )


def _hold_construction(state: TriadicState) -> TriadicState:
    return replace(
        state,
        history=(*state.history, "construction:hold"),
    )


def _run(
    state: TriadicState,
    schedule: tuple[Axis, ...],
    spatial_program: Any,
) -> RunReport:
    transitions: dict[Axis, Callable[[TriadicState], TriadicState]] = {
        "t": _open_temporal_gate,
        "X": lambda current: _activate_spatial(spatial_program, current),
        "K": _hold_construction,
    }
    states = [state]
    for axis in schedule:
        state = transitions[axis](state)
        states.append(state)
    return RunReport(schedule, tuple(states))


def _coarse_spatial_observer(state: TriadicState) -> int:
    return state.spatial_value


def _minimal_activation_schedules(
    left: TriadicState,
    right: TriadicState,
    spatial_program: Any,
    maximum_length: int,
) -> tuple[tuple[Axis, ...], ...]:
    for length in range(maximum_length + 1):
        witnesses = tuple(
            schedule
            for schedule in product(AXES, repeat=length)
            if _coarse_spatial_observer(
                _run(left, schedule, spatial_program).final
            )
            != _coarse_spatial_observer(
                _run(right, schedule, spatial_program).final
            )
        )
        if witnesses:
            return witnesses
    return ()


def test_balanced_pairwise_marginals_leave_one_binary_triadic_phase() -> None:
    even = frozenset(point for point in BINARY_POINTS if sum(point) % 2 == 0)
    odd = frozenset(point for point in BINARY_POINTS if sum(point) % 2 == 1)

    target = _pairwise_marginals(even)
    assert target == _pairwise_marginals(odd)
    assert even != odd

    compatible = {
        frozenset(candidate)
        for candidate in combinations(BINARY_POINTS, 4)
        if _pairwise_marginals(frozenset(candidate)) == target
    }
    assert compatible == {even, odd}

    for temporal, spatial in product((0, 1), repeat=2):
        assert _section_on_construction(even, temporal, spatial) != (
            _section_on_construction(odd, temporal, spatial)
        )


def test_typed_construction_residual_has_a_minimal_activation_schedule() -> None:
    workspace = _workspace()
    spatial_program = workspace.function(
        "triadic-residual-activation",
        "activate-construction",
    )

    space, gate, construction = sympy.symbols(
        "space gate construction",
        real=True,
    )
    assert sympy.simplify(
        spatial_program.to_sympy() - (space + gate * construction)
    ) == 0

    positive = TriadicState(0, 0, 1, ("origin:positive",))
    negative = TriadicState(0, 0, -1, ("origin:negative",))
    assert _coarse_spatial_observer(positive) == _coarse_spatial_observer(negative)

    witnesses = _minimal_activation_schedules(
        positive,
        negative,
        spatial_program,
        maximum_length=3,
    )
    assert witnesses == (("t", "X"),)

    positive_after = _run(positive, witnesses[0], spatial_program).final
    negative_after = _run(negative, witnesses[0], spatial_program).final
    assert positive_after.spatial_value == 1
    assert negative_after.spatial_value == -1

    resource_count = Counter(witnesses[0])
    assert tuple(resource_count[axis] for axis in AXES) == (1, 1, 0)


def test_schedule_controls_when_the_residual_becomes_observable() -> None:
    spatial_program = _workspace().function(
        "triadic-residual-activation",
        "activate-construction",
    )
    positive = TriadicState(0, 0, 1, ("positive",))
    negative = TriadicState(0, 0, -1, ("negative",))

    forward = ("t", "X")
    reverse = ("X", "t")
    delayed = ("X", "t", "X")

    assert _coarse_spatial_observer(
        _run(positive, forward, spatial_program).final
    ) != _coarse_spatial_observer(
        _run(negative, forward, spatial_program).final
    )
    assert _coarse_spatial_observer(
        _run(positive, reverse, spatial_program).final
    ) == _coarse_spatial_observer(
        _run(negative, reverse, spatial_program).final
    )
    assert _coarse_spatial_observer(
        _run(positive, delayed, spatial_program).final
    ) != _coarse_spatial_observer(
        _run(negative, delayed, spatial_program).final
    )


def test_context_execution_generates_a_future_spatial_proposition() -> None:
    spatial_program = _workspace().function(
        "triadic-residual-activation",
        "activate-construction",
    )
    positive = TriadicState(0, 0, 1, ("positive",))
    negative = TriadicState(0, 0, -1, ("negative",))
    context = ("t", "X")

    def proposition(state: TriadicState) -> bool:
        return _run(state, context, spatial_program).final.spatial_value > 0

    assert not (_coarse_spatial_observer(positive) > 0)
    assert not (_coarse_spatial_observer(negative) > 0)
    assert proposition(positive)
    assert not proposition(negative)


def test_history_only_residual_is_inert_for_history_blind_programs() -> None:
    spatial_program = _workspace().function(
        "triadic-residual-activation",
        "activate-construction",
    )
    left = TriadicState(0, 2, 1, ("history:left",))
    right = TriadicState(0, 2, 1, ("history:right",))
    assert left.extensional_projection() == right.extensional_projection()
    assert left.history != right.history

    for length in range(5):
        for schedule in product(AXES, repeat=length):
            left_after = _run(left, schedule, spatial_program).final
            right_after = _run(right, schedule, spatial_program).final
            assert left_after.extensional_projection() == (
                right_after.extensional_projection()
            )
            assert left_after.history != right_after.history

