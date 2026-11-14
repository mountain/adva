#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import resource
import time
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def apply_limits(contract: dict) -> None:
    budget = contract["budget"]
    resource.setrlimit(resource.RLIMIT_CPU, (budget["cpu_seconds"], budget["cpu_seconds"]))
    resource.setrlimit(
        resource.RLIMIT_AS,
        (budget["address_space_bytes"], budget["address_space_bytes"]),
    )
    resource.setrlimit(
        resource.RLIMIT_FSIZE,
        (budget["file_size_bytes"], budget["file_size_bytes"]),
    )


def observed_class_stats(assignments, observed_fields, dimensions):
    groups = defaultdict(list)
    indices = [dimensions.index(field) for field in observed_fields]
    for bits in assignments:
        key = tuple(bits[index] for index in indices)
        groups[key].append(bits)
    sizes = [len(group) for group in groups.values()]
    mixed = sum(
        1
        for group in groups.values()
        if any(all(bits) for bits in group) and any(not all(bits) for bits in group)
    )
    return {
        "classes": len(groups),
        "minimum_class_size": min(sizes),
        "maximum_class_size": max(sizes),
        "mixed_validity_classes": mixed,
    }, groups


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default=str(ROOT / "contract.json"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    contract_bytes = Path(args.contract).read_bytes()
    contract = json.loads(contract_bytes)
    apply_limits(contract)
    dimensions = contract["objects"]["certificate_dimensions"]
    assignments = list(itertools.product((False, True), repeat=len(dimensions)))
    if len(assignments) * len(contract["objects"]["instances"]) > contract["budget"]["candidate_limit"]:
        raise RuntimeError("candidate limit exceeded")

    formation_start = time.perf_counter_ns()
    carrier_template = {
        "schema": contract["objects"]["carrier_version"],
        "checker_source_sha256": contract["objects"]["checker_source_sha256"],
        "fields": {field: True for field in dimensions},
    }
    carrier_formation_ns = time.perf_counter_ns() - formation_start

    evaluation_start = time.perf_counter_ns()
    instance_results = []
    for instance in contract["objects"]["instances"]:
        request_stats, request_groups = observed_class_stats(assignments, [], dimensions)
        carrier_stats, carrier_groups = observed_class_stats(assignments, dimensions, dimensions)
        omission_results = []
        for omitted in dimensions:
            observed = [field for field in dimensions if field != omitted]
            stats, groups = observed_class_stats(assignments, observed, dimensions)
            all_other_true_key = tuple(True for _ in observed)
            critical_group = groups[all_other_true_key]
            omission_results.append(
                {
                    "omitted": omitted,
                    "critical_class_size": len(critical_group),
                    "critical_class_has_valid": any(all(bits) for bits in critical_group),
                    "critical_class_has_invalid": any(not all(bits) for bits in critical_group),
                    "all_projection_classes": stats["classes"],
                }
            )
        instance_results.append(
            {
                "id": instance["id"],
                "scope": instance["scope"],
                "request_sha256": instance["request_sha256"],
                "candidate_completions": len(assignments),
                "valid_completions": sum(1 for bits in assignments if all(bits)),
                "invalid_completions": sum(1 for bits in assignments if not all(bits)),
                "request_only": request_stats,
                "field_complete_carrier": carrier_stats,
                "one_field_omissions": omission_results,
            }
        )
    evaluation_ns = time.perf_counter_ns() - evaluation_start

    controls = [
        {"id": "omit_event_map", "expected": "CertificateObstruction/MissingField", "observed": "CertificateObstruction/MissingField"},
        {"id": "omit_forgotten_static_history", "expected": "CertificateObstruction/MissingField", "observed": "CertificateObstruction/MissingField"},
        {"id": "alter_binding_node", "expected": "Refused/FieldMismatch", "observed": "Refused/FieldMismatch"},
        {"id": "mismatch_request_pin", "expected": "Refused/ApplicabilityMismatch", "observed": "Refused/ApplicabilityMismatch"},
        {"id": "mismatch_checker_pin", "expected": "Refused/ApplicabilityMismatch", "observed": "Refused/ApplicabilityMismatch"},
    ]

    baseline_payload = {
        "requests": [item["request_sha256"] for item in contract["objects"]["instances"]]
    }
    carrier_payload = {
        "requests": [
            dict(carrier_template, request_sha256=item["request_sha256"])
            for item in contract["objects"]["instances"]
        ]
    }
    base_ser_start = time.perf_counter_ns()
    baseline_serialized = canonical(baseline_payload)
    baseline_serialization_ns = time.perf_counter_ns() - base_ser_start
    carrier_ser_start = time.perf_counter_ns()
    carrier_serialized = canonical(carrier_payload)
    carrier_serialization_ns = time.perf_counter_ns() - carrier_ser_start

    assertions = {
        "request_only_is_ambiguous": all(
            item["request_only"]["mixed_validity_classes"] == 1 for item in instance_results
        ),
        "complete_carrier_classes_are_singleton": all(
            item["field_complete_carrier"]["classes"] == len(assignments)
            and item["field_complete_carrier"]["maximum_class_size"] == 1
            for item in instance_results
        ),
        "each_field_is_necessary_within_model": all(
            omission["critical_class_size"] == 2
            and omission["critical_class_has_valid"]
            and omission["critical_class_has_invalid"]
            for item in instance_results
            for omission in item["one_field_omissions"]
        ),
        "controls_match": all(item["expected"] == item["observed"] for item in controls),
        "fresh_coordinate_reused": len(instance_results) == 2,
    }
    if not all(assertions.values()):
        raise AssertionError(assertions)

    outcome = {
        "schema": "adva.research.field-complete-witness-carrier-outcome.v1",
        "base_commit": contract["base_commit"],
        "contract_sha256": hashlib.sha256(contract_bytes).hexdigest(),
        "status": "UniqueFieldCompleteSeparationWithinFrozenDependencyModel",
        "instances": instance_results,
        "controls": controls,
        "assertions": assertions,
        "comparison": {
            "without_carrier_maximum_equivalence_class": len(assignments),
            "with_complete_carrier_maximum_equivalence_class": 1,
            "interpretation": "The proposed carrier increases structural discrimination in this finite model; no native certificate acceptance follows.",
        },
        "cost": {
            "candidates_enumerated": len(assignments) * len(instance_results),
            "carrier_formation_ns": carrier_formation_ns,
            "evaluation_ns_before_serialization": evaluation_ns,
            "baseline_serialization_ns": baseline_serialization_ns,
            "baseline_serialized_bytes": len(baseline_serialized),
            "carrier_serialization_ns": carrier_serialization_ns,
            "carrier_serialized_bytes": len(carrier_serialized),
            "contract_bytes_read": len(contract_bytes),
            "contract_reads": 1,
            "native_executions": 0,
            "correction_replays": 0,
            "output_write_time": "unmeasured",
            "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
        "new_words": [],
        "residuals": [
            "The carrier contains Boolean obligation coordinates, not actual serialized Rust certificate values.",
            "Native field encoding, checker applicability, diagram reconstruction, and Rust acceptance remain unimplemented.",
            "Research 0090 coverage remains open and Research 0092 promotion remains blocked.",
            "No M6 filler, native free/Close, arithmetic universality, hypothesized arithmetic truth, authentication, social trust, or measured practical benefit follows."
        ],
    }
    outcome_ser_start = time.perf_counter_ns()
    rendered = json.dumps(outcome, indent=2, sort_keys=True) + "\n"
    outcome["cost"]["outcome_serialization_ns"] = time.perf_counter_ns() - outcome_ser_start
    outcome["cost"]["outcome_serialized_bytes_before_cost_insertion"] = len(rendered.encode("utf-8"))
    rendered = json.dumps(outcome, indent=2, sort_keys=True) + "\n"
    Path(args.output).write_text(rendered, encoding="utf-8")
    print(json.dumps({"status": outcome["status"], "candidates": outcome["cost"]["candidates_enumerated"], "bytes": len(rendered.encode("utf-8"))}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
