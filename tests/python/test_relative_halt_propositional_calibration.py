from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Literal, TypeAlias


Domain: TypeAlias = Literal["K", "X", "t"]
Face: TypeAlias = frozenset[Domain]
Proposition: TypeAlias = frozenset[Face]

DOMAINS: tuple[Domain, ...] = ("K", "X", "t")


def _nonempty_faces() -> frozenset[Face]:
    return frozenset(
        frozenset(face)
        for size in range(1, len(DOMAINS) + 1)
        for face in combinations(DOMAINS, size)
    )


HALT_WORLDS = _nonempty_faces()


@dataclass(frozen=True)
class RelativeMachineView:
    stable: Face
    quiescent: bool
    residual: tuple[str, ...] = ()


def _exact_halt(machine: RelativeMachineView) -> Face | None:
    if not machine.stable or not machine.quiescent:
        return None
    return machine.stable


def _atomic_support(domain: Domain) -> Proposition:
    return frozenset(face for face in HALT_WORLDS if domain in face)


def _sat_request(requested: Face) -> Proposition:
    if not requested:
        raise ValueError("a face request must be nonempty")
    return frozenset(face for face in HALT_WORLDS if requested <= face)


def _boolean_closure(generators: set[Proposition]) -> set[Proposition]:
    universe = HALT_WORLDS
    closure = {frozenset(), universe, *generators}
    changed = True
    while changed:
        before = len(closure)
        current = tuple(closure)
        closure.update(universe - proposition for proposition in current)
        closure.update(left & right for left in current for right in current)
        closure.update(left | right for left in current for right in current)
        changed = len(closure) != before
    return closure


def test_exact_relative_halt_has_seven_quiescent_worlds() -> None:
    assert len(HALT_WORLDS) == 7
    assert frozenset() not in HALT_WORLDS

    quiescent = {
        _exact_halt(RelativeMachineView(face, quiescent=True))
        for face in HALT_WORLDS
    }
    active = {
        _exact_halt(
            RelativeMachineView(
                face,
                quiescent=False,
                residual=("enabled:inject",),
            )
        )
        for face in HALT_WORLDS
    }

    assert quiescent == set(HALT_WORLDS)
    assert active == {None}


def test_three_face_atoms_generate_all_128_extensional_propositions() -> None:
    atoms = {_atomic_support(domain) for domain in DOMAINS}
    closure = _boolean_closure(atoms)

    assert len(atoms) == 3
    assert len(closure) == 2 ** len(HALT_WORLDS) == 128

    for face in HALT_WORLDS:
        singleton = HALT_WORLDS
        for domain in DOMAINS:
            atom = _atomic_support(domain)
            singleton &= atom if domain in face else HALT_WORLDS - atom
        assert singleton == frozenset({face})


def test_positive_face_requests_have_conjunction_but_not_closed_disjunction() -> None:
    for left in HALT_WORLDS:
        for right in HALT_WORLDS:
            assert _sat_request(left) & _sat_request(right) == _sat_request(
                left | right
            )

    construction_or_space = _sat_request(frozenset({"K"})) | _sat_request(
        frozenset({"X"})
    )
    assert construction_or_space not in {
        _sat_request(face) for face in HALT_WORLDS
    }


def test_seven_faces_are_not_a_closed_scalar_truth_algebra() -> None:
    construction = frozenset({"K"})
    space = frozenset({"X"})

    assert construction in HALT_WORLDS
    assert space in HALT_WORLDS
    assert construction & space == frozenset()
    assert construction & space not in HALT_WORLDS

    # Empty visible stability is not silently promoted to an execution result.
    assert _exact_halt(RelativeMachineView(frozenset(), quiescent=True)) is None
