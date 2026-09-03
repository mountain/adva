from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations, product
from typing import TypeAlias


Domain: TypeAlias = str
Face: TypeAlias = frozenset[Domain]
Support: TypeAlias = frozenset[int]
Permutation: TypeAlias = tuple[Domain, Domain, Domain]

DOMAINS: tuple[Domain, ...] = ("K", "X", "t")
FACE_NAMES: tuple[str, ...] = ("K", "X", "t", "KX", "Xt", "tK", "KXt")
FACES: tuple[Face, ...] = (
    frozenset({"K"}),
    frozenset({"X"}),
    frozenset({"t"}),
    frozenset({"K", "X"}),
    frozenset({"X", "t"}),
    frozenset({"t", "K"}),
    frozenset({"K", "X", "t"}),
)
UNIVERSE: Support = frozenset(range(len(FACES)))
PERMUTATIONS: tuple[Permutation, ...] = tuple(permutations(DOMAINS))
ROTATIONS: tuple[Permutation, ...] = (
    ("K", "X", "t"),
    ("X", "t", "K"),
    ("t", "K", "X"),
)
REFLECTIONS: tuple[Permutation, ...] = (
    ("K", "t", "X"),
    ("t", "X", "K"),
    ("X", "K", "t"),
)


@dataclass(frozen=True)
class Archetype:
    label: str
    name: str
    representative: tuple[str, ...]
    arity: int
    chiral: bool
    orbit_size: int


ARCHETYPES: tuple[Archetype, ...] = (
    Archetype("G00", "empty/full", (), 0, False, 2),
    Archetype("G01", "face point", ("KXt",), 3, False, 2),
    Archetype("G02", "edge point", ("tK",), 3, False, 6),
    Archetype("G03", "vertex point", ("t",), 2, False, 6),
    Archetype("G04", "edge-face chain", ("tK", "KXt"), 2, False, 6),
    Archetype("G05", "edge pair", ("Xt", "tK"), 3, False, 6),
    Archetype("G06", "vertex-face pair", ("t", "KXt"), 3, False, 6),
    Archetype("G07", "oriented vertex-edge flag", ("t", "tK"), 2, True, 12),
    Archetype("G08", "vertex-opposite-edge pair", ("t", "KX"), 3, False, 6),
    Archetype("G09", "vertex pair", ("X", "t"), 3, False, 6),
    Archetype(
        "G10",
        "two-edge face cap",
        ("Xt", "tK", "KXt"),
        3,
        False,
        6,
    ),
    Archetype("G11", "edge triad", ("KX", "Xt", "tK"), 3, False, 2),
    Archetype(
        "G12",
        "oriented full flag",
        ("t", "tK", "KXt"),
        3,
        True,
        12,
    ),
    Archetype(
        "G13",
        "vertex-opposite-edge face",
        ("t", "KX", "KXt"),
        2,
        False,
        6,
    ),
    Archetype(
        "G14",
        "vertex two-edge fan",
        ("t", "Xt", "tK"),
        3,
        False,
        6,
    ),
    Archetype(
        "G15",
        "oriented mixed edge fan",
        ("t", "KX", "tK"),
        3,
        True,
        12,
    ),
    Archetype(
        "G16",
        "two-vertex face",
        ("X", "t", "KXt"),
        3,
        False,
        6,
    ),
    Archetype(
        "G17",
        "oriented broken boundary",
        ("X", "t", "tK"),
        3,
        True,
        12,
    ),
    Archetype("G18", "closed edge", ("X", "t", "Xt"), 1, False, 6),
    Archetype("G19", "vertex triad", ("K", "X", "t"), 3, False, 2),
)


def _all_supports() -> tuple[Support, ...]:
    return tuple(
        frozenset(index for index, bit in enumerate(bits) if bit)
        for bits in product((False, True), repeat=len(FACES))
    )


def _support(*face_names: str) -> Support:
    return frozenset(FACE_NAMES.index(name) for name in face_names)


def _permute(support: Support, permutation: Permutation) -> Support:
    domain_map = dict(zip(DOMAINS, permutation, strict=True))
    return frozenset(
        FACES.index(frozenset(domain_map[domain] for domain in FACES[index]))
        for index in support
    )


def _orbit(support: Support, *, include_complement: bool) -> frozenset[Support]:
    images = frozenset(_permute(support, permutation) for permutation in PERMUTATIONS)
    if not include_complement:
        return images
    return images | frozenset(UNIVERSE - image for image in images)


def _factors_through(support: Support, coordinates: tuple[Domain, ...]) -> bool:
    values: dict[tuple[bool, ...], bool] = {}
    for index, face in enumerate(FACES):
        key = tuple(domain in face for domain in coordinates)
        value = index in support
        if key in values and values[key] != value:
            return False
        values[key] = value
    return True


def _essential_arity(support: Support) -> int:
    return min(
        len(coordinates)
        for size in range(len(DOMAINS) + 1)
        for coordinates in combinations(DOMAINS, size)
        if _factors_through(support, coordinates)
    )


def _is_chiral(support: Support) -> bool:
    rotations = {_permute(support, rotation) for rotation in ROTATIONS}
    return all(
        _permute(support, reflection) not in rotations
        for reflection in REFLECTIONS
    )


def _atomic_support(domain: Domain) -> Support:
    return frozenset(index for index, face in enumerate(FACES) if domain in face)


def _edge_form_support(
    left: Domain,
    right: Domain,
    truth_table: tuple[bool, bool, bool, bool],
) -> Support:
    # Table order is 00, 10, 01, 11 for the ordered pair (left, right).
    table_index = {(False, False): 0, (True, False): 1,
                   (False, True): 2, (True, True): 3}
    return frozenset(
        index
        for index, face in enumerate(FACES)
        if truth_table[table_index[(left in face, right in face)]]
    )


def _is_essential_binary(truth_table: tuple[bool, bool, bool, bool]) -> bool:
    table_index = {
        (False, False): 0,
        (True, False): 1,
        (False, True): 2,
        (True, True): 3,
    }

    def value(left: bool, right: bool) -> bool:
        return truth_table[table_index[(left, right)]]

    depends_on_left = any(
        value(False, right) != value(True, right) for right in (False, True)
    )
    depends_on_right = any(
        value(left, False) != value(left, True) for left in (False, True)
    )
    return depends_on_left and depends_on_right


def test_h7_is_exactly_the_nonempty_face_lattice_of_a_triangle() -> None:
    expected = {
        frozenset(face)
        for size in range(1, len(DOMAINS) + 1)
        for face in combinations(DOMAINS, size)
    }

    assert set(FACES) == expected
    assert len(FACES) == 7
    assert frozenset() not in FACES


def test_128_supports_partition_by_minimal_domain_dependency() -> None:
    counts = {arity: 0 for arity in range(4)}
    for support in _all_supports():
        counts[_essential_arity(support)] += 1

    assert counts == {0: 2, 1: 6, 2: 30, 3: 90}


def test_each_edge_has_six_symmetric_and_four_oriented_binary_forms() -> None:
    tables = tuple(product((False, True), repeat=4))
    essential = tuple(table for table in tables if _is_essential_binary(table))
    symmetric = tuple(table for table in essential if table[1] == table[2])
    oriented = tuple(table for table in essential if table[1] != table[2])

    assert len(essential) == 10
    assert len(symmetric) == 6
    assert len(oriented) == 4

    edge_supports: set[Support] = set()
    oriented_supports: set[Support] = set()
    for left, right in combinations(DOMAINS, 2):
        edge_supports.update(
            _edge_form_support(left, right, table) for table in essential
        )
        oriented_supports.update(
            _edge_form_support(left, right, table) for table in oriented
        )

    assert len(edge_supports) == 30
    assert len(oriented_supports) == 12
    assert all(_essential_arity(support) == 2 for support in edge_supports)
    assert all(_is_chiral(support) for support in oriented_supports)


def test_triangle_chirality_splits_edge_and_genuine_triadic_supports() -> None:
    counts = {(arity, chiral): 0 for arity in range(4) for chiral in (False, True)}
    for support in _all_supports():
        counts[(_essential_arity(support), _is_chiral(support))] += 1

    assert counts == {
        (0, False): 2,
        (0, True): 0,
        (1, False): 6,
        (1, True): 0,
        (2, False): 18,
        (2, True): 12,
        (3, False): 54,
        (3, True): 36,
    }


def test_twenty_labeled_archetypes_partition_all_supports() -> None:
    covered: set[Support] = set()
    for archetype in ARCHETYPES:
        representative = _support(*archetype.representative)
        orbit = _orbit(representative, include_complement=True)

        assert len(orbit) == archetype.orbit_size
        assert _essential_arity(representative) == archetype.arity
        assert _is_chiral(representative) is archetype.chiral
        assert covered.isdisjoint(orbit)
        covered.update(orbit)

    assert len(ARCHETYPES) == 20
    assert covered == set(_all_supports())


def test_domain_symmetry_has_40_orbits_and_complement_reduces_them_to_20() -> None:
    domain_orbits = {
        frozenset(_orbit(support, include_complement=False))
        for support in _all_supports()
    }
    domain_complement_orbits = {
        frozenset(_orbit(support, include_complement=True))
        for support in _all_supports()
    }

    assert len(domain_orbits) == 40
    assert len(domain_complement_orbits) == 20


def test_clockwise_and_counterclockwise_disjunctions_have_one_shadow() -> None:
    atoms = {domain: _atomic_support(domain) for domain in DOMAINS}

    def defect(left: Domain, right: Domain) -> Support:
        return atoms[left] - atoms[right]

    clockwise = (
        defect("K", "X") | defect("X", "t") | defect("t", "K")
    )
    counterclockwise = (
        defect("X", "K") | defect("t", "X") | defect("K", "t")
    )

    assert clockwise == counterclockwise
    assert clockwise == UNIVERSE - _support("KXt")


def test_reversing_an_ordered_domain_pair_keeps_only_the_opposite_role() -> None:
    def opposite(left: Domain, right: Domain) -> Domain:
        remaining = set(DOMAINS) - {left, right}
        assert len(remaining) == 1
        return remaining.pop()

    directed = {
        (left, right, opposite(left, right))
        for left in DOMAINS
        for right in DOMAINS
        if left != right
    }

    assert len(directed) == 6
    for left, right, middle in directed:
        assert (right, left, middle) in directed
        assert (left, right) != (right, left)
