"""Pure-Python research oracle; it creates no Adva semantic authority."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from itertools import permutations, product

import pytest


class Domain(Enum):
    CONSTRUCTIVE = "K"
    SPATIAL = "X"
    TEMPORAL = "t"


DOMAINS = (Domain.CONSTRUCTIVE, Domain.SPATIAL, Domain.TEMPORAL)
Permutation = tuple[int, ...]
Section = tuple[int, int, int]


class NotRepresentable(ValueError):
    pass


def opposite_context(domain: Domain) -> frozenset[Domain]:
    return frozenset(set(DOMAINS) - {domain})


def overlap_type(left: Domain, right: Domain) -> Domain:
    if left is right:
        raise NotRepresentable("an overlap needs two distinct charts")
    shared = opposite_context(left) & opposite_context(right)
    if len(shared) != 1:
        raise NotRepresentable("V0 requires one typed overlap")
    return next(iter(shared))


def identity(size: int) -> Permutation:
    if size < 1:
        raise NotRepresentable("a marked fibre must be nonempty")
    return tuple(range(size))


def rotation(size: int, steps: int) -> Permutation:
    return tuple((index + steps) % size for index in range(size))


def transposition(size: int, left: int, right: int) -> Permutation:
    result = list(identity(size))
    result[left], result[right] = result[right], result[left]
    return tuple(result)


def _validate_permutation(permutation: Permutation) -> None:
    if not permutation or set(permutation) != set(range(len(permutation))):
        raise NotRepresentable("an overlap comparison must be a finite bijection")


def compose(after: Permutation, before: Permutation) -> Permutation:
    _validate_permutation(after)
    _validate_permutation(before)
    if len(after) != len(before):
        raise NotRepresentable("permutations require one fibre size")
    return tuple(after[before[index]] for index in range(len(before)))


def inverse(permutation: Permutation) -> Permutation:
    _validate_permutation(permutation)
    result = [0] * len(permutation)
    for source, target in enumerate(permutation):
        result[target] = source
    return tuple(result)


@dataclass(frozen=True, slots=True)
class Transition:
    source: Domain
    target: Domain
    overlap: Domain
    image: Permutation
    observer_version: str
    fibre_version: str

    def __post_init__(self) -> None:
        if self.overlap is not overlap_type(self.source, self.target):
            raise NotRepresentable("transition carries the wrong overlap type")
        _validate_permutation(self.image)
        if not self.observer_version or not self.fibre_version:
            raise NotRepresentable("transition versions must be explicit")

    def apply(self, phase: int) -> int:
        return self.image[phase]

    def reversed(self) -> Transition:
        return Transition(
            source=self.target,
            target=self.source,
            overlap=self.overlap,
            image=inverse(self.image),
            observer_version=self.observer_version,
            fibre_version=self.fibre_version,
        )


class GluingStatus(Enum):
    FLAT = "flat-all-sections"
    RESIDUAL_FIXED = "residual-holonomy-with-fixed-sections"
    OBSTRUCTED = "fixed-point-free-holonomy-obstruction"


@dataclass(frozen=True, slots=True)
class GluingReport:
    status: GluingStatus
    holonomy: Permutation
    fixed_phases: tuple[int, ...]
    sections: tuple[Section, ...]


@dataclass(frozen=True, slots=True)
class CircularLocalSystem:
    cycle: tuple[Domain, Domain, Domain]
    transitions: tuple[Transition, Transition, Transition]

    def __post_init__(self) -> None:
        if len(set(self.cycle)) != 3 or set(self.cycle) != set(DOMAINS):
            raise NotRepresentable("the chart cycle must contain each domain once")
        expected_edges = tuple(zip(self.cycle, self.cycle[1:] + self.cycle[:1]))
        actual_edges = tuple(
            (transition.source, transition.target) for transition in self.transitions
        )
        if actual_edges != expected_edges:
            raise NotRepresentable("transitions must follow the declared chart cycle")

        sizes = {len(transition.image) for transition in self.transitions}
        observer_versions = {
            transition.observer_version for transition in self.transitions
        }
        fibre_versions = {transition.fibre_version for transition in self.transitions}
        if len(sizes) != 1:
            raise NotRepresentable("all chart fibres need one finite size")
        if len(observer_versions) != 1 or len(fibre_versions) != 1:
            raise NotRepresentable("all transitions need matching versions")

    @property
    def fibre_size(self) -> int:
        return len(self.transitions[0].image)

    @property
    def holonomy(self) -> Permutation:
        result = identity(self.fibre_size)
        for transition in self.transitions:
            result = compose(transition.image, result)
        return result

    @property
    def fixed_phases(self) -> tuple[int, ...]:
        return tuple(
            phase for phase, image in enumerate(self.holonomy) if phase == image
        )

    @property
    def sections(self) -> tuple[Section, ...]:
        result: list[Section] = []
        for start in range(self.fibre_size):
            chart_values = {self.cycle[0]: start}
            current = start
            for transition in self.transitions[:-1]:
                current = transition.apply(current)
                chart_values[transition.target] = current
            if self.transitions[-1].apply(current) == start:
                result.append(tuple(chart_values[domain] for domain in DOMAINS))
        return tuple(result)

    @property
    def report(self) -> GluingReport:
        if self.holonomy == identity(self.fibre_size):
            status = GluingStatus.FLAT
        elif self.fixed_phases:
            status = GluingStatus.RESIDUAL_FIXED
        else:
            status = GluingStatus.OBSTRUCTED
        return GluingReport(status, self.holonomy, self.fixed_phases, self.sections)

    def rebase(self, base: Domain) -> CircularLocalSystem:
        offset = self.cycle.index(base)
        cycle = self.cycle[offset:] + self.cycle[:offset]
        transitions = self.transitions[offset:] + self.transitions[:offset]
        return CircularLocalSystem(cycle, transitions)

    def reverse_orientation(self) -> CircularLocalSystem:
        first, second, third = self.transitions
        cycle = (self.cycle[0], self.cycle[2], self.cycle[1])
        return CircularLocalSystem(
            cycle,
            (third.reversed(), second.reversed(), first.reversed()),
        )

    def regauge(self, gauges: dict[Domain, Permutation]) -> CircularLocalSystem:
        if set(gauges) != set(DOMAINS):
            raise NotRepresentable("a gauge change needs all three charts")
        if any(len(gauge) != self.fibre_size for gauge in gauges.values()):
            raise NotRepresentable("gauge maps need the local fibre size")
        for gauge in gauges.values():
            _validate_permutation(gauge)

        transitions = tuple(
            Transition(
                source=transition.source,
                target=transition.target,
                overlap=transition.overlap,
                image=compose(
                    gauges[transition.target],
                    compose(transition.image, inverse(gauges[transition.source])),
                ),
                observer_version=transition.observer_version,
                fibre_version=transition.fibre_version,
            )
            for transition in self.transitions
        )
        return CircularLocalSystem(self.cycle, transitions)


def make_system(
    images: tuple[Permutation, Permutation, Permutation],
    *,
    cycle: tuple[Domain, Domain, Domain] = DOMAINS,
    observer_version: str = "observer.v0",
    fibre_version: str = "phase.v0",
) -> CircularLocalSystem:
    edges = tuple(zip(cycle, cycle[1:] + cycle[:1]))
    transitions = tuple(
        Transition(
            source=source,
            target=target,
            overlap=overlap_type(source, target),
            image=image,
            observer_version=observer_version,
            fibre_version=fibre_version,
        )
        for (source, target), image in zip(edges, images, strict=True)
    )
    return CircularLocalSystem(cycle, transitions)


def test_overlap_types_are_exactly_the_opposite_chart_intersections() -> None:
    expected = {
        (Domain.CONSTRUCTIVE, Domain.SPATIAL): Domain.TEMPORAL,
        (Domain.SPATIAL, Domain.TEMPORAL): Domain.CONSTRUCTIVE,
        (Domain.TEMPORAL, Domain.CONSTRUCTIVE): Domain.SPATIAL,
    }
    for edge, overlap in expected.items():
        assert overlap_type(*edge) is overlap
        assert overlap_type(*reversed(edge)) is overlap


def test_identity_holonomy_glues_every_marked_phase() -> None:
    system = make_system((rotation(5, 1), rotation(5, 2), rotation(5, 2)))
    report = system.report

    assert report.status is GluingStatus.FLAT
    assert report.holonomy == identity(5)
    assert report.fixed_phases == tuple(range(5))
    assert len(report.sections) == 5
    assert len(set(report.sections)) == 5


def test_nonidentity_holonomy_can_retain_some_global_sections() -> None:
    system = make_system((identity(4), identity(4), transposition(4, 1, 2)))
    report = system.report

    assert report.status is GluingStatus.RESIDUAL_FIXED
    assert report.holonomy != identity(4)
    assert report.fixed_phases == (0, 3)
    assert report.sections == ((0, 0, 0), (3, 3, 3))


def test_valid_pairwise_transitions_can_have_no_global_section() -> None:
    system = make_system((rotation(5, 1), rotation(5, 1), rotation(5, 1)))
    report = system.report

    assert all(
        set(transition.image) == set(range(system.fibre_size))
        for transition in system.transitions
    )
    assert report.status is GluingStatus.OBSTRUCTED
    assert report.holonomy == rotation(5, 3)
    assert report.fixed_phases == ()
    assert report.sections == ()


def test_global_sections_are_exactly_holonomy_fixed_points() -> None:
    systems = (
        make_system((rotation(5, 1), rotation(5, 2), rotation(5, 2))),
        make_system((identity(4), identity(4), transposition(4, 1, 2))),
        make_system((rotation(5, 1), rotation(5, 1), rotation(5, 1))),
    )
    for system in systems:
        section_starts = tuple(
            section[DOMAINS.index(system.cycle[0])] for section in system.sections
        )
        assert section_starts == system.fixed_phases


def test_all_three_phase_systems_have_the_exact_status_distribution() -> None:
    all_permutations = tuple(permutations(range(3)))
    counts: Counter[GluingStatus] = Counter()

    for images in product(all_permutations, repeat=3):
        system = make_system(images)
        section_starts = tuple(section[0] for section in system.sections)
        assert section_starts == system.fixed_phases
        counts[system.report.status] += 1

    assert counts == Counter(
        {
            GluingStatus.FLAT: 36,
            GluingStatus.RESIDUAL_FIXED: 108,
            GluingStatus.OBSTRUCTED: 72,
        }
    )


def test_local_gauge_changes_conjugate_holonomy_and_preserve_classification() -> None:
    system = make_system(
        (
            rotation(4, 1),
            transposition(4, 0, 1),
            transposition(4, 2, 3),
        )
    )
    gauges = {
        Domain.CONSTRUCTIVE: transposition(4, 0, 2),
        Domain.SPATIAL: rotation(4, 1),
        Domain.TEMPORAL: transposition(4, 1, 3),
    }
    transformed = system.regauge(gauges)
    base_gauge = gauges[system.cycle[0]]
    expected = compose(base_gauge, compose(system.holonomy, inverse(base_gauge)))

    assert transformed.holonomy == expected
    assert transformed.report.status is system.report.status
    assert len(transformed.fixed_phases) == len(system.fixed_phases)
    assert len(transformed.sections) == len(system.sections)


def test_moving_the_cut_conjugates_holonomy() -> None:
    system = make_system(
        (
            rotation(4, 1),
            transposition(4, 0, 1),
            rotation(4, 2),
        )
    )
    rebased = system.rebase(Domain.SPATIAL)
    transport = system.transitions[0].image
    expected = compose(transport, compose(system.holonomy, inverse(transport)))

    assert rebased.holonomy == expected
    assert len(rebased.fixed_phases) == len(system.fixed_phases)
    assert rebased.report.status is system.report.status


def test_orientation_reversal_inverts_holonomy_and_preserves_sections() -> None:
    system = make_system(
        (
            rotation(5, 1),
            transposition(5, 0, 1),
            rotation(5, 2),
        )
    )
    reversed_system = system.reverse_orientation()

    assert reversed_system.holonomy == inverse(system.holonomy)
    assert reversed_system.fixed_phases == system.fixed_phases
    assert len(reversed_system.sections) == len(system.sections)
    assert reversed_system.reverse_orientation() == system


def test_malformed_transport_is_not_representable() -> None:
    with pytest.raises(NotRepresentable, match="bijection"):
        Transition(
            Domain.CONSTRUCTIVE,
            Domain.SPATIAL,
            Domain.TEMPORAL,
            (0, 0, 2),
            "observer.v0",
            "phase.v0",
        )

    with pytest.raises(NotRepresentable, match="wrong overlap"):
        Transition(
            Domain.CONSTRUCTIVE,
            Domain.SPATIAL,
            Domain.CONSTRUCTIVE,
            identity(3),
            "observer.v0",
            "phase.v0",
        )

    valid = make_system((identity(3), identity(3), identity(3)))
    mismatched_version = Transition(
        Domain.TEMPORAL,
        Domain.CONSTRUCTIVE,
        Domain.SPATIAL,
        identity(3),
        "observer.v1",
        "phase.v0",
    )
    with pytest.raises(NotRepresentable, match="matching versions"):
        CircularLocalSystem(
            DOMAINS,
            (valid.transitions[0], valid.transitions[1], mismatched_version),
        )

    with pytest.raises(NotRepresentable, match="declared chart cycle"):
        CircularLocalSystem(
            DOMAINS,
            (valid.transitions[1], valid.transitions[0], valid.transitions[2]),
        )
