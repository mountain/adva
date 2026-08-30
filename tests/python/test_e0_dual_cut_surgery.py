from __future__ import annotations

import json
from collections.abc import Hashable, Mapping
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import gcd
from typing import Any, TypeAlias

from adva import link_modules


E0_DUAL_CUT_KERNEL = r"""
(module e0-dual-cut
  (export fork-recombine hidden-history)

  (def fork-recombine-expanded
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (neg (use left))
          (id (use right))))))

  (def fork-recombine
    (fn ((x Real)) Real
      (call fork-recombine-expanded
        (copy (use x)))))

  (def hidden-history
    (fn ((x Real)) Real
      (frontier
        (use x)
        (discard 1))))
)
"""


E0_NESTED_GRAFT_KERNEL = r"""
(module e0-nested-graft
  (export root)

  (def add-two
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (use left)
          (use right)))))

  (def diamond
    (fn ((left Real) (right Real)) Real
      (call add-two
        (neg (use left))
        (id (use right)))))

  (def wrapper
    (fn ((left Real) (right Real)) Real
      (call diamond
        (use left)
        (use right))))

  (def root
    (fn ((x Real)) Real
      (call wrapper
        (copy (use x)))))
)
"""


Relation: TypeAlias = frozenset[tuple[Hashable, Hashable]]


@dataclass(frozen=True, slots=True)
class ProjectivePoint:
    """One oriented homogeneous point in the minimal E0 frame."""

    x: int
    y: int

    def __post_init__(self) -> None:
        if self.x == 0 and self.y == 0:
            raise ValueError("a projective point cannot be zero")

    def j_lift(self) -> ProjectivePoint:
        """The oriented lift of J(z)=-1/z."""

        return ProjectivePoint(-self.y, self.x)

    def projective_key(self) -> tuple[int, int]:
        divisor = gcd(abs(self.x), abs(self.y))
        x = self.x // divisor
        y = self.y // divisor
        if y < 0 or (y == 0 and x < 0):
            x = -x
            y = -y
        return x, y

    @property
    def valuation(self) -> Fraction | None:
        """The point-side coordinate a=-X/Y; None denotes infinity."""

        if self.y == 0:
            return None
        return Fraction(-self.x, self.y)


@dataclass(frozen=True, slots=True)
class ProjectiveCovector:
    """One row covector transported contravariantly by J."""

    r: int
    s: int

    def star_lift(self) -> ProjectiveCovector:
        """Return phi J^-1 for J=((0,-1),(1,0))."""

        return ProjectiveCovector(-self.s, self.r)

    def pair(self, point: ProjectivePoint) -> int:
        return self.r * point.x + self.s * point.y


@dataclass(frozen=True, slots=True)
class PrimalEdge:
    """One checked linear wire and its declared cellular-dual endpoints."""

    edge_id: str
    producer: str
    consumer: str
    dual_vertices: tuple[str, str]
    cut_wire: dict[str, Any]


@dataclass(frozen=True, slots=True)
class DecoratedDualCut:
    """A research-local dual cycle retaining its checked causal past."""

    completed: frozenset[int]
    cycle: frozenset[str]


@dataclass(frozen=True, slots=True)
class DecodedCutView:
    """A read-only view reconstructed from checked wires, not a judgment."""

    completed: tuple[int, ...]
    frontier: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class E0EdgeCoordinate:
    """One declared finite chart from a checked wire to G and J(G)."""

    edge_id: str
    primal: ProjectivePoint
    dual: ProjectivePoint


@dataclass(frozen=True, slots=True)
class FrameEventRole:
    """One exact graft-frame incidence carried by one event surgery."""

    frame_id: str
    scope_path: str
    region_in_parent: str
    event_region: str


@dataclass(frozen=True, slots=True)
class FrameDecoratedFaceSurgery:
    """One event boundary on the dual graph, decorated without duplication."""

    event: int
    boundary: frozenset[str]
    dual_coordinates: frozenset[tuple[int, int]]
    frame_roles: tuple[FrameEventRole, ...]


@dataclass(frozen=True, slots=True)
class NestedGridInputExpression:
    frame_stack: tuple[tuple[str, str, str], ...]
    ordered_holes: tuple[tuple[str, tuple[tuple[int, str], ...]], ...]
    entry_wires: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class NestedGridOutputExpression:
    frame_stack: tuple[tuple[str, str, str], ...]
    body_events: tuple[int, ...]
    exit_wires: tuple[str, ...]


class DiamondDualPresentation:
    """Declared planar dual presentation of the checked fork-recombine DAG.

    P-star encodes one Rust-certified cut as a decorated dual cycle.  P reads
    that cycle back through the same pre-indexed checked wires.  Neither map
    allocates semantic identities or claims to be a stable observer pullback.
    """

    OUTER_FACE = "outer"
    INNER_FACE = "diamond"

    def __init__(self, whole: Any) -> None:
        if whole.validation_certificate["graph"] != "checked":
            raise ValueError("the dual presentation requires checked IR")
        self.whole = whole
        self.node_order = tuple(node["id"] for node in whole.ir["nodes"])
        self.edges = self._build_edges()
        self.edge_order = tuple(edge.edge_id for edge in self.edges)
        self.edge_by_id = {edge.edge_id: edge for edge in self.edges}
        self.event_boundaries = self._event_boundaries()

    def encode_cut(self, cut: Any) -> DecoratedDualCut:
        certificate = cut.certificate
        if certificate["diagram_integrity"] != "checked":
            raise ValueError("P-star accepts only Rust-certified causal cuts")
        by_consumer = {
            self._consumer_key(edge.cut_wire["consumer"]): edge.edge_id
            for edge in self.edges
        }
        support = frozenset(
            by_consumer[self._consumer_key(wire["consumer"])]
            for wire in cut.frontier
        )
        return DecoratedDualCut(frozenset(cut.completed), support)

    def decode_cut(self, state: DecoratedDualCut) -> DecodedCutView:
        unknown = state.cycle - self.edge_by_id.keys()
        if unknown:
            raise ValueError(f"unknown dual edges: {sorted(unknown)}")
        completed = tuple(
            node for node in self.node_order if node in state.completed
        )
        frontier = tuple(
            self.edge_by_id[edge_id].cut_wire
            for edge_id in self.edge_order
            if edge_id in state.cycle
        )
        return DecodedCutView(completed, frontier)

    def surgery(self, state: DecoratedDualCut, event: int) -> DecoratedDualCut:
        if event in state.completed:
            raise ValueError("a completed event cannot cross the cut twice")
        predecessors = self.predecessors[event]
        if not predecessors <= state.completed:
            raise ValueError("dual surgery requires an enabled event")
        return DecoratedDualCut(
            state.completed | {event},
            state.cycle ^ self.event_boundaries[event],
        )

    @property
    def predecessors(self) -> dict[int, frozenset[int]]:
        return {
            node["id"]: frozenset(
                wire["producer"]["node"]
                for wire in node["inputs"]
                if wire["producer"]["kind"] == "node"
            )
            for node in self.whole.ir["nodes"]
        }

    def completed_pasts(self) -> tuple[frozenset[int], ...]:
        nodes = self.node_order
        return tuple(
            selected
            for size in range(len(nodes) + 1)
            for choice in combinations(nodes, size)
            if self._is_past(selected := frozenset(choice))
        )

    def enabled(self, completed: frozenset[int]) -> tuple[int, ...]:
        return tuple(
            node
            for node in self.node_order
            if node not in completed and self.predecessors[node] <= completed
        )

    def schedules(self) -> tuple[tuple[int, ...], ...]:
        target = frozenset(self.node_order)
        result: list[tuple[int, ...]] = []

        def visit(completed: frozenset[int], prefix: tuple[int, ...]) -> None:
            if completed == target:
                result.append(prefix)
                return
            for event in self.enabled(completed):
                visit(completed | {event}, (*prefix, event))

        visit(frozenset(), ())
        return tuple(result)

    def foata_layers(self) -> tuple[tuple[int, ...], ...]:
        depth: dict[int, int] = {}
        for node in self.node_order:
            parents = self.predecessors[node]
            depth[node] = 0 if not parents else 1 + max(depth[item] for item in parents)
        return tuple(
            tuple(node for node in self.node_order if depth[node] == level)
            for level in range(max(depth.values()) + 1)
        )

    def is_mod_two_cycle(self, support: frozenset[str]) -> bool:
        parity = {self.OUTER_FACE: 0, self.INNER_FACE: 0}
        for edge_id in support:
            left, right = self.edge_by_id[edge_id].dual_vertices
            parity[left] ^= 1
            parity[right] ^= 1
        return all(value == 0 for value in parity.values())

    def _is_past(self, selected: frozenset[int]) -> bool:
        return all(self.predecessors[node] <= selected for node in selected)

    def _build_edges(self) -> tuple[PrimalEdge, ...]:
        nodes = self.whole.ir["nodes"]
        if [node["operation"]["name"] for node in nodes] != [
            "copy",
            "neg",
            "id",
            "add",
        ]:
            raise ValueError("the declared diamond embedding no longer matches the IR")

        cut_wires = self._all_cut_wires()
        dual_endpoints = {
            "node:0:0": (self.OUTER_FACE, self.OUTER_FACE),
            "node:1:0": (self.OUTER_FACE, self.INNER_FACE),
            "node:2:0": (self.OUTER_FACE, self.INNER_FACE),
            "node:3:0": (self.OUTER_FACE, self.INNER_FACE),
            "node:3:1": (self.OUTER_FACE, self.INNER_FACE),
            "output:0": (self.OUTER_FACE, self.OUTER_FACE),
        }
        if set(cut_wires) != set(dual_endpoints):
            raise ValueError(
                "the checked wire set no longer matches the cellular model"
            )
        return tuple(
            PrimalEdge(
                edge_id=edge_id,
                producer=self._producer_key(wire["wire"]["producer"]),
                consumer=edge_id,
                dual_vertices=dual_endpoints[edge_id],
                cut_wire=wire,
            )
            for edge_id, wire in cut_wires.items()
        )

    def _all_cut_wires(self) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for cut in (
            self.whole.causal_cut(completed)
            for completed in self.completed_pasts()
        ):
            for wire in cut.frontier:
                result[self._consumer_key(wire["consumer"])] = dict(wire)
        return result

    def _event_boundaries(self) -> dict[int, frozenset[str]]:
        result: dict[int, frozenset[str]] = {}
        for node in self.node_order:
            incident = frozenset(
                edge.edge_id
                for edge in self.edges
                if edge.producer == f"node:{node}"
                or edge.consumer.startswith(f"node:{node}:")
            )
            result[node] = incident
        return result

    @staticmethod
    def _producer_key(producer: dict[str, Any]) -> str:
        if producer["kind"] == "input":
            return f"input:{producer['index']}"
        return f"node:{producer['node']}"

    @staticmethod
    def _consumer_key(consumer: dict[str, Any]) -> str:
        if consumer["kind"] == "output":
            return f"output:{consumer['index']}"
        return f"node:{consumer['node']}:{consumer['input_index']}"


def _workspace() -> Any:
    return link_modules([E0_DUAL_CUT_KERNEL])


def _diamond() -> Any:
    return _workspace().function("e0-dual-cut", "fork-recombine")


def _nested_diamond() -> Any:
    return link_modules([E0_NESTED_GRAFT_KERNEL]).function(
        "e0-nested-graft", "root"
    )


def _json_key(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _then(left: Relation, right: Relation) -> Relation:
    return frozenset(
        (source, target)
        for source, middle in left
        for candidate, target in right
        if middle == candidate
    )


def _converse(relation: Relation) -> Relation:
    return frozenset((target, source) for source, target in relation)


def _call_frame(function: Any, callee: str) -> Mapping[str, Any]:
    trace = function.graft_trace
    assert trace is not None
    return next(
        frame
        for frame in trace.result.frames
        if frame["kind"] == "call" and frame["callee"]["function"] == callee
    )


def _ordered_holes(frame: Mapping[str, Any]) -> tuple[tuple[int, str], ...]:
    return tuple(
        (hole["hole_index"], hole["hole"]["name"])
        for hole in frame["holes"]
    )


def _nested_expressions(function: Any):
    frames = tuple(
        _call_frame(function, name)
        for name in ("wrapper", "diamond", "add-two")
    )
    frame_stack = tuple(
        (
            frame["id"],
            _json_key(frame["scope_path"]),
            _json_key(frame["region_in_parent"]),
        )
        for frame in frames
    )
    input_expression = NestedGridInputExpression(
        frame_stack=frame_stack,
        ordered_holes=tuple(
            (frame["id"], _ordered_holes(frame)) for frame in frames
        ),
        entry_wires=tuple(_json_key(wire) for wire in frames[0]["entry_wires"]),
    )
    output_expression = NestedGridOutputExpression(
        frame_stack=frame_stack,
        body_events=tuple(frames[0]["body_region"]),
        exit_wires=tuple(_json_key(wire) for wire in frames[0]["exit_wires"]),
    )
    return frames, input_expression, output_expression


def _e0_edge_chart(model: DiamondDualPresentation) -> dict[str, E0EdgeCoordinate]:
    point_grid = tuple(
        ProjectivePoint(-value, 1) for value in range(-2, 3)
    ) + (ProjectivePoint(1, 0),)
    assert len(point_grid) == len(model.edge_order)
    return {
        edge_id: E0EdgeCoordinate(edge_id, point, point.j_lift())
        for edge_id, point in zip(model.edge_order, point_grid, strict=True)
    }


def _event_roles(function: Any, event: int) -> tuple[FrameEventRole, ...]:
    trace = function.graft_trace
    assert trace is not None
    roles = []
    for frame in trace.result.frames:
        if event in frame["body_region"]:
            event_region = "body"
        else:
            argument = next(
                (
                    item
                    for item in frame["arguments"]
                    if event in item["nodes"]
                ),
                None,
            )
            if argument is None:
                continue
            event_region = f"argument:{argument['argument_index']}"
        roles.append(
            FrameEventRole(
                frame_id=frame["id"],
                scope_path=_json_key(frame["scope_path"]),
                region_in_parent=_json_key(frame["region_in_parent"]),
                event_region=event_region,
            )
        )
    return tuple(roles)


def _decorated_surgery(
    function: Any,
    model: DiamondDualPresentation,
    chart: Mapping[str, E0EdgeCoordinate],
    event: int,
) -> FrameDecoratedFaceSurgery:
    boundary = model.event_boundaries[event]
    return FrameDecoratedFaceSurgery(
        event=event,
        boundary=boundary,
        dual_coordinates=frozenset(
            chart[edge].dual.projective_key() for edge in boundary
        ),
        frame_roles=_event_roles(function, event),
    )


def _apply_decorated_word(
    model: DiamondDualPresentation,
    state: DecoratedDualCut,
    word: tuple[FrameDecoratedFaceSurgery, ...],
) -> DecoratedDualCut:
    for surgery in word:
        state = model.surgery(state, surgery.event)
    return state


def _coordinate_support(
    state: DecoratedDualCut,
    chart: Mapping[str, E0EdgeCoordinate],
) -> frozenset[tuple[int, int]]:
    return frozenset(chart[edge].dual.projective_key() for edge in state.cycle)


def _intersection_roles(slice_result: Any, event: int) -> set[tuple[str, str]]:
    assert slice_result.graft_intersections is not None
    result = set()
    for intersection in slice_result.graft_intersections:
        if event in intersection["body_events"]:
            result.add((intersection["frame"], "body"))
        for argument in intersection["argument_events"]:
            if event in argument["events"]:
                result.add(
                    (
                        intersection["frame"],
                        f"argument:{argument['argument_index']}",
                    )
                )
    return result


def test_minimal_projective_grid_and_covaluation_are_j_dual() -> None:
    point_grid = tuple(
        ProjectivePoint(-value, 1) for value in range(-2, 3)
    ) + (ProjectivePoint(1, 0),)
    covectors = (
        ProjectiveCovector(1, 0),
        ProjectiveCovector(0, 1),
        ProjectiveCovector(2, -3),
    )

    for point in point_grid:
        lifted_twice = point.j_lift().j_lift()
        assert lifted_twice == ProjectivePoint(-point.x, -point.y)
        assert lifted_twice.projective_key() == point.projective_key()

        value = point.valuation
        dual_value = point.j_lift().valuation
        if value is None:
            assert dual_value == 0
        elif value == 0:
            assert dual_value is None
        else:
            assert dual_value == -1 / value

        for covector in covectors:
            assert covector.pair(point) == covector.star_lift().pair(
                point.j_lift()
            )


def test_every_checked_cut_is_a_decorated_dual_cycle_and_retracts_exactly() -> None:
    whole = _diamond()
    model = DiamondDualPresentation(whole)

    for completed in model.completed_pasts():
        cut = whole.causal_cut(tuple(completed))
        state = model.encode_cut(cut)
        decoded = model.decode_cut(state)

        assert model.is_mod_two_cycle(state.cycle)
        assert decoded.completed == cut.completed
        assert decoded.frontier == cut.frontier
        assert model.encode_cut(cut) == state


def test_enabled_event_is_exactly_one_dual_face_surgery() -> None:
    whole = _diamond()
    model = DiamondDualPresentation(whole)

    for completed in model.completed_pasts():
        before = model.encode_cut(whole.causal_cut(tuple(completed)))
        for event in model.enabled(completed):
            predicted = model.surgery(before, event)
            after = whole.advance_causal_cut(tuple(completed), event).after
            actual = model.encode_cut(
                whole.causal_cut(tuple(after["completed"]))
            )

            assert model.is_mod_two_cycle(model.event_boundaries[event])
            assert predicted == actual
            assert model.decode_cut(predicted).frontier == tuple(after["frontier"])


def test_independent_surgeries_form_the_same_dual_interchange_square() -> None:
    whole = _diamond()
    model = DiamondDualPresentation(whole)
    copy, left, right, join = model.node_order
    after_copy = model.encode_cut(whole.causal_cut((copy,)))

    left_then_right = model.surgery(model.surgery(after_copy, left), right)
    right_then_left = model.surgery(model.surgery(after_copy, right), left)

    assert left_then_right == right_then_left
    assert left_then_right.completed == frozenset({copy, left, right})
    assert model.enabled(left_then_right.completed) == (join,)


def test_characteristic_surgery_word_has_a_schedule_independent_trace_form() -> None:
    whole = _diamond()
    model = DiamondDualPresentation(whole)
    schedules = model.schedules()
    final_states = []

    for schedule in schedules:
        state = model.encode_cut(whole.causal_cut(()))
        for event in schedule:
            state = model.surgery(state, event)
        final_states.append(state)

    assert len(schedules) == 2
    assert schedules[0] != schedules[1]
    assert final_states[0] == final_states[1]
    assert model.foata_layers() == (
        (model.node_order[0],),
        (model.node_order[1], model.node_order[2]),
        (model.node_order[3],),
    )


def test_bare_terminal_cycle_does_not_recover_hidden_history() -> None:
    whole = _workspace().function("e0-dual-cut", "hidden-history")
    initial = whole.causal_cut(())
    final = whole.causal_cut(tuple(node["id"] for node in whole.ir["nodes"]))

    assert initial.frontier == final.frontier
    assert initial.completed != final.completed
    assert [node["operation"]["name"] for node in whole.ir["nodes"]] == [
        "constant",
        "discard",
    ]


def test_current_call_history_is_not_a_scope_faithful_p_star() -> None:
    whole = _diamond()
    calls = [
        event
        for event in whole.history["prefix"]
        if event["kind"] == "call"
    ]

    assert len(calls) == 1
    assert set(calls[0]) == {"kind", "function"}
    assert [port["name"] for port in whole.ir["signature"]["inputs"]] == ["x"]
    assert [node["operation"]["name"] for node in whole.ir["nodes"]] == [
        "copy",
        "neg",
        "id",
        "add",
    ]


def test_nested_two_hole_stack_is_carried_by_the_same_checked_diamond() -> None:
    function = _nested_diamond()
    wrapper, diamond, add_two = _nested_expressions(function)[0]

    assert [node["operation"]["name"] for node in function.ir["nodes"]] == [
        "copy",
        "neg",
        "id",
        "add",
    ]
    assert diamond["parent"] == wrapper["id"]
    assert add_two["parent"] == diamond["id"]
    assert diamond["region_in_parent"] == {"kind": "callee_body"}
    assert add_two["region_in_parent"] == {"kind": "callee_body"}
    assert wrapper["body_region"] == [1, 2, 3]
    assert diamond["body_region"] == [1, 2, 3]
    assert add_two["arguments"][0]["nodes"] == [1]
    assert add_two["arguments"][1]["nodes"] == [2]
    assert add_two["body_region"] == [3]
    assert _ordered_holes(wrapper) == ((0, "left"), (1, "right"))
    assert _ordered_holes(diamond) == ((0, "left"), (1, "right"))
    assert _ordered_holes(add_two) == ((0, "left"), (1, "right"))


def test_each_dual_face_surgery_carries_every_exact_frame_role_once() -> None:
    function = _nested_diamond()
    model = DiamondDualPresentation(function)
    chart = _e0_edge_chart(model)
    lower_by_event = {1: (0,), 2: (0,), 3: (0, 1, 2)}

    assert len(chart) == 6
    assert len(
        {item.primal.projective_key() for item in chart.values()}
    ) == len(chart)
    assert len(
        {item.dual.projective_key() for item in chart.values()}
    ) == len(chart)

    for event, lower in lower_by_event.items():
        surgery = _decorated_surgery(function, model, chart, event)
        upper = (*lower, event)
        program_slice = function.program_slice(lower, upper)
        expected_roles = _intersection_roles(program_slice.result, event)
        decorated_roles = {
            (role.frame_id, role.event_region) for role in surgery.frame_roles
        }
        before = model.encode_cut(function.causal_cut(lower))
        after = model.surgery(before, event)

        assert decorated_roles == expected_roles
        assert len(surgery.frame_roles) == len(decorated_roles)
        assert model.is_mod_two_cycle(surgery.boundary)
        assert _coordinate_support(after, chart) == (
            _coordinate_support(before, chart) ^ surgery.dual_coordinates
        )
        assert all(
            chart[edge].dual == chart[edge].primal.j_lift()
            for edge in surgery.boundary
        )


def test_decorated_surgeries_compose_over_adjacent_slices_without_duplication():
    function = _nested_diamond()
    model = DiamondDualPresentation(function)
    chart = _e0_edge_chart(model)
    start = model.encode_cut(function.causal_cut((0,)))
    schedules = tuple(schedule[1:] for schedule in model.schedules())
    words = tuple(
        tuple(
            _decorated_surgery(function, model, chart, event)
            for event in schedule
        )
        for schedule in schedules
    )
    final_states = tuple(
        _apply_decorated_word(model, start, word) for word in words
    )

    assert schedules == ((1, 2, 3), (2, 1, 3))
    assert final_states[0] == final_states[1]
    for word in words:
        assert [surgery.event for surgery in word] in ([1, 2, 3], [2, 1, 3])
        assert len({surgery.event for surgery in word}) == len(word)

    composed = function.compose_program_slices(
        (0,),
        (0, 1),
        (0, 1, 2, 3),
    )
    direct = function.program_slice((0,), (0, 1, 2, 3))
    first_word = words[0]
    left_state = _apply_decorated_word(model, start, first_word[:1])
    glued_state = _apply_decorated_word(model, left_state, first_word[1:])

    assert composed.result == direct.result
    assert composed.certificate["exact_composition"] == "checked"
    assert composed.certificate["left_event_ids"] == [1]
    assert composed.certificate["right_event_ids"] == [2, 3]
    assert glued_state == final_states[0]


def test_nested_e0_characteristic_relation_factors_forward_and_reverse():
    function = _nested_diamond()
    model = DiamondDualPresentation(function)
    chart = _e0_edge_chart(model)
    _, input_expression, output_expression = _nested_expressions(function)
    start = model.encode_cut(function.causal_cut((0,)))
    schedules = tuple(schedule[1:] for schedule in model.schedules())
    words = tuple(
        tuple(
            _decorated_surgery(function, model, chart, event)
            for event in schedule
        )
        for schedule in schedules
    )
    characteristic: Relation = frozenset(
        (start, _apply_decorated_word(model, start, word)) for word in words
    )
    final = next(iter(characteristic))[1]
    p_star_input: Relation = frozenset({(input_expression, start)})
    p_output: Relation = frozenset({(final, output_expression)})
    transformation: Relation = frozenset(
        {(input_expression, output_expression)}
    )

    assert len(characteristic) == 1
    assert _then(_then(p_star_input, characteristic), p_output) == transformation
    assert _then(
        _then(_converse(p_output), _converse(characteristic)),
        _converse(p_star_input),
    ) == _converse(transformation)
