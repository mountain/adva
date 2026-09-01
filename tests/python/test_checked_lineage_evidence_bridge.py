from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import pytest

from adva import link_modules


EVIDENCE_BRIDGE = """
(module evidence-bridge
  (export independent-sum shared-sum exchange-sum drop-left)

  (def independent-sum
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (use left)
          (use right)))))

  (def shared-sum
    (fn ((x Real)) Real
      (add (copy (use x)))))

  (def exchange-sum
    (fn ((left Real) (right Real)) Real
      (add
        (swap
          (frontier
            (use left)
            (use right))))))

  (def drop-left
    (fn ((left Real) (right Real)) Real
      (frontier
        (discard (use left))
        (use right))))
)
"""


@dataclass(frozen=True, slots=True)
class CheckedResource:
    """Read-only source and occurrence data copied from one Rust cut wire."""

    sources: tuple[str, ...]
    lineage: tuple[str, ...]

    @property
    def key(self) -> tuple[tuple[str, ...], tuple[str, ...]]:
        return (self.sources, self.lineage)


@pytest.fixture(scope="module")
def workspace():
    return link_modules([EVIDENCE_BRIDGE])


def _resources(frontier: Sequence[Mapping[str, Any]]) -> tuple[CheckedResource, ...]:
    resources = tuple(
        CheckedResource(
            sources=tuple(item["sources"]),
            lineage=tuple(item["wire"]["lineage"]),
        )
        for item in frontier
    )
    occurrence_ids = [
        occurrence
        for resource in resources
        for occurrence in resource.lineage
    ]
    if len(occurrence_ids) != len(set(occurrence_ids)):
        raise ValueError("Rust cut exposed one occurrence through multiple resources")
    return resources


def _one_operation(slice_result: Any, name: str) -> Mapping[str, Any]:
    operations = [
        event
        for event in slice_result.event_history
        if event["kind"] == "operation"
        and event["operation"]["name"] == name
    ]
    assert len(operations) == 1
    return operations[0]


def _partition_occurrences(
    partition: Mapping[str, tuple[str, ...]],
) -> set[str]:
    return {
        occurrence
        for occurrences in partition.values()
        for occurrence in occurrences
    }


def test_independent_pairing_uses_two_checked_sources_and_occurrences(
    workspace,
) -> None:
    function = workspace.function("evidence-bridge", "independent-sum")
    initial = function.causal_cut([])
    resources = _resources(initial.frontier)

    assert initial.certificate["completed_past"] == "checked"
    assert initial.certificate["lineage_preservation"] == "checked"
    assert len(resources) == 2
    assert all(len(resource.sources) == 1 for resource in resources)
    assert all(len(resource.lineage) == 1 for resource in resources)
    assert resources[0].sources != resources[1].sources
    assert resources[0].lineage != resources[1].lineage

    partition = function.source_partition
    assert len(partition) == 2
    assert {resource.sources[0] for resource in resources} == set(partition)
    assert {
        resource.lineage[0] for resource in resources
    } == _partition_occurrences(partition)


def test_exchange_is_a_checked_bijection_of_existing_resources(workspace) -> None:
    function = workspace.function("evidence-bridge", "exchange-sum")
    step = function.advance_causal_cut([], 0)
    before = _resources(step.consumed)
    after = _resources(step.produced)

    assert step.certificate["frontier_replacement"] == "checked"
    assert len(before) == len(after) == 2
    assert after == (before[1], before[0])

    exchange_slice = function.program_slice([], [0])
    assert [event["operation"]["name"] for event in exchange_slice.result.events] == [
        "swap"
    ]
    _one_operation(exchange_slice.result, "swap")
    assert all(
        event["kind"] != "copy"
        for event in exchange_slice.result.event_history
    )


def test_explicit_copy_branches_one_source_into_two_new_occurrences(workspace) -> None:
    function = workspace.function("evidence-bridge", "shared-sum")
    step = function.advance_causal_cut([], 0)
    before = _resources(step.consumed)
    after = _resources(step.produced)
    copy_slice = function.program_slice([], [0])

    assert len(before) == 1
    assert len(after) == 2
    assert after[0].sources == after[1].sources == before[0].sources
    assert after[0].lineage != after[1].lineage

    copy_events = [
        event
        for event in copy_slice.result.event_history
        if event["kind"] == "copy"
    ]
    assert len(copy_events) == 1
    copy_event = copy_events[0]
    parent = before[0].lineage[0]
    children = tuple(resource.lineage[0] for resource in after)
    assert copy_event["parent"] == parent
    assert tuple(copy_event["children"]) == children
    assert parent not in children
    assert len(set(children)) == 2
    _one_operation(copy_slice.result, "copy")

    partition = function.source_partition
    assert len(partition) == 1
    assert set(next(iter(partition.values()))) == {parent, *children}


def test_explicit_discard_removes_one_resource_but_retains_the_event(workspace) -> None:
    function = workspace.function("evidence-bridge", "drop-left")
    initial = function.causal_cut([])
    step = function.advance_causal_cut([], 0)
    discard_slice = function.program_slice([], [0])

    initial_resources = _resources(initial.frontier)
    consumed = _resources(step.consumed)
    produced = _resources(step.produced)
    remaining = _resources(step.after["frontier"])

    assert len(initial_resources) == 2
    assert len(consumed) == 1
    assert produced == ()
    assert len(remaining) == 1
    assert {resource.key for resource in remaining} == {
        resource.key for resource in initial_resources
    } - {consumed[0].key}

    assert [event["operation"]["name"] for event in discard_slice.result.events] == [
        "discard"
    ]
    assert discard_slice.result.lower_boundary
    assert discard_slice.result.upper_boundary == ()
    assert discard_slice.result.internal_events == (0,)
    assert len(discard_slice.result.through_wires) == 1
    _one_operation(discard_slice.result, "discard")


def test_host_aliasing_still_cannot_enter_the_checked_boundary(workspace) -> None:
    function = workspace.function("evidence-bridge", "independent-sum")
    initial = function.causal_cut([])
    forged = [initial.frontier[0], initial.frontier[0]]

    with pytest.raises(ValueError, match="one occurrence"):
        _resources(forged)

    assert function.validation_certificate["linear_use"] == "checked"
