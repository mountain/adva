from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from typing import Any

from adva import link_modules


HANDLE_CELLULATION_KERNEL = r"""
(module decorated-handle-cellulation
  (export fork-recombine)

  (def fork-recombine-expanded
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (neg (use left))
          (id (use right))))))

  (def fork-recombine
    (fn ((x Real)) Real
      (call fork-recombine-expanded
        (copy (use x)))))
)
"""


Vertex = tuple[str, int, int]
Edge = tuple[Vertex, Vertex]


@dataclass(frozen=True, slots=True)
class CellFace:
    """One oriented quadrilateral in the research-local trace presentation."""

    event: int
    operation: str
    vertices: tuple[Vertex, Vertex, Vertex, Vertex]


@dataclass(frozen=True, slots=True)
class TracePatch:
    """One program event and the standard surface patch assigned to it."""

    event: int
    operation: str
    kind: str
    causal_layer: int


@dataclass(frozen=True, slots=True)
class CellPiece:
    """A surface patch before its declared port circles are glued."""

    faces: tuple[CellFace, ...]
    boundaries: dict[str, tuple[Vertex, ...]]


@dataclass(frozen=True, slots=True)
class CellulatedTrace:
    """A finite oriented 2-complex derived from one checked program diamond.

    This remains a research presentation rather than an Adva semantic object.
    Its cells are intentionally elementary: planar grid squares supply the
    pants and copants, and four quadrilaterals supply each branch cylinder.
    """

    faces: tuple[CellFace, ...]
    patches: tuple[TracePatch, ...]
    input_vertices: frozenset[Vertex]
    output_vertices: frozenset[Vertex]
    gluing_sizes: tuple[int, ...]

    @property
    def vertices(self) -> frozenset[Vertex]:
        return frozenset(vertex for face in self.faces for vertex in face.vertices)

    @property
    def edge_incidence(self) -> dict[Edge, tuple[tuple[Vertex, Vertex, int], ...]]:
        incidence: dict[Edge, list[tuple[Vertex, Vertex, int]]] = defaultdict(list)
        for face_index, face in enumerate(self.faces):
            for left, right in _directed_edges(face.vertices):
                incidence[_edge(left, right)].append((left, right, face_index))
        return {edge: tuple(uses) for edge, uses in incidence.items()}

    @property
    def edges(self) -> frozenset[Edge]:
        return frozenset(self.edge_incidence)

    @property
    def boundary_cycles(self) -> tuple[tuple[Vertex, ...], ...]:
        return _boundary_cycles(self.faces)

    @property
    def euler_characteristic(self) -> int:
        return len(self.vertices) - len(self.edges) + len(self.faces)

    @property
    def genus(self) -> int:
        if not self.is_connected:
            raise ValueError("the calibration expects one connected trace")
        numerator = 2 - len(self.boundary_cycles) - self.euler_characteristic
        if numerator < 0 or numerator % 2:
            raise ValueError("the finite complex does not classify an oriented surface")
        return numerator // 2

    @property
    def is_connected(self) -> bool:
        adjacency: dict[Vertex, set[Vertex]] = defaultdict(set)
        for left, right in self.edges:
            adjacency[left].add(right)
            adjacency[right].add(left)
        if not self.vertices:
            return False
        reached = _reachable(adjacency, min(self.vertices))
        return reached == set(self.vertices)

    @property
    def seam_profile(self) -> Counter[tuple[str, str]]:
        result: Counter[tuple[str, str]] = Counter()
        for uses in self.edge_incidence.values():
            if len(uses) != 2:
                continue
            operations = tuple(
                sorted({self.faces[face_index].operation for _, _, face_index in uses})
            )
            if len(operations) == 2:
                result[operations] += 1
        return result

    def assert_oriented_surface(self) -> None:
        """Check every edge and vertex link, not only global classification data."""

        boundary_edges = set()
        for edge, uses in self.edge_incidence.items():
            if len(uses) == 1:
                boundary_edges.add(edge)
                continue
            assert len(uses) == 2, f"nonmanifold edge {edge!r} has {len(uses)} faces"
            first_left, first_right, _ = uses[0]
            second_left, second_right, _ = uses[1]
            assert (first_left, first_right) == (second_right, second_left), (
                f"interior edge {edge!r} does not have opposite face orientations"
            )

        link_edges: dict[Vertex, list[tuple[Edge, Edge]]] = defaultdict(list)
        for face in self.faces:
            for index, vertex in enumerate(face.vertices):
                previous = face.vertices[index - 1]
                following = face.vertices[(index + 1) % len(face.vertices)]
                previous_edge = _edge(vertex, previous)
                following_edge = _edge(vertex, following)
                assert previous_edge != following_edge
                link_edges[vertex].append((previous_edge, following_edge))

        for vertex in self.vertices:
            links = link_edges[vertex]
            degrees: Counter[Edge] = Counter()
            adjacency: dict[Edge, set[Edge]] = defaultdict(set)
            for left, right in links:
                degrees[left] += 1
                degrees[right] += 1
                adjacency[left].add(right)
                adjacency[right].add(left)

            link_nodes = set(degrees)
            assert _reachable(adjacency, min(link_nodes)) == link_nodes
            incident_boundary = {edge for edge in boundary_edges if vertex in edge}
            if incident_boundary:
                assert len(incident_boundary) == 2
                assert sorted(degrees.values()).count(1) == 2
                assert all(degree in (1, 2) for degree in degrees.values())
            else:
                assert all(degree == 2 for degree in degrees.values())


class _UnionFind:
    def __init__(self, vertices: set[Vertex]) -> None:
        self.parent = {vertex: vertex for vertex in vertices}

    def find(self, vertex: Vertex) -> Vertex:
        parent = self.parent[vertex]
        if parent != vertex:
            self.parent[vertex] = self.find(parent)
        return self.parent[vertex]

    def union(self, left: Vertex, right: Vertex) -> None:
        left_root = self.find(left)
        right_root = self.find(right)
        if left_root == right_root:
            raise ValueError("a declared gluing would collapse an existing vertex")
        if right_root < left_root:
            left_root, right_root = right_root, left_root
        self.parent[right_root] = left_root


def _edge(left: Vertex, right: Vertex) -> Edge:
    if left == right:
        raise ValueError("a surface edge cannot collapse to one vertex")
    return (left, right) if left < right else (right, left)


def _directed_edges(vertices: tuple[Vertex, ...]) -> tuple[tuple[Vertex, Vertex], ...]:
    return tuple(
        (vertices[index], vertices[(index + 1) % len(vertices)])
        for index in range(len(vertices))
    )


def _reachable(adjacency: dict[Any, set[Any]], start: Any) -> set[Any]:
    reached = {start}
    queue = deque([start])
    while queue:
        item = queue.popleft()
        for neighbor in adjacency[item] - reached:
            reached.add(neighbor)
            queue.append(neighbor)
    return reached


def _boundary_cycles(faces: tuple[CellFace, ...]) -> tuple[tuple[Vertex, ...], ...]:
    incidence: dict[Edge, list[tuple[Vertex, Vertex]]] = defaultdict(list)
    for face in faces:
        for left, right in _directed_edges(face.vertices):
            incidence[_edge(left, right)].append((left, right))

    successor: dict[Vertex, Vertex] = {}
    predecessor: dict[Vertex, Vertex] = {}
    for uses in incidence.values():
        if len(uses) != 1:
            continue
        left, right = uses[0]
        if left in successor or right in predecessor:
            raise ValueError("the oriented boundary is not a disjoint union of circles")
        successor[left] = right
        predecessor[right] = left

    if set(successor) != set(predecessor):
        raise ValueError("the oriented boundary contains an open arc")

    remaining = set(successor)
    cycles = []
    while remaining:
        start = min(remaining)
        cycle = []
        vertex = start
        while True:
            if vertex not in remaining:
                raise ValueError("a boundary walk intersects an earlier component")
            cycle.append(vertex)
            remaining.remove(vertex)
            vertex = successor[vertex]
            if vertex == start:
                break
        cycles.append(tuple(cycle))
    return tuple(sorted(cycles, key=lambda cycle: (len(cycle), cycle)))


def _grid_pants(prefix: str, event: int, operation: str) -> CellPiece:
    """Build a rectangle with two open interior squares: a pair of pants."""

    holes = {(1, 1), (3, 1)}

    def vertex(x: int, y: int) -> Vertex:
        return (prefix, x, y)

    faces = tuple(
        CellFace(
            event=event,
            operation=operation,
            vertices=(
                vertex(x, y),
                vertex(x + 1, y),
                vertex(x + 1, y + 1),
                vertex(x, y + 1),
            ),
        )
        for y in range(3)
        for x in range(5)
        if (x, y) not in holes
    )
    cycles = _boundary_cycles(faces)
    outer = next(cycle for cycle in cycles if len(cycle) == 16)

    def hole_cycle(x: int) -> tuple[Vertex, ...]:
        expected = {
            vertex(x, 1),
            vertex(x + 1, 1),
            vertex(x + 1, 2),
            vertex(x, 2),
        }
        return next(cycle for cycle in cycles if set(cycle) == expected)

    assert len(faces) == 13
    assert sorted(len(cycle) for cycle in cycles) == [4, 4, 16]
    return CellPiece(
        faces=faces,
        boundaries={"outer": outer, "left": hole_cycle(1), "right": hole_cycle(3)},
    )


def _branch_cylinder(prefix: str, event: int, operation: str) -> CellPiece:
    """Build a four-band identity cylinder carrying one branch decoration."""

    def vertex(position: int, level: int) -> Vertex:
        return (prefix, position, level)

    faces = tuple(
        CellFace(
            event=event,
            operation=operation,
            vertices=(
                vertex(position, 0),
                vertex((position + 1) % 4, 0),
                vertex((position + 1) % 4, 1),
                vertex(position, 1),
            ),
        )
        for position in range(4)
    )
    cycles = _boundary_cycles(faces)

    def level_cycle(level: int) -> tuple[Vertex, ...]:
        return next(cycle for cycle in cycles if all(vertex[2] == level for vertex in cycle))

    assert sorted(len(cycle) for cycle in cycles) == [4, 4]
    return CellPiece(
        faces=faces,
        boundaries={"input": level_cycle(0), "output": level_cycle(1)},
    )


def _glue_reversing(
    quotient: _UnionFind,
    left: tuple[Vertex, ...],
    right: tuple[Vertex, ...],
) -> None:
    """Identify two induced boundary cycles with opposite orientations."""

    if len(left) != len(right):
        raise ValueError("glued boundary circles require equal subdivisions")
    for index, left_vertex in enumerate(left):
        quotient.union(left_vertex, right[-index % len(right)])


def _cellulated_handle(operations: dict[str, int]) -> CellulatedTrace:
    copy = _grid_pants("copy", operations["copy"], "copy-copants")
    neg = _branch_cylinder("neg", operations["neg"], "neg-cylinder")
    identity = _branch_cylinder("id", operations["id"], "id-cylinder")
    add = _grid_pants("add", operations["add"], "add-pants")
    pieces = (copy, neg, identity, add)

    raw_faces = tuple(face for piece in pieces for face in piece.faces)
    raw_vertices = {vertex for face in raw_faces for vertex in face.vertices}
    quotient = _UnionFind(raw_vertices)
    gluings = (
        (copy.boundaries["left"], neg.boundaries["input"]),
        (neg.boundaries["output"], add.boundaries["left"]),
        (copy.boundaries["right"], identity.boundaries["input"]),
        (identity.boundaries["output"], add.boundaries["right"]),
    )
    for left, right in gluings:
        _glue_reversing(quotient, left, right)

    faces = tuple(
        CellFace(
            event=face.event,
            operation=face.operation,
            vertices=tuple(quotient.find(vertex) for vertex in face.vertices),
        )
        for face in raw_faces
    )
    input_vertices = frozenset(
        quotient.find(vertex) for vertex in copy.boundaries["outer"]
    )
    output_vertices = frozenset(
        quotient.find(vertex) for vertex in add.boundaries["outer"]
    )
    return CellulatedTrace(
        faces=faces,
        patches=(
            TracePatch(operations["copy"], "copy", "copants", 0),
            TracePatch(operations["neg"], "neg", "decorated-cylinder", 1),
            TracePatch(operations["id"], "id", "decorated-cylinder", 1),
            TracePatch(operations["add"], "add", "pants", 2),
        ),
        input_vertices=input_vertices,
        output_vertices=output_vertices,
        gluing_sizes=tuple(len(left) for left, _ in gluings),
    )


def _diamond() -> Any:
    workspace = link_modules([HANDLE_CELLULATION_KERNEL])
    return workspace.function("decorated-handle-cellulation", "fork-recombine")


def test_program_diamond_generates_an_explicit_oriented_genus_one_cellulation() -> None:
    function = _diamond()
    assert tuple(node["operation"]["name"] for node in function.ir["nodes"]) == (
        "copy",
        "neg",
        "id",
        "add",
    )
    operations = {
        node["operation"]["name"]: node["id"] for node in function.ir["nodes"]
    }
    trace = _cellulated_handle(operations)

    trace.assert_oriented_surface()

    assert trace.is_connected
    assert (len(trace.vertices), len(trace.edges), len(trace.faces)) == (48, 84, 34)
    assert trace.euler_characteristic == -2
    assert len(trace.boundary_cycles) == 2
    assert trace.genus == 1
    assert {frozenset(cycle) for cycle in trace.boundary_cycles} == {
        trace.input_vertices,
        trace.output_vertices,
    }


def test_cellulation_uses_only_declared_event_patches_and_program_seams() -> None:
    function = _diamond()
    operations = {
        node["operation"]["name"]: node["id"] for node in function.ir["nodes"]
    }
    trace = _cellulated_handle(operations)

    assert trace.gluing_sizes == (4, 4, 4, 4)
    assert tuple(patch.event for patch in trace.patches) == (0, 1, 2, 3)
    assert tuple(patch.causal_layer for patch in trace.patches) == (0, 1, 1, 2)
    assert {face.event for face in trace.faces} == set(operations.values())
    assert Counter(face.operation for face in trace.faces) == Counter(
        {
            "copy-copants": 13,
            "neg-cylinder": 4,
            "id-cylinder": 4,
            "add-pants": 13,
        }
    )
    assert trace.seam_profile == Counter(
        {
            ("copy-copants", "neg-cylinder"): 4,
            ("add-pants", "neg-cylinder"): 4,
            ("copy-copants", "id-cylinder"): 4,
            ("add-pants", "id-cylinder"): 4,
        }
    )
