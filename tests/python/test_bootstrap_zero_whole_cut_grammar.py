from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace
from enum import Enum
from typing import TypeAlias

import pytest


class Role(Enum):
    CONSTRUCTION = "K"
    SPACE = "X"
    TIME = "t"


class Side(Enum):
    LEFT = "L"
    RIGHT = "R"


class Polarity(Enum):
    POSITIVE = "+"
    NEGATIVE = "-"


class Motion(Enum):
    FORWARD = "forward"
    REVERSE = "reverse"


class Carrier(Enum):
    LINE = "line"
    CIRCLE = "circle"


class ExtensionSlot(Enum):
    ARITY = "arity"
    TOPOLOGY = "topology"
    COLLISION_THEORY = "collision-theory"
    CHARACTER = "character"
    INTERPRETER = "interpreter"
    EQUATION = "equation"
    OBSERVER = "observer"
    PROOF = "proof"
    LEARNING = "learning"
    OMEGA = "omega"
    ARITHMETIC = "arithmetic"
    PHYSICAL = "physical"


@dataclass(frozen=True)
class Port:
    name: str
    cut: str
    side: Side
    polarity: Polarity
    value_type: str
    source: str
    occurrence: str
    multiplicity: int = 1


@dataclass(frozen=True)
class WholeCutCell:
    name: str
    left_role: Role
    right_role: Role
    middle_role: Role
    left_port: str
    right_port: str


@dataclass(frozen=True)
class ThroughChannel:
    name: str
    source_port: str
    target_port: str
    motion: Motion


@dataclass(frozen=True)
class OpenPort:
    port: str
    hole: str
    residual: str


@dataclass(frozen=True)
class Production:
    source: str
    occurrences: tuple[str, ...]


@dataclass(frozen=True)
class HoleDecl:
    name: str
    value_type: str
    port: str


@dataclass(frozen=True)
class Alternative:
    name: str
    value_type: str
    form: AMTerm


@dataclass(frozen=True)
class AlternativeDecl:
    hole: str
    alternatives: tuple[Alternative, ...]


@dataclass(frozen=True)
class WholeCut6:
    name: str
    cells: tuple[WholeCutCell, ...]
    ports: tuple[Port, ...]
    channels: tuple[ThroughChannel, ...]
    open_ports: tuple[OpenPort, ...]
    circle_order: tuple[str, ...]
    residuals: tuple[str, ...]
    productions: tuple[Production, ...]
    holes: tuple[HoleDecl, ...]
    alternatives: tuple[AlternativeDecl, ...]


@dataclass(frozen=True)
class LineView:
    carrier: Carrier
    whole: str
    ports: tuple[Port, ...]
    channels: tuple[ThroughChannel, ...]


@dataclass(frozen=True)
class CircleView:
    carrier: Carrier
    whole: str
    ports: tuple[Port, ...]
    circle_order: tuple[str, ...]


@dataclass(frozen=True)
class Collision:
    name: str
    locus: str
    members: tuple[Port, ...]
    output_multiplicity: int


@dataclass(frozen=True)
class Boundary:
    name: str


@dataclass(frozen=True)
class Expansion:
    name: str


@dataclass(frozen=True)
class Generate:
    name: str
    source: Boundary
    target: Expansion


@dataclass(frozen=True)
class FibrePoint:
    name: str
    value_type: str


@dataclass(frozen=True)
class Fibre:
    target: FibrePoint
    members: tuple[FibrePoint, ...]


@dataclass(frozen=True)
class FibreAccount:
    expansion: str
    boundary: str
    domain: tuple[FibrePoint, ...]
    codomain: tuple[FibrePoint, ...]
    images: tuple[tuple[str, str], ...]
    fibres: tuple[Fibre, ...]


@dataclass(frozen=True)
class Retract:
    name: str
    source: Expansion
    target: Boundary
    residuals: tuple[str, ...]
    account: FibreAccount


@dataclass(frozen=True)
class SplitWitness:
    name: str
    generate: Generate
    retract: Retract


@dataclass(frozen=True)
class Traversal:
    name: str
    source: Expansion
    target: Expansion
    retract: Retract
    generate: Generate
    common: Boundary


@dataclass(frozen=True)
class Atom:
    name: str


@dataclass(frozen=True)
class EmptyZero:
    name: str


@dataclass(frozen=True)
class PolarDual:
    term: AMTerm


@dataclass(frozen=True)
class Plus:
    left: AMTerm
    right: AMTerm


@dataclass(frozen=True)
class Tensor:
    outer: AMTerm
    inner: AMTerm


AMTerm: TypeAlias = Atom | EmptyZero | PolarDual | Plus | Tensor


@dataclass(frozen=True)
class BalancedZero:
    positive: AMTerm
    negative: PolarDual


@dataclass(frozen=True)
class HistoryComposition:
    first: str
    second: str


@dataclass(frozen=True)
class ExtensionDecl:
    name: str
    slot: ExtensionSlot
    inputs: tuple[str, ...]
    outputs: tuple[str, ...]
    preserves: tuple[str, ...]
    countercases: tuple[str, ...]
    status: str = "research"


EXPECTED_ROLE_TRIPLES = (
    (Role.CONSTRUCTION, Role.SPACE, Role.TIME),
    (Role.SPACE, Role.TIME, Role.CONSTRUCTION),
    (Role.TIME, Role.CONSTRUCTION, Role.SPACE),
)


def minimum_positive_degrees(cut_count: int, ports_per_cut: int = 2) -> int:
    if cut_count <= 0 or ports_per_cut <= 0:
        raise ValueError("cut and port counts must be positive")
    return cut_count * ports_per_cut


def _fixture(open_last: bool = False) -> WholeCut6:
    cells = (
        WholeCutCell("c-KX", *EXPECTED_ROLE_TRIPLES[0], "p-KX-L", "p-KX-R"),
        WholeCutCell("c-Xt", *EXPECTED_ROLE_TRIPLES[1], "p-Xt-L", "p-Xt-R"),
        WholeCutCell("c-tK", *EXPECTED_ROLE_TRIPLES[2], "p-tK-L", "p-tK-R"),
    )
    ports = tuple(
        Port(
            name=f"p-{edge}-{side.value}",
            cut=f"c-{edge}",
            side=side,
            polarity=(Polarity.POSITIVE if side is Side.LEFT else Polarity.NEGATIVE),
            value_type="A",
            source=f"s-{edge}-{side.value}",
            occurrence=f"o-{edge}-{side.value}",
        )
        for edge in ("KX", "Xt", "tK")
        for side in (Side.LEFT, Side.RIGHT)
    )
    channels = (
        ThroughChannel("e-1", "p-KX-L", "p-Xt-R", Motion.FORWARD),
        ThroughChannel("e-2", "p-Xt-L", "p-tK-R", Motion.FORWARD),
        ThroughChannel("e-3", "p-tK-L", "p-KX-R", Motion.FORWARD),
    )
    open_ports: tuple[OpenPort, ...] = ()
    residuals: tuple[str, ...] = ()
    if open_last:
        channels = channels[:2]
        open_ports = (
            OpenPort("p-tK-L", "h-tK-L", "r-tK-L"),
            OpenPort("p-KX-R", "h-KX-R", "r-KX-R"),
        )
        residuals = ("r-tK-L", "r-KX-R")
    return WholeCut6(
        "whole-6",
        cells,
        ports,
        channels,
        open_ports,
        (
            "p-KX-L",
            "p-KX-R",
            "p-tK-L",
            "p-tK-R",
            "p-Xt-L",
            "p-Xt-R",
        ),
        residuals,
        tuple(Production(port.source, (port.occurrence,)) for port in ports),
        tuple(HoleDecl(item.hole, "A", item.port) for item in open_ports),
        tuple(
            AlternativeDecl(
                item.hole,
                tuple(
                    Alternative(f"{item.hole}-option-{i}", "A", Atom(f"body-{i}")) for i in (0, 1)
                ),
            )
            for item in open_ports
        ),
    )


def _validate_closed_alternating_cycle(form: WholeCut6) -> None:
    edge_kind: dict[frozenset[str], str] = {}
    for cell in form.cells:
        edge = frozenset((cell.left_port, cell.right_port))
        if edge in edge_kind:
            raise ValueError("cut pairings must be distinct")
        edge_kind[edge] = "cut"
    for channel in form.channels:
        edge = frozenset((channel.source_port, channel.target_port))
        if edge in edge_kind:
            if edge_kind[edge] == "cut":
                raise ValueError("cut and through pairings must be disjoint")
            raise ValueError("through pairings must be distinct")
        edge_kind[edge] = "thread"

    ordered_edges = tuple(
        frozenset(
            (
                form.circle_order[index],
                form.circle_order[(index + 1) % len(form.circle_order)],
            )
        )
        for index in range(len(form.circle_order))
    )
    if len(set(ordered_edges)) != 6 or set(ordered_edges) != set(edge_kind):
        raise ValueError("circle order must be induced by the cut and through pairings")
    kinds = tuple(edge_kind[edge] for edge in ordered_edges)
    if any(kinds[index] == kinds[(index + 1) % len(kinds)] for index in range(6)):
        raise ValueError("cut and through steps must alternate around the circle")


def _validate_productions(form: WholeCut6) -> None:
    """Check research-local allocation records, without allocating native IDs."""
    ports = {port.occurrence: port for port in form.ports}
    sources: set[str] = set()
    assigned: list[str] = []
    for production in form.productions:
        if not isinstance(production.source, str) or not production.source:
            raise ValueError("production source must be a nonempty name")
        if production.source in sources:
            raise ValueError("one production entry is required per source")
        sources.add(production.source)
        if not production.occurrences:
            raise ValueError("a production must retain at least one occurrence")
        value_types: set[str] = set()
        for occurrence in production.occurrences:
            if not isinstance(occurrence, str) or not occurrence:
                raise ValueError("production occurrence must be a nonempty name")
            if occurrence not in ports:
                raise ValueError("production names an unknown occurrence")
            port = ports[occurrence]
            if port.source != production.source:
                raise ValueError("production source disagrees with port source")
            value_types.add(port.value_type)
            assigned.append(occurrence)
        if len(value_types) != 1:
            raise ValueError("one source must retain one value type")
    if Counter(assigned) != Counter(port.occurrence for port in form.ports):
        raise ValueError("production ledger must account for each occurrence exactly once")


def _validate_whole(form: WholeCut6) -> None:
    triples = tuple((cell.left_role, cell.right_role, cell.middle_role) for cell in form.cells)
    if triples != EXPECTED_ROLE_TRIPLES:
        raise ValueError("WholeCut6 needs the ordered three-role cut cycle")
    if len(form.ports) != 6:
        raise ValueError("the open stratum must contain six ports")

    port_names = tuple(port.name for port in form.ports)
    occurrences = tuple(port.occurrence for port in form.ports)
    if len(set(port_names)) != 6 or len(set(occurrences)) != 6:
        raise ValueError("initial port and occurrence names must be distinct")
    if any(port.multiplicity != 1 for port in form.ports):
        raise ValueError("initial ports must have unit multiplicity")

    _validate_productions(form)

    ports_by_name = {port.name: port for port in form.ports}
    for cell in form.cells:
        expected_ports = {cell.left_port, cell.right_port}
        actual_ports = {port.name for port in form.ports if port.cut == cell.name}
        if actual_ports != expected_ports:
            raise ValueError("each cut must own its two declared ports")
        pair = tuple(ports_by_name[name] for name in (cell.left_port, cell.right_port))
        if {port.side for port in pair} != {Side.LEFT, Side.RIGHT}:
            raise ValueError("a cut must have one left and one right side")
        if {port.polarity for port in pair} != {
            Polarity.POSITIVE,
            Polarity.NEGATIVE,
        }:
            raise ValueError("a cut must have opposite local polarities")

    accounted = tuple(
        name for channel in form.channels for name in (channel.source_port, channel.target_port)
    ) + tuple(item.port for item in form.open_ports)
    if Counter(accounted) != Counter(port_names):
        raise ValueError("every port must be accounted for exactly once")
    if Counter(form.circle_order) != Counter(port_names):
        raise ValueError("the circle view must use the authoritative port ledger")
    if not form.open_ports:
        _validate_closed_alternating_cycle(form)

    for channel in form.channels:
        source = ports_by_name[channel.source_port]
        target = ports_by_name[channel.target_port]
        if source.value_type != target.value_type:
            raise ValueError("through endpoints must have equal value types")
    for item in form.open_ports:
        if not item.hole or item.residual not in form.residuals:
            raise ValueError("an open port needs a named hole and retained residual")

    _validate_hole_ledgers(form)


def _validate_hole_ledgers(form: WholeCut6) -> None:
    expected = {item.hole: item.port for item in form.open_ports}
    if len(expected) != len(form.open_ports):
        raise ValueError("open ports must have distinct hole names")
    names = tuple(hole.name for hole in form.holes)
    if len(set(names)) != len(names) or set(names) != set(expected):
        raise ValueError("hole declarations must exactly account for open holes")
    ports = {port.name: port for port in form.ports}
    holes = {hole.name: hole for hole in form.holes}
    for hole in form.holes:
        if hole.port != expected[hole.name] or hole.value_type != ports[hole.port].value_type:
            raise ValueError("hole declaration must retain its port and type")
    alternative_holes = tuple(entry.hole for entry in form.alternatives)
    if len(set(alternative_holes)) != len(alternative_holes) or not set(alternative_holes) <= set(
        expected
    ):
        raise ValueError("alternative declarations must name distinct existing open holes")
    for entry in form.alternatives:
        option_names = tuple(option.name for option in entry.alternatives)
        if not option_names or len(set(option_names)) != len(option_names):
            raise ValueError("an alternative declaration needs distinct nonempty options")
        if any(not isinstance(name, str) or not name for name in option_names):
            raise ValueError("alternative names must be nonempty strings")
        if any(option.value_type != holes[entry.hole].value_type for option in entry.alternatives):
            raise ValueError("alternative type disagrees with its hole")
        # Bodies are retained raw AM syntax; no evaluation or general type inference.
        if any(
            not isinstance(option.form, (Atom, EmptyZero, PolarDual, Plus, Tensor))
            for option in entry.alternatives
        ):
            raise ValueError("unsupported alternative body constructor")


def _line_view(form: WholeCut6) -> LineView:
    _validate_whole(form)
    if form.open_ports:
        raise ValueError("a closed line view needs a perfect through matching")
    return LineView(Carrier.LINE, form.name, form.ports, form.channels)


def _circle_view(form: WholeCut6) -> CircleView:
    _validate_whole(form)
    if form.open_ports:
        raise ValueError("a circle view needs a closed alternating pairing cycle")
    return CircleView(Carrier.CIRCLE, form.name, form.ports, form.circle_order)


def _flip_polarity(ports: tuple[Port, ...]) -> tuple[Port, ...]:
    return tuple(
        replace(
            port,
            polarity=(
                Polarity.NEGATIVE if port.polarity is Polarity.POSITIVE else Polarity.POSITIVE
            ),
        )
        for port in ports
    )


def _conjugate_motion(
    channels: tuple[ThroughChannel, ...],
) -> tuple[ThroughChannel, ...]:
    return tuple(
        replace(
            channel,
            motion=(Motion.REVERSE if channel.motion is Motion.FORWARD else Motion.FORWARD),
        )
        for channel in channels
    )


def _route_adjacent(ports: tuple[Port, ...], gap: int) -> tuple[Port, ...]:
    left = gap - 1
    right = gap
    if left < 0 or right >= len(ports):
        raise ValueError("a braid gap must select adjacent ports")
    routed = list(ports)
    routed[left], routed[right] = routed[right], routed[left]
    return tuple(routed)


def _validate_collision(collision: Collision) -> None:
    if len(collision.members) < 2:
        raise ValueError("a collision needs at least two retained members")
    if len({member.name for member in collision.members}) != len(collision.members):
        raise ValueError("collision members must retain distinct port names")
    if collision.output_multiplicity != sum(member.multiplicity for member in collision.members):
        raise ValueError("collision multiplicity must equal member multiplicity")


def _validate_retraction(retract: Retract) -> None:
    account = retract.account
    if (account.expansion, account.boundary) != (retract.source.name, retract.target.name):
        raise ValueError("fibre account must bind the declared retraction boundary")
    domain = {point.name: point for point in account.domain}
    codomain = {point.name: point for point in account.codomain}
    if len(domain) != len(account.domain) or len(codomain) != len(account.codomain):
        raise ValueError("fibre point names must be distinct within each boundary")
    if any(
        not isinstance(p.name, str)
        or not p.name
        or not isinstance(p.value_type, str)
        or not p.value_type
        for p in (*account.domain, *account.codomain)
    ):
        raise ValueError("fibre points need nonempty names and types")
    if Counter(source for source, _ in account.images) != Counter(tuple(domain)):
        raise ValueError("retraction images must account for each domain point once")
    if any(target not in codomain for _, target in account.images):
        raise ValueError("retraction image is outside the codomain")
    expected = {target: [] for target in codomain}
    for source, target in account.images:
        expected[target].append(domain[source])
    if Counter(f.target.name for f in account.fibres) != Counter(tuple(codomain)):
        raise ValueError("fibres must retain every codomain point, including empty fibres")
    for fibre in account.fibres:
        if fibre.target != codomain[fibre.target.name]:
            raise ValueError("fibre target payload disagrees with the codomain")
        if Counter(fibre.members) != Counter(expected[fibre.target.name]):
            raise ValueError("fibre members disagree with the declared map")


def _singleton_account(expansion: Expansion, boundary: Boundary) -> FibreAccount:
    source = FibrePoint("domain-point", "A")
    target = FibrePoint("boundary-point", "A")
    return FibreAccount(
        expansion.name,
        boundary.name,
        (source,),
        (target,),
        ((source.name, target.name),),
        (Fibre(target, (source,)),),
    )


def _validate_split(witness: SplitWitness) -> None:
    _validate_retraction(witness.retract)
    if witness.generate.source != witness.retract.target:
        raise ValueError("retract after generate must return the same boundary")
    if witness.generate.target != witness.retract.source:
        raise ValueError("generate and retract must share one expansion")


def _factor_traversal(name: str, retract: Retract, generate: Generate) -> Traversal:
    _validate_retraction(retract)
    if retract.target != generate.source:
        raise ValueError("traversal needs one common retraction/generation boundary")
    return Traversal(
        name,
        retract.source,
        generate.target,
        retract,
        generate,
        retract.target,
    )


def _validate_extension(extension: ExtensionDecl) -> None:
    if not extension.inputs or not extension.outputs:
        raise ValueError("an extension needs typed input and output boundaries")
    if not extension.preserves:
        raise ValueError("an extension needs preservation obligations")
    if not extension.countercases:
        raise ValueError("an extension needs visible countercases")
    if extension.status not in {"research", "proposed-stable"}:
        raise ValueError("an extension needs an explicit status")


def test_three_binary_cuts_have_six_as_the_conditional_minimum() -> None:
    assert minimum_positive_degrees(3) == 6
    assert minimum_positive_degrees(1) == 2
    assert minimum_positive_degrees(4) == 8


def test_whole_cut_six_forms_one_closed_sustained_carrier() -> None:
    form = _fixture()

    _validate_whole(form)
    assert len(form.cells) == 3
    assert len(form.ports) == 6
    assert len(form.channels) == 3
    assert sum(port.multiplicity for port in form.ports) == 6


def test_a_severed_port_is_rejected_but_an_explicit_hole_is_accepted() -> None:
    form = _fixture()
    broken = replace(form, channels=form.channels[:2])

    with pytest.raises(ValueError, match="accounted for exactly once"):
        _validate_whole(broken)
    _validate_whole(_fixture(open_last=True))


def test_line_and_circle_views_share_one_literal_occurrence_ledger() -> None:
    form = _fixture()
    line = _line_view(form)
    circle = _circle_view(form)

    assert line.whole == circle.whole == form.name
    assert line.ports is form.ports
    assert circle.ports is form.ports
    assert tuple(port.occurrence for port in line.ports) == tuple(
        port.occurrence for port in circle.ports
    )


def test_circle_order_must_follow_the_two_alternating_pairings() -> None:
    form = _fixture()
    merely_recounted = replace(
        form,
        circle_order=tuple(port.name for port in form.ports),
    )

    with pytest.raises(ValueError, match="induced by"):
        _validate_whole(merely_recounted)
    with pytest.raises(ValueError, match="closed alternating"):
        _circle_view(_fixture(open_last=True))


def test_duality_polarity_and_conjugation_change_different_fields() -> None:
    form = _fixture()
    line = _line_view(form)
    circle = _circle_view(form)
    flipped = _flip_polarity(form.ports)
    conjugated = _conjugate_motion(form.channels)

    assert line.carrier is Carrier.LINE
    assert circle.carrier is Carrier.CIRCLE
    assert tuple(port.side for port in flipped) == tuple(port.side for port in form.ports)
    assert tuple(port.polarity for port in flipped) != tuple(port.polarity for port in form.ports)
    assert tuple(channel.motion for channel in conjugated) != tuple(
        channel.motion for channel in form.channels
    )
    assert tuple(channel.source_port for channel in conjugated) == tuple(
        channel.source_port for channel in form.channels
    )


def test_braid_routing_preserves_every_complete_port_record() -> None:
    ports = _fixture().ports
    routed = _route_adjacent(_route_adjacent(ports, 1), 4)

    assert Counter(routed) == Counter(ports)
    assert {port.occurrence for port in routed} == {port.occurrence for port in ports}
    assert sum(port.multiplicity for port in routed) == 6


def test_collision_reduces_loci_without_erasing_members_or_degree() -> None:
    left, right = _fixture().ports[:2]
    collision = Collision("xi-1", "lambda-1", (left, right), 2)

    _validate_collision(collision)
    assert len({collision.locus}) == 1
    assert len(collision.members) == 2
    assert {member.polarity for member in collision.members} == {
        Polarity.POSITIVE,
        Polarity.NEGATIVE,
    }
    assert collision.output_multiplicity == 2


def test_collision_cannot_claim_cancellation_by_dropping_a_member() -> None:
    left, right = _fixture().ports[:2]
    malformed = Collision("xi-bad", "lambda", (left, right), 1)

    with pytest.raises(ValueError, match="multiplicity"):
        _validate_collision(malformed)


def test_split_witness_returns_the_boundary_but_not_raw_expansion_identity() -> None:
    boundary = Boundary("B")
    expansion = Expansion("E")
    generate = Generate("g", boundary, expansion)
    retract = Retract(
        "r",
        expansion,
        boundary,
        ("forgotten-local-detail",),
        _singleton_account(expansion, boundary),
    )
    witness = SplitWitness("split-rg", generate, retract)

    _validate_split(witness)
    assert witness.retract.target == witness.generate.source
    assert witness.generate.target is expansion
    assert witness.retract.residuals


def test_traversal_must_factor_as_retraction_then_generation() -> None:
    common = Boundary("B")
    source = Expansion("E-i")
    target = Expansion("E-j")
    retract = Retract("r-i", source, common, ("r-i-residual",), _singleton_account(source, common))
    generate = Generate("g-j", common, target)

    traversal = _factor_traversal("T-i-j", retract, generate)

    assert traversal.source is source
    assert traversal.target is target
    assert traversal.common is common
    with pytest.raises(ValueError, match="common"):
        _factor_traversal(
            "bad",
            retract,
            Generate("g-k", Boundary("different"), target),
        )


def test_plus_tensor_and_historical_composition_are_distinct_syntax() -> None:
    left = Atom("A")
    right = Atom("B")

    assert Plus(left, right) != Tensor(left, right)
    assert not isinstance(HistoryComposition("f", "g"), (Plus, Tensor))


def test_zero_shaped_forms_do_not_collapse_in_raw_syntax() -> None:
    zero = EmptyZero("zero-empty")
    term = Atom("E")
    absorbed = Tensor(zero, term)
    polar_pair = Plus(term, PolarDual(term))
    balanced = BalancedZero(term, PolarDual(term))

    assert absorbed != zero
    assert polar_pair != zero
    assert balanced.positive is term
    assert balanced.negative.term is term


def test_six_direction_labels_are_three_channels_with_two_orientations() -> None:
    directions = {
        ("KX", Motion.FORWARD),
        ("KX", Motion.REVERSE),
        ("Xt", Motion.FORWARD),
        ("Xt", Motion.REVERSE),
        ("tK", Motion.FORWARD),
        ("tK", Motion.REVERSE),
    }

    assert len(directions) == 6
    assert {edge for edge, _ in directions} == {"KX", "Xt", "tK"}


def test_every_future_family_has_a_visible_extension_slot() -> None:
    assert {slot.value for slot in ExtensionSlot} == {
        "arity",
        "topology",
        "collision-theory",
        "character",
        "interpreter",
        "equation",
        "observer",
        "proof",
        "learning",
        "omega",
        "arithmetic",
        "physical",
    }


def test_extension_needs_preservation_obligations_and_countercases() -> None:
    extension = ExtensionDecl(
        "other-topology",
        ExtensionSlot.TOPOLOGY,
        ("WholeCut6",),
        ("PresentedGraph",),
        ("occurrence-ledger", "typed-boundary"),
        ("disconnected-port",),
    )

    _validate_extension(extension)
    with pytest.raises(ValueError, match="preservation"):
        _validate_extension(replace(extension, preserves=()))
    with pytest.raises(ValueError, match="countercases"):
        _validate_extension(replace(extension, countercases=()))
