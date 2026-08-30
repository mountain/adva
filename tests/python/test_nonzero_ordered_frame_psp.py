from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass
import json
from typing import Any, TypeAlias

from adva import KernelFunction, link_modules


NONZERO_ORDERED_FRAME = r"""
(module nonzero-ordered-frame
  (export root)

  (def add-two
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (use left)
          (use right)))))

  (def root
    (fn ((x Real) (y Real) (z Real)) (outputs Real Real)
      (frontier
        (call add-two
          (use x)
          (use y))
        (neg (use z)))))
)
"""


Relation: TypeAlias = frozenset[tuple[Hashable, Hashable]]


@dataclass(frozen=True, slots=True)
class InputExpression:
    frame: str
    holes: tuple[tuple[int, str], ...]
    entry_wires: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class OutputExpression:
    frame: str
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


def _wire_key(wire: Mapping[str, Any]) -> str:
    return json.dumps(wire, sort_keys=True, separators=(",", ":"))


def _call_frame(function: KernelFunction) -> Mapping[str, Any]:
    trace = function.graft_trace
    assert trace is not None
    frames = [frame for frame in trace.result.frames if frame["kind"] == "call"]
    assert len(frames) == 1
    return frames[0]


def _frontier_wires(function: KernelFunction, completed) -> tuple[Mapping[str, Any], ...]:
    return tuple(crossing["wire"] for crossing in function.causal_cut(completed).frontier)


def _contains_boundary(frontier, boundary) -> bool:
    return all(wire in frontier for wire in boundary)


def _fixture():
    function = link_modules([NONZERO_ORDERED_FRAME]).function(
        "nonzero-ordered-frame", "root"
    )
    frame = _call_frame(function)
    input_expression = InputExpression(
        frame=frame["id"],
        holes=tuple(
            (hole["hole_index"], hole["hole"]["name"]) for hole in frame["holes"]
        ),
        entry_wires=tuple(_wire_key(wire) for wire in frame["entry_wires"]),
    )
    output_expression = OutputExpression(
        frame=frame["id"],
        body_events=tuple(frame["body_region"]),
        exit_wires=tuple(_wire_key(wire) for wire in frame["exit_wires"]),
    )
    return function, frame, input_expression, output_expression


def test_nonzero_frame_requires_polarized_entry_and_exit_incidence():
    function, frame, input_expression, output_expression = _fixture()
    cuts = ((), (0,), (1,), (0, 1))

    assert input_expression.holes == ((0, "left"), (1, "right"))
    assert output_expression.body_events == (0,)
    assert [argument["nodes"] for argument in frame["arguments"]] == [[], []]
    assert frame["entry_wires"] != frame["exit_wires"]

    unpolarized = tuple(
        cut
        for cut in cuts
        if _contains_boundary(_frontier_wires(function, cut), frame["entry_wires"])
        and _contains_boundary(_frontier_wires(function, cut), frame["exit_wires"])
    )
    assert unpolarized == ()


def test_body_surgery_factors_the_ordered_add_transformation_on_both_concurrency_paths():
    function, frame, input_expression, output_expression = _fixture()
    cuts = ((), (0,), (1,), (0, 1))

    p_star_input: Relation = frozenset(
        (input_expression, cut)
        for cut in cuts
        if _contains_boundary(_frontier_wires(function, cut), frame["entry_wires"])
    )
    p_output: Relation = frozenset(
        (cut, output_expression)
        for cut in cuts
        if _contains_boundary(_frontier_wires(function, cut), frame["exit_wires"])
    )
    assert p_star_input == frozenset(
        {(input_expression, ()), (input_expression, (1,))}
    )
    assert p_output == frozenset(
        {((0,), output_expression), ((0, 1), output_expression)}
    )

    body_surgery: Relation = frozenset(
        (
            tuple(function.advance_causal_cut(lower, 0).before["completed"]),
            tuple(function.advance_causal_cut(lower, 0).after["completed"]),
        )
        for lower in ((), (1,))
    )
    assert body_surgery == frozenset({((), (0,)), ((1,), (0, 1))})

    transformation: Relation = frozenset({(input_expression, output_expression)})
    assert _then(_then(p_star_input, body_surgery), p_output) == transformation

    reverse = _then(
        _then(_converse(p_output), _converse(body_surgery)),
        _converse(p_star_input),
    )
    assert reverse == _converse(transformation)


def test_both_body_slices_retain_the_same_exact_frame_role_and_event():
    function, frame, _, _ = _fixture()

    for lower, upper in (((), (0,)), ((1,), (0, 1))):
        program_slice = function.program_slice(lower, upper)
        assert [event["id"] for event in program_slice.result.events] == [0]
        assert program_slice.result.graft_intersections is not None
        intersection = next(
            item
            for item in program_slice.result.graft_intersections
            if item["frame"] == frame["id"]
        )
        assert intersection["argument_events"] == [
            {"argument_index": 0, "events": []},
            {"argument_index": 1, "events": []},
        ]
        assert intersection["body_events"] == [0]
        assert program_slice.certificate["graft_frame_consistency"] == "checked"
