from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

import sympy

Cell = Hashable


@dataclass(frozen=True)
class Complex2:
    vertices: tuple[Cell, ...]
    edges: tuple[Cell, ...]
    faces: tuple[Cell, ...]
    d1: sympy.Matrix
    d2: sympy.Matrix

    def __post_init__(self) -> None:
        assert self.d1 * self.d2 == sympy.zeros(len(self.vertices), len(self.faces))

    def betti(self) -> tuple[int, int, int]:
        r1, r2 = self.d1.rank(), self.d2.rank()
        return (
            len(self.vertices) - r1,
            len(self.edges) - r1 - r2,
            len(self.faces) - r2,
        )


def _index(items: tuple[Cell, ...]) -> dict[Cell, int]:
    return {item: i for i, item in enumerate(items)}


def _sparse(rows: int, cols: int) -> sympy.MutableSparseMatrix:
    return sympy.MutableSparseMatrix(rows, cols, {})


def cubical(n: int, *, periodic_vertical: bool) -> Complex2:
    height = n if periodic_vertical else n + 1
    vertices = tuple(("v", i, j) for j in range(height) for i in range(n))
    horizontal = tuple(("h", i, j) for j in range(height) for i in range(n))
    radial = tuple(("r", i, j) for j in range(n) for i in range(n))
    edges = horizontal + radial
    faces = tuple(("f", i, j) for j in range(n) for i in range(n))
    vi, ei, fi = _index(vertices), _index(edges), _index(faces)
    d1 = _sparse(len(vertices), len(edges))
    for edge in horizontal:
        _, i, j = edge
        d1[vi[("v", i, j)], ei[edge]] = -1
        d1[vi[("v", (i + 1) % n, j)], ei[edge]] = 1
    for edge in radial:
        _, i, j = edge
        target_j = (j + 1) % n if periodic_vertical else j + 1
        d1[vi[("v", i, j)], ei[edge]] = -1
        d1[vi[("v", i, target_j)], ei[edge]] = 1
    d2 = _sparse(len(edges), len(faces))
    for face in faces:
        _, i, j = face
        top_j = (j + 1) % n if periodic_vertical else j + 1
        col = fi[face]
        d2[ei[("h", i, j)], col] = 1
        d2[ei[("r", (i + 1) % n, j)], col] = 1
        d2[ei[("h", i, top_j)], col] = -1
        d2[ei[("r", i, j)], col] = -1
    return Complex2(vertices, edges, faces, sympy.Matrix(d1), sympy.Matrix(d2))


def _linear_map(
    basis: tuple[Cell, ...],
    images: dict[Cell, dict[Cell, int]],
) -> sympy.Matrix:
    index = _index(basis)
    result = _sparse(len(basis), len(basis))
    for source, image in images.items():
        for target, coefficient in image.items():
            result[index[target], index[source]] += coefficient
    return sympy.Matrix(result)


def twist(complex_: Complex2, n: int, *, inverse: bool = False) -> tuple[sympy.Matrix, ...]:
    v_images: dict[Cell, dict[Cell, int]] = {}
    e_images: dict[Cell, dict[Cell, int]] = {}
    f_images: dict[Cell, dict[Cell, int]] = {}
    for vertex in complex_.vertices:
        _, i, j = vertex
        target_i = (i - j if inverse else i + j) % n
        v_images[vertex] = {("v", target_i, j): 1}
    for edge in complex_.edges:
        kind, i, j = edge
        if kind == "h":
            target_i = (i - j if inverse else i + j) % n
            e_images[edge] = {("h", target_i, j): 1}
        elif inverse:
            k = (i - j - 1) % n
            e_images[edge] = {("h", k, j): -1, ("r", k, j): 1}
        else:
            k = (i + j) % n
            e_images[edge] = {("h", k, j): 1, ("r", (k + 1) % n, j): 1}
    for face in complex_.faces:
        _, i, j = face
        k = (i - j - 1 if inverse else i + j + 1) % n
        f_images[face] = {("f", k, j): 1}
    return (
        _linear_map(complex_.vertices, v_images),
        _linear_map(complex_.edges, e_images),
        _linear_map(complex_.faces, f_images),
    )


def gluing(annulus: Complex2, torus: Complex2, n: int) -> tuple[sympy.Matrix, ...]:
    def matrix(
        target: tuple[Cell, ...],
        source: tuple[Cell, ...],
        image: dict[Cell, Cell],
    ) -> sympy.Matrix:
        ti, si = _index(target), _index(source)
        result = _sparse(len(target), len(source))
        for cell, target_cell in image.items():
            result[ti[target_cell], si[cell]] = 1
        return sympy.Matrix(result)

    vertex_image = {v: ("v", v[1], v[2] % n) for v in annulus.vertices}
    edge_image = {e: (e[0], e[1], e[2] % n) for e in annulus.edges}
    face_image = {f: f for f in annulus.faces}
    return (
        matrix(torus.vertices, annulus.vertices, vertex_image),
        matrix(torus.edges, annulus.edges, edge_image),
        matrix(torus.faces, annulus.faces, face_image),
    )


def cycle(complex_: Complex2, terms: dict[Cell, int]) -> sympy.Matrix:
    result = sympy.zeros(len(complex_.edges), 1)
    index = _index(complex_.edges)
    for edge, coefficient in terms.items():
        result[index[edge], 0] = coefficient
    assert complex_.d1 * result == sympy.zeros(len(complex_.vertices), 1)
    return result


def torus_basis(torus: Complex2, n: int) -> tuple[sympy.Matrix, ...]:
    a = cycle(torus, {("h", i, 0): 1 for i in range(n)})
    b = cycle(torus, {("r", 0, j): 1 for j in range(n)})
    dx = sympy.zeros(1, len(torus.edges))
    dy = sympy.zeros(1, len(torus.edges))
    ei = _index(torus.edges)
    for j in range(n):
        dx[0, ei[("h", n - 1, j)]] = 1
    for i in range(n):
        dy[0, ei[("r", i, n - 1)]] = 1
    assert dx * torus.d2 == sympy.zeros(1, len(torus.faces))
    assert dy * torus.d2 == sympy.zeros(1, len(torus.faces))
    return a, b, dx, dy


def quotient_row(
    complex_: Complex2,
    n: int,
    row: int,
    *,
    periodic_vertical: bool,
) -> tuple[Complex2, sympy.Matrix, sympy.Matrix, sympy.Matrix]:
    node = ("node", row)
    vertex_image = {v: node if v[2] == row else v for v in complex_.vertices}
    vertices = tuple(dict.fromkeys(vertex_image.values()))
    edges = tuple(e for e in complex_.edges if not (e[0] == "h" and e[2] == row))
    vi, ei = _index(vertices), _index(edges)
    q0 = _sparse(len(vertices), len(complex_.vertices))
    q1 = _sparse(len(edges), len(complex_.edges))
    for col, vertex in enumerate(complex_.vertices):
        q0[vi[vertex_image[vertex]], col] = 1
    for col, edge in enumerate(complex_.edges):
        if edge in ei:
            q1[ei[edge], col] = 1
    d1 = _sparse(len(vertices), len(edges))
    for edge in edges:
        kind, i, j = edge
        source = vertex_image[("v", i, j)]
        if kind == "h":
            target = vertex_image[("v", (i + 1) % n, j)]
        else:
            target_j = (j + 1) % n if periodic_vertical else j + 1
            target = vertex_image[("v", i, target_j)]
        d1[vi[source], ei[edge]] -= 1
        d1[vi[target], ei[edge]] += 1
    q2 = sympy.eye(len(complex_.faces))
    d2 = sympy.Matrix(q1) * complex_.d2
    quotient = Complex2(vertices, edges, complex_.faces, sympy.Matrix(d1), d2)
    assert quotient.d1 * sympy.Matrix(q1) == sympy.Matrix(q0) * complex_.d1
    return quotient, sympy.Matrix(q0), sympy.Matrix(q1), q2


def test_annulus_twist_and_torus_descent() -> None:
    n = 4
    annulus = cubical(n, periodic_vertical=False)
    torus = cubical(n, periodic_vertical=True)
    assert annulus.betti() == (1, 1, 0)
    assert torus.betti() == (1, 2, 1)
    forward = twist(annulus, n)
    inverse = twist(annulus, n, inverse=True)
    torus_map = twist(torus, n)
    for degree in range(3):
        assert forward[degree] * inverse[degree] == sympy.eye(forward[degree].rows)
        assert inverse[degree] * forward[degree] == sympy.eye(forward[degree].rows)
    assert annulus.d1 * forward[1] == forward[0] * annulus.d1
    assert annulus.d2 * forward[2] == forward[1] * annulus.d2
    vi, ei = _index(annulus.vertices), _index(annulus.edges)
    for i in range(n):
        for j in (0, n):
            assert forward[0][:, vi[("v", i, j)]] == sympy.eye(len(vi))[:, vi[("v", i, j)]]
            assert forward[1][:, ei[("h", i, j)]] == sympy.eye(len(ei))[:, ei[("h", i, j)]]
    for glue, annulus_map, descended in zip(gluing(annulus, torus, n), forward, torus_map):
        assert glue * annulus_map == descended * glue


def test_picard_lefschetz_matrix_and_path_lift() -> None:
    n = 4
    torus = cubical(n, periodic_vertical=True)
    d0, d1, _ = twist(torus, n)
    a, b, dx, dy = torus_basis(torus, n)
    matrix = sympy.Matrix(
        [
            [(dx * d1 * a)[0], (dx * d1 * b)[0]],
            [(dy * d1 * a)[0], (dy * d1 * b)[0]],
        ]
    )
    assert matrix == sympy.Matrix([[1, 1], [0, 1]])
    j = sympy.Matrix([[0, 1], [-1, 0]])
    assert matrix.T * j * matrix == j
    assert d0**n == sympy.eye(d0.rows)
    assert d1**n != sympy.eye(d1.rows)
    assert matrix**n == sympy.Matrix([[1, n], [0, 1]])


def test_nodal_quotients_and_marked_pinch() -> None:
    n = 4
    annulus = cubical(n, periodic_vertical=False)
    nodal_annulus, *_ = quotient_row(
        annulus,
        n,
        row=2,
        periodic_vertical=False,
    )
    assert nodal_annulus.betti() == (1, 0, 0)

    torus = cubical(n, periodic_vertical=True)
    nodal_torus, q0, q1, q2 = quotient_row(
        torus,
        n,
        row=0,
        periodic_vertical=True,
    )
    assert nodal_torus.betti() == (1, 1, 1)
    forward = twist(torus, n)
    inverse = twist(torus, n, inverse=True)
    a, b, _, _ = torus_basis(torus, n)
    assert q1 * a == sympy.zeros(q1.rows, 1)
    difference = q1 * forward[1] * b - q1 * b
    assert nodal_torus.d2.row_join(difference).rank() == nodal_torus.d2.rank()
    for pinch, direct, reverse in zip((q0, q1, q2), forward, inverse):
        outgoing = pinch * reverse
        assert outgoing * direct == pinch


def test_picard_lefschetz_formula_on_homology_coordinates() -> None:
    n = 5
    torus = cubical(n, periodic_vertical=True)
    _, d1, _ = twist(torus, n)
    a, b, dx, dy = torus_basis(torus, n)
    for p, q in ((2, 3), (-1, 4), (0, 7)):
        image = d1 * (p * a + q * b)
        assert sympy.Matrix([(dx * image)[0], (dy * image)[0]]) == sympy.Matrix([p + q, q])
