from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Any

from adva import link_modules


CAUSAL_TOPOLOGY_KERNEL = r"""
(module causal-topology
  (export fork-recombine-expanded fork-recombine)

  (def fork-recombine-expanded
    (fn ((left Real) (right Real)) Real
      (add
        (frontier
          (scale 2 (use left))
          (mul (copy (use right)))))))

  (def fork-recombine
    (fn ((x Real)) Real
      (call fork-recombine-expanded
        (copy (use x)))))
)
"""


@dataclass(frozen=True, slots=True)
class CausalEvent:
    """One Rust-checked operation node and its immediate causal past."""

    node_id: int
    operation: str
    predecessors: frozenset[int]


@dataclass(frozen=True, slots=True)
class CutWire:
    """One checked wire crossing from a completed past to its future."""

    producer: tuple[str, int]
    output_index: int
    value_type: str
    lineage: tuple[str, ...]
    sources: tuple[str, ...]
    consumer: tuple[str, int]


@dataclass(frozen=True, slots=True)
class CausalCut:
    """A past-closed event set together with its checked open frontier."""

    completed: frozenset[int]
    frontier: tuple[CutWire, ...]


@dataclass(frozen=True, slots=True)
class CausalCutTopology:
    """The finite Alexandrov topology read from a checked operation DAG.

    The temporal reading is the dependency order on operation nodes.  The
    spatial reading is the family of completed pasts: all downward-closed
    event sets, ordered by inclusion.  Python only reads checked graph and
    lineage data; it creates no program equation or higher semantic cell.
    """

    whole: Any

    def __post_init__(self) -> None:
        if self.whole.validation_certificate["graph"] != "checked":
            raise ValueError("causal topology requires a Rust-checked diagram")

    @property
    def events(self) -> tuple[CausalEvent, ...]:
        return tuple(
            CausalEvent(
                node_id=node["id"],
                operation=node["operation"]["name"],
                predecessors=frozenset(
                    wire["producer"]["node"]
                    for wire in node["inputs"]
                    if wire["producer"]["kind"] == "node"
                ),
            )
            for node in self.whole.ir["nodes"]
        )

    @property
    def event_ids(self) -> frozenset[int]:
        return frozenset(event.node_id for event in self.events)

    @property
    def opens(self) -> tuple[frozenset[int], ...]:
        """Enumerate every past-closed event set in deterministic order."""

        ordered = tuple(event.node_id for event in self.events)
        return tuple(
            candidate
            for size in range(len(ordered) + 1)
            for selected in combinations(ordered, size)
            if self.is_open(candidate := frozenset(selected))
        )

    def is_open(self, candidate: frozenset[int]) -> bool:
        if not candidate <= self.event_ids:
            return False
        return all(
            event.predecessors <= candidate
            for event in self.events
            if event.node_id in candidate
        )

    def causally_precedes(self, earlier: int, later: int) -> bool:
        """Reachability in the checked operation DAG, including equality."""

        if earlier == later:
            return earlier in self.event_ids
        event_by_id = {event.node_id: event for event in self.events}
        pending = list(event_by_id[later].predecessors)
        visited: set[int] = set()
        while pending:
            current = pending.pop()
            if current == earlier:
                return True
            if current not in visited:
                visited.add(current)
                pending.extend(event_by_id[current].predecessors)
        return False

    def precedes_from_opens(self, earlier: int, later: int) -> bool:
        """Recover time order from the spatial family of completed pasts."""

        return all(later not in opened or earlier in opened for opened in self.opens)

    def cut(self, completed: frozenset[int]) -> CausalCut:
        if not self.is_open(completed):
            raise ValueError("a causal cut must contain the past of every event")

        occurrence_sources = {
            occurrence["id"]: occurrence["source"]
            for occurrence in self.whole.ir["occurrences"]
        }
        crossing: list[CutWire] = []
        for consumer_kind, consumer_id, wire in self._consumed_wires:
            producer = wire["producer"]
            producer_ready = (
                producer["kind"] == "input"
                or producer["node"] in completed
            )
            consumer_waiting = (
                consumer_kind == "output"
                or consumer_id not in completed
            )
            if producer_ready and consumer_waiting:
                lineage = tuple(wire["lineage"])
                crossing.append(
                    CutWire(
                        producer=(
                            producer["kind"],
                            producer.get("node", producer.get("index")),
                        ),
                        output_index=wire["output_index"],
                        value_type=wire["value_type"],
                        lineage=lineage,
                        sources=tuple(occurrence_sources[item] for item in lineage),
                        consumer=(consumer_kind, consumer_id),
                    )
                )
        return CausalCut(completed, tuple(crossing))

    @property
    def _consumed_wires(self) -> tuple[tuple[str, int, dict[str, Any]], ...]:
        node_inputs = tuple(
            ("node", node["id"], wire)
            for node in self.whole.ir["nodes"]
            for wire in node["inputs"]
        )
        outputs = tuple(
            ("output", index, wire)
            for index, wire in enumerate(self.whole.ir["outputs"])
        )
        return (*node_inputs, *outputs)


def _topology() -> CausalCutTopology:
    workspace = link_modules([CAUSAL_TOPOLOGY_KERNEL])
    return CausalCutTopology(workspace.function("causal-topology", "fork-recombine"))


def test_checked_causal_pasts_form_a_non_boolean_alexandrov_topology():
    topology = _topology()
    opens = topology.opens

    assert frozenset() in opens
    assert topology.event_ids in opens

    # Downward-closed subsets are closed under all finite unions and
    # intersections.  Hence they are simultaneously a finite topology and a
    # distributive lattice.  The exhaustive check is deliberately bounded to
    # this five-event witness.
    for left, right, third in product(opens, repeat=3):
        assert left | right in opens
        assert left & right in opens
        assert left & (right | third) == (left & right) | (left & third)
        assert left | (right & third) == (left | right) & (left | third)

    root_copy = next(
        event
        for event in topology.events
        if event.operation == "copy" and not event.predecessors
    )
    first_past = frozenset({root_copy.node_id})
    assert first_past in opens

    # Causal dependence removes most subsets.  In particular the complement
    # of the first nonempty past contains descendants without their cause, so
    # it is not open.  The spatial lattice is distributive but not Boolean.
    assert topology.event_ids - first_past not in opens
    assert len(opens) < 2 ** len(topology.event_ids)


def test_spatial_opens_recover_the_checked_temporal_order():
    topology = _topology()

    # An earlier event belongs to every completed past containing a later
    # event.  Conversely, incomparable events are separated by some past-open
    # set.  Thus the spatial open family determines the temporal dependency
    # order in this finite T0 calibration.
    for earlier, later in product(topology.event_ids, repeat=2):
        assert topology.precedes_from_opens(earlier, later) == (
            topology.causally_precedes(earlier, later)
        )


def test_shared_source_becomes_two_ports_on_the_first_branch_cut():
    topology = _topology()
    root_copy = next(
        event
        for event in topology.events
        if event.operation == "copy" and not event.predecessors
    )
    cut = topology.cut(frozenset({root_copy.node_id}))

    assert len(cut.frontier) == 2
    assert all(wire.value_type == "real" for wire in cut.frontier)
    assert all(len(wire.lineage) == 1 for wire in cut.frontier)
    assert cut.frontier[0].lineage != cut.frontier[1].lineage
    assert len({source for wire in cut.frontier for source in wire.sources}) == 1


def test_non_downward_closed_event_set_is_rejected_as_a_cut():
    topology = _topology()
    join = next(event for event in topology.events if event.operation == "add")
    invalid = frozenset({join.node_id})

    assert not topology.is_open(invalid)
    try:
        topology.cut(invalid)
    except ValueError as error:
        assert "contain the past" in str(error)
    else:  # pragma: no cover - defensive assertion
        raise AssertionError("a future event without its past was accepted")
