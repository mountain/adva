#!/usr/bin/env python3
import copy
import hashlib
import json
import resource
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def canonical_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def evaluate(reference, native):
    if reference is None:
        return "CertificateObstruction/MissingRetrievalReceipt"
    if native is None:
        return "CertificateObstruction/MissingNativeEvidence"
    if reference.get("retrieval_result") != "Retrieved/ByteExact":
        return "Refused/RetrievalNotExact"
    fixture = native.get("fixture", {})
    consumer = native.get("consumer", {})
    workflow = native.get("workflow", {})
    pins = native.get("verified_pins", {})
    comparisons = (
        (reference.get("repository"), native.get("repository"), "Refused/RepositoryMismatch"),
        (reference.get("path"), fixture.get("path"), "Refused/FixturePathMismatch"),
        (reference.get("git_blob_sha1"), fixture.get("git_blob_sha1"), "Refused/FixtureBlobMismatch"),
        (reference.get("bytes"), fixture.get("bytes"), "Refused/FixtureLengthMismatch"),
        (reference.get("sha256"), fixture.get("sha256"), "Refused/FixtureDigestMismatch"),
        (reference.get("byte_budget"), consumer.get("byte_budget"), "Refused/ByteBudgetMismatch"),
    )
    for left, right, refusal in comparisons:
        if left != right:
            return refusal
    if not consumer.get("path") or not consumer.get("sha256") or consumer.get("work_budget") is None:
        return "CertificateObstruction/IncompleteConsumerPin"
    native_pin_checks = (
        (fixture.get("git_blob_sha1"), pins.get("fixture_git_blob_sha1"), "Refused/NativeFixturePinMismatch"),
        (fixture.get("sha256"), pins.get("fixture_sha256"), "Refused/NativeFixturePinMismatch"),
        (consumer.get("path"), pins.get("consumer_path"), "Refused/NativeConsumerPinMismatch"),
        (consumer.get("sha256"), pins.get("consumer_sha256"), "Refused/NativeConsumerPinMismatch"),
        (consumer.get("byte_budget"), pins.get("consumer_byte_budget"), "Refused/NativeConsumerBudgetMismatch"),
        (consumer.get("work_budget"), pins.get("consumer_work_budget"), "Refused/NativeConsumerBudgetMismatch"),
    )
    for observed, verified_pin, refusal in native_pin_checks:
        if observed != verified_pin:
            return refusal
    if workflow.get("conclusion") != "success":
        return "Refused/WorkflowNotSuccessful"
    if not workflow.get("run_id") or not workflow.get("job_id"):
        return "CertificateObstruction/MissingWorkflowCoordinate"
    if native.get("case") != "matching":
        return "Refused/CaseMismatch"
    if native.get("consumer_outcome") != "AcceptedCurrentFixture":
        return "Refused/ConsumerOutcomeMismatch"
    if native.get("native_outcome") != "SuccessorVerified":
        return "Refused/NativeOutcomeMismatch"
    return "HistoricallyJoined/NativeAcceptedAtPinnedRun"


def mutate(base, path, value):
    result = copy.deepcopy(base)
    cursor = result
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value
    return result


def digest_projection(reference, native):
    if reference is None or native is None:
        return "DigestProjection/MissingSide"
    return (
        "DigestProjection/Match"
        if reference.get("sha256") == native.get("fixture", {}).get("sha256")
        else "DigestProjection/Mismatch"
    )


def main():
    started = time.perf_counter_ns()
    reference = json.loads((ROOT / "reference-receipt.json").read_text())
    native = json.loads((ROOT / "native-evidence.json").read_text())
    constructed = time.perf_counter_ns()

    cases = [
        ("exact", reference, native),
        ("wrong-fixture-digest", reference, mutate(native, ["fixture", "sha256"], "0" * 64)),
        ("wrong-consumer-digest", reference, mutate(native, ["consumer", "sha256"], "1" * 64)),
        ("wrong-byte-budget", reference, mutate(native, ["consumer", "byte_budget"], 65535)),
        ("failed-workflow", reference, mutate(native, ["workflow", "conclusion"], "failure")),
        ("wrong-case", reference, mutate(native, ["case"], "renamed-module")),
        ("wrong-native-outcome", reference, mutate(native, ["native_outcome"], "NotRun")),
        ("missing-reference", None, native),
    ]
    evaluated = []
    for name, left, right in cases:
        evaluated.append({
            "name": name,
            "digest_only": digest_projection(left, right),
            "coordinate_join": evaluate(left, right),
        })

    fresh_payload = b'{"fresh":"historical-acceptance-join","version":0}\n'
    fresh_digest = hashlib.sha256(fresh_payload).hexdigest()
    fresh_reference = {
        "schema": "adva.research.reference-handoff-receipt.v0",
        "repository": "synthetic/reuse",
        "path": "fresh.json",
        "git_blob_sha1": "2" * 40,
        "bytes": len(fresh_payload),
        "sha256": fresh_digest,
        "byte_budget": 1024,
        "retrieval_result": "Retrieved/ByteExact",
    }
    fresh_native = {
        "repository": "synthetic/reuse",
        "fixture": {
            "path": "fresh.json",
            "git_blob_sha1": "2" * 40,
            "bytes": len(fresh_payload),
            "sha256": fresh_digest,
        },
        "consumer": {
            "path": "fresh-consumer.rs",
            "sha256": "3" * 64,
            "byte_budget": 1024,
            "work_budget": 64,
        },
        "verified_pins": {
            "fixture_git_blob_sha1": "2" * 40,
            "fixture_sha256": fresh_digest,
            "consumer_path": "fresh-consumer.rs",
            "consumer_sha256": "3" * 64,
            "consumer_byte_budget": 1024,
            "consumer_work_budget": 64,
        },
        "workflow": {"run_id": 1, "job_id": 2, "conclusion": "success"},
        "case": "matching",
        "consumer_outcome": "AcceptedCurrentFixture",
        "native_outcome": "SuccessorVerified",
    }
    evaluated.extend([
        {
            "name": "fresh-exact-reuse",
            "digest_only": digest_projection(fresh_reference, fresh_native),
            "coordinate_join": evaluate(fresh_reference, fresh_native),
        },
        {
            "name": "fresh-failed-run-reuse",
            "digest_only": digest_projection(fresh_reference, fresh_native),
            "coordinate_join": evaluate(
                fresh_reference,
                mutate(fresh_native, ["workflow", "conclusion"], "failure"),
            ),
        },
    ])
    verified = time.perf_counter_ns()

    expected = {
        "exact": "HistoricallyJoined/NativeAcceptedAtPinnedRun",
        "wrong-fixture-digest": "Refused/FixtureDigestMismatch",
        "wrong-consumer-digest": "Refused/NativeConsumerPinMismatch",
        "wrong-byte-budget": "Refused/ByteBudgetMismatch",
        "failed-workflow": "Refused/WorkflowNotSuccessful",
        "wrong-case": "Refused/CaseMismatch",
        "wrong-native-outcome": "Refused/NativeOutcomeMismatch",
        "missing-reference": "CertificateObstruction/MissingRetrievalReceipt",
        "fresh-exact-reuse": "HistoricallyJoined/NativeAcceptedAtPinnedRun",
        "fresh-failed-run-reuse": "Refused/WorkflowNotSuccessful",
    }
    actual = {row["name"]: row["coordinate_join"] for row in evaluated}
    checks = {
        "all_expected": actual == expected,
        "never_current_acceptance": all("AcceptedNow" not in value for value in actual.values()),
        "digest_projection_false_coalescences": sum(
            row["digest_only"] == "DigestProjection/Match"
            and row["coordinate_join"].startswith("Refused/")
            for row in evaluated
        ),
    }
    assertions_ok = checks["all_expected"] and checks["never_current_acceptance"]
    if not assertions_ok:
        raise AssertionError({"expected": expected, "actual": actual, "checks": checks})

    outcome = {
        "schema": "adva.research.historical-acceptance-join.outcome.v0",
        "status": "PassedBoundedHistoricalJoin",
        "claim": "The canonical retrieval receipt joins to one pinned historical native success; this is not current execution or current acceptance.",
        "instances": evaluated,
        "checks": checks,
        "fresh_reuse": {
            "bytes": len(fresh_payload),
            "sha256": fresh_digest,
            "positive": actual["fresh-exact-reuse"],
            "negative": actual["fresh-failed-run-reuse"],
        },
        "cost": {
            "routes": 1,
            "counted_cases": len(evaluated),
            "search_candidates": 0,
            "construction_ns": constructed - started,
            "evaluation_and_verification_ns": verified - constructed,
            "serialization_ns": None,
            "serialized_bytes": None,
            "ru_maxrss_kib_before_serialization": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "implementation_correction_replays": 1,
        },
        "proposed_word": {
            "word": "historical acceptance join",
            "state": "Proposed",
            "role": "join an exact retrieval receipt to a separately pinned successful native run without upgrading historical evidence to current acceptance",
            "input": "reference-handoff receipt plus pinned consumer, budgets, workflow run/job, case and native outcome",
            "output_relation": "HistoricallyJoined/NativeAcceptedAtPinnedRun or a coordinate-specific refusal/obstruction",
            "applicability": "both records expose the exact shared fixture coordinates and the native record exposes a complete consumer and successful run coordinate",
            "witness": "eight canonical fixed cases plus one fresh positive and one fresh failed-run reuse",
            "refusal_conditions": [
                "repository, fixture path/blob/length/digest, or byte budget differs",
                "retrieval is not exact",
                "native evidence lacks a complete consumer or workflow coordinate",
                "workflow conclusion is not success",
                "case or consumer/native outcome differs",
                "either evidence side is missing"
            ],
            "expansion": "compare the six shared retrieval/fixture coordinates, verify the independently pinned consumer and its byte/work budgets, verify run/job success and the matching-case native outcome, then emit only the pinned historical relation",
            "counterexample": "the same fixture digest paired with a failed workflow remains DigestProjection/Match but is Refused/WorkflowNotSuccessful",
            "replay": "python3 run.py",
            "residual": "no current Rust execution, no temporal freshness theorem, no independent implementation, no semantic ResearchCertificate acceptance, no 0090 coverage, no 0092 promotion and no M6 filler"
        },
        "claim_boundary": "Finite evidence plumbing only. Additive-zero and multiplicative-unit normalization are untouched; no arithmetic theorem or global universality claim is made."
    }
    pre_serialization = time.perf_counter_ns()
    probe = canonical_bytes(outcome)
    outcome["cost"]["serialization_ns"] = time.perf_counter_ns() - pre_serialization
    # Resolve length to a fixed point because the decimal length is itself serialized.
    previous = -1
    while previous != outcome["cost"]["serialized_bytes"]:
        previous = outcome["cost"]["serialized_bytes"]
        outcome["cost"]["serialized_bytes"] = len(canonical_bytes(outcome))
    data = canonical_bytes(outcome)
    (ROOT / "outcome.json").write_bytes(data)
    print(json.dumps({
        "status": outcome["status"],
        "cases": len(evaluated),
        "checks": checks,
        "serialized_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "ru_maxrss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
