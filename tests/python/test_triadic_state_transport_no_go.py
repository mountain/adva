from __future__ import annotations

from collections import Counter, deque
from itertools import product
from typing import Callable


Axis = str
Context = tuple[Axis, ...]
CoreState = tuple[int, int, int]
Transformation = tuple[int, ...]
Proposition = frozenset[int]

AXES: tuple[Axis, ...] = ("T", "X", "K")
CORE_STATES: tuple[CoreState, ...] = tuple(product((0, 1), repeat=3))
CORE_INDEX = {state: index for index, state in enumerate(CORE_STATES)}
IDENTITY: Transformation = tuple(range(len(CORE_STATES)))
ENVELOPE: tuple[Proposition, ...] = tuple(
    frozenset(
        index
        for index in range(len(CORE_STATES))
        if mask & (1 << index)
    )
    for mask in range(1 << len(CORE_STATES))
)


def _core_step(state: CoreState, axis: Axis) -> CoreState:
    temporal, spatial, construction = state
    if axis == "T":
        return (1, spatial, construction)
    if axis == "X":
        return (temporal, temporal & construction, construction)
    if axis == "K":
        return (temporal, spatial, 1 - construction)
    raise ValueError(f"unknown axis: {axis}")


def _generator(axis: Axis) -> Transformation:
    return tuple(CORE_INDEX[_core_step(state, axis)] for state in CORE_STATES)


def _compose(
    first: Transformation,
    second: Transformation,
) -> Transformation:
    """Execute ``first`` and then ``second``."""

    return tuple(second[first[index]] for index in range(len(CORE_STATES)))


def _transformation_monoid() -> dict[Transformation, Context]:
    generators = {axis: _generator(axis) for axis in AXES}
    shortest: dict[Transformation, Context] = {IDENTITY: ()}
    frontier = deque([IDENTITY])
    while frontier:
        transformation = frontier.popleft()
        for axis in AXES:
            candidate = _compose(transformation, generators[axis])
            if candidate not in shortest:
                shortest[candidate] = (*shortest[transformation], axis)
                frontier.append(candidate)
    return shortest


def _image(
    transformation: Transformation,
    proposition: Proposition,
) -> Proposition:
    return frozenset(transformation[index] for index in proposition)


def _preimage(
    transformation: Transformation,
    proposition: Proposition,
) -> Proposition:
    return frozenset(
        index
        for index in range(len(CORE_STATES))
        if transformation[index] in proposition
    )


def _support(predicate: Callable[[CoreState], bool]) -> Proposition:
    return frozenset(
        index
        for index, state in enumerate(CORE_STATES)
        if predicate(state)
    )


def _named_direct_propositions() -> dict[str, Proposition]:
    return {
        "x": _support(lambda state: state[1] == 1),
        "tk": _support(lambda state: state[0] == 1 and state[2] == 1),
        "t!k": _support(lambda state: state[0] == 1 and state[2] == 0),
        "k": _support(lambda state: state[2] == 1),
        "!k": _support(lambda state: state[2] == 0),
    }


def _transporters(
    antecedent: Proposition,
    consequent: Proposition,
) -> tuple[tuple[Transformation, Context], ...]:
    return tuple(
        (transformation, word)
        for transformation, word in _transformation_monoid().items()
        if _image(transformation, antecedent) <= consequent
    )


def _shortest_transporter(
    antecedent: Proposition,
    consequent: Proposition,
) -> Context | None:
    witnesses = _transporters(antecedent, consequent)
    if not witnesses:
        return None
    return min((word for _, word in witnesses), key=len)


def test_context_propositions_are_weakest_preconditions_of_the_spatial_atom() -> None:
    spatial_atom = _support(lambda state: state[1] == 1)
    monoid = _transformation_monoid()
    generated = {
        _preimage(transformation, spatial_atom) for transformation in monoid
    }

    assert len(monoid) == 16
    assert generated == set(_named_direct_propositions().values())
    assert len(generated) == 5

    for transformation in monoid:
        for consequent in ENVELOPE:
            weakest_precondition = _preimage(transformation, consequent)
            assert weakest_precondition in ENVELOPE
            for antecedent in ENVELOPE:
                assert (
                    _image(transformation, antecedent) <= consequent
                ) == (antecedent <= weakest_precondition)


def test_every_semantic_inclusion_has_the_trivial_identity_transporter() -> None:
    inclusion_count = 0
    for antecedent in ENVELOPE:
        for consequent in ENVELOPE:
            if antecedent <= consequent:
                inclusion_count += 1
                assert _image(IDENTITY, antecedent) <= consequent
                assert any(
                    transformation == IDENTITY
                    for transformation, _ in _transporters(
                        antecedent,
                        consequent,
                    )
                )

    assert inclusion_count == 3**8 == 6_561


def test_state_transport_strictly_exceeds_semantic_inclusion() -> None:
    monoid = _transformation_monoid()
    transportable = 0
    non_inclusion_transport = 0
    no_transporter = 0
    minimal_lengths: Counter[int] = Counter()

    for antecedent in ENVELOPE:
        for consequent in ENVELOPE:
            witnesses = tuple(
                word
                for transformation, word in monoid.items()
                if _image(transformation, antecedent) <= consequent
            )
            if witnesses:
                transportable += 1
                minimal_lengths[min(map(len, witnesses))] += 1
                if not antecedent <= consequent:
                    non_inclusion_transport += 1
            else:
                no_transporter += 1

    assert len(ENVELOPE) ** 2 == 65_536
    assert transportable == 37_621
    assert non_inclusion_transport == 31_060
    assert no_transporter == 27_915
    assert minimal_lengths == Counter(
        {
            0: 6_561,
            1: 13_208,
            2: 11_682,
            3: 6_038,
            4: 132,
        }
    )


def test_direct_transport_matrix_exposes_action_rather_than_implication() -> None:
    propositions = _named_direct_propositions()
    expected: dict[str, dict[str, Context | None]] = {
        "x": {
            "x": (),
            "tk": None,
            "t!k": None,
            "k": None,
            "!k": None,
        },
        "tk": {
            "x": ("X",),
            "tk": (),
            "t!k": ("K",),
            "k": (),
            "!k": ("K",),
        },
        "t!k": {
            "x": ("K", "X"),
            "tk": ("K",),
            "t!k": (),
            "k": ("K",),
            "!k": (),
        },
        "k": {
            "x": ("T", "X"),
            "tk": ("T",),
            "t!k": ("T", "K"),
            "k": (),
            "!k": ("K",),
        },
        "!k": {
            "x": ("T", "K", "X"),
            "tk": ("T", "K"),
            "t!k": ("T",),
            "k": ("K",),
            "!k": (),
        },
    }

    actual = {
        antecedent_name: {
            consequent_name: _shortest_transporter(antecedent, consequent)
            for consequent_name, consequent in propositions.items()
        }
        for antecedent_name, antecedent in propositions.items()
    }
    assert actual == expected

    positive = propositions["k"]
    negative = propositions["!k"]
    flip = _generator("K")
    assert not positive <= negative
    assert not negative <= positive
    assert _image(flip, positive) <= negative
    assert _image(flip, negative) <= positive


def test_hoare_transport_has_identity_and_composition_but_not_proof_order() -> None:
    monoid = _transformation_monoid()
    direct = tuple(_named_direct_propositions().values())

    for proposition in direct:
        assert _image(IDENTITY, proposition) <= proposition

    for antecedent in direct:
        for middle in direct:
            for consequent in direct:
                for first in monoid:
                    if not _image(first, antecedent) <= middle:
                        continue
                    for second in monoid:
                        if not _image(second, middle) <= consequent:
                            continue
                        composite = _compose(first, second)
                        assert composite in monoid
                        assert _image(composite, antecedent) <= consequent

    empty: Proposition = frozenset()
    whole: Proposition = frozenset(range(len(CORE_STATES)))
    for consequent in ENVELOPE:
        assert all(
            _image(transformation, empty) <= consequent
            for transformation in monoid
        )
    assert not any(
        _image(transformation, whole) <= empty for transformation in monoid
    )
