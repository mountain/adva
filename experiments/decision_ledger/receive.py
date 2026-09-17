#!/usr/bin/env python3
"""Original bounded receiver-owned SQLite continuation ledger, Unknown v0.3.

ChatGPT (OpenAI), through Mingli Yuan's authorized account proxy. Account use
is not his review or a correctness guarantee. Only trusted sequential local
storage and the frozen experiment are covered; no external task is executed.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import signal
import sqlite3
import time

PROFILE = "adva.research.decision-ledger.v0"
WORK = 0
PARENT = None
MAX_WIRE = 196608
MAX_DB = 1048576
DELTA = ["complete saved two-step prefix independently rechecked",
         "pending third step checked at the same complete endpoint",
         "all four history entries retained without capacity increase",
         "one abstract attempt debit checked without external consumption"]
META_SQL = ("CREATE TABLE meta (singleton INTEGER PRIMARY KEY CHECK(singleton = 1), "
            "profile TEXT NOT NULL, expected_json TEXT NOT NULL, "
            "checker_json TEXT NOT NULL, initial_allowance_json TEXT NOT NULL, "
            "allowance_json TEXT NOT NULL)")
TRANSITION_SQL = ("CREATE TABLE transitions (slot INTEGER PRIMARY KEY CHECK(slot = 1), "
                  "transition_key TEXT NOT NULL, payload_json TEXT NOT NULL, "
                  "result_json TEXT NOT NULL)")


class Refusal(Exception):
    def __init__(self, outcome, reason):
        self.outcome, self.reason = outcome, reason


def demand(ok, reason):
    if not ok:
        raise ValueError(reason)


def tick(count=1):
    global WORK
    # Reserve the final unit for a mandatory rollback on refusal.
    if WORK + count > 9999:
        raise Refusal("UnknownBudget", "receiver-work-limit")
    WORK += count


def deadline(_signum, _frame):
    raise Refusal("UnknownBudget", "receiver-wall-limit")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def parse(text):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            demand(key not in result, "json:duplicate-key")
            result[key] = value
        return result

    def constant(_value):
        raise ValueError("json:nonfinite")

    tick()
    return json.loads(text, object_pairs_hook=unique, parse_constant=constant)


def read(path, maximum=MAX_WIRE):
    with Path(path).open("rb") as stream:
        raw = stream.read(maximum + 1)
    if len(raw) > maximum:
        raise Refusal("UnknownBudget", "wire-byte-limit")
    return parse(raw)


def keys(value, names, label):
    demand(type(value) is dict and set(value) == set(names), label + ":fields")


def balance(value):
    keys(value, ("grant", "spent", "remaining"), "allowance")
    tick(3)
    demand(all(type(value[key]) is int for key in value), "allowance:integer-type")
    demand(1 <= value["grant"] <= 4 and 0 <= value["spent"] <= value["grant"],
           "allowance:bound")
    demand(value["remaining"] == value["grant"] - value["spent"], "allowance:balance")


def envelope(value):
    keys(value, ("profile", "transition_key", "checkpoint_receipt"), "candidate")
    demand(value["profile"] == PROFILE, "profile:unsupported")
    key = value["transition_key"]
    demand(type(key) is str and 1 <= len(key) <= 80, "transition-key:label")
    tick()


def fingerprint():
    root = Path(__file__).resolve().parents[1]
    names = ("decision_ledger", "decision_checkpoint", "decision_scale_composition",
             "decision_scale", "finite_decision", "probability_receipt")
    result = {}
    for name in names:
        path = root / name / "receive.py"
        result["experiments/" + name + "/receive.py"] = hashlib.sha256(path.read_bytes()).hexdigest()
        tick()
    return result


def load_parent():
    global PARENT
    path = Path(__file__).resolve().parents[1] / "decision_checkpoint" / "receive.py"
    spec = importlib.util.spec_from_file_location("decision_ledger_parent", path)
    demand(spec is not None and spec.loader is not None, "parent:loader")
    PARENT = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PARENT)
    PARENT.load_parent()


def parent_call(function, *args):
    global WORK
    tick(0)
    # Reserve rollback capacity inside the unchanged ancestors' 10000 cap.
    # The reserved unit is not actual work and is removed on return.
    PARENT.WORK = WORK + 1
    try:
        return function(*args)
    except PARENT.Refusal as error:
        raise Refusal(error.outcome, "parent:" + error.reason) from error
    finally:
        WORK = PARENT.WORK - 1


def sql(connection, statement, parameters=()):
    tick()
    return connection.execute(statement, parameters)


def stored_json(text):
    demand(type(text) is str, "ledger:json-text")
    value = parse(text)
    demand(canonical(value) == text, "ledger:noncanonical-json")
    return value


def ledger_state(connection, expected, checkers):
    """Validate the finite trusted storage format, without arithmetic replay."""
    schema = sql(connection,
                 "SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
    demand(schema == [("meta", META_SQL), ("transitions", TRANSITION_SQL)], "ledger:schema")
    objects = sql(connection,
                  "SELECT type, name FROM sqlite_master WHERE type != 'table'").fetchall()
    demand(not objects, "ledger:unexpected-schema-object")
    meta = sql(connection,
               "SELECT singleton, profile, expected_json, checker_json, "
               "initial_allowance_json, allowance_json FROM meta").fetchall()
    demand(len(meta) == 1, "ledger:metadata-row-count")
    singleton, profile, expected_text, checker_text, initial_text, current_text = meta[0]
    demand(singleton == 1 and type(singleton) is int and profile == PROFILE,
           "ledger:metadata-profile")
    saved_expected = stored_json(expected_text)
    saved_checkers = stored_json(checker_text)
    initial, current = stored_json(initial_text), stored_json(current_text)
    balance(initial)
    balance(current)
    demand(type(saved_expected) is dict and
           canonical(saved_expected.get("allowance")) == canonical(initial),
           "ledger:initial-allowance-binding")
    demand(canonical(saved_checkers) == canonical(checkers), "ledger:checker-fingerprint")
    rows = sql(connection,
               "SELECT slot, transition_key, payload_json, result_json FROM transitions").fetchall()
    demand(len(rows) <= 1, "ledger:transition-capacity")
    stored = None
    if not rows:
        demand(canonical(current) == canonical(initial), "ledger:empty-balance")
    else:
        slot, key, payload_text, result_text = rows[0]
        demand(type(slot) is int and slot == 1, "ledger:slot")
        payload, result = stored_json(payload_text), stored_json(result_text)
        envelope(payload)
        demand(key == payload["transition_key"], "ledger:key-binding")
        keys(result, ("outcome", "reason", "checkpoint_retained", "allowance_after", "semantic_delta"),
             "ledger:result")
        demand(initial["remaining"] > 0, "ledger:committed-without-allowance")
        after = {"grant": initial["grant"], "spent": initial["spent"] + 1,
                 "remaining": initial["remaining"] - 1}
        demand(canonical(current) == canonical(after) and
               canonical(result["allowance_after"]) == canonical(after), "ledger:committed-balance")
        demand(result["outcome"] == "AcceptedCheckpointContinuation" and
               result["reason"] == "prefix-and-declared-next-step-checked" and
               canonical(result["semantic_delta"]) == canonical(DELTA), "ledger:result-scope")
        parent_receipt = payload["checkpoint_receipt"]
        demand(type(parent_receipt) is dict and
               canonical(result["checkpoint_retained"]) == canonical(parent_receipt.get("checkpoint")) and
               canonical(parent_receipt.get("allowance_after")) == canonical(after),
               "ledger:result-payload-binding")
        stored = (key, payload_text, result)
    if canonical(expected) != canonical(saved_expected):
        # The stored problem stays authoritative; caller changes are not corruption.
        raise Refusal("InvalidContext", "ledger:expected-binding")
    return current, stored


def connect_existing(path):
    if not path.is_file():
        raise Refusal("MissingLedger", "ledger:existing-file-required")
    if path.stat().st_size > MAX_DB:
        raise Refusal("InvalidLedger", "ledger:database-byte-limit")
    try:
        return sqlite3.connect(path.resolve().as_uri() + "?mode=rw", uri=True,
                               timeout=0.1, isolation_level=None)
    except sqlite3.DatabaseError as error:
        raise Refusal("InvalidLedger", str(error)) from error


def rollback(connection):
    global WORK
    # This statement consumes the unit reserved by tick()/parent_call().
    WORK += 1
    connection.execute("ROLLBACK")


def configure(connection, initializing=False):
    if initializing:
        sql(connection, "PRAGMA page_size=4096")
    demand(sql(connection, "PRAGMA page_size").fetchone()[0] == 4096, "ledger:page-size")
    demand(sql(connection, "PRAGMA journal_mode=DELETE").fetchone()[0].lower() == "delete",
           "ledger:journal-mode")
    sql(connection, "PRAGMA synchronous=FULL")
    demand(sql(connection, "PRAGMA synchronous").fetchone()[0] == 2, "ledger:synchronous")
    sql(connection, "PRAGMA busy_timeout=100")
    pages = sql(connection, "PRAGMA max_page_count=256").fetchone()[0]
    demand(pages <= 256, "ledger:page-count-bound")


def fault_exit(name, phase, parent_checked):
    print(json.dumps({"fault": name, "work_units": WORK,
                      "parent_checked": parent_checked, "phase": phase}, sort_keys=True),
          file=__import__("sys").stderr, flush=True)
    os._exit(17 if name == "before_commit" else 19)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("init", "submit"):
        command = sub.add_parser(name)
        command.add_argument("--expected", required=True)
        command.add_argument("--ledger", required=True)
        if name == "submit":
            command.add_argument("--candidate", required=True)
            command.add_argument("--fault", choices=("none", "before_commit", "after_commit"), default="none")
    args = parser.parse_args()
    started = time.perf_counter()
    expected, connection, stored_result, current = None, None, None, None
    checked, debit, commit_uncertain = False, 0, False
    outcome, reason = "ImplementationFailure", "unstarted"
    signal.signal(signal.SIGALRM, deadline)
    signal.setitimer(signal.ITIMER_REAL, 3)
    try:
        try:
            expected = read(args.expected, 131072)
        except ValueError as error:
            raise Refusal("InvalidContext", str(error)) from error
        path = Path(args.ledger)
        checkers = fingerprint()
        if args.command == "init":
            if path.exists():
                raise Refusal("LedgerExists", "ledger:initialization-never-overwrites")
            load_parent()
            try:
                parent_call(PARENT.request, expected)
            except ValueError as error:
                raise Refusal("InvalidContext", str(error)) from error
            try:
                descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            except FileExistsError as error:
                raise Refusal("LedgerExists", "ledger:initialization-never-overwrites") from error
            os.close(descriptor)
            connection = connect_existing(path)
            configure(connection, True)
            sql(connection, "BEGIN IMMEDIATE")
            sql(connection, META_SQL)
            sql(connection, TRANSITION_SQL)
            initial = expected["allowance"]
            sql(connection, "INSERT INTO meta VALUES (1, ?, ?, ?, ?, ?)",
                (PROFILE, canonical(expected), canonical(checkers), canonical(initial), canonical(initial)))
            commit_uncertain = True
            sql(connection, "COMMIT")
            commit_uncertain = False
            current = initial
            outcome, reason = "InitializedLedger", "receiver-owned-single-slot-ledger-created"
        else:
            connection = connect_existing(path)
            try:
                configure(connection)
                sql(connection, "BEGIN IMMEDIATE")
                # Read the authoritative balance for informative refusal output.
                raw_balance = sql(connection, "SELECT allowance_json FROM meta WHERE singleton=1").fetchall()
                if len(raw_balance) == 1:
                    tentative = stored_json(raw_balance[0][0])
                    balance(tentative)
                    current = tentative
                current, stored = ledger_state(connection, expected, checkers)
            except (ValueError, sqlite3.DatabaseError) as error:
                raise Refusal("InvalidLedger", str(error)) from error
            try:
                candidate = read(args.candidate)
                envelope(candidate)
            except ValueError as error:
                raise Refusal("InvalidEvidence", str(error)) from error
            payload = canonical(candidate)
            if stored is not None:
                key, saved_payload, result = stored
                if candidate["transition_key"] != key:
                    outcome, reason = "PausedLedgerCapacity", "ledger:single-accepted-slot-occupied"
                elif payload != saved_payload:
                    outcome, reason = "Conflict", "ledger:same-key-different-canonical-payload"
                else:
                    outcome, reason = "ReplayedContinuation", "ledger:stored-result-no-new-debit"
                    stored_result = result
            else:
                if len(canonical(candidate["checkpoint_receipt"]).encode("utf-8")) > 131072:
                    raise Refusal("UnknownBudget", "checkpoint-receipt:wire-byte-limit")
                load_parent()
                try:
                    prepared = parent_call(PARENT.request, expected)
                except ValueError as error:
                    raise Refusal("InvalidContext", str(error)) from error
                try:
                    checked = True
                    result = parent_call(PARENT.verify, expected, candidate["checkpoint_receipt"],
                                         prepared, {"prefix": False, "next": False})
                except ValueError as error:
                    raise Refusal("InvalidEvidence", str(error)) from error
                parent_outcome, parent_reason, retained, after = result
                deterministic = {"outcome": parent_outcome, "reason": parent_reason,
                                 "checkpoint_retained": retained, "allowance_after": after,
                                 "semantic_delta": DELTA if parent_outcome == "AcceptedCheckpointContinuation" else []}
                if parent_outcome != "AcceptedCheckpointContinuation":
                    stored_result = deterministic
                    outcome, reason = parent_outcome, parent_reason
                else:
                    sql(connection, "INSERT INTO transitions VALUES (1, ?, ?, ?)",
                        (candidate["transition_key"], payload, canonical(deterministic)))
                    sql(connection, "UPDATE meta SET allowance_json=? WHERE singleton=1", (canonical(after),))
                    if args.fault == "before_commit":
                        fault_exit(args.fault, "writes-complete-before-commit", checked)
                    commit_uncertain = True
                    sql(connection, "COMMIT")
                    commit_uncertain = False
                    current, debit, stored_result = after, 1, deterministic
                    if args.fault == "after_commit":
                        fault_exit(args.fault, "commit-succeeded-before-reply", checked)
                    outcome, reason = "CommittedContinuation", "ledger:checked-result-and-debit-committed"
    except Refusal as error:
        outcome, reason = error.outcome, error.reason
    except Exception as error:
        outcome, reason = "ImplementationFailure", type(error).__name__ + ": " + str(error)
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if commit_uncertain:
            outcome, reason = "ImplementationFailure", "ledger:commit-state-unknown-reconcile-existing-ledger"
            current, stored_result, debit = None, None, 0
        if connection is not None:
            try:
                if connection.in_transaction:
                    rollback(connection)
                connection.close()
            except Exception:
                outcome, reason = "ImplementationFailure", "ledger:cleanup-failed-reconcile-existing-ledger"
                current, stored_result, debit = None, None, 0
    print(json.dumps({"profile": PROFILE, "outcome": outcome, "reason": reason,
                      "expected_request": expected, "stored_result": stored_result,
                      "allowance": current, "debit_delta": debit, "parent_checked": checked,
                      "work_units": WORK, "wall_seconds": time.perf_counter() - started,
                      "native_authority": False, "close_authorized": False,
                      "free_authorized": False}, sort_keys=True, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
