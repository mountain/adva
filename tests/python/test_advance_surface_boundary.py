"""Finite protocol/byte-gate tests; no execution of the symbol-surface trial."""

import copy
import json
from pathlib import Path

import pytest
from adva.advance_surface import FILES, check_loaded, check_payload_bindings

SOURCE = Path(__file__).resolve().parents[2] / "experiments/symbol_surface"


@pytest.fixture
def payloads():
    return {name: (SOURCE / name).read_bytes() for name in FILES}


def test_original_external_bindings_keep_nine_annotations(payloads):
    _, sites = check_payload_bindings(payloads)
    assert len(sites) == 9


def test_payload_drift_is_rejected_even_when_it_still_parses(payloads):
    payloads["presentation.json"] += b" "
    with pytest.raises(ValueError, match="payload binding mismatch"):
        check_payload_bindings(payloads)


@pytest.fixture
def load_protocol(payloads):
    # This is synthetic protocol data, never presented as a native certificate.
    doc, sites = check_payload_bindings(payloads)
    certificate = dict.fromkeys(
        ("schema_and_version", "canonical_tables", "resolved_references", "mechanism_forms"),
        "checked",
    )
    certificate.update(schema=doc["schema"], version=0, entrypoint="inspect", frame=0)
    return {
        "certificate": certificate,
        "transition": {
            "state": "ready",
            "recorded_output": None,
            "form": {
                "mechanism": "verify",
                "discharges": [],
                "declared_subject": {"sites": copy.deepcopy(sites)},
                "input": {"subject": {"frontier": {"sites": copy.deepcopy(sites)}}},
            },
            "admission": {
                "mechanism": "verify",
                "status": "conditional",
                "remaining_subject": {"sites": copy.deepcopy(sites)},
            },
        },
    }, sites


def test_expected_protocol_is_read_without_mutation(load_protocol):
    loaded, sites = load_protocol
    before = copy.deepcopy(loaded)
    check_loaded(loaded, sites)
    assert loaded == before


def test_conditional_load_cannot_be_reported_as_closed(load_protocol):
    loaded, sites = load_protocol
    loaded["transition"]["admission"]["status"] = "closed"
    with pytest.raises(ValueError, match="conditional boundary"):
        check_loaded(loaded, sites)


def test_losing_one_frontier_annotation_is_rejected(load_protocol):
    loaded, sites = load_protocol
    loaded["transition"]["admission"]["remaining_subject"]["sites"].pop()
    with pytest.raises(ValueError, match="conditional boundary"):
        check_loaded(loaded, sites)


def test_loading_cannot_manufacture_recorded_outputs(load_protocol):
    loaded, sites = load_protocol
    loaded["transition"]["recorded_output"] = {"result": "invented"}
    with pytest.raises(ValueError, match="absent outputs"):
        check_loaded(loaded, sites)


def test_missing_rust_reference_check_is_rejected(load_protocol):
    loaded, sites = load_protocol
    loaded["certificate"].pop("resolved_references")
    with pytest.raises(ValueError, match="missing Rust load check"):
        check_loaded(loaded, sites)


def test_wrong_entrypoint_certificate_is_rejected(load_protocol):
    loaded, sites = load_protocol
    loaded["certificate"]["entrypoint"] = "some-other-frame"
    with pytest.raises(ValueError, match="selected envelope"):
        check_loaded(loaded, sites)


def test_obligation_status_promotion_is_rejected_even_with_consistent_pins(payloads):
    from adva.quine_relay import digest

    obligations = json.loads(payloads["obligations.json"])
    obligations["items"][0]["status"] = "Closed"
    payloads["obligations.json"] = json.dumps(obligations).encode()
    document = json.loads(payloads["symbol-surface.adva"])
    document["carriers"][2]["carrier"]["structure"] = "sha256:" + digest(
        payloads["obligations.json"]
    )
    payloads["symbol-surface.adva"] = json.dumps(document).encode()
    with pytest.raises(ValueError, match="Open annotations"):
        check_payload_bindings(payloads)
