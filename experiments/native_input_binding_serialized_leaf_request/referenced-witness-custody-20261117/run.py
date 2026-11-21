#!/usr/bin/env python3
"""Equal-budget comparison of two- and three-branch witness custody."""

from __future__ import annotations

import hashlib
import json
import resource
import time
from collections import Counter

BIT_NAMES = [
    "carried_fields_complete",
    "recipe_present",
    "reconstruction_inputs_present",
    "reference_locator_present",
    "content_digest_present",
    "authority_pin_present",
    "retrieval_receipt_present",
    "request_pin_matches",
    "checker_pin_matches",
    "noncommutative_order_preserved",
    "reference_digest_matches",
]
G2 = ("carried", "reconstructed", "reserved-unexpressed")
G3 = ("carried", "reconstructed", "referenced")


def bits(shape: int) -> dict[str, bool]:
    return {name: bool(shape & (1 << index)) for index, name in enumerate(BIT_NAMES)}


def classify(branch: str, shape: int) -> str:
    b = bits(shape)
    if not b["request_pin_matches"]:
        return "Refused/RequestPinMismatch"
    if not b["checker_pin_matches"]:
        return "Refused/CheckerPinMismatch"
    if not b["noncommutative_order_preserved"]:
        return "Refused/NoncommutativeOrderMismatch"
    if branch == "reserved-unexpressed":
        return "Unknown/UnexpressedCustodyMode"

    reference_members = (
        b["reference_locator_present"]
        or b["content_digest_present"]
        or b["authority_pin_present"]
        or b["retrieval_receipt_present"]
    )

    if branch == "carried":
        if b["recipe_present"] or b["reconstruction_inputs_present"] or reference_members:
            return "Refused/MixedCustodyShape"
        if not b["carried_fields_complete"]:
            return "CertificateObstruction/MissingCarriedFields"
        return "StructurallyReady/CarriedFieldsPresent"

    if branch == "reconstructed":
        if b["carried_fields_complete"] or reference_members:
            return "Refused/MixedCustodyShape"
        if not b["recipe_present"]:
            return "CertificateObstruction/MissingRecipe"
        if not b["reconstruction_inputs_present"]:
            return "CertificateObstruction/MissingReconstructionInputs"
        return "Unknown/NativeReconstructionNotRun"

    if branch == "referenced":
        if b["carried_fields_complete"] or b["recipe_present"] or b["reconstruction_inputs_present"]:
            return "Refused/MixedCustodyShape"
        if not b["reference_locator_present"]:
            return "CertificateObstruction/MissingReferenceLocator"
        if not b["content_digest_present"]:
            return "CertificateObstruction/MissingContentDigest"
        if not b["authority_pin_present"]:
            return "CertificateObstruction/MissingAuthorityPin"
        if not b["retrieval_receipt_present"]:
            return "CertificateObstruction/MissingRetrievalReceipt"
        if not b["reference_digest_matches"]:
            return "Refused/ReferenceDigestMismatch"
        return "StructurallyReady/ReferencedReceiptPresent"

    raise ValueError(branch)


def shape_for(**values: bool) -> int:
    result = 0
    for index, name in enumerate(BIT_NAMES):
        if values.get(name, False):
            result |= 1 << index
    return result


def statuses(grammar: tuple[str, ...], shape: int) -> dict[str, str]:
    return {branch: classify(branch, shape) for branch in grammar}


def main() -> None:
    start = time.perf_counter_ns()
    evaluation_start = time.perf_counter_ns()
    counts = {"two_branch": Counter(), "three_branch": Counter()}
    ready_shapes = {"two_branch": set(), "three_branch": set()}
    invariant_checks = 0
    nodes = 0

    for shape in range(1 << len(BIT_NAMES)):
        for grammar_name, grammar in (("two_branch", G2), ("three_branch", G3)):
            branch_statuses = statuses(grammar, shape)
            nodes += len(grammar)
            counts[grammar_name].update(branch_statuses.values())
            if any(value.startswith("StructurallyReady/") for value in branch_statuses.values()):
                ready_shapes[grammar_name].add(shape)
        assert classify("carried", shape) == statuses(G3, shape)["carried"]
        assert classify("reconstructed", shape) == statuses(G3, shape)["reconstructed"]
        invariant_checks += 2
    evaluation_ns = time.perf_counter_ns() - evaluation_start

    target = shape_for(
        reference_locator_present=True,
        content_digest_present=True,
        authority_pin_present=True,
        retrieval_receipt_present=True,
        request_pin_matches=True,
        checker_pin_matches=True,
        noncommutative_order_preserved=True,
        reference_digest_matches=True,
    )
    missing_authority = target & ~(1 << BIT_NAMES.index("authority_pin_present"))
    missing_receipt = target & ~(1 << BIT_NAMES.index("retrieval_receipt_present"))
    digest_mismatch = target & ~(1 << BIT_NAMES.index("reference_digest_matches"))
    carried = shape_for(
        carried_fields_complete=True,
        request_pin_matches=True,
        checker_pin_matches=True,
        noncommutative_order_preserved=True,
        reference_digest_matches=True,
    )

    verification_start = time.perf_counter_ns()
    controls = {
        "target_two_branch": statuses(G2, target),
        "target_three_branch": statuses(G3, target),
        "referenced_missing_authority": classify("referenced", missing_authority),
        "referenced_missing_receipt": classify("referenced", missing_receipt),
        "referenced_digest_mismatch": classify("referenced", digest_mismatch),
        "carried_two_branch": classify("carried", carried),
        "carried_three_branch": statuses(G3, carried)["carried"],
    }
    assert nodes == 12_288
    assert invariant_checks == 4_096
    assert not any(value.startswith("StructurallyReady/") for value in controls["target_two_branch"].values())
    assert controls["target_three_branch"]["referenced"] == "StructurallyReady/ReferencedReceiptPresent"
    assert controls["referenced_missing_authority"] == "CertificateObstruction/MissingAuthorityPin"
    assert controls["referenced_missing_receipt"] == "CertificateObstruction/MissingRetrievalReceipt"
    assert controls["referenced_digest_mismatch"] == "Refused/ReferenceDigestMismatch"
    assert controls["carried_two_branch"] == controls["carried_three_branch"]
    newly_ready = ready_shapes["three_branch"] - ready_shapes["two_branch"]
    assert newly_ready == {target}
    verification_ns = time.perf_counter_ns() - verification_start

    formation_start = time.perf_counter_ns()
    two_branch_bytes = json.dumps(
        {"witness_custody_mode": ["carried", "reconstructed"]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    two_branch_formation_ns = time.perf_counter_ns() - formation_start
    formation_start = time.perf_counter_ns()
    three_branch_bytes = json.dumps(
        {"witness_custody_mode": ["carried", "reconstructed", "referenced"]},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    three_branch_formation_ns = time.perf_counter_ns() - formation_start

    reuse_start = time.perf_counter_ns()
    reuse = {
        "instance": "external TransportCertificate manifest",
        "complete_reference": classify("referenced", target),
        "missing_authority": classify("referenced", missing_authority),
        "missing_receipt": classify("referenced", missing_receipt),
        "changed_digest": classify("referenced", digest_mismatch),
    }
    assert reuse == {
        "instance": "external TransportCertificate manifest",
        "complete_reference": "StructurallyReady/ReferencedReceiptPresent",
        "missing_authority": "CertificateObstruction/MissingAuthorityPin",
        "missing_receipt": "CertificateObstruction/MissingRetrievalReceipt",
        "changed_digest": "Refused/ReferenceDigestMismatch",
    }
    reuse_ns = time.perf_counter_ns() - reuse_start

    outcome = {
        "schema": "adva.research.referenced-witness-custody.outcome.v0",
        "status": "PassedFiniteReferencedCustodyNeed",
        "vocabulary_revision": {
            "word": "witness-custody mode",
            "state": "Proposed",
            "previous_values": ["carried", "reconstructed"],
            "revised_values": ["carried", "reconstructed", "referenced"],
            "referenced_input": "locator, content digest, authority pin, retrieval receipt, request/checker pins, preserved order",
            "output_relation": "StructurallyReady/ReferencedReceiptPresent with semantic import still residual",
            "applicability": "witness bytes are held outside the request and are neither carried fields nor reconstructed from a recipe",
            "witness": "equal-budget 12,288-node comparison and fresh external TransportCertificate reuse",
            "refusal_conditions": [
                "custody members mixed",
                "locator, digest, authority pin, or receipt absent",
                "retrieved digest mismatches",
                "request/checker pin mismatch",
                "noncommutative order changed",
            ],
            "expansion": "resolve the pinned locator, verify authority and digest against the receipt, import bytes, then run native semantic validation",
            "residual": "no network fetch, external byte import, or native certificate validation was executed",
        },
        "comparison": {
            "evidence_shapes": 1 << len(BIT_NAMES),
            "nodes_per_grammar": 6_144,
            "total_nodes": nodes,
            "carried_reconstructed_invariant_checks": invariant_checks,
            "two_branch_ready_shape_count": len(ready_shapes["two_branch"]),
            "three_branch_ready_shape_count": len(ready_shapes["three_branch"]),
            "newly_ready_shape_count": len(newly_ready),
            "newly_ready_shapes": sorted(newly_ready),
            "target_shape": target,
            "two_branch_target_statuses": controls["target_two_branch"],
            "three_branch_target_statuses": controls["target_three_branch"],
            "two_branch_status_counts": dict(sorted(counts["two_branch"].items())),
            "three_branch_status_counts": dict(sorted(counts["three_branch"].items())),
        },
        "controls": controls,
        "reuse": reuse,
        "cost": {
            "routes": 1,
            "evaluation_nodes": nodes,
            "evaluation_ns": evaluation_ns,
            "verification_ns": verification_ns,
            "two_branch_formation_ns": two_branch_formation_ns,
            "three_branch_formation_ns": three_branch_formation_ns,
            "two_branch_bytes": len(two_branch_bytes),
            "three_branch_bytes": len(three_branch_bytes),
            "vocabulary_byte_delta": len(three_branch_bytes) - len(two_branch_bytes),
            "reuse_ns": reuse_ns,
            "whole_run_before_serialization_ns": time.perf_counter_ns() - start,
            "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "native_executions": 0,
            "external_fetches": 0,
            "implementation_correction_replays": 0,
        },
        "claim_boundaries": {
            "finite_structural_model_only": True,
            "word_promoted": False,
            "native_adapter": False,
            "external_reference_imported": False,
            "semantic_certificate_acceptance": False,
            "research_0090_coverage": False,
            "research_0092_promotion": False,
            "m6_filler": False,
            "arithmetic_universality": False,
            "hypothesized_arithmetic_truth": False,
            "social_trust": False,
            "measured_practical_adoption": False,
        },
    }
    serialization_start = time.perf_counter_ns()
    encoded = json.dumps(outcome, indent=2, sort_keys=True) + "\n"
    serialization_ns = time.perf_counter_ns() - serialization_start
    outcome["cost"]["serialization_ns"] = serialization_ns
    while True:
        encoded = json.dumps(outcome, indent=2, sort_keys=True) + "\n"
        size = len(encoded.encode())
        if outcome["cost"].get("serialized_bytes") == size:
            break
        outcome["cost"]["serialized_bytes"] = size
    encoded = json.dumps(outcome, indent=2, sort_keys=True) + "\n"
    print(encoded, end="")
    print("OUTCOME_SHA256 " + hashlib.sha256(encoded.encode()).hexdigest(), file=__import__("sys").stderr)


if __name__ == "__main__":
    main()

