"""Calibrate typed apertures, exact filling selection, and retained reopening."""

from __future__ import annotations

from adva import TriadicDomainV0, TriadicObserverPolicyV0
from adva.hole_research import (
    HoleCloseRequestV0,
    HoleObstructionV0,
    HoleOpenCloseMachineV0,
    HoleOperationV0,
)
from adva.research import (
    ExperimentVerdictV0,
    MultiHoleThroughMachineV0,
    MultiHoleThroughRequestV0,
    ResearchCodeV0,
)
from adva.triangular_research import (
    TriangularThroughMachineV0,
    TriangularThroughRequestV0,
)

POLICY = TriadicObserverPolicyV0(
    (
        TriadicDomainV0.CONSTRUCTION,
        TriadicDomainV0.SPACE,
        TriadicDomainV0.TIME,
    )
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


def _triangle():
    code = ResearchCodeV0(
        sources=(TRIANGULAR_THROUGH,),
        module="triangular-through",
        function="witness",
        input_domains=POLICY.input_domains,
        schedule=(0, 5, 6, 7, 1),
        initial_completed=(2, 3, 4),
    )
    request = TriangularThroughRequestV0(
        configuration_callee_module="triangular-through",
        configuration_callee_function="triangle",
        pair_callee_module="triangular-through",
        pair_callee_function="add-pair",
        alternative_schedules=((0, 7, 6, 5, 1), (5, 6, 7, 0, 1)),
    )
    return TriangularThroughMachineV0().run(code, request)


def _through(
    source: str,
    module: str,
    function: str,
    schedule: tuple[int, ...],
    *,
    initial_completed: tuple[int, ...] = (),
):
    code = ResearchCodeV0(
        sources=(source,),
        module=module,
        function="witness",
        input_domains=POLICY.input_domains,
        schedule=schedule,
        initial_completed=initial_completed,
    )
    request = MultiHoleThroughRequestV0(
        callee_module=module,
        callee_function=function,
        left_domain=TriadicDomainV0.SPACE,
        right_domain=TriadicDomainV0.TIME,
        interface_domain=TriadicDomainV0.CONSTRUCTION,
    )
    return MultiHoleThroughMachineV0().run(code, request)


def test_three_local_interfaces_form_one_typed_open_boundary() -> None:
    triangle = _triangle()
    result = HoleOpenCloseMachineV0().from_triangle(triangle)

    assert triangle.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.boundary is not None
    boundary = result.boundary
    assert boundary.surface == "{}[]()"
    assert tuple(hole.domain for hole in boundary.holes) == tuple(TriadicDomainV0)
    assert all(len(hole.fillings) == 1 for hole in boundary.holes)
    assert all(hole.residual is boundary.residual for hole in boundary.holes)
    assert all(not hole.semantic_authority for hole in boundary.holes)
    assert all(not hole.vocabulary_creation_authorized for hole in boundary.holes)
    assert all(not hole.singularity_identification_authorized for hole in boundary.holes)


def test_unique_close_and_reopen_recover_the_aperture_but_not_empty_history() -> None:
    boundary_result = HoleOpenCloseMachineV0().from_triangle(_triangle())
    assert boundary_result.boundary is not None
    aperture = boundary_result.boundary.hole(TriadicDomainV0.TIME)

    close = HoleOpenCloseMachineV0.close(
        aperture,
        HoleCloseRequestV0(domain=TriadicDomainV0.TIME),
    )
    assert close.verdict is ExperimentVerdictV0.SUPPORTED
    assert close.closed is not None
    assert close.closed.residual is aperture.residual
    assert close.closed.unselected_fillings == ()
    assert close.closed.trace[0].operation is HoleOperationV0.CLOSE
    assert not close.closed.forgetting_authorized
    assert not close.closed.historical_inverse_authorized

    reopened = HoleOpenCloseMachineV0.reopen(close.closed)
    assert reopened.hole == aperture
    assert reopened.residual is aperture.residual
    assert reopened.released_filling == close.closed.selected_filling
    assert tuple(event.operation for event in reopened.trace) == (
        HoleOperationV0.CLOSE,
        HoleOperationV0.REOPEN,
    )
    assert not reopened.historical_inverse_authorized
    assert not reopened.forgetting_authorized


def test_multivalued_fibre_refuses_unwitnessed_close_and_retains_alternatives() -> None:
    through = _through(
        GROUNDED_THROUGH,
        "grounded-through",
        "join-three",
        (0, 3, 1, 4),
        initial_completed=(2,),
    )
    result = HoleOpenCloseMachineV0().from_through(through)

    assert through.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.hole is not None
    aperture = result.hole
    assert aperture.domain is TriadicDomainV0.CONSTRUCTION
    assert aperture.surface == "{}"
    assert len(aperture.fillings) == 2
    assert len({filling.right_occurrence_id for filling in aperture.fillings}) == 2

    ambiguous = HoleOpenCloseMachineV0.close(
        aperture,
        HoleCloseRequestV0(domain=TriadicDomainV0.CONSTRUCTION),
    )
    assert ambiguous.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert ambiguous.obstruction is HoleObstructionV0.MULTIPLE_FILLINGS
    assert ambiguous.closed is None

    selected = HoleOpenCloseMachineV0.close(
        aperture,
        HoleCloseRequestV0(
            domain=TriadicDomainV0.CONSTRUCTION,
            selected_filling_index=1,
        ),
    )
    assert selected.verdict is ExperimentVerdictV0.SUPPORTED
    assert selected.closed is not None
    assert selected.closed.selected_filling.filling_index == 1
    assert tuple(
        filling.filling_index for filling in selected.closed.unselected_fillings
    ) == (0,)
    assert selected.closed.residual is through.cell.carrier


def test_wrong_domain_and_residual_erasure_are_separate_refusals() -> None:
    through = _through(
        GROUNDED_THROUGH,
        "grounded-through",
        "join-three",
        (0, 3, 1, 4),
        initial_completed=(2,),
    )
    result = HoleOpenCloseMachineV0().from_through(through)
    assert result.hole is not None

    wrong_domain = HoleOpenCloseMachineV0.close(
        result.hole,
        HoleCloseRequestV0(domain=TriadicDomainV0.SPACE, selected_filling_index=0),
    )
    assert wrong_domain.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert wrong_domain.obstruction is HoleObstructionV0.WRONG_DOMAIN

    erase = HoleOpenCloseMachineV0.close(
        result.hole,
        HoleCloseRequestV0(
            domain=TriadicDomainV0.CONSTRUCTION,
            selected_filling_index=0,
            retain_residual=False,
        ),
    )
    assert erase.verdict is ExperimentVerdictV0.OBSTRUCTION
    assert erase.obstruction is HoleObstructionV0.RESIDUAL_ERASURE


def test_unfillable_aperture_is_not_confused_with_absence_of_an_aperture() -> None:
    through = _through(
        PARTIAL_DISCARD,
        "partial-discard",
        "drop-right",
        (0,),
    )
    result = HoleOpenCloseMachineV0().from_through(through)

    assert through.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert result.verdict is ExperimentVerdictV0.SUPPORTED
    assert result.hole is not None
    assert result.hole.fillings == ()
    assert result.hole.residual is through.cell.carrier

    close = HoleOpenCloseMachineV0.close(
        result.hole,
        HoleCloseRequestV0(domain=TriadicDomainV0.CONSTRUCTION),
    )
    assert close.verdict is ExperimentVerdictV0.NOT_REPRESENTABLE
    assert close.obstruction is HoleObstructionV0.NO_FILLING
    assert close.closed is None
