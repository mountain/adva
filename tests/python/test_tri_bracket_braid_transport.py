from __future__ import annotations

from itertools import product
from typing import TypeAlias


BraidWord: TypeAlias = tuple[int, ...]
FreeWord: TypeAlias = tuple[int, ...]
FreeAutomorphism: TypeAlias = tuple[FreeWord, FreeWord, FreeWord]
Boundary: TypeAlias = tuple[str, ...]
FiniteMap: TypeAlias = tuple[int, ...]

COLORS: Boundary = ("K", "X", "t")
GLYPHS = {"{}": "K", "[]": "X", "()": "t"}
FREE_IDENTITY: FreeAutomorphism = ((1,), (2,), (3,))
PAIR_ORDER = (("K", "X"), ("K", "t"), ("X", "t"))


def _parse_flat_boundary(source: str) -> Boundary:
    """Parse only juxtaposed empty pairs; no pair may contain another."""

    if len(source) % 2:
        raise ValueError("a flat boundary is a word of two-character empty pairs")
    try:
        return tuple(GLYPHS[source[offset : offset + 2]] for offset in range(0, len(source), 2))
    except KeyError as error:
        raise ValueError(
            "mixed, nested, or nonempty brackets are outside the flat grammar"
        ) from error


def _endpoint_boundary(boundary: Boundary, word: BraidWord) -> Boundary:
    result = list(boundary)
    for letter in word:
        index = abs(letter) - 1
        if index not in (0, 1):
            raise ValueError(f"B_3 has only sigma_1 and sigma_2, not {letter}")
        result[index], result[index + 1] = result[index + 1], result[index]
    return tuple(result)


def _reduce_free(word: FreeWord) -> FreeWord:
    result: list[int] = []
    for letter in word:
        if letter == 0 or abs(letter) > 3:
            raise ValueError(f"invalid F_3 generator {letter}")
        if result and result[-1] == -letter:
            result.pop()
        else:
            result.append(letter)
    return tuple(result)


def _inverse_free(word: FreeWord) -> FreeWord:
    return tuple(-letter for letter in reversed(word))


def _substitute(word: FreeWord, images: FreeAutomorphism) -> FreeWord:
    expanded: list[int] = []
    for letter in word:
        image = images[abs(letter) - 1]
        expanded.extend(image if letter > 0 else _inverse_free(image))
    return _reduce_free(tuple(expanded))


def _compose(after: FreeAutomorphism, before: FreeAutomorphism) -> FreeAutomorphism:
    """Return after o before as exact reduced words in the free group F_3."""

    return tuple(_substitute(image, after) for image in before)  # type: ignore[return-value]


def _artin_generator(letter: int) -> FreeAutomorphism:
    index = abs(letter) - 1
    if index not in (0, 1):
        raise ValueError(f"B_3 has only sigma_1 and sigma_2, not {letter}")
    left = index + 1
    right = index + 2
    images = list(FREE_IDENTITY)
    if letter > 0:
        images[index] = (left, right, -left)
        images[index + 1] = (left,)
    else:
        images[index] = (right,)
        images[index + 1] = (-right, left, right)
    return tuple(images)  # type: ignore[return-value]


def _artin_action(word: BraidWord) -> FreeAutomorphism:
    """Execute crossings left to right using Artin's faithful B_3 action on F_3."""

    result = FREE_IDENTITY
    for letter in word:
        result = _compose(_artin_generator(letter), result)
    return result


def _inverse_braid(word: BraidWord) -> BraidWord:
    return tuple(-letter for letter in reversed(word))


def _pair_crossing_counts(boundary: Boundary, word: BraidWord) -> dict[tuple[str, str], int]:
    positions = list(boundary)
    counts = {tuple(sorted(pair)): 0 for pair in PAIR_ORDER}
    for letter in word:
        index = abs(letter) - 1
        pair = tuple(sorted((positions[index], positions[index + 1])))
        counts[pair] += 1 if letter > 0 else -1
        positions[index], positions[index + 1] = positions[index + 1], positions[index]
    return counts


def _opposite_pair_windings(word: BraidWord) -> dict[str, int]:
    if _endpoint_boundary(COLORS, word) != COLORS:
        raise ValueError("pair windings are integral only for a pure fixed-boundary braid")
    counts = _pair_crossing_counts(COLORS, word)
    if any(count % 2 for count in counts.values()):
        raise AssertionError("a pure braid has even signed crossing count for every labelled pair")
    return {
        "t": counts[("K", "X")] // 2,
        "X": counts[("K", "t")] // 2,
        "K": counts[("X", "t")] // 2,
    }


def _multiply_2x2(
    left: tuple[tuple[int, int], tuple[int, int]],
    right: tuple[tuple[int, int], tuple[int, int]],
) -> tuple[tuple[int, int], tuple[int, int]]:
    return (
        (
            left[0][0] * right[0][0] + left[0][1] * right[1][0],
            left[0][0] * right[0][1] + left[0][1] * right[1][1],
        ),
        (
            left[1][0] * right[0][0] + left[1][1] * right[1][0],
            left[1][0] * right[0][1] + left[1][1] * right[1][1],
        ),
    )


def _matrix_power(
    matrix: tuple[tuple[int, int], tuple[int, int]],
    exponent: int,
) -> tuple[tuple[int, int], tuple[int, int]]:
    result = ((1, 0), (0, 1))
    for _ in range(exponent):
        result = _multiply_2x2(result, matrix)
    return result


def _compose_finite(after: FiniteMap, before: FiniteMap) -> FiniteMap:
    return tuple(after[value] for value in before)


def test_three_typed_vacua_form_one_flat_fixed_boundary() -> None:
    omega = _parse_flat_boundary("{}[]()")

    assert _parse_flat_boundary("") == ()
    assert omega == COLORS
    assert omega != ()
    assert _parse_flat_boundary("[](){}") == ("X", "t", "K")

    for invalid in ("{[]}", "[()]", "({})", "{{}}", "{x}[]()", "{}[]("):
        try:
            _parse_flat_boundary(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"the flat grammar accepted {invalid!r}")


def test_colored_crossings_form_a_groupoid_and_pure_braids_preserve_omega() -> None:
    sigma_1 = (1,)
    sigma_2 = (2,)
    rotation = sigma_1 + sigma_2

    assert _endpoint_boundary(COLORS, sigma_1) == ("X", "K", "t")
    assert _endpoint_boundary(COLORS, rotation) == ("X", "t", "K")
    assert _endpoint_boundary(COLORS, rotation * 3) == COLORS

    a_12 = sigma_1 * 2
    a_23 = sigma_2 * 2
    a_13 = sigma_2 + sigma_1 * 2 + (-2,)
    assert all(_endpoint_boundary(COLORS, pure) == COLORS for pure in (a_12, a_13, a_23))


def test_artin_action_checks_the_braid_relation_and_inverses_exactly() -> None:
    sigma_1 = (1,)
    sigma_2 = (2,)
    left = sigma_1 + sigma_2 + sigma_1
    right = sigma_2 + sigma_1 + sigma_2

    assert _artin_action(left) == _artin_action(right)
    assert _endpoint_boundary(COLORS, (1,)) == _endpoint_boundary(COLORS, (-1,))
    assert _artin_action((1,)) != _artin_action((-1,))
    for word in (sigma_1, sigma_2, left, sigma_1 + (-2, 1, 2)):
        assert _artin_action(word + _inverse_braid(word)) == FREE_IDENTITY
        assert _artin_action(_inverse_braid(word) + word) == FREE_IDENTITY


def test_three_rotations_close_on_colors_but_leave_a_central_full_twist() -> None:
    sigma_1 = (1,)
    sigma_2 = (2,)
    rotation = sigma_1 + sigma_2
    delta = sigma_1 + sigma_2 + sigma_1
    full_twist = rotation * 3

    assert _endpoint_boundary(COLORS, full_twist) == COLORS
    assert _artin_action(full_twist) == _artin_action(delta * 2)
    assert _artin_action(full_twist) != FREE_IDENTITY
    assert _artin_action(full_twist + sigma_1) == _artin_action(sigma_1 + full_twist)
    assert _artin_action(full_twist + sigma_2) == _artin_action(sigma_2 + full_twist)


def test_projective_shadow_forgets_the_nontrivial_central_lift() -> None:
    sigma_1 = ((1, 1), (0, 1))
    sigma_2 = ((1, 0), (-1, 1))
    rotation = _multiply_2x2(sigma_1, sigma_2)
    negative_identity = ((-1, 0), (0, -1))

    assert _multiply_2x2(
        _multiply_2x2(sigma_1, sigma_2), sigma_1
    ) == _multiply_2x2(_multiply_2x2(sigma_2, sigma_1), sigma_2)
    assert _matrix_power(rotation, 3) == negative_identity
    assert _artin_action((1, 2) * 3) != FREE_IDENTITY


def test_opposite_pair_windings_are_complete_only_after_abelianization() -> None:
    sigma_1 = (1,)
    sigma_2 = (2,)
    a_12 = sigma_1 * 2
    a_23 = sigma_2 * 2
    a_13 = sigma_2 + sigma_1 * 2 + (-2,)

    assert _opposite_pair_windings(a_12) == {"t": 1, "X": 0, "K": 0}
    assert _opposite_pair_windings(a_13) == {"t": 0, "X": 1, "K": 0}
    assert _opposite_pair_windings(a_23) == {"t": 0, "X": 0, "K": 1}

    left_schedule = a_12 + a_23
    right_schedule = a_23 + a_12
    assert _opposite_pair_windings(left_schedule) == _opposite_pair_windings(right_schedule)
    assert _artin_action(left_schedule) != _artin_action(right_schedule)

    commutator = a_12 + a_23 + _inverse_braid(a_12) + _inverse_braid(a_23)
    assert _opposite_pair_windings(commutator) == {"t": 0, "X": 0, "K": 0}
    assert _artin_action(commutator) != FREE_IDENTITY


def test_equal_nonzero_pair_shadows_do_not_detect_centrality() -> None:
    full_twist = (1, 2) * 3
    a_12 = (1, 1)
    a_23 = (2, 2)
    a_13 = (2, 1, 1, -2)
    noncentral = a_12 + a_23 + a_13

    assert _opposite_pair_windings(full_twist) == {"t": 1, "X": 1, "K": 1}
    assert _opposite_pair_windings(noncentral) == {"t": 1, "X": 1, "K": 1}
    assert _artin_action(full_twist) != _artin_action(noncentral)
    assert _artin_action(full_twist + (1,)) == _artin_action((1,) + full_twist)
    assert _artin_action(noncentral + (1,)) != _artin_action((1,) + noncentral)


def test_invertible_braid_transport_cannot_realize_nontrivial_idempotents() -> None:
    identity = tuple(range(8))

    def temporal_open(index: int) -> int:
        t, x, k = ((index >> 2) & 1, (index >> 1) & 1, index & 1)
        return (1 << 2) | (x << 1) | k

    def spatial_write(index: int) -> int:
        t, _, k = ((index >> 2) & 1, (index >> 1) & 1, index & 1)
        return (t << 2) | ((t & k) << 1) | k

    temporal = tuple(temporal_open(index) for index in identity)
    spatial = tuple(spatial_write(index) for index in identity)

    assert temporal != identity
    assert spatial != identity
    assert _compose_finite(temporal, temporal) == temporal
    assert _compose_finite(spatial, spatial) == spatial
    assert len(set(temporal)) == 4
    assert len(set(spatial)) == 4

    # Every Artin action is an automorphism.  In any group action, e^2 = e
    # implies e = identity by cancellation.  The bounded enumeration below is
    # an executable regression witness for this general algebraic no-go.
    actions = {
        _artin_action(word)
        for length in range(6)
        for word in product((-2, -1, 1, 2), repeat=length)
    }
    assert all(
        action == FREE_IDENTITY
        for action in actions
        if _compose(action, action) == action
    )
