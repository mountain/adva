#!/usr/bin/env python3
"""Independently derive the frozen ledger snapshot projection.

This implementation does not import the inherited snapshot builder or ledger
validator. Original contribution under Unknown v0.3. ChatGPT (OpenAI), through
Mingli Yuan's authorized account proxy; not his review or correctness guarantee.
"""
import argparse
import hashlib
import json
from pathlib import Path
import signal
import sqlite3
import time

PROFILE = "adva.research.commit-snapshot-builder.v0"
SNAPSHOT_PROFILE = "adva.research.commit-snapshot.v0"
SOURCE_PROFILE = "adva.research.decision-ledger-contention.v0"
MAX_WIRE = 262144
MAX_DB = 1048576
WORK = 0
META_SQL = ("CREATE TABLE meta (singleton INTEGER PRIMARY KEY CHECK(singleton = 1), "
            "profile TEXT NOT NULL, expected_json TEXT NOT NULL, "
            "checker_json TEXT NOT NULL, initial_allowance_json TEXT NOT NULL, "
            "allowance_json TEXT NOT NULL)")
TRANSITION_SQL = ("CREATE TABLE transitions (slot INTEGER PRIMARY KEY CHECK(slot = 1), "
                  "transition_key TEXT NOT NULL, payload_json TEXT NOT NULL, "
                  "result_json TEXT NOT NULL)")
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
        raise ValueError("builder:work-limit")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def digest(raw):
    tick()
    return hashlib.sha256(raw).hexdigest()


def parse_bytes(raw, label):
    if len(raw) > MAX_WIRE:
        raise ValueError(label + ":wire-byte-limit")

    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(label + ":duplicate-key")
            result[key] = value
        return result

    tick()
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError(label + ":nonfinite")))


def exact_dict(value, fields, label):
    tick()
    if type(value) is not dict or set(value) != set(fields):
        raise ValueError(label + ":fields")


def stored(text, label):
    if type(text) is not str:
        raise ValueError(label + ":text")
    value = parse_bytes(text.encode("utf-8"), label)
    if canonical(value) != text:
        raise ValueError(label + ":noncanonical")
    return value


def balance(value, label):
    exact_dict(value, ("grant", "spent", "remaining"), label)
    tick(3)
    if not all(type(value[key]) is int for key in value):
        raise ValueError(label + ":integer")
    if not (1 <= value["grant"] <= 4 and 0 <= value["spent"] <= value["grant"]):
        raise ValueError(label + ":range")
    if value["remaining"] != value["grant"] - value["spent"]:
        raise ValueError(label + ":balance")


def candidate_shape(candidate):
    exact_dict(candidate, ("profile", "transition_key", "checkpoint_receipt"), "candidate")
    if candidate["profile"] != SOURCE_PROFILE:
        raise ValueError("candidate:profile")
    key = candidate["transition_key"]
    if type(key) is not str or not (1 <= len(key) <= 80):
        raise ValueError("candidate:key")


def checker_fingerprint(root):
    result = {}
    for directory in ("decision_ledger", "decision_checkpoint", "decision_scale_composition",
                      "decision_scale", "finite_decision", "probability_receipt"):
        path = root / directory / "receive.py"
        result["experiments/" + directory + "/receive.py"] = digest(path.read_bytes())
    path = root / "decision_ledger_contention" / "receive.py"
    result["experiments/decision_ledger_contention/receive.py"] = digest(path.read_bytes())
    return result


def main(request_path, ledger_path, output_path):
    global WORK
    WORK = 0
    started = time.perf_counter()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        request = parse_bytes(Path(request_path).read_bytes(), "request")
        exact_dict(request, ("profile", "expected_request", "candidate"), "request")
        if request["profile"] != PROFILE:
            raise ValueError("request:profile")
        expected, candidate = request["expected_request"], request["candidate"]
        candidate_shape(candidate)
        ledger = Path(ledger_path)
        if not ledger.is_file() or ledger.stat().st_size > MAX_DB:
            raise ValueError("ledger:missing-or-size")
        ledger_raw = ledger.read_bytes()
        ledger_sha256 = digest(ledger_raw)
        root = Path(__file__).resolve().parents[1]
        expected_checkers = checker_fingerprint(root)
        connection = sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True,
                                     timeout=0.1, isolation_level=None)
        try:
            tick()
            schema = connection.execute(
                "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
            if schema != [("meta", META_SQL), ("transitions", TRANSITION_SQL)]:
                raise ValueError("ledger:schema")
            tick()
            if connection.execute("SELECT type, name FROM sqlite_master WHERE type != 'table'").fetchall():
                raise ValueError("ledger:unexpected-schema-object")
            tick()
            meta = connection.execute(
                "SELECT singleton, profile, expected_json, checker_json, "
                "initial_allowance_json, allowance_json FROM meta").fetchall()
            if len(meta) != 1:
                raise ValueError("ledger:metadata-row-count")
            singleton, profile, expected_text, checker_text, initial_text, current_text = meta[0]
            if singleton != 1 or type(singleton) is not int or profile != SOURCE_PROFILE:
                raise ValueError("ledger:metadata-profile")
            saved_expected = stored(expected_text, "ledger:expected")
            saved_checkers = stored(checker_text, "ledger:checkers")
            initial = stored(initial_text, "ledger:initial")
            current = stored(current_text, "ledger:current")
            balance(initial, "ledger:initial")
            balance(current, "ledger:current")
            if canonical(saved_expected.get("allowance")) != canonical(initial):
                raise ValueError("ledger:initial-allowance-binding")
            if canonical(saved_checkers) != canonical(expected_checkers):
                raise ValueError("ledger:checker-fingerprint")
            if canonical(saved_expected) != canonical(expected):
                raise ValueError("ledger:expected-binding")
            tick()
            rows = connection.execute(
                "SELECT slot, transition_key, payload_json, result_json FROM transitions").fetchall()
            if len(rows) > 1:
                raise ValueError("ledger:transition-capacity")
        finally:
            connection.close()

        state = "empty"
        transition = None
        if not rows:
            if canonical(current) != canonical(initial):
                raise ValueError("ledger:empty-balance")
        else:
            slot, key, payload_text, result_text = rows[0]
            if type(slot) is not int or slot != 1:
                raise ValueError("ledger:slot")
            payload = stored(payload_text, "ledger:payload")
            result = stored(result_text, "ledger:result")
            candidate_shape(payload)
            if key != payload["transition_key"] or key != candidate["transition_key"]:
                raise ValueError("ledger:key-binding")
            if canonical(payload) != canonical(candidate):
                raise ValueError("ledger:candidate-binding")
            exact_dict(result, ("outcome", "reason", "checkpoint_retained", "allowance_after",
                                "semantic_delta"), "ledger:result")
            if initial["remaining"] <= 0:
                raise ValueError("ledger:committed-without-allowance")
            after = {"grant": initial["grant"], "spent": initial["spent"] + 1,
                     "remaining": initial["remaining"] - 1}
            if canonical(current) != canonical(after) or canonical(result["allowance_after"]) != canonical(after):
                raise ValueError("ledger:committed-balance")
            if result["outcome"] != "AcceptedCheckpointContinuation" or result["reason"] != "prefix-and-declared-next-step-checked":
                raise ValueError("ledger:result-scope")
            if canonical(result["semantic_delta"]) != canonical(DELTA):
                raise ValueError("ledger:result-delta")
            receipt = payload["checkpoint_receipt"]
            if type(receipt) is not dict or canonical(result["checkpoint_retained"]) != canonical(receipt.get("checkpoint")):
                raise ValueError("ledger:checkpoint-binding")
            if canonical(receipt.get("allowance_after")) != canonical(after):
                raise ValueError("ledger:candidate-allowance-binding")
            state = "committed"
            transition = {"transition_key": key, "payload": payload, "stored_result": result}

        own = Path(__file__).resolve()
        body = {
            "source_profile": SOURCE_PROFILE,
            "source_ledger_sha256": ledger_sha256,
            "expected_request": expected,
            "candidate": candidate,
            "checker_fingerprint": expected_checkers,
            "allowance": current,
            "snapshot_state": state,
            "transition": transition,
            "builder_source_sha256": {
                str(own.relative_to(Path(__file__).resolve().parents[2])): digest(own.read_bytes())
            },
        }
        envelope = {"profile": SNAPSHOT_PROFILE, "version": 0, "body": body,
                    "body_sha256": digest(canonical(body).encode("utf-8"))}
        raw = (canonical(envelope) + "\n").encode("utf-8")
        output = Path(output_path)
        if output.exists():
            raise ValueError("snapshot:output-exists")
        output.write_bytes(raw)
        projection = dict(body)
        del projection["builder_source_sha256"]
        print(json.dumps({
            "profile": "adva.research.commit-snapshot-independent-builder.v0",
            "outcome": "SnapshotCreated",
            "snapshot_file_sha256": digest(raw),
            "projection_sha256": digest(canonical(projection).encode("utf-8")),
            "source_ledger_sha256": ledger_sha256,
            "snapshot_state": state,
            "work_units": WORK,
            "wall_seconds": time.perf_counter() - started,
            "parent_checked": False,
            "debit_delta": 0,
            "retry_authorized": False,
            "native_authority": False,
        }, sort_keys=True, separators=(",", ":")))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.request, args.ledger, args.output)
