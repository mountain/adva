from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias

import pytest


class DomainRole(Enum):
    CONSTRUCTION = "K"
    SPACE = "X"
    TIME = "t"


@dataclass(frozen=True)
class HistoryName:
    display: str


@dataclass(frozen=True)
class Use:
    source: str
    occurrence: str


@dataclass(frozen=True)
class Atom:
    name: str


@dataclass(frozen=True)
class Add:
    left: AMTerm
    right: AMTerm


@dataclass(frozen=True)
class Mul:
    left: AMTerm
    right: AMTerm


@dataclass(frozen=True)
class Neg:
    value: AMTerm


AMTerm: TypeAlias = Atom | Use | Add | Mul | Neg


@dataclass(frozen=True)
class ConstraintCell:
    name: str
    left: AMTerm
    right: AMTerm


@dataclass(frozen=True)
class HistoryDerivative:
    name: str
    history: HistoryName
    input_source: str
    output_source: str
    value_type: str


@dataclass(frozen=True)
class EnergyTag:
    name: str
    source: str
    occurrence: str
    residual: tuple[str, ...]


@dataclass(frozen=True)
class Perturbation:
    name: str
    energy_name: str
    axis_name: str
    history: HistoryName
    residual: tuple[str, ...]


@dataclass(frozen=True)
class AxisLine:
    name: str
    incidence: str
    aspects: tuple[str, str]
    dual_atom: str


@dataclass(frozen=True)
class Circle:
    name: str
    cyclic_word: tuple[str, ...]


@dataclass(frozen=True)
class Pierce:
    name: str
    axis_name: str
    cycle_name: str


@dataclass(frozen=True)
class ThroughSegment:
    left: DomainRole
    right: DomainRole
    middle: DomainRole


@dataclass(frozen=True)
class OmegaWord:
    cycle_name: str
    segments: tuple[ThroughSegment, ...]
    connectors: tuple[str, ...]
    returned_frontier: bool


@dataclass(frozen=True)
class ForgetRecord:
    name: str
    cycle_name: str
    fine: tuple[str, ...]
    seen: tuple[str, ...]
    fibre: tuple[str, ...]
    residual: tuple[str, ...]


@dataclass(frozen=True)
class ClosureWitness:
    name: str
    cycle_name: str
    incidence_ledger: tuple[str, ...]
    connector_ledger: tuple[str, ...]


@dataclass(frozen=True)
class PendulumSyntax:
    axis: AxisLine
    circle: Circle
    pierce: Pierce
    history: HistoryName
    derivative: HistoryDerivative
    energy: EnergyTag
    perturbation: Perturbation
    characteristic: ConstraintCell
    omega_word: OmegaWord
    forgetting: ForgetRecord
    closure: ClosureWitness
    residual: tuple[str, ...]


def _uses(term: AMTerm) -> tuple[Use, ...]:
    if isinstance(term, Use):
        return (term,)
    if isinstance(term, Atom):
        return ()
    if isinstance(term, Neg):
        return _uses(term.value)
    return _uses(term.left) + _uses(term.right)


def _pendulum_constraint() -> ConstraintCell:
    left = Mul(Use("Y", "y-1"), Use("Y", "y-2"))
    right = Mul(
        Atom("2"),
        Mul(
            Add(Use("E", "e-1"), Neg(Use("U", "u-1"))),
            Add(
                Atom("1"),
                Neg(Mul(Use("U", "u-2"), Use("U", "u-3"))),
            ),
        ),
    )
    return ConstraintCell("pendulum-characteristic", left, right)


def _omega_word(cycle_name: str, returned_frontier: bool = True) -> OmegaWord:
    return OmegaWord(
        cycle_name,
        (
            ThroughSegment(
                DomainRole.CONSTRUCTION,
                DomainRole.SPACE,
                DomainRole.TIME,
            ),
            ThroughSegment(
                DomainRole.SPACE,
                DomainRole.TIME,
                DomainRole.CONSTRUCTION,
            ),
            ThroughSegment(
                DomainRole.TIME,
                DomainRole.CONSTRUCTION,
                DomainRole.SPACE,
            ),
        ),
        ("k-X", "k-t", "k-K"),
        returned_frontier,
    )


def _fixture() -> PendulumSyntax:
    cycle_name = "gamma"
    history = HistoryName("zeta")
    characteristic = _pendulum_constraint()
    return PendulumSyntax(
        axis=AxisLine(
            "axis",
            "identity-i",
            ("empty", "universal"),
            "dual-empty-universal",
        ),
        circle=Circle(cycle_name, ("i-KX", "i-Xt", "i-tK")),
        pierce=Pierce("z", "axis", cycle_name),
        history=history,
        derivative=HistoryDerivative("delta", history, "U", "Y", "A"),
        energy=EnergyTag("epsilon", "E", "e-1", ("energy-provenance",)),
        perturbation=Perturbation(
            "kick",
            "epsilon",
            "axis",
            history,
            ("uninterpreted-perturbation",),
        ),
        characteristic=characteristic,
        omega_word=_omega_word(cycle_name),
        forgetting=ForgetRecord(
            "forget-observer",
            cycle_name,
            ("fine-0", "fine-1"),
            ("seen",),
            ("fine-0", "fine-1"),
            ("forgotten-distinctions",),
        ),
        closure=ClosureWitness(
            "close-gamma",
            cycle_name,
            ("i-KX", "i-Xt", "i-tK"),
            ("k-X", "k-t", "k-K"),
        ),
        residual=("unproved-coordination",),
    )


def _validate_forgetting(record: ForgetRecord) -> None:
    if record.fine != record.seen and (not record.fibre or not record.residual):
        raise ValueError("forgetting requires a fibre and residual")


def _validate_package(form: PendulumSyntax) -> None:
    cycle_names = {
        form.circle.name,
        form.pierce.cycle_name,
        form.omega_word.cycle_name,
        form.forgetting.cycle_name,
        form.closure.cycle_name,
    }
    if len(cycle_names) != 1:
        raise ValueError("all cycle records must cite one name")
    if form.axis.name != form.pierce.axis_name:
        raise ValueError("the piercing record cites a different axis")
    if form.axis.aspects != ("empty", "universal") or not form.axis.dual_atom:
        raise ValueError("the axis needs an explicit empty/universal dual atom")
    if form.derivative.history != form.history:
        raise ValueError("the derivative cites a different history")
    if (
        form.perturbation.energy_name != form.energy.name
        or form.perturbation.axis_name != form.axis.name
        or form.perturbation.history != form.history
        or not form.perturbation.residual
    ):
        raise ValueError("the perturbation must join energy, axis, and history")

    uses = _uses(form.characteristic.left) + _uses(form.characteristic.right)
    if len({use.occurrence for use in uses}) != len(uses):
        raise ValueError("all A/M occurrences must be fresh")
    census = Counter(use.source for use in uses)
    if census != Counter({"Y": 2, "U": 3, "E": 1}):
        raise ValueError("the pendulum occurrence census is malformed")
    if {form.derivative.input_source, form.derivative.output_source} != {"U", "Y"}:
        raise ValueError("the derivative must cite the U/Y source pair")
    if form.energy.source != "E" or form.energy.occurrence not in {
        use.occurrence for use in uses if use.source == "E"
    }:
        raise ValueError("the energy tag must cite the characteristic E use")

    expected_segments = (
        (DomainRole.CONSTRUCTION, DomainRole.SPACE, DomainRole.TIME),
        (DomainRole.SPACE, DomainRole.TIME, DomainRole.CONSTRUCTION),
        (DomainRole.TIME, DomainRole.CONSTRUCTION, DomainRole.SPACE),
    )
    actual_segments = tuple(
        (segment.left, segment.right, segment.middle)
        for segment in form.omega_word.segments
    )
    if actual_segments != expected_segments or len(form.omega_word.connectors) != 3:
        raise ValueError("the Omega word must be the ordered three-domain cycle")
    if not form.closure.incidence_ledger or not form.closure.connector_ledger:
        raise ValueError("closure needs incidence and connector ledgers")
    _validate_forgetting(form.forgetting)
    if not form.residual:
        raise ValueError("the package must retain unresolved coordination")


def _route_adjacent(uses: tuple[Use, ...], gap: int) -> tuple[Use, ...]:
    left = gap - 1
    right = gap
    if left < 0 or right >= len(uses):
        raise ValueError("the gap must select adjacent occurrences")
    result = list(uses)
    result[left], result[right] = result[right], result[left]
    return tuple(result)


def test_history_name_is_not_the_domain_time_role() -> None:
    history = HistoryName("t")

    assert history.display == DomainRole.TIME.value
    assert history != DomainRole.TIME


def test_derivative_and_characteristic_share_u_y_sources_only() -> None:
    form = _fixture()
    sources = {use.source for use in _uses(form.characteristic.left)} | {
        use.source for use in _uses(form.characteristic.right)
    }

    assert {form.derivative.input_source, form.derivative.output_source} == {"U", "Y"}
    assert {form.derivative.input_source, form.derivative.output_source} < sources


def test_pendulum_am_tree_has_exact_source_and_occurrence_census() -> None:
    characteristic = _pendulum_constraint()
    uses = _uses(characteristic.left) + _uses(characteristic.right)

    assert Counter(use.source for use in uses) == Counter({"Y": 2, "U": 3, "E": 1})
    assert len(uses) == 6
    assert len({use.occurrence for use in uses}) == 6


def test_routing_preserves_occurrences_and_cannot_manufacture_copies() -> None:
    supplied = (Use("Y", "y-1"), Use("U", "u-1"), Use("E", "e-1"))
    routed = _route_adjacent(_route_adjacent(supplied, 1), 2)

    assert Counter(routed) == Counter(supplied)
    assert Counter(use.source for use in routed) == Counter({"Y": 1, "U": 1, "E": 1})
    assert Counter(use.source for use in routed) != Counter({"Y": 2, "U": 3, "E": 1})


def test_axis_duality_piercing_and_perturbation_share_literal_names() -> None:
    form = _fixture()

    _validate_package(form)
    assert form.axis.aspects == ("empty", "universal")
    assert form.axis.dual_atom == "dual-empty-universal"
    assert form.axis.name == form.pierce.axis_name
    assert form.perturbation.axis_name == form.axis.name
    assert form.perturbation.energy_name == form.energy.name
    assert form.perturbation.history == form.history


def test_all_cycle_records_share_one_literal_name() -> None:
    form = _fixture()

    assert {
        form.circle.name,
        form.pierce.cycle_name,
        form.omega_word.cycle_name,
        form.forgetting.cycle_name,
        form.closure.cycle_name,
    } == {"gamma"}


def test_omega_word_has_three_ordered_through_segments_and_connectors() -> None:
    word = _omega_word("gamma")

    assert tuple((segment.left, segment.right) for segment in word.segments) == (
        (DomainRole.CONSTRUCTION, DomainRole.SPACE),
        (DomainRole.SPACE, DomainRole.TIME),
        (DomainRole.TIME, DomainRole.CONSTRUCTION),
    )
    assert tuple(segment.middle for segment in word.segments) == (
        DomainRole.TIME,
        DomainRole.CONSTRUCTION,
        DomainRole.SPACE,
    )
    assert word.connectors == ("k-X", "k-t", "k-K")


def test_endpoint_return_does_not_construct_a_closure_witness() -> None:
    word = _omega_word("gamma", returned_frontier=True)
    characteristic = _pendulum_constraint()

    assert word.returned_frontier
    assert not isinstance(word, ClosureWitness)
    assert not isinstance(characteristic, ClosureWitness)


def test_forgetting_without_fibre_or_residual_is_rejected() -> None:
    with pytest.raises(ValueError, match="fibre and residual"):
        _validate_forgetting(
            ForgetRecord("bad", "gamma", ("fine",), ("seen",), (), ("lost",))
        )
    with pytest.raises(ValueError, match="fibre and residual"):
        _validate_forgetting(
            ForgetRecord("bad", "gamma", ("fine",), ("seen",), ("fine",), ())
        )


def test_complete_finite_package_forms_without_equation_evaluation() -> None:
    form = _fixture()

    _validate_package(form)
    assert form.characteristic.left != form.characteristic.right
    assert form.residual == ("unproved-coordination",)
