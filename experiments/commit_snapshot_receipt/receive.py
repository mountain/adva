#!/usr/bin/env python3
"""Check a pinned commit snapshot without importing SQLite or opening a ledger.

Original contribution under Unknown v0.3. ChatGPT (OpenAI), through Mingli
Yuan's authorized account proxy; not his review or correctness guarantee.
"""
import argparse
import hashlib
import json
from pathlib import Path
import signal
import time

PROFILE = "adva.research.commit-snapshot-receive.v0"
SNAPSHOT_PROFILE = "adva.research.commit-snapshot.v0"
SOURCE_PROFILE = "adva.research.decision-ledger-contention.v0"
MAX_WIRE = 262144
WORK = 0
DELTA = [
    "complete saved two-step prefix independently rechecked",
    "pending third step checked at the same complete endpoint",
    "all four history entries retained without capacity increase",
    "one abstract attempt debit checked without external consumption",
]


def tick(count=1):
    global WORK
    WORK += count
    if WORK > 10000:
        raise ValueError("receiver:work-limit")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def sha(raw):
    tick()
    return hashlib.sha256(raw).hexdigest()


def parse(raw):
    if len(raw) > MAX_WIRE:
        raise ValueError("wire:byte-limit")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("json:duplicate-key")
            result[key] = value
        return result

    tick()
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("json:nonfinite")))


def exact_dict(value, fields, label):
    tick()
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(label + ":fields")


def hex_digest(value, label):
    tick()
    if type(value) is not str or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(label + ":sha256")


def balance(value, label):
    exact_dict(value, ("grant", "spent", "remaining"), label)
    tick(3)
    if not all(type(value[key]) is int for key in value):
        raise ValueError(label + ":integer")
    if not (1 <= value["grant"] <= 4 and 0 <= value["spent"] <= value["grant"]):
        raise ValueError(label + ":range")
    if value["remaining"] != value["grant"] - value["spent"]:
        raise ValueError(label + ":balance")


def check(request_path, snapshot_path):
    global WORK
    WORK = 0
    started = time.perf_counter()
    outcome, reason = "UnknownCommitState", "unstarted"
    stored_result = allowance = state = actual_file_sha = None
    expected = candidate = None
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        request_raw = Path(request_path).read_bytes()
        request = parse(request_raw)
        exact_dict(request, ("profile", "expected_request", "candidate", "snapshot_file_sha256"), "request")
        if request["profile"] != PROFILE:
            raise ValueError("request:profile")
        expected, candidate = request["expected_request"], request["candidate"]
        hex_digest(request["snapshot_file_sha256"], "request:snapshot-file")
        exact_dict(candidate, ("profile", "transition_key", "checkpoint_receipt"), "candidate")
        if candidate["profile"] != SOURCE_PROFILE or type(candidate["transition_key"]) is not str:
            raise ValueError("candidate:profile-or-key")
        snapshot_raw = Path(snapshot_path).read_bytes()
        actual_file_sha = sha(snapshot_raw)
        if actual_file_sha != request["snapshot_file_sha256"]:
            raise ValueError("snapshot:file-pin")
        snapshot = parse(snapshot_raw)
        if snapshot_raw != (canonical(snapshot) + "\n").encode("utf-8"):
            raise ValueError("snapshot:noncanonical-file")
        exact_dict(snapshot, ("profile", "version", "body", "body_sha256"), "snapshot")
        if snapshot["profile"] != SNAPSHOT_PROFILE or snapshot["version"] != 0:
            raise ValueError("snapshot:profile-or-version")
        hex_digest(snapshot["body_sha256"], "snapshot:body")
        body = snapshot["body"]
        if sha(canonical(body).encode("utf-8")) != snapshot["body_sha256"]:
            raise ValueError("snapshot:body-digest")
        exact_dict(body, ("source_profile", "source_ledger_sha256", "expected_request", "candidate",
                          "checker_fingerprint", "allowance", "snapshot_state", "transition",
                          "builder_source_sha256"), "body")
        if body["source_profile"] != SOURCE_PROFILE:
            raise ValueError("body:source-profile")
        hex_digest(body["source_ledger_sha256"], "body:source-ledger")
        for label in ("checker_fingerprint", "builder_source_sha256"):
            mapping = body[label]
            if type(mapping) is not dict or not mapping:
                raise ValueError(label + ":mapping")
            for name, value in mapping.items():
                if type(name) is not str or not name:
                    raise ValueError(label + ":name")
                hex_digest(value, label)
        if canonical(body["expected_request"]) != canonical(expected):
            raise ValueError("body:expected-binding")
        if canonical(body["candidate"]) != canonical(candidate):
            raise ValueError("body:candidate-binding")
        allowance = body["allowance"]
        balance(allowance, "allowance")
        initial = expected.get("allowance") if type(expected) is dict else None
        balance(initial, "initial-allowance")
        state = body["snapshot_state"]
        if state == "empty":
            if body["transition"] is not None or canonical(allowance) != canonical(initial):
                raise ValueError("empty:transition-or-allowance")
            outcome, reason = "ProvenUncommittedLedger", "pinned-valid-snapshot-has-no-transition"
        elif state == "committed":
            transition = body["transition"]
            exact_dict(transition, ("transition_key", "payload", "stored_result"), "transition")
            if transition["transition_key"] != candidate["transition_key"]:
                raise ValueError("transition:key-binding")
            if canonical(transition["payload"]) != canonical(candidate):
                raise ValueError("transition:payload-binding")
            result = transition["stored_result"]
            exact_dict(result, ("outcome", "reason", "checkpoint_retained", "allowance_after", "semantic_delta"), "result")
            after = {"grant": initial["grant"], "spent": initial["spent"] + 1,
                     "remaining": initial["remaining"] - 1}
            if initial["remaining"] <= 0 or canonical(after) != canonical(allowance):
                raise ValueError("committed:allowance")
            if canonical(result["allowance_after"]) != canonical(after):
                raise ValueError("result:allowance-binding")
            if result["outcome"] != "AcceptedCheckpointContinuation" or result["reason"] != "prefix-and-declared-next-step-checked":
                raise ValueError("result:scope")
            if canonical(result["semantic_delta"]) != canonical(DELTA):
                raise ValueError("result:delta")
            checkpoint = candidate["checkpoint_receipt"]
            if type(checkpoint) is not dict or canonical(result["checkpoint_retained"]) != canonical(checkpoint.get("checkpoint")):
                raise ValueError("result:checkpoint-binding")
            if canonical(checkpoint.get("allowance_after")) != canonical(after):
                raise ValueError("candidate:allowance-binding")
            stored_result = result
            outcome, reason = "StoredCommitted", "pinned-valid-snapshot-stores-exact-transition"
        else:
            raise ValueError("body:snapshot-state")
    except Exception as error:
        reason = type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    report = {
        "profile": PROFILE,
        "outcome": outcome,
        "reason": reason,
        "expected_request": expected,
        "candidate": candidate,
        "stored_result": stored_result,
        "allowance": allowance,
        "snapshot_state": state,
        "snapshot_file_sha256": actual_file_sha,
        "parent_checked": False,
        "debit_delta": 0,
        "retry_authorized": False,
        "sqlite_opened": False,
        "work_units": WORK,
        "wall_seconds": time.perf_counter() - started,
        "native_authority": False,
        "close_authorized": False,
        "free_authorized": False,
    }
    print(json.dumps(report, sort_keys=True, ensure_ascii=True, allow_nan=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    check(args.request, args.snapshot)
