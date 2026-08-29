from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from adva import link_modules


PROGRAM_CELL_KERNEL = r"""
(module program-cells
  (export
    identity shared-double scale-double square
    square-after-shared-double
    square-after-scale-double
    square-after-shared-double-through-identity)

  (def identity
    (fn ((x Real)) Real
      (use x)))

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
          (call shared-double (use x)))))))
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
class ProgramCell:
    """One whole checked program together with one declared way to cut it.

    This research-local object is intentionally richer than either a value
    function or an action table.  Reading ``stages`` from left to right gives
    temporal composition.  Reading the same stages from right to left gives
    successive inverse images of an output neighborhood.  The checked whole
    retains call, operation, occurrence, and source data across the cut.
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
            raise ValueError("the checked call history does not realize the declared cut")

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

    def temporal_value(self, value: float) -> float:
        current = value
        for stage in self.stages:
            current = stage.evaluate({"x": current})
            assert isinstance(current, float)
        return current

    def pull_back(self, neighborhood: ScalarNeighborhood) -> PulledNeighborhood:
        return PulledNeighborhood(neighborhood, self.stages)

    def boundary_lineage_before(self, segment_index: int) -> tuple[str, ...]:
        segment = self.segments[segment_index]
        if not segment.node_ids:
            return ()
        first_node = segment.node_ids[0]
        node = next(item for item in self.whole.ir["nodes"] if item["id"] == first_node)
        return tuple(
            occurrence
            for wire in node["inputs"]
            for occurrence in wire["lineage"]
        )


def _workspace():
    return link_modules([PROGRAM_CELL_KERNEL])


def _cell(workspace: Any, whole_name: str, stage_names: tuple[str, ...]) -> ProgramCell:
    return ProgramCell(
        whole=workspace.function("program-cells", whole_name),
        stages=tuple(workspace.function("program-cells", name) for name in stage_names),
    )


def test_one_checked_program_cell_has_temporal_and_spatial_readings():
    workspace = _workspace()
    cell = _cell(
        workspace,
        "square-after-shared-double",
        ("shared-double", "square"),
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
        ("shared-double", "square"),
    )
    scaled = _cell(
        workspace,
        "square-after-scale-double",
        ("scale-double", "square"),
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
    assert len(shared.boundary_lineage_before(1)) == 2
    assert len(scaled.boundary_lineage_before(1)) == 1
    assert shared.whole.history != scaled.whole.history
    assert shared.whole.source_partition != scaled.whole.source_partition


def test_unit_insertion_is_an_explicit_empty_stage_not_history_equality():
    workspace = _workspace()
    direct = _cell(
        workspace,
        "square-after-shared-double",
        ("shared-double", "square"),
    )
    through_unit = _cell(
        workspace,
        "square-after-shared-double-through-identity",
        ("shared-double", "identity", "square"),
    )

    assert through_unit.segments[1] == CallSegment(
        "program-cells/identity", ()
    )
    assert direct.whole.ir["nodes"] == through_unit.whole.ir["nodes"]
    assert direct.whole.history != through_unit.whole.history

    for value in (-2.0, 0.0, 2.0):
        assert direct.temporal_value(value) == through_unit.temporal_value(value)
