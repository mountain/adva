"""End-to-end checks for the bounded three-layer research machine."""

from __future__ import annotations

import json

import pytest
from adva import (
    TriadicDomainV0,
    TriadicObserverPolicyV0,
    compile_module,
)
from adva.research import (
    BoundaryMatchV0,
    ExperimentVerdictV0,
    FeedbackRequestV0,
    ResearchCodeV0,
    ResearchMachineV0,
)

BOUNDARY_RETURN_WITNESS = """
(module checked-boundary-return
  (export witness)
  (def witness
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard 1)
        (discard (neg 1))
        (use temporal)
        (use spatial)
        (use construction)))))
"""


NONRETURN_WITNESS = """
(module nonreturn
  (export witness)
  (def witness
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (neg (use temporal))
        (use spatial)
        (use construction)))))
"""


POLICY = TriadicObserverPolicyV0(
    (
        TriadicDomainV0.TIME,
        TriadicDomainV0.SPACE,
        TriadicDomainV0.CONSTRUCTION,
    )
)


def return_code(
    *,
    schedule: tuple[int, ...] = (0, 1, 2, 3, 4),
    fuel: int | None = None,
    feedback: FeedbackRequestV0 | None = None,
) -> ResearchCodeV0:
    return ResearchCodeV0(
        sources=(BOUNDARY_RETURN_WITNESS,),
        module="checked-boundary-return",
        function="witness",
        input_domains=POLICY.input_domains,
        schedule=schedule,
        fuel=fuel,
        feedback=feedback,
    )


def test_python_reads_and_composes_rust_triadic_transitions() -> None:
    function = compile_module(BOUNDARY_RETURN_WITNESS).function(
        "checked-boundary-return", "witness"
    )

    first = function.triadic_observer_transition_v0(POLICY, [], [0])
    second = function.triadic_observer_transition_v0(POLICY, [0], [0, 1])
    direct = function.triadic_observer_transition_v0(POLICY, [], [0, 1])
    composed = function.compose_triadic_observer_transitions_v0(POLICY, [], [0], [0, 1])

    assert first.result.upper == second.result.lower
    assert direct.result.slice == function.program_slice([], [0, 1]).result
    assert composed.result == direct.result
    assert composed.certificate["exact_composition"] == "checked"
    assert composed.certificate["lineage_relation_composition"] == "checked"
    assert direct.certificate["complete_slice_residual"] == "checked"
    assert direct.result.policy == POLICY


def test_three_epoch_boundary_replay_retains_every_cell_and_static_residual() -> None:
    code = return_code(
        feedback=FeedbackRequestV0(epochs=3, boundary_match=BoundaryMatchV0.EXACT_FRONTIER)
    )
    result = ResearchMachineV0().run(code)

    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert len(result.cells) == 3
    assert result.feedback is not None
    assert result.feedback.epoch_count == 3
    assert result.feedback.semantic_feedback_authorized is False
    assert result.feedback.residual_event_ids == (0, 1, 2, 3, 4)

    epoch_refs = result.feedback.epoch_event_refs
    assert len({ref for refs in epoch_refs for ref in refs}) == 15
    for epoch, cell in enumerate(result.cells):
        assert cell.epoch == epoch
        assert cell.trace.event_ids == (0, 1, 2, 3, 4)
        assert cell.residual_event_ids == (0, 1, 2, 3, 4)
        assert cell.lower_interface.cut["frontier"] == cell.upper_interface.cut["frontier"]
        assert cell.lower_interface.cut != cell.upper_interface.cut
        assert cell.transition_certificate["complete_slice_residual"] == "checked"


def test_research_code_round_trip_replays_to_the_same_digest() -> None:
    code = return_code(
        feedback=FeedbackRequestV0(epochs=2, boundary_match=BoundaryMatchV0.EXACT_FRONTIER)
    )
    restored = ResearchCodeV0.from_json(code.to_json())
    machine = ResearchMachineV0()

    assert restored == code
    assert machine.run(restored).replay_digest == machine.run(code).replay_digest

    malformed = json.loads(code.to_json())
    malformed["invented_semantics"] = True
    with pytest.raises(ValueError, match="fields do not match"):
        ResearchCodeV0.from_json(json.dumps(malformed))

    malformed = json.loads(code.to_json())
    malformed["schedule"] = [True, 1, 2]
    with pytest.raises(ValueError, match="JSON integers"):
        ResearchCodeV0.from_json(json.dumps(malformed))


def test_fuel_exhaustion_returns_a_partial_exact_cell_not_a_nonexistence_claim() -> None:
    result = ResearchMachineV0().run(return_code(fuel=2))

    assert result.verdict is ExperimentVerdictV0.FUEL_EXHAUSTED
    assert result.remaining_schedule == (2, 3, 4)
    assert len(result.cells) == 1
    assert result.cells[0].trace.event_ids == (0, 1)
    assert result.cells[0].residual_event_ids == (0, 1)
    assert "nonexistence" not in result.reason


def test_positive_exact_cut_feedback_is_explicitly_not_representable() -> None:
    result = ResearchMachineV0().run(
        return_code(feedback=FeedbackRequestV0(epochs=2, boundary_match=BoundaryMatchV0.EXACT_CUT))
    )

    assert result.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert len(result.cells) == 1
    assert result.feedback is None
    assert result.cells[0].lower_interface.cut != result.cells[0].upper_interface.cut


def test_frontier_mismatch_is_an_obstruction_not_a_fabricated_feedback() -> None:
    code = ResearchCodeV0(
        sources=(NONRETURN_WITNESS,),
        module="nonreturn",
        function="witness",
        input_domains=POLICY.input_domains,
        schedule=(0,),
        feedback=FeedbackRequestV0(epochs=2, boundary_match=BoundaryMatchV0.EXACT_FRONTIER),
    )
    result = ResearchMachineV0().run(code)

    assert result.verdict is ExperimentVerdictV0.OBSTRUCTION
    assert len(result.cells) == 1
    assert result.feedback is None
    assert (
        result.cells[0].lower_interface.cut["frontier"]
        != (result.cells[0].upper_interface.cut["frontier"])
    )


def test_schedule_path_remains_distinct_from_the_same_canonical_outer_cell() -> None:
    machine = ResearchMachineV0()
    left = machine.run(return_code(schedule=(0, 1, 2, 3, 4)))
    right = machine.run(return_code(schedule=(2, 3, 4, 0, 1)))

    assert left.verdict is ExperimentVerdictV0.SUPPORTED
    assert right.verdict is ExperimentVerdictV0.SUPPORTED
    assert left.cells[0].observer_transition == right.cells[0].observer_transition
    assert left.cells[0].trace.event_ids != right.cells[0].trace.event_ids
    assert left.replay_digest != right.replay_digest


def test_policy_and_schedule_inputs_are_rejected_before_they_can_forge_views() -> None:
    with pytest.raises(ValueError, match="requires construction, space, and time"):
        TriadicObserverPolicyV0(
            (
                TriadicDomainV0.TIME,
                TriadicDomainV0.TIME,
                TriadicDomainV0.CONSTRUCTION,
            )
        )

    with pytest.raises(ValueError, match="same event twice"):
        return_code(schedule=(0, 0))
