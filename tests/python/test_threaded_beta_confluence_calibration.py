from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from itertools import product
from typing import Literal, TypeAlias

import pytest

import test_threaded_beta_transport_calibration as beta
import test_threaded_natural_deduction_calibration as nd


ProofPosition = beta.ProofPosition
PositionKind: TypeAlias = Literal["same", "independent", "nested"]
NestedShape: TypeAlias = Literal[
    "outer-argument",
    "outer-body-off-spine",
    "outer-body-x-in-inner-body",
    "outer-body-x-in-inner-argument",
]
ResidualKind: TypeAlias = Literal[
    "independent",
    "ancestor",
    "body-projection",
    "argument-graft",
]


@dataclass(frozen=True)
class BetaRedexAuthority:
    occurrence_key: tuple[nd.ScopeId, nd.OccurrenceId]
    resource_source_id: nd.ResourceSourceId
    binder_id: nd.BinderId


@dataclass(frozen=True)
class BetaHistoryEvent:
    event_id: beta.BetaEventId
    authority: BetaRedexAuthority
    selected_path: ProofPosition


@dataclass(frozen=True)
class BetaHistory:
    events: tuple[BetaHistoryEvent, ...]


@dataclass(frozen=True)
class CompositeSurvivorEmbedding:
    occurrence_key: tuple[nd.ScopeId, nd.OccurrenceId]
    source_index: int
    result_index: int
    source_use: nd.ResourceUse
    result_use: nd.ResourceUse


@dataclass(frozen=True)
class CompositeBoundaryTransport:
    source: nd.NDProof
    result: nd.NDProof
    survivor_partial_bijection: tuple[
        CompositeSurvivorEmbedding, ...
    ]
    retired_authorities: frozenset[BetaRedexAuthority]
    boundary_context: nd.Context
    boundary_conclusion: nd.Formula
    source_node_count: int
    result_node_count: int
    source_discharged_count: int
    result_discharged_count: int

    @property
    def node_count_decrease(self) -> int:
        return self.source_node_count - self.result_node_count

    @property
    def discharged_decrease(self) -> int:
        return (
            self.source_discharged_count
            - self.result_discharged_count
        )


@dataclass(frozen=True)
class PositionRelation:
    kind: PositionKind
    outer_path: ProofPosition | None
    inner_path: ProofPosition | None


@dataclass(frozen=True)
class ResidualWitness:
    contracted_event: BetaHistoryEvent
    residual_authority: BetaRedexAuthority
    original_path: ProofPosition
    residual_path: ProofPosition
    relation: PositionRelation
    residual_kind: ResidualKind


@dataclass(frozen=True)
class BetaRoute:
    history: BetaHistory
    corners: tuple[nd.NDProof, ...]
    endpoint: nd.NDProof
    composite: CompositeBoundaryTransport


@dataclass(frozen=True)
class InterchangeCell:
    source: nd.NDProof
    left_event_id: beta.BetaEventId
    right_event_id: beta.BetaEventId
    left_path: ProofPosition
    right_path: ProofPosition
    right_after_left: ResidualWitness
    left_after_right: ResidualWitness
    left_then_right: BetaRoute
    right_then_left: BetaRoute


@dataclass(frozen=True)
class NestedCoherenceCell:
    source: nd.NDProof
    shape: NestedShape
    outer_event_id: beta.BetaEventId
    inner_event_id: beta.BetaEventId
    outer_path: ProofPosition
    inner_path: ProofPosition
    inner_after_outer: ResidualWitness
    outer_after_inner: ResidualWitness
    outer_then_inner: BetaRoute
    inner_then_outer: BetaRoute


Cell: TypeAlias = InterchangeCell | NestedCoherenceCell


@dataclass(frozen=True)
class Peak:
    name: str
    source: nd.NDProof
    left_name: str
    right_name: str
    left_path: ProofPosition
    right_path: ProofPosition


def _valid_authority(value: object) -> bool:
    return (
        type(value) is BetaRedexAuthority
        and type(value.occurrence_key) is tuple
        and len(value.occurrence_key) == 2
        and type(value.occurrence_key[0]) is nd.ScopeId
        and type(value.occurrence_key[1]) is nd.OccurrenceId
        and type(value.resource_source_id) is nd.ResourceSourceId
        and type(value.binder_id) is nd.BinderId
    )


def _valid_history_event(value: object) -> bool:
    return (
        type(value) is BetaHistoryEvent
        and type(value.event_id) is beta.BetaEventId
        and type(value.event_id.value) is str
        and bool(value.event_id.value)
        and _valid_authority(value.authority)
        and beta._is_valid_proof_position(value.selected_path)
    )


def _valid_position_relation(value: object) -> bool:
    if type(value) is not PositionRelation:
        return False
    if value.kind not in {"same", "independent", "nested"}:
        return False
    for position in (value.outer_path, value.inner_path):
        if position is not None and not beta._is_valid_proof_position(
            position
        ):
            return False
    if value.kind == "independent":
        return value.outer_path is None and value.inner_path is None
    if value.outer_path is None or value.inner_path is None:
        return False
    if value.kind == "same":
        return value.outer_path == value.inner_path
    return (
        len(value.outer_path) < len(value.inner_path)
        and value.inner_path[: len(value.outer_path)] == value.outer_path
    )


def _event_authorities_are_injective(
    events: tuple[BetaHistoryEvent, ...],
) -> bool:
    event_map: dict[beta.BetaEventId, BetaRedexAuthority] = {}
    for event in events:
        previous = event_map.get(event.event_id)
        if previous is not None and previous != event.authority:
            return False
        event_map[event.event_id] = event.authority
    return len(event_map) == len(events)


def _authority_from_transport(
    transport: beta.ContextualBetaTransport,
) -> BetaRedexAuthority:
    retired = transport.local.retired_target
    hypothesis = retired.hypothesis
    assert retired.binder_id is not None
    return BetaRedexAuthority(
        occurrence_key=nd._occurrence_key(hypothesis),
        resource_source_id=hypothesis.resource_source_id,
        binder_id=retired.binder_id,
    )


def _authority_matches_use(
    authority: BetaRedexAuthority,
    use: nd.ResourceUse,
) -> bool:
    return (
        nd._occurrence_key(use.hypothesis) == authority.occurrence_key
        and use.hypothesis.resource_source_id
        == authority.resource_source_id
        and use.binder_id == authority.binder_id
        and use.status == "discharged"
    )


def _contract(
    source: nd.NDProof,
    position: ProofPosition,
    event_id: beta.BetaEventId,
) -> tuple[nd.NDProof, beta.ContextualBetaTransport] | None:
    if type(source) is not nd.NDProof or not nd._check_proof(source):
        return None
    if not beta._is_valid_proof_position(position):
        return None
    if type(event_id) is not beta.BetaEventId:
        return None
    try:
        outcome = beta._contextual_beta_transport(
            source,
            position,
            event=event_id.value,
        )
    except (AttributeError, IndexError, TypeError, ValueError):
        return None
    if not isinstance(outcome, beta.ContextualBetaSucceeded):
        return None
    if not beta._check_contextual_beta_transport(outcome.transport):
        return None
    return outcome.transport.result, outcome.transport


def _redex_authority_at(
    source: nd.NDProof,
    position: ProofPosition,
) -> BetaRedexAuthority | None:
    contracted = _contract(
        source,
        position,
        beta.BetaEventId("beta:authority-probe"),
    )
    if contracted is None:
        return None
    return _authority_from_transport(contracted[1])


def _position_relation(
    left: object,
    right: object,
) -> PositionRelation | None:
    if not beta._is_valid_proof_position(left):
        return None
    if not beta._is_valid_proof_position(right):
        return None
    left_position = left
    right_position = right
    if left_position == right_position:
        return PositionRelation("same", left_position, right_position)
    common = min(len(left_position), len(right_position))
    first_difference = next(
        (
            index
            for index in range(common)
            if left_position[index] != right_position[index]
        ),
        None,
    )
    if first_difference is not None:
        return PositionRelation("independent", None, None)
    if len(left_position) < len(right_position):
        return PositionRelation("nested", left_position, right_position)
    return PositionRelation("nested", right_position, left_position)


def _make_history_event(
    source: nd.NDProof,
    position: ProofPosition,
    event_id: beta.BetaEventId,
) -> BetaHistoryEvent | None:
    if type(event_id) is not beta.BetaEventId:
        return None
    authority = _redex_authority_at(source, position)
    if authority is None:
        return None
    return BetaHistoryEvent(event_id, authority, position)


def _replay_history(
    source: nd.NDProof,
    history: BetaHistory,
) -> tuple[nd.NDProof, tuple[nd.NDProof, ...]] | None:
    if type(source) is not nd.NDProof or not nd._check_proof(source):
        return None
    if type(history) is not BetaHistory:
        return None
    if type(history.events) is not tuple:
        return None
    if not all(_valid_history_event(event) for event in history.events):
        return None
    if not _event_authorities_are_injective(history.events):
        return None
    current = source
    corners: list[nd.NDProof] = []
    for event in history.events:
        contracted = _contract(
            current,
            event.selected_path,
            event.event_id,
        )
        if contracted is None:
            return None
        current, transport = contracted
        if _authority_from_transport(transport) != event.authority:
            return None
        corners.append(current)
    return current, tuple(corners)


def _make_composite(
    source: nd.NDProof,
    result: nd.NDProof,
    retired_authorities: frozenset[BetaRedexAuthority],
) -> CompositeBoundaryTransport | None:
    if type(source) is not nd.NDProof or not nd._check_proof(source):
        return None
    if type(result) is not nd.NDProof or not nd._check_proof(result):
        return None
    if type(retired_authorities) is not frozenset:
        return None
    if not all(
        _valid_authority(authority)
        for authority in retired_authorities
    ):
        return None
    retired_source_indices: set[int] = set()
    for authority in retired_authorities:
        matches = {
            index
            for index, use in enumerate(source.ledger)
            if _authority_matches_use(authority, use)
        }
        if len(matches) != 1:
            return None
        if any(
            _authority_matches_use(authority, use)
            for use in result.ledger
        ):
            return None
        retired_source_indices.update(matches)
    if len(retired_source_indices) != len(retired_authorities):
        return None

    embeddings: list[CompositeSurvivorEmbedding] = []
    for result_index, result_use in enumerate(result.ledger):
        source_indices = tuple(
            index
            for index, source_use in enumerate(source.ledger)
            if index not in retired_source_indices
            and source_use == result_use
        )
        if len(source_indices) != 1:
            return None
        source_index = source_indices[0]
        embeddings.append(
            CompositeSurvivorEmbedding(
                occurrence_key=nd._occurrence_key(
                    result_use.hypothesis
                ),
                source_index=source_index,
                result_index=result_index,
                source_use=source.ledger[source_index],
                result_use=result_use,
            )
        )
    source_survivors = {
        index
        for index in range(len(source.ledger))
        if index not in retired_source_indices
    }
    if {item.source_index for item in embeddings} != source_survivors:
        return None
    if {item.result_index for item in embeddings} != set(
        range(len(result.ledger))
    ):
        return None
    if source.context != result.context:
        return None
    if source.conclusion != result.conclusion:
        return None
    return CompositeBoundaryTransport(
        source=source,
        result=result,
        survivor_partial_bijection=tuple(embeddings),
        retired_authorities=retired_authorities,
        boundary_context=source.context,
        boundary_conclusion=source.conclusion,
        source_node_count=beta._proof_node_count(source),
        result_node_count=beta._proof_node_count(result),
        source_discharged_count=beta._discharged_count(source.ledger),
        result_discharged_count=beta._discharged_count(result.ledger),
    )


def _check_composite(transport: CompositeBoundaryTransport) -> bool:
    if type(transport) is not CompositeBoundaryTransport:
        return False
    if type(transport.survivor_partial_bijection) is not tuple:
        return False
    if type(transport.retired_authorities) is not frozenset:
        return False
    if any(
        type(value) is not int
        for value in (
            transport.source_node_count,
            transport.result_node_count,
            transport.source_discharged_count,
            transport.result_discharged_count,
        )
    ):
        return False
    for embedding in transport.survivor_partial_bijection:
        if type(embedding) is not CompositeSurvivorEmbedding:
            return False
        if type(embedding.source_index) is not int:
            return False
        if type(embedding.result_index) is not int:
            return False
        if type(embedding.source_use) is not nd.ResourceUse:
            return False
        if type(embedding.result_use) is not nd.ResourceUse:
            return False
        if (
            type(embedding.occurrence_key) is not tuple
            or len(embedding.occurrence_key) != 2
            or type(embedding.occurrence_key[0]) is not nd.ScopeId
            or type(embedding.occurrence_key[1]) is not nd.OccurrenceId
        ):
            return False
    try:
        replay = _make_composite(
            transport.source,
            transport.result,
            transport.retired_authorities,
        )
    except (AttributeError, IndexError, TypeError, ValueError):
        return False
    return replay == transport


def _make_route(
    source: nd.NDProof,
    events: tuple[BetaHistoryEvent, ...],
) -> BetaRoute | None:
    if type(events) is not tuple:
        return None
    if not all(_valid_history_event(event) for event in events):
        return None
    if not _event_authorities_are_injective(events):
        return None
    history = BetaHistory(events)
    replay = _replay_history(source, history)
    if replay is None:
        return None
    endpoint, corners = replay
    authorities = frozenset(event.authority for event in events)
    if len(authorities) != len(events):
        return None
    composite = _make_composite(source, endpoint, authorities)
    if composite is None:
        return None
    return BetaRoute(history, corners, endpoint, composite)


def _check_route(source: nd.NDProof, route: BetaRoute) -> bool:
    if type(route) is not BetaRoute:
        return False
    if type(route.history) is not BetaHistory:
        return False
    if type(route.history.events) is not tuple:
        return False
    if type(route.corners) is not tuple:
        return False
    if type(route.endpoint) is not nd.NDProof:
        return False
    try:
        replay = _make_route(source, route.history.events)
    except (AttributeError, IndexError, TypeError, ValueError):
        return False
    return replay == route and _check_composite(route.composite)


def _expected_residual(
    source: nd.NDProof,
    contracted_path: ProofPosition,
    original_path: ProofPosition,
    transport: beta.ContextualBetaTransport,
) -> tuple[ProofPosition, ResidualKind] | None:
    relation = _position_relation(contracted_path, original_path)
    if relation is None or relation.kind == "same":
        return None
    if relation.kind == "independent":
        return original_path, "independent"
    if relation.outer_path == original_path:
        return original_path, "ancestor"
    if relation.outer_path != contracted_path:
        return None

    relative = original_path[len(contracted_path) :]
    if relative[:1] == (1,):
        return (
            (
                *contracted_path,
                *transport.local.target_leaf_path,
                *relative[1:],
            ),
            "argument-graft",
        )
    if relative[:2] == (0, 0):
        return (
            (*contracted_path, *relative[2:]),
            "body-projection",
        )
    return None


def _make_residual_witness(
    source: nd.NDProof,
    contracted_event: BetaHistoryEvent,
    original_path: ProofPosition,
) -> ResidualWitness | None:
    residual_authority = _redex_authority_at(source, original_path)
    if residual_authority is None:
        return None
    contracted = _contract(
        source,
        contracted_event.selected_path,
        contracted_event.event_id,
    )
    if contracted is None:
        return None
    result, transport = contracted
    if _authority_from_transport(transport) != contracted_event.authority:
        return None
    expected = _expected_residual(
        source,
        contracted_event.selected_path,
        original_path,
        transport,
    )
    if expected is None:
        return None
    residual_path, residual_kind = expected
    if _redex_authority_at(result, residual_path) != residual_authority:
        return None
    relation = _position_relation(
        contracted_event.selected_path,
        original_path,
    )
    assert relation is not None
    return ResidualWitness(
        contracted_event=contracted_event,
        residual_authority=residual_authority,
        original_path=original_path,
        residual_path=residual_path,
        relation=relation,
        residual_kind=residual_kind,
    )


def _check_residual_witness(
    source: nd.NDProof,
    witness: ResidualWitness,
) -> bool:
    if type(witness) is not ResidualWitness:
        return False
    if not _valid_history_event(witness.contracted_event):
        return False
    if not _valid_authority(witness.residual_authority):
        return False
    if not beta._is_valid_proof_position(witness.original_path):
        return False
    if not beta._is_valid_proof_position(witness.residual_path):
        return False
    if not _valid_position_relation(witness.relation):
        return False
    if witness.residual_kind not in {
        "independent",
        "ancestor",
        "body-projection",
        "argument-graft",
    }:
        return False
    try:
        replay = _make_residual_witness(
            source,
            witness.contracted_event,
            witness.original_path,
        )
    except (AttributeError, IndexError, TypeError, ValueError):
        return False
    return replay == witness


def _make_interchange_cell(
    source: nd.NDProof,
    left_path: ProofPosition,
    right_path: ProofPosition,
    left_event_id: beta.BetaEventId,
    right_event_id: beta.BetaEventId,
) -> InterchangeCell | None:
    if type(left_event_id) is not beta.BetaEventId:
        return None
    if type(right_event_id) is not beta.BetaEventId:
        return None
    if left_event_id == right_event_id:
        return None
    relation = _position_relation(left_path, right_path)
    if relation is None or relation.kind != "independent":
        return None
    left_event = _make_history_event(source, left_path, left_event_id)
    right_event = _make_history_event(source, right_path, right_event_id)
    if left_event is None or right_event is None:
        return None
    right_after_left = _make_residual_witness(
        source,
        left_event,
        right_path,
    )
    left_after_right = _make_residual_witness(
        source,
        right_event,
        left_path,
    )
    if right_after_left is None or left_after_right is None:
        return None
    right_residual_event = BetaHistoryEvent(
        right_event_id,
        right_event.authority,
        right_after_left.residual_path,
    )
    left_residual_event = BetaHistoryEvent(
        left_event_id,
        left_event.authority,
        left_after_right.residual_path,
    )
    left_then_right = _make_route(
        source,
        (left_event, right_residual_event),
    )
    right_then_left = _make_route(
        source,
        (right_event, left_residual_event),
    )
    if left_then_right is None or right_then_left is None:
        return None
    if left_then_right.endpoint != right_then_left.endpoint:
        return None
    if left_then_right.composite != right_then_left.composite:
        return None
    if left_then_right.history == right_then_left.history:
        return None
    return InterchangeCell(
        source=source,
        left_event_id=left_event_id,
        right_event_id=right_event_id,
        left_path=left_path,
        right_path=right_path,
        right_after_left=right_after_left,
        left_after_right=left_after_right,
        left_then_right=left_then_right,
        right_then_left=right_then_left,
    )


def _check_interchange_cell(cell: InterchangeCell) -> bool:
    if type(cell) is not InterchangeCell:
        return False
    if type(cell.left_event_id) is not beta.BetaEventId:
        return False
    if type(cell.right_event_id) is not beta.BetaEventId:
        return False
    try:
        replay = _make_interchange_cell(
            cell.source,
            cell.left_path,
            cell.right_path,
            cell.left_event_id,
            cell.right_event_id,
        )
    except (AttributeError, IndexError, TypeError, ValueError):
        return False
    return replay == cell


def _nested_shape(
    source: nd.NDProof,
    outer_path: ProofPosition,
    inner_path: ProofPosition,
) -> NestedShape | None:
    relation = _position_relation(outer_path, inner_path)
    if (
        relation is None
        or relation.kind != "nested"
        or relation.outer_path != outer_path
    ):
        return None
    outer_event = _make_history_event(
        source,
        outer_path,
        beta.BetaEventId("beta:shape-probe"),
    )
    if outer_event is None:
        return None
    contracted = _contract(source, outer_path, outer_event.event_id)
    if contracted is None:
        return None
    local = contracted[1].local
    relative = inner_path[len(outer_path) :]
    if relative[:1] == (1,):
        return "outer-argument"
    if relative[:2] != (0, 0):
        return None
    body_inner_path = relative[2:]
    target_path = local.target_leaf_path
    if target_path[: len(body_inner_path)] != body_inner_path:
        return "outer-body-off-spine"
    inside_inner = target_path[len(body_inner_path) :]
    if inside_inner[:2] == (0, 0):
        return "outer-body-x-in-inner-body"
    if inside_inner[:1] == (1,):
        return "outer-body-x-in-inner-argument"
    return None


def _make_nested_cell(
    source: nd.NDProof,
    outer_path: ProofPosition,
    inner_path: ProofPosition,
    outer_event_id: beta.BetaEventId,
    inner_event_id: beta.BetaEventId,
) -> NestedCoherenceCell | None:
    if type(outer_event_id) is not beta.BetaEventId:
        return None
    if type(inner_event_id) is not beta.BetaEventId:
        return None
    if outer_event_id == inner_event_id:
        return None
    shape = _nested_shape(source, outer_path, inner_path)
    if shape is None:
        return None
    outer_event = _make_history_event(source, outer_path, outer_event_id)
    inner_event = _make_history_event(source, inner_path, inner_event_id)
    if outer_event is None or inner_event is None:
        return None
    inner_after_outer = _make_residual_witness(
        source,
        outer_event,
        inner_path,
    )
    outer_after_inner = _make_residual_witness(
        source,
        inner_event,
        outer_path,
    )
    if inner_after_outer is None or outer_after_inner is None:
        return None
    inner_residual_event = BetaHistoryEvent(
        inner_event_id,
        inner_event.authority,
        inner_after_outer.residual_path,
    )
    outer_residual_event = BetaHistoryEvent(
        outer_event_id,
        outer_event.authority,
        outer_after_inner.residual_path,
    )
    outer_then_inner = _make_route(
        source,
        (outer_event, inner_residual_event),
    )
    inner_then_outer = _make_route(
        source,
        (inner_event, outer_residual_event),
    )
    if outer_then_inner is None or inner_then_outer is None:
        return None
    if outer_then_inner.endpoint != inner_then_outer.endpoint:
        return None
    if outer_then_inner.composite != inner_then_outer.composite:
        return None
    return NestedCoherenceCell(
        source=source,
        shape=shape,
        outer_event_id=outer_event_id,
        inner_event_id=inner_event_id,
        outer_path=outer_path,
        inner_path=inner_path,
        inner_after_outer=inner_after_outer,
        outer_after_inner=outer_after_inner,
        outer_then_inner=outer_then_inner,
        inner_then_outer=inner_then_outer,
    )


def _check_nested_cell(cell: NestedCoherenceCell) -> bool:
    if type(cell) is not NestedCoherenceCell:
        return False
    if type(cell.outer_event_id) is not beta.BetaEventId:
        return False
    if type(cell.inner_event_id) is not beta.BetaEventId:
        return False
    try:
        replay = _make_nested_cell(
            cell.source,
            cell.outer_path,
            cell.inner_path,
            cell.outer_event_id,
            cell.inner_event_id,
        )
    except (AttributeError, IndexError, TypeError, ValueError):
        return False
    return replay == cell


def _hypothesis(
    label: str,
    formula: nd.Formula,
    *,
    stem: str,
    domain: nd.ResourceDomainName,
) -> nd.HypothesisOccurrence:
    return beta._hypothesis(
        label,
        formula,
        source=f"source:confluence:{stem}:{label}",
        occurrence=f"occurrence:confluence:{stem}:{label}",
        domain=domain,
    )


def _identity_redex(
    formula: nd.Formula,
    *,
    stem: str,
    domain: nd.ResourceDomainName,
) -> tuple[nd.NDProof, nd.NDProof]:
    return beta._identity_redex(
        formula,
        stem=f"confluence:{stem}",
        target_domain=domain,
        argument_domain=domain,
    )


def _independent_peak(stem: str = "independent") -> Peak:
    premise = nd.Atom("K")
    result = nd.Atom("X")
    function_type = nd.RightLinearImplication(premise, result)
    function_redex, _ = _identity_redex(
        function_type,
        stem=f"{stem}:function",
        domain="K",
    )
    argument_redex, _ = _identity_redex(
        premise,
        stem=f"{stem}:argument",
        domain="X",
    )
    source = nd._right_implication_elimination(
        function_redex,
        argument_redex,
    ).proof
    assert source is not None
    return Peak(
        "independent",
        source,
        "function",
        "argument",
        (0,),
        (1,),
    )


def _outer_argument_peak(stem: str = "outer-argument") -> Peak:
    formula = nd.Atom("K")
    inner_redex, _ = _identity_redex(
        formula,
        stem=f"{stem}:inner",
        domain="X",
    )
    target = _hypothesis(
        "target",
        formula,
        stem=stem,
        domain="K",
    )
    abstraction = nd._right_implication_introduction(
        target,
        nd._assume(target),
        binder=f"binder:confluence:{stem}:target",
    )
    source = nd._right_implication_elimination(
        abstraction,
        inner_redex,
    ).proof
    assert source is not None
    return Peak("outer-argument", source, "outer", "inner", (), (1,))


def _outer_argument_nonempty_graft_peak(
    stem: str = "outer-argument-nonempty-graft",
) -> Peak:
    atom = nd.Atom("K")
    result = nd.Atom("X")
    closed_type = nd.RightLinearImplication(atom, atom)
    target_type = nd.RightLinearImplication(closed_type, result)

    target = _hypothesis("target", target_type, stem=stem, domain="K")
    closed_target = _hypothesis(
        "closed-target",
        atom,
        stem=stem,
        domain="X",
    )
    closed_argument = nd._right_implication_introduction(
        closed_target,
        nd._assume(closed_target),
        binder=f"binder:confluence:{stem}:closed-target",
    )
    outer_body = nd._right_implication_elimination(
        nd._assume(target),
        closed_argument,
    ).proof
    assert outer_body is not None
    outer_abstraction = nd._right_implication_introduction(
        target,
        outer_body,
        binder=f"binder:confluence:{stem}:target",
    )

    inner_redex, _ = _identity_redex(
        target_type,
        stem=f"{stem}:inner",
        domain="t",
    )
    replacement_target = _hypothesis(
        "replacement-target",
        closed_type,
        stem=stem,
        domain="X",
    )
    replacement_body = nd._right_implication_elimination(
        inner_redex,
        nd._assume(replacement_target),
    ).proof
    assert replacement_body is not None
    replacement = nd._right_implication_introduction(
        replacement_target,
        replacement_body,
        binder=f"binder:confluence:{stem}:replacement-target",
    )
    source = nd._right_implication_elimination(
        outer_abstraction,
        replacement,
    ).proof
    assert source is not None
    return Peak(
        "outer-argument-nonempty-graft",
        source,
        "outer",
        "inner",
        (),
        (1, 0, 0),
    )


def _outer_body_off_spine_peak(
    stem: str = "outer-body-off-spine",
) -> Peak:
    premise = nd.Atom("K")
    result = nd.Atom("X")
    function_type = nd.RightLinearImplication(premise, result)
    inner_redex, _ = _identity_redex(
        function_type,
        stem=f"{stem}:inner",
        domain="K",
    )
    target = _hypothesis("target", premise, stem=stem, domain="X")
    body = nd._right_implication_elimination(
        inner_redex,
        nd._assume(target),
    ).proof
    assert body is not None
    abstraction = nd._right_implication_introduction(
        target,
        body,
        binder=f"binder:confluence:{stem}:target",
    )
    replacement = _hypothesis(
        "replacement",
        premise,
        stem=stem,
        domain="t",
    )
    source = nd._right_implication_elimination(
        abstraction,
        nd._assume(replacement),
    ).proof
    assert source is not None
    return Peak(
        "outer-body-off-spine",
        source,
        "outer",
        "inner",
        (),
        (0, 0, 0),
    )


def _outer_body_x_in_inner_body_peak(
    stem: str = "outer-body-x-in-inner-body",
) -> Peak:
    atom = nd.Atom("K")
    result = nd.Atom("X")
    premise = nd.RightLinearImplication(atom, atom)
    target_type = nd.RightLinearImplication(premise, result)
    target = _hypothesis("target", target_type, stem=stem, domain="K")
    inner_target = _hypothesis(
        "inner-target",
        premise,
        stem=stem,
        domain="X",
    )
    inner_body = nd._right_implication_elimination(
        nd._assume(target),
        nd._assume(inner_target),
    ).proof
    assert inner_body is not None
    inner_abstraction = nd._right_implication_introduction(
        inner_target,
        inner_body,
        binder=f"binder:confluence:{stem}:inner-target",
    )
    closed_target = _hypothesis(
        "closed-target",
        atom,
        stem=stem,
        domain="t",
    )
    inner_argument = nd._right_implication_introduction(
        closed_target,
        nd._assume(closed_target),
        binder=f"binder:confluence:{stem}:closed-target",
    )
    body = nd._right_implication_elimination(
        inner_abstraction,
        inner_argument,
    ).proof
    assert body is not None
    outer_abstraction = nd._right_implication_introduction(
        target,
        body,
        binder=f"binder:confluence:{stem}:target",
    )
    replacement = _hypothesis(
        "replacement",
        target_type,
        stem=stem,
        domain="t",
    )
    source = nd._right_implication_elimination(
        outer_abstraction,
        nd._assume(replacement),
    ).proof
    assert source is not None
    return Peak(
        "outer-body-x-in-inner-body",
        source,
        "outer",
        "inner",
        (),
        (0, 0),
    )


def _outer_body_x_in_inner_argument_peak(
    stem: str = "outer-body-x-in-inner-argument",
) -> Peak:
    formula = nd.Atom("K")
    target = _hypothesis("target", formula, stem=stem, domain="K")
    inner_target = _hypothesis(
        "inner-target",
        formula,
        stem=stem,
        domain="X",
    )
    inner_abstraction = nd._right_implication_introduction(
        inner_target,
        nd._assume(inner_target),
        binder=f"binder:confluence:{stem}:inner-target",
    )
    body = nd._right_implication_elimination(
        inner_abstraction,
        nd._assume(target),
    ).proof
    assert body is not None
    outer_abstraction = nd._right_implication_introduction(
        target,
        body,
        binder=f"binder:confluence:{stem}:target",
    )
    replacement = _hypothesis(
        "replacement",
        formula,
        stem=stem,
        domain="t",
    )
    source = nd._right_implication_elimination(
        outer_abstraction,
        nd._assume(replacement),
    ).proof
    assert source is not None
    return Peak(
        "outer-body-x-in-inner-argument",
        source,
        "outer",
        "inner",
        (),
        (0, 0),
    )


def _prefix_peak(
    peak: Peak,
    source: nd.NDProof,
    prefix: ProofPosition,
    name: str,
) -> Peak:
    return Peak(
        name,
        source,
        peak.left_name,
        peak.right_name,
        (*prefix, *peak.left_path),
        (*prefix, *peak.right_path),
    )


def _elimination_whisker(peak: Peak, stem: str) -> Peak:
    result = nd.Atom("t")
    function = _hypothesis(
        "whisker-function",
        nd.RightLinearImplication(peak.source.conclusion, result),
        stem=stem,
        domain="K",
    )
    source = nd._right_implication_elimination(
        nd._assume(function),
        peak.source,
    ).proof
    assert source is not None
    return _prefix_peak(peak, source, (1,), f"{peak.name}:E")


def _function_elimination_whisker(peak: Peak, stem: str) -> Peak:
    introduced = _introduction_whisker(peak, f"{stem}:I")
    conclusion = introduced.source.conclusion
    assert isinstance(conclusion, nd.RightLinearImplication)
    argument = _hypothesis(
        "function-whisker-argument",
        conclusion.premise,
        stem=stem,
        domain="t",
    )
    source = nd._right_implication_elimination(
        introduced.source,
        nd._assume(argument),
    ).proof
    assert source is not None
    return _prefix_peak(
        introduced,
        source,
        (0,),
        f"{peak.name}:E0",
    )


def _introduction_whisker(peak: Peak, stem: str) -> Peak:
    assert peak.source.context
    principal = peak.source.context[-1]
    source = nd._right_implication_introduction(
        principal,
        peak.source,
        binder=f"binder:confluence:{stem}:whisker",
    )
    return _prefix_peak(peak, source, (0,), f"{peak.name}:I")


def _deep_whisker(peak: Peak, depth: int) -> Peak:
    current = peak
    for index in range(depth):
        current = _elimination_whisker(
            current,
            f"{peak.name}:depth:{depth}:E:{index}",
        )
        if index % 2 == 1:
            current = _introduction_whisker(
                current,
                f"{peak.name}:depth:{depth}:I:{index}",
            )
    return current


def _make_cell(peak: Peak) -> Cell | None:
    relation = _position_relation(peak.left_path, peak.right_path)
    if relation is None:
        return None
    left_event = beta.BetaEventId(f"beta:{peak.name}:{peak.left_name}")
    right_event = beta.BetaEventId(f"beta:{peak.name}:{peak.right_name}")
    if relation.kind == "independent":
        return _make_interchange_cell(
            peak.source,
            peak.left_path,
            peak.right_path,
            left_event,
            right_event,
        )
    if relation.kind != "nested":
        return None
    assert relation.outer_path is not None
    assert relation.inner_path is not None
    if peak.left_path == relation.outer_path:
        outer_event, inner_event = left_event, right_event
    else:
        outer_event, inner_event = right_event, left_event
    return _make_nested_cell(
        peak.source,
        relation.outer_path,
        relation.inner_path,
        outer_event,
        inner_event,
    )


def _check_cell(cell: Cell) -> bool:
    if isinstance(cell, InterchangeCell):
        return _check_interchange_cell(cell)
    return _check_nested_cell(cell)


def _normalize(
    source: nd.NDProof,
    *,
    choose_last: bool,
) -> BetaRoute:
    current = source
    events: list[BetaHistoryEvent] = []
    while beta._beta_redex_positions(current):
        positions = beta._beta_redex_positions(current)
        position = positions[-1] if choose_last else positions[0]
        event_id = beta.BetaEventId(
            f"beta:normalize:{len(events)}:{'last' if choose_last else 'first'}"
        )
        event = _make_history_event(current, position, event_id)
        assert event is not None
        events.append(event)
        contracted = _contract(current, position, event_id)
        assert contracted is not None
        current = contracted[0]
    route = _make_route(source, tuple(events))
    assert route is not None
    return route


def test_position_trichotomy_is_exhaustive_and_rejects_bool() -> None:
    positions = tuple(
        tuple(bits)
        for length in range(4)
        for bits in product((0, 1), repeat=length)
    )
    for left, right in product(positions, repeat=2):
        relation = _position_relation(left, right)
        assert relation is not None
        assert relation.kind in {"same", "independent", "nested"}
        assert sum(
            (
                left == right,
                relation.kind == "independent",
                relation.kind == "nested",
            )
        ) == 1
    for malformed in ((True,), (-1,), ("0",), (0.0,), [], None):
        assert _position_relation(malformed, ()) is None
        assert _position_relation((), malformed) is None


def test_same_position_has_one_deterministic_endpoint() -> None:
    source = _outer_argument_peak("same-position").source
    first_id = beta.BetaEventId("beta:same-position:first-name")
    second_id = beta.BetaEventId("beta:same-position:second-name")
    first_event = _make_history_event(source, (), first_id)
    second_event = _make_history_event(source, (), second_id)
    assert first_event is not None
    assert second_event is not None
    first_route = _make_route(source, (first_event,))
    second_route = _make_route(source, (second_event,))
    assert first_route is not None
    assert second_route is not None
    assert first_route.endpoint == second_route.endpoint
    assert first_route.composite == second_route.composite
    assert first_route.history != second_route.history


def test_independent_interchange_replays_exact_extensional_summary() -> None:
    cell = _make_cell(_independent_peak())
    assert isinstance(cell, InterchangeCell)
    assert _check_interchange_cell(cell)
    assert cell.left_then_right.endpoint == cell.right_then_left.endpoint
    assert cell.left_then_right.composite == cell.right_then_left.composite
    assert cell.left_then_right.history != cell.right_then_left.history
    assert Counter(cell.left_then_right.history.events) == Counter(
        cell.right_then_left.history.events
    )
    assert {
        event.authority for event in cell.left_then_right.history.events
    } == {
        event.authority for event in cell.right_then_left.history.events
    }
    composite = cell.left_then_right.composite
    assert composite.node_count_decrease == 6
    assert composite.discharged_decrease == 2
    assert len(composite.source.ledger) - len(composite.result.ledger) == 2
    assert all(
        item.source_use == item.result_use
        for item in composite.survivor_partial_bijection
    )


def test_each_route_step_and_two_step_measure_drop_is_exact() -> None:
    cell = _make_cell(_outer_body_x_in_inner_body_peak("measure"))
    assert isinstance(cell, NestedCoherenceCell)
    for route in (cell.outer_then_inner, cell.inner_then_outer):
        stages = (cell.source, *route.corners)
        assert len(stages) == 3
        for source, result in zip(stages[:-1], stages[1:], strict=True):
            assert (
                beta._proof_node_count(source)
                - beta._proof_node_count(result)
                == 3
            )
            assert (
                beta._discharged_count(source.ledger)
                - beta._discharged_count(result.ledger)
                == 1
            )
            assert len(source.ledger) - len(result.ledger) == 1
        assert route.composite.node_count_decrease == 6
        assert route.composite.discharged_decrease == 2
        assert (
            len(route.composite.source.ledger)
            - len(route.composite.result.ledger)
            == 2
        )


@pytest.mark.parametrize(
    ("factory", "shape", "residual_kind"),
    (
        (_outer_argument_peak, "outer-argument", "argument-graft"),
        (
            _outer_body_off_spine_peak,
            "outer-body-off-spine",
            "body-projection",
        ),
        (
            _outer_body_x_in_inner_body_peak,
            "outer-body-x-in-inner-body",
            "body-projection",
        ),
        (
            _outer_body_x_in_inner_argument_peak,
            "outer-body-x-in-inner-argument",
            "body-projection",
        ),
    ),
)
def test_nested_cells_replay_all_linear_substitution_shapes(
    factory,
    shape: NestedShape,
    residual_kind: ResidualKind,
) -> None:
    cell = _make_cell(factory())
    assert isinstance(cell, NestedCoherenceCell)
    assert _check_nested_cell(cell)
    assert cell.shape == shape
    assert cell.inner_after_outer.residual_kind == residual_kind
    assert cell.outer_after_inner.residual_kind == "ancestor"
    assert cell.outer_then_inner.endpoint == cell.inner_then_outer.endpoint
    assert cell.outer_then_inner.composite == cell.inner_then_outer.composite
    assert cell.outer_then_inner.history != cell.inner_then_outer.history
    assert cell.outer_then_inner.composite.node_count_decrease == 6
    assert cell.outer_then_inner.composite.discharged_decrease == 2


def test_outer_argument_residual_is_grafted_at_target_leaf() -> None:
    cell = _make_cell(_outer_argument_peak())
    assert isinstance(cell, NestedCoherenceCell)
    witness = cell.inner_after_outer
    assert witness.original_path == (1,)
    assert witness.residual_path == ()
    assert witness.residual_kind == "argument-graft"
    assert _check_residual_witness(cell.source, witness)


def test_outer_argument_graft_uses_nonempty_r_and_v_under_prefix() -> None:
    peak = _elimination_whisker(
        _outer_argument_nonempty_graft_peak(),
        "outer-argument-nonempty-graft:prefix",
    )
    cell = _make_cell(peak)
    assert isinstance(cell, NestedCoherenceCell)
    witness = cell.inner_after_outer
    p = (1,)
    r = (0,)
    v = (0, 0)
    assert cell.outer_path == p
    assert witness.original_path == (*p, 1, *v)
    assert witness.residual_path == (*p, *r, *v)
    assert witness.original_path != witness.residual_path
    assert witness.residual_kind == "argument-graft"
    contracted = _contract(
        cell.source,
        cell.outer_path,
        cell.inner_after_outer.contracted_event.event_id,
    )
    assert contracted is not None
    assert contracted[1].local.target_leaf_path == r
    assert _check_nested_cell(cell)


@pytest.mark.parametrize(
    "factory",
    (_independent_peak, _outer_argument_peak),
)
def test_cells_whisker_through_outer_introduction_and_elimination(
    factory,
) -> None:
    base = factory("whisker")
    for whiskered in (
        _introduction_whisker(base, f"{base.name}:I"),
        _elimination_whisker(base, f"{base.name}:E"),
    ):
        cell = _make_cell(whiskered)
        assert cell is not None
        assert _check_cell(cell)
        first_route = (
            cell.left_then_right
            if isinstance(cell, InterchangeCell)
            else cell.outer_then_inner
        )
        second_route = (
            cell.right_then_left
            if isinstance(cell, InterchangeCell)
            else cell.inner_then_outer
        )
        assert first_route.endpoint == second_route.endpoint
        assert first_route.composite == second_route.composite


def test_cells_replay_through_both_elimination_premises() -> None:
    base = _independent_peak("both-elimination-premises")
    argument_side = _elimination_whisker(base, "elimination-premise-1")
    function_side = _function_elimination_whisker(
        base,
        "elimination-premise-0",
    )
    assert argument_side.left_path[:1] == (1,)
    assert function_side.left_path[:1] == (0,)
    for peak in (argument_side, function_side):
        cell = _make_cell(peak)
        assert isinstance(cell, InterchangeCell)
        assert _check_interchange_cell(cell)
        assert cell.left_then_right.endpoint == cell.right_then_left.endpoint


@pytest.mark.parametrize(
    ("factory", "depth"),
    tuple(
        (factory, depth)
        for factory in (
            _independent_peak,
            _outer_argument_peak,
            _outer_body_off_spine_peak,
            _outer_body_x_in_inner_body_peak,
            _outer_body_x_in_inner_argument_peak,
        )
        for depth in range(9)
    ),
)
def test_deep_cell_search_has_no_endpoint_or_residual_path_drift(
    factory,
    depth: int,
) -> None:
    peak = _deep_whisker(factory(f"search:{depth}"), depth)
    cell = _make_cell(peak)
    assert cell is not None
    assert _check_cell(cell)


def test_replay_rejects_forged_corner_path_authority_map_history() -> None:
    cell = _make_cell(_independent_peak("forgery"))
    assert isinstance(cell, InterchangeCell)
    left_route = cell.left_then_right
    first_event = left_route.history.events[0]
    forged_authority = replace(
        first_event.authority,
        resource_source_id=nd.ResourceSourceId("source:forged"),
    )
    forged_corner_route = replace(
        left_route,
        corners=(cell.source, *left_route.corners[1:]),
    )
    forged_history_route = replace(
        left_route,
        history=BetaHistory(tuple(reversed(left_route.history.events))),
    )
    forged_authority_route = replace(
        left_route,
        history=BetaHistory(
            (
                replace(first_event, authority=forged_authority),
                *left_route.history.events[1:],
            )
        ),
    )
    forged_map = replace(
        left_route.composite,
        survivor_partial_bijection=(
            left_route.composite.survivor_partial_bijection[1:]
        ),
    )
    forged_map_route = replace(left_route, composite=forged_map)
    forged_endpoint_route = replace(left_route, endpoint=cell.source)
    forged_path = replace(
        cell.right_after_left,
        residual_path=(),
    )
    forged_relation = replace(
        cell.right_after_left,
        relation=PositionRelation("nested", (0,), (1,)),
    )

    assert not _check_route(cell.source, forged_corner_route)
    assert not _check_route(cell.source, forged_history_route)
    assert not _check_route(cell.source, forged_authority_route)
    assert not _check_route(cell.source, forged_map_route)
    assert not _check_route(cell.source, forged_endpoint_route)
    assert not _check_residual_witness(cell.source, forged_path)
    assert not _check_residual_witness(cell.source, forged_relation)
    assert not _check_interchange_cell(
        replace(cell, right_after_left=forged_path)
    )


def test_replay_rejects_unchecked_empty_and_exact_type_forgeries() -> None:
    cell = _make_cell(_independent_peak("exact-type-forgery"))
    assert isinstance(cell, InterchangeCell)
    route = cell.left_then_right
    event = route.history.events[0]
    unchecked = replace(cell.source, context=())
    assert not nd._check_proof(unchecked)

    fake_event_id = replace(
        event,
        event_id="beta:fake",  # type: ignore[arg-type]
    )
    list_history = replace(
        route.history,
        events=list(route.history.events),  # type: ignore[arg-type]
    )
    duplicate_id_event = replace(
        route.history.events[1],
        event_id=event.event_id,
    )
    retired_set = set(route.composite.retired_authorities)
    forged_retired_type = replace(
        route.composite,
        retired_authorities=retired_set,  # type: ignore[arg-type]
    )
    first_embedding = route.composite.survivor_partial_bijection[0]
    forged_bool_index = replace(first_embedding, source_index=True)
    forged_embedding = replace(
        route.composite,
        survivor_partial_bijection=(
            forged_bool_index,
            *route.composite.survivor_partial_bijection[1:],
        ),
    )
    forged_bool_count = replace(
        route.composite,
        source_node_count=True,
    )
    forged_bool_relation = replace(
        cell.right_after_left,
        relation=PositionRelation("nested", (True,), (True, 0)),
    )

    assert _replay_history(cell.source, list_history) is None
    assert _replay_history(
        cell.source,
        BetaHistory((fake_event_id,)),
    ) is None
    assert _replay_history(unchecked, route.history) is None
    assert _make_composite(
        unchecked,
        route.endpoint,
        frozenset(route.composite.retired_authorities),
    ) is None
    assert _make_composite(
        cell.source,
        route.endpoint,
        retired_set,  # type: ignore[arg-type]
    ) is None
    assert _make_route(
        cell.source,
        (event, duplicate_id_event),
    ) is None
    assert not _check_composite(forged_retired_type)
    assert not _check_composite(forged_embedding)
    assert not _check_composite(forged_bool_count)
    assert not _check_route(
        cell.source,
        replace(route, history=list_history),
    )
    assert not _check_route(
        cell.source,
        replace(
            route,
            history=BetaHistory((fake_event_id,)),
        ),
    )
    assert not _check_residual_witness(
        cell.source,
        forged_bool_relation,
    )
    assert _make_interchange_cell(
        cell.source,
        cell.left_path,
        cell.right_path,
        cell.left_event_id,
        cell.left_event_id,
    ) is None


def test_checked_empty_history_is_exact_identity_transport() -> None:
    _, source = _identity_redex(
        nd.Atom("K"),
        stem="checked-identity-route",
        domain="K",
    )
    history = BetaHistory(())
    assert beta._beta_redex_positions(source) == ()
    assert _replay_history(source, history) == (source, ())
    route = _make_route(source, ())
    assert route is not None
    assert _check_route(source, route)
    assert route.history == history
    assert route.corners == ()
    assert route.endpoint == source
    assert route.composite.source == source
    assert route.composite.result == source
    assert route.composite.retired_authorities == frozenset()
    assert route.composite.node_count_decrease == 0
    assert route.composite.discharged_decrease == 0
    assert tuple(
        item.source_use
        for item in route.composite.survivor_partial_bijection
    ) == source.ledger
    assert tuple(
        item.result_use
        for item in route.composite.survivor_partial_bijection
    ) == source.ledger
    assert _normalize(source, choose_last=False) == route
    assert _normalize(source, choose_last=True) == route


def test_unchecked_empty_history_identity_is_rejected() -> None:
    _, source = _identity_redex(
        nd.Atom("K"),
        stem="unchecked-identity-route",
        domain="X",
    )
    unchecked = replace(source, context=())
    assert not nd._check_proof(unchecked)
    assert _replay_history(unchecked, BetaHistory(())) is None
    assert _make_route(unchecked, ()) is None
    assert _make_composite(
        unchecked,
        unchecked,
        frozenset(),
    ) is None


def test_nested_replay_rejects_forged_shape_and_authority() -> None:
    cell = _make_cell(_outer_argument_peak("nested-forgery"))
    assert isinstance(cell, NestedCoherenceCell)
    forged_shape = replace(cell, shape="outer-body-off-spine")
    forged_authority = replace(
        cell.inner_after_outer.residual_authority,
        binder_id=nd.BinderId("binder:forged"),
    )
    forged_witness = replace(
        cell.inner_after_outer,
        residual_authority=forged_authority,
    )
    assert not _check_nested_cell(forged_shape)
    assert not _check_residual_witness(cell.source, forged_witness)
    assert not _check_nested_cell(
        replace(cell, inner_after_outer=forged_witness)
    )


@pytest.mark.parametrize(
    "factory",
    (
        _independent_peak,
        _outer_argument_peak,
        _outer_body_off_spine_peak,
        _outer_body_x_in_inner_body_peak,
        _outer_body_x_in_inner_argument_peak,
    ),
)
def test_leftmost_and_rightmost_strategies_have_one_exact_beta_nf(
    factory,
) -> None:
    source = _deep_whisker(factory("normal-form"), 3).source
    leftmost = _normalize(source, choose_last=False)
    rightmost = _normalize(source, choose_last=True)
    assert _check_route(source, leftmost)
    assert _check_route(source, rightmost)
    assert leftmost.endpoint == rightmost.endpoint
    assert leftmost.composite == rightmost.composite
    assert beta._beta_redex_positions(leftmost.endpoint) == ()
    assert beta._beta_redex_positions(rightmost.endpoint) == ()
    assert leftmost.history != rightmost.history
