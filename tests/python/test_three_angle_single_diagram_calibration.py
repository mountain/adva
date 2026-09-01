"""Calibrate all three local through angles in one Rust diagram and slice."""

from __future__ import annotations

import pytest

from adva import TriadicDomainV0, TriadicObserverPolicyV0, compile_module
from adva.research import ExperimentVerdictV0, LayerOutcomeV0, ResearchCodeV0
from adva.triangular_research import (
    TriangleValidationLayerV0,
    TriangularThroughMachineV0,
    TriangularThroughRequestV0,
)

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

POLICY = TriadicObserverPolicyV0(
    (
        TriadicDomainV0.CONSTRUCTION,
        TriadicDomainV0.SPACE,
        TriadicDomainV0.TIME,
    )
)

PRIMARY_SCHEDULE = (0, 5, 6, 7, 1)
ALTERNATIVE_SCHEDULES = (
    (0, 7, 6, 5, 1),
    (5, 6, 7, 0, 1),
)


def _code(schedule: tuple[int, ...] = PRIMARY_SCHEDULE) -> ResearchCodeV0:
    return ResearchCodeV0(
        sources=(TRIANGULAR_THROUGH,),
        module="triangular-through",
        function="witness",
        input_domains=POLICY.input_domains,
        schedule=schedule,
        initial_completed=(2, 3, 4),
    )


def _request(
    schedules: tuple[tuple[int, ...], ...] = ALTERNATIVE_SCHEDULES,
) -> TriangularThroughRequestV0:
    return TriangularThroughRequestV0(
        configuration_callee_module="triangular-through",
        configuration_callee_function="triangle",
        pair_callee_module="triangular-through",
        pair_callee_function="add-pair",
        alternative_schedules=schedules,
    )


def _run(
    schedules: tuple[tuple[int, ...], ...] = ALTERNATIVE_SCHEDULES,
):
    return TriangularThroughMachineV0().run(_code(), _request(schedules))


def _outcome(result, layer: TriangleValidationLayerV0) -> LayerOutcomeV0:
    return next(record.outcome for record in result.validation if record.layer is layer)


def test_one_compilation_derives_all_three_typed_angles() -> None:
    result = _run()

    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert all(record.outcome is LayerOutcomeV0.SATISFIED for record in result.validation)
    assert len(result.cells) == 3
    assert len(result.angles) == 3
    assert tuple(
        (angle.left_domain, angle.right_domain, angle.interface_domain)
        for angle in result.angles
    ) == (
        (
            TriadicDomainV0.CONSTRUCTION,
            TriadicDomainV0.SPACE,
            TriadicDomainV0.TIME,
        ),
        (
            TriadicDomainV0.SPACE,
            TriadicDomainV0.TIME,
            TriadicDomainV0.CONSTRUCTION,
        ),
        (
            TriadicDomainV0.TIME,
            TriadicDomainV0.CONSTRUCTION,
            TriadicDomainV0.SPACE,
        ),
    )
    assert all(len(angle.relation) == 1 for angle in result.angles)
    assert len(result.used_lower_incidence_indices) == 6
    assert set(result.used_lower_incidence_indices) == set(range(6))


def test_schedules_share_one_carrier_but_keep_distinct_traces() -> None:
    result = _run()

    primary, *alternatives = result.cells
    assert all(
        cell.observer_transition == primary.observer_transition
        for cell in alternatives
    )
    assert all(cell.carrier == primary.carrier for cell in alternatives)
    assert tuple(cell.trace.event_ids for cell in result.cells) == (
        PRIMARY_SCHEDULE,
        *ALTERNATIVE_SCHEDULES,
    )


def test_source_free_residual_survives_all_local_angles() -> None:
    result = _run()

    primary = result.cells[0]
    assert tuple(event["id"] for event in primary.carrier.events) == (0, 1, 5, 6, 7)
    assert {event["operation"]["name"] for event in primary.carrier.events} == {
        "constant",
        "discard",
        "add",
    }
    assert all(angle.residual is primary.carrier for angle in result.angles)

    middle = (
        compile_module(TRIANGULAR_THROUGH)
        .function("triangular-through", "witness")
        .causal_cut([0, 2, 3, 4])
    )
    assert any(crossing["sources"] == [] for crossing in middle.frontier)


def test_raw_cycle_refuses_three_undeclared_sibling_connectors() -> None:
    result = _run()

    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.closure is not None
    assert result.closure.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert result.closure.raw_cycle_relation == ()
    assert set(result.closure.missing_connector_domains) == set(TriadicDomainV0)
    assert result.closure.same_domain_connectors_authorized is False
    assert result.closure.global_closure_authorized is False
    assert (
        _outcome(result, TriangleValidationLayerV0.GLOBAL_CLOSURE)
        is LayerOutcomeV0.SATISFIED
    )


def test_non_permutation_schedule_is_rejected_before_closure() -> None:
    result = _run(((0, 5, 6, 1),))

    assert result.verdict is ExperimentVerdictV0.OBSTRUCTION
    assert result.closure is None
    assert (
        _outcome(result, TriangleValidationLayerV0.SCHEDULE_INDEPENDENCE)
        is LayerOutcomeV0.FAILED
    )
    assert (
        _outcome(result, TriangleValidationLayerV0.GLOBAL_CLOSURE)
        is LayerOutcomeV0.BLOCKED
    )


def test_repeated_alternative_event_is_invalid_input() -> None:
    with pytest.raises(ValueError, match="repeats an event"):
        _request(((0, 5, 5, 7, 1),))
