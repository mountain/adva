from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from typing import Literal, TypeAlias

import test_threaded_natural_deduction_calibration as nd


TraceAction: TypeAlias = Literal["reuse", "replace", "descend"]


@dataclass(frozen=True)
class SubstitutionTraceNode:
    original_rule: nd.ProofRule
    action: TraceAction
    premise_index: int | None = None
    child: SubstitutionTraceNode | None = None

    @property
    def replacement_count(self) -> int:
        if self.action == "replace":
            return 1
        if self.child is None:
            return 0
        return self.child.replacement_count


@dataclass(frozen=True)
class OrderedOneHoleSubstitutionCertificate:
    body: nd.NDProof
    target: nd.HypothesisOccurrence
    replacement: nd.NDProof
    result: nd.NDProof
    trace: SubstitutionTraceNode
    target_context_index: int
    target_ledger_index: int
    left_context: nd.Context
    right_context: nd.Context
    left_ledger: nd.ResourceLedger
    right_ledger: nd.ResourceLedger
    expected_context: nd.Context
    expected_ledger: nd.ResourceLedger


@dataclass(frozen=True)
class SubstitutionSucceeded:
    certificate: OrderedOneHoleSubstitutionCertificate


@dataclass(frozen=True)
class PreGraftFreshnessAperture:
    aperture: nd.ApertureBoundaryDiagnostic


@dataclass(frozen=True)
class SubstitutionRejected:
    obstruction: str


SubstitutionOutcome: TypeAlias = (
    SubstitutionSucceeded | PreGraftFreshnessAperture | SubstitutionRejected
)


def _contains_open_target(
    proof: nd.NDProof,
    target: nd.HypothesisOccurrence,
) -> bool:
    return any(
        use.hypothesis == target and use.status == "open"
        for use in proof.ledger
    )


def _substitute_checked_tree(
    proof: nd.NDProof,
    target: nd.HypothesisOccurrence,
    replacement: nd.NDProof,
) -> tuple[nd.NDProof, SubstitutionTraceNode]:
    if not _contains_open_target(proof, target):
        return proof, SubstitutionTraceNode(
            original_rule=proof.rule,
            action="reuse",
        )

    if proof.rule == "assumption":
        if proof.principal != target:
            raise ValueError("the open target does not reach its assumption leaf")
        return replacement, SubstitutionTraceNode(
            original_rule=proof.rule,
            action="replace",
        )

    if proof.rule == "right-implication-introduction":
        assert proof.principal is not None
        assert proof.binder_id is not None
        rebuilt_body, child = _substitute_checked_tree(
            proof.premises[0],
            target,
            replacement,
        )
        rebuilt = nd._right_implication_introduction(
            proof.principal,
            rebuilt_body,
            binder=proof.binder_id.value,
        )
        return rebuilt, SubstitutionTraceNode(
            original_rule=proof.rule,
            action="descend",
            premise_index=0,
            child=child,
        )

    if proof.rule == "right-implication-elimination":
        function, argument = proof.premises
        function_contains = _contains_open_target(function, target)
        argument_contains = _contains_open_target(argument, target)
        if function_contains == argument_contains:
            raise ValueError("the linear target must occur in exactly one premise")
        premise_index = 0 if function_contains else 1
        if function_contains:
            rebuilt_function, child = _substitute_checked_tree(
                function,
                target,
                replacement,
            )
            rebuilt_argument = argument
        else:
            rebuilt_function = function
            rebuilt_argument, child = _substitute_checked_tree(
                argument,
                target,
                replacement,
            )
        attempt = nd._right_implication_elimination(
            rebuilt_function,
            rebuilt_argument,
        )
        if attempt.proof is None:
            detail = attempt.obstruction or "unexpected-resource-aperture"
            raise ValueError(f"substitution rebuild failed: {detail}")
        return attempt.proof, SubstitutionTraceNode(
            original_rule=proof.rule,
            action="descend",
            premise_index=premise_index,
            child=child,
        )

    raise ValueError(f"unsupported proof rule: {proof.rule}")


def _ordered_one_hole_substitute(
    body: nd.NDProof,
    target: nd.HypothesisOccurrence,
    replacement: nd.NDProof,
) -> SubstitutionOutcome:
    if not nd._check_proof(body):
        return SubstitutionRejected("unchecked-body")
    if not nd._check_proof(replacement):
        return SubstitutionRejected("unchecked-replacement")
    if replacement.conclusion != target.formula:
        return SubstitutionRejected("replacement-conclusion-mismatch")

    target_context_indices = tuple(
        index
        for index, hypothesis in enumerate(body.context)
        if hypothesis == target
    )
    if len(target_context_indices) != 1:
        return SubstitutionRejected("target-is-not-one-open-context-hole")

    target_use = nd._open_use(target)
    target_indices = tuple(
        index
        for index, use in enumerate(body.ledger)
        if use == target_use
    )
    if len(target_indices) != 1:
        return SubstitutionRejected("target-use-is-not-open-exactly-once")

    freshness = nd._merge_resource_ledgers(
        body.ledger,
        replacement.ledger,
    )
    if freshness.aperture is not None:
        return PreGraftFreshnessAperture(freshness.aperture)
    if freshness.obstruction is not None:
        return SubstitutionRejected(
            "freshness:" + freshness.obstruction
        )

    try:
        result, trace = _substitute_checked_tree(
            body,
            target,
            replacement,
        )
    except ValueError as error:
        return SubstitutionRejected("rebuild:" + str(error))

    target_index = target_indices[0]
    target_context_index = target_context_indices[0]
    left_context = body.context[:target_context_index]
    right_context = body.context[target_context_index + 1 :]
    left_ledger = body.ledger[:target_index]
    right_ledger = body.ledger[target_index + 1 :]
    expected_context = left_context + replacement.context + right_context
    expected_ledger = (
        *left_ledger,
        *replacement.ledger,
        *right_ledger,
    )
    if trace.replacement_count != 1:
        return SubstitutionRejected("replacement-count-is-not-one")
    if not nd._check_proof(result):
        return SubstitutionRejected("rebuilt-proof-is-not-checked")
    if result.context != expected_context:
        return SubstitutionRejected("ordered-context-splice-mismatch")
    if result.ledger != expected_ledger:
        return SubstitutionRejected("ordered-ledger-splice-mismatch")
    if result.conclusion != body.conclusion:
        return SubstitutionRejected("substitution-changed-the-conclusion")

    return SubstitutionSucceeded(
        OrderedOneHoleSubstitutionCertificate(
            body=body,
            target=target,
            replacement=replacement,
            result=result,
            trace=trace,
            target_context_index=target_context_index,
            target_ledger_index=target_index,
            left_context=left_context,
            right_context=right_context,
            left_ledger=left_ledger,
            right_ledger=right_ledger,
            expected_context=expected_context,
            expected_ledger=expected_ledger,
        )
    )


def _right_boundary_substitute(
    body: nd.NDProof,
    target: nd.HypothesisOccurrence,
    replacement: nd.NDProof,
) -> SubstitutionOutcome:
    if not body.context or body.context[-1] != target:
        return SubstitutionRejected("target-is-not-right-boundary")
    return _ordered_one_hole_substitute(body, target, replacement)


def _check_substitution_certificate(
    certificate: OrderedOneHoleSubstitutionCertificate,
) -> bool:
    replay = _ordered_one_hole_substitute(
        certificate.body,
        certificate.target,
        certificate.replacement,
    )
    return (
        isinstance(replay, SubstitutionSucceeded)
        and replay.certificate == certificate
    )


def _hypothesis(
    label: str,
    formula: nd.Formula,
    *,
    source: str,
    occurrence: str,
    domain: nd.ResourceDomainName,
    scope: str = "scope:substitution",
) -> nd.HypothesisOccurrence:
    return nd._hypothesis(
        label,
        formula,
        source=source,
        occurrence=occurrence,
        domain=domain,
        provenance="evidence:substitution",
        scope=scope,
    )


def _assumption(
    label: str,
    formula: nd.Formula,
    *,
    source: str,
    occurrence: str,
    domain: nd.ResourceDomainName,
) -> nd.NDProof:
    return nd._assume(
        _hypothesis(
            label,
            formula,
            source=source,
            occurrence=occurrence,
            domain=domain,
        )
    )


def _successful(
    outcome: SubstitutionOutcome,
) -> OrderedOneHoleSubstitutionCertificate:
    assert isinstance(outcome, SubstitutionSucceeded)
    assert _check_substitution_certificate(outcome.certificate)
    return outcome.certificate


def _resource_bag(ledger: nd.ResourceLedger) -> Counter[nd.ResourceUse]:
    return Counter(ledger)


def test_identity_substitution_replaces_one_assumption_leaf() -> None:
    formula = nd.Atom("K")
    target = _hypothesis(
        "x",
        formula,
        source="source:x",
        occurrence="occurrence:x",
        domain="K",
    )
    replacement = _assumption(
        "a",
        formula,
        source="source:a",
        occurrence="occurrence:a",
        domain="X",
    )

    certificate = _successful(
        _right_boundary_substitute(
            nd._assume(target),
            target,
            replacement,
        )
    )

    assert certificate.result == replacement
    assert certificate.trace.action == "replace"
    assert certificate.trace.replacement_count == 1
    assert certificate.expected_context == replacement.context
    assert certificate.expected_ledger == replacement.ledger


def test_substitution_splices_an_ordered_multi_source_derivation() -> None:
    construction = nd.Atom("K")
    space = nd.Atom("X")
    time = nd.Atom("t")
    function = _hypothesis(
        "f",
        nd.RightLinearImplication(construction, space),
        source="source:f",
        occurrence="occurrence:f",
        domain="K",
    )
    target = _hypothesis(
        "x",
        construction,
        source="source:x",
        occurrence="occurrence:x",
        domain="X",
    )
    body_attempt = nd._right_implication_elimination(
        nd._assume(function),
        nd._assume(target),
    )
    assert body_attempt.proof is not None

    generator = _hypothesis(
        "g",
        nd.RightLinearImplication(time, construction),
        source="source:g",
        occurrence="occurrence:g",
        domain="t",
    )
    input_hypothesis = _hypothesis(
        "c",
        time,
        source="source:c",
        occurrence="occurrence:c",
        domain="K",
    )
    replacement_attempt = nd._right_implication_elimination(
        nd._assume(generator),
        nd._assume(input_hypothesis),
    )
    assert replacement_attempt.proof is not None

    certificate = _successful(
        _right_boundary_substitute(
            body_attempt.proof,
            target,
            replacement_attempt.proof,
        )
    )

    assert certificate.result.context == (
        function,
        generator,
        input_hypothesis,
    )
    assert certificate.result.conclusion == space
    assert certificate.result.ledger == (
        nd._open_use(function),
        nd._open_use(generator),
        nd._open_use(input_hypothesis),
    )
    assert certificate.trace.premise_index == 1
    assert certificate.trace.replacement_count == 1
    soundness = nd._build_rule_soundness_cell(certificate.result)
    assert soundness.verified_worlds == frozenset(nd.BOOLEAN_WORLDS)
    assert nd._context_grade(certificate.result.context) == nd._grade(
        certificate.result.conclusion
    )


def test_ordered_one_hole_substitution_preserves_both_context_sides() -> None:
    construction = nd.Atom("K")
    space = nd.Atom("X")
    time = nd.Atom("t")
    endomorphism = nd.RightLinearImplication(
        construction,
        construction,
    )
    left = _hypothesis(
        "q",
        nd.RightLinearImplication(construction, space),
        source="source:q",
        occurrence="occurrence:q",
        domain="K",
    )
    target = _hypothesis(
        "x",
        endomorphism,
        source="source:x",
        occurrence="occurrence:x",
        domain="X",
    )
    right = _hypothesis(
        "y",
        construction,
        source="source:y",
        occurrence="occurrence:y",
        domain="t",
    )
    inner = nd._right_implication_elimination(
        nd._assume(target),
        nd._assume(right),
    ).proof
    assert inner is not None
    body = nd._right_implication_elimination(
        nd._assume(left),
        inner,
    ).proof
    assert body is not None

    generator = _hypothesis(
        "g",
        nd.RightLinearImplication(time, endomorphism),
        source="source:g",
        occurrence="occurrence:g",
        domain="K",
    )
    seed = _hypothesis(
        "c",
        time,
        source="source:c",
        occurrence="occurrence:c",
        domain="X",
    )
    replacement = nd._right_implication_elimination(
        nd._assume(generator),
        nd._assume(seed),
    ).proof
    assert replacement is not None

    certificate = _successful(
        _ordered_one_hole_substitute(body, target, replacement)
    )
    boundary_attempt = _right_boundary_substitute(
        body,
        target,
        replacement,
    )

    assert certificate.left_context == (left,)
    assert certificate.right_context == (right,)
    assert certificate.result.context == (
        left,
        generator,
        seed,
        right,
    )
    assert certificate.result.ledger == (
        nd._open_use(left),
        nd._open_use(generator),
        nd._open_use(seed),
        nd._open_use(right),
    )
    assert certificate.trace.premise_index == 1
    assert certificate.trace.child is not None
    assert certificate.trace.child.premise_index == 0
    assert isinstance(boundary_attempt, SubstitutionRejected)
    assert boundary_attempt.obstruction == "target-is-not-right-boundary"


def test_substitution_descends_under_a_right_implication_binder() -> None:
    formula = nd.Atom("K")
    identity_type = nd.RightLinearImplication(formula, formula)
    target = _hypothesis(
        "f",
        identity_type,
        source="source:f",
        occurrence="occurrence:f",
        domain="K",
    )
    argument = _hypothesis(
        "y",
        formula,
        source="source:y",
        occurrence="occurrence:y",
        domain="X",
    )
    application = nd._right_implication_elimination(
        nd._assume(target),
        nd._assume(argument),
    ).proof
    assert application is not None
    body = nd._right_implication_introduction(
        argument,
        application,
        binder="binder:y",
    )

    replacement_argument = _hypothesis(
        "h",
        formula,
        source="source:h",
        occurrence="occurrence:h",
        domain="t",
    )
    replacement = nd._right_implication_introduction(
        replacement_argument,
        nd._assume(replacement_argument),
        binder="binder:h",
    )

    certificate = _successful(
        _right_boundary_substitute(body, target, replacement)
    )

    assert certificate.result.context == ()
    assert certificate.result.conclusion == identity_type
    assert certificate.trace.original_rule == (
        "right-implication-introduction"
    )
    assert certificate.trace.premise_index == 0
    assert certificate.trace.child is not None
    assert certificate.trace.child.premise_index == 0
    assert certificate.trace.replacement_count == 1


def test_substitution_rejects_wrong_boundary_type_and_aliases() -> None:
    construction = nd.Atom("K")
    space = nd.Atom("X")
    function = _hypothesis(
        "f",
        nd.RightLinearImplication(construction, space),
        source="source:f",
        occurrence="occurrence:f",
        domain="K",
    )
    target = _hypothesis(
        "x",
        construction,
        source="source:x",
        occurrence="occurrence:x",
        domain="X",
    )
    body = nd._right_implication_elimination(
        nd._assume(function),
        nd._assume(target),
    ).proof
    assert body is not None

    wrong_type = _assumption(
        "wrong",
        space,
        source="source:wrong",
        occurrence="occurrence:wrong",
        domain="t",
    )
    function_replacement = _assumption(
        "function-replacement",
        function.formula,
        source="source:function-replacement",
        occurrence="occurrence:function-replacement",
        domain="t",
    )
    occurrence_alias = _assumption(
        "alias",
        construction,
        source="source:alias",
        occurrence=target.occurrence_id.value,
        domain="t",
    )

    type_result = _right_boundary_substitute(body, target, wrong_type)
    boundary_result = _right_boundary_substitute(
        body,
        function,
        function_replacement,
    )
    alias_result = _right_boundary_substitute(
        body,
        target,
        occurrence_alias,
    )

    assert isinstance(type_result, SubstitutionRejected)
    assert type_result.obstruction == "replacement-conclusion-mismatch"
    assert isinstance(boundary_result, SubstitutionRejected)
    assert boundary_result.obstruction == "target-is-not-right-boundary"
    assert isinstance(alias_result, SubstitutionRejected)
    assert alias_result.obstruction == "freshness:occurrence-alias"

    target_identity = _hypothesis(
        "identity-k",
        nd.RightLinearImplication(construction, construction),
        source="source:identity-k",
        occurrence="occurrence:identity-k",
        domain="K",
    )
    space_argument = _hypothesis(
        "space",
        space,
        source="source:space",
        occurrence="occurrence:space",
        domain="X",
    )
    space_identity = nd._right_implication_introduction(
        space_argument,
        nd._assume(space_argument),
        binder="binder:space",
    )
    equivalent_shadow_result = _right_boundary_substitute(
        nd._assume(target_identity),
        target_identity,
        space_identity,
    )

    assert all(
        nd._satisfies(target_identity.formula, world)
        == nd._satisfies(space_identity.conclusion, world)
        for world in nd.HALT_WORLDS
    )
    assert isinstance(equivalent_shadow_result, SubstitutionRejected)
    assert equivalent_shadow_result.obstruction == (
        "replacement-conclusion-mismatch"
    )


def test_labels_and_provenance_are_not_nominal_resource_authority() -> None:
    formula = nd.Atom("K")
    target = _hypothesis(
        "shared-label",
        formula,
        source="source:target",
        occurrence="occurrence:shared",
        domain="K",
        scope="scope:target",
    )
    replacement_hypothesis = _hypothesis(
        "shared-label",
        formula,
        source="source:replacement",
        occurrence="occurrence:shared",
        domain="X",
        scope="scope:replacement",
    )
    replacement = nd._assume(replacement_hypothesis)

    certificate = _successful(
        _right_boundary_substitute(
            nd._assume(target),
            target,
            replacement,
        )
    )

    assert target.label == replacement_hypothesis.label
    assert target.provenance_id == replacement_hypothesis.provenance_id
    assert target.occurrence_id == replacement_hypothesis.occurrence_id
    assert target.scope_id != replacement_hypothesis.scope_id
    assert certificate.result == replacement


def test_shared_target_source_returns_a_pre_graft_freshness_diagnostic() -> None:
    formula = nd.Atom("K")
    target = _hypothesis(
        "x",
        formula,
        source="source:shared",
        occurrence="occurrence:x",
        domain="K",
    )
    replacement = _assumption(
        "a",
        formula,
        source="source:shared",
        occurrence="occurrence:a",
        domain="X",
    )

    outcome = _right_boundary_substitute(
        nd._assume(target),
        target,
        replacement,
    )

    assert isinstance(outcome, PreGraftFreshnessAperture)
    assert outcome.aperture.source_id == target.resource_source_id
    assert outcome.aperture.source_formula == formula
    assert outcome.aperture.left_port == nd.AperturePort(
        "left",
        nd._open_use(target),
    )
    assert outcome.aperture.right_port == nd.AperturePort(
        "right",
        replacement.ledger[0],
    )
    assert outcome.aperture.required_domain == nd.ResourceDomain.T
    assert outcome.aperture.required_role == "order-schedule"
    assert outcome.aperture.orientation == "forward"
    assert outcome.aperture.residual == ()


def test_substitution_rejects_source_type_and_binder_collisions() -> None:
    construction = nd.Atom("K")
    time = nd.Atom("t")
    target = _hypothesis(
        "x",
        construction,
        source="source:shared",
        occurrence="occurrence:x",
        domain="K",
    )
    generator = _hypothesis(
        "g",
        nd.RightLinearImplication(time, construction),
        source="source:shared",
        occurrence="occurrence:g",
        domain="X",
    )
    input_hypothesis = _hypothesis(
        "c",
        time,
        source="source:c",
        occurrence="occurrence:c",
        domain="t",
    )
    replacement = nd._right_implication_elimination(
        nd._assume(generator),
        nd._assume(input_hypothesis),
    ).proof
    assert replacement is not None

    source_result = _right_boundary_substitute(
        nd._assume(target),
        target,
        replacement,
    )
    assert isinstance(source_result, SubstitutionRejected)
    assert source_result.obstruction == "freshness:source-formula-mismatch"

    identity_type = nd.RightLinearImplication(construction, construction)
    function_target = _hypothesis(
        "f",
        identity_type,
        source="source:f",
        occurrence="occurrence:f",
        domain="K",
    )
    body_argument = _hypothesis(
        "body-argument",
        construction,
        source="source:body-argument",
        occurrence="occurrence:body-argument",
        domain="X",
    )
    application = nd._right_implication_elimination(
        nd._assume(function_target),
        nd._assume(body_argument),
    ).proof
    assert application is not None
    body = nd._right_implication_introduction(
        body_argument,
        application,
        binder="binder:collision",
    )
    replacement_argument = _hypothesis(
        "replacement-argument",
        construction,
        source="source:replacement-argument",
        occurrence="occurrence:replacement-argument",
        domain="t",
    )
    colliding_replacement = nd._right_implication_introduction(
        replacement_argument,
        nd._assume(replacement_argument),
        binder="binder:collision",
    )

    binder_result = _right_boundary_substitute(
        body,
        function_target,
        colliding_replacement,
    )
    assert isinstance(binder_result, SubstitutionRejected)
    assert binder_result.obstruction == "freshness:binder-alias"


def test_substitution_certificate_is_replayable_not_declarative() -> None:
    formula = nd.Atom("K")
    target = _hypothesis(
        "x",
        formula,
        source="source:x",
        occurrence="occurrence:x",
        domain="K",
    )
    replacement = _assumption(
        "a",
        formula,
        source="source:a",
        occurrence="occurrence:a",
        domain="X",
    )
    certificate = _successful(
        _right_boundary_substitute(
            nd._assume(target),
            target,
            replacement,
        )
    )
    forged = replace(
        certificate,
        expected_context=(target,),
    )
    forged_position = replace(
        certificate,
        target_context_index=certificate.target_context_index + 1,
    )

    assert _check_substitution_certificate(certificate)
    assert not _check_substitution_certificate(forged)
    assert not _check_substitution_certificate(forged_position)


def test_beta_redex_and_contractum_need_an_explicit_ledger_map() -> None:
    formula = nd.Atom("K")
    target = _hypothesis(
        "x",
        formula,
        source="source:x",
        occurrence="occurrence:x",
        domain="K",
    )
    body = nd._assume(target)
    abstraction = nd._right_implication_introduction(
        target,
        body,
        binder="binder:x",
    )
    replacement = _assumption(
        "a",
        formula,
        source="source:a",
        occurrence="occurrence:a",
        domain="X",
    )
    redex = nd._right_implication_elimination(
        abstraction,
        replacement,
    ).proof
    assert redex is not None
    contractum = _successful(
        _right_boundary_substitute(body, target, replacement)
    ).result

    retired_target = nd.ResourceUse(
        target,
        status="discharged",
        binder_id=nd.BinderId("binder:x"),
    )
    redex_without_retired_target = tuple(
        use for use in redex.ledger if use != retired_target
    )

    assert redex.conclusion == contractum.conclusion
    assert redex.context == contractum.context
    assert redex.ledger != contractum.ledger
    assert redex_without_retired_target == contractum.ledger


def test_general_beta_changes_order_around_discharged_audit_suffixes() -> None:
    construction = nd.Atom("K")
    space = nd.Atom("X")
    identity_type = nd.RightLinearImplication(construction, construction)
    target_type = nd.RightLinearImplication(identity_type, space)
    target = _hypothesis(
        "x",
        target_type,
        source="source:x",
        occurrence="occurrence:x",
        domain="K",
    )
    internal = _hypothesis(
        "h",
        construction,
        source="source:h",
        occurrence="occurrence:h",
        domain="X",
    )
    closed_identity = nd._right_implication_introduction(
        internal,
        nd._assume(internal),
        binder="binder:h",
    )
    body = nd._right_implication_elimination(
        nd._assume(target),
        closed_identity,
    ).proof
    assert body is not None
    assert body.context == (target,)
    abstraction = nd._right_implication_introduction(
        target,
        body,
        binder="binder:x",
    )
    replacement = _assumption(
        "r",
        target_type,
        source="source:r",
        occurrence="occurrence:r",
        domain="t",
    )
    redex = nd._right_implication_elimination(
        abstraction,
        replacement,
    ).proof
    assert redex is not None
    contractum = _successful(
        _right_boundary_substitute(body, target, replacement)
    ).result

    retired_target = nd.ResourceUse(
        target,
        status="discharged",
        binder_id=nd.BinderId("binder:x"),
    )
    target_index = body.ledger.index(nd._open_use(target))
    prefix = body.ledger[:target_index]
    discharged_suffix = body.ledger[target_index + 1 :]
    redex_without_target = tuple(
        use for use in redex.ledger if use != retired_target
    )

    assert all(use.status == "discharged" for use in discharged_suffix)
    assert redex.ledger == (
        *prefix,
        retired_target,
        *discharged_suffix,
        *replacement.ledger,
    )
    assert contractum.ledger == (
        *prefix,
        *replacement.ledger,
        *discharged_suffix,
    )
    assert redex.context == contractum.context == replacement.context
    assert redex.conclusion == contractum.conclusion == space
    assert redex_without_target != contractum.ledger
    assert _resource_bag(redex_without_target) == _resource_bag(
        contractum.ledger
    )
    assert redex_without_target == (
        closed_identity.ledger[0],
        replacement.ledger[0],
    )
    assert contractum.ledger == (
        replacement.ledger[0],
        closed_identity.ledger[0],
    )
