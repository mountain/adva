from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from typing import Literal, TypeAlias

import test_threaded_natural_deduction_calibration as nd
import test_threaded_substitution_calibration as sub


SurvivorOrigin: TypeAlias = Literal[
    "body-prefix",
    "argument",
    "body-suffix",
]
ProofPosition: TypeAlias = tuple[int, ...]


@dataclass(frozen=True)
class BetaEventId:
    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value:
            raise ValueError("BetaEventId requires a nonempty string")


@dataclass(frozen=True)
class LocalSurvivorEmbedding:
    use: nd.ResourceUse
    occurrence_key: tuple[nd.ScopeId, nd.OccurrenceId]
    origin: SurvivorOrigin
    redex_index: int
    contractum_index: int


@dataclass(frozen=True)
class GlobalLedgerSurvivorEmbedding:
    occurrence_key: tuple[nd.ScopeId, nd.OccurrenceId]
    source_index: int
    result_index: int
    source_use: nd.ResourceUse
    result_use: nd.ResourceUse


@dataclass(frozen=True)
class LedgerBlockTransport:
    origin: SurvivorOrigin
    uses: nd.ResourceLedger
    redex_start: int
    contractum_start: int


@dataclass(frozen=True)
class AncestorTransportFrame:
    original: nd.NDProof
    premise_index: int
    rebuilt: nd.NDProof


@dataclass(frozen=True)
class RootBetaLedgerTransport:
    event_id: BetaEventId
    redex: nd.NDProof
    abstraction: nd.NDProof
    body: nd.NDProof
    replacement: nd.NDProof
    contractum: nd.NDProof
    substitution: sub.OrderedOneHoleSubstitutionCertificate
    target_leaf_path: ProofPosition
    target_open_use: nd.ResourceUse
    retired_target: nd.ResourceUse
    body_prefix: nd.ResourceLedger
    discharged_suffix: nd.ResourceLedger
    blocks: tuple[LedgerBlockTransport, ...]
    survivor_embeddings: tuple[LocalSurvivorEmbedding, ...]
    boundary_context: nd.Context
    boundary_conclusion: nd.Formula


@dataclass(frozen=True)
class RootBetaSucceeded:
    transport: RootBetaLedgerTransport


@dataclass(frozen=True)
class BetaRejected:
    obstruction: str


@dataclass(frozen=True)
class BetaInvariantViolation:
    obstruction: str


RootBetaOutcome: TypeAlias = (
    RootBetaSucceeded | BetaRejected | BetaInvariantViolation
)


@dataclass(frozen=True)
class ContextualBetaTransport:
    event_id: BetaEventId
    source: nd.NDProof
    position: ProofPosition
    local: RootBetaLedgerTransport
    frames_inner_to_outer: tuple[AncestorTransportFrame, ...]
    result: nd.NDProof
    retired_source_index: int
    survivor_embeddings: tuple[GlobalLedgerSurvivorEmbedding, ...]
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
class ContextualBetaSucceeded:
    transport: ContextualBetaTransport


ContextualBetaOutcome: TypeAlias = (
    ContextualBetaSucceeded | BetaRejected | BetaInvariantViolation
)


def _proof_node_count(proof: nd.NDProof) -> int:
    return 1 + sum(
        _proof_node_count(premise) for premise in proof.premises
    )


def _discharged_count(ledger: nd.ResourceLedger) -> int:
    return sum(use.status == "discharged" for use in ledger)


def _is_valid_proof_position(value: object) -> bool:
    return isinstance(value, tuple) and all(
        type(index) is int and index >= 0
        for index in value
    )


def _proof_at_position(
    proof: nd.NDProof,
    position: ProofPosition,
) -> nd.NDProof | None:
    if not _is_valid_proof_position(position):
        return None
    selected = proof
    for premise_index in position:
        if premise_index >= len(selected.premises):
            return None
        selected = selected.premises[premise_index]
    return selected


def _checked_substitution_certificate(
    outcome: sub.SubstitutionOutcome,
) -> (
    sub.OrderedOneHoleSubstitutionCertificate
    | BetaInvariantViolation
):
    if isinstance(outcome, sub.SubstitutionSucceeded):
        return outcome.certificate
    if isinstance(outcome, sub.PreGraftFreshnessAperture):
        return BetaInvariantViolation(
            "checked-redex-substitution-produced-a-freshness-aperture"
        )
    return BetaInvariantViolation(
        "checked-redex-substitution-failed:" + outcome.obstruction
    )


def _substitution_leaf_path(
    trace: sub.SubstitutionTraceNode,
) -> ProofPosition:
    if trace.action == "replace":
        return ()
    if (
        trace.action != "descend"
        or trace.premise_index is None
        or trace.child is None
    ):
        raise ValueError("substitution trace does not reach a target leaf")
    return (
        trace.premise_index,
        *_substitution_leaf_path(trace.child),
    )


def _is_root_beta_redex(proof: nd.NDProof) -> bool:
    return (
        proof.rule == "right-implication-elimination"
        and len(proof.premises) == 2
        and proof.premises[0].rule
        == "right-implication-introduction"
    )


def _beta_redex_positions(
    proof: nd.NDProof,
    prefix: ProofPosition = (),
) -> tuple[ProofPosition, ...]:
    here = (prefix,) if _is_root_beta_redex(proof) else ()
    below = tuple(
        position
        for index, premise in enumerate(proof.premises)
        for position in _beta_redex_positions(
            premise,
            (*prefix, index),
        )
    )
    return here + below


def _local_embeddings(
    prefix: nd.ResourceLedger,
    suffix: nd.ResourceLedger,
    argument: nd.ResourceLedger,
) -> tuple[LocalSurvivorEmbedding, ...]:
    prefix_length = len(prefix)
    suffix_length = len(suffix)
    argument_length = len(argument)
    prefix_embeddings = tuple(
        LocalSurvivorEmbedding(
            use=use,
            occurrence_key=nd._occurrence_key(use.hypothesis),
            origin="body-prefix",
            redex_index=index,
            contractum_index=index,
        )
        for index, use in enumerate(prefix)
    )
    argument_embeddings = tuple(
        LocalSurvivorEmbedding(
            use=use,
            occurrence_key=nd._occurrence_key(use.hypothesis),
            origin="argument",
            redex_index=prefix_length + 1 + suffix_length + index,
            contractum_index=prefix_length + index,
        )
        for index, use in enumerate(argument)
    )
    suffix_embeddings = tuple(
        LocalSurvivorEmbedding(
            use=use,
            occurrence_key=nd._occurrence_key(use.hypothesis),
            origin="body-suffix",
            redex_index=prefix_length + 1 + index,
            contractum_index=prefix_length + argument_length + index,
        )
        for index, use in enumerate(suffix)
    )
    return (
        *prefix_embeddings,
        *argument_embeddings,
        *suffix_embeddings,
    )


def _check_local_embeddings(
    redex: nd.ResourceLedger,
    contractum: nd.ResourceLedger,
    retired_target: nd.ResourceUse,
    embeddings: tuple[LocalSurvivorEmbedding, ...],
) -> bool:
    surviving_redex_indices = tuple(
        index
        for index, use in enumerate(redex)
        if use != retired_target
    )
    if len(surviving_redex_indices) != len(embeddings):
        return False
    if len(contractum) != len(embeddings):
        return False
    if len({item.redex_index for item in embeddings}) != len(embeddings):
        return False
    if len({item.contractum_index for item in embeddings}) != len(
        embeddings
    ):
        return False
    for item in embeddings:
        if item.redex_index not in surviving_redex_indices:
            return False
        if not 0 <= item.contractum_index < len(contractum):
            return False
        if redex[item.redex_index] != item.use:
            return False
        if contractum[item.contractum_index] != item.use:
            return False
        if item.occurrence_key != nd._occurrence_key(
            item.use.hypothesis
        ):
            return False
    return True


def _root_beta_transport(
    redex: nd.NDProof,
    *,
    event: str,
) -> RootBetaOutcome:
    event_id = BetaEventId(event)
    if not nd._check_proof(redex):
        return BetaRejected("unchecked-redex")
    if redex.rule != "right-implication-elimination":
        return BetaRejected("root-is-not-implication-elimination")
    abstraction, replacement = redex.premises
    if abstraction.rule != "right-implication-introduction":
        return BetaRejected("function-is-not-implication-introduction")
    if (
        abstraction.principal is None
        or abstraction.binder_id is None
        or len(abstraction.premises) != 1
    ):
        return BetaRejected("malformed-implication-introduction")

    target = abstraction.principal
    body = abstraction.premises[0]
    substitution = sub._right_boundary_substitute(
        body,
        target,
        replacement,
    )
    substitution_certificate = _checked_substitution_certificate(
        substitution
    )
    if isinstance(
        substitution_certificate,
        BetaInvariantViolation,
    ):
        return substitution_certificate
    contractum = substitution_certificate.result
    try:
        target_leaf_path = _substitution_leaf_path(
            substitution_certificate.trace
        )
    except ValueError:
        return BetaInvariantViolation(
            "substitution-trace-has-no-target-leaf"
        )

    target_open_use = nd._open_use(target)
    target_indices = tuple(
        index
        for index, use in enumerate(body.ledger)
        if use == target_open_use
    )
    if len(target_indices) != 1:
        return BetaInvariantViolation("target-open-use-is-not-unique")
    target_index = target_indices[0]
    prefix = body.ledger[:target_index]
    suffix = body.ledger[target_index + 1 :]
    if any(use.status != "discharged" for use in suffix):
        return BetaInvariantViolation(
            "right-boundary-ledger-suffix-is-not-discharged"
        )

    retired_target = nd.ResourceUse(
        hypothesis=target,
        status="discharged",
        binder_id=abstraction.binder_id,
    )
    expected_redex_ledger = (
        *prefix,
        retired_target,
        *suffix,
        *replacement.ledger,
    )
    expected_contractum_ledger = (
        *prefix,
        *replacement.ledger,
        *suffix,
    )
    if redex.ledger != expected_redex_ledger:
        return BetaInvariantViolation(
            "redex-ledger-decomposition-mismatch"
        )
    if contractum.ledger != expected_contractum_ledger:
        return BetaInvariantViolation(
            "contractum-ledger-transport-mismatch"
        )
    target_key = nd._occurrence_key(target)
    if any(
        nd._occurrence_key(use.hypothesis) == target_key
        or use.hypothesis.resource_source_id
        == target.resource_source_id
        or use.binder_id == abstraction.binder_id
        for use in contractum.ledger
    ):
        return BetaInvariantViolation("retired-target-authority-survived")
    if redex.context != contractum.context:
        return BetaInvariantViolation("beta-changed-the-open-context")
    if redex.conclusion != contractum.conclusion:
        return BetaInvariantViolation("beta-changed-the-conclusion")
    if len(redex.ledger) - len(contractum.ledger) != 1:
        return BetaInvariantViolation(
            "root-beta-ledger-length-did-not-decrease-by-one"
        )
    if (
        _discharged_count(redex.ledger)
        - _discharged_count(contractum.ledger)
        != 1
    ):
        return BetaInvariantViolation(
            "root-beta-discharged-count-did-not-decrease-by-one"
        )

    embeddings = _local_embeddings(
        prefix,
        suffix,
        replacement.ledger,
    )
    if not _check_local_embeddings(
        redex.ledger,
        contractum.ledger,
        retired_target,
        embeddings,
    ):
        return BetaInvariantViolation(
            "invalid-local-survivor-embeddings"
        )

    prefix_length = len(prefix)
    blocks = (
        LedgerBlockTransport(
            origin="body-prefix",
            uses=prefix,
            redex_start=0,
            contractum_start=0,
        ),
        LedgerBlockTransport(
            origin="argument",
            uses=replacement.ledger,
            redex_start=prefix_length + 1 + len(suffix),
            contractum_start=prefix_length,
        ),
        LedgerBlockTransport(
            origin="body-suffix",
            uses=suffix,
            redex_start=prefix_length + 1,
            contractum_start=prefix_length + len(replacement.ledger),
        ),
    )

    return RootBetaSucceeded(
        RootBetaLedgerTransport(
            event_id=event_id,
            redex=redex,
            abstraction=abstraction,
            body=body,
            replacement=replacement,
            contractum=contractum,
            substitution=substitution_certificate,
            target_leaf_path=target_leaf_path,
            target_open_use=target_open_use,
            retired_target=retired_target,
            body_prefix=prefix,
            discharged_suffix=suffix,
            blocks=blocks,
            survivor_embeddings=embeddings,
            boundary_context=redex.context,
            boundary_conclusion=redex.conclusion,
        )
    )


def _check_root_beta_transport(
    transport: RootBetaLedgerTransport,
) -> bool:
    if not isinstance(transport, RootBetaLedgerTransport):
        return False
    if not _is_valid_proof_position(transport.target_leaf_path):
        return False
    try:
        replay = _root_beta_transport(
            transport.redex,
            event=transport.event_id.value,
        )
    except (AttributeError, TypeError, ValueError):
        return False
    return (
        isinstance(replay, RootBetaSucceeded)
        and replay.transport == transport
    )


def _rebuild_with_premise(
    proof: nd.NDProof,
    premise_index: int,
    replacement: nd.NDProof,
) -> nd.NDProof | None:
    if proof.rule == "right-implication-introduction":
        if (
            premise_index != 0
            or proof.principal is None
            or proof.binder_id is None
        ):
            return None
        try:
            return nd._right_implication_introduction(
                proof.principal,
                replacement,
                binder=proof.binder_id.value,
            )
        except ValueError:
            return None
    if proof.rule == "right-implication-elimination":
        if premise_index not in (0, 1):
            return None
        function, argument = proof.premises
        if premise_index == 0:
            function = replacement
        else:
            argument = replacement
        attempt = nd._right_implication_elimination(function, argument)
        return attempt.proof
    return None


def _contract_at_position(
    proof: nd.NDProof,
    position: ProofPosition,
    *,
    event: str,
) -> (
    tuple[
        nd.NDProof,
        RootBetaLedgerTransport,
        tuple[AncestorTransportFrame, ...],
    ]
    | BetaRejected
    | BetaInvariantViolation
):
    if not position:
        root = _root_beta_transport(proof, event=event)
        if isinstance(root, (BetaRejected, BetaInvariantViolation)):
            return root
        return root.transport.contractum, root.transport, ()

    premise_index = position[0]
    if premise_index >= len(proof.premises):
        return BetaRejected("proof-position-is-out-of-range")
    child = _contract_at_position(
        proof.premises[premise_index],
        position[1:],
        event=event,
    )
    if isinstance(child, (BetaRejected, BetaInvariantViolation)):
        return child
    rebuilt = _rebuild_with_premise(proof, premise_index, child[0])
    if rebuilt is None:
        return BetaInvariantViolation("contextual-rebuild-failed")
    frame = AncestorTransportFrame(
        original=proof,
        premise_index=premise_index,
        rebuilt=rebuilt,
    )
    return rebuilt, child[1], (*child[2], frame)


def _proof_survivor_embeddings(
    source: nd.ResourceLedger,
    result: nd.ResourceLedger,
    retired_target: nd.ResourceUse,
) -> tuple[GlobalLedgerSurvivorEmbedding, ...] | None:
    retired_indices = tuple(
        index
        for index, use in enumerate(source)
        if use == retired_target
    )
    if len(retired_indices) != 1:
        return None
    if retired_target in result:
        return None
    source_without_target = tuple(
        use for use in source if use != retired_target
    )
    if Counter(source_without_target) != Counter(result):
        return None

    embeddings: list[GlobalLedgerSurvivorEmbedding] = []
    for result_index, use in enumerate(result):
        source_indices = tuple(
            index
            for index, candidate in enumerate(source)
            if candidate == use
        )
        if len(source_indices) != 1:
            return None
        embeddings.append(
            GlobalLedgerSurvivorEmbedding(
                occurrence_key=nd._occurrence_key(use.hypothesis),
                source_index=source_indices[0],
                result_index=result_index,
                source_use=source[source_indices[0]],
                result_use=use,
            )
        )
    if len({item.source_index for item in embeddings}) != len(embeddings):
        return None
    if any(item.source_use != item.result_use for item in embeddings):
        return None
    return tuple(embeddings)


def _contextual_beta_transport(
    source: nd.NDProof,
    position: ProofPosition,
    *,
    event: str,
) -> ContextualBetaOutcome:
    event_id = BetaEventId(event)
    if not nd._check_proof(source):
        return BetaRejected("unchecked-source-proof")
    if not _is_valid_proof_position(position):
        return BetaRejected("invalid-proof-position")

    contracted = _contract_at_position(
        source,
        position,
        event=event_id.value,
    )
    if isinstance(
        contracted,
        (BetaRejected, BetaInvariantViolation),
    ):
        return contracted
    result, local, frames = contracted
    if not nd._check_proof(result):
        return BetaInvariantViolation("unchecked-contextual-result")
    if _proof_at_position(result, position) != local.contractum:
        return BetaInvariantViolation(
            "contractum-is-not-at-the-certified-position"
        )
    if result.context != source.context:
        return BetaInvariantViolation(
            "contextual-beta-changed-the-open-context"
        )
    if result.conclusion != source.conclusion:
        return BetaInvariantViolation(
            "contextual-beta-changed-the-conclusion"
        )

    embeddings = _proof_survivor_embeddings(
        source.ledger,
        result.ledger,
        local.retired_target,
    )
    if embeddings is None:
        return BetaInvariantViolation(
            "invalid-proof-survivor-embeddings"
        )
    retired_indices = tuple(
        index
        for index, use in enumerate(source.ledger)
        if use == local.retired_target
    )
    if len(retired_indices) != 1:
        return BetaInvariantViolation(
            "retired-target-is-not-unique-at-source-root"
        )
    if len(source.ledger) - len(result.ledger) != 1:
        return BetaInvariantViolation(
            "root-ledger-length-did-not-decrease-by-one"
        )
    source_node_count = _proof_node_count(source)
    result_node_count = _proof_node_count(result)
    if source_node_count - result_node_count != 3:
        return BetaInvariantViolation(
            "beta-node-count-did-not-decrease-by-three"
        )
    source_discharged_count = _discharged_count(source.ledger)
    result_discharged_count = _discharged_count(result.ledger)
    if source_discharged_count - result_discharged_count != 1:
        return BetaInvariantViolation(
            "beta-discharged-count-did-not-decrease-by-one"
        )

    return ContextualBetaSucceeded(
        ContextualBetaTransport(
            event_id=event_id,
            source=source,
            position=position,
            local=local,
            frames_inner_to_outer=frames,
            result=result,
            retired_source_index=retired_indices[0],
            survivor_embeddings=embeddings,
            boundary_context=source.context,
            boundary_conclusion=source.conclusion,
            source_node_count=source_node_count,
            result_node_count=result_node_count,
            source_discharged_count=source_discharged_count,
            result_discharged_count=result_discharged_count,
        )
    )


def _check_contextual_beta_transport(
    transport: ContextualBetaTransport,
) -> bool:
    if not isinstance(transport, ContextualBetaTransport):
        return False
    if not _is_valid_proof_position(transport.position):
        return False
    try:
        replay = _contextual_beta_transport(
            transport.source,
            transport.position,
            event=transport.event_id.value,
        )
    except (AttributeError, TypeError, ValueError):
        return False
    return (
        isinstance(replay, ContextualBetaSucceeded)
        and replay.transport == transport
    )


def _hypothesis(
    label: str,
    formula: nd.Formula,
    *,
    source: str,
    occurrence: str,
    domain: nd.ResourceDomainName,
) -> nd.HypothesisOccurrence:
    return sub._hypothesis(
        label,
        formula,
        source=source,
        occurrence=occurrence,
        domain=domain,
        scope="scope:beta-transport",
    )


def _identity_redex(
    formula: nd.Formula,
    *,
    stem: str,
    target_domain: nd.ResourceDomainName = "K",
    argument_domain: nd.ResourceDomainName = "X",
) -> tuple[nd.NDProof, nd.NDProof]:
    target = _hypothesis(
        f"{stem}:x",
        formula,
        source=f"source:{stem}:x",
        occurrence=f"occurrence:{stem}:x",
        domain=target_domain,
    )
    body = nd._assume(target)
    abstraction = nd._right_implication_introduction(
        target,
        body,
        binder=f"binder:{stem}:x",
    )
    argument_hypothesis = _hypothesis(
        f"{stem}:a",
        formula,
        source=f"source:{stem}:a",
        occurrence=f"occurrence:{stem}:a",
        domain=argument_domain,
    )
    argument = nd._assume(argument_hypothesis)
    redex = nd._right_implication_elimination(
        abstraction,
        argument,
    ).proof
    assert redex is not None
    return redex, argument


def _successful_root(
    outcome: RootBetaOutcome,
) -> RootBetaLedgerTransport:
    assert isinstance(outcome, RootBetaSucceeded)
    assert _check_root_beta_transport(outcome.transport)
    return outcome.transport


def _successful_contextual(
    outcome: ContextualBetaOutcome,
) -> ContextualBetaTransport:
    assert isinstance(outcome, ContextualBetaSucceeded)
    assert _check_contextual_beta_transport(outcome.transport)
    return outcome.transport


def test_identity_detour_has_a_replayable_root_transport() -> None:
    redex, argument = _identity_redex(nd.Atom("K"), stem="identity")

    transport = _successful_root(
        _root_beta_transport(redex, event="beta:identity")
    )

    assert transport.contractum == argument
    assert transport.body_prefix == ()
    assert transport.discharged_suffix == ()
    assert transport.boundary_context == argument.context
    assert transport.boundary_conclusion == argument.conclusion
    assert tuple(
        item.origin for item in transport.survivor_embeddings
    ) == ("argument",)
    assert transport.survivor_embeddings[0].redex_index == 1
    assert transport.survivor_embeddings[0].contractum_index == 0
    assert tuple(block.origin for block in transport.blocks) == (
        "body-prefix",
        "argument",
        "body-suffix",
    )
    assert transport.target_leaf_path == ()


def test_nontrivial_transport_moves_only_the_argument_block() -> None:
    construction = nd.Atom("K")
    space = nd.Atom("X")
    identity_type = nd.RightLinearImplication(construction, construction)
    target_type = nd.RightLinearImplication(identity_type, space)
    target = _hypothesis(
        "x",
        target_type,
        source="source:nontrivial:x",
        occurrence="occurrence:nontrivial:x",
        domain="K",
    )
    internal = _hypothesis(
        "h",
        construction,
        source="source:nontrivial:h",
        occurrence="occurrence:nontrivial:h",
        domain="X",
    )
    closed_identity = nd._right_implication_introduction(
        internal,
        nd._assume(internal),
        binder="binder:nontrivial:h",
    )
    body = nd._right_implication_elimination(
        nd._assume(target),
        closed_identity,
    ).proof
    assert body is not None
    abstraction = nd._right_implication_introduction(
        target,
        body,
        binder="binder:nontrivial:x",
    )
    replacement_hypothesis = _hypothesis(
        "r",
        target_type,
        source="source:nontrivial:r",
        occurrence="occurrence:nontrivial:r",
        domain="t",
    )
    replacement = nd._assume(replacement_hypothesis)
    redex = nd._right_implication_elimination(
        abstraction,
        replacement,
    ).proof
    assert redex is not None

    transport = _successful_root(
        _root_beta_transport(redex, event="beta:nontrivial")
    )

    assert transport.body_prefix == ()
    assert transport.discharged_suffix == closed_identity.ledger
    assert transport.redex.ledger == (
        transport.retired_target,
        *closed_identity.ledger,
        *replacement.ledger,
    )
    assert transport.contractum.ledger == (
        *replacement.ledger,
        *closed_identity.ledger,
    )
    assert tuple(
        item.origin for item in transport.survivor_embeddings
    ) == ("argument", "body-suffix")
    assert tuple(
        item.use for item in transport.survivor_embeddings
    ) == (
        replacement.ledger[0],
        closed_identity.ledger[0],
    )
    redex_without_target = tuple(
        use
        for use in transport.redex.ledger
        if use != transport.retired_target
    )
    assert redex_without_target != transport.contractum.ledger
    assert Counter(redex_without_target) == Counter(
        transport.contractum.ledger
    )


def test_three_nonempty_blocks_preserve_internal_order() -> None:
    construction = nd.Atom("K")
    space = nd.Atom("X")
    time = nd.Atom("t")
    identity_type = nd.RightLinearImplication(
        construction,
        construction,
    )
    target_type = nd.RightLinearImplication(identity_type, space)
    target = _hypothesis(
        "x",
        target_type,
        source="source:blocks:x",
        occurrence="occurrence:blocks:x",
        domain="K",
    )
    internal = _hypothesis(
        "h",
        construction,
        source="source:blocks:h",
        occurrence="occurrence:blocks:h",
        domain="X",
    )
    closed_identity = nd._right_implication_introduction(
        internal,
        nd._assume(internal),
        binder="binder:blocks:h",
    )
    inner = nd._right_implication_elimination(
        nd._assume(target),
        closed_identity,
    ).proof
    assert inner is not None
    prefix_function = _hypothesis(
        "q",
        nd.RightLinearImplication(space, time),
        source="source:blocks:q",
        occurrence="occurrence:blocks:q",
        domain="t",
    )
    body = nd._right_implication_elimination(
        nd._assume(prefix_function),
        inner,
    ).proof
    assert body is not None
    abstraction = nd._right_implication_introduction(
        target,
        body,
        binder="binder:blocks:x",
    )
    generator = _hypothesis(
        "g",
        nd.RightLinearImplication(construction, target_type),
        source="source:blocks:g",
        occurrence="occurrence:blocks:g",
        domain="K",
    )
    seed = _hypothesis(
        "c",
        construction,
        source="source:blocks:c",
        occurrence="occurrence:blocks:c",
        domain="X",
    )
    replacement = nd._right_implication_elimination(
        nd._assume(generator),
        nd._assume(seed),
    ).proof
    assert replacement is not None
    redex = nd._right_implication_elimination(
        abstraction,
        replacement,
    ).proof
    assert redex is not None

    transport = _successful_root(
        _root_beta_transport(redex, event="beta:three-blocks")
    )
    prefix_block, argument_block, suffix_block = transport.blocks

    assert tuple(
        len(block.uses) for block in transport.blocks
    ) == (1, 2, 1)
    assert transport.target_leaf_path == (1, 0)
    assert (
        prefix_block.redex_start,
        argument_block.redex_start,
        suffix_block.redex_start,
    ) == (0, 3, 2)
    assert (
        prefix_block.contractum_start,
        argument_block.contractum_start,
        suffix_block.contractum_start,
    ) == (0, 1, 3)
    assert redex.ledger == (
        *prefix_block.uses,
        transport.retired_target,
        *suffix_block.uses,
        *argument_block.uses,
    )
    assert transport.contractum.ledger == (
        *prefix_block.uses,
        *argument_block.uses,
        *suffix_block.uses,
    )
    argument_embeddings = tuple(
        item
        for item in transport.survivor_embeddings
        if item.origin == "argument"
    )
    assert tuple(item.redex_index for item in argument_embeddings) == (
        3,
        4,
    )
    assert tuple(
        item.contractum_index for item in argument_embeddings
    ) == (1, 2)


def test_contextual_contraction_whiskers_through_introduction() -> None:
    formula = nd.Atom("K")
    redex, argument = _identity_redex(formula, stem="under-intro")
    outer_hypothesis = argument.context[0]
    source = nd._right_implication_introduction(
        outer_hypothesis,
        redex,
        binder="binder:under-intro:outer",
    )

    transport = _successful_contextual(
        _contextual_beta_transport(
            source,
            (0,),
            event="beta:under-intro",
        )
    )
    expected = nd._right_implication_introduction(
        outer_hypothesis,
        argument,
        binder="binder:under-intro:outer",
    )

    assert transport.result == expected
    assert transport.position == (0,)
    assert tuple(
        frame.premise_index
        for frame in transport.frames_inner_to_outer
    ) == (0,)
    assert transport.boundary_context == source.context == ()
    assert transport.boundary_conclusion == source.conclusion
    assert transport.node_count_decrease == 3
    assert transport.discharged_decrease == 1
    local_argument_use = transport.local.replacement.ledger[0]
    root_argument_embedding = next(
        item
        for item in transport.survivor_embeddings
        if item.occurrence_key
        == nd._occurrence_key(local_argument_use.hypothesis)
    )
    assert local_argument_use.status == "open"
    assert root_argument_embedding.source_use.status == "discharged"
    assert root_argument_embedding.result_use.status == "discharged"
    assert root_argument_embedding.source_use.binder_id == nd.BinderId(
        "binder:under-intro:outer"
    )


def test_intro_frame_recomputes_a_body_prefix_status() -> None:
    construction = nd.Atom("K")
    result_formula = nd.Atom("X")
    target_formula = nd.RightLinearImplication(
        construction,
        construction,
    )
    target = _hypothesis(
        "prefix-status-target",
        target_formula,
        source="source:prefix-status:target",
        occurrence="occurrence:prefix-status:target",
        domain="X",
    )
    prefix = _hypothesis(
        "prefix-status-function",
        nd.RightLinearImplication(target_formula, result_formula),
        source="source:prefix-status:function",
        occurrence="occurrence:prefix-status:function",
        domain="K",
    )
    body = nd._right_implication_elimination(
        nd._assume(prefix),
        nd._assume(target),
    ).proof
    assert body is not None
    abstraction = nd._right_implication_introduction(
        target,
        body,
        binder="binder:prefix-status:target",
    )
    closed_seed = _hypothesis(
        "prefix-status-seed",
        construction,
        source="source:prefix-status:seed",
        occurrence="occurrence:prefix-status:seed",
        domain="t",
    )
    closed_replacement = nd._right_implication_introduction(
        closed_seed,
        nd._assume(closed_seed),
        binder="binder:prefix-status:seed",
    )
    redex = nd._right_implication_elimination(
        abstraction,
        closed_replacement,
    ).proof
    assert redex is not None
    outer_binder = "binder:prefix-status:outer"
    source = nd._right_implication_introduction(
        prefix,
        redex,
        binder=outer_binder,
    )

    transport = _successful_contextual(
        _contextual_beta_transport(
            source,
            (0,),
            event="beta:prefix-status",
        )
    )
    prefix_embedding = next(
        item
        for item in transport.survivor_embeddings
        if item.occurrence_key == nd._occurrence_key(prefix)
    )

    assert transport.local.body_prefix == (nd._open_use(prefix),)
    assert transport.local.replacement == closed_replacement
    assert prefix_embedding.source_use.status == "discharged"
    assert prefix_embedding.result_use.status == "discharged"
    assert prefix_embedding.source_use.binder_id == nd.BinderId(
        outer_binder
    )
    assert prefix_embedding.result_use == prefix_embedding.source_use


def test_contextual_contraction_whiskers_through_both_elimination_sides() -> None:
    construction = nd.Atom("K")
    space = nd.Atom("X")

    argument_redex, argument_contractum = _identity_redex(
        construction,
        stem="elim-argument",
    )
    outer_function = _hypothesis(
        "q",
        nd.RightLinearImplication(construction, space),
        source="source:elim-argument:q",
        occurrence="occurrence:elim-argument:q",
        domain="t",
    )
    source_argument_side = nd._right_implication_elimination(
        nd._assume(outer_function),
        argument_redex,
    ).proof
    assert source_argument_side is not None
    argument_transport = _successful_contextual(
        _contextual_beta_transport(
            source_argument_side,
            (1,),
            event="beta:elim-argument",
        )
    )
    expected_argument_side = nd._right_implication_elimination(
        nd._assume(outer_function),
        argument_contractum,
    ).proof
    assert argument_transport.result == expected_argument_side

    function_type = nd.RightLinearImplication(construction, space)
    function_redex, function_contractum = _identity_redex(
        function_type,
        stem="elim-function",
    )
    outer_argument = _hypothesis(
        "k",
        construction,
        source="source:elim-function:k",
        occurrence="occurrence:elim-function:k",
        domain="t",
    )
    source_function_side = nd._right_implication_elimination(
        function_redex,
        nd._assume(outer_argument),
    ).proof
    assert source_function_side is not None
    function_transport = _successful_contextual(
        _contextual_beta_transport(
            source_function_side,
            (0,),
            event="beta:elim-function",
        )
    )
    expected_function_side = nd._right_implication_elimination(
        function_contractum,
        nd._assume(outer_argument),
    ).proof
    assert function_transport.result == expected_function_side

    assert argument_transport.node_count_decrease == 3
    assert function_transport.node_count_decrease == 3
    assert argument_transport.discharged_decrease == 1
    assert function_transport.discharged_decrease == 1
    outer_function_embedding = next(
        item
        for item in argument_transport.survivor_embeddings
        if item.occurrence_key == nd._occurrence_key(outer_function)
    )
    assert outer_function_embedding.source_index == 0
    assert outer_function_embedding.result_index == 0
    outer_argument_embedding = next(
        item
        for item in function_transport.survivor_embeddings
        if item.occurrence_key == nd._occurrence_key(outer_argument)
    )
    assert outer_argument_embedding.source_index == 2
    assert outer_argument_embedding.result_index == 1


def test_freshness_conflicts_stop_before_a_checked_redex_exists() -> None:
    formula = nd.Atom("K")
    shared_source_target = _hypothesis(
        "source-target",
        formula,
        source="source:freshness:shared",
        occurrence="occurrence:freshness:source-target",
        domain="K",
    )
    source_abstraction = nd._right_implication_introduction(
        shared_source_target,
        nd._assume(shared_source_target),
        binder="binder:freshness:source-target",
    )
    shared_source_argument = _hypothesis(
        "source-argument",
        formula,
        source="source:freshness:shared",
        occurrence="occurrence:freshness:source-argument",
        domain="X",
    )
    source_attempt = nd._right_implication_elimination(
        source_abstraction,
        nd._assume(shared_source_argument),
    )

    occurrence_target = _hypothesis(
        "occurrence-target",
        formula,
        source="source:freshness:occurrence-target",
        occurrence="occurrence:freshness:shared",
        domain="K",
    )
    occurrence_abstraction = nd._right_implication_introduction(
        occurrence_target,
        nd._assume(occurrence_target),
        binder="binder:freshness:occurrence-target",
    )
    occurrence_argument = _hypothesis(
        "occurrence-argument",
        formula,
        source="source:freshness:occurrence-argument",
        occurrence="occurrence:freshness:shared",
        domain="X",
    )
    occurrence_attempt = nd._right_implication_elimination(
        occurrence_abstraction,
        nd._assume(occurrence_argument),
    )

    binder_name = "binder:freshness:shared"
    binder_target = _hypothesis(
        "binder-target",
        formula,
        source="source:freshness:binder-target",
        occurrence="occurrence:freshness:binder-target",
        domain="K",
    )
    binder_abstraction = nd._right_implication_introduction(
        binder_target,
        nd._assume(binder_target),
        binder=binder_name,
    )
    internal = _hypothesis(
        "binder-internal",
        formula,
        source="source:freshness:binder-internal",
        occurrence="occurrence:freshness:binder-internal",
        domain="X",
    )
    closed_identity = nd._right_implication_introduction(
        internal,
        nd._assume(internal),
        binder=binder_name,
    )
    identity_type = closed_identity.conclusion
    eliminator = _hypothesis(
        "binder-eliminator",
        nd.RightLinearImplication(identity_type, formula),
        source="source:freshness:binder-eliminator",
        occurrence="occurrence:freshness:binder-eliminator",
        domain="t",
    )
    binder_argument = nd._right_implication_elimination(
        nd._assume(eliminator),
        closed_identity,
    ).proof
    assert binder_argument is not None
    binder_attempt = nd._right_implication_elimination(
        binder_abstraction,
        binder_argument,
    )

    assert source_attempt.proof is None
    assert source_attempt.aperture is not None
    assert source_attempt.aperture.source_id == (
        shared_source_target.resource_source_id
    )
    assert occurrence_attempt.proof is None
    assert occurrence_attempt.obstruction == "occurrence-alias"
    assert binder_attempt.proof is None
    assert binder_attempt.obstruction == "binder-alias"


def test_checked_redex_substitution_failure_is_an_invariant_violation() -> None:
    classified = _checked_substitution_certificate(
        sub.SubstitutionRejected("forced-calibration-failure")
    )

    assert isinstance(classified, BetaInvariantViolation)
    assert classified.obstruction == (
        "checked-redex-substitution-failed:forced-calibration-failure"
    )


def test_deep_alternating_position_rebuild_is_replayable() -> None:
    source, _ = _identity_redex(
        nd.Atom("K"),
        stem="deep:local",
    )
    position: ProofPosition = ()
    result_formulas = (nd.Atom("X"), nd.Atom("t"), nd.Atom("K"))

    for round_index in range(4):
        result_formula = result_formulas[round_index % 3]
        outer_function = _hypothesis(
            f"deep-function-{round_index}",
            nd.RightLinearImplication(
                source.conclusion,
                result_formula,
            ),
            source=f"source:deep:function:{round_index}",
            occurrence=f"occurrence:deep:function:{round_index}",
            domain=("K", "X", "t")[round_index % 3],
        )
        right_lift = nd._right_implication_elimination(
            nd._assume(outer_function),
            source,
        ).proof
        assert right_lift is not None
        source = right_lift
        position = (1, *position)

        principal = source.context[-1]
        source = nd._right_implication_introduction(
            principal,
            source,
            binder=f"binder:deep:{round_index}",
        )
        position = (0, *position)

        outer_argument = _hypothesis(
            f"deep-argument-{round_index}",
            source.conclusion.premise,
            source=f"source:deep:argument:{round_index}",
            occurrence=f"occurrence:deep:argument:{round_index}",
            domain=("X", "t", "K")[round_index % 3],
        )
        left_lift = nd._right_implication_elimination(
            source,
            nd._assume(outer_argument),
        ).proof
        assert left_lift is not None
        source = left_lift
        position = (0, *position)

    transport = _successful_contextual(
        _contextual_beta_transport(
            source,
            position,
            event="beta:deep-alternating",
        )
    )

    assert len(position) == 12
    assert tuple(
        frame.premise_index
        for frame in transport.frames_inner_to_outer
    ) == tuple(reversed(position))
    assert _proof_at_position(
        transport.result,
        position,
    ) == transport.local.contractum
    assert len(transport.source.ledger) - len(transport.result.ledger) == 1
    assert transport.discharged_decrease == 1
    assert transport.node_count_decrease == 3


def test_transport_rejects_nonredexes_and_invalid_positions() -> None:
    formula = nd.Atom("K")
    hypothesis = _hypothesis(
        "a",
        formula,
        source="source:invalid:a",
        occurrence="occurrence:invalid:a",
        domain="K",
    )
    assumption = nd._assume(hypothesis)
    nonredex_function = _hypothesis(
        "f",
        nd.RightLinearImplication(formula, formula),
        source="source:invalid:f",
        occurrence="occurrence:invalid:f",
        domain="X",
    )
    nonredex = nd._right_implication_elimination(
        nd._assume(nonredex_function),
        assumption,
    ).proof
    assert nonredex is not None
    unchecked = replace(assumption, context=())
    assert not nd._check_proof(unchecked)

    root_result = _root_beta_transport(assumption, event="beta:invalid-root")
    function_result = _root_beta_transport(
        nonredex,
        event="beta:invalid-function",
    )
    range_result = _contextual_beta_transport(
        nonredex,
        (2,),
        event="beta:invalid-range",
    )
    position_result = _contextual_beta_transport(
        nonredex,
        (-1,),
        event="beta:invalid-position",
    )
    malformed_positions = (
        [],
        (True,),
        ("0",),
        (0.0,),
        None,
    )
    malformed_results = tuple(
        _contextual_beta_transport(
            nonredex,
            position,  # type: ignore[arg-type]
            event=f"beta:malformed-position:{index}",
        )
        for index, position in enumerate(malformed_positions)
    )
    unchecked_root_result = _root_beta_transport(
        unchecked,
        event="beta:unchecked-root",
    )
    unchecked_contextual_result = _contextual_beta_transport(
        unchecked,
        (),
        event="beta:unchecked-contextual-root",
    )

    assert isinstance(root_result, BetaRejected)
    assert root_result.obstruction == "root-is-not-implication-elimination"
    assert isinstance(function_result, BetaRejected)
    assert function_result.obstruction == (
        "function-is-not-implication-introduction"
    )
    assert isinstance(range_result, BetaRejected)
    assert range_result.obstruction == "proof-position-is-out-of-range"
    assert isinstance(position_result, BetaRejected)
    assert position_result.obstruction == "invalid-proof-position"
    assert isinstance(unchecked_root_result, BetaRejected)
    assert unchecked_root_result.obstruction == "unchecked-redex"
    assert isinstance(unchecked_contextual_result, BetaRejected)
    assert unchecked_contextual_result.obstruction == (
        "unchecked-source-proof"
    )
    assert all(
        isinstance(result, BetaRejected)
        and result.obstruction == "invalid-proof-position"
        for result in malformed_results
    )


def test_contextual_transport_replay_rejects_forged_fields() -> None:
    redex, _ = _identity_redex(nd.Atom("K"), stem="forgery")
    transport = _successful_contextual(
        _contextual_beta_transport(
            redex,
            (),
            event="beta:forgery",
        )
    )
    forged_node_count = replace(
        transport,
        result_node_count=transport.result_node_count + 1,
    )
    forged_position = replace(transport, position=(0,))
    forged_embeddings = replace(
        transport,
        survivor_embeddings=(),
    )
    forged_frames = replace(
        transport,
        frames_inner_to_outer=(
            AncestorTransportFrame(
                original=redex,
                premise_index=0,
                rebuilt=redex,
            ),
        ),
    )
    forged_retired_index = replace(
        transport,
        retired_source_index=transport.retired_source_index + 1,
    )
    forged_discharged_count = replace(
        transport,
        result_discharged_count=(
            transport.result_discharged_count + 1
        ),
    )
    forged_position_list = replace(
        transport,
        position=[],  # type: ignore[arg-type]
    )
    forged_position_bool = replace(
        transport,
        position=(True,),  # type: ignore[arg-type]
    )
    forged_malformed_positions = tuple(
        replace(
            transport,
            position=position,  # type: ignore[arg-type]
        )
        for position in (("0",), (0.0,), None)
    )
    local = transport.local
    forged_target_leaf = replace(
        local,
        target_leaf_path=(True,),  # type: ignore[arg-type]
    )
    first_block = local.blocks[0]
    forged_blocks = replace(
        local,
        blocks=(
            replace(first_block, redex_start=99),
            *local.blocks[1:],
        ),
    )
    first_local_embedding = local.survivor_embeddings[0]
    forged_occurrence_key = replace(
        local,
        survivor_embeddings=(
            replace(
                first_local_embedding,
                occurrence_key=(
                    nd.ScopeId("scope:forged"),
                    nd.OccurrenceId("occurrence:forged"),
                ),
            ),
            *local.survivor_embeddings[1:],
        ),
    )

    assert _check_contextual_beta_transport(transport)
    assert not _check_contextual_beta_transport(forged_node_count)
    assert not _check_contextual_beta_transport(forged_position)
    assert not _check_contextual_beta_transport(forged_embeddings)
    assert not _check_contextual_beta_transport(forged_frames)
    assert not _check_contextual_beta_transport(forged_retired_index)
    assert not _check_contextual_beta_transport(forged_discharged_count)
    assert not _check_contextual_beta_transport(forged_position_list)
    assert not _check_contextual_beta_transport(forged_position_bool)
    assert all(
        not _check_contextual_beta_transport(forged)
        for forged in forged_malformed_positions
    )
    assert not _check_root_beta_transport(forged_target_leaf)
    assert not _check_root_beta_transport(forged_blocks)
    assert not _check_root_beta_transport(forged_occurrence_key)


def test_each_beta_step_decreases_proof_node_count_by_exactly_three() -> None:
    formula = nd.Atom("K")
    inner_redex, _ = _identity_redex(formula, stem="normalization-inner")
    outer_target = _hypothesis(
        "y",
        formula,
        source="source:normalization-outer:y",
        occurrence="occurrence:normalization-outer:y",
        domain="t",
    )
    outer_abstraction = nd._right_implication_introduction(
        outer_target,
        nd._assume(outer_target),
        binder="binder:normalization-outer:y",
    )
    current = nd._right_implication_elimination(
        outer_abstraction,
        inner_redex,
    ).proof
    assert current is not None
    initial_node_count = _proof_node_count(current)
    transports: list[ContextualBetaTransport] = []

    while _beta_redex_positions(current):
        position = _beta_redex_positions(current)[0]
        transport = _successful_contextual(
            _contextual_beta_transport(
                current,
                position,
                event=f"beta:normalization:{len(transports)}",
            )
        )
        assert transport.node_count_decrease == 3
        assert transport.discharged_decrease == 1
        transports.append(transport)
        current = transport.result

    assert len(transports) == 2
    assert _proof_node_count(current) == (
        initial_node_count - 3 * len(transports)
    )
    assert not _beta_redex_positions(current)
    assert len(transports) <= (initial_node_count - 1) // 3
    assert len(transports) <= _discharged_count(
        transports[0].source.ledger
    )


def test_event_identity_is_typed_but_global_allocation_is_deferred() -> None:
    try:
        BetaEventId("")
    except ValueError as error:
        assert "nonempty" in str(error)
    else:
        raise AssertionError("empty beta event identity was accepted")

    first = BetaEventId("beta:event")
    second = BetaEventId("beta:event")

    assert first == second
