"""Calibrate distributivity as one learning/proof characteristic task."""

from __future__ import annotations

from adva.characteristic_research import (
    CharacteristicDirectionV0,
    CharacteristicLayerV0,
    CharacteristicResultKindV0,
    DistributivityCharacteristicMachineV0,
    DistributivityTaskRequestV0,
)
from adva.research import ExperimentVerdictV0, LayerOutcomeV0


DISTRIBUTIVITY = r"""
(module distributivity-task
  (export factored expanded wrong)

  (def factored-body
    (fn ((a Real) (x Real) (y Real)) Real
      (mul
        (frontier
          (use a)
          (add
            (frontier
              (use x)
              (use y)))))))

  (def expanded-body
    (fn ((a-left Real) (a-right Real) (x Real) (y Real)) Real
      (add
        (frontier
          (mul
            (frontier
              (use a-left)
              (use x)))
          (mul
            (frontier
              (use a-right)
              (use y)))))))

  (def wrong-body
    (fn ((a Real) (x Real) (y Real)) Real
      (add
        (frontier
          (mul
            (frontier
              (use a)
              (use x)))
          (use y)))))

  (def factored
    (fn ((a Real) (x Real) (y Real)) Real
      (call factored-body
        (use a)
        (use x)
        (use y))))

  (def expanded
    (fn ((a Real) (x Real) (y Real)) Real
      (frontier
        (discard 1)
        (call expanded-body
          (copy (use a))
          (use x)
          (use y)))))

  (def wrong
    (fn ((a Real) (x Real) (y Real)) Real
      (call wrong-body
        (use a)
        (use x)
        (use y))))
)
"""


def _request(
    direction: CharacteristicDirectionV0,
    *,
    right: str = "expanded",
    max_degree: int = 2,
    fuel: int | None = None,
    retain_residual: bool = True,
) -> DistributivityTaskRequestV0:
    return DistributivityTaskRequestV0(
        sources=(DISTRIBUTIVITY,),
        module="distributivity-task",
        left_function="factored",
        right_function=right,
        direction=direction,
        max_degree=max_degree,
        fuel=fuel,
        retain_residual=retain_residual,
    )


def _run(
    direction: CharacteristicDirectionV0,
    **kwargs,
):
    return DistributivityCharacteristicMachineV0().run(
        _request(direction, **kwargs)
    )


def test_proof_readout_builds_a_bounded_distributivity_witness() -> None:
    result = _run(CharacteristicDirectionV0.PROVE)

    assert result.kind is CharacteristicResultKindV0.PROVED
    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert all(record.outcome is LayerOutcomeV0.SATISFIED for record in result.validation)
    assert tuple(record.layer for record in result.validation) == tuple(
        CharacteristicLayerV0
    )
    assert result.left is not None
    assert result.right is not None
    assert result.common_characteristic is not None
    assert {
        (term.exponents, term.numerator, term.denominator)
        for term in result.common_characteristic.terms
    } == {
        ((1, 1, 0), 1, 1),
        ((1, 0, 1), 1, 1),
    }
    assert result.proof_witness is not None
    assert result.proof_witness.rule == "left-distributivity-over-addition-v0"
    assert result.proof_witness.exact_polynomial_identity
    assert result.proof_witness.residuals_retained
    assert not result.proof_witness.equation_cell_authorized
    assert not result.program_equivalence_authorized
    assert not result.learning_proof_self_duality_authorized


def test_one_core_has_three_presentations_and_exact_local_composition() -> None:
    result = _run(CharacteristicDirectionV0.PROVE)
    assert result.left is not None
    assert result.right is not None

    for atlas in (result.left, result.right):
        assert atlas.boundary.public_form == "{}[]()"
        assert len(atlas.through.forms) == 3
        assert atlas.through.exact_lineage_links
        assert atlas.through.relational_converse_authorized
        assert not atlas.through.inverse_execution_authorized
        assert len(atlas.multi_hole.graft.frames) >= 2
        assert atlas.multi_hole.carrier.events
        assert atlas.multi_hole.composition_middle
        assert atlas.correspondence.exact_slice_shared
        assert atlas.correspondence.original_ids_checked
        assert atlas.correspondence.lineage_checked
        assert atlas.correspondence.graft_checked
        assert atlas.correspondence.slice_composition_checked
        assert atlas.correspondence.observer_composition_checked
        assert not atlas.correspondence.semantic_authority

    assert result.left.core_ir != result.right.core_ir
    assert result.left.qualified_name != result.right.qualified_name


def test_learning_returns_feature_equality_with_unequal_process_residuals() -> None:
    result = _run(CharacteristicDirectionV0.LEARN)

    assert result.kind is CharacteristicResultKindV0.OBSERVATIONALLY_EQUAL
    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.left is not None
    assert result.right is not None
    assert result.left.characteristic == result.right.characteristic
    assert result.left.residual.operation_names != result.right.residual.operation_names
    assert "copy" not in result.left.residual.operation_names
    assert "copy" in result.right.residual.operation_names
    assert {"constant", "discard"} <= set(result.right.residual.operation_names)
    assert result.left.residual.retained
    assert result.right.residual.retained

    forget = result.forget_evidence
    assert forget is not None
    assert forget.feature_comparison_authorized
    assert not forget.program_identification_authorized
    assert not forget.equation_cell_authorized
    assert not forget.provenance_erasure_authorized
    assert not forget.semantic_authority


def test_wrong_expansion_is_refuted_by_an_exact_finite_counterexample() -> None:
    result = _run(CharacteristicDirectionV0.PROVE, right="wrong")

    assert result.kind is CharacteristicResultKindV0.REFUTED
    assert result.verdict is ExperimentVerdictV0.COUNTEREXAMPLE
    assert result.proof_witness is None
    assert result.counterexample is not None
    assert result.counterexample.left_value != result.counterexample.right_value
    assert {name for name, _ in result.counterexample.assignment} == {"a", "x", "y"}
    assert result.left is not None
    assert result.right is not None
    assignment = dict(result.counterexample.assignment)
    assert result.left.characteristic.evaluate(assignment) == (
        result.counterexample.left_value
    )
    assert result.right.characteristic.evaluate(assignment) == (
        result.counterexample.right_value
    )


def test_degree_outside_the_declared_fragment_is_not_representable() -> None:
    result = _run(CharacteristicDirectionV0.PROVE, max_degree=1)

    assert result.kind is CharacteristicResultKindV0.NOT_REPRESENTABLE
    assert result.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert "degree 2" in result.reason
    characteristic = next(
        record
        for record in result.validation
        if record.layer is CharacteristicLayerV0.PRESENTATION_CORRESPONDENCE
    )
    assert characteristic.outcome is LayerOutcomeV0.FAILED


def test_exhaustion_is_not_refutation_or_nonrepresentability() -> None:
    result = _run(CharacteristicDirectionV0.PROVE, fuel=0)

    assert result.kind is CharacteristicResultKindV0.FUEL_EXHAUSTED
    assert result.verdict is ExperimentVerdictV0.FUEL_EXHAUSTED
    assert len(result.checked_core_names) == 2
    assert result.remaining_fuel_cost > 0
    assert result.left is None
    assert result.right is None
    assert result.counterexample is None


def test_feature_projection_is_refused_when_the_residual_would_be_dropped() -> None:
    result = _run(
        CharacteristicDirectionV0.LEARN,
        retain_residual=False,
    )

    assert result.kind is CharacteristicResultKindV0.NOT_REPRESENTABLE
    assert result.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert "without complete process residuals" in result.reason
    residual = next(
        record
        for record in result.validation
        if record.layer is CharacteristicLayerV0.RESIDUAL
    )
    assert residual.outcome is LayerOutcomeV0.FAILED


def test_result_vocabulary_keeps_the_five_required_outcomes_distinct() -> None:
    assert set(CharacteristicResultKindV0) == {
        CharacteristicResultKindV0.PROVED,
        CharacteristicResultKindV0.REFUTED,
        CharacteristicResultKindV0.OBSERVATIONALLY_EQUAL,
        CharacteristicResultKindV0.NOT_REPRESENTABLE,
        CharacteristicResultKindV0.FUEL_EXHAUSTED,
    }
