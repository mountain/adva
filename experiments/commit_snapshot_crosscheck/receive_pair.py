#!/usr/bin/env python3
"""Receive two pinned snapshots and proceed only on projection agreement.

This receiver imports no SQLite module and accepts no ledger path. Original
contribution under Unknown v0.3. ChatGPT (OpenAI), through Mingli Yuan's
authorized account proxy; not his review or correctness guarantee.
"""
import argparse
import hashlib
import json
from pathlib import Path
import signal
import time

PROFILE = "adva.research.commit-snapshot-pair-receive.v0"
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


def parse(raw, label):
    if len(raw) > MAX_WIRE:
        raise ValueError(label + ":wire-byte-limit")

    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError(label + ":duplicate-key")
            out[key] = value
        return out

    tick()
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError(label + ":nonfinite")))


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


def read_snapshot(path, pin, label):
    hex_digest(pin, label + ":pin")
    raw = Path(path).read_bytes()
    if sha(raw) != pin:
        raise ValueError(label + ":file-pin")
    snapshot = parse(raw, label)
    if raw != (canonical(snapshot) + "\n").encode("utf-8"):
        raise ValueError(label + ":noncanonical-file")
    exact_dict(snapshot, ("profile", "version", "body", "body_sha256"), label)
    if snapshot["profile"] != SNAPSHOT_PROFILE or snapshot["version"] != 0:
        raise ValueError(label + ":profile-or-version")
    hex_digest(snapshot["body_sha256"], label + ":body")
    body = snapshot["body"]
    if sha(canonical(body).encode("utf-8")) != snapshot["body_sha256"]:
        raise ValueError(label + ":body-digest")
    exact_dict(body, ("source_profile", "source_ledger_sha256", "expected_request", "candidate",
                      "checker_fingerprint", "allowance", "snapshot_state", "transition",
                      "builder_source_sha256"), label + ":body")
    if body["source_profile"] != SOURCE_PROFILE:
        raise ValueError(label + ":source-profile")
    hex_digest(body["source_ledger_sha256"], label + ":source-ledger")
    for name in ("checker_fingerprint", "builder_source_sha256"):
        mapping = body[name]
        if type(mapping) is not dict or not mapping:
            raise ValueError(label + ":" + name)
        for key, value in mapping.items():
            if type(key) is not str or not key:
                raise ValueError(label + ":" + name + ":key")
            hex_digest(value, label + ":" + name)
    return body


def validate_projection(projection, expected, candidate):
    if projection["source_profile"] != SOURCE_PROFILE:
        raise ValueError("projection:source-profile")
    if canonical(projection["expected_request"]) != canonical(expected):
        raise ValueError("projection:expected-binding")
    if canonical(projection["candidate"]) != canonical(candidate):
        raise ValueError("projection:candidate-binding")
    exact_dict(candidate, ("profile", "transition_key", "checkpoint_receipt"), "candidate")
    if candidate["profile"] != SOURCE_PROFILE or type(candidate["transition_key"]) is not str:
        raise ValueError("candidate:profile-or-key")
    allowance = projection["allowance"]
    balance(allowance, "allowance")
    initial = expected.get("allowance") if type(expected) is dict else None
    balance(initial, "initial-allowance")
    state = projection["snapshot_state"]
    stored_result = None
    if state == "empty":
        if projection["transition"] is not None or canonical(allowance) != canonical(initial):
            raise ValueError("empty:transition-or-allowance")
        outcome = "ProvenUncommittedLedger"
    elif state == "committed":
        transition = projection["transition"]
        exact_dict(transition, ("transition_key", "payload", "stored_result"), "transition")
        if transition["transition_key"] != candidate["transition_key"] or canonical(transition["payload"]) != canonical(candidate):
            raise ValueError("transition:binding")
        result = transition["stored_result"]
        exact_dict(result, ("outcome", "reason", "checkpoint_retained", "allowance_after",
                            "semantic_delta"), "result")
        if initial["remaining"] <= 0:
            raise ValueError("committed:initial-allowance")
        after = {"grant": initial["grant"], "spent": initial["spent"] + 1,
                 "remaining": initial["remaining"] - 1}
        if canonical(after) != canonical(allowance) or canonical(result["allowance_after"]) != canonical(after):
            raise ValueError("committed:allowance")
        if result["outcome"] != "AcceptedCheckpointContinuation" or result["reason"] != "prefix-and-declared-next-step-checked":
            raise ValueError("result:scope")
        if canonical(result["semantic_delta"]) != canonical(DELTA):
            raise ValueError("result:delta")
        receipt = candidate["checkpoint_receipt"]
        if type(receipt) is not dict or canonical(result["checkpoint_retained"]) != canonical(receipt.get("checkpoint")):
            raise ValueError("result:checkpoint-binding")
        if canonical(receipt.get("allowance_after")) != canonical(after):
            raise ValueError("candidate:allowance-binding")
        outcome, stored_result = "StoredCommitted", result
    else:
        raise ValueError("projection:snapshot-state")
    return outcome, state, allowance, stored_result


def main(request_path, left_path, right_path):
    global WORK
    WORK = 0
    started = time.perf_counter()
    outcome, reason = "UnknownCommitState", "unstarted"
    state = allowance = stored_result = projection_sha256 = None
    left_sources = right_sources = None
    expected = candidate = None
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        request = parse(Path(request_path).read_bytes(), "request")
        exact_dict(request, ("profile", "expected_request", "candidate", "left_snapshot_sha256",
                             "right_snapshot_sha256"), "request")
        if request["profile"] != PROFILE:
            raise ValueError("request:profile")
        expected, candidate = request["expected_request"], request["candidate"]
        left = read_snapshot(left_path, request["left_snapshot_sha256"], "left")
        right = read_snapshot(right_path, request["right_snapshot_sha256"], "right")
        left_sources, right_sources = left["builder_source_sha256"], right["builder_source_sha256"]
        if canonical(left_sources) == canonical(right_sources):
            raise ValueError("builders:provenance-not-distinct")
        left_projection, right_projection = dict(left), dict(right)
        del left_projection["builder_source_sha256"]
        del right_projection["builder_source_sha256"]
        left_bytes = canonical(left_projection).encode("utf-8")
        right_bytes = canonical(right_projection).encode("utf-8")
        if left_bytes != right_bytes:
            raise ValueError("builders:projection-disagreement")
        projection_sha256 = sha(left_bytes)
        outcome, state, allowance, stored_result = validate_projection(
            left_projection, expected, candidate)
        reason = "distinct-builders-agree-on-pinned-ledger-projection"
    except Exception as error:
        reason = type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    print(json.dumps({
        "profile": PROFILE,
        "outcome": outcome,
        "reason": reason,
        "expected_request": expected,
        "candidate": candidate,
        "stored_result": stored_result,
        "allowance": allowance,
        "snapshot_state": state,
        "projection_sha256": projection_sha256,
        "left_builder_source_sha256": left_sources,
        "right_builder_source_sha256": right_sources,
        "parent_checked": False,
        "debit_delta": 0,
        "retry_authorized": False,
        "sqlite_opened": False,
        "work_units": WORK,
        "wall_seconds": time.perf_counter() - started,
        "native_authority": False,
        "close_authorized": False,
        "free_authorized": False,
    }, sort_keys=True, ensure_ascii=True, allow_nan=False))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    args = parser.parse_args()
    main(args.request, args.left, args.right)
