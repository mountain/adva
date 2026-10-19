"""Finite pairing of accepted AM syntax with the built-in closed LineView."""

from dataclasses import dataclass, replace

import pytest
from test_bootstrap_zero_syntax_coordination import (
    SyntaxCoordinationProjection,
    _constructor_signature,
    _coordinate_am,
)
from test_bootstrap_zero_whole_cut_grammar import (
    Atom,
    Carrier,
    HistoryComposition,
    LineView,
    Production,
    Use,
    _fixture,
    _line_view,
    _validate_whole,
)


@dataclass(frozen=True)
class LineCoordinationCandidate:
    line: LineView
    residuals: tuple[str, ...]


@dataclass(frozen=True)
class PairedLineCoordination:
    am: SyntaxCoordinationProjection
    line: LineView
    shared_occurrences: tuple[tuple[str, str, str, int], ...]
    line_channels: tuple[tuple[str, str, str, str, tuple[tuple[str, int, str], ...]], ...]
    residuals: tuple[str, ...]


def _channel_ledger(line):
    return tuple(
        (
            channel.name,
            channel.source_port,
            channel.target_port,
            channel.motion.value,
            tuple((step.name, step.gap, step.crossing.value) for step in channel.thread),
        )
        for channel in line.channels
    )


def _receive_line_coordination(term, expected, candidate):
    """Pair two checked syntax views; do not infer semantics or reconstruct the source."""
    _validate_whole(expected)
    expected_line = _line_view(expected)
    if candidate.line != expected_line:
        raise ValueError("line view must equal the view derived from the independent source")
    if candidate.residuals != expected.residuals:
        raise ValueError("coordination must retain the exact ordered source residual ledger")

    am = _coordinate_am(term, expected)
    occurrences = tuple(
        (port.source, port.occurrence, port.value_type, port.multiplicity)
        for port in candidate.line.ports
    )
    if occurrences != am.occurrence_ledger:
        raise ValueError("AM and LineView must share one exact ordered occurrence ledger")
    return PairedLineCoordination(
        am=am,
        line=candidate.line,
        shared_occurrences=occurrences,
        line_channels=_channel_ledger(candidate.line),
        residuals=candidate.residuals,
    )


def _one_use_term(form):
    port = form.ports[0]
    return HistoryComposition(
        Use(port.source, port.occurrence, port.value_type),
        Atom("line-context"),
    )


def _renamed_closed(prefix):
    form = _fixture()
    cell_names = {cell.name: f"{prefix}{cell.name}" for cell in form.cells}
    port_names = {port.name: f"{prefix}{port.name}" for port in form.ports}
    sources = {port.source: f"{prefix}{port.source}" for port in form.ports}
    occurrences = {port.occurrence: f"{prefix}{port.occurrence}" for port in form.ports}
    cells = tuple(
        replace(
            cell,
            name=cell_names[cell.name],
            left_port=port_names[cell.left_port],
            right_port=port_names[cell.right_port],
        )
        for cell in form.cells
    )
    ports = tuple(
        replace(
            port,
            name=port_names[port.name],
            cut=cell_names[port.cut],
            source=sources[port.source],
            occurrence=occurrences[port.occurrence],
        )
        for port in form.ports
    )
    channels = tuple(
        replace(
            channel,
            name=f"{prefix}{channel.name}",
            source_port=port_names[channel.source_port],
            target_port=port_names[channel.target_port],
            thread=tuple(replace(step, name=f"{prefix}{step.name}") for step in channel.thread),
        )
        for channel in form.channels
    )
    productions = tuple(
        Production(
            sources[production.source],
            tuple(occurrences[item] for item in production.occurrences),
        )
        for production in form.productions
    )
    renamed = replace(
        form,
        name=f"{prefix}{form.name}",
        cells=cells,
        ports=ports,
        channels=channels,
        circle_order=tuple(port_names[item] for item in form.circle_order),
        productions=productions,
    )
    _validate_whole(renamed)
    return renamed


def test_accepted_am_and_line_view_share_exact_source_coordinates():
    form = _fixture()
    candidate = LineCoordinationCandidate(_line_view(form), form.residuals)

    received = _receive_line_coordination(_one_use_term(form), form, candidate)

    assert received.line.carrier is Carrier.LINE
    assert received.am.whole == received.line.whole == form.name
    assert received.shared_occurrences == received.am.occurrence_ledger
    assert received.line_channels == _channel_ledger(_line_view(form))
    assert received.residuals == form.residuals == ()


def test_fresh_closed_source_reuses_relation_without_reusing_identities():
    first = _fixture()
    fresh = _renamed_closed("line-fresh-")
    original = _receive_line_coordination(
        _one_use_term(first),
        first,
        LineCoordinationCandidate(_line_view(first), first.residuals),
    )
    reused = _receive_line_coordination(
        _one_use_term(fresh),
        fresh,
        LineCoordinationCandidate(_line_view(fresh), fresh.residuals),
    )

    assert _constructor_signature(original.am) == _constructor_signature(reused.am)
    assert original.line.whole != reused.line.whole
    assert original.shared_occurrences != reused.shared_occurrences
    assert original.line_channels != reused.line_channels
    assert original.residuals == reused.residuals == ()


@pytest.mark.parametrize(
    "case",
    (
        "foreign-am",
        "foreign-line",
        "reordered-ports",
        "omitted-channel",
        "altered-residual",
        "open-source",
    ),
)
def test_pairing_refuses_source_view_and_ledger_substitution(case):
    form = _fixture()
    term = _one_use_term(form)
    line = _line_view(form)
    residuals = form.residuals
    if case == "foreign-am":
        term = _one_use_term(_renamed_closed("foreign-am-"))
    elif case == "foreign-line":
        line = _line_view(_renamed_closed("foreign-line-"))
    elif case == "reordered-ports":
        line = replace(line, ports=line.ports[::-1])
    elif case == "omitted-channel":
        line = replace(line, channels=line.channels[:-1])
    elif case == "altered-residual":
        residuals = ("invented-residual",)
    else:
        form = _fixture(open_last=True)
        term = Atom("open-source")
        line = LineView(Carrier.LINE, form.name, form.ports, form.channels)
        residuals = form.residuals

    with pytest.raises(ValueError):
        _receive_line_coordination(
            term,
            form,
            LineCoordinationCandidate(line, residuals),
        )
