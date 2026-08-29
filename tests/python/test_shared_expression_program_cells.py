from __future__ import annotations

import math
from dataclasses import dataclass
from itertools import combinations
from typing import Any

from adva import link_modules


PROGRAM_CELL_KERNEL = r"""
(module program-cells
  (export
    identity increment shared-double scale-double square
    square-after-shared-double
    square-after-scale-double
    square-after-shared-double-through-identity
    square-after-shared-double-after-increment)

  (def identity
    (fn ((x Real)) Real
      (use x)))

  (def increment
    (fn ((x Real)) Real
      (add (use x) 1)))

  (def shared-double
    (fn ((x Real)) Real
      (add (copy (use x)))))

  (def scale-double
    (fn ((x Real)) Real
      (scale 2 (use x))))

  (def square
    (fn ((x Real)) Real
      (mul (copy (use x)))))

  (def square-after-shared-double
    (fn ((x Real)) Real
      (call square
        (call shared-double (use x)))))

  (def square-after-scale-double
    (fn ((x Real)) Real
      (call square
        (call scale-double (use x)))))

  (def square-after-shared-double-through-identity
    (fn ((x Real)) Real
      (call square
        (call identity
          (call shared-double (use x))))))

  (def square-after-shared-double-after-increment
    (fn ((x Real)) Real
      (call square
        (call shared-double
          (call increment (use x)))))))
"""


@dataclass(frozen=True, slots=True)
class ScalarNeighborhood:
    """A deliberately small output neighborhood used by the calibration."""

    lower: float
    upper: float

    def contains(self, value: float) -> bool:
        return self.lower < value < self.upper


@dataclass(frozen=True, slots=True)
class PulledNeighborhood:
    """A neighborhood read backwards through checked program stages."""

    target: ScalarNeighborhood
    forward_stages: tuple[Any, ...]

    @property
    def pullback_trace(self) -> tuple[str, ...]:
        return tuple(stage.qualified_name for stage in reversed(self.forward_stages))

    def contains(self, value: float) -> bool:
        current = value
        for stage in self.forward_stages:
            (input_name,) = stage.signature.input_names
            current = stage.evaluate({input_name: current})
            assert isinstance(current, float)
        return self.target.contains(current)


@dataclass(frozen=True, slots=True)
class CallSegment:
    """One declared factor and the checked operation nodes emitted for it."""

    function: str
    node_ids: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class BoundaryWitness:
    """Checked data carried by one internal call boundary."""

    position: int
    typed_frontier: tuple[str, ...]
    left_trace: tuple[str, ...]
    right_trace: tuple[str, ...]
    source_lineage: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RefinementSignature:
    """A canonical finite view of one compatible cut refinement."""

    cut_positions: tuple[int, ...]
    blocks: tuple[tuple[str, ...], ...]
    boundaries: tuple[BoundaryWitness, ...]


@dataclass(frozen=True, slots=True)
class ProgramCell:
    """One whole checked program together with its checked atomic call trace.

    This research-local object is intentionally richer than either a value
    function or an action table.  The internal call boundaries generate every
    compatible sequential cut; no cut position is supplied by the caller.
    Reading ``stages`` from left to right gives temporal composition.  Reading
    the same stages from right to left gives successive inverse images of an
    output neighborhood.  The checked whole retains call, operation,
    occurrence, and source data across every cut.
    """

    whole: Any
    stages: tuple[Any, ...]

    def __post_init__(self) -> None:
        if not self.stages:
            raise ValueError("a program cell needs at least one stage")
        for stage in (self.whole, *self.stages):
            if stage.signature.inputs != (("x", "real"),):
                raise TypeError("the calibration expects one named Real input")
            if stage.signature.outputs != ("real",):
                raise TypeError("the calibration expects one Real output")
            if stage.validation_certificate["graph"] != "checked":
                raise ValueError("every program-cell boundary must be Rust checked")
        if self.call_trace != tuple(stage.qualified_name for stage in self.stages):
            raise ValueError("the inferred stages do not reproduce checked call history")
        if any(
            event["kind"] == "call"
            for stage in self.stages
            for event in stage.history["prefix"]
        ):
            raise ValueError("the calibration expects a flat trace of leaf calls")

    @classmethod
    def from_checked_whole(cls, workspace: Any, whole: Any) -> ProgramCell:
        call_trace = tuple(
            (
                event["function"]["module"],
                event["function"]["function"],
            )
            for event in whole.history["prefix"]
            if event["kind"] == "call"
        )
        return cls(
            whole=whole,
            stages=tuple(workspace.function(module, function) for module, function in call_trace),
        )

    @property
    def call_trace(self) -> tuple[str, ...]:
        return tuple(
            f"{event['function']['module']}/{event['function']['function']}"
            for event in self.whole.history["prefix"]
            if event["kind"] == "call"
        )

    @property
    def segments(self) -> tuple[CallSegment, ...]:
        segments: list[tuple[str, list[int]]] = []
        for event in self.whole.history["prefix"]:
            if event["kind"] == "call":
                function = event["function"]
                segments.append(
                    (f"{function['module']}/{function['function']}", [])
                )
            elif event["kind"] == "operation" and segments:
                segments[-1][1].append(event["node"])
        return tuple(CallSegment(name, tuple(nodes)) for name, nodes in segments)

    @property
    def compatible_cut_positions(self) -> tuple[int, ...]:
        """All internal boundaries induced by the checked linear call trace."""

        return tuple(range(1, len(self.stages)))

    @property
    def all_refinements(self) -> tuple[RefinedProgramCell, ...]:
        """The finite Boolean refinement lattice of compatible cut sets."""

        positions = self.compatible_cut_positions
        return tuple(
            self.refinement(selected)
            for size in range(len(positions) + 1)
            for selected in combinations(positions, size)
        )

    def temporal_value(self, value: float) -> float:
        current = value
        for stage in self.stages:
            current = stage.evaluate({"x": current})
            assert isinstance(current, float)
        return current

    def pull_back(self, neighborhood: ScalarNeighborhood) -> PulledNeighborhood:
        return PulledNeighborhood(neighborhood, self.stages)

    def refinement(self, cut_positions: tuple[int, ...]) -> RefinedProgramCell:
        return RefinedProgramCell(self, cut_positions)

    def boundary_witness(self, position: int) -> BoundaryWitness:
        if position not in self.compatible_cut_positions:
            raise ValueError(f"{position} is not an internal checked call boundary")

        left_types = self.stages[position - 1].signature.outputs
        right_types = tuple(
            value_type for _, value_type in self.stages[position].signature.inputs
        )
        if left_types != right_types:
            raise TypeError("adjacent stages do not share the same typed frontier")

        return BoundaryWitness(
            position=position,
            typed_frontier=left_types,
            left_trace=self.call_trace[:position],
            right_trace=self.call_trace[position:],
            source_lineage=self._lineage_after_segment(position - 1),
        )

    def _lineage_after_segment(self, segment_index: int) -> tuple[str, ...]:
        """Read a scalar stage output from checked wires, across empty stages."""

        node_id = next(
            (
                segment.node_ids[-1]
                for segment in reversed(self.segments[: segment_index + 1])
                if segment.node_ids
            ),
            None,
        )
        producer = (
            {"kind": "node", "node": node_id}
            if node_id is not None
            else {"kind": "input", "index": 0}
        )
        wires = [
            wire
            for node in self.whole.ir["nodes"]
            for wire in node["inputs"]
        ] + list(self.whole.ir["outputs"])
        matching = [wire for wire in wires if wire["producer"] == producer]
        if len(matching) != 1:
            raise ValueError("the checked scalar boundary did not have one consumer")
        return tuple(matching[0]["lineage"])


@dataclass(frozen=True, slots=True)
class RefinedProgramCell:
    """One face of the compatible-cut lattice of a checked program cell."""

    cell: ProgramCell
    cut_positions: tuple[int, ...]

    def __post_init__(self) -> None:
        canonical = tuple(sorted(set(self.cut_positions)))
        if canonical != self.cut_positions:
            raise ValueError("cut positions must be unique and increasing")
        invalid = set(canonical) - set(self.cell.compatible_cut_positions)
        if invalid:
            raise ValueError(f"incompatible cut positions: {sorted(invalid)}")

    @property
    def blocks(self) -> tuple[tuple[str, ...], ...]:
        trace = self.cell.call_trace
        stops = (0, *self.cut_positions, len(trace))
        return tuple(trace[start:stop] for start, stop in zip(stops, stops[1:]))

    @property
    def boundaries(self) -> tuple[BoundaryWitness, ...]:
        return tuple(self.cell.boundary_witness(position) for position in self.cut_positions)

    @property
    def signature(self) -> RefinementSignature:
        return RefinementSignature(self.cut_positions, self.blocks, self.boundaries)

    def refine(self, position: int) -> RefinedProgramCell:
        return self.cell.refinement(tuple(sorted({*self.cut_positions, position})))

    def temporal_value(self, value: float) -> float:
        current = value
        for block in self._stage_blocks:
            for stage in block:
                current = stage.evaluate({"x": current})
                assert isinstance(current, float)
        return current

    def pull_back(self, neighborhood: ScalarNeighborhood) -> PulledNeighborhood:
        return self.cell.pull_back(neighborhood)

    @property
    def _stage_blocks(self) -> tuple[tuple[Any, ...], ...]:
        stages = self.cell.stages
        stops = (0, *self.cut_positions, len(stages))
        return tuple(stages[start:stop] for start, stop in zip(stops, stops[1:]))


def _workspace():
    return link_modules([PROGRAM_CELL_KERNEL])


def _cell(workspace: Any, whole_name: str) -> ProgramCell:
    return ProgramCell.from_checked_whole(
        workspace,
        workspace.function("program-cells", whole_name),
    )


def test_one_checked_program_cell_has_temporal_and_spatial_readings():
    workspace = _workspace()
    cell = _cell(
        workspace,
        "square-after-shared-double",
    )

    neighborhood = ScalarNeighborhood(15.0, 17.0)
    pulled = cell.pull_back(neighborhood)
    assert pulled.pullback_trace == (
        "program-cells/square",
        "program-cells/shared-double",
    )

    for value in (-3.0, -2.0, -1.5, 0.0, 1.5, 2.0, 3.0):
        temporal = cell.temporal_value(value)
        whole = cell.whole.evaluate({"x": value})
        assert isinstance(whole, float)
        assert math.isclose(temporal, whole, rel_tol=1e-14, abs_tol=1e-14)
        assert pulled.contains(value) == neighborhood.contains(whole)


def test_equal_value_neighborhoods_do_not_erase_shared_cut_geometry():
    workspace = _workspace()
    shared = _cell(
        workspace,
        "square-after-shared-double",
    )
    scaled = _cell(
        workspace,
        "square-after-scale-double",
    )
    neighborhood = ScalarNeighborhood(8.0, 20.0)

    for value in (-3.0, -1.0, 0.0, 1.0, 3.0):
        assert shared.temporal_value(value) == scaled.temporal_value(value)
        assert shared.pull_back(neighborhood).contains(value) == scaled.pull_back(
            neighborhood
        ).contains(value)

    # Both cuts present the same scalar function and the same scalar inverse
    # neighborhoods.  The richer cell still remembers that the first program
    # duplicated one source before its cut boundary.
    assert len(shared.boundary_witness(1).source_lineage) == 2
    assert len(scaled.boundary_witness(1).source_lineage) == 1
    assert shared.whole.history != scaled.whole.history
    assert shared.whole.source_partition != scaled.whole.source_partition


def test_unit_insertion_is_an_explicit_empty_stage_not_history_equality():
    workspace = _workspace()
    direct = _cell(
        workspace,
        "square-after-shared-double",
    )
    through_unit = _cell(
        workspace,
        "square-after-shared-double-through-identity",
    )

    assert through_unit.segments[1] == CallSegment(
        "program-cells/identity", ()
    )
    assert direct.whole.ir["nodes"] == through_unit.whole.ir["nodes"]
    assert direct.whole.history != through_unit.whole.history

    for value in (-2.0, 0.0, 2.0):
        assert direct.temporal_value(value) == through_unit.temporal_value(value)


def test_three_stage_cut_refinement_forms_a_checked_diamond():
    workspace = _workspace()
    cell = _cell(
        workspace,
        "square-after-shared-double-after-increment",
    )

    # A three-stage linear trace has two internal call boundaries.  Its four
    # compatible cut sets form the Boolean diamond B_2; no arbitrary graph
    # factorization or Python-created semantic identity is being asserted.
    assert cell.compatible_cut_positions == (1, 2)
    assert tuple(refinement.cut_positions for refinement in cell.all_refinements) == (
        (),
        (1,),
        (2,),
        (1, 2),
    )

    uncut = cell.refinement(())
    cut_left_first = uncut.refine(1)
    cut_right_first = uncut.refine(2)
    left_then_right = cut_left_first.refine(2)
    right_then_left = cut_right_first.refine(1)

    assert cut_left_first.signature != cut_right_first.signature
    assert cut_left_first.refine(1).signature == cut_left_first.signature
    assert left_then_right.signature == right_then_left.signature
    assert left_then_right.signature == cell.refinement((1, 2)).signature
    assert left_then_right.blocks == tuple((name,) for name in cell.call_trace)

    first_boundary, second_boundary = left_then_right.boundaries
    assert first_boundary.typed_frontier == ("real",)
    assert second_boundary.typed_frontier == ("real",)
    assert len(first_boundary.source_lineage) == 1
    assert len(second_boundary.source_lineage) == 2

    neighborhood = ScalarNeighborhood(35.0, 37.0)
    for value in (-2.0, -1.0, 0.0, 1.0, 2.0):
        whole = cell.whole.evaluate({"x": value})
        assert isinstance(whole, float)
        assert math.isclose(uncut.temporal_value(value), whole)
        assert math.isclose(cut_left_first.temporal_value(value), whole)
        assert math.isclose(cut_right_first.temporal_value(value), whole)
        assert left_then_right.pull_back(neighborhood).contains(value) == (
            neighborhood.contains(whole)
        )
