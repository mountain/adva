from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias, get_args


class Status(Enum):
    HARD_KERNEL = "H"
    CALIBRATION = "C"
    GEOMETRIC_CANDIDATE = "G"


@dataclass(frozen=True)
class Factor:
    name: str
    status: Status


INVENTORY = (
    Factor("typed-names", Status.HARD_KERNEL),
    Factor("domain-roles", Status.HARD_KERNEL),
    Factor("derivative-index-sum", Status.HARD_KERNEL),
    Factor("orientation-alphabets", Status.HARD_KERNEL),
    Factor("type-and-frontier-grammar", Status.HARD_KERNEL),
    Factor("three-shell-boundary", Status.HARD_KERNEL),
    Factor("through-cell", Status.HARD_KERNEL),
    Factor("thread-alphabet", Status.HARD_KERNEL),
    Factor("strand-and-incidence-diagram", Status.HARD_KERNEL),
    Factor("pure-add-mul-grammar", Status.HARD_KERNEL),
    Factor("formation-judgements", Status.HARD_KERNEL),
    Factor("interpreter-declarations", Status.HARD_KERNEL),
    Factor("ordered-through-separation", Status.CALIBRATION),
    Factor("signed-crossing-separation", Status.CALIBRATION),
    Factor("formal-braid-inverse", Status.CALIBRATION),
    Factor("mixed-word-block-preservation", Status.CALIBRATION),
    Factor("explicit-occurrence-production", Status.CALIBRATION),
    Factor("ordered-hole-binding", Status.CALIBRATION),
    Factor("retained-residual", Status.CALIBRATION),
    Factor("pend-form-profile", Status.GEOMETRIC_CANDIDATE),
    Factor("axis-circle-piercing", Status.GEOMETRIC_CANDIDATE),
    Factor("energy-history-perturbation", Status.GEOMETRIC_CANDIDATE),
    Factor("six-use-characteristic", Status.GEOMETRIC_CANDIDATE),
    Factor("omega-cycle-coupling", Status.GEOMETRIC_CANDIDATE),
    Factor("forgetting-closure-coupling", Status.GEOMETRIC_CANDIDATE),
)


class DomainRole(Enum):
    CONSTRUCTION = "K"
    SPACE = "X"
    TIME = "t"


@dataclass(frozen=True)
class HistoryName:
    display: str


@dataclass(frozen=True)
class RoleDerivativeIndex:
    role: DomainRole


@dataclass(frozen=True)
class HistoryDerivativeIndex:
    history: HistoryName


DerivativeIndex: TypeAlias = RoleDerivativeIndex | HistoryDerivativeIndex


@dataclass(frozen=True)
class SourceName:
    display: str


@dataclass(frozen=True)
class OccurrenceName:
    display: str


@dataclass(frozen=True)
class HoleName:
    display: str


@dataclass(frozen=True)
class IncidenceName:
    display: str


@dataclass(frozen=True)
class Atom:
    name: str


@dataclass(frozen=True)
class Use:
    source: SourceName
    occurrence: OccurrenceName


@dataclass(frozen=True)
class Add:
    left: AMTerm
    right: AMTerm


@dataclass(frozen=True)
class Mul:
    left: AMTerm
    right: AMTerm


AMTerm: TypeAlias = Atom | Use | Add | Mul


@dataclass(frozen=True)
class Hole:
    name: HoleName
    value_type: str


@dataclass(frozen=True)
class Binding:
    occurrence: OccurrenceName
    hole: HoleName


@dataclass(frozen=True)
class OccurrenceProduction:
    source: SourceName
    occurrences: tuple[OccurrenceName, ...]


def _pendulum_tree() -> tuple[AMTerm, AMTerm]:
    y1 = Use(SourceName("Y"), OccurrenceName("o-Y1"))
    y2 = Use(SourceName("Y"), OccurrenceName("o-Y2"))
    e1 = Use(SourceName("E"), OccurrenceName("o-E1"))
    u1 = Use(SourceName("U"), OccurrenceName("o-U1"))
    u2 = Use(SourceName("U"), OccurrenceName("o-U2"))
    u3 = Use(SourceName("U"), OccurrenceName("o-U3"))
    negative_unit = Atom("neg-unit-A")
    return (
        Mul(y1, y2),
        Mul(
            Atom("2"),
            Mul(
                Add(e1, Mul(negative_unit, u1)),
                Add(Atom("1"), Mul(negative_unit, Mul(u2, u3))),
            ),
        ),
    )


def _uses(term: AMTerm) -> tuple[Use, ...]:
    if isinstance(term, Use):
        return (term,)
    if isinstance(term, Atom):
        return ()
    return _uses(term.left) + _uses(term.right)


def test_status_inventory_is_finite_unique_and_partitioned() -> None:
    names = tuple(factor.name for factor in INVENTORY)
    by_status = {
        status: {factor.name for factor in INVENTORY if factor.status is status}
        for status in Status
    }

    assert len(names) == len(set(names))
    assert all(by_status.values())
    assert set().union(*by_status.values()) == set(names)
    for status, factors in by_status.items():
        assert factors.isdisjoint(
            set().union(
                *(other for other_status, other in by_status.items() if other_status is not status)
            )
        )


def test_derivative_index_variants_are_disjoint_at_same_display() -> None:
    role = RoleDerivativeIndex(DomainRole.TIME)
    history = HistoryDerivativeIndex(HistoryName("t"))

    assert role.role.value == history.history.display
    assert role != history
    assert set(get_args(DerivativeIndex)) == {
        RoleDerivativeIndex,
        HistoryDerivativeIndex,
    }


def test_am_term_algebra_is_pure_add_mul_without_neg_constructor() -> None:
    constructors = {constructor.__name__ for constructor in get_args(AMTerm)}

    assert constructors == {"Atom", "Use", "Add", "Mul"}
    assert "Neg" not in constructors


def test_source_occurrence_hole_and_incidence_names_are_separate() -> None:
    source = SourceName("n")
    occurrence = OccurrenceName("n")
    hole = HoleName("n")
    incidence = IncidenceName("n")

    assert len({type(source), type(occurrence), type(hole), type(incidence)}) == 4
    assert source != occurrence != hole != incidence


def test_six_source_uses_bind_bijectively_to_six_holes() -> None:
    left, right = _pendulum_tree()
    uses = _uses(left) + _uses(right)
    holes = tuple(Hole(HoleName(f"h-{index}"), "A") for index in range(1, 7))
    binding = tuple(
        Binding(use.occurrence, hole.name)
        for use, hole in zip(uses, holes, strict=True)
    )

    assert len(uses) == len(holes) == len(binding) == 6
    assert len({use.occurrence for use in uses}) == 6
    assert len({item.hole for item in binding}) == 6
    assert tuple(item.occurrence for item in binding) == tuple(
        use.occurrence for use in uses
    )
    assert Counter(use.source.display for use in uses) == Counter(
        {"Y": 2, "U": 3, "E": 1}
    )


def test_occurrence_production_ledger_precedes_routing() -> None:
    productions = (
        OccurrenceProduction(
            SourceName("Y"), (OccurrenceName("o-Y1"), OccurrenceName("o-Y2"))
        ),
        OccurrenceProduction(SourceName("E"), (OccurrenceName("o-E1"),)),
        OccurrenceProduction(
            SourceName("U"),
            (
                OccurrenceName("o-U1"),
                OccurrenceName("o-U2"),
                OccurrenceName("o-U3"),
            ),
        ),
    )
    produced = tuple(
        occurrence
        for production in productions
        for occurrence in production.occurrences
    )
    routed = produced[1:3] + produced[:1] + produced[3:]

    assert Counter(routed) == Counter(produced)
    assert len(routed) == 6


def test_pend_form_is_candidate_profile_not_global_kernel() -> None:
    pend = next(factor for factor in INVENTORY if factor.name == "pend-form-profile")

    assert pend.status is Status.GEOMETRIC_CANDIDATE
    assert pend.status is not Status.HARD_KERNEL


def test_shared_cycle_seam_remains_an_explicit_proof_obligation() -> None:
    records = {"Circle(gamma)", "circle_Omega(gamma)", "ClosureWitness(gamma)"}
    proved_coordination: frozenset[tuple[str, str]] = frozenset()

    assert len(records) == 3
    assert not proved_coordination
