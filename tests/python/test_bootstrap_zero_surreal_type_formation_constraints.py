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


class ArithmeticSign(Enum):
    NEGATE = "neg"


@dataclass(frozen=True)
class Var:
    name: str


@dataclass(frozen=True)
class Add:
    left: Term
    right: Term


@dataclass(frozen=True)
class Mul:
    left: Term
    right: Term


@dataclass(frozen=True)
class Neg:
    value: Term


Term: TypeAlias = Var | Add | Mul | Neg
RankPair: TypeAlias = tuple[int, int]


@dataclass(frozen=True)
class Option:
    term: Term
    side: OptionSide


@dataclass(frozen=True)
class OperationSignature:
    operations: frozenset[str]


@dataclass(frozen=True)
class Port:
    incidence: str
    source: str
    occurrence: str
    value_type: str


def _add_kernel(left: Term, right: Term) -> Term:
    return Add(left, right)


def _product_kernel(a: Term, x: Term, b: Term, y: Term) -> Term:
    return Add(Add(Mul(a, y), Mul(x, b)), Neg(Mul(a, b)))


def _sum_options(
    x: Var,
    x_left: Var,
    x_right: Var,
    y: Var,
    y_left: Var,
    y_right: Var,
) -> tuple[Option, ...]:
    return (
        Option(_add_kernel(x_left, y), OptionSide.LEFT),
        Option(_add_kernel(x, y_left), OptionSide.LEFT),
        Option(_add_kernel(x_right, y), OptionSide.RIGHT),
        Option(_add_kernel(x, y_right), OptionSide.RIGHT),
    )


def _product_side(left: OptionSide, right: OptionSide) -> OptionSide:
    if left is right:
        return OptionSide.LEFT
    return OptionSide.RIGHT


def _product_options(
    x: Var,
    x_left: Var,
    x_right: Var,
    y: Var,
    y_left: Var,
    y_right: Var,
) -> tuple[Option, ...]:
    option_pairs = (
        (x_left, OptionSide.LEFT, y_left, OptionSide.LEFT),
        (x_right, OptionSide.RIGHT, y_right, OptionSide.RIGHT),
        (x_left, OptionSide.LEFT, y_right, OptionSide.RIGHT),
        (x_right, OptionSide.RIGHT, y_left, OptionSide.LEFT),
    )
    return tuple(
        Option(
            _product_kernel(x_option, x, y_option, y),
            _product_side(x_side, y_side),
        )
        for x_option, x_side, y_option, y_side in option_pairs
    )


def _variables(term: Term) -> tuple[str, ...]:
    if isinstance(term, Var):
        return (term.name,)
    if isinstance(term, Neg):
        return _variables(term.value)
    return _variables(term.left) + _variables(term.right)


def _precedes(child: RankPair, parent: RankPair) -> bool:
    return (
        child[0] <= parent[0]
        and child[1] <= parent[1]
        and child != parent
    )


def _product_recursive_calls(
    x_option_rank: int,
    x_rank: int,
    y_option_rank: int,
    y_rank: int,
) -> tuple[RankPair, ...]:
    return (
        (x_option_rank, y_rank),
        (x_rank, y_option_rank),
        (x_option_rank, y_option_rank),
    )


def _route_adjacent(frontier: tuple[Port, ...], gap: int) -> tuple[Port, ...]:
    left = gap - 1
    right = gap
    if left < 0 or right >= len(frontier):
        raise ValueError("the gap must select two adjacent ports")
    result = list(frontier)
    result[left], result[right] = result[right], result[left]
    return tuple(result)


def _can_form_sum(signature: OperationSignature) -> bool:
    return {"add"} <= signature.operations


def _can_form_product(signature: OperationSignature) -> bool:
    return {"add", "mul", "neg"} <= signature.operations


def test_sum_schema_has_two_options_on_each_side() -> None:
    x, x_left, x_right = Var("x"), Var("xL"), Var("xR")
    y, y_left, y_right = Var("y"), Var("yL"), Var("yR")
    options = _sum_options(x, x_left, x_right, y, y_left, y_right)

    assert tuple(option.side for option in options) == (
        OptionSide.LEFT,
        OptionSide.LEFT,
        OptionSide.RIGHT,
        OptionSide.RIGHT,
    )
    assert tuple(option.term for option in options) == (
        Add(x_left, y),
        Add(x, y_left),
        Add(x_right, y),
        Add(x, y_right),
    )


def test_sum_schema_changes_one_operand_option_at_a_time() -> None:
    x, x_left, x_right = Var("x"), Var("xL"), Var("xR")
    y, y_left, y_right = Var("y"), Var("yL"), Var("yR")

    for option in _sum_options(x, x_left, x_right, y, y_left, y_right):
        names = set(_variables(option.term))
        changed_x = bool(names & {"xL", "xR"})
        changed_y = bool(names & {"yL", "yR"})
        assert changed_x is not changed_y


def test_product_schema_has_the_four_standard_option_kernels() -> None:
    x, x_left, x_right = Var("x"), Var("xL"), Var("xR")
    y, y_left, y_right = Var("y"), Var("yL"), Var("yR")
    options = _product_options(x, x_left, x_right, y, y_left, y_right)

    assert tuple(option.term for option in options) == (
        _product_kernel(x_left, x, y_left, y),
        _product_kernel(x_right, x, y_right, y),
        _product_kernel(x_left, x, y_right, y),
        _product_kernel(x_right, x, y_left, y),
    )


def test_product_side_is_symmetric_option_polarity_parity() -> None:
    assert _product_side(OptionSide.LEFT, OptionSide.LEFT) is OptionSide.LEFT
    assert _product_side(OptionSide.RIGHT, OptionSide.RIGHT) is OptionSide.LEFT
    assert _product_side(OptionSide.LEFT, OptionSide.RIGHT) is OptionSide.RIGHT
    assert _product_side(OptionSide.RIGHT, OptionSide.LEFT) is OptionSide.RIGHT
    for left in OptionSide:
        for right in OptionSide:
            assert _product_side(left, right) is _product_side(right, left)


def test_recursive_sum_and_product_calls_strictly_precede_the_parent() -> None:
    parent = (5, 7)
    sum_calls = ((4, 7), (5, 6))
    product_calls = _product_recursive_calls(4, 5, 6, 7)

    assert all(_precedes(call, parent) for call in sum_calls)
    assert all(_precedes(call, parent) for call in product_calls)


def test_product_kernel_requires_repeated_option_occurrences() -> None:
    kernel = _product_kernel(Var("a"), Var("x"), Var("b"), Var("y"))

    assert Counter(_variables(kernel)) == Counter(
        {"a": 2, "x": 1, "b": 2, "y": 1}
    )


def test_routing_preserves_ports_and_cannot_supply_product_copies() -> None:
    frontier = (
        Port("ia", "a", "oa", "A"),
        Port("ix", "x", "ox", "A"),
        Port("ib", "b", "ob", "A"),
        Port("iy", "y", "oy", "A"),
    )
    routed = _route_adjacent(_route_adjacent(frontier, 1), 3)

    assert Counter(port.source for port in routed) == Counter(
        port.source for port in frontier
    )
    assert set(routed) == set(frontier)
    assert Counter(port.source for port in routed) != Counter(
        {"a": 2, "x": 1, "b": 2, "y": 1}
    )


def test_four_different_orientation_alphabets_remain_disjoint() -> None:
    alphabets = (
        {item.value for item in OptionSide},
        {item.value for item in IncidencePolarity},
        {item.value for item in CrossingSign},
        {item.value for item in ArithmeticSign},
    )

    for index, alphabet in enumerate(alphabets):
        for other in alphabets[index + 1 :]:
            assert alphabet.isdisjoint(other)


def test_product_formation_requires_typed_negation_capability() -> None:
    additive = OperationSignature(frozenset({"add"}))
    positive_semiring = OperationSignature(frozenset({"add", "mul"}))
    signed_ring_fragment = OperationSignature(frozenset({"add", "mul", "neg"}))

    assert _can_form_sum(additive)
    assert not _can_form_product(additive)
    assert not _can_form_product(positive_semiring)
    assert _can_form_product(signed_ring_fragment)


def test_same_arithmetic_spelling_under_swap_is_not_raw_syntax_equality() -> None:
    x = Var("x")
    y = Var("y")

    assert Add(x, y) != Add(y, x)
    assert Mul(x, y) != Mul(y, x)


def test_self_dependency_fails_the_finite_predecessor_check() -> None:
    omega_rank = (3, 3)

    assert not _precedes(omega_rank, omega_rank)
