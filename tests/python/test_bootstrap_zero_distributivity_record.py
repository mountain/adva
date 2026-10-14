"""One source-bound, syntax-only distributivity formation calibration."""

from __future__ import annotations

from dataclasses import replace

import pytest
from test_bootstrap_zero_whole_cut_grammar import (
    Alternative,
    AlternativeDecl,
    Atom,
    Crossing,
    DistributivityRecord,
    Hole,
    HoleBinding,
    HoleDecl,
    OpenPort,
    Plus,
    PolarDual,
    Production,
    Tensor,
    ThreadStep,
    Use,
    _circle_view,
    _fixture,
    _validate_am,
    _validate_distributivity,
    _validate_whole,
)


def _distributivity_fixture(prefix=""):
    original = _fixture()
    # A's two distinct occurrences are explicitly allocated before a witness
    # is proposed. The record neither creates native IDs nor supplies a copy.
    ports = tuple(
        replace(port, source=f"{prefix}s-A" if i in (2, 4) else f"{prefix}{port.source}")
        for i, port in enumerate(original.ports)
    )
    allocation = {}
    for port in ports:
        allocation.setdefault(port.source, []).append(port.occurrence)
    productions = tuple(Production(source, tuple(names)) for source, names in allocation.items())
    open_indices = ((2, "A"), (5, "B"), (1, "C"), (4, "A-repeat"))
    open_ports = tuple(
        OpenPort(ports[i].name, f"{prefix}h-{label}", f"{prefix}r-{label}")
        for i, label in open_indices
    )
    holes = tuple(
        HoleDecl(item.hole, ports[i].value_type, item.port)
        for (i, _), item in zip(open_indices, open_ports, strict=True)
    )
    whole = replace(
        original,
        name=f"{prefix}whole-distributivity",
        ports=ports,
        productions=productions,
        channels=(
            replace(
                original.channels[0],
                name=f"{prefix}thread-1",
                thread=(
                    ThreadStep(f"{prefix}crossing-1", 1, Crossing.OVER),
                    ThreadStep(f"{prefix}crossing-2", 4, Crossing.UNDER),
                ),
            ),
        ),
        open_ports=open_ports,
        holes=holes,
        alternatives=tuple(
            AlternativeDecl(hole.name, (Alternative(f"{hole.name}-option", "A", Atom("body")),))
            for hole in holes
        ),
        residuals=tuple(item.residual for item in open_ports),
    )
    boundary = holes[:3]
    a, b, c = (Hole(h.name, h.value_type) for h in boundary)
    first_a, use_b, use_c, second_a = (
        Use(ports[i].source, ports[i].occurrence, ports[i].value_type) for i, _ in open_indices
    )
    witness = DistributivityRecord(
        f"{prefix}distribute",
        whole,
        boundary,
        Tensor(a, Plus(b, c)),
        Plus(Tensor(a, b), Tensor(a, c)),
        productions,
        (
            HoleBinding("source", (0,), a, first_a),
            HoleBinding("source", (1, 0), b, use_b),
            HoleBinding("source", (1, 1), c, use_c),
            HoleBinding("target", (0, 0), a, first_a),
            HoleBinding("target", (0, 1), b, use_b),
            HoleBinding("target", (1, 0), a, second_a),
            HoleBinding("target", (1, 1), c, use_c),
        ),
        whole.channels,
        whole.residuals,
    )
    return whole, boundary, witness


def test_source_bound_distributivity_retains_raw_accounting_and_open_data():
    whole, boundary, witness = _distributivity_fixture()
    _validate_distributivity(whole, boundary, witness)

    source_uses = tuple(entry.use for entry in witness.hole_bindings[:3])
    target_uses = tuple(entry.use for entry in witness.hole_bindings[3:])
    assert len({use.occurrence for use in source_uses}) == 3
    assert len({use.occurrence for use in target_uses}) == 4
    assert target_uses[0].source == target_uses[2].source
    assert target_uses[0].occurrence != target_uses[2].occurrence
    allocation = {production.source: production.occurrences for production in witness.productions}
    assert set(allocation[target_uses[0].source]) == {
        target_uses[0].occurrence,
        target_uses[2].occurrence,
    }
    assert sum(map(len, allocation.values())) == len(whole.ports) == 6
    assert len(whole.holes) == len(whole.residuals) == 4
    assert witness.source.holes[-1].name not in {h.name for h in boundary}
    assert witness.thread_ledger == whole.channels
    assert tuple(step.gap for step in witness.thread_ledger[0].thread) == (1, 4)
    assert tuple(step.crossing for step in witness.thread_ledger[0].thread) == (
        Crossing.OVER,
        Crossing.UNDER,
    )
    assert witness.source.alternatives == whole.alternatives
    with pytest.raises(ValueError, match="closed alternating"):
        _circle_view(witness.source)


@pytest.mark.parametrize("omitted", range(7))
def test_every_missing_expression_position_binding_is_rejected(omitted):
    whole, boundary, witness = _distributivity_fixture()
    shortened = witness.hole_bindings[:omitted] + witness.hole_bindings[omitted + 1 :]
    with pytest.raises(ValueError, match="all seven hole positions"):
        _validate_distributivity(whole, boundary, replace(witness, hole_bindings=shortened))


def test_repeated_a_cannot_reuse_the_first_occurrence_or_invent_an_unallocated_one():
    whole, boundary, witness = _distributivity_fixture()
    repeated = witness.hole_bindings[5]
    for use, reason in (
        (witness.hole_bindings[0].use, "fresh explicitly allocated"),
        (replace(repeated.use, occurrence="undeclared-A-copy"), "declared occurrence"),
        (replace(repeated.use, source="different-source"), "declared occurrence"),
    ):
        bindings = list(witness.hole_bindings)
        bindings[5] = replace(repeated, use=use)
        with pytest.raises(ValueError, match=reason):
            _validate_distributivity(
                whole, boundary, replace(witness, hole_bindings=tuple(bindings))
            )


def test_repeated_a_allocation_cannot_be_removed_or_reordered_in_the_record():
    whole, boundary, witness = _distributivity_fixture()
    production = next(p for p in whole.productions if len(p.occurrences) == 2)
    changed = tuple(
        replace(p, occurrences=p.occurrences[:1]) if p == production else p
        for p in whole.productions
    )
    for ledger in ((), changed, whole.productions[::-1]):
        with pytest.raises(ValueError, match="complete ordered production"):
            _validate_distributivity(whole, boundary, replace(witness, productions=ledger))
    invalid_source = replace(whole, productions=changed)
    with pytest.raises(ValueError, match="each occurrence exactly once"):
        _validate_distributivity(invalid_source, boundary, replace(witness, source=invalid_source))


def test_candidate_cannot_replace_source_alternatives_holes_or_residuals():
    whole, boundary, witness = _distributivity_fixture()
    for changed in (
        replace(whole, name="replacement-source"),
        replace(whole, alternatives=()),
        replace(whole, holes=whole.holes[:3]),
        replace(whole, residuals=()),
    ):
        with pytest.raises(ValueError, match="independently supplied source"):
            _validate_distributivity(whole, boundary, replace(witness, source=changed))


def test_lost_or_changed_thread_and_residual_data_are_rejected():
    whole, boundary, witness = _distributivity_fixture()
    for threads in (
        (),
        (replace(whole.channels[0], name="replaced-thread"),),
        (replace(whole.channels[0], thread=()),),
        (replace(whole.channels[0], thread=whole.channels[0].thread[::-1]),),
    ):
        with pytest.raises(ValueError, match="complete source thread"):
            _validate_distributivity(whole, boundary, replace(witness, thread_ledger=threads))
    for residuals in ((), whole.residuals[:-1], whole.residuals[::-1]):
        with pytest.raises(ValueError, match="every ordered source residual"):
            _validate_distributivity(whole, boundary, replace(witness, residuals=residuals))


def test_ordered_expression_shapes_boundary_and_binding_payloads_cannot_drift():
    whole, boundary, witness = _distributivity_fixture()
    a, b, c = (Hole(h.name, h.value_type) for h in boundary)
    with pytest.raises(ValueError, match="both ordered expression shapes"):
        _validate_distributivity(
            whole, boundary, replace(witness, target_expression=Plus(Tensor(a, c), Tensor(a, b)))
        )
    with pytest.raises(ValueError, match="independently supplied source and boundary"):
        _validate_distributivity(whole, boundary[::-1], witness)
    bad_bindings = list(witness.hole_bindings)
    bad_bindings[1], bad_bindings[2] = bad_bindings[2], bad_bindings[1]
    with pytest.raises(ValueError, match="all seven hole positions"):
        _validate_distributivity(
            whole, boundary, replace(witness, hole_bindings=tuple(bad_bindings))
        )
    bad_bindings = list(witness.hole_bindings)
    bad_bindings[4] = replace(bad_bindings[4], use=witness.hole_bindings[2].use)
    with pytest.raises(ValueError, match="unchanged ordered B and C"):
        _validate_distributivity(
            whole, boundary, replace(witness, hole_bindings=tuple(bad_bindings))
        )


def test_new_source_is_rechecked_against_its_own_independent_boundary():
    original, boundary, witness = _distributivity_fixture()
    fresh, fresh_boundary, fresh_witness = _distributivity_fixture("fresh-")
    _validate_distributivity(fresh, fresh_boundary, fresh_witness)
    with pytest.raises(ValueError, match="independently supplied source"):
        _validate_distributivity(original, boundary, fresh_witness)
    with pytest.raises(ValueError, match="named formation record"):
        _validate_distributivity(original, boundary, replace(witness, name=""))


@pytest.mark.parametrize("position", ((False,), (0.0,), [0]))
def test_binding_positions_cannot_coerce_boolean_float_or_list_coordinates(position):
    whole, boundary, witness = _distributivity_fixture()
    bindings = (replace(witness.hole_bindings[0], position=position), *witness.hole_bindings[1:])
    with pytest.raises(ValueError, match="exact integer coordinates"):
        _validate_distributivity(whole, boundary, replace(witness, hole_bindings=bindings))


@pytest.mark.parametrize("probe", ("empty-name", "invalid-motion", "nested-object"))
def test_previous_whole_cut_formation_holes_are_now_rejected(probe):
    whole = _fixture(open_last=True)
    if probe == "empty-name":
        malformed = replace(whole, name="")
        reason = "nonempty carrier name"
    elif probe == "invalid-motion":
        channels = (replace(whole.channels[0], motion="invalid"), *whole.channels[1:])
        malformed = replace(whole, channels=channels)
        reason = "Motion alphabet"
    else:
        entry = whole.alternatives[0]
        options = (replace(entry.alternatives[0], form=Plus(object(), Atom("B"))),)
        malformed = replace(
            whole, alternatives=(replace(entry, alternatives=options), *whole.alternatives[1:])
        )
        reason = "recursive position"
    with pytest.raises(ValueError, match=reason):
        _validate_whole(malformed)


def test_recursive_am_holes_and_uses_are_checked_against_the_source():
    whole, boundary, witness = _distributivity_fixture()
    term = Plus(Hole(boundary[1].name, boundary[1].value_type), witness.hole_bindings[0].use)
    entry = whole.alternatives[0]
    alternatives = (replace(entry, alternatives=(replace(entry.alternatives[0], form=term),)),)
    _validate_whole(replace(whole, alternatives=alternatives))
    for malformed, reason in (
        (Tensor(Atom("A"), object()), "recursive position"),
        (Hole("foreign-hole", "A"), "declared hole name and type"),
        (Hole(boundary[0].name, "Wrong"), "declared hole name and type"),
        (replace(witness.hole_bindings[0].use, value_type="Wrong"), "declared occurrence"),
        (Plus(witness.hole_bindings[0].use, witness.hole_bindings[0].use), "must not be reused"),
        (Atom(""), "nonempty names"),
    ):
        with pytest.raises(ValueError, match=reason):
            _validate_am(malformed, whole)


def test_recursive_am_validation_has_an_explicit_finite_budget():
    whole = _fixture()
    deep = Atom("A")
    for _ in range(33):
        deep = PolarDual(deep)
    wide = Atom("A")
    for _ in range(8):
        wide = Plus(wide, wide)
    for term in (deep, wide):
        with pytest.raises(ValueError, match="256-node / 32-depth budget"):
            _validate_am(term, whole)


@pytest.mark.parametrize("malformation", ("name", "gap", "crossing", "duplicate", "budget"))
def test_raw_thread_word_alphabet_occurrences_and_budget_are_checked(malformation):
    whole, boundary, witness = _distributivity_fixture()
    channel = whole.channels[0]
    step = channel.thread[0]
    words = {
        "name": ((replace(step, name=""),), "nonempty names"),
        "gap": ((replace(step, gap=6),), "adjacent ports"),
        "crossing": ((replace(step, crossing="+"),), "Crossing alphabet"),
        "duplicate": ((step, step), "distinct within the raw word"),
        "budget": ((step,) * 257, "256-step finite budget"),
    }
    word, reason = words[malformation]
    invalid = replace(whole, channels=(replace(channel, thread=word),))
    with pytest.raises(ValueError, match=reason):
        _validate_distributivity(invalid, boundary, replace(witness, source=invalid))
