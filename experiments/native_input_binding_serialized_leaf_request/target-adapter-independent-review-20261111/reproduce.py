#!/usr/bin/env python3
"""Independent contract probes and finite countermodels. NOT an Adva receiver.

Toy endpoint labels and admission premises below are mathematical model inputs,
not native SourceId/OccurrenceId creation, native imports, or certificates.
Original review tooling: Codex (OpenAI), Unknown v0.3.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import sys
import time

ROOT = Path(__file__).resolve().parent
MIB = 1024 * 1024
resource.setrlimit(resource.RLIMIT_CPU, (10, 10))
resource.setrlimit(resource.RLIMIT_AS, (256 * MIB, 256 * MIB))
resource.setrlimit(resource.RLIMIT_FSIZE, (MIB, MIB))
STARTED = time.perf_counter_ns()


def digest(data):
    return hashlib.sha256(data).hexdigest()


PINS = {
    "adapter-obligation-v0.json": "2cb19dff7fc86ce0940ce6877e5b3be2c570cd7e8667e4bac0bcfed2c795f8f3",
    "verify.py": "6f8032de83a6c00eaeed2c3d1662894712a55d6cac9cbbf843213f38d3d1766f",
}
for name, expected in PINS.items():
    assert digest((ROOT / "source" / name).read_bytes()) == expected, name
spec = importlib.util.spec_from_file_location("upstream_contract_checker", ROOT / "source/verify.py")
upstream = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upstream)
canonical = json.loads((ROOT / "source/adapter-obligation-v0.json").read_text())


def coherent_change(document, field, value):
    document["ordered_diagrams"][0]["qualified_endpoint"][field] = value
    document["relation"]["left"][field] = value


probes = [("S00-canonical", copy.deepcopy(canonical))]
for field, value in [("path", "missing/999"), ("source_id", "foreign-source"),
                     ("occurrence_id", "foreign-occurrence")]:
    doc = copy.deepcopy(canonical)
    coherent_change(doc, field, value)
    probes.append(("S0%d-coherent-%s" % (len(probes), field), doc))
doc = copy.deepcopy(canonical)
doc["ordered_diagrams"][0]["serialized_sha256"] = "5" * 64
doc["relation"]["left"]["diagram_sha256"] = "5" * 64
probes.append(("S04-coherent-diagram-pin", doc))
doc = copy.deepcopy(canonical)
doc["request_binding"]["canonical_bytes_sha256"] = "9" * 64
probes.append(("S05-request-repin-without-rederivation", doc))
doc = copy.deepcopy(canonical)
doc["request_binding"]["request_schema"] = "unregistered-schema"
probes.append(("S06-unregistered-request-schema", doc))
assert len(probes) == 7
structural = []
for name, doc in probes:
    observation = upstream.validate(doc)
    structural.append({"id": name, "document": doc, "observed": observation})
    assert observation["status"] == "StructurallyCompleteProposedInterface"
assert canonical["relation"]["left"] != canonical["relation"]["right"]


def endpoint(slot, graph, context, source, occurrence, path, value):
    return {"selector": {"slot": slot, "diagram": graph, "context": context,
                         "source": source, "occurrence": occurrence, "path": path},
            "value": value, "image": "one-local-point"}


# Distinct, separately assumed-well-formed finite diagrams, no native claim.
WORLD = [
    endpoint("left", "DL", "source", "a", "u", [], 1),
    endpoint("left", "DL", "source", "c", "w", [1], 1),
    endpoint("right", "DR", "residual", "b", "v", [], 1),
    endpoint("right", "DR", "residual", "d", "z", [1], 1),
    endpoint("right", "DR", "residual", "b", "t", [2], 2),
]
def key(selector):
    return json.dumps(selector, sort_keys=True, separators=(",", ":"))


BASE_PAIR = [copy.deepcopy(WORLD[0]["selector"]), copy.deepcopy(WORLD[2]["selector"])]
FINITE_RELATION = {(key(BASE_PAIR[0]), key(BASE_PAIR[1]))}


def model(case):
    """A deliberately specified finite oracle, not a proposed implementation."""
    if case.get("budget_exhausted"):
        return "Unknown", "BudgetExhausted"
    if case.get("receiver_context") != "toy-context":
        return "Refused", "ReceiverContextMismatch"
    if case["supplied_pair"] != case["request_pair"]:
        return "Refused", "RequestSelectorMismatch"
    if case.get("missing_admission"):
        return "Unknown", "AdmissionUnavailable"
    pair = case["supplied_pair"]
    if [e["slot"] for e in pair] != ["left", "right"]:
        return "Refused", "OrderedSlotMismatch"
    if [e["diagram"] for e in pair] != ["DL", "DR"]:
        return "Refused", "DiagramBindingMismatch"
    resolved = []
    for selector in pair:
        matches = [e for e in WORLD if e["selector"] == selector]
        if len(matches) != 1:
            return "Refused", "JointEndpointBindingMismatch"
        resolved.append(matches[0])
    kind = case["predicate"]
    if kind == "PinnedPairMembership":
        pass
    elif kind == "FiniteRelation":
        if (key(pair[0]), key(pair[1])) not in FINITE_RELATION:
            return "Refused", "FiniteRelationFalse"
    elif kind == "ExactIntegerValueEquality":
        if resolved[0]["value"] != resolved[1]["value"]:
            return "Refused", "ValueMismatch"
    elif kind == "ProofRequiredTransport":
        return "Unknown", "RelationEvidenceUnavailable"
    else:
        return "Unknown", "RelationUnderspecified"
    if case.get("receipt_subject") != "same-request-pair-profile-context":
        return "Refused", "ReceiptBindingMismatch"
    if case.get("record_write_failed"):
        return "Unknown", "ReceiptPersistenceFailure"
    return "Accepted", "OnlyTheNamedToyPredicate"


def fresh(name, expected, reason, predicate="FiniteRelation"):
    return {"id": name, "expected": {"status": expected, "reason": reason},
            "request_pair": copy.deepcopy(BASE_PAIR),
            "supplied_pair": copy.deepcopy(BASE_PAIR), "predicate": predicate,
            "receiver_context": "toy-context",
            "receipt_subject": "same-request-pair-profile-context"}


def set_pair(case, pair):
    case["request_pair"] = copy.deepcopy(pair)
    case["supplied_pair"] = copy.deepcopy(pair)


cases = [fresh("M01-distinct-identities-valid-relation", "Accepted", "OnlyTheNamedToyPredicate")]
for name, field, value in [
    ("M02-coherent-nonexistent-path", "path", [999]),
    ("M03-foreign-source-same-value", "source", "foreign-a"),
    ("M04-spliced-source-occurrence-path", "source", "d"),
]:
    c = fresh(name, "Refused", "JointEndpointBindingMismatch")
    p = copy.deepcopy(BASE_PAIR)
    p[1][field] = value
    set_pair(c, p)
    cases.append(c)
unrelated = [copy.deepcopy(BASE_PAIR[0]), copy.deepcopy(WORLD[3]["selector"])]
c = fresh("M05-equal-value-valid-unrelated-endpoints", "Refused", "FiniteRelationFalse")
set_pair(c, unrelated)
cases.append(c)
c = fresh("M06-equal-local-image-missing-transport-witness", "Unknown", "RelationEvidenceUnavailable", "ProofRequiredTransport")
set_pair(c, unrelated)
cases.append(c)
c = fresh("M07-reversed-order", "Refused", "OrderedSlotMismatch")
set_pair(c, list(reversed(BASE_PAIR)))
cases.append(c)
c = fresh("M08-membership-only-is-weaker", "Accepted", "OnlyTheNamedToyPredicate", "PinnedPairMembership")
set_pair(c, unrelated)
cases.append(c)
c = fresh("M09-new-value-only-request-preserves-distinct-origins", "Accepted", "OnlyTheNamedToyPredicate", "ExactIntegerValueEquality")
set_pair(c, unrelated)
cases.append(c)
c = fresh("M10-unequal-values", "Refused", "ValueMismatch", "ExactIntegerValueEquality")
set_pair(c, [BASE_PAIR[0], WORLD[4]["selector"]])
cases.append(c)
cases.append(fresh("M11-predicate-not-defined", "Unknown", "RelationUnderspecified", None))
c = fresh("M12-resource-exhaustion", "Unknown", "BudgetExhausted")
c["budget_exhausted"] = True
cases.append(c)
c = fresh("M13-foreign-receipt", "Refused", "ReceiptBindingMismatch")
c["receipt_subject"] = "different-request"
cases.append(c)
c = fresh("M14-missing-right-admission", "Unknown", "AdmissionUnavailable")
c["missing_admission"] = "right"
cases.append(c)
c = fresh("M15-selector-substitution-against-frozen-request", "Refused", "RequestSelectorMismatch")
c["supplied_pair"] = copy.deepcopy(unrelated)
cases.append(c)
c = fresh("M16-required-record-write-failure", "Unknown", "ReceiptPersistenceFailure")
c["record_write_failed"] = True
cases.append(c)
assert len(cases) == 16
for c in cases:
    status, reason = model(c)
    c["observed_model_result"] = {"status": status, "reason": reason}
    assert c["observed_model_result"] == c["expected"], c["id"]
assert WORLD[2]["value"] == WORLD[3]["value"]
assert WORLD[0]["image"] == WORLD[3]["image"]
assert (key(unrelated[0]), key(unrelated[1])) not in FINITE_RELATION

payload = {
    "status": "IndependentContractCountermodelsChecked",
    "semantic_authority": False, "real_request_reads": 0,
    "native_diagram_byte_reads": 0, "native_executions": 0,
    "original_helper_test_runs": 0, "reference_inventory_runs": 0,
    "upstream_sha256": PINS, "structural_probe_count": len(probes),
    "canonical_full_left_equals_right": False, "structural_probes": structural,
    "toy_world": WORLD, "toy_relation_edges": [BASE_PAIR], "finite_model_cases": cases,
    "finite_model_case_count": len(cases),
    "native_results": "NotRun; every Accepted/Refused/Unknown inside finite_model_cases is a model result only.",
    "elapsed_ns_before_output": time.perf_counter_ns() - STARTED,
    "process_ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    "limitations": ["No claim about target satisfiability.", "No implementation or native conformance proof.",
                    "Toy relation is chosen explicitly; it does not infer the caller's intended target relation."]
}
sys.stdout.write(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
