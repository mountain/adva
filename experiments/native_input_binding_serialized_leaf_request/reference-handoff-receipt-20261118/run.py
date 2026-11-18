#!/usr/bin/env python3
"""Form and test a receipt for bytes handed to one pinned native consumer."""

from __future__ import annotations

import base64
import hashlib
import json
import resource
import shutil
import time
from copy import deepcopy
from pathlib import Path

HERE = Path(__file__).resolve().parent
CONTRACT_PATH = HERE / "contract.json"
FIXTURE_B64 = HERE / "canonical-request-20261031.json.b64"
CONSUMER_SOURCE = HERE / "native_input_binding_serialized_consumer.rs"


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def resolve(
    raw: bytes,
    locator: dict[str, object],
    expected_authority: dict[str, object],
    expected_digest: str,
    byte_budget: int,
    retrieval_medium: str,
) -> tuple[str, dict[str, object] | None]:
    if locator != expected_authority:
        return "Refused/AuthorityPinMismatch", None
    if len(raw) > byte_budget:
        return "Refused/ByteBudgetExceeded", None
    observed = sha256(raw)
    if observed != expected_digest:
        return "Refused/ContentDigestMismatch", None
    receipt = {
        "schema": "adva.research.reference-handoff-receipt.v0",
        "locator": locator,
        "expected_sha256": expected_digest,
        "observed_sha256": observed,
        "bytes": len(raw),
        "byte_budget": byte_budget,
        "retrieval_medium": retrieval_medium,
    }
    return "Retrieved/ByteExact", receipt


def validate_handoff(raw: bytes, receipt: dict[str, object] | None) -> str:
    if receipt is None:
        return "CertificateObstruction/MissingRetrievalReceipt"
    if receipt.get("observed_sha256") != sha256(raw):
        return "Refused/ReceiptDigestMismatch"
    if receipt.get("bytes") != len(raw):
        return "Refused/ReceiptLengthMismatch"
    return "StructurallyReady/ReceiptBoundBytes"


def main() -> None:
    started = time.perf_counter_ns()
    contract = json.loads(CONTRACT_PATH.read_text())
    fixture_read_start = time.perf_counter_ns()
    fixture = base64.b64decode(FIXTURE_B64.read_text(), validate=False)
    fixture_read_ns = time.perf_counter_ns() - fixture_read_start

    locator = contract["objects"]["reference_locator"]
    digest = contract["objects"]["content_digest"]
    boundary = contract["objects"]["native_boundary"]

    source_read_start = time.perf_counter_ns()
    source = CONSUMER_SOURCE.read_bytes()
    source_read_ns = time.perf_counter_ns() - source_read_start

    evaluation_start = time.perf_counter_ns()
    source_text = source.decode()
    source_patterns = {
        "reads_path_from_environment": 'env::var("ADVA_SERIALIZED_LEAF_REQUEST_PATH")' in source_text,
        "reads_utf8_file": "fs::read_to_string(path).unwrap()" in source_text,
        "calls_receiver_with_frozen_budgets": "receive(expected_module, &encoded, 65_536, 512)" in source_text,
        "requires_canonical_bytes": "if encoded != FIXTURE" in source_text,
        "matching_case_names_native_acceptance": '"matching" => assert_eq!(outcome, Outcome::AcceptedCurrentFixture)' in source_text,
    }

    assert sha256(fixture) == digest["value"]
    assert len(fixture) == digest["bytes"]
    assert sha256(source) == boundary["source_sha256"]
    assert all(source_patterns.values())

    positive_status, receipt = resolve(
        fixture,
        locator,
        locator,
        digest["value"],
        boundary["byte_budget"],
        "checked-in-base64-mirror",
    )

    wrong_authority = deepcopy(locator)
    wrong_authority["repository"] = "mountain/not-adva"
    wrong_authority_status, _ = resolve(
        fixture,
        wrong_authority,
        locator,
        digest["value"],
        boundary["byte_budget"],
        "checked-in-base64-mirror",
    )

    wrong_digest_status, _ = resolve(
        fixture,
        locator,
        locator,
        "0" * 64,
        boundary["byte_budget"],
        "checked-in-base64-mirror",
    )
    byte_budget_status, _ = resolve(
        fixture,
        locator,
        locator,
        digest["value"],
        len(fixture) - 1,
        "checked-in-base64-mirror",
    )

    valid_handoff = validate_handoff(fixture, receipt)
    missing_receipt = validate_handoff(fixture, None)
    altered_receipt = deepcopy(receipt)
    assert altered_receipt is not None
    altered_receipt["observed_sha256"] = "f" * 64
    altered_receipt_status = validate_handoff(fixture, altered_receipt)

    fresh_payload = canonical(
        {
            "profile": "adva.research.fresh-reference-control.v0",
            "items": [1, 2, 3],
        }
    )
    fresh_locator = {
        "scheme": "synthetic",
        "name": "fresh-reference-control",
        "version": 0,
    }
    fresh_status, fresh_receipt = resolve(
        fresh_payload,
        fresh_locator,
        fresh_locator,
        sha256(fresh_payload),
        1024,
        "synthetic-in-memory",
    )
    fresh_handoff = validate_handoff(fresh_payload, fresh_receipt)

    assert positive_status == "Retrieved/ByteExact"
    assert wrong_authority_status == "Refused/AuthorityPinMismatch"
    assert wrong_digest_status == "Refused/ContentDigestMismatch"
    assert byte_budget_status == "Refused/ByteBudgetExceeded"
    assert valid_handoff == "StructurallyReady/ReceiptBoundBytes"
    assert missing_receipt == "CertificateObstruction/MissingRetrievalReceipt"
    assert altered_receipt_status == "Refused/ReceiptDigestMismatch"
    assert fresh_status == "Retrieved/ByteExact"
    assert fresh_handoff == "StructurallyReady/ReceiptBoundBytes"

    baseline_projection = {
        "bytes_sha256": sha256(fixture),
        "bytes": len(fixture),
    }
    explicit_projection = {
        **baseline_projection,
        "reference_handoff_receipt": receipt,
    }
    baseline_start = time.perf_counter_ns()
    baseline_bytes = canonical(baseline_projection)
    baseline_formation_ns = time.perf_counter_ns() - baseline_start
    explicit_start = time.perf_counter_ns()
    explicit_bytes = canonical(explicit_projection)
    explicit_formation_ns = time.perf_counter_ns() - explicit_start

    rust_tools = {"cargo": shutil.which("cargo"), "rustc": shutil.which("rustc")}
    native_status = (
        "NotRun/RustToolchainUnavailable"
        if not all(rust_tools.values())
        else "NotRun/OutsideFrozenExecutionRoute"
    )
    evaluation_ns = time.perf_counter_ns() - evaluation_start

    outcome = {
        "schema": "adva.research.reference-handoff-receipt.outcome.v0",
        "status": "RetrievedExactBytes/NativeAcceptanceUnknown",
        "byte_retrieval_result": "PassedBoundedReferenceRetrieval",
        "native_consumer_result": native_status,
        "source_surface": {
            "source_sha256": sha256(source),
            "patterns": source_patterns,
        },
        "instances": {
            "canonical_matching": positive_status,
            "canonical_wrong_authority": wrong_authority_status,
            "canonical_wrong_digest": wrong_digest_status,
            "canonical_byte_budget": byte_budget_status,
            "fresh_reuse": fresh_status,
        },
        "receipt_controls": {
            "valid": valid_handoff,
            "missing": missing_receipt,
            "altered_digest": altered_receipt_status,
            "fresh": fresh_handoff,
        },
        "receipt": receipt,
        "fresh_receipt": fresh_receipt,
        "toolchain": rust_tools,
        "proposed_word": {
            "word": "reference-handoff receipt",
            "state": "Proposed",
            "role": "bind exact retrieved bytes to a locator, authority tuple, digest and bounded retrieval event without granting semantic acceptance",
            "input": "pinned locator and authority, expected digest, byte budget and retrieved bytes",
            "output_relation": "Retrieved/ByteExact followed by StructurallyReady/ReceiptBoundBytes",
            "applicability": "the witness-custody mode is referenced and the receiver must hand external bytes to a separately pinned consumer",
            "witness": "five fixed instances, three receipt controls, a pinned Rust source-surface check and one fresh payload reuse",
            "refusal_conditions": [
                "authority tuple differs",
                "byte budget is exceeded",
                "content digest differs",
                "receipt is missing",
                "receipt digest or length differs",
            ],
            "expansion": "resolve bounded bytes, compare the exact authority tuple, check length and digest, serialize the receipt with the bytes, then invoke the separately pinned native consumer",
            "residual": "cargo/rustc are unavailable here, so native consumer execution and semantic certificate acceptance were not performed",
        },
        "comparison": {
            "baseline_bytes": len(baseline_bytes),
            "explicit_receipt_bytes": len(explicit_bytes),
            "formation_byte_delta": len(explicit_bytes) - len(baseline_bytes),
            "baseline_formation_ns": baseline_formation_ns,
            "explicit_formation_ns": explicit_formation_ns,
            "claim": "the explicit form carries authority and retrieval history that the byte-only form omits; no global expressivity or efficiency theorem is claimed",
        },
        "cost": {
            "routes": 1,
            "counted_units": 12,
            "fixture_decode_and_read_ns": fixture_read_ns,
            "consumer_source_read_ns": source_read_ns,
            "evaluation_and_verification_ns": evaluation_ns,
            "whole_run_before_serialization_ns": time.perf_counter_ns() - started,
            "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "external_network_fetches_during_execution": 0,
            "native_executions": 0,
            "implementation_correction_replays": 1,
        },
        "claim_boundaries": {
            "finite_receipt_checks_only": True,
            "native_consumer_executed": False,
            "semantic_certificate_accepted": False,
            "word_promoted": False,
            "three_custody_modes_exhaustive": False,
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
    print("OUTCOME_SHA256 " + sha256(encoded.encode()), file=__import__("sys").stderr)


if __name__ == "__main__":
    main()
