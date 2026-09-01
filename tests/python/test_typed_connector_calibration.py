"""Distinguish identity, sibling comparison, and source quotient connectors."""

from __future__ import annotations

from adva import TriadicDomainV0, TriadicObserverPolicyV0
from adva.connector_research import (
    ConnectorCalibrationLayerV0,
    ConnectorCalibrationMachineV0,
    ConnectorReadingV0,
)
from adva.research import ExperimentVerdictV0, LayerOutcomeV0, ResearchCodeV0
from adva.triangular_research import TriangularThroughRequestV0

TRIANGULAR_THROUGH = r"""
(module triangular-through
  (export witness)

  (def add-pair
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (use left)
          (use right)))))

  (def triangle
    (fn ((k-left Real) (k-right Real)
         (x-left Real) (x-right Real)
         (t-left Real) (t-right Real))
        (outputs Real Real Real)
      (frontier
        (call add-pair
          (use k-left)
          (use x-left))
        (call add-pair
          (use x-right)
          (use t-left))
        (call add-pair
          (use t-right)
          (use k-right)))))

  (def witness
    (fn ((construction Real) (space Real) (time Real))
        (outputs Real Real Real)
      (frontier
        (discard 1)
        (call triangle
          (copy (use construction))
          (copy (use space))
          (copy (use time))))))
)
"""

COUSIN_THROUGH = r"""
(module cousin-through
  (export witness)

  (def add-pair
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (use left)
          (use right)))))

  (def keep-first
    (fn ((keep Real) (drop Real)) Real
      (frontier
        (use keep)
        (discard (use drop)))))

  (def refine
    (fn ((left Real) (right Real)) (outputs Real Real)
      (frontier
        (use left)
        (call keep-first
          (copy (use right))))))

  (def triangle
    (fn ((k-left Real) (k-right Real)
         (x-left Real) (x-right Real)
         (t-left Real) (t-right Real))
        (outputs Real Real Real)
      (frontier
        (call add-pair
          (use k-left)
          (use x-left))
        (call add-pair
          (use x-right)
          (use t-left))
        (call add-pair
          (use t-right)
          (use k-right)))))

  (def witness
    (fn ((construction Real) (space Real) (time Real))
        (outputs Real Real Real)
      (frontier
        (discard 1)
        (call triangle
          (call refine
            (copy (use construction)))
          (copy (use space))
          (copy (use time))))))
)
"""

POLICY = TriadicObserverPolicyV0(
    (
        TriadicDomainV0.CONSTRUCTION,
        TriadicDomainV0.SPACE,
        TriadicDomainV0.TIME,
    )
)


def _code(
    source: str = TRIANGULAR_THROUGH,
    module: str = "triangular-through",
    *,
    schedule: tuple[int, ...] = (0, 5, 6, 7, 1),
    initial_completed: tuple[int, ...] = (2, 3, 4),
) -> ResearchCodeV0:
    return ResearchCodeV0(
        sources=(source,),
        module=module,
        function="witness",
        input_domains=POLICY.input_domains,
        schedule=schedule,
        initial_completed=initial_completed,
    )


def _request(
    module: str = "triangular-through",
    *,
    alternatives: tuple[tuple[int, ...], ...] = (
        (0, 7, 6, 5, 1),
        (5, 6, 7, 0, 1),
    ),
) -> TriangularThroughRequestV0:
    return TriangularThroughRequestV0(
        configuration_callee_module=module,
        configuration_callee_function="triangle",
        pair_callee_module=module,
        pair_callee_function="add-pair",
        alternative_schedules=alternatives,
    )


def _run():
    return ConnectorCalibrationMachineV0().run(_code(), _request())


def _trial(result, reading: ConnectorReadingV0):
    return next(trial for trial in result.trials if trial.reading is reading)


def _outcome(result, layer: ConnectorCalibrationLayerV0) -> LayerOutcomeV0:
    return next(record.outcome for record in result.validation if record.layer is layer)


def test_three_typed_boundaries_are_exact_direct_copy_siblings() -> None:
    result = _run()

    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert all(record.outcome is LayerOutcomeV0.SATISFIED for record in result.validation)
    assert tuple(boundary.domain for boundary in result.boundaries) == (
        TriadicDomainV0.SPACE,
        TriadicDomainV0.TIME,
        TriadicDomainV0.CONSTRUCTION,
    )
    assert len({boundary.source_id for boundary in result.boundaries}) == 3
    for boundary in result.boundaries:
        assert boundary.direct_copy_siblings
        assert boundary.exit_occurrence_id != boundary.entry_occurrence_id
        assert boundary.common_parent_path == ()
        assert {boundary.exit_path, boundary.entry_path} == {(0,), (1,)}


def test_exact_identity_preserves_occurrences_and_refuses_the_cycle() -> None:
    result = _run()
    trial = _trial(result, ConnectorReadingV0.EXACT_IDENTITY)

    assert trial.finite_composition_verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert trial.promotion_verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert trial.occurrence_cycle_relation == ()
    assert trial.source_cycle_relation == ()
    assert trial.preserves_occurrence_identity
    assert not trial.requires_forgetting
    assert not trial.forgetting_authorized
    assert len(trial.connectors) == 3
    for connector in trial.connectors:
        assert connector.symmetric
        assert len(connector.relation) == 2
        assert all(left == right for left, right in connector.relation)


def test_sibling_comparison_closes_a_relation_without_identifying_endpoints() -> None:
    result = _run()
    trial = _trial(result, ConnectorReadingV0.DIRECT_SIBLING_COMPARISON)

    assert trial.finite_composition_verdict is ExperimentVerdictV0.SUPPORTED
    assert trial.promotion_verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert len(trial.occurrence_cycle_relation) == 1
    assert trial.occurrence_cycle_relation[0][0] == trial.occurrence_cycle_relation[0][1]
    assert trial.source_cycle_relation == ()
    assert trial.preserves_occurrence_identity
    assert not trial.requires_forgetting
    assert not trial.global_closure_authorized
    for connector in trial.connectors:
        boundary = connector.boundary
        assert connector.relation == tuple(
            sorted(
                (
                    (
                        boundary.exit_incidence_index,
                        boundary.entry_incidence_index,
                    ),
                    (
                        boundary.entry_incidence_index,
                        boundary.exit_incidence_index,
                    ),
                )
            )
        )
        assert boundary.exit_occurrence_id != boundary.entry_occurrence_id
        assert connector.semantic_authority is False


def test_source_projection_closes_only_by_a_visible_many_to_one_forgetting() -> None:
    result = _run()
    trial = _trial(result, ConnectorReadingV0.SOURCE_QUOTIENT)

    assert trial.finite_composition_verdict is ExperimentVerdictV0.SUPPORTED
    assert trial.promotion_verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert trial.occurrence_cycle_relation == ()
    assert len(trial.source_cycle_relation) == 1
    assert trial.source_cycle_relation[0][0] == trial.source_cycle_relation[0][1]
    assert not trial.preserves_occurrence_identity
    assert trial.requires_forgetting
    assert not trial.forgetting_authorized
    assert not trial.global_closure_authorized
    assert trial.connectors == ()
    assert len(result.quotient_classes) == 3
    for quotient in result.quotient_classes:
        assert len(quotient.incidence_indices) == 2
        assert len(set(quotient.occurrence_ids)) == 2
        assert set(quotient.occurrence_paths) == {(0,), (1,)}


def test_all_readings_retain_one_complete_process_residual() -> None:
    result = _run()

    primary = result.triangle.cells[0]
    assert all(trial.residual_retained for trial in result.trials)
    assert all(angle.residual is primary.carrier for angle in result.triangle.angles)
    assert tuple(event["id"] for event in primary.carrier.events) == (0, 1, 5, 6, 7)
    assert {event["operation"]["name"] for event in primary.carrier.events} == {
        "constant",
        "discard",
        "add",
    }


def test_same_source_cousins_do_not_receive_a_direct_sibling_witness() -> None:
    code = _code(
        COUSIN_THROUGH,
        "cousin-through",
        schedule=(0, 7, 8, 9, 1),
        initial_completed=(2, 3, 4, 5, 6),
    )
    request = _request(
        "cousin-through",
        alternatives=(
            (0, 9, 8, 7, 1),
            (7, 8, 9, 0, 1),
        ),
    )
    result = ConnectorCalibrationMachineV0().run(code, request)

    assert result.triangle.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert (
        _outcome(result, ConnectorCalibrationLayerV0.TYPED_BOUNDARIES)
        is LayerOutcomeV0.FAILED
    )
    construction = next(
        boundary
        for boundary in result.boundaries
        if boundary.domain is TriadicDomainV0.CONSTRUCTION
    )
    assert construction.source_id
    assert construction.exit_occurrence_id != construction.entry_occurrence_id
    assert {construction.exit_path, construction.entry_path} == {
        (0,),
        (1, 0),
    }
    assert not construction.direct_copy_siblings
    assert (
        _outcome(result, ConnectorCalibrationLayerV0.SIBLING_COMPARISON)
        is LayerOutcomeV0.BLOCKED
    )
