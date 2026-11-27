#!/usr/bin/env python3
import copy
import hashlib
import importlib.util
import json
import resource
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return digest_bytes(canonical_bytes(value))


def load_module(expected_sha256):
    candidates = [
        ROOT.parent / "typed-interchange-obligation-20261124" / "run.py",
        ROOT.parent / "to24_typed_interchange_obligation_20261124" / "run.py",
    ]
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    if path is None:
        raise FileNotFoundError("PinnedPredecessorRunMissing")
    actual = digest_bytes(path.read_bytes())
    if actual != expected_sha256:
        raise ValueError("PinnedPredecessorRunMismatch")
    spec = importlib.util.spec_from_file_location("typed_interchange_predecessor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path, actual


def target_inventory(target):
    keys = sorted(target)
    return {
        "top_level_keys": keys,
        "objects": len(target.get("objects", [])),
        "one_cells": len(target.get("one_cells", [])),
        "two_cells": len(target.get("two_cells", [])),
        "higher_constructor_registry_declared": "higher_constructors" in target,
        "higher_constructor_count": (
            len(target["higher_constructors"])
            if isinstance(target.get("higher_constructors"), list) else None
        ),
    }


def base_projection(attempt):
    return {
        "target_digest": attempt["target_digest"],
        "obligation_digest": attempt["obligation_digest"],
        "obligation_status": "Checked",
    }


def make_attempt(obligation, target_digest, candidate=None):
    return {
        "schema": "adva.research.typed-discharge-attempt.v0",
        "target_digest": target_digest,
        "obligation_digest": digest(obligation),
        "candidate_constructor": copy.deepcopy(candidate),
        "semantic_equality": "NotClaimed",
        "higher_cell": "NotConstructed",
        "filler": "NotConstructed",
        "discharge": "NotClaimed",
    }


def audit(attempt, obligation, target, target_digest, required):
    if attempt.get("semantic_equality") != "NotClaimed":
        return {"result": "Refused/PrematureSemanticEquality", "frontier": required}
    if attempt.get("higher_cell") != "NotConstructed":
        return {"result": "Refused/PrematureHigherCell", "frontier": required}
    if attempt.get("filler") != "NotConstructed":
        return {"result": "Refused/PrematureFiller", "frontier": required}
    if attempt.get("discharge") != "NotClaimed":
        return {"result": "Refused/PrematureDischargeClaim", "frontier": required}
    if attempt.get("target_digest") != target_digest:
        return {"result": "Refused/TargetDigestMismatch", "frontier": required}
    if attempt.get("obligation_digest") != digest(obligation):
        return {"result": "Refused/ObligationDigestMismatch", "frontier": required}

    candidate = attempt.get("candidate_constructor")
    inventory = target_inventory(target)
    if candidate is not None:
        if candidate.get("boundary_digest") != digest(obligation):
            return {"result": "Refused/ConstructorBoundaryMismatch", "frontier": required}
        if candidate.get("state") == "AdmittedInTarget":
            if not inventory["higher_constructor_registry_declared"]:
                return {"result": "Refused/AdmissionNotBackedByTarget", "frontier": required}
        if candidate.get("semantic_equality") != "NotClaimed":
            return {"result": "Refused/CandidatePrematureEquality", "frontier": required}
        if candidate.get("filler") != "NotConstructed":
            return {"result": "Refused/CandidatePrematureFiller", "frontier": required}
        return {
            "result": "UnknownDischarge/ExternalConstructorUnadmitted",
            "frontier": [
                "higher_constructor_registry",
                "target_admission_receipt",
                "discharge_receipt",
            ],
        }

    if not inventory["higher_constructor_registry_declared"]:
        return {
            "result": "UnknownDischarge/NoRegisteredHigherConstructor",
            "frontier": list(required),
        }
    if inventory["higher_constructor_count"] == 0:
        return {
            "result": "UnknownDischarge/NoApplicableHigherConstructor",
            "frontier": list(required[1:]),
        }
    return {
        "result": "UnknownDischarge/ApplicabilityNotEvaluated",
        "frontier": list(required[1:]),
    }


def main():
    started = time.perf_counter_ns()
    input_data = json.loads((ROOT / "input.json").read_text())

    predecessor_started = time.perf_counter_ns()
    pred, pred_path, pred_sha = load_module(input_data["predecessor"]["run_sha256"])
    segment, segment_path, segment_sha = pred.load_predecessor(
        input_data["predecessor"]["segment_run_sha256"])
    anchor, anchor_path, anchor_sha = segment.load_predecessor(
        input_data["predecessor"]["anchor_run_sha256"])
    predecessor_ns = time.perf_counter_ns() - predecessor_started

    target_started = time.perf_counter_ns()
    target = anchor.build_target(input_data["target_descriptor"])
    target_digest = anchor.digest(target)
    target_ns = time.perf_counter_ns() - target_started
    if target_digest != input_data["predecessor"]["target_digest"]:
        raise ValueError("PinnedTargetDigestMismatch")
    inventory = target_inventory(target)
    target_nodes = inventory["objects"] + inventory["one_cells"] + inventory["two_cells"]

    # Reuse the exact two square declarations retained by the predecessor input.
    predecessor_input = json.loads(
        (pred_path.parent / "input.json").read_text())
    primary_square, fresh_square = predecessor_input["squares"]
    obligation_started = time.perf_counter_ns()
    primary = pred.form_obligation(
        primary_square, segment, anchor, target, target_digest,
        predecessor_input["rule"])
    primary_ns = time.perf_counter_ns() - obligation_started
    reuse_started = time.perf_counter_ns()
    fresh = pred.form_obligation(
        fresh_square, segment, anchor, target, target_digest,
        predecessor_input["rule"])
    fresh_ns = time.perf_counter_ns() - reuse_started
    if pred.validate_obligation(
            primary, primary_square, segment, anchor, target, target_digest) != pred.PASS:
        raise ValueError("PrimaryObligationInvalid")
    if pred.validate_obligation(
            fresh, fresh_square, segment, anchor, target, target_digest) != pred.PASS:
        raise ValueError("FreshObligationInvalid")

    required = input_data["required_capabilities"]
    external = copy.deepcopy(input_data["external_candidate"])
    external["boundary_digest"] = digest(primary)
    primary_attempt = make_attempt(primary, target_digest)
    fresh_attempt = make_attempt(fresh, target_digest)
    baseline = base_projection(primary_attempt)

    cases = []
    validation_started = time.perf_counter_ns()

    def record(name, attempt, obligation, expected_result, expected_frontier):
        result = audit(attempt, obligation, target, target_digest, required)
        cases.append({
            "name": name,
            "base_projection_equal_to_primary": base_projection(attempt) == baseline,
            "result": result["result"],
            "frontier": result["frontier"],
            "expected_result": expected_result,
            "expected_frontier": expected_frontier,
            "matched": result["result"] == expected_result and result["frontier"] == expected_frontier,
        })

    full = list(required)
    record("primary-no-registry", primary_attempt, primary,
           "UnknownDischarge/NoRegisteredHigherConstructor", full)
    record("fresh-obligation-reuse", fresh_attempt, fresh,
           "UnknownDischarge/NoRegisteredHigherConstructor", full)

    proposed = make_attempt(primary, target_digest, external)
    reduced = ["higher_constructor_registry", "target_admission_receipt", "discharge_receipt"]
    record("external-proposal-unadmitted", proposed, primary,
           "UnknownDischarge/ExternalConstructorUnadmitted", reduced)

    wrong_boundary = copy.deepcopy(proposed)
    wrong_boundary["candidate_constructor"]["boundary_digest"] = "0" * 64
    record("wrong-constructor-boundary", wrong_boundary, primary,
           "Refused/ConstructorBoundaryMismatch", full)

    false_admission = copy.deepcopy(proposed)
    false_admission["candidate_constructor"]["state"] = "AdmittedInTarget"
    record("unbacked-target-admission", false_admission, primary,
           "Refused/AdmissionNotBackedByTarget", full)

    premature_discharge = copy.deepcopy(primary_attempt)
    premature_discharge["discharge"] = "Discharged"
    record("premature-discharge", premature_discharge, primary,
           "Refused/PrematureDischargeClaim", full)

    premature_equality = copy.deepcopy(primary_attempt)
    premature_equality["semantic_equality"] = "EqualCompositeClaimed"
    record("premature-equality", premature_equality, primary,
           "Refused/PrematureSemanticEquality", full)

    premature_filler = copy.deepcopy(primary_attempt)
    premature_filler["filler"] = "M6FillerClaimed"
    record("premature-filler", premature_filler, primary,
           "Refused/PrematureFiller", full)

    wrong_target = copy.deepcopy(primary_attempt)
    wrong_target["target_digest"] = "0" * 64
    record("changed-target", wrong_target, primary,
           "Refused/TargetDigestMismatch", full)

    wrong_obligation = copy.deepcopy(primary_attempt)
    wrong_obligation["obligation_digest"] = "f" * 64
    record("changed-obligation", wrong_obligation, primary,
           "Refused/ObligationDigestMismatch", full)

    validation_ns = time.perf_counter_ns() - validation_started
    all_expected = all(case["matched"] for case in cases)
    collision_count = sum(
        case["base_projection_equal_to_primary"] and case["name"] != "primary-no-registry"
        for case in cases)
    primary_record = {
        "target_digest": target_digest,
        "obligation_digest": digest(primary),
        "target_inventory": inventory,
        "result": cases[0]["result"],
        "frontier": cases[0]["frontier"],
    }
    baseline_bytes = len(canonical_bytes(baseline))
    record_bytes = len(canonical_bytes(primary_record))
    constructed_nodes = target_nodes + 8 + 4 + 2 + len(cases)
    before_serialization_ns = time.perf_counter_ns() - started

    outcome = {
        "schema": "adva.research.typed-discharge-frontier.outcome.v0",
        "status": "PassedBoundedTypedDischargeFrontier" if all_expected else "Failed",
        "claim": "The exact pinned 240-node target declares no higher-constructor registry, so both checked interchange obligations remain UnknownDischarge with the same five-coordinate frontier.",
        "claim_boundary": "This is an exhaustive inventory result for one finite target representation, not a mathematical nonexistence theorem for 3-cells, an impossibility theorem, or a discharged obligation.",
        "predecessor": {
            "run_path": pred_path.name,
            "run_sha256": pred_sha,
            "segment_run_path": segment_path.name,
            "segment_run_sha256": segment_sha,
            "anchor_run_path": anchor_path.name,
            "anchor_run_sha256": anchor_sha,
        },
        "target": {"digest": target_digest, "inventory": inventory, "nodes": target_nodes},
        "primary_record": primary_record,
        "fresh_obligation_digest": digest(fresh),
        "cases": cases,
        "comparison": {
            "checked_obligation_projection_bytes": baseline_bytes,
            "typed_frontier_record_bytes": record_bytes,
            "formation_byte_delta": record_bytes - baseline_bytes,
            "base_projection_collisions_beyond_primary": collision_count,
            "finite_distinction": "the checked-obligation-only projection cannot state whether registry, applicability, admission, boundary, or discharge evidence is missing",
            "claim_boundary": "No general expressivity, minimality, completeness, or asymptotic efficiency theorem is claimed.",
        },
        "proposed_word": {
            "word": "typed discharge frontier",
            "state": "Proposed",
            "role": "retain the ordered target capabilities still missing between a checked higher obligation and an admissible discharge",
            "input": "one target digest and complete finite target inventory, one checked typed obligation, and an optional external constructor proposal",
            "output_relation": "UnknownDischarge with an ordered frontier, or a target-, obligation-, boundary-, admission-, or promotion-specific refusal",
            "applicability": "the checked obligation and target are exactly pinned and the audit is restricted to explicitly declared target registries and receipts",
            "witness": "the target top-level key inventory and node counts, target and obligation digests, optional candidate digest, result, and ordered missing-capability list",
            "counterexample": "a structurally plausible external constructor proposal with the correct boundary remains unadmitted because the target has no registry; claiming target admission without such a registry is refused",
            "expansion": "validate the obligation; inventory the target; locate an explicit higher-constructor registry; match boundary and applicability; require target-backed admission and a discharge receipt; otherwise return the remaining ordered frontier",
            "refusal_conditions": [
                "target or obligation digest mismatch",
                "constructor boundary mismatch",
                "claimed target admission without registry support",
                "premature equality, higher cell, filler, or discharge",
            ],
            "replay": "timeout 30s python3 run.py",
            "residual": "no search outside the exact target representation, no theorem that a 3-cell cannot exist, no admitted constructor, no discharge, equality, confluence, filler, Research 0090 coverage, Research 0092 promotion, or arithmetic-universality result",
        },
        "cost": {
            "routes": 1,
            "cases": len(cases),
            "constructed_nodes": constructed_nodes,
            "predecessor_verification_ns": predecessor_ns,
            "target_formation_ns": target_ns,
            "primary_obligation_formation_ns": primary_ns,
            "fresh_reuse_formation_ns": fresh_ns,
            "case_validation_ns": validation_ns,
            "whole_run_before_serialization_ns": before_serialization_ns,
            "ru_maxrss_kib_before_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "implementation_correction_replays": 1,
        },
    }
    serialization_started = time.perf_counter_ns()
    outcome["cost"]["serialization_ns"] = 0
    outcome["cost"]["serialized_bytes"] = 0
    while True:
        encoded = canonical_bytes(outcome)
        size = len(encoded)
        if outcome["cost"]["serialized_bytes"] == size:
            break
        outcome["cost"]["serialized_bytes"] = size
    outcome["cost"]["serialization_ns"] = time.perf_counter_ns() - serialization_started
    encoded = canonical_bytes(outcome)
    # A final size stabilization is needed after inserting serialization time.
    while outcome["cost"]["serialized_bytes"] != len(encoded):
        outcome["cost"]["serialized_bytes"] = len(encoded)
        encoded = canonical_bytes(outcome)
    (ROOT / "outcome.json").write_bytes(encoded)
    print(json.dumps({
        "status": outcome["status"],
        "target_keys": inventory["top_level_keys"],
        "higher_registry": inventory["higher_constructor_registry_declared"],
        "cases": len(cases),
        "constructed_nodes": constructed_nodes,
        "fresh_reuse": cases[1]["result"],
        "serialized_bytes": len(encoded),
        "ru_maxrss_kib": outcome["cost"]["ru_maxrss_kib_before_serialization"],
        "sha256": digest_bytes(encoded),
    }, sort_keys=True))
    if not all_expected:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
