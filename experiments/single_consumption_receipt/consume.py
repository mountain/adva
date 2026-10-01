#!/usr/bin/env python3
"""Finite file-backed consumption-state transition and reconciliation tool.

Project-original Codex (OpenAI), Unknown v0.3, submitted through Mingli
Yuan's authorized account proxy. Account use is not review or correctness.
"""
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path


WORK = 0


class InvalidEvidence(Exception):
    pass


class InvalidContext(Exception):
    pass


def charge(units=1):
    global WORK
    WORK += units


def require(condition, reason, error=InvalidEvidence):
    charge()
    if not condition:
        raise error(reason)


def strict(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, "DuplicateKey")
            value[key] = item
        return value

    charge(len(raw))
    return json.loads(
        raw,
        object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(InvalidEvidence("Number")),
    )


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def hexdigest(value):
    charge()
    return (type(value) is str and len(value) == 64 and
            all(character in "0123456789abcdef" for character in value))


def label(value, maximum=96):
    charge()
    return type(value) is str and 0 < len(value) <= maximum


def validate(state):
    require(type(state) is dict and set(state) == {
        "attempt_id", "pair_digest", "profile", "receipt_digest", "state"
    }, "StateFields")
    require(state["profile"] == "single-consumption-ledger-v0", "StateProfile")
    require(hexdigest(state["pair_digest"]), "PairDigest")
    require(state["state"] in ("unconsumed", "pending", "consumed"), "StateKind")
    if state["state"] == "unconsumed":
        require(state["attempt_id"] is None and state["receipt_digest"] is None,
                "UnconsumedShape")
    elif state["state"] == "pending":
        require(label(state["attempt_id"]) and state["receipt_digest"] is None,
                "PendingShape")
    else:
        require(label(state["attempt_id"]) and hexdigest(state["receipt_digest"]),
                "ConsumedShape")


def read_state(path):
    raw = path.read_bytes()
    require(len(raw) <= 4096, "StateSize")
    state = strict(raw)
    require(raw == wire(state), "NoncanonicalState")
    validate(state)
    return state


def write_atomic(path, state):
    raw = wire(state)
    require(len(raw) <= 4096, "OutputSize")
    temporary = path.with_name(path.name + ".next-" + str(os.getpid()))
    with temporary.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory)
    finally:
        os.close(directory)
    charge(len(raw))


def result(outcome, reason, state, transition=None):
    return {
        "profile": "adva.research.single-consumption-receipt.v0",
        "outcome": outcome,
        "reason": reason,
        "state": state["state"],
        "pair_digest": state["pair_digest"],
        "attempt_id": state["attempt_id"],
        "receipt_digest": state["receipt_digest"],
        "transition": transition,
        "effect_authorized": False,
        "retry_authorized": False,
        "refund_authorized": False,
        "native_authority": False,
        "free_authorized": False,
        "work_units": WORK,
    }


def operate(path, command, pair_digest, attempt_id, receipt_digest, crash_after_reserve):
    require(hexdigest(pair_digest), "RequestedPairDigest")
    lock_path = path.with_name(path.name + ".lock")
    lock_path.touch(exist_ok=True)
    with lock_path.open("rb") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        state = read_state(path)
        require(state["pair_digest"] == pair_digest,
                "PairDigestMismatch", InvalidContext)

        if command == "reconcile":
            if state["state"] == "unconsumed":
                return result("ProvenUnconsumed", "NoConsumptionAttemptRecorded", state)
            if state["state"] == "pending":
                return result("UnknownConsumptionState", "PendingWithoutReceipt", state)
            return result("StoredConsumed", "ConsumptionReceiptPresent", state)

        require(label(attempt_id), "AttemptId")
        if command == "reserve":
            require(receipt_digest is None, "UnexpectedReceiptDigest")
            if state["state"] == "unconsumed":
                following = dict(state, state="pending", attempt_id=attempt_id)
                write_atomic(path, following)
                if crash_after_reserve:
                    os._exit(23)
                return result("PendingRecorded", "ExclusivePendingSlot", following,
                              "unconsumed->pending")
            if state["state"] == "pending":
                return result("UnknownConsumptionState", "PendingWithoutReceipt", state)
            return result("StoredConsumed", "ConsumptionReceiptPresent", state)

        require(command == "commit", "Command")
        require(hexdigest(receipt_digest), "ReceiptDigest")
        if state["state"] == "unconsumed":
            raise InvalidContext("CommitWithoutPending")
        if state["state"] == "pending":
            require(state["attempt_id"] == attempt_id,
                    "AttemptIdMismatch", InvalidContext)
            following = dict(state, state="consumed", receipt_digest=receipt_digest)
            write_atomic(path, following)
            return result("ConsumedRecorded", "ReceiptStored", following,
                          "pending->consumed")
        require(state["attempt_id"] == attempt_id and
                state["receipt_digest"] == receipt_digest,
                "ConsumedReceiptMismatch", InvalidContext)
        return result("StoredConsumed", "ConsumptionReceiptPresent", state)


def main(args):
    global WORK
    WORK = 0
    try:
        value = operate(args.ledger, args.command, args.pair_digest,
                        args.attempt_id, args.receipt_digest,
                        args.crash_after_reserve)
    except InvalidContext as error:
        value = {
            "profile": "adva.research.single-consumption-receipt.v0",
            "outcome": "InvalidContext",
            "reason": str(error),
            "effect_authorized": False,
            "retry_authorized": False,
            "refund_authorized": False,
            "native_authority": False,
            "free_authorized": False,
            "work_units": WORK,
        }
    except (OSError, ValueError, InvalidEvidence) as error:
        value = {
            "profile": "adva.research.single-consumption-receipt.v0",
            "outcome": "InvalidEvidence",
            "reason": type(error).__name__ + ": " + str(error),
            "effect_authorized": False,
            "retry_authorized": False,
            "refund_authorized": False,
            "native_authority": False,
            "free_authorized": False,
            "work_units": WORK,
        }
    print(wire(value).decode(), end="")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--command", required=True,
                        choices=("reserve", "commit", "reconcile"))
    parser.add_argument("--pair-digest", required=True)
    parser.add_argument("--attempt-id")
    parser.add_argument("--receipt-digest")
    parser.add_argument("--crash-after-reserve", action="store_true")
    raise SystemExit(main(parser.parse_args()))
