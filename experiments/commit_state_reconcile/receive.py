#!/usr/bin/env python3
"""Read-only finite reconciliation for one trusted continuation ledger.

Original contribution under Unknown v0.3. ChatGPT (OpenAI), through Mingli
Yuan's authorized account proxy; not his review or correctness guarantee.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import signal
import sqlite3
import time

PROFILE = "adva.research.commit-state-reconcile.v0"
MAX_WIRE = 196608
MAX_DB = 1048576


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def read(path):
    raw = Path(path).read_bytes()
    if len(raw) > MAX_WIRE:
        raise ValueError("request:wire-byte-limit")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result: raise ValueError("json:duplicate-key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=unique,
                      parse_constant=lambda _: (_ for _ in ()).throw(ValueError("json:nonfinite")))


def load_engine():
    path = Path(__file__).resolve().parents[1] / "decision_ledger_contention/receive.py"
    spec = importlib.util.spec_from_file_location("reconcile_adapter", path)
    if spec is None or spec.loader is None: raise RuntimeError("adapter:loader")
    adapter = importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
    adapter.constrain_process()
    return adapter.build_engine()


def main(request_path, ledger_path):
    started = time.perf_counter(); outcome = "UnknownCommitState"; reason = "unstarted"
    expected = candidate = stored_result = allowance = ledger_digest = None
    work = 0
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError("wall-limit")))
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        request = read(request_path)
        if type(request) is not dict or set(request) != {"profile","expected_request","candidate"}:
            raise ValueError("request:fields")
        if request["profile"] != PROFILE: raise ValueError("request:profile")
        expected, candidate = request["expected_request"], request["candidate"]
        engine = load_engine(); engine.WORK = 0
        engine.envelope(candidate)
        path = Path(ledger_path)
        if not path.is_file(): raise ValueError("ledger:missing")
        if path.stat().st_size > MAX_DB: raise ValueError("ledger:database-byte-limit")
        ledger_digest = hashlib.sha256(path.read_bytes()).hexdigest()
        connection = sqlite3.connect(path.resolve().as_uri()+"?mode=ro", uri=True,
                                     timeout=0.1, isolation_level=None)
        try:
            allowance, stored = engine.ledger_state(connection, expected, engine.fingerprint())
        finally:
            connection.close()
        work = engine.WORK
        if stored is None:
            outcome, reason = "ProvenUncommittedLedger", "valid-selected-ledger-has-no-transition"
        else:
            key, payload, result = stored
            if key == candidate["transition_key"] and payload == canonical(candidate):
                outcome, reason, stored_result = "StoredCommitted", "exact-candidate-and-result-found", result
            else:
                reason = "stored-transition-does-not-match-query"
    except Exception as error:
        try: work = engine.WORK
        except Exception: pass
        reason = type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
    report = {"profile":PROFILE,"outcome":outcome,"reason":reason,
              "expected_request":expected,"candidate":candidate,"stored_result":stored_result,
              "allowance":allowance,"ledger_sha256":ledger_digest,"parent_checked":False,
              "debit_delta":0,"retry_authorized":False,"work_units":work,
              "wall_seconds":time.perf_counter()-started,"native_authority":False,
              "close_authorized":False,"free_authorized":False}
    print(json.dumps(report,sort_keys=True,ensure_ascii=False,allow_nan=False))


if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--request",required=True); p.add_argument("--ledger",required=True)
    a=p.parse_args(); main(a.request,a.ledger)
