from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Any

from adva import link_modules


HANDLE_CALIBRATION_KERNEL = r"""
(module decorated-handle
  (export fork-recombine)

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
)
"""


@dataclass(frozen=True, slots=True)
class BoundaryCircle:
    """One ordered external circle in a research-local cobordism shadow."""

    component: int
    label: str


@dataclass(frozen=True, slots=True)
class SurfaceComponent:
    """One connected orientable component, recorded by exact classification data."""

    euler_characteristic: int
    events: frozenset[int]
    decorations: tuple[tuple[int, str], ...]


@dataclass(frozen=True, slots=True)
class DecoratedCobordism:
    """A finite topological presentation derived from checked event identities.

    This is deliberately not an Adva semantic object.  It records only the
    classification data of connected orientable surfaces and the exact event
    labels used to assemble them.  Composition glues every ordered outgoing
    circle to the corresponding incoming circle.  Since a circle has Euler
    characteristic zero, component Euler characteristics add under gluing.
    """

    components: tuple[SurfaceComponent, ...]
    inputs: tuple[BoundaryCircle, ...]
    outputs: tuple[BoundaryCircle, ...]

    def __post_init__(self) -> None:
        for boundary in (*self.inputs, *self.outputs):
            if boundary.component < 0 or boundary.component >= len(self.components):
                raise ValueError("a boundary circle must name an existing component")
        all_events = [event for component in self.components for event in component.events]
        if len(all_events) != len(set(all_events)):
            raise ValueError("one checked event cannot occur in two surface components")
        for index in range(len(self.components)):
            self.genus(index)

    def genus(self, component: int) -> int:
        boundary_count = sum(
            boundary.component == component
            for boundary in (*self.inputs, *self.outputs)
        )
        numerator = 2 - boundary_count - self.components[component].euler_characteristic
        if numerator < 0 or numerator % 2:
            raise ValueError("the component data do not classify an orientable surface")
        return numerator // 2

    def then(self, following: DecoratedCobordism) -> DecoratedCobordism:
        """Glue this trace to the following trace in exact boundary order."""

        if len(self.outputs) != len(following.inputs):
            raise ValueError("cobordism composition requires equal middle arity")
        if self.event_ids & following.event_ids:
            raise ValueError("composition cannot execute one checked event twice")

        offset = len(self.components)
        all_components = (*self.components, *following.components)
        parent = list(range(len(all_components)))

        def find(item: int) -> int:
            while parent[item] != item:
                parent[item] = parent[parent[item]]
                item = parent[item]
            return item

        def union(left: int, right: int) -> None:
            left_root = find(left)
            right_root = find(right)
            if left_root != right_root:
                parent[right_root] = left_root

        for outgoing, incoming in zip(self.outputs, following.inputs, strict=True):
            union(outgoing.component, offset + incoming.component)

        grouped: dict[int, list[int]] = {}
        for index in range(len(all_components)):
            grouped.setdefault(find(index), []).append(index)
        roots = sorted(grouped, key=lambda root: min(grouped[root]))
        new_index = {root: index for index, root in enumerate(roots)}

        components = []
        for root in roots:
            members = grouped[root]
            component_events = frozenset(
                event
                for member in members
                for event in all_components[member].events
            )
            components.append(
                SurfaceComponent(
                    euler_characteristic=sum(
                        all_components[member].euler_characteristic
                        for member in members
                    ),
                    events=component_events,
                    decorations=tuple(
                        sorted(
                            decoration
                            for member in members
                            for decoration in all_components[member].decorations
                        )
                    ),
                )
            )

        def remap_left(boundary: BoundaryCircle) -> BoundaryCircle:
            return BoundaryCircle(
                new_index[find(boundary.component)],
                boundary.label,
            )

        def remap_right(boundary: BoundaryCircle) -> BoundaryCircle:
            return BoundaryCircle(
                new_index[find(offset + boundary.component)],
                boundary.label,
            )

        return DecoratedCobordism(
            components=tuple(components),
            inputs=tuple(remap_left(boundary) for boundary in self.inputs),
            outputs=tuple(remap_right(boundary) for boundary in following.outputs),
        )

    @property
    def event_ids(self) -> frozenset[int]:
        return frozenset(
            event for component in self.components for event in component.events
        )

    @property
    def canonical_signature(self) -> tuple[Any, ...]:
        """Forget construction parentheses but retain topology and decorations."""

        records = []
        for component, data in enumerate(self.components):
            records.append(
                (
                    self.genus(component),
                    data.euler_characteristic,
                    tuple(
                        index
                        for index, boundary in enumerate(self.inputs)
                        if boundary.component == component
                    ),
                    tuple(
                        index
                        for index, boundary in enumerate(self.outputs)
                        if boundary.component == component
                    ),
                    tuple(sorted(data.events)),
                    data.decorations,
                )
            )
        return tuple(sorted(records))


def _connected_patch(
    name: str,
    event: int,
    input_count: int,
    output_count: int,
    *,
    genus: int = 0,
) -> DecoratedCobordism:
    boundary_count = input_count + output_count
    component = SurfaceComponent(
        euler_characteristic=2 - 2 * genus - boundary_count,
        events=frozenset({event}),
        decorations=((event, name),),
    )
    return DecoratedCobordism(
        components=(component,),
        inputs=tuple(
            BoundaryCircle(0, f"{name}:input:{index}")
            for index in range(input_count)
        ),
        outputs=tuple(
            BoundaryCircle(0, f"{name}:output:{index}")
            for index in range(output_count)
        ),
    )


def _tensor(*cobordisms: DecoratedCobordism) -> DecoratedCobordism:
    components: list[SurfaceComponent] = []
    inputs: list[BoundaryCircle] = []
    outputs: list[BoundaryCircle] = []
    events: set[int] = set()
    for cobordism in cobordisms:
        if events & cobordism.event_ids:
            raise ValueError("tensor product cannot duplicate a checked event")
        events.update(cobordism.event_ids)
        offset = len(components)
        components.extend(cobordism.components)
        inputs.extend(
            BoundaryCircle(offset + boundary.component, boundary.label)
            for boundary in cobordism.inputs
        )
        outputs.extend(
            BoundaryCircle(offset + boundary.component, boundary.label)
            for boundary in cobordism.outputs
        )
    return DecoratedCobordism(tuple(components), tuple(inputs), tuple(outputs))


def _diamond() -> Any:
    workspace = link_modules([HANDLE_CALIBRATION_KERNEL])
    return workspace.function("decorated-handle", "fork-recombine")


def _predecessors(function: Any) -> dict[int, frozenset[int]]:
    return {
        node["id"]: frozenset(
            wire["producer"]["node"]
            for wire in node["inputs"]
            if wire["producer"]["kind"] == "node"
        )
        for node in function.ir["nodes"]
    }


def _completed_pasts(function: Any) -> tuple[frozenset[int], ...]:
    predecessors = _predecessors(function)
    nodes = tuple(predecessors)
    result = []
    for size in range(len(nodes) + 1):
        for choice in combinations(nodes, size):
            selected = frozenset(choice)
            if all(predecessors[event] <= selected for event in selected):
                result.append(selected)
    return tuple(result)


def _schedules(function: Any) -> tuple[tuple[int, ...], ...]:
    predecessors = _predecessors(function)
    nodes = tuple(predecessors)
    target = frozenset(nodes)
    result: list[tuple[int, ...]] = []

    def visit(completed: frozenset[int], prefix: tuple[int, ...]) -> None:
        if completed == target:
            result.append(prefix)
            return
        for event in nodes:
            if event not in completed and predecessors[event] <= completed:
                visit(completed | {event}, (*prefix, event))

    visit(frozenset(), ())
    return tuple(result)


def _consumer_key(consumer: dict[str, Any]) -> str:
    if consumer["kind"] == "output":
        return f"output:{consumer['index']}"
    return f"node:{consumer['node']}:{consumer['input_index']}"


def _producer_key(producer: dict[str, Any]) -> str:
    if producer["kind"] == "input":
        return f"input:{producer['index']}"
    return f"node:{producer['node']}"


def _all_cut_wires(
    function: Any,
    pasts: tuple[frozenset[int], ...],
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for completed in pasts:
        for wire in function.causal_cut(tuple(completed)).frontier:
            result[_consumer_key(wire["consumer"])] = dict(wire)
    return result


def _cut_support(function: Any, completed: frozenset[int]) -> frozenset[str]:
    return frozenset(
        _consumer_key(wire["consumer"])
        for wire in function.causal_cut(tuple(completed)).frontier
    )


def _event_boundaries(
    function: Any,
    pasts: tuple[frozenset[int], ...],
) -> dict[int, frozenset[str]]:
    wires = _all_cut_wires(function, pasts)
    return {
        event: frozenset(
            edge_id
            for edge_id, wire in wires.items()
            if _producer_key(wire["wire"]["producer"]) == f"node:{event}"
            or edge_id.startswith(f"node:{event}:")
        )
        for event in _predecessors(function)
    }


def _interval_face_boundary(
    boundaries: dict[int, frozenset[str]],
    lower: frozenset[int],
    upper: frozenset[int],
) -> frozenset[str]:
    result: frozenset[str] = frozenset()
    for event in upper - lower:
        result ^= boundaries[event]
    return result


def _handle_patches(function: Any, *, copy_genus: int = 0):
    operations = {
        node["operation"]["name"]: node["id"]
        for node in function.ir["nodes"]
    }
    assert tuple(node["operation"]["name"] for node in function.ir["nodes"]) == (
        "copy",
        "neg",
        "id",
        "add",
    )
    copy = _connected_patch(
        "copy-copants",
        operations["copy"],
        1,
        2,
        genus=copy_genus,
    )
    branches = _tensor(
        _connected_patch("neg-cylinder", operations["neg"], 1, 1),
        _connected_patch("id-cylinder", operations["id"], 1, 1),
    )
    add = _connected_patch("add-pants", operations["add"], 2, 1)
    return copy, branches, add


def test_interval_face_chain_integrates_every_checked_surgery() -> None:
    function = _diamond()
    pasts = _completed_pasts(function)
    boundaries = _event_boundaries(function, pasts)

    checked_pairs = 0
    checked_triples = 0
    for lower in pasts:
        for upper in pasts:
            if not lower <= upper:
                continue
            checked_pairs += 1
            assert _interval_face_boundary(boundaries, lower, upper) == (
                _cut_support(function, lower) ^ _cut_support(function, upper)
            )
            for outer in pasts:
                if not upper <= outer:
                    continue
                checked_triples += 1
                assert _interval_face_boundary(boundaries, lower, outer) == (
                    _interval_face_boundary(boundaries, lower, upper)
                    ^ _interval_face_boundary(boundaries, upper, outer)
                )

    assert checked_pairs > len(pasts)
    assert checked_triples > checked_pairs


def test_minimal_split_branch_merge_trace_is_a_decorated_genus_one_handle() -> None:
    function = _diamond()
    copy, branches, add = _handle_patches(function)
    handle = copy.then(branches).then(add)

    assert len(handle.components) == 1
    assert len(handle.inputs) == len(handle.outputs) == 1
    assert handle.components[0].euler_characteristic == -2
    assert handle.genus(0) == 1
    assert handle.event_ids == frozenset(node["id"] for node in function.ir["nodes"])
    assert handle.components[0].decorations == (
        (0, "copy-copants"),
        (1, "neg-cylinder"),
        (2, "id-cylinder"),
        (3, "add-pants"),
    )


def test_handle_trace_composition_is_associative_after_exact_boundary_gluing() -> None:
    function = _diamond()
    copy, branches, add = _handle_patches(function)

    left_associated = copy.then(branches).then(add)
    right_associated = copy.then(branches.then(add))

    assert left_associated.canonical_signature == right_associated.canonical_signature


def test_independent_schedules_remain_distinct_but_share_one_trace_surface() -> None:
    function = _diamond()
    copy, branches, add = _handle_patches(function)
    handle = copy.then(branches).then(add)
    schedules = _schedules(function)

    assert schedules == ((0, 1, 2, 3), (0, 2, 1, 3))
    assert schedules[0] != schedules[1]
    assert handle.canonical_signature == copy.then(branches).then(add).canonical_signature
    assert handle.components[0].decorations == tuple(
        sorted(handle.components[0].decorations)
    )


def test_event_arity_alone_does_not_force_the_minimal_handle() -> None:
    function = _diamond()
    minimal_copy, branches, add = _handle_patches(function)
    hidden_handle_copy, _, _ = _handle_patches(function, copy_genus=1)

    minimal = minimal_copy.then(branches).then(add)
    nonminimal = hidden_handle_copy.then(branches).then(add)

    assert len(minimal.inputs) == len(nonminimal.inputs) == 1
    assert len(minimal.outputs) == len(nonminimal.outputs) == 1
    assert minimal.event_ids == nonminimal.event_ids
    assert minimal.genus(0) == 1
    assert nonminimal.genus(0) == 2
    assert minimal.canonical_signature != nonminimal.canonical_signature
