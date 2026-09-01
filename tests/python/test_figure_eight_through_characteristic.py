"""Exact research oracle for a figure-eight closed-through characteristic.

This fixture is pure Python.  It creates no Adva semantic authority and does
not promote a knot, Laurent polynomial, Fox derivative, or AEG word operation
to the stable Rust surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True, slots=True)
class Laurent:
    """A tiny exact element of Z[t, t^-1] used only by this fixture."""

    terms: tuple[tuple[int, int], ...]

    @classmethod
    def from_dict(cls, terms: dict[int, int]) -> Laurent:
        return cls(
            tuple(sorted((power, coeff) for power, coeff in terms.items() if coeff))
        )

    @classmethod
    def monomial(cls, power: int, coeff: int = 1) -> Laurent:
        return cls.from_dict({power: coeff})

    def as_dict(self) -> dict[int, int]:
        return dict(self.terms)

    def __add__(self, other: Laurent) -> Laurent:
        result = self.as_dict()
        for power, coeff in other.terms:
            result[power] = result.get(power, 0) + coeff
        return Laurent.from_dict(result)

    def __neg__(self) -> Laurent:
        return Laurent(tuple((power, -coeff) for power, coeff in self.terms))

    def __sub__(self, other: Laurent) -> Laurent:
        return self + -other

    def shift(self, power: int) -> Laurent:
        return Laurent(tuple((degree + power, coeff) for degree, coeff in self.terms))

    def dual(self) -> Laurent:
        """Apply the deck-character involution t -> t^-1."""

        return Laurent.from_dict({-power: coeff for power, coeff in self.terms})

    def canonical_associate(self) -> Laurent:
        """Quotient only by the declared Alexander units +/- t^k."""

        if not self.terms:
            return self
        shifted = self.shift(-self.terms[0][0])
        sign = 1 if shifted.terms[-1][1] > 0 else -1
        return shifted if sign == 1 else -shifted


ZERO = Laurent(())
ONE = Laurent.monomial(0)
T = Laurent.monomial(1)
FIGURE_EIGHT_DELTA = Laurent.from_dict({2: 1, 1: -3, 0: 1})
FIGURE_EIGHT_RELATOR = "abbbaBAAB"


@dataclass(frozen=True, slots=True)
class AffinePath:
    """The exact Laurent affine map x |-> t^slope_power x + translation."""

    slope_power: int
    translation: Laurent


def aeg_affine_path(word: str) -> AffinePath:
    """Evaluate AEG letters as operators, with the rightmost acting first."""

    slope_power = 0
    translation = ZERO
    for letter in reversed(word):
        if letter == "a":
            slope_power += 1
            translation = translation.shift(1)
        elif letter == "A":
            slope_power -= 1
            translation = translation.shift(-1)
        elif letter == "b":
            translation += ONE
        elif letter == "B":
            translation -= ONE
        else:
            raise ValueError(f"unknown AEG letter: {letter!r}")
    return AffinePath(slope_power, translation)


def fox_db_after_abelianization(word: str) -> Laurent:
    """Compute phi(partial word / partial b) for phi(a)=t and phi(b)=1."""

    prefix_a_power = 0
    derivative = ZERO
    for letter in word:
        if letter == "b":
            derivative += Laurent.monomial(prefix_a_power)
        elif letter == "B":
            derivative -= Laurent.monomial(prefix_a_power)

        if letter == "a":
            prefix_a_power += 1
        elif letter == "A":
            prefix_a_power -= 1
        elif letter not in {"b", "B"}:
            raise ValueError(f"unknown free-group letter: {letter!r}")
    return derivative


def two_by_two_characteristic(
    matrix: tuple[tuple[int, int], tuple[int, int]],
) -> Laurent:
    """Return det(tI-M) exactly."""

    (a, b), (c, d) = matrix
    return Laurent.from_dict({2: 1, 1: -(a + d), 0: a * d - b * c})


def cyclic_rotations(word: str) -> tuple[str, ...]:
    return tuple(word[index:] + word[:index] for index in range(len(word)))


def test_figure_eight_has_one_characteristic_in_three_exact_readings() -> None:
    path = aeg_affine_path(FIGURE_EIGHT_RELATOR)
    fox_residual = fox_db_after_abelianization(FIGURE_EIGHT_RELATOR)
    monodromy_characteristic = two_by_two_characteristic(((2, 1), (1, 1)))

    assert path.slope_power == 0
    assert path.translation == -FIGURE_EIGHT_DELTA
    assert fox_residual == path.translation
    assert monodromy_characteristic == FIGURE_EIGHT_DELTA
    assert (-fox_residual).canonical_associate() == monodromy_characteristic


def test_duality_exchanges_the_two_closure_characters_but_preserves_feature() -> None:
    dual = FIGURE_EIGHT_DELTA.dual()
    assert dual.canonical_associate() == FIGURE_EIGHT_DELTA

    root_minus = (3 - sqrt(5)) / 2
    root_plus = (3 + sqrt(5)) / 2
    assert abs(root_minus * root_plus - 1.0) < 1e-12
    assert abs(root_plus - 1.0 / root_minus) < 1e-12


def test_cyclic_basepoint_change_keeps_only_an_alexander_unit_residual() -> None:
    residuals = tuple(
        aeg_affine_path(word).translation
        for word in cyclic_rotations(FIGURE_EIGHT_RELATOR)
    )
    assert len(set(residuals)) > 1
    assert {
        residual.canonical_associate() for residual in residuals
    } == {FIGURE_EIGHT_DELTA}


def test_letter_counts_do_not_determine_the_feature() -> None:
    shuffled = "aaAAbbbBB"
    assert sorted(shuffled) == sorted(FIGURE_EIGHT_RELATOR)
    assert aeg_affine_path(shuffled).slope_power == 0
    assert aeg_affine_path(shuffled).translation == ONE
    assert (
        aeg_affine_path(shuffled).translation.canonical_associate()
        != FIGURE_EIGHT_DELTA
    )


def test_open_or_malformed_words_are_not_silently_promoted_to_closed_threads() -> None:
    assert aeg_affine_path("ab").slope_power != 0

    try:
        aeg_affine_path("ab?")
    except ValueError as error:
        assert "unknown AEG letter" in str(error)
    else:
        raise AssertionError("an untyped crossing letter must be rejected")
