from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import sympy


Port = str
Edge = tuple[str, str]
Point = tuple[str, int]


def _edge(left: str, right: str) -> Edge:
    return tuple(sorted((left, right)))


@dataclass(frozen=True, slots=True)
class BoundaryMatching:
    """One pairing of the four external ports of a real saddle patch."""

    pairs: tuple[Edge, ...]

    def __post_init__(self) -> None:
        canonical = tuple(sorted(_edge(*pair) for pair in self.pairs))
        if canonical != self.pairs:
            raise ValueError("boundary pairs must be canonical and sorted")
        ports = tuple(port for pair in self.pairs for port in pair)
        if len(ports) != len(set(ports)):
            raise ValueError("every boundary port must occur exactly once")

    @property
    def ports(self) -> frozenset[Port]:
        return frozenset(port for pair in self.pairs for port in pair)


NEGATIVE_FIBRE = BoundaryMatching(
    tuple(
        sorted(
            (
                _edge("N", "W"),
                _edge("S", "E"),
            )
        )
    )
)

POSITIVE_FIBRE = BoundaryMatching(
    tuple(
        sorted(
            (
                _edge("N", "E"),
                _edge("S", "W"),
            )
        )
    )
)


@dataclass(frozen=True, slots=True)
class SaddleCellulation:
    """A finite disk cellulation carrying one index-one real Morse crossing."""

    vertices: tuple[str, ...]
    edges: tuple[Edge, ...]
    faces: tuple[tuple[str, ...], ...]
    incoming: BoundaryMatching
    outgoing: BoundaryMatching
    centre: str = "O"

    @property
    def euler_characteristic(self) -> int:
        return len(self.vertices) - len(self.edges) + len(self.faces)

    @property
    def incoming_euler_characteristic(self) -> int:
        return len(self.incoming.ports) - len(self.incoming.pairs)

    @property
    def relative_euler_characteristic(self) -> int:
        return self.euler_characteristic - self.incoming_euler_characteristic

    @property
    def edge_face_incidence(self) -> Counter[Edge]:
        counts: Counter[Edge] = Counter()
        for face in self.faces:
            cyclic = face[1:] + face[:1]
            for left, right in zip(face, cyclic):
                counts[_edge(left, right)] += 1
        return counts

    def specialization_paths(
        self,
        matching: BoundaryMatching,
    ) -> tuple[tuple[str, str, str], ...]:
        return tuple((left, self.centre, right) for left, right in matching.pairs)

    def specialization_image(self, matching: BoundaryMatching) -> frozenset[Edge]:
        return frozenset(
            edge
            for left, centre, right in self.specialization_paths(matching)
            for edge in (_edge(left, centre), _edge(centre, right))
        )


SADDLE = SaddleCellulation(
    vertices=("N", "E", "S", "W", "O"),
    edges=tuple(
        sorted(
            (
                _edge("N", "E"),
                _edge("E", "S"),
                _edge("S", "W"),
                _edge("W", "N"),
                _edge("O", "N"),
                _edge("O", "E"),
                _edge("O", "S"),
                _edge("O", "W"),
            )
        )
    ),
    faces=(
        ("O", "N", "E"),
        ("O", "E", "S"),
        ("O", "S", "W"),
        ("O", "W", "N"),
    ),
    incoming=NEGATIVE_FIBRE,
    outgoing=POSITIVE_FIBRE,
)


def _component_count(
    local: BoundaryMatching,
    exterior: BoundaryMatching,
) -> int:
    if local.ports != exterior.ports:
        raise ValueError("local and exterior matchings need the same ports")

    adjacency = {port: set() for port in local.ports}
    for matching in (local, exterior):
        for left, right in matching.pairs:
            adjacency[left].add(right)
            adjacency[right].add(left)

    seen: set[str] = set()
    components = 0
    for start in adjacency:
        if start in seen:
            continue
        components += 1
        pending = [start]
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            pending.extend(adjacency[current] - seen)
    return components


@dataclass(frozen=True, slots=True)
class FinitePinchCospan:
    """A bounded quotient model of an annular nodal pinch."""

    regular_count: int
    cycle_size: int

    def __post_init__(self) -> None:
        if self.regular_count < 0:
            raise ValueError("regular_count must be non-negative")
        if self.cycle_size < 2:
            raise ValueError("the finite vanishing cycle needs at least two points")

    @property
    def minus_points(self) -> tuple[Point, ...]:
        regular = tuple(("regular", index) for index in range(self.regular_count))
        cycle = tuple(("vanishing", index) for index in range(self.cycle_size))
        return regular + cycle

    @property
    def plus_points(self) -> tuple[Point, ...]:
        return self.minus_points

    def pinch(self, point: Point) -> Point:
        kind, index = point
        if kind == "regular":
            return ("regular", index)
        if kind == "vanishing":
            return ("node", 0)
        raise ValueError(f"unknown point kind: {kind}")

    @property
    def through_relation(self) -> frozenset[tuple[Point, Point]]:
        return frozenset(
            (left, right)
            for left in self.minus_points
            for right in self.plus_points
            if self.pinch(left) == self.pinch(right)
        )

    def resolution(self, phase: int) -> dict[Point, Point]:
        result: dict[Point, Point] = {}
        for point in self.minus_points:
            kind, index = point
            if kind == "regular":
                result[point] = point
            else:
                result[point] = (
                    "vanishing",
                    (index + phase) % self.cycle_size,
                )
        return result

    def rotation(self, steps: int) -> dict[Point, Point]:
        return self.resolution(steps)


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


def _primitive_twist(delta: sympy.Matrix) -> sympy.Matrix:
    symplectic = sympy.Matrix([[0, 1], [-1, 0]])
    identity = sympy.eye(2)
    return identity - delta * (symplectic * delta).T


def test_real_saddle_cellulation_is_one_index_one_handle() -> None:
    assert SADDLE.euler_characteristic == 1
    assert SADDLE.incoming_euler_characteristic == 2
    assert SADDLE.relative_euler_characteristic == -1
    assert SADDLE.relative_euler_characteristic == (-1) ** 1

    incidence = SADDLE.edge_face_incidence
    boundary_edges = NEGATIVE_FIBRE.pairs + POSITIVE_FIBRE.pairs
    radial_edges = tuple(_edge("O", port) for port in ("N", "E", "S", "W"))

    assert all(incidence[edge] == 1 for edge in boundary_edges)
    assert all(incidence[edge] == 2 for edge in radial_edges)


def test_two_smoothings_specialize_to_the_same_singular_star() -> None:
    negative_image = SADDLE.specialization_image(NEGATIVE_FIBRE)
    positive_image = SADDLE.specialization_image(POSITIVE_FIBRE)

    assert negative_image == positive_image
    assert negative_image == frozenset(
        _edge("O", port) for port in ("N", "E", "S", "W")
    )
    assert SADDLE.specialization_paths(NEGATIVE_FIBRE) != (
        SADDLE.specialization_paths(POSITIVE_FIBRE)
    )


def test_the_same_local_saddle_can_merge_or_split_after_global_gluing() -> None:
    merge_exterior = NEGATIVE_FIBRE
    split_exterior = POSITIVE_FIBRE

    assert _component_count(NEGATIVE_FIBRE, merge_exterior) == 2
    assert _component_count(POSITIVE_FIBRE, merge_exterior) == 1

    assert _component_count(NEGATIVE_FIBRE, split_exterior) == 1
    assert _component_count(POSITIVE_FIBRE, split_exterior) == 2


def test_pinch_cospan_is_functional_off_the_node_and_relational_at_it() -> None:
    cospan = FinitePinchCospan(regular_count=3, cycle_size=8)
    relation = cospan.through_relation

    assert len(relation) == 3 + 8 * 8

    outgoing_degree = {
        source: sum(1 for left, _ in relation if left == source)
        for source in cospan.minus_points
    }
    assert {
        degree
        for point, degree in outgoing_degree.items()
        if point[0] == "regular"
    } == {1}
    assert {
        degree
        for point, degree in outgoing_degree.items()
        if point[0] == "vanishing"
    } == {8}


def test_smoothing_phase_selects_sections_and_their_difference_is_monodromy() -> None:
    cospan = FinitePinchCospan(regular_count=2, cycle_size=8)
    relation = cospan.through_relation

    lower = cospan.resolution(0)
    upper = cospan.resolution(1)

    assert all((source, target) in relation for source, target in lower.items())
    assert all((source, target) in relation for source, target in upper.items())
    assert all(
        cospan.pinch(source) == cospan.pinch(target)
        for source, target in upper.items()
    )

    difference = _compose(_inverse(lower), upper)
    assert difference == cospan.rotation(1)
    assert difference != cospan.rotation(0)


def test_legendre_node_is_the_elementary_node_after_a_quadratic_base_change() -> None:
    x, local_y, parameter = sympy.symbols("x local_y parameter")
    left = (2 * x - parameter) + 2 * sympy.I * local_y
    right = (2 * x - parameter) - 2 * sympy.I * local_y

    residual = sympy.expand(left * right - parameter**2)
    residual = sympy.expand(
        residual.subs(local_y**2, x * (parameter - x))
    )
    assert residual == 0

    # The map parameter |-> s=parameter^2 doubles winding in C*.
    elementary_winding = 1
    legendre_winding = 2 * elementary_winding
    assert legendre_winding == 2


def test_legendre_cusp_monodromy_is_the_square_of_the_elementary_twist() -> None:
    vanishing_cycle = sympy.Matrix([1, 0])
    elementary = _primitive_twist(vanishing_cycle)
    legendre = elementary**2

    assert elementary == sympy.Matrix([[1, 1], [0, 1]])
    assert legendre == sympy.Matrix([[1, 2], [0, 1]])

    cospan = FinitePinchCospan(regular_count=1, cycle_size=8)
    discrete_elementary = cospan.rotation(1)
    discrete_legendre = _compose(discrete_elementary, discrete_elementary)
    assert discrete_legendre == cospan.rotation(2)
