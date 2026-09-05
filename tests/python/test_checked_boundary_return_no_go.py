"""Checked finite boundary returns and the feedback-period no-go.

The Rust kernel owns every causal cut and ProgramSlice used here.  This
research companion only compares checked boundaries and groups source-free
internal events; it creates no iteration, period, bracket, or topological
semantic authority.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from math import gcd, lcm
from typing import Any

from adva import compile_module


WITNESS = """
(module checked-boundary-return
  (export witness)
  (def witness
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard 1)
        (discard (neg 1))
        (use temporal)
        (use spatial)
        (use construction)))))
"""


@dataclass(frozen=True, slots=True)
class BoundaryReturnWordV0:
    """One finite return of a boundary projection, with its exact residual."""

    component: tuple[int, ...]
    operation_word: tuple[str, ...]
    least_event_length: int
    lower_completed: tuple[int, ...]
    upper_completed: tuple[int, ...]
    residual_event_ids: tuple[int, ...]
    exact_cut_return: bool


@dataclass(frozen=True, slots=True)
class DoubleReturnCompanionV0:
    """A typed candidate phase reading, explicitly blocked on feedback."""

    first: BoundaryReturnWordV0
    second: BoundaryReturnWordV0
    feedback_witness: None = None
    homology_return_map: None = None
    orbifold_orders: None = None

    @property
    def visible_lengths(self) -> tuple[int, int]:
        return self.first.least_event_length, self.second.least_event_length

    @property
    def candidate_joint_return(self) -> int:
        return lcm(*self.visible_lengths)

    @property
    def candidate_phase_components(self) -> int:
        return gcd(*self.visible_lengths)

    @property
    def status(self) -> str:
        return "not_representable_without_feedback"


def checked_witness() -> Any:
    workspace = compile_module(WITNESS)
    return workspace.function("checked-boundary-return", "witness")


def node_name(node: dict[str, Any]) -> str:
    return str(node["operation"]["name"])


def source_free_internal_components(function: Any) -> tuple[tuple[int, ...], ...]:
    """Derive connected source-free components from one Rust-owned full slice."""

    nodes = {int(node["id"]): node for node in function.ir["nodes"]}
    all_ids = tuple(sorted(nodes))
    whole = function.program_slice([], all_ids)
    internal = set(whole.result.internal_events)
    source_free = {
        node_id
        for node_id in internal
        if all(not wire["lineage"] for wire in nodes[node_id]["inputs"])
    }

    adjacency = {node_id: set() for node_id in source_free}
    for node_id in source_free:
        for wire in nodes[node_id]["inputs"]:
            producer = wire["producer"]
            if producer["kind"] != "node":
                continue
            parent = int(producer["node"])
            if parent in source_free:
                adjacency[node_id].add(parent)
                adjacency[parent].add(node_id)

    unseen = set(source_free)
    components: list[tuple[int, ...]] = []
    while unseen:
        seed = min(unseen)
        stack = [seed]
        component: set[int] = set()
        while stack:
            current = stack.pop()
            if current in component:
                continue
            component.add(current)
            unseen.discard(current)
            stack.extend(adjacency[current] - component)
        components.append(tuple(sorted(component)))
    return tuple(sorted(components, key=lambda component: (len(component), component)))


def boundary_return_word(function: Any, component: tuple[int, ...]) -> BoundaryReturnWordV0:
    """Find the least local prefix returning to the initial checked frontier."""

    initial = function.causal_cut([])
    least_length: int | None = None
    for length in range(1, len(component) + 1):
        prefix = component[:length]
        candidate = function.causal_cut(prefix)
        if candidate.frontier == initial.frontier:
            least_length = length
            break
    if least_length is None:
        raise AssertionError("component does not return under boundary-only observation")
    if least_length != len(component):
        raise AssertionError("the supplied component is not a least return word")

    interval = function.program_slice([], component)
    nodes = {int(node["id"]): node for node in function.ir["nodes"]}
    return BoundaryReturnWordV0(
        component=component,
        operation_word=tuple(node_name(nodes[node_id]) for node_id in component),
        least_event_length=least_length,
        lower_completed=tuple(interval.result.lower["completed"]),
        upper_completed=tuple(interval.result.upper["completed"]),
        residual_event_ids=tuple(int(node["id"]) for node in interval.result.events),
        exact_cut_return=interval.result.lower == interval.result.upper,
    )


def test_one_checked_history_contains_two_least_boundary_return_words() -> None:
    function = checked_witness()
    components = source_free_internal_components(function)
    words = tuple(boundary_return_word(function, component) for component in components)

    assert tuple(word.operation_word for word in words) == (
        ("constant", "discard"),
        ("constant", "neg", "discard"),
    )
    assert tuple(word.least_event_length for word in words) == (2, 3)
    assert all(word.residual_event_ids == word.component for word in words)
    assert all(word.lower_completed == () for word in words)
    assert all(word.upper_completed == word.component for word in words)

    # Boundary equality is real, but exact cut equality is not.
    assert all(not word.exact_cut_return for word in words)


def test_finite_acyclic_checked_cuts_have_no_positive_exact_period() -> None:
    function = checked_witness()
    node_ids = tuple(sorted(int(node["id"]) for node in function.ir["nodes"]))
    legal_cuts = []
    for size in range(len(node_ids) + 1):
        for completed in combinations(node_ids, size):
            try:
                legal_cuts.append(function.causal_cut(completed))
            except ValueError:
                pass

    exact_cut_ids = {tuple(cut.completed) for cut in legal_cuts}
    assert len(exact_cut_ids) == len(legal_cuts)

    for lower in legal_cuts:
        for upper in legal_cuts:
            lower_set = set(lower.completed)
            upper_set = set(upper.completed)
            if lower_set < upper_set:
                assert len(lower.completed) < len(upper.completed)
                interval = function.program_slice(lower.completed, upper.completed)
                assert interval.result.events
                assert interval.result.lower != interval.result.upper

    for cut in legal_cuts:
        identity = function.program_slice(cut.completed, cut.completed)
        assert identity.result.events == ()
        assert identity.result.lower == identity.result.upper


def test_candidate_2_3_phase_data_is_blocked_without_a_feedback_witness() -> None:
    function = checked_witness()
    first, second = (
        boundary_return_word(function, component)
        for component in source_free_internal_components(function)
    )
    companion = DoubleReturnCompanionV0(first, second)

    assert companion.visible_lengths == (2, 3)
    assert companion.candidate_joint_return == 6
    assert companion.candidate_phase_components == 1
    assert companion.feedback_witness is None
    assert companion.homology_return_map is None
    assert companion.orbifold_orders is None
    assert companion.status == "not_representable_without_feedback"


def test_boundary_forgetting_is_not_invariant_under_history_refinement() -> None:
    """A harmless closed detour changes length while preserving the boundary."""

    function = checked_witness()
    words = tuple(
        boundary_return_word(function, component)
        for component in source_free_internal_components(function)
    )

    assert words[0].operation_word == ("constant", "discard")
    assert words[1].operation_word == ("constant", "neg", "discard")
    assert words[0].least_event_length != words[1].least_event_length

    for word in words:
        interval = function.program_slice([], word.component)
        assert interval.result.lower["frontier"] == interval.result.upper["frontier"]
        assert interval.result.lower_boundary == ()
        assert interval.result.upper_boundary == ()
        assert interval.result.through_wires == tuple(interval.result.lower["frontier"])
        assert interval.result.internal_events == word.component
