#!/usr/bin/env python3
"""Bounded source audit for an explicit ResearchCertificate wire codec."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import resource
import time
from pathlib import Path


EXPECTED_SHA256 = "391c6eef4df0f63a7cbd8d19dbc0967fd717ef26b3a70342aaa19c5e4c90c8bb"
EXPECTED_FIELDS = [
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
EXPECTED_REQUEST_KEYS = [
    "external_leaf",
    "native_occurrence_map",
    "profile",
    "residual_diagram_json",
    "source_diagram_json",
]


def line_of(text: str, needle: str) -> int | None:
    position = text.find(needle)
    return None if position < 0 else text.count("\n", 0, position) + 1


def function_slice(text: str, name: str, next_marker: str) -> str:
    start = text.find(f"fn {name}(")
    end = text.find(next_marker, start)
    if start < 0 or end < 0:
        raise ValueError(f"missing function boundary for {name}")
    return text[start:end]


def audit(text: str) -> dict:
    declaration_matches = list(
        re.finditer(
            r"#\[derive\((?P<derive>[^)]*)\)\]\s*struct ResearchCertificate\s*\{(?P<body>.*?)\n\}",
            text,
            flags=re.S,
        )
    )
    if len(declaration_matches) != 1:
        raise ValueError(f"expected one ResearchCertificate declaration, found {len(declaration_matches)}")
    declaration = declaration_matches[0]
    fields = re.findall(r"^\s*([a-z_][a-z0-9_]*)\s*:\s*(.*?)\s*,\s*$", declaration.group("body"), re.M)
    field_names = [name for name, _type in fields]
    serializer = function_slice(text, "serialized_leaf_request", "fn receive_serialized_leaf_request(")
    receiver = function_slice(text, "receive_serialized_leaf_request", "#[test]")
    root_match = re.search(r"let expected_root = BTreeSet::from\(\[(.*?)\]\);", receiver, re.S)
    if not root_match:
        raise ValueError("missing accepted request-root declaration")
    root_keys = re.findall(r'"([a-z_]+)"', root_match.group(1))
    derives = {part.strip() for part in declaration.group("derive").split(",")}
    explicit_serialize = bool(
        re.search(r"impl(?:<[^>]*>)?\s+(?:serde::)?Serialize\s+for\s+ResearchCertificate", text)
        or re.search(r"serde_json::to_(?:string|value)\s*\(\s*certificate\s*\)", text)
    )
    explicit_deserialize = bool(
        re.search(r"impl(?:<[^>]*>)?\s+(?:serde::)?Deserialize[^\s]*\s+for\s+ResearchCertificate", text)
        or re.search(r"serde_json::from_(?:str|value)[^;]*ResearchCertificate", text)
    )
    reconstruction = "ResearchCertificate {" in receiver
    external_certificate_parameter = bool(
        re.search(r"certificate\s*:\s*&ResearchCertificate", receiver)
    )
    field_root_membership = {field: field in root_keys for field in field_names}
    complete = (
        field_names == EXPECTED_FIELDS
        and all(field_root_membership.values())
        and ("Serialize" in derives or explicit_serialize)
        and ("Deserialize" in derives or explicit_deserialize)
        and reconstruction
        and not external_certificate_parameter
    )
    return {
        "declaration_count": len(declaration_matches),
        "fields": [{"name": name, "rust_type": rust_type.strip()} for name, rust_type in fields],
        "derives": sorted(derives),
        "has_serialize_direction": "Serialize" in derives or explicit_serialize,
        "has_deserialize_direction": "Deserialize" in derives or explicit_deserialize,
        "has_receiver_reconstruction": reconstruction,
        "receiver_requires_external_certificate": external_certificate_parameter,
        "accepted_request_root_keys": root_keys,
        "field_root_membership": field_root_membership,
        "serializer_projects_one_dynamic_pair": "only_dynamic_pair(certificate)" in serializer,
        "receiver_rechecks_one_dynamic_pair_from_external_certificate": "only_dynamic_pair(certificate)" in receiver,
        "receiver_delegates_external_certificate_to_receive": "receive(source, residual, certificate, request, structural_work)" in receiver,
        "classification": "PassedExplicitFieldCompleteEncodingShape" if complete else "Unknown/NativeEncodingAbsentAtPinnedSourceSurface",
        "line_witnesses": {
            "certificate_declaration": line_of(text, "struct ResearchCertificate"),
            "serializer": line_of(text, "fn serialized_leaf_request("),
            "receiver": line_of(text, "fn receive_serialized_leaf_request("),
            "accepted_root": line_of(text, "let expected_root = BTreeSet::from(["),
            "external_certificate_delegation": line_of(text, "receive(source, residual, certificate, request, structural_work)"),
        },
    }


def positive_control() -> str:
    fields = "\n".join(f"    {name}: Value," for name in EXPECTED_FIELDS)
    keys = "\n".join(f'        "{name}",' for name in EXPECTED_FIELDS)
    constructor = "\n".join(f"        {name}: value[{name!r}].clone()," for name in EXPECTED_FIELDS)
    return f'''use serde::{{Deserialize, Serialize}};
use serde_json::Value;
#[derive(Clone, Debug, Eq, PartialEq, Serialize, Deserialize)]
struct ResearchCertificate {{
{fields}
}}
fn serialized_leaf_request(certificate: &ResearchCertificate) -> String {{
    serde_json::to_value(certificate).unwrap().to_string()
}}
fn receive_serialized_leaf_request(encoded: &str) -> ResearchCertificate {{
    let value: Value = serde_json::from_str(encoded).unwrap();
    let expected_root = BTreeSet::from([
{keys}
    ]);
    ResearchCertificate {{
{constructor}
    }}
}}
#[test]
fn control() {{}}
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=Path(__file__).parents[1] / "native_input_binding_certificate" / "native_input_binding_certificate.rs")
    args = parser.parse_args()

    started = time.perf_counter_ns()
    source_started = time.perf_counter_ns()
    source = args.source.read_text(encoding="utf-8")
    source_ns = time.perf_counter_ns() - source_started
    source_sha = hashlib.sha256(source.encode()).hexdigest()
    if source_sha != EXPECTED_SHA256:
        raise SystemExit(f"refused: source hash {source_sha} != {EXPECTED_SHA256}")

    actual_started = time.perf_counter_ns()
    actual = audit(source)
    actual_ns = time.perf_counter_ns() - actual_started

    control_formation_started = time.perf_counter_ns()
    control_source = positive_control()
    control_formation_ns = time.perf_counter_ns() - control_formation_started
    control_started = time.perf_counter_ns()
    control = audit(control_source)
    control_ns = time.perf_counter_ns() - control_started

    verification_started = time.perf_counter_ns()
    assert [field["name"] for field in actual["fields"]] == EXPECTED_FIELDS
    assert actual["accepted_request_root_keys"] == EXPECTED_REQUEST_KEYS
    assert actual["classification"] == "Unknown/NativeEncodingAbsentAtPinnedSourceSurface"
    assert not any(actual["field_root_membership"].values())
    assert not actual["has_serialize_direction"]
    assert not actual["has_deserialize_direction"]
    assert not actual["has_receiver_reconstruction"]
    assert actual["receiver_requires_external_certificate"]
    assert actual["serializer_projects_one_dynamic_pair"]
    assert actual["receiver_rechecks_one_dynamic_pair_from_external_certificate"]
    assert actual["receiver_delegates_external_certificate_to_receive"]
    assert control["classification"] == "PassedExplicitFieldCompleteEncodingShape"
    verification_ns = time.perf_counter_ns() - verification_started

    field_status = {}
    for name in EXPECTED_FIELDS:
        if name in {"source_snapshot", "residual_snapshot"}:
            field_status[name] = "diagram bytes are present and compared, but no certificate field is reconstructed"
        elif name == "occurrence_map":
            field_status[name] = "one dynamic pair is projected and rechecked; the full ordered map is not carried"
        else:
            field_status[name] = "no explicit certificate field member or reconstruction on the selected wire surface"

    outcome = {
        "schema": "adva.research.native-certificate-encoding-audit.outcome.v0",
        "status": actual["classification"],
        "scope": "one pinned Rust source file; static source audit only",
        "source": {
            "path": str(args.source),
            "sha256": source_sha,
            "bytes": len(source.encode()),
            "lines": len(source.splitlines()),
        },
        "actual": actual,
        "field_status": field_status,
        "control": {
            "purpose": "fresh synthetic field-complete shape; parser discrimination only, not a compiling adapter",
            "classification": control["classification"],
            "fields": len(control["fields"]),
            "accepted_root_fields": sum(control["field_root_membership"].values()),
            "receiver_requires_external_certificate": control["receiver_requires_external_certificate"],
        },
        "cost": {
            "routes": 1,
            "selected_sources": 1,
            "structural_controls": 1,
            "candidates": 2,
            "source_lines_examined": len(source.splitlines()),
            "source_read_ns": source_ns,
            "actual_audit_ns": actual_ns,
            "control_formation_ns": control_formation_ns,
            "control_audit_ns": control_ns,
            "verification_ns": verification_ns,
            "whole_run_before_serialization_ns": time.perf_counter_ns() - started,
            "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "native_executions": 0,
            "implementation_correction_replays": 1,
            "address_space_limit": "not installed",
        },
        "residuals": [
            "No explicit native lossless certificate codec or decoder exists on the pinned file surface.",
            "A separately versioned carrier or pinned native reconstruction route remains to be designed and executed.",
            "Repository-wide codec absence was not searched or proved.",
            "Research 0090 coverage is open; Research 0092 promotion remains blocked.",
            "The resource-inventory CI mismatch on draft PR #234 remains an independent engineering residual.",
        ],
        "claim_boundaries": {
            "new_word": False,
            "native_runtime_result": False,
            "reconstruction_impossibility": False,
            "m6_filler": False,
            "arithmetic_universality": False,
            "hypothesized_arithmetic_truth": False,
            "social_trust": False,
            "measured_practical_value": False,
        },
    }
    serialization_started = time.perf_counter_ns()
    encoded = json.dumps(outcome, indent=2, sort_keys=True) + "\n"
    serialization_ns = time.perf_counter_ns() - serialization_started
    outcome["cost"]["serialization_ns"] = serialization_ns
    while True:
        encoded = json.dumps(outcome, indent=2, sort_keys=True) + "\n"
        size = len(encoded.encode())
        if outcome["cost"].get("serialized_bytes") == size:
            break
        outcome["cost"]["serialized_bytes"] = size
    print(json.dumps(outcome, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
