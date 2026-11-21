#!/usr/bin/env python3
"""Finite model of a relation-selection gate; no native semantic authority."""
import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
U32_MAX = 2**32 - 1
FIELDS = (
    "slot", "diagram_sha256", "context", "source_id", "occurrence_id",
    "occurrence_path",
)


def outcome(kind, reason, permitted_use=None):
    return {"outcome": kind, "reason": reason, "permitted_use": permitted_use}


def valid_path(value):
    return isinstance(value, list) and all(
        type(item) is int and 0 <= item <= U32_MAX for item in value
    )


def valid_selector(value, slot):
    if not isinstance(value, dict) or set(value) != set(FIELDS):
        return False
    if value["slot"] != slot or not valid_path(value["occurrence_path"]):
        return False
    for name in FIELDS[:-1]:
        if not isinstance(value[name], str) or not value[name]:
            return False
    digest = value["diagram_sha256"]
    return len(digest) == 64 and all(char in "0123456789abcdef" for char in digest)


def evaluate(case, base):
    expected = {
        "left": copy.deepcopy(base["expected_left"]),
        "right": copy.deepcopy(base["expected_right"]),
    }
    actual = copy.deepcopy(expected)
    mutation = case["mutation"]
    if mutation == "actual-left-path-[1]":
        actual["left"]["occurrence_path"] = [1]
    elif mutation == "actual-right-origin-substitution":
        actual["right"]["source_id"] = "source:right:same-value-substitute"
        actual["right"]["occurrence_id"] = "occ:right:substitute"
    elif mutation == "expected-left-path-[true]":
        expected["left"]["occurrence_path"] = [True]
    elif mutation != "none":
        raise ValueError(f"undeclared mutation: {mutation}")

    if not valid_selector(expected["left"], "left") or not valid_selector(
        expected["right"], "right"
    ):
        return outcome("Refused", "MalformedOccurrencePath")
    if actual["left"] != expected["left"] or actual["right"] != expected["right"]:
        return outcome("Refused", "EndpointBindingMismatch")

    relation = case["selected_relation"]
    if relation is None:
        return outcome("Unknown", "TargetRelationUnderspecified")
    if relation == "PinnedPairMembershipV1":
        permitted = "QualifiedPairLocatedOnly"
    elif relation == "CertifiedRelationV1":
        checker = case["checker"]
        if checker == "unavailable":
            return outcome("Unknown", "RelationCheckerUnavailable")
        if checker == "false":
            return outcome("Refused", "CertifiedRelationFalse")
        if checker != "true":
            return outcome("Unknown", "RelationEvidenceUnavailable")
        permitted = "ExactCertifiedRelationOnly"
    else:
        return outcome("Refused", "UnsupportedRelationProfile")

    if case["receipt_persisted"] is not True:
        return outcome("Unknown", "ReceiptPersistenceFailure")
    return outcome("Accepted", permitted, permitted)


def load_cases():
    return json.loads((ROOT / "cases.json").read_text(encoding="utf-8"))


def run_all():
    document = load_cases()
    base = document["base_instance"]
    results = []
    for case in document["cases"]:
        observed = evaluate(case, base)
        expected = {
            "outcome": case["expected_outcome"],
            "reason": case["expected_reason"],
        }
        passed = observed["outcome"] == expected["outcome"] and observed["reason"] == expected["reason"]
        results.append({"id": case["id"], "expected": expected, "observed": observed,
                        "passed": passed})
    return results


if __name__ == "__main__":
    print(json.dumps(run_all(), indent=2, sort_keys=True))
