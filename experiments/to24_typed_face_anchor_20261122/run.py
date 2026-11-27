#!/usr/bin/env python3
import copy
import hashlib
import itertools
import json
import resource
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
IDENTITY = (1, 2, 3, 4)
W0 = (4, 3, 2, 1)
RELATIONS = (
    ("13", "31"),
    ("31", "13"),
    ("121", "212"),
    ("212", "121"),
    ("232", "323"),
    ("323", "232"),
)


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def name(permutation):
    return "".join(map(str, permutation))


def step(permutation, generator):
    result = list(permutation)
    index = int(generator) - 1
    result[index], result[index + 1] = result[index + 1], result[index]
    return tuple(result)


def act(start, word):
    current = start
    vertices = [current]
    for generator in word:
        current = step(current, generator)
        vertices.append(current)
    return current, vertices


def one_cell_id(source, generator):
    return f"e:{name(source)}:s{generator}"


def path_ids(source, word):
    current = source
    result = []
    for generator in word:
        result.append(one_cell_id(current, generator))
        current = step(current, generator)
    return result, current


def two_cell_id(source, old, new):
    return f"f:{name(source)}:{old}>{new}"


def build_target(descriptor):
    objects = sorted(itertools.permutations((1, 2, 3, 4)))
    one_cells = []
    for source in objects:
        for generator in "123":
            one_cells.append({
                "id": one_cell_id(source, generator),
                "source": name(source),
                "target": name(step(source, generator)),
                "generator": generator,
            })
    two_cells = []
    for source in objects:
        for old, new in RELATIONS:
            source_path, source_end = path_ids(source, old)
            target_path, target_end = path_ids(source, new)
            assert source_end == target_end
            two_cells.append({
                "id": two_cell_id(source, old, new),
                "source_object": name(source),
                "target_object": name(source_end),
                "source_path": source_path,
                "target_path": target_path,
                "relation": f"{old}->{new}",
                "face_type": "Q4" if len(old) == 2 else "M6",
            })
    return {
        "descriptor": descriptor,
        "objects": [name(value) for value in objects],
        "one_cells": one_cells,
        "two_cells": two_cells,
    }


def relation_at(instance):
    before = instance["before"]
    after = instance["after"]
    offset = instance["offset"]
    for old, new in RELATIONS:
        if before[offset:offset + len(old)] != old:
            continue
        candidate = before[:offset] + new + before[offset + len(old):]
        if candidate == after:
            return old, new
    raise ValueError("NonLocalRewrite")


def occurrence_projection(instance):
    old, new = relation_at(instance)
    before_end, _ = act(IDENTITY, instance["before"])
    after_end, _ = act(IDENTITY, instance["after"])
    if before_end != W0 or after_end != W0:
        raise ValueError("GlobalEndpointMismatch")
    prefix = instance["before"][:instance["offset"]]
    suffix = instance["before"][instance["offset"] + len(old):]
    if instance["after"][:instance["offset"]] != prefix:
        raise ValueError("PrefixHistoryMismatch")
    if instance["after"][instance["offset"] + len(new):] != suffix:
        raise ValueError("SuffixHistoryMismatch")
    local_start, _ = act(IDENTITY, prefix)
    old_end, _ = act(local_start, old)
    new_end, _ = act(local_start, new)
    if old_end != new_end:
        raise ValueError("LocalEndpointMismatch")
    return {
        "occurrence_id": instance["id"],
        "before": instance["before"],
        "after": instance["after"],
        "offset": instance["offset"],
        "relation": f"{old}->{new}",
        "face_id": instance["face_id"],
        "face_type": "Q4" if len(old) == 2 else "M6",
        "prefix": prefix,
        "suffix": suffix,
        "local_source_object": name(local_start),
        "local_target_object": name(old_end),
    }


def form_anchor(instance, target, target_digest):
    projection = occurrence_projection(instance)
    old, new = projection["relation"].split("->")
    local_start = tuple(map(int, projection["local_source_object"]))
    local_end = tuple(map(int, projection["local_target_object"]))
    prefix_path, prefix_end = path_ids(IDENTITY, projection["prefix"])
    suffix_path, suffix_end = path_ids(local_end, projection["suffix"])
    source_path, source_end = path_ids(IDENTITY, projection["before"])
    target_path, target_end = path_ids(IDENTITY, projection["after"])
    assert prefix_end == local_start
    assert suffix_end == source_end == target_end == W0
    cell_id = two_cell_id(local_start, old, new)
    if not any(cell["id"] == cell_id for cell in target["two_cells"]):
        raise ValueError("TwoCellAbsent")
    return {
        "schema": "adva.research.typed-face-anchor.v0",
        "target_digest": target_digest,
        "occurrence": projection,
        "global_source_object": name(IDENTITY),
        "global_target_object": name(W0),
        "prefix_whisker": prefix_path,
        "generating_two_cell": cell_id,
        "suffix_whisker": suffix_path,
        "source_path": source_path,
        "target_path": target_path,
        "higher_cell": "NotConstructed",
    }


def refusal(reason):
    return f"Refused/{reason}"


def validate_anchor(anchor, instance, target, target_digest):
    if not anchor.get("occurrence"):
        return refusal("OccurrenceHistoryMissing")
    if anchor.get("higher_cell") != "NotConstructed":
        return refusal("PrematureHigherCell")
    if anchor.get("target_digest") != target_digest:
        return refusal("TargetComputadMismatch")
    try:
        expected = form_anchor(instance, target, target_digest)
    except ValueError as error:
        return refusal(str(error))
    if anchor.get("global_source_object") != expected["global_source_object"]:
        return refusal("ObjectAnchorMismatch")
    if anchor.get("global_target_object") != expected["global_target_object"]:
        return refusal("ObjectAnchorMismatch")
    if anchor.get("generating_two_cell") != expected["generating_two_cell"]:
        return refusal("TwoCellMismatch")
    if anchor.get("prefix_whisker") != expected["prefix_whisker"]:
        return refusal("WhiskerTypeMismatch")
    if anchor.get("suffix_whisker") != expected["suffix_whisker"]:
        return refusal("WhiskerTypeMismatch")
    if anchor.get("source_path") != expected["source_path"]:
        return refusal("SourcePathMismatch")
    if anchor.get("target_path") != expected["target_path"]:
        return refusal("TargetPathMismatch")
    if anchor.get("occurrence") != expected["occurrence"]:
        return refusal("OccurrenceHistoryMismatch")
    return "TypedLocalComparisonAnchored"


def main():
    input_data = json.loads((ROOT / "input.json").read_text())
    started = time.perf_counter_ns()
    target_started = time.perf_counter_ns()
    target = build_target(input_data["target_descriptor"])
    target_formation_ns = time.perf_counter_ns() - target_started
    target_digest = digest(target)
    node_count = len(target["objects"]) + len(target["one_cells"]) + len(target["two_cells"])
    if node_count != 240:
        raise AssertionError(node_count)

    canonical_instance, reuse_instance = input_data["instances"]
    baseline_started = time.perf_counter_ns()
    baseline = occurrence_projection(canonical_instance)
    baseline_formation_ns = time.perf_counter_ns() - baseline_started
    anchor_started = time.perf_counter_ns()
    canonical = form_anchor(canonical_instance, target, target_digest)
    anchor_formation_ns = time.perf_counter_ns() - anchor_started

    reuse_started = time.perf_counter_ns()
    reuse_anchor = form_anchor(reuse_instance, target, target_digest)
    reuse_result = validate_anchor(reuse_anchor, reuse_instance, target, target_digest)
    reuse_ns = time.perf_counter_ns() - reuse_started

    cases = []
    validation_started = time.perf_counter_ns()

    def record(case_name, candidate, instance, expected, baseline_equal):
        result = validate_anchor(candidate, instance, target, target_digest)
        cases.append({
            "name": case_name,
            "baseline_equal_to_canonical": baseline_equal,
            "result": result,
            "expected": expected,
            "matched": result == expected,
        })

    record("canonical-m6", canonical, canonical_instance,
           "TypedLocalComparisonAnchored", True)
    record("fresh-q4-reuse", reuse_anchor, reuse_instance,
           "TypedLocalComparisonAnchored", False)
    changed_target = copy.deepcopy(canonical)
    changed_target["target_digest"] = "0" * 64
    record("changed-target", changed_target, canonical_instance,
           refusal("TargetComputadMismatch"), True)
    wrong_cell = copy.deepcopy(canonical)
    wrong_cell["generating_two_cell"] = reuse_anchor["generating_two_cell"]
    record("wrong-two-cell", wrong_cell, canonical_instance,
           refusal("TwoCellMismatch"), True)
    wrong_object = copy.deepcopy(canonical)
    wrong_object["global_target_object"] = "3412"
    record("wrong-object-anchor", wrong_object, canonical_instance,
           refusal("ObjectAnchorMismatch"), True)
    broken_whisker = copy.deepcopy(canonical)
    broken_whisker["suffix_whisker"] = list(reversed(broken_whisker["suffix_whisker"]))
    record("broken-suffix-whisker", broken_whisker, canonical_instance,
           refusal("WhiskerTypeMismatch"), True)
    premature = copy.deepcopy(canonical)
    premature["higher_cell"] = "M6FillerClaimed"
    record("premature-higher-cell", premature, canonical_instance,
           refusal("PrematureHigherCell"), True)

    missing_history = copy.deepcopy(canonical)
    del missing_history["occurrence"]
    missing_history_result = validate_anchor(
        missing_history, canonical_instance, target, target_digest)
    validation_ns = time.perf_counter_ns() - validation_started

    all_expected = all(case["matched"] for case in cases)
    if missing_history_result != refusal("OccurrenceHistoryMissing"):
        all_expected = False
    if reuse_result != "TypedLocalComparisonAnchored":
        all_expected = False

    before_serialization_ns = time.perf_counter_ns() - started
    outcome = {
        "schema": "adva.research.typed-face-anchor.outcome.v0",
        "status": "PassedBoundedTypedFaceAnchor" if all_expected else "Failed",
        "claim": "One M6 and one Q4 occurrence are well-typed generating 2-cell comparisons in the declared finite A3 computad syntax, with exact prefix and suffix whiskers.",
        "claim_boundary": "External finite syntax result only. It creates no native Adva semantic identity, composes no fourteen-face pasting, and supplies no 3-cell or Q4/M6 filler.",
        "target": {
            "digest": target_digest,
            "objects": len(target["objects"]),
            "one_cells": len(target["one_cells"]),
            "two_cells": len(target["two_cells"]),
            "nodes": node_count,
        },
        "canonical_anchor": canonical,
        "reuse_anchor": reuse_anchor,
        "cases": cases,
        "extra_missing_history_control": missing_history_result,
        "comparison": {
            "baseline_projection_sha256": digest(baseline),
            "changed_target_baseline_sha256": digest(occurrence_projection(canonical_instance)),
            "finite_distinction": "the occurrence-only projection is identical after changing the target digest, but the typed anchor refuses the changed target",
            "baseline_bytes": len(canonical_bytes(baseline)),
            "anchor_bytes": len(canonical_bytes(canonical)),
            "formation_byte_delta": len(canonical_bytes(canonical)) - len(canonical_bytes(baseline)),
            "claim_boundary": "No general expressivity or asymptotic efficiency theorem is claimed."
        },
        "proposed_word": {
            "word": "typed face anchor",
            "state": "Proposed",
            "role": "bind one retained rewrite occurrence to a versioned target computad and an explicit whiskered generating 2-cell",
            "input": "one signed-face occurrence, a finite target computad descriptor, exact before/after words, and the retained prefix/suffix history",
            "output_relation": "TypedLocalComparisonAnchored or a target-, object-, 2-cell-, whisker-, history-, path-, or promotion-specific refusal",
            "applicability": "the occurrence is one declared Q4/M6 rank-two rewrite and the target presentation contains its parallel local paths with exact global whiskers",
            "witness": "the target digest, global endpoints, ordered prefix and suffix one-cell paths, the generating two-cell id, and both full boundary paths",
            "counterexample": "changing only the target digest leaves the untyped occurrence projection identical but is refused by the anchor",
            "expansion": "rebuild the target presentation, replay the prefix to the local source, verify the two-cell boundary, replay the common suffix from the local target, and compare all stored ids and paths",
            "refusal_conditions": [
                "target computad digest mismatch",
                "wrong object or generating two-cell",
                "noncomposable prefix or suffix whisker",
                "missing or altered occurrence history or full path",
                "claim of a higher cell or filler"
            ],
            "replay": "timeout 30s python3 run.py",
            "residual": "no comparison between the two seven-step pastings, no native relation-witness composition, no 3-cell, no Q4/M6 filler, no arbitrary A_n coherence, and no arithmetic-universality result"
        },
        "cost": {
            "routes": 1,
            "target_nodes": node_count,
            "anchor_cases": len(cases),
            "target_formation_ns": target_formation_ns,
            "baseline_formation_ns": baseline_formation_ns,
            "anchor_formation_ns": anchor_formation_ns,
            "reuse_formation_and_validation_ns": reuse_ns,
            "case_validation_ns": validation_ns,
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
        "target": outcome["target"],
        "all_expected": all_expected,
        "reuse_result": reuse_result,
        "missing_history_result": missing_history_result,
        "baseline_bytes": outcome["comparison"]["baseline_bytes"],
        "anchor_bytes": outcome["comparison"]["anchor_bytes"],
        "serialized_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
