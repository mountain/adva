#!/usr/bin/env python3
import copy
import hashlib
import importlib.util
import json
import resource
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent

EXPECTED_REQUIRED = [
    "exact_a3_target_binding",
    "versioned_entry_identity",
    "higher_constructor_entry_kind",
    "higher_constructor_boundary_applicability",
    "target_authority_issuer",
    "target_admission_receipt",
    "obligation_discharge_receipt",
    "runtime_semantic_authority",
]

EXPECTED_SOURCE_PINS = {
    "operation-rust": "1bdacdd98ed52e8e7518afd1438240bfb1d987bf",
    "operation-adr": "e8d2084046c49ba94659be2f842099998df3406d",
    "witness-seed": "1fcd7ac08472676e1bbd489d575aa2aabaed9317",
    "witness-seal": "059523e2011d5536b629e1caa1daaa1ef501c4f9",
    "claims-registry": "d60c1a775a696b70f509a0018cf76085aa3e5b64",
    "publication-boundary": "19a6fd34bb947881dfc2e3467010cef7e0351037",
    "math-catalog-boundary": "5581ff577bb459ca466d4b309cff0ab6b9b6678a",
    "external-a3-slot": "ec9b64f330b7cf2574647611b86bd5e615da79a6",
}

EXPECTED_CANDIDATE_SUPPORT = {
    "builtin-operation-registry": [
        "versioned_entry_identity", "runtime_semantic_authority"],
    "witness-seed-and-seal": [
        "versioned_entry_identity", "runtime_semantic_authority"],
    "claims-registry": ["versioned_entry_identity"],
    "publication-admission": ["versioned_entry_identity"],
    "external-a3-admission-slot": [
        "exact_a3_target_binding",
        "versioned_entry_identity",
        "higher_constructor_entry_kind",
        "higher_constructor_boundary_applicability",
    ],
}


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest(value):
    return digest_bytes(canonical_bytes(value))


def load_predecessor(expected_run, expected_outcome):
    candidates = [
        ROOT.parent / "constructor-admission-slot-20261126" / "run.py",
        ROOT.parent / "to24_typed_constructor_admission_slot_20261126" / "run.py",
    ]
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    if path is None:
        raise FileNotFoundError("PinnedPredecessorRunMissing")
    if digest_bytes(path.read_bytes()) != expected_run:
        raise ValueError("PinnedPredecessorRunMismatch")
    outcome_path = path.parent / "outcome.json"
    if digest_bytes(outcome_path.read_bytes()) != expected_outcome:
        raise ValueError("PinnedPredecessorOutcomeMismatch")
    spec = importlib.util.spec_from_file_location("constructor_slot_predecessor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path


def base_projection(request, candidates):
    return {
        "target_digest": request["target_digest"],
        "obligation_digest": request["obligation_digest"],
        "candidate_ids": [candidate["candidate_id"] for candidate in candidates],
    }


def validate_inventory(required, sources, candidates):
    if required != EXPECTED_REQUIRED:
        return "Refused/RequiredCapabilitySetMismatch"
    if len(sources) != len(EXPECTED_SOURCE_PINS):
        return "Refused/SourceInventoryMismatch"
    observed_pins = {source.get("source_id"): source.get("blob_sha") for source in sources}
    if observed_pins != EXPECTED_SOURCE_PINS:
        return "Refused/SourcePinMismatch"
    if any(not source.get("path") or not source.get("ref") or not source.get("evidence")
           for source in sources):
        return "Refused/IncompleteSourceEvidence"
    if len(candidates) != len(EXPECTED_CANDIDATE_SUPPORT):
        return "Refused/CandidateInventoryMismatch"
    observed = {candidate.get("candidate_id"): candidate.get("supported_capabilities")
                for candidate in candidates}
    if set(observed) != set(EXPECTED_CANDIDATE_SUPPORT):
        return "Refused/CandidateInventoryMismatch"
    for candidate_id, support in observed.items():
        if support != EXPECTED_CANDIDATE_SUPPORT[candidate_id]:
            return "Refused/UnsupportedCapabilityClaim"
        if any(capability not in required for capability in support):
            return "Refused/CapabilityOutsideProfile"
    source_ids = set(EXPECTED_SOURCE_PINS)
    if any(not set(candidate.get("source_ids", [])).issubset(source_ids)
           or not candidate.get("scope") for candidate in candidates):
        return "Refused/CandidateEvidenceMismatch"
    return None


def analyze(request, required, sources, candidates, predecessor):
    if request.get("target_digest") != predecessor["target_digest"]:
        return {"result": "Refused/TargetDigestMismatch"}
    if request.get("obligation_digest") not in {
            predecessor["primary_obligation_digest"], predecessor["fresh_obligation_digest"]}:
        return {"result": "Refused/ObligationDigestMismatch"}
    inventory_error = validate_inventory(required, sources, candidates)
    if inventory_error:
        return {"result": inventory_error}
    if request.get("allow_cross_surface_union") is not False:
        return {"result": "Refused/UnauthorizedCrossSurfaceUnion"}

    rows = []
    union_support = set()
    for candidate in candidates:
        support = set(candidate["supported_capabilities"])
        union_support.update(support)
        missing = [capability for capability in required if capability not in support]
        rows.append({
            "candidate_id": candidate["candidate_id"],
            "scope": candidate["scope"],
            "source_ids": candidate["source_ids"],
            "supported": candidate["supported_capabilities"],
            "missing": missing,
            "covers_all": not missing,
        })
    complete = [row["candidate_id"] for row in rows if row["covers_all"]]
    union_missing = [capability for capability in required if capability not in union_support]
    return {
        "result": "CandidateFound/FullAuthority" if complete else "AuthorityGap/NoCandidateCoversAll",
        "complete_candidates": complete,
        "candidate_rows": rows,
        "declared_union_missing": union_missing,
        "cross_surface_union_authorized": False,
    }


def main():
    started = time.perf_counter_ns()
    input_data = json.loads((ROOT / "input.json").read_text())

    predecessor_started = time.perf_counter_ns()
    _, predecessor_path = load_predecessor(
        input_data["predecessor"]["run_sha256"],
        input_data["predecessor"]["outcome_sha256"],
    )
    predecessor_ns = time.perf_counter_ns() - predecessor_started

    inventory_started = time.perf_counter_ns()
    required = copy.deepcopy(input_data["required_capabilities"])
    sources = copy.deepcopy(input_data["sources"])
    candidates = copy.deepcopy(input_data["candidates"])
    inventory_error = validate_inventory(required, sources, candidates)
    if inventory_error:
        raise ValueError(inventory_error)
    inventory_ns = time.perf_counter_ns() - inventory_started

    predecessor = input_data["predecessor"]
    primary_request = {
        "target_digest": predecessor["target_digest"],
        "obligation_digest": predecessor["primary_obligation_digest"],
        "allow_cross_surface_union": False,
    }
    fresh_request = {
        "target_digest": predecessor["target_digest"],
        "obligation_digest": predecessor["fresh_obligation_digest"],
        "allow_cross_surface_union": False,
    }
    primary_started = time.perf_counter_ns()
    primary_result = analyze(primary_request, required, sources, candidates, predecessor)
    primary_ns = time.perf_counter_ns() - primary_started
    fresh_started = time.perf_counter_ns()
    fresh_result = analyze(fresh_request, required, sources, candidates, predecessor)
    fresh_ns = time.perf_counter_ns() - fresh_started

    expected_gap = "AuthorityGap/NoCandidateCoversAll"
    cases = []
    baseline = base_projection(primary_request, candidates)
    validation_started = time.perf_counter_ns()

    def record(name, request, case_required, case_sources, case_candidates, expected):
        result = analyze(request, case_required, case_sources, case_candidates, predecessor)
        cases.append({
            "name": name,
            "base_projection_equal_to_primary": (
                base_projection(request, case_candidates) == baseline),
            "result": result["result"],
            "expected": expected,
            "matched": result["result"] == expected,
        })

    record("primary-five-surface-audit", primary_request, required, sources, candidates,
           expected_gap)
    record("fresh-obligation-reuse", fresh_request, required, sources, candidates,
           expected_gap)

    mutation_specs = [
        ("operation-registry-scope-conflation", "builtin-operation-registry"),
        ("witness-seal-scope-conflation", "witness-seed-and-seal"),
        ("claims-registry-authority-conflation", "claims-registry"),
        ("publication-admission-authority-conflation", "publication-admission"),
        ("external-slot-self-authority", "external-a3-admission-slot"),
    ]
    for name, candidate_id in mutation_specs:
        mutated = copy.deepcopy(candidates)
        item = next(candidate for candidate in mutated if candidate["candidate_id"] == candidate_id)
        item["supported_capabilities"] = list(required)
        record(name, primary_request, required, sources, mutated,
               "Refused/UnsupportedCapabilityClaim")

    drifted_sources = copy.deepcopy(sources)
    drifted_sources[0]["blob_sha"] = "0" * 40
    record("source-pin-drift", primary_request, required, drifted_sources, candidates,
           "Refused/SourcePinMismatch")

    shortened_required = required[:-1]
    record("required-capability-omission", primary_request, shortened_required, sources, candidates,
           "Refused/RequiredCapabilitySetMismatch")

    union_request = copy.deepcopy(primary_request)
    union_request["allow_cross_surface_union"] = True
    record("unauthorized-cross-surface-union", union_request, required, sources, candidates,
           "Refused/UnauthorizedCrossSurfaceUnion")

    validation_ns = time.perf_counter_ns() - validation_started
    all_expected = all(case["matched"] for case in cases)
    collision_count = sum(
        case["base_projection_equal_to_primary"] and case["name"] != "primary-five-surface-audit"
        for case in cases)
    primary_record = {
        "target_digest": primary_request["target_digest"],
        "obligation_digest": primary_request["obligation_digest"],
        "required_capabilities": required,
        "candidate_rows": primary_result["candidate_rows"],
        "declared_union_missing": primary_result["declared_union_missing"],
        "result": primary_result["result"],
        "scope_boundary": "the five declared source-pinned surfaces only",
    }
    baseline_bytes = len(canonical_bytes(baseline))
    record_bytes = len(canonical_bytes(primary_record))
    constructed_nodes = len(sources) + len(candidates) + 2 + len(cases)
    before_serialization_ns = time.perf_counter_ns() - started

    outcome = {
        "schema": "adva.research.scoped-constructor-authority-gap.outcome.v0",
        "status": "PassedBoundedScopedConstructorAuthorityGap" if all_expected else "Failed",
        "claim": "Within five exact source-pinned Adva surfaces, no single candidate covers all eight A3 higher-constructor authority capabilities; even their unauthorized union lacks target authority issuance, a target-admission receipt and an obligation-discharge receipt.",
        "claim_boundary": "This is an exhaustive finite result over the five declared surfaces, not a whole-repository absence theorem, a proof that no future mechanism can exist, or authority to compose the candidates.",
        "predecessor": {
            "path": predecessor_path.name,
            "run_sha256": predecessor["run_sha256"],
            "outcome_sha256": predecessor["outcome_sha256"],
        },
        "source_pins": {source["source_id"]: source["blob_sha"] for source in sources},
        "primary_record": primary_record,
        "fresh_record": {
            "obligation_digest": fresh_request["obligation_digest"],
            "result": fresh_result["result"],
            "declared_union_missing": fresh_result["declared_union_missing"],
        },
        "cases": cases,
        "comparison": {
            "candidate_name_projection_bytes": baseline_bytes,
            "typed_authority_gap_record_bytes": record_bytes,
            "formation_byte_delta": record_bytes - baseline_bytes,
            "base_projection_collisions_beyond_primary": collision_count,
            "finite_distinction": "candidate names alone do not retain per-capability support, source scope, missing sets, union residual or the prohibition on cross-surface authority composition",
            "claim_boundary": "No general expressivity, minimality, completeness, global source inventory or efficiency theorem is claimed.",
        },
        "proposed_word": {
            "word": "scoped constructor authority gap",
            "state": "Proposed",
            "role": "retain the exact missing authority capabilities after a declared finite inventory of possible constructor-owning surfaces has been checked",
            "input": "one target and obligation coordinate, one ordered required-capability profile, and finitely many source-pinned candidate surfaces with scoped supported-capability sets",
            "output_relation": "AuthorityGap with per-candidate and declared-union residuals, CandidateFound, or a source-, inventory-, scope-, capability-, target-, obligation-, or union-specific refusal",
            "applicability": "the candidate inventory, source pins, capability meanings and no-cross-surface-composition rule are frozen before evaluation",
            "witness": "all source pins, the required profile, one row of supported and missing capabilities per candidate, the declared-union residual, target and obligation digests, and the scope boundary",
            "counterexample": "promoting OperationSpec, WitnessProofV0::Seal, claim registration, publication admission or an external slot to full A3 constructor authority is refused because each crosses its pinned scope",
            "expansion": "verify source pins and the predecessor coordinate; validate the exact candidate inventory and supported sets; subtract each set from the required profile; require a single full candidate; compute but do not authorize the union; retain both residuals",
            "refusal_conditions": [
                "source-pin or candidate-inventory drift",
                "required-capability omission or unsupported capability claim",
                "operation, arithmetic Seal, documentary claim, publication or external-interface scope conflated with A3 constructor authority",
                "unauthorized composition of authority across surfaces"
            ],
            "replay": "timeout 30s python3 run.py",
            "residual": "the inventory is not a whole-repository absence theorem; no target authority issuer, admission receipt, discharge receipt, admitted constructor, higher cell, filler, Research 0090 coverage, Research 0092 promotion, arithmetic-universality or hypothesized-arithmetic-truth result is obtained",
        },
        "cost": {
            "routes": 1,
            "source_records": len(sources),
            "candidates": len(candidates),
            "cases": len(cases),
            "constructed_nodes": constructed_nodes,
            "predecessor_verification_ns": predecessor_ns,
            "source_inventory_formation_ns": inventory_ns,
            "primary_analysis_ns": primary_ns,
            "fresh_reuse_ns": fresh_ns,
            "case_validation_ns": validation_ns,
            "whole_run_before_serialization_ns": before_serialization_ns,
            "ru_maxrss_kib_before_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "implementation_correction_replays": 0,
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
    while outcome["cost"]["serialized_bytes"] != len(encoded):
        outcome["cost"]["serialized_bytes"] = len(encoded)
        encoded = canonical_bytes(outcome)
    (ROOT / "outcome.json").write_bytes(encoded)
    print(json.dumps({
        "status": outcome["status"],
        "sources": len(sources),
        "candidates": len(candidates),
        "cases": len(cases),
        "constructed_nodes": constructed_nodes,
        "primary": primary_result["result"],
        "fresh": fresh_result["result"],
        "union_missing": primary_result["declared_union_missing"],
        "collisions": collision_count,
        "serialized_bytes": len(encoded),
        "ru_maxrss_kib": outcome["cost"]["ru_maxrss_kib_before_serialization"],
        "sha256": digest_bytes(encoded),
    }, sort_keys=True))
    if not all_expected:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
