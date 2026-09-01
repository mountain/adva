from __future__ import annotations

from collections import Counter, deque
from itertools import product
from typing import Any, Mapping

import pytest

from adva import link_modules


CHECKED_TRIADIC_GENERATORS = r"""
(module checked-triadic-generators
  (export
    temporal-preserve temporal-replace spatial-update construction-flip)

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

  (def temporal-preserve
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (add 1 (mul 0 (use temporal)))
        (use spatial)
        (use construction))))

  (def temporal-replace
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use temporal))
        1
        (use spatial)
        (use construction))))

  (def spatial-update
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use spatial))
        (call spatial-body
          (frontier
            (copy (use temporal))
            (copy (use construction)))))))

  (def construction-flip
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (use temporal)
        (use spatial)
        (add 1 (neg (use construction))))))
)
"""


Axis = str
Context = tuple[Axis, ...]
CoreState = tuple[int, int, int]
Transformation = tuple[int, ...]

AXES: tuple[Axis, ...] = ("T", "X", "K")
PROGRAM_NAMES: Mapping[Axis, str] = {
    "T": "temporal-preserve",
    "X": "spatial-update",
    "K": "construction-flip",
}
CORE_STATES: tuple[CoreState, ...] = tuple(product((0, 1), repeat=3))
CORE_INDEX = {state: index for index, state in enumerate(CORE_STATES)}
IDENTITY: Transformation = tuple(range(len(CORE_STATES)))


@pytest.fixture(scope="module")
def workspace():
    return link_modules([CHECKED_TRIADIC_GENERATORS])


def _oracle_step(state: CoreState, axis: Axis) -> CoreState:
    temporal, spatial, construction = state
    if axis == "T":
        return (1, spatial, construction)
    if axis == "X":
        return (temporal, temporal & construction, construction)
    if axis == "K":
        return (temporal, spatial, 1 - construction)
    raise ValueError(f"unknown axis: {axis}")


def _evaluate_state(function: Any, state: CoreState) -> CoreState:
    values = function.evaluate(
        {
            "temporal": state[0],
            "spatial": state[1],
            "construction": state[2],
        }
    )
    assert isinstance(values, tuple)
    assert len(values) == 3
    assert all(float(value).is_integer() for value in values)
    return tuple(int(value) for value in values)  # type: ignore[return-value]


def _checked_generators(workspace: Any) -> dict[Axis, Transformation]:
    return {
        axis: tuple(
            CORE_INDEX[
                _evaluate_state(
                    workspace.function(
                        "checked-triadic-generators",
                        function_name,
                    ),
                    state,
                )
            ]
            for state in CORE_STATES
        )
        for axis, function_name in PROGRAM_NAMES.items()
    }


def _oracle_generators() -> dict[Axis, Transformation]:
    return {
        axis: tuple(CORE_INDEX[_oracle_step(state, axis)] for state in CORE_STATES)
        for axis in AXES
    }


def _compose(
    first: Transformation,
    second: Transformation,
) -> Transformation:
    """Execute ``first`` and then ``second``."""

    return tuple(second[first[index]] for index in range(len(CORE_STATES)))


def _monoid(
    generators: Mapping[Axis, Transformation],
) -> dict[Transformation, Context]:
    shortest: dict[Transformation, Context] = {IDENTITY: ()}
    frontier = deque([IDENTITY])
    while frontier:
        transformation = frontier.popleft()
        for axis in AXES:
            candidate = _compose(transformation, generators[axis])
            if candidate not in shortest:
                shortest[candidate] = (*shortest[transformation], axis)
                frontier.append(candidate)
    return shortest


def _node_ids(function: Any) -> tuple[int, ...]:
    return tuple(node["id"] for node in function.ir["nodes"])


def _operation_names(function: Any) -> Counter[str]:
    return Counter(node["operation"]["name"] for node in function.ir["nodes"])


def _final_frontier(function: Any) -> tuple[Mapping[str, Any], ...]:
    return function.causal_cut(_node_ids(function)).frontier


def _sources_by_input(function: Any) -> dict[int, tuple[str, ...]]:
    initial = function.causal_cut([])
    return {
        item["wire"]["producer"]["index"]: tuple(item["sources"])
        for item in initial.frontier
        if item["wire"]["producer"]["kind"] == "input"
    }


def test_rust_execution_generates_the_exact_sixteen_element_monoid(
    workspace,
) -> None:
    checked = _checked_generators(workspace)
    oracle = _oracle_generators()

    assert checked == oracle
    for axis, function_name in PROGRAM_NAMES.items():
        function = workspace.function(
            "checked-triadic-generators",
            function_name,
        )
        assert function.validation_certificate["graph"] == "checked"
        assert function.validation_certificate["linear_use"] == "checked"
        for state in CORE_STATES:
            assert _evaluate_state(function, state) == _oracle_step(state, axis)

    checked_monoid = _monoid(checked)
    oracle_monoid = _monoid(oracle)
    assert checked_monoid == oracle_monoid
    assert len(checked_monoid) == 16
    assert max(map(len, checked_monoid.values())) == 4
    assert set(checked_monoid) == {
        _compose(left, right)
        for left in checked_monoid
        for right in checked_monoid
    }


def test_atomic_temporal_suffix_is_a_complete_checked_program_interval(
    workspace,
) -> None:
    temporal = workspace.function(
        "checked-triadic-generators",
        "temporal-preserve",
    )
    nodes = _node_ids(temporal)
    interval = temporal.program_slice([], nodes)

    assert interval.certificate["event_difference"] == "checked"
    assert interval.certificate["original_id_preservation"] == "checked"
    assert interval.result.lower["completed"] == []
    assert tuple(interval.result.upper["completed"]) == nodes
    assert tuple(event["id"] for event in interval.result.events) == nodes
    assert len(interval.result.through_wires) == 2

    temporal_generator = _checked_generators(workspace)["T"]
    for state in CORE_STATES:
        checked_target = _evaluate_state(temporal, state)
        assert CORE_INDEX[checked_target] == temporal_generator[CORE_INDEX[state]]


def test_spatial_generator_retains_copy_discard_and_output_lineage(
    workspace,
) -> None:
    spatial = workspace.function(
        "checked-triadic-generators",
        "spatial-update",
    )
    nodes = _node_ids(spatial)
    interval = spatial.program_slice([], nodes)
    names = _operation_names(spatial)

    assert names == Counter({"copy": 2, "discard": 1, "mul": 1})
    assert len(interval.result.lower_boundary) == 3
    assert len(interval.result.upper_boundary) == 3
    assert interval.result.through_wires == ()

    discard_node = next(
        node["id"]
        for node in spatial.ir["nodes"]
        if node["operation"]["name"] == "discard"
    )
    assert discard_node in interval.result.internal_events

    copy_events = [
        event
        for event in interval.result.event_history
        if event["kind"] == "copy"
    ]
    assert len(copy_events) == 2
    operation_history = Counter(
        event["operation"]["name"]
        for event in interval.result.event_history
        if event["kind"] == "operation"
    )
    assert operation_history == names

    inputs = _sources_by_input(spatial)
    final = _final_frontier(spatial)
    output_sources = tuple(tuple(item["sources"]) for item in final)
    assert output_sources[0] == inputs[0]
    assert set(output_sources[1]) == {*inputs[0], *inputs[2]}
    assert output_sources[2] == inputs[2]
    assert inputs[1][0] not in {
        source for sources in output_sources for source in sources
    }

    final_lineage = {
        occurrence
        for item in final
        for occurrence in item["wire"]["lineage"]
    }
    for event in copy_events:
        assert event["parent"] not in final_lineage
        assert set(event["children"]) <= final_lineage


def test_extensional_temporal_action_does_not_select_one_presentation(
    workspace,
) -> None:
    preserve = workspace.function(
        "checked-triadic-generators",
        "temporal-preserve",
    )
    replace = workspace.function(
        "checked-triadic-generators",
        "temporal-replace",
    )

    for state in CORE_STATES:
        assert _evaluate_state(preserve, state) == _evaluate_state(replace, state)
        assert _evaluate_state(preserve, state) == _oracle_step(state, "T")

    assert preserve.ir != replace.ir
    assert preserve.history != replace.history
    assert _operation_names(preserve) == Counter(
        {"constant": 2, "mul": 1, "add": 1}
    )
    assert _operation_names(replace) == Counter({"discard": 1, "constant": 1})

    preserve_temporal = _final_frontier(preserve)[0]
    replace_temporal = _final_frontier(replace)[0]
    assert preserve_temporal["sources"]
    assert preserve_temporal["wire"]["lineage"]
    assert replace_temporal["sources"] == []
    assert replace_temporal["wire"]["lineage"] == []

    preserve_interval = preserve.program_slice([], _node_ids(preserve))
    replace_interval = replace.program_slice([], _node_ids(replace))
    assert preserve_interval.result != replace_interval.result
    assert replace_interval.result.internal_events
