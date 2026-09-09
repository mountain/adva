from __future__ import annotations

from dataclasses import replace

import pytest
from test_bootstrap_zero_whole_cut_grammar import (
    Production,
    _circle_view,
    _fixture,
    _line_view,
    _validate_whole,
)


def _partitions(prefix=(0,)):
    if len(prefix) == 6:
        yield prefix
        return
    for label in range(max(prefix) + 2):
        yield from _partitions((*prefix, label))


PARTITIONS = tuple(_partitions())


def _allocated(labels, prefix="allocated"):
    form = _fixture()
    ports = tuple(
        replace(port, source=f"{prefix}-source-{label}")
        for port, label in zip(form.ports, labels, strict=True)
    )
    productions = tuple(
        Production(
            f"{prefix}-source-{label}",
            tuple(port.occurrence for port in ports if port.source == f"{prefix}-source-{label}"),
        )
        for label in sorted(set(labels))
    )
    return replace(form, ports=ports, productions=productions)


def test_partition_family_is_complete_for_six_canonical_positions():
    # Bell recurrence, independent of the restricted-growth generator.
    from math import comb

    bell = [1]
    for n in range(6):
        bell.append(sum(comb(n, k) * bell[k] for k in range(n + 1)))
    assert len(set(PARTITIONS)) == len(PARTITIONS) == bell[6] == 203
    assert all(p[0] == 0 and all(p[i] <= max(p[:i]) + 1 for i in range(1, 6)) for p in PARTITIONS)


@pytest.mark.parametrize("labels", PARTITIONS)
def test_all_source_partitions_require_exact_production_accounting(labels):
    form = _allocated(labels)
    _validate_whole(form)
    # Independent relation readout: no normalization or occurrence erasure.
    port_relation = {(p.source, p.occurrence) for p in form.ports}
    ledger_pairs = [(p.source, o) for p in form.productions for o in p.occurrences]
    assert len(ledger_pairs) == 6 and set(ledger_pairs) == port_relation
    assert _line_view(form).ports == _circle_view(form).ports == form.ports
    first, *rest = form.productions
    with pytest.raises(ValueError):
        _validate_whole(
            replace(form, productions=(replace(first, occurrences=first.occurrences[1:]), *rest))
        )
    with pytest.raises(ValueError, match="exactly once"):
        _validate_whole(
            replace(
                form,
                productions=(
                    replace(first, occurrences=first.occurrences + first.occurrences[:1]),
                    *rest,
                ),
            )
        )
    with pytest.raises(ValueError, match="disagrees"):
        _validate_whole(replace(form, productions=(replace(first, source="wrong-source"), *rest)))


def test_source_reuse_is_not_silently_inferred_from_port_labels():
    form = _fixture()
    shared = tuple(replace(p, source="undeclared-shared-source") for p in form.ports)
    with pytest.raises(ValueError, match="disagrees"):
        _validate_whole(replace(form, ports=shared))
    with pytest.raises(ValueError, match="exactly once"):
        _validate_whole(replace(form, productions=()))


def test_empty_extra_and_split_source_entries_are_rejected():
    form = _allocated((0, 0, 0, 0, 0, 0))
    entry = form.productions[0]
    with pytest.raises(ValueError, match="at least one"):
        _validate_whole(replace(form, productions=(replace(entry, occurrences=()),)))
    with pytest.raises(ValueError, match="unknown occurrence"):
        _validate_whole(
            replace(
                form, productions=(replace(entry, occurrences=(*entry.occurrences, "foreign")),)
            )
        )
    split = (
        replace(entry, occurrences=entry.occurrences[:3]),
        replace(entry, occurrences=entry.occurrences[3:]),
    )
    with pytest.raises(ValueError, match="per source"):
        _validate_whole(replace(form, productions=split))


def test_one_source_cannot_acquire_two_value_types():
    form = _allocated((0, 0, 0, 0, 0, 0))
    ports = (replace(form.ports[0], value_type="B"), *form.ports[1:])
    with pytest.raises(ValueError, match="one value type"):
        _validate_whole(replace(form, ports=ports))


def test_fresh_names_reuse_the_rule_and_keep_the_bridge_open():
    from test_bootstrap_zero_whole_cut_m6_bridge import _bridge_whole_cut6_to_m6

    form = _allocated((0, 1, 0, 2, 1, 2), prefix="fresh")
    rename = {p.occurrence: f"fresh-{p.occurrence}" for p in form.ports}
    form = replace(
        form,
        ports=tuple(replace(p, occurrence=rename[p.occurrence]) for p in form.ports),
        productions=tuple(
            replace(p, occurrences=tuple(rename[o] for o in p.occurrences))
            for p in form.productions
        ),
    )
    _validate_whole(form)
    bridge = _bridge_whole_cut6_to_m6(form)
    assert bridge.carrier.fillers == ()
    assert {s.occurrence for s in bridge.carrier.states} == set(rename.values())


def test_accepted_production_order_remains_a_raw_distinction():
    form = _allocated((0, 0, 0, 0, 0, 0))
    entry = form.productions[0]
    other = replace(form, productions=(replace(entry, occurrences=entry.occurrences[::-1]),))
    _validate_whole(form)
    _validate_whole(other)
    assert form != other


@pytest.mark.parametrize(
    "source,occurrences", [("", ("o",)), (False, ("o",)), ("s", ("",)), ("s", (False,))]
)
def test_production_names_have_the_declared_string_type(source, occurrences):
    form = _fixture()
    with pytest.raises(ValueError, match="nonempty name"):
        _validate_whole(replace(form, productions=(Production(source, occurrences),)))
