"""Pure-Python research oracle; it creates no Adva semantic authority."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum

import pytest


class Side(Enum):
    PROOF = "proof"
    LEARNING = "learning"


class Stage(Enum):
    ZERO = 0
    ONE = 1


@dataclass(frozen=True)
class Configuration:
    side: Side
    stage: Stage


P0 = Configuration(Side.PROOF, Stage.ZERO)
P1 = Configuration(Side.PROOF, Stage.ONE)
L0 = Configuration(Side.LEARNING, Stage.ZERO)
L1 = Configuration(Side.LEARNING, Stage.ONE)
CARRIER = (P0, P1, L0, L1)
EDGES = frozenset({(P1, P0), (L0, L1)})


def star(configuration: Configuration) -> Configuration:
    side = Side.LEARNING if configuration.side is Side.PROOF else Side.PROOF
    return Configuration(side, configuration.stage)


def _unique_walk(start: Configuration, *, backwards: bool) -> Configuration:
    current = start
    visited: set[Configuration] = set()
    while current not in visited:
        visited.add(current)
        candidates = [
            source if backwards else target
            for source, target in EDGES
            if (target if backwards else source) == current
        ]
        if not candidates:
            return current
        if len(candidates) != 1:
            raise ValueError("V0 requires a unique finite normalizing path")
        current = candidates[0]
    raise ValueError("the finite normalization relation contains a cycle")


def forward_normal_form(configuration: Configuration) -> Configuration:
    return _unique_walk(configuration, backwards=False)


def learning_generator(configuration: Configuration) -> Configuration:
    if configuration.side is not Side.LEARNING:
        raise TypeError("a learning generator requires a learning configuration")
    return _unique_walk(configuration, backwards=True)


class LocalStatus(Enum):
    REDUCIBLE = "reducible"
    SATURATED = "saturated"


class RunDisposition(Enum):
    COMPLETE = "complete"
    BUDGET_EXHAUSTED = "budget-exhausted"


@dataclass(frozen=True)
class Atom:
    name: str


@dataclass(frozen=True)
class SignedAtom:
    atom: Atom
    positive: bool


@dataclass(frozen=True)
class WorkItem:
    rule: str
    subject: Atom


@dataclass(frozen=True)
class ClosureCertificate:
    atom: Atom


@dataclass(frozen=True)
class Branch:
    literals: tuple[SignedAtom, ...]
    local_status: LocalStatus
    pending: tuple[WorkItem, ...] = ()
    certificate: ClosureCertificate | None = None
    provenance_residual: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if self.local_status is LocalStatus.SATURATED and self.pending:
            raise ValueError("a saturated branch cannot retain local work")


@dataclass(frozen=True)
class Forest:
    branches: tuple[Branch, ...]

    def __post_init__(self) -> None:
        if not self.branches:
            raise ValueError("a search forest must retain at least one leaf")


@dataclass(frozen=True)
class UnknownEvidence:
    budget_limit: int
    budget_remaining: int
    frontier: tuple[Branch, ...]
    scheduler: str
    rule_version: str
    continuation: str

    def __post_init__(self) -> None:
        if self.budget_limit < 0 or self.budget_remaining != 0 or not self.frontier:
            raise ValueError("unknown evidence requires an exhausted nonempty frontier")
        forest = Forest(self.frontier)
        if all_closed(forest) or exists_open(forest):
            raise ValueError("unknown evidence cannot contain a certified endpoint")


@dataclass(frozen=True)
class RunReport:
    forest: Forest
    disposition: RunDisposition
    budget_limit: int
    budget_remaining: int
    scheduler: str
    rule_version: str
    continuation: str

    def __post_init__(self) -> None:
        if not 0 <= self.budget_remaining <= self.budget_limit:
            raise ValueError("remaining budget must lie within the declared limit")
        if (
            self.disposition is RunDisposition.BUDGET_EXHAUSTED
            and self.budget_remaining != 0
        ):
            raise ValueError("budget exhaustion requires zero remaining fuel")


def _signs(branch: Branch, atom: Atom) -> set[bool]:
    return {literal.positive for literal in branch.literals if literal.atom == atom}


def checked_closed(branch: Branch) -> bool:
    certificate = branch.certificate
    return certificate is not None and _signs(branch, certificate.atom) == {
        False,
        True,
    }


def open_and_saturated(branch: Branch) -> bool:
    has_clash = any(
        _signs(branch, literal.atom) == {False, True} for literal in branch.literals
    )
    return not has_clash and branch.local_status is LocalStatus.SATURATED


def all_closed(forest: Forest) -> bool:
    return all(checked_closed(branch) for branch in forest.branches)


def exists_open(forest: Forest) -> bool:
    return any(open_and_saturated(branch) for branch in forest.branches)


def unknown_readout(report: RunReport) -> UnknownEvidence | None:
    if report.disposition is not RunDisposition.BUDGET_EXHAUSTED:
        return None
    if all_closed(report.forest) or exists_open(report.forest):
        return None
    return UnknownEvidence(
        budget_limit=report.budget_limit,
        budget_remaining=report.budget_remaining,
        frontier=report.forest.branches,
        scheduler=report.scheduler,
        rule_version=report.rule_version,
        continuation=report.continuation,
    )


def evaluate_formula(formula: object, valuation: Mapping[str, bool]) -> bool:
    if not isinstance(formula, Atom):
        raise TypeError("runtime statuses are not object-language formulas")
    return valuation[formula.name]


def test_exact_two_state_rules_are_reverse_duals() -> None:
    assert EDGES == frozenset({(P1, P0), (L0, L1)})
    for source in CARRIER:
        for target in CARRIER:
            assert ((source, target) in EDGES) is (
                (star(target), star(source)) in EDGES
            )


def test_star_is_an_involution_on_the_complete_typed_carrier() -> None:
    assert {star(configuration) for configuration in CARRIER} == set(CARRIER)
    for configuration in CARRIER:
        assert star(star(configuration)) == configuration


def test_proof_normal_form_dual_is_the_learning_generator() -> None:
    for proof in (P0, P1):
        assert star(forward_normal_form(proof)) == learning_generator(star(proof))


def test_old_forward_nf_nf_equation_has_a_finite_counterexample() -> None:
    assert forward_normal_form(star(P1)) == L1
    assert star(forward_normal_form(P1)) == L0
    assert forward_normal_form(star(P1)) != star(forward_normal_form(P1))


def test_forest_distinguishes_all_closed_from_exists_open() -> None:
    p, q = Atom("p"), Atom("q")
    closed_p = Branch(
        (SignedAtom(p, True), SignedAtom(p, False)),
        LocalStatus.SATURATED,
        certificate=ClosureCertificate(p),
        provenance_residual=("source:p",),
    )
    closed_q = Branch(
        (SignedAtom(q, False), SignedAtom(q, True)),
        LocalStatus.SATURATED,
        certificate=ClosureCertificate(q),
    )
    open_branch = Branch(
        (SignedAtom(p, True), SignedAtom(q, False)),
        LocalStatus.SATURATED,
    )
    proof_forest = Forest((closed_p, closed_q))
    countermodel_forest = Forest((closed_p, open_branch))
    assert all_closed(proof_forest) and not exists_open(proof_forest)
    assert proof_forest.branches[0].provenance_residual == ("source:p",)
    assert not all_closed(countermodel_forest)
    assert exists_open(countermodel_forest)
    with pytest.raises(ValueError, match="at least one leaf"):
        Forest(())


def test_budget_exhaustion_preserves_pending_work() -> None:
    p = Atom("p")
    pending = WorkItem("split-disjunction", p)
    branch = Branch(
        (SignedAtom(p, True),),
        LocalStatus.REDUCIBLE,
        pending=(pending,),
    )
    report = RunReport(
        Forest((branch,)),
        RunDisposition.BUDGET_EXHAUSTED,
        0,
        0,
        scheduler="fifo.v0",
        rule_version="reverse-dual.v0",
        continuation="resume:branch-0",
    )
    unknown = unknown_readout(report)
    assert report.forest.branches[0].pending == (pending,)
    assert not all_closed(report.forest)
    assert not exists_open(report.forest)
    assert unknown == UnknownEvidence(
        budget_limit=0,
        budget_remaining=0,
        frontier=(branch,),
        scheduler="fifo.v0",
        rule_version="reverse-dual.v0",
        continuation="resume:branch-0",
    )


def test_unknown_is_not_an_object_language_truth_value() -> None:
    assert evaluate_formula(Atom("p"), {"p": True}) is True
    p = Atom("p")
    branch = Branch(
        (SignedAtom(p, True),),
        LocalStatus.REDUCIBLE,
        pending=(WorkItem("resume", p),),
    )
    unknown = UnknownEvidence(
        0, 0, (branch,), "fifo.v0", "reverse-dual.v0", "resume:branch-0"
    )
    with pytest.raises(TypeError, match="not object-language"):
        evaluate_formula(unknown, {})

    closed = Branch(
        (SignedAtom(p, True), SignedAtom(p, False)),
        LocalStatus.SATURATED,
        certificate=ClosureCertificate(p),
    )
    with pytest.raises(ValueError, match="certified endpoint"):
        UnknownEvidence(0, 0, (closed,), "fifo.v0", "v0", "resume")

    open_branch = Branch((SignedAtom(p, True),), LocalStatus.SATURATED)
    with pytest.raises(ValueError, match="certified endpoint"):
        UnknownEvidence(0, 0, (open_branch,), "fifo.v0", "v0", "resume")
