#!/usr/bin/env python3
"""Verify one v1 charge--reservation binding without launching a task.

Project-original Codex (OpenAI), Unknown v0.3, submitted through Mingli
Yuan's authorized account proxy. Account use is not review or correctness.
"""
import argparse
import hashlib
import json
from pathlib import Path


class InvalidEvidence(Exception):
    pass


class InvalidContext(Exception):
    pass


def require(condition, reason, error=InvalidEvidence):
    if not condition:
        raise error(reason)


def strict(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            require(key not in value, "DuplicateKey")
            value[key] = item
        return value

    return json.loads(
        raw,
        object_pairs_hook=pairs,
        parse_constant=lambda _: (_ for _ in ()).throw(InvalidEvidence("Number")),
    )


def wire(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode()


def digest(value):
    return hashlib.sha256(wire(value)).hexdigest()


def integer(value, lower=0, upper=100000):
    return type(value) is int and lower <= value <= upper


def text(value, maximum=128):
    return type(value) is str and 0 < len(value) <= maximum


def hexdigest(value):
    return (type(value) is str and len(value) == 64 and
            all(character in "0123456789abcdef" for character in value))


def fields(value, names):
    require(type(value) is dict and set(value) == set(names), "Fields")


def nodes(value):
    if type(value) is dict:
        return 1 + sum(1 + nodes(item) for item in value.values())
    if type(value) is list:
        return 1 + sum(nodes(item) for item in value)
    return 1


def read_canonical(path, limit):
    raw = Path(path).read_bytes()
    require(len(raw) <= limit, "InputSize")
    value = strict(raw)
    require(raw == wire(value), "NoncanonicalInput")
    return value, nodes(value)


def validate_contract(contract):
    fields(contract, ("call_cap", "correction_cap", "purpose", "task", "work_cap"))
    require(text(contract["task"]) and text(contract["purpose"]), "TaskContract")
    require(integer(contract["work_cap"], 1) and integer(contract["call_cap"], 1),
            "TaskCap")
    require(integer(contract["correction_cap"], 0, 1), "CorrectionCap")


def receive(account_path, journal_path):
    account, account_nodes = read_canonical(account_path, 8192)
    journal, journal_nodes = read_canonical(journal_path, 32768)

    fields(account, ("charges", "profile"))
    require(account["profile"] == "cumulative-trial-v1", "AccountProfile")
    require(type(account["charges"]) is list and 0 < len(account["charges"]) <= 8,
            "Charges")
    charge_ids = []
    for charge in account["charges"]:
        fields(charge, ("charge_id", "phase", "task_contract_sha256", "units"))
        require(text(charge["charge_id"], 96), "ChargeId")
        require(charge["phase"] == "charged", "ChargePhase")
        require(hexdigest(charge["task_contract_sha256"]), "ChargeTaskDigest")
        require(integer(charge["units"], 1), "ChargeUnits")
        charge_ids.append(charge["charge_id"])
    require(len(set(charge_ids)) == len(charge_ids), "DuplicateChargeId")

    fields(journal, ("contract", "events", "profile"))
    require(journal["profile"] == "task-reservation-v1", "JournalProfile")
    validate_contract(journal["contract"])
    require(type(journal["events"]) is list and 0 < len(journal["events"]) <= 16,
            "Events")
    contract_digest = digest(journal["contract"])
    reservation_ids = []
    reservations = []
    for index, event in enumerate(journal["events"], 1):
        fields(event, ("charge_id", "id", "kind", "phase",
                       "task_contract_sha256", "units"))
        require(event["kind"] == "reserve" and event["id"] == index,
                "ReservationSequence")
        require(text(event["charge_id"], 96), "ReservationChargeId")
        require(event["phase"] == "reserved", "ReservationPhase")
        require(hexdigest(event["task_contract_sha256"]), "ReservationTaskDigest")
        require(integer(event["units"], 1), "ReservationUnits")
        reservation_ids.append(event["charge_id"])
        reservations.append(event)
    require(len(set(reservation_ids)) == len(reservation_ids),
            "DuplicateReservationChargeId")
    require(len(account["charges"]) == 1 and len(reservations) == 1,
            "SinglePairProfile")

    charge = account["charges"][0]
    reservation = reservations[0]
    require(charge["charge_id"] == reservation["charge_id"],
            "ChargeIdMismatch", InvalidContext)
    require(charge["units"] == reservation["units"],
            "ChargeUnitsMismatch", InvalidContext)
    require(charge["task_contract_sha256"] == contract_digest,
            "AccountTaskMismatch", InvalidContext)
    require(reservation["task_contract_sha256"] == contract_digest,
            "ReservationTaskMismatch", InvalidContext)

    work_units = account_nodes + journal_nodes + len(wire(account)) + len(wire(journal)) + 16
    return {
        "profile": "adva.research.bound-charge-pair-receipt.v0",
        "outcome": "BindingVerified",
        "reason": "ExactChargeReservationPair",
        "charge_id": charge["charge_id"],
        "task": journal["contract"]["task"],
        "task_contract_sha256": contract_digest,
        "units": charge["units"],
        "account_phase": charge["phase"],
        "reservation_phase": reservation["phase"],
        "launch_authorized": False,
        "retry_authorized": False,
        "account_mutation_authorized": False,
        "native_authority": False,
        "free_authorized": False,
        "work_units": work_units,
    }


def main(account, journal):
    try:
        result = receive(account, journal)
    except InvalidContext as error:
        result = {
            "profile": "adva.research.bound-charge-pair-receipt.v0",
            "outcome": "InvalidContext",
            "reason": str(error),
            "launch_authorized": False,
            "retry_authorized": False,
            "account_mutation_authorized": False,
            "native_authority": False,
            "free_authorized": False,
            "work_units": 0,
        }
    except (OSError, ValueError, InvalidEvidence) as error:
        result = {
            "profile": "adva.research.bound-charge-pair-receipt.v0",
            "outcome": "InvalidEvidence",
            "reason": type(error).__name__ + ": " + str(error),
            "launch_authorized": False,
            "retry_authorized": False,
            "account_mutation_authorized": False,
            "native_authority": False,
            "free_authorized": False,
            "work_units": 0,
        }
    print(wire(result).decode(), end="")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", required=True, type=Path)
    parser.add_argument("--journal", required=True, type=Path)
    args = parser.parse_args()
    raise SystemExit(main(args.account, args.journal))
