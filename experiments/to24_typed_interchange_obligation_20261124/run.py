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
RULE_ID = "disjoint-equal-length-local-rewrite-swap.v0"
PASS = "TypedInterchangeObligationChecked/NoHigherCellConstructed"


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return digest_bytes(canonical_bytes(value))


def refusal(reason):
    return f"Refused/{reason}"


def load_predecessor(expected_sha256):
    candidates = [
        ROOT.parent / "typed-comparison-segment-20261123" / "run.py",
        ROOT.parent / "to24_typed_comparison_segment_20261123" / "run.py",
    ]
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    if path is None:
        raise FileNotFoundError("PinnedPredecessorRunMissing")
    actual = digest_bytes(path.read_bytes())
    if actual != expected_sha256:
        raise ValueError("PinnedPredecessorRunMismatch")
    spec = importlib.util.spec_from_file_location(
        "typed_comparison_segment_predecessor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path, actual


def relation_parts(factor):
    old, new = factor["occurrence"]["relation"].split("->")
    return old, new


def apply_factor(word, factor):
    old, new = relation_parts(factor)
    offset = factor["occurrence"]["offset"]
    if word[offset:offset + len(old)] != old:
        raise ValueError("RedexUnavailable")
    return word[:offset] + new + word[offset + len(old):]


def intervals_disjoint(intervals):
    if len(intervals) != 2:
        return False
    first, second = sorted(intervals)
    return first[1] <= second[0]


def canonical_correspondence(left, right):
    result = []
    for left_index, left_factor in enumerate(left["factors"]):
        matches = []
        for right_index, right_factor in enumerate(right["factors"]):
            if (
                left_factor["generating_two_cell"]
                == right_factor["generating_two_cell"]
                and left_factor["occurrence"]["offset"]
                == right_factor["occurrence"]["offset"]
                and left_factor["occurrence"]["relation"]
                == right_factor["occurrence"]["relation"]
            ):
                matches.append(right_index)
        if len(matches) != 1:
            raise ValueError("NonUniqueFactorCorrespondence")
        right_index = matches[0]
        result.append({
            "left_index": left_index,
            "right_index": right_index,
            "offset": left_factor["occurrence"]["offset"],
            "relation": left_factor["occurrence"]["relation"],
            "generating_two_cell": left_factor["generating_two_cell"],
        })
    return result


def replay_witness(square):
    return {
        "source_word": square["left"]["words"][0],
        "left_intermediate_word": square["left"]["words"][1],
        "right_intermediate_word": square["right"]["words"][1],
        "target_word": square["left"]["words"][2],
    }


def form_obligation(square, predecessor, anchor_predecessor, target,
                    target_digest, rule):
    left = predecessor.form_segment(
        square["left"], anchor_predecessor, target, target_digest)
    right = predecessor.form_segment(
        square["right"], anchor_predecessor, target, target_digest)
    return {
        "schema": "adva.research.typed-interchange-obligation.v0",
        "obligation_id": square["id"],
        "target_digest": target_digest,
        "rule": copy.deepcopy(rule),
        "left_segment": left,
        "right_segment": right,
        "factor_correspondence": canonical_correspondence(left, right),
        "replay_witness": replay_witness(square),
        "semantic_equality": "NotClaimed",
        "higher_cell": "NotConstructed",
        "filler": "NotConstructed",
    }


def bare_eligibility_projection(obligation):
    return {
        "target_digest": obligation.get("target_digest"),
        "left_segment_sha256": digest(obligation.get("left_segment")),
        "right_segment_sha256": digest(obligation.get("right_segment")),
        "eligibility": "EligibleDisjointInterchangeBoundary/HistoriesRetained",
    }


def validate_obligation(obligation, square, predecessor, anchor_predecessor,
                        target, target_digest):
    if obligation.get("semantic_equality") != "NotClaimed":
        return refusal("PrematureSemanticEquality")
    if obligation.get("higher_cell") != "NotConstructed":
        return refusal("PrematureHigherCell")
    if obligation.get("filler") != "NotConstructed":
        return refusal("PrematureFiller")
    if obligation.get("target_digest") != target_digest:
        return refusal("TargetComputadMismatch")
    rule = obligation.get("rule", {})
    if rule.get("id") != RULE_ID:
        return refusal("RuleIdentifierMismatch")
    left = obligation.get("left_segment", {})
    right = obligation.get("right_segment", {})
    if left == right:
        return refusal("DistinctSegmentsRequired")
    left_result = predecessor.validate_segment(
        left, square["left"], anchor_predecessor, target, target_digest)
    if left_result != "TypedComparisonSegmentComposed":
        return refusal(f"LeftSegmentInvalid/{left_result}")
    right_result = predecessor.validate_segment(
        right, square["right"], anchor_predecessor, target, target_digest)
    if right_result != "TypedComparisonSegmentComposed":
        return refusal(f"RightSegmentInvalid/{right_result}")
    if predecessor.endpoint_projection(left) != predecessor.endpoint_projection(right):
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
        return refusal("DistinctHistoriesRequired")
    try:
        expected_correspondence = canonical_correspondence(left, right)
    except ValueError as error:
        return refusal(str(error))
    if obligation.get("factor_correspondence") != expected_correspondence:
        return refusal("FactorCorrespondenceMismatch")
    if obligation.get("replay_witness") != replay_witness(square):
        return refusal("ReplayWitnessMismatch")

    witness = obligation["replay_witness"]
    source = witness["source_word"]
    target_word = witness["target_word"]
    try:
        left_first = apply_factor(source, left["factors"][0])
        left_final = apply_factor(left_first, left["factors"][1])
        right_first = apply_factor(source, right["factors"][0])
        right_final = apply_factor(right_first, right["factors"][1])
    except ValueError as error:
        return refusal(str(error))
    if (
        left_first != witness["left_intermediate_word"]
        or right_first != witness["right_intermediate_word"]
        or left_final != target_word
        or right_final != target_word
    ):
        return refusal("TwoOrderReplayMismatch")

    # The correspondence must be the adjacent transposition [1, 0].  Checking
    # availability during both replays above establishes that each first
    # rewrite leaves the matched other redex available at its declared site.
    if [entry["right_index"] for entry in expected_correspondence] != [1, 0]:
        return refusal("CorrespondenceIsNotAdjacentSwap")
    return PASS


def main():
    input_data = json.loads((ROOT / "input.json").read_text())
    started = time.perf_counter_ns()

    predecessor_started = time.perf_counter_ns()
    predecessor, predecessor_path, predecessor_sha = load_predecessor(
        input_data["predecessor"]["run_sha256"])
    anchor_predecessor, anchor_path, anchor_sha = predecessor.load_predecessor(
        input_data["predecessor"]["anchor_run_sha256"])
    predecessor_ns = time.perf_counter_ns() - predecessor_started

    target_started = time.perf_counter_ns()
    target = anchor_predecessor.build_target(input_data["target_descriptor"])
    target_digest = anchor_predecessor.digest(target)
    target_ns = time.perf_counter_ns() - target_started
    if target_digest != input_data["predecessor"]["target_digest"]:
        raise ValueError("PinnedTargetDigestMismatch")
    target_nodes = sum(len(target[key]) for key in ("objects", "one_cells", "two_cells"))

    primary, fresh = input_data["squares"]
    formation_started = time.perf_counter_ns()
    primary_obligation = form_obligation(
        primary, predecessor, anchor_predecessor, target, target_digest,
        input_data["rule"])
    primary_formation_ns = time.perf_counter_ns() - formation_started
    reuse_started = time.perf_counter_ns()
    fresh_obligation = form_obligation(
        fresh, predecessor, anchor_predecessor, target, target_digest,
        input_data["rule"])
    fresh_reuse_formation_ns = time.perf_counter_ns() - reuse_started

    validation_started = time.perf_counter_ns()
    primary_projection = bare_eligibility_projection(primary_obligation)
    cases = []

    def record(name, candidate, square, expected):
        result = validate_obligation(
            candidate, square, predecessor, anchor_predecessor, target,
            target_digest)
        cases.append({
            "name": name,
            "bare_projection_equal_to_primary": (
                bare_eligibility_projection(candidate) == primary_projection),
            "result": result,
            "expected": expected,
            "matched": result == expected,
        })

    record("primary-square", primary_obligation, primary, PASS)
    record("fresh-square-reuse", fresh_obligation, fresh, PASS)

    changed_target = copy.deepcopy(primary_obligation)
    changed_target["target_digest"] = "0" * 64
    record("changed-target", changed_target, primary,
           refusal("TargetComputadMismatch"))

    unknown_rule = copy.deepcopy(primary_obligation)
    unknown_rule["rule"]["id"] = "unregistered-swap.v0"
    record("unknown-rule", unknown_rule, primary,
           refusal("RuleIdentifierMismatch"))

    wrong_correspondence = copy.deepcopy(primary_obligation)
    wrong_correspondence["factor_correspondence"][0]["right_index"] = 0
    record("wrong-factor-correspondence", wrong_correspondence, primary,
           refusal("FactorCorrespondenceMismatch"))

    wrong_replay = copy.deepcopy(primary_obligation)
    wrong_replay["replay_witness"]["left_intermediate_word"] = "213213"
    record("wrong-replay-witness", wrong_replay, primary,
           refusal("ReplayWitnessMismatch"))

    premature_equality = copy.deepcopy(primary_obligation)
    premature_equality["semantic_equality"] = "EqualCompositeClaimed"
    record("premature-semantic-equality", premature_equality, primary,
           refusal("PrematureSemanticEquality"))

    premature_higher = copy.deepcopy(primary_obligation)
    premature_higher["higher_cell"] = "InterchangeThreeCellClaimed"
    record("premature-higher-cell", premature_higher, primary,
           refusal("PrematureHigherCell"))

    premature_filler = copy.deepcopy(primary_obligation)
    premature_filler["filler"] = "M6FillerClaimed"
    record("premature-filler", premature_filler, primary,
           refusal("PrematureFiller"))

    duplicated = copy.deepcopy(primary_obligation)
    duplicated["right_segment"] = copy.deepcopy(duplicated["left_segment"])
    record("duplicated-segment", duplicated, primary,
           refusal("DistinctSegmentsRequired"))

    overlap = copy.deepcopy(primary_obligation)
    overlap["left_segment"]["rewrite_intervals"][1] = [2, 4]
    record("overlapping-declared-interval", overlap, primary,
           refusal("LeftSegmentInvalid/Refused/rewrite_intervalsMismatch"))

    validation_ns = time.perf_counter_ns() - validation_started
    all_expected = all(case["matched"] for case in cases)
    bare_collisions_refused = sum(
        case["bare_projection_equal_to_primary"]
        and case["result"].startswith("Refused/")
        for case in cases
    )
    constructed_nodes = target_nodes + 8 + 4 + 2
    before_serialization_ns = time.perf_counter_ns() - started

    bare_bytes = len(canonical_bytes(primary_projection))
    obligation_bytes = len(canonical_bytes(primary_obligation))
    outcome = {
        "schema": "adva.research.typed-interchange-obligation.outcome.v0",
        "status": "PassedBoundedTypedInterchangeObligation" if all_expected else "Failed",
        "claim": "Two fixed disjoint squares each admit a rule-bound, exactly replayable interchange obligation while their composite equality and every higher cell remain unclaimed and unconstructed.",
        "claim_boundary": "Finite external syntax evidence only. A checked obligation is a boundary-plus-rule witness, not the discharge of that obligation, semantic equality, confluence, a 3-cell, or a filler.",
        "predecessor": {
            "path_used": predecessor_path.name,
            "run_sha256": predecessor_sha,
            "anchor_path_used": anchor_path.name,
            "anchor_run_sha256": anchor_sha,
            "target_digest": target_digest,
        },
        "target_nodes": target_nodes,
        "primary_obligation": primary_obligation,
        "fresh_reuse_obligation": fresh_obligation,
        "cases": cases,
        "comparison": {
            "bare_projection_sha256": digest(primary_projection),
            "bare_projection_bytes": bare_bytes,
            "obligation_sha256": digest(primary_obligation),
            "obligation_bytes": obligation_bytes,
            "formation_byte_delta": obligation_bytes - bare_bytes,
            "bare_projection_collisions_with_refused_controls": bare_collisions_refused,
            "finite_distinction": "the bare eligibility projection omits the rule, factor correspondence, replay witness, and promotion guards; six refused mutations preserve it exactly",
            "claim_boundary": "No general expressivity, completeness, equality, or asymptotic efficiency theorem is claimed.",
        },
        "proposed_word": {
            "word": "typed interchange obligation",
            "state": "Proposed",
            "role": "bind two retained comparison segments to one explicit admissible local-swap rule, factor correspondence, and two-order replay witness without discharging the higher comparison",
            "input": "one versioned target, two valid typed comparison segments with common endpoints, one declared rule id, an explicit factor correspondence, and source/intermediate/target replay words",
            "output_relation": PASS + " or a rule-, segment-, correspondence-, replay-, target-, independence-, or promotion-specific refusal",
            "applicability": "exactly two equal-length local rewrites occur on disjoint half-open sites, both orders retain valid typed segments, and applying either first leaves the other redex available at the same site",
            "witness": "both complete segments, target digest, registered rule payload, reversed factor-index correspondence, matched offsets/relations/2-cells, and both exact word replays",
            "counterexample": "changing the rule, factor correspondence, replay witness, equality flag, higher-cell flag, or filler flag preserves the bare eligibility projection but is specifically refused",
            "expansion": "validate both segments; reconstruct the unique reversed factor correspondence; replay left then right and right then left from the shared source; verify the common target and preserved other redex; retain all promotion guards",
            "refusal_conditions": [
                "target or rule mismatch",
                "invalid, duplicated, overlapping, endpoint-mismatched, or history-erased segment",
                "nonunique or altered factor correspondence",
                "redex unavailable or two-order replay mismatch",
                "premature semantic equality, higher cell, or filler",
            ],
            "replay": "timeout 30s python3 run.py",
            "residual": "no discharge of the interchange obligation, semantic equality, native horizontal or vertical composition, common 3-cell, Q4/M6 filler, fourteen-face pasting comparison, arbitrary A_n coherence, Research 0090 coverage, or arithmetic-universality result",
        },
        "cost": {
            "routes": 1,
            "squares": 2,
            "cases": len(cases),
            "constructed_nodes": constructed_nodes,
            "predecessor_verification_ns": predecessor_ns,
            "target_formation_ns": target_ns,
            "primary_obligation_formation_ns": primary_formation_ns,
            "fresh_reuse_obligation_formation_ns": fresh_reuse_formation_ns,
            "case_validation_ns": validation_ns,
            "whole_run_before_serialization_ns": before_serialization_ns,
            "implementation_correction_replays": 1,
            "ru_maxrss_kib_before_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    }

    serialization_started = time.perf_counter_ns()
    provisional = canonical_bytes(outcome)
    outcome["cost"]["serialization_ns"] = time.perf_counter_ns() - serialization_started
    outcome["cost"]["serialized_bytes"] = 0
    while True:
        encoded = canonical_bytes(outcome)
        size = len(encoded)
        if outcome["cost"]["serialized_bytes"] == size:
            break
        outcome["cost"]["serialized_bytes"] = size
    (ROOT / "outcome.json").write_bytes(encoded)
    print(json.dumps({
        "status": outcome["status"],
        "target_nodes": target_nodes,
        "constructed_nodes": constructed_nodes,
        "cases": len(cases),
        "fresh_reuse": cases[1]["result"],
        "bare_collisions_refused": bare_collisions_refused,
        "ru_maxrss_kib": outcome["cost"]["ru_maxrss_kib_before_serialization"],
        "serialized_bytes": len(encoded),
        "sha256": digest_bytes(encoded),
    }, sort_keys=True))
    if not all_expected:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
