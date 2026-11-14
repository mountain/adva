#!/usr/bin/env python3
"""Bounded dependency-separation model for the serialized leaf request."""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import resource
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONTRACT_PATH = HERE / "contract.json"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_unique_json(data: bytes, label: str) -> object:
    def unique(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{label}: duplicate key {key}")
            result[key] = value
        return result

    return json.loads(data, object_pairs_hook=unique)


def function_body(source: str, name: str) -> str:
    marker = f"fn {name}("
    start = source.index(marker)
    brace = source.index("{", start)
    depth = 0
    for index in range(brace, len(source)):
        char = source[index]
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return source[brace + 1 : index]
    raise ValueError(f"unclosed function {name}")


def certificate_fields(source: str) -> list[str]:
    marker = "struct ResearchCertificate {"
    start = source.index(marker) + len(marker)
    end = source.index("\n}", start)
    fields = []
    for line in source[start:end].splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("//"):
            fields.append(stripped.split(":", 1)[0])
    return fields


def used_fields(body: str, declared: set[str]) -> list[str]:
    fields = set()
    token = "certificate."
    cursor = 0
    while True:
        try:
            cursor = body.index(token, cursor) + len(token)
        except ValueError:
            break
        end = cursor
        while end < len(body) and (body[end].isalnum() or body[end] == "_"):
            end += 1
        candidate = body[cursor:end]
        if candidate in declared:
            fields.add(candidate)
        cursor = end
    return sorted(fields)


def apply_limits(contract: dict[str, object]) -> None:
    budget = contract["budget"]
    assert isinstance(budget, dict)
    resource.setrlimit(resource.RLIMIT_CPU, (budget["cpu_seconds"], budget["cpu_seconds"]))
    resource.setrlimit(
        resource.RLIMIT_AS,
        (budget["address_space_bytes"], budget["address_space_bytes"]),
    )
    resource.setrlimit(resource.RLIMIT_FSIZE, (budget["file_bytes"], budget["file_bytes"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    started = time.perf_counter_ns()
    contract_bytes = CONTRACT_PATH.read_bytes()
    contract = load_unique_json(contract_bytes, "contract")
    assert isinstance(contract, dict)
    apply_limits(contract)

    inputs: dict[str, dict[str, object]] = {}
    loaded: dict[str, bytes] = {}
    objects = contract["objects"]
    assert isinstance(objects, dict)
    for name, specification in objects.items():
        assert isinstance(specification, dict)
        path = ROOT / str(specification["path"])
        data = path.read_bytes()
        observed = sha256(data)
        if observed != specification["sha256"]:
            raise ValueError(f"{name}: sha256 mismatch")
        loaded[name] = data
        inputs[name] = {
            "path": specification["path"],
            "bytes": len(data),
            "sha256": observed,
        }

    request = load_unique_json(loaded["canonical_request"], "canonical request")
    legacy_contract = load_unique_json(loaded["legacy_contract"], "legacy contract")
    merged_contract = load_unique_json(loaded["merged_relation_contract"], "merged contract")
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
        raise ValueError("canonical occurrence map is not a singleton")
    if set(mapping[0]) != {"source", "target"}:
        raise ValueError("canonical occurrence map endpoint roles changed")

    rust_source = loaded["rust_certificate_source"].decode("utf-8")
    declared_fields = certificate_fields(rust_source)
    expected_fields = [
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
    if declared_fields != expected_fields:
        raise ValueError("ResearchCertificate field set changed")

    declared_set = set(declared_fields)
    check_fields = used_fields(function_body(rust_source, "check"), declared_set)
    if check_fields != sorted(expected_fields):
        raise ValueError("Rust check dependency set changed")
    pair_fields = used_fields(
        function_body(rust_source, "only_dynamic_pair"), declared_set
    )
    if pair_fields != ["occurrence_map"]:
        raise ValueError("serializer certificate dependency changed")
    serializer = function_body(rust_source, "serialized_leaf_request")
    if "only_dynamic_pair(certificate)" not in serializer:
        raise ValueError("serializer no longer uses only_dynamic_pair")
    if used_fields(serializer, declared_set):
        raise ValueError("serializer gained a direct certificate field read")

    relation_fields = {
        "selected_relation",
        "relation_profile_id",
        "relation_profile_sha256",
        "quantifier_and_domain",
        "claim_sha256",
        "evidence_reference",
        "certificate",
        "graft_trace",
    }
    explicit_relation_fields = sorted(set(request) & relation_fields)
    if explicit_relation_fields:
        raise ValueError("canonical request unexpectedly carries relation evidence")
    if "existing native Rust certificate" not in str(legacy_contract["question"]):
        raise ValueError("legacy target relation wording changed")
    variants = merged_contract["types"]["SelectedRelation"]["variants"]
    if set(variants) != {"PinnedPairMembershipV1", "CertifiedRelationV1"}:
        raise ValueError("merged relation alternatives changed")

    synthetic = copy.deepcopy(request)
    synthetic["profile"] = "adva.research.synthetic-projection-reuse.v0"
    synthetic["native_occurrence_map"][0]["source"]["context"] = "fresh/source"
    synthetic["native_occurrence_map"][0]["target"]["context"] = "fresh/residual"
    instances = [
        {
            "id": "canonical-request",
            "projection_sha256": sha256(loaded["canonical_request"]),
            "native_status": "FrozenCanonicalBytes",
        },
        {
            "id": "fresh-coordinate-reuse",
            "projection_sha256": sha256(
                json.dumps(synthetic, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ),
            "native_status": "SyntheticDependencyModelOnly",
        },
    ]

    candidates = 0
    for instance in instances:
        valid = 0
        invalid = 0
        projection_digests = set()
        for bits in itertools.product((False, True), repeat=len(expected_fields)):
            candidates += 1
            projection_digests.add(instance["projection_sha256"])
            if all(bits):
                valid += 1
            else:
                invalid += 1
        instance.update(
            {
                "candidate_completions": valid + invalid,
                "valid_completions": valid,
                "invalid_completions": invalid,
                "distinct_request_projections": len(projection_digests),
                "valid_and_invalid_share_projection": valid > 0 and invalid > 0,
            }
        )

    limit = contract["budget"]["candidate_limit"]
    if candidates > limit:
        raise ValueError("candidate budget exceeded")
    if any(
        instance["valid_completions"] != 1
        or instance["invalid_completions"] != 1023
        or instance["distinct_request_projections"] != 1
        or not instance["valid_and_invalid_share_projection"]
        for instance in instances
    ):
        raise ValueError("projection separation expectation failed")

    evaluated = time.perf_counter_ns()
    outcome: dict[str, object] = {
        "schema": "adva.research.request-relation-projection-outcome.v0",
        "status": "ProjectionUnderdeterminesCertificateWithinFrozenModel",
        "base_commit": contract["base_commit"],
        "inputs": inputs,
        "source_dependency": {
            "certificate_fields_declared": declared_fields,
            "certificate_fields_checked": check_fields,
            "serializer_certificate_fields": pair_fields,
            "occurrence_map_projection": "exactly one dynamic source/target pair; complete map coverage is not serialized",
            "request_root_fields": sorted(request),
            "explicit_relation_or_witness_fields": explicit_relation_fields,
        },
        "target_decision": {
            "legacy_intended_relation": "LegacyResearchNativeInputBindingCertificateV0",
            "request_bytes_alone_support": "PinnedPairMembershipV1",
            "certified_relation_without_additional_witness": "Unknown/WitnessNotCarried",
            "reason": "The legacy contract requires the existing native certificate, but the request serializer projects only one dynamic occurrence pair from that certificate while the Rust checker consumes all ten certificate fields plus native compilation/graft artifacts.",
        },
        "finite_model": {
            "dimensions": expected_fields,
            "instances": instances,
            "candidates_enumerated": candidates,
            "candidate_limit": limit,
        },
        "cost": {
            "input_reads": 4,
            "input_bytes": sum(item["bytes"] for item in inputs.values()),
            "opaque_request_reads": 1,
            "embedded_diagram_json_parses": 0,
            "native_executions": 0,
            "evaluation_ns_before_serialization": evaluated - started,
            "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "correction_replays": 0,
        },
        "residuals": contract["residuals"],
        "new_words": [],
    }
    encoded = (json.dumps(outcome, indent=2, sort_keys=True) + "\n").encode("utf-8")
    outcome["cost"]["serialized_bytes_without_final_measurement"] = len(encoded)
    encoded = (json.dumps(outcome, indent=2, sort_keys=True) + "\n").encode("utf-8")
    output_path = Path(args.output)
    output_path.write_bytes(encoded)
    print(
        json.dumps(
            {
                "status": outcome["status"],
                "candidates": candidates,
                "output": str(output_path),
                "sha256": sha256(encoded),
                "bytes": len(encoded),
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
