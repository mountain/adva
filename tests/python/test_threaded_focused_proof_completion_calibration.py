from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import combinations_with_replacement, product
from typing import Literal, TypeAlias

import pytest

import test_threaded_beta_transport_calibration as beta
import test_threaded_natural_deduction_calibration as nd


SkeletonRule: TypeAlias = Literal[
    "assumption",
    "right-implication-introduction",
    "right-implication-elimination",
]
DescentKind: TypeAlias = Literal[
    "right-introduction",
    "spine-argument",
]
FocusOutcome: TypeAlias = Literal[
    "empty-atomic-context",
    "head-terminal-mismatch",
    "unused-context-suffix",
    "argument-failure",
    "success",
]


@dataclass(frozen=True)
class FormulaSkeletonProof:
    rule: SkeletonRule
    conclusion: nd.Formula
    context: tuple[nd.Formula, ...]
    premises: tuple[FormulaSkeletonProof, ...] = ()
    principal_formula: nd.Formula | None = None


@dataclass(frozen=True)
class FreshDecorationLift:
    skeleton: FormulaSkeletonProof
    namespace: str
    boundary_context: nd.Context
    proof: nd.NDProof


@dataclass(frozen=True)
class FocusedJudgment:
    context: tuple[nd.Formula, ...]
    conclusion: nd.Formula


@dataclass(frozen=True)
class FocusedDescent:
    parent: FocusedJudgment
    child: FocusedJudgment
    kind: DescentKind
    parent_measure: int
    child_measure: int


@dataclass(frozen=True)
class AtomicFocusAttempt:
    judgment: FocusedJudgment
    head_formula: nd.Formula | None
    argument_types: tuple[nd.Formula, ...]
    terminal_formula: nd.Formula | None
    segments: tuple[tuple[nd.Formula, ...], ...] | None
    outcome: FocusOutcome


@dataclass(frozen=True)
class FocusedProofFound:
    candidate_index: int
    lift: FreshDecorationLift


@dataclass(frozen=True)
class FocusedSearchExhausted:
    scope: Literal["complete-eta-long-tnd0-skeleton-plan"]
    atomic_attempt_count: int


FocusedSearchResult: TypeAlias = (
    FocusedProofFound | FocusedSearchExhausted
)


@dataclass(frozen=True)
class FocusedSearchReport:
    # Replay reruns this deterministic enumerator; it is not a second kernel.
    problem: FocusedJudgment
    namespace: str
    boundary_context: nd.Context
    visited_judgments: tuple[FocusedJudgment, ...]
    descents: tuple[FocusedDescent, ...]
    atomic_focus_attempts: tuple[AtomicFocusAttempt, ...]
    candidates: tuple[FormulaSkeletonProof, ...]
    result: FocusedSearchResult


def _valid_formula_tuple(value: object) -> bool:
    return type(value) is tuple and all(
        isinstance(formula, nd.Formula)
        and nd._is_threaded_formula(formula)
        for formula in value
    )


def _check_skeleton(proof: FormulaSkeletonProof) -> bool:
    if type(proof) is not FormulaSkeletonProof:
        return False
    if proof.rule not in {
        "assumption",
        "right-implication-introduction",
        "right-implication-elimination",
    }:
        return False
    if not isinstance(proof.conclusion, nd.Formula):
        return False
    if not nd._is_threaded_formula(proof.conclusion):
        return False
    if not _valid_formula_tuple(proof.context):
        return False
    if type(proof.premises) is not tuple:
        return False

    if proof.rule == "assumption":
        return (
            proof.context == (proof.conclusion,)
            and proof.premises == ()
            and proof.principal_formula == proof.conclusion
        )

    if proof.rule == "right-implication-introduction":
        if (
            len(proof.premises) != 1
            or not isinstance(proof.principal_formula, nd.Formula)
        ):
            return False
        body = proof.premises[0]
        return (
            _check_skeleton(body)
            and bool(body.context)
            and body.context[-1] == proof.principal_formula
            and proof.context == body.context[:-1]
            and proof.conclusion
            == nd.RightLinearImplication(
                proof.principal_formula,
                body.conclusion,
            )
        )

    if (
        len(proof.premises) != 2
        or proof.principal_formula is not None
    ):
        return False
    function, argument = proof.premises
    return (
        _check_skeleton(function)
        and _check_skeleton(argument)
        and isinstance(function.conclusion, nd.RightLinearImplication)
        and function.conclusion.premise == argument.conclusion
        and proof.context == function.context + argument.context
        and proof.conclusion == function.conclusion.conclusion
    )


def _skeleton_assumption(formula: nd.Formula) -> FormulaSkeletonProof:
    if not isinstance(formula, nd.Formula):
        raise ValueError("a skeleton assumption requires a formula")
    if not nd._is_threaded_formula(formula):
        raise ValueError("formula is outside the threaded fragment")
    return FormulaSkeletonProof(
        rule="assumption",
        conclusion=formula,
        context=(formula,),
        principal_formula=formula,
    )


def _skeleton_introduction(
    body: FormulaSkeletonProof,
) -> FormulaSkeletonProof:
    if not _check_skeleton(body) or not body.context:
        raise ValueError("introduction needs a checked right boundary")
    principal = body.context[-1]
    return FormulaSkeletonProof(
        rule="right-implication-introduction",
        conclusion=nd.RightLinearImplication(
            principal,
            body.conclusion,
        ),
        context=body.context[:-1],
        premises=(body,),
        principal_formula=principal,
    )


def _skeleton_elimination(
    function: FormulaSkeletonProof,
    argument: FormulaSkeletonProof,
) -> FormulaSkeletonProof | None:
    if not _check_skeleton(function) or not _check_skeleton(argument):
        return None
    if not isinstance(function.conclusion, nd.RightLinearImplication):
        return None
    if function.conclusion.premise != argument.conclusion:
        return None
    return FormulaSkeletonProof(
        rule="right-implication-elimination",
        conclusion=function.conclusion.conclusion,
        context=function.context + argument.context,
        premises=(function, argument),
    )


def _erase_formula_skeleton(
    proof: nd.NDProof,
) -> FormulaSkeletonProof | None:
    if type(proof) is not nd.NDProof or not nd._check_proof(proof):
        return None
    premises = tuple(
        _erase_formula_skeleton(premise) for premise in proof.premises
    )
    if any(premise is None for premise in premises):
        return None
    checked_premises = tuple(
        premise for premise in premises if premise is not None
    )
    principal_formula = (
        proof.principal.formula if proof.principal is not None else None
    )
    skeleton = FormulaSkeletonProof(
        rule=proof.rule,
        conclusion=proof.conclusion,
        context=tuple(item.formula for item in proof.context),
        premises=checked_premises,
        principal_formula=principal_formula,
    )
    return skeleton if _check_skeleton(skeleton) else None


class _FreshNominalSupply:
    def __init__(
        self,
        namespace: str,
        boundary_context: nd.Context,
    ) -> None:
        if type(namespace) is not str or not namespace:
            raise ValueError("fresh namespace must be a nonempty string")
        self.namespace = namespace
        self.next_hypothesis = 0
        self.next_binder = 0
        self.sources = {
            hypothesis.resource_source_id
            for hypothesis in boundary_context
        }
        self.occurrences = {
            nd._occurrence_key(hypothesis)
            for hypothesis in boundary_context
        }
        self.binders: set[nd.BinderId] = set()

    def fresh_hypothesis(
        self,
        formula: nd.Formula,
    ) -> nd.HypothesisOccurrence:
        domains = tuple(nd.ResourceDomain)
        while True:
            serial = self.next_hypothesis
            self.next_hypothesis += 1
            source = nd.ResourceSourceId(
                f"source:focused:{self.namespace}:{serial}"
            )
            scope = nd.ScopeId(f"scope:focused:{self.namespace}")
            occurrence = nd.OccurrenceId(
                f"occurrence:focused:{self.namespace}:{serial}"
            )
            occurrence_key = (scope, occurrence)
            if source in self.sources or occurrence_key in self.occurrences:
                continue
            self.sources.add(source)
            self.occurrences.add(occurrence_key)
            return nd.HypothesisOccurrence(
                label=f"focused:{serial}",
                formula=formula,
                provenance_id=nd.ProvenanceId(
                    f"provenance:focused:{self.namespace}:{serial}"
                ),
                resource_source_id=source,
                occurrence_id=occurrence,
                scope_id=scope,
                domain=domains[serial % len(domains)],
            )

    def fresh_binder(self) -> nd.BinderId:
        while True:
            serial = self.next_binder
            self.next_binder += 1
            binder = nd.BinderId(
                f"binder:focused:{self.namespace}:{serial}"
            )
            if binder in self.binders:
                continue
            self.binders.add(binder)
            return binder


def _fresh_boundary_context(
    formulas: tuple[nd.Formula, ...],
    namespace: str,
) -> nd.Context:
    supply = _FreshNominalSupply(namespace, ())
    return tuple(supply.fresh_hypothesis(formula) for formula in formulas)


def _decorate_node(
    skeleton: FormulaSkeletonProof,
    boundary_context: nd.Context,
    supply: _FreshNominalSupply,
) -> nd.NDProof | None:
    if tuple(item.formula for item in boundary_context) != skeleton.context:
        return None
    if skeleton.rule == "assumption":
        if len(boundary_context) != 1:
            return None
        return nd._assume(boundary_context[0])

    if skeleton.rule == "right-implication-elimination":
        function, argument = skeleton.premises
        split = len(function.context)
        decorated_function = _decorate_node(
            function,
            boundary_context[:split],
            supply,
        )
        decorated_argument = _decorate_node(
            argument,
            boundary_context[split:],
            supply,
        )
        if decorated_function is None or decorated_argument is None:
            return None
        return nd._right_implication_elimination(
            decorated_function,
            decorated_argument,
        ).proof

    assert skeleton.principal_formula is not None
    bound = supply.fresh_hypothesis(skeleton.principal_formula)
    body = _decorate_node(
        skeleton.premises[0],
        (*boundary_context, bound),
        supply,
    )
    if body is None:
        return None
    binder = supply.fresh_binder()
    try:
        return nd._right_implication_introduction(
            bound,
            body,
            binder=binder.value,
        )
    except ValueError:
        return None


def _make_fresh_decoration_lift(
    skeleton: FormulaSkeletonProof,
    *,
    namespace: str,
    boundary_context: nd.Context | None = None,
) -> FreshDecorationLift | None:
    if not _check_skeleton(skeleton):
        return None
    if type(namespace) is not str or not namespace:
        return None
    context = (
        _fresh_boundary_context(skeleton.context, namespace)
        if boundary_context is None
        else boundary_context
    )
    if type(context) is not tuple:
        return None
    if nd._validate_threaded_context(context) is not None:
        return None
    if tuple(item.formula for item in context) != skeleton.context:
        return None
    supply = _FreshNominalSupply(namespace, context)
    proof = _decorate_node(skeleton, context, supply)
    if proof is None or not nd._check_proof(proof):
        return None
    if proof.context != context:
        return None
    if _erase_formula_skeleton(proof) != skeleton:
        return None
    return FreshDecorationLift(skeleton, namespace, context, proof)


def _check_fresh_decoration_lift(lift: FreshDecorationLift) -> bool:
    if type(lift) is not FreshDecorationLift:
        return False
    if type(lift.namespace) is not str or not lift.namespace:
        return False
    if type(lift.boundary_context) is not tuple:
        return False
    try:
        replay = _make_fresh_decoration_lift(
            lift.skeleton,
            namespace=lift.namespace,
            boundary_context=lift.boundary_context,
        )
    except (AttributeError, IndexError, TypeError, ValueError):
        return False
    return replay == lift


def _skeleton_beta_positions(
    proof: FormulaSkeletonProof,
    prefix: tuple[int, ...] = (),
) -> tuple[tuple[int, ...], ...]:
    if not _check_skeleton(proof):
        return ()
    here = (
        (prefix,)
        if proof.rule == "right-implication-elimination"
        and proof.premises[0].rule
        == "right-implication-introduction"
        else ()
    )
    below = tuple(
        position
        for index, premise in enumerate(proof.premises)
        for position in _skeleton_beta_positions(
            premise,
            (*prefix, index),
        )
    )
    return here + below


def _is_neutral(proof: FormulaSkeletonProof) -> bool:
    if not _check_skeleton(proof):
        return False
    if proof.rule == "assumption":
        return True
    if proof.rule != "right-implication-elimination":
        return False
    function, argument = proof.premises
    return _is_neutral(function) and _is_normal(argument)


def _is_normal(proof: FormulaSkeletonProof) -> bool:
    if not _check_skeleton(proof):
        return False
    if proof.rule == "right-implication-introduction":
        return _is_normal(proof.premises[0])
    return _is_neutral(proof)


def _is_long_neutral(proof: FormulaSkeletonProof) -> bool:
    if not _check_skeleton(proof):
        return False
    if proof.rule == "assumption":
        return True
    if proof.rule != "right-implication-elimination":
        return False
    function, argument = proof.premises
    return _is_long_neutral(function) and _is_eta_long(argument)


def _is_eta_long(proof: FormulaSkeletonProof) -> bool:
    if not _check_skeleton(proof):
        return False
    if isinstance(proof.conclusion, nd.RightLinearImplication):
        return (
            proof.rule == "right-implication-introduction"
            and _is_eta_long(proof.premises[0])
        )
    return isinstance(proof.conclusion, nd.Atom) and _is_long_neutral(
        proof
    )


def _eta_long_neutral(
    proof: FormulaSkeletonProof,
) -> FormulaSkeletonProof:
    if not _is_neutral(proof):
        raise ValueError("eta-long neutral completion needs a neutral proof")
    if proof.rule == "assumption":
        return proof
    function, argument = proof.premises
    completed = _skeleton_elimination(
        _eta_long_neutral(function),
        _eta_long_completion(argument),
    )
    assert completed is not None
    return completed


def _eta_long_completion(
    proof: FormulaSkeletonProof,
) -> FormulaSkeletonProof:
    if not _is_normal(proof):
        raise ValueError("eta-long completion needs a beta-normal proof")
    if isinstance(proof.conclusion, nd.Atom):
        return _eta_long_neutral(proof)
    assert isinstance(proof.conclusion, nd.RightLinearImplication)
    if proof.rule == "right-implication-introduction":
        completed_body = _eta_long_completion(proof.premises[0])
        return _skeleton_introduction(completed_body)

    argument = _eta_long_completion(
        _skeleton_assumption(proof.conclusion.premise)
    )
    applied = _skeleton_elimination(
        _eta_long_neutral(proof),
        argument,
    )
    assert applied is not None
    completed_body = _eta_long_completion(applied)
    return _skeleton_introduction(completed_body)


def _formula_subformulas(formula: nd.Formula) -> frozenset[nd.Formula]:
    if isinstance(formula, nd.Atom):
        return frozenset({formula})
    if isinstance(formula, nd.RightLinearImplication):
        return frozenset(
            {
                formula,
                *_formula_subformulas(formula.premise),
                *_formula_subformulas(formula.conclusion),
            }
        )
    raise TypeError("subformula is defined on the threaded fragment")


def _proof_formulas(
    proof: FormulaSkeletonProof,
) -> frozenset[nd.Formula]:
    if not _check_skeleton(proof):
        return frozenset()
    local = {
        proof.conclusion,
        *proof.context,
    }
    if proof.principal_formula is not None:
        local.add(proof.principal_formula)
    for premise in proof.premises:
        local.update(_proof_formulas(premise))
    return frozenset(local)


def _has_subformula_property(proof: FormulaSkeletonProof) -> bool:
    if not _check_skeleton(proof):
        return False
    boundary = set(_formula_subformulas(proof.conclusion))
    for formula in proof.context:
        boundary.update(_formula_subformulas(formula))
    return _proof_formulas(proof) <= boundary


def _right_spine(
    formula: nd.Formula,
) -> tuple[tuple[nd.Formula, ...], nd.Formula]:
    arguments: list[nd.Formula] = []
    result = formula
    while isinstance(result, nd.RightLinearImplication):
        arguments.append(result.premise)
        result = result.conclusion
    return tuple(arguments), result


def _weak_segments(
    context: tuple[nd.Formula, ...],
    parts: int,
) -> tuple[tuple[tuple[nd.Formula, ...], ...], ...]:
    if type(parts) is not int or parts < 0:
        return ()
    if parts == 0:
        return ((),) if not context else ()
    boundaries = tuple(
        (0, *cuts, len(context))
        for cuts in combinations_with_replacement(
            range(len(context) + 1),
            parts - 1,
        )
    )
    return tuple(
        tuple(
            context[left:right]
            for left, right in zip(
                boundary[:-1],
                boundary[1:],
                strict=True,
            )
        )
        for boundary in boundaries
    )


def _deduplicate_skeletons(
    proofs: tuple[FormulaSkeletonProof, ...],
) -> tuple[FormulaSkeletonProof, ...]:
    seen: set[FormulaSkeletonProof] = set()
    result: list[FormulaSkeletonProof] = []
    for proof in proofs:
        if proof in seen:
            continue
        seen.add(proof)
        result.append(proof)
    return tuple(result)


def _right_connective_count(formula: nd.Formula) -> int:
    if isinstance(formula, nd.Atom):
        return 0
    if isinstance(formula, nd.RightLinearImplication):
        return 1 + _right_connective_count(
            formula.premise
        ) + _right_connective_count(formula.conclusion)
    raise TypeError("connective count is defined on the threaded fragment")


def _judgment_measure(judgment: FocusedJudgment) -> int:
    return sum(
        _right_connective_count(formula)
        for formula in judgment.context
    ) + _right_connective_count(
        judgment.conclusion
    )


def _make_descent(
    parent: FocusedJudgment,
    child: FocusedJudgment,
    kind: DescentKind,
) -> FocusedDescent:
    descent = FocusedDescent(
        parent=parent,
        child=child,
        kind=kind,
        parent_measure=_judgment_measure(parent),
        child_measure=_judgment_measure(child),
    )
    if descent.child_measure >= descent.parent_measure:
        raise ValueError("focused recursive measure did not decrease")
    return descent


def _check_descent(descent: FocusedDescent) -> bool:
    if type(descent) is not FocusedDescent:
        return False
    if descent.kind not in {"right-introduction", "spine-argument"}:
        return False
    if type(descent.parent_measure) is not int:
        return False
    if type(descent.child_measure) is not int:
        return False
    try:
        replay = _make_descent(
            descent.parent,
            descent.child,
            descent.kind,
        )
    except (AttributeError, TypeError, ValueError):
        return False
    return replay == descent


def _check_atomic_focus_attempt(attempt: AtomicFocusAttempt) -> bool:
    if type(attempt) is not AtomicFocusAttempt:
        return False
    if type(attempt.judgment) is not FocusedJudgment:
        return False
    if attempt.head_formula is not None and not isinstance(
        attempt.head_formula,
        nd.Formula,
    ):
        return False
    if not _valid_formula_tuple(attempt.argument_types):
        return False
    if attempt.terminal_formula is not None and not isinstance(
        attempt.terminal_formula,
        nd.Formula,
    ):
        return False
    if attempt.segments is not None:
        if type(attempt.segments) is not tuple:
            return False
        if not all(_valid_formula_tuple(segment) for segment in attempt.segments):
            return False
    return attempt.outcome in {
        "empty-atomic-context",
        "head-terminal-mismatch",
        "unused-context-suffix",
        "argument-failure",
        "success",
    }


def _focused_candidates(
    problem: FocusedJudgment,
) -> tuple[
    tuple[FormulaSkeletonProof, ...],
    tuple[FocusedJudgment, ...],
    tuple[FocusedDescent, ...],
    tuple[AtomicFocusAttempt, ...],
]:
    if type(problem) is not FocusedJudgment:
        return (), (), (), ()
    if not _valid_formula_tuple(problem.context):
        return (), (), (), ()
    if not isinstance(problem.conclusion, nd.Formula):
        return (), (), (), ()
    if not nd._is_threaded_formula(problem.conclusion):
        return (), (), (), ()

    memo: dict[FocusedJudgment, tuple[FormulaSkeletonProof, ...]] = {}
    visited: list[FocusedJudgment] = []
    descents: list[FocusedDescent] = []
    focus_attempts: list[AtomicFocusAttempt] = []

    def solve(
        context: tuple[nd.Formula, ...],
        conclusion: nd.Formula,
    ) -> tuple[FormulaSkeletonProof, ...]:
        judgment = FocusedJudgment(context, conclusion)
        cached = memo.get(judgment)
        if cached is not None:
            return cached
        visited.append(judgment)

        if isinstance(conclusion, nd.RightLinearImplication):
            child = FocusedJudgment(
                (*context, conclusion.premise),
                conclusion.conclusion,
            )
            descents.append(
                _make_descent(
                    judgment,
                    child,
                    "right-introduction",
                )
            )
            bodies = solve(
                child.context,
                child.conclusion,
            )
            candidates = tuple(
                _skeleton_introduction(body) for body in bodies
            )
            memo[judgment] = _deduplicate_skeletons(candidates)
            return memo[judgment]

        candidates_list: list[FormulaSkeletonProof] = []
        if not context and isinstance(conclusion, nd.Atom):
            focus_attempts.append(
                AtomicFocusAttempt(
                    judgment=judgment,
                    head_formula=None,
                    argument_types=(),
                    terminal_formula=None,
                    segments=None,
                    outcome="empty-atomic-context",
                )
            )
        elif context and isinstance(conclusion, nd.Atom):
            head = _skeleton_assumption(context[0])
            argument_types, head_result = _right_spine(context[0])
            if head_result != conclusion:
                focus_attempts.append(
                    AtomicFocusAttempt(
                        judgment=judgment,
                        head_formula=context[0],
                        argument_types=argument_types,
                        terminal_formula=head_result,
                        segments=None,
                        outcome="head-terminal-mismatch",
                    )
                )
            else:
                weak_segments = _weak_segments(
                    context[1:],
                    len(argument_types),
                )
                if not weak_segments:
                    focus_attempts.append(
                        AtomicFocusAttempt(
                            judgment=judgment,
                            head_formula=context[0],
                            argument_types=argument_types,
                            terminal_formula=head_result,
                            segments=None,
                            outcome="unused-context-suffix",
                        )
                    )
                for segments in weak_segments:
                    children = tuple(
                        FocusedJudgment(segment, argument_type)
                        for segment, argument_type in zip(
                            segments,
                            argument_types,
                            strict=True,
                        )
                    )
                    descents.extend(
                        _make_descent(
                            judgment,
                            child,
                            "spine-argument",
                        )
                        for child in children
                    )
                    choices = tuple(
                        solve(child.context, child.conclusion)
                        for child in children
                    )
                    if any(not choice for choice in choices):
                        focus_attempts.append(
                            AtomicFocusAttempt(
                                judgment=judgment,
                                head_formula=context[0],
                                argument_types=argument_types,
                                terminal_formula=head_result,
                                segments=segments,
                                outcome="argument-failure",
                            )
                        )
                        continue
                    focus_attempts.append(
                        AtomicFocusAttempt(
                            judgment=judgment,
                            head_formula=context[0],
                            argument_types=argument_types,
                            terminal_formula=head_result,
                            segments=segments,
                            outcome="success",
                        )
                    )
                    combinations = product(*choices) if choices else ((),)
                    for arguments in combinations:
                        candidate = head
                        for argument in arguments:
                            eliminated = _skeleton_elimination(
                                candidate,
                                argument,
                            )
                            assert eliminated is not None
                            candidate = eliminated
                        if candidate.context == context:
                            candidates_list.append(candidate)
        candidates = _deduplicate_skeletons(tuple(candidates_list))
        memo[judgment] = candidates
        return candidates

    candidates = solve(problem.context, problem.conclusion)
    return (
        candidates,
        tuple(visited),
        tuple(descents),
        tuple(focus_attempts),
    )


def _make_focused_search_report(
    problem: FocusedJudgment,
    *,
    namespace: str,
    boundary_context: nd.Context | None = None,
) -> FocusedSearchReport | None:
    if type(problem) is not FocusedJudgment:
        return None
    if not _valid_formula_tuple(problem.context):
        return None
    if not isinstance(problem.conclusion, nd.Formula):
        return None
    if not nd._is_threaded_formula(problem.conclusion):
        return None
    if type(namespace) is not str or not namespace:
        return None
    context = (
        _fresh_boundary_context(problem.context, namespace)
        if boundary_context is None
        else boundary_context
    )
    if type(context) is not tuple:
        return None
    if nd._validate_threaded_context(context) is not None:
        return None
    if tuple(item.formula for item in context) != problem.context:
        return None

    candidates, visited, descents, focus_attempts = _focused_candidates(
        problem
    )
    if candidates:
        lift = _make_fresh_decoration_lift(
            candidates[0],
            namespace=namespace,
            boundary_context=context,
        )
        if lift is None:
            return None
        result: FocusedSearchResult = FocusedProofFound(0, lift)
    else:
        result = FocusedSearchExhausted(
            "complete-eta-long-tnd0-skeleton-plan",
            len(focus_attempts),
        )
    return FocusedSearchReport(
        problem=problem,
        namespace=namespace,
        boundary_context=context,
        visited_judgments=visited,
        descents=descents,
        atomic_focus_attempts=focus_attempts,
        candidates=candidates,
        result=result,
    )


def _check_focused_search_report(report: FocusedSearchReport) -> bool:
    if type(report) is not FocusedSearchReport:
        return False
    if type(report.namespace) is not str or not report.namespace:
        return False
    if type(report.boundary_context) is not tuple:
        return False
    if type(report.visited_judgments) is not tuple:
        return False
    if type(report.descents) is not tuple:
        return False
    if not all(_check_descent(item) for item in report.descents):
        return False
    if type(report.atomic_focus_attempts) is not tuple:
        return False
    if not all(
        _check_atomic_focus_attempt(item)
        for item in report.atomic_focus_attempts
    ):
        return False
    if type(report.candidates) is not tuple:
        return False
    if isinstance(report.result, FocusedProofFound):
        if type(report.result.candidate_index) is not int:
            return False
        if type(report.result.lift) is not FreshDecorationLift:
            return False
    elif isinstance(report.result, FocusedSearchExhausted):
        if (
            report.result.scope
            != "complete-eta-long-tnd0-skeleton-plan"
        ):
            return False
        if type(report.result.atomic_attempt_count) is not int:
            return False
        if report.result.atomic_attempt_count != len(
            report.atomic_focus_attempts
        ):
            return False
    else:
        return False
    try:
        replay = _make_focused_search_report(
            report.problem,
            namespace=report.namespace,
            boundary_context=report.boundary_context,
        )
    except (AttributeError, IndexError, TypeError, ValueError):
        return False
    return replay == report


def _formula_size(formula: nd.Formula) -> int:
    if isinstance(formula, nd.Atom):
        return 1
    if isinstance(formula, nd.RightLinearImplication):
        return 1 + _formula_size(formula.premise) + _formula_size(
            formula.conclusion
        )
    raise TypeError("formula size is defined on the threaded fragment")


def _proof_node_count(proof: FormulaSkeletonProof) -> int:
    return 1 + sum(_proof_node_count(item) for item in proof.premises)


def _bounded_skeletons(
    formulas: tuple[nd.Formula, ...],
    *,
    max_nodes: int,
    max_formula_size: int,
) -> tuple[FormulaSkeletonProof, ...]:
    by_nodes: dict[int, tuple[FormulaSkeletonProof, ...]] = {
        1: tuple(_skeleton_assumption(formula) for formula in formulas)
    }
    for nodes in range(2, max_nodes + 1):
        generated: list[FormulaSkeletonProof] = []
        for body in by_nodes.get(nodes - 1, ()):
            if body.context:
                introduced = _skeleton_introduction(body)
                if _formula_size(introduced.conclusion) <= max_formula_size:
                    generated.append(introduced)
        for left_nodes in range(1, nodes - 1):
            right_nodes = nodes - 1 - left_nodes
            for function, argument in product(
                by_nodes.get(left_nodes, ()),
                by_nodes.get(right_nodes, ()),
            ):
                eliminated = _skeleton_elimination(function, argument)
                if eliminated is not None:
                    generated.append(eliminated)
        by_nodes[nodes] = _deduplicate_skeletons(tuple(generated))
    return tuple(
        proof
        for nodes in range(1, max_nodes + 1)
        for proof in by_nodes.get(nodes, ())
    )


def _external_context(
    formulas: tuple[nd.Formula, ...],
    *,
    stem: str,
) -> nd.Context:
    domains: tuple[nd.ResourceDomainName, ...] = ("K", "X", "t")
    return tuple(
        beta._hypothesis(
            f"{stem}:{index}",
            formula,
            source=f"source:focused-test:{stem}:{index}",
            occurrence=f"occurrence:focused-test:{stem}:{index}",
            domain=domains[index % len(domains)],
        )
        for index, formula in enumerate(formulas)
    )


def _expect_found(report: FocusedSearchReport) -> FocusedProofFound:
    assert _check_focused_search_report(report)
    assert isinstance(report.result, FocusedProofFound)
    return report.result


def test_formula_skeleton_erasure_and_fresh_lifting_replay() -> None:
    k = nd.Atom("K")
    x = nd.Atom("X")
    function_type = nd.RightLinearImplication(k, x)
    problem = FocusedJudgment((function_type, k), x)
    boundary = _external_context(problem.context, stem="erase-lift")
    report = _make_focused_search_report(
        problem,
        namespace="erase-lift",
        boundary_context=boundary,
    )
    assert report is not None
    found = _expect_found(report)
    lift = found.lift
    assert _check_fresh_decoration_lift(lift)
    assert lift.proof.context == boundary
    assert lift.proof.conclusion == x
    assert _erase_formula_skeleton(lift.proof) == lift.skeleton
    assert lift.skeleton == report.candidates[0]

    forged = replace(lift, proof=nd._assume(boundary[0]))
    assert not _check_fresh_decoration_lift(forged)


def test_fresh_lifting_preserves_duplicate_formula_positions() -> None:
    k = nd.Atom("K")
    function_type = nd.RightLinearImplication(k, k)
    problem = FocusedJudgment((function_type, k), k)
    boundary = _external_context(problem.context, stem="duplicate-types")
    report = _make_focused_search_report(
        problem,
        namespace="duplicate-types",
        boundary_context=boundary,
    )
    assert report is not None
    found = _expect_found(report)
    assert found.lift.proof.context == boundary
    assert tuple(
        item.formula for item in found.lift.proof.context
    ) == problem.context
    assert nd._validate_ledger(found.lift.proof.ledger) is None


def test_normal_neutral_exactly_characterizes_no_beta_redex() -> None:
    k = nd.Atom("K")
    identity = _skeleton_introduction(_skeleton_assumption(k))
    detour_function = _skeleton_introduction(
        _skeleton_assumption(identity.conclusion)
    )
    detour = _skeleton_elimination(detour_function, identity)
    assert detour is not None

    assert _is_normal(identity)
    assert not _is_neutral(identity)
    assert _skeleton_beta_positions(identity) == ()
    assert not _is_normal(detour)
    assert _skeleton_beta_positions(detour) == ((),)
    assert _is_normal(identity) == (
        _skeleton_beta_positions(identity) == ()
    )
    assert _is_normal(detour) == (
        _skeleton_beta_positions(detour) == ()
    )


def test_beta_normal_subformula_and_principal_detour_control() -> None:
    k = nd.Atom("K")
    identity = _skeleton_introduction(_skeleton_assumption(k))
    outer_identity = _skeleton_introduction(
        _skeleton_assumption(identity.conclusion)
    )
    detour = _skeleton_elimination(outer_identity, identity)
    assert detour is not None

    assert _is_normal(identity)
    assert _has_subformula_property(identity)
    assert not _is_normal(detour)
    assert not _has_subformula_property(detour)
    assert outer_identity.conclusion in _proof_formulas(detour)
    assert outer_identity.conclusion not in _formula_subformulas(
        detour.conclusion
    )


def test_closed_identity_and_already_normal_atomic_identity() -> None:
    k = nd.Atom("K")
    closed_problem = FocusedJudgment(
        (),
        nd.RightLinearImplication(k, k),
    )
    closed_report = _make_focused_search_report(
        closed_problem,
        namespace="closed-identity",
    )
    assert closed_report is not None
    closed = _expect_found(closed_report).lift.skeleton
    assert closed.rule == "right-implication-introduction"
    assert closed.context == ()
    assert _is_eta_long(closed)

    open_problem = FocusedJudgment((k,), k)
    open_report = _make_focused_search_report(
        open_problem,
        namespace="open-atomic-identity",
    )
    assert open_report is not None
    opened = _expect_found(open_report).lift.skeleton
    assert opened == _skeleton_assumption(k)
    assert _is_neutral(opened)
    assert _is_eta_long(opened)


def test_arrow_identity_is_eta_completed_not_called_a_reduction() -> None:
    k = nd.Atom("K")
    arrow = nd.RightLinearImplication(k, k)
    short = _skeleton_assumption(arrow)
    completed = _eta_long_completion(short)
    assert _is_normal(short)
    assert not _is_eta_long(short)
    assert _is_eta_long(completed)
    assert completed.context == short.context
    assert completed.conclusion == short.conclusion
    assert completed != short
    assert _skeleton_beta_positions(completed) == ()

    report = _make_focused_search_report(
        FocusedJudgment((arrow,), arrow),
        namespace="eta-completed-arrow-identity",
    )
    assert report is not None
    assert _expect_found(report).lift.skeleton == completed


def test_focused_search_is_order_sensitive_in_both_directions() -> None:
    k = nd.Atom("K")
    x = nd.Atom("X")
    function_type = nd.RightLinearImplication(k, x)
    forward = _make_focused_search_report(
        FocusedJudgment((function_type, k), x),
        namespace="order-forward",
    )
    reverse = _make_focused_search_report(
        FocusedJudgment((k, function_type), x),
        namespace="order-reverse",
    )
    assert forward is not None
    assert reverse is not None
    _expect_found(forward)
    assert _check_focused_search_report(reverse)
    assert isinstance(reverse.result, FocusedSearchExhausted)
    assert reverse.candidates == ()


def test_weak_partition_accepts_a_closed_spine_argument() -> None:
    k = nd.Atom("K")
    x = nd.Atom("X")
    closed_argument_type = nd.RightLinearImplication(x, x)
    head_type = nd.RightLinearImplication(closed_argument_type, k)
    report = _make_focused_search_report(
        FocusedJudgment((head_type,), k),
        namespace="closed-spine-argument",
    )
    assert report is not None
    found = _expect_found(report)
    skeleton = found.lift.skeleton
    assert skeleton.rule == "right-implication-elimination"
    argument = skeleton.premises[1]
    assert argument.context == ()
    assert argument.conclusion == closed_argument_type
    assert _is_eta_long(argument)
    assert _weak_segments((), 1) == (((),),)


def test_multi_argument_spine_checks_all_ordered_weak_partitions() -> None:
    k = nd.Atom("K")
    x = nd.Atom("X")
    t = nd.Atom("t")
    head_type = nd.RightLinearImplication(
        k,
        nd.RightLinearImplication(x, t),
    )
    report = _make_focused_search_report(
        FocusedJudgment((head_type, k, x), t),
        namespace="two-spine-arguments",
    )
    assert report is not None
    found = _expect_found(report)
    assert found.lift.skeleton.context == (head_type, k, x)
    successful = tuple(
        attempt
        for attempt in report.atomic_focus_attempts
        if attempt.judgment == report.problem
        and attempt.outcome == "success"
    )
    assert tuple(item.segments for item in successful) == (((k,), (x,)),)
    expected_segments = (
        ((), (k, x)),
        ((k,), (x,)),
        ((k, x), ()),
    )
    assert _weak_segments((k, x), 2) == expected_segments
    root_attempts = tuple(
        attempt
        for attempt in report.atomic_focus_attempts
        if attempt.judgment == report.problem
    )
    assert tuple(item.segments for item in root_attempts) == (
        expected_segments
    )
    assert all(_check_descent(item) for item in report.descents)
    assert all(
        item.child_measure < item.parent_measure
        for item in report.descents
    )
    forged_attempts = replace(
        report,
        atomic_focus_attempts=report.atomic_focus_attempts[1:],
    )
    assert not _check_focused_search_report(forged_attempts)


def test_reused_closed_skeleton_gets_distinct_fresh_authorities() -> None:
    p = nd.Atom("K")
    q = nd.Atom("X")
    unit = nd.RightLinearImplication(p, p)
    head_type = nd.RightLinearImplication(
        unit,
        nd.RightLinearImplication(unit, q),
    )
    report = _make_focused_search_report(
        FocusedJudgment((head_type,), q),
        namespace="reused-closed-skeleton",
    )
    assert report is not None
    found = _expect_found(report)
    assert len(report.candidates) == 1

    skeleton = found.lift.skeleton
    first_skeleton_argument = skeleton.premises[0].premises[1]
    second_skeleton_argument = skeleton.premises[1]
    assert first_skeleton_argument is second_skeleton_argument
    assert first_skeleton_argument.context == ()

    proof = found.lift.proof
    first_argument = proof.premises[0].premises[1]
    second_argument = proof.premises[1]
    assert first_argument != second_argument
    assert nd._check_proof(first_argument)
    assert nd._check_proof(second_argument)
    assert nd._check_proof(proof)

    first_use = first_argument.ledger[0]
    second_use = second_argument.ledger[0]
    assert first_use.status == "discharged"
    assert second_use.status == "discharged"
    assert first_use.hypothesis.resource_source_id != (
        second_use.hypothesis.resource_source_id
    )
    assert nd._occurrence_key(first_use.hypothesis) != (
        nd._occurrence_key(second_use.hypothesis)
    )
    assert first_use.binder_id != second_use.binder_id
    assert beta._discharged_count(proof.ledger) == 2
    assert _check_fresh_decoration_lift(found.lift)


def test_focused_search_retains_two_noncanonical_proofs() -> None:
    p = nd.Atom("K")
    q = nd.Atom("X")
    unit = nd.RightLinearImplication(p, p)
    head_type = nd.RightLinearImplication(
        unit,
        nd.RightLinearImplication(unit, q),
    )
    problem = FocusedJudgment((head_type, unit), q)
    boundary = _external_context(problem.context, stem="two-focused-proofs")
    report = _make_focused_search_report(
        problem,
        namespace="two-focused-proofs",
        boundary_context=boundary,
    )
    assert report is not None
    _expect_found(report)
    assert len(report.candidates) == 2
    assert report.candidates[0] != report.candidates[1]
    assert len(set(report.candidates)) == 2

    root_attempts = tuple(
        attempt
        for attempt in report.atomic_focus_attempts
        if attempt.judgment == problem
    )
    assert tuple(item.segments for item in root_attempts) == (
        ((), (unit,)),
        ((unit,), ()),
    )
    assert all(item.outcome == "success" for item in root_attempts)

    lifts = tuple(
        _make_fresh_decoration_lift(
            candidate,
            namespace=f"two-focused-proofs:{index}",
            boundary_context=boundary,
        )
        for index, candidate in enumerate(report.candidates)
    )
    assert all(lift is not None for lift in lifts)
    checked_lifts = tuple(lift for lift in lifts if lift is not None)
    assert len(checked_lifts) == 2
    assert checked_lifts[0].proof != checked_lifts[1].proof
    for lift in checked_lifts:
        assert nd._check_proof(lift.proof)
        assert lift.proof.context == boundary
        assert _is_normal(lift.skeleton)
        assert _is_eta_long(lift.skeleton)
        assert _has_subformula_property(lift.skeleton)


def test_head_terminal_with_unused_suffix_is_complete_failure() -> None:
    k = nd.Atom("K")
    report = _make_focused_search_report(
        FocusedJudgment((k, k), k),
        namespace="unused-suffix",
    )
    assert report is not None
    assert _check_focused_search_report(report)
    assert isinstance(report.result, FocusedSearchExhausted)
    assert report.atomic_focus_attempts == (
        AtomicFocusAttempt(
            judgment=report.problem,
            head_formula=k,
            argument_types=(),
            terminal_formula=k,
            segments=None,
            outcome="unused-context-suffix",
        ),
    )


def test_closed_atomic_goal_has_a_complete_empty_focus_attempt() -> None:
    k = nd.Atom("K")
    report = _make_focused_search_report(
        FocusedJudgment((), k),
        namespace="closed-atom-failure",
    )
    assert report is not None
    assert _check_focused_search_report(report)
    assert isinstance(report.result, FocusedSearchExhausted)
    assert report.atomic_focus_attempts == (
        AtomicFocusAttempt(
            judgment=report.problem,
            head_formula=None,
            argument_types=(),
            terminal_formula=None,
            segments=None,
            outcome="empty-atomic-context",
        ),
    )


def test_complete_syntactic_failure_is_not_a_semantic_result() -> None:
    k = nd.Atom("K")
    x = nd.Atom("X")
    report = _make_focused_search_report(
        FocusedJudgment((k,), x),
        namespace="complete-syntactic-failure",
    )
    assert report is not None
    assert _check_focused_search_report(report)
    assert isinstance(report.result, FocusedSearchExhausted)
    assert report.result.scope == (
        "complete-eta-long-tnd0-skeleton-plan"
    )
    assert report.result.atomic_attempt_count == 1
    assert report.candidates == ()
    assert report.visited_judgments == (
        FocusedJudgment((k,), x),
    )
    assert report.atomic_focus_attempts[0].outcome == (
        "head-terminal-mismatch"
    )


def test_search_report_rejects_forged_plan_result_and_boundary() -> None:
    k = nd.Atom("K")
    problem = FocusedJudgment((k,), k)
    report = _make_focused_search_report(
        problem,
        namespace="report-forgery",
    )
    assert report is not None
    found = _expect_found(report)
    forged_plan = replace(report, visited_judgments=())
    forged_index = replace(
        report,
        result=replace(found, candidate_index=False),
    )
    wrong_boundary = _external_context((nd.Atom("X"),), stem="wrong")
    forged_boundary = replace(report, boundary_context=wrong_boundary)
    forged_candidate = replace(
        report,
        candidates=(
            _skeleton_introduction(_skeleton_assumption(k)),
        ),
    )
    assert not _check_focused_search_report(forged_plan)
    assert not _check_focused_search_report(forged_index)
    assert not _check_focused_search_report(forged_boundary)
    assert not _check_focused_search_report(forged_candidate)


def test_invalid_skeletons_and_unchecked_lifts_are_rejected() -> None:
    k = nd.Atom("K")
    valid = _skeleton_assumption(k)
    invalid = replace(valid, context=())
    assert not _check_skeleton(invalid)
    assert _erase_formula_skeleton(
        replace(nd._assume(_external_context((k,), stem="unchecked")[0]),
                context=())
    ) is None
    assert _make_fresh_decoration_lift(
        invalid,
        namespace="invalid",
    ) is None
    assert _make_focused_search_report(
        FocusedJudgment((k,), k),
        namespace="",
    ) is None


@pytest.mark.parametrize("max_nodes", (1, 2, 3, 4, 5))
def test_bounded_generated_skeleton_cross_check(max_nodes: int) -> None:
    k = nd.Atom("K")
    x = nd.Atom("X")
    formulas = (
        k,
        x,
        nd.RightLinearImplication(k, k),
        nd.RightLinearImplication(k, x),
        nd.RightLinearImplication(x, k),
    )
    generated = _bounded_skeletons(
        formulas,
        max_nodes=max_nodes,
        max_formula_size=7,
    )
    assert generated
    for index, skeleton in enumerate(generated):
        assert _check_skeleton(skeleton)
        assert _proof_node_count(skeleton) <= max_nodes
        is_redex_free = _skeleton_beta_positions(skeleton) == ()
        assert _is_normal(skeleton) == is_redex_free
        direct_lift = _make_fresh_decoration_lift(
            skeleton,
            namespace=f"generated-direct:{max_nodes}:{index}",
        )
        assert direct_lift is not None
        assert beta._beta_redex_positions(direct_lift.proof) == (
            _skeleton_beta_positions(skeleton)
        )
        if is_redex_free:
            assert _has_subformula_property(skeleton)
            completed = _eta_long_completion(skeleton)
            assert _is_eta_long(completed)
            assert completed.context == skeleton.context
            assert completed.conclusion == skeleton.conclusion

        problem = FocusedJudgment(
            skeleton.context,
            skeleton.conclusion,
        )
        report = _make_focused_search_report(
            problem,
            namespace=f"generated:{max_nodes}:{index}",
        )
        assert report is not None
        found = _expect_found(report)
        assert _is_eta_long(found.lift.skeleton)
        assert found.lift.skeleton.context == skeleton.context
        assert found.lift.skeleton.conclusion == skeleton.conclusion
        assert nd._check_proof(found.lift.proof)
