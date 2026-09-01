"""Pure-Python research oracle; it creates no Adva semantic authority."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from itertools import combinations

import pytest


class Domain(Enum):
    CONSTRUCTIVE = "K"
    SPATIAL = "X"
    TEMPORAL = "t"


class Endpoint(Enum):
    OPEN = "open"
    CLOSE = "close"


class Polarity(Enum):
    VACUUM = "vacuum"
    UNIVERSAL = "observer-relative-universal"


DOMAINS = (Domain.CONSTRUCTIVE, Domain.SPATIAL, Domain.TEMPORAL)
GLYPHS = {
    Domain.CONSTRUCTIVE: "{}",
    Domain.SPATIAL: "[]",
    Domain.TEMPORAL: "()",
}


@dataclass(frozen=True, slots=True)
class Mark:
    domain: Domain
    endpoint: Endpoint


CIRCLE = tuple(
    Mark(domain, endpoint)
    for domain in DOMAINS
    for endpoint in (Endpoint.OPEN, Endpoint.CLOSE)
)


def _open_arc(circle: tuple[Mark, ...], start: int, stop: int) -> tuple[Mark, ...]:
    if start == stop:
        raise ValueError("an arc requires two distinct endpoints")
    result: list[Mark] = []
    index = (start + 1) % len(circle)
    while index != stop:
        result.append(circle[index])
        index = (index + 1) % len(circle)
    return tuple(result)


def _endpoint_positions(domain: Domain) -> tuple[int, int]:
    opening = CIRCLE.index(Mark(domain, Endpoint.OPEN))
    closing = CIRCLE.index(Mark(domain, Endpoint.CLOSE))
    return opening, closing


@dataclass(frozen=True, slots=True)
class BoundaryReading:
    domain: Domain
    polarity: Polarity
    selected_arc: tuple[Mark, ...]
    complementary_arc: tuple[Mark, ...]
    coorientation: int

    def __post_init__(self) -> None:
        if self.coorientation not in {-1, 1}:
            raise ValueError("coorientation must be signed")
        all_marks = self.selected_arc + self.complementary_arc
        expected = tuple(mark for mark in CIRCLE if mark.domain is not self.domain)
        if set(all_marks) != set(expected) or len(all_marks) != len(expected):
            raise ValueError("the two arcs must partition all opposite marks")

    @property
    def selected_domains(self) -> frozenset[Domain]:
        return frozenset(mark.domain for mark in self.selected_arc)


def vacuum_reading(domain: Domain) -> BoundaryReading:
    opening, closing = _endpoint_positions(domain)
    return BoundaryReading(
        domain=domain,
        polarity=Polarity.VACUUM,
        selected_arc=_open_arc(CIRCLE, opening, closing),
        complementary_arc=_open_arc(CIRCLE, closing, opening),
        coorientation=1,
    )


def star_reading(reading: BoundaryReading) -> BoundaryReading:
    polarity = (
        Polarity.UNIVERSAL if reading.polarity is Polarity.VACUUM else Polarity.VACUUM
    )
    return BoundaryReading(
        domain=reading.domain,
        polarity=polarity,
        selected_arc=reading.complementary_arc,
        complementary_arc=reading.selected_arc,
        coorientation=-reading.coorientation,
    )


def opposite_context(domain: Domain) -> frozenset[Domain]:
    return frozenset(set(DOMAINS) - {domain})


def nerve_faces() -> dict[int, frozenset[frozenset[Domain]]]:
    cover = {domain: opposite_context(domain) for domain in DOMAINS}
    faces: dict[int, frozenset[frozenset[Domain]]] = {}
    for size in range(1, len(DOMAINS) + 1):
        accepted: set[frozenset[Domain]] = set()
        for labels in combinations(DOMAINS, size):
            intersection = set(DOMAINS)
            for label in labels:
                intersection &= cover[label]
            if intersection:
                accepted.add(frozenset(labels))
        faces[size - 1] = frozenset(accepted)
    return faces


class NotRepresentable(ValueError):
    pass


def linearize(cut: int) -> str:
    if not 0 <= cut < len(CIRCLE):
        raise ValueError("cut must select one of the six cyclic gaps")
    marks = CIRCLE[cut:] + CIRCLE[:cut]
    blocks: list[str] = []
    for index in range(0, len(marks), 2):
        opening, closing = marks[index : index + 2]
        if (
            opening.domain is not closing.domain
            or opening.endpoint is not Endpoint.OPEN
            or closing.endpoint is not Endpoint.CLOSE
        ):
            raise NotRepresentable("the cut splits a typed bracket pair")
        blocks.append(GLYPHS[opening.domain])
    return "".join(blocks)


@dataclass(frozen=True, slots=True)
class TypedNode:
    domain: Domain


State = BoundaryReading | TypedNode


@dataclass(frozen=True, slots=True)
class Arrow:
    source: State
    target: State


def star_state(state: State) -> State:
    if isinstance(state, BoundaryReading):
        return star_reading(state)
    return state


def star_arrow(arrow: Arrow) -> Arrow:
    return Arrow(star_state(arrow.target), star_state(arrow.source))


@dataclass(frozen=True, slots=True)
class Specialization:
    public_node: TypedNode
    visible_marks: tuple[Mark, ...]
    residual: BoundaryReading


def specialize(reading: BoundaryReading) -> Specialization:
    return Specialization(
        public_node=TypedNode(reading.domain),
        visible_marks=tuple(
            mark for mark in CIRCLE if mark.domain is not reading.domain
        ),
        residual=reading,
    )


Point = tuple[str, int]


@dataclass(frozen=True, slots=True)
class FiniteTypedPinch:
    domain: Domain
    regular_count: int
    phase_count: int

    def __post_init__(self) -> None:
        if self.regular_count < 0:
            raise ValueError("regular_count must be non-negative")
        if self.phase_count < 2:
            raise ValueError("the collapsed phase fibre needs at least two points")

    @property
    def smooth_points(self) -> tuple[Point, ...]:
        regular = tuple(("regular", index) for index in range(self.regular_count))
        phases = tuple(("phase", index) for index in range(self.phase_count))
        return regular + phases

    def pinch(self, point: Point) -> Point:
        kind, _index = point
        if kind == "regular":
            return point
        if kind == "phase":
            return (f"node:{self.domain.value}", 0)
        raise ValueError(f"unknown point kind: {kind}")

    @property
    def through_relation(self) -> frozenset[tuple[Point, Point]]:
        return frozenset(
            (left, right)
            for left in self.smooth_points
            for right in self.smooth_points
            if self.pinch(left) == self.pinch(right)
        )

    def resolution(self, phase: int) -> dict[Point, Point]:
        result: dict[Point, Point] = {}
        for point in self.smooth_points:
            kind, index = point
            if kind == "regular":
                result[point] = point
            else:
                result[point] = ("phase", (index + phase) % self.phase_count)
        return result


def _inverse(mapping: dict[Point, Point]) -> dict[Point, Point]:
    inverse: dict[Point, Point] = {}
    for source, target in mapping.items():
        if target in inverse:
            raise ValueError("mapping is not invertible")
        inverse[target] = source
    return inverse


def _compose(
    after: dict[Point, Point],
    before: dict[Point, Point],
) -> dict[Point, Point]:
    return {source: after[target] for source, target in before.items()}


def test_short_and_complementary_arcs_recover_opposite_pair_readings() -> None:
    for domain in DOMAINS:
        vacuum = vacuum_reading(domain)
        universal = star_reading(vacuum)

        assert vacuum.selected_arc == ()
        assert universal.selected_domains == opposite_context(domain)
        assert len(universal.selected_arc) == 4
        for opposite in opposite_context(domain):
            assert sum(mark.domain is opposite for mark in universal.selected_arc) == 2


def test_outside_cover_has_the_nerve_of_a_triangle_boundary() -> None:
    faces = nerve_faces()
    assert tuple(len(faces[dimension]) for dimension in range(3)) == (3, 3, 0)
    assert len(faces[0]) - len(faces[1]) == 0

    cover = {domain: opposite_context(domain) for domain in DOMAINS}
    for left, right in combinations(DOMAINS, 2):
        assert len(cover[left] & cover[right]) == 1
    assert set.intersection(*(set(context) for context in cover.values())) == set()
    assert all(context != frozenset(DOMAINS) for context in cover.values())


def test_side_reversal_is_typed_and_involutive() -> None:
    for domain in DOMAINS:
        reading = vacuum_reading(domain)
        reversed_reading = star_reading(reading)

        assert reversed_reading.domain is domain
        assert reversed_reading.polarity is Polarity.UNIVERSAL
        assert reversed_reading.coorientation == -reading.coorientation
        assert reversed_reading.selected_arc == reading.complementary_arc
        assert star_reading(reversed_reading) == reading


def test_star_reverses_arrows_instead_of_preserving_their_direction() -> None:
    reading = vacuum_reading(Domain.SPATIAL)
    node = TypedNode(Domain.SPATIAL)
    specialization = Arrow(reading, node)
    dual = star_arrow(specialization)

    assert dual == Arrow(node, star_reading(reading))
    assert dual != Arrow(star_reading(reading), node)
    assert star_arrow(dual) == specialization


def test_admissible_cuts_are_exactly_the_three_cyclic_linearizations() -> None:
    assert {linearize(cut) for cut in (0, 2, 4)} == {
        "{}[]()",
        "[](){}",
        "(){}[]",
    }
    for cut in (1, 3, 5):
        with pytest.raises(NotRepresentable, match="splits"):
            linearize(cut)


def test_specialization_identifies_public_polarity_but_retains_residual() -> None:
    for domain in DOMAINS:
        vacuum = vacuum_reading(domain)
        universal = star_reading(vacuum)
        collapsed_vacuum = specialize(vacuum)
        collapsed_universal = specialize(universal)

        assert collapsed_vacuum.public_node == collapsed_universal.public_node
        assert collapsed_vacuum.visible_marks == collapsed_universal.visible_marks
        assert collapsed_vacuum.residual != collapsed_universal.residual
        assert {mark.domain for mark in collapsed_vacuum.visible_marks} == set(
            opposite_context(domain)
        )


def test_through_is_functional_off_the_node_and_relational_over_it() -> None:
    for domain in DOMAINS:
        pinch = FiniteTypedPinch(domain, regular_count=3, phase_count=8)
        relation = pinch.through_relation
        assert len(relation) == 3 + 8 * 8

        outgoing_degree = {
            source: sum(1 for left, _ in relation if left == source)
            for source in pinch.smooth_points
        }
        assert {
            degree for point, degree in outgoing_degree.items() if point[0] == "regular"
        } == {1}
        assert {
            degree for point, degree in outgoing_degree.items() if point[0] == "phase"
        } == {8}


def test_difference_of_through_resolutions_is_around_rotation() -> None:
    for domain in DOMAINS:
        pinch = FiniteTypedPinch(domain, regular_count=2, phase_count=8)
        lower = pinch.resolution(2)
        upper = pinch.resolution(5)

        assert all(
            (source, target) in pinch.through_relation
            for source, target in lower.items()
        )
        assert all(
            (source, target) in pinch.through_relation
            for source, target in upper.items()
        )

        difference = _compose(_inverse(lower), upper)
        assert difference == pinch.resolution(3)
        assert difference != pinch.resolution(0)
