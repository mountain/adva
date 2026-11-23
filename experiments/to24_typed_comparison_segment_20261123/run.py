#!/usr/bin/env python3
import copy
import hashlib
import importlib.util
import json
import resource
import time
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return digest_bytes(canonical_bytes(value))


def load_predecessor(expected_sha256):
    candidates = [
        ROOT.parent / "typed-face-anchor-20261122" / "run.py",
        ROOT.parent / "to24_typed_face_anchor_20261122" / "run.py",
    ]
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    if path is None:
        raise FileNotFoundError("PinnedPredecessorRunMissing")
    actual = digest_bytes(path.read_bytes())
    if actual != expected_sha256:
        raise ValueError("PinnedPredecessorRunMismatch")
    spec = importlib.util.spec_from_file_location("typed_face_anchor_predecessor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path, actual


def endpoint_projection(segment):
    return {
        "target_digest": segment["target_digest"],
        "global_source_object": segment["global_source_object"],
        "global_target_object": segment["global_target_object"],
        "source_path": segment["source_path"],
        "target_path": segment["target_path"],
    }


def form_segment(route, predecessor, target, target_digest):
    anchors = [
        predecessor.form_anchor(instance, target, target_digest)
        for instance in route["occurrences"]
    ]
    return {
        "schema": "adva.research.typed-comparison-segment.v0",
        "segment_id": route["id"],
        "target_digest": target_digest,
        "global_source_object": anchors[0]["global_source_object"],
        "global_target_object": anchors[-1]["global_target_object"],
        "source_path": anchors[0]["source_path"],
        "intermediate_paths": [anchors[0]["target_path"]],
        "target_path": anchors[-1]["target_path"],
        "factors": anchors,
        "factor_occurrence_ids": [
            anchor["occurrence"]["occurrence_id"] for anchor in anchors
        ],
        "factor_two_cells": [
            anchor["generating_two_cell"] for anchor in anchors
        ],
        "rewrite_intervals": [
            [
                anchor["occurrence"]["offset"],
                anchor["occurrence"]["offset"]
                + len(anchor["occurrence"]["relation"].split("->")[0]),
            ]
            for anchor in anchors
        ],
        "higher_cell": "NotConstructed",
        "interchange_identification": "NotClaimed",
    }


def refusal(reason):
    return f"Refused/{reason}"


def validate_segment(segment, route, predecessor, target, target_digest):
    if segment.get("higher_cell") != "NotConstructed":
        return refusal("PrematureHigherCell")
    if segment.get("interchange_identification") != "NotClaimed":
        return refusal("PrematureInterchangeIdentification")
    if segment.get("target_digest") != target_digest:
        return refusal("TargetComputadMismatch")
    factors = segment.get("factors", [])
    if len(factors) != 2:
        return refusal("FactorCountMismatch")
    occurrence_ids = [
        factor.get("occurrence", {}).get("occurrence_id") for factor in factors
    ]
    if len(set(occurrence_ids)) != len(occurrence_ids):
        return refusal("DuplicateOccurrenceHistory")
    expected = form_segment(route, predecessor, target, target_digest)
    if segment.get("factor_occurrence_ids") != expected["factor_occurrence_ids"]:
        return refusal("FactorOrderMismatch")
    for factor, instance in zip(factors, route["occurrences"]):
        result = predecessor.validate_anchor(
            factor, instance, target, target_digest)
        if result != "TypedLocalComparisonAnchored":
            return refusal("InvalidFactorAnchor")
    if factors[0]["target_path"] != factors[1]["source_path"]:
        return refusal("IntermediateBoundaryMismatch")
    if segment.get("intermediate_paths") != expected["intermediate_paths"]:
        return refusal("IntermediateHistoryMismatch")
    for field in (
        "global_source_object",
        "global_target_object",
        "source_path",
        "target_path",
        "factor_two_cells",
        "rewrite_intervals",
    ):
        if segment.get(field) != expected[field]:
            return refusal(f"{field}Mismatch")
    if factors != expected["factors"]:
        return refusal("FactorAnchorMismatch")
    return "TypedComparisonSegmentComposed"


def intervals_disjoint(intervals):
    if len(intervals) != 2:
        return False
    first, second = sorted(intervals)
    return first[1] <= second[0]


def interchange_eligibility(left, right):
    if endpoint_projection(left) != endpoint_projection(right):
        return refusal("EndpointProjectionMismatch")
    if not intervals_disjoint(left["rewrite_intervals"]):
        return refusal("LeftIntervalsOverlap")
    if not intervals_disjoint(right["rewrite_intervals"]):
        return refusal("RightIntervalsOverlap")
    if Counter(left["factor_two_cells"]) != Counter(right["factor_two_cells"]):
        return refusal("FactorCellMultisetMismatch")
    if left["factor_two_cells"] != list(reversed(right["factor_two_cells"])):
        return refusal("FactorOrderNotReversed")
    if left["intermediate_paths"] == right["intermediate_paths"]:
        return refusal("HistoriesNotDistinct")
    return "EligibleDisjointInterchangeBoundary/HistoriesRetained"


def main():
    started = time.perf_counter_ns()
    input_data = json.loads((ROOT / "input.json").read_text())
    predecessor_started = time.perf_counter_ns()
    predecessor, predecessor_path, predecessor_sha = load_predecessor(
        input_data["predecessor"]["run_sha256"])
    predecessor_verification_ns = time.perf_counter_ns() - predecessor_started

    target_started = time.perf_counter_ns()
    target = predecessor.build_target(input_data["target_descriptor"])
    target_digest = predecessor.digest(target)
    target_formation_ns = time.perf_counter_ns() - target_started
    if target_digest != input_data["predecessor"]["target_digest"]:
        raise ValueError("PinnedTargetDigestMismatch")
    target_nodes = (
        len(target["objects"])
        + len(target["one_cells"])
        + len(target["two_cells"])
    )

    route_a, route_b = input_data["routes"]
    segment_a_started = time.perf_counter_ns()
    segment_a = form_segment(route_a, predecessor, target, target_digest)
    segment_a_formation_ns = time.perf_counter_ns() - segment_a_started
    segment_b_started = time.perf_counter_ns()
    segment_b = form_segment(route_b, predecessor, target, target_digest)
    segment_b_formation_ns = time.perf_counter_ns() - segment_b_started

    validation_started = time.perf_counter_ns()
    cases = []

    def record(name, candidate, route, expected, endpoint_equal):
        result = validate_segment(
            candidate, route, predecessor, target, target_digest)
        cases.append({
            "name": name,
            "endpoint_projection_equal_to_route_a": endpoint_equal,
            "result": result,
            "expected": expected,
            "matched": result == expected,
        })

    record("route-a", segment_a, route_a,
           "TypedComparisonSegmentComposed", True)
    record("route-b-reuse", segment_b, route_b,
           "TypedComparisonSegmentComposed", True)
    reordered = copy.deepcopy(segment_a)
    reordered["factors"] = list(reversed(reordered["factors"]))
    reordered["factor_occurrence_ids"] = list(
        reversed(reordered["factor_occurrence_ids"])
    )
    reordered["factor_two_cells"] = list(reversed(reordered["factor_two_cells"]))
    record("reordered-factors-without-retyping", reordered, route_a,
           refusal("FactorOrderMismatch"), True)
    missing_factor = copy.deepcopy(segment_a)
    missing_factor["factors"] = missing_factor["factors"][:1]
    record("missing-factor", missing_factor, route_a,
           refusal("FactorCountMismatch"), True)
    duplicate = copy.deepcopy(segment_a)
    duplicate["factors"][1]["occurrence"]["occurrence_id"] = (
        duplicate["factors"][0]["occurrence"]["occurrence_id"]
    )
    record("duplicate-occurrence-history", duplicate, route_a,
           refusal("DuplicateOccurrenceHistory"), True)
    changed_target = copy.deepcopy(segment_a)
    changed_target["target_digest"] = "0" * 64
    record("changed-target", changed_target, route_a,
           refusal("TargetComputadMismatch"), True)
    premature_equality = copy.deepcopy(segment_a)
    premature_equality["interchange_identification"] = "EqualCompositeClaimed"
    record("premature-interchange-identification", premature_equality, route_a,
           refusal("PrematureInterchangeIdentification"), True)
    premature_higher = copy.deepcopy(segment_a)
    premature_higher["higher_cell"] = "ThreeCellClaimed"
    record("premature-higher-cell", premature_higher, route_a,
           refusal("PrematureHigherCell"), True)
    validation_ns = time.perf_counter_ns() - validation_started

    interchange_started = time.perf_counter_ns()
    interchange_result = interchange_eligibility(segment_a, segment_b)
    interchange_ns = time.perf_counter_ns() - interchange_started
    expected_interchange = "EligibleDisjointInterchangeBoundary/HistoriesRetained"

    baseline_started = time.perf_counter_ns()
    baseline_a = endpoint_projection(segment_a)
    baseline_b = endpoint_projection(segment_b)
    baseline_formation_ns = time.perf_counter_ns() - baseline_started
    all_expected = (
        all(case["matched"] for case in cases)
        and interchange_result == expected_interchange
        and baseline_a == baseline_b
        and segment_a != segment_b
    )

    before_serialization_ns = time.perf_counter_ns() - started
    outcome = {
        "schema": "adva.research.typed-comparison-segment.outcome.v0",
        "status": "PassedBoundedTypedComparisonSegment" if all_expected else "Failed",
        "claim": "Each two-anchor route has a well-typed intermediate boundary; the two routes share endpoint projection and reversed disjoint factor cells while retaining distinct histories.",
        "claim_boundary": "Finite external syntax result only. Eligibility for a disjoint interchange boundary is not an equality proof, common 3-cell, filler, or native Adva semantic judgment.",
        "predecessor": {
            "path_used": predecessor_path.name,
            "run_sha256": predecessor_sha,
            "target_digest": target_digest,
        },
        "target_nodes": target_nodes,
        "route_a_segment": segment_a,
        "route_b_segment": segment_b,
        "cases": cases,
        "interchange_result": interchange_result,
        "comparison": {
            "endpoint_projection_equal": baseline_a == baseline_b,
            "endpoint_projection_sha256": digest(baseline_a),
            "route_a_segment_sha256": digest(segment_a),
            "route_b_segment_sha256": digest(segment_b),
            "histories_distinct": segment_a["intermediate_paths"] != segment_b["intermediate_paths"],
            "factor_cell_multisets_equal": Counter(segment_a["factor_two_cells"]) == Counter(segment_b["factor_two_cells"]),
            "factor_orders_reversed": segment_a["factor_two_cells"] == list(reversed(segment_b["factor_two_cells"])),
            "endpoint_projection_bytes": len(canonical_bytes(baseline_a)),
            "segment_bytes": len(canonical_bytes(segment_a)),
            "formation_byte_delta": len(canonical_bytes(segment_a)) - len(canonical_bytes(baseline_a)),
            "finite_distinction": "the two valid routes have the same endpoint-only projection but distinct intermediate galleries and reversed ordered factors",
            "claim_boundary": "No general expressivity, equality, confluence, or asymptotic efficiency theorem is claimed."
        },
        "proposed_word": {
            "word": "typed comparison segment",
            "state": "Proposed",
            "role": "compose a short ordered sequence of typed face anchors while retaining the exact intermediate gallery and factor history",
            "input": "a versioned target, exactly two adjacent typed face anchors, their ordered occurrence identities, and a declared source/intermediate/target gallery chain",
            "output_relation": "TypedComparisonSegmentComposed or a target-, factor-, history-, intermediate-boundary-, or promotion-specific refusal",
            "applicability": "both anchors validate against one target digest and the first target path equals the second source path exactly",
            "witness": "the two complete anchors, ordered occurrence ids and 2-cell ids, rewrite intervals, and source/intermediate/target paths",
            "counterexample": "the two commuting-square routes have identical endpoint projection but distinct intermediate paths and reverse factor order; endpoint-only data cannot retain which route was used",
            "expansion": "validate each anchor, compare the shared intermediate path, replay the ordered factors, and retain the endpoint projection without erasing the intermediate history",
            "refusal_conditions": [
                "target digest mismatch",
                "missing, reordered, invalid, or duplicate factor",
                "intermediate target/source path mismatch",
                "altered occurrence or factor history",
                "premature composite equality, interchange identification, higher cell, or filler"
            ],
            "replay": "timeout 30s python3 run.py",
            "residual": "no semantic equality of the two routes, no native vertical/horizontal composition, no 3-cell or Q4/M6 filler, no fourteen-face pasting comparison, and no arithmetic-universality result"
        },
        "cost": {
            "routes": 1,
            "constructed_nodes": target_nodes + 4 + 2,
            "segment_cases": len(cases),
            "predecessor_verification_ns": predecessor_verification_ns,
            "target_formation_ns": target_formation_ns,
            "route_a_segment_formation_ns": segment_a_formation_ns,
            "route_b_reuse_formation_ns": segment_b_formation_ns,
            "case_validation_ns": validation_ns,
            "interchange_eligibility_ns": interchange_ns,
            "endpoint_projection_formation_ns": baseline_formation_ns,
            "whole_run_before_serialization_ns": before_serialization_ns,
            "serialization_ns": 0,
            "serialized_bytes": 0,
            "ru_maxrss_kib_before_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "implementation_correction_replays": 0
        }
    }
    serialization_started = time.perf_counter_ns()
    canonical_bytes(outcome)
    outcome["cost"]["serialization_ns"] = time.perf_counter_ns() - serialization_started
    previous = -1
    while previous != outcome["cost"]["serialized_bytes"]:
        previous = outcome["cost"]["serialized_bytes"]
        outcome["cost"]["serialized_bytes"] = len(canonical_bytes(outcome))
    data = canonical_bytes(outcome)
    (ROOT / "outcome.json").write_bytes(data)
    print(json.dumps({
        "status": outcome["status"],
        "all_expected": all_expected,
        "target_nodes": target_nodes,
        "constructed_nodes": outcome["cost"]["constructed_nodes"],
        "endpoint_projection_equal": baseline_a == baseline_b,
        "histories_distinct": outcome["comparison"]["histories_distinct"],
        "interchange_result": interchange_result,
        "serialized_bytes": len(data),
        "sha256": digest_bytes(data),
        "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
