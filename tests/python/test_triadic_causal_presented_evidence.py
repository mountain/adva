from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from itertools import product


Axis = str
Context = tuple[Axis, ...]
CoreState = tuple[int, int, int]
Transformation = tuple[int, ...]
Proposition = frozenset[int]

AXES: tuple[Axis, ...] = ("T", "X", "K")
CORE_STATES: tuple[CoreState, ...] = tuple(product((0, 1), repeat=3))
CORE_INDEX = {state: index for index, state in enumerate(CORE_STATES)}
IDENTITY: Transformation = tuple(range(len(CORE_STATES)))
SPATIAL_ATOM: Proposition = frozenset(
    index for index, state in enumerate(CORE_STATES) if state[1] == 1
)


@dataclass(frozen=True, slots=True)
class PresentedEvidence:
    presentation: Transformation
    initial_state: int
    word: Context
    trace: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CausalContinuation:
    source: Transformation
    target: Transformation
    suffix: Context


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


def _evaluate_word(word: Context) -> Transformation:
    generators = {axis: _generator(axis) for axis in AXES}
    transformation = IDENTITY
    for axis in word:
        transformation = _compose(transformation, generators[axis])
    return transformation


def _run_word(initial_state: int, word: Context) -> tuple[int, ...]:
    trace = [initial_state]
    current = initial_state
    for axis in word:
        current = _generator(axis)[current]
        trace.append(current)
    return tuple(trace)


def _support(presentation: Transformation) -> Proposition:
    return frozenset(
        initial_state
        for initial_state in range(len(CORE_STATES))
        if presentation[initial_state] in SPATIAL_ATOM
    )


def _evidence(
    presentation: Transformation,
    initial_state: int,
    word: Context,
) -> PresentedEvidence:
    if _evaluate_word(word) != presentation:
        raise ValueError("word does not realize the declared presentation")
    if initial_state not in _support(presentation):
        raise ValueError("initial state does not satisfy the presented predicate")
    trace = _run_word(initial_state, word)
    if trace[-1] not in SPATIAL_ATOM:
        raise ValueError("evidence trace does not reach the spatial atom")
    return PresentedEvidence(presentation, initial_state, word, trace)


def _apply_continuation(
    continuation: CausalContinuation,
    evidence: PresentedEvidence,
) -> PresentedEvidence:
    if evidence.presentation != continuation.source:
        raise ValueError("evidence has the wrong source presentation")
    target = _compose(
        continuation.source,
        _evaluate_word(continuation.suffix),
    )
    if target != continuation.target:
        raise ValueError("suffix does not reach the target presentation")
    if not _support(continuation.source) <= _support(continuation.target):
        raise ValueError("continuation is not total on the source support")

    result = _evidence(
        continuation.target,
        evidence.initial_state,
        (*evidence.word, *continuation.suffix),
    )
    assert result.trace[: len(evidence.trace)] == evidence.trace
    return result


def _compose_continuations(
    first: CausalContinuation,
    second: CausalContinuation,
) -> CausalContinuation:
    if first.target != second.source:
        raise ValueError("continuation boundaries do not match")
    return CausalContinuation(
        first.source,
        second.target,
        (*first.suffix, *second.suffix),
    )


def _right_reachability(
    source: Transformation,
) -> dict[Transformation, Context]:
    generators = {axis: _generator(axis) for axis in AXES}
    shortest: dict[Transformation, Context] = {source: ()}
    frontier = deque([source])
    while frontier:
        presentation = frontier.popleft()
        for axis in AXES:
            target = _compose(presentation, generators[axis])
            if target not in shortest:
                shortest[target] = (*shortest[presentation], axis)
                frontier.append(target)
    return shortest


def _shortest_continuation(
    source: Transformation,
    target: Transformation,
) -> CausalContinuation | None:
    if not _support(source) <= _support(target):
        return None
    suffix = _right_reachability(source).get(target)
    if suffix is None:
        return None
    return CausalContinuation(source, target, suffix)


def _word_name(word: Context) -> str:
    return "".join(word) or "eps"


def test_presented_evidence_accepts_open_histories_with_finite_types() -> None:
    monoid = _transformation_monoid()
    assert len(monoid) == 16

    for presentation, canonical_word in monoid.items():
        for initial_state in _support(presentation):
            evidence = _evidence(
                presentation,
                initial_state,
                canonical_word,
            )
            assert evidence.trace[0] == initial_state
            assert evidence.trace[-1] == presentation[initial_state]

    positive_spatial_state = next(iter(SPATIAL_ATOM))
    identity_evidence = _evidence(IDENTITY, positive_spatial_state, ())
    nontrivial_identity = CausalContinuation(
        IDENTITY,
        IDENTITY,
        ("K", "K"),
    )
    extended = _apply_continuation(nontrivial_identity, identity_evidence)
    assert extended.presentation == identity_evidence.presentation
    assert extended.initial_state == identity_evidence.initial_state
    assert extended.word == ("K", "K")
    assert extended.trace != identity_evidence.trace


def test_support_inclusion_does_not_always_lift_to_causal_evidence() -> None:
    monoid = _transformation_monoid()
    inclusions = 0
    lifted = 0
    strict_lifts = 0
    equal_support_lifts = 0
    missing: set[tuple[str, str]] = set()
    shortest_lengths: Counter[int] = Counter()

    for source, source_word in monoid.items():
        for target, target_word in monoid.items():
            if not _support(source) <= _support(target):
                continue
            inclusions += 1
            continuation = _shortest_continuation(source, target)
            if continuation is None:
                missing.add(
                    (_word_name(source_word), _word_name(target_word))
                )
                continue
            lifted += 1
            shortest_lengths[len(continuation.suffix)] += 1
            if _support(source) < _support(target):
                strict_lifts += 1
            else:
                equal_support_lifts += 1

    assert inclusions == 72
    assert lifted == 60
    assert strict_lifts == 16
    assert equal_support_lifts == 44
    assert shortest_lengths == Counter({0: 16, 1: 24, 2: 12, 3: 6, 4: 2})
    assert missing == {
        ("T", "eps"),
        ("T", "K"),
        ("TK", "eps"),
        ("TK", "K"),
        ("XT", "X"),
        ("XT", "XK"),
        ("XTK", "X"),
        ("XTK", "XK"),
        ("KXT", "KX"),
        ("KXT", "KXK"),
        ("KXTK", "KX"),
        ("KXTK", "KXK"),
    }


def test_temporal_opening_is_not_evidence_reversible_but_flip_is() -> None:
    monoid = _transformation_monoid()
    by_word = {word: presentation for presentation, word in monoid.items()}

    identity = by_word[()]
    temporal = by_word[("T",)]
    construction = by_word[("K",)]
    spatial = by_word[("X",)]
    spatial_then_temporal = by_word[("X", "T")]
    spatial_then_construction = by_word[("X", "K")]

    assert _support(identity) == _support(temporal) == _support(construction)
    assert _shortest_continuation(identity, temporal) is not None
    assert _shortest_continuation(temporal, identity) is None

    assert _shortest_continuation(identity, construction) is not None
    assert _shortest_continuation(construction, identity) is not None

    assert _support(spatial) == _support(spatial_then_temporal)
    assert _support(spatial) == _support(spatial_then_construction)
    assert _shortest_continuation(spatial, spatial_then_temporal) is not None
    assert _shortest_continuation(spatial_then_temporal, spatial) is None
    assert _shortest_continuation(
        spatial,
        spatial_then_construction,
    ) is not None
    assert _shortest_continuation(
        spatial_then_construction,
        spatial,
    ) is not None


def test_strict_inclusion_can_lift_without_rewriting_the_past() -> None:
    monoid = _transformation_monoid()
    by_word = {word: presentation for presentation, word in monoid.items()}
    source = by_word[("X",)]
    target = by_word[("T", "X")]

    assert _support(source) < _support(target)
    continuation = _shortest_continuation(source, target)
    assert continuation == CausalContinuation(
        source,
        target,
        ("T", "X"),
    )

    for initial_state in _support(source):
        source_evidence = _evidence(source, initial_state, ("X",))
        target_evidence = _apply_continuation(
            continuation,
            source_evidence,
        )
        assert target_evidence.word == ("X", "T", "X")
        assert target_evidence.trace[:2] == source_evidence.trace
        assert target_evidence.presentation == target


def test_causal_evidence_continuations_have_identity_and_cut() -> None:
    monoid = _transformation_monoid()
    continuations = tuple(
        continuation
        for source in monoid
        for target in monoid
        if (continuation := _shortest_continuation(source, target)) is not None
    )
    assert len(continuations) == 60

    for presentation, canonical_word in monoid.items():
        identity = _shortest_continuation(presentation, presentation)
        assert identity == CausalContinuation(presentation, presentation, ())
        for initial_state in _support(presentation):
            evidence = _evidence(
                presentation,
                initial_state,
                canonical_word,
            )
            assert _apply_continuation(identity, evidence) == evidence

    for first in continuations:
        for second in continuations:
            if first.target != second.source:
                continue
            composite = _compose_continuations(first, second)
            assert _evaluate_word(composite.suffix) in _transformation_monoid()
            assert _compose(
                composite.source,
                _evaluate_word(composite.suffix),
            ) == composite.target
            assert _support(composite.source) <= _support(composite.target)
            source_word = monoid[composite.source]
            for initial_state in _support(composite.source):
                evidence = _evidence(
                    composite.source,
                    initial_state,
                    source_word,
                )
                sequential = _apply_continuation(
                    second,
                    _apply_continuation(first, evidence),
                )
                direct = _apply_continuation(composite, evidence)
                assert sequential == direct


def test_forgetting_presentations_restores_all_extensional_inclusions() -> None:
    monoid = _transformation_monoid()
    propositions = {_support(presentation) for presentation in monoid}
    comparisons = 0

    for source in monoid:
        reachable = _right_reachability(source)
        for target_support in propositions:
            if not _support(source) <= target_support:
                continue
            comparisons += 1
            candidates = {
                target: suffix
                for target, suffix in reachable.items()
                if _support(target) == target_support
            }
            assert candidates

    assert len(propositions) == 5
    assert comparisons == 24
