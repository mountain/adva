from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass, replace
from typing import Any, Literal, TypeAlias

import pytest
from adva import KernelFunction, link_modules

LINEAGE_AWARE_BRACKETS = r"""
(module lineage-aware-brackets
  (export
    spatial-mul
    spatial-add
    ancestry-chain
    nontransitive-chain
    identity-support
    cycle-support
    parallel-temporal-support
    shared-child-support)

  (def spatial-mul-body
    (fn (
          (temporal-output Real)
          (temporal-use Real)
          (construction-use Real)
          (construction-output Real))
        (outputs Real Real Real)
      (frontier
        (use temporal-output)
        (mul (use temporal-use) (use construction-use))
        (use construction-output))))

  (def spatial-add-body
    (fn (
          (temporal-output Real)
          (temporal-use Real)
          (construction-use Real)
          (construction-output Real))
        (outputs Real Real Real)
      (frontier
        (use temporal-output)
        (add (use temporal-use) (use construction-use))
        (use construction-output))))

  (def spatial-mul
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use spatial))
        (call spatial-mul-body
          (frontier
            (copy (use temporal))
            (copy (use construction)))))))

  (def spatial-add
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use spatial))
        (call spatial-add-body
          (frontier
            (copy (use temporal))
            (copy (use construction)))))))

  (def cycle-support
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (swap
          (frontier
            (use temporal)
            (use spatial)))
        (use construction))))

  (def identity-support
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (use temporal)
        (use spatial)
        (use construction))))

  (def ancestry-chain-body
    (fn ((temporal-x Real) (temporal-k Real) (spatial-k Real))
        (outputs Real Real)
      (frontier
        (use temporal-x)
        (add (use temporal-k) (use spatial-k)))))

  (def ancestry-chain
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use construction))
        0
        (call ancestry-chain-body
          (frontier
            (copy (use temporal))
            (use spatial))))))

  (def nontransitive-chain
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use construction))
        0
        (use temporal)
        (use spatial))))

  (def triple-copy-expanded
    (fn ((left Real) (right Real)) (outputs Real Real Real)
      (frontier
        (use left)
        (copy (use right)))))

  (def triple-copy
    (fn ((value Real)) (outputs Real Real Real)
      (call triple-copy-expanded
        (copy (use value)))))

  (def parallel-body
    (fn (
          (temporal-output Real)
          (temporal-left Real)
          (temporal-right Real)
          (construction-output Real))
        (outputs Real Real Real)
      (frontier
        (use temporal-output)
        (add (use temporal-left) (use temporal-right))
        (use construction-output))))

  (def parallel-temporal-support
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use spatial))
        (call parallel-body
          (frontier
            (call triple-copy (use temporal))
            (use construction))))))

  (def shared-child-support
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use spatial))
        (discard (use construction))
        (call triple-copy (use temporal)))))
)
"""


Domain: TypeAlias = Literal["K", "X", "t"]
DOMAINS: tuple[Domain, ...] = ("K", "X", "t")
INPUT_DOMAINS: tuple[Domain, ...] = ("t", "X", "K")
OUTPUT_DOMAINS: tuple[Domain, ...] = ("t", "X", "K")
DOMAIN_ORDER = {domain: index for index, domain in enumerate(DOMAINS)}
OPEN = {"K": "{", "X": "[", "t": "("}
CLOSE = {"K": "}", "X": "]", "t": ")"}
OBSERVER_POLICY = "adva.research.lineage-aware-brackets.v0"
STRICT_PROJECTION_POLICY = "direct-foreign-incidence.v0"
ANCESTRY_PROJECTION_POLICY = "domain-support-set-strict-ancestry.v0"
PROMOTION_RULE = "root-child-complete-fibre.v0"


@dataclass(frozen=True, slots=True)
class Bracket:
    """One Raw111 observer cell, never a Rust occurrence or boundary port."""

    domain: Domain
    children: tuple[Bracket, ...] = ()


Forest: TypeAlias = tuple[Bracket, ...]
FLAT: Forest = tuple(Bracket(domain) for domain in DOMAINS)


@dataclass(frozen=True, slots=True)
class OutputPort:
    """A declared observer role attached to one exact Rust upper crossing."""

    domain: Domain
    output_index: int
    consumer_json: str
    wire_ref_json: str
    lineage: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SourceRef:
    source_id: str
    domain: Domain


@dataclass(frozen=True, slots=True)
class OccurrenceRef:
    occurrence_id: str
    source_id: str
    occurrence_path: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class CopyLink:
    node_id: int
    parent_occurrence: str
    child_occurrences: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SupportIncidence:
    """One exact upper occurrence attached to its source and output role."""

    output_domain: Domain
    output_index: int
    consumer_json: str
    wire_ref_json: str
    lineage_index: int
    occurrence_id: str
    occurrence_path: tuple[int, ...]
    source_domain: Domain
    source_id: str


@dataclass(frozen=True, slots=True)
class SupportHypergraph:
    """Read-only observer data copied from one validated diagram and slice."""

    shells: tuple[Domain, ...]
    observer_policy: str
    ports: tuple[OutputPort, ...]
    sources: tuple[SourceRef, ...]
    occurrences: tuple[OccurrenceRef, ...]
    incidences: tuple[SupportIncidence, ...]
    copy_links: tuple[CopyLink, ...]
    slice_nodes: tuple[int, ...]
    checked_snapshot_json: str
    validation_certificate_json: str
    slice_certificate_json: str


@dataclass(frozen=True, slots=True)
class ObservedWithResidual:
    projection_policy: str
    surface: Forest
    foreign_edges: tuple[tuple[Domain, Domain], ...]
    residual: SupportHypergraph


@dataclass(frozen=True, slots=True)
class NotRepresentable:
    projection_policy: str
    reason: Literal[
        "cycle",
        "non-transitive",
        "incomparable-ancestors",
        "repeated-foreign-color",
        "shared-foreign-child",
    ]
    obstruction: tuple[tuple[Domain, Domain], ...]
    obstruction_incidences: tuple[SupportIncidence, ...]
    residual: SupportHypergraph


RawProjection: TypeAlias = ObservedWithResidual | NotRepresentable


@dataclass(frozen=True, slots=True)
class StrictRaw111WithResidual:
    """A direct-edge Raw111 view preserving every foreign incidence."""

    projection_policy: str
    surface: Forest
    foreign_incidence_bindings: tuple[SupportIncidence, ...]
    residual: SupportHypergraph


StrictProjection: TypeAlias = StrictRaw111WithResidual | NotRepresentable


@dataclass(frozen=True, slots=True)
class ObserverState:
    """A visible Raw111 surface plus a lossless incidence partition."""

    projection_policy: str
    surface: Forest
    support: SupportHypergraph
    visible_incidences: tuple[SupportIncidence, ...]
    residual_incidences: tuple[SupportIncidence, ...]


@dataclass(frozen=True, slots=True)
class ProvenanceHideWitness:
    """Hide one visible support edge; never claim that provenance disappeared."""

    kind: Literal["provenance-hide"]
    observer_policy: str
    projection_policy: str
    promotion_rule: str
    checked_snapshot_json: str
    before_surface: Forest
    before_visible: tuple[SupportIncidence, ...]
    before_residual: tuple[SupportIncidence, ...]
    after_surface: Forest
    parent_path: tuple[int, ...]
    child_index: int
    parent_domain: Domain
    child_domain: Domain
    parent_output_index: int
    parent_consumer_json: str
    parent_wire_ref_json: str
    exact_support: tuple[SupportIncidence, ...]


@pytest.fixture(scope="module")
def workspace():
    return link_modules([LINEAGE_AWARE_BRACKETS])


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _render(forest: Forest) -> str:
    def render_one(bracket: Bracket) -> str:
        return (
            OPEN[bracket.domain]
            + "".join(render_one(child) for child in bracket.children)
            + CLOSE[bracket.domain]
        )

    return "".join(render_one(root) for root in forest)


def _walk_edges(
    forest: Forest,
) -> Iterator[tuple[tuple[int, ...], int, Bracket, Bracket]]:
    def visit(
        siblings: tuple[Bracket, ...],
        prefix: tuple[int, ...],
    ) -> Iterator[tuple[tuple[int, ...], int, Bracket, Bracket]]:
        for index, parent in enumerate(siblings):
            parent_path = (*prefix, index)
            for child_index, child in enumerate(parent.children):
                yield parent_path, child_index, parent, child
            yield from visit(parent.children, parent_path)

    yield from visit(forest, ())


def _node_ids(function: KernelFunction) -> tuple[int, ...]:
    return tuple(node["id"] for node in function.ir["nodes"])


def _support_hypergraph(function: KernelFunction) -> SupportHypergraph:
    """Decorate fixed shells without allocating semantic IDs in Python."""

    node_ids = _node_ids(function)
    interval = function.program_slice([], node_ids)
    lower_frontier = interval.result.lower["frontier"]
    upper_frontier = interval.result.upper["frontier"]

    source_domains: dict[str, Domain] = {}
    for crossing in lower_frontier:
        producer = crossing["wire"]["producer"]
        if producer["kind"] != "input":
            continue
        domain = INPUT_DOMAINS[producer["index"]]
        for source_id in crossing["sources"]:
            previous = source_domains.setdefault(source_id, domain)
            if previous != domain:
                raise ValueError("one Rust source was assigned two observer domains")

    occurrence_rows = {
        item["id"]: item for item in interval.result.occurrences
    }
    if len(occurrence_rows) != len(interval.result.occurrences):
        raise ValueError("the checked slice repeated an occurrence record")
    occurrence_sources = {
        occurrence_id: item["source"]
        for occurrence_id, item in occurrence_rows.items()
    }
    partition_pairs = {
        (occurrence_id, source_id)
        for source_id, occurrence_ids in function.source_partition.items()
        for occurrence_id in occurrence_ids
    }
    if not all(
        (occurrence_id, source_id) in partition_pairs
        for occurrence_id, source_id in occurrence_sources.items()
    ):
        raise ValueError("slice occurrences disagree with the checked source partition")
    if set(source_domains) != set(function.source_partition):
        raise ValueError("the lower cut does not expose every checked source")
    source_refs = tuple(
        sorted(
            (
                SourceRef(source_id=source_id, domain=domain)
                for source_id, domain in source_domains.items()
            ),
            key=lambda item: (DOMAIN_ORDER[item.domain], item.source_id),
        )
    )

    ports: list[OutputPort] = []
    incidences: list[SupportIncidence] = []
    seen_upper_occurrences: set[str] = set()
    for crossing in upper_frontier:
        consumer = crossing["consumer"]
        if consumer["kind"] != "output":
            raise ValueError("the full upper cut is not output-ready")
        output_index = consumer["index"]
        output_domain = OUTPUT_DOMAINS[output_index]
        consumer_json = _canonical_json(consumer)
        wire_ref_json = _canonical_json(crossing["wire"])
        lineage = tuple(crossing["wire"]["lineage"])
        ports.append(
            OutputPort(
                output_domain,
                output_index,
                consumer_json,
                wire_ref_json,
                lineage,
            )
        )

        crossing_sources = tuple(crossing["sources"])
        for lineage_index, (occurrence_id, source_id) in enumerate(
            zip(lineage, crossing_sources, strict=True)
        ):
            if occurrence_id in seen_upper_occurrences:
                raise ValueError("one upper occurrence crossed two output ports")
            seen_upper_occurrences.add(occurrence_id)
            if occurrence_sources[occurrence_id] != source_id:
                raise ValueError(
                    "upper source sequence disagrees with occurrence records"
                )
            occurrence_path = tuple(occurrence_rows[occurrence_id]["path"])
            incidences.append(
                SupportIncidence(
                    output_domain=output_domain,
                    output_index=output_index,
                    consumer_json=consumer_json,
                    wire_ref_json=wire_ref_json,
                    lineage_index=lineage_index,
                    occurrence_id=occurrence_id,
                    occurrence_path=occurrence_path,
                    source_domain=source_domains[source_id],
                    source_id=source_id,
                )
            )
        if crossing_sources != tuple(
            incidence.source_id
            for incidence in incidences
            if incidence.output_index == output_index
        ):
            raise ValueError("upper sources and lineage are not position-wise equal")

    ports.sort(key=lambda item: DOMAIN_ORDER[item.domain])
    incidences.sort(
        key=lambda item: (
            DOMAIN_ORDER[item.output_domain],
            item.lineage_index,
            item.occurrence_id,
        )
    )
    copy_links = tuple(
        sorted(
            (
                CopyLink(
                    node_id=event["node"],
                    parent_occurrence=event["parent"],
                    child_occurrences=tuple(event["children"]),
                )
                for event in interval.result.event_history
                if event["kind"] == "copy"
            ),
            key=lambda item: item.node_id,
        )
    )
    occurrence_paths = {
        occurrence_id: tuple(item["path"])
        for occurrence_id, item in occurrence_rows.items()
    }
    for link in copy_links:
        parent_path = occurrence_paths[link.parent_occurrence]
        expected_children = tuple(
            (*parent_path, branch)
            for branch in range(len(link.child_occurrences))
        )
        child_paths = tuple(
            occurrence_paths[child] for child in link.child_occurrences
        )
        if child_paths != expected_children:
            raise ValueError("copy children do not extend the checked occurrence path")
    occurrences = tuple(
        sorted(
            (
                OccurrenceRef(
                    occurrence_id,
                    item["source"],
                    tuple(item["path"]),
                )
                for occurrence_id, item in occurrence_rows.items()
            ),
            key=lambda item: item.occurrence_id,
        )
    )
    snapshot_payload = {
        "observer_policy": OBSERVER_POLICY,
        "input_domains": INPUT_DOMAINS,
        "output_domains": OUTPUT_DOMAINS,
        "display_order": DOMAINS,
        "ir": function.ir,
        "validation_certificate": function.validation_certificate,
        "lower": interval.result.lower,
        "upper": interval.result.upper,
        "events": interval.result.events,
        "lower_boundary": interval.result.lower_boundary,
        "upper_boundary": interval.result.upper_boundary,
        "through_wires": interval.result.through_wires,
        "internal_events": interval.result.internal_events,
        "occurrences": interval.result.occurrences,
        "event_history": interval.result.event_history,
        "graft_intersections": interval.result.graft_intersections,
        "certificate": interval.certificate,
    }
    checked_snapshot_json = _canonical_json(snapshot_payload)

    if tuple(port.domain for port in ports) != DOMAINS:
        raise ValueError("the full upper cut is not the declared output-ready triad")
    if function.validation_certificate["graph"] != "checked":
        raise ValueError("the diagram is not Rust-validated")
    if function.validation_certificate["linear_use"] != "checked":
        raise ValueError("the diagram does not have checked linear use")
    if interval.certificate["lineage_preservation"] != "checked":
        raise ValueError("the slice does not certify lineage preservation")
    if interval.certificate["original_id_preservation"] != "checked":
        raise ValueError("the slice does not certify original IDs")
    return SupportHypergraph(
        shells=DOMAINS,
        observer_policy=OBSERVER_POLICY,
        ports=tuple(ports),
        sources=source_refs,
        occurrences=occurrences,
        incidences=tuple(incidences),
        copy_links=copy_links,
        slice_nodes=node_ids,
        checked_snapshot_json=checked_snapshot_json,
        validation_certificate_json=_canonical_json(
            function.validation_certificate
        ),
        slice_certificate_json=_canonical_json(interval.certificate),
    )


def _foreign_edges(
    support: SupportHypergraph,
) -> tuple[tuple[Domain, Domain], ...]:
    return tuple(
        sorted(
            {
                (incidence.output_domain, incidence.source_domain)
                for incidence in support.incidences
                if incidence.output_domain != incidence.source_domain
            },
            key=lambda edge: (DOMAIN_ORDER[edge[0]], DOMAIN_ORDER[edge[1]]),
        )
    )


def _alpha_lineage_support_shape(
    support: SupportHypergraph,
) -> tuple[Any, ...]:
    """Forget artifact-local labels but retain the decorated support shape."""

    source_ranks: dict[str, tuple[Domain, int]] = {}
    ranks_by_domain: dict[Domain, int] = defaultdict(int)
    for source in support.sources:
        rank = ranks_by_domain[source.domain]
        source_ranks[source.source_id] = (source.domain, rank)
        ranks_by_domain[source.domain] += 1
    occurrence_keys = {
        occurrence.occurrence_id: (
            source_ranks[occurrence.source_id],
            occurrence.occurrence_path,
        )
        for occurrence in support.occurrences
    }

    return (
        support.shells,
        support.observer_policy,
        tuple(source.domain for source in support.sources),
        tuple(sorted(occurrence_keys.values())),
        tuple(
            (
                port.domain,
                port.output_index,
                tuple(occurrence_keys[item] for item in port.lineage),
            )
            for port in support.ports
        ),
        tuple(
            (
                incidence.output_domain,
                incidence.output_index,
                incidence.lineage_index,
                occurrence_keys[incidence.occurrence_id],
                incidence.source_domain,
                source_ranks[incidence.source_id],
            )
            for incidence in support.incidences
        ),
        tuple(
            (
                occurrence_keys[link.parent_occurrence],
                tuple(
                    occurrence_keys[child]
                    for child in link.child_occurrences
                ),
            )
            for link in support.copy_links
        ),
        len(support.slice_nodes),
    )


def _foreign_incidences(
    support: SupportHypergraph,
) -> tuple[SupportIncidence, ...]:
    return tuple(
        incidence
        for incidence in support.incidences
        if incidence.output_domain != incidence.source_domain
    )


def _incidences_for_edges(
    support: SupportHypergraph,
    edges: tuple[tuple[Domain, Domain], ...],
) -> tuple[SupportIncidence, ...]:
    selected = set(edges)
    return tuple(
        incidence
        for incidence in support.incidences
        if (incidence.output_domain, incidence.source_domain) in selected
    )


def _observe_domain_support_set(support: SupportHypergraph) -> RawProjection:
    """Project only when support is exactly a strict forest ancestry order."""

    edges = _foreign_edges(support)
    edge_set = set(edges)
    children: dict[Domain, set[Domain]] = {domain: set() for domain in DOMAINS}
    for parent, child in edges:
        children[parent].add(child)

    state: dict[Domain, Literal["active", "done"]] = {}

    def visit(domain: Domain) -> bool:
        if state.get(domain) == "active":
            return True
        if state.get(domain) == "done":
            return False
        state[domain] = "active"
        if any(visit(child) for child in children[domain]):
            return True
        state[domain] = "done"
        return False

    if any(visit(domain) for domain in DOMAINS):
        return NotRepresentable(
            projection_policy=ANCESTRY_PROJECTION_POLICY,
            reason="cycle",
            obstruction=edges,
            obstruction_incidences=_incidences_for_edges(support, edges),
            residual=support,
        )

    for ancestor, middle in edges:
        for next_parent, descendant in edges:
            if middle == next_parent and (ancestor, descendant) not in edge_set:
                obstruction = tuple(
                    sorted(
                        {(ancestor, middle), (middle, descendant)},
                        key=lambda edge: (
                            DOMAIN_ORDER[edge[0]], DOMAIN_ORDER[edge[1]]
                        ),
                    )
                )
                return NotRepresentable(
                    projection_policy=ANCESTRY_PROJECTION_POLICY,
                    reason="non-transitive",
                    obstruction=obstruction,
                    obstruction_incidences=_incidences_for_edges(
                        support, obstruction
                    ),
                    residual=support,
                )

    ancestors_by_child: dict[Domain, set[Domain]] = defaultdict(set)
    for ancestor, descendant in edges:
        ancestors_by_child[descendant].add(ancestor)
    for descendant, ancestors in ancestors_by_child.items():
        for left in ancestors:
            for right in ancestors:
                if left == right:
                    continue
                if (left, right) not in edge_set and (right, left) not in edge_set:
                    obstruction = tuple(
                        sorted(
                            {(left, descendant), (right, descendant)},
                            key=lambda edge: (
                                DOMAIN_ORDER[edge[0]], DOMAIN_ORDER[edge[1]]
                            ),
                        )
                    )
                    return NotRepresentable(
                        projection_policy=ANCESTRY_PROJECTION_POLICY,
                        reason="incomparable-ancestors",
                        obstruction=obstruction,
                        obstruction_incidences=_incidences_for_edges(
                            support, obstruction
                        ),
                        residual=support,
                    )

    direct_children: dict[Domain, set[Domain]] = {
        domain: set() for domain in DOMAINS
    }
    immediate_parents: dict[Domain, Domain] = {}
    for descendant, ancestors in ancestors_by_child.items():
        nearest = [
            ancestor
            for ancestor in ancestors
            if not any(
                ancestor != other and (ancestor, other) in edge_set
                for other in ancestors
            )
        ]
        if len(nearest) != 1:
            obstruction = tuple(
                edge for edge in edges if edge[1] == descendant
            )
            return NotRepresentable(
                projection_policy=ANCESTRY_PROJECTION_POLICY,
                reason="incomparable-ancestors",
                obstruction=obstruction,
                obstruction_incidences=_incidences_for_edges(
                    support, obstruction
                ),
                residual=support,
            )
        immediate_parents[descendant] = nearest[0]
        direct_children[nearest[0]].add(descendant)

    roots = [domain for domain in DOMAINS if domain not in immediate_parents]

    def build(domain: Domain) -> Bracket:
        return Bracket(
            domain,
            tuple(
                build(child)
                for child in DOMAINS
                if child in direct_children[domain]
            ),
        )

    surface = tuple(build(root) for root in roots)
    if {bracket.domain for bracket in _walk_brackets(surface)} != set(DOMAINS):
        obstruction = tuple(
            sorted(
                edges,
                key=lambda edge: (DOMAIN_ORDER[edge[0]], DOMAIN_ORDER[edge[1]]),
            )
        )
        return NotRepresentable(
            projection_policy=ANCESTRY_PROJECTION_POLICY,
            reason="cycle",
            obstruction=obstruction,
            obstruction_incidences=_incidences_for_edges(
                support, obstruction
            ),
            residual=support,
        )
    return ObservedWithResidual(
        projection_policy=ANCESTRY_PROJECTION_POLICY,
        surface=surface,
        foreign_edges=edges,
        residual=support,
    )


def _project_raw111_strict(support: SupportHypergraph) -> StrictProjection:
    """Keep every foreign incidence as one direct ordered Raw111 edge."""

    foreign = _foreign_incidences(support)
    by_child: dict[Domain, list[SupportIncidence]] = defaultdict(list)
    for incidence in foreign:
        by_child[incidence.source_domain].append(incidence)
    for child, bundle in by_child.items():
        if len(bundle) <= 1:
            continue
        parents = {incidence.output_domain for incidence in bundle}
        reason: Literal["repeated-foreign-color", "shared-foreign-child"] = (
            "shared-foreign-child"
            if len(parents) > 1
            else "repeated-foreign-color"
        )
        obstruction = tuple(
            (incidence.output_domain, child) for incidence in bundle
        )
        return NotRepresentable(
            projection_policy=STRICT_PROJECTION_POLICY,
            reason=reason,
            obstruction=obstruction,
            obstruction_incidences=tuple(bundle),
            residual=support,
        )

    direct_children: dict[Domain, list[Domain]] = {
        domain: [] for domain in DOMAINS
    }
    parent_by_child: dict[Domain, Domain] = {}
    for incidence in foreign:
        parent = incidence.output_domain
        child = incidence.source_domain
        direct_children[parent].append(child)
        parent_by_child[child] = parent

    state: dict[Domain, Literal["active", "done"]] = {}

    def has_cycle(domain: Domain) -> bool:
        if state.get(domain) == "active":
            return True
        if state.get(domain) == "done":
            return False
        state[domain] = "active"
        if any(has_cycle(child) for child in direct_children[domain]):
            return True
        state[domain] = "done"
        return False

    if any(has_cycle(domain) for domain in DOMAINS):
        edges = _foreign_edges(support)
        return NotRepresentable(
            projection_policy=STRICT_PROJECTION_POLICY,
            reason="cycle",
            obstruction=edges,
            obstruction_incidences=foreign,
            residual=support,
        )

    def build(domain: Domain) -> Bracket:
        return Bracket(
            domain,
            tuple(build(child) for child in direct_children[domain]),
        )

    roots = [domain for domain in DOMAINS if domain not in parent_by_child]
    surface = tuple(build(root) for root in roots)
    if {bracket.domain for bracket in _walk_brackets(surface)} != set(DOMAINS):
        edges = _foreign_edges(support)
        return NotRepresentable(
            projection_policy=STRICT_PROJECTION_POLICY,
            reason="cycle",
            obstruction=edges,
            obstruction_incidences=foreign,
            residual=support,
        )
    return StrictRaw111WithResidual(
        projection_policy=STRICT_PROJECTION_POLICY,
        surface=surface,
        foreign_incidence_bindings=foreign,
        residual=support,
    )


def _walk_brackets(forest: Forest) -> Iterator[Bracket]:
    for bracket in forest:
        yield bracket
        yield from _walk_brackets(bracket.children)


def _ancestry_edges(forest: Forest) -> set[tuple[Domain, Domain]]:
    edges: set[tuple[Domain, Domain]] = set()

    def visit(bracket: Bracket, ancestors: tuple[Domain, ...]) -> None:
        edges.update((ancestor, bracket.domain) for ancestor in ancestors)
        for child in bracket.children:
            visit(child, (*ancestors, bracket.domain))

    for root in forest:
        visit(root, ())
    return edges


def _initial_observer_state(projection: ObservedWithResidual) -> ObserverState:
    visible = _foreign_incidences(projection.residual)
    residual = tuple(
        incidence
        for incidence in projection.residual.incidences
        if incidence not in visible
    )
    state = ObserverState(
        projection_policy=projection.projection_policy,
        surface=projection.surface,
        support=projection.residual,
        visible_incidences=visible,
        residual_incidences=residual,
    )
    _check_incidence_partition(state)
    return state


def _check_incidence_partition(state: ObserverState) -> None:
    if state.projection_policy != ANCESTRY_PROJECTION_POLICY:
        raise ValueError("observer state uses a different projection policy")
    visible = set(state.visible_incidences)
    residual = set(state.residual_incidences)
    if visible & residual:
        raise ValueError("visible and residual incidence fibres overlap")
    if visible | residual != set(state.support.incidences):
        raise ValueError("observer incidence partition lost checked evidence")
    if len(visible) + len(residual) != len(state.support.incidences):
        raise ValueError("observer incidence partition changed multiplicity")
    canonical_visible = tuple(
        incidence
        for incidence in state.support.incidences
        if incidence in visible
    )
    canonical_residual = tuple(
        incidence
        for incidence in state.support.incidences
        if incidence in residual
    )
    if (
        state.visible_incidences != canonical_visible
        or state.residual_incidences != canonical_residual
    ):
        raise ValueError("observer state changed canonical incidence order")
    cells = tuple(_walk_brackets(state.surface))
    if len(cells) != len(DOMAINS) or {cell.domain for cell in cells} != set(DOMAINS):
        raise ValueError("observer surface is not one-color-once Raw111")
    if any(
        incidence.output_domain == incidence.source_domain
        for incidence in state.visible_incidences
    ):
        raise ValueError("self support cannot enter the visible foreign quotient")
    fibres: dict[tuple[Domain, Domain], set[SupportIncidence]] = defaultdict(set)
    for incidence in state.support.incidences:
        fibres[(incidence.output_domain, incidence.source_domain)].add(incidence)
    for fibre in fibres.values():
        visible_members = fibre & visible
        if visible_members and visible_members != fibre:
            raise ValueError("observer state split a complete incidence fibre")
    visible_edges = {
        (incidence.output_domain, incidence.source_domain)
        for incidence in state.visible_incidences
    }
    if _ancestry_edges(state.surface) != visible_edges:
        raise ValueError("surface and visible incidence quotient disagree")


def _promote_root_child(
    surface: Forest,
    parent_path: tuple[int, ...],
    child_index: int,
) -> Forest:
    if len(parent_path) != 1 or any(
        isinstance(index, bool) or not isinstance(index, int) or index < 0
        for index in parent_path
    ):
        raise ValueError("only root-child provenance hiding is calibrated")
    if (
        isinstance(child_index, bool)
        or not isinstance(child_index, int)
        or child_index < 0
    ):
        raise ValueError("child index is outside the current parent")
    root_index = parent_path[0]
    if root_index >= len(surface):
        raise ValueError("parent path is outside the current surface")
    parent = surface[root_index]
    if child_index >= len(parent.children):
        raise ValueError("child index is outside the current parent")
    child = parent.children[child_index]
    remaining = parent.children[:child_index] + parent.children[child_index + 1 :]
    updated_parent = Bracket(parent.domain, remaining)
    return (
        surface[:root_index]
        + (updated_parent, child)
        + surface[root_index + 1 :]
    )


def _provenance_hide_witnesses(
    state: ObserverState,
) -> tuple[ProvenanceHideWitness, ...]:
    """Witness complete fibres only on depth-one domain-support stars."""

    _check_incidence_partition(state)
    if any(child.children for root in state.surface for child in root.children):
        return ()
    support = state.support
    ports = {port.domain: port for port in support.ports}
    witnesses: list[ProvenanceHideWitness] = []
    for parent_path, child_index, parent, child in _walk_edges(state.surface):
        if len(parent_path) != 1:
            continue
        port = ports[parent.domain]
        exact_support = tuple(
            incidence
            for incidence in support.incidences
            if incidence.output_domain == parent.domain
            and incidence.source_domain == child.domain
        )
        if not exact_support or not all(
            incidence in state.visible_incidences for incidence in exact_support
        ):
            continue
        witnesses.append(
            ProvenanceHideWitness(
                kind="provenance-hide",
                observer_policy=support.observer_policy,
                projection_policy=state.projection_policy,
                promotion_rule=PROMOTION_RULE,
                checked_snapshot_json=support.checked_snapshot_json,
                before_surface=state.surface,
                before_visible=state.visible_incidences,
                before_residual=state.residual_incidences,
                after_surface=_promote_root_child(
                    state.surface, parent_path, child_index
                ),
                parent_path=parent_path,
                child_index=child_index,
                parent_domain=parent.domain,
                child_domain=child.domain,
                parent_output_index=port.output_index,
                parent_consumer_json=port.consumer_json,
                parent_wire_ref_json=port.wire_ref_json,
                exact_support=exact_support,
            )
        )
    return tuple(witnesses)


def _hide_provenance(
    function: KernelFunction,
    state: ObserverState,
    witness: ProvenanceHideWitness,
) -> ObserverState:
    """Verify one artifact-scoped witness and move its edge into the residual."""

    support = _support_hypergraph(function)
    _check_incidence_partition(state)
    if state.support != support:
        raise ValueError("observer state belongs to a different checked snapshot")
    if witness.kind != "provenance-hide":
        raise ValueError("wrong observer event kind")
    if witness.observer_policy != support.observer_policy:
        raise ValueError("witness uses a different observer policy")
    if (
        state.projection_policy != ANCESTRY_PROJECTION_POLICY
        or witness.projection_policy != state.projection_policy
    ):
        raise ValueError("witness uses a different projection policy")
    if witness.promotion_rule != PROMOTION_RULE:
        raise ValueError("witness uses a different promotion rule")
    if witness.checked_snapshot_json != support.checked_snapshot_json:
        raise ValueError("witness belongs to a different checked snapshot")
    if (
        witness.before_surface,
        witness.before_visible,
        witness.before_residual,
    ) != (
        state.surface,
        state.visible_incidences,
        state.residual_incidences,
    ):
        raise ValueError("witness does not match the current surface")

    if len(witness.parent_path) != 1 or any(
        isinstance(index, bool) or not isinstance(index, int) or index < 0
        for index in witness.parent_path
    ):
        raise ValueError("only root-child provenance hiding is calibrated")
    if (
        isinstance(witness.child_index, bool)
        or not isinstance(witness.child_index, int)
        or witness.child_index < 0
    ):
        raise ValueError("child index is outside the current parent")
    root_index = witness.parent_path[0]
    if root_index >= len(state.surface):
        raise ValueError("parent path is outside the current surface")
    parent = state.surface[root_index]
    if witness.child_index >= len(parent.children):
        raise ValueError("child index is outside the current parent")
    child = parent.children[witness.child_index]
    if (parent.domain, child.domain) != (
        witness.parent_domain,
        witness.child_domain,
    ):
        raise ValueError("path and declared domains disagree")

    port = next(
        item for item in support.ports if item.domain == witness.parent_domain
    )
    if isinstance(witness.parent_output_index, bool) or not isinstance(
        witness.parent_output_index, int
    ):
        raise TypeError("parent output index has the wrong type")
    if (
        witness.parent_output_index,
        witness.parent_consumer_json,
        witness.parent_wire_ref_json,
    ) != (port.output_index, port.consumer_json, port.wire_ref_json):
        raise ValueError("parent is not the exact checked upper port")
    exact_support = tuple(
        incidence
        for incidence in support.incidences
        if incidence.output_domain == witness.parent_domain
        and incidence.source_domain == witness.child_domain
    )
    if not all(
        incidence in state.visible_incidences for incidence in exact_support
    ):
        raise ValueError("support fibre is not completely visible")
    if witness.exact_support != exact_support:
        raise ValueError("source or occurrence support was forged")
    expected_after = _promote_root_child(
        state.surface, witness.parent_path, witness.child_index
    )
    if witness.after_surface != expected_after:
        raise ValueError("witness after-surface commitment was forged")

    hidden = set(exact_support)
    visible = tuple(
        incidence
        for incidence in state.visible_incidences
        if incidence not in hidden
    )
    residual = tuple(
        incidence for incidence in support.incidences if incidence not in visible
    )
    after = ObserverState(
        projection_policy=state.projection_policy,
        surface=expected_after,
        support=support,
        visible_incidences=visible,
        residual_incidences=residual,
    )
    _check_incidence_partition(after)
    return after


def _calibrate_flat(forest: Forest) -> Forest:
    if any(bracket.children for bracket in forest):
        raise ValueError("cannot calibrate a nested observer surface")
    return tuple(sorted(forest, key=lambda item: DOMAIN_ORDER[item.domain]))


def test_fixed_shells_lineage_order_and_display_order_are_separate(workspace) -> None:
    function = workspace.function("lineage-aware-brackets", "spatial-mul")
    support = _support_hypergraph(function)
    strict = _project_raw111_strict(support)
    display = _observe_domain_support_set(support)

    assert support.shells == DOMAINS
    assert support.observer_policy == OBSERVER_POLICY
    assert tuple(source.domain for source in support.sources) == DOMAINS
    assert _render(tuple(Bracket(domain) for domain in support.shells)) == "{}[]()"
    assert isinstance(strict, StrictRaw111WithResidual)
    assert isinstance(display, ObservedWithResidual)
    assert strict.projection_policy == STRICT_PROJECTION_POLICY
    assert display.projection_policy == ANCESTRY_PROJECTION_POLICY
    assert _render(strict.surface) == "[(){}]"
    assert _render(display.surface) == "[{}()]"
    assert display.foreign_edges == (("X", "K"), ("X", "t"))
    assert _ancestry_edges(display.surface) == set(display.foreign_edges)

    incidence_pairs = [
        (item.output_domain, item.source_domain) for item in support.incidences
    ]
    assert incidence_pairs == [("K", "K"), ("X", "t"), ("X", "K"), ("t", "t")]
    assert tuple(
        item.source_domain
        for item in support.incidences
        if item.output_domain == "X"
    ) == ("t", "K")
    assert len({item.occurrence_id for item in support.incidences}) == 4
    assert len(
        {(item.source_id, item.occurrence_path) for item in support.incidences}
    ) == 4
    assert len(support.copy_links) == 2
    discarded_spatial_source = next(
        source.source_id for source in support.sources if source.domain == "X"
    )
    assert any(
        occurrence.source_id == discarded_spatial_source
        for occurrence in support.occurrences
    )
    assert all(
        incidence.source_id != discarded_spatial_source
        for incidence in support.incidences
    )
    upper_occurrences = {item.occurrence_id for item in support.incidences}
    assert all(
        link.parent_occurrence not in upper_occurrences
        for link in support.copy_links
    )
    assert {
        child for link in support.copy_links for child in link.child_occurrences
    } == upper_occurrences

    outputs_by_source: dict[str, set[Domain]] = defaultdict(set)
    for incidence in support.incidences:
        outputs_by_source[incidence.source_id].add(incidence.output_domain)
    assert sorted(len(outputs) for outputs in outputs_by_source.values()) == [2, 2]


def test_direct_incidence_and_ancestry_set_are_distinct_partial_observers(
    workspace,
) -> None:
    identity = _support_hypergraph(
        workspace.function("lineage-aware-brackets", "identity-support")
    )
    identity_strict = _project_raw111_strict(identity)
    identity_set = _observe_domain_support_set(identity)
    assert isinstance(identity_strict, StrictRaw111WithResidual)
    assert identity_strict.surface == FLAT
    assert isinstance(identity_set, ObservedWithResidual)
    assert identity_set.surface == FLAT

    ancestry = _support_hypergraph(
        workspace.function("lineage-aware-brackets", "ancestry-chain")
    )
    ancestry_strict = _project_raw111_strict(ancestry)
    ancestry_set = _observe_domain_support_set(ancestry)
    assert isinstance(ancestry_strict, NotRepresentable)
    assert ancestry_strict.projection_policy == STRICT_PROJECTION_POLICY
    assert ancestry_strict.reason == "shared-foreign-child"
    assert isinstance(ancestry_set, ObservedWithResidual)
    assert ancestry_set.projection_policy == ANCESTRY_PROJECTION_POLICY
    assert ancestry_set.foreign_edges == (("K", "X"), ("K", "t"), ("X", "t"))
    assert _render(ancestry_set.surface) == "{[()]}"
    assert _ancestry_edges(ancestry_set.surface) == set(ancestry_set.foreign_edges)
    assert _provenance_hide_witnesses(_initial_observer_state(ancestry_set)) == ()

    nontransitive = _support_hypergraph(
        workspace.function("lineage-aware-brackets", "nontransitive-chain")
    )
    nontransitive_strict = _project_raw111_strict(nontransitive)
    nontransitive_set = _observe_domain_support_set(nontransitive)
    assert isinstance(nontransitive_strict, StrictRaw111WithResidual)
    assert _render(nontransitive_strict.surface) == "{[()]}"
    assert isinstance(nontransitive_set, NotRepresentable)
    assert nontransitive_set.projection_policy == ANCESTRY_PROJECTION_POLICY
    assert nontransitive_set.reason == "non-transitive"
    assert set(nontransitive_set.obstruction) == {("K", "X"), ("X", "t")}
    assert {
        (item.output_domain, item.source_domain)
        for item in nontransitive_set.obstruction_incidences
    } == set(nontransitive_set.obstruction)


def test_cycles_and_shared_children_return_exact_counterevidence(workspace) -> None:
    cycle_function = workspace.function("lineage-aware-brackets", "cycle-support")
    cycle_support = _support_hypergraph(cycle_function)
    cycle_slice = cycle_function.program_slice([], _node_ids(cycle_function))
    assert [
        node["operation"]["name"] for node in cycle_function.ir["nodes"]
    ] == ["swap"]
    assert len(cycle_slice.result.through_wires) == 1
    assert len(cycle_support.ports) == 3
    for projection in (
        _project_raw111_strict(cycle_support),
        _observe_domain_support_set(cycle_support),
    ):
        assert isinstance(projection, NotRepresentable)
        assert projection.reason == "cycle"
        assert set(projection.obstruction) == {("X", "t"), ("t", "X")}
        assert set(projection.obstruction_incidences) == set(
            _foreign_incidences(cycle_support)
        )

    shared = _support_hypergraph(
        workspace.function("lineage-aware-brackets", "shared-child-support")
    )
    assert len(shared.incidences) == 3
    assert len({item.source_id for item in shared.incidences}) == 1
    assert len({item.occurrence_id for item in shared.incidences}) == 3
    assert {item.occurrence_path for item in shared.incidences} == {
        (0,),
        (1, 0),
        (1, 1),
    }
    assert len(shared.copy_links) == 2
    strict = _project_raw111_strict(shared)
    weak = _observe_domain_support_set(shared)
    assert isinstance(strict, NotRepresentable)
    assert strict.reason == "shared-foreign-child"
    assert isinstance(weak, NotRepresentable)
    assert weak.reason == "incomparable-ancestors"
    assert set(weak.obstruction) == {("K", "t"), ("X", "t")}


def test_parallel_fibre_is_hidden_atomically_and_retained_in_residual(
    workspace,
) -> None:
    function = workspace.function(
        "lineage-aware-brackets", "parallel-temporal-support"
    )
    support = _support_hypergraph(function)
    strict = _project_raw111_strict(support)
    weak = _observe_domain_support_set(support)
    assert isinstance(strict, NotRepresentable)
    assert strict.reason == "repeated-foreign-color"
    assert len(strict.obstruction_incidences) == 2
    assert len({item.source_id for item in strict.obstruction_incidences}) == 1
    assert len({item.occurrence_id for item in strict.obstruction_incidences}) == 2
    assert isinstance(weak, ObservedWithResidual)
    assert _render(weak.surface) == "{}[()]"

    state = _initial_observer_state(weak)
    half_visible = state.visible_incidences[:1]
    half_residual = tuple(
        incidence
        for incidence in support.incidences
        if incidence not in half_visible
    )
    with pytest.raises(ValueError, match="complete incidence fibre"):
        _check_incidence_partition(
            replace(
                state,
                visible_incidences=half_visible,
                residual_incidences=half_residual,
            )
        )
    with pytest.raises(ValueError, match="canonical incidence order"):
        _check_incidence_partition(
            replace(
                state,
                visible_incidences=tuple(reversed(state.visible_incidences)),
            )
        )
    witnesses = _provenance_hide_witnesses(state)
    assert len(witnesses) == 1
    witness = witnesses[0]
    assert witness.projection_policy == ANCESTRY_PROJECTION_POLICY
    assert witness.promotion_rule == PROMOTION_RULE
    assert len(witness.exact_support) == 2
    with pytest.raises(ValueError, match="forged"):
        _hide_provenance(
            function,
            state,
            replace(witness, exact_support=witness.exact_support[:1]),
        )

    after = _hide_provenance(function, state, witness)
    assert after.surface == FLAT
    assert after.visible_incidences == ()
    assert set(after.residual_incidences) == set(support.incidences)
    with pytest.raises(ValueError, match="current surface"):
        _hide_provenance(function, after, witness)


def test_x_provenance_hiding_has_a_lossless_incidence_partition(workspace) -> None:
    function = workspace.function("lineage-aware-brackets", "spatial-mul")
    support = _support_hypergraph(function)
    projection = _observe_domain_support_set(support)
    assert isinstance(projection, ObservedWithResidual)
    initial = _initial_observer_state(projection)
    with pytest.raises(ValueError, match="surface and visible"):
        _check_incidence_partition(
            replace(
                initial,
                surface=_promote_root_child(initial.surface, (0,), 0),
            )
        )

    endpoints: set[Forest] = set()
    schedules: set[tuple[Domain, ...]] = set()
    for first in _provenance_hide_witnesses(initial):
        after_first = _hide_provenance(function, initial, first)
        second_candidates = _provenance_hide_witnesses(after_first)
        assert len(second_candidates) == 1
        second = second_candidates[0]
        after_second = _hide_provenance(function, after_first, second)
        endpoints.add(_calibrate_flat(after_second.surface))
        schedules.add((first.child_domain, second.child_domain))

        assert first.parent_path == (0,)
        assert first.parent_output_index == 1
        assert first.exact_support
        assert after_second.visible_incidences == ()
        assert set(after_second.residual_incidences) == set(support.incidences)
        assert after_second.support == support

    assert schedules == {("K", "t"), ("t", "K")}
    assert endpoints == {FLAT}
    assert _foreign_edges(support) == (("X", "K"), ("X", "t"))


def test_witness_tampering_and_cross_artifact_replay_are_rejected(workspace) -> None:
    multiply = workspace.function("lineage-aware-brackets", "spatial-mul")
    addition = workspace.function("lineage-aware-brackets", "spatial-add")
    multiply_support = _support_hypergraph(multiply)
    addition_support = _support_hypergraph(addition)
    multiply_projection = _observe_domain_support_set(multiply_support)
    addition_projection = _observe_domain_support_set(addition_support)
    assert isinstance(multiply_projection, ObservedWithResidual)
    assert isinstance(addition_projection, ObservedWithResidual)
    multiply_state = _initial_observer_state(multiply_projection)
    addition_state = _initial_observer_state(addition_projection)
    witness = _provenance_hide_witnesses(multiply_state)[0]

    for forged_path in ((), (0, 0), (-1,), (True,)):
        with pytest.raises(ValueError, match="root-child"):
            _hide_provenance(
                multiply,
                multiply_state,
                replace(witness, parent_path=forged_path),
            )
    for forged_index in (-1, True):
        with pytest.raises(ValueError, match="child index"):
            _hide_provenance(
                multiply,
                multiply_state,
                replace(witness, child_index=forged_index),
            )
    with pytest.raises(ValueError, match="child index"):
        _hide_provenance(
            multiply,
            multiply_state,
            replace(witness, child_index=len(multiply_state.surface[0].children)),
        )
    witness = next(
        item
        for item in _provenance_hide_witnesses(multiply_state)
        if item.child_domain == "t"
    )
    wrong_real_incidence = next(
        item
        for item in multiply_support.incidences
        if item.output_domain == "t" and item.source_domain == "t"
    )
    with pytest.raises(ValueError, match="forged"):
        _hide_provenance(
            multiply,
            multiply_state,
            replace(witness, exact_support=(wrong_real_incidence,)),
        )
    wrong_port = next(
        item for item in multiply_support.ports if item.domain == "t"
    )
    with pytest.raises(ValueError, match="exact checked upper port"):
        _hide_provenance(
            multiply,
            multiply_state,
            replace(
                witness,
                parent_output_index=wrong_port.output_index,
                parent_consumer_json=wrong_port.consumer_json,
                parent_wire_ref_json=wrong_port.wire_ref_json,
            ),
        )
    with pytest.raises(ValueError, match="observer policy"):
        _hide_provenance(
            multiply,
            multiply_state,
            replace(witness, observer_policy="forged-policy"),
        )
    with pytest.raises(ValueError, match="projection policy"):
        _hide_provenance(
            multiply,
            multiply_state,
            replace(witness, projection_policy="forged-projection"),
        )
    with pytest.raises(ValueError, match="promotion rule"):
        _hide_provenance(
            multiply,
            multiply_state,
            replace(witness, promotion_rule="forged-promotion"),
        )
    with pytest.raises(ValueError, match="after-surface"):
        _hide_provenance(
            multiply,
            multiply_state,
            replace(witness, after_surface=multiply_state.surface),
        )

    assert multiply_projection.surface == addition_projection.surface
    assert multiply_projection.foreign_edges == addition_projection.foreign_edges
    assert _alpha_lineage_support_shape(
        multiply_support
    ) == _alpha_lineage_support_shape(addition_support)
    assert (
        multiply_support.checked_snapshot_json
        != addition_support.checked_snapshot_json
    )
    assert multiply.evaluate(
        {"temporal": 1, "spatial": 0, "construction": 1}
    ) != addition.evaluate(
        {"temporal": 1, "spatial": 0, "construction": 1}
    )
    with pytest.raises(ValueError, match="different checked snapshot"):
        _hide_provenance(addition, addition_state, witness)
