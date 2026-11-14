#!/usr/bin/env python3
"""Enumerate a pinned finite request/certificate projection model."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import re
import resource
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONTRACT_PATH = HERE / "contract.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def unique_json(data: bytes, label: str) -> object:
    def reject_duplicates(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{label}: duplicate key {key}")
            result[key] = value
        return result

    return json.loads(data, object_pairs_hook=reject_duplicates)


def function_body(source: str, name: str) -> str:
    marker = f"fn {name}("
    start = source.index(marker)
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[opening + 1 : index]
    raise ValueError(f"unclosed function: {name}")


def declared_certificate_fields(source: str) -> list[str]:
    marker = "struct ResearchCertificate {"
    start = source.index(marker) + len(marker)
    end = source.index("\n}", start)
    result = []
    for line in source[start:end].splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("//"):
            result.append(stripped.split(":", 1)[0])
    return result


def certificate_member_fields(body: str, declared: set[str]) -> list[str]:
    pattern = re.compile(r"\bcertificate\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)")
    return sorted(
        {
            match.group(1)
            for match in pattern.finditer(body)
            if match.group(1) in declared
        }
    )


def apply_limits(contract: dict[str, object]) -> None:
    budget = contract["budget"]
    assert isinstance(budget, dict)
    resource.setrlimit(
        resource.RLIMIT_CPU,
        (int(budget["cpu_seconds"]), int(budget["cpu_seconds"])),
    )
    resource.setrlimit(
        resource.RLIMIT_AS,
        (int(budget["address_space_bytes"]), int(budget["address_space_bytes"])),
    )
    resource.setrlimit(
        resource.RLIMIT_FSIZE,
        (int(budget["file_bytes"]), int(budget["file_bytes"])),
    )


def fixed_size_json(value: dict[str, object]) -> bytes:
    cost = value["cost"]
    assert isinstance(cost, dict)
    cost["final_output_bytes"] = 0
    for _ in range(8):
        encoded = (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()
        if cost["final_output_bytes"] == len(encoded):
            return encoded
        cost["final_output_bytes"] = len(encoded)
    raise ValueError("final byte count did not reach a fixed point")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    started_ns = time.perf_counter_ns()

    contract_bytes = CONTRACT_PATH.read_bytes()
    contract = unique_json(contract_bytes, "contract")
    assert isinstance(contract, dict)
    apply_limits(contract)

    objects = contract["objects"]
    assert isinstance(objects, dict)
    loaded: dict[str, bytes] = {}
    input_receipts: dict[str, dict[str, object]] = {}
    for name, specification in objects.items():
        assert isinstance(specification, dict)
        data = (ROOT / str(specification["path"])).read_bytes()
        digest = sha256(data)
        if digest != specification["sha256"]:
            raise ValueError(f"{name}: sha256 mismatch")
        loaded[name] = data
        input_receipts[name] = {
            "path": specification["path"],
            "bytes": len(data),
            "sha256": digest,
        }

    request = unique_json(loaded["canonical_request"], "canonical request")
    legacy_contract = unique_json(loaded["legacy_contract"], "legacy contract")
    merged_contract = unique_json(
        loaded["merged_relation_contract"], "merged relation contract"
    )
    assert isinstance(request, dict)
    assert isinstance(legacy_contract, dict)
    assert isinstance(merged_contract, dict)

    expected_root = {
        "external_leaf",
        "native_occurrence_map",
        "profile",
        "residual_diagram_json",
        "source_diagram_json",
    }
    if set(request) != expected_root:
        raise ValueError("canonical request root fields changed")
    mapping = request["native_occurrence_map"]
    if not isinstance(mapping, list) or len(mapping) != 1:
        raise ValueError("canonical request no longer has one occurrence pair")
    if not isinstance(mapping[0], dict) or set(mapping[0]) != {"source", "target"}:
        raise ValueError("canonical occurrence roles changed")

    dimensions = contract["candidate_grammar"]["dimensions"]
    assert isinstance(dimensions, list)
    source = loaded["rust_certificate_source"].decode()
    declared = declared_certificate_fields(source)
    if declared != dimensions:
        raise ValueError("ResearchCertificate declaration changed")
    declared_set = set(declared)
    strong_fields = certificate_member_fields(function_body(source, "check"), declared_set)
    if strong_fields != sorted(dimensions):
        raise ValueError("strong checker field dependency changed")
    pair_fields = certificate_member_fields(
        function_body(source, "only_dynamic_pair"), declared_set
    )
    if pair_fields != ["occurrence_map"]:
        raise ValueError("only_dynamic_pair dependency changed")
    serializer = function_body(source, "serialized_leaf_request")
    if "only_dynamic_pair(certificate)" not in serializer:
        raise ValueError("serializer no longer calls only_dynamic_pair")
    if certificate_member_fields(serializer, declared_set):
        raise ValueError("serializer gained a direct certificate field read")
    checker_body = function_body(source, "check")
    if "source.graft_trace" not in checker_body or "residual.graft_trace" not in checker_body:
        raise ValueError("strong checker graft dependency changed")

    if "existing native Rust certificate" not in str(legacy_contract["question"]):
        raise ValueError("legacy target wording changed")
    variants = merged_contract["types"]["SelectedRelation"]["variants"]
    if set(variants) != {"PinnedPairMembershipV1", "CertifiedRelationV1"}:
        raise ValueError("merged relation alternatives changed")
    explicit_witness_fields = sorted(
        set(request)
        & {
            "certificate",
            "claim_sha256",
            "evidence_reference",
            "graft_trace",
            "quantifier_and_domain",
            "relation_profile_id",
            "relation_profile_sha256",
            "selected_relation",
        }
    )
    if explicit_witness_fields:
        raise ValueError("canonical request gained an explicit relation witness")

    synthetic = copy.deepcopy(request)
    synthetic["profile"] = "adva.research.synthetic-projection-reuse.v1"
    synthetic["native_occurrence_map"][0]["source"]["context"] = "fresh/source"
    synthetic["native_occurrence_map"][0]["target"]["context"] = "fresh/residual"
    synthetic_bytes = json.dumps(
        synthetic, sort_keys=True, separators=(",", ":")
    ).encode()
    instances = [
        {
            "id": "canonical-request",
            "projection_sha256": sha256(loaded["canonical_request"]),
            "scope": "FrozenCanonicalBytes",
        },
        {
            "id": "fresh-coordinate-reuse",
            "projection_sha256": sha256(synthetic_bytes),
            "scope": "SyntheticDependencyModelOnly",
        },
    ]

    candidate_count = 0
    for instance in instances:
        projection_digests: set[str] = set()
        valid_count = 0
        invalid_count = 0
        for values in itertools.product((False, True), repeat=len(dimensions)):
            candidate_count += 1
            completion = dict(zip(dimensions, values, strict=True))
            projection_digests.add(str(instance["projection_sha256"]))
            if all(completion.values()):
                valid_count += 1
            else:
                invalid_count += 1
        instance.update(
            {
                "candidate_completions": valid_count + invalid_count,
                "valid_completions": valid_count,
                "invalid_completions": invalid_count,
                "distinct_request_projections": len(projection_digests),
                "valid_and_invalid_share_projection": valid_count == 1
                and invalid_count > 0
                and len(projection_digests) == 1,
            }
        )

    limit = int(contract["budget"]["candidate_limit"])
    if candidate_count > limit:
        raise ValueError("candidate limit exceeded")
    for instance in instances:
        if (
            instance["candidate_completions"] != 1024
            or instance["valid_completions"] != 1
            or instance["invalid_completions"] != 1023
            or instance["distinct_request_projections"] != 1
            or not instance["valid_and_invalid_share_projection"]
        ):
            raise ValueError("finite projection expectation failed")

    evaluated_ns = time.perf_counter_ns()
    outcome: dict[str, object] = {
        "schema": "adva.research.request-relation-projection-outcome.v1",
        "status": "ProjectionUnderdeterminesCertificateWithinFrozenFieldModel",
        "base_commit": contract["base_commit"],
        "predecessor": contract["predecessor"],
        "inputs": input_receipts,
        "source_dependency": {
            "certificate_fields_declared": declared,
            "certificate_fields_checked": strong_fields,
            "serializer_certificate_fields": pair_fields,
            "occurrence_map_projection": "One unique dynamic pair; full occurrence-map coverage is not emitted.",
            "request_root_fields": sorted(request),
            "explicit_relation_witness_fields": explicit_witness_fields,
            "strong_checker_uses_native_graft_material": True,
        },
        "finite_model": {
            "dimensions": dimensions,
            "instances": instances,
            "candidates_enumerated": candidate_count,
            "candidate_limit": limit,
        },
        "target_decision": {
            "legacy_target": "LegacyResearchNativeInputBindingCertificateV0",
            "request_projection_directly_carries": "PinnedPairMembershipV1 inputs",
            "strong_relation_from_request_bytes_alone": "UnderdeterminedWithinFrozenFieldModel",
            "required_continuation": "Carry an applicable versioned witness or pin a native reconstruction route; otherwise remain Unknown. Do not silently downgrade the legacy target to pair membership.",
        },
        "cost": {
            "input_files_read": 4,
            "input_bytes": sum(item["bytes"] for item in input_receipts.values()),
            "canonical_request_reads": 1,
            "embedded_diagram_json_parses": 0,
            "native_executions": 0,
            "evaluation_ns_before_serialization": evaluated_ns - started_ns,
            "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "correction_replays": 0,
            "output_write_time": "unmeasured",
        },
        "new_words": [],
        "residuals": contract["residuals"],
    }
    serialization_started = time.perf_counter_ns()
    measured_payload = (json.dumps(outcome, indent=2, sort_keys=True) + "\n").encode()
    serialization_ns = time.perf_counter_ns() - serialization_started
    cost = outcome["cost"]
    assert isinstance(cost, dict)
    cost["measured_payload_serialization_ns"] = serialization_ns
    cost["measured_payload_bytes"] = len(measured_payload)
    encoded = fixed_size_json(outcome)
    output = Path(args.output)
    output.write_bytes(encoded)
    print(
        json.dumps(
            {
                "bytes": len(encoded),
                "candidates": candidate_count,
                "output": str(output),
                "sha256": sha256(encoded),
                "status": outcome["status"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise
