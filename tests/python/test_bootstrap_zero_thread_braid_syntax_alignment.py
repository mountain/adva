from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Literal, TypeAlias

import pytest


Domain: TypeAlias = Literal["K", "X", "t"]


class IncidencePolarity(Enum):
    POSITIVE = "+"
    NEGATIVE = "-"


class CrossingSign(Enum):
    OVER = "over"
    UNDER = "under"


@dataclass(frozen=True)
class Incidence:
    name: str
    value_type: str
    source: str
    occurrence: str
    role: Domain
    polarity: IncidencePolarity


@dataclass(frozen=True)
class Crossing:
    name: str
    gap: int
    sign: CrossingSign


@dataclass(frozen=True)
class FunctionAtom:
    name: str


@dataclass(frozen=True)
class ThroughType:
    left_role: Domain
    right_role: Domain
    middle_role: Domain


Frontier: TypeAlias = tuple[Incidence, ...]
BraidWord: TypeAlias = tuple[Crossing, ...]
ThreadAtom: TypeAlias = Crossing | FunctionAtom
ThreadWord: TypeAlias = tuple[ThreadAtom, ...]
PresentedBlock: TypeAlias = tuple[str, object]


PUBLIC_FRONTIER: Frontier = (
    Incidence("iK", "Real", "sK", "oK", "K", IncidencePolarity.POSITIVE),
    Incidence("iX", "Real", "sX", "oX", "X", IncidencePolarity.NEGATIVE),
    Incidence("it", "Real", "st", "ot", "t", IncidencePolarity.POSITIVE),
)


def _crossing(name: str, gap: int, sign: CrossingSign) -> Crossing:
    return Crossing(name=name, gap=gap, sign=sign)


def _route_crossing(frontier: Frontier, crossing: Crossing) -> Frontier:
    left_index = crossing.gap - 1
    right_index = crossing.gap
    if left_index < 0 or right_index >= len(frontier):
        raise ValueError("a crossing gap must select two adjacent incidences")

    routed = list(frontier)
    routed[left_index], routed[right_index] = (
        routed[right_index],
        routed[left_index],
    )
    return tuple(routed)


def _route_braid(frontier: Frontier, word: BraidWord) -> Frontier:
    routed = frontier
    for crossing in word:
        routed = _route_crossing(routed, crossing)
    return routed


def _flip(sign: CrossingSign) -> CrossingSign:
    if sign is CrossingSign.OVER:
        return CrossingSign.UNDER
    return CrossingSign.OVER


def _formal_inverse(word: BraidWord) -> BraidWord:
    return tuple(
        Crossing(crossing.name, crossing.gap, _flip(crossing.sign))
        for crossing in reversed(word)
    )


def _braid_blocks(word: ThreadWord) -> tuple[PresentedBlock, ...]:
    blocks: list[PresentedBlock] = []
    braid: list[Crossing] = []

    def flush() -> None:
        if braid:
            blocks.append(("braid", tuple(braid)))
            braid.clear()

    for atom in word:
        if isinstance(atom, Crossing):
            braid.append(atom)
        else:
            flush()
            blocks.append(("function", atom))
    flush()
    return tuple(blocks)


def _opposite(left: Domain, right: Domain) -> Domain:
    if left == right:
        raise ValueError("an opposite role needs two distinct endpoint roles")
    remaining = {"K", "X", "t"} - {left, right}
    assert len(remaining) == 1
    return remaining.pop()  # type: ignore[return-value]


def _roles(frontier: Frontier) -> tuple[Domain, ...]:
    return tuple(incidence.role for incidence in frontier)


def test_signed_crossings_have_one_routing_and_two_raw_spellings() -> None:
    over = _crossing("x1-over", 1, CrossingSign.OVER)
    under = _crossing("x1-under", 1, CrossingSign.UNDER)

    assert over != under
    assert _route_crossing(PUBLIC_FRONTIER, over) == _route_crossing(
        PUBLIC_FRONTIER,
        under,
    )
    assert _roles(_route_crossing(PUBLIC_FRONTIER, over)) == ("X", "K", "t")


def test_crossing_moves_complete_incidence_records() -> None:
    crossing = _crossing("x2", 2, CrossingSign.OVER)
    routed = _route_crossing(PUBLIC_FRONTIER, crossing)

    assert routed == (PUBLIC_FRONTIER[0], PUBLIC_FRONTIER[2], PUBLIC_FRONTIER[1])
    assert routed[1] is PUBLIC_FRONTIER[2]
    assert routed[2] is PUBLIC_FRONTIER[1]
    assert {item.source for item in routed} == {"sK", "sX", "st"}
    assert {item.occurrence for item in routed} == {"oK", "oX", "ot"}


def test_invalid_crossing_gap_is_rejected_by_formation() -> None:
    with pytest.raises(ValueError, match="two adjacent incidences"):
        _route_crossing(
            PUBLIC_FRONTIER,
            _crossing("x0", 0, CrossingSign.OVER),
        )
    with pytest.raises(ValueError, match="two adjacent incidences"):
        _route_crossing(
            PUBLIC_FRONTIER,
            _crossing("x3", 3, CrossingSign.OVER),
        )


def test_elementary_crossings_are_not_public_boundary_endomorphisms() -> None:
    sigma_1 = (_crossing("sigma-1", 1, CrossingSign.OVER),)
    sigma_2 = (_crossing("sigma-2", 2, CrossingSign.OVER),)

    assert _roles(_route_braid(PUBLIC_FRONTIER, sigma_1)) == ("X", "K", "t")
    assert _roles(_route_braid(PUBLIC_FRONTIER, sigma_2)) == ("K", "t", "X")
    assert _route_braid(PUBLIC_FRONTIER, sigma_1) != PUBLIC_FRONTIER
    assert _route_braid(PUBLIC_FRONTIER, sigma_2) != PUBLIC_FRONTIER


def test_endpoint_return_does_not_make_a_braid_word_empty() -> None:
    sigma_1 = _crossing("sigma-1", 1, CrossingSign.OVER)
    sigma_2 = _crossing("sigma-2", 2, CrossingSign.OVER)
    pure_pair = (sigma_1, sigma_1)
    full_twist = (sigma_1, sigma_2) * 3

    assert _route_braid(PUBLIC_FRONTIER, pure_pair) == PUBLIC_FRONTIER
    assert _route_braid(PUBLIC_FRONTIER, full_twist) == PUBLIC_FRONTIER
    assert pure_pair
    assert full_twist
    assert pure_pair != ()
    assert full_twist != ()


def test_formal_inverse_restores_routing_without_creating_word_equality() -> None:
    word = (
        _crossing("x1", 1, CrossingSign.OVER),
        _crossing("x2", 2, CrossingSign.UNDER),
        _crossing("x3", 1, CrossingSign.OVER),
    )
    inverse = _formal_inverse(word)

    assert inverse == (
        _crossing("x3", 1, CrossingSign.UNDER),
        _crossing("x2", 2, CrossingSign.OVER),
        _crossing("x1", 1, CrossingSign.UNDER),
    )
    assert _route_braid(PUBLIC_FRONTIER, word + inverse) == PUBLIC_FRONTIER
    assert word + inverse != ()


def test_braid_relation_paths_remain_distinct_raw_words() -> None:
    sigma_1 = _crossing("sigma-1", 1, CrossingSign.OVER)
    sigma_2 = _crossing("sigma-2", 2, CrossingSign.OVER)
    left = (sigma_1, sigma_2, sigma_1)
    right = (sigma_2, sigma_1, sigma_2)

    assert left != right
    assert _route_braid(PUBLIC_FRONTIER, left) == _route_braid(
        PUBLIC_FRONTIER,
        right,
    )
    assert _roles(_route_braid(PUBLIC_FRONTIER, left)) == ("t", "X", "K")


def test_crossing_sign_is_not_incidence_polarity_or_through_direction() -> None:
    through = ThroughType("K", "X", _opposite("K", "X"))
    reverse = ThroughType("X", "K", _opposite("X", "K"))

    assert through.middle_role == reverse.middle_role == "t"
    assert through != reverse
    assert CrossingSign.OVER.value not in {
        polarity.value for polarity in IncidencePolarity
    }
    assert CrossingSign.UNDER.value not in {
        polarity.value for polarity in IncidencePolarity
    }


def test_mixed_thread_word_retains_braid_blocks_and_function_separators() -> None:
    sigma_1 = _crossing("sigma-1", 1, CrossingSign.OVER)
    sigma_2_inverse = _crossing("sigma-2", 2, CrossingSign.UNDER)
    gate = FunctionAtom("spatial-update")
    word: ThreadWord = (sigma_1, sigma_2_inverse, gate, sigma_1)

    assert _braid_blocks(word) == (
        ("braid", (sigma_1, sigma_2_inverse)),
        ("function", gate),
        ("braid", (sigma_1,)),
    )
    assert _braid_blocks((gate, sigma_1)) != _braid_blocks((sigma_1, gate))
