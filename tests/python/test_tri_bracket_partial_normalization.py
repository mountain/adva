from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from functools import lru_cache
from itertools import permutations
from typing import Literal, TypeAlias


Domain: TypeAlias = Literal["K", "X", "t"]
DOMAINS: tuple[Domain, ...] = ("K", "X", "t")
DOMAIN_ORDER = {domain: index for index, domain in enumerate(DOMAINS)}
OPEN = {"K": "{", "X": "[", "t": "("}
CLOSE = {"K": "}", "X": "]", "t": ")"}
OPEN_DOMAIN = {glyph: domain for domain, glyph in OPEN.items()}
CLOSE_DOMAIN = {glyph: domain for domain, glyph in CLOSE.items()}


@dataclass(frozen=True)
class Bracket:
    domain: Domain
    children: tuple[Bracket, ...] = ()


Forest: TypeAlias = tuple[Bracket, ...]


@dataclass(frozen=True)
class Shape:
    children: tuple[Shape, ...] = ()


@dataclass(frozen=True)
class Step:
    kind: Literal["split", "exchange", "inject"]
    detail: str


@dataclass(frozen=True)
class Residual:
    target: frozenset[Domain]
    stable: frozenset[Domain]
    missing: frozenset[Domain]
    nesting_edges: int
    boundary_inversions: int
    enabled: tuple[str, ...]
    trace: tuple[Step, ...] = ()


@dataclass(frozen=True)
class Judgment:
    status: Literal["satisfied", "open", "unknown"]
    term: Forest
    residual: Residual


@dataclass(frozen=True)
class ActiveMachine:
    term: Forest
    phase: Literal["inject", "split"]
    trace: tuple[Step, ...] = ()


def _render(forest: Forest) -> str:
    def render_bracket(bracket: Bracket) -> str:
        return (
            OPEN[bracket.domain]
            + "".join(render_bracket(child) for child in bracket.children)
            + CLOSE[bracket.domain]
        )

    return "".join(render_bracket(root) for root in forest)


def _parse_tricell(source: str) -> Forest:
    """Parse one finite cell containing exactly one bracket of each color."""

    roots: list[Bracket] = []
    stack: list[tuple[Domain, list[Bracket]]] = []
    seen: set[Domain] = set()
    for glyph in source:
        if glyph in OPEN_DOMAIN:
            domain = OPEN_DOMAIN[glyph]
            if domain in seen:
                raise ValueError(f"the first tri-cell has one {domain} bracket")
            seen.add(domain)
            stack.append((domain, []))
            continue
        if glyph not in CLOSE_DOMAIN or not stack:
            raise ValueError(f"invalid tri-bracket glyph {glyph!r}")
        domain = CLOSE_DOMAIN[glyph]
        opened, children = stack.pop()
        if opened != domain:
            raise ValueError(f"mismatched {OPEN[opened]} ... {glyph}")
        bracket = Bracket(domain, tuple(children))
        if stack:
            stack[-1][1].append(bracket)
        else:
            roots.append(bracket)
    if stack:
        raise ValueError("unclosed tri-bracket")
    if seen != set(DOMAINS):
        raise ValueError("the first tri-cell requires K, X, and t exactly once")
    return tuple(roots)


@lru_cache(maxsize=None)
def _forest_shapes(size: int) -> tuple[tuple[Shape, ...], ...]:
    """All ordered forests with ``size`` unlabeled nodes."""

    if size == 0:
        return ((),)
    result: list[tuple[Shape, ...]] = []
    for root_size in range(1, size + 1):
        for children in _forest_shapes(root_size - 1):
            root = Shape(children)
            for suffix in _forest_shapes(size - root_size):
                result.append((root, *suffix))
    return tuple(result)


def _label_forest(
    shapes: tuple[Shape, ...],
    labels: tuple[Domain, ...],
) -> Forest:
    position = 0

    def label_shape(shape: Shape) -> Bracket:
        nonlocal position
        domain = labels[position]
        position += 1
        return Bracket(domain, tuple(label_shape(child) for child in shape.children))

    result = tuple(label_shape(shape) for shape in shapes)
    assert position == len(labels)
    return result


def _all_tricells() -> tuple[Forest, ...]:
    return tuple(
        _label_forest(shape, coloring)
        for shape in _forest_shapes(3)
        for coloring in permutations(DOMAINS)
    )


def _walk(forest: Forest) -> Iterator[Bracket]:
    for root in forest:
        yield root
        yield from _walk(root.children)


def _descendant_domains(bracket: Bracket) -> frozenset[Domain]:
    return frozenset(child.domain for child in _walk(bracket.children))


def _stable_domains(forest: Forest) -> frozenset[Domain]:
    """A domain is stable when its bracket contains no foreign color."""

    return frozenset(
        bracket.domain
        for bracket in _walk(forest)
        if _descendant_domains(bracket) <= {bracket.domain}
    )


def _nesting_edges(forest: Forest) -> int:
    return sum(len(bracket.children) for bracket in _walk(forest))


def _boundary_inversions(forest: Forest) -> int:
    roots = [DOMAIN_ORDER[root.domain] for root in forest]
    return sum(
        roots[left] > roots[right]
        for left in range(len(roots))
        for right in range(left + 1, len(roots))
    )


def _measure(forest: Forest) -> tuple[int, int]:
    return (_nesting_edges(forest), _boundary_inversions(forest))


def _is_eigenform(forest: Forest) -> bool:
    return _nesting_edges(forest) == 0


def _is_calibrated(forest: Forest) -> bool:
    return _is_eigenform(forest) and tuple(root.domain for root in forest) == DOMAINS


def _split_steps(forest: Forest) -> tuple[tuple[Forest, Step], ...]:
    """Cut one root-to-child containment edge and promote the child to a root."""

    results: list[tuple[Forest, Step]] = []
    for root_index, root in enumerate(forest):
        for child_index, child in enumerate(root.children):
            remaining = root.children[:child_index] + root.children[child_index + 1 :]
            promoted_parent = Bracket(root.domain, remaining)
            candidate = (
                forest[:root_index]
                + (promoted_parent, child)
                + forest[root_index + 1 :]
            )
            step = Step("split", f"{root.domain}>{child.domain}")
            assert _measure(candidate) < _measure(forest)
            results.append((candidate, step))
    return tuple(results)


def _exchange_steps(forest: Forest) -> tuple[tuple[Forest, Step], ...]:
    """Use the unsigned S3 endpoint projection only on the flat sort."""

    if _nesting_edges(forest):
        return ()
    results: list[tuple[Forest, Step]] = []
    for index, (left, right) in enumerate(zip(forest, forest[1:], strict=False)):
        if DOMAIN_ORDER[left.domain] <= DOMAIN_ORDER[right.domain]:
            continue
        candidate = forest[:index] + (right, left) + forest[index + 2 :]
        step = Step("exchange", f"s_{index + 1}:{left.domain}/{right.domain}")
        assert _measure(candidate) < _measure(forest)
        results.append((candidate, step))
    return tuple(results)


def _normalizing_steps(forest: Forest) -> tuple[tuple[Forest, Step], ...]:
    return _split_steps(forest) if _nesting_edges(forest) else _exchange_steps(forest)


def _normal_endpoints(start: Forest) -> frozenset[Forest]:
    frontier = [start]
    visited: set[Forest] = set()
    endpoints: set[Forest] = set()
    while frontier:
        current = frontier.pop()
        if current in visited:
            continue
        visited.add(current)
        steps = _normalizing_steps(current)
        if not steps:
            endpoints.add(current)
        else:
            frontier.extend(candidate for candidate, _ in steps)
    return frozenset(endpoints)


def _normalization_traces(start: Forest) -> tuple[tuple[Step, ...], ...]:
    traces: list[tuple[Step, ...]] = []

    def visit(current: Forest, trace: tuple[Step, ...]) -> None:
        steps = _normalizing_steps(current)
        if not steps:
            assert _is_calibrated(current)
            traces.append(trace)
            return
        for candidate, step in steps:
            visit(candidate, (*trace, step))

    visit(start, ())
    return tuple(traces)


def _enabled(forest: Forest) -> tuple[str, ...]:
    return tuple(step.detail for _, step in _normalizing_steps(forest))


def _judge(
    forest: Forest,
    target: Iterable[Domain],
    trace: tuple[Step, ...] = (),
) -> Judgment:
    requested = frozenset(target)
    if not requested or not requested <= set(DOMAINS):
        raise ValueError("a requested face is a nonempty subset of {K, X, t}")
    stable = _stable_domains(forest)
    residual = Residual(
        target=requested,
        stable=stable,
        missing=requested - stable,
        nesting_edges=_nesting_edges(forest),
        boundary_inversions=_boundary_inversions(forest),
        enabled=_enabled(forest),
        trace=trace,
    )
    status = "satisfied" if requested <= stable else "open"
    return Judgment(status, forest, residual)


def _inject_first_pair(forest: Forest) -> tuple[Forest, Step]:
    """Consume two empty adjacent roots and create one mixed containment edge."""

    if len(forest) < 2 or forest[0].children or forest[1].children:
        raise ValueError("the bounded inject gate expects two adjacent empty roots")
    outer, inner = forest[0], forest[1]
    candidate = (Bracket(outer.domain, (inner,)), *forest[2:])
    return candidate, Step("inject", f"{outer.domain}>{inner.domain}")


def _active_step(machine: ActiveMachine) -> ActiveMachine:
    if machine.phase == "inject":
        term, step = _inject_first_pair(machine.term)
        return ActiveMachine(term, "split", (*machine.trace, step))
    splits = _split_steps(machine.term)
    if not splits:
        raise ValueError("the active split phase has no containment edge")
    term, step = splits[0]
    return ActiveMachine(term, "inject", (*machine.trace, step))


def _run_active_with_fuel(machine: ActiveMachine, fuel: int) -> Judgment:
    current = machine
    for _ in range(fuel):
        current = _active_step(current)
    stable = _stable_domains(current.term)
    pending = (f"active:{current.phase}",)
    residual = Residual(
        target=frozenset(DOMAINS),
        stable=stable,
        missing=frozenset(DOMAINS) - stable,
        nesting_edges=_nesting_edges(current.term),
        boundary_inversions=_boundary_inversions(current.term),
        enabled=pending,
        trace=current.trace,
    )
    # A normal-looking surface is not quiescent while an active gate remains.
    return Judgment("unknown", current.term, residual)


def test_the_first_mixed_grammar_has_exactly_thirty_colored_catalan_forms() -> None:
    tricells = _all_tricells()

    assert len(_forest_shapes(3)) == 5
    assert len(tricells) == 30
    assert len({_render(term) for term in tricells}) == 30
    assert all(_parse_tricell(_render(term)) == term for term in tricells)
    assert _parse_tricell("{[()]}") == (
        Bracket("K", (Bracket("X", (Bracket("t"),)),)),
    )
    assert _render(_parse_tricell("{}[]()")) == "{}[]()"

    for invalid in ("", "{}[]", "{{}}[]()", "{[)]}", "{x}[]()"):
        try:
            _parse_tricell(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError(f"the tri-cell grammar accepted {invalid!r}")


def test_the_seven_nonempty_stable_faces_are_exactly_the_leaf_color_sets() -> None:
    counts = Counter(_stable_domains(term) for term in _all_tricells())
    expected_faces = {
        frozenset(face)
        for size in (1, 2, 3)
        for face in permutations(DOMAINS, size)
    }

    assert set(counts) == expected_faces
    assert len(counts) == 7
    assert frozenset() not in counts
    assert counts == Counter(
        {
            frozenset({"K"}): 2,
            frozenset({"X"}): 2,
            frozenset({"t"}): 2,
            frozenset({"K", "X"}): 6,
            frozenset({"X", "t"}): 6,
            frozenset({"K", "t"}): 6,
            frozenset(DOMAINS): 6,
        }
    )

    # Target predicates overlap; the exact stable set supplies the disjoint
    # seven-face stratification.  A fully stable term satisfies every target.
    canonical = _parse_tricell("{}[]()")
    assert all(
        _judge(canonical, face).status == "satisfied"
        for face in expected_faces
    )


def test_split_plus_oriented_exchange_normalizes_all_thirty_forms() -> None:
    canonical = _parse_tricell("{}[]()")
    for term in _all_tricells():
        assert _normal_endpoints(term) == frozenset({canonical})
        for candidate, _ in _normalizing_steps(term):
            assert _measure(candidate) < _measure(term)

    nested = [term for term in _all_tricells() if _nesting_edges(term)]
    eigenforms = [term for term in _all_tricells() if _is_eigenform(term)]
    assert len(nested) == 24
    assert len(eigenforms) == 6
    assert sum(_is_calibrated(term) for term in eigenforms) == 1


def test_coxeter_exchange_is_unavailable_on_nested_terms() -> None:
    nested = [term for term in _all_tricells() if _nesting_edges(term)]
    assert len(nested) == 24

    for term in nested:
        assert _exchange_steps(term) == ()
        assert not _is_eigenform(term)


def test_split_schedules_converge_but_retain_distinct_raw_traces() -> None:
    branching = _parse_tricell("{[]()}")
    traces = _normalization_traces(branching)

    assert len(traces) >= 2
    assert len(set(traces)) == len(traces)
    assert {step.detail for trace in traces for step in trace if step.kind == "split"} == {
        "K>X",
        "K>t",
    }
    assert _normal_endpoints(branching) == frozenset({_parse_tricell("{}[]()")})


def test_three_root_exchange_has_a_yang_baxter_critical_pair() -> None:
    reverse = _parse_tricell("()[]{}")

    def take(term: Forest, index: int) -> tuple[Forest, Step]:
        candidates = {
            int(step.detail.split(":", 1)[0].removeprefix("s_")) - 1: (next_term, step)
            for next_term, step in _exchange_steps(term)
        }
        return candidates[index]

    left = reverse
    left_trace: list[Step] = []
    for index in (0, 1, 0):
        left, step = take(left, index)
        left_trace.append(step)

    right = reverse
    right_trace: list[Step] = []
    for index in (1, 0, 1):
        right, step = take(right, index)
        right_trace.append(step)

    assert left == right == _parse_tricell("{}[]()")
    assert tuple(left_trace) != tuple(right_trace)
    assert [step.detail.split(":", 1)[0] for step in left_trace] == [
        "s_1",
        "s_2",
        "s_1",
    ]
    assert [step.detail.split(":", 1)[0] for step in right_trace] == [
        "s_2",
        "s_1",
        "s_2",
    ]


def test_partial_judgment_returns_the_open_complement_as_residual() -> None:
    term = _parse_tricell("{[()]}")

    temporal = _judge(term, {"t"})
    spatial_temporal = _judge(term, {"X", "t"})

    assert temporal.status == "satisfied"
    assert temporal.residual.stable == frozenset({"t"})
    assert temporal.residual.missing == frozenset()
    assert temporal.residual.nesting_edges == 2
    assert spatial_temporal.status == "open"
    assert spatial_temporal.residual.missing == frozenset({"X"})
    assert spatial_temporal.residual.enabled


def test_an_active_inject_gate_reopens_a_normalized_domain_and_prevents_quiescence() -> None:
    canonical = _parse_tricell("{}[]()")
    injected, inject = _inject_first_pair(canonical)

    assert _render(injected) == "{[]}()"
    assert _stable_domains(injected) == frozenset({"X", "t"})
    assert _judge(injected, {"K", "X", "t"}, (inject,)).status == "open"

    split_back, split = _split_steps(injected)[0]
    assert split_back == canonical
    assert inject.kind == "inject"
    assert split.kind == "split"

    machine = ActiveMachine(canonical, "inject")
    after_two = _active_step(_active_step(machine))
    assert after_two.term == canonical
    assert after_two.phase == "inject"
    assert after_two.trace != machine.trace

    exhausted = _run_active_with_fuel(machine, fuel=6)
    assert exhausted.status == "unknown"
    assert exhausted.term == canonical
    assert exhausted.residual.stable == frozenset(DOMAINS)
    assert exhausted.residual.enabled == ("active:inject",)
    assert len(exhausted.residual.trace) == 6
