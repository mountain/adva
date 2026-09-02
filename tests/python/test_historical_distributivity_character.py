"""Pressure-test reusable and reopenable distributivity characters."""

from __future__ import annotations

from adva.characteristic_research import (
    CharacteristicDirectionV0,
    DistributivityTaskRequestV0,
)
from adva.historical_character_research import (
    HistoricalCharacterResultKindV0,
    HistoricalClosureReadingV0,
    HistoricalDistributivityMachineV0,
    HistoricalInstantiationRequestV0,
    HistoricalObserverV0,
    TypedDistributivitySubstitutionV0,
)
from adva.research import ExperimentVerdictV0


DISTRIBUTIVITY = r"""
(module historical-distributivity-root
  (export factored expanded)

  (def factored-body
    (fn ((a Real) (x Real) (y Real)) Real
      (mul
        (frontier
          (use a)
          (add (frontier (use x) (use y)))))))

  (def expanded-body
    (fn ((a-left Real) (a-right Real) (x Real) (y Real)) Real
      (add
        (frontier
          (mul (frontier (use a-left) (use x)))
          (mul (frontier (use a-right) (use y)))))))

  (def factored
    (fn ((a Real) (x Real) (y Real)) Real
      (call factored-body (use a) (use x) (use y))))

  (def expanded
    (fn ((a Real) (x Real) (y Real)) Real
      (frontier
        (discard 1)
        (call expanded-body (copy (use a)) (use x) (use y)))))
)
"""


def _build(*, fuel: int | None = None, retain_residual: bool = True):
    request = DistributivityTaskRequestV0(
        sources=(DISTRIBUTIVITY,),
        module="historical-distributivity-root",
        left_function="factored",
        right_function="expanded",
        direction=CharacteristicDirectionV0.PROVE,
        fuel=fuel,
        retain_residual=retain_residual,
    )
    return HistoricalDistributivityMachineV0().create(request)


def _request(
    name: str,
    *,
    depth: int = 1,
    substitution: TypedDistributivitySubstitutionV0 | None = None,
    value_type: str = "Real",
    context_operation: str = "mul",
    closure_reading: HistoricalClosureReadingV0 = (
        HistoricalClosureReadingV0.MARKED_CORRESPONDENCE
    ),
    max_degree: int = 2,
    fuel: int | None = None,
    retain_residual: bool = True,
) -> HistoricalInstantiationRequestV0:
    built = _build()
    assert built.character is not None
    typed = substitution or TypedDistributivitySubstitutionV0(
        factor="a",
        left_addend="x",
        right_addend="y",
        value_type=value_type,
    )
    return HistoricalInstantiationRequestV0(
        character=built.character,
        instance_name=name,
        substitution=typed,
        context_scalars=(2,) * (depth - 1),
        context_operation=context_operation,
        closure_reading=closure_reading,
        max_degree=max_degree,
        fuel=fuel,
        retain_residual=retain_residual,
    )


def test_create_retains_law_scope_history_and_reopen_handle() -> None:
    result = _build()

    assert result.kind is HistoricalCharacterResultKindV0.CREATED
    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.character is not None
    character = result.character
    assert character.body.total_degree == 2
    assert character.certificate.exact_polynomial_identity
    assert character.certificate.residuals_retained
    assert character.history.left_residual.retained
    assert character.history.right_residual.retained
    assert character.reopen_handle.from_observer is HistoricalObserverV0.POLYNOMIAL
    assert character.reopen_handle.to_observer is HistoricalObserverV0.OCCURRENCE
    assert not character.scope.rule_has_fixed_semantic_depth
    assert not character.semantic_identity_authorized
    assert not character.provenance_erasure_authorized
    assert not character.certificate.rust_certificate
    assert not character.certificate.equation_cell_authorized
    assert not character.deck_transformation_authorized
    assert not character.hyperbolic_axis_authorized


def test_fresh_typed_permutation_is_checked_without_program_identity() -> None:
    machine = HistoricalDistributivityMachineV0()
    substitution = TypedDistributivitySubstitutionV0(
        factor="x",
        left_addend="a",
        right_addend="y",
    )
    result = machine.instantiate(
        _request("permuted", substitution=substitution)
    )

    assert result.kind is HistoricalCharacterResultKindV0.INSTANTIATED
    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.evidence is not None
    evidence = result.evidence
    assert evidence.substitution == substitution
    assert evidence.character_certificate_reused
    assert evidence.instance_feature_rechecked
    assert evidence.rust_programs_rechecked
    assert evidence.checked_programs != evidence.source_programs
    assert len(evidence.generated_source_sha256) == 64
    assert evidence.generated_module == "historical-dist-permuted"
    assert not evidence.program_identity_authorized
    assert not evidence.equation_cell_authorized
    terms = {
        (term.exponents, term.numerator, term.denominator)
        for term in evidence.common_characteristic.terms
    }
    assert terms == {
        ((1, 1, 0), 1, 1),
        ((0, 1, 1), 1, 1),
    }


def test_finite_depth_family_reuses_one_character_without_a_semantic_cap() -> None:
    machine = HistoricalDistributivityMachineV0()
    results = tuple(
        machine.instantiate(_request(f"depth-{depth}", depth=depth))
        for depth in range(1, 5)
    )

    assert all(
        result.kind is HistoricalCharacterResultKindV0.INSTANTIATED
        for result in results
    )
    assert tuple(result.evidence.finite_depth for result in results if result.evidence) == (
        1,
        2,
        3,
        4,
    )
    assert all(
        result.evidence is not None
        and not result.evidence.rule_has_fixed_semantic_depth
        and result.evidence.character_certificate_reused
        for result in results
    )
    assert len(
        {
            result.evidence.generated_source_sha256
            for result in results
            if result.evidence is not None
        }
    ) == 4
    coefficients = tuple(
        tuple(
            sorted(
                term.numerator
                for term in result.evidence.common_characteristic.terms
            )
        )
        for result in results
        if result.evidence is not None
    )
    assert coefficients == ((1, 1), (2, 2), (4, 4), (8, 8))


def test_occurrence_refinement_reopens_copy_history_without_refuting_law() -> None:
    machine = HistoricalDistributivityMachineV0()
    instance = machine.instantiate(_request("reopen", depth=3))
    reopened = machine.reopen(instance, HistoricalObserverV0.OCCURRENCE)

    assert reopened.kind is HistoricalCharacterResultKindV0.REOPENED
    assert reopened.verdict is ExperimentVerdictV0.SUPPORTED
    assert reopened.evidence is not None
    evidence = reopened.evidence
    assert evidence.from_observer is HistoricalObserverV0.POLYNOMIAL
    assert evidence.to_observer is HistoricalObserverV0.OCCURRENCE
    assert evidence.copy_history.left_copy_event_ids == ()
    assert evidence.copy_history.right_copy_event_ids
    assert ("copy", 1) in evidence.copy_history.extra_right_operations
    assert evidence.polynomial_law_remains_reusable
    assert evidence.program_identity_refuted
    assert evidence.residuals_retained
    assert not evidence.historical_inverse_authorized
    assert not evidence.provenance_erasure_authorized


def test_residual_drop_and_source_quotient_closure_are_refused() -> None:
    machine = HistoricalDistributivityMachineV0()
    dropped = machine.instantiate(
        _request("drop", retain_residual=False)
    )
    quotient = machine.instantiate(
        _request(
            "quotient",
            closure_reading=HistoricalClosureReadingV0.SOURCE_QUOTIENT,
        )
    )

    assert dropped.kind is HistoricalCharacterResultKindV0.NOT_REPRESENTABLE
    assert "residuals would be dropped" in dropped.reason
    assert quotient.kind is HistoricalCharacterResultKindV0.NOT_REPRESENTABLE
    assert "right-to-forget" in quotient.reason


def test_wrong_type_operation_and_degree_are_separate_refusals() -> None:
    machine = HistoricalDistributivityMachineV0()
    wrong_type = machine.instantiate(_request("wrong-type", value_type="Bool"))
    unsupported = machine.instantiate(
        _request("unsupported", context_operation="sin")
    )
    degree = machine.instantiate(_request("degree", max_degree=1))

    assert wrong_type.kind is HistoricalCharacterResultKindV0.NOT_REPRESENTABLE
    assert "value type" in wrong_type.reason
    assert unsupported.kind is HistoricalCharacterResultKindV0.NOT_REPRESENTABLE
    assert "context operation" in unsupported.reason
    assert degree.kind is HistoricalCharacterResultKindV0.NOT_REPRESENTABLE
    assert "degree 2" in degree.reason


def test_fuel_exhaustion_is_not_refutation_or_impossibility() -> None:
    machine = HistoricalDistributivityMachineV0()
    result = machine.instantiate(_request("fuel", fuel=0))

    assert result.kind is HistoricalCharacterResultKindV0.FUEL_EXHAUSTED
    assert result.verdict is ExperimentVerdictV0.FUEL_EXHAUSTED
    assert result.evidence is None
    assert result.characteristic_artifact is not None


def test_character_cannot_be_built_without_the_original_residuals() -> None:
    result = _build(retain_residual=False)

    assert result.kind is HistoricalCharacterResultKindV0.NOT_REPRESENTABLE
    assert result.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert result.character is None
    assert "complete process residuals" in result.reason


def test_reopen_requires_an_actual_observer_refinement() -> None:
    machine = HistoricalDistributivityMachineV0()
    instance = machine.instantiate(_request("no-refinement"))
    result = machine.reopen(instance, HistoricalObserverV0.POLYNOMIAL)

    assert result.kind is HistoricalCharacterResultKindV0.NOT_REPRESENTABLE
    assert result.evidence is None
