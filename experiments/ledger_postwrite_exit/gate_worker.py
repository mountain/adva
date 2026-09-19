#!/usr/bin/env python3
"""Pause the unchanged ledger receiver after writes and before COMMIT.

Original test wrapper under Unknown v0.3. ChatGPT (OpenAI), through Mingli
Yuan's authorized account proxy; not his review or correctness guarantee.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ready-fd", type=int, required=True)
    p.add_argument("--release-fd", type=int, required=True)
    p.add_argument("receiver_args", nargs=argparse.REMAINDER)
    a = p.parse_args()
    tail = a.receiver_args[1:] if a.receiver_args[:1] == ["--"] else a.receiver_args
    path = Path(__file__).resolve().parents[1] / "decision_ledger_contention/receive.py"
    spec = importlib.util.spec_from_file_location("postwrite_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("adapter-loader-unavailable")
    adapter = importlib.util.module_from_spec(spec); spec.loader.exec_module(adapter)
    adapter.constrain_process()
    engine = adapter.build_engine()
    original_sql, gated = engine.sql, False

    def sql(connection, statement, parameters=()):
        nonlocal gated
        if statement == "COMMIT" and not gated:
            gated = True
            rows = connection.execute("SELECT slot, transition_key FROM transitions ORDER BY slot").fetchall()
            balance = connection.execute("SELECT allowance_json FROM meta WHERE singleton=1").fetchone()
            wire = json.dumps({"event": "writes-complete-before-commit", "pid": os.getpid(),
                               "work_units": engine.WORK, "in_transaction": connection.in_transaction,
                               "tentative_rows": rows, "tentative_allowance": json.loads(balance[0])},
                              sort_keys=True).encode() + b"\n"
            if len(wire) > 4096 or os.write(a.ready_fd, wire) != len(wire):
                raise engine.Refusal("ImplementationFailure", "gate:ready-write")
            if not os.read(a.release_fd, 1):
                raise engine.Refusal("ImplementationFailure", "gate:release-eof")
        return original_sql(connection, statement, parameters)

    engine.sql = sql
    try:
        adapter.run_engine(engine, tail)
    finally:
        os.close(a.ready_fd); os.close(a.release_fd)


if __name__ == "__main__":
    main()
