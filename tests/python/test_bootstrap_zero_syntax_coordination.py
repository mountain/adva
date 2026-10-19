"""Finite constructor-by-constructor AM syntax coordination calibration."""

from dataclasses import dataclass, replace
from itertools import product

import pytest
from test_bootstrap_zero_distributivity_record import _distributivity_fixture
from test_bootstrap_zero_whole_cut_grammar import (
    Atom,
    BalancedZero,
    EmptyZero,
    HistoryComposition,
    Hole,
    Plus,
    PolarDual,
    Tensor,
    Use,
    _validate_am,
    _validate_whole,
)


@dataclass(frozen=True)
class SyntaxCoordinationProjection:
    whole: str
    constructor_word: tuple[tuple[str, ...], ...]
    holes: tuple[tuple[str, str], ...]
    uses: tuple[tuple[str, str, str], ...]
    occurrence_ledger: tuple[tuple[str, str, str, int], ...]
    production_ledger: tuple[tuple[str, tuple[str, ...]], ...]
    residuals: tuple[str, ...]
    balanced_views: int
    history_compositions: int


def _coordinate_am(term, whole):
    """Project accepted syntax only; do not evaluate or identify terms."""
    _validate_whole(whole)
    _validate_am(term, whole)

    word = []
    holes = []
    uses = []
    balanced_views = 0
    history_compositions = 0
    pending = [("visit", term)]
    visited = 0
    while pending:
        action, item = pending.pop()
        if action == "token":
            word.append(item)
            continue

        visited += 1
        if visited > 256:
            raise AssertionError("accepted term exceeded its formation budget")
        if type(item) is Atom:
            word.append(("Atom", item.name))
        elif type(item) is EmptyZero:
            word.append(("EmptyZero", item.name))
        elif type(item) is Hole:
            word.append(("Hole", item.name, item.value_type))
            holes.append((item.name, item.value_type))
        elif type(item) is Use:
            word.append(("Use", item.source, item.occurrence, item.value_type))
            uses.append((item.source, item.occurrence, item.value_type))
        elif type(item) is PolarDual:
            pending.extend(
                (
                    ("token", ("close", "PolarDual")),
                    ("visit", item.term),
                    ("token", ("open", "PolarDual")),
                )
            )
        elif type(item) in (Plus, Tensor, HistoryComposition):
            if type(item) is Plus:
                constructor, left, right = "Plus", item.left, item.right
            elif type(item) is Tensor:
                constructor, left, right = "Tensor", item.outer, item.inner
            else:
                constructor, left, right = (
                    "HistoryComposition",
                    item.first,
                    item.second,
                )
                history_compositions += 1
            pending.extend(
                (
                    ("token", ("close", constructor)),
                    ("visit", right),
                    ("token", ("middle", constructor)),
                    ("visit", left),
                    ("token", ("open", constructor)),
                )
            )
        elif type(item) is BalancedZero:
            balanced_views += 1
            pending.extend(
                (
                    ("token", ("close", "BalancedZero")),
                    ("token", ("dual-view", "PolarDual")),
                    ("visit", item.positive),
                    ("token", ("open", "BalancedZero")),
                )
            )
        else:  # pragma: no cover - _validate_am refuses this first.
            raise AssertionError("accepted term used an unknown constructor")

    return SyntaxCoordinationProjection(
        whole=whole.name,
        constructor_word=tuple(word),
        holes=tuple(holes),
        uses=tuple(uses),
        occurrence_ledger=tuple(
            (port.source, port.occurrence, port.value_type, port.multiplicity)
            for port in whole.ports
        ),
        production_ledger=tuple(
            (production.source, production.occurrences) for production in whole.productions
        ),
        residuals=whole.residuals,
        balanced_views=balanced_views,
        history_compositions=history_compositions,
    )


def _constructor_signature(projection):
    return tuple(
        token[:2] if token[0] in {"open", "middle", "close", "dual-view"} else token[:1]
        for token in projection.constructor_word
    )


def _all_constructor_term(whole, boundary, witness):
    use = witness.hole_bindings[0].use
    hole = Hole(boundary[1].name, boundary[1].value_type)
    return HistoryComposition(
        Plus(Atom("context"), EmptyZero("zero-empty")),
        Tensor(
            PolarDual(hole),
            BalancedZero(use, PolarDual(use)),
        ),
    )


def test_all_nine_constructors_have_one_exact_ordered_projection():
    whole, boundary, witness = _distributivity_fixture()
    term = _all_constructor_term(whole, boundary, witness)

    projection = _coordinate_am(term, whole)

    assert projection.holes == ((boundary[1].name, boundary[1].value_type),)
    use = witness.hole_bindings[0].use
    assert projection.uses == ((use.source, use.occurrence, use.value_type),)
    assert projection.balanced_views == projection.history_compositions == 1
    assert ("dual-view", "PolarDual") in projection.constructor_word
    assert projection.residuals == whole.residuals
    assert projection.production_ledger == tuple(
        (production.source, production.occurrences) for production in whole.productions
    )
    assert {entry[:3] for entry in projection.occurrence_ledger} >= set(projection.uses)


def test_fresh_source_reuses_constructor_signature_without_reusing_identity():
    whole, boundary, witness = _distributivity_fixture()
    fresh, fresh_boundary, fresh_witness = _distributivity_fixture("coordination-fresh-")

    original = _coordinate_am(_all_constructor_term(whole, boundary, witness), whole)
    reused = _coordinate_am(
        _all_constructor_term(fresh, fresh_boundary, fresh_witness),
        fresh,
    )

    assert _constructor_signature(original) == _constructor_signature(reused)
    assert original.whole != reused.whole
    assert original.uses != reused.uses
    assert original.occurrence_ledger != reused.occurrence_ledger


def test_constructor_and_history_order_remain_visible():
    whole, _, witness = _distributivity_fixture()
    left = witness.hole_bindings[0].use
    right = Atom("right")

    history = _coordinate_am(HistoryComposition(left, right), whole)
    reversed_history = _coordinate_am(HistoryComposition(right, left), whole)
    plus = _coordinate_am(Plus(left, right), whole)
    tensor = _coordinate_am(Tensor(left, right), whole)

    assert history != reversed_history
    assert len({history.constructor_word, plus.constructor_word, tensor.constructor_word}) == 3


def test_balanced_dual_is_one_use_plus_one_view_marker():
    whole, _, witness = _distributivity_fixture()
    use = witness.hole_bindings[0].use

    projection = _coordinate_am(BalancedZero(use, PolarDual(use)), whole)

    assert projection.uses == ((use.source, use.occurrence, use.value_type),)
    assert projection.balanced_views == 1
    assert projection.constructor_word.count(("dual-view", "PolarDual")) == 1


@pytest.mark.parametrize(
    ("case", "reason"),
    (
        ("cross-source", "declared occurrence"),
        ("duplicate-use", "must not be reused"),
        ("mismatched-dual", "exact PolarDual view"),
        ("residual-ledger", "residual ledger"),
    ),
)
def test_projection_requires_prior_formation_and_exact_source_binding(case, reason):
    whole, _, witness = _distributivity_fixture()
    use = witness.hole_bindings[0].use
    term = Atom("valid")
    if case == "cross-source":
        term = replace(use, source="foreign-source")
    elif case == "duplicate-use":
        term = HistoryComposition(use, use)
    elif case == "mismatched-dual":
        term = BalancedZero(Atom("A"), PolarDual(Atom("B")))
    else:
        whole = replace(whole, residuals=whole.residuals[::-1])

    with pytest.raises(ValueError, match=reason):
        _coordinate_am(term, whole)


def _depth_two_candidates(whole, boundary, witness):
    leaves = (
        Atom("atom"),
        EmptyZero("zero"),
        Hole(boundary[0].name, boundary[0].value_type),
        witness.hole_bindings[0].use,
    )

    def extend(terms):
        return (
            *terms,
            *(PolarDual(term) for term in terms),
            *(BalancedZero(term, PolarDual(term)) for term in terms),
            *(
                constructor(left, right)
                for constructor in (Plus, Tensor, HistoryComposition)
                for left, right in product(terms, repeat=2)
            ),
        )

    level_one = tuple(dict.fromkeys(extend(leaves)))
    return tuple(dict.fromkeys(extend(level_one)))


def test_depth_two_declared_family_has_no_projection_collision():
    whole, boundary, witness = _distributivity_fixture()
    candidates = _depth_two_candidates(whole, boundary, witness)
    assert len(candidates) == 10924

    accepted = {}
    rejected = 0
    for term in candidates:
        try:
            projection = _coordinate_am(term, whole)
        except ValueError:
            rejected += 1
            continue
        previous = accepted.setdefault(projection, term)
        assert previous == term

    assert len(accepted) == 8542
    assert rejected == 2382
