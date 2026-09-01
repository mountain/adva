from __future__ import annotations

from dataclasses import dataclass
from math import gcd
from typing import Any

import sympy

from adva import link_modules


LEGENDRE_COHERENCE = r"""
(module legendre-crossing-coherence
  (export
    legendre-affine
    legendre-at-zero
    legendre-at-one
    cusp-zero-factorized
    cusp-one-factorized)

  (def triple-copy-expanded
    (fn ((left Real) (right Real)) (outputs Real Real Real)
      (frontier
        (use left)
        (copy (use right)))))

  (def triple-copy
    (fn ((x Real)) (outputs Real Real Real)
      (call triple-copy-expanded
        (copy (use x)))))

  (def legendre-affine-expanded
    (fn ((x0 Real) (x1 Real) (x2 Real) (parameter Real)) Real
      (mul
        (mul
          (use x0)
          (add (use x1) (neg 1)))
        (add (use x2) (neg (use parameter))))))

  (def legendre-affine
    (fn ((x Real) (parameter Real)) Real
      (call legendre-affine-expanded
        (frontier
          (call triple-copy (use x))
          (use parameter)))))

  (def legendre-at-zero
    (fn ((x Real)) Real
      (call legendre-affine
        (frontier (use x) 0))))

  (def legendre-at-one
    (fn ((x Real)) Real
      (call legendre-affine
        (frontier (use x) 1))))

  (def cusp-zero-expanded
    (fn ((x0 Real) (x1 Real) (x2 Real)) Real
      (mul
        (mul (use x0) (use x1))
        (add (use x2) (neg 1)))))

  (def cusp-zero-factorized
    (fn ((x Real)) Real
      (call cusp-zero-expanded
        (call triple-copy (use x)))))

  (def cusp-one-expanded
    (fn ((x0 Real) (x1 Real) (x2 Real)) Real
      (mul
        (use x0)
        (mul
          (add (use x1) (neg 1))
          (add (use x2) (neg 1))))))

  (def cusp-one-factorized
    (fn ((x Real)) Real
      (call cusp-one-expanded
        (call triple-copy (use x)))))
)
"""


Vector = tuple[int, int]


@dataclass(frozen=True, slots=True)
class ConstructionState:
    """A lifted construction-side charge with exact presentation history."""

    charge: Vector
    presentation: str
    history: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SpatialState:
    """An oriented homology charge."""

    cycle: Vector


@dataclass(frozen=True, slots=True)
class TemporalState:
    """A period covector paired with the spatial charge."""

    covector: Vector


@dataclass(frozen=True, slots=True)
class CoarseState:
    """A projective observer state that forgets sign and construction history."""

    domain: str
    line: Vector


@dataclass(frozen=True, slots=True)
class CuspFixture:
    """One exact Legendre cusp crossing convention."""

    name: str
    delta: Vector
    positive_lift: sympy.Matrix
    actual_monodromy: sympy.Matrix

    @property
    def token(self) -> str:
        return f"cross:{self.name}"


@dataclass(frozen=True, slots=True)
class TotalDefect:
    """Independent residual channels after one three-cusp circuit."""

    central_lift: sympy.Matrix
    construction_history: tuple[str, ...]


J = sympy.Matrix([[0, 1], [-1, 0]])
IDENTITY = sympy.eye(2)
NEGATIVE_IDENTITY = -IDENTITY


def _matrix(vector: Vector) -> sympy.Matrix:
    return sympy.Matrix(vector)


def _vector(matrix: sympy.Matrix) -> Vector:
    return (int(matrix[0]), int(matrix[1]))


def _primitive_twist(delta: Vector) -> sympy.Matrix:
    column = _matrix(delta)
    return IDENTITY - column * (J * column).T


def _fixtures() -> tuple[CuspFixture, ...]:
    deltas = ((1, 0), (0, 1), (-1, -1))
    positive = tuple(_primitive_twist(delta) ** 2 for delta in deltas)
    actual = (positive[0], positive[1], -positive[2])
    return tuple(
        CuspFixture(name, delta, lift, monodromy)
        for name, delta, lift, monodromy in zip(
            ("zero", "one", "infinity"),
            deltas,
            positive,
            actual,
        )
    )


def _projective_line(vector: Vector) -> Vector:
    left, right = vector
    if left == 0 and right == 0:
        raise ValueError("the projective observer cannot observe the zero vector")
    divisor = gcd(abs(left), abs(right))
    left //= divisor
    right //= divisor
    if left < 0 or (left == 0 and right < 0):
        left = -left
        right = -right
    return (left, right)


def _projective_matrix(matrix: sympy.Matrix) -> tuple[int, ...]:
    entries = tuple(int(value) for value in matrix)
    first = next(value for value in entries if value != 0)
    sign = -1 if first < 0 else 1
    return tuple(sign * value for value in entries)


def construction_to_space(state: ConstructionState) -> SpatialState:
    return SpatialState(state.charge)


def space_to_time(state: SpatialState) -> TemporalState:
    return TemporalState(_vector(J * _matrix(state.cycle)))


def time_to_construction(state: TemporalState) -> ConstructionState:
    return ConstructionState(
        charge=_vector(-J * _matrix(state.covector)),
        presentation="canonical-from-temporal",
        history=(),
    )


def cross_construction(
    fixture: CuspFixture,
    state: ConstructionState,
    *,
    positive_lift: bool = False,
) -> ConstructionState:
    matrix = fixture.positive_lift if positive_lift else fixture.actual_monodromy
    return ConstructionState(
        charge=_vector(matrix * _matrix(state.charge)),
        presentation=state.presentation,
        history=(*state.history, fixture.token),
    )


def cross_space(
    fixture: CuspFixture,
    state: SpatialState,
    *,
    positive_lift: bool = False,
) -> SpatialState:
    matrix = fixture.positive_lift if positive_lift else fixture.actual_monodromy
    return SpatialState(_vector(matrix * _matrix(state.cycle)))


def cross_time(
    fixture: CuspFixture,
    state: TemporalState,
    *,
    positive_lift: bool = False,
) -> TemporalState:
    matrix = fixture.positive_lift if positive_lift else fixture.actual_monodromy
    return TemporalState(_vector(matrix.inv().T * _matrix(state.covector)))


def observe_coarse(
    state: ConstructionState | SpatialState | TemporalState,
) -> CoarseState:
    if isinstance(state, ConstructionState):
        return CoarseState("K", _projective_line(state.charge))
    if isinstance(state, SpatialState):
        return CoarseState("X", _projective_line(state.cycle))
    return CoarseState("t", _projective_line(state.covector))


def coarse_construction_to_space(state: CoarseState) -> CoarseState:
    if state.domain != "K":
        raise TypeError("expected a constructive coarse state")
    return CoarseState("X", state.line)


def coarse_space_to_time(state: CoarseState) -> CoarseState:
    if state.domain != "X":
        raise TypeError("expected a spatial coarse state")
    return CoarseState("t", _projective_line(_vector(J * _matrix(state.line))))


def coarse_time_to_construction(state: CoarseState) -> CoarseState:
    if state.domain != "t":
        raise TypeError("expected a temporal coarse state")
    return CoarseState(
        "K",
        _projective_line(_vector(-J * _matrix(state.line))),
    )


def cross_coarse(
    fixture: CuspFixture,
    state: CoarseState,
    *,
    positive_lift: bool = False,
) -> CoarseState:
    matrix = fixture.positive_lift if positive_lift else fixture.actual_monodromy
    if state.domain in {"K", "X"}:
        transformed = matrix * _matrix(state.line)
    elif state.domain == "t":
        transformed = matrix.inv().T * _matrix(state.line)
    else:
        raise TypeError(f"unknown coarse domain {state.domain!r}")
    return CoarseState(state.domain, _projective_line(_vector(transformed)))


def _workspace() -> Any:
    return link_modules([LEGENDRE_COHERENCE])


def _history_fingerprint(function: Any) -> tuple[str, ...]:
    fingerprint: list[str] = []
    for event in function.history["prefix"]:
        if event["kind"] == "call":
            target = event["function"]
            fingerprint.append(f"call:{target['module']}/{target['function']}")
        elif "node" in event:
            fingerprint.append(f"{event['kind']}:{event['node']}")
        else:
            fingerprint.append(event["kind"])
    return tuple(fingerprint)


def test_six_paths_form_three_typed_crossing_squares() -> None:
    seed = ConstructionState(
        charge=(2, 1),
        presentation="seed",
        history=("origin",),
    )

    for fixture in _fixtures():
        # K -> X square: two paths, strict after forgetting constructive history.
        kx_left = construction_to_space(cross_construction(fixture, seed))
        kx_right = cross_space(fixture, construction_to_space(seed))
        assert kx_left == kx_right

        # X -> t square: two paths, strict by symplectic duality.
        spatial = construction_to_space(seed)
        xt_left = space_to_time(cross_space(fixture, spatial))
        xt_right = cross_time(fixture, space_to_time(spatial))
        assert xt_left == xt_right
        assert (
            J * fixture.actual_monodromy
            == fixture.actual_monodromy.inv().T * J
        )

        # t -> K square: charge commutes, but temporal data cannot reconstruct
        # the exact crossing token in construction history.
        temporal = space_to_time(spatial)
        tk_left = time_to_construction(cross_time(fixture, temporal))
        tk_right = cross_construction(
            fixture,
            time_to_construction(temporal),
        )
        assert tk_left.charge == tk_right.charge
        assert tk_left.presentation == tk_right.presentation
        assert tk_left.history == ()
        assert tk_right.history == (fixture.token,)
        assert observe_coarse(tk_left) == observe_coarse(tk_right)


def test_observer_forgetting_commutes_with_crossings_and_interpretations() -> None:
    construction = ConstructionState(
        charge=(-3, 2),
        presentation="lifted",
        history=("source", "rewrite"),
    )
    spatial = construction_to_space(construction)
    temporal = space_to_time(spatial)

    assert observe_coarse(construction_to_space(construction)) == (
        coarse_construction_to_space(observe_coarse(construction))
    )
    assert observe_coarse(space_to_time(spatial)) == (
        coarse_space_to_time(observe_coarse(spatial))
    )
    assert observe_coarse(time_to_construction(temporal)) == (
        coarse_time_to_construction(observe_coarse(temporal))
    )

    for fixture in _fixtures():
        for positive_lift in (False, True):
            assert observe_coarse(
                cross_construction(
                    fixture,
                    construction,
                    positive_lift=positive_lift,
                )
            ) == cross_coarse(
                fixture,
                observe_coarse(construction),
                positive_lift=positive_lift,
            )
            assert observe_coarse(
                cross_space(
                    fixture,
                    spatial,
                    positive_lift=positive_lift,
                )
            ) == cross_coarse(
                fixture,
                observe_coarse(spatial),
                positive_lift=positive_lift,
            )
            assert observe_coarse(
                cross_time(
                    fixture,
                    temporal,
                    positive_lift=positive_lift,
                )
            ) == cross_coarse(
                fixture,
                observe_coarse(temporal),
                positive_lift=positive_lift,
            )


def test_three_cusp_closure_has_independent_lift_and_history_residuals() -> None:
    fixtures = _fixtures()
    start = ConstructionState(
        charge=(2, 1),
        presentation="generic",
        history=("origin",),
    )

    # The declared column-vector path product is M_0 M_1 M_infinity.
    # Function application is right-to-left, so the state is updated in the
    # reversed fixture order.
    actual = start
    positive = start
    for fixture in reversed(fixtures):
        actual = cross_construction(fixture, actual)
        positive = cross_construction(fixture, positive, positive_lift=True)

    actual_product = (
        fixtures[0].actual_monodromy
        * fixtures[1].actual_monodromy
        * fixtures[2].actual_monodromy
    )
    positive_product = (
        fixtures[0].positive_lift
        * fixtures[1].positive_lift
        * fixtures[2].positive_lift
    )

    assert actual_product == IDENTITY
    assert positive_product == NEGATIVE_IDENTITY
    assert actual.charge == start.charge
    assert positive.charge == (-start.charge[0], -start.charge[1])

    expected_history = (
        "origin",
        "cross:infinity",
        "cross:one",
        "cross:zero",
    )
    assert actual.history == expected_history
    assert positive.history == expected_history

    # The coarse observer erases both the central sign and the exact history.
    assert observe_coarse(actual) == observe_coarse(start)
    assert observe_coarse(positive) == observe_coarse(start)

    defect = TotalDefect(
        central_lift=positive_product,
        construction_history=actual.history[len(start.history) :],
    )
    assert defect.central_lift == NEGATIVE_IDENTITY
    assert defect.construction_history == (
        "cross:infinity",
        "cross:one",
        "cross:zero",
    )


def test_equal_cusp_values_retain_distinct_lifted_construction_histories() -> None:
    workspace = _workspace()
    generic_zero = workspace.function(
        "legendre-crossing-coherence",
        "legendre-at-zero",
    )
    factorized_zero = workspace.function(
        "legendre-crossing-coherence",
        "cusp-zero-factorized",
    )
    generic_one = workspace.function(
        "legendre-crossing-coherence",
        "legendre-at-one",
    )
    factorized_one = workspace.function(
        "legendre-crossing-coherence",
        "cusp-one-factorized",
    )

    x = sympy.Symbol("x", real=True)
    assert sympy.simplify(generic_zero.to_sympy() - x**2 * (x - 1)) == 0
    assert sympy.simplify(factorized_zero.to_sympy() - x**2 * (x - 1)) == 0
    assert sympy.simplify(generic_one.to_sympy() - x * (x - 1) ** 2) == 0
    assert sympy.simplify(factorized_one.to_sympy() - x * (x - 1) ** 2) == 0

    pairs = (
        ("zero", generic_zero, factorized_zero),
        ("one", generic_one, factorized_one),
    )
    fixtures = {fixture.name: fixture for fixture in _fixtures()}

    for name, generic, factorized in pairs:
        generic_history = _history_fingerprint(generic)
        factorized_history = _history_fingerprint(factorized)
        assert generic_history != factorized_history
        assert generic.ir != factorized.ir

        generic_state = ConstructionState(
            charge=(2, 1),
            presentation="generic-specialization",
            history=generic_history,
        )
        factorized_state = ConstructionState(
            charge=(2, 1),
            presentation="factorized-cusp",
            history=factorized_history,
        )

        assert observe_coarse(generic_state) == observe_coarse(factorized_state)
        assert construction_to_space(generic_state) == construction_to_space(
            factorized_state
        )

        generic_after = cross_construction(fixtures[name], generic_state)
        factorized_after = cross_construction(fixtures[name], factorized_state)
        assert generic_after.charge == factorized_after.charge
        assert generic_after.history != factorized_after.history

        # A complete domain round trip retains the extensional charge but
        # canonicalizes away both source histories.
        generic_roundtrip = time_to_construction(
            space_to_time(construction_to_space(generic_after))
        )
        factorized_roundtrip = time_to_construction(
            space_to_time(construction_to_space(factorized_after))
        )
        assert generic_roundtrip == factorized_roundtrip
        assert generic_roundtrip.charge == generic_after.charge
        assert generic_roundtrip.history == ()


def test_projective_matrix_observer_forgets_the_infinity_chart_sign() -> None:
    zero, one, infinity = _fixtures()
    assert _projective_matrix(infinity.positive_lift) == _projective_matrix(
        infinity.actual_monodromy
    )

    positive_product = zero.positive_lift * one.positive_lift * infinity.positive_lift
    actual_product = (
        zero.actual_monodromy
        * one.actual_monodromy
        * infinity.actual_monodromy
    )
    assert positive_product == NEGATIVE_IDENTITY
    assert actual_product == IDENTITY
    assert _projective_matrix(positive_product) == _projective_matrix(
        actual_product
    )
