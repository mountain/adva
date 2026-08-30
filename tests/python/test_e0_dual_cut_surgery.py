from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from math import gcd
from typing import Any

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
