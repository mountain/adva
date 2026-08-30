from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass
import json
from typing import Any, TypeAlias

from adva import KernelFunction, link_modules


NESTED_FRAME_PSP = r"""
(module nested-frame-psp
  (export root)

  (def add-two
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (use left)
          (use right)))))

  (def wrapper
    (fn ((left Real) (right Real)) Real
      (call add-two
        (use left)
        (use right))))

  (def root
    (fn ((x Real) (y Real) (z Real)) (outputs Real Real)
      (frontier
        (call wrapper
          (use x)
          (use y))
        (neg (use z)))))
)
"""


Relation: TypeAlias = frozenset[tuple[Hashable, Hashable]]


@dataclass(frozen=True, slots=True)
class NestedInputExpression:
    frame_stack: tuple[tuple[str, str, str], ...]
    ordered_holes: tuple[tuple[str, tuple[tuple[int, str], ...]], ...]
    entry_wires: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NestedOutputExpression:
    frame_stack: tuple[tuple[str, str, str], ...]
    body_events: tuple[int, ...]
    exit_wires: tuple[str, ...]


def _then(left: Relation, right: Relation) -> Relation:
    return frozenset(
        (source, target)
        for source, middle in left
        for candidate, target in right
        if middle == candidate
    )


def _converse(relation: Relation) -> Relation:
    return frozenset((target, source) for source, target in relation)


def _key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _call_frame(function: KernelFunction, callee: str) -> Mapping[str, Any]:
    trace = function.graft_trace
    assert trace is not None
    return next(
        frame
        for frame in trace.result.frames
        if frame["kind"] == "call" and frame["callee"]["function"] == callee
    )


def _frontier_wires(function: KernelFunction, completed) -> tuple[Mapping[str, Any], ...]:
    return tuple(crossing["wire"] for crossing in function.causal_cut(completed).frontier)


def _contains_boundary(frontier, boundary) -> bool:
    return all(wire in frontier for wire in boundary)


def _ordered_holes(frame: Mapping[str, Any]) -> tuple[tuple[int, str], ...]:
    return tuple(
        (hole["hole_index"], hole["hole"]["name"]) for hole in frame["holes"]
    )


def _fixture():
    function = link_modules([NESTED_FRAME_PSP]).function("nested-frame-psp", "root")
    parent = _call_frame(function, "wrapper")
    child = _call_frame(function, "add-two")
    frame_stack = tuple(
        (frame["id"], _key(frame["scope_path"]), _key(frame["region_in_parent"]))
        for frame in (parent, child)
    )
    input_expression = NestedInputExpression(
        frame_stack=frame_stack,
        ordered_holes=tuple(
            (frame["id"], _ordered_holes(frame)) for frame in (parent, child)
        ),
        entry_wires=tuple(_key(wire) for wire in parent["entry_wires"]),
    )
    output_expression = NestedOutputExpression(
        frame_stack=frame_stack,
        body_events=tuple(parent["body_region"]),
        exit_wires=tuple(_key(wire) for wire in parent["exit_wires"]),
    )
    return function, parent, child, input_expression, output_expression


def _body_surgery(function: KernelFunction) -> Relation:
    edges = []
    for lower in ((), (1,)):
        step = function.advance_causal_cut(lower, 0)
        edges.append(
            (tuple(step.before["completed"]), tuple(step.after["completed"]))
        )
    return frozenset(edges)


def test_nested_parent_and_child_overlap_on_one_exact_callee_body_event():
    function, parent, child, input_expression, output_expression = _fixture()

    assert child["parent"] == parent["id"]
    assert child["id"] in parent["children"]
    assert child["region_in_parent"] == {"kind": "callee_body"}
    assert parent["body_region"] == [0]
    assert child["body_region"] == [0]
    assert parent["entry_wires"] == child["entry_wires"]
    assert parent["exit_wires"] == child["exit_wires"]
    assert input_expression.ordered_holes == (
        (parent["id"], ((0, "left"), (1, "right"))),
        (child["id"], ((0, "left"), (1, "right"))),
    )
    assert output_expression.body_events == (0,)
    assert _body_surgery(function) == frozenset({((), (0,)), ((1,), (0, 1))})


def test_naive_nested_surgery_composition_would_execute_the_shared_event_twice():
    function, _, _, _, _ = _fixture()
    surgery = _body_surgery(function)

    assert _then(surgery, surgery) == frozenset()


def test_frame_stack_glues_the_shared_surgery_once_and_factors_both_directions():
    function, parent, _, input_expression, output_expression = _fixture()
    cuts = ((), (0,), (1,), (0, 1))
    p_star_input: Relation = frozenset(
        (input_expression, cut)
        for cut in cuts
        if _contains_boundary(_frontier_wires(function, cut), parent["entry_wires"])
    )
    p_output: Relation = frozenset(
        (cut, output_expression)
        for cut in cuts
        if _contains_boundary(_frontier_wires(function, cut), parent["exit_wires"])
    )
    surgery = _body_surgery(function)
    transformation: Relation = frozenset({(input_expression, output_expression)})

    assert _then(_then(p_star_input, surgery), p_output) == transformation
    assert _then(
        _then(_converse(p_output), _converse(surgery)),
        _converse(p_star_input),
    ) == _converse(transformation)


def test_one_slice_records_both_overlapping_frame_roles_without_event_duplication():
    function, parent, child, _, _ = _fixture()

    for lower, upper in (((), (0,)), ((1,), (0, 1))):
        program_slice = function.program_slice(lower, upper)
        assert [event["id"] for event in program_slice.result.events] == [0]
        assert program_slice.result.graft_intersections is not None
        intersections = {
            item["frame"]: item for item in program_slice.result.graft_intersections
        }
        assert intersections[parent["id"]]["body_events"] == [0]
        assert intersections[child["id"]]["body_events"] == [0]
        assert len(program_slice.result.events) == 1
