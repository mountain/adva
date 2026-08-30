from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pytest

from adva import KernelFunction, link_modules


ZERO_EVENT_SCOPE = r"""
(module scope-cut-incidence
  (export call-first call-second)

  (def identity-callee
    (fn ((value Real)) Real
      (use value)))

  (def call-first
    (fn ((x Real) (y Real)) (outputs Real Real)
      (frontier
        (call identity-callee (use x))
        (neg (use y)))))

  (def call-second
    (fn ((x Real) (y Real)) (outputs Real Real)
      (frontier
        (neg (use y))
        (call identity-callee (use x)))))
)
"""


@dataclass(frozen=True, slots=True)
class ScopeCutPlacement:
    """One research-local compatible placement, not a stable semantic type."""

    completed: tuple[int, ...]
    cut_frontier: tuple[Mapping[str, Any], ...]


@pytest.fixture
def workspace():
    return link_modules([ZERO_EVENT_SCOPE])


def _identity_frame(function: KernelFunction) -> Mapping[str, Any]:
    trace = function.graft_trace
    assert trace is not None
    frames = [frame for frame in trace.result.frames if frame["kind"] == "call"]
    assert len(frames) == 1
    return frames[0]


def _wire_crosses(cut_frontier, wire):
    return any(crossing["wire"] == wire for crossing in cut_frontier)


def _compatible_identity_placements(
    function: KernelFunction, frame: Mapping[str, Any]
) -> tuple[ScopeCutPlacement, ...]:
    placements = []
    for completed in ((), (0,)):
        cut = function.causal_cut(completed)
        identity_slice = function.program_slice(completed, completed)
        entries_cross = all(
            _wire_crosses(cut.frontier, wire) for wire in frame["entry_wires"]
        )
        exits_cross = all(
            _wire_crosses(cut.frontier, wire) for wire in frame["exit_wires"]
        )
        if not identity_slice.result.events and entries_cross and exits_cross:
            placements.append(ScopeCutPlacement(completed, cut.frontier))
    return tuple(placements)


def test_zero_event_frame_has_two_scope_compatible_cut_placements(workspace):
    function = workspace.function("scope-cut-incidence", "call-first")
    frame = _identity_frame(function)

    assert frame["arguments"][0]["nodes"] == []
    assert frame["body_region"] == []
    assert frame["entry_wires"] == frame["exit_wires"]
    assert [
        placement.completed
        for placement in _compatible_identity_placements(function, frame)
    ] == [(), (0,)]


def test_independent_surgery_stays_inside_the_same_scope_cut_incidence_fiber(workspace):
    function = workspace.function("scope-cut-incidence", "call-first")
    frame = _identity_frame(function)
    step = function.advance_causal_cut([], 0)

    assert step.before["completed"] == []
    assert step.after["completed"] == [0]
    changed_wires = [item["wire"] for item in (*step.consumed, *step.produced)]
    assert all(wire not in changed_wires for wire in frame["entry_wires"])
    assert len(_compatible_identity_placements(function, frame)) == 2


def test_event_intersections_cannot_reconstruct_the_zero_event_frame_placement(workspace):
    function = workspace.function("scope-cut-incidence", "call-first")

    before = function.program_slice([], [])
    after = function.program_slice([0], [0])
    assert before.result.graft_intersections == ()
    assert after.result.graft_intersections == ()
    assert before.result.lower != after.result.lower


def test_frontier_order_changes_scope_path_but_not_causal_placement_ambiguity(workspace):
    first = workspace.function("scope-cut-incidence", "call-first")
    second = workspace.function("scope-cut-incidence", "call-second")
    first_frame = _identity_frame(first)
    second_frame = _identity_frame(second)

    assert first_frame["scope_path"] != second_frame["scope_path"]
    assert [
        placement.completed
        for placement in _compatible_identity_placements(first, first_frame)
    ] == [(), (0,)]
    assert [
        placement.completed
        for placement in _compatible_identity_placements(second, second_frame)
    ] == [(), (0,)]
