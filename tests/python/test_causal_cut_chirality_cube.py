from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, permutations
from typing import Any

import sympy
from adva import link_modules

CAUSAL_CUT_CHIRALITY_KERNEL = r"""
(module causal-cut-chirality
  (export triple-independent)

  (def fork-tail
    (fn ((left Real) (right Real)) (outputs Real Real Real)
      (frontier
        (use left)
        (copy (use right)))))

  (def fork-three
    (fn ((x Real)) (outputs Real Real Real)
      (call fork-tail
        (copy (use x)))))

  (def independent-branches
    (fn ((t Real) (s Real) (r Real)) (outputs Real Real Real)
      (frontier
        (neg (use t))
        (scale 2 (use s))
        (id (use r)))))

  (def sum-three
    (fn ((a Real) (b Real) (c Real)) Real
      (add
        (frontier
          (use a)
          (add
            (frontier
              (use b)
              (use c)))))))

  (def triple-independent
    (fn ((x Real)) Real
      (call sum-three
        (call independent-branches
          (call fork-three
            (use x))))))
)
"""


@dataclass(frozen=True, order=True, slots=True)
class WireKey:
    producer_kind: str
    producer_id: int
    output_index: int


@dataclass(frozen=True, order=True, slots=True)
class CutPort:
    """One checked wire crossing a completed causal past."""

    wire: WireKey
    value_type: str
    lineage: tuple[str, ...]
    sources: tuple[str, ...]
    consumer_kind: str
    consumer_id: int


@dataclass(frozen=True, slots=True)
class CubeEvent:
    node_id: int
    operation: str
    predecessors: frozenset[int]
    consumed: tuple[WireKey, ...]


@dataclass(frozen=True, slots=True)
class CubeEdge:
    start_mask: int
    end_mask: int
    direction: int
    event: CubeEvent
    before: tuple[CutPort, ...]
    after: tuple[CutPort, ...]
    consumed: tuple[CutPort, ...]
    produced: tuple[CutPort, ...]


@dataclass(frozen=True, slots=True)
class CheckedCausalDiagram:
    """Research reader for causal cuts and checked frontier wires."""

    whole: Any

    def __post_init__(self) -> None:
        if self.whole.validation_certificate["graph"] != "checked":
            raise ValueError("the causal cube requires a Rust-checked diagram")

    @property
    def events(self) -> tuple[CubeEvent, ...]:
        return tuple(
            CubeEvent(
                node_id=node["id"],
                operation=node["operation"]["name"],
                predecessors=frozenset(
                    wire["producer"]["node"]
                    for wire in node["inputs"]
                    if wire["producer"]["kind"] == "node"
                ),
                consumed=tuple(_wire_key(wire) for wire in node["inputs"]),
            )
            for node in self.whole.ir["nodes"]
        )

    @property
    def event_ids(self) -> frozenset[int]:
        return frozenset(event.node_id for event in self.events)

    @property
    def opens(self) -> tuple[frozenset[int], ...]:
        ordered = tuple(event.node_id for event in self.events)
        return tuple(
            candidate
            for size in range(len(ordered) + 1)
            for selected in combinations(ordered, size)
            for candidate in (frozenset(selected),)
            if self.is_open(candidate)
        )

    def is_open(self, completed: frozenset[int]) -> bool:
        if not completed <= self.event_ids:
            return False
        event_by_id = {event.node_id: event for event in self.events}
        return all(event_by_id[event_id].predecessors <= completed for event_id in completed)

    def enabled(self, completed: frozenset[int]) -> tuple[CubeEvent, ...]:
        if not self.is_open(completed):
            raise ValueError("enabled events require a completed causal past")
        return tuple(
            event
            for event in self.events
            if event.node_id not in completed and event.predecessors <= completed
        )

    def frontier(self, completed: frozenset[int]) -> tuple[CutPort, ...]:
        if not self.is_open(completed):
            raise ValueError("frontiers require a completed causal past")

        occurrence_sources = {
            occurrence["id"]: occurrence["source"] for occurrence in self.whole.ir["occurrences"]
        }
        consumers = (
            *(
                ("node", node["id"], wire)
                for node in self.whole.ir["nodes"]
                for wire in node["inputs"]
            ),
            *(
                ("output", output_index, wire)
                for output_index, wire in enumerate(self.whole.ir["outputs"])
            ),
        )
        crossing: list[CutPort] = []
        for consumer_kind, consumer_id, wire in consumers:
            producer = wire["producer"]
            producer_ready = producer["kind"] == "input" or (
                producer["kind"] == "node" and producer["node"] in completed
            )
            consumer_waiting = consumer_kind == "output" or consumer_id not in completed
            if producer_ready and consumer_waiting:
                lineage = tuple(wire["lineage"])
                crossing.append(
                    CutPort(
                        wire=_wire_key(wire),
                        value_type=wire["value_type"],
                        lineage=lineage,
                        sources=tuple(occurrence_sources[item] for item in lineage),
                        consumer_kind=consumer_kind,
                        consumer_id=consumer_id,
                    )
                )
        return tuple(sorted(crossing))

    def local_independence_cube(self) -> LocalIndependenceCube:
        candidates: list[tuple[frozenset[int], tuple[CubeEvent, ...]]] = []
        for completed in self.opens:
            enabled = self.enabled(completed)
            for directions in combinations(enabled, 3):
                consumed = tuple(frozenset(event.consumed) for event in directions)
                if any(
                    consumed[left] & consumed[right] for left, right in combinations(range(3), 2)
                ):
                    continue
                if {event.operation for event in directions} == {"neg", "scale", "id"}:
                    candidates.append(
                        (
                            completed,
                            tuple(sorted(directions, key=lambda event: event.node_id)),
                        )
                    )
        if len(candidates) != 1:
            raise AssertionError(
                f"expected one checked three-direction cube, found {len(candidates)}"
            )
        base, directions = candidates[0]
        return LocalIndependenceCube(self, base, directions)


@dataclass(frozen=True, slots=True)
class LocalIndependenceCube:
    """The Boolean interval generated by three independent checked events."""

    diagram: CheckedCausalDiagram
    base: frozenset[int]
    directions: tuple[CubeEvent, CubeEvent, CubeEvent]

    def completed(self, mask: int) -> frozenset[int]:
        if not 0 <= mask < 8:
            raise ValueError("a three-direction cube mask must lie in [0, 8)")
        return self.base | frozenset(
            event.node_id
            for direction, event in enumerate(self.directions)
            if mask & (1 << direction)
        )

    def coordinate(self, mask: int, direction: int) -> int:
        event_id = self.directions[direction].node_id
        return int(event_id in self.completed(mask))

    def edge(self, mask: int, direction: int) -> CubeEdge:
        if mask & (1 << direction):
            raise ValueError("an oriented cube edge must cross a missing event forward")
        completed = self.completed(mask)
        event = self.directions[direction]
        if event not in self.diagram.enabled(completed):
            raise AssertionError("a declared cube direction was not causally enabled")

        before = self.diagram.frontier(completed)
        after = self.diagram.frontier(completed | {event.node_id})
        before_set = frozenset(before)
        after_set = frozenset(after)
        return CubeEdge(
            start_mask=mask,
            end_mask=mask | (1 << direction),
            direction=direction,
            event=event,
            before=before,
            after=after,
            consumed=tuple(port for port in before if port not in after_set),
            produced=tuple(port for port in after if port not in before_set),
        )

    @property
    def incidence_pairing(self) -> tuple[tuple[int, int, int], ...]:
        """Pair cut-membership cochains with forward generation edges."""

        return tuple(
            tuple(
                self.coordinate(self.edge(0, edge_direction).end_mask, cut_direction)
                - self.coordinate(0, cut_direction)
                for edge_direction in range(3)
            )
            for cut_direction in range(3)
        )

    def transport(self, schedule: tuple[int, ...]) -> tuple[CubeEdge, ...]:
        mask = 0
        edges: list[CubeEdge] = []
        for direction in schedule:
            edge = self.edge(mask, direction)
            edges.append(edge)
            mask = edge.end_mask
        return tuple(edges)


Form = tuple[int, int, int, int, int, int, int, int]
Pairing = tuple[tuple[int, int, int], ...]

CARRIER_BASIS = (
    (0b001, 1),
    (0b010, 1),
    (0b100, 1),
    (0b110, 1),
    (0b101, -1),
    (0b011, 1),
)


def _wire_key(wire: dict[str, Any]) -> WireKey:
    producer = wire["producer"]
    return WireKey(
        producer_kind=producer["kind"],
        producer_id=producer.get("node", producer.get("index")),
        output_index=wire["output_index"],
    )


def _cube() -> LocalIndependenceCube:
    workspace = link_modules([CAUSAL_CUT_CHIRALITY_KERNEL])
    whole = workspace.function("causal-cut-chirality", "triple-independent")
    return CheckedCausalDiagram(whole).local_independence_cube()


def _basis_form(mask: int, coefficient: int = 1) -> Form:
    return tuple(coefficient if index == mask else 0 for index in range(8))  # type: ignore[return-value]


def _add_forms(left: Form, right: Form) -> Form:
    return tuple(a + b for a, b in zip(left, right, strict=True))  # type: ignore[return-value]


def _scale_form(scale: int, value: Form) -> Form:
    return tuple(scale * coefficient for coefficient in value)  # type: ignore[return-value]


def _wedge(direction: int, value: Form) -> Form:
    """Left exterior multiplication with orientation supplied by cube order."""

    output = [0] * 8
    bit = 1 << direction
    for blade, coefficient in enumerate(value):
        if coefficient == 0 or blade & bit:
            continue
        lower_directions = blade & (bit - 1)
        sign = -1 if lower_directions.bit_count() % 2 else 1
        output[blade | bit] += sign * coefficient
    return tuple(output)  # type: ignore[return-value]


def _contract(direction: int, value: Form, pairing: Pairing) -> Form:
    """Contract by the cut cochain dual to one forward generation direction."""

    output = [0] * 8
    for blade, coefficient in enumerate(value):
        if coefficient == 0:
            continue
        factors = tuple(index for index in range(3) if blade & (1 << index))
        for position, factor in enumerate(factors):
            paired = pairing[direction][factor]
            if paired:
                output[blade ^ (1 << factor)] += (-1 if position % 2 else 1) * paired * coefficient
    return tuple(output)  # type: ignore[return-value]


def _clifford(direction: int, value: Form, pairing: Pairing) -> Form:
    """The derived wedge-plus-cut-contraction action."""

    return _add_forms(
        _wedge(direction, value),
        _contract(direction, value, pairing),
    )


def _word(
    directions: tuple[int, ...],
    value: Form,
    action: Any,
    pairing: Pairing | None = None,
) -> Form:
    output = value
    for direction in reversed(directions):
        output = (
            action(direction, output, pairing) if pairing is not None else action(direction, output)
        )
    return output


def _volume_action(value: Form, pairing: Pairing) -> Form:
    return _word((0, 1, 2), value, _clifford, pairing)


def _permutation_sign(permutation: tuple[int, int, int]) -> int:
    inversions = sum(
        permutation[left] > permutation[right] for left in range(3) for right in range(left + 1, 3)
    )
    return -1 if inversions % 2 else 1


def _inverse_permutation(permutation: tuple[int, int, int]) -> tuple[int, int, int]:
    inverse = [0, 0, 0]
    for source, target in enumerate(permutation):
        inverse[target] = source
    return tuple(inverse)  # type: ignore[return-value]


def _permute_form(value: Form, permutation: tuple[int, int, int]) -> Form:
    output = [0] * 8
    for blade, coefficient in enumerate(value):
        if coefficient == 0:
            continue
        targets = [permutation[index] for index in range(3) if blade & (1 << index)]
        inversions = sum(
            targets[left] > targets[right]
            for left in range(len(targets))
            for right in range(left + 1, len(targets))
        )
        output_blade = sum(1 << target for target in targets)
        output[output_blade] += (-1 if inversions % 2 else 1) * coefficient
    return tuple(output)  # type: ignore[return-value]


def _carrier_matrix(pairing: Pairing) -> sympy.Matrix:
    columns: list[sympy.Matrix] = []
    for input_blade, input_sign in CARRIER_BASIS:
        output = _volume_action(_basis_form(input_blade, input_sign), pairing)
        coordinates = []
        for output_blade, output_sign in CARRIER_BASIS:
            coordinates.append(output[output_blade] // output_sign)
        assert all(
            coefficient == 0
            for blade, coefficient in enumerate(output)
            if blade not in {item[0] for item in CARRIER_BASIS}
        )
        columns.append(sympy.Matrix(coordinates))
    return sympy.Matrix.hstack(*columns)


def test_checked_relation_generation_boundary_data_form_one_local_three_cube() -> None:
    cube = _cube()
    whole = cube.diagram.whole

    assert whole.signature.inputs == (("x", "real"),)
    assert whole.signature.outputs == ("real",)
    assert whole.evaluate({"x": 3.0}) == 6.0
    assert tuple(event.operation for event in cube.directions) == ("neg", "scale", "id")

    vertices = tuple(cube.completed(mask) for mask in range(8))
    assert len(set(vertices)) == 8
    assert all(cube.diagram.is_open(vertex) for vertex in vertices)

    base_frontier = cube.diagram.frontier(cube.base)
    object_ports = tuple(port for port in base_frontier if port.sources)
    parameter_ports = tuple(port for port in base_frontier if not port.sources)
    assert len(object_ports) == 3
    assert len(parameter_ports) == 1
    assert all(port.value_type == "real" for port in base_frontier)
    assert len({port.lineage for port in object_ports}) == 3
    assert len({source for port in object_ports for source in port.sources}) == 1
    assert parameter_ports[0].lineage == ()

    for mask in range(8):
        for direction in range(3):
            if not mask & (1 << direction):
                edge = cube.edge(mask, direction)
                consumed_objects = tuple(port for port in edge.consumed if port.sources)
                produced_objects = tuple(port for port in edge.produced if port.sources)
                assert len(consumed_objects) == 1
                assert len(produced_objects) == 1
                assert {source for port in consumed_objects for source in port.sources} == {
                    source for port in produced_objects for source in port.sources
                }


def test_all_six_schedules_and_all_six_interchange_faces_close_on_checked_frontiers() -> None:
    cube = _cube()
    schedules = tuple(permutations(range(3)))
    transports = tuple(cube.transport(schedule) for schedule in schedules)

    assert len(transports) == 6
    assert all(transport[-1].end_mask == 0b111 for transport in transports)
    final_frontiers = {
        cube.diagram.frontier(cube.completed(transport[-1].end_mask)) for transport in transports
    }
    assert len(final_frontiers) == 1

    face_count = 0
    for first, second in combinations(range(3), 2):
        remaining = next(direction for direction in range(3) if direction not in {first, second})
        for remaining_state in (0, 1):
            start = remaining_state << remaining
            first_then_second = (
                cube.edge(start, first),
                cube.edge(start | (1 << first), second),
            )
            second_then_first = (
                cube.edge(start, second),
                cube.edge(start | (1 << second), first),
            )
            assert first_then_second[-1].after == second_then_first[-1].after
            assert not (
                frozenset(first_then_second[0].consumed) & frozenset(second_then_first[0].consumed)
            )
            face_count += 1
    assert face_count == 6


def test_cut_coordinates_are_the_exact_duals_of_forward_generation_edges() -> None:
    cube = _cube()
    assert cube.incidence_pairing == (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    )

    for mask in range(8):
        for edge_direction in range(3):
            if mask & (1 << edge_direction):
                continue
            edge = cube.edge(mask, edge_direction)
            for cut_direction in range(3):
                difference = cube.coordinate(edge.end_mask, cut_direction) - cube.coordinate(
                    edge.start_mask, cut_direction
                )
                assert difference == int(cut_direction == edge_direction)


def test_interchange_orientation_and_cut_contraction_derive_clifford_relations() -> None:
    pairing = _cube().incidence_pairing

    for blade in range(8):
        value = _basis_form(blade)
        for left in range(3):
            for right in range(3):
                anticommutator = _add_forms(
                    _clifford(left, _clifford(right, value, pairing), pairing),
                    _clifford(right, _clifford(left, value, pairing), pairing),
                )
                expected = _scale_form(2 if left == right else 0, value)
                assert anticommutator == expected

    scalar = _basis_form(0)
    for left, right in combinations(range(3), 2):
        left_then_right = _word((left, right), scalar, _wedge)
        right_then_left = _word((right, left), scalar, _wedge)
        assert left_then_right == _scale_form(-1, right_then_left)


def test_interchange_alone_is_nilpotent_but_cut_duality_makes_volume_complex() -> None:
    pairing = _cube().incidence_pairing
    scalar = _basis_form(0)

    exterior_volume = _word((0, 1, 2), scalar, _wedge)
    assert exterior_volume == _basis_form(0b111)
    assert _word((0, 1, 2), exterior_volume, _wedge) == _scale_form(0, scalar)

    for blade in range(8):
        value = _basis_form(blade)
        assert _volume_action(_volume_action(value, pairing), pairing) == _scale_form(
            -1,
            value,
        )


def test_derived_volume_recovers_three_pairs_spectrum_and_chirality_reversal() -> None:
    pairing = _cube().incidence_pairing
    volume = _carrier_matrix(pairing)
    pair_action = sympy.Matrix([[0, -1], [1, 0]])

    for aspect, opposite_face in ((0, 3), (1, 4), (2, 5)):
        assert (
            volume.extract(
                (aspect, opposite_face),
                (aspect, opposite_face),
            )
            == pair_action
        )

    spectral_parameter = sympy.symbols("lambda")
    assert volume**2 == -sympy.eye(6)
    assert (
        sympy.factor(volume.charpoly(spectral_parameter).as_expr())
        == (spectral_parameter**2 + 1) ** 3
    )

    for permutation in permutations(range(3)):
        inverse = _inverse_permutation(permutation)
        parity = _permutation_sign(permutation)
        for blade in range(8):
            value = _basis_form(blade)
            conjugated = _permute_form(
                _volume_action(_permute_form(value, inverse), pairing),
                permutation,
            )
            assert conjugated == _scale_form(
                parity,
                _volume_action(value, pairing),
            )
