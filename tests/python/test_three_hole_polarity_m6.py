"""Exact finite checks for the nonprincipal HolePolarityM6 member.

The matching and permutation checks are symbolic/exhaustive.  The rational
reciprocal check is supplementary sample evidence and is not the proof of the
projective identity.
"""

from fractions import Fraction
from itertools import permutations


PORTS = ("h1+", "h1-", "h2+", "h2-", "h3+", "h3-")


def matching(*edges: tuple[str, str]) -> frozenset[frozenset[str]]:
    return frozenset(frozenset(edge) for edge in edges)


KAPPA = matching(("h1+", "h1-"), ("h2+", "h2-"), ("h3+", "h3-"))
TAU_PLUS = matching(("h1+", "h2-"), ("h2+", "h3-"), ("h3+", "h1-"))
TAU_MINUS = matching(("h1+", "h3-"), ("h3+", "h2-"), ("h2+", "h1-"))


def image(
    edges: frozenset[frozenset[str]], transform: dict[str, str]
) -> frozenset[frozenset[str]]:
    return frozenset(
        frozenset(transform[port] for port in edge) for edge in edges
    )


def compose(left: dict[str, str], right: dict[str, str]) -> dict[str, str]:
    return {port: left[right[port]] for port in PORTS}


def is_identity(transform: dict[str, str]) -> bool:
    return all(transform[port] == port for port in PORTS)


def hole_flip(*holes: int) -> dict[str, str]:
    selected = set(holes)
    return {
        f"h{hole}{sign}": f"h{hole}{'-' if sign == '+' else '+'}"
        if hole in selected
        else f"h{hole}{sign}"
        for hole in (1, 2, 3)
        for sign in ("+", "-")
    }


def hole_swap(left: int, right: int) -> dict[str, str]:
    hole_image = {1: 1, 2: 2, 3: 3}
    hole_image[left], hole_image[right] = right, left
    return {
        f"h{hole}{sign}": f"h{hole_image[hole]}{sign}"
        for hole in (1, 2, 3)
        for sign in ("+", "-")
    }


def permutation_key(transform: dict[str, str]) -> tuple[str, ...]:
    return tuple(transform[port] for port in PORTS)


def test_symbolic_global_hole_polarity_flip_conjugates_threadings() -> None:
    global_flip = hole_flip(1, 2, 3)

    assert image(KAPPA, global_flip) == KAPPA
    assert image(TAU_PLUS, global_flip) == TAU_MINUS
    assert is_identity(compose(global_flip, global_flip))


def test_symbolic_no_single_or_double_hole_flip_conjugates_threadings() -> None:
    for holes in ((1,), (2,), (3,), (1, 2), (1, 3), (2, 3)):
        assert image(TAU_PLUS, hole_flip(*holes)) != TAU_MINUS


def test_exhaustive_symbolic_port_permutation_classification() -> None:
    kappa_preserving = []
    conjugating = []
    involutive_conjugating = []

    for outputs in permutations(PORTS):
        transform = dict(zip(PORTS, outputs, strict=True))
        if image(KAPPA, transform) != KAPPA:
            continue
        kappa_preserving.append(transform)
        if image(TAU_PLUS, transform) != TAU_MINUS:
            continue
        conjugating.append(transform)
        if is_identity(compose(transform, transform)):
            involutive_conjugating.append(transform)

    assert len(kappa_preserving) == 48
    assert len(conjugating) == 6
    assert len(involutive_conjugating) == 4
    assert {permutation_key(transform) for transform in involutive_conjugating} == {
        permutation_key(hole_flip(1, 2, 3)),
        permutation_key(hole_swap(1, 2)),
        permutation_key(hole_swap(1, 3)),
        permutation_key(hole_swap(2, 3)),
    }


def test_symbolic_linear_j_square_is_minus_identity() -> None:
    j = ((0, -1), (1, 0))
    square = tuple(
        tuple(sum(j[row][k] * j[k][column] for k in range(2)) for column in range(2))
        for row in range(2)
    )

    assert square == ((-1, 0), (0, -1))


def test_sample_exact_rational_reciprocal_round_trip() -> None:
    """Supplementary exact samples; the symbolic matrix test is the proof."""

    def reciprocal_switch(value: Fraction) -> Fraction:
        return -1 / value

    for value in map(Fraction, (-3, -2, -1, 1, 2, 3)):
        assert reciprocal_switch(reciprocal_switch(value)) == value
