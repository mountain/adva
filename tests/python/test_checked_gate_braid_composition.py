from __future__ import annotations

from collections import Counter, deque
from itertools import permutations, product
from typing import Any, Mapping, TypeAlias

import pytest

from adva import link_modules


CHECKED_BRAID_GATE = r"""
(module checked-braid-gate
  (export spatial-update)

  (def spatial-body
    (fn (
          (temporal-output Real)
          (temporal-use Real)
          (construction-use Real)
          (construction-output Real))
        (outputs Real Real Real)
      (frontier
        (use temporal-output)
        (mul (use temporal-use) (use construction-use))
        (use construction-output))))

  (def spatial-update
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use spatial))
        (call spatial-body
          (frontier
            (copy (use temporal))
            (copy (use construction)))))))
)
"""


BraidWord: TypeAlias = tuple[int, ...]
FreeWord: TypeAlias = tuple[int, ...]
FreeAutomorphism: TypeAlias = tuple[FreeWord, FreeWord, FreeWord]
Boundary: TypeAlias = tuple[str, ...]
Port: TypeAlias = tuple[str, int]
Frame: TypeAlias = tuple[Port, ...]
CoreState: TypeAlias = tuple[int, int, int]
ScheduleEvent: TypeAlias = str | BraidWord
Schedule: TypeAlias = tuple[ScheduleEvent, ...]

COLORS: Boundary = ("K", "X", "t")
FREE_IDENTITY: FreeAutomorphism = ((1,), (2,), (3,))
CORE_STATES: tuple[CoreState, ...] = tuple(product((0, 1), repeat=3))


@pytest.fixture(scope="module")
def workspace():
    return link_modules([CHECKED_BRAID_GATE])


def _evaluate_x(function: Any, state: CoreState) -> CoreState:
    temporal, spatial, construction = state
    values = function.evaluate(
        {
            "temporal": temporal,
            "spatial": spatial,
            "construction": construction,
        }
    )
    assert isinstance(values, tuple)
    assert len(values) == 3
    assert all(float(value).is_integer() for value in values)
    return tuple(int(value) for value in values)  # type: ignore[return-value]


def _oracle_x(state: CoreState) -> CoreState:
    temporal, _, construction = state
    return (temporal, temporal & construction, construction)


def _public_frame(state: CoreState) -> Frame:
    """Map program order (t, x, k) to the public colored order (K, X, t)."""

    return _frame(COLORS, state)


def _frame(boundary: Boundary, state: CoreState) -> Frame:
    """Attach one program state to any typed permutation of the boundary."""

    temporal, spatial, construction = state
    values = {"K": construction, "X": spatial, "t": temporal}
    if len(boundary) != len(COLORS) or set(boundary) != set(COLORS):
        raise ValueError("a boundary must contain exactly one K, X, and t color")
    return tuple((color, values[color]) for color in boundary)


def _logical_state(frame: Frame) -> CoreState:
    values = {color: value for color, value in frame}
    if set(values) != set(COLORS) or len(frame) != len(COLORS):
        raise ValueError("a frame must contain exactly one K, X, and t port")
    return (values["t"], values["X"], values["K"])


def _apply_checked_x(function: Any, frame: Frame) -> Frame:
    """Run the checked gate by color names, never by the current tuple positions."""

    output = _evaluate_x(function, _logical_state(frame))
    updated = {"t": output[0], "X": output[1], "K": output[2]}
    return tuple((color, updated[color]) for color, _ in frame)


def _transport(frame: Frame, word: BraidWord) -> Frame:
    result = list(frame)
    for letter in word:
        index = abs(letter) - 1
        if index not in (0, 1):
            raise ValueError(f"B_3 has only sigma_1 and sigma_2, not {letter}")
        result[index], result[index + 1] = result[index + 1], result[index]
    return tuple(result)


def _endpoint_boundary(boundary: Boundary, word: BraidWord) -> Boundary:
    frame = tuple((color, 0) for color in boundary)
    return tuple(color for color, _ in _transport(frame, word))


def _run(function: Any, state: CoreState, schedule: Schedule) -> Frame:
    frame = _public_frame(state)
    for event in schedule:
        if event == "X":
            frame = _apply_checked_x(function, frame)
        elif isinstance(event, tuple):
            frame = _transport(frame, event)
        else:
            raise ValueError(f"unknown schedule event: {event!r}")
    return frame


def _reduce_free(word: FreeWord) -> FreeWord:
    result: list[int] = []
    for letter in word:
        if letter == 0 or abs(letter) > 3:
            raise ValueError(f"invalid F_3 generator {letter}")
        if result and result[-1] == -letter:
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def _inverse_free(word: FreeWord) -> FreeWord:
    return tuple(-letter for letter in reversed(word))


def _substitute(word: FreeWord, images: FreeAutomorphism) -> FreeWord:
    expanded: list[int] = []
    for letter in word:
        image = images[abs(letter) - 1]
        expanded.extend(image if letter > 0 else _inverse_free(image))
    return _reduce_free(tuple(expanded))


def _compose(after: FreeAutomorphism, before: FreeAutomorphism) -> FreeAutomorphism:
    """Return after o before as exact reduced words in the free group F_3."""

    return tuple(_substitute(image, after) for image in before)  # type: ignore[return-value]


def _artin_generator(letter: int) -> FreeAutomorphism:
    index = abs(letter) - 1
    if index not in (0, 1):
        raise ValueError(f"B_3 has only sigma_1 and sigma_2, not {letter}")
    left = index + 1
    right = index + 2
    images = list(FREE_IDENTITY)
    if letter > 0:
        images[index] = (left, right, -left)
        images[index + 1] = (left,)
    else:
        images[index] = (right,)
        images[index + 1] = (-right, left, right)
    return tuple(images)  # type: ignore[return-value]


def _artin_action(word: BraidWord) -> FreeAutomorphism:
    result = FREE_IDENTITY
    for letter in word:
        result = _compose(_artin_generator(letter), result)
    return result


def _inverse_braid(word: BraidWord) -> BraidWord:
    return tuple(-letter for letter in reversed(word))


def _presented_history(schedule: Schedule) -> tuple[object, ...]:
    """Normalize maximal braid blocks by Artin equality and retain gate separators."""

    result: list[object] = []
    braid_block: BraidWord = ()
    for event in schedule:
        if isinstance(event, tuple):
            braid_block += event
            continue
        action = _artin_action(braid_block)
        if action != FREE_IDENTITY:
            result.append(("braid", action))
        braid_block = ()
        result.append(("gate", event))
    action = _artin_action(braid_block)
    if action != FREE_IDENTITY:
        result.append(("braid", action))
    return tuple(result)


def _pair_windings(boundary: Boundary, word: BraidWord) -> dict[tuple[str, str], int]:
    if _endpoint_boundary(boundary, word) != boundary:
        raise ValueError("pair windings require a pure colored braid")
    positions = list(boundary)
    counts = {
        tuple(sorted((left, right))): 0
        for offset, left in enumerate(boundary)
        for right in boundary[offset + 1 :]
    }
    for letter in word:
        index = abs(letter) - 1
        pair = tuple(sorted((positions[index], positions[index + 1])))
        counts[pair] += 1 if letter > 0 else -1
        positions[index], positions[index + 1] = positions[index + 1], positions[index]
    if any(count % 2 for count in counts.values()):
        raise AssertionError("a pure colored braid has even signed pair counts")
    return {pair: count // 2 for pair, count in counts.items()}


def _operation_names(function: Any) -> Counter[str]:
    return Counter(node["operation"]["name"] for node in function.ir["nodes"])


def _node_ids(function: Any) -> tuple[int, ...]:
    return tuple(node["id"] for node in function.ir["nodes"])


def _final_frontier(function: Any) -> tuple[Mapping[str, Any], ...]:
    return function.causal_cut(_node_ids(function)).frontier


def _sources_by_input(function: Any) -> dict[int, tuple[str, ...]]:
    initial = function.causal_cut([])
    return {
        item["wire"]["producer"]["index"]: tuple(item["sources"])
        for item in initial.frontier
        if item["wire"]["producer"]["kind"] == "input"
    }


def _dilation(state: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    """One-step reversible dilation with the old x retained as explicit garbage."""

    temporal, spatial, construction, garbage = state
    return (
        temporal,
        garbage ^ (temporal & construction),
        construction,
        spatial,
    )


def _inverse_dilation(state: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    temporal, spatial, construction, old_spatial = state
    return (
        temporal,
        old_spatial,
        construction,
        spatial ^ (temporal & construction),
    )


def test_checked_x_is_rank_four_idempotent_with_explicit_resource_loss(workspace) -> None:
    spatial = workspace.function("checked-braid-gate", "spatial-update")

    assert spatial.validation_certificate["graph"] == "checked"
    assert spatial.validation_certificate["linear_use"] == "checked"
    assert _operation_names(spatial) == Counter({"copy": 2, "discard": 1, "mul": 1})

    targets = tuple(_evaluate_x(spatial, state) for state in CORE_STATES)
    assert targets == tuple(_oracle_x(state) for state in CORE_STATES)
    assert len(set(targets)) == 4
    assert sorted(Counter(targets).values()) == [2, 2, 2, 2]
    assert tuple(_oracle_x(target) for target in targets) == targets

    interval = spatial.program_slice([], _node_ids(spatial))
    assert len(interval.result.lower_boundary) == 3
    assert len(interval.result.upper_boundary) == 3
    assert interval.result.through_wires == ()

    discard_node = next(
        node["id"]
        for node in spatial.ir["nodes"]
        if node["operation"]["name"] == "discard"
    )
    assert discard_node in interval.result.internal_events

    inputs = _sources_by_input(spatial)
    final = _final_frontier(spatial)
    output_sources = tuple(tuple(item["sources"]) for item in final)
    assert output_sources[0] == inputs[0]
    assert set(output_sources[1]) == {*inputs[0], *inputs[2]}
    assert output_sources[2] == inputs[2]
    assert inputs[1][0] not in {
        source for sources in output_sources for source in sources
    }

    copy_events = [
        event for event in interval.result.event_history if event["kind"] == "copy"
    ]
    final_lineage = {
        occurrence
        for item in final
        for occurrence in item["wire"]["lineage"]
    }
    assert len(copy_events) == 2
    for event in copy_events:
        assert event["parent"] not in final_lineage
        assert set(event["children"]) <= final_lineage


def test_checked_x_is_color_natural_across_every_elementary_crossing(workspace) -> None:
    spatial = workspace.function("checked-braid-gate", "spatial-update")

    for boundary in permutations(COLORS):
        for letter in (-2, -1, 1, 2):
            crossing = (letter,)
            for state in CORE_STATES:
                frame = _frame(boundary, state)
                gate_then_braid = _transport(_apply_checked_x(spatial, frame), crossing)
                braid_then_gate = _apply_checked_x(spatial, _transport(frame, crossing))

                assert gate_then_braid == braid_then_gate
                assert Counter(_transport(frame, crossing)) == Counter(frame)


def test_artin_equal_transports_give_coherent_conjugated_gate_runs(workspace) -> None:
    spatial = workspace.function("checked-braid-gate", "spatial-update")
    left = (1, 2, 1)
    right = (2, 1, 2)
    left_schedule: Schedule = (left, "X", _inverse_braid(left))
    right_schedule: Schedule = (right, "X", _inverse_braid(right))

    assert _endpoint_boundary(COLORS, left) == _endpoint_boundary(COLORS, right)
    assert _artin_action(left) == _artin_action(right)
    assert _presented_history(left_schedule) == _presented_history(right_schedule)
    assert _presented_history(((1,), (2,), "X")) == _presented_history(((1, 2), "X"))
    assert _presented_history(((), "X")) == _presented_history(("X",))
    for state in CORE_STATES:
        assert _run(spatial, state, left_schedule) == _run(spatial, state, right_schedule)
        assert _logical_state(_run(spatial, state, left_schedule)) == _oracle_x(state)


def test_pure_braid_history_is_a_contextual_kernel_for_the_checked_gate(workspace) -> None:
    spatial = workspace.function("checked-braid-gate", "spatial-update")
    full_twist = (1, 2) * 3
    a_12 = (1, 1)
    a_23 = (2, 2)
    commutator = a_12 + a_23 + _inverse_braid(a_12) + _inverse_braid(a_23)
    pure_braids = (full_twist, commutator)
    contexts: tuple[tuple[Schedule, Schedule], ...] = (
        ((), ()),
        (("X",), ()),
        (((1,), "X"), ((-1,),)),
        (((1, 2), "X"), ((-2, -1), "X")),
    )

    assert _pair_windings(COLORS, commutator) == {
        ("K", "X"): 0,
        ("K", "t"): 0,
        ("X", "t"): 0,
    }
    for pure in pure_braids:
        assert _endpoint_boundary(COLORS, pure) == COLORS
        assert _artin_action(pure) != FREE_IDENTITY
        assert _presented_history((pure, "X")) != _presented_history(("X", pure))
        for prefix, suffix in contexts:
            with_residual = prefix + (pure,) + suffix
            without_residual = prefix + suffix
            for state in CORE_STATES:
                assert _run(spatial, state, with_residual) == _run(
                    spatial,
                    state,
                    without_residual,
                )


def test_complete_mixed_state_closure_has_only_identity_and_x_at_public_boundary(
    workspace,
) -> None:
    spatial = workspace.function("checked-braid-gate", "spatial-update")
    identity = CORE_STATES
    checked_x = tuple(_evaluate_x(spatial, state) for state in CORE_STATES)
    start = (COLORS, identity)
    closure = {start}
    frontier = deque([start])

    while frontier:
        boundary, transformation = frontier.popleft()
        candidates = [
            (_endpoint_boundary(boundary, (letter,)), transformation)
            for letter in (-2, -1, 1, 2)
        ]
        candidates.append(
            (
                boundary,
                tuple(_evaluate_x(spatial, state) for state in transformation),
            )
        )
        for candidate in candidates:
            if candidate not in closure:
                closure.add(candidate)
                frontier.append(candidate)

    all_boundaries = set(permutations(COLORS))
    assert {boundary for boundary, _ in closure} == all_boundaries
    assert len(closure) == 2 * len(all_boundaries)
    assert {
        transformation
        for boundary, transformation in closure
        if boundary == COLORS
    } == {identity, checked_x}


def test_a_position_coded_gate_fails_the_typed_transport_square() -> None:
    def overwrite_middle(frame: Frame) -> Frame:
        left, middle, right = frame
        return (left, (middle[0], left[1] & right[1]), right)

    frame = _public_frame((1, 0, 1))
    gate_then_braid = _transport(overwrite_middle(frame), (1,))
    braid_then_gate = overwrite_middle(_transport(frame, (1,)))

    assert gate_then_braid != braid_then_gate
    assert gate_then_braid == (("X", 1), ("K", 1), ("t", 1))
    assert braid_then_gate == (("X", 0), ("K", 0), ("t", 1))


def test_one_bit_dilation_is_reversible_but_does_not_preserve_x_iteration() -> None:
    extended_states = tuple(product((0, 1), repeat=4))
    images = tuple(_dilation(state) for state in extended_states)

    assert len(set(images)) == len(extended_states)
    assert all(_inverse_dilation(_dilation(state)) == state for state in extended_states)
    for state in CORE_STATES:
        temporal, spatial, construction = state
        lifted = _dilation((temporal, spatial, construction, 0))
        assert lifted[:3] == _oracle_x(state)
        assert lifted[3] == spatial

    assert any(
        _dilation(_dilation((*state, 0)))[:3] != _oracle_x(_oracle_x(state))
        for state in CORE_STATES
    )
