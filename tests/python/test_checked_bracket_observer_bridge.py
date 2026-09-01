from __future__ import annotations

from collections import Counter
from collections.abc import Iterator, Mapping
from dataclasses import dataclass
from itertools import permutations, product
from typing import Any, Literal, TypeAlias

import pytest

from adva import KernelFunction, link_modules


CHECKED_BRACKET_BRIDGE = r"""
(module checked-bracket-bridge
  (export bridge-step)

  (def spatial-body
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

  (def spatial-update
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (discard (use spatial))
        (call spatial-body
          (frontier
            (copy (use temporal))
            (copy (use construction)))))))

  (def bridge-step
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (call spatial-update
        (use temporal)
        (use spatial)
        (use construction))))
)
"""


Domain: TypeAlias = Literal["K", "X", "t"]
DOMAINS: tuple[Domain, ...] = ("K", "X", "t")
DOMAIN_ORDER = {domain: index for index, domain in enumerate(DOMAINS)}
OPEN = {"K": "{", "X": "[", "t": "("}
CLOSE = {"K": "}", "X": "]", "t": ")"}
CoreState: TypeAlias = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class Bracket:
    """One observer-domain occurrence, never a Rust OccurrenceId."""

    domain: Domain
    children: tuple[Bracket, ...] = ()


Forest: TypeAlias = tuple[Bracket, ...]


@dataclass(frozen=True, slots=True)
class SurfaceStep:
    kind: Literal["split", "coxeter"]
    detail: str


@dataclass(frozen=True, slots=True)
class DefectCode:
    temporal: int
    construction: int
    surface: Forest


@dataclass(frozen=True, slots=True)
class SupportObservation:
    surface: Forest


@dataclass(frozen=True, slots=True)
class PendingObservation:
    surface: Forest
    quiescent: bool


FLAT: Forest = (Bracket("K"), Bracket("X"), Bracket("t"))
DEPENDENCY_SURFACE: Forest = (
    Bracket("X", (Bracket("K"), Bracket("t"))),
)
DEFECT_SURFACE: Forest = DEPENDENCY_SURFACE
CORE_STATES: tuple[CoreState, ...] = tuple(product((0, 1), repeat=3))


@pytest.fixture(scope="module")
def function() -> KernelFunction:
    return link_modules([CHECKED_BRACKET_BRIDGE]).function(
        "checked-bracket-bridge", "bridge-step"
    )


def _render(forest: Forest) -> str:
    def render_one(bracket: Bracket) -> str:
        return (
            OPEN[bracket.domain]
            + "".join(render_one(child) for child in bracket.children)
            + CLOSE[bracket.domain]
        )

    return "".join(render_one(root) for root in forest)


def _walk(forest: Forest) -> Iterator[Bracket]:
    for root in forest:
        yield root
        yield from _walk(root.children)


def _edge_count(forest: Forest) -> int:
    return sum(len(bracket.children) for bracket in _walk(forest))


def _split_steps(forest: Forest) -> tuple[tuple[Forest, SurfaceStep], ...]:
    """Cut one root-child edge while preserving the three domain cells."""

    results = []
    for root_index, root in enumerate(forest):
        for child_index, child in enumerate(root.children):
            remaining = root.children[:child_index] + root.children[child_index + 1 :]
            parent = Bracket(root.domain, remaining)
            candidate = (
                forest[:root_index]
                + (parent, child)
                + forest[root_index + 1 :]
            )
            results.append(
                (candidate, SurfaceStep("split", f"{root.domain}>{child.domain}"))
            )
    return tuple(results)


def _coxeter_steps(forest: Forest) -> tuple[tuple[Forest, SurfaceStep], ...]:
    """Unsigned S3 endpoint sorting, defined only on the flat six-object sort."""

    if _edge_count(forest):
        return ()
    results = []
    for index, (left, right) in enumerate(zip(forest, forest[1:], strict=False)):
        if DOMAIN_ORDER[left.domain] <= DOMAIN_ORDER[right.domain]:
            continue
        candidate = forest[:index] + (right, left) + forest[index + 2 :]
        results.append((candidate, SurfaceStep("coxeter", f"s_{index + 1}")))
    return tuple(results)


def _normalization_traces(
    start: Forest,
) -> tuple[tuple[Forest, tuple[SurfaceStep, ...]], ...]:
    """Split all containment first, then calibrate the flat endpoint."""

    results: list[tuple[Forest, tuple[SurfaceStep, ...]]] = []

    def visit(current: Forest, trace: tuple[SurfaceStep, ...]) -> None:
        steps = (
            _split_steps(current)
            if _edge_count(current)
            else _coxeter_steps(current)
        )
        if not steps:
            results.append((current, trace))
            return
        for candidate, step in steps:
            visit(candidate, (*trace, step))

    visit(start, ())
    return tuple(results)


def _node_ids(function: KernelFunction) -> tuple[int, ...]:
    return tuple(node["id"] for node in function.ir["nodes"])


def _operation_names(function: KernelFunction) -> Counter[str]:
    return Counter(node["operation"]["name"] for node in function.ir["nodes"])


def _initial_sources(function: KernelFunction) -> dict[Domain, tuple[str, ...]]:
    # The checked signature is explicitly (temporal, spatial, construction).
    domains_by_index: tuple[Domain, ...] = ("t", "X", "K")
    return {
        domains_by_index[item["wire"]["producer"]["index"]]: tuple(item["sources"])
        for item in function.causal_cut([]).frontier
        if item["wire"]["producer"]["kind"] == "input"
    }


def _final_frontier(function: KernelFunction) -> tuple[Mapping[str, Any], ...]:
    return function.causal_cut(_node_ids(function)).frontier


def _outputs_ready(function: KernelFunction, completed: tuple[int, ...]) -> bool:
    current = function.causal_cut(completed).frontier
    final = _final_frontier(function)
    return all(
        any(crossing["wire"] == target["wire"] for crossing in current)
        for target in final
    )


def _pending_observation(
    function: KernelFunction,
    completed: tuple[int, ...],
) -> PendingObservation:
    """One slice-relative liveness observer, not retained provenance."""

    surface = FLAT if _outputs_ready(function, completed) else DEPENDENCY_SURFACE
    return PendingObservation(surface, set(completed) == set(_node_ids(function)))


def _evaluate_x(function: KernelFunction, state: CoreState) -> CoreState:
    temporal, spatial, construction = state
    value = function.evaluate(
        {
            "temporal": temporal,
            "spatial": spatial,
            "construction": construction,
        }
    )
    assert isinstance(value, tuple) and len(value) == 3
    return tuple(int(item) for item in value)  # type: ignore[return-value]


def _oracle_x(state: CoreState) -> CoreState:
    temporal, _, construction = state
    return (temporal, temporal & construction, construction)


def _support_observation(function: KernelFunction) -> SupportObservation:
    """Project exact foreign source support, then forget IDs and multiplicity."""

    source_domains = {
        source: domain
        for domain, sources in _initial_sources(function).items()
        for source in sources
    }
    output_domains: tuple[Domain, ...] = ("t", "X", "K")
    children: dict[Domain, set[Domain]] = {domain: set() for domain in DOMAINS}
    for crossing in _final_frontier(function):
        consumer = crossing["consumer"]
        assert consumer["kind"] == "output"
        domain = output_domains[consumer["index"]]
        children[domain] = {
            source_domains[source]
            for source in crossing["sources"]
            if source_domains[source] != domain
        }

    parents = {
        child
        for domain in DOMAINS
        for child in children[domain]
    }
    assert all(
        sum(child in children[parent] for parent in DOMAINS) <= 1
        for child in DOMAINS
    )

    def build(domain: Domain) -> Bracket:
        return Bracket(
            domain,
            tuple(build(child) for child in DOMAINS if child in children[domain]),
        )

    surface = tuple(build(domain) for domain in DOMAINS if domain not in parents)
    return SupportObservation(surface)


def _encode_defect(state: CoreState) -> DefectCode:
    temporal, spatial, construction = state
    defect = spatial ^ (temporal & construction)
    return DefectCode(
        temporal,
        construction,
        DEFECT_SURFACE if defect else FLAT,
    )


def _decode_defect(code: DefectCode) -> CoreState:
    if code.surface == FLAT:
        defect = 0
    elif code.surface == DEFECT_SURFACE:
        defect = 1
    else:
        raise ValueError("outside the Boolean defect-pattern code")
    spatial = (code.temporal & code.construction) ^ defect
    return (code.temporal, spatial, code.construction)


def _normalize_defect(
    code: DefectCode,
) -> tuple[DefectCode, tuple[tuple[SurfaceStep, ...], ...]]:
    if code.surface == FLAT:
        return code, ((),)
    normalizations = _normalization_traces(code.surface)
    assert normalizations
    assert {surface for surface, _ in normalizations} == {FLAT}
    return (
        DefectCode(code.temporal, code.construction, FLAT),
        tuple(trace for _, trace in normalizations),
    )


def test_direct_split_identification_fails_value_rank_and_composition(
    function: KernelFunction,
) -> None:
    # Checked X loses the old spatial value and is idempotent on the Boolean core.
    assert _evaluate_x(function, (0, 0, 0)) == _evaluate_x(function, (0, 1, 0))
    assert all(
        _evaluate_x(function, state) == _oracle_x(state) for state in CORE_STATES
    )
    assert all(
        _evaluate_x(function, _evaluate_x(function, state))
        == _evaluate_x(function, state)
        for state in CORE_STATES
    )


    # An elementary split preserves the same three cells and removes one edge.
    # On a two-edge term it is not idempotent, so it cannot equal checked X.
    first = _split_steps(DEPENDENCY_SURFACE)
    assert len(first) == 2
    after_one = first[0][0]
    after_two = _split_steps(after_one)[0][0]
    assert {item.domain for item in _walk(DEPENDENCY_SURFACE)} == set(DOMAINS)
    assert {item.domain for item in _walk(after_one)} == set(DOMAINS)
    assert {item.domain for item in _walk(after_two)} == set(DOMAINS)
    assert (
        _edge_count(DEPENDENCY_SURFACE),
        _edge_count(after_one),
        _edge_count(after_two),
    ) == (2, 1, 0)
    assert after_one != after_two


def test_direct_split_identification_fails_resource_and_occurrence_evidence(
    function: KernelFunction,
) -> None:
    assert function.validation_certificate["graph"] == "checked"
    assert function.validation_certificate["linear_use"] == "checked"
    assert _operation_names(function) == Counter({"copy": 2, "discard": 1, "mul": 1})

    initial = _initial_sources(function)
    final = _final_frontier(function)
    output_sources = tuple(tuple(item["sources"]) for item in final)
    assert output_sources[0] == initial["t"]
    assert set(output_sources[1]) == {*initial["t"], *initial["K"]}
    assert output_sources[2] == initial["K"]
    assert initial["X"][0] not in {
        source for sources in output_sources for source in sources
    }

    interval = function.program_slice([], _node_ids(function))
    assert len(interval.result.lower_boundary) == 3
    assert len(interval.result.upper_boundary) == 3
    assert interval.result.through_wires == ()
    copy_events = [
        event for event in interval.result.event_history if event["kind"] == "copy"
    ]
    assert len(copy_events) == 2

    lower_lineage = {
        occurrence
        for crossing in function.causal_cut([]).frontier
        for occurrence in crossing["wire"]["lineage"]
    }
    upper_lineage = {
        occurrence
        for crossing in final
        for occurrence in crossing["wire"]["lineage"]
    }
    assert len(lower_lineage) == 3
    assert len(upper_lineage) == 4
    for event in copy_events:
        assert event["parent"] not in upper_lineage
        assert set(event["children"]) <= upper_lineage


def test_completed_source_support_projects_provenance_then_quotient_normalization(
    function: KernelFunction,
) -> None:
    surface = _support_observation(function).surface
    assert surface == DEPENDENCY_SURFACE
    assert _render(surface) == "[{}()]"

    traces = _normalization_traces(surface)
    assert len(traces) == 2
    assert {endpoint for endpoint, _ in traces} == {FLAT}
    split_traces = {
        tuple(step.detail for step in trace if step.kind == "split")
        for _, trace in traces
    }
    assert split_traces == {
        ("X>K", "X>t"),
        ("X>t", "X>K"),
    }
    assert len({trace for _, trace in traces}) == 2

    # Normalization only hides the dependency surface.  The checked residual
    # still reconstructs X -> {K, t} and the discarded old-X source.
    initial = _initial_sources(function)
    final = _final_frontier(function)
    assert set(final[1]["sources"]) == {*initial["t"], *initial["K"]}
    assert initial["X"][0] not in {
        source for crossing in final for source in crossing["sources"]
    }


def test_plain_split_label_is_a_trace_hint_not_an_identity_certificate() -> None:
    first = (Bracket("K", (Bracket("X"), Bracket("t"))),)
    second = (Bracket("K", (Bracket("t"), Bracket("X"))),)

    def split_k_x(forest: Forest) -> tuple[Forest, SurfaceStep]:
        return next(
            (candidate, step)
            for candidate, step in _split_steps(forest)
            if step.detail == "K>X"
        )

    first_output, first_step = split_k_x(first)
    second_output, second_step = split_k_x(second)

    assert first != second
    assert first_output == second_output
    assert first_step == second_step == SurfaceStep("split", "K>X")


def test_boolean_defect_observer_makes_checked_x_a_conditional_split(
    function: KernelFunction,
) -> None:
    normalized_states = 0
    for state in CORE_STATES:
        encoded = _encode_defect(state)
        assert _decode_defect(encoded) == state

        normalized, traces = _normalize_defect(encoded)
        checked_output = _evaluate_x(function, state)
        encoded_output = _encode_defect(checked_output)

        assert normalized == encoded_output
        assert _decode_defect(normalized) == checked_output
        if state == checked_output:
            assert encoded.surface == FLAT
        else:
            assert encoded.surface == DEFECT_SURFACE
        assert len(traces) == (1 if state == checked_output else 2)
        assert all(
            sum(step.kind == "split" for step in trace)
            == (0 if state == checked_output else 2)
            for trace in traces
        )
        normalized_states += state != checked_output

    # X has four fixed states and four one-bit defects.  Flattening the joint
    # two-edge dependency pattern is the finite quotient of the discarded bit.
    assert normalized_states == 4
    assert len({_evaluate_x(function, state) for state in CORE_STATES}) == 4


def test_pending_dependency_surface_can_be_flat_before_machine_quiescence(
    function: KernelFunction,
) -> None:
    nodes_by_operation: dict[str, list[int]] = {}
    for node in function.ir["nodes"]:
        nodes_by_operation.setdefault(node["operation"]["name"], []).append(node["id"])

    ready_cut = tuple(
        sorted((*nodes_by_operation["copy"], nodes_by_operation["mul"][0]))
    )
    all_nodes = _node_ids(function)
    discard = nodes_by_operation["discard"][0]

    lower = _pending_observation(function, ())
    ready = _pending_observation(function, ready_cut)
    upper = _pending_observation(function, all_nodes)

    assert lower.surface == DEPENDENCY_SURFACE
    assert not lower.quiescent
    assert ready.surface == FLAT
    assert not ready.quiescent
    assert discard not in ready_cut
    assert set(ready_cut) < set(all_nodes)
    assert function.causal_cut(ready_cut).certificate["completed_past"] == "checked"
    assert upper.surface == FLAT
    assert upper.quiescent

    # Surface satisfaction occurs once all three outputs are ready, but the
    # independent old-X discard still has to run before the slice is quiescent.
    pending = set(all_nodes) - set(ready_cut)
    assert pending == {discard}


def test_eight_checked_schedules_project_to_two_split_orders_and_one_endpoint(
    function: KernelFunction,
) -> None:
    node_ids = _node_ids(function)
    valid_schedules: list[tuple[int, ...]] = []
    for schedule in permutations(node_ids):
        completed: tuple[int, ...] = ()
        try:
            for event in schedule:
                step = function.advance_causal_cut(completed, event)
                completed = tuple(step.after["completed"])
        except ValueError:
            continue
        assert set(completed) == set(node_ids)
        valid_schedules.append(schedule)

    interval = function.program_slice([], node_ids)
    copy_events = {
        event["node"]: event
        for event in interval.result.event_history
        if event["kind"] == "copy"
    }
    occurrence_sources = {
        occurrence["id"]: occurrence["source"]
        for occurrence in interval.result.occurrences
    }
    source_domains = {
        source: domain
        for domain, sources in _initial_sources(function).items()
        for source in sources
    }
    copy_domains = {
        node: source_domains[occurrence_sources[event["parent"]]]
        for node, event in copy_events.items()
    }
    projected = Counter(
        tuple(copy_domains[event] for event in schedule if event in copy_domains)
        for schedule in valid_schedules
    )

    assert len(valid_schedules) == 8
    assert projected == Counter({("t", "K"): 4, ("K", "t"): 4})
    assert {
        tuple(
            step.detail.removeprefix("X>")
            for step in trace
            if step.kind == "split"
        )
        for _, trace in _normalization_traces(DEPENDENCY_SURFACE)
    } == set(projected)
    assert {
        endpoint for endpoint, _ in _normalization_traces(DEPENDENCY_SURFACE)
    } == {FLAT}


def test_graft_containment_is_compiler_owned_and_slices_only_intersect_it(
    function: KernelFunction,
) -> None:
    trace = function.graft_trace
    assert trace is not None
    assert trace.certificate["parent_child_nesting"] == "checked"
    assert trace.certificate["deterministic_frame_ids"] == "checked"
    assert trace.certificate["argument_body_regions"] == "checked"
    assert trace.certificate["call_history_links"] == "checked"
    assert [frame["kind"] for frame in trace.result.frames] == ["root", "call", "call"]

    root = trace.result.frames[0]
    outer = next(
        frame
        for frame in trace.result.frames
        if frame["kind"] == "call" and frame["callee"]["function"] == "spatial-update"
    )
    inner = next(
        frame
        for frame in trace.result.frames
        if frame["kind"] == "call" and frame["callee"]["function"] == "spatial-body"
    )
    assert outer["parent"] == root["id"]
    assert inner["parent"] == outer["id"]
    assert outer["id"] in root["children"]
    assert inner["id"] in outer["children"]
    assert outer["region_in_parent"] == {"kind": "root_body"}
    assert inner["region_in_parent"] == {"kind": "callee_body"}

    before = tuple(
        (frame["id"], frame["parent"], tuple(frame["children"]))
        for frame in trace.result.frames
    )
    interval = function.program_slice([], _node_ids(function))
    assert interval.result.graft_intersections is not None
    intersections = {
        item["frame"]: item for item in interval.result.graft_intersections
    }
    assert set(intersections) == {root["id"], outer["id"], inner["id"]}
    assert intersections[root["id"]]["body_events"] == list(_node_ids(function))
    assert intersections[outer["id"]]["body_events"] == list(_node_ids(function))

    copy_ids = [
        node["id"]
        for node in function.ir["nodes"]
        if node["operation"]["name"] == "copy"
    ]
    mul_id = next(
        node["id"]
        for node in function.ir["nodes"]
        if node["operation"]["name"] == "mul"
    )
    assert intersections[inner["id"]]["argument_events"] == [
        {"argument_index": 0, "events": copy_ids}
    ]
    assert intersections[inner["id"]]["body_events"] == [mul_id]

    after_trace = function.graft_trace
    assert after_trace is not None
    after = tuple(
        (frame["id"], frame["parent"], tuple(frame["children"]))
        for frame in after_trace.result.frames
    )
    assert after == before
    assert interval.certificate["graft_frame_consistency"] == "checked"
    assert interval.certificate["original_id_preservation"] == "checked"
    assert interval.certificate["lineage_preservation"] == "checked"
