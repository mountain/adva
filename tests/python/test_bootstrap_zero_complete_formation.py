"""Complete the finite AM constructor and WholeCut6 name-formation boundary."""

from dataclasses import replace

import pytest
from test_bootstrap_zero_distributivity_record import _distributivity_fixture
from test_bootstrap_zero_whole_cut_grammar import (
    Atom,
    BalancedZero,
    HistoryComposition,
    Plus,
    PolarDual,
    Tensor,
    _fixture,
    _validate_am,
    _validate_whole,
)


def test_history_composition_and_balanced_zero_complete_the_finite_am_grammar():
    whole, _, witness = _distributivity_fixture()
    left = witness.hole_bindings[0].use
    right = witness.hole_bindings[1].use
    term = HistoryComposition(
        Tensor(left, Atom("context")),
        BalancedZero(right, PolarDual(right)),
    )

    _validate_am(term, whole)
    assert HistoryComposition(left, right) != HistoryComposition(right, left)
    assert BalancedZero(right, PolarDual(right)) != Plus(right, PolarDual(right))


def test_complete_grammar_reuses_on_a_fresh_source_without_cross_source_aliasing():
    original, _, original_witness = _distributivity_fixture()
    fresh, _, fresh_witness = _distributivity_fixture("formation-fresh-")
    original_use = original_witness.hole_bindings[0].use
    fresh_use = fresh_witness.hole_bindings[0].use

    _validate_am(BalancedZero(fresh_use, PolarDual(fresh_use)), fresh)
    with pytest.raises(ValueError, match="declared occurrence"):
        _validate_am(HistoryComposition(fresh_use, original_use), fresh)
    with pytest.raises(ValueError, match="declared occurrence"):
        _validate_am(HistoryComposition(original_use, fresh_use), original)


@pytest.mark.parametrize(
    ("malformed", "reason"),
    (
        (BalancedZero(Atom("A"), PolarDual(Atom("B"))), "exact PolarDual view"),
        (BalancedZero(Atom("A"), object()), "exact PolarDual view"),
        (HistoryComposition(Atom("A"), object()), "recursive position"),
        (HistoryComposition(object(), Atom("B")), "recursive position"),
    ),
)
def test_new_constructors_reject_mismatched_or_unformed_children(malformed, reason):
    with pytest.raises(ValueError, match=reason):
        _validate_am(malformed, _fixture())


@pytest.mark.parametrize(
    "mutation",
    (
        "cell-name",
        "port-name",
        "port-type",
        "channel-name",
        "open-residual",
        "residual-extra",
        "residual-order",
        "hole-type",
        "alternative-type",
    ),
)
def test_all_current_whole_cut_name_and_type_boundaries_are_explicit(mutation):
    whole = _fixture(open_last=True)
    if mutation == "cell-name":
        malformed = replace(whole, cells=(replace(whole.cells[0], name=""), *whole.cells[1:]))
    elif mutation == "port-name":
        malformed = replace(whole, ports=(replace(whole.ports[0], name=""), *whole.ports[1:]))
    elif mutation == "port-type":
        malformed = replace(whole, ports=(replace(whole.ports[0], value_type=""), *whole.ports[1:]))
    elif mutation == "channel-name":
        malformed = replace(
            whole, channels=(replace(whole.channels[0], name=""), *whole.channels[1:])
        )
    elif mutation == "open-residual":
        malformed = replace(
            whole,
            open_ports=(replace(whole.open_ports[0], residual=""), *whole.open_ports[1:]),
            residuals=("", *whole.residuals[1:]),
        )
    elif mutation == "residual-extra":
        malformed = replace(whole, residuals=(*whole.residuals, "unbound-residual"))
    elif mutation == "residual-order":
        malformed = replace(whole, residuals=whole.residuals[::-1])
    elif mutation == "hole-type":
        malformed = replace(whole, holes=(replace(whole.holes[0], value_type=""), *whole.holes[1:]))
    else:
        entry = whole.alternatives[0]
        options = (replace(entry.alternatives[0], value_type=""), *entry.alternatives[1:])
        malformed = replace(
            whole, alternatives=(replace(entry, alternatives=options), *whole.alternatives[1:])
        )

    with pytest.raises(ValueError):
        _validate_whole(malformed)
