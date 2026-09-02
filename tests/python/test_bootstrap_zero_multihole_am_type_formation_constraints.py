from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias


class OptionSide(Enum):
    LEFT = "L"
    RIGHT = "R"


class IncidencePolarity(Enum):
    POSITIVE = "+"
    NEGATIVE = "-"


class CrossingSign(Enum):
    OVER = "over"
    UNDER = "under"


@dataclass(frozen=True)
class Use:
    source: str
    occurrence: str


@dataclass(frozen=True)
class Atom:
    name: str


@dataclass(frozen=True)
class Add:
    left: Term
    right: Term


@dataclass(frozen=True)
class Mul:
    left: Term
    right: Term


Term: TypeAlias = Atom | Use | Add | Mul


@dataclass(frozen=True)
class Port:
    incidence: str
    source: str
    occurrence: str
    value_type: str


@dataclass(frozen=True)
class OperationSignature:
    operations: frozenset[str]
    atoms: frozenset[str]


@dataclass(frozen=True)
class AlternativeFamily:
    terms: tuple[Term, ...]


@dataclass(frozen=True)
class ConstraintCell:
    left: Term
    right: Term


def _fresh_use(source: str, index: int) -> Use:
    return Use(source, f"{source}-{index}")


def _add_kernel() -> tuple[tuple[str, ...], Term]:
    holes = ("x", "y")
    return holes, Add(_fresh_use("x", 1), _fresh_use("y", 1))


def _product_kernel() -> tuple[tuple[str, ...], Term]:
    holes = ("a", "x", "b", "y")
    a1 = _fresh_use("a", 1)
    a2 = _fresh_use("a", 2)
    x1 = _fresh_use("x", 1)
    b1 = _fresh_use("b", 1)
    b2 = _fresh_use("b", 2)
    y1 = _fresh_use("y", 1)
    term = Add(
        Add(Mul(a1, y1), Mul(x1, b1)),
        Mul(Atom("neg-unit-A"), Mul(a2, b2)),
    )
    return holes, term


def _uses(term: Term) -> tuple[Use, ...]:
    if isinstance(term, Use):
        return (term,)
    if isinstance(term, Atom):
        return ()
    return _uses(term.left) + _uses(term.right)


def _route_adjacent(frontier: tuple[Port, ...], gap: int) -> tuple[Port, ...]:
    left = gap - 1
    right = gap
    if left < 0 or right >= len(frontier):
        raise ValueError("the gap must select two adjacent ports")
    result = list(frontier)
    result[left], result[right] = result[right], result[left]
    return tuple(result)


def _can_form_product(signature: OperationSignature) -> bool:
    return (
        {"add", "mul"} <= signature.operations
        and "neg-unit-A" in signature.atoms
    )


def test_kernels_have_fixed_ordered_hole_boundaries() -> None:
    add_holes, _ = _add_kernel()
    product_holes, _ = _product_kernel()

    assert add_holes == ("x", "y")
    assert add_holes != tuple(reversed(add_holes))
    assert product_holes == ("a", "x", "b", "y")
    assert product_holes != tuple(reversed(product_holes))


def test_product_kernel_has_six_fresh_occurrences_and_four_sources() -> None:
    _, product = _product_kernel()
    uses = _uses(product)

    assert len(uses) == 6
    assert len({use.occurrence for use in uses}) == 6
    assert Counter(use.source for use in uses) == Counter(
        {"a": 2, "x": 1, "b": 2, "y": 1}
    )


def test_common_source_does_not_identify_occurrences() -> None:
    _, product = _product_kernel()
    a_uses = tuple(use for use in _uses(product) if use.source == "a")
    b_uses = tuple(use for use in _uses(product) if use.source == "b")

    assert a_uses[0] != a_uses[1]
    assert b_uses[0] != b_uses[1]


def test_routing_preserves_occurrences_and_cannot_supply_copies() -> None:
    frontier = (
        Port("ia", "a", "a-1", "A"),
        Port("ix", "x", "x-1", "A"),
        Port("ib", "b", "b-1", "A"),
        Port("iy", "y", "y-1", "A"),
    )
    routed = _route_adjacent(_route_adjacent(frontier, 1), 3)

    assert set(routed) == set(frontier)
    assert Counter(port.occurrence for port in routed) == Counter(
        port.occurrence for port in frontier
    )
    assert Counter(port.source for port in routed) != Counter(
        {"a": 2, "x": 1, "b": 2, "y": 1}
    )


def test_negative_unit_atom_is_not_an_orientation_token() -> None:
    alphabets = (
        {item.value for item in OptionSide},
        {item.value for item in IncidencePolarity},
        {item.value for item in CrossingSign},
        {"neg-unit-A"},
    )

    for index, alphabet in enumerate(alphabets):
        for other in alphabets[index + 1 :]:
            assert alphabet.isdisjoint(other)


def test_product_formation_requires_declared_gate_capabilities() -> None:
    additive = OperationSignature(frozenset({"add"}), frozenset())
    gates_only = OperationSignature(frozenset({"add", "mul"}), frozenset())
    complete = OperationSignature(
        frozenset({"add", "mul"}), frozenset({"neg-unit-A"})
    )

    assert not _can_form_product(additive)
    assert not _can_form_product(gates_only)
    assert _can_form_product(complete)


def test_swapped_arguments_are_distinct_raw_terms() -> None:
    x = _fresh_use("x", 1)
    y = _fresh_use("y", 1)

    assert Add(x, y) != Add(y, x)
    assert Mul(x, y) != Mul(y, x)


def test_alternative_family_is_not_an_add_tree() -> None:
    _, add_term = _add_kernel()
    family = AlternativeFamily((add_term, Mul(Atom("neg-unit-A"), add_term)))

    assert isinstance(family, AlternativeFamily)
    assert not isinstance(family, Add)


def test_constraint_cell_retains_both_trees_without_equating_them() -> None:
    _, left = _add_kernel()
    _, right = _product_kernel()
    constraint = ConstraintCell(left, right)

    assert constraint.left is left
    assert constraint.right is right
    assert constraint.left != constraint.right
