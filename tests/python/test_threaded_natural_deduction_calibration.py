from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, replace
from enum import Enum
from itertools import combinations
from typing import Literal, TypeAlias


CoordinateName: TypeAlias = Literal["K", "X", "t"]
ResourceDomainName: TypeAlias = Literal["K", "X", "t"]
Orientation: TypeAlias = Literal["forward", "reverse"]
SearchBranch: TypeAlias = Literal["proof", "model"]
ResourceStatus: TypeAlias = Literal["open", "discharged"]
FillerRole: TypeAlias = Literal[
    "construct-mediator",
    "separate-placement",
    "order-schedule",
]


class BooleanCoordinate(Enum):
    K = "K"
    X = "X"
    T = "t"


class ResourceDomain(Enum):
    K = "K"
    X = "X"
    T = "t"


World: TypeAlias = frozenset[BooleanCoordinate]

BOOLEAN_COORDINATES: tuple[BooleanCoordinate, ...] = tuple(BooleanCoordinate)
RESOURCE_DOMAINS: frozenset[ResourceDomain] = frozenset(ResourceDomain)
FORWARD_PAIRS: frozenset[tuple[ResourceDomain, ResourceDomain]] = frozenset(
    {
        (ResourceDomain.K, ResourceDomain.X),
        (ResourceDomain.X, ResourceDomain.T),
        (ResourceDomain.T, ResourceDomain.K),
    }
)
FILLER_ROLE: dict[ResourceDomain, FillerRole] = {
    ResourceDomain.K: "construct-mediator",
    ResourceDomain.X: "separate-placement",
    ResourceDomain.T: "order-schedule",
}


def _worlds(*, include_empty: bool) -> tuple[World, ...]:
    first_size = 0 if include_empty else 1
    return tuple(
        frozenset(face)
        for size in range(first_size, len(BOOLEAN_COORDINATES) + 1)
        for face in combinations(BOOLEAN_COORDINATES, size)
    )


def _world(*coordinates: CoordinateName) -> World:
    return frozenset(BooleanCoordinate(item) for item in coordinates)


BOOLEAN_WORLDS = _worlds(include_empty=True)
HALT_WORLDS = _worlds(include_empty=False)


def _require_nominal_text(value: object, label: str) -> None:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} requires a nonempty string")


@dataclass(frozen=True)
class TaskId:
    value: str

    def __post_init__(self) -> None:
        _require_nominal_text(self.value, "TaskId")


@dataclass(frozen=True)
class ProvenanceId:
    value: str

    def __post_init__(self) -> None:
        _require_nominal_text(self.value, "ProvenanceId")


@dataclass(frozen=True)
class ResourceSourceId:
    value: str

    def __post_init__(self) -> None:
        _require_nominal_text(self.value, "ResourceSourceId")


@dataclass(frozen=True)
class OccurrenceId:
    value: str

    def __post_init__(self) -> None:
        _require_nominal_text(self.value, "OccurrenceId")


@dataclass(frozen=True)
class ScopeId:
    value: str

    def __post_init__(self) -> None:
        _require_nominal_text(self.value, "ScopeId")


@dataclass(frozen=True)
class BinderId:
    value: str

    def __post_init__(self) -> None:
        _require_nominal_text(self.value, "BinderId")


class Formula:
    pass


@dataclass(frozen=True, init=False)
class Atom(Formula):
    name: BooleanCoordinate

    def __init__(
        self,
        name: BooleanCoordinate | CoordinateName,
    ) -> None:
        coordinate = (
            name
            if isinstance(name, BooleanCoordinate)
            else BooleanCoordinate(name)
        )
        object.__setattr__(self, "name", coordinate)


@dataclass(frozen=True)
class SupportOr(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True)
class RightLinearImplication(Formula):
    premise: Formula
    conclusion: Formula


def _is_threaded_formula(formula: Formula) -> bool:
    if isinstance(formula, Atom):
        return isinstance(formula.name, BooleanCoordinate)
    if isinstance(formula, RightLinearImplication):
        return _is_threaded_formula(
            formula.premise
        ) and _is_threaded_formula(formula.conclusion)
    return False


def _satisfies(formula: Formula, world: World) -> bool:
    if isinstance(formula, Atom):
        return formula.name in world
    if isinstance(formula, SupportOr):
        return _satisfies(formula.left, world) or _satisfies(
            formula.right,
            world,
        )
    if isinstance(formula, RightLinearImplication):
        return not _satisfies(formula.premise, world) or _satisfies(
            formula.conclusion,
            world,
        )
    raise TypeError(f"unsupported support formula: {formula!r}")


H7_BACKGROUND = SupportOr(SupportOr(Atom("K"), Atom("X")), Atom("t"))


@contextmanager
def _raises_value_error(message: str):
    try:
        yield
    except ValueError as error:
        assert message in str(error)
    else:
        raise AssertionError("the expected ValueError was not raised")


Grade: TypeAlias = tuple[int, int, int]


def _grade(formula: Formula) -> Grade:
    if isinstance(formula, Atom):
        return tuple(
            1 if formula.name == coordinate else 0
            for coordinate in BOOLEAN_COORDINATES
        )
    if isinstance(formula, RightLinearImplication):
        premise = _grade(formula.premise)
        conclusion = _grade(formula.conclusion)
        return tuple(
            conclusion[index] - premise[index]
            for index in range(len(BOOLEAN_COORDINATES))
        )
    raise TypeError("the grade is defined only on the threaded fragment")


@dataclass(frozen=True)
class HypothesisOccurrence:
    label: str
    formula: Formula
    provenance_id: ProvenanceId
    resource_source_id: ResourceSourceId
    occurrence_id: OccurrenceId
    scope_id: ScopeId
    domain: ResourceDomain


Context: TypeAlias = tuple[HypothesisOccurrence, ...]


def _context_grade(context: Context) -> Grade:
    grades = tuple(_grade(hypothesis.formula) for hypothesis in context)
    return tuple(sum(grade[index] for grade in grades) for index in range(3))


def _occurrence_key(
    hypothesis: HypothesisOccurrence,
) -> tuple[ScopeId, OccurrenceId]:
    return hypothesis.scope_id, hypothesis.occurrence_id


def _validate_threaded_context(context: Context) -> str | None:
    for item in context:
        if not _is_threaded_formula(item.formula):
            return "formula-outside-threaded-fragment"
        if not isinstance(item.domain, ResourceDomain):
            return "resource-domain-outside-triad"
        if not all(
            (
                isinstance(item.provenance_id, ProvenanceId),
                isinstance(item.resource_source_id, ResourceSourceId),
                isinstance(item.occurrence_id, OccurrenceId),
                isinstance(item.scope_id, ScopeId),
            )
        ):
            return "untagged-nominal-identity"
        if not all(
            nominal.value
            for nominal in (
                item.provenance_id,
                item.resource_source_id,
                item.occurrence_id,
                item.scope_id,
            )
        ):
            return "empty-nominal-identity"
    occurrence_keys = tuple(_occurrence_key(item) for item in context)
    if len(set(occurrence_keys)) != len(occurrence_keys):
        return "occurrence-alias"
    source_ids = tuple(item.resource_source_id for item in context)
    if len(set(source_ids)) != len(source_ids):
        return "open-linear-source-alias"
    return None


@dataclass(frozen=True)
class ResourceUse:
    hypothesis: HypothesisOccurrence
    status: ResourceStatus
    binder_id: BinderId | None = None


ResourceLedger: TypeAlias = tuple[ResourceUse, ...]


def _open_use(hypothesis: HypothesisOccurrence) -> ResourceUse:
    return ResourceUse(hypothesis=hypothesis, status="open")


def _validate_ledger(ledger: ResourceLedger) -> str | None:
    context_obstruction = _validate_threaded_context(
        tuple(use.hypothesis for use in ledger)
    )
    if context_obstruction is not None:
        return context_obstruction

    occurrence_keys = tuple(
        _occurrence_key(use.hypothesis)
        for use in ledger
    )
    if len(set(occurrence_keys)) != len(occurrence_keys):
        return "occurrence-alias"

    source_ids = tuple(
        use.hypothesis.resource_source_id
        for use in ledger
    )
    if len(set(source_ids)) != len(source_ids):
        return "linear-source-alias"

    binders = tuple(
        use.binder_id
        for use in ledger
        if use.binder_id is not None
    )
    if len(set(binders)) != len(binders):
        return "binder-alias"

    for use in ledger:
        if use.status not in ("open", "discharged"):
            return "unknown-resource-status"
        if use.status == "open" and use.binder_id is not None:
            return "open-use-has-binder"
        if use.status == "discharged" and use.binder_id is None:
            return "discharged-use-lacks-binder"
        if use.binder_id is not None and not isinstance(
            use.binder_id,
            BinderId,
        ):
            return "untagged-binder-identity"
    return None


def _open_context(ledger: ResourceLedger) -> Context:
    return tuple(
        use.hypothesis
        for use in ledger
        if use.status == "open"
    )


@dataclass(frozen=True)
class AperturePort:
    side: Literal["left", "right"]
    use: ResourceUse


@dataclass(frozen=True)
class ApertureDiagnosticId:
    source_id: ResourceSourceId
    left_occurrence: tuple[ScopeId, OccurrenceId]
    right_occurrence: tuple[ScopeId, OccurrenceId]


@dataclass(frozen=True)
class ApertureBoundaryDiagnostic:
    aperture_id: ApertureDiagnosticId
    source_id: ResourceSourceId
    source_formula: Formula
    left_port: AperturePort
    right_port: AperturePort
    required_domain: ResourceDomain
    required_role: FillerRole
    orientation: Orientation
    residual: ResourceLedger


@dataclass(frozen=True)
class LedgerMerge:
    ledger: ResourceLedger | None = None
    aperture: ApertureBoundaryDiagnostic | None = None
    obstruction: str | None = None


def _remaining_domain(
    left: ResourceDomain,
    right: ResourceDomain,
) -> ResourceDomain | None:
    if left == right:
        return None
    remaining = RESOURCE_DOMAINS - {left, right}
    if len(remaining) != 1:
        return None
    return next(iter(remaining))


def _merge_resource_ledgers(
    left: ResourceLedger,
    right: ResourceLedger,
) -> LedgerMerge:
    if _validate_ledger(left) is not None:
        return LedgerMerge(obstruction="invalid-left-ledger")
    if _validate_ledger(right) is not None:
        return LedgerMerge(obstruction="invalid-right-ledger")

    left_occurrences = {
        _occurrence_key(use.hypothesis)
        for use in left
    }
    right_occurrences = {
        _occurrence_key(use.hypothesis)
        for use in right
    }
    if left_occurrences & right_occurrences:
        return LedgerMerge(obstruction="occurrence-alias")

    left_binders = {
        use.binder_id
        for use in left
        if use.binder_id is not None
    }
    right_binders = {
        use.binder_id
        for use in right
        if use.binder_id is not None
    }
    if left_binders & right_binders:
        return LedgerMerge(obstruction="binder-alias")

    collisions = tuple(
        (left_use, right_use)
        for left_use in left
        for right_use in right
        if left_use.hypothesis.resource_source_id
        == right_use.hypothesis.resource_source_id
    )
    if not collisions:
        merged = left + right
        if _validate_ledger(merged) is not None:
            return LedgerMerge(obstruction="invalid-merged-ledger")
        return LedgerMerge(ledger=merged)
    if len(collisions) != 1:
        return LedgerMerge(obstruction="multiple-linear-source-conflicts")

    left_use, right_use = collisions[0]
    left_hypothesis = left_use.hypothesis
    right_hypothesis = right_use.hypothesis
    if left_hypothesis.formula != right_hypothesis.formula:
        return LedgerMerge(obstruction="source-formula-mismatch")
    if left_hypothesis.domain == right_hypothesis.domain:
        return LedgerMerge(obstruction="same-domain-linear-conflict")
    remaining = _remaining_domain(
        left_hypothesis.domain,
        right_hypothesis.domain,
    )
    if remaining is None:
        return LedgerMerge(obstruction="remaining-domain-not-unique")

    residual = tuple(
        use
        for use in (*left, *right)
        if use not in (left_use, right_use)
    )
    aperture_id = ApertureDiagnosticId(
        source_id=left_hypothesis.resource_source_id,
        left_occurrence=_occurrence_key(left_hypothesis),
        right_occurrence=_occurrence_key(right_hypothesis),
    )
    return LedgerMerge(
        aperture=ApertureBoundaryDiagnostic(
            aperture_id=aperture_id,
            source_id=left_hypothesis.resource_source_id,
            source_formula=left_hypothesis.formula,
            left_port=AperturePort("left", left_use),
            right_port=AperturePort("right", right_use),
            required_domain=remaining,
            required_role=FILLER_ROLE[remaining],
            orientation=(
                "forward"
                if (left_hypothesis.domain, right_hypothesis.domain)
                in FORWARD_PAIRS
                else "reverse"
            ),
            residual=residual,
        )
    )


ProofRule: TypeAlias = Literal[
    "assumption",
    "right-implication-introduction",
    "right-implication-elimination",
]


@dataclass(frozen=True)
class NDProof:
    rule: ProofRule
    conclusion: Formula
    context: Context
    ledger: ResourceLedger
    premises: tuple[NDProof, ...] = ()
    principal: HypothesisOccurrence | None = None
    binder_id: BinderId | None = None


@dataclass(frozen=True)
class ProofAttempt:
    proof: NDProof | None = None
    aperture: ApertureBoundaryDiagnostic | None = None
    obstruction: str | None = None


def _assume(hypothesis: HypothesisOccurrence) -> NDProof:
    obstruction = _validate_threaded_context((hypothesis,))
    if obstruction is not None:
        raise ValueError(f"invalid assumption occurrence: {obstruction}")
    return NDProof(
        rule="assumption",
        conclusion=hypothesis.formula,
        context=(hypothesis,),
        ledger=(_open_use(hypothesis),),
        principal=hypothesis,
    )


def _discharge_use(
    ledger: ResourceLedger,
    hypothesis: HypothesisOccurrence,
    binder_id: BinderId,
) -> ResourceLedger | None:
    if any(use.binder_id == binder_id for use in ledger):
        return None
    matches = tuple(
        index
        for index, use in enumerate(ledger)
        if use.hypothesis == hypothesis and use.status == "open"
    )
    if len(matches) != 1:
        return None
    index = matches[0]
    replacement = ResourceUse(
        hypothesis=hypothesis,
        status="discharged",
        binder_id=binder_id,
    )
    return (*ledger[:index], replacement, *ledger[index + 1 :])


def _right_implication_introduction(
    hypothesis: HypothesisOccurrence,
    body: NDProof,
    *,
    binder: str,
) -> NDProof:
    if not _check_proof(body):
        raise ValueError("the implication body is not a checked derivation")
    if not body.context or body.context[-1] != hypothesis:
        raise ValueError("right implication discharges the right boundary")
    if sum(
        current.resource_source_id == hypothesis.resource_source_id
        for current in body.context
    ) != 1:
        raise ValueError("the discharged source must be open exactly once")

    binder_id = BinderId(binder)
    ledger = _discharge_use(body.ledger, hypothesis, binder_id)
    if ledger is None or _validate_ledger(ledger) is not None:
        raise ValueError("the discharged occurrence must be globally fresh")
    return NDProof(
        rule="right-implication-introduction",
        conclusion=RightLinearImplication(
            hypothesis.formula,
            body.conclusion,
        ),
        context=body.context[:-1],
        ledger=ledger,
        premises=(body,),
        principal=hypothesis,
        binder_id=binder_id,
    )


def _right_implication_elimination(
    function: NDProof,
    argument: NDProof,
) -> ProofAttempt:
    if not _check_proof(function) or not _check_proof(argument):
        return ProofAttempt(obstruction="unchecked-premise")
    if not isinstance(function.conclusion, RightLinearImplication):
        return ProofAttempt(obstruction="function-is-not-right-implication")
    if function.conclusion.premise != argument.conclusion:
        return ProofAttempt(obstruction="implication-premise-mismatch")

    merge = _merge_resource_ledgers(function.ledger, argument.ledger)
    if merge.aperture is not None:
        return ProofAttempt(aperture=merge.aperture)
    if merge.obstruction is not None:
        return ProofAttempt(obstruction=merge.obstruction)
    assert merge.ledger is not None

    context = function.context + argument.context
    if _validate_threaded_context(context) is not None:
        return ProofAttempt(obstruction="invalid-open-context")
    return ProofAttempt(
        proof=NDProof(
            rule="right-implication-elimination",
            conclusion=function.conclusion.conclusion,
            context=context,
            ledger=merge.ledger,
            premises=(function, argument),
        )
    )


def _check_proof(proof: NDProof) -> bool:
    if _validate_threaded_context(proof.context) is not None:
        return False
    if _validate_ledger(proof.ledger) is not None:
        return False
    if _open_context(proof.ledger) != proof.context:
        return False

    if proof.rule == "assumption":
        return (
            proof.principal is not None
            and proof.conclusion == proof.principal.formula
            and proof.context == (proof.principal,)
            and proof.ledger == (_open_use(proof.principal),)
            and not proof.premises
            and proof.binder_id is None
        )

    if proof.rule == "right-implication-introduction":
        if (
            len(proof.premises) != 1
            or proof.principal is None
            or proof.binder_id is None
        ):
            return False
        body = proof.premises[0]
        if not _check_proof(body):
            return False
        expected_ledger = _discharge_use(
            body.ledger,
            proof.principal,
            proof.binder_id,
        )
        return (
            bool(body.context)
            and body.context[-1] == proof.principal
            and proof.context == body.context[:-1]
            and proof.conclusion
            == RightLinearImplication(
                proof.principal.formula,
                body.conclusion,
            )
            and expected_ledger is not None
            and proof.ledger == expected_ledger
        )

    if proof.rule == "right-implication-elimination":
        if (
            len(proof.premises) != 2
            or proof.principal is not None
            or proof.binder_id is not None
        ):
            return False
        function, argument = proof.premises
        if not _check_proof(function) or not _check_proof(argument):
            return False
        if not isinstance(function.conclusion, RightLinearImplication):
            return False
        if function.conclusion.premise != argument.conclusion:
            return False
        merge = _merge_resource_ledgers(function.ledger, argument.ledger)
        return (
            merge.ledger is not None
            and merge.aperture is None
            and merge.obstruction is None
            and proof.context == function.context + argument.context
            and proof.ledger == merge.ledger
            and proof.conclusion == function.conclusion.conclusion
        )

    return False


@dataclass(frozen=True)
class EntailmentProblem:
    task_id: TaskId
    context: Context
    conclusion: Formula
    model_space: tuple[World, ...] = HALT_WORLDS

    def __post_init__(self) -> None:
        if not isinstance(self.task_id, TaskId) or not self.task_id.value:
            raise ValueError("entailment task requires a nonempty TaskId")
        obstruction = _validate_threaded_context(self.context)
        if obstruction is not None:
            raise ValueError(f"invalid threaded context: {obstruction}")
        if not _is_threaded_formula(self.conclusion):
            raise ValueError("conclusion is outside the threaded fragment")
        if self.model_space != HALT_WORLDS:
            raise ValueError("threaded entailment calibration fixes H7")


@dataclass(frozen=True)
class ModelInspection:
    world: World
    premise_truths: tuple[bool, ...]
    conclusion_truth: bool

    @property
    def is_countermodel(self) -> bool:
        return all(self.premise_truths) and not self.conclusion_truth

    @property
    def sequent_holds(self) -> bool:
        return not all(self.premise_truths) or self.conclusion_truth


@dataclass(frozen=True)
class SemanticCertificate:
    problem: EntailmentProblem
    inspections: tuple[ModelInspection, ...]

    @property
    def premise_models(self) -> frozenset[World]:
        return frozenset(
            inspection.world
            for inspection in self.inspections
            if all(inspection.premise_truths)
        )

    @property
    def countermodels(self) -> frozenset[World]:
        return frozenset(
            inspection.world
            for inspection in self.inspections
            if inspection.is_countermodel
        )

    @property
    def sequent_support(self) -> frozenset[World]:
        return frozenset(
            inspection.world
            for inspection in self.inspections
            if inspection.sequent_holds
        )

    @property
    def entails(self) -> bool:
        return not self.countermodels


def _semantic_certificate(problem: EntailmentProblem) -> SemanticCertificate:
    return SemanticCertificate(
        problem=problem,
        inspections=tuple(
            ModelInspection(
                world=world,
                premise_truths=tuple(
                    _satisfies(hypothesis.formula, world)
                    for hypothesis in problem.context
                ),
                conclusion_truth=_satisfies(problem.conclusion, world),
            )
            for world in problem.model_space
        ),
    )


def _check_semantic_certificate(certificate: SemanticCertificate) -> bool:
    return certificate == _semantic_certificate(certificate.problem)


@dataclass(frozen=True)
class RuleWorldObligation:
    world: World
    context_satisfied: bool
    conclusion_satisfied: bool
    verified: bool


@dataclass(frozen=True)
class RuleSoundnessCell:
    rule: ProofRule
    obligations: tuple[RuleWorldObligation, ...]
    premises: tuple[RuleSoundnessCell, ...] = ()

    @property
    def verified_worlds(self) -> frozenset[World]:
        return frozenset(
            obligation.world
            for obligation in self.obligations
            if obligation.verified
        )


def _obligation_for_world(
    proof: NDProof,
    premise_cells: tuple[RuleSoundnessCell, ...],
    world: World,
) -> RuleWorldObligation:
    context_satisfied = all(
        _satisfies(hypothesis.formula, world)
        for hypothesis in proof.context
    )
    conclusion_satisfied = _satisfies(proof.conclusion, world)
    if not context_satisfied:
        verified = True
    elif proof.rule == "assumption":
        verified = conclusion_satisfied
    elif proof.rule == "right-implication-introduction":
        assert proof.principal is not None
        body_cell = premise_cells[0]
        body_obligation = next(
            item
            for item in body_cell.obligations
            if item.world == world
        )
        premise_satisfied = _satisfies(proof.principal.formula, world)
        verified = (
            not premise_satisfied
            or (
                body_obligation.context_satisfied
                and body_obligation.conclusion_satisfied
                and body_obligation.verified
                and conclusion_satisfied
            )
        )
    else:
        function, argument = proof.premises
        function_obligation = next(
            item
            for item in premise_cells[0].obligations
            if item.world == world
        )
        argument_obligation = next(
            item
            for item in premise_cells[1].obligations
            if item.world == world
        )
        verified = (
            function_obligation.context_satisfied
            and argument_obligation.context_satisfied
            and function_obligation.conclusion_satisfied
            and argument_obligation.conclusion_satisfied
            and function_obligation.verified
            and argument_obligation.verified
            and _satisfies(function.conclusion, world)
            and _satisfies(argument.conclusion, world)
            and conclusion_satisfied
        )
    return RuleWorldObligation(
        world=world,
        context_satisfied=context_satisfied,
        conclusion_satisfied=conclusion_satisfied,
        verified=verified,
    )


def _build_rule_soundness_cell(proof: NDProof) -> RuleSoundnessCell:
    if not _check_proof(proof):
        raise ValueError("rule soundness requires a recursively checked proof")
    premise_cells = tuple(
        _build_rule_soundness_cell(premise)
        for premise in proof.premises
    )
    obligations = tuple(
        _obligation_for_world(proof, premise_cells, world)
        for world in BOOLEAN_WORLDS
    )
    if not all(obligation.verified for obligation in obligations):
        raise ValueError("a local rule failed Boolean soundness")
    return RuleSoundnessCell(
        rule=proof.rule,
        obligations=obligations,
        premises=premise_cells,
    )


@dataclass(frozen=True)
class SearchEvent:
    branch: SearchBranch
    index: int
    accepted: bool


@dataclass(frozen=True)
class BoundedSearchState:
    problem: EntailmentProblem
    proof_candidates: tuple[NDProof, ...] = ()
    model_worlds: tuple[World, ...] = HALT_WORLDS
    proof_cursor: int = 0
    model_cursor: int = 0
    next_branch: SearchBranch = "proof"

    def __post_init__(self) -> None:
        if self.next_branch not in ("proof", "model"):
            raise ValueError("unknown search branch")
        if any(
            not isinstance(candidate, NDProof)
            for candidate in self.proof_candidates
        ):
            raise ValueError("proof candidate is not an NDProof")
        if not isinstance(self.proof_cursor, int) or isinstance(
            self.proof_cursor,
            bool,
        ):
            raise ValueError("proof cursor must be an integer")
        if not isinstance(self.model_cursor, int) or isinstance(
            self.model_cursor,
            bool,
        ):
            raise ValueError("model cursor must be an integer")
        if not 0 <= self.proof_cursor <= len(self.proof_candidates):
            raise ValueError("proof cursor is outside the candidate list")
        if not 0 <= self.model_cursor <= len(self.model_worlds):
            raise ValueError("model cursor is outside the world list")
        if len(set(self.model_worlds)) != len(self.model_worlds):
            raise ValueError("model world list contains duplicates")
        if not set(self.model_worlds) <= set(self.problem.model_space):
            raise ValueError("model world is outside the problem space")


@dataclass(frozen=True)
class ProofFound:
    candidate_index: int


@dataclass(frozen=True)
class CountermodelFound:
    world_index: int


@dataclass(frozen=True)
class Frontier:
    pass


@dataclass(frozen=True)
class SearchExhausted:
    pass


SearchResult: TypeAlias = (
    ProofFound | CountermodelFound | Frontier | SearchExhausted
)


@dataclass(frozen=True)
class SearchTrace:
    initial_state: BoundedSearchState
    budget: int
    final_state: BoundedSearchState
    events: tuple[SearchEvent, ...]
    result: SearchResult


def _matches_problem(proof: NDProof, problem: EntailmentProblem) -> bool:
    return (
        _check_proof(proof)
        and proof.context == problem.context
        and proof.conclusion == problem.conclusion
    )


def _is_countermodel(problem: EntailmentProblem, world: World) -> bool:
    if world not in problem.model_space:
        return False
    return all(
        _satisfies(hypothesis.formula, world)
        for hypothesis in problem.context
    ) and not _satisfies(problem.conclusion, world)


def _search_result_for_stopping_state(
    state: BoundedSearchState,
) -> SearchResult:
    proof_available = state.proof_cursor < len(state.proof_candidates)
    model_available = state.model_cursor < len(state.model_worlds)
    if proof_available or model_available:
        return Frontier()
    return SearchExhausted()


def _advance_bounded_search(
    state: BoundedSearchState,
    budget: int,
) -> SearchTrace:
    if not isinstance(budget, int) or isinstance(budget, bool):
        raise ValueError("search budget must be an integer")
    if budget < 0:
        raise ValueError("search budget must be nonnegative")

    current = state
    events: list[SearchEvent] = []
    for _ in range(budget):
        proof_available = current.proof_cursor < len(current.proof_candidates)
        model_available = current.model_cursor < len(current.model_worlds)
        if not proof_available and not model_available:
            break

        branch = current.next_branch
        if branch == "proof" and not proof_available:
            branch = "model"
        elif branch == "model" and not model_available:
            branch = "proof"

        if branch == "proof":
            index = current.proof_cursor
            proof = current.proof_candidates[index]
            accepted = _matches_problem(proof, current.problem)
            events.append(SearchEvent("proof", index, accepted))
            current = replace(
                current,
                proof_cursor=index + 1,
                next_branch="model",
            )
            if accepted:
                return SearchTrace(
                    state,
                    budget,
                    current,
                    tuple(events),
                    ProofFound(index),
                )
        else:
            index = current.model_cursor
            world = current.model_worlds[index]
            accepted = _is_countermodel(current.problem, world)
            events.append(SearchEvent("model", index, accepted))
            current = replace(
                current,
                model_cursor=index + 1,
                next_branch="proof",
            )
            if accepted:
                return SearchTrace(
                    state,
                    budget,
                    current,
                    tuple(events),
                    CountermodelFound(index),
                )

    return SearchTrace(
        state,
        budget,
        current,
        tuple(events),
        _search_result_for_stopping_state(current),
    )


def _check_search_trace(trace: SearchTrace) -> bool:
    return trace == _advance_bounded_search(
        trace.initial_state,
        trace.budget,
    )


@dataclass(frozen=True)
class EntailmentTriangleCell:
    problem: EntailmentProblem
    k_proof: NDProof
    k_to_x_cell: RuleSoundnessCell
    x_certificate: SemanticCertificate
    t_trace: SearchTrace
    coherence_worlds: frozenset[World]


def _close_entailment_triangle(
    trace: SearchTrace,
) -> EntailmentTriangleCell:
    if not _check_search_trace(trace):
        raise ValueError("the search trace does not replay")
    if not isinstance(trace.result, ProofFound):
        raise ValueError("only a checked derivation closes the positive triangle")

    problem = trace.initial_state.problem
    proof = trace.initial_state.proof_candidates[
        trace.result.candidate_index
    ]
    if not _matches_problem(proof, problem):
        raise ValueError("the extracted proof does not match the entailment task")

    rule_soundness = _build_rule_soundness_cell(proof)
    certificate = _semantic_certificate(problem)
    if not _check_semantic_certificate(certificate):
        raise ValueError("the direct model scan does not replay")
    if not certificate.entails:
        raise ValueError("a countermodel prevents positive triangle closure")

    direct_support = certificate.sequent_support
    interpreted_support = frozenset(
        world
        for world in rule_soundness.verified_worlds
        if world in problem.model_space
    )
    if direct_support != interpreted_support:
        raise ValueError("the K-X-t support masks do not agree")
    return EntailmentTriangleCell(
        problem=problem,
        k_proof=proof,
        k_to_x_cell=rule_soundness,
        x_certificate=certificate,
        t_trace=trace,
        coherence_worlds=direct_support,
    )


@dataclass(frozen=True)
class CountermodelCell:
    problem: EntailmentProblem
    world: World
    premise_truths: tuple[bool, ...]
    conclusion_false: bool
    t_trace: SearchTrace


def _close_countermodel_cell(trace: SearchTrace) -> CountermodelCell:
    if not _check_search_trace(trace):
        raise ValueError("the search trace does not replay")
    if not isinstance(trace.result, CountermodelFound):
        raise ValueError("only an exact countermodel closes the negative cell")

    problem = trace.initial_state.problem
    world = trace.initial_state.model_worlds[trace.result.world_index]
    if not _is_countermodel(problem, world):
        raise ValueError("the proposed world is not an H7 countermodel")
    premise_truths = tuple(
        _satisfies(hypothesis.formula, world)
        for hypothesis in problem.context
    )
    return CountermodelCell(
        problem=problem,
        world=world,
        premise_truths=premise_truths,
        conclusion_false=not _satisfies(problem.conclusion, world),
        t_trace=trace,
    )


def _hypothesis(
    label: str,
    formula: Formula,
    *,
    source: str,
    occurrence: str,
    domain: ResourceDomain | ResourceDomainName,
    provenance: str = "evidence:shared",
    scope: str = "scope:global",
) -> HypothesisOccurrence:
    return HypothesisOccurrence(
        label=label,
        formula=formula,
        provenance_id=ProvenanceId(provenance),
        resource_source_id=ResourceSourceId(source),
        occurrence_id=OccurrenceId(occurrence),
        scope_id=ScopeId(scope),
        domain=(
            domain
            if isinstance(domain, ResourceDomain)
            else ResourceDomain(domain)
        ),
    )


def _task(value: str) -> TaskId:
    return TaskId(value)


def _rules_in(cell: RuleSoundnessCell) -> tuple[ProofRule, ...]:
    return (
        cell.rule,
        *(
            rule
            for premise in cell.premises
            for rule in _rules_in(premise)
        ),
    )


def test_h7_background_is_a_relative_axiom_not_a_tautology() -> None:
    assert all(_satisfies(H7_BACKGROUND, world) for world in HALT_WORLDS)
    assert not _satisfies(H7_BACKGROUND, frozenset())
    assert len(BOOLEAN_WORLDS) == 8
    assert len(HALT_WORLDS) == 7


def test_formula_resource_and_ledger_sorts_are_runtime_closed() -> None:
    with _raises_value_error("not a valid BooleanCoordinate"):
        Atom("Z")  # type: ignore[arg-type]
    with _raises_value_error("ResourceSourceId requires a nonempty string"):
        ResourceSourceId(1)  # type: ignore[arg-type]
    with _raises_value_error("BinderId requires a nonempty string"):
        BinderId("")

    construction = Atom("K")
    with _raises_value_error("not a valid ResourceDomain"):
        _hypothesis(
            "bad-domain",
            construction,
            source="source:bad-domain",
            occurrence="occurrence:bad-domain",
            domain="Z",  # type: ignore[arg-type]
        )

    hypothesis = _hypothesis(
        "k",
        construction,
        source="source:k",
        occurrence="occurrence:k",
        domain="K",
    )
    untagged_domain = replace(
        hypothesis,
        domain="K",  # type: ignore[arg-type]
    )
    with _raises_value_error("resource-domain-outside-triad"):
        _assume(untagged_domain)
    with _raises_value_error("nonempty TaskId"):
        EntailmentProblem(
            ProvenanceId("wrong-task-sort"),  # type: ignore[arg-type]
            (),
            construction,
        )
    with _raises_value_error("BinderId requires a nonempty string"):
        _right_implication_introduction(
            hypothesis,
            _assume(hypothesis),
            binder="",
        )

    ghost_use = ResourceUse(
        hypothesis,
        status="ghost",  # type: ignore[arg-type]
    )
    identity = _right_implication_introduction(
        hypothesis,
        _assume(hypothesis),
        binder="binder:k",
    )
    raw_binder = replace(
        identity,
        binder_id="raw",  # type: ignore[arg-type]
        ledger=(
            ResourceUse(
                hypothesis,
                status="discharged",
                binder_id="raw",  # type: ignore[arg-type]
            ),
        ),
    )

    assert _validate_ledger((ghost_use,)) == "unknown-resource-status"
    assert not _check_proof(raw_binder)


def test_assumption_and_right_implication_keep_a_complete_ledger() -> None:
    construction = Atom("K")
    hypothesis = _hypothesis(
        "k",
        construction,
        source="source:k",
        occurrence="occurrence:k",
        domain="K",
    )

    identity = _assume(hypothesis)
    abstraction = _right_implication_introduction(
        hypothesis,
        identity,
        binder="binder:k",
    )

    assert _check_proof(identity)
    assert _check_proof(abstraction)
    assert abstraction.context == ()
    assert abstraction.conclusion == RightLinearImplication(
        construction,
        construction,
    )
    assert abstraction.ledger == (
        ResourceUse(
            hypothesis,
            status="discharged",
            binder_id=BinderId("binder:k"),
        ),
    )


def test_right_boundary_discharge_succeeds_with_a_nonempty_prefix() -> None:
    construction = Atom("K")
    space = Atom("X")
    function_hypothesis = _hypothesis(
        "f",
        RightLinearImplication(construction, space),
        source="source:f",
        occurrence="occurrence:f",
        domain="K",
    )
    argument_hypothesis = _hypothesis(
        "a",
        construction,
        source="source:a",
        occurrence="occurrence:a",
        domain="X",
    )
    application = _right_implication_elimination(
        _assume(function_hypothesis),
        _assume(argument_hypothesis),
    ).proof
    assert application is not None

    abstraction = _right_implication_introduction(
        argument_hypothesis,
        application,
        binder="binder:a",
    )

    assert _check_proof(abstraction)
    assert abstraction.context == (function_hypothesis,)
    assert abstraction.conclusion == RightLinearImplication(
        construction,
        space,
    )
    with _raises_value_error("right boundary"):
        _right_implication_introduction(
            function_hypothesis,
            application,
            binder="binder:f",
        )


def test_elimination_preserves_order_and_is_boolean_sound() -> None:
    construction = Atom("K")
    space = Atom("X")
    function_hypothesis = _hypothesis(
        "f",
        RightLinearImplication(construction, space),
        source="source:f",
        occurrence="occurrence:f",
        domain="K",
    )
    argument_hypothesis = _hypothesis(
        "a",
        construction,
        source="source:a",
        occurrence="occurrence:a",
        domain="X",
    )

    attempt = _right_implication_elimination(
        _assume(function_hypothesis),
        _assume(argument_hypothesis),
    )

    assert attempt.proof is not None
    assert attempt.proof.context == (
        function_hypothesis,
        argument_hypothesis,
    )
    assert attempt.proof.conclusion == space
    assert _check_proof(attempt.proof)
    soundness = _build_rule_soundness_cell(attempt.proof)
    assert soundness.verified_worlds == frozenset(BOOLEAN_WORLDS)


def test_task_provenance_and_resource_identity_are_distinct_sorts() -> None:
    marker = "same-display"
    nominal_ids = (
        TaskId(marker),
        ProvenanceId(marker),
        ResourceSourceId(marker),
        OccurrenceId(marker),
        ScopeId(marker),
        BinderId(marker),
    )
    assert len(set(nominal_ids)) == len(nominal_ids)
    assert BooleanCoordinate.K != ResourceDomain.K

    construction = Atom("K")
    space = Atom("X")
    function_hypothesis = _hypothesis(
        "f",
        RightLinearImplication(construction, space),
        source="source:f",
        occurrence="occurrence:f",
        domain="K",
        provenance="evidence:function",
    )
    argument_hypothesis = _hypothesis(
        "a",
        construction,
        source="source:a",
        occurrence="occurrence:a",
        domain="X",
        provenance="evidence:argument",
    )

    attempt = _right_implication_elimination(
        _assume(function_hypothesis),
        _assume(argument_hypothesis),
    )
    problem = EntailmentProblem(
        _task("entailment:one"),
        attempt.proof.context if attempt.proof is not None else (),
        space,
    )

    assert attempt.proof is not None
    assert problem.task_id != function_hypothesis.provenance_id
    assert (
        function_hypothesis.provenance_id
        != argument_hypothesis.provenance_id
    )


def test_shared_source_requires_one_canonical_formula_before_opening() -> None:
    construction = Atom("K")
    space = Atom("X")
    function_use = _open_use(
        _hypothesis(
            "f",
            RightLinearImplication(construction, space),
            source="source:shared",
            occurrence="occurrence:f",
            domain="K",
        )
    )
    argument_use = _open_use(
        _hypothesis(
            "a",
            construction,
            source="source:shared",
            occurrence="occurrence:a",
            domain="X",
        )
    )

    merge = _merge_resource_ledgers((function_use,), (argument_use,))

    assert merge.aperture is None
    assert merge.obstruction == "source-formula-mismatch"


def test_typed_shared_source_exposes_the_remaining_domain_boundary() -> None:
    construction = Atom("K")
    left_use = _open_use(
        _hypothesis(
            "left",
            construction,
            source="source:shared",
            occurrence="occurrence:left",
            domain="K",
            provenance="evidence:left",
        )
    )
    right_use = _open_use(
        _hypothesis(
            "right",
            construction,
            source="source:shared",
            occurrence="occurrence:right",
            domain="X",
            provenance="evidence:right",
        )
    )

    merge = _merge_resource_ledgers((left_use,), (right_use,))
    left_residual = _open_use(
        _hypothesis(
            "left-residual",
            Atom("X"),
            source="source:left-residual",
            occurrence="occurrence:left-residual",
            domain="t",
        )
    )
    right_residual = _open_use(
        _hypothesis(
            "right-residual",
            Atom("X"),
            source="source:right-residual",
            occurrence="occurrence:right-residual",
            domain="K",
        )
    )
    merge_with_residual = _merge_resource_ledgers(
        (left_use, left_residual),
        (right_use, right_residual),
    )

    assert merge.ledger is None
    assert merge.aperture is not None
    assert merge.aperture.source_formula == construction
    assert merge.aperture.required_domain == ResourceDomain.T
    assert merge.aperture.required_role == "order-schedule"
    assert merge.aperture.orientation == "forward"
    assert merge.aperture.left_port.use == left_use
    assert merge.aperture.right_port.use == right_use
    assert merge.aperture.residual == ()
    assert merge_with_residual.aperture is not None
    assert merge_with_residual.aperture.residual == (
        left_residual,
        right_residual,
    )


def test_alias_and_same_domain_conflicts_do_not_open_a_hole() -> None:
    construction = Atom("K")
    left = _open_use(
        _hypothesis(
            "left",
            construction,
            source="source:shared",
            occurrence="occurrence:alias",
            domain="K",
        )
    )
    occurrence_alias = _open_use(
        _hypothesis(
            "alias",
            construction,
            source="source:other",
            occurrence="occurrence:alias",
            domain="X",
        )
    )
    same_domain = _open_use(
        _hypothesis(
            "same-domain",
            construction,
            source="source:shared",
            occurrence="occurrence:other",
            domain="K",
        )
    )

    alias_merge = _merge_resource_ledgers((left,), (occurrence_alias,))
    domain_merge = _merge_resource_ledgers((left,), (same_domain,))
    left_second = _open_use(
        _hypothesis(
            "left-second",
            construction,
            source="source:second",
            occurrence="occurrence:left-second",
            domain="X",
        )
    )
    right_second = _open_use(
        _hypothesis(
            "right-second",
            construction,
            source="source:second",
            occurrence="occurrence:right-second",
            domain="t",
        )
    )
    multiple_merge = _merge_resource_ledgers(
        (left, left_second),
        (
            _open_use(
                _hypothesis(
                    "right-first",
                    construction,
                    source="source:shared",
                    occurrence="occurrence:right-first",
                    domain="X",
                )
            ),
            right_second,
        ),
    )
    binder = BinderId("binder:alias")
    left_bound = ResourceUse(
        _hypothesis(
            "left-bound",
            construction,
            source="source:left-bound",
            occurrence="occurrence:left-bound",
            domain="K",
        ),
        status="discharged",
        binder_id=binder,
    )
    right_bound = ResourceUse(
        _hypothesis(
            "right-bound",
            construction,
            source="source:right-bound",
            occurrence="occurrence:right-bound",
            domain="X",
        ),
        status="discharged",
        binder_id=binder,
    )
    binder_merge = _merge_resource_ledgers(
        (left_bound,),
        (right_bound,),
    )

    assert alias_merge.obstruction == "occurrence-alias"
    assert alias_merge.aperture is None
    assert domain_merge.obstruction == "same-domain-linear-conflict"
    assert domain_merge.aperture is None
    assert multiple_merge.obstruction == "multiple-linear-source-conflicts"
    assert multiple_merge.aperture is None
    assert binder_merge.obstruction == "binder-alias"


def test_discharge_cannot_hide_reuse_of_a_linear_occurrence() -> None:
    construction = Atom("K")
    hypothesis = _hypothesis(
        "h",
        construction,
        source="source:shared",
        occurrence="occurrence:shared",
        domain="K",
    )
    closed_identity = _right_implication_introduction(
        hypothesis,
        _assume(hypothesis),
        binder="binder:identity",
    )

    attempt = _right_implication_elimination(
        closed_identity,
        _assume(hypothesis),
    )
    fresh_occurrence_same_source = _hypothesis(
        "fresh-name",
        construction,
        source="source:shared",
        occurrence="occurrence:fresh",
        domain="K",
    )
    source_reuse = _right_implication_elimination(
        closed_identity,
        _assume(fresh_occurrence_same_source),
    )

    assert attempt.proof is None
    assert attempt.obstruction == "occurrence-alias"
    assert source_reuse.proof is None
    assert source_reuse.obstruction == "same-domain-linear-conflict"


def test_checked_trace_closes_a_structural_entailment_triangle() -> None:
    construction = Atom("K")
    space = Atom("X")
    function_hypothesis = _hypothesis(
        "f",
        RightLinearImplication(construction, space),
        source="source:f",
        occurrence="occurrence:f",
        domain="K",
    )
    argument_hypothesis = _hypothesis(
        "a",
        construction,
        source="source:a",
        occurrence="occurrence:a",
        domain="X",
    )
    application = _right_implication_elimination(
        _assume(function_hypothesis),
        _assume(argument_hypothesis),
    ).proof
    assert application is not None
    proof = _right_implication_introduction(
        argument_hypothesis,
        application,
        binder="binder:a",
    )
    problem = EntailmentProblem(
        _task("entailment:eta"),
        proof.context,
        proof.conclusion,
    )
    trace = _advance_bounded_search(
        BoundedSearchState(problem, proof_candidates=(proof,)),
        budget=1,
    )

    cell = _close_entailment_triangle(trace)

    assert cell.problem == problem
    assert cell.k_proof == proof
    assert cell.x_certificate.entails
    assert cell.x_certificate.countermodels == frozenset()
    assert cell.coherence_worlds == frozenset(HALT_WORLDS)
    assert set(_rules_in(cell.k_to_x_cell)) == {
        "assumption",
        "right-implication-introduction",
        "right-implication-elimination",
    }
    assert isinstance(cell.t_trace.result, ProofFound)
    assert cell.t_trace.events[-1] == SearchEvent("proof", 0, True)


def test_forged_empty_event_proof_trace_cannot_close_the_triangle() -> None:
    construction = Atom("K")
    hypothesis = _hypothesis(
        "k",
        construction,
        source="source:k",
        occurrence="occurrence:k",
        domain="K",
    )
    proof = _right_implication_introduction(
        hypothesis,
        _assume(hypothesis),
        binder="binder:k",
    )
    problem = EntailmentProblem(
        _task("entailment:forged-trace"),
        (),
        proof.conclusion,
    )
    state = BoundedSearchState(problem, proof_candidates=(proof,))
    forged = SearchTrace(
        initial_state=state,
        budget=1,
        final_state=state,
        events=(),
        result=ProofFound(0),
    )

    assert not _check_search_trace(forged)
    with _raises_value_error("does not replay"):
        _close_entailment_triangle(forged)


def test_search_trace_replay_rejects_a_wrong_branch_coordinate() -> None:
    construction = Atom("K")
    hypothesis = _hypothesis(
        "k",
        construction,
        source="source:k",
        occurrence="occurrence:k",
        domain="K",
    )
    proof = _right_implication_introduction(
        hypothesis,
        _assume(hypothesis),
        binder="binder:k",
    )
    problem = EntailmentProblem(
        _task("entailment:wrong-coordinate"),
        (),
        proof.conclusion,
    )
    valid = _advance_bounded_search(
        BoundedSearchState(problem, proof_candidates=(proof,)),
        budget=1,
    )
    forged = replace(
        valid,
        events=(SearchEvent("model", 0, True),),
    )

    assert _check_search_trace(valid)
    assert not _check_search_trace(forged)


def test_non_entailment_closes_a_replayable_countermodel_cell() -> None:
    construction = Atom("K")
    space = Atom("X")
    construction_hypothesis = _hypothesis(
        "k",
        construction,
        source="source:k",
        occurrence="occurrence:k",
        domain="K",
    )
    reverse_hypothesis = _hypothesis(
        "reverse",
        RightLinearImplication(space, construction),
        source="source:reverse",
        occurrence="occurrence:reverse",
        domain="X",
    )
    problem = EntailmentProblem(
        _task("entailment:countermodel"),
        (construction_hypothesis, reverse_hypothesis),
        space,
    )
    trace = _advance_bounded_search(
        BoundedSearchState(
            problem,
            proof_candidates=(),
            model_worlds=(_world("K"),),
            next_branch="model",
        ),
        budget=1,
    )

    cell = _close_countermodel_cell(trace)

    assert cell.problem == problem
    assert cell.world == _world("K")
    assert all(cell.premise_truths)
    assert cell.conclusion_false
    assert _semantic_certificate(problem).countermodels == frozenset(
        {_world("K"), _world("K", "t")}
    )
    with _raises_value_error("positive triangle"):
        _close_entailment_triangle(trace)


def test_world_outside_h7_is_rejected_before_countermodel_search() -> None:
    problem = EntailmentProblem(
        _task("entailment:h7-membership"),
        (),
        Atom("K"),
    )

    assert not _is_countermodel(problem, frozenset())
    with _raises_value_error("outside the problem space"):
        BoundedSearchState(
            problem,
            proof_candidates=(),
            model_worlds=(frozenset(),),
            next_branch="model",
        )


def test_budget_frontier_and_finite_exhaustion_are_distinct() -> None:
    construction = Atom("K")
    identity_hypothesis = _hypothesis(
        "k",
        construction,
        source="source:k",
        occurrence="occurrence:k",
        domain="K",
    )
    identity = _right_implication_introduction(
        identity_hypothesis,
        _assume(identity_hypothesis),
        binder="binder:k",
    )
    problem = EntailmentProblem(
        _task("entailment:bounded-schedule"),
        (),
        identity.conclusion,
    )
    bad_candidate = _assume(identity_hypothesis)
    first = _advance_bounded_search(
        BoundedSearchState(
            problem,
            proof_candidates=(bad_candidate, identity),
            model_worlds=HALT_WORLDS,
        ),
        budget=2,
    )

    assert isinstance(first.result, Frontier)
    assert tuple(event.branch for event in first.events) == ("proof", "model")
    second = _advance_bounded_search(first.final_state, budget=1)
    assert isinstance(second.result, ProofFound)
    assert _close_entailment_triangle(second).k_proof == identity

    exhausted = _advance_bounded_search(
        BoundedSearchState(
            problem,
            proof_candidates=(),
            model_worlds=(_world("K"),),
            next_branch="model",
        ),
        budget=1,
    )
    assert isinstance(exhausted.result, SearchExhausted)
    with _raises_value_error("positive triangle"):
        _close_entailment_triangle(exhausted)
    with _raises_value_error("countermodel"):
        _close_countermodel_cell(exhausted)


def test_finite_inventory_exhaustion_does_not_decide_entailment() -> None:
    problem = EntailmentProblem(
        _task("entailment:uncovered-inventory"),
        (),
        Atom("K"),
    )
    exhausted = _advance_bounded_search(
        BoundedSearchState(
            problem,
            proof_candidates=(),
            model_worlds=(),
        ),
        budget=0,
    )

    assert isinstance(exhausted.result, SearchExhausted)
    assert _semantic_certificate(problem).countermodels
    with _raises_value_error("positive triangle"):
        _close_entailment_triangle(exhausted)
    with _raises_value_error("countermodel"):
        _close_countermodel_cell(exhausted)


def test_search_state_rejects_cursor_and_world_invariant_violations() -> None:
    problem = EntailmentProblem(
        _task("entailment:state-invariants"),
        (),
        RightLinearImplication(Atom("K"), Atom("K")),
    )

    with _raises_value_error("proof cursor"):
        BoundedSearchState(problem, proof_cursor=-1)
    with _raises_value_error("proof cursor must be an integer"):
        BoundedSearchState(
            problem,
            proof_cursor=0.5,  # type: ignore[arg-type]
        )
    with _raises_value_error("model cursor"):
        BoundedSearchState(problem, model_cursor=len(HALT_WORLDS) + 1)
    with _raises_value_error("model cursor must be an integer"):
        BoundedSearchState(
            problem,
            model_cursor=0.5,  # type: ignore[arg-type]
        )
    with _raises_value_error("duplicates"):
        BoundedSearchState(
            problem,
            model_worlds=(_world("K"), _world("K")),
        )
    with _raises_value_error("unknown search branch"):
        BoundedSearchState(
            problem,
            next_branch="ghost",  # type: ignore[arg-type]
        )
    with _raises_value_error("not an NDProof"):
        BoundedSearchState(
            problem,
            proof_candidates=("ghost",),  # type: ignore[arg-type]
        )
    with _raises_value_error("budget must be an integer"):
        _advance_bounded_search(
            BoundedSearchState(problem),
            budget=0.5,  # type: ignore[arg-type]
        )


def test_entailment_problem_rejects_an_unresolved_shared_source() -> None:
    construction = Atom("K")
    left = _hypothesis(
        "left",
        construction,
        source="source:shared",
        occurrence="occurrence:left",
        domain="K",
    )
    right = _hypothesis(
        "right",
        construction,
        source="source:shared",
        occurrence="occurrence:right",
        domain="X",
    )

    with _raises_value_error("open-linear-source-alias"):
        EntailmentProblem(
            _task("entailment:unresolved-source"),
            (left, right),
            construction,
        )


def test_boolean_validity_does_not_imply_strict_linear_derivability() -> None:
    construction = Atom("K")
    space = Atom("X")
    hypothesis = _hypothesis(
        "k",
        construction,
        source="source:k",
        occurrence="occurrence:k",
        domain="K",
    )
    problem = EntailmentProblem(
        _task("entailment:weakening-gap"),
        (hypothesis,),
        RightLinearImplication(space, construction),
    )

    certificate = _semantic_certificate(problem)

    assert certificate.entails
    assert certificate.countermodels == frozenset()
    assert _context_grade(problem.context) == (1, 0, 0)
    assert _grade(problem.conclusion) == (1, -1, 0)
    assert _context_grade(problem.context) != _grade(problem.conclusion)


def test_forged_proof_node_is_rejected_by_recursive_checking() -> None:
    construction = Atom("K")
    hypothesis = _hypothesis(
        "k",
        construction,
        source="source:k",
        occurrence="occurrence:k",
        domain="K",
    )
    forged = NDProof(
        rule="assumption",
        conclusion=Atom("X"),
        context=(hypothesis,),
        ledger=(_open_use(hypothesis),),
        principal=hypothesis,
    )

    assert not _check_proof(forged)
