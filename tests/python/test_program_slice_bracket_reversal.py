"""Checked-grounded research observer; Python creates no semantic identity."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal

import pytest
from adva import KernelFunction, link_modules

BRACKET_REVERSAL = r"""
(module bracket-reversal
  (export identity-triad cycle-triad spatial-mul spatial-add)

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

  (def cycle-triad
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (swap
          (frontier
            (use temporal)
            (use spatial)))
        (use construction))))

  (def identity-triad
    (fn ((temporal Real) (spatial Real) (construction Real))
        (outputs Real Real Real)
      (frontier
        (use temporal)
        (use spatial)
        (use construction))))
)
"""


class Domain(Enum):
    CONSTRUCTIVE = "K"
    SPATIAL = "X"
    TEMPORAL = "t"


CANONICAL_DOMAINS = (Domain.CONSTRUCTIVE, Domain.SPATIAL, Domain.TEMPORAL)
INPUT_DOMAINS = (Domain.TEMPORAL, Domain.SPATIAL, Domain.CONSTRUCTIVE)
OUTPUT_DOMAINS = INPUT_DOMAINS
DOMAIN_ORDER = {domain: index for index, domain in enumerate(CANONICAL_DOMAINS)}
GLYPHS = {
    Domain.CONSTRUCTIVE: "{}",
    Domain.SPATIAL: "[]",
    Domain.TEMPORAL: "()",
}
OBSERVER_POLICY = "adva.research.program-slice-bracket-reversal.v0"


class NotRepresentable(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class BoundaryEndpoint:
    cut_role: Literal["lower", "upper"]
    crossing_json: str


@dataclass(frozen=True, slots=True)
class BracketPair:
    domain: Domain
    opening: BoundaryEndpoint
    closing: BoundaryEndpoint
    orientation: int

    def __post_init__(self) -> None:
        if self.orientation not in {-1, 1}:
            raise ValueError("a bracket-pair orientation must be signed")
        if self.opening.cut_role == self.closing.cut_role:
            raise ValueError("a bracket pair needs one endpoint from each cut")

    def flipped(self) -> BracketPair:
        return BracketPair(
            domain=self.domain,
            opening=self.closing,
            closing=self.opening,
            orientation=-self.orientation,
        )


@dataclass(frozen=True, slots=True)
class DualSurfaceObservation:
    observer_policy: str
    raw_pairs: tuple[BracketPair, ...]
    normalized_pairs: tuple[BracketPair, ...]
    normalization_permutation: tuple[int, ...]
    surface: str
    checked_slice_json: str
    derivation_certificate_json: str


@pytest.fixture(scope="module")
def workspace():
    return link_modules([BRACKET_REVERSAL])


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _node_ids(function: KernelFunction) -> tuple[int, ...]:
    return tuple(node["id"] for node in function.ir["nodes"])


def _render(pairs: tuple[BracketPair, ...]) -> str:
    return "".join(GLYPHS[pair.domain] for pair in pairs)


def _surface_star(
    pairs: tuple[BracketPair, ...],
) -> tuple[tuple[BracketPair, ...], tuple[BracketPair, ...], tuple[int, ...]]:
    raw = tuple(pair.flipped() for pair in reversed(pairs))
    normalized = tuple(sorted(raw, key=lambda pair: DOMAIN_ORDER[pair.domain]))
    permutation = tuple(
        next(index for index, pair in enumerate(raw) if pair.domain is domain)
        for domain in CANONICAL_DOMAINS
    )
    return raw, normalized, permutation


def _require_checked(function: KernelFunction, analysis: Any) -> None:
    if function.validation_certificate["graph"] != "checked":
        raise NotRepresentable("the source diagram is not Rust-validated")
    if function.validation_certificate["linear_use"] != "checked":
        raise NotRepresentable("the source diagram lacks checked linear use")

    certificate = analysis.certificate
    if "exact_composition" in certificate:
        required = (
            "diagram_integrity",
            "inputs_revalidated",
            "boundary_agreement",
            "event_partition",
            "original_id_preservation",
            "lineage_preservation",
            "exact_composition",
        )
    else:
        required = (
            "diagram_integrity",
            "lower_past",
            "upper_past",
            "past_inclusion",
            "event_difference",
            "boundary_partition",
            "internal_events",
            "original_id_preservation",
            "lineage_preservation",
        )
    if any(certificate[field] != "checked" for field in required):
        raise NotRepresentable("the ProgramSlice derivation is not fully checked")


def _lower_crossings(analysis: Any) -> dict[Domain, Any]:
    result: dict[Domain, Any] = {}
    for crossing in analysis.result.lower["frontier"]:
        producer = crossing["wire"]["producer"]
        if producer["kind"] != "input":
            raise NotRepresentable("V0 requires the complete initial lower cut")
        domain = INPUT_DOMAINS[producer["index"]]
        if domain in result:
            raise NotRepresentable("the lower cut repeats one observer domain")
        result[domain] = crossing
    if set(result) != set(CANONICAL_DOMAINS):
        raise NotRepresentable("the lower cut is not a complete triad")
    return result


def _upper_crossings(analysis: Any) -> dict[Domain, Any]:
    result: dict[Domain, Any] = {}
    for crossing in analysis.result.upper["frontier"]:
        consumer = crossing["consumer"]
        if consumer["kind"] != "output":
            raise NotRepresentable("V0 requires the complete output-ready upper cut")
        domain = OUTPUT_DOMAINS[consumer["index"]]
        if domain in result:
            raise NotRepresentable("the upper cut repeats one observer domain")
        result[domain] = crossing
    if set(result) != set(CANONICAL_DOMAINS):
        raise NotRepresentable("the upper cut is not a complete triad")
    return result


def _slice_snapshot(function: KernelFunction, analysis: Any) -> str:
    result = analysis.result
    payload = {
        "observer_policy": OBSERVER_POLICY,
        "input_domains": tuple(domain.value for domain in INPUT_DOMAINS),
        "output_domains": tuple(domain.value for domain in OUTPUT_DOMAINS),
        "display_order": tuple(domain.value for domain in CANONICAL_DOMAINS),
        "ir": function.ir,
        "validation_certificate": function.validation_certificate,
        "slice": {
            "lower": result.lower,
            "upper": result.upper,
            "events": result.events,
            "lower_boundary": result.lower_boundary,
            "upper_boundary": result.upper_boundary,
            "through_wires": result.through_wires,
            "internal_events": result.internal_events,
            "occurrences": result.occurrences,
            "event_history": result.event_history,
            "graft_intersections": result.graft_intersections,
        },
    }
    return _canonical_json(payload)


def _observe(function: KernelFunction, analysis: Any) -> DualSurfaceObservation:
    _require_checked(function, analysis)
    node_ids = _node_ids(function)
    if tuple(analysis.result.lower["completed"]) != ():
        raise NotRepresentable("V0 requires the initial lower causal past")
    if tuple(analysis.result.upper["completed"]) != node_ids:
        raise NotRepresentable("V0 requires the complete upper causal past")

    lower = _lower_crossings(analysis)
    upper = _upper_crossings(analysis)
    forward_pairs = tuple(
        BracketPair(
            domain=domain,
            opening=BoundaryEndpoint("lower", _canonical_json(lower[domain])),
            closing=BoundaryEndpoint("upper", _canonical_json(upper[domain])),
            orientation=1,
        )
        for domain in CANONICAL_DOMAINS
    )
    raw, normalized, permutation = _surface_star(forward_pairs)
    return DualSurfaceObservation(
        observer_policy=OBSERVER_POLICY,
        raw_pairs=raw,
        normalized_pairs=normalized,
        normalization_permutation=permutation,
        surface=_render(normalized),
        checked_slice_json=_slice_snapshot(function, analysis),
        derivation_certificate_json=_canonical_json(analysis.certificate),
    )


def _full_observation(function: KernelFunction) -> DualSurfaceObservation:
    return _observe(function, function.program_slice([], _node_ids(function)))


def test_each_pair_flips_then_outer_order_normalizes(workspace) -> None:
    function = workspace.function("bracket-reversal", "cycle-triad")
    observation = _full_observation(function)

    assert tuple(pair.domain for pair in observation.raw_pairs) == tuple(
        reversed(CANONICAL_DOMAINS)
    )
    assert _render(observation.raw_pairs) == "()[]{}"
    assert tuple(pair.domain for pair in observation.normalized_pairs) == (
        CANONICAL_DOMAINS
    )
    assert observation.normalization_permutation == (2, 1, 0)
    assert observation.surface == "{}[]()"
    assert all(pair.opening.cut_role == "upper" for pair in observation.raw_pairs)
    assert all(pair.closing.cut_role == "lower" for pair in observation.raw_pairs)
    assert all(pair.orientation == -1 for pair in observation.raw_pairs)


def test_normalized_surface_star_is_an_involution(workspace) -> None:
    for name in ("identity-triad", "cycle-triad", "spatial-mul", "spatial-add"):
        function = workspace.function("bracket-reversal", name)
        observation = _full_observation(function)
        _, restored, permutation = _surface_star(observation.normalized_pairs)

        assert tuple(pair.domain for pair in restored) == CANONICAL_DOMAINS
        assert all(pair.orientation == 1 for pair in restored)
        assert all(pair.opening.cut_role == "lower" for pair in restored)
        assert all(pair.closing.cut_role == "upper" for pair in restored)
        assert permutation == (2, 1, 0)


def test_pair_movement_preserves_complete_crossing_records(workspace) -> None:
    function = workspace.function("bracket-reversal", "spatial-mul")
    direct = function.program_slice([], _node_ids(function))
    lower = _lower_crossings(direct)
    upper = _upper_crossings(direct)
    observation = _observe(function, direct)

    for pair in observation.normalized_pairs:
        assert pair.opening.crossing_json == _canonical_json(upper[pair.domain])
        assert pair.closing.crossing_json == _canonical_json(lower[pair.domain])


def test_one_surface_retains_distinct_boundary_and_event_residuals(workspace) -> None:
    names = ("identity-triad", "cycle-triad", "spatial-mul")
    observations = {
        name: _full_observation(workspace.function("bracket-reversal", name))
        for name in names
    }
    assert {observation.surface for observation in observations.values()} == {"{}[]()"}
    assert (
        len({observation.checked_slice_json for observation in observations.values()})
        == 3
    )

    identity = json.loads(observations["identity-triad"].checked_slice_json)["slice"]
    cycle = json.loads(observations["cycle-triad"].checked_slice_json)["slice"]
    spatial = json.loads(observations["spatial-mul"].checked_slice_json)["slice"]

    assert (len(identity["events"]), len(identity["through_wires"])) == (0, 3)
    assert (len(cycle["events"]), len(cycle["through_wires"])) == (1, 1)
    assert Counter(
        event["operation"]["name"] for event in spatial["events"]
    ) == Counter({"copy": 2, "discard": 1, "mul": 1})
    assert len(spatial["lower_boundary"]) == 3
    assert len(spatial["upper_boundary"]) == 3
    assert spatial["through_wires"] == []


def test_mul_and_add_collide_only_at_the_surface(workspace) -> None:
    multiply = workspace.function("bracket-reversal", "spatial-mul")
    addition = workspace.function("bracket-reversal", "spatial-add")
    multiply_view = _full_observation(multiply)
    addition_view = _full_observation(addition)
    inputs = {"temporal": 2.0, "spatial": 7.0, "construction": 3.0}

    assert multiply_view.surface == addition_view.surface == "{}[]()"
    assert multiply_view.checked_slice_json != addition_view.checked_slice_json
    assert tuple(multiply.evaluate(inputs)) == (2.0, 6.0, 3.0)
    assert tuple(addition.evaluate(inputs)) == (2.0, 5.0, 3.0)


def test_incomplete_cut_is_not_given_forged_domain_roles(workspace) -> None:
    function = workspace.function("bracket-reversal", "spatial-mul")
    copy_id = next(
        node["id"]
        for node in function.ir["nodes"]
        if node["operation"]["name"] == "copy"
    )
    partial = function.program_slice([], [copy_id])

    with pytest.raises(NotRepresentable, match="complete upper causal past"):
        _observe(function, partial)


def test_reversing_nonempty_cuts_is_not_a_program_slice(workspace) -> None:
    function = workspace.function("bracket-reversal", "spatial-mul")
    node_ids = _node_ids(function)

    with pytest.raises(ValueError):
        function.program_slice(node_ids, [])


def test_observation_commutes_with_certified_outer_slice_composition(workspace) -> None:
    function = workspace.function("bracket-reversal", "spatial-mul")
    node_ids = _node_ids(function)
    middle = (
        next(
            node["id"]
            for node in function.ir["nodes"]
            if node["operation"]["name"] == "copy"
        ),
    )
    direct = function.program_slice([], node_ids)
    composed = function.compose_program_slices([], middle, node_ids)
    direct_view = _observe(function, direct)
    composed_view = _observe(function, composed)

    assert composed.result == direct.result
    assert composed.certificate["exact_composition"] == "checked"
    assert composed_view.raw_pairs == direct_view.raw_pairs
    assert composed_view.normalized_pairs == direct_view.normalized_pairs
    assert composed_view.checked_slice_json == direct_view.checked_slice_json
    assert composed_view.surface == direct_view.surface
    assert composed_view.derivation_certificate_json != (
        direct_view.derivation_certificate_json
    )
