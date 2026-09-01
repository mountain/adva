"""Ground one relation-valued angle form in exact Rust process artifacts."""

from __future__ import annotations

from adva import TriadicDomainV0, TriadicObserverPolicyV0, compile_module
from adva.research import (
    ExperimentVerdictV0,
    LayerOutcomeV0,
    MultiHoleThroughMachineV0,
    MultiHoleThroughRequestV0,
    ResearchCodeV0,
    ThroughValidationLayerV0,
)

GROUNDED_THROUGH = r"""
(module grounded-through
  (export witness)

  (def join-three
    (fn ((left Real) (right-a Real) (right-b Real)) Real
      (add
        (frontier
          (use left)
          (add
            (frontier
              (use right-a)
              (use right-b)))))))

  (def witness
    (fn ((construction Real) (space Real) (time Real))
        (outputs Real Real)
      (frontier
        (discard 1)
        (call join-three
          (use space)
          (copy (use time)))
        (use construction))))
)
"""


SEPARATED_HOLES = r"""
(module separated-holes
  (export witness)

  (def keep-separate
    (fn ((left Real) (right Real)) (outputs Real Real)
      (frontier
        (id (use left))
        (id (use right)))))

  (def witness
    (fn ((construction Real) (space Real) (time Real))
        (outputs Real Real Real)
      (frontier
        (call keep-separate
          (use space)
          (use time))
        (use construction))))
)
"""


PARTIAL_DISCARD = r"""
(module partial-discard
  (export witness)

  (def drop-right
    (fn ((left Real) (right Real)) Real
      (frontier
        (use left)
        (discard (use right)))))

  (def witness
    (fn ((construction Real) (space Real) (time Real))
        (outputs Real Real)
      (frontier
        (call drop-right
          (use space)
          (use time))
        (use construction))))
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
    source: str,
    module: str,
    schedule: tuple[int, ...],
    *,
    initial_completed: tuple[int, ...] = (),
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
    module: str,
    function: str,
    *,
    interface_domain: TriadicDomainV0 = TriadicDomainV0.CONSTRUCTION,
    composition_middle: tuple[int, ...] | None = None,
) -> MultiHoleThroughRequestV0:
    return MultiHoleThroughRequestV0(
        callee_module=module,
        callee_function=function,
        left_domain=TriadicDomainV0.SPACE,
        right_domain=TriadicDomainV0.TIME,
        interface_domain=interface_domain,
        composition_middle=composition_middle,
    )


def _outcome(result, layer: ThroughValidationLayerV0) -> LayerOutcomeV0:
    return next(record.outcome for record in result.validation if record.layer is layer)


def test_copy_merge_frame_forms_a_nonfunctional_exact_fibre_product() -> None:
    code = _code(
        GROUNDED_THROUGH,
        "grounded-through",
        (0, 3, 1, 4),
        initial_completed=(2,),
    )
    request = _request(
        "grounded-through",
        "join-three",
        composition_middle=(0, 2, 3),
    )
    result = MultiHoleThroughMachineV0().run(code, request)

    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert all(record.outcome is LayerOutcomeV0.SATISFIED for record in result.validation)
    assert result.cell is not None
    assert result.candidate is not None
    candidate = result.candidate

    assert tuple(hole["hole_index"] for hole in candidate.ordered_holes) == (0, 1, 2)
    assert tuple(hole["argument_index"] for hole in candidate.ordered_holes) == (0, 1, 1)
    assert tuple(hole["argument_output_index"] for hole in candidate.ordered_holes) == (0, 0, 1)
    assert candidate.left_hole_indices == (0,)
    assert candidate.right_hole_indices == (1, 2)
    assert len(candidate.left_incidence_indices) == 1
    assert len(candidate.right_incidence_indices) == 2
    assert len(candidate.relation) == 2
    assert not candidate.is_total_function_from_left
    assert {pair.middle_upper_wire_indices for pair in candidate.relation} == {
        candidate.middle_upper_wire_indices
    }
    assert tuple(pair.reversed() for pair in candidate.converse_relation) == candidate.relation


def test_complete_residual_and_source_free_middle_survive_the_abstraction() -> None:
    code = _code(
        GROUNDED_THROUGH,
        "grounded-through",
        (0, 3, 1, 4),
        initial_completed=(2,),
    )
    result = MultiHoleThroughMachineV0().run(
        code,
        _request(
            "grounded-through",
            "join-three",
            composition_middle=(0, 2, 3),
        ),
    )

    assert result.cell is not None
    assert result.candidate is not None
    assert result.candidate.residual is result.cell.carrier
    assert tuple(event["id"] for event in result.cell.carrier.events) == (0, 1, 3, 4)
    assert {event["operation"]["name"] for event in result.cell.carrier.events} == {
        "constant",
        "discard",
        "add",
    }
    assert {0, 1} <= set(result.cell.carrier.internal_events)
    assert result.cell.carrier.graft_intersections is not None
    selected = next(
        item
        for item in result.cell.carrier.graft_intersections
        if item["frame"] == result.candidate.frame_id
    )
    assert selected["body_events"] == [3, 4]
    assert {0, 1}.isdisjoint(selected["body_events"])

    middle = (
        compile_module(GROUNDED_THROUGH)
        .function("grounded-through", "witness")
        .causal_cut([0, 2, 3])
    )
    assert any(crossing["sources"] == [] for crossing in middle.frontier)
    assert result.adjacent_composition_certificate is not None
    assert result.adjacent_composition_certificate["middle_completed"] == [0, 2, 3]
    assert result.adjacent_composition_certificate["exact_composition"] == "checked"


def test_wrong_opposite_type_is_not_representable_before_a_relation_is_built() -> None:
    result = MultiHoleThroughMachineV0().run(
        _code(
            GROUNDED_THROUGH,
            "grounded-through",
            (0, 3, 1, 4),
            initial_completed=(2,),
        ),
        _request(
            "grounded-through",
            "join-three",
            interface_domain=TriadicDomainV0.SPACE,
        ),
    )

    assert result.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert result.candidate is None
    assert _outcome(result, ThroughValidationLayerV0.INTERFACE_TYPING) is LayerOutcomeV0.FAILED
    assert _outcome(result, ThroughValidationLayerV0.FIBRE_PRODUCT) is LayerOutcomeV0.BLOCKED


def test_parallel_equal_typed_outputs_do_not_fabricate_a_middle_relation() -> None:
    result = MultiHoleThroughMachineV0().run(
        _code(SEPARATED_HOLES, "separated-holes", (0, 1)),
        _request("separated-holes", "keep-separate", composition_middle=(0,)),
    )

    assert result.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert result.candidate is not None
    assert result.candidate.left_specialization
    assert result.candidate.right_specialization
    assert result.candidate.relation == ()
    assert _outcome(result, ThroughValidationLayerV0.MIDDLE_QUOTIENT) is LayerOutcomeV0.SATISFIED
    assert _outcome(result, ThroughValidationLayerV0.FIBRE_PRODUCT) is LayerOutcomeV0.FAILED


def test_discard_yields_a_partial_specialization_instead_of_erasing_provenance() -> None:
    result = MultiHoleThroughMachineV0().run(
        _code(PARTIAL_DISCARD, "partial-discard", (0,)),
        _request("partial-discard", "drop-right"),
    )

    assert result.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert result.cell is not None
    assert result.candidate is not None
    assert result.candidate.left_specialization
    assert result.candidate.right_specialization == ()
    assert tuple(event["id"] for event in result.candidate.residual.events) == (0,)
    assert result.candidate.residual is result.cell.carrier
    assert _outcome(result, ThroughValidationLayerV0.MIDDLE_QUOTIENT) is LayerOutcomeV0.FAILED
    assert result.candidate.forgetting_authorized is False
