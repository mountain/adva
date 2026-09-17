#!/usr/bin/env python3
"""Original finite SQLite-contention adapter, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy. Account use
is not his review or a correctness guarantee. This new profile delegates the
arithmetic and single-slot storage rules to the unchanged ledger receiver.
"""
import contextlib
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import resource
import sqlite3
import sys

PROFILE = "adva.research.decision-ledger-contention.v0"


def constrain_process():
    """Only lower limits; the supervisor independently bounds wall time."""
    for kind, cap in ((resource.RLIMIT_AS, 134217728), (resource.RLIMIT_CPU, 3)):
        soft, hard = resource.getrlimit(kind)
        new_hard = cap if hard == resource.RLIM_INFINITY else min(hard, cap)
        new_soft = new_hard if soft == resource.RLIM_INFINITY else min(soft, new_hard)
        resource.setrlimit(kind, (new_soft, new_hard))


def load_legacy():
    path = Path(__file__).resolve().parents[1] / "decision_ledger" / "receive.py"
    spec = importlib.util.spec_from_file_location("contention_legacy_receiver", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("ledger receiver loader unavailable")
    engine = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine)
    return engine


def build_engine():
    engine = load_legacy()
    engine.PROFILE = PROFILE
    engine.CONTENTION_DIAGNOSTIC = None
    old_fingerprint, old_sql = engine.fingerprint, engine.sql

    def fingerprint():
        result = old_fingerprint()
        result["experiments/decision_ledger_contention/receive.py"] = hashlib.sha256(
            Path(__file__).read_bytes()).hexdigest()
        engine.tick()
        return result

    def classify(error, connection, statement):
        code = getattr(error, "sqlite_errorcode", None)
        primary = code & 255 if type(code) is int else None
        active = connection.in_transaction if connection is not None else None
        engine.CONTENTION_DIAGNOSTIC = {
            "sqlite_errorcode": code,
            "sqlite_errorname": getattr(error, "sqlite_errorname", None),
            "primary_code": primary,
            "statement": statement,
            "in_transaction": active,
        }
        if primary == 5 and active is False:
            outcome, reason = "LedgerBusy", "ledger:sqlite-busy-before-transaction"
        elif primary in (11, 26):
            outcome, reason = "InvalidLedger", "ledger:sqlite-invalid-database"
        else:
            # LOCKED(6), IO errors and unknown codes have no automatic retry rule.
            outcome, reason = "UnknownStorage", "ledger:sqlite-storage-state-unresolved"
        raise engine.Refusal(outcome, reason) from error

    class Cursor:
        """Preserve classification when SQLite defers an error to row fetching."""
        def __init__(self, cursor, connection, statement):
            self.cursor, self.connection, self.statement = cursor, connection, statement

        def fetchone(self):
            try:
                return self.cursor.fetchone()
            except sqlite3.DatabaseError as error:
                classify(error, self.connection, self.statement)

        def fetchall(self):
            try:
                return self.cursor.fetchall()
            except sqlite3.DatabaseError as error:
                classify(error, self.connection, self.statement)

    def sql(connection, statement, parameters=()):
        try:
            return Cursor(old_sql(connection, statement, parameters), connection, statement)
        except sqlite3.DatabaseError as error:
            classify(error, connection, statement)

    def connect_existing(path):
        if not path.is_file():
            raise engine.Refusal("MissingLedger", "ledger:existing-file-required")
        if path.stat().st_size > engine.MAX_DB:
            raise engine.Refusal("InvalidLedger", "ledger:database-byte-limit")
        try:
            return sqlite3.connect(path.resolve().as_uri() + "?mode=rw", uri=True,
                                   timeout=0.1, isolation_level=None)
        except sqlite3.DatabaseError as error:
            # No connection exists here, so pre-transaction BUSY is not inferred.
            classify(error, None, "CONNECT mode=rw")

    engine.fingerprint = fingerprint
    engine.sql = sql
    engine.connect_existing = connect_existing
    return engine


def run_engine(engine, argv):
    """Run the unchanged control flow and add a separate storage diagnostic."""
    previous = sys.argv
    capture = io.StringIO()
    try:
        sys.argv = [str(Path(__file__)), *argv]
        with contextlib.redirect_stdout(capture):
            engine.main()
    finally:
        sys.argv = previous
    report = json.loads(capture.getvalue())
    report["sqlite_diagnostic"] = engine.CONTENTION_DIAGNOSTIC
    print(json.dumps(report, sort_keys=True, ensure_ascii=False, allow_nan=False))


def main():
    constrain_process()
    run_engine(build_engine(), sys.argv[1:])


if __name__ == "__main__":
    main()
