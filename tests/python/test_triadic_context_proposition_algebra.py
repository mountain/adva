from __future__ import annotations

from collections import deque
from itertools import combinations, product
from typing import Any, Callable

import sympy

from adva import link_modules


TRIADIC_CONTEXT_PROGRAMS = r"""
(module triadic-context-programs
  (export open-temporal write-spatial flip-construction)

  (def open-temporal
    (fn ((temporal Real)) Real
      (add 1 (mul 0 (use temporal)))))

  (def write-spatial
    (fn ((temporal Real) (construction Real)) Real
      (mul (use temporal) (use construction))))

  (def flip-construction
    (fn ((construction Real)) Real
      (add 1 (neg (use construction)))))
)
"""


Axis = str
Context = tuple[Axis, ...]
CoreState = tuple[int, int, int]
FineState = tuple[int, int, int, int]
Transformation = tuple[int, ...]
Proposition = frozenset[FineState]

AXES: tuple[Axis, ...] = ("T", "X", "K")
CORE_STATES: tuple[CoreState, ...] = tuple(product((0, 1), repeat=3))
FINE_STATES: tuple[FineState, ...] = tuple(product((0, 1), repeat=4))
CORE_INDEX = {state: index for index, state in enumerate(CORE_STATES)}
IDENTITY: Transformation = tuple(range(len(CORE_STATES)))


def _workspace() -> Any:
    return link_modules([TRIADIC_CONTEXT_PROGRAMS])


def _core_step(state: CoreState, axis: Axis) -> CoreState:
    temporal, spatial, construction = state
    if axis == "T":
        return (1, spatial, construction)
    if axis == "X":
        return (temporal, temporal & construction, construction)
    if axis == "K":
        return (temporal, spatial, 1 - construction)
    raise ValueError(f"unknown axis: {axis}")


def _generator(axis: Axis) -> Transformation:
    return tuple(CORE_INDEX[_core_step(state, axis)] for state in CORE_STATES)


def _compose(
    first: Transformation,
    second: Transformation,
) -> Transformation:
    """Execute ``first`` and then ``second``."""

    return tuple(second[first[index]] for index in range(len(CORE_STATES)))


def _run_context(context: Context) -> Transformation:
    generators = {axis: _generator(axis) for axis in AXES}
    transformation = IDENTITY
    for axis in context:
        transformation = _compose(transformation, generators[axis])
    return transformation


def _transformation_monoid() -> dict[Transformation, Context]:
    """Return the exact closure with one shortest word per transformation."""

    generators = {axis: _generator(axis) for axis in AXES}
    shortest: dict[Transformation, Context] = {IDENTITY: ()}
    frontier = deque([IDENTITY])
    while frontier:
        transformation = frontier.popleft()
        for axis in AXES:
            candidate = _compose(transformation, generators[axis])
            if candidate not in shortest:
                shortest[candidate] = (*shortest[transformation], axis)
                frontier.append(candidate)
    return shortest


def _fine_image(
    transformation: Transformation,
    state: FineState,
) -> FineState:
    temporal, spatial, construction, history = state
    core = (temporal, spatial, construction)
    final_core = CORE_STATES[transformation[CORE_INDEX[core]]]
    return (*final_core, history)


def _spatial_proposition(transformation: Transformation) -> Proposition:
    return frozenset(
        state for state in FINE_STATES if _fine_image(transformation, state)[1] == 1
    )


def _context_generated_propositions() -> dict[Proposition, Context]:
    minimal: dict[Proposition, Context] = {}
    for transformation, context in _transformation_monoid().items():
        proposition = _spatial_proposition(transformation)
        previous = minimal.get(proposition)
        if previous is None or len(context) < len(previous):
            minimal[proposition] = context
    return minimal


def _support(predicate: Callable[[FineState], bool]) -> Proposition:
    return frozenset(state for state in FINE_STATES if predicate(state))


def _contextual_partition(
    propositions: tuple[Proposition, ...],
) -> tuple[frozenset[FineState], ...]:
    fibres: dict[tuple[bool, ...], set[FineState]] = {}
    for state in FINE_STATES:
        signature = tuple(state in proposition for proposition in propositions)
        fibres.setdefault(signature, set()).add(state)
    return tuple(frozenset(fibre) for fibre in fibres.values())


def _boolean_envelope(
    propositions: tuple[Proposition, ...],
) -> frozenset[Proposition]:
    """Compute the Boolean algebra from its exact membership atoms."""

    atoms = _contextual_partition(propositions)
    envelope: set[Proposition] = set()
    for count in range(len(atoms) + 1):
        for selected in combinations(atoms, count):
            envelope.add(frozenset().union(*selected))
    return frozenset(envelope)


def test_rust_checked_programs_realize_the_three_boolean_updates() -> None:
    workspace = _workspace()
    open_temporal = workspace.function(
        "triadic-context-programs",
        "open-temporal",
    )
    write_spatial = workspace.function(
        "triadic-context-programs",
        "write-spatial",
    )
    flip_construction = workspace.function(
        "triadic-context-programs",
        "flip-construction",
    )

    temporal, construction = sympy.symbols("temporal construction", real=True)
    assert sympy.simplify(open_temporal.to_sympy() - 1) == 0
    assert sympy.simplify(
        write_spatial.to_sympy() - temporal * construction
    ) == 0
    assert sympy.simplify(
        flip_construction.to_sympy() - (1 - construction)
    ) == 0

    for bit in (0, 1):
        assert open_temporal.evaluate({"temporal": bit}) == 1
        assert flip_construction.evaluate({"construction": bit}) == 1 - bit
    for temporal_bit, construction_bit in product((0, 1), repeat=2):
        assert write_spatial.evaluate(
            {
                "temporal": temporal_bit,
                "construction": construction_bit,
            }
        ) == temporal_bit & construction_bit


def test_generator_closure_is_an_exact_sixteen_element_monoid() -> None:
    monoid = _transformation_monoid()
    assert len(monoid) == 16
    assert max(map(len, monoid.values())) == 4
    assert set(monoid) == {
        _compose(left, right) for left in monoid for right in monoid
    }

    expected_shortest_words = {
        (),
        ("K",),
        ("T",),
        ("X",),
        ("K", "X"),
        ("T", "K"),
        ("T", "X"),
        ("X", "K"),
        ("X", "T"),
        ("K", "X", "K"),
        ("K", "X", "T"),
        ("T", "K", "X"),
        ("T", "X", "K"),
        ("X", "T", "K"),
        ("K", "X", "T", "K"),
        ("T", "K", "X", "K"),
    }
    assert set(monoid.values()) == expected_shortest_words


def test_exact_program_equations_give_a_partial_ordering_discipline() -> None:
    temporal = _generator("T")
    spatial = _generator("X")
    construction = _generator("K")

    assert _compose(temporal, temporal) == temporal
    assert _compose(spatial, spatial) == spatial
    assert _compose(construction, construction) == IDENTITY

    assert _compose(temporal, construction) == _compose(
        construction,
        temporal,
    )
    assert _compose(temporal, spatial) != _compose(spatial, temporal)
    assert _compose(construction, spatial) != _compose(spatial, construction)

    for left in ((), ("T",), ("K", "X"), ("T", "X", "K")):
        for right in ((), ("X",), ("T", "K"), ("K", "X", "T")):
            assert _run_context((*left, *right)) == _compose(
                _run_context(left),
                _run_context(right),
            )


def test_contexts_generate_exactly_five_direct_spatial_propositions() -> None:
    generated = _context_generated_propositions()
    expected = {
        _support(lambda state: state[1] == 1): (),
        _support(lambda state: state[0] == 1 and state[2] == 1): ("X",),
        _support(lambda state: state[0] == 1 and state[2] == 0): ("K", "X"),
        _support(lambda state: state[2] == 1): ("T", "X"),
        _support(lambda state: state[2] == 0): ("T", "K", "X"),
    }
    assert generated == expected
    assert len(generated) == 5
    assert len(generated) < 2 ** len(FINE_STATES)

    costs = {
        context: tuple(context.count(axis) for axis in AXES)
        for context in generated.values()
    }
    assert costs == {
        (): (0, 0, 0),
        ("X",): (0, 1, 0),
        ("K", "X"): (0, 1, 1),
        ("T", "X"): (1, 1, 0),
        ("T", "K", "X"): (1, 1, 1),
    }


def test_direct_context_family_is_not_a_boolean_algebra() -> None:
    direct = frozenset(_context_generated_propositions())
    spatial = _support(lambda state: state[1] == 1)
    construction = _support(lambda state: state[2] == 1)
    universe = frozenset(FINE_STATES)

    assert universe - spatial not in direct
    assert spatial & construction not in direct
    assert spatial | construction not in direct

    positive_construction = _support(lambda state: state[2] == 1)
    negative_construction = _support(lambda state: state[2] == 0)
    assert universe - positive_construction == negative_construction
    assert positive_construction in direct
    assert negative_construction in direct


def test_boolean_envelope_is_complete_only_on_the_contextual_quotient() -> None:
    direct = tuple(_context_generated_propositions())
    partition = _contextual_partition(direct)
    expected_partition = {
        frozenset({(*core, 0), (*core, 1)}) for core in CORE_STATES
    }
    assert set(partition) == expected_partition

    envelope = _boolean_envelope(direct)
    assert len(direct) == 5
    assert len(partition) == 8
    assert len(envelope) == 2**8 == 256
    assert len(envelope) < 2 ** len(FINE_STATES) == 65_536

    for proposition in envelope:
        for temporal, spatial, construction in CORE_STATES:
            assert (
                (temporal, spatial, construction, 0) in proposition
            ) == ((temporal, spatial, construction, 1) in proposition)

    one_core_state = frozenset({(0, 0, 0, 0), (0, 0, 0, 1)})
    one_history = frozenset({(0, 0, 0, 0)})
    assert one_core_state in envelope
    assert one_history not in envelope


def test_schedule_order_changes_the_generated_proposition() -> None:
    temporal_then_spatial = _spatial_proposition(_run_context(("T", "X")))
    spatial_then_temporal = _spatial_proposition(_run_context(("X", "T")))
    construction_then_spatial = _spatial_proposition(
        _run_context(("K", "X"))
    )
    spatial_then_construction = _spatial_proposition(
        _run_context(("X", "K"))
    )

    assert temporal_then_spatial == _support(lambda state: state[2] == 1)
    assert spatial_then_temporal == _support(
        lambda state: state[0] == 1 and state[2] == 1
    )
    assert construction_then_spatial == _support(
        lambda state: state[0] == 1 and state[2] == 0
    )
    assert spatial_then_construction == spatial_then_temporal
    assert temporal_then_spatial != spatial_then_temporal
    assert construction_then_spatial != spatial_then_construction
