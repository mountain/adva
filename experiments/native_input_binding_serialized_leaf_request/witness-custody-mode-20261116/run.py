#!/usr/bin/env python3
"""Exhaustive finite comparison for a proposed witness-custody mode."""

from __future__ import annotations

import hashlib
import json
import resource
import time
from collections import Counter, defaultdict

FIELDS = [
    "source_snapshot",
    "residual_snapshot",
    "static_value",
    "bound_source",
    "dynamic_source",
    "event_map",
    "occurrence_map",
    "forgotten_static_occurrences",
    "forgotten_static_history",
    "binding_node",
]
MODES = ("omitted", "carried", "reconstructed")


def classify(mode: str, mask: int, auxiliary: int, field_count: int) -> str:
    recipe = bool(auxiliary & 1)
    inputs = bool(auxiliary & 2)
    request_pin = bool(auxiliary & 4)
    checker_pin = bool(auxiliary & 8)
    ordered = bool(auxiliary & 16)
    full = (1 << field_count) - 1

    if not request_pin:
        return "Refused/RequestPinMismatch"
    if not checker_pin:
        return "Refused/CheckerPinMismatch"
    if not ordered:
        return "Refused/NoncommutativeOrderMismatch"

    if mode == "omitted":
        if mask == full or (recipe and inputs):
            return "Unknown/CustodyModeOmitted"
        return "CertificateObstruction/IncompleteWitness"

    if mode == "carried":
        if recipe or inputs:
            return "Refused/MixedCustodyShape"
        if mask != full:
            return "CertificateObstruction/MissingCarriedFields"
        return "StructurallyReady/CarriedFieldsPresent"

    if mode == "reconstructed":
        if mask:
            return "Refused/MixedCustodyShape"
        if not recipe:
            return "CertificateObstruction/MissingRecipe"
        if not inputs:
            return "CertificateObstruction/MissingReconstructionInputs"
        return "Unknown/NativeReconstructionNotRun"

    raise ValueError(mode)


def main() -> None:
    start = time.perf_counter_ns()
    baseline = defaultdict(set)
    explicit = defaultdict(set)
    status_counts = Counter()
    candidates = 0

    enumeration_start = time.perf_counter_ns()
    for mode in MODES:
        for mask in range(1 << len(FIELDS)):
            for auxiliary in range(32):
                status = classify(mode, mask, auxiliary, len(FIELDS))
                baseline[(mask, auxiliary)].add(status)
                explicit[(mode, mask, auxiliary)].add(status)
                status_counts[status] += 1
                candidates += 1
    enumeration_ns = time.perf_counter_ns() - enumeration_start

    verification_start = time.perf_counter_ns()
    mixed_baseline = {key: sorted(values) for key, values in baseline.items() if len(values) > 1}
    mixed_explicit = {key: sorted(values) for key, values in explicit.items() if len(values) > 1}
    full = (1 << len(FIELDS)) - 1
    controls = {
        "mode_omitted_complete_fields": classify("omitted", full, 28, len(FIELDS)),
        "carried_complete": classify("carried", full, 28, len(FIELDS)),
        "carried_missing_history": classify("carried", full ^ (1 << 8), 28, len(FIELDS)),
        "carried_mixed_recipe": classify("carried", full, 29, len(FIELDS)),
        "reconstructed_ready_but_unexecuted": classify("reconstructed", 0, 31, len(FIELDS)),
        "reconstructed_missing_recipe": classify("reconstructed", 0, 30, len(FIELDS)),
        "altered_order": classify("carried", full, 12, len(FIELDS)),
        "request_pin_mismatch": classify("carried", full, 24, len(FIELDS)),
        "checker_pin_mismatch": classify("carried", full, 20, len(FIELDS)),
    }
    expected_controls = {
        "mode_omitted_complete_fields": "Unknown/CustodyModeOmitted",
        "carried_complete": "StructurallyReady/CarriedFieldsPresent",
        "carried_missing_history": "CertificateObstruction/MissingCarriedFields",
        "carried_mixed_recipe": "Refused/MixedCustodyShape",
        "reconstructed_ready_but_unexecuted": "Unknown/NativeReconstructionNotRun",
        "reconstructed_missing_recipe": "CertificateObstruction/MissingRecipe",
        "altered_order": "Refused/NoncommutativeOrderMismatch",
        "request_pin_mismatch": "Refused/RequestPinMismatch",
        "checker_pin_mismatch": "Refused/CheckerPinMismatch",
    }
    assert candidates == 98_304
    assert len(mixed_baseline) == 4_096
    assert not mixed_explicit
    assert controls == expected_controls
    verification_ns = time.perf_counter_ns() - verification_start

    formation_record = {
        "profile": "adva.research.certificate-envelope.v0",
        "request_pin": "request:example",
        "checker_pin": "checker:example",
    }
    formation_start = time.perf_counter_ns()
    baseline_bytes = json.dumps(formation_record, sort_keys=True, separators=(",", ":")).encode()
    baseline_formation_ns = time.perf_counter_ns() - formation_start
    formation_start = time.perf_counter_ns()
    explicit_bytes = json.dumps(
        {**formation_record, "witness_custody_mode": "carried"},
        sort_keys=True,
        separators=(",", ":"),
    ).encode()
    explicit_formation_ns = time.perf_counter_ns() - formation_start

    reuse_start = time.perf_counter_ns()
    fresh_fields = ["source", "ordered_history", "binding_node"]
    fresh_full = (1 << len(fresh_fields)) - 1
    reuse = {
        "fields": fresh_fields,
        "omitted_complete": classify("omitted", fresh_full, 28, len(fresh_fields)),
        "carried_complete": classify("carried", fresh_full, 28, len(fresh_fields)),
        "carried_missing_history": classify("carried", fresh_full ^ 2, 28, len(fresh_fields)),
        "reconstructed_ready_but_unexecuted": classify("reconstructed", 0, 31, len(fresh_fields)),
        "altered_order": classify("carried", fresh_full, 12, len(fresh_fields)),
    }
    assert reuse["omitted_complete"] == "Unknown/CustodyModeOmitted"
    assert reuse["carried_complete"] == "StructurallyReady/CarriedFieldsPresent"
    assert reuse["carried_missing_history"] == "CertificateObstruction/MissingCarriedFields"
    assert reuse["reconstructed_ready_but_unexecuted"] == "Unknown/NativeReconstructionNotRun"
    assert reuse["altered_order"] == "Refused/NoncommutativeOrderMismatch"
    reuse_ns = time.perf_counter_ns() - reuse_start

    representative_key = (full, 28)
    outcome = {
        "schema": "adva.research.witness-custody-mode.outcome.v0",
        "status": "PassedFiniteCustodyDiscrimination",
        "proposed_word": {
            "name": "witness-custody mode",
            "state": "Proposed",
            "role": "select exactly one obligation family before semantic certificate validation",
            "input": "request/checker pins, ordered field carrier or reconstruction recipe/inputs, and an explicit carried|reconstructed tag",
            "output_relation": "a typed structural status and remaining native validation obligation",
            "applicability": "a witness may be supplied as fields or produced by a pinned reconstruction route",
            "witness": "98,304-record exhaustive finite comparison plus a fresh three-field reuse",
            "refusal_conditions": [
                "mode omitted",
                "carried and reconstructed members mixed",
                "required carried field absent",
                "recipe or reconstruction inputs absent",
                "request/checker pin mismatch",
                "noncommutative order changed",
            ],
            "expansion": "branch on the tag, replay only that branch's structural checks, then retain semantic/native residuals",
            "residual": "no native field codec or reconstruction route was implemented or executed",
        },
        "comparison": {
            "candidate_count": candidates,
            "mode_free_projection_classes": len(baseline),
            "mode_free_mixed_status_classes": len(mixed_baseline),
            "explicit_mode_classes": len(explicit),
            "explicit_mode_mixed_status_classes": len(mixed_explicit),
            "representative_mode_free_projection": {
                "field_mask": representative_key[0],
                "auxiliary": representative_key[1],
                "statuses": sorted(baseline[representative_key]),
            },
            "status_counts": dict(sorted(status_counts.items())),
        },
        "controls": controls,
        "reuse": reuse,
        "cost": {
            "routes": 1,
            "candidates": candidates,
            "enumeration_ns": enumeration_ns,
            "verification_ns": verification_ns,
            "baseline_formation_ns": baseline_formation_ns,
            "explicit_formation_ns": explicit_formation_ns,
            "baseline_bytes": len(baseline_bytes),
            "explicit_bytes": len(explicit_bytes),
            "word_byte_delta": len(explicit_bytes) - len(baseline_bytes),
            "reuse_ns": reuse_ns,
            "whole_run_before_serialization_ns": time.perf_counter_ns() - start,
            "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "native_executions": 0,
            "implementation_correction_replays": 0,
        },
        "claim_boundaries": {
            "structural_model_only": True,
            "word_promoted": False,
            "native_adapter": False,
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
    outcome_sha = hashlib.sha256(encoded.encode()).hexdigest()
    print(encoded, end="")
    print("OUTCOME_SHA256 " + outcome_sha, file=__import__("sys").stderr)


if __name__ == "__main__":
    main()

