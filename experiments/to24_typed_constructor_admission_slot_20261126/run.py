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


def load_predecessor(expected_sha256, expected_outcome_sha256):
    candidates = [
        ROOT.parent / "typed-discharge-frontier-20261125" / "run.py",
        ROOT.parent / "to24_typed_discharge_frontier_20261125" / "run.py",
    ]
    path = next((candidate for candidate in candidates if candidate.exists()), None)
    if path is None:
        raise FileNotFoundError("PinnedPredecessorRunMissing")
    actual = digest_bytes(path.read_bytes())
    if actual != expected_sha256:
        raise ValueError("PinnedPredecessorRunMismatch")
    outcome_path = path.parent / "outcome.json"
    if digest_bytes(outcome_path.read_bytes()) != expected_outcome_sha256:
        raise ValueError("PinnedPredecessorOutcomeMismatch")
    spec = importlib.util.spec_from_file_location("typed_discharge_predecessor", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, path, actual


def base_projection(slot):
    return {
        "target_digest": slot["target_digest"],
        "obligation_digest": slot["obligation_digest"],
        "registry_interface_declared": True,
    }


def form_slot(obligation, target_digest, registry, candidate=None):
    return {
        "schema": "adva.research.typed-constructor-admission-slot.v0",
        "target_digest": target_digest,
        "obligation_digest": digest(obligation),
        "registry_interface_digest": digest(registry),
        "slot_state": "Open",
        "candidate": copy.deepcopy(candidate),
        "target_admission_receipt": None,
        "discharge_receipt": None,
        "semantic_equality": "NotClaimed",
        "higher_cell": "NotConstructed",
        "filler": "NotConstructed",
    }


def validate_registry(registry, target_digest, exact_interface):
    if registry.get("schema") != exact_interface["schema"]:
        return "Refused/RegistrySchemaMismatch"
    if registry.get("target_digest") != target_digest:
        return "Refused/RegistryTargetMismatch"
    if registry.get("authority") != "ExternalInterfaceOnly":
        return "Refused/UnverifiableRegistryAuthority"
    if registry.get("target_authority_receipt") is not None:
        return "Refused/UnverifiableRegistryAuthority"
    if registry.get("required_entry_fields") != exact_interface["required_entry_fields"]:
        return "Refused/RegistryInterfaceFieldSetMismatch"
    if registry.get("transition_order") != exact_interface["transition_order"]:
        return "Refused/RegistryTransitionOrderMismatch"
    if registry.get("semantic_equality") != "NotClaimed":
        return "Refused/PrematureRegistryEquality"
    if registry.get("higher_cell") != "NotConstructed":
        return "Refused/PrematureRegistryHigherCell"
    if registry.get("filler") != "NotConstructed":
        return "Refused/PrematureRegistryFiller"
    if registry.get("entries") != []:
        return "Refused/ExternalInterfaceCannotAdmitEntry"
    return None


def audit(slot, obligation, target_digest, registry, exact_interface):
    if slot.get("semantic_equality") != "NotClaimed":
        return "Refused/PrematureSemanticEquality"
    if slot.get("higher_cell") != "NotConstructed":
        return "Refused/PrematureHigherCell"
    if slot.get("filler") != "NotConstructed":
        return "Refused/PrematureFiller"
    if slot.get("discharge_receipt") is not None:
        return "Refused/PrematureDischargeReceipt"
    if slot.get("target_admission_receipt") is not None:
        return "Refused/UnverifiableTargetAuthority"
    if slot.get("target_digest") != target_digest:
        return "Refused/TargetDigestMismatch"
    if slot.get("obligation_digest") != digest(obligation):
        return "Refused/ObligationDigestMismatch"
    if slot.get("registry_interface_digest") != digest(registry):
        return "Refused/RegistryDigestMismatch"
    registry_error = validate_registry(registry, target_digest, exact_interface)
    if registry_error:
        return registry_error

    candidate = slot.get("candidate")
    if candidate is None:
        return "OpenAdmissionSlot/EmptyExternalInterface"
    if candidate.get("boundary_digest") != digest(obligation):
        return "Refused/CandidateBoundaryMismatch"
    if candidate.get("authority") != "ExternalProposal":
        return "Refused/UnverifiableTargetAuthority"
    if candidate.get("target_admission_receipt") is not None:
        return "Refused/UnverifiableTargetAuthority"
    if candidate.get("semantic_equality") != "NotClaimed":
        return "Refused/CandidatePrematureEquality"
    if candidate.get("higher_cell") != "NotConstructed":
        return "Refused/CandidatePrematureHigherCell"
    if candidate.get("filler") != "NotConstructed":
        return "Refused/CandidatePrematureFiller"
    return "UnknownAdmission/ExternalCandidateOnly"


def main():
    started = time.perf_counter_ns()
    input_data = json.loads((ROOT / "input.json").read_text())

    predecessor_started = time.perf_counter_ns()
    pred, pred_path, pred_sha = load_predecessor(
        input_data["predecessor"]["run_sha256"],
        input_data["predecessor"]["outcome_sha256"],
    )
    pred_input = json.loads((pred_path.parent / "input.json").read_text())
    interchange, interchange_path, interchange_sha = pred.load_module(
        pred_input["predecessor"]["run_sha256"])
    segment, segment_path, segment_sha = interchange.load_predecessor(
        pred_input["predecessor"]["segment_run_sha256"])
    anchor, anchor_path, anchor_sha = segment.load_predecessor(
        pred_input["predecessor"]["anchor_run_sha256"])
    predecessor_ns = time.perf_counter_ns() - predecessor_started

    target_started = time.perf_counter_ns()
    target = anchor.build_target(input_data["target_descriptor"])
    target_digest = anchor.digest(target)
    target_ns = time.perf_counter_ns() - target_started
    if target_digest != input_data["predecessor"]["target_digest"]:
        raise ValueError("PinnedTargetDigestMismatch")
    inventory = pred.target_inventory(target)
    if inventory["higher_constructor_registry_declared"]:
        raise ValueError("TargetUnexpectedlyDeclaresHigherRegistry")
    target_nodes = inventory["objects"] + inventory["one_cells"] + inventory["two_cells"]

    interchange_input = json.loads((interchange_path.parent / "input.json").read_text())
    primary_square, fresh_square = interchange_input["squares"]
    obligation_started = time.perf_counter_ns()
    primary = interchange.form_obligation(
        primary_square, segment, anchor, target, target_digest, interchange_input["rule"])
    primary_ns = time.perf_counter_ns() - obligation_started
    reuse_started = time.perf_counter_ns()
    fresh = interchange.form_obligation(
        fresh_square, segment, anchor, target, target_digest, interchange_input["rule"])
    fresh_ns = time.perf_counter_ns() - reuse_started
    if interchange.validate_obligation(
            primary, primary_square, segment, anchor, target, target_digest) != interchange.PASS:
        raise ValueError("PrimaryObligationInvalid")
    if interchange.validate_obligation(
            fresh, fresh_square, segment, anchor, target, target_digest) != interchange.PASS:
        raise ValueError("FreshObligationInvalid")

    registry_started = time.perf_counter_ns()
    registry = copy.deepcopy(input_data["registry_interface"])
    registry_error = validate_registry(registry, target_digest, registry)
    if registry_error:
        raise ValueError(registry_error)
    registry_ns = time.perf_counter_ns() - registry_started

    primary_slot_started = time.perf_counter_ns()
    primary_slot = form_slot(primary, target_digest, registry)
    primary_slot_ns = time.perf_counter_ns() - primary_slot_started
    fresh_slot_started = time.perf_counter_ns()
    fresh_slot = form_slot(fresh, target_digest, registry)
    fresh_slot_ns = time.perf_counter_ns() - fresh_slot_started
    baseline = base_projection(primary_slot)

    external = copy.deepcopy(input_data["external_candidate"])
    external["boundary_digest"] = digest(primary)
    cases = []
    validation_started = time.perf_counter_ns()

    def record(name, slot, obligation, case_registry, expected):
        result = audit(slot, obligation, target_digest, case_registry, registry)
        cases.append({
            "name": name,
            "base_projection_equal_to_primary": base_projection(slot) == baseline,
            "result": result,
            "expected": expected,
            "matched": result == expected,
        })

    record("primary-empty-interface", primary_slot, primary, registry,
           "OpenAdmissionSlot/EmptyExternalInterface")
    record("fresh-obligation-reuse", fresh_slot, fresh, registry,
           "OpenAdmissionSlot/EmptyExternalInterface")

    proposed = form_slot(primary, target_digest, registry, external)
    record("complete-external-candidate", proposed, primary, registry,
           "UnknownAdmission/ExternalCandidateOnly")

    wrong_boundary = copy.deepcopy(proposed)
    wrong_boundary["candidate"]["boundary_digest"] = "0" * 64
    record("wrong-candidate-boundary", wrong_boundary, primary, registry,
           "Refused/CandidateBoundaryMismatch")

    wrong_target = copy.deepcopy(primary_slot)
    wrong_target["target_digest"] = "0" * 64
    record("changed-target", wrong_target, primary, registry,
           "Refused/TargetDigestMismatch")

    wrong_obligation = copy.deepcopy(primary_slot)
    wrong_obligation["obligation_digest"] = "f" * 64
    record("changed-obligation", wrong_obligation, primary, registry,
           "Refused/ObligationDigestMismatch")

    forged_authority = copy.deepcopy(proposed)
    forged_authority["candidate"]["authority"] = "TargetOwned"
    forged_authority["candidate"]["target_admission_receipt"] = "self-issued"
    record("forged-target-authority", forged_authority, primary, registry,
           "Refused/UnverifiableTargetAuthority")

    inserted_registry = copy.deepcopy(registry)
    inserted_registry["entries"] = [copy.deepcopy(external)]
    inserted_slot = copy.deepcopy(primary_slot)
    inserted_slot["registry_interface_digest"] = digest(inserted_registry)
    record("direct-external-entry-insertion", inserted_slot, primary, inserted_registry,
           "Refused/ExternalInterfaceCannotAdmitEntry")

    premature_discharge = copy.deepcopy(primary_slot)
    premature_discharge["discharge_receipt"] = "self-issued"
    record("premature-discharge-receipt", premature_discharge, primary, registry,
           "Refused/PrematureDischargeReceipt")

    changed_fields = copy.deepcopy(registry)
    changed_fields["required_entry_fields"] = changed_fields["required_entry_fields"][:-1]
    changed_fields_slot = copy.deepcopy(primary_slot)
    changed_fields_slot["registry_interface_digest"] = digest(changed_fields)
    record("changed-interface-field-set", changed_fields_slot, primary, changed_fields,
           "Refused/RegistryInterfaceFieldSetMismatch")

    premature_equality = copy.deepcopy(primary_slot)
    premature_equality["semantic_equality"] = "EqualCompositeClaimed"
    record("premature-semantic-equality", premature_equality, primary, registry,
           "Refused/PrematureSemanticEquality")

    premature_filler = copy.deepcopy(primary_slot)
    premature_filler["filler"] = "M6FillerClaimed"
    record("premature-filler", premature_filler, primary, registry,
           "Refused/PrematureFiller")

    validation_ns = time.perf_counter_ns() - validation_started
    all_expected = all(case["matched"] for case in cases)
    collision_count = sum(
        case["base_projection_equal_to_primary"] and case["name"] != "primary-empty-interface"
        for case in cases)
    primary_record = {
        "target_digest": target_digest,
        "obligation_digest": digest(primary),
        "registry_interface": registry,
        "slot": primary_slot,
        "result": cases[0]["result"],
        "residual": [
            "target-owned registry authority",
            "one admitted applicable constructor entry",
            "one target-backed discharge receipt"
        ],
    }
    baseline_bytes = len(canonical_bytes(baseline))
    record_bytes = len(canonical_bytes(primary_record))
    constructed_nodes = target_nodes + 8 + 4 + 2 + 1 + 2 + len(cases) + 1
    before_serialization_ns = time.perf_counter_ns() - started

    outcome = {
        "schema": "adva.research.typed-constructor-admission-slot.outcome.v0",
        "status": "PassedBoundedTypedConstructorAdmissionSlot" if all_expected else "Failed",
        "claim": "One exact external registry interface can retain an explicitly empty admission slot for each checked obligation, while a complete external proposal remains outside target authority and each declared direct self-admission route is refused.",
        "claim_boundary": "This is a finite interface and refusal result. The external registry contract does not modify the target, admit a constructor, discharge an obligation, or construct a 3-cell.",
        "predecessor": {
            "run_path": pred_path.name,
            "run_sha256": pred_sha,
            "interchange_run_path": interchange_path.name,
            "interchange_run_sha256": interchange_sha,
            "segment_run_sha256": segment_sha,
            "anchor_run_sha256": anchor_sha,
        },
        "target": {"digest": target_digest, "inventory": inventory, "nodes": target_nodes},
        "registry_interface_digest": digest(registry),
        "primary_record": primary_record,
        "fresh_obligation_digest": digest(fresh),
        "cases": cases,
        "comparison": {
            "untyped_projection_bytes": baseline_bytes,
            "typed_slot_record_bytes": record_bytes,
            "formation_byte_delta": record_bytes - baseline_bytes,
            "base_projection_collisions_beyond_primary": collision_count,
            "finite_distinction": "the untyped projection says only that an interface is declared; it cannot distinguish empty, external-only, forged-authority, direct-insertion, field-set, equality, filler, or discharge states",
            "claim_boundary": "No general expressivity, minimality, completeness, admission, or efficiency theorem is claimed.",
        },
        "proposed_word": {
            "word": "typed constructor admission slot",
            "state": "Proposed",
            "role": "retain one explicit open target-and-obligation coordinate in a versioned external registry interface without granting registry membership or discharge",
            "input": "one exact target digest, one checked typed obligation, one validated external empty registry interface, and an optional external constructor candidate",
            "output_relation": "OpenAdmissionSlot, UnknownAdmission, or a registry-, target-, obligation-, boundary-, authority-, discharge-, equality-, or filler-specific refusal",
            "applicability": "the target and obligation are exactly pinned, the registry interface is external and empty, and no target authority receipt exists",
            "witness": "the registry interface digest and exact fields, target and obligation digests, open slot state, optional candidate, result, and residual authority/admission/discharge requirements",
            "counterexample": "a complete boundary-matching external proposal remains UnknownAdmission; self-issued target authority and direct insertion into the external interface are refused",
            "expansion": "verify the predecessor obligation; validate the registry schema, target pin, authority, field set, transition order and empty entries; bind one open slot; validate any candidate boundary; stop at Unknown unless a separately supplied target-owned registry and admission receipt exist",
            "refusal_conditions": [
                "target, obligation, registry digest, schema, field-set or transition mismatch",
                "boundary mismatch or unverifiable target authority",
                "direct entry insertion into an external-only interface",
                "premature discharge, equality, higher cell or filler"
            ],
            "replay": "timeout 30s python3 run.py",
            "residual": "no target-owned registry, admitted constructor, discharge receipt, semantic equality, higher cell, filler, Research 0090 coverage, Research 0092 promotion, arithmetic-universality or hypothesized-arithmetic-truth result",
        },
        "cost": {
            "routes": 1,
            "cases": len(cases),
            "constructed_nodes": constructed_nodes,
            "predecessor_verification_ns": predecessor_ns,
            "target_formation_ns": target_ns,
            "primary_obligation_formation_ns": primary_ns,
            "fresh_obligation_formation_ns": fresh_ns,
            "registry_interface_formation_ns": registry_ns,
            "primary_slot_formation_ns": primary_slot_ns,
            "fresh_slot_reuse_ns": fresh_slot_ns,
            "case_validation_ns": validation_ns,
            "whole_run_before_serialization_ns": before_serialization_ns,
            "ru_maxrss_kib_before_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "implementation_correction_replays": 1,
            "implementation_correction": "The first passing output said every direct self-admission route; the sole correction narrowed this to each declared route. The interface, cases, budget and decisions were unchanged.",
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
        "cases": len(cases),
        "constructed_nodes": constructed_nodes,
        "fresh_reuse": cases[1]["result"],
        "external_candidate": cases[2]["result"],
        "collisions": collision_count,
        "serialized_bytes": len(encoded),
        "ru_maxrss_kib": outcome["cost"]["ru_maxrss_kib_before_serialization"],
        "sha256": digest_bytes(encoded),
    }, sort_keys=True))
    if not all_expected:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
