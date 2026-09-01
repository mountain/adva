from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable

import sympy

Cell = Hashable


@dataclass(frozen=True)
class ChainComplex2:
    vertices: tuple[Cell, ...]
    edges: tuple[Cell, ...]
    faces: tuple[Cell, ...]
    d1: sympy.Matrix
    d2: sympy.Matrix

    def betti(self) -> tuple[int, int, int]:
        r1 = self.d1.rank()
        r2 = self.d2.rank()
        return (
            len(self.vertices) - r1,
            len(self.edges) - r1 - r2,
            len(self.faces) - r2,
        )

    def assert_chain(self) -> None:
        assert self.d1 * self.d2 == sympy.zeros(len(self.vertices), len(self.faces))


def _index(items: tuple[Cell, ...]) -> dict[Cell, int]:
    return {item: i for i, item in enumerate(items)}


def _column_matrix(rows: int, columns: int) -> sympy.MutableSparseMatrix:
    return sympy.MutableSparseMatrix(rows, columns, {})


def cubical_annulus(n: int) -> ChainComplex2:
    assert n >= 3
    vertices = tuple(("v", i, j) for j in range(n + 1) for i in range(n))
    horizontal = tuple(("h", i, j) for j in range(n + 1) for i in range(n))
    radial = tuple(("r", i, j) for j in range(n) for i in range(n))
    edges = horizontal + radial
    faces = tuple(("f", i, j) for j in range(n) for i in range(n))
    vi, ei, fi = _index(vertices), _index(edges), _index(faces)
    d1 = _column_matrix(len(vertices), len(edges))
    for edge in horizontal:
        _, i, j = edge
        d1[vi[("v", i, j)], ei[edge]] = -1
        d1[vi[("v", (i + 1) % n, j)], ei[edge]] = 1
    for edge in radial:
        _, i, j = edge
        d1[vi[("v", i, j)], ei[edge]] = -1
        d1[vi[("v", i, j + 1)], ei[edge]] = 1
    d2 = _column_matrix(len(edges), len(faces))
    for face in faces:
        _, i, j = face
        col = fi[face]
        d2[ei[("h", i, j)], col] = 1
        d2[ei[("r", (i + 1) % n, j)], col] = 1
        d2[ei[("h", i, j + 1)], col] = -1
        d2[ei[("r", i, j)], col] = -1
    result = ChainComplex2(vertices, edges, faces, sympy.Matrix(d1), sympy.Matrix(d2))
    result.assert_chain()
    return result


def cubical_torus(n: int) -> ChainComplex2:
    vertices = tuple(("v", i, j) for j in range(n) for i in range(n))
    horizontal = tuple(("h", i, j) for j in range(n) for i in range(n))
    radial = tuple(("r", i, j) for j in range(n) for i in range(n))
    edges = horizontal + radial
    faces = tuple(("f", i, j) for j in range(n) for i in range(n))
    vi, ei, fi = _index(vertices), _index(edges), _index(faces)
    d1 = _column_matrix(len(vertices), len(edges))
    for edge in horizontal:
        _, i, j = edge
        d1[vi[("v", i, j)], ei[edge]] = -1
        d1[vi[("v", (i + 1) % n, j)], ei[edge]] = 1
    for edge in radial:
        _, i, j = edge
        d1[vi[("v", i, j)], ei[edge]] = -1
        d1[vi[("v", i, (j + 1) % n)], ei[edge]] = 1
    d2 = _column_matrix(len(edges), len(faces))
    for face in faces:
        _, i, j = face
        col = fi[face]
        d2[ei[("h", i, j)], col] = 1
        d2[ei[("r", (i + 1) % n, j)], col] = 1
        d2[ei[("h", i, (j + 1) % n)], col] = -1
        d2[ei[("r", i, j)], col] = -1
    result = ChainComplex2(vertices, edges, faces, sympy.Matrix(d1), sympy.Matrix(d2))
    result.assert_chain()
    return result


def _basis_map(
    rows: tuple[Cell, ...],
    columns: tuple[Cell, ...],
    images: dict[Cell, dict[Cell, int]],
) -> sympy.Matrix:
    ri, ci = _index(rows), _index(columns)
    matrix = _column_matrix(len(rows), len(columns))
    for source, image in images.items():
        for target, coefficient in image.items():
            matrix[ri[target], ci[source]] += coefficient
    return sympy.Matrix(matrix)


def annulus_twist(
    complex_: ChainComplex2,
    n: int,
    inverse: bool = False,
) -> tuple[sympy.Matrix, sympy.Matrix, sympy.Matrix]:
    vertices, edges, faces = complex_.vertices, complex_.edges, complex_.faces
    v_images: dict[Cell, dict[Cell, int]] = {}
    e_images: dict[Cell, dict[Cell, int]] = {}
    f_images: dict[Cell, dict[Cell, int]] = {}
    for vertex in vertices:
        _, i, j = vertex
        v_images[vertex] = {("v", (i - j if inverse else i + j) % n, j): 1}
    for edge in edges:
        kind, i, j = edge
        if kind == "h":
            target = ("h", (i - j if inverse else i + j) % n, j)
            e_images[edge] = {target: 1}
        elif inverse:
            k = (i - j - 1) % n
            e_images[edge] = {("h", k, j): -1, ("r", k, j): 1}
        else:
            k = (i + j) % n
            e_images[edge] = {("h", k, j): 1, ("r", (k + 1) % n, j): 1}
    for face in faces:
        _, i, j = face
        k = (i - j - 1 if inverse else i + j + 1) % n
        f_images[face] = {("f", k, j): 1}
    return (
        _basis_map(vertices, vertices, v_images),
        _basis_map(edges, edges, e_images),
        _basis_map(faces, faces, f_images),
    )


def torus_twist(
    complex_: ChainComplex2,
    n: int,
    inverse: bool = False,
) -> tuple[sympy.Matrix, sympy.Matrix, sympy.Matrix]:
    # The same formulas descend after identifying j=n with j=0.
    return annulus_twist(complex_, n, inverse=inverse)


def gluing_maps(
    annulus: ChainComplex2,
    torus: ChainComplex2,
    n: int,
) -> tuple[sympy.Matrix, sympy.Matrix, sympy.Matrix]:
    v_images = {v: {("v", v[1], v[2] % n): 1} for v in annulus.vertices}
    e_images: dict[Cell, dict[Cell, int]] = {}
    for edge in annulus.edges:
        kind, i, j = edge
        e_images[edge] = {(kind, i, j % n): 1}
    f_images = {f: {f: 1} for f in annulus.faces}
    return (
        _basis_map(torus.vertices, annulus.vertices, v_images),
        _basis_map(torus.edges, annulus.edges, e_images),
        _basis_map(torus.faces, annulus.faces, f_images),
    )


def _cycle(complex_: ChainComplex2, coefficients: dict[Cell, int]) -> sympy.Matrix:
    vector = sympy.zeros(len(complex_.edges), 1)
    ei = _index(complex_.edges)
    for edge, coefficient in coefficients.items():
        vector[ei[edge], 0] = coefficient
    assert complex_.d1 * vector == sympy.zeros(len(complex_.vertices), 1)
    return vector


def torus_generators(
    torus: ChainComplex2,
    n: int,
) -> tuple[sympy.Matrix, sympy.Matrix, sympy.Matrix, sympy.Matrix]:
    a = _cycle(torus, {("h", i, 0): 1 for i in range(n)})
    b = _cycle(torus, {("r", 0, j): 1 for j in range(n)})
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


def quotient_by_row(
    complex_: ChainComplex2,
    n: int,
    row: int,
    *,
    periodic_vertical: bool,
) -> tuple[ChainComplex2, sympy.Matrix, sympy.Matrix, sympy.Matrix]:
    assert 0 <= row < n
    node = ("node", row)
    v_target = {v: node if v[2] == row else v for v in complex_.vertices}
    q_vertices = tuple(dict.fromkeys(v_target.values()))
    q_edges = tuple(edge for edge in complex_.edges if not (edge[0] == "h" and edge[2] == row))
    q_faces = complex_.faces
    vi, ei, fi = _index(q_vertices), _index(q_edges), _index(q_faces)
    q0 = _column_matrix(len(q_vertices), len(complex_.vertices))
    for col, vertex in enumerate(complex_.vertices):
        q0[vi[v_target[vertex]], col] = 1
    q1 = _column_matrix(len(q_edges), len(complex_.edges))
    for col, edge in enumerate(complex_.edges):
        if edge in ei:
            q1[ei[edge], col] = 1
    q2 = sympy.eye(len(q_faces))
    d1 = _column_matrix(len(q_vertices), len(q_edges))
    for edge in q_edges:
        kind, i, j = edge
        if kind == "h":
            source = v_target[("v", i, j)]
            target = v_target[("v", (i + 1) % n, j)]
        else:
            source = v_target[("v", i, j)]
            target_j = (j + 1) % n if periodic_vertical else j + 1
            target = v_target[("v", i, target_j)]
        d1[vi[source], ei[edge]] -= 1
        d1[vi[target], ei[edge]] += 1
    d2 = sympy.Matrix(q1) * complex_.d2
    quotient = ChainComplex2(q_vertices, q_edges, q_faces, sympy.Matrix(d1), d2)
    quotient.assert_chain()
    assert quotient.d1 * sympy.Matrix(q1) == sympy.Matrix(q0) * complex_.d1
    assert quotient.d2 * q2 == sympy.Matrix(q1) * complex_.d2
    return quotient, sympy.Matrix(q0), sympy.Matrix(q1), q2


def two_disks() -> ChainComplex2:
    vertices = tuple((component, i) for component in range(2) for i in range(4))
    edges = tuple((component, i) for component in range(2) for i in range(4))
    faces = ((0, 0), (1, 0))
    vi, ei = _index(vertices), _index(edges)
    d1 = _column_matrix(8, 8)
    d2 = _column_matrix(8, 2)
    for component in range(2):
        for i in range(4):
            edge = (component, i)
            d1[vi[(component, i)], ei[edge]] = -1
            d1[vi[(component, (i + 1) % 4)], ei[edge]] = 1
            d2[ei[edge], component] = 1
    result = ChainComplex2(vertices, edges, faces, sympy.Matrix(d1), sympy.Matrix(d2))
    result.assert_chain()
    return result


def sphere_cw() -> ChainComplex2:
    return ChainComplex2((("v", 0),), (), (("f", 0),), sympy.zeros(1, 0), sympy.zeros(0, 1))


def test_annulus_and_torus_cellulations_and_twist() -> None:
    n = 4
    annulus = cubical_annulus(n)
    torus = cubical_torus(n)
    assert annulus.betti() == (1, 1, 0)
    assert torus.betti() == (1, 2, 1)

    da = annulus_twist(annulus, n)
    ia = annulus_twist(annulus, n, inverse=True)
    dt = torus_twist(torus, n)
    degree_maps = (
        (annulus.d1, da[1], ia[1]),
        (annulus.d2, da[2], ia[2]),
    )
    for boundary, forward, inverse in degree_maps:
        assert forward * inverse == sympy.eye(forward.rows)
        assert inverse * forward == sympy.eye(forward.rows)
    assert annulus.d1 * da[1] == da[0] * annulus.d1
    assert annulus.d2 * da[2] == da[1] * annulus.d2
    assert torus.d1 * dt[1] == dt[0] * torus.d1
    assert torus.d2 * dt[2] == dt[1] * torus.d2

    vi, ei = _index(annulus.edges), _index(annulus.edges)
    for i in range(n):
        identity_vertices = sympy.eye(len(annulus.vertices))
        assert da[0][:, vi[("v", i, 0)]] == identity_vertices[:, vi[("v", i, 0)]]
        assert da[0][:, vi[("v", i, n)]] == identity_vertices[:, vi[("v", i, n)]]
        for j in (0, n):
            identity_edges = sympy.eye(len(annulus.edges))
            assert da[1][:, ei[("h", i, j)]] == identity_edges[:, ei[("h", i, j)]]

    gluing = gluing_maps(annulus, torus, n)
    for g, a_map, t_map in zip(gluing, da, dt):
        assert g * a_map == t_map * g


def test_picard_lefschetz_matrix_and_infinite_path_lift() -> None:
    n = 4
    torus = cubical_torus(n)
    d0, d1, _ = torus_twist(torus, n)
    a, b, dx, dy = torus_generators(torus, n)
    assert (dx * a)[0] == 1 and (dy * a)[0] == 0
    assert (dx * b)[0] == 0 and (dy * b)[0] == 1
    matrix = sympy.Matrix(
        [
            [(dx * d1 * a)[0], (dx * d1 * b)[0]],
            [(dy * d1 * a)[0], (dy * d1 * b)[0]],
        ]
    )
    expected = sympy.Matrix([[1, 1], [0, 1]])
    assert matrix == expected
    j = sympy.Matrix([[0, 1], [-1, 0]])
    assert matrix.T * j * matrix == j
    assert d0**n == sympy.eye(d0.rows)
    assert d1**n != sympy.eye(d1.rows)
    assert matrix**n == sympy.Matrix([[1, n], [0, 1]])


def test_nodal_quotients_normalizations_and_pinch() -> None:
    n = 4
    annulus = cubical_annulus(n)
    # Use the torus quotient for the global nodal fibre and an interior row
    # quotient of the annulus for the local two-branch model.
    nodal_annulus, *_ = quotient_by_row(
        annulus,
        n,
        row=2,
        periodic_vertical=False,
    )
    assert nodal_annulus.betti() == (1, 0, 0)
    assert two_disks().betti() == (2, 0, 0)

    torus = cubical_torus(n)
    nodal_torus, q0, q1, q2 = quotient_by_row(
        torus,
        n,
        row=0,
        periodic_vertical=True,
    )
    assert nodal_torus.betti() == (1, 1, 1)
    assert sphere_cw().betti() == (1, 0, 1)

    d = torus_twist(torus, n)
    inv = torus_twist(torus, n, inverse=True)
    a, b, _, _ = torus_generators(torus, n)
    assert q1 * a == sympy.zeros(q1.rows, 1)
    difference = q1 * d[1] * b - q1 * b
    assert nodal_torus.d1 * difference == sympy.zeros(len(nodal_torus.vertices), 1)
    assert nodal_torus.d2.row_join(difference).rank() == nodal_torus.d2.rank()

    # Marked outgoing pinch: q_+ = q_- D^{-1}.
    for q, forward, inverse in ((q0, d[0], inv[0]), (q1, d[1], inv[1]), (q2, d[2], inv[2])):
        q_plus = q * inverse
        assert q_plus * forward == q


def test_chain_level_picard_lefschetz_formula_on_homology_coordinates() -> None:
    n = 5
    torus = cubical_torus(n)
    _, d1, _ = torus_twist(torus, n)
    a, b, dx, dy = torus_generators(torus, n)
    for p, q in ((2, 3), (-1, 4), (0, 7)):
        cycle = p * a + q * b
        image = d1 * cycle
        coordinates = sympy.Matrix([(dx * image)[0], (dy * image)[0]])
        assert coordinates == sympy.Matrix([p + q, q])
