from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, TypeAlias

import sympy

from adva import link_modules


TRIADIC_LOGIC_CALIBRATION = r"""
(module triadic-satisfaction-logic
  (export
    identity-lift
    central-sign-lift
    open-prefix-lift
    projective-readout
    projective-after-identity
    projective-after-central-sign
    projective-after-open-prefix)

  (def identity-lift
    (fn ((x Real)) Real
      (use x)))

  (def central-sign-lift
    (fn ((x Real)) Real
      (neg (use x))))

  (def open-prefix-lift
    (fn ((x Real)) Real
      (scale 2 (use x))))

  (def projective-readout
    (fn ((x Real)) Real
      (mul (copy (use x)))))

  (def projective-after-identity
    (fn ((x Real)) Real
      (call projective-readout
        (call identity-lift (use x)))))

  (def projective-after-central-sign
    (fn ((x Real)) Real
      (call projective-readout
        (call central-sign-lift (use x)))))

  (def projective-after-open-prefix
    (fn ((x Real)) Real
      (call projective-readout
        (call open-prefix-lift (use x)))))
)
"""


TriadicPoint: TypeAlias = tuple[str, str, str]


@dataclass(frozen=True, slots=True)
class FiniteTriadicForm:
    """A finite satisfaction relation on time, space, and construction."""

    temporal: tuple[str, ...]
    spatial: tuple[str, ...]
    constructive: tuple[str, ...]
    accepted: frozenset[TriadicPoint]

    def __post_init__(self) -> None:
        temporal = set(self.temporal)
        spatial = set(self.spatial)
        constructive = set(self.constructive)
        if len(temporal) != len(self.temporal):
            raise ValueError("temporal carrier entries must be unique")
        if len(spatial) != len(self.spatial):
            raise ValueError("spatial carrier entries must be unique")
        if len(constructive) != len(self.constructive):
            raise ValueError("constructive carrier entries must be unique")
        for time, space, construction in self.accepted:
            if time not in temporal:
                raise ValueError(f"unknown temporal entry: {time}")
            if space not in spatial:
                raise ValueError(f"unknown spatial entry: {space}")
            if construction not in constructive:
                raise ValueError(f"unknown constructive entry: {construction}")

    def holds(self, time: str, space: str, construction: str) -> bool:
        """The finite Sierpinski reading: accepted evidence is observable."""

        return (time, space, construction) in self.accepted

    def temporal_section(self, space: str, construction: str) -> frozenset[str]:
        return frozenset(
            time
            for time in self.temporal
            if self.holds(time, space, construction)
        )

    def spatial_section(self, time: str, construction: str) -> frozenset[str]:
        return frozenset(
            space
            for space in self.spatial
            if self.holds(time, space, construction)
        )

    def constructive_section(self, time: str, space: str) -> frozenset[str]:
        return frozenset(
            construction
            for construction in self.constructive
            if self.holds(time, space, construction)
        )


@dataclass(frozen=True, slots=True)
class TriadicProposition:
    """A finite proposition represented by its accepted triadic support."""

    name: str
    support: frozenset[TriadicPoint]

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("a proposition requires a name")

    def is_well_typed_for(self, form: FiniteTriadicForm) -> bool:
        return self.support <= form.accepted

    def entails(self, other: TriadicProposition) -> bool:
        """Finite extensional entailment under the declared observer."""

        return self.support <= other.support


@dataclass(frozen=True, slots=True)
class TriadicQuotient:
    """A finite observer quotient with every forgotten fine point retained."""

    coarse: FiniteTriadicForm
    preimages: tuple[tuple[TriadicPoint, frozenset[TriadicPoint]], ...]

    def preimage(self, point: TriadicPoint) -> frozenset[TriadicPoint]:
        return dict(self.preimages)[point]


def _ordered_image(
    carrier: tuple[str, ...],
    mapping: Callable[[str], str],
) -> tuple[str, ...]:
    return tuple(dict.fromkeys(mapping(item) for item in carrier))


def quotient_form(
    form: FiniteTriadicForm,
    temporal_map: Callable[[str], str],
    spatial_map: Callable[[str], str],
    constructive_map: Callable[[str], str],
) -> TriadicQuotient:
    """Compute a finite triadic observer quotient and its exact residual."""

    def map_point(point: TriadicPoint) -> TriadicPoint:
        time, space, construction = point
        return (
            temporal_map(time),
            spatial_map(space),
            constructive_map(construction),
        )

    coarse_points = frozenset(map_point(point) for point in form.accepted)
    coarse = FiniteTriadicForm(
        temporal=_ordered_image(form.temporal, temporal_map),
        spatial=_ordered_image(form.spatial, spatial_map),
        constructive=_ordered_image(form.constructive, constructive_map),
        accepted=coarse_points,
    )
    preimages = tuple(
        (
            coarse_point,
            frozenset(
                point for point in form.accepted if map_point(point) == coarse_point
            ),
        )
        for coarse_point in sorted(coarse_points)
    )
    return TriadicQuotient(coarse=coarse, preimages=preimages)


IDENTITY_POINT: TriadicPoint = (
    "compatible_monodromy_history",
    "lifted_identity",
    "compatible_monodromy_word",
)
CENTRAL_POINT: TriadicPoint = (
    "positive_unipotent_history",
    "central_minus_identity",
    "positive_unipotent_word",
)
OPEN_POINT: TriadicPoint = (
    "two_cusp_prefix_history",
    "noncentral_lift",
    "two_cusp_prefix_word",
)


def legendre_lifted_form() -> FiniteTriadicForm:
    points = (IDENTITY_POINT, CENTRAL_POINT, OPEN_POINT)
    return FiniteTriadicForm(
        temporal=tuple(point[0] for point in points),
        spatial=tuple(point[1] for point in points),
        constructive=tuple(point[2] for point in points),
        accepted=frozenset({IDENTITY_POINT, CENTRAL_POINT, OPEN_POINT}),
    )


def _projective_temporal(time: str) -> str:
    if time in {IDENTITY_POINT[0], CENTRAL_POINT[0]}:
        return "closed_circuit_history"
    return "open_prefix_history"


def _projective_spatial(space: str) -> str:
    if space in {IDENTITY_POINT[1], CENTRAL_POINT[1]}:
        return "projective_identity"
    return "projective_nonidentity"


def _projective_constructive(construction: str) -> str:
    if construction in {IDENTITY_POINT[2], CENTRAL_POINT[2]}:
        return "closed_circuit_word"
    return "open_prefix_word"


def test_legendre_products_supply_the_three_spatial_readings() -> None:
    identity = sympy.eye(2)
    negative_identity = -identity
    intersection = sympy.Matrix([[0, 1], [-1, 0]])

    def primitive_twist(delta: sympy.Matrix) -> sympy.Matrix:
        return identity - delta * (intersection * delta).T

    delta_zero = sympy.Matrix([1, 0])
    delta_one = sympy.Matrix([0, 1])
    delta_infinity = -delta_zero - delta_one
    U_zero, U_one, U_infinity = tuple(
        primitive_twist(delta) ** 2
        for delta in (delta_zero, delta_one, delta_infinity)
    )

    positive_unipotent_product = U_zero * U_one * U_infinity
    compatible_monodromy_product = U_zero * U_one * (-U_infinity)
    two_cusp_prefix_product = U_zero * U_one

    assert positive_unipotent_product == negative_identity
    assert compatible_monodromy_product == identity
    assert two_cusp_prefix_product not in (identity, negative_identity)


def test_opposite_pairs_recover_the_three_sections_of_the_form() -> None:
    form = legendre_lifted_form()

    assert form.spatial_section(CENTRAL_POINT[0], CENTRAL_POINT[2]) == frozenset(
        {CENTRAL_POINT[1]}
    )
    assert form.temporal_section(IDENTITY_POINT[1], IDENTITY_POINT[2]) == frozenset(
        {IDENTITY_POINT[0]}
    )
    assert form.constructive_section(OPEN_POINT[0], OPEN_POINT[1]) == frozenset(
        {OPEN_POINT[2]}
    )

    # Mixing two incompatible readings produces no positive evidence.
    assert form.spatial_section(CENTRAL_POINT[0], IDENTITY_POINT[2]) == frozenset()
    assert not form.holds(
        "positive_unipotent_history",
        "lifted_identity",
        "positive_unipotent_word",
    )


def test_projective_quotient_merges_sign_and_retains_its_preimage() -> None:
    fine = legendre_lifted_form()
    quotient = quotient_form(
        fine,
        _projective_temporal,
        _projective_spatial,
        _projective_constructive,
    )

    closed_point: TriadicPoint = (
        "closed_circuit_history",
        "projective_identity",
        "closed_circuit_word",
    )
    open_point: TriadicPoint = (
        "open_prefix_history",
        "projective_nonidentity",
        "open_prefix_word",
    )
    assert quotient.coarse.accepted == frozenset({closed_point, open_point})
    assert quotient.preimage(closed_point) == frozenset(
        {IDENTITY_POINT, CENTRAL_POINT}
    )
    assert quotient.preimage(open_point) == frozenset({OPEN_POINT})

    # The quotient has forgotten one bit of lifted sign information, while
    # the residual preimage records exactly which fine witnesses were merged.
    assert len(fine.accepted) == 3
    assert len(quotient.coarse.accepted) == 2


def test_support_inclusion_induces_the_first_entailment_order() -> None:
    form = legendre_lifted_form()
    exact_identity = TriadicProposition(
        "exact lifted identity",
        frozenset({IDENTITY_POINT}),
    )
    central_residual = TriadicProposition(
        "central minus identity",
        frozenset({CENTRAL_POINT}),
    )
    projective_closure = TriadicProposition(
        "projective closure",
        frozenset({IDENTITY_POINT, CENTRAL_POINT}),
    )
    any_observed_crossing = TriadicProposition(
        "any observed crossing",
        form.accepted,
    )

    assert all(
        proposition.is_well_typed_for(form)
        for proposition in (
            exact_identity,
            central_residual,
            projective_closure,
            any_observed_crossing,
        )
    )
    assert exact_identity.entails(projective_closure)
    assert central_residual.entails(projective_closure)
    assert projective_closure.entails(any_observed_crossing)
    assert not projective_closure.entails(exact_identity)
    assert not exact_identity.entails(central_residual)
    assert projective_closure.support == (
        exact_identity.support | central_residual.support
    )


def test_adva_retains_the_lift_history_forgotten_by_projective_readout() -> None:
    workspace = link_modules([TRIADIC_LOGIC_CALIBRATION])
    identity_lift = workspace.function(
        "triadic-satisfaction-logic", "identity-lift"
    )
    central_lift = workspace.function(
        "triadic-satisfaction-logic", "central-sign-lift"
    )
    open_lift = workspace.function(
        "triadic-satisfaction-logic", "open-prefix-lift"
    )
    after_identity = workspace.function(
        "triadic-satisfaction-logic", "projective-after-identity"
    )
    after_central = workspace.function(
        "triadic-satisfaction-logic", "projective-after-central-sign"
    )
    after_open = workspace.function(
        "triadic-satisfaction-logic", "projective-after-open-prefix"
    )

    x = sympy.Symbol("x", real=True)
    assert sympy.simplify(identity_lift.to_sympy() - x) == 0
    assert sympy.simplify(central_lift.to_sympy() + x) == 0
    assert sympy.simplify(open_lift.to_sympy() - 2 * x) == 0

    assert sympy.simplify(after_identity.to_sympy() - x**2) == 0
    assert sympy.simplify(after_central.to_sympy() - x**2) == 0
    assert sympy.simplify(after_open.to_sympy() - 4 * x**2) == 0

    assert after_identity.history != after_central.history
    assert after_identity.ir != after_central.ir
    assert all(
        function.validation_certificate["graph"] == "checked"
        for function in (
            identity_lift,
            central_lift,
            open_lift,
            after_identity,
            after_central,
            after_open,
        )
    )
