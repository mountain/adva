from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations
from typing import Literal, TypeAlias


Domain: TypeAlias = Literal["K", "X", "t"]
Orientation: TypeAlias = Literal["forward", "reverse"]

DOMAINS: frozenset[Domain] = frozenset({"K", "X", "t"})
FILLER_ROLE: dict[Domain, str] = {
    "K": "construct-mediator",
    "X": "separate-placement",
    "t": "order-schedule",
}
FORWARD_PAIRS: frozenset[tuple[Domain, Domain]] = frozenset(
    {
        ("K", "X"),
        ("X", "t"),
        ("t", "K"),
    }
)


@dataclass(frozen=True)
class TriadicThread:
    label: str
    domain: Domain
    source_id: str
    occurrence_id: str
    wire_type: str


@dataclass(frozen=True)
class AperturePort:
    domain: Domain
    occurrence_id: str
    orientation: Literal["left", "right"]


@dataclass(frozen=True)
class TriadicConflictAperture:
    domain: Domain
    source_id: str
    wire_type: str
    ports: tuple[AperturePort, AperturePort]
    orientation: Orientation
    required_role: str

    def dual(self) -> TriadicConflictAperture:
        left, right = self.ports
        return TriadicConflictAperture(
            domain=self.domain,
            source_id=self.source_id,
            wire_type=self.wire_type,
            ports=(
                AperturePort(
                    domain=right.domain,
                    occurrence_id=right.occurrence_id,
                    orientation="left",
                ),
                AperturePort(
                    domain=left.domain,
                    occurrence_id=left.occurrence_id,
                    orientation="right",
                ),
            ),
            orientation=(
                "reverse" if self.orientation == "forward" else "forward"
            ),
            required_role=self.required_role,
        )


@dataclass(frozen=True)
class ThirdDomainFiller:
    label: str
    domain: Domain
    aperture: TriadicConflictAperture
    role: str
    orientation: Orientation
    projections: tuple[str, str]
    linear_source_uses: int = 1
    closure_certificate: str = ""


@dataclass(frozen=True)
class DirectPair:
    left: TriadicThread
    right: TriadicThread


@dataclass(frozen=True)
class ClosedTriadicCell:
    left: TriadicThread
    right: TriadicThread
    filler: ThirdDomainFiller


ConjunctionWitness: TypeAlias = DirectPair | ClosedTriadicCell


@dataclass(frozen=True)
class PairingResult:
    witness: ConjunctionWitness | None = None
    aperture: TriadicConflictAperture | None = None
    obstruction: str | None = None


def _remaining_domain(left: Domain, right: Domain) -> Domain | None:
    if left == right:
        return None
    remaining = DOMAINS - {left, right}
    if len(remaining) != 1:
        return None
    return next(iter(remaining))


def _open_conflict_aperture(
    left: TriadicThread,
    right: TriadicThread,
) -> TriadicConflictAperture | None:
    if left.source_id != right.source_id:
        return None
    if left.occurrence_id == right.occurrence_id:
        return None
    if left.wire_type != right.wire_type:
        return None
    domain = _remaining_domain(left.domain, right.domain)
    if domain is None:
        return None
    return TriadicConflictAperture(
        domain=domain,
        source_id=left.source_id,
        wire_type=left.wire_type,
        ports=(
            AperturePort(left.domain, left.occurrence_id, "left"),
            AperturePort(right.domain, right.occurrence_id, "right"),
        ),
        orientation=(
            "forward"
            if (left.domain, right.domain) in FORWARD_PAIRS
            else "reverse"
        ),
        required_role=FILLER_ROLE[domain],
    )


def _pair_threads(
    left: TriadicThread,
    right: TriadicThread,
    filler: ThirdDomainFiller | None = None,
) -> PairingResult:
    if left.wire_type != right.wire_type:
        return PairingResult(obstruction="wire-type-mismatch")
    if left.source_id != right.source_id:
        return PairingResult(witness=DirectPair(left, right))
    if left.occurrence_id == right.occurrence_id:
        return PairingResult(obstruction="occurrence-alias")
    if left.domain == right.domain:
        return PairingResult(obstruction="same-domain-linear-conflict")

    aperture = _open_conflict_aperture(left, right)
    if aperture is None:
        return PairingResult(obstruction="triadic-aperture-not-derivable")
    if filler is None:
        return PairingResult(aperture=aperture)
    if filler.aperture != aperture:
        return PairingResult(
            aperture=aperture,
            obstruction="filler-aperture-mismatch",
        )
    if filler.domain != aperture.domain:
        return PairingResult(
            aperture=aperture,
            obstruction="filler-domain-mismatch",
        )
    if filler.role != aperture.required_role:
        return PairingResult(
            aperture=aperture,
            obstruction="filler-role-mismatch",
        )
    if filler.orientation != aperture.orientation:
        return PairingResult(
            aperture=aperture,
            obstruction="filler-orientation-mismatch",
        )
    expected_projections = tuple(
        port.occurrence_id for port in aperture.ports
    )
    if filler.projections != expected_projections:
        return PairingResult(
            aperture=aperture,
            obstruction="filler-projection-mismatch",
        )
    if filler.linear_source_uses != 1:
        return PairingResult(
            aperture=aperture,
            obstruction="nonlinear-source-use",
        )
    if not filler.closure_certificate:
        return PairingResult(
            aperture=aperture,
            obstruction="missing-closure-certificate",
        )
    return PairingResult(
        witness=ClosedTriadicCell(left, right, filler),
    )


def _thread(
    domain: Domain,
    occurrence: str,
    *,
    source: str = "source:shared",
) -> TriadicThread:
    return TriadicThread(
        label=f"line:{domain}:{occurrence}",
        domain=domain,
        source_id=source,
        occurrence_id=occurrence,
        wire_type="Scalar",
    )


def test_each_ordered_domain_pair_opens_the_unique_oriented_hole() -> None:
    expected = {
        frozenset({"K", "X"}): "t",
        frozenset({"X", "t"}): "K",
        frozenset({"K", "t"}): "X",
    }

    for left_domain, right_domain in permutations(("K", "X", "t"), 2):
        left = _thread(left_domain, f"{left_domain}:0")
        right = _thread(right_domain, f"{right_domain}:0")
        result = _pair_threads(left, right)

        assert result.witness is None
        assert result.obstruction is None
        assert result.aperture is not None
        assert result.aperture.domain == expected[
            frozenset({left_domain, right_domain})
        ]
        assert result.aperture.required_role == FILLER_ROLE[
            result.aperture.domain
        ]
        assert result.aperture.orientation == (
            "forward"
            if (left_domain, right_domain) in FORWARD_PAIRS
            else "reverse"
        )


def test_open_aperture_is_not_yet_a_conjunction_witness() -> None:
    left = _thread("K", "K:0")
    right = _thread("X", "X:0")

    open_result = _pair_threads(left, right)

    assert open_result.aperture is not None
    assert open_result.aperture.domain == "t"
    assert open_result.witness is None
    assert open_result.obstruction is None


def test_only_a_matching_third_domain_filler_closes_the_cell() -> None:
    left = _thread("K", "K:0")
    right = _thread("X", "X:0")
    aperture = _pair_threads(left, right).aperture
    assert aperture is not None

    valid = ThirdDomainFiller(
        label="schedule:K-before-X",
        domain="t",
        aperture=aperture,
        role="order-schedule",
        orientation="forward",
        projections=("K:0", "X:0"),
        closure_certificate="cell:K-X-t",
    )
    wrong_domain = ThirdDomainFiller(
        label="wrong-domain",
        domain="K",
        aperture=aperture,
        role="order-schedule",
        orientation="forward",
        projections=("K:0", "X:0"),
        closure_certificate="cell:wrong-domain",
    )
    wrong_role = ThirdDomainFiller(
        label="wrong-role",
        domain="t",
        aperture=aperture,
        role="construct-mediator",
        orientation="forward",
        projections=("K:0", "X:0"),
        closure_certificate="cell:wrong-role",
    )

    closed = _pair_threads(left, right, valid)
    assert isinstance(closed.witness, ClosedTriadicCell)
    assert closed.aperture is None
    assert closed.obstruction is None
    assert _pair_threads(left, right, wrong_domain).obstruction == (
        "filler-domain-mismatch"
    )
    assert _pair_threads(left, right, wrong_role).obstruction == (
        "filler-role-mismatch"
    )


def test_filler_must_be_an_oriented_linear_common_lift() -> None:
    left = _thread("X", "X:0")
    right = _thread("t", "t:0")
    aperture = _pair_threads(left, right).aperture
    assert aperture is not None

    wrong_orientation = ThirdDomainFiller(
        label="wrong-orientation",
        domain="K",
        aperture=aperture,
        role="construct-mediator",
        orientation="reverse",
        projections=("X:0", "t:0"),
        closure_certificate="cell:wrong-orientation",
    )
    wrong_projection = ThirdDomainFiller(
        label="wrong-projection",
        domain="K",
        aperture=aperture,
        role="construct-mediator",
        orientation="forward",
        projections=("X:0", "other"),
        closure_certificate="cell:wrong-projection",
    )
    nonlinear = ThirdDomainFiller(
        label="implicit-copy",
        domain="K",
        aperture=aperture,
        role="construct-mediator",
        orientation="forward",
        projections=("X:0", "t:0"),
        linear_source_uses=2,
        closure_certificate="cell:implicit-copy",
    )
    missing_certificate = ThirdDomainFiller(
        label="bare-third-color",
        domain="K",
        aperture=aperture,
        role="construct-mediator",
        orientation="forward",
        projections=("X:0", "t:0"),
    )

    assert _pair_threads(left, right, wrong_orientation).obstruction == (
        "filler-orientation-mismatch"
    )
    assert _pair_threads(left, right, wrong_projection).obstruction == (
        "filler-projection-mismatch"
    )
    assert _pair_threads(left, right, nonlinear).obstruction == (
        "nonlinear-source-use"
    )
    assert _pair_threads(left, right, missing_certificate).obstruction == (
        "missing-closure-certificate"
    )


def test_direct_pair_and_nontriadic_conflicts_remain_distinct() -> None:
    independent = _pair_threads(
        _thread("K", "K:0", source="source:left"),
        _thread("X", "X:0", source="source:right"),
    )
    same_domain = _pair_threads(
        _thread("K", "K:0"),
        _thread("K", "K:1"),
    )
    same_domain_independent = _pair_threads(
        _thread("K", "K:0", source="source:left"),
        _thread("K", "K:1", source="source:right"),
    )
    aliased = _pair_threads(
        _thread("K", "same"),
        _thread("X", "same"),
    )

    assert isinstance(independent.witness, DirectPair)
    assert isinstance(same_domain_independent.witness, DirectPair)
    assert independent.aperture is None
    assert same_domain.obstruction == "same-domain-linear-conflict"
    assert same_domain.aperture is None
    assert aliased.obstruction == "occurrence-alias"
    assert aliased.aperture is None


def test_swapping_lines_dualizes_ports_but_preserves_the_hole_domain() -> None:
    left = _thread("t", "t:0")
    right = _thread("K", "K:0")
    forward = _pair_threads(left, right).aperture
    reverse = _pair_threads(right, left).aperture

    assert forward is not None
    assert reverse is not None
    assert forward.domain == reverse.domain == "X"
    assert forward.dual() == reverse
