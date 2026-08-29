from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Any

from adva import link_modules

OCCURRENCE_AFFINE_KERNEL = r"""
(module occurrence-affine
  (export square shifted-square shared-double scale-double fork-recombine-expanded)

  (def square
    (fn ((x Real)) Real
      (mul (copy (use x)))))

  (def shifted-square
    (fn ((x Real)) Real
      (mul (copy (add (use x) 1)))))

  (def shared-double
    (fn ((x Real)) Real
      (add (copy (use x)))))

  (def scale-double
    (fn ((x Real)) Real
      (scale 2 (use x))))

  (def fork-recombine-expanded
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (neg (use left))
          (mul (copy (use right)))))))
)
"""


@dataclass(frozen=True, order=True, slots=True)
class WireKey:
    """Canonical identity derived from one checked wire producer."""

    producer_kind: str
    producer_id: int
    output_index: int


@dataclass(frozen=True, order=True, slots=True)
class LiftedHole:
    """A future-demand lift of one raw cut wire.

    ``origin`` is checked data. ``copy_path`` is derived entirely from checked
    copy nodes and branch indices, so this test-local adapter allocates no
    semantic source or occurrence identity.
    """

    origin: WireKey
    copy_path: tuple[tuple[int, int], ...]
    lineage: tuple[str, ...]
    sources: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Expr:
    """An expression-valued boundary term, not a scalar coordinate."""

    operation: str
    arguments: tuple[Expr, ...] = ()
    data: tuple[Any, ...] = ()

    @classmethod
    def source(cls, occurrence: str, source: str, input_name: str) -> Expr:
        return cls("source", data=(occurrence, source, input_name))

    @classmethod
    def hole(cls, hole: LiftedHole) -> Expr:
        return cls("hole", data=(hole,))

    @classmethod
    def constant(cls, numerator: int, denominator: int, node_id: int) -> Expr:
        return cls("constant", data=(numerator, denominator, node_id))

    @classmethod
    def apply(cls, operation: str, node_id: int, *arguments: Expr) -> Expr:
        return cls(operation, tuple(arguments), (node_id,))

    @property
    def holes(self) -> frozenset[LiftedHole]:
        if self.operation == "hole":
            return frozenset({self.data[0]})
        return frozenset().union(*(argument.holes for argument in self.arguments))

    def degree(self, hole: LiftedHole) -> int:
        if self.operation == "hole":
            return int(self.data[0] == hole)
        if self.operation in {"source", "constant"}:
            return 0
        child_degrees = tuple(argument.degree(hole) for argument in self.arguments)
        if self.operation in {"mul", "scale"}:
            return sum(child_degrees)
        return max(child_degrees, default=0)

    @property
    def is_occurrence_multiaffine(self) -> bool:
        return all(self.degree(hole) <= 1 for hole in self.holes)

    def replace_holes(self, replacement: Callable[[LiftedHole], Expr]) -> Expr:
        if self.operation == "hole":
            return replacement(self.data[0])
        return Expr(
            self.operation,
            tuple(argument.replace_holes(replacement) for argument in self.arguments),
            self.data,
        )

    def relabel_sources(self, occurrence_map: dict[str, str]) -> Expr:
        if self.operation == "source":
            occurrence, source, input_name = self.data
            return Expr.source(occurrence_map.get(occurrence, occurrence), source, input_name)
        return Expr(
            self.operation,
            tuple(argument.relabel_sources(occurrence_map) for argument in self.arguments),
            self.data,
        )


Polynomial = dict[tuple[str, ...], Fraction]


def _add_polynomials(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, Fraction()) + coefficient
        if result[monomial] == 0:
            del result[monomial]
    return result


def _multiply_polynomials(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(sorted((*left_monomial, *right_monomial)))
            result[monomial] = (
                result.get(monomial, Fraction()) + left_coefficient * right_coefficient
            )
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def _polynomial(expression: Expr, source_key: str = "occurrence") -> Polynomial:
    """A commutative Real shadow used only for bounded comparison."""

    if expression.operation == "source":
        occurrence, source, input_name = expression.data
        if source_key == "occurrence":
            label = occurrence
        elif source_key == "source":
            label = source
        elif source_key == "input":
            label = input_name
        else:
            raise ValueError(f"unknown polynomial variable chart {source_key!r}")
        return {(label,): Fraction(1)}
    if expression.operation == "hole":
        return {(repr(expression.data[0]),): Fraction(1)}
    if expression.operation == "constant":
        numerator, denominator, _ = expression.data
        return {(): Fraction(numerator, denominator)}
    arguments = tuple(_polynomial(argument, source_key) for argument in expression.arguments)
    if expression.operation in {"id"}:
        return arguments[0]
    if expression.operation == "neg":
        return {monomial: -coefficient for monomial, coefficient in arguments[0].items()}
    if expression.operation == "add":
        return _add_polynomials(arguments[0], arguments[1])
    if expression.operation in {"mul", "scale"}:
        return _multiply_polynomials(arguments[0], arguments[1])
    raise TypeError(f"operation {expression.operation!r} is outside the AM calibration")


@dataclass(frozen=True, slots=True)
class OccurrenceAffineCut:
    """One expression-valued lift of a Rust-checked causal cut."""

    diagram: MappingView
    completed: frozenset[int]
    boundary_values: tuple[tuple[WireKey, Expr], ...]
    residual_outputs: tuple[Expr, ...]
    copy_maps: tuple[tuple[int, tuple[tuple[tuple[str, str], ...], ...]], ...]

    @property
    def lifted_holes(self) -> frozenset[LiftedHole]:
        return frozenset().union(*(output.holes for output in self.residual_outputs))

    @property
    def is_occurrence_multiaffine(self) -> bool:
        return all(output.is_occurrence_multiaffine for output in self.residual_outputs)

    @property
    def diagonal_outputs(self) -> tuple[Expr, ...]:
        boundary = dict(self.boundary_values)
        copy_maps = {
            node_id: tuple(dict(branch) for branch in branches)
            for node_id, branches in self.copy_maps
        }

        def diagonal(hole: LiftedHole) -> Expr:
            expression = boundary[hole.origin]
            for node_id, branch in hole.copy_path:
                expression = expression.relabel_sources(copy_maps[node_id][branch])
            return expression

        return tuple(output.replace_holes(diagonal) for output in self.residual_outputs)


MappingView = dict[str, Any]


@dataclass(frozen=True, slots=True)
class OccurrenceAffineAtlas:
    """Research-local cut presentations derived from a checked PSC0 diagram."""

    whole: Any

    def __post_init__(self) -> None:
        if self.whole.validation_certificate["graph"] != "checked":
            raise ValueError("an occurrence-affine atlas requires a Rust-checked diagram")
        unsupported = {node["operation"]["name"] for node in self.diagram["nodes"]} - {
            "constant",
            "id",
            "copy",
            "add",
            "mul",
            "scale",
            "neg",
        }
        if unsupported:
            raise TypeError(f"operations outside the bounded AM fragment: {sorted(unsupported)}")

    @property
    def diagram(self) -> MappingView:
        return dict(self.whole.ir)

    @property
    def event_ids(self) -> frozenset[int]:
        return frozenset(node["id"] for node in self.diagram["nodes"])

    @property
    def occurrence_sources(self) -> dict[str, str]:
        return {
            occurrence["id"]: occurrence["source"] for occurrence in self.diagram["occurrences"]
        }

    @property
    def copy_maps(self) -> dict[int, tuple[dict[str, str], dict[str, str]]]:
        mutable: dict[int, tuple[dict[str, str], dict[str, str]]] = {}
        for event in self.diagram["history"]["prefix"]:
            if event["kind"] != "copy":
                continue
            branches = mutable.setdefault(event["node"], ({}, {}))
            for branch, child in enumerate(event["children"]):
                branches[branch][event["parent"]] = child
        return mutable

    @property
    def opens(self) -> tuple[frozenset[int], ...]:
        ordered = tuple(node["id"] for node in self.diagram["nodes"])
        predecessors = {
            node["id"]: frozenset(
                wire["producer"]["node"]
                for wire in node["inputs"]
                if wire["producer"]["kind"] == "node"
            )
            for node in self.diagram["nodes"]
        }
        return tuple(
            candidate
            for size in range(len(ordered) + 1)
            for selected in combinations(ordered, size)
            for candidate in (frozenset(selected),)
            if all(predecessors[event] <= candidate for event in candidate)
        )

    def presentation(
        self,
        completed: frozenset[int],
        *,
        lift_future_copy: bool = True,
    ) -> OccurrenceAffineCut:
        if completed not in self.opens:
            raise ValueError("the selected events are not a completed causal past")

        past_values = self._past_values(completed)
        crossing = self._crossing_wires(completed)
        future_values = {
            wire_key: Expr.hole(
                LiftedHole(
                    origin=wire_key,
                    copy_path=(),
                    lineage=tuple(wire["lineage"]),
                    sources=tuple(
                        self.occurrence_sources[occurrence] for occurrence in wire["lineage"]
                    ),
                )
            )
            for wire_key, wire in crossing.items()
        }
        for node in self.diagram["nodes"]:
            if node["id"] in completed:
                continue
            arguments = tuple(future_values[_wire_key(wire)] for wire in node["inputs"])
            outputs = self._node_outputs(node, arguments, lift_copy=lift_future_copy)
            for output_index, output in enumerate(outputs):
                future_values[WireKey("node", node["id"], output_index)] = output

        residual_outputs = tuple(future_values[_wire_key(wire)] for wire in self.diagram["outputs"])
        frozen_copy_maps = tuple(
            (
                node_id,
                tuple(tuple(sorted(branch.items())) for branch in branches),
            )
            for node_id, branches in sorted(self.copy_maps.items())
        )
        return OccurrenceAffineCut(
            diagram=self.diagram,
            completed=completed,
            boundary_values=tuple(
                (wire_key, past_values[wire_key]) for wire_key in sorted(crossing)
            ),
            residual_outputs=residual_outputs,
            copy_maps=frozen_copy_maps,
        )

    def _past_values(self, completed: frozenset[int]) -> dict[WireKey, Expr]:
        source_events = tuple(
            event for event in self.diagram["history"]["prefix"] if event["kind"] == "source"
        )
        values = {
            WireKey("input", index, 0): Expr.source(
                event["occurrence"],
                event["source"],
                port["name"],
            )
            for index, (port, event) in enumerate(
                zip(self.diagram["signature"]["inputs"], source_events, strict=True)
            )
        }
        for node in self.diagram["nodes"]:
            if node["id"] not in completed:
                continue
            arguments = tuple(values[_wire_key(wire)] for wire in node["inputs"])
            for output_index, output in enumerate(
                self._node_outputs(node, arguments, lift_copy=True)
            ):
                values[WireKey("node", node["id"], output_index)] = output
        return values

    def _crossing_wires(self, completed: frozenset[int]) -> dict[WireKey, MappingView]:
        consumers = (
            *(
                ("node", node["id"], wire)
                for node in self.diagram["nodes"]
                if node["id"] not in completed
                for wire in node["inputs"]
            ),
            *(("output", index, wire) for index, wire in enumerate(self.diagram["outputs"])),
        )
        crossing: dict[WireKey, MappingView] = {}
        for _, _, wire in consumers:
            producer = wire["producer"]
            if producer["kind"] == "input" or producer["node"] in completed:
                key = _wire_key(wire)
                if key in crossing:
                    raise AssertionError("checked linear use produced an aliased raw cut wire")
                crossing[key] = wire
        return crossing

    def _node_outputs(
        self,
        node: MappingView,
        arguments: tuple[Expr, ...],
        *,
        lift_copy: bool,
    ) -> tuple[Expr, ...]:
        operation = node["operation"]["name"]
        if operation == "constant":
            value = node["operation"]["parameters"]["value"]
            return (Expr.constant(value["numerator"], value["denominator"], node["id"]),)
        if operation == "copy":
            if not lift_copy:
                return (arguments[0], arguments[0])
            return tuple(self._lift_copy(arguments[0], node["id"], branch) for branch in range(2))
        if operation == "swap":
            return (arguments[1], arguments[0])
        if operation == "discard":
            return ()
        return (Expr.apply(operation, node["id"], *arguments),)

    def _lift_copy(self, expression: Expr, node_id: int, branch: int) -> Expr:
        occurrence_map = self.copy_maps[node_id][branch]

        def lift_hole(hole: LiftedHole) -> Expr:
            return Expr.hole(
                LiftedHole(
                    origin=hole.origin,
                    copy_path=(*hole.copy_path, (node_id, branch)),
                    lineage=tuple(occurrence_map[item] for item in hole.lineage),
                    sources=hole.sources,
                )
            )

        return expression.replace_holes(lift_hole).relabel_sources(occurrence_map)


def _wire_key(wire: MappingView) -> WireKey:
    producer = wire["producer"]
    return WireKey(
        producer_kind=producer["kind"],
        producer_id=producer.get("node", producer.get("index")),
        output_index=wire["output_index"],
    )


def _workspace() -> Any:
    return link_modules([OCCURRENCE_AFFINE_KERNEL])


def _atlas(workspace: Any, name: str) -> OccurrenceAffineAtlas:
    return OccurrenceAffineAtlas(workspace.function("occurrence-affine", name))


def test_raw_cut_is_not_multiaffine_but_checked_occurrence_lift_is() -> None:
    atlas = _atlas(_workspace(), "square")
    raw = atlas.presentation(frozenset(), lift_future_copy=False)
    lifted = atlas.presentation(frozenset())
    copy_node = next(
        node["id"] for node in atlas.diagram["nodes"] if node["operation"]["name"] == "copy"
    )

    assert len(raw.lifted_holes) == 1
    assert not raw.is_occurrence_multiaffine
    assert raw.residual_outputs[0].degree(next(iter(raw.lifted_holes))) == 2

    assert len(lifted.boundary_values) == 1
    assert len(lifted.lifted_holes) == 2
    assert len({hole.origin for hole in lifted.lifted_holes}) == 1
    assert len({hole.sources for hole in lifted.lifted_holes}) == 1
    assert lifted.is_occurrence_multiaffine
    assert {hole.copy_path for hole in lifted.lifted_holes} == {
        ((copy_node, 0),),
        ((copy_node, 1),),
    }

    after_copy = atlas.presentation(frozenset({copy_node}))
    assert len(after_copy.boundary_values) == 2
    assert len(after_copy.lifted_holes) == 2
    assert lifted.diagonal_outputs == after_copy.diagonal_outputs
    assert _polynomial(lifted.diagonal_outputs[0], "source") == {
        (
            next(iter(atlas.occurrence_sources.values())),
            next(iter(atlas.occurrence_sources.values())),
        ): Fraction(1)
    }


def test_diagonal_carries_a_boundary_expression_not_a_number() -> None:
    atlas = _atlas(_workspace(), "shifted-square")
    completed = frozenset(
        node["id"]
        for node in atlas.diagram["nodes"]
        if node["operation"]["name"] in {"constant", "add"}
    )
    raw = atlas.presentation(completed, lift_future_copy=False)
    lifted = atlas.presentation(completed)

    assert len(lifted.boundary_values) == 1
    assert lifted.boundary_values[0][1].operation == "add"
    assert not raw.is_occurrence_multiaffine
    assert lifted.is_occurrence_multiaffine
    assert len(lifted.lifted_holes) == 2

    reconstructed = lifted.diagonal_outputs[0]
    assert reconstructed.operation == "mul"
    assert tuple(argument.operation for argument in reconstructed.arguments) == ("add", "add")
    source = next(iter(atlas.occurrence_sources.values()))
    assert _polynomial(reconstructed, "source") == {
        (): Fraction(1),
        (source,): Fraction(2),
        (source, source): Fraction(1),
    }


def test_every_causal_cut_in_branch_fixture_has_one_multiaffine_lift() -> None:
    atlas = _atlas(_workspace(), "fork-recombine-expanded")
    terminal = atlas.presentation(atlas.event_ids).diagonal_outputs

    presentations = tuple(atlas.presentation(opened) for opened in atlas.opens)
    assert all(presentation.is_occurrence_multiaffine for presentation in presentations)
    assert all(presentation.diagonal_outputs == terminal for presentation in presentations)

    # The future-demand lift is essential on at least one cut: the raw wire
    # presentation repeats a single hole when an unexecuted copy is followed by mul.
    assert any(
        not atlas.presentation(opened, lift_future_copy=False).is_occurrence_multiaffine
        for opened in atlas.opens
    )

    neg = next(node["id"] for node in atlas.diagram["nodes"] if node["operation"]["name"] == "neg")
    copy = next(
        node["id"] for node in atlas.diagram["nodes"] if node["operation"]["name"] == "copy"
    )
    left_then_right = (neg, copy)
    right_then_left = (copy, neg)
    assert left_then_right != right_then_left
    assert atlas.presentation(frozenset(left_then_right)) == atlas.presentation(
        frozenset(right_then_left)
    )


def test_input_polynomial_shadow_forgets_the_shared_expression_presentation() -> None:
    workspace = _workspace()
    shared = _atlas(workspace, "shared-double")
    scaled = _atlas(workspace, "scale-double")
    shared_expression = shared.presentation(shared.event_ids).diagonal_outputs[0]
    scaled_expression = scaled.presentation(scaled.event_ids).diagonal_outputs[0]

    assert shared_expression.operation == "add"
    assert scaled_expression.operation == "scale"
    assert shared_expression != scaled_expression
    assert _polynomial(shared_expression, "occurrence") != _polynomial(
        scaled_expression,
        "occurrence",
    )
    assert _polynomial(shared_expression, "source") != _polynomial(
        scaled_expression,
        "source",
    )
    assert _polynomial(shared_expression, "input") == _polynomial(
        scaled_expression,
        "input",
    )
