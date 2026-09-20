#!/usr/bin/env python3
"""Create one canonical snapshot after validating a trusted local ledger.

Original contribution under Unknown v0.3. ChatGPT (OpenAI), through Mingli
Yuan's authorized account proxy; not his review or correctness guarantee.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import signal
import sqlite3
import time

PROFILE = "adva.research.commit-snapshot-builder.v0"
SNAPSHOT_PROFILE = "adva.research.commit-snapshot.v0"
MAX_WIRE = 262144
MAX_DB = 1048576


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)


def digest_bytes(raw):
    return hashlib.sha256(raw).hexdigest()


def read(path):
    raw = Path(path).read_bytes()
    if len(raw) > MAX_WIRE:
        raise ValueError("request:wire-byte-limit")

    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError("json:duplicate-key")
            out[key] = value
        return out

    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("json:nonfinite")))


def load_engine():
    path = Path(__file__).resolve().parents[1] / "commit_state_reconcile" / "receive.py"
    spec = importlib.util.spec_from_file_location("snapshot_reconcile_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("adapter:loader")
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    engine = adapter.load_engine()
    return adapter, engine


def main(request_path, ledger_path, output_path):
    started = time.perf_counter()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        request = read(request_path)
        if type(request) is not dict or set(request) != {"profile", "expected_request", "candidate"}:
            raise ValueError("request:fields")
        if request["profile"] != PROFILE:
            raise ValueError("request:profile")
        expected, candidate = request["expected_request"], request["candidate"]
        adapter, engine = load_engine()
        engine.WORK = 0
        engine.envelope(candidate)
        ledger = Path(ledger_path)
        if not ledger.is_file():
            raise ValueError("ledger:missing")
        if ledger.stat().st_size > MAX_DB:
            raise ValueError("ledger:database-byte-limit")
        ledger_raw = ledger.read_bytes()
        ledger_sha256 = digest_bytes(ledger_raw)
        checkers = engine.fingerprint()
        connection = sqlite3.connect(ledger.resolve().as_uri() + "?mode=ro", uri=True,
                                     timeout=0.1, isolation_level=None)
        try:
            allowance, stored = engine.ledger_state(connection, expected, checkers)
        finally:
            connection.close()
        transition = None
        state = "empty"
        if stored is not None:
            key, payload_text, result = stored
            payload = json.loads(payload_text)
            if key != candidate["transition_key"] or canonical(payload) != canonical(candidate):
                raise ValueError("ledger:stored-transition-does-not-match-query")
            transition = {"transition_key": key, "payload": payload, "stored_result": result}
            state = "committed"
        sources = {}
        for path in (Path(__file__), Path(adapter.__file__),
                     Path(__file__).resolve().parents[1] / "decision_ledger_contention" / "receive.py",
                     Path(__file__).resolve().parents[1] / "decision_ledger" / "receive.py"):
            sources[str(path.resolve().relative_to(Path(__file__).resolve().parents[2]))] = digest_bytes(path.read_bytes())
        body = {
            "source_profile": "adva.research.decision-ledger-contention.v0",
            "source_ledger_sha256": ledger_sha256,
            "expected_request": expected,
            "candidate": candidate,
            "checker_fingerprint": checkers,
            "allowance": allowance,
            "snapshot_state": state,
            "transition": transition,
            "builder_source_sha256": sources,
        }
        envelope = {
            "profile": SNAPSHOT_PROFILE,
            "version": 0,
            "body": body,
            "body_sha256": digest_bytes(canonical(body).encode("utf-8")),
        }
        raw = (canonical(envelope) + "\n").encode("utf-8")
        output = Path(output_path)
        if output.exists():
            raise ValueError("snapshot:output-exists")
        output.write_bytes(raw)
        report = {
            "profile": PROFILE,
            "outcome": "SnapshotCreated",
            "snapshot_file_sha256": digest_bytes(raw),
            "source_ledger_sha256": ledger_sha256,
            "snapshot_state": state,
            "work_units": engine.WORK,
            "wall_seconds": time.perf_counter() - started,
            "parent_checked": False,
            "debit_delta": 0,
            "retry_authorized": False,
            "native_authority": False,
        }
        print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--request", required=True)
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    main(args.request, args.ledger, args.output)
