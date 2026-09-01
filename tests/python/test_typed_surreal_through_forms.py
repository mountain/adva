"""Pure-Python research oracle; it creates no Adva semantic authority."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from itertools import product

import pytest


class Domain(Enum):
    CONSTRUCTIVE = "K"
    SPATIAL = "X"
    TEMPORAL = "t"


DOMAINS = (Domain.CONSTRUCTIVE, Domain.SPATIAL, Domain.TEMPORAL)


class NotRepresentable(ValueError):
    pass


def opposite_type(source: Domain, target: Domain) -> Domain:
    if source is target:
        raise NotRepresentable("a circular interface needs two distinct charts")
    remaining = set(DOMAINS) - {source, target}
    if len(remaining) != 1:
        raise NotRepresentable("a triadic interface needs one opposite type")
    return remaining.pop()


@dataclass(frozen=True, slots=True)
class SmoothPoint:
    chart: Domain
    kind: str
    index: int


@dataclass(frozen=True, slots=True)
class PublicPoint:
    interface_type: Domain
    kind: str
    index: int


Relation = frozenset[tuple[SmoothPoint, SmoothPoint]]


def converse(relation: Relation) -> Relation:
    return frozenset((target, source) for source, target in relation)


def compose(after: Relation, before: Relation) -> Relation:
    return frozenset(
        (source, target)
        for source, middle in before
        for candidate, target in after
        if middle == candidate
    )


def is_total_function(
    relation: Relation,
    sources: tuple[SmoothPoint, ...],
) -> bool:
    return all(
        sum(left == source for left, _right in relation) == 1
        for source in sources
    )


@dataclass(frozen=True, slots=True)
class TypedThroughInterface:
    source: Domain
    target: Domain
    interface_type: Domain
    regular_count: int
    phase_count: int
    observer_version: str = "observer.v0"

    def __post_init__(self) -> None:
        if self.interface_type is not opposite_type(self.source, self.target):
            raise NotRepresentable("the interface carries the wrong opposite type")
        if self.regular_count < 0:
            raise NotRepresentable("regular_count must be non-negative")
        if self.phase_count < 2:
            raise NotRepresentable("a collapsed phase fibre needs at least two points")
        if not self.observer_version:
            raise NotRepresentable("the observer policy version must be explicit")

    def points(self, chart: Domain) -> tuple[SmoothPoint, ...]:
        if chart not in {self.source, self.target}:
            raise NotRepresentable("a point must belong to one interface chart")
        regular = tuple(
            SmoothPoint(chart, "regular", index) for index in range(self.regular_count)
        )
        phases = tuple(
            SmoothPoint(chart, "phase", index) for index in range(self.phase_count)
        )
        return regular + phases

    @property
    def source_points(self) -> tuple[SmoothPoint, ...]:
        return self.points(self.source)

    @property
    def target_points(self) -> tuple[SmoothPoint, ...]:
        return self.points(self.target)

    def pinch(self, point: SmoothPoint) -> PublicPoint:
        if point.chart not in {self.source, self.target}:
            raise NotRepresentable("the pinch point belongs to another chart")
        if point.kind == "regular" and 0 <= point.index < self.regular_count:
            return PublicPoint(self.interface_type, "regular", point.index)
        if point.kind == "phase" and 0 <= point.index < self.phase_count:
            return PublicPoint(self.interface_type, "node", 0)
        raise NotRepresentable("the point is outside the declared finite fibre")

    @property
    def through_relation(self) -> Relation:
        return frozenset(
            (left, right)
            for left in self.source_points
            for right in self.target_points
            if self.pinch(left) == self.pinch(right)
        )

    def resolution(self, phase: int) -> Relation:
        graph: set[tuple[SmoothPoint, SmoothPoint]] = set()
        for point in self.source_points:
            if point.kind == "regular":
                target = SmoothPoint(self.target, "regular", point.index)
            else:
                target = SmoothPoint(
                    self.target,
                    "phase",
                    (point.index + phase) % self.phase_count,
                )
            graph.add((point, target))
        return frozenset(graph)

    def reversed(self) -> TypedThroughInterface:
        return TypedThroughInterface(
            source=self.target,
            target=self.source,
            interface_type=self.interface_type,
            regular_count=self.regular_count,
            phase_count=self.phase_count,
            observer_version=self.observer_version,
        )


def circular_interfaces(
    *, regular_count: int = 2, phase_count: int = 5
) -> tuple[TypedThroughInterface, TypedThroughInterface, TypedThroughInterface]:
    edges = tuple(zip(DOMAINS, DOMAINS[1:] + DOMAINS[:1]))
    return tuple(
        TypedThroughInterface(
            source,
            target,
            opposite_type(source, target),
            regular_count,
            phase_count,
        )
        for source, target in edges
    )


def cyclic_composite(relations: tuple[Relation, Relation, Relation]) -> Relation:
    first, second, third = relations
    return compose(third, compose(second, first))


def conway_number_admissible(
    left_options: tuple[int, ...], right_options: tuple[int, ...]
) -> bool:
    return all(left < right for left in left_options for right in right_options)


def test_each_circular_interface_is_typed_by_the_opposite_domain() -> None:
    interfaces = circular_interfaces()
    assert tuple(
        (interface.source, interface.target, interface.interface_type)
        for interface in interfaces
    ) == (
        (Domain.CONSTRUCTIVE, Domain.SPATIAL, Domain.TEMPORAL),
        (Domain.SPATIAL, Domain.TEMPORAL, Domain.CONSTRUCTIVE),
        (Domain.TEMPORAL, Domain.CONSTRUCTIVE, Domain.SPATIAL),
    )

    with pytest.raises(NotRepresentable, match="wrong opposite"):
        TypedThroughInterface(
            Domain.CONSTRUCTIVE,
            Domain.SPATIAL,
            Domain.CONSTRUCTIVE,
            2,
            5,
        )


def test_angle_through_form_is_exactly_a_typed_fibre_product_relation() -> None:
    for interface in circular_interfaces():
        relation = interface.through_relation
        assert len(relation) == interface.regular_count + interface.phase_count**2
        assert relation == frozenset(
            (left, right)
            for left in interface.source_points
            for right in interface.target_points
            if interface.pinch(left) == interface.pinch(right)
        )

        for source in interface.source_points:
            degree = sum(left == source for left, _right in relation)
            assert degree == (1 if source.kind == "regular" else interface.phase_count)


def test_conway_order_and_through_compatibility_are_independent_judgements() -> None:
    interface = circular_interfaces()[0]
    phase_pair = (
        SmoothPoint(interface.source, "phase", 0),
        SmoothPoint(interface.target, "phase", 1),
    )
    regular_mismatch = (
        SmoothPoint(interface.source, "regular", 0),
        SmoothPoint(interface.target, "regular", 1),
    )

    assert phase_pair in interface.through_relation
    assert regular_mismatch not in interface.through_relation
    assert {
        (conway_number_admissible(options[0], options[1]), compatible)
        for options, compatible in (
            (((0,), (2,)), phase_pair in interface.through_relation),
            (((0,), (2,)), regular_mismatch in interface.through_relation),
            (((2,), (0,)), phase_pair in interface.through_relation),
            (((2,), (0,)), regular_mismatch in interface.through_relation),
        )
    } == {(True, True), (True, False), (False, True), (False, False)}


def test_resolutions_are_distinct_graphs_with_one_public_specialization() -> None:
    for interface in circular_interfaces():
        resolutions = tuple(
            interface.resolution(phase) for phase in range(interface.phase_count)
        )
        assert len(set(resolutions)) == interface.phase_count
        for resolution in resolutions:
            assert resolution <= interface.through_relation
            assert is_total_function(resolution, interface.source_points)
            assert {
                (interface.pinch(left), interface.pinch(right))
                for left, right in resolution
            } == {
                (PublicPoint(interface.interface_type, "regular", index),) * 2
                for index in range(interface.regular_count)
            } | {
                (
                    PublicPoint(interface.interface_type, "node", 0),
                    PublicPoint(interface.interface_type, "node", 0),
                )
            }


def test_duality_is_relational_converse_and_is_involutive() -> None:
    for interface in circular_interfaces():
        reversed_interface = interface.reversed()
        assert reversed_interface.through_relation == converse(
            interface.through_relation
        )
        assert reversed_interface.reversed() == interface
        for phase in range(interface.phase_count):
            assert reversed_interface.resolution(-phase) == converse(
                interface.resolution(phase)
            )


def test_unresolved_circular_through_is_not_a_single_normalization_map() -> None:
    interfaces = circular_interfaces()
    raw_cycle = cyclic_composite(
        tuple(interface.through_relation for interface in interfaces)
    )
    base_points = interfaces[0].source_points

    assert len(raw_cycle) == interfaces[0].regular_count + interfaces[0].phase_count**2
    assert not is_total_function(raw_cycle, base_points)
    for source in base_points:
        degree = sum(left == source for left, _right in raw_cycle)
        assert degree == (1 if source.kind == "regular" else interfaces[0].phase_count)


def test_unresolved_cycle_is_the_union_of_all_resolution_holonomies() -> None:
    interfaces = circular_interfaces()
    phase_count = interfaces[0].phase_count
    raw_cycle = cyclic_composite(
        tuple(interface.through_relation for interface in interfaces)
    )
    resolved_cycles: set[Relation] = set()
    shift_counts: Counter[int] = Counter()

    for phases in product(range(phase_count), repeat=3):
        resolved = cyclic_composite(
            tuple(
                interface.resolution(phase)
                for interface, phase in zip(interfaces, phases, strict=True)
            )
        )
        resolved_cycles.add(resolved)
        shift_counts[sum(phases) % phase_count] += 1

    assert len(resolved_cycles) == phase_count
    assert shift_counts == Counter(
        {shift: phase_count**2 for shift in range(phase_count)}
    )
    assert frozenset().union(*resolved_cycles) == raw_cycle


def test_reversing_the_circle_converses_both_raw_and_resolved_holonomy() -> None:
    interfaces = circular_interfaces()
    forward_raw = cyclic_composite(
        tuple(interface.through_relation for interface in interfaces)
    )
    reverse_raw = cyclic_composite(
        tuple(
            interface.reversed().through_relation for interface in reversed(interfaces)
        )
    )
    assert reverse_raw == converse(forward_raw)

    phases = (1, 2, 3)
    forward = cyclic_composite(
        tuple(
            interface.resolution(phase)
            for interface, phase in zip(interfaces, phases, strict=True)
        )
    )
    reverse = cyclic_composite(
        tuple(
            interface.reversed().resolution(-phase)
            for interface, phase in zip(
                reversed(interfaces), reversed(phases), strict=True
            )
        )
    )
    assert reverse == converse(forward)
