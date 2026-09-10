from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product

import pytest
from test_bootstrap_zero_whole_cut_grammar import (
    Alternative,
    AlternativeDecl,
    Atom,
    Boundary,
    Collision,
    Expansion,
    ExtensionDecl,
    ExtensionSlot,
    Fibre,
    FibreAccount,
    FibrePoint,
    Generate,
    Retract,
    WholeCut6,
    _circle_view,
    _factor_traversal,
    _fixture,
    _validate_collision,
    _validate_extension,
    _validate_retraction,
    _validate_whole,
)


@dataclass(frozen=True)
class ChoiceWitness:
    name: str
    source: WholeCut6
    hole: str
    selected: Alternative
    retained: tuple[AlternativeDecl, ...]


def _validate_choice(expected: WholeCut6, choice: ChoiceWitness) -> None:
    """Expected is supplied by the caller, not recovered from the request."""
    _validate_whole(expected)
    if not isinstance(choice.name, str) or not choice.name:
        raise ValueError("selection needs a named witness")
    if choice.source != expected or choice.retained != expected.alternatives:
        raise ValueError("selection must retain the complete expected source and alternatives")
    entries = {entry.hole: entry for entry in expected.alternatives}
    if choice.hole not in entries or choice.selected not in entries[choice.hole].alternatives:
        raise ValueError("selected alternative must belong to this hole with unchanged payload")


@dataclass(frozen=True)
class RetainedSyntax:
    whole: WholeCut6
    retractions: tuple[Retract, ...]
    collisions: tuple[Collision, ...]
    extensions: tuple[ExtensionDecl, ...]


@dataclass(frozen=True)
class InterpreterDeclaration:
    name: str
    target: str
    source: RetainedSyntax


SIGNATURES = (
    ("I_K", "View_K"),
    ("I_X", "View_X"),
    ("I_t", "View_t"),
    ("I_thread", "ThreadMachineForm"),
    ("I_AM", "AMForm"),
)


def _validate_declarations(expected: RetainedSyntax, declarations) -> None:
    _validate_whole(expected.whole)
    for retract in expected.retractions:
        _validate_retraction(retract)
    ports = {p.name: p for p in expected.whole.ports}
    for collision in expected.collisions:
        _validate_collision(collision)
        if any(member != ports.get(member.name) for member in collision.members):
            raise ValueError("collision member must retain the source port payload")
    for extension in expected.extensions:
        _validate_extension(extension)
    if tuple((d.name, d.target) for d in declarations) != SIGNATURES:
        raise ValueError("exactly five ordered interpreter signatures are required")
    if any(d.source != expected for d in declarations):
        raise ValueError("interpreter declaration must retain the complete expected source")


def _retraction(images=(0, 1, 2, 0, 1, 2), prefix="r"):
    domain = tuple(FibrePoint(f"{prefix}-point-{i}", "Expanded") for i in range(6))
    codomain = tuple(FibrePoint(f"{prefix}-base-{i}", "Boundary") for i in range(3))
    account = FibreAccount(
        f"{prefix}-expansion",
        f"{prefix}-boundary",
        domain,
        codomain,
        tuple(
            (point.name, codomain[target].name)
            for point, target in zip(domain, images, strict=True)
        ),
        tuple(
            Fibre(target, tuple(domain[i] for i, image in enumerate(images) if image == j))
            for j, target in enumerate(codomain)
        ),
    )
    return Retract(
        prefix,
        Expansion(account.expansion),
        Boundary(account.boundary),
        (f"{prefix}-residual",),
        account,
    )


def _packet(prefix="r"):
    whole = _fixture(open_last=True)
    return RetainedSyntax(
        whole,
        (_retraction(prefix=prefix),),
        (Collision("collision", "locus", whole.ports[:2], 2),),
        (
            ExtensionDecl(
                "future",
                ExtensionSlot.INTERPRETER,
                ("WholeCut6",),
                ("Future",),
                ("ledger",),
                ("missing-ledger",),
            ),
        ),
    )


def _declarations(packet):
    return tuple(InterpreterDeclaration(name, target, packet) for name, target in SIGNATURES)


def test_open_holes_cannot_alias_or_disappear():
    whole = _fixture(open_last=True)
    first, second = whole.open_ports
    with pytest.raises(ValueError, match="distinct hole"):
        _validate_whole(replace(whole, open_ports=(first, replace(second, hole=first.hole))))
    with pytest.raises(ValueError, match="hole declarations"):
        _validate_whole(replace(whole, holes=whole.holes[:1]))
    with pytest.raises(ValueError, match="port and type"):
        _validate_whole(
            replace(whole, holes=(replace(whole.holes[0], value_type="Wrong"), whole.holes[1]))
        )
    # A newly declared open carrier need not already have candidate options.
    _validate_whole(replace(whole, alternatives=()))
    with pytest.raises(ValueError, match="alternative declarations"):
        _validate_whole(
            replace(whole, alternatives=(replace(whole.alternatives[0], hole="foreign"),))
        )


def test_unexplored_hole_remains_open_without_claiming_no_solution():
    original = _fixture(open_last=True)
    whole = replace(original, alternatives=())
    _validate_whole(whole)
    option = original.alternatives[0].alternatives[0]
    request = ChoiceWitness("unsupported-choice", whole, whole.holes[0].name, option, ())
    with pytest.raises(ValueError, match="must belong"):
        _validate_choice(whole, request)
    with pytest.raises(ValueError, match="closed alternating"):
        _circle_view(whole)


def test_alternative_ledger_refuses_duplicate_empty_and_wrong_type():
    whole = _fixture(open_last=True)
    first, second = whole.alternatives
    for options, pattern in (
        ((), "nonempty options"),
        ((first.alternatives[0],) * 2, "nonempty options"),
        ((replace(first.alternatives[0], value_type="Wrong"),), "type disagrees"),
    ):
        with pytest.raises(ValueError, match=pattern):
            _validate_whole(
                replace(whole, alternatives=(replace(first, alternatives=options), second))
            )


@pytest.mark.parametrize("hole_index,option_index", tuple(product(range(2), range(2))))
def test_choice_retains_both_holes_and_every_alternative(hole_index, option_index):
    whole = _fixture(open_last=True)
    entry = whole.alternatives[hole_index]
    choice = ChoiceWitness(
        "choose", whole, entry.hole, entry.alternatives[option_index], whole.alternatives
    )
    _validate_choice(whole, choice)
    with pytest.raises(ValueError, match="complete expected"):
        _validate_choice(whole, replace(choice, retained=whole.alternatives[:1]))
    changed = tuple(
        replace(e, alternatives=(choice.selected,)) if e.hole == entry.hole else e
        for e in whole.alternatives
    )
    with pytest.raises(ValueError, match="complete expected"):
        _validate_choice(
            whole, replace(choice, source=replace(whole, alternatives=changed), retained=changed)
        )
    with pytest.raises(ValueError, match="unchanged payload"):
        _validate_choice(
            whole, replace(choice, selected=replace(choice.selected, form=Atom("changed")))
        )
    with pytest.raises(ValueError, match="named witness"):
        _validate_choice(whole, replace(choice, name=""))
    # A selection declaration supplies no missing through edge.
    with pytest.raises(ValueError, match="closed alternating"):
        _circle_view(choice.source)


@pytest.mark.parametrize("images", tuple(product(range(3), repeat=6)))
def test_all_729_retraction_maps_have_checked_complete_fibres(images):
    retract = _retraction(images)
    _validate_retraction(retract)
    # Independent readout: each declared domain point occurs in the fibre
    # indexed by the input image tuple, including retained empty fibres.
    for i, point in enumerate(retract.account.domain):
        assert [j for j, f in enumerate(retract.account.fibres) if point in f.members] == [
            images[i]
        ]
    assert len(retract.account.fibres) == 3
    occupied = next(i for i, f in enumerate(retract.account.fibres) if f.members)
    fibres = list(retract.account.fibres)
    fibres[occupied] = replace(fibres[occupied], members=fibres[occupied].members[1:])
    bad = replace(retract, account=replace(retract.account, fibres=tuple(fibres)))
    with pytest.raises(ValueError, match="members disagree"):
        _validate_retraction(bad)
    with pytest.raises(ValueError, match="each domain point once"):
        _validate_retraction(
            replace(retract, account=replace(retract.account, images=retract.account.images[:-1]))
        )


def test_empty_fibres_foreign_targets_and_duplicate_assignments_are_not_silent():
    retract = _retraction((0,) * 6)
    account = retract.account
    assert [len(f.members) for f in account.fibres] == [6, 0, 0]
    _validate_retraction(retract)
    with pytest.raises(ValueError, match="including empty fibres"):
        _validate_retraction(replace(retract, account=replace(account, fibres=account.fibres[:1])))
    with pytest.raises(ValueError, match="each domain point once"):
        _validate_retraction(
            replace(retract, account=replace(account, images=(*account.images, account.images[0])))
        )
    with pytest.raises(ValueError, match="outside the codomain"):
        _validate_retraction(
            replace(
                retract,
                account=replace(
                    account, images=((account.domain[0].name, "foreign"), *account.images[1:])
                ),
            )
        )
    with pytest.raises(ValueError, match="retraction boundary"):
        _validate_retraction(replace(retract, account=replace(account, expansion="foreign")))
    fibres = (
        replace(
            account.fibres[0],
            members=(replace(account.domain[0], value_type="Wrong"), *account.domain[1:]),
        ),
        *account.fibres[1:],
    )
    with pytest.raises(ValueError, match="members disagree"):
        _validate_retraction(replace(retract, account=replace(account, fibres=fibres)))


def test_traversal_rechecks_the_fibre_account():
    retract = _retraction()
    generate = Generate("g", retract.target, Expansion("next"))
    traversal = _factor_traversal("T", retract, generate)
    assert traversal.retract.account == retract.account
    with pytest.raises(ValueError, match="including empty fibres"):
        _factor_traversal(
            "T", replace(retract, account=replace(retract.account, fibres=())), generate
        )


@pytest.mark.parametrize("index", range(5))
def test_each_interpreter_declaration_is_bound_to_external_expected_source(index):
    packet = _packet()
    declarations = _declarations(packet)
    _validate_declarations(packet, declarations)
    mutations = (
        replace(packet, whole=replace(packet.whole, alternatives=())),
        replace(packet, whole=replace(packet.whole, residuals=())),
        replace(packet, retractions=()),
        replace(packet, collisions=()),
        replace(packet, extensions=()),
    )
    for changed in mutations:
        forged = list(declarations)
        forged[index] = replace(forged[index], source=changed)
        with pytest.raises(ValueError, match="complete expected source"):
            _validate_declarations(packet, tuple(forged))


def test_interpreter_family_refuses_missing_duplicate_wrong_target_and_wrong_source():
    packet = _packet()
    declarations = _declarations(packet)
    for changed in (
        declarations[:-1],
        (declarations[0],) * 5,
        (replace(declarations[0], target="Wrong"), *declarations[1:]),
    ):
        with pytest.raises(ValueError, match="five ordered"):
            _validate_declarations(packet, changed)
    fresh = _packet(prefix="fresh")
    _validate_declarations(fresh, _declarations(fresh))
    with pytest.raises(ValueError, match="complete expected source"):
        _validate_declarations(packet, _declarations(fresh))


def test_fresh_hole_choice_reuses_contract_without_inheriting_old_acceptance():
    whole = _fixture(open_last=True)
    names = {h.name: f"fresh-{h.name}" for h in whole.holes}
    fresh = replace(
        whole,
        open_ports=tuple(replace(p, hole=names[p.hole]) for p in whole.open_ports),
        holes=tuple(replace(h, name=names[h.name]) for h in whole.holes),
        alternatives=tuple(replace(e, hole=names[e.hole]) for e in whole.alternatives),
    )
    entry = fresh.alternatives[0]
    choice = ChoiceWitness(
        "fresh-choice", fresh, entry.hole, entry.alternatives[1], fresh.alternatives
    )
    _validate_choice(fresh, choice)
    with pytest.raises(ValueError, match="complete expected"):
        _validate_choice(whole, choice)
