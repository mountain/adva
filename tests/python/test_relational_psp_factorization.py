from __future__ import annotations

from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from typing import Any, TypeAlias

from adva import KernelFunction, link_modules


RELATIONAL_PSP = r"""
(module relational-psp
  (export root)

  (def ordered-pair
    (fn ((left Real) (right Real)) (outputs Real Real)
      (frontier
        (use left)
        (use right))))

  (def root
    (fn ((x Real) (y Real) (z Real)) (outputs Real Real Real)
      (frontier
        (call ordered-pair
          (use x)
          (use y))
        (neg (use z)))))
)
"""


Relation: TypeAlias = frozenset[tuple[Hashable, Hashable]]


@dataclass(frozen=True, slots=True)
class OrderedScope:
    """Test-local intensional scope state retaining ordered hole names."""

    frame: str
    holes: tuple[tuple[int, str], ...]


def _then(left: Relation, right: Relation) -> Relation:
    """Relational composition in diagrammatic left-to-right order."""

    return frozenset(
        (source, target)
        for source, middle in left
        for candidate, target in right
        if middle == candidate
    )


def _call_frame(function: KernelFunction) -> Mapping[str, Any]:
    trace = function.graft_trace
    assert trace is not None
    frames = [frame for frame in trace.result.frames if frame["kind"] == "call"]
    assert len(frames) == 1
    return frames[0]


def _wire_crosses(function: KernelFunction, completed, wire) -> bool:
    return any(
        crossing["wire"] == wire
        for crossing in function.causal_cut(completed).frontier
    )


def test_ordered_two_hole_identity_scope_factors_through_relational_cut_surgery():
    function = link_modules([RELATIONAL_PSP]).function("relational-psp", "root")
    frame = _call_frame(function)
    scope = OrderedScope(
        frame=frame["id"],
        holes=tuple(
            (hole["hole_index"], hole["hole"]["name"]) for hole in frame["holes"]
        ),
    )

    assert scope.holes == ((0, "left"), (1, "right"))
    assert [argument["nodes"] for argument in frame["arguments"]] == [[], []]
    assert frame["body_region"] == []
    assert frame["entry_wires"] == frame["exit_wires"]

    cuts = ((), (0,))
    p_star: Relation = frozenset(
        (scope, cut)
        for cut in cuts
        if all(_wire_crosses(function, cut, wire) for wire in frame["entry_wires"])
    )
    p: Relation = frozenset((cut, state) for state, cut in p_star)
    assert p_star == frozenset({(scope, ()), (scope, (0,))})

    step = function.advance_causal_cut([], 0)
    contract: Relation = frozenset(
        {(tuple(step.before["completed"]), tuple(step.after["completed"]))}
    )
    expand: Relation = frozenset((target, source) for source, target in contract)
    identity_scope: Relation = frozenset({(scope, scope)})

    assert _then(_then(p_star, contract), p) == identity_scope
    assert _then(_then(p_star, expand), p) == identity_scope


def test_single_cut_selector_with_its_converse_is_not_closed_under_surgery():
    function = link_modules([RELATIONAL_PSP]).function("relational-psp", "root")
    frame = _call_frame(function)
    scope = OrderedScope(
        frame=frame["id"],
        holes=tuple(
            (hole["hole_index"], hole["hole"]["name"]) for hole in frame["holes"]
        ),
    )
    step = function.advance_causal_cut([], 0)
    contract: Relation = frozenset(
        {(tuple(step.before["completed"]), tuple(step.after["completed"]))}
    )
    expand: Relation = frozenset((target, source) for source, target in contract)

    earliest_p_star: Relation = frozenset({(scope, ())})
    earliest_p: Relation = frozenset({((), scope)})
    latest_p_star: Relation = frozenset({(scope, (0,))})
    latest_p: Relation = frozenset({((0,), scope)})

    for p_star, p in (
        (earliest_p_star, earliest_p),
        (latest_p_star, latest_p),
    ):
        assert _then(_then(p_star, contract), p) == frozenset()
        assert _then(_then(p_star, expand), p) == frozenset()
