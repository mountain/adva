#!/usr/bin/env python3
"""Original test-only transaction gate, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy; not his
review or correctness guarantee. The gate changes the schedule only. Its
wait remains inside the inherited receiver's three-second wall deadline.
"""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engine", choices=("new", "legacy"), required=True)
    parser.add_argument("--ready-fd", type=int, required=True)
    parser.add_argument("--release-fd", type=int, required=True)
    parser.add_argument("receiver_args", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    tail = args.receiver_args
    if tail[:1] == ["--"]:
        tail = tail[1:]
    path = Path(__file__).with_name("receive.py")
    spec = importlib.util.spec_from_file_location("contention_adapter", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("contention adapter loader unavailable")
    adapter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(adapter)
    adapter.constrain_process()
    engine = adapter.build_engine() if args.engine == "new" else adapter.load_legacy()
    original_sql = engine.sql
    gated = False

    def sql(connection, statement, parameters=()):
        nonlocal gated
        cursor = original_sql(connection, statement, parameters)
        if statement == "BEGIN IMMEDIATE" and not gated:
            gated = True
            wire = json.dumps({"event": "begin-immediate-acquired", "pid": os.getpid(),
                               "work_units": engine.WORK}, sort_keys=True).encode() + b"\n"
            if len(wire) > 4096 or os.write(args.ready_fd, wire) != len(wire):
                raise engine.Refusal("ImplementationFailure", "gate:ready-write")
            if not os.read(args.release_fd, 1):
                raise engine.Refusal("ImplementationFailure", "gate:release-eof")
        return cursor

    engine.sql = sql
    try:
        if args.engine == "new":
            adapter.run_engine(engine, tail)
        else:
            sys.argv = [str(path), *tail]
            engine.main()
    finally:
        os.close(args.ready_fd)
        os.close(args.release_fd)


if __name__ == "__main__":
    main()
