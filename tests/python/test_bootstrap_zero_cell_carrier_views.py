from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from enum import Enum, IntEnum
from itertools import permutations
from typing import TypeAlias

import pytest


class CellDimension(IntEnum):
    STATE = 0
    STEP = 1
    RELATION = 2
    COHERENCE = 3


class RelationKind(Enum):
    INTERCHANGE = "interchange"
    BRAID = "braid"


@dataclass(frozen=True)
class StateOccurrence:
    name: str
    source: str
    occurrence: str
    value_type: str = "A"
    multiplicity: int = 1
    origin_port: str | None = None


@dataclass(frozen=True)
class StepOccurrence:
    name: str
    operator: str
    source: str
    target: str
    origin: str | None = None
    presentation: str = "presented"


@dataclass(frozen=True)
class Thread:
    name: str
    states: tuple[str, ...]
    steps: tuple[str, ...]


@dataclass(frozen=True)
class RelationBoundary:
    name: str
    kind: RelationKind
    source_thread: Thread
    target_thread: Thread
    circle_order: tuple[str, ...]


@dataclass(frozen=True)
class RelationFiller:
    name: str
    boundary: str
    witness: str


@dataclass(frozen=True)
class StratifiedCarrier:
    name: str
    states: tuple[StateOccurrence, ...]
    steps: tuple[StepOccurrence, ...]
    relations: tuple[RelationBoundary, ...]
    fillers: tuple[RelationFiller, ...] = ()


@dataclass(frozen=True)
class ViewContract:
    name: str
    target: str
    preserves: tuple[str, ...]
    forgets: tuple[str, ...]
    kernel: tuple[str, ...] = ()


@dataclass(frozen=True)
class PresentedView:
    contract: ViewContract
    carrier: str
    occurrences: tuple[StateOccurrence, ...]
    circle_orders: tuple[tuple[str, ...], ...]
    threads: tuple[Thread, ...]
    obligations: tuple[RelationBoundary, ...]
    witnesses: tuple[RelationFiller, ...]


PermutationState: TypeAlias = tuple[str, str, str, str]


@dataclass(frozen=True)
class RankTwoFace:
    kind: RelationKind
    generators: tuple[int, int]
    boundary: tuple[PermutationState, ...]


@dataclass(frozen=True)
class CoherenceEnvelope:
    name: str
    states: tuple[PermutationState, ...]
    edges: tuple[frozenset[PermutationState], ...]
    faces: tuple[RankTwoFace, ...]


LINE_VIEW = ViewContract(
    "line",
    "LinearBoundary",
    ("occurrence-ledger", "typed-boundary", "path-endpoints"),
    ("cyclic-root", "relation-filler"),
    ("cyclic-root", "relation-filler"),
)

CIRCLE_VIEW = ViewContract(
    "circle",
    "CyclicBoundary",
    ("occurrence-ledger", "typed-boundary", "cyclic-incidence"),
    ("chosen-seam", "relation-filler"),
    ("chosen-seam", "relation-filler"),
)

THREAD_VIEW = ViewContract(
    "thread",
    "OrderedHistory",
    ("occurrence-ledger", "typed-boundary", "ordered-history"),
    ("geometric-embedding",),
    ("geometric-embedding",),
)

LOGIC_VIEW = ViewContract(
    "logic",
    "ProofRelevantDerivation",
    (
        "occurrence-ledger",
        "typed-boundary",
        "ordered-history",
        "proof-obligation",
        "proof-witness",
    ),
    ("metric", "geometric-embedding"),
    ("metric", "geometric-embedding"),
)


def _validate_thread(thread: Thread, steps: dict[str, StepOccurrence]) -> None:
    if len(thread.states) != len(thread.steps) + 1:
        raise ValueError("a thread needs one more state than step")
    for index, step_name in enumerate(thread.steps):
        if step_name not in steps:
            raise ValueError("a thread step must occur in the carrier")
        step = steps[step_name]
        if (step.source, step.target) != (
            thread.states[index],
            thread.states[index + 1],
        ):
            raise ValueError("thread state order must match step boundaries")


def _thread_word(
    thread: Thread, steps: dict[str, StepOccurrence]
) -> tuple[str, ...]:
    return tuple(steps[name].operator for name in thread.steps)


def _validate_relation(
    relation: RelationBoundary,
    states: dict[str, StateOccurrence],
    steps: dict[str, StepOccurrence],
) -> None:
    _validate_thread(relation.source_thread, steps)
    _validate_thread(relation.target_thread, steps)
    source = relation.source_thread
    target = relation.target_thread
    if (source.states[0], source.states[-1]) != (
        target.states[0],
        target.states[-1],
    ):
        raise ValueError("relation threads need common typed endpoints")
    if states[source.states[0]].value_type != states[target.states[0]].value_type:
        raise ValueError("relation source types must agree")
    if states[source.states[-1]].value_type != states[target.states[-1]].value_type:
        raise ValueError("relation target types must agree")
    if len(source.steps) != len(target.steps):
        raise ValueError("relation threads need equal positive length")
    if not source.steps:
        raise ValueError("a relation boundary cannot be empty")
    if set(source.states[1:-1]) & set(target.states[1:-1]):
        raise ValueError("relation threads must retain distinct internal occurrences")

    boundary_states = set(source.states) | set(target.states)
    expected_count = 2 * len(source.steps)
    if len(boundary_states) != expected_count:
        raise ValueError("parallel length-m threads must expose 2m occurrences")
    if (
        len(relation.circle_order) != expected_count
        or set(relation.circle_order) != boundary_states
    ):
        raise ValueError("circle order must use every boundary occurrence exactly once")

    source_word = _thread_word(source, steps)
    target_word = _thread_word(target, steps)
    if relation.kind is RelationKind.INTERCHANGE:
        if (
            len(source_word) != 2
            or source_word[0] == source_word[1]
            or target_word != tuple(reversed(source_word))
        ):
            raise ValueError("an interchange cell needs ab and ba")
    elif relation.kind is RelationKind.BRAID:
        a, b = source_word[0], source_word[1]
        if (
            len(source_word) != 3
            or a == b
            or source_word != (a, b, a)
            or target_word != (b, a, b)
        ):
            raise ValueError("a braid cell needs aba and bab")


def _validate_carrier(carrier: StratifiedCarrier) -> None:
    state_names = tuple(state.name for state in carrier.states)
    occurrences = tuple(state.occurrence for state in carrier.states)
    step_names = tuple(step.name for step in carrier.steps)
    relation_names = tuple(relation.name for relation in carrier.relations)
    if len(state_names) != len(set(state_names)):
        raise ValueError("carrier state names must be distinct")
    if len(occurrences) != len(set(occurrences)):
        raise ValueError("carrier occurrence names must be distinct")
    if any(state.multiplicity <= 0 for state in carrier.states):
        raise ValueError("carrier occurrences need positive multiplicity")
    if len(step_names) != len(set(step_names)):
        raise ValueError("carrier step names must be distinct")
    if len(relation_names) != len(set(relation_names)):
        raise ValueError("carrier relation names must be distinct")

    states = {state.name: state for state in carrier.states}
    steps = {step.name: step for step in carrier.steps}
    if any(step.source not in states or step.target not in states for step in carrier.steps):
        raise ValueError("step boundaries must occur in the carrier")
    if any(step.presentation not in {"presented", "native", "converse"} for step in carrier.steps):
        raise ValueError("step presentation must be explicit")
    for relation in carrier.relations:
        _validate_relation(relation, states, steps)

    known_relations = set(relation_names)
    filler_names = tuple(filler.name for filler in carrier.fillers)
    if len(filler_names) != len(set(filler_names)):
        raise ValueError("relation filler names must be distinct")
    for filler in carrier.fillers:
        if filler.boundary not in known_relations or not filler.witness:
            raise ValueError("a filler needs a known boundary and nonempty witness")


def _validate_view_contract(contract: ViewContract) -> None:
    if not contract.name or not contract.target:
        raise ValueError("a view needs a name and target syntax")
    preserves = set(contract.preserves)
    forgets = set(contract.forgets)
    if "occurrence-ledger" not in preserves:
        raise ValueError("every Bootstrap Zero view must preserve the occurrence ledger")
    if preserves & forgets:
        raise ValueError("a view cannot both preserve and forget one coordinate")
    if not set(contract.kernel) <= forgets:
        raise ValueError("a view kernel must name forgotten distinctions")


def _project(carrier: StratifiedCarrier, contract: ViewContract) -> PresentedView:
    _validate_carrier(carrier)
    _validate_view_contract(contract)
    keep = set(contract.preserves)
    threads = tuple(
        thread
        for relation in carrier.relations
        for thread in (relation.source_thread, relation.target_thread)
    )
    return PresentedView(
        contract,
        carrier.name,
        carrier.states,
        tuple(
            relation.circle_order
            for relation in carrier.relations
            if "cyclic-incidence" in keep
        ),
        threads if "ordered-history" in keep or "path-endpoints" in keep else (),
        carrier.relations if "proof-obligation" in keep else (),
        carrier.fillers if "proof-witness" in keep else (),
    )


def _states(names: tuple[str, ...], prefix: str) -> tuple[StateOccurrence, ...]:
    return tuple(
        StateOccurrence(name, f"source-{prefix}-{index}", f"occ-{prefix}-{index}")
        for index, name in enumerate(names)
    )


def _q4(filled: bool = False) -> StratifiedCarrier:
    names = ("q-LL", "q-RL", "q-RR", "q-LR")
    steps = (
        StepOccurrence("q-a-top", "a", names[0], names[1]),
        StepOccurrence("q-b-top", "b", names[1], names[2]),
        StepOccurrence("q-b-bottom", "b", names[0], names[3]),
        StepOccurrence("q-a-bottom", "a", names[3], names[2]),
    )
    relation = RelationBoundary(
        "q4-boundary",
        RelationKind.INTERCHANGE,
        Thread("ab", names[:3], ("q-a-top", "q-b-top")),
        Thread("ba", (names[0], names[3], names[2]), ("q-b-bottom", "q-a-bottom")),
        names,
    )
    fillers = (
        (RelationFiller("chi-ab", relation.name, "independent-interchange"),)
        if filled
        else ()
    )
    return StratifiedCarrier("Q4", _states(names, "q"), steps, (relation,), fillers)


def _m6(filled: bool = False) -> StratifiedCarrier:
    names = (
        "p[K,X;t]",
        "p[X,K;t]",
        "p[X,t;K]",
        "p[t,X;K]",
        "p[t,K;X]",
        "p[K,t;X]",
    )
    steps = (
        StepOccurrence("m-a-1", "a", names[0], names[1]),
        StepOccurrence("m-b-1", "b", names[1], names[2]),
        StepOccurrence("m-a-2", "a", names[2], names[3]),
        StepOccurrence("m-b-2", "b", names[0], names[5]),
        StepOccurrence("m-a-3", "a", names[5], names[4]),
        StepOccurrence("m-b-3", "b", names[4], names[3]),
    )
    relation = RelationBoundary(
        "m6-boundary",
        RelationKind.BRAID,
        Thread("aba", names[:4], ("m-a-1", "m-b-1", "m-a-2")),
        Thread(
            "bab",
            (names[0], names[5], names[4], names[3]),
            ("m-b-2", "m-a-3", "m-b-3"),
        ),
        names,
    )
    fillers = (
        (RelationFiller("beta-ab", relation.name, "typed-braid-coherence"),)
        if filled
        else ()
    )
    return StratifiedCarrier("M6", _states(names, "m"), steps, (relation,), fillers)


def _swap(state: PermutationState, generator: int) -> PermutationState:
    if generator not in (0, 1, 2):
        raise ValueError("TO24 generators are the three adjacent swaps")
    result = list(state)
    result[generator], result[generator + 1] = (
        result[generator + 1],
        result[generator],
    )
    return tuple(result)  # type: ignore[return-value]


def _act(state: PermutationState, word: tuple[int, ...]) -> PermutationState:
    for generator in word:
        state = _swap(state, generator)
    return state


def _rank_two_boundary(
    start: PermutationState, generators: tuple[int, int], length: int
) -> tuple[PermutationState, ...]:
    boundary = [start]
    state = start
    for index in range(length - 1):
        state = _swap(state, generators[index % 2])
        boundary.append(state)
    if _swap(state, generators[(length - 1) % 2]) != start:
        raise ValueError("rank-two boundary does not close")
    if len(set(boundary)) != length:
        raise ValueError("rank-two boundary repeats before closure")
    return tuple(boundary)


def _to24() -> CoherenceEnvelope:
    states = tuple(permutations(("0", "K", "X", "t")))
    edges = {
        frozenset((state, _swap(state, generator)))
        for state in states
        for generator in (0, 1, 2)
    }
    face_specs = (
        (RelationKind.INTERCHANGE, (0, 2), 4),
        (RelationKind.BRAID, (0, 1), 6),
        (RelationKind.BRAID, (1, 2), 6),
    )
    faces: list[RankTwoFace] = []
    seen: set[frozenset[PermutationState]] = set()
    for kind, generators, length in face_specs:
        for state in states:
            boundary = _rank_two_boundary(state, generators, length)
            key = frozenset(boundary)
            if key not in seen:
                seen.add(key)
                faces.append(RankTwoFace(kind, generators, boundary))
    return CoherenceEnvelope(
        "TO24",
        states,
        tuple(sorted(edges, key=lambda edge: sorted(edge))),
        tuple(faces),
    )


def _validate_to24(envelope: CoherenceEnvelope) -> None:
    if len(envelope.states) != 24 or len(set(envelope.states)) != 24:
        raise ValueError("TO24 needs the 24 permutations of four chart symbols")
    if len(envelope.edges) != 36:
        raise ValueError("TO24 needs 36 adjacent-transposition edges")
    if Counter(face.kind for face in envelope.faces) != Counter(
        {RelationKind.INTERCHANGE: 6, RelationKind.BRAID: 8}
    ):
        raise ValueError("TO24 needs six Q4 and eight M6 face occurrences")

    edge_incidence: Counter[frozenset[PermutationState]] = Counter()
    vertex_faces: defaultdict[PermutationState, Counter[RelationKind]] = defaultdict(
        Counter
    )
    for face in envelope.faces:
        for index, vertex in enumerate(face.boundary):
            next_vertex = face.boundary[(index + 1) % len(face.boundary)]
            edge_incidence[frozenset((vertex, next_vertex))] += 1
            vertex_faces[vertex][face.kind] += 1
    if set(edge_incidence) != set(envelope.edges) or set(edge_incidence.values()) != {2}:
        raise ValueError("each TO24 edge must occur in two opposite face boundaries")
    expected = Counter({RelationKind.INTERCHANGE: 1, RelationKind.BRAID: 2})
    if any(vertex_faces[state] != expected for state in envelope.states):
        raise ValueError("every TO24 vertex needs local face pattern 4.6.6")


def test_cell_dimensions_leave_higher_coherence_open() -> None:
    assert tuple(CellDimension) == (
        CellDimension.STATE,
        CellDimension.STEP,
        CellDimension.RELATION,
        CellDimension.COHERENCE,
    )


def test_q4_is_one_open_interchange_boundary_between_distinct_histories() -> None:
    carrier = _q4()
    _validate_carrier(carrier)
    relation = carrier.relations[0]
    steps = {step.name: step for step in carrier.steps}

    assert len(carrier.states) == 4
    assert _thread_word(relation.source_thread, steps) == ("a", "b")
    assert _thread_word(relation.target_thread, steps) == ("b", "a")
    assert relation.source_thread != relation.target_thread
    assert carrier.fillers == ()


def test_m6_is_one_open_braid_boundary_between_distinct_histories() -> None:
    carrier = _m6()
    _validate_carrier(carrier)
    relation = carrier.relations[0]
    steps = {step.name: step for step in carrier.steps}

    assert len(carrier.states) == 6
    assert _thread_word(relation.source_thread, steps) == ("a", "b", "a")
    assert _thread_word(relation.target_thread, steps) == ("b", "a", "b")
    assert relation.source_thread != relation.target_thread
    assert carrier.fillers == ()


def test_logic_view_turns_open_m6_into_an_obligation_not_an_equality() -> None:
    carrier = _m6()
    logic = _project(carrier, LOGIC_VIEW)

    assert logic.occurrences is carrier.states
    assert len(logic.obligations) == 1
    assert logic.witnesses == ()
    assert logic.threads[0] != logic.threads[1]


def test_filled_m6_retains_both_histories_and_the_braid_witness() -> None:
    carrier = _m6(filled=True)
    logic = _project(carrier, LOGIC_VIEW)

    assert len(logic.obligations) == 1
    assert len(logic.witnesses) == 1
    assert logic.witnesses[0].boundary == logic.obligations[0].name
    assert logic.threads[0] != logic.threads[1]


def test_four_core_views_reuse_one_literal_occurrence_ledger() -> None:
    carrier = _m6(filled=True)
    views = tuple(
        _project(carrier, contract)
        for contract in (LINE_VIEW, CIRCLE_VIEW, THREAD_VIEW, LOGIC_VIEW)
    )

    assert all(view.occurrences is carrier.states for view in views)
    assert all(
        tuple(state.occurrence for state in view.occurrences)
        == tuple(state.occurrence for state in carrier.states)
        for view in views
    )
    assert views[1].circle_orders == (carrier.relations[0].circle_order,)
    assert views[2].threads == (
        carrier.relations[0].source_thread,
        carrier.relations[0].target_thread,
    )


def test_view_contract_is_open_but_its_forgetting_is_auditable() -> None:
    energy = ViewContract(
        "energy-candidate",
        "CharacteristicGrading",
        ("occurrence-ledger", "typed-boundary"),
        ("ordered-history",),
        ("ordered-history",),
    )

    view = _project(_q4(), energy)
    assert view.contract.name == "energy-candidate"
    with pytest.raises(ValueError, match="occurrence ledger"):
        _validate_view_contract(
            ViewContract("bad", "BadTarget", ("typed-boundary",), (), ())
        )
    with pytest.raises(ValueError, match="both preserve and forget"):
        _validate_view_contract(
            ViewContract(
                "bad",
                "BadTarget",
                ("occurrence-ledger", "ordered-history"),
                ("ordered-history",),
                (),
            )
        )
    with pytest.raises(ValueError, match="kernel"):
        _validate_view_contract(
            ViewContract(
                "bad",
                "BadTarget",
                ("occurrence-ledger",),
                ("metric",),
                ("history",),
            )
        )


def test_forged_relation_boundary_is_rejected() -> None:
    carrier = _m6()
    relation = carrier.relations[0]
    forged = RelationBoundary(
        relation.name,
        relation.kind,
        relation.source_thread,
        Thread(
            relation.target_thread.name,
            relation.target_thread.states,
            tuple(reversed(relation.target_thread.steps)),
        ),
        relation.circle_order,
    )

    with pytest.raises(ValueError, match="step boundaries"):
        _validate_carrier(
            StratifiedCarrier(
                carrier.name,
                carrier.states,
                carrier.steps,
                (forged,),
                carrier.fillers,
            )
        )


def test_to24_is_the_finite_q4_m6_coherence_envelope() -> None:
    envelope = _to24()
    _validate_to24(envelope)

    assert len(envelope.states) == 24
    assert len(envelope.edges) == 36
    assert Counter(face.kind for face in envelope.faces) == Counter(
        {RelationKind.INTERCHANGE: 6, RelationKind.BRAID: 8}
    )


def test_nonempty_relation_words_return_to_identity_without_becoming_empty() -> None:
    identity: PermutationState = ("0", "K", "X", "t")
    square_word = (0, 2, 0, 2)
    left_hexagon_word = (0, 1, 0, 1, 0, 1)
    right_hexagon_word = (1, 2, 1, 2, 1, 2)

    assert square_word and _act(identity, square_word) == identity
    assert left_hexagon_word and _act(identity, left_hexagon_word) == identity
    assert right_hexagon_word and _act(identity, right_hexagon_word) == identity
    assert square_word != ()
    assert left_hexagon_word != ()
    assert right_hexagon_word != ()
