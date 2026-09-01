from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from itertools import permutations, product
from typing import Callable


Axis = str
Context = tuple[Axis, ...]
CoreState = tuple[int, int, int]
Transformation = tuple[int, ...]
Proposition = frozenset[int]
EvidenceType = tuple[Transformation, ...]

AXES: tuple[Axis, ...] = ("T", "X", "K")
CORE_STATES: tuple[CoreState, ...] = tuple(product((0, 1), repeat=3))
CORE_INDEX = {state: index for index, state in enumerate(CORE_STATES)}
IDENTITY: Transformation = tuple(range(len(CORE_STATES)))
SPATIAL_ATOM: Proposition = frozenset(
    index for index, state in enumerate(CORE_STATES) if state[1] == 1
)
WHOLE_CORE: Proposition = frozenset(range(len(CORE_STATES)))


@dataclass(frozen=True, slots=True)
class PresentedEvidence:
    presentation: Transformation
    initial_state: int
    word: Context
    trace: tuple[int, ...]
    resource_id: str


@dataclass(frozen=True, slots=True)
class CausalContinuation:
    source: Transformation
    target: Transformation
    suffix: Context


@dataclass(frozen=True, slots=True)
class SynchronizedEvidence:
    initial_state: int
    components: tuple[PresentedEvidence, ...]

    @property
    def evidence_type(self) -> EvidenceType:
        return tuple(component.presentation for component in self.components)

    @property
    def resource_ids(self) -> tuple[str, ...]:
        return tuple(component.resource_id for component in self.components)


@dataclass(frozen=True, slots=True)
class LinearTensorMap:
    source: EvidenceType
    target: EvidenceType
    permutation: tuple[int, ...]
    continuations: tuple[CausalContinuation, ...]


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


def _type_support(evidence_type: EvidenceType) -> Proposition:
    support = WHOLE_CORE
    for presentation in evidence_type:
        support = support & _support(presentation)
    return support


def _evidence(
    presentation: Transformation,
    initial_state: int,
    word: Context,
    resource_id: str,
) -> PresentedEvidence:
    if _evaluate_word(word) != presentation:
        raise ValueError("word does not realize the declared presentation")
    if initial_state not in _support(presentation):
        raise ValueError("initial state does not satisfy the presented predicate")
    trace = _run_word(initial_state, word)
    if trace[-1] not in SPATIAL_ATOM:
        raise ValueError("evidence trace does not reach the spatial atom")
    return PresentedEvidence(
        presentation,
        initial_state,
        word,
        trace,
        resource_id,
    )


def _synchronize(
    initial_state: int,
    *components: PresentedEvidence,
) -> SynchronizedEvidence:
    if any(component.initial_state != initial_state for component in components):
        raise ValueError("tensor components must have the same initial state")
    resource_ids = [component.resource_id for component in components]
    if len(resource_ids) != len(set(resource_ids)):
        raise ValueError("each input evidence resource must be used exactly once")
    return SynchronizedEvidence(initial_state, tuple(components))


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
        evidence.resource_id,
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


def _right_reachability(source: Transformation) -> dict[Transformation, Context]:
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


def _linear_map(
    source: EvidenceType,
    target: EvidenceType,
    permutation: tuple[int, ...],
    continuations: tuple[CausalContinuation, ...],
) -> LinearTensorMap:
    arity = len(source)
    if len(target) != arity:
        raise ValueError("linear maps cannot copy or discard evidence resources")
    if tuple(sorted(permutation)) != tuple(range(arity)):
        raise ValueError("linear maps require a bijection of evidence resources")
    if len(continuations) != arity:
        raise ValueError("each target component needs one continuation")
    for target_slot, continuation in enumerate(continuations):
        source_slot = permutation[target_slot]
        if continuation.source != source[source_slot]:
            raise ValueError("continuation has the wrong source component")
        if continuation.target != target[target_slot]:
            raise ValueError("continuation has the wrong target component")
    return LinearTensorMap(source, target, permutation, continuations)


def _linear_maps(
    source: EvidenceType,
    target: EvidenceType,
) -> tuple[LinearTensorMap, ...]:
    if len(source) != len(target):
        return ()
    maps: list[LinearTensorMap] = []
    for permutation in permutations(range(len(source))):
        continuations: list[CausalContinuation] = []
        for target_slot, source_slot in enumerate(permutation):
            continuation = _shortest_continuation(
                source[source_slot],
                target[target_slot],
            )
            if continuation is None:
                break
            continuations.append(continuation)
        else:
            maps.append(
                _linear_map(
                    source,
                    target,
                    permutation,
                    tuple(continuations),
                )
            )
    return tuple(maps)


def _apply_linear_map(
    linear_map: LinearTensorMap,
    evidence: SynchronizedEvidence,
) -> SynchronizedEvidence:
    if evidence.evidence_type != linear_map.source:
        raise ValueError("evidence has the wrong tensor source type")
    result = tuple(
        _apply_continuation(
            linear_map.continuations[target_slot],
            evidence.components[source_slot],
        )
        for target_slot, source_slot in enumerate(linear_map.permutation)
    )
    return _synchronize(evidence.initial_state, *result)


def _compose_linear_maps(
    first: LinearTensorMap,
    second: LinearTensorMap,
) -> LinearTensorMap:
    if first.target != second.source:
        raise ValueError("linear map boundaries do not match")
    permutation = tuple(
        first.permutation[middle_slot]
        for middle_slot in second.permutation
    )
    continuations = tuple(
        _compose_continuations(
            first.continuations[middle_slot],
            second.continuations[target_slot],
        )
        for target_slot, middle_slot in enumerate(second.permutation)
    )
    return _linear_map(
        first.source,
        second.target,
        permutation,
        continuations,
    )


def _tensor_atomic_maps(
    left: LinearTensorMap,
    right: LinearTensorMap,
) -> LinearTensorMap:
    if len(left.source) != 1 or len(right.source) != 1:
        raise ValueError("this finite constructor tensors two atomic maps")
    return _linear_map(
        (*left.source, *right.source),
        (*left.target, *right.target),
        (0, 1),
        (*left.continuations, *right.continuations),
    )


def _only_map(source: EvidenceType, target: EvidenceType) -> LinearTensorMap:
    maps = _linear_maps(source, target)
    if len(maps) != 1:
        raise AssertionError(f"expected one map, found {len(maps)}")
    return maps[0]


def _assert_value_error(operation: Callable[[], object]) -> None:
    try:
        operation()
    except ValueError:
        return
    raise AssertionError("expected ValueError")


def test_finite_tensor_fragment_separates_support_from_linear_maps() -> None:
    monoid = _transformation_monoid()
    presentations = tuple(monoid)
    evidence_types: tuple[EvidenceType, ...] = (
        (),
        *((presentation,) for presentation in presentations),
        *product(presentations, repeat=2),
    )

    assert len(evidence_types) == 273
    distinct_supports = {
        _type_support(evidence_type) for evidence_type in evidence_types
    }
    assert len(distinct_supports) == 11
    arity_distribution = Counter(map(len, evidence_types))
    assert arity_distribution == Counter({2: 256, 1: 16, 0: 1})
    assert Counter(map(lambda item: len(_type_support(item)), evidence_types)) == Counter(
        {0: 72, 1: 64, 2: 104, 4: 32, 8: 1}
    )

    inclusions = Counter()
    map_pairs = Counter()
    map_multiplicity = Counter()
    same_support_cross_arity = 0

    for source in evidence_types:
        for target in evidence_types:
            if not _type_support(source) <= _type_support(target):
                continue
            arities = (len(source), len(target))
            inclusions[arities] += 1
            if (
                len(source) != len(target)
                and _type_support(source) == _type_support(target)
            ):
                same_support_cross_arity += 1
            maps = _linear_maps(source, target)
            if maps:
                map_pairs[arities] += 1
                map_multiplicity[len(maps)] += 1

    assert inclusions == Counter(
        {
            (0, 0): 1,
            (1, 0): 16,
            (1, 1): 72,
            (1, 2): 368,
            (2, 0): 256,
            (2, 1): 2_448,
            (2, 2): 28_576,
        }
    )
    assert sum(inclusions.values()) == 31_737
    assert map_pairs == Counter({(0, 0): 1, (1, 1): 60, (2, 2): 6_256})
    assert sum(map_pairs.values()) == 6_317
    assert sum(inclusions.values()) - sum(map_pairs.values()) == 25_420
    assert sum(
        count for arities, count in inclusions.items() if arities[0] != arities[1]
    ) == 3_088
    assert map_multiplicity == Counter({1: 5_373, 2: 944})
    routing_witnesses = sum(
        count * multiplicity
        for multiplicity, count in map_multiplicity.items()
    )
    assert routing_witnesses == 7_261
    assert same_support_cross_arity == 672


def test_synchronized_tensor_has_explicit_exchange_but_no_alias_copy() -> None:
    monoid = _transformation_monoid()
    by_word = {word: presentation for presentation, word in monoid.items()}
    spatial = by_word[("X",)]
    initial_state = next(iter(_support(spatial)))
    first = _evidence(spatial, initial_state, ("X",), "r0")
    second = _evidence(spatial, initial_state, ("X",), "r1")

    pair = _synchronize(initial_state, first, second)
    maps = _linear_maps((spatial, spatial), (spatial, spatial))
    assert {linear_map.permutation for linear_map in maps} == {(0, 1), (1, 0)}

    identity = next(item for item in maps if item.permutation == (0, 1))
    exchange = next(item for item in maps if item.permutation == (1, 0))
    assert _apply_linear_map(identity, pair).resource_ids == ("r0", "r1")
    assert _apply_linear_map(exchange, pair).resource_ids == ("r1", "r0")

    _assert_value_error(lambda: _synchronize(initial_state, first, first))

    other_state = next(state for state in _support(spatial) if state != initial_state)
    foreign = _evidence(spatial, other_state, ("X",), "r2")
    _assert_value_error(lambda: _synchronize(initial_state, first, foreign))


def test_equal_support_does_not_authorize_contraction_or_weakening() -> None:
    monoid = _transformation_monoid()
    by_word = {word: presentation for presentation, word in monoid.items()}
    spatial = by_word[("X",)]
    atom = (spatial,)
    duplicate_shape = (spatial, spatial)

    assert _type_support(atom) == _type_support(duplicate_shape)
    assert _linear_maps(atom, duplicate_shape) == ()
    assert _linear_maps(duplicate_shape, atom) == ()

    _assert_value_error(
        lambda: _linear_map(
            atom,
            duplicate_shape,
            (0, 0),
            (
                CausalContinuation(spatial, spatial, ()),
                CausalContinuation(spatial, spatial, ()),
            ),
        )
    )
    _assert_value_error(
        lambda: _linear_map(
            duplicate_shape,
            atom,
            (0,),
            (CausalContinuation(spatial, spatial, ()),),
        )
    )


def test_tensor_maps_preserve_lineage_under_tensor_and_cut() -> None:
    monoid = _transformation_monoid()
    by_word = {word: presentation for presentation, word in monoid.items()}
    spatial = by_word[("X",)]
    spatial_temporal = by_word[("X", "T")]
    spatial_construction = by_word[("X", "K")]
    spatial_temporal_construction = by_word[("X", "T", "K")]

    temporal_map = _only_map((spatial,), (spatial_temporal,))
    construction_map = _only_map((spatial,), (spatial_construction,))
    first = _tensor_atomic_maps(temporal_map, construction_map)
    assert first.source == (spatial, spatial)
    assert first.target == (spatial_temporal, spatial_construction)
    assert first.permutation == (0, 1)

    second = _linear_map(
        first.target,
        (spatial, spatial_temporal_construction),
        (1, 0),
        (
            _shortest_continuation(spatial_construction, spatial),
            _shortest_continuation(
                spatial_temporal,
                spatial_temporal_construction,
            ),
        ),
    )
    composite = _compose_linear_maps(first, second)
    assert composite.permutation == (1, 0)

    initial_state = next(iter(_type_support(first.source)))
    evidence = _synchronize(
        initial_state,
        _evidence(spatial, initial_state, ("X",), "left"),
        _evidence(spatial, initial_state, ("X",), "right"),
    )
    sequential = _apply_linear_map(second, _apply_linear_map(first, evidence))
    direct = _apply_linear_map(composite, evidence)
    assert sequential == direct
    assert direct.resource_ids == ("right", "left")
    assert set(direct.resource_ids) == set(evidence.resource_ids)


def test_unit_has_only_its_linear_identity() -> None:
    monoid = _transformation_monoid()
    spatial = next(
        presentation for presentation, word in monoid.items() if word == ("X",)
    )
    unit = _synchronize(0)

    assert unit.evidence_type == ()
    assert _type_support(()) == WHOLE_CORE
    assert _linear_maps((), ()) == (
        LinearTensorMap((), (), (), ()),
    )
    assert _apply_linear_map(_linear_maps((), ())[0], unit) == unit
    assert _linear_maps((), (spatial,)) == ()
    assert _linear_maps((spatial,), ()) == ()
