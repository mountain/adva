from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, replace

import pytest

from test_bootstrap_zero_cell_carrier_views import (
    LOGIC_VIEW,
    RelationBoundary,
    RelationKind,
    StateOccurrence,
    StepOccurrence,
    StratifiedCarrier,
    Thread,
    _project,
    _thread_word,
    _validate_carrier,
)
from test_bootstrap_zero_whole_cut_grammar import (
    Motion,
    Port,
    ThroughChannel,
    WholeCut6,
    _fixture as _whole_cut_fixture,
    _validate_whole,
)


@dataclass(frozen=True)
class PairingEdge:
    family: str
    origin: str
    first_port: str
    second_port: str
    native_source: str
    native_target: str


@dataclass(frozen=True)
class WholeCutM6Bridge:
    name: str
    whole: str
    carrier: StratifiedCarrier
    port_to_state: tuple[tuple[str, str], ...]
    step_to_origin: tuple[tuple[str, str], ...]


def _state_name(port: str) -> str:
    return f"state[{port}]"


def _pairing_edges(form: WholeCut6) -> dict[frozenset[str], PairingEdge]:
    edges: dict[frozenset[str], PairingEdge] = {}
    for cell in form.cells:
        edge = frozenset((cell.left_port, cell.right_port))
        if edge in edges:
            raise ValueError("cut pairings must be distinct")
        edges[edge] = PairingEdge(
            "cut",
            cell.name,
            cell.left_port,
            cell.right_port,
            cell.left_port,
            cell.right_port,
        )
    for channel in form.channels:
        edge = frozenset((channel.source_port, channel.target_port))
        if edge in edges:
            if edges[edge].family == "cut":
                raise ValueError("cut and through pairings must be disjoint")
            raise ValueError("through pairings must be distinct")
        edges[edge] = PairingEdge(
            "thread",
            channel.name,
            channel.source_port,
            channel.target_port,
            channel.source_port,
            channel.target_port,
        )
    return edges


def _bridge_state(port: Port) -> StateOccurrence:
    return StateOccurrence(
        _state_name(port.name),
        port.source,
        port.occurrence,
        port.value_type,
        port.multiplicity,
        port.name,
    )


def _bridge_step(
    index: int,
    source_port: str,
    target_port: str,
    edge: PairingEdge,
) -> StepOccurrence:
    presentation = (
        "native"
        if (source_port, target_port) == (edge.native_source, edge.native_target)
        else "converse"
    )
    return StepOccurrence(
        f"boundary-step-{index}",
        edge.family,
        _state_name(source_port),
        _state_name(target_port),
        edge.origin,
        presentation,
    )


def _bridge_whole_cut6_to_m6(form: WholeCut6) -> WholeCutM6Bridge:
    _validate_whole(form)
    if form.open_ports:
        raise ValueError("the WholeCut6 to M6 bridge requires a closed through matching")

    ports_by_name = {port.name: port for port in form.ports}
    edges = _pairing_edges(form)
    if len(edges) != 6:
        raise ValueError("three cut and three through pairings must give six edges")

    cycle = form.circle_order
    top_ports = cycle[:4]
    bottom_ports = (cycle[0], cycle[5], cycle[4], cycle[3])
    oriented_pairs = tuple(zip(top_ports[:-1], top_ports[1:], strict=True)) + tuple(
        zip(bottom_ports[:-1], bottom_ports[1:], strict=True)
    )

    steps: list[StepOccurrence] = []
    for index, (source_port, target_port) in enumerate(oriented_pairs):
        key = frozenset((source_port, target_port))
        if key not in edges:
            raise ValueError("every M6 boundary step must come from one whole-cut pairing")
        steps.append(_bridge_step(index, source_port, target_port, edges[key]))

    source_thread = Thread(
        "whole-cut-kappa-tau-kappa",
        tuple(_state_name(port) for port in top_ports),
        tuple(step.name for step in steps[:3]),
    )
    target_thread = Thread(
        "whole-cut-tau-kappa-tau",
        tuple(_state_name(port) for port in bottom_ports),
        tuple(step.name for step in steps[3:]),
    )
    relation = RelationBoundary(
        "whole-cut-m6-boundary",
        RelationKind.BRAID,
        source_thread,
        target_thread,
        tuple(_state_name(port) for port in cycle),
    )
    states = tuple(_bridge_state(ports_by_name[name]) for name in cycle)
    carrier = StratifiedCarrier(
        "M6[whole-6]",
        states,
        tuple(steps),
        (relation,),
    )
    bridge = WholeCutM6Bridge(
        "whole-cut6-to-m6",
        form.name,
        carrier,
        tuple((port, _state_name(port)) for port in cycle),
        tuple((step.name, step.origin or "") for step in steps),
    )
    _validate_bridge(form, bridge)
    return bridge


def _validate_bridge(form: WholeCut6, bridge: WholeCutM6Bridge) -> None:
    _validate_carrier(bridge.carrier)
    if bridge.whole != form.name:
        raise ValueError("bridge must retain its WholeCut6 source name")

    ports_by_name = {port.name: port for port in form.ports}
    port_to_state = dict(bridge.port_to_state)
    if set(port_to_state) != set(ports_by_name):
        raise ValueError("bridge must account for every source port exactly once")
    if len(set(port_to_state.values())) != 6:
        raise ValueError("bridge state names must be distinct from one another")

    states_by_name = {state.name: state for state in bridge.carrier.states}
    if set(states_by_name) != set(port_to_state.values()):
        raise ValueError("bridge state map must cover the carrier state ledger")
    for port_name, state_name in bridge.port_to_state:
        port = ports_by_name[port_name]
        state = states_by_name[state_name]
        if state.name == port.name or state.origin_port != port.name:
            raise ValueError("port and state names must stay typed and distinct")
        if (
            state.source,
            state.occurrence,
            state.value_type,
            state.multiplicity,
        ) != (
            port.source,
            port.occurrence,
            port.value_type,
            port.multiplicity,
        ):
            raise ValueError("state view must reuse the complete port occurrence record")

    cell_names = {cell.name for cell in form.cells}
    channel_names = {channel.name for channel in form.channels}
    expected_origins = cell_names | channel_names
    step_origins = dict(bridge.step_to_origin)
    if set(step_origins) != {step.name for step in bridge.carrier.steps}:
        raise ValueError("every boundary step needs one recorded origin")
    if set(step_origins.values()) != expected_origins:
        raise ValueError("boundary steps must use every cut and through origin once")
    if any(step.name in ports_by_name for step in bridge.carrier.steps):
        raise ValueError("step occurrences cannot reuse port names")
    if any(step.name in states_by_name for step in bridge.carrier.steps):
        raise ValueError("step occurrences cannot reuse state names")

    relation = bridge.carrier.relations[0]
    steps_by_name = {step.name: step for step in bridge.carrier.steps}
    if _thread_word(relation.source_thread, steps_by_name) != (
        "cut",
        "thread",
        "cut",
    ):
        raise ValueError("the first M6 side must read cut-thread-cut")
    if _thread_word(relation.target_thread, steps_by_name) != (
        "thread",
        "cut",
        "thread",
    ):
        raise ValueError("the second M6 side must read thread-cut-thread")
    if bridge.carrier.fillers:
        raise ValueError("whole-cut incidence alone cannot manufacture a braid filler")


def test_two_whole_cut_pairings_form_one_alternating_six_cycle() -> None:
    form = _whole_cut_fixture()
    bridge = _bridge_whole_cut6_to_m6(form)
    relation = bridge.carrier.relations[0]

    assert len(bridge.carrier.states) == 6
    assert len(bridge.carrier.steps) == 6
    assert Counter(step.operator for step in bridge.carrier.steps) == Counter(
        {"cut": 3, "thread": 3}
    )
    assert relation.circle_order == tuple(
        _state_name(port) for port in form.circle_order
    )


def test_bridge_reuses_occurrences_without_conflating_ports_states_or_steps() -> None:
    form = _whole_cut_fixture()
    bridge = _bridge_whole_cut6_to_m6(form)

    assert tuple(state.occurrence for state in bridge.carrier.states) == tuple(
        next(port.occurrence for port in form.ports if port.name == name)
        for name in form.circle_order
    )
    assert all(state.name != state.origin_port for state in bridge.carrier.states)
    assert {
        step.origin for step in bridge.carrier.steps if step.operator == "cut"
    } == {cell.name for cell in form.cells}
    assert {
        step.origin for step in bridge.carrier.steps if step.operator == "thread"
    } == {channel.name for channel in form.channels}


def test_bridge_logic_view_exposes_an_open_braid_obligation_only() -> None:
    bridge = _bridge_whole_cut6_to_m6(_whole_cut_fixture())
    logic = _project(bridge.carrier, LOGIC_VIEW)

    assert logic.occurrences is bridge.carrier.states
    assert len(logic.obligations) == 1
    assert logic.obligations[0].kind is RelationKind.BRAID
    assert logic.witnesses == ()
    assert logic.threads[0] != logic.threads[1]


def test_six_ports_without_the_alternating_pairing_cycle_do_not_make_m6() -> None:
    form = _whole_cut_fixture()
    nonalternating_channels = tuple(
        ThroughChannel(
            f"bad-{index}",
            cell.left_port,
            cell.right_port,
            Motion.FORWARD,
        )
        for index, cell in enumerate(form.cells)
    )

    with pytest.raises(ValueError, match="disjoint"):
        _bridge_whole_cut6_to_m6(replace(form, channels=nonalternating_channels))
    with pytest.raises(ValueError, match="induced by"):
        _bridge_whole_cut6_to_m6(
            replace(form, circle_order=tuple(port.name for port in form.ports))
        )


def test_open_holes_remain_valid_whole_cut_syntax_but_cannot_fake_m6() -> None:
    form = _whole_cut_fixture(open_last=True)

    _validate_whole(form)
    with pytest.raises(ValueError, match="closed through matching"):
        _bridge_whole_cut6_to_m6(form)
